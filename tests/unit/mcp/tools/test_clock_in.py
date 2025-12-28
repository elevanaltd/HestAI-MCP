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


@pytest.mark.unit
class TestFASTLayerPopulation:
    """
    Test FAST layer population per ADR-0046 and ADR-0056.

    The FAST layer at .hestai/context/state/ should be dynamically
    populated during clock_in with session-specific context.
    """

    def test_clock_in_creates_state_directory(self, mock_hestai_structure: Path):
        """
        clock_in creates .hestai/context/state/ directory if not exists.

        ADR-0046: FAST layer is at .hestai/context/state/
        ADR-0056: clock_in must ensure this directory exists
        """
        from hestai_mcp.mcp.tools.clock_in import clock_in

        # Ensure state directory doesn't exist initially
        state_dir = mock_hestai_structure / ".hestai" / "context" / "state"
        assert not state_dir.exists()

        clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="test-fast-layer",
        )

        # State directory should be created
        assert state_dir.exists()
        assert state_dir.is_dir()

    def test_clock_in_populates_current_focus(self, mock_hestai_structure: Path):
        """
        clock_in populates current-focus.oct.md with session info.

        ADR-0056 format:
        ===CURRENT_FOCUS===
        META:
          TYPE::SESSION_FOCUS
          VELOCITY::HOURLY_DAILY
        SESSION:
          ID::"{session_id}"
          ROLE::{role}
          FOCUS::"{focus}"
          BRANCH::{branch}
          STARTED::"{timestamp}"
        ===END===
        """
        from hestai_mcp.mcp.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="b2-implementation",
        )

        current_focus_path = (
            mock_hestai_structure / ".hestai" / "context" / "state" / "current-focus.oct.md"
        )
        assert current_focus_path.exists()

        content = current_focus_path.read_text()

        # Verify OCTAVE structure
        assert "===CURRENT_FOCUS===" in content
        assert "META:" in content
        assert "TYPE::SESSION_FOCUS" in content
        assert "VELOCITY::HOURLY_DAILY" in content
        assert "SESSION:" in content
        assert f'ID::"{result["session_id"]}"' in content
        assert "ROLE::implementation-lead" in content
        assert 'FOCUS::"b2-implementation"' in content
        assert "STARTED::" in content
        assert "===END===" in content

    def test_clock_in_populates_checklist(self, mock_hestai_structure: Path):
        """
        clock_in populates checklist.oct.md with session task.

        ADR-0056 format includes current task and carried forward items.
        """
        from hestai_mcp.mcp.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="implement-fast-layer",
        )

        checklist_path = (
            mock_hestai_structure / ".hestai" / "context" / "state" / "checklist.oct.md"
        )
        assert checklist_path.exists()

        content = checklist_path.read_text()

        # Verify OCTAVE structure
        assert "===SESSION_CHECKLIST===" in content
        assert "META:" in content
        assert "TYPE::FAST_CHECKLIST" in content
        assert f'SESSION::"{result["session_id"]}"' in content
        assert 'CURRENT_TASK::"implement-fast-layer"' in content
        assert "===END===" in content

    def test_clock_in_preserves_blockers(self, mock_hestai_structure: Path):
        """
        clock_in preserves existing blockers from previous sessions.

        ADR-0056: Unresolved blockers should survive session transitions.
        """
        from hestai_mcp.mcp.tools.clock_in import clock_in

        # Create state directory with existing blocker
        state_dir = mock_hestai_structure / ".hestai" / "context" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)

        existing_blockers = """===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS
  VELOCITY::HOURLY_DAILY

ACTIVE:
  blocker_001:
    DESCRIPTION::"CI pipeline failing"
    SINCE::"2025-12-27T10:00:00Z"
    STATUS::UNRESOLVED

===END===
"""
        blockers_path = state_dir / "blockers.oct.md"
        blockers_path.write_text(existing_blockers)

        clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="test-blockers",
        )

        # Blockers file should still exist with preserved content
        assert blockers_path.exists()
        content = blockers_path.read_text()

        # Original blocker should be preserved
        assert 'DESCRIPTION::"CI pipeline failing"' in content
        assert "STATUS::UNRESOLVED" in content

    def test_clock_in_creates_blockers_file_if_missing(self, mock_hestai_structure: Path):
        """
        clock_in creates blockers.oct.md if it doesn't exist.
        """
        from hestai_mcp.mcp.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="test-new-blockers",
        )

        blockers_path = mock_hestai_structure / ".hestai" / "context" / "state" / "blockers.oct.md"
        assert blockers_path.exists()

        content = blockers_path.read_text()
        assert "===BLOCKERS===" in content
        assert "TYPE::FAST_BLOCKERS" in content
        assert f'SESSION::"{result["session_id"]}"' in content

    def test_clock_in_carries_forward_incomplete_checklist_items(self, mock_hestai_structure: Path):
        """
        clock_in carries forward incomplete items from previous checklist.

        ADR-0056: Incomplete tasks should be preserved across sessions.
        """
        from hestai_mcp.mcp.tools.clock_in import clock_in

        # Create state directory with existing checklist containing incomplete items
        state_dir = mock_hestai_structure / ".hestai" / "context" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)

        existing_checklist = """===SESSION_CHECKLIST===
META:
  TYPE::FAST_CHECKLIST
  VELOCITY::HOURLY_DAILY
  SESSION::"previous-session"

CURRENT_TASK::"previous-focus"

ITEMS:
  task_001::COMPLETED
  task_002::PENDING
  task_003::IN_PROGRESS

===END===
"""
        checklist_path = state_dir / "checklist.oct.md"
        checklist_path.write_text(existing_checklist)

        clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="new-session-focus",
        )

        content = checklist_path.read_text()

        # New session should have new current task
        assert 'CURRENT_TASK::"new-session-focus"' in content

        # Incomplete items should be carried forward
        assert "task_002::PENDING" in content or "CARRIED_FORWARD:" in content
        assert "task_003::IN_PROGRESS" in content or "CARRIED_FORWARD:" in content
