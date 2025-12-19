"""
Tests for ClockIn MCP Tool - Session registration and initialization.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase)
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

Test Coverage:
- Session creation (UUID generation, directory structure)
- Context path resolution from .hestai/context/
- Focus conflict detection (warn on duplicate focus)
- Security validation (path traversal, role format)

Note: Worktree/anchor tests excluded - ADR-0007 uses direct .hestai/ structure
"""

import json
import uuid
from pathlib import Path

import pytest


@pytest.fixture
def mock_hestai_structure(tmp_path: Path) -> Path:
    """
    Create minimal .hestai directory structure for testing.

    Returns:
        Path to project root with .hestai directory
    """
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    hestai_dir = project_root / ".hestai"
    sessions_dir = hestai_dir / "sessions"
    active_dir = sessions_dir / "active"
    archive_dir = sessions_dir / "archive"
    context_dir = hestai_dir / "context"

    active_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    context_dir.mkdir(parents=True)

    return project_root


@pytest.mark.unit
class TestSessionCreation:
    """Test session directory creation and metadata."""

    def test_creates_session_directory_and_metadata(self, mock_hestai_structure: Path):
        """Creates session directory with session.json metadata."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="b2-implementation",
            model="claude-opus-4-5",
        )

        # Verify session_id is valid UUID
        session_id = result["session_id"]
        assert uuid.UUID(session_id)  # Raises if invalid

        # Verify session directory exists
        session_dir = mock_hestai_structure / ".hestai" / "sessions" / "active" / session_id
        assert session_dir.exists()

        # Verify session.json contains expected fields
        session_file = session_dir / "session.json"
        assert session_file.exists()

        session_data = json.loads(session_file.read_text())
        assert session_data["session_id"] == session_id
        assert session_data["role"] == "implementation-lead"
        assert session_data["working_dir"] == str(mock_hestai_structure)
        assert session_data["focus"] == "b2-implementation"
        assert session_data["model"] == "claude-opus-4-5"
        assert "started_at" in session_data
        assert "transcript_path" in session_data

    def test_uses_default_focus_when_not_provided(self, mock_hestai_structure: Path):
        """Defaults focus to 'general' when not specified."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
        )

        session_id = result["session_id"]
        session_file = (
            mock_hestai_structure / ".hestai" / "sessions" / "active" / session_id / "session.json"
        )
        session_data = json.loads(session_file.read_text())

        assert session_data["focus"] == "general"

    def test_handles_none_model_parameter(self, mock_hestai_structure: Path):
        """Handles None model parameter correctly."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            model=None,
        )

        session_id = result["session_id"]
        session_file = (
            mock_hestai_structure / ".hestai" / "sessions" / "active" / session_id / "session.json"
        )
        session_data = json.loads(session_file.read_text())

        assert session_data["model"] is None


@pytest.mark.unit
class TestContextPathResolution:
    """Test context path resolution from .hestai/context/."""

    def test_returns_context_paths_from_hestai_context(self, mock_hestai_structure: Path):
        """Returns context paths from .hestai/context/ directory."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        # Create some context files (.oct.md format)
        context_dir = mock_hestai_structure / ".hestai" / "context"
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("# Context")
        # Create a non-.oct.md file which should be excluded
        (context_dir / "SYSTEM-STATE.md").write_text("# State")

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
        )

        # Verify context_paths includes expected files
        context_paths = result["context_paths"]
        assert isinstance(context_paths, list)

        # Should include .oct.md files from context directory
        assert any("PROJECT-CONTEXT.oct.md" in path for path in context_paths)
        # Should NOT include regular .md files (only .oct.md)
        assert not any("SYSTEM-STATE.md" in path for path in context_paths)

    def test_handles_empty_context_directory(self, mock_hestai_structure: Path):
        """Returns empty list when .hestai/context/ has no files."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
        )

        # Should return empty list or minimal paths
        context_paths = result["context_paths"]
        assert isinstance(context_paths, list)


@pytest.mark.unit
class TestFocusConflictDetection:
    """Test focus conflict detection for concurrent sessions."""

    def test_detects_focus_conflict_with_active_session(self, mock_hestai_structure: Path):
        """Warns when another active session has the same focus."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        # Create first session with focus "b2-implementation"
        result1 = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="b2-implementation",
        )

        # Create second session with same focus
        result2 = clock_in(
            role="critical-engineer",
            working_dir=str(mock_hestai_structure),
            focus="b2-implementation",
        )

        # Second session should detect conflict
        assert result2["focus_conflict"] is not None
        conflict = result2["focus_conflict"]
        assert conflict["session_id"] == result1["session_id"]
        assert conflict["role"] == "implementation-lead"
        assert conflict["focus"] == "b2-implementation"

    def test_no_conflict_with_different_focus(self, mock_hestai_structure: Path):
        """No conflict when active sessions have different focus."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        # Create first session
        clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="b2-implementation",
        )

        # Create second session with different focus
        result2 = clock_in(
            role="critical-engineer",
            working_dir=str(mock_hestai_structure),
            focus="d2-architecture",
        )

        # Should not detect conflict
        assert result2["focus_conflict"] is None


@pytest.mark.unit
class TestSecurityValidation:
    """Test security validation for path traversal and role format."""

    def test_rejects_path_traversal_in_working_dir(self, mock_hestai_structure: Path):
        """Rejects working_dir with path traversal attempts."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Pp]ath traversal|[Ii]nvalid"):
            clock_in(
                role="implementation-lead",
                working_dir="../../../etc/passwd",
            )

    def test_rejects_invalid_role_format(self, mock_hestai_structure: Path):
        """Rejects role names containing path separators."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Ii]nvalid.*role|path separator"):
            clock_in(
                role="../../etc/passwd",
                working_dir=str(mock_hestai_structure),
            )

    def test_validates_working_dir_exists(self, tmp_path: Path):
        """Validates that working_dir exists."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        nonexistent_dir = tmp_path / "does_not_exist"

        with pytest.raises(FileNotFoundError, match="[Ww]orking.*director"):
            clock_in(
                role="implementation-lead",
                working_dir=str(nonexistent_dir),
            )

    def test_creates_sessions_directory_if_missing(self, tmp_path: Path):
        """Creates sessions directory if .hestai exists but sessions doesn't."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create .hestai but not sessions directory
        (project_root / ".hestai").mkdir()

        # Should auto-create sessions directory and succeed
        result = clock_in(
            role="implementation-lead",
            working_dir=str(project_root),
        )

        # Verify sessions directory was created
        assert (project_root / ".hestai" / "sessions" / "active").exists()
        assert "session_id" in result


@pytest.mark.unit
class TestResponseStructure:
    """Test response structure and required fields."""

    def test_returns_required_fields(self, mock_hestai_structure: Path):
        """Returns all required fields in response."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="b2-implementation",
            model="claude-opus-4-5",
        )

        # Verify required fields
        assert "session_id" in result
        assert "context_paths" in result
        assert "focus_conflict" in result

        # Verify types
        assert isinstance(result["session_id"], str)
        assert isinstance(result["context_paths"], list)
        assert result["focus_conflict"] is None or isinstance(result["focus_conflict"], dict)


@pytest.mark.unit
class TestRoleControlCharacterValidation:
    """Test role validation rejects control characters (security)."""

    def test_rejects_role_with_newline(self, mock_hestai_structure: Path):
        """Rejects role containing newline character (log forging prevention)."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Cc]ontrol.*character|[Ii]nvalid.*role"):
            clock_in(
                role="lead\nINJECTED",
                working_dir=str(mock_hestai_structure),
            )

    def test_rejects_role_with_carriage_return(self, mock_hestai_structure: Path):
        """Rejects role containing carriage return."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Cc]ontrol.*character|[Ii]nvalid.*role"):
            clock_in(
                role="lead\rINJECTED",
                working_dir=str(mock_hestai_structure),
            )

    def test_rejects_role_with_tab(self, mock_hestai_structure: Path):
        """Rejects role containing tab character."""
        from hestai_mcp.mcp.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Cc]ontrol.*character|[Ii]nvalid.*role"):
            clock_in(
                role="lead\tINJECTED",
                working_dir=str(mock_hestai_structure),
            )
