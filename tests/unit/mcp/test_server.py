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
        """Returns path to bundled hub directory when it exists."""
        from hestai_mcp.mcp import server

        # Layout:
        #   tmp_path/src/hestai_mcp/mcp/server.py
        #   tmp_path/src/hestai_mcp/_bundled_hub/
        bundled_hub = tmp_path / "src" / "hestai_mcp" / "_bundled_hub"
        bundled_hub.mkdir(parents=True)

        fake_server_file = tmp_path / "src" / "hestai_mcp" / "mcp" / "server.py"
        fake_server_file.parent.mkdir(parents=True)
        fake_server_file.touch()

        with patch.object(server, "__file__", str(fake_server_file)):
            result = server.get_hub_path()

        assert result == bundled_hub

    def test_raises_file_not_found_when_hub_missing(self, tmp_path: Path):
        """Raises FileNotFoundError when bundled hub directory doesn't exist."""
        from hestai_mcp.mcp import server

        # Mock __file__ to point to a location without _bundled_hub
        fake_server_file = tmp_path / "src" / "hestai_mcp" / "mcp" / "server.py"
        fake_server_file.parent.mkdir(parents=True)
        fake_server_file.touch()

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

    def test_raises_when_version_file_missing(self, tmp_path: Path):
        """Raises FileNotFoundError when VERSION file doesn't exist (fail-closed)."""
        from hestai_mcp.mcp import server

        # Create hub without VERSION file
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()

        with (
            patch.object(server, "get_hub_path", return_value=fake_hub),
            pytest.raises(FileNotFoundError, match="VERSION"),
        ):
            server.get_hub_version()


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
        (project_root / ".git").mkdir()

        # Create minimal hub structure
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["governance", "agents", "library", "templates"]:
            (fake_hub / dir_name).mkdir()

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        assert (project_root / ".hestai-sys").exists()
        assert (project_root / ".hestai-sys").is_dir()

    def test_copies_governance_directories(self, tmp_path: Path):
        """Copies governance, agents, library, templates from hub."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

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
        (project_root / ".git").mkdir()

        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("2.0.0")
        for dir_name in ["governance", "agents", "library", "templates"]:
            (fake_hub / dir_name).mkdir()

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
        (project_root / ".git").mkdir()

        # Pre-create .hestai-sys with old content
        hestai_sys = project_root / ".hestai-sys"
        old_agents = hestai_sys / "agents"
        old_agents.mkdir(parents=True)
        (old_agents / "old-agent.md").write_text("Old content")

        # Create hub with new content
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["governance", "agents", "library", "templates"]:
            (fake_hub / dir_name).mkdir(exist_ok=True)
        new_agents = fake_hub / "agents"
        (new_agents / "new-agent.md").write_text("New content")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        # Old file should be gone, new file should exist
        assert not (hestai_sys / "agents" / "old-agent.md").exists()
        assert (hestai_sys / "agents" / "new-agent.md").exists()


# =============================================================================
# PHASE 2: ensure_system_governance tests
# =============================================================================


@pytest.mark.unit
class TestEnsureSystemGovernance:
    """Test idempotent system governance materialization into .hestai-sys/."""

    def test_injects_when_hestai_sys_missing(self, tmp_path: Path):
        """Injects hub into .hestai-sys when missing."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        # Create minimal hub structure
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["governance", "agents", "library", "templates"]:
            (fake_hub / dir_name).mkdir()

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            result = server.ensure_system_governance(project_root)

        assert result["status"] in {"injected", "updated"}
        assert (project_root / ".hestai-sys" / ".version").read_text() == "1.0.0"

    def test_noop_when_version_matches(self, tmp_path: Path):
        """Does nothing when .hestai-sys version matches hub version and required dirs exist."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("1.0.0")
        for dir_name in ["governance", "agents", "library", "templates"]:
            (hestai_sys / dir_name).mkdir()

        with (
            patch.object(server, "get_hub_version", return_value="1.0.0"),
            patch.object(server, "inject_system_governance") as mock_inject,
        ):
            result = server.ensure_system_governance(project_root)

        mock_inject.assert_not_called()
        assert result["status"] == "up_to_date"

    def test_reinjects_when_required_dirs_missing_even_if_version_matches(self, tmp_path: Path):
        """Re-injects if required subdirectories are missing (fail-closed integrity)."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("1.0.0")
        # Intentionally do NOT create governance/agents/library/templates

        with (
            patch.object(server, "get_hub_version", return_value="1.0.0"),
            patch.object(server, "inject_system_governance") as mock_inject,
        ):
            result = server.ensure_system_governance(project_root)

        mock_inject.assert_called_once_with(project_root)
        assert result["status"] == "updated"

    def test_reinjects_when_version_mismatched(self, tmp_path: Path):
        """Re-injects when hub version changes."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("0.9.0")

        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["governance", "agents", "library", "templates"]:
            (fake_hub / dir_name).mkdir()

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            result = server.ensure_system_governance(project_root)

        assert result["status"] == "updated"
        assert (project_root / ".hestai-sys" / ".version").read_text() == "1.0.0"


# =============================================================================
# PHASE 2: startup bootstrap tests
# =============================================================================


@pytest.mark.unit
class TestStartupBootstrap:
    def test_bootstrap_uses_explicit_project_root(self, tmp_path: Path):
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        with patch.object(
            server, "ensure_system_governance", return_value={"status": "ok"}
        ) as mock_ensure:
            result = server.bootstrap_system_governance(project_root)

        mock_ensure.assert_called_once_with(project_root)
        assert result == {"status": "ok"}

    def test_bootstrap_uses_env_when_project_root_not_provided(self, tmp_path: Path, monkeypatch):
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        monkeypatch.setenv("HESTAI_PROJECT_ROOT", str(project_root))

        with patch.object(
            server, "ensure_system_governance", return_value={"status": "ok"}
        ) as mock_ensure:
            result = server.bootstrap_system_governance(None)

        mock_ensure.assert_called_once_with(project_root)
        assert result == {"status": "ok"}

    def test_bootstrap_uses_cwd_when_env_missing_and_cwd_is_project_root(
        self, tmp_path: Path, monkeypatch
    ):
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        monkeypatch.delenv("HESTAI_PROJECT_ROOT", raising=False)
        monkeypatch.chdir(project_root)

        with patch.object(
            server, "ensure_system_governance", return_value={"status": "ok"}
        ) as mock_ensure:
            result = server.bootstrap_system_governance(None)

        mock_ensure.assert_called_once_with(project_root)
        assert result == {"status": "ok"}

    def test_bootstrap_raises_when_env_missing_and_cwd_not_project_root(
        self, tmp_path: Path, monkeypatch
    ):
        from hestai_mcp.mcp import server

        monkeypatch.delenv("HESTAI_PROJECT_ROOT", raising=False)
        monkeypatch.chdir(tmp_path)

        with pytest.raises(RuntimeError, match="HESTAI_PROJECT_ROOT"):
            server.bootstrap_system_governance(None)


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
    async def test_returns_bind_tool_schema(self):
        """Returns bind tool with correct schema."""
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        # Find bind tool
        bind_tool = next((t for t in tools if t.name == "bind"), None)
        assert bind_tool is not None

        # Verify schema properties
        schema = bind_tool.inputSchema
        assert schema["type"] == "object"
        assert "role" in schema["properties"]
        assert "topic" in schema["properties"]
        assert "tier" in schema["properties"]
        assert "working_dir" in schema["properties"]
        assert "role" in schema["required"]
        assert "topic" not in schema["required"]  # Optional with default
        assert "tier" not in schema["required"]  # Optional with default
        assert "working_dir" not in schema["required"]  # Optional

    @pytest.mark.asyncio
    async def test_bind_tool_validates_working_dir(self, tmp_path: Path):
        """Test that bind tool validates working_dir when provided."""
        from hestai_mcp.mcp.server import call_tool

        # Create minimal hestai structure
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

        # Bind without working_dir should work
        arguments = {
            "role": "technical-architect",
        }

        from hestai_mcp.mcp import server

        with patch.object(
            server, "ensure_system_governance", return_value={"status": "up_to_date"}
        ) as mock_ensure:
            result = await call_tool("bind", arguments)

        mock_ensure.assert_not_called()  # Should not be called without working_dir
        assert len(result) == 1
        assert result[0].type == "text"

        # Parse response
        response_data = json.loads(result[0].text)
        assert "success" in response_data

        # Bind with working_dir should call validate functions
        arguments_with_dir = {
            "role": "technical-architect",
            "working_dir": str(project),
        }

        with patch.object(server, "_validate_project_identity", return_value=None) as mock_validate:
            await call_tool("bind", arguments_with_dir)

        mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_four_tools(self):
        """Returns exactly four tools (clock_in, clock_out, odyssean_anchor, bind)."""
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        assert len(tools) == 4
        tool_names = {t.name for t in tools}
        assert tool_names == {"clock_in", "clock_out", "odyssean_anchor", "bind"}


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
        (project / ".git").mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

        arguments = {
            "role": "test-role",
            "working_dir": str(project),
            "focus": "test-focus",
        }

        from hestai_mcp.mcp import server

        with patch.object(
            server, "ensure_system_governance", return_value={"status": "up_to_date"}
        ) as mock_ensure:
            result = await call_tool("clock_in", arguments)

        mock_ensure.assert_called_once_with(project)

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
        (project / ".git").mkdir()
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


# =============================================================================
# PHASE 3: AI Synthesis Integration Tests (Issue #56 Rework)
# =============================================================================


@pytest.mark.unit
class TestMCPClockInAISynthesisIntegration:
    """
    Test that MCP tool surface triggers AI synthesis path.

    Per CRS gate feedback (BLOCK-1):
    - The MCP tool invocation must be able to trigger AI synthesis
    - CI-I3 requires AIClient.complete_text() to be reachable from runtime
    - The exported clock_in must use async path with AI synthesis capability
    """

    @pytest.mark.asyncio
    async def test_mcp_clock_in_calls_async_path_with_ai_synthesis(self, tmp_path: Path):
        """
        MCP call_tool("clock_in") invokes clock_in_async with AI synthesis.

        This test proves that:
        1. The MCP surface uses the async path (clock_in_async)
        2. AI synthesis is attempted when configured
        3. ai_synthesis field is present in response

        Per CRS BLOCK-1: The wiring gap between sync clock_in and async
        clock_in_async must be fixed.
        """
        from hestai_mcp.mcp.server import call_tool

        # Create minimal hestai structure
        project = tmp_path / "project"
        project.mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

        # Mock the AI synthesis to verify it's called
        with patch(
            "hestai_mcp.mcp.tools.shared.fast_layer.synthesize_fast_layer_with_ai",
            new_callable=AsyncMock,
        ) as mock_ai_synthesis:
            mock_ai_synthesis.return_value = {
                "synthesis": "Test AI synthesis result",
                "source": "ai",
            }

            arguments = {
                "role": "test-role",
                "working_dir": str(project),
                "focus": "test-focus",
            }

            result = await call_tool("clock_in", arguments)

            # Parse response
            response_data = json.loads(result[0].text)

            # CRITICAL: AI synthesis must be present in response
            # This proves the async path with AI is being used
            assert (
                "ai_synthesis" in response_data
            ), "ai_synthesis field missing - MCP surface is not using clock_in_async"
            assert response_data["ai_synthesis"]["source"] == "ai"

            # Verify AI synthesis function was called
            mock_ai_synthesis.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_clock_in_returns_ai_synthesis_fallback_on_failure(self, tmp_path: Path):
        """
        MCP clock_in gracefully falls back when AI synthesis fails.

        Per SS-I6: Graceful degradation is required.
        """
        from hestai_mcp.mcp.server import call_tool

        # Create minimal hestai structure
        project = tmp_path / "project"
        project.mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

        # Mock AI synthesis to fail
        with patch(
            "hestai_mcp.mcp.tools.shared.fast_layer.synthesize_fast_layer_with_ai",
            new_callable=AsyncMock,
            side_effect=Exception("AI service unavailable"),
        ):
            arguments = {
                "role": "test-role",
                "working_dir": str(project),
                "focus": "test-focus",
            }

            result = await call_tool("clock_in", arguments)

            # Parse response
            response_data = json.loads(result[0].text)

            # Should still succeed with fallback
            assert "session_id" in response_data
            assert "ai_synthesis" in response_data
            assert response_data["ai_synthesis"]["source"] == "fallback"

    @pytest.mark.asyncio
    async def test_mcp_clock_in_async_export_available(self):
        """
        clock_in_async is exported from tools module.

        Ensures the async function is discoverable and usable.
        """
        # Just verify it's importable and is a coroutine function
        import inspect

        from hestai_mcp.mcp.tools import clock_in_async

        assert inspect.iscoroutinefunction(clock_in_async)
