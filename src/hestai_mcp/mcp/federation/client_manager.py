"""MCP Client Manager for upstream tool federation.

SS-I3 Compliance: HestAI-MCP must act as both MCP Server (outward) and MCP Client
(inward to OCTAVE and other MCP servers). Upstream tools are namespaced.

Namespacing per SS-I3:
- octave.ingest, octave.create, octave.amend
- memory.query, memory.write
- git.status, git.diff
- repomix.pack, repomix.grep
"""

import logging
from types import TracebackType
from typing import Any

from typing_extensions import Self

logger = logging.getLogger(__name__)


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
    SERVER_CONFIGS: dict[str, dict[str, Any]] = {
        "octave": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@hestai/octave-mcp"],
        },
        "repomix": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "repomix"],
        },
    }

    def __init__(self) -> None:
        """Initialize MCP Client Manager."""
        self._connections: dict[str, Any] = {}
        self._connected = False

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

        Note: Actual MCP client connection implementation depends on
        the MCP SDK. This is a stub that can be extended.
        """
        # Currently a stub - actual implementation requires MCP SDK
        # For now, we log connection attempts and mark as connected
        for server_name, config in self.SERVER_CONFIGS.items():
            logger.info(f"Would connect to MCP server: {server_name} with config: {config}")

        self._connected = True
        logger.info("MCP Client Manager connected (stub mode)")

    async def disconnect(self) -> None:
        """Disconnect from all upstream MCP servers."""
        for server_name in list(self._connections.keys()):
            logger.info(f"Disconnecting from MCP server: {server_name}")
            del self._connections[server_name]

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

        Args:
            tool_name: Namespaced tool name (e.g., "octave.ingest")
            arguments: Tool arguments

        Returns:
            Tool result

        Raises:
            ValueError: If tool name is invalid or not in allowlist
            RuntimeError: If not connected
        """
        # Validate tool name and check allowlist
        server_name, local_tool_name = self.validate_tool(tool_name)

        if not self._connected:
            raise RuntimeError("MCPClientManager not connected. Use 'async with' context manager.")

        # Stub implementation - actual implementation requires MCP SDK
        logger.info(
            f"Would call tool: {local_tool_name} on server: {server_name} "
            f"with arguments: {arguments}"
        )

        # Return stub result for now
        return {
            "status": "stub",
            "tool": tool_name,
            "message": "MCP client federation not yet implemented",
        }

    def is_connected(self) -> bool:
        """Check if manager is connected to upstream servers."""
        return self._connected
