"""MCP Client Manager for upstream tool federation.

SS-I3 Compliance: HestAI-MCP must act as both MCP Server (outward) and MCP Client
(inward to OCTAVE and other MCP servers). Upstream tools are namespaced.

Namespacing per SS-I3:
- octave.ingest, octave.create, octave.amend
- memory.query, memory.write
- git.status, git.diff
- repomix.pack, repomix.grep

Configuration: Server commands and args can be overridden via environment variables:
- HESTAI_MCP_<SERVER>_COMMAND: Override the command (default: npx)
- HESTAI_MCP_<SERVER>_ARGS: Override args as comma-separated string (e.g., "-y,repomix")
"""

import asyncio
import logging
import os
from contextlib import AsyncExitStack
from types import TracebackType
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing_extensions import Self

logger = logging.getLogger(__name__)


def _get_server_config(
    server_name: str, default_command: str, default_args: list[str]
) -> dict[str, Any]:
    """Build server config from environment variables with fallback to defaults.

    Environment variables checked:
    - HESTAI_MCP_<SERVER>_COMMAND: Command to run (e.g., "/usr/local/bin/octave-mcp")
    - HESTAI_MCP_<SERVER>_ARGS: Comma-separated args (e.g., "-y,@hestai/octave-mcp")

    Args:
        server_name: Server name used in env var prefix (e.g., "octave" -> HESTAI_MCP_OCTAVE_*)
        default_command: Default command if env var not set
        default_args: Default args list if env var not set

    Returns:
        Server configuration dict with transport, command, and args
    """
    env_prefix = f"HESTAI_MCP_{server_name.upper()}"

    command = os.environ.get(f"{env_prefix}_COMMAND", default_command)
    args_str = os.environ.get(f"{env_prefix}_ARGS")

    if args_str:
        # Parse comma-separated args, strip whitespace
        args = [arg.strip() for arg in args_str.split(",") if arg.strip()]
        # Fall back to defaults if parsing results in empty list
        if not args:
            args = default_args
    else:
        args = default_args

    return {
        "transport": "stdio",
        "command": command,
        "args": args,
    }


def _build_server_configs() -> dict[str, dict[str, Any]]:
    """Build SERVER_CONFIGS dict from environment variables with defaults.

    Returns:
        Dict mapping server name to configuration
    """
    return {
        "octave": _get_server_config("octave", "npx", ["-y", "@hestai/octave-mcp"]),
        "repomix": _get_server_config("repomix", "npx", ["-y", "repomix"]),
    }


class MCPConnectionError(Exception):
    """Raised when connection to an MCP server fails.

    SS-I6: Graceful degradation with meaningful error messages.
    """

    def __init__(self, server_name: str, message: str, cause: Exception | None = None):
        self.server_name = server_name
        self.cause = cause
        super().__init__(f"Failed to connect to MCP server '{server_name}': {message}")


class MCPToolError(Exception):
    """Raised when an MCP tool invocation fails.

    SS-I6: Graceful degradation with meaningful error messages.
    """

    def __init__(
        self, server_name: str, tool_name: str, message: str, cause: Exception | None = None
    ):
        self.server_name = server_name
        self.tool_name = tool_name
        self.cause = cause
        super().__init__(f"Tool '{tool_name}' on server '{server_name}' failed: {message}")


class MCPClientManager:
    """Manager for upstream MCP server connections.

    SS-I3 Compliance:
    - Connection manager for upstream servers
    - Explicit allowlist of callable upstream tools
    - Namespaced tool access (server.tool format)

    Usage:
        async with MCPClientManager() as manager:
            result = await manager.call_tool("octave.ingest", {"content": "..."})
    """

    # SS-I3: Namespace separator
    TOOL_NAMESPACE_SEPARATOR = "."

    # SS-I3: "Explicit allowlist of callable upstream tools"
    # These are the only tools that can be called through federation
    ALLOWED_UPSTREAM_TOOLS: frozenset[str] = frozenset(
        [
            # OCTAVE MCP tools
            "octave.ingest",
            "octave.create",
            "octave.amend",
            "octave.eject",
            # Repomix MCP tools
            "repomix.pack",
            "repomix.grep",
            "repomix.read",
            # Memory MCP tools (future)
            "memory.query",
            "memory.write",
            # Git MCP tools (future)
            "git.status",
            "git.diff",
        ]
    )

    # Server connection configurations
    # Maps server name to connection config
    # NOTE: Built from env vars at module load time via _build_server_configs()
    SERVER_CONFIGS: dict[str, dict[str, Any]] = _build_server_configs()

    # Default timeout values (seconds)
    DEFAULT_CONNECT_TIMEOUT = 30.0
    DEFAULT_TOOL_TIMEOUT = 60.0

    def __init__(
        self,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
        tool_timeout: float = DEFAULT_TOOL_TIMEOUT,
    ) -> None:
        """Initialize MCP Client Manager.

        Args:
            connect_timeout: Timeout for session.initialize() in seconds (default: 30.0)
            tool_timeout: Timeout for session.call_tool() in seconds (default: 60.0)
        """
        self._connections: dict[str, Any] = {}
        self._connected = False
        # Track MCP sessions per server
        self._sessions: dict[str, ClientSession] = {}
        # Track AsyncExitStacks for atomic cleanup (replaces separate context tracking)
        self._exit_stacks: dict[str, AsyncExitStack] = {}
        # Track connection errors per server for graceful degradation
        self._connection_errors: dict[str, MCPConnectionError] = {}
        # Concurrency control: serialize connect() calls to prevent race conditions
        self._connect_lock = asyncio.Lock()
        # Timeout configuration
        self.connect_timeout = connect_timeout
        self.tool_timeout = tool_timeout

    async def __aenter__(self) -> Self:
        """Enter async context manager, establishing connections."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager, closing connections."""
        await self.disconnect()

    async def connect(self) -> None:
        """Connect to configured upstream MCP servers.

        SS-I3: Connection manager for upstream servers.
        SS-I6: Graceful degradation - partial failures don't crash.

        Uses MCP SDK stdio_client to spawn subprocess and establish connection.
        Idempotent: calling connect() on already-connected manager is a no-op.

        Thread-safe: Uses asyncio.Lock to prevent race conditions when multiple
        coroutines call connect() concurrently. Without the lock, concurrent calls
        could pass the _connected check before any sets it True, causing duplicate
        subprocess spawning and resource leaks.
        """
        async with self._connect_lock:
            # Idempotency guard: prevent double-connect which would orphan contexts
            # This check is inside the lock to prevent race conditions
            if self._connected:
                logger.debug("MCPClientManager already connected, skipping")
                return

            connection_failures: list[tuple[str, Exception]] = []

            for server_name, config in self.SERVER_CONFIGS.items():
                if config["transport"] == "stdio":
                    try:
                        await self._connect_stdio_server(server_name, config)
                        logger.info(f"Connected to MCP server: {server_name}")
                    except Exception as e:
                        error = MCPConnectionError(
                            server_name=server_name,
                            message=str(e),
                            cause=e,
                        )
                        self._connection_errors[server_name] = error
                        connection_failures.append((server_name, e))
                        logger.warning(f"Failed to connect to {server_name}: {e}")

            # If all connections failed, raise error
            if len(connection_failures) == len(self.SERVER_CONFIGS):
                first_error = connection_failures[0][1]
                raise MCPConnectionError(
                    server_name="all",
                    message=f"All server connections failed. First error: {first_error}",
                    cause=first_error,
                )

            self._connected = True
            logger.info(
                f"MCP Client Manager connected. "
                f"Success: {len(self._sessions)}, Failures: {len(connection_failures)}"
            )

    async def _connect_stdio_server(self, server_name: str, config: dict[str, Any]) -> None:
        """Connect to a single stdio-based MCP server with atomic rollback.

        Uses AsyncExitStack for atomic connect-or-rollback: if any step fails
        after entering the stdio context (spawning subprocess), the stack
        ensures cleanup happens immediately, preventing zombie processes.

        Args:
            server_name: Name of the server (e.g., "octave")
            config: Server configuration dict with command/args

        Raises:
            MCPConnectionError: If connection times out or fails
        """
        stack = AsyncExitStack()
        try:
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command=config["command"],
                args=config["args"],
            )

            # Enter stdio context - spawns subprocess
            stdio_ctx = stdio_client(server_params)
            read_stream, write_stream = await stack.enter_async_context(stdio_ctx)

            # Enter session context
            session_ctx = ClientSession(read_stream, write_stream)
            session = await stack.enter_async_context(session_ctx)

            # Initialize MCP connection with timeout to prevent deadlock
            try:
                await asyncio.wait_for(
                    session.initialize(),
                    timeout=self.connect_timeout,
                )
            except asyncio.TimeoutError:
                raise MCPConnectionError(
                    server_name=server_name,
                    message=f"Connection timed out after {self.connect_timeout}s",
                    cause=None,
                ) from None

            # Success - transfer ownership of stack to instance
            self._exit_stacks[server_name] = stack
            self._sessions[server_name] = session
            self._connections[server_name] = session

        except MCPConnectionError:
            # Re-raise MCPConnectionError without wrapping
            await stack.aclose()
            raise
        except Exception:
            # Rollback: close all entered contexts (kills subprocess)
            await stack.aclose()
            raise

    async def disconnect(self) -> None:
        """Disconnect from all upstream MCP servers.

        Uses AsyncExitStack.aclose() for each server which properly exits
        all context managers in reverse order (session first, then stdio).
        """
        for server_name, stack in list(self._exit_stacks.items()):
            try:
                await stack.aclose()
                logger.debug(f"Closed connection to {server_name}")
            except Exception as e:
                logger.warning(f"Error closing {server_name}: {e}")

        # Clear all tracking dicts
        self._exit_stacks.clear()
        self._sessions.clear()
        self._connections.clear()
        self._connection_errors.clear()

        self._connected = False
        logger.info("MCP Client Manager disconnected")

    def validate_tool(self, tool_name: str) -> tuple[str, str]:
        """Validate tool name and extract server/tool parts.

        SS-I3: Explicit allowlist of callable upstream tools.

        Args:
            tool_name: Namespaced tool name (e.g., "octave.ingest")

        Returns:
            Tuple of (server_name, tool_name)

        Raises:
            ValueError: If tool name is invalid or not in allowlist
        """
        if self.TOOL_NAMESPACE_SEPARATOR not in tool_name:
            raise ValueError(
                f"Invalid tool namespace: '{tool_name}'. "
                f"Expected format: 'server{self.TOOL_NAMESPACE_SEPARATOR}tool'"
            )

        parts = tool_name.split(self.TOOL_NAMESPACE_SEPARATOR, 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(
                f"Invalid tool namespace: '{tool_name}'. "
                f"Expected format: 'server{self.TOOL_NAMESPACE_SEPARATOR}tool'"
            )

        server_name, local_tool_name = parts

        if tool_name not in self.ALLOWED_UPSTREAM_TOOLS:
            raise ValueError(
                f"Tool '{tool_name}' is not in the allowed upstream tools list. "
                f"Allowed tools: {sorted(self.ALLOWED_UPSTREAM_TOOLS)}"
            )

        return server_name, local_tool_name

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call an upstream MCP tool.

        SS-I3: Namespaced tool access through federation.
        SS-I6: Graceful degradation with meaningful errors.

        Args:
            tool_name: Namespaced tool name (e.g., "octave.ingest")
            arguments: Tool arguments

        Returns:
            Tool result from the MCP server

        Raises:
            ValueError: If tool name is invalid or not in allowlist
            RuntimeError: If not connected
            MCPToolError: If tool invocation fails or times out
        """
        # Validate tool name and check allowlist
        server_name, local_tool_name = self.validate_tool(tool_name)

        if not self._connected:
            raise RuntimeError("MCPClientManager not connected. Use 'async with' context manager.")

        # Check if this server had a connection error
        if server_name in self._connection_errors:
            error = self._connection_errors[server_name]
            raise MCPToolError(
                server_name=server_name,
                tool_name=local_tool_name,
                message=f"Server not available: {error}",
                cause=error,
            )

        # Get the session for this server
        session = self._sessions.get(server_name)
        if not session:
            raise RuntimeError(f"Not connected to server: {server_name}")

        # Call the tool via MCP SDK with timeout to prevent deadlock
        try:
            result = await asyncio.wait_for(
                session.call_tool(local_tool_name, arguments or {}),
                timeout=self.tool_timeout,
            )
            logger.debug(f"Tool {tool_name} returned: {result}")
            return result
        except asyncio.TimeoutError:
            raise MCPToolError(
                server_name=server_name,
                tool_name=local_tool_name,
                message=f"Tool call timed out after {self.tool_timeout}s",
                cause=None,
            ) from None
        except Exception as e:
            raise MCPToolError(
                server_name=server_name,
                tool_name=local_tool_name,
                message=str(e),
                cause=e,
            ) from e

    def is_connected(self) -> bool:
        """Check if manager is connected to upstream servers."""
        return self._connected

    def get_available_servers(self) -> list[str]:
        """Get list of successfully connected servers.

        Returns:
            List of server names that are connected and available.
        """
        return list(self._sessions.keys())

    def get_failed_servers(self) -> dict[str, MCPConnectionError]:
        """Get servers that failed to connect with their errors.

        Returns:
            Dict mapping server name to connection error.
        """
        return dict(self._connection_errors)
