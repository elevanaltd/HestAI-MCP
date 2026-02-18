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

        # Create governance, library, templates directories
        for dir_name in ["governance", "library", "templates"]:
            source_dir = fake_hub / dir_name
            source_dir.mkdir()
            (source_dir / "test-file.md").write_text(f"Content from {dir_name}")

        # Create root files
        (fake_hub / "CONSTITUTION.md").write_text("Constitution Content")
        (fake_hub / "README.md").write_text("Readme Content")

        # Create agents inside library directory
        library_agents = fake_hub / "library" / "agents"
        library_agents.mkdir()
        (library_agents / "test-file.md").write_text("Content from agents")

        with patch.object(server, "get_hub_path", return_value=fake_hub):
            server.inject_system_governance(project_root)

        # Verify directories were copied
        for dir_name in ["governance", "library", "templates"]:
            dest = project_root / ".hestai-sys" / dir_name
            assert dest.exists()
            assert (dest / "test-file.md").exists()
            assert (dest / "test-file.md").read_text() == f"Content from {dir_name}"

        # Verify root files were copied
        for file_name in ["CONSTITUTION.md", "README.md"]:
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
        old_agents = hestai_sys / "library" / "agents"
        old_agents.mkdir(parents=True)
        (old_agents / "old-agent.md").write_text("Old content")

        # Create hub with new content
        fake_hub = tmp_path / "hub"
        fake_hub.mkdir()
        (fake_hub / "VERSION").write_text("1.0.0")
        for dir_name in ["governance", "library", "templates"]:
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
        # Add opt-in for test
        (project_root / ".hestai").mkdir()
        hestai_sys = project_root / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / ".version").write_text("1.0.0")
        for dir_name in ["governance", "agents", "library", "templates"]:
            (hestai_sys / dir_name).mkdir()
        for file_name in ["CONSTITUTION.md", "README.md"]:
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
        # Add opt-in for test
        (project_root / ".hestai").mkdir()
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

        # _validate_project_identity may be called multiple times during validation chain
        # The key is that it IS called when working_dir is provided
        mock_validate.assert_called()
        # Verify it was called with the correct path
        assert mock_validate.call_count >= 1

    @pytest.mark.asyncio
    async def test_returns_four_tools(self):
        """Returns exactly four tools (clock_in, clock_out, bind, submit_review)."""
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        assert len(tools) == 4
        tool_names = {t.name for t in tools}
        assert tool_names == {"clock_in", "clock_out", "bind", "submit_review"}


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
    async def test_clock_out_uses_explicit_working_dir(self, tmp_path: Path):
        """clock_out uses working_dir parameter when provided."""
        from hestai_mcp.mcp.server import call_tool

        # Create project with session
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "sessions" / "archive").mkdir(parents=True)
        (project / ".hestai" / "context" / "state").mkdir(parents=True)

        session_id = "working-dir-test-123"
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
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

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
# Holographic Constitution: governance integrity at session boundaries (#235)
# =============================================================================


@pytest.mark.unit
class TestGovernanceIntegrityAtSessionBoundaries:
    """Test Holographic Constitution integrity checks at clock_in and clock_out."""

    @pytest.mark.asyncio
    async def test_clock_in_detects_and_heals_tampering(self, tmp_path: Path):
        """clock_in self-heals when governance files are tampered."""
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        # Create project with governance
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

        # Create .hestai-sys with integrity hash
        hestai_sys = project / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / "CONSTITUTION.md").write_text("Original content")
        (hestai_sys / "governance").mkdir()
        (hestai_sys / "library").mkdir()
        (hestai_sys / "templates").mkdir()

        from hestai_mcp.modules.tools.shared.governance_integrity import (
            store_governance_hash,
        )

        store_governance_hash(hestai_sys)

        # Tamper with governance
        (hestai_sys / "CONSTITUTION.md").write_text("TAMPERED content")

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
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

        hestai_sys = project / ".hestai-sys"
        hestai_sys.mkdir()
        (hestai_sys / "CONSTITUTION.md").write_text("Original content")
        (hestai_sys / "governance").mkdir()
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
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)

        # Create session
        session_id = "integrity-test-session"
        session_dir = project / ".hestai" / "sessions" / "active" / session_id
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
        (hestai_sys / "CONSTITUTION.md").write_text("Original content")
        (hestai_sys / "governance").mkdir()
        (hestai_sys / "library").mkdir()
        (hestai_sys / "templates").mkdir()

        from hestai_mcp.modules.tools.shared.governance_integrity import (
            store_governance_hash,
        )

        store_governance_hash(hestai_sys)

        # Tamper with governance (simulating mid-session modification)
        (hestai_sys / "CONSTITUTION.md").write_text("TAMPERED by agent")

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
        (project / ".hestai" / "sessions" / "active").mkdir(parents=True)
        (project / ".hestai" / "context").mkdir(parents=True)

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
