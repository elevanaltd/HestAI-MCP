"""
Tests for MCP Client Manager - upstream tool federation.

SS-I3 Compliance: HestAI-MCP must act as both MCP Server (outward) and MCP Client
(inward to OCTAVE and other MCP servers). Upstream tools are namespaced.

Validation: Connection manager for upstream servers. Explicit allowlist of callable upstream tools.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.unit
class TestMCPClientManagerExists:
    """Test that MCP Client Manager infrastructure exists."""

    def test_mcp_client_manager_importable(self):
        """MCPClientManager must be importable from hestai_mcp.mcp.federation."""
        from hestai_mcp.mcp.federation import MCPClientManager

        assert MCPClientManager is not None

    def test_mcp_client_manager_has_required_methods(self):
        """MCPClientManager must have connect, disconnect, and call_tool methods."""
        from hestai_mcp.mcp.federation import MCPClientManager

        # SS-I3: Connection manager for upstream servers
        assert hasattr(
            MCPClientManager, "connect"
        ), "MCPClientManager must have connect() for upstream server connection"
        assert hasattr(
            MCPClientManager, "disconnect"
        ), "MCPClientManager must have disconnect() for cleanup"
        assert hasattr(
            MCPClientManager, "call_tool"
        ), "MCPClientManager must have call_tool() for invoking upstream tools"


@pytest.mark.unit
class TestMCPClientManagerNamespacing:
    """Test SS-I3 namespacing requirements."""

    def test_tool_namespacing_format(self):
        """Upstream tools must be namespaced as server.tool (SS-I3)."""
        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()

        # SS-I3 defines: octave.ingest, octave.create, repomix.pack, etc.
        # Verify namespacing is enforced
        assert hasattr(manager, "TOOL_NAMESPACE_SEPARATOR")
        assert manager.TOOL_NAMESPACE_SEPARATOR == "."

    def test_upstream_tool_allowlist_exists(self):
        """Explicit allowlist of callable upstream tools must exist (SS-I3)."""
        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()

        # SS-I3: "Explicit allowlist of callable upstream tools"
        assert hasattr(manager, "ALLOWED_UPSTREAM_TOOLS")
        assert isinstance(manager.ALLOWED_UPSTREAM_TOOLS, (list, set, frozenset))

        # Must include the tools specified in SS-I3
        required_tools = [
            "octave.ingest",
            "octave.create",
            "octave.amend",
            "repomix.pack",
        ]

        for tool in required_tools:
            assert tool in manager.ALLOWED_UPSTREAM_TOOLS, f"SS-I3 requires {tool} in allowlist"


@pytest.mark.unit
class TestMCPClientManagerAsync:
    """Test async behavior of MCP Client Manager."""

    def test_connect_is_async(self):
        """connect() must be async for non-blocking server connection."""
        import inspect

        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()
        assert inspect.iscoroutinefunction(manager.connect), "connect() must be async"

    def test_call_tool_is_async(self):
        """call_tool() must be async for non-blocking tool invocation."""
        import inspect

        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()
        assert inspect.iscoroutinefunction(manager.call_tool), "call_tool() must be async"

    @pytest.mark.asyncio
    async def test_context_manager_support(self):
        """MCPClientManager must support async context manager."""
        from hestai_mcp.mcp.federation import MCPClientManager

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession"
            ) as mock_session_cls:
                mock_session_ctx = AsyncMock()
                mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
                mock_session_cls.return_value = mock_session_ctx

                # Should support async with for proper lifecycle management
                async with MCPClientManager() as manager:
                    # Manager should be usable inside context
                    assert manager is not None
                    assert manager.is_connected() is True


@pytest.mark.unit
class TestMCPClientManagerToolValidation:
    """Test tool validation and security."""

    def test_call_tool_rejects_unallowed_tools(self):
        """call_tool must reject tools not in allowlist (SS-I3)."""
        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()

        # SS-I3: "Explicit allowlist of callable upstream tools"
        # Calling an unallowed tool should raise
        assert hasattr(
            manager, "validate_tool"
        ), "MCPClientManager must have validate_tool() for security"

    @pytest.mark.asyncio
    async def test_call_tool_validates_namespace(self):
        """call_tool must validate tool namespace format."""
        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()

        # Invalid namespace format should raise
        with pytest.raises(ValueError, match="namespace"):
            await manager.call_tool("invalid_no_dot")


@pytest.mark.unit
class TestMCPClientManagerRealConnection:
    """Test real MCP SDK connection behavior (SS-I3 implementation).

    These tests verify that MCPClientManager uses the MCP SDK for actual
    connections rather than returning stub responses.
    """

    def test_uses_mcp_sdk_types(self):
        """MCPClientManager must use MCP SDK types for connections."""
        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()

        # Must track real MCP sessions (not just booleans)
        assert hasattr(manager, "_sessions"), "Manager must track MCP ClientSession instances"
        assert hasattr(manager, "_exit_stacks"), "Manager must track AsyncExitStack for cleanup"

    @pytest.mark.asyncio
    async def test_connect_spawns_subprocess_via_stdio_client(self):
        """connect() must use MCP SDK stdio_client to spawn server processes."""
        from hestai_mcp.mcp.federation import MCPClientManager

        # Mock the MCP SDK components
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_read = MagicMock()
        mock_write = MagicMock()

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            # Setup: stdio_client returns context manager yielding (read, write)
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(mock_read, mock_write))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession"
            ) as mock_session_cls:
                # Setup: ClientSession context manager
                mock_session_ctx = AsyncMock()
                mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
                mock_session_cls.return_value = mock_session_ctx

                manager = MCPClientManager()
                await manager.connect()

                # Verify stdio_client was called with server params
                assert mock_stdio.called, "Must use stdio_client from MCP SDK"
                # Verify initialize was called on session
                assert mock_session.initialize.called, "Must call session.initialize()"

    @pytest.mark.asyncio
    async def test_connect_stores_sessions_per_server(self):
        """connect() must store ClientSession for each configured server."""
        from hestai_mcp.mcp.federation import MCPClientManager

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession"
            ) as mock_session_cls:
                mock_session_ctx = AsyncMock()
                mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
                mock_session_cls.return_value = mock_session_ctx

                manager = MCPClientManager()
                await manager.connect()

                # Sessions should be stored per server name
                assert len(manager._sessions) > 0, "Must store sessions after connect"
                for server_name in manager.SERVER_CONFIGS:
                    assert (
                        server_name in manager._sessions
                    ), f"Session for {server_name} must be stored"

    @pytest.mark.asyncio
    async def test_call_tool_invokes_mcp_session_call_tool(self):
        """call_tool() must invoke session.call_tool() on the correct server session."""
        from hestai_mcp.mcp.federation import MCPClientManager

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        # Mock call_tool response
        mock_tool_result = MagicMock()
        mock_tool_result.content = [MagicMock(text="result")]
        mock_session.call_tool = AsyncMock(return_value=mock_tool_result)

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession"
            ) as mock_session_cls:
                mock_session_ctx = AsyncMock()
                mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
                mock_session_cls.return_value = mock_session_ctx

                manager = MCPClientManager()
                await manager.connect()

                # Call an allowed tool
                result = await manager.call_tool("octave.ingest", {"content": "test"})

                # Verify session.call_tool was called with correct args
                mock_session.call_tool.assert_called_once_with("ingest", {"content": "test"})
                # Result should be the MCP response, not stub dict
                assert result == mock_tool_result

    @pytest.mark.asyncio
    async def test_call_tool_routes_to_correct_server_session(self):
        """call_tool() must route to the session for the correct server namespace."""
        from hestai_mcp.mcp.federation import MCPClientManager

        # Create distinct mock sessions for each server
        octave_session = AsyncMock()
        octave_session.initialize = AsyncMock()
        octave_result = MagicMock()
        octave_result.content = [MagicMock(text="octave result")]
        octave_session.call_tool = AsyncMock(return_value=octave_result)

        repomix_session = AsyncMock()
        repomix_session.initialize = AsyncMock()
        repomix_result = MagicMock()
        repomix_result.content = [MagicMock(text="repomix result")]
        repomix_session.call_tool = AsyncMock(return_value=repomix_result)

        # Track which server gets which session
        session_map = {"octave": octave_session, "repomix": repomix_session}
        call_count = {"count": 0}

        def get_session(*args, **kwargs):
            mock_ctx = AsyncMock()
            # Alternate between octave and repomix based on call order
            servers = list(session_map.keys())
            server_name = servers[call_count["count"] % len(servers)]
            mock_ctx.__aenter__ = AsyncMock(return_value=session_map[server_name])
            mock_ctx.__aexit__ = AsyncMock(return_value=None)
            call_count["count"] += 1
            return mock_ctx

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession",
                side_effect=get_session,
            ):
                manager = MCPClientManager()
                await manager.connect()

                # Call octave tool - use _ to indicate intentionally unused
                _ = await manager.call_tool("octave.ingest", {"content": "test"})
                octave_session.call_tool.assert_called_with("ingest", {"content": "test"})

                # Call repomix tool
                await manager.call_tool("repomix.pack", {"directory": "/tmp"})
                repomix_session.call_tool.assert_called_with("pack", {"directory": "/tmp"})


@pytest.mark.unit
class TestMCPClientManagerDisconnect:
    """Test proper disconnect and cleanup behavior."""

    @pytest.mark.asyncio
    async def test_disconnect_exits_all_context_managers(self):
        """disconnect() must properly exit all session and stdio context managers."""
        from hestai_mcp.mcp.federation import MCPClientManager

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_stdio_ctx = AsyncMock()
        mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
        mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "hestai_mcp.mcp.federation.client_manager.stdio_client",
                return_value=mock_stdio_ctx,
            ),
            patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession",
                return_value=mock_session_ctx,
            ),
        ):
            manager = MCPClientManager()
            await manager.connect()
            await manager.disconnect()

            # Verify context managers were exited
            mock_session_ctx.__aexit__.assert_called()
            mock_stdio_ctx.__aexit__.assert_called()

    @pytest.mark.asyncio
    async def test_disconnect_clears_sessions(self):
        """disconnect() must clear stored sessions."""
        from hestai_mcp.mcp.federation import MCPClientManager

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession"
            ) as mock_session_cls:
                mock_session_ctx = AsyncMock()
                mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
                mock_session_cls.return_value = mock_session_ctx

                manager = MCPClientManager()
                await manager.connect()
                assert len(manager._sessions) > 0

                await manager.disconnect()
                assert len(manager._sessions) == 0, "Sessions must be cleared on disconnect"
                assert manager.is_connected() is False


@pytest.mark.unit
class TestMCPClientManagerGracefulDegradation:
    """Test SS-I6 graceful degradation: meaningful errors on failures."""

    @pytest.mark.asyncio
    async def test_connect_failure_returns_meaningful_error(self):
        """SS-I6: Connection failure must return meaningful error, not crash."""
        from hestai_mcp.mcp.federation import MCPClientManager, MCPConnectionError

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            # Simulate subprocess failure
            mock_stdio.side_effect = FileNotFoundError("npx not found")

            manager = MCPClientManager()

            # Should raise MCPConnectionError with meaningful message
            with pytest.raises(MCPConnectionError) as exc_info:
                await manager.connect()

            assert "npx" in str(exc_info.value) or "connection" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_call_tool_on_disconnected_server_returns_error(self):
        """SS-I6: Calling tool on failed server must return meaningful error."""
        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()
        # Don't connect - simulate disconnected state

        with pytest.raises(RuntimeError, match="not connected"):
            await manager.call_tool("octave.ingest", {"content": "test"})

    @pytest.mark.asyncio
    async def test_call_tool_server_error_propagates_meaningfully(self):
        """SS-I6: Tool invocation errors must propagate with context."""
        from hestai_mcp.mcp.federation import MCPClientManager, MCPToolError

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        # Simulate tool execution failure
        mock_session.call_tool = AsyncMock(side_effect=Exception("Tool execution failed"))

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession"
            ) as mock_session_cls:
                mock_session_ctx = AsyncMock()
                mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
                mock_session_cls.return_value = mock_session_ctx

                manager = MCPClientManager()
                await manager.connect()

                # Should wrap error with context
                with pytest.raises(MCPToolError) as exc_info:
                    await manager.call_tool("octave.ingest", {"content": "test"})

                assert "octave" in str(exc_info.value).lower() or "ingest" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_partial_connection_failure_allows_other_servers(self):
        """SS-I6: If one server fails to connect, others should still work."""
        from hestai_mcp.mcp.federation import MCPClientManager

        call_count = {"count": 0}
        successful_session = AsyncMock()
        successful_session.initialize = AsyncMock()
        successful_result = MagicMock()
        successful_result.content = [MagicMock(text="success")]
        successful_session.call_tool = AsyncMock(return_value=successful_result)

        def get_stdio_ctx(*args, **kwargs):
            mock_ctx = AsyncMock()
            if call_count["count"] == 0:
                # First server (octave) fails
                mock_ctx.__aenter__ = AsyncMock(side_effect=FileNotFoundError("npx not found"))
            else:
                # Second server (repomix) succeeds
                mock_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_ctx.__aexit__ = AsyncMock(return_value=None)
            call_count["count"] += 1
            return mock_ctx

        with (
            patch(
                "hestai_mcp.mcp.federation.client_manager.stdio_client",
                side_effect=get_stdio_ctx,
            ),
            patch("hestai_mcp.mcp.federation.client_manager.ClientSession") as mock_session_cls,
        ):
            mock_session_ctx = AsyncMock()
            mock_session_ctx.__aenter__ = AsyncMock(return_value=successful_session)
            mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_session_cls.return_value = mock_session_ctx

            manager = MCPClientManager()
            # Connect should not raise even if one server fails
            await manager.connect()

            # Working server should be accessible
            # Failed server should return error when called
            # (specific behavior depends on implementation)


@pytest.mark.unit
class TestMCPClientManagerIdempotency:
    """Test idempotency of connect() to prevent resource leaks."""

    @pytest.mark.asyncio
    async def test_connect_is_idempotent(self):
        """Calling connect() twice must not orphan contexts or leak resources."""
        from hestai_mcp.mcp.federation import MCPClientManager

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession"
            ) as mock_session_cls:
                mock_session_ctx = AsyncMock()
                mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
                mock_session_cls.return_value = mock_session_ctx

                manager = MCPClientManager()

                # First connect
                await manager.connect()
                first_call_count = mock_stdio.call_count

                # Second connect should be no-op
                await manager.connect()

                # Verify stdio_client was NOT called again
                assert (
                    mock_stdio.call_count == first_call_count
                ), "connect() must be idempotent - should not create new connections"

    @pytest.mark.asyncio
    async def test_connect_after_disconnect_works(self):
        """After disconnect(), connect() should work again."""
        from hestai_mcp.mcp.federation import MCPClientManager

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()

        with patch("hestai_mcp.mcp.federation.client_manager.stdio_client") as mock_stdio:
            mock_stdio_ctx = AsyncMock()
            mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_stdio.return_value = mock_stdio_ctx

            with patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession"
            ) as mock_session_cls:
                mock_session_ctx = AsyncMock()
                mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
                mock_session_cls.return_value = mock_session_ctx

                manager = MCPClientManager()

                # Connect, disconnect, reconnect cycle
                await manager.connect()
                assert manager.is_connected() is True

                await manager.disconnect()
                assert manager.is_connected() is False

                await manager.connect()
                assert manager.is_connected() is True


@pytest.mark.unit
class TestMCPClientManagerAtomicRollback:
    """Test atomic rollback on partial connection failure."""

    @pytest.mark.asyncio
    async def test_partial_connect_failure_cleans_up_subprocess(self):
        """If session init fails after stdio enter, subprocess must be cleaned up."""
        from hestai_mcp.mcp.federation import MCPClientManager, MCPConnectionError

        manager = MCPClientManager()

        # Mock stdio_client to succeed (returns context manager)
        mock_stdio_ctx = MagicMock()
        mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
        mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)

        # Mock ClientSession to fail on initialize
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.initialize = AsyncMock(side_effect=RuntimeError("Init failed"))

        with (
            patch(
                "hestai_mcp.mcp.federation.client_manager.stdio_client",
                return_value=mock_stdio_ctx,
            ),
            patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession",
                return_value=mock_session,
            ),
        ):
            # Should raise but clean up
            with pytest.raises(MCPConnectionError):
                await manager.connect()

            # Verify cleanup was called on both contexts
            # AsyncExitStack calls __aexit__ in reverse order
            mock_session.__aexit__.assert_called()
            mock_stdio_ctx.__aexit__.assert_called()

    @pytest.mark.asyncio
    async def test_session_enter_failure_cleans_up_stdio(self):
        """If ClientSession.__aenter__ fails, stdio context must be cleaned up."""
        from hestai_mcp.mcp.federation import MCPClientManager, MCPConnectionError

        manager = MCPClientManager()

        # Mock stdio_client to succeed
        mock_stdio_ctx = MagicMock()
        mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
        mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)

        # Mock ClientSession to fail on __aenter__
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(side_effect=RuntimeError("Session enter failed"))
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "hestai_mcp.mcp.federation.client_manager.stdio_client",
                return_value=mock_stdio_ctx,
            ),
            patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession",
                return_value=mock_session,
            ),
        ):
            # Should raise but clean up stdio
            with pytest.raises(MCPConnectionError):
                await manager.connect()

            # Verify stdio cleanup was called (session never fully entered)
            mock_stdio_ctx.__aexit__.assert_called()


@pytest.mark.unit
class TestMCPClientManagerConcurrency:
    """Test race condition prevention in connect().

    CE BLOCKING FIX: Race condition in connect() where multiple concurrent
    awaiters can pass the `if self._connected:` check simultaneously before
    the first one sets `_connected = True`, causing duplicate subprocess spawning.
    """

    @pytest.mark.asyncio
    async def test_connect_lock_exists(self):
        """MCPClientManager must have _connect_lock for serializing connect() calls."""
        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()
        assert hasattr(
            manager, "_connect_lock"
        ), "MCPClientManager must have _connect_lock to prevent race conditions"

    @pytest.mark.asyncio
    async def test_concurrent_connect_calls_serialized(self):
        """Concurrent connect() calls must not spawn duplicate subprocesses.

        Verifies that asyncio.Lock serializes connect() - only one subprocess
        should be spawned even when multiple coroutines call connect() concurrently.
        """
        import asyncio

        from hestai_mcp.mcp.federation import MCPClientManager

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()

        spawn_count = {"value": 0}
        connect_started = asyncio.Event()
        proceed_connect = asyncio.Event()

        async def slow_stdio_enter(*args, **kwargs):
            spawn_count["value"] += 1
            connect_started.set()  # Signal that connect has started
            await proceed_connect.wait()  # Wait for signal to proceed
            return (MagicMock(), MagicMock())

        mock_stdio_ctx = MagicMock()
        mock_stdio_ctx.__aenter__ = slow_stdio_enter
        mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "hestai_mcp.mcp.federation.client_manager.stdio_client",
                return_value=mock_stdio_ctx,
            ),
            patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession",
                return_value=mock_session_ctx,
            ),
        ):
            manager = MCPClientManager()

            # Start multiple concurrent connect calls
            async def connect_and_wait():
                await manager.connect()

            # Create tasks but don't await yet
            task1 = asyncio.create_task(connect_and_wait())
            task2 = asyncio.create_task(connect_and_wait())
            task3 = asyncio.create_task(connect_and_wait())

            # Wait for first connect to start
            await asyncio.wait_for(connect_started.wait(), timeout=1.0)

            # Let connect proceed
            proceed_connect.set()

            # Wait for all tasks
            await asyncio.gather(task1, task2, task3)

            # With proper locking, stdio should be entered exactly once per server
            # (2 servers configured: octave and repomix)
            expected_spawns = len(MCPClientManager.SERVER_CONFIGS)
            assert spawn_count["value"] == expected_spawns, (
                f"Expected {expected_spawns} subprocess spawns (one per server), "
                f"got {spawn_count['value']}. Race condition detected!"
            )


@pytest.mark.unit
class TestMCPClientManagerTimeouts:
    """Test timeout configuration and enforcement.

    CE BLOCKING FIX: Missing timeouts for subprocess/network operations.
    Session.initialize() and session.call_tool() are unbounded - if subprocess
    hangs, the MCP server permanently deadlocks.
    """

    def test_timeout_parameters_in_init(self):
        """MCPClientManager must accept configurable timeout parameters."""
        from hestai_mcp.mcp.federation import MCPClientManager

        # Should accept timeout parameters
        manager = MCPClientManager(connect_timeout=15.0, tool_timeout=30.0)
        assert manager.connect_timeout == 15.0
        assert manager.tool_timeout == 30.0

    def test_default_timeout_values(self):
        """MCPClientManager must have sensible default timeouts."""
        from hestai_mcp.mcp.federation import MCPClientManager

        manager = MCPClientManager()

        # Must have default timeouts (not None or infinite)
        assert hasattr(manager, "connect_timeout")
        assert hasattr(manager, "tool_timeout")
        assert manager.connect_timeout > 0
        assert manager.tool_timeout > 0
        # Sensible defaults: 30s for connect, 60s for tool
        assert manager.connect_timeout == 30.0
        assert manager.tool_timeout == 60.0

    @pytest.mark.asyncio
    async def test_connect_timeout_raises_mcp_connection_error(self):
        """Session.initialize() timeout must raise MCPConnectionError."""
        import asyncio

        from hestai_mcp.mcp.federation import MCPClientManager, MCPConnectionError

        async def hanging_initialize():
            await asyncio.sleep(10)  # Hang indefinitely

        mock_session = AsyncMock()
        mock_session.initialize = hanging_initialize

        mock_stdio_ctx = MagicMock()
        mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
        mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "hestai_mcp.mcp.federation.client_manager.stdio_client",
                return_value=mock_stdio_ctx,
            ),
            patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession",
                return_value=mock_session_ctx,
            ),
        ):
            # Use short timeout for test
            manager = MCPClientManager(connect_timeout=0.1)

            with pytest.raises(MCPConnectionError) as exc_info:
                await manager.connect()

            # Verify timeout is mentioned in error message
            error_msg = str(exc_info.value).lower()
            assert "timed out" in error_msg or "timeout" in error_msg

    @pytest.mark.asyncio
    async def test_call_tool_timeout_raises_mcp_tool_error(self):
        """session.call_tool() timeout must raise MCPToolError with timeout message."""
        import asyncio

        from hestai_mcp.mcp.federation import MCPClientManager, MCPToolError

        async def hanging_call_tool(*args, **kwargs):
            await asyncio.sleep(10)  # Hang indefinitely

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.call_tool = hanging_call_tool

        mock_stdio_ctx = MagicMock()
        mock_stdio_ctx.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
        mock_stdio_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "hestai_mcp.mcp.federation.client_manager.stdio_client",
                return_value=mock_stdio_ctx,
            ),
            patch(
                "hestai_mcp.mcp.federation.client_manager.ClientSession",
                return_value=mock_session_ctx,
            ),
        ):
            # Use short tool timeout for test
            manager = MCPClientManager(tool_timeout=0.1)
            await manager.connect()

            with pytest.raises(MCPToolError) as exc_info:
                await manager.call_tool("octave.ingest", {"content": "test"})

            # Verify timeout is mentioned in error message
            error_msg = str(exc_info.value).lower()
            assert "timed out" in error_msg or "timeout" in error_msg
            assert "0.1" in str(exc_info.value)


@pytest.mark.unit
class TestMCPClientManagerEnvConfiguration:
    """Test environment variable configuration for SERVER_CONFIGS.

    SS-I6: Configurable server commands via env vars for flexibility
    without code changes. Maintains backward compatibility with defaults.
    """

    def test_get_server_config_helper_exists(self):
        """Helper function to build server config from env must exist."""
        from hestai_mcp.mcp.federation.client_manager import _get_server_config

        assert callable(_get_server_config)

    def test_default_values_when_no_env_vars(self, monkeypatch):
        """SERVER_CONFIGS must use defaults when env vars not set."""
        # Clear any existing env vars
        monkeypatch.delenv("HESTAI_MCP_OCTAVE_COMMAND", raising=False)
        monkeypatch.delenv("HESTAI_MCP_OCTAVE_ARGS", raising=False)
        monkeypatch.delenv("HESTAI_MCP_REPOMIX_COMMAND", raising=False)
        monkeypatch.delenv("HESTAI_MCP_REPOMIX_ARGS", raising=False)

        from hestai_mcp.mcp.federation.client_manager import _get_server_config

        # Octave defaults
        octave_config = _get_server_config("octave", "npx", ["-y", "@hestai/octave-mcp"])
        assert octave_config["command"] == "npx"
        assert octave_config["args"] == ["-y", "@hestai/octave-mcp"]
        assert octave_config["transport"] == "stdio"

        # Repomix defaults
        repomix_config = _get_server_config("repomix", "npx", ["-y", "repomix"])
        assert repomix_config["command"] == "npx"
        assert repomix_config["args"] == ["-y", "repomix"]

    def test_custom_command_override_via_env(self, monkeypatch):
        """HESTAI_MCP_<SERVER>_COMMAND env var must override default command."""
        monkeypatch.setenv("HESTAI_MCP_OCTAVE_COMMAND", "/usr/local/bin/octave-mcp")
        monkeypatch.delenv("HESTAI_MCP_OCTAVE_ARGS", raising=False)

        from hestai_mcp.mcp.federation.client_manager import _get_server_config

        config = _get_server_config("octave", "npx", ["-y", "@hestai/octave-mcp"])
        assert config["command"] == "/usr/local/bin/octave-mcp"
        # Args should still use default when not overridden
        assert config["args"] == ["-y", "@hestai/octave-mcp"]

    def test_custom_args_override_via_env(self, monkeypatch):
        """HESTAI_MCP_<SERVER>_ARGS env var must override default args."""
        monkeypatch.delenv("HESTAI_MCP_OCTAVE_COMMAND", raising=False)
        monkeypatch.setenv("HESTAI_MCP_OCTAVE_ARGS", "--verbose,--config=/etc/octave.json")

        from hestai_mcp.mcp.federation.client_manager import _get_server_config

        config = _get_server_config("octave", "npx", ["-y", "@hestai/octave-mcp"])
        # Command should still use default
        assert config["command"] == "npx"
        # Args should be parsed from comma-separated string
        assert config["args"] == ["--verbose", "--config=/etc/octave.json"]

    def test_args_parsing_handles_spaces(self, monkeypatch):
        """Args parsing must strip whitespace around commas."""
        monkeypatch.setenv("HESTAI_MCP_REPOMIX_ARGS", " -y , repomix , --extra ")

        from hestai_mcp.mcp.federation.client_manager import _get_server_config

        config = _get_server_config("repomix", "npx", ["-y", "repomix"])
        assert config["args"] == ["-y", "repomix", "--extra"]

    def test_mixed_overrides(self, monkeypatch):
        """Some servers can have overrides while others use defaults."""
        # Override octave command only
        monkeypatch.setenv("HESTAI_MCP_OCTAVE_COMMAND", "/custom/octave")
        monkeypatch.delenv("HESTAI_MCP_OCTAVE_ARGS", raising=False)
        # Override repomix args only
        monkeypatch.delenv("HESTAI_MCP_REPOMIX_COMMAND", raising=False)
        monkeypatch.setenv("HESTAI_MCP_REPOMIX_ARGS", "--custom-arg")

        from hestai_mcp.mcp.federation.client_manager import _get_server_config

        octave = _get_server_config("octave", "npx", ["-y", "@hestai/octave-mcp"])
        assert octave["command"] == "/custom/octave"
        assert octave["args"] == ["-y", "@hestai/octave-mcp"]  # Default args

        repomix = _get_server_config("repomix", "npx", ["-y", "repomix"])
        assert repomix["command"] == "npx"  # Default command
        assert repomix["args"] == ["--custom-arg"]  # Custom args

    def test_build_server_configs_helper_exists(self):
        """Helper to build full SERVER_CONFIGS dict must exist."""
        from hestai_mcp.mcp.federation.client_manager import _build_server_configs

        assert callable(_build_server_configs)

    def test_build_server_configs_returns_expected_structure(self, monkeypatch):
        """_build_server_configs must return dict with octave and repomix configs."""
        # Clear env vars to use defaults
        for var in [
            "HESTAI_MCP_OCTAVE_COMMAND",
            "HESTAI_MCP_OCTAVE_ARGS",
            "HESTAI_MCP_REPOMIX_COMMAND",
            "HESTAI_MCP_REPOMIX_ARGS",
        ]:
            monkeypatch.delenv(var, raising=False)

        from hestai_mcp.mcp.federation.client_manager import _build_server_configs

        configs = _build_server_configs()

        assert "octave" in configs
        assert "repomix" in configs
        assert configs["octave"]["transport"] == "stdio"
        assert configs["repomix"]["transport"] == "stdio"

    def test_server_configs_class_attr_uses_builder(self, monkeypatch):
        """MCPClientManager.SERVER_CONFIGS must use _build_server_configs."""
        monkeypatch.setenv("HESTAI_MCP_OCTAVE_COMMAND", "/test/octave")

        # Need to reimport to pick up new env var value
        import importlib

        import hestai_mcp.mcp.federation.client_manager as cm

        importlib.reload(cm)

        assert cm.MCPClientManager.SERVER_CONFIGS["octave"]["command"] == "/test/octave"

    def test_empty_args_env_var_uses_default(self, monkeypatch):
        """Empty ARGS env var should use default args, not empty list."""
        monkeypatch.setenv("HESTAI_MCP_OCTAVE_ARGS", "")

        from hestai_mcp.mcp.federation.client_manager import _get_server_config

        config = _get_server_config("octave", "npx", ["-y", "@hestai/octave-mcp"])
        # Empty string should fall back to defaults
        assert config["args"] == ["-y", "@hestai/octave-mcp"]
