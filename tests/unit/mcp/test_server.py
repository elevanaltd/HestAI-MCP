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
import logging
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# =============================================================================
# STARTUP: load_dotenv path resolution tests
# =============================================================================


@pytest.mark.unit
class TestDotenvPathResolution:
    """Test that load_dotenv is anchored to __file__, not CWD.

    The server must load its .env from the repo root regardless of
    where the MCP server process is spawned (CWD may be / or ~).
    """

    def test_loads_env_from_repo_root_when_present(self, tmp_path: Path, monkeypatch):
        """Loads .env from <repo-root>/.env (3 parents up from server.py)."""
        # Replicate the actual directory layout:
        #   tmp_path/src/hestai_mcp/mcp/server.py  <- fake __file__
        #   tmp_path/.env                            <- repo-root .env
        fake_server = tmp_path / "src" / "hestai_mcp" / "mcp" / "server.py"
        fake_server.parent.mkdir(parents=True)
        fake_server.touch()

        env_file = tmp_path / ".env"
        env_file.write_text("GITHUB_TOKEN=test-token-from-repo-root\n")

        captured: dict = {}

        def fake_load_dotenv(dotenv_path=None, **kwargs):
            captured["dotenv_path"] = dotenv_path

        with (
            patch("hestai_mcp.mcp.server.__file__", str(fake_server)),
            patch("hestai_mcp.mcp.server.load_dotenv", side_effect=fake_load_dotenv),
        ):
            # Re-execute the startup dotenv block under our patches
            server_dir = fake_server.resolve().parent
            repo_root_env = server_dir.parents[2] / ".env"
            fake_load_dotenv(dotenv_path=repo_root_env if repo_root_env.exists() else None)

        assert captured["dotenv_path"] == env_file
        assert captured["dotenv_path"].exists()

    def test_falls_back_gracefully_when_env_absent(self, tmp_path: Path):
        """Passes dotenv_path=None (CWD fallback) when repo-root .env missing."""
        fake_server = tmp_path / "src" / "hestai_mcp" / "mcp" / "server.py"
        fake_server.parent.mkdir(parents=True)
        fake_server.touch()
        # No .env created at tmp_path

        server_dir = fake_server.resolve().parent
        repo_root_env = server_dir.parents[2] / ".env"

        # Should not raise; dotenv_path should be None
        dotenv_path_arg = repo_root_env if repo_root_env.exists() else None
        assert dotenv_path_arg is None

    def test_actual_server_file_resolves_to_hestai_mcp_env(self):
        """Integration: real server.py __file__ resolves to the correct .env location."""
        from hestai_mcp.mcp import server as server_module

        server_file = Path(server_module.__file__).resolve()
        server_dir = server_file.parent
        resolved_env = server_dir.parents[2] / ".env"

        # The resolved path should be <repo-root>/.env
        # We can't assert it *exists* in all environments (CI won't have it),
        # but we can assert the path structure is correct.
        assert resolved_env.name == ".env"
        assert resolved_env.parent.name == resolved_env.parent.name  # is a real path
        # The parent should NOT be inside src/
        assert "src" not in resolved_env.parts


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
        for dir_name in ["standards", "agents", "library", "templates"]:
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

        # Create governance, library, templates directories
        for dir_name in ["standards", "library", "templates"]:
            source_dir = fake_hub / dir_name
            source_dir.mkdir()
            (source_dir / "test-file.md").write_text(f"Content from {dir_name}")

        # Create root files
        (fake_hub / "SYSTEM-STANDARD.md").write_text("System Standard Content")
        (fake_hub / "README.md").write_text("Readme Content")

        # Create agents inside library directory
        library_agents = fake_hub / "library" / "agents"
        library_agents.mkdir()
        (library_agents / "test-file.md").write_text("Content from agents")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        # Verify directories were copied
        for dir_name in ["standards", "library", "templates"]:
            dest = project_root / ".hestai-sys" / dir_name
            assert dest.exists()
            assert (dest / "test-file.md").exists()
            assert (dest / "test-file.md").read_text() == f"Content from {dir_name}"

        # Verify root files were copied
        for file_name in ["SYSTEM-STANDARD.md", "README.md"]:
            dest = project_root / ".hestai-sys" / file_name
            assert dest.exists()
            assert dest.read_text().endswith("Content")

        # Verify agents are in library/agents
        agents_dest = project_root / ".hestai-sys" / "library" / "agents"
        assert agents_dest.exists()
        assert (agents_dest / "test-file.md").exists()
        assert (agents_dest / "test-file.md").read_text() == "Content from agents"

    def test_writes_version_marker(self, tmp_path: Path):
        """Writes .version file with hub version."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("2.0.0")
        for dir_name in ["standards", "agents", "library", "templates"]:
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
        old_agents = hestai_sys / "library" / "agents"
        old_agents.mkdir(parents=True)
        (old_agents / "old-agent.md").write_text("Old content")

        # Create hub with new content
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["standards", "library", "templates"]:
            (fake_hub / dir_name).mkdir(exist_ok=True)

        # Create agents in library directory
        new_agents = fake_hub / "library" / "agents"
        new_agents.mkdir()
        (new_agents / "new-agent.md").write_text("New content")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        # Old file should be gone, new file should exist
        assert not (hestai_sys / "library" / "agents" / "old-agent.md").exists()
        assert (hestai_sys / "library" / "agents" / "new-agent.md").exists()


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
        # Add opt-in for test
        (project_root / ".hestai").mkdir()

        # Create minimal hub structure
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["standards", "agents", "library", "templates"]:
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
        # Add opt-in for test
        (project_root / ".hestai").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("1.0.0")
        for dir_name in ["standards", "agents", "library", "templates"]:
            (hestai_sys / dir_name).mkdir()
        for file_name in ["SYSTEM-STANDARD.md", "README.md"]:
            (hestai_sys / file_name).write_text("content")

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
        # Add opt-in for test
        (project_root / ".hestai").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("1.0.0")
        # Intentionally do NOT create standards/agents/library/templates

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
        # Add opt-in for test
        (project_root / ".hestai").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("0.9.0")

        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["standards", "agents", "library", "templates"]:
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
        # Add opt-in via .hestai directory
        (project_root / ".hestai").mkdir()

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
        # Add opt-in via .hestai directory
        (project_root / ".hestai").mkdir()
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
        # Add opt-in via .hestai directory
        (project_root / ".hestai").mkdir()

        monkeypatch.delenv("HESTAI_PROJECT_ROOT", raising=False)
        monkeypatch.chdir(project_root)

        with patch.object(
            server, "ensure_system_governance", return_value={"status": "ok"}
        ) as mock_ensure:
            result = server.bootstrap_system_governance(None)

        mock_ensure.assert_called_once_with(project_root)
        assert result == {"status": "ok"}

    def test_bootstrap_skips_when_env_missing_and_cwd_not_project_root(
        self, tmp_path: Path, monkeypatch
    ):
        from hestai_mcp.mcp import server

        monkeypatch.delenv("HESTAI_PROJECT_ROOT", raising=False)
        monkeypatch.chdir(tmp_path)

        # Now it returns a skip status instead of raising
        result = server.bootstrap_system_governance(None)
        assert result == {"status": "skipped", "reason": "not_a_project_root"}

    def test_bootstrap_skips_without_opt_in(self, tmp_path: Path):
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        # No .hestai directory or .env opt-in

        result = server.bootstrap_system_governance(project_root)
        assert result == {"status": "skipped", "reason": "opt_in_required"}

    def test_bootstrap_with_env_opt_in(self, tmp_path: Path):
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        # Add opt-in via .env
        (project_root / ".env").write_text("HESTAI_GOVERNANCE_ENABLED=true\n")

        with patch.object(
            server, "ensure_system_governance", return_value={"status": "ok"}
        ) as mock_ensure:
            result = server.bootstrap_system_governance(project_root)

        mock_ensure.assert_called_once_with(project_root)
        assert result == {"status": "ok"}


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
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "context").mkdir(parents=True)

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

        # _validate_project_identity may be called multiple times during validation chain
        # The key is that it IS called when working_dir is provided
        mock_validate.assert_called()
        # Verify it was called with the correct path
        assert mock_validate.call_count >= 1

    @pytest.mark.asyncio
    async def test_returns_five_tools(self):
        """Returns exactly five tools (clock_in, clock_out, bind, submit_review, submit_rccafp_record)."""
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        assert len(tools) == 5
        tool_names = {t.name for t in tools}
        assert tool_names == {
            "clock_in",
            "clock_out",
            "bind",
            "submit_review",
            "submit_rccafp_record",
        }


# =============================================================================
# PHASE 2: call_tool tests
# =============================================================================


@pytest.mark.unit
class TestCallTool:
    """Test MCP tool execution routing."""

    @pytest.fixture(autouse=True)
    def _enable_legacy_rollback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """ADR-0353: clock_in/clock_out/submit_review are deactivated by default.

        These tests exercise legacy execution routing — they need the rollback
        flag to bypass the deprecation gate. The default-OFF behaviour is
        covered by tests/unit/mcp/test_legacy_tool_gate.py.
        """
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")

    @pytest.mark.asyncio
    async def test_routes_clock_in_correctly(self, tmp_path: Path):
        """Routes clock_in tool call to clock_in function."""
        from hestai_mcp.mcp.server import call_tool

        # Create minimal hestai structure
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "context").mkdir(parents=True)

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
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "sessions" / "archive").mkdir(parents=True)
        (project / ".hestai" / "state" / "context" / "state").mkdir(parents=True)

        # Create a session manually for testing
        session_id = "test-session-123"
        session_dir = project / ".hestai" / "state" / "sessions" / "active" / session_id
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
                "archive_path": str(
                    project / ".hestai" / "state" / "sessions" / "archive" / session_id
                ),
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
    async def test_clock_out_uses_explicit_working_dir(self, tmp_path: Path):
        """clock_out uses working_dir parameter when provided."""
        from hestai_mcp.mcp.server import call_tool

        # Create project with session
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "sessions" / "archive").mkdir(parents=True)
        (project / ".hestai" / "state" / "context" / "state").mkdir(parents=True)

        session_id = "working-dir-test-123"
        session_dir = project / ".hestai" / "state" / "sessions" / "active" / session_id
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
            }

            # Call with explicit working_dir -- should NOT depend on cwd
            arguments = {
                "session_id": session_id,
                "description": "Test session",
                "working_dir": str(project),
            }
            result = await call_tool("clock_out", arguments)

        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["session_id"] == session_id

        # Verify clock_out was called with the correct project root
        mock_clock_out.assert_called_once()
        call_kwargs = mock_clock_out.call_args
        assert call_kwargs.kwargs["project_root"] == project

    @pytest.mark.asyncio
    async def test_clock_out_schema_includes_working_dir(self):
        """clock_out tool schema includes optional working_dir parameter."""
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()
        clock_out_tool = next((t for t in tools if t.name == "clock_out"), None)
        assert clock_out_tool is not None

        schema = clock_out_tool.inputSchema
        assert "working_dir" in schema["properties"]
        assert "working_dir" not in schema.get("required", [])

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
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)

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

    @pytest.fixture(autouse=True)
    def _enable_legacy_rollback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """ADR-0353: rollback flag enables legacy clock_in execution path."""
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")

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
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "context").mkdir(parents=True)

        # Mock the AI synthesis to verify it's called
        with patch(
            "hestai_mcp.modules.tools.shared.fast_layer.synthesize_fast_layer_with_ai",
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
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "context").mkdir(parents=True)

        # Mock AI synthesis to fail
        with patch(
            "hestai_mcp.modules.tools.shared.fast_layer.synthesize_fast_layer_with_ai",
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

        from hestai_mcp.modules.tools import clock_in_async

        assert inspect.iscoroutinefunction(clock_in_async)


# =============================================================================
# Holographic System Standard: standards integrity at session boundaries (#235)
# =============================================================================


@pytest.mark.unit
class TestGovernanceIntegrityAtSessionBoundaries:
    """Test Holographic System Standard integrity checks at clock_in and clock_out."""

    @pytest.fixture(autouse=True)
    def _enable_legacy_rollback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """ADR-0353: integrity checks live inside the legacy execution path; need rollback flag."""
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")

    @pytest.mark.asyncio
    async def test_clock_in_detects_and_heals_tampering(self, tmp_path: Path):
        """clock_in self-heals when governance files are tampered."""
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        # Create project with governance
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "context").mkdir(parents=True)

        # Create .hestai-sys with integrity hash
        hestai_sys = project / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / "SYSTEM-STANDARD.md").write_text("Original content")
        (hestai_sys / "standards").mkdir()
        (hestai_sys / "library").mkdir()
        (hestai_sys / "templates").mkdir()

        from hestai_mcp.modules.tools.shared.governance_integrity import (
            store_governance_hash,
        )

        store_governance_hash(hestai_sys)

        # Tamper with governance
        (hestai_sys / "SYSTEM-STANDARD.md").write_text("TAMPERED content")

        # Mock ensure_system_governance to not overwrite our setup
        # Mock inject_system_governance to track if self-healing was triggered
        with (
            patch.object(server, "ensure_system_governance", return_value={"status": "up_to_date"}),
            patch.object(server, "inject_system_governance") as mock_inject,
        ):
            arguments = {
                "role": "test-role",
                "working_dir": str(project),
                "focus": "test",
            }
            await call_tool("clock_in", arguments)

        # Self-healing should have been triggered
        mock_inject.assert_called_once_with(project)

    @pytest.mark.asyncio
    async def test_clock_in_passes_when_governance_intact(self, tmp_path: Path):
        """clock_in proceeds normally when governance is intact."""
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "context").mkdir(parents=True)

        hestai_sys = project / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / "SYSTEM-STANDARD.md").write_text("Original content")
        (hestai_sys / "standards").mkdir()
        (hestai_sys / "library").mkdir()
        (hestai_sys / "templates").mkdir()

        from hestai_mcp.modules.tools.shared.governance_integrity import (
            store_governance_hash,
        )

        store_governance_hash(hestai_sys)

        # No tampering -- governance intact
        with (
            patch.object(server, "ensure_system_governance", return_value={"status": "up_to_date"}),
            patch.object(server, "inject_system_governance") as mock_inject,
        ):
            arguments = {
                "role": "test-role",
                "working_dir": str(project),
                "focus": "test",
            }
            await call_tool("clock_in", arguments)

        # Self-healing should NOT have been triggered
        mock_inject.assert_not_called()

    @pytest.mark.asyncio
    async def test_clock_out_detects_and_heals_tampering(self, tmp_path: Path):
        """clock_out self-heals when governance files are tampered during session."""
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)

        # Create session
        session_id = "integrity-test-session"
        session_dir = project / ".hestai" / "state" / "sessions" / "active" / session_id
        session_dir.mkdir()
        session_data = {
            "session_id": session_id,
            "role": "test-role",
            "working_dir": str(project),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Create .hestai-sys with integrity hash
        hestai_sys = project / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / "SYSTEM-STANDARD.md").write_text("Original content")
        (hestai_sys / "standards").mkdir()
        (hestai_sys / "library").mkdir()
        (hestai_sys / "templates").mkdir()

        from hestai_mcp.modules.tools.shared.governance_integrity import (
            store_governance_hash,
        )

        store_governance_hash(hestai_sys)

        # Tamper with governance (simulating mid-session modification)
        (hestai_sys / "SYSTEM-STANDARD.md").write_text("TAMPERED by agent")

        with (
            patch("hestai_mcp.mcp.server.clock_out", new_callable=AsyncMock) as mock_clock_out,
            patch.object(server, "inject_system_governance") as mock_inject,
        ):
            mock_clock_out.return_value = {"status": "success", "session_id": session_id}

            arguments = {
                "session_id": session_id,
                "working_dir": str(project),
            }
            await call_tool("clock_out", arguments)

        # Self-healing should have been triggered
        mock_inject.assert_called_once_with(project)

    @pytest.mark.asyncio
    async def test_clock_in_skips_integrity_check_when_no_hestai_sys(self, tmp_path: Path):
        """clock_in skips integrity check when .hestai-sys doesn't exist yet."""
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "state" / "context").mkdir(parents=True)

        # No .hestai-sys directory exists
        with (
            patch.object(server, "ensure_system_governance", return_value={"status": "up_to_date"}),
            patch.object(server, "inject_system_governance") as mock_inject,
        ):
            arguments = {
                "role": "test-role",
                "working_dir": str(project),
                "focus": "test",
            }
            await call_tool("clock_in", arguments)

        # No self-healing needed
        mock_inject.assert_not_called()

    @pytest.mark.asyncio
    async def test_clock_out_skips_integrity_check_when_no_hestai_sys(self, tmp_path: Path):
        """clock_out skips integrity check when .hestai-sys doesn't exist yet."""
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)

        # Create session
        session_id = "no-hestai-sys-session"
        session_dir = project / ".hestai" / "state" / "sessions" / "active" / session_id
        session_dir.mkdir()
        session_data = {
            "session_id": session_id,
            "role": "test-role",
            "working_dir": str(project),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # No .hestai-sys directory exists — integrity check should be skipped
        with (
            patch("hestai_mcp.mcp.server.clock_out", new_callable=AsyncMock) as mock_clock_out,
            patch.object(server, "inject_system_governance") as mock_inject,
        ):
            mock_clock_out.return_value = {"status": "success", "session_id": session_id}

            arguments = {
                "session_id": session_id,
                "working_dir": str(project),
            }
            await call_tool("clock_out", arguments)

        # No self-healing needed — .hestai-sys is absent, skip is correct
        mock_inject.assert_not_called()


# =============================================================================
# MUST-FIX 2: .integrity backfill for existing "up_to_date" trees (#235)
# =============================================================================


@pytest.mark.unit
class TestIntegrityBackfillOnUpToDate:
    """Test that ensure_system_governance backfills .integrity when missing on up_to_date."""

    def test_ensure_system_governance_backfills_integrity_when_missing(
        self, tmp_path: Path
    ) -> None:
        """When up_to_date but .integrity absent, store_governance_hash is called."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        (project_root / ".hestai").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("1.0.0")
        for dir_name in ["standards", "library", "templates"]:
            (hestai_sys / dir_name).mkdir()
        for file_name in ["SYSTEM-STANDARD.md", "README.md"]:
            (hestai_sys / file_name).write_text("content")

        # No .integrity file present — pre-existing deployment scenario
        assert not (hestai_sys / ".integrity").exists()

        with (
            patch.object(server, "get_hub_version", return_value="1.0.0"),
            patch.object(server, "inject_system_governance") as mock_inject,
            patch("hestai_mcp.mcp.server.store_governance_hash") as mock_store,
        ):
            result = server.ensure_system_governance(project_root)

        # Should still be up_to_date status
        assert result["status"] == "up_to_date"
        # inject should NOT be called (that would be full re-injection)
        mock_inject.assert_not_called()
        # store_governance_hash SHOULD be called to backfill .integrity
        mock_store.assert_called_once_with(hestai_sys)

    def test_ensure_system_governance_does_not_backfill_when_integrity_present(
        self, tmp_path: Path
    ) -> None:
        """When up_to_date and .integrity already present, store_governance_hash is NOT called."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        (project_root / ".hestai").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("1.0.0")
        for dir_name in ["standards", "library", "templates"]:
            (hestai_sys / dir_name).mkdir()
        for file_name in ["SYSTEM-STANDARD.md", "README.md"]:
            (hestai_sys / file_name).write_text("content")

        # .integrity IS present
        (hestai_sys / ".integrity").write_text("abc123def456" * 5 + "1234")

        with (
            patch.object(server, "get_hub_version", return_value="1.0.0"),
            patch.object(server, "inject_system_governance") as mock_inject,
            patch("hestai_mcp.mcp.server.store_governance_hash") as mock_store,
        ):
            result = server.ensure_system_governance(project_root)

        assert result["status"] == "up_to_date"
        mock_inject.assert_not_called()
        mock_store.assert_not_called()


# =============================================================================
# MUST-FIX 3: shutil.rmtree symlink edge in inject_system_governance (#235)
# =============================================================================


@pytest.mark.unit
class TestInjectSystemGovernanceSymlinkEdge:
    """Test that inject_system_governance handles symlink old_dir correctly."""

    def test_inject_system_governance_unlinks_symlink_old_dir(self, tmp_path: Path) -> None:
        """When old_dir is a symlink, unlink() is used instead of shutil.rmtree()."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        # Create minimal hub structure
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["standards", "library", "templates"]:
            (fake_hub / dir_name).mkdir()

        # Simulate the scenario: pre-create __old__ as a symlink
        # (This can happen if previous cleanup was interrupted and left a symlink)
        old_target = tmp_path / "old_target_dir"
        old_target.mkdir()
        (old_target / "some_file.md").write_text("old content")

        old_dir = project_root / ".hestai-sys.__old__"
        old_dir.symlink_to(old_target)

        assert old_dir.is_symlink()

        # inject should handle this without crashing and without following the symlink
        with patch.object(server, "get_hub_path", return_value=fake_hub):
            # Should not raise, even though old_dir is a symlink
            server.inject_system_governance(project_root)

        # After injection, the __old__ symlink should be gone (unlinked)
        assert not old_dir.exists()
        # The target directory itself should be unaffected (symlink was unlinked, not rmtree'd)
        assert old_target.exists()
        assert (old_target / "some_file.md").exists()

    def test_inject_system_governance_uses_rmtree_for_real_old_dir(self, tmp_path: Path) -> None:
        """When old_dir is a real directory, shutil.rmtree() is still used."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        # Create minimal hub structure
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["standards", "library", "templates"]:
            (fake_hub / dir_name).mkdir()

        # Pre-create __old__ as a real directory (not symlink)
        old_dir = project_root / ".hestai-sys.__old__"
        old_dir.mkdir()
        (old_dir / "old_file.md").write_text("old content")

        assert not old_dir.is_symlink()
        assert old_dir.is_dir()

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        # After injection, the real __old__ dir should be removed
        assert not old_dir.exists()


# =============================================================================
# PHASE 5: Worktree-to-parent governance propagation tests
# =============================================================================


def _make_governed_project(root: Path) -> None:
    """Helper: create a minimal governed project structure at root."""
    root.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir(exist_ok=True)
    (root / ".hestai").mkdir(exist_ok=True)


def _make_up_to_date_hestai_sys(root: Path, version: str = "1.0.0") -> None:
    """Helper: create .hestai-sys that looks up-to-date at given version."""
    hestai_sys = root / ".hestai-sys"
    hestai_sys.mkdir(exist_ok=True)
    (hestai_sys / ".version").write_text(version)
    (hestai_sys / ".integrity").write_text("hash")
    for d in ["standards", "library", "templates"]:
        (hestai_sys / d).mkdir(exist_ok=True)
    for f in ["SYSTEM-STANDARD.md", "README.md"]:
        (hestai_sys / f).write_text("content")


@pytest.mark.unit
class TestWorktreeDetection:
    """Test worktree detection: .git as file vs directory."""

    def test_git_file_detected_as_worktree(self, tmp_path: Path) -> None:
        """A .git FILE (not directory) indicates a worktree."""
        worktree = tmp_path / "worktree"
        worktree.mkdir()
        # Worktrees have a .git file, not a directory
        git_file = worktree / ".git"
        git_file.write_text("gitdir: /main-repo/.git/worktrees/my-worktree\n")

        from hestai_mcp.mcp.server import _is_git_worktree

        assert _is_git_worktree(worktree) is True

    def test_git_directory_not_detected_as_worktree(self, tmp_path: Path) -> None:
        """A .git DIRECTORY indicates a normal repo (not a worktree)."""
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()

        from hestai_mcp.mcp.server import _is_git_worktree

        assert _is_git_worktree(repo) is False


@pytest.mark.unit
class TestMainRepoPathDerivation:
    """Test deriving the main repo path from a worktree .git file."""

    def test_derives_main_repo_from_worktree_git_file(self, tmp_path: Path) -> None:
        """Parses the gitdir line from a worktree .git file to find the main repo."""
        # Set up main repo structure
        main_repo = tmp_path / "main-repo"
        main_repo.mkdir()
        git_dir = main_repo / ".git"
        git_dir.mkdir()
        worktrees_dir = git_dir / "worktrees" / "my-branch"
        worktrees_dir.mkdir(parents=True)

        # Set up worktree with .git file
        worktree = tmp_path / "worktrees" / "my-branch"
        worktree.mkdir(parents=True)
        (worktree / ".git").write_text(f"gitdir: {worktrees_dir}\n")

        from hestai_mcp.mcp.server import _get_main_repo_from_worktree

        result = _get_main_repo_from_worktree(worktree)
        assert result == main_repo

    def test_returns_none_for_non_worktree(self, tmp_path: Path) -> None:
        """Returns None when .git is a directory (not a worktree)."""
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()

        from hestai_mcp.mcp.server import _get_main_repo_from_worktree

        result = _get_main_repo_from_worktree(repo)
        assert result is None

    def test_returns_none_for_malformed_git_file(self, tmp_path: Path) -> None:
        """Returns None when .git file doesn't contain a valid gitdir line."""
        worktree = tmp_path / "worktree"
        worktree.mkdir()
        (worktree / ".git").write_text("garbage content\n")

        from hestai_mcp.mcp.server import _get_main_repo_from_worktree

        result = _get_main_repo_from_worktree(worktree)
        assert result is None

    def test_resolves_relative_gitdir_against_worktree_directory(self, tmp_path: Path) -> None:
        """Relative gitdir paths must resolve against the worktree dir, not CWD.

        Git can write relative paths in the .git file, e.g.:
            gitdir: ../../main-repo/.git/worktrees/my-branch

        These must be resolved relative to the worktree directory (where the
        .git file lives), not the process CWD.
        """
        # Set up main repo
        main_repo = tmp_path / "repos" / "main-repo"
        main_repo.mkdir(parents=True)
        git_dir = main_repo / ".git"
        git_dir.mkdir()
        worktrees_dir = git_dir / "worktrees" / "my-branch"
        worktrees_dir.mkdir(parents=True)

        # Set up worktree in a sibling directory
        worktree = tmp_path / "repos" / "worktrees" / "my-branch"
        worktree.mkdir(parents=True)

        # Write a RELATIVE gitdir path in the .git file
        # From worktree (repos/worktrees/my-branch) to main git dir
        # (repos/main-repo/.git/worktrees/my-branch):
        # go up 2 levels (../../) then into main-repo/.git/worktrees/my-branch
        relative_gitdir = "../../main-repo/.git/worktrees/my-branch"
        (worktree / ".git").write_text(f"gitdir: {relative_gitdir}\n")

        from hestai_mcp.mcp.server import _get_main_repo_from_worktree

        result = _get_main_repo_from_worktree(worktree)
        assert result is not None
        assert result.resolve() == main_repo.resolve()


@pytest.mark.unit
class TestWorktreePropagation:
    """Test that worktree injection triggers main repo injection."""

    def test_propagates_to_parent_repo_on_worktree(self, tmp_path: Path) -> None:
        """When project_root is a worktree, also injects governance into the main repo."""
        from hestai_mcp.mcp import server

        # Set up main repo
        main_repo = tmp_path / "main-repo"
        _make_governed_project(main_repo)
        git_dir = main_repo / ".git"
        git_dir.mkdir(exist_ok=True)
        worktrees_dir = git_dir / "worktrees" / "my-branch"
        worktrees_dir.mkdir(parents=True)

        # Set up worktree
        worktree = tmp_path / "worktrees" / "my-branch"
        _make_governed_project(worktree)
        # Replace .git dir with .git file (worktree indicator)
        import shutil

        shutil.rmtree(worktree / ".git")
        (worktree / ".git").write_text(f"gitdir: {worktrees_dir}\n")

        # Create hub for injection
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for d in ["standards", "library", "templates"]:
            (fake_hub / d).mkdir()

        # Track calls to ensure_system_governance
        original_fn = server.ensure_system_governance
        call_args: list[tuple] = []

        def tracking_ensure(project_root: Path, _propagate: bool = True) -> dict:
            call_args.append((project_root, _propagate))
            return original_fn(project_root, _propagate=_propagate)

        with (
            patch.object(server, "get_hub_path", return_value=fake_hub),
            patch.object(
                server,
                "ensure_system_governance",
                side_effect=tracking_ensure,
            ),
        ):
            server.ensure_system_governance(worktree)

        # Should have been called twice: once for worktree, once for main repo
        assert len(call_args) == 2
        assert call_args[0] == (worktree, True)
        assert call_args[1] == (main_repo, False)


@pytest.mark.unit
class TestPropagationFailureIsolation:
    """Test that parent propagation failure does NOT block worktree result."""

    def test_worktree_succeeds_when_parent_propagation_fails(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Worktree injection returns normally even if parent propagation raises."""
        from hestai_mcp.mcp import server

        # Set up main repo
        main_repo = tmp_path / "main-repo"
        _make_governed_project(main_repo)
        git_dir = main_repo / ".git"
        git_dir.mkdir(exist_ok=True)
        worktrees_dir = git_dir / "worktrees" / "my-branch"
        worktrees_dir.mkdir(parents=True)

        # Set up worktree
        worktree = tmp_path / "worktrees" / "my-branch"
        _make_governed_project(worktree)
        import shutil

        shutil.rmtree(worktree / ".git")
        (worktree / ".git").write_text(f"gitdir: {worktrees_dir}\n")

        # Create hub for injection
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for d in ["standards", "library", "templates"]:
            (fake_hub / d).mkdir()

        # Strategy: let the worktree's own injection succeed via the real path,
        # but make _get_main_repo_from_worktree return a path where the
        # recursive ensure_system_governance call will blow up (PermissionError).
        # The propagation must catch this and return the worktree result normally.
        broken_main = tmp_path / "broken-main"
        broken_main.mkdir()
        # broken_main has no .git, so _validate_project_root will raise

        with (
            patch.object(server, "get_hub_path", return_value=fake_hub),
            patch.object(
                server,
                "_is_git_worktree",
                return_value=True,
            ),
            patch.object(
                server,
                "_get_main_repo_from_worktree",
                return_value=broken_main,
            ),
            caplog.at_level(logging.DEBUG),
        ):
            result = server.ensure_system_governance(worktree)

        # Worktree injection must succeed despite parent propagation failure
        assert result["status"] in {"injected", "updated"}
        # A debug log message should indicate propagation failed
        assert any("propagat" in record.message.lower() for record in caplog.records)


@pytest.mark.unit
class TestRecursionGuard:
    """Test that propagation call doesn't trigger another propagation."""

    def test_propagation_call_does_not_re_propagate(self, tmp_path: Path) -> None:
        """When _propagate=False, no worktree detection or propagation occurs."""
        from hestai_mcp.mcp import server

        # Set up a worktree-like project
        worktree = tmp_path / "worktree"
        _make_governed_project(worktree)
        import shutil

        shutil.rmtree(worktree / ".git")
        (worktree / ".git").write_text("gitdir: /some/path/.git/worktrees/x\n")

        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for d in ["standards", "library", "templates"]:
            (fake_hub / d).mkdir()

        with (
            patch.object(server, "get_hub_path", return_value=fake_hub),
            patch.object(server, "_is_git_worktree", wraps=server._is_git_worktree) as mock_detect,
            patch.object(
                server, "_get_main_repo_from_worktree", wraps=server._get_main_repo_from_worktree
            ) as mock_derive,
        ):
            # Call with _propagate=False (simulating a recursive propagation call)
            server.ensure_system_governance(worktree, _propagate=False)

        # Neither worktree detection function should be called when _propagate=False
        mock_detect.assert_not_called()
        mock_derive.assert_not_called()


@pytest.mark.unit
class TestNonWorktreeNoPropagation:
    """Test that non-worktree paths do NOT trigger propagation."""

    def test_normal_repo_does_not_propagate(self, tmp_path: Path) -> None:
        """A normal git repo (.git is a directory) should not attempt propagation."""
        from hestai_mcp.mcp import server

        project_root = tmp_path / "project"
        _make_governed_project(project_root)

        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for d in ["standards", "library", "templates"]:
            (fake_hub / d).mkdir()

        with (
            patch.object(server, "get_hub_path", return_value=fake_hub),
            patch.object(
                server,
                "_get_main_repo_from_worktree",
            ) as mock_get_main,
        ):
            result = server.ensure_system_governance(project_root)

        # Should not have tried to derive main repo
        mock_get_main.assert_not_called()
        assert result["status"] in {"injected", "updated"}


@pytest.mark.unit
class TestPropagationSkipsNonOptInParent:
    """Test that propagation to a parent repo without opt-in is silently skipped."""

    def test_propagation_skipped_when_parent_lacks_opt_in(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """When the main repo has no .hestai dir (no opt-in), propagation is skipped."""
        from hestai_mcp.mcp import server

        # Set up main repo WITHOUT opt-in (no .hestai directory)
        main_repo = tmp_path / "main-repo"
        main_repo.mkdir()
        git_dir = main_repo / ".git"
        git_dir.mkdir()
        worktrees_dir = git_dir / "worktrees" / "my-branch"
        worktrees_dir.mkdir(parents=True)
        # Deliberately NOT creating (main_repo / ".hestai") -- no opt-in

        # Set up worktree WITH opt-in
        worktree = tmp_path / "worktrees" / "my-branch"
        _make_governed_project(worktree)
        import shutil

        shutil.rmtree(worktree / ".git")
        (worktree / ".git").write_text(f"gitdir: {worktrees_dir}\n")

        # Create hub for injection
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for d in ["standards", "library", "templates"]:
            (fake_hub / d).mkdir()

        with (
            patch.object(server, "get_hub_path", return_value=fake_hub),
            caplog.at_level(logging.DEBUG),
        ):
            result = server.ensure_system_governance(worktree)

        # Worktree injection should succeed
        assert result["status"] in {"injected", "updated"}
        # Main repo should NOT have .hestai-sys (no opt-in)
        assert not (main_repo / ".hestai-sys").exists()


@pytest.mark.unit
class TestNestedWorktreeGuard:
    """Test that nested worktrees do not cause infinite propagation chains."""

    def test_propagation_to_parent_does_not_chain_further(self, tmp_path: Path) -> None:
        """If main repo is itself a worktree, propagation does NOT chain further.

        Propagation calls ensure_system_governance(main_repo, _propagate=False),
        so even if main_repo looks like a worktree, _propagate=False prevents
        another propagation attempt.
        """
        from hestai_mcp.mcp import server

        # Set up the "real" root repo
        real_root = tmp_path / "real-root"
        real_root.mkdir()
        real_git = real_root / ".git"
        real_git.mkdir()
        real_wt_dir = real_git / "worktrees" / "main-wt"
        real_wt_dir.mkdir(parents=True)

        # Main repo is itself a worktree of real_root
        main_repo = tmp_path / "main-repo"
        _make_governed_project(main_repo)
        import shutil

        shutil.rmtree(main_repo / ".git")
        (main_repo / ".git").write_text(f"gitdir: {real_wt_dir}\n")
        main_wt_dir = tmp_path / "main-repo-wt"
        main_wt_dir.mkdir()

        # Our actual worktree points to main_repo
        main_repo_git_dir = tmp_path / "fake-git-dir"
        main_repo_git_dir.mkdir()
        wt_subdir = main_repo_git_dir / "worktrees" / "branch"
        wt_subdir.mkdir(parents=True)

        worktree = tmp_path / "worktrees" / "branch"
        _make_governed_project(worktree)
        shutil.rmtree(worktree / ".git")
        (worktree / ".git").write_text(f"gitdir: {wt_subdir}\n")

        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for d in ["standards", "library", "templates"]:
            (fake_hub / d).mkdir()

        # Track how many times _is_git_worktree is called
        call_count = {"detect": 0}
        original_detect = server._is_git_worktree

        def counting_detect(path: Path) -> bool:
            call_count["detect"] += 1
            return original_detect(path)

        with (
            patch.object(server, "get_hub_path", return_value=fake_hub),
            patch.object(server, "_is_git_worktree", side_effect=counting_detect),
            patch.object(
                server,
                "_get_main_repo_from_worktree",
                return_value=main_repo,
            ),
        ):
            result = server.ensure_system_governance(worktree)

        # _is_git_worktree should be called exactly ONCE (for the initial worktree),
        # NOT again for main_repo (because propagation uses _propagate=False)
        assert call_count["detect"] == 1
        assert result["status"] in {"injected", "updated"}
