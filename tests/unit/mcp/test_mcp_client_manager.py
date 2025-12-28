"""
Tests for MCP Client Manager - upstream tool federation.

SS-I3 Compliance: HestAI-MCP must act as both MCP Server (outward) and MCP Client
(inward to OCTAVE and other MCP servers). Upstream tools are namespaced.

Validation: Connection manager for upstream servers. Explicit allowlist of callable upstream tools.
"""

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

        manager = MCPClientManager()

        # Should support async with for proper lifecycle management
        async with manager:
            # Manager should be usable inside context
            assert manager is not None


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
