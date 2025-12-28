"""
Tests for HestAI MCP Server - Dual-Layer Context Architecture.

TDD Discipline:
1. RED: Write failing tests first
2. GREEN: Minimal implementation to pass
3. REFACTOR: Improve while tests pass

Coverage Targets:
- get_hub_path: 90%
- get_hub_version: 90%
- inject_system_governance: 90%
- list_tools: 100%
- call_tool: 80%
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# =============================================================================
# PHASE 2: get_hub_path tests
# =============================================================================


@pytest.mark.unit
class TestGetHubPath:
    """Test hub path discovery from bundled package."""

    def test_returns_hub_path_when_exists(self, tmp_path: Path):
        """Returns path to hub directory when it exists."""
        from hestai_mcp.mcp import server

        # Create a mock hub directory
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()

        # Mock __file__ to point to our test directory
        fake_server_file = tmp_path / "src" / "hestai_mcp" / "mcp" / "server.py"
        fake_server_file.parent.mkdir(parents=True)
        fake_server_file.touch()

        with patch.object(server, "__file__", str(fake_server_file)):
            # Now the hub path will be:
            # fake_server_file.parent.parent.parent.parent / "hub"
            # = tmp_path / "hub"
            result = server.get_hub_path()

        assert result == fake_hub

    def test_raises_file_not_found_when_hub_missing(self, tmp_path: Path):
        """Raises FileNotFoundError when hub directory doesn't exist."""
        from hestai_mcp.mcp import server

        # Mock __file__ to point to a location without hub
        fake_server_file = tmp_path / "src" / "hestai_mcp" / "mcp" / "server.py"
        fake_server_file.parent.mkdir(parents=True)
        fake_server_file.touch()
        # Note: We don't create the hub directory

        with (
            patch.object(server, "__file__", str(fake_server_file)),
            pytest.raises(FileNotFoundError, match="Bundled hub not found"),
        ):
            server.get_hub_path()


# =============================================================================
# PHASE 2: get_hub_version tests
# =============================================================================


@pytest.mark.unit
class TestGetHubVersion:
    """Test hub version reading from VERSION file."""

    def test_returns_version_from_file(self, tmp_path: Path):
        """Returns version string from VERSION file."""
        from hestai_mcp.mcp import server

        # Create hub with VERSION file
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        version_file = fake_hub / "VERSION"
        version_file.write_text("1.2.3\n")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            result = server.get_hub_version()

        assert result == "1.2.3"

    def test_returns_unknown_when_version_file_missing(self, tmp_path: Path):
        """Returns 'unknown' when VERSION file doesn't exist."""
        from hestai_mcp.mcp import server

        # Create hub without VERSION file
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            result = server.get_hub_version()

        assert result == "unknown"


# =============================================================================
# PHASE 2: inject_system_governance tests
# =============================================================================


@pytest.mark.unit
class TestInjectSystemGovernance:
    """Test system governance injection into .hestai-sys/."""

    def test_creates_hestai_sys_directory(self, tmp_path: Path):
        """Creates .hestai-sys/ directory if it doesn't exist."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create minimal hub structure
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        assert (project_root / ".hestai-sys").exists()
        assert (project_root / ".hestai-sys").is_dir()

    def test_copies_governance_directories(self, tmp_path: Path):
        """Copies governance, agents, library, templates from hub."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create hub with governance directories
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")

        for dir_name in ["governance", "agents", "library", "templates"]:
            source_dir = fake_hub / dir_name
            source_dir.mkdir()
            (source_dir / "test-file.md").write_text(f"Content from {dir_name}")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        # Verify directories were copied
        for dir_name in ["governance", "agents", "library", "templates"]:
            dest = project_root / ".hestai-sys" / dir_name
            assert dest.exists()
            assert (dest / "test-file.md").exists()
            assert (dest / "test-file.md").read_text() == f"Content from {dir_name}"

    def test_writes_version_marker(self, tmp_path: Path):
        """Writes .version file with hub version."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()

        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("2.0.0")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        version_marker = project_root / ".hestai-sys" / ".version"
        assert version_marker.exists()
        assert version_marker.read_text() == "2.0.0"

    def test_removes_existing_directories_before_copy(self, tmp_path: Path):
        """Removes existing directories to ensure clean copy."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()

        # Pre-create .hestai-sys with old content
        hestai_sys = project_root / ".hestai-sys"
        old_agents = hestai_sys / "agents"
        old_agents.mkdir(parents=True)
        (old_agents / "old-agent.md").write_text("Old content")

        # Create hub with new content
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        new_agents = fake_hub / "agents"
        new_agents.mkdir()
        (new_agents / "new-agent.md").write_text("New content")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        # Old file should be gone, new file should exist
        assert not (hestai_sys / "agents" / "old-agent.md").exists()
        assert (hestai_sys / "agents" / "new-agent.md").exists()


# =============================================================================
# PHASE 2: list_tools tests
# =============================================================================


@pytest.mark.unit
class TestListTools:
    """Test MCP tool listing."""

    @pytest.mark.asyncio
    async def test_returns_clock_in_tool_schema(self):
        """Returns clock_in tool with correct schema."""
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        # Find clock_in tool
        clock_in_tool = next((t for t in tools if t.name == "clock_in"), None)
        assert clock_in_tool is not None

        # Verify schema properties
        schema = clock_in_tool.inputSchema
        assert schema["type"] == "object"
        assert "role" in schema["properties"]
        assert "working_dir" in schema["properties"]
        assert "focus" in schema["properties"]
        assert "model" in schema["properties"]
        assert "role" in schema["required"]
        assert "working_dir" in schema["required"]

    @pytest.mark.asyncio
    async def test_returns_clock_out_tool_schema(self):
        """Returns clock_out tool with correct schema."""
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        # Find clock_out tool
        clock_out_tool = next((t for t in tools if t.name == "clock_out"), None)
        assert clock_out_tool is not None

        # Verify schema properties
        schema = clock_out_tool.inputSchema
        assert schema["type"] == "object"
        assert "session_id" in schema["properties"]
        assert "description" in schema["properties"]
        assert "session_id" in schema["required"]

    @pytest.mark.asyncio
    async def test_returns_two_tools(self):
        """Returns exactly two tools (clock_in and clock_out)."""
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        assert len(tools) == 2
        tool_names = {t.name for t in tools}
        assert tool_names == {"clock_in", "clock_out"}


# =============================================================================
# PHASE 2: call_tool tests
# =============================================================================


@pytest.mark.unit
class TestCallTool:
    """Test MCP tool execution routing."""

    @pytest.mark.asyncio
    async def test_routes_clock_in_correctly(self, tmp_path: Path):
        """Routes clock_in tool call to clock_in function."""
        from hestai_mcp.mcp.server import call_tool

        # Create minimal hestai structure
        project = tmp_path / "project"
        project.mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

        arguments = {
            "role": "test-role",
            "working_dir": str(project),
            "focus": "test-focus",
        }

        result = await call_tool("clock_in", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        # Parse the JSON response
        response_data = json.loads(result[0].text)
        assert "session_id" in response_data
        assert "context_paths" in response_data

    @pytest.mark.asyncio
    async def test_routes_clock_out_correctly(self, tmp_path: Path):
        """Routes clock_out tool call to clock_out function."""
        from hestai_mcp.mcp.server import call_tool

        # First create a session using clock_in
        project = tmp_path / "project"
        project.mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "sessions" / "archive").mkdir(parents=True)
        (project / ".hestai" / "context" / "state").mkdir(parents=True)

        # Create a session manually for testing
        session_id = "test-session-123"
        session_dir = project / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir()
        session_data = {
            "session_id": session_id,
            "role": "test-role",
            "working_dir": str(project),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Mock clock_out function to avoid complex dependencies
        with patch("hestai_mcp.mcp.server.clock_out", new_callable=AsyncMock) as mock_clock_out:
            mock_clock_out.return_value = {
                "status": "completed",
                "session_id": session_id,
                "archive_path": str(project / ".hestai" / "sessions" / "archive" / session_id),
            }

            # Change to project directory for test
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(project)
                arguments = {
                    "session_id": session_id,
                    "description": "Test session",
                }
                result = await call_tool("clock_out", arguments)
            finally:
                os.chdir(original_cwd)

        assert len(result) == 1
        assert result[0].type == "text"

        response_data = json.loads(result[0].text)
        assert response_data["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_raises_value_error_for_unknown_tool(self):
        """Raises ValueError for unknown tool name."""
        from hestai_mcp.mcp.server import call_tool

        with pytest.raises(ValueError, match="Unknown tool"):
            await call_tool("unknown_tool", {})

    @pytest.mark.asyncio
    async def test_clock_out_raises_when_session_not_found(self, tmp_path: Path):
        """Raises FileNotFoundError when session doesn't exist."""
        from hestai_mcp.mcp.server import call_tool

        # Create minimal structure but no session
        project = tmp_path / "project"
        project.mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(project)
            with pytest.raises(FileNotFoundError, match="Session.*not found"):
                await call_tool("clock_out", {"session_id": "nonexistent-session"})
        finally:
            os.chdir(original_cwd)
