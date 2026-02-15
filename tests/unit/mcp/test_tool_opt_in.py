"""Test that MCP tools respect opt-in mechanism for governance injection."""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestToolOptInEnforcement:
    """Test that ensure_system_governance respects opt-in mechanism."""

    def test_ensure_governance_skips_without_opt_in(self, tmp_path: Path):
        """Test ensure_system_governance skips injection without opt-in."""
        from hestai_mcp.mcp import server

        # Create a git project without opt-in
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        # No .hestai directory or .env with opt-in

        result = server.ensure_system_governance(project_root)

        # Should skip without opt-in
        assert result["status"] == "skipped"
        assert result["reason"] == "opt_in_required"

        # Verify .hestai-sys was NOT created
        assert not (project_root / ".hestai-sys").exists()

    def test_ensure_governance_with_env_opt_in(self, tmp_path: Path):
        """Test ensure_system_governance injects with env opt-in."""
        from hestai_mcp.mcp import server

        # Create a git project WITH opt-in
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        (project_root / ".env").write_text("HESTAI_GOVERNANCE_ENABLED=true\n")

        # DON'T modify the real bundled hub VERSION file - just run the test
        # The actual VERSION content doesn't matter for this test

        result = server.ensure_system_governance(project_root)

        # Should inject governance with opt-in
        assert result["status"] == "injected"
        assert (project_root / ".hestai-sys").exists()
        assert (project_root / ".gitignore").exists()

    def test_ensure_governance_with_existing_hestai(self, tmp_path: Path):
        """Test ensure_system_governance works with existing .hestai."""
        from hestai_mcp.mcp import server

        # Create a project with existing .hestai
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        (project_root / ".hestai").mkdir()  # Existing HestAI project

        # DON'T modify the real bundled hub VERSION file - just run the test
        # The actual VERSION content doesn't matter for this test

        result = server.ensure_system_governance(project_root)

        # Should inject governance for existing HestAI projects
        assert result["status"] == "injected"
        assert (project_root / ".hestai-sys").exists()

    def test_bootstrap_skips_without_opt_in(self, tmp_path: Path):
        """Test bootstrap_system_governance skips without opt-in."""
        from hestai_mcp.mcp import server

        # Create a git project without opt-in
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()
        # No .hestai directory or .env with opt-in

        result = server.bootstrap_system_governance(project_root)

        # Should skip without opt-in
        assert result["status"] == "skipped"
        assert result["reason"] == "opt_in_required"
        assert not (project_root / ".hestai-sys").exists()
