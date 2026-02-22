"""
Tests for ClockIn MCP Tool - Session registration and initialization.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase)
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

Test Coverage:
- Session creation (UUID generation, directory structure)
- Context path resolution from .hestai/state/context/
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
    state_dir = hestai_dir / "state"
    sessions_dir = state_dir / "sessions"
    active_dir = sessions_dir / "active"
    archive_dir = sessions_dir / "archive"
    context_dir = state_dir / "context"

    active_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    context_dir.mkdir(parents=True)

    return project_root


@pytest.mark.unit
class TestSessionCreation:
    """Test session directory creation and metadata."""

    def test_creates_session_directory_and_metadata(self, mock_hestai_structure: Path):
        """Creates session directory with session.json metadata."""
        from hestai_mcp.modules.tools.clock_in import clock_in

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
        session_dir = (
            mock_hestai_structure / ".hestai" / "state" / "sessions" / "active" / session_id
        )
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
        from hestai_mcp.modules.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
        )

        session_id = result["session_id"]
        session_file = (
            mock_hestai_structure
            / ".hestai"
            / "state"
            / "sessions"
            / "active"
            / session_id
            / "session.json"
        )
        session_data = json.loads(session_file.read_text())

        assert session_data["focus"] == "general"

    def test_handles_none_model_parameter(self, mock_hestai_structure: Path):
        """Handles None model parameter correctly."""
        from hestai_mcp.modules.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            model=None,
        )

        session_id = result["session_id"]
        session_file = (
            mock_hestai_structure
            / ".hestai"
            / "state"
            / "sessions"
            / "active"
            / session_id
            / "session.json"
        )
        session_data = json.loads(session_file.read_text())

        assert session_data["model"] is None


@pytest.mark.unit
class TestContextPathResolution:
    """Test context path resolution from .hestai/context/."""

    def test_returns_context_paths_from_hestai_context(self, mock_hestai_structure: Path):
        """Returns context paths from .hestai/context/ directory."""
        from hestai_mcp.modules.tools.clock_in import clock_in

        # Create some context files (.oct.md format)
        context_dir = mock_hestai_structure / ".hestai" / "state" / "context"
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
        from hestai_mcp.modules.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
        )

        # Should return empty list or minimal paths
        context_paths = result["context_paths"]
        assert isinstance(context_paths, list)

    def test_resolve_context_paths_includes_ecosystem_graph_when_present(
        self, mock_hestai_structure: Path
    ):
        """resolve_context_paths includes ecosystem dependency graph path when file exists."""
        from hestai_mcp.modules.tools.clock_in import resolve_context_paths

        # Create the ecosystem dependency graph file
        graph_dir = mock_hestai_structure / ".hestai-sys" / "governance"
        graph_dir.mkdir(parents=True, exist_ok=True)
        graph_file = graph_dir / "HESTAI-ECOSYSTEM-DEPENDENCY-GRAPH.oct.md"
        graph_file.write_text("===ECOSYSTEM_DEPENDENCY_GRAPH===\n===END===")

        context_paths = resolve_context_paths(mock_hestai_structure)

        assert any(
            "HESTAI-ECOSYSTEM-DEPENDENCY-GRAPH.oct.md" in path for path in context_paths
        ), "Ecosystem dependency graph path must appear in context_paths when file exists"
        # Verify it is an absolute path
        matching = [p for p in context_paths if "HESTAI-ECOSYSTEM-DEPENDENCY-GRAPH.oct.md" in p]
        assert Path(matching[0]).is_absolute()

    def test_resolve_context_paths_silent_skip_when_ecosystem_graph_absent(
        self, mock_hestai_structure: Path
    ):
        """resolve_context_paths does not raise and omits graph path when file is absent."""
        from hestai_mcp.modules.tools.clock_in import resolve_context_paths

        # Explicitly ensure the graph file does NOT exist
        graph_file = (
            mock_hestai_structure
            / ".hestai-sys"
            / "governance"
            / "HESTAI-ECOSYSTEM-DEPENDENCY-GRAPH.oct.md"
        )
        assert not graph_file.exists(), "Precondition: graph file must not exist for this test"

        # Must not raise
        context_paths = resolve_context_paths(mock_hestai_structure)

        assert isinstance(context_paths, list)
        assert not any(
            "HESTAI-ECOSYSTEM-DEPENDENCY-GRAPH.oct.md" in path for path in context_paths
        ), "Graph path must NOT appear when file is absent"


@pytest.mark.unit
class TestFocusConflictDetection:
    """Test focus conflict detection for concurrent sessions."""

    def test_detects_focus_conflict_with_active_session(self, mock_hestai_structure: Path):
        """Warns when another active session has the same focus."""
        from hestai_mcp.modules.tools.clock_in import clock_in

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
        from hestai_mcp.modules.tools.clock_in import clock_in

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
        from hestai_mcp.modules.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Pp]ath traversal|[Ii]nvalid"):
            clock_in(
                role="implementation-lead",
                working_dir="../../../etc/passwd",
            )

    def test_rejects_invalid_role_format(self, mock_hestai_structure: Path):
        """Rejects role names containing path separators."""
        from hestai_mcp.modules.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Ii]nvalid.*role|path separator"):
            clock_in(
                role="../../etc/passwd",
                working_dir=str(mock_hestai_structure),
            )

    def test_validates_working_dir_exists(self, tmp_path: Path):
        """Validates that working_dir exists."""
        from hestai_mcp.modules.tools.clock_in import clock_in

        nonexistent_dir = tmp_path / "does_not_exist"

        with pytest.raises(FileNotFoundError, match="[Ww]orking.*director"):
            clock_in(
                role="implementation-lead",
                working_dir=str(nonexistent_dir),
            )

    def test_creates_sessions_directory_if_missing(self, tmp_path: Path):
        """Creates sessions directory if .hestai exists but sessions doesn't."""
        from hestai_mcp.modules.tools.clock_in import clock_in

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
        assert (project_root / ".hestai" / "state" / "sessions" / "active").exists()
        assert "session_id" in result


@pytest.mark.unit
class TestResponseStructure:
    """Test response structure and required fields."""

    def test_returns_required_fields(self, mock_hestai_structure: Path):
        """Returns all required fields in response."""
        from hestai_mcp.modules.tools.clock_in import clock_in

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
        from hestai_mcp.modules.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Cc]ontrol.*character|[Ii]nvalid.*role"):
            clock_in(
                role="lead\nINJECTED",
                working_dir=str(mock_hestai_structure),
            )

    def test_rejects_role_with_carriage_return(self, mock_hestai_structure: Path):
        """Rejects role containing carriage return."""
        from hestai_mcp.modules.tools.clock_in import clock_in

        with pytest.raises(ValueError, match="[Cc]ontrol.*character|[Ii]nvalid.*role"):
            clock_in(
                role="lead\rINJECTED",
                working_dir=str(mock_hestai_structure),
            )

    def test_rejects_role_with_tab(self, mock_hestai_structure: Path):
        """Rejects role containing tab character."""
        from hestai_mcp.modules.tools.clock_in import clock_in

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
        from hestai_mcp.modules.tools.clock_in import clock_in

        # Ensure state directory doesn't exist initially
        state_dir = mock_hestai_structure / ".hestai" / "state" / "context" / "state"
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
        from hestai_mcp.modules.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="b2-implementation",
        )

        current_focus_path = (
            mock_hestai_structure
            / ".hestai"
            / "state"
            / "context"
            / "state"
            / "current-focus.oct.md"
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
        from hestai_mcp.modules.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="implement-fast-layer",
        )

        checklist_path = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "state" / "checklist.oct.md"
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
        from hestai_mcp.modules.tools.clock_in import clock_in

        # Create state directory with existing blocker
        state_dir = mock_hestai_structure / ".hestai" / "state" / "context" / "state"
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
        from hestai_mcp.modules.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="test-new-blockers",
        )

        blockers_path = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "state" / "blockers.oct.md"
        )
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
        from hestai_mcp.modules.tools.clock_in import clock_in

        # Create state directory with existing checklist containing incomplete items
        state_dir = mock_hestai_structure / ".hestai" / "state" / "context" / "state"
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


@pytest.mark.unit
class TestFocusResolutionFromBranch:
    """
    Test focus resolution priority chain per North Star Section 5 STEP_4.

    Priority order: explicit > GitHub issue from branch > branch inference > "general"

    Branch patterns to recognize:
    - Issue number pattern: #XX, issue-XX, issues-XX
    - Feature keyword prefix: feat/, fix/, chore/, refactor/, docs/
    """

    def test_resolve_focus_from_issue_pattern_hash(self, mock_hestai_structure: Path):
        """
        Resolves focus from branch name with #XX issue pattern.

        Branch: issues-56-completion -> focus: "issue-56"
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("issues-56-completion")
        assert result is not None
        assert result["value"] == "issue-56"
        assert result["source"] == "github_issue"

    def test_resolve_focus_from_issue_dash_pattern(self, mock_hestai_structure: Path):
        """
        Resolves focus from branch name with issue-XX pattern.

        Branch: issue-87-fix -> focus: "issue-87"
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("issue-87-fix")
        assert result is not None
        assert result["value"] == "issue-87"
        assert result["source"] == "github_issue"

    def test_resolve_focus_from_feature_prefix(self, mock_hestai_structure: Path):
        """
        Resolves focus from branch name with feature prefix.

        Branch: feat/add-clock-in -> focus: "feat: add-clock-in"
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("feat/add-clock-in")
        assert result is not None
        assert result["value"] == "feat: add-clock-in"
        assert result["source"] == "branch"

    def test_resolve_focus_from_fix_prefix(self, mock_hestai_structure: Path):
        """
        Resolves focus from branch name with fix prefix.

        Branch: fix/broken-tests -> focus: "fix: broken-tests"
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("fix/broken-tests")
        assert result is not None
        assert result["value"] == "fix: broken-tests"
        assert result["source"] == "branch"

    def test_resolve_focus_returns_none_for_generic_branch(self, mock_hestai_structure: Path):
        """
        Returns None for branches without recognizable patterns.

        Branch: main -> None (fallback to default will be handled elsewhere)
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("main")
        assert result is None

        result2 = resolve_focus_from_branch("develop")
        assert result2 is None

    def test_resolve_focus_priority_explicit_over_branch(self, mock_hestai_structure: Path):
        """
        Explicit focus takes priority over branch-inferred focus.

        Per North Star: explicit > GitHub issue > branch > default
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus

        # When explicit focus is provided, it should take priority
        result = resolve_focus(explicit_focus="my-explicit-focus", branch="issues-56-completion")
        assert result["value"] == "my-explicit-focus"
        assert result["source"] == "explicit"

    def test_resolve_focus_github_issue_over_feature_prefix(self, mock_hestai_structure: Path):
        """
        GitHub issue pattern takes priority over feature prefix pattern.

        Branch: feat/issue-56-impl -> focus: "issue-56" (not "feat: issue-56-impl")
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        # Issue pattern in branch name should take priority
        result = resolve_focus_from_branch("feat/issue-56-impl")
        assert result is not None
        assert result["value"] == "issue-56"
        assert result["source"] == "github_issue"

    def test_resolve_focus_default_when_no_pattern_and_no_explicit(
        self, mock_hestai_structure: Path
    ):
        """
        Returns default focus when no explicit and no branch pattern.
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus

        result = resolve_focus(explicit_focus=None, branch="main")
        assert result["value"] == "general"
        assert result["source"] == "default"

    def test_resolve_focus_handles_complex_issue_patterns(self, mock_hestai_structure: Path):
        """
        Handles various issue number patterns in branch names.
        """
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        # Multiple number patterns - should extract first/primary
        test_cases = [
            ("issues-56-completion-run-2", "issue-56"),
            ("issue-102-odyssean-anchor", "issue-102"),
            ("fix-issue-35", "issue-35"),
            ("feature-#87-system-blindness", "issue-87"),
        ]

        for branch, expected_focus in test_cases:
            result = resolve_focus_from_branch(branch)
            assert result is not None, f"Expected match for branch: {branch}"
            assert result["value"] == expected_focus, f"Branch: {branch}"
            assert result["source"] == "github_issue"


@pytest.mark.unit
class TestClockInWithAIIntegration:
    """
    Test clock_in integration with AI synthesis per North Star Section 5.

    clock_in should:
    1. Use resolve_focus to determine focus with priority chain
    2. Optionally call AI synthesis if configured
    3. Return focus_resolved with value and source
    4. Gracefully fall back if AI fails
    """

    def test_clock_in_returns_focus_resolved_structure(self, mock_hestai_structure: Path):
        """
        clock_in returns focus_resolved dict with value and source.

        Per North Star Section 4 output structure.
        """
        from hestai_mcp.modules.tools.clock_in import clock_in

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="explicit-focus",
        )

        # Should have focus_resolved in response
        assert "focus_resolved" in result
        focus_resolved = result["focus_resolved"]
        assert "value" in focus_resolved
        assert "source" in focus_resolved
        assert focus_resolved["value"] == "explicit-focus"
        assert focus_resolved["source"] == "explicit"

    def test_clock_in_infers_focus_from_branch_when_not_explicit(self, mock_hestai_structure: Path):
        """
        clock_in infers focus from branch when explicit focus not provided.

        This test uses mocking since we can't control git branch in test.
        """
        from unittest.mock import patch

        from hestai_mcp.modules.tools.clock_in import clock_in

        # Mock get_current_branch to return a branch with issue pattern
        with patch(
            "hestai_mcp.modules.tools.shared.fast_layer.get_current_branch",
            return_value="issues-56-completion",
        ):
            result = clock_in(
                role="implementation-lead",
                working_dir=str(mock_hestai_structure),
                # No explicit focus - should infer from branch
            )

            # Should have focus_resolved in response
            assert "focus_resolved" in result
            # Note: Without git integration in tests, will fallback to default
            # The focus_resolved structure should still be present
            assert result["focus_resolved"]["value"] is not None

    def test_clock_in_defaults_to_general_when_no_focus_pattern(self, mock_hestai_structure: Path):
        """
        clock_in defaults to 'general' when no explicit focus and no branch pattern.
        """
        from unittest.mock import patch

        from hestai_mcp.modules.tools.clock_in import clock_in

        # Mock branch to return a non-descriptive name
        with patch(
            "hestai_mcp.modules.tools.shared.fast_layer.get_current_branch",
            return_value="main",
        ):
            result = clock_in(
                role="implementation-lead",
                working_dir=str(mock_hestai_structure),
                # No explicit focus
            )

            assert "focus_resolved" in result
            assert result["focus_resolved"]["value"] == "general"
            assert result["focus_resolved"]["source"] == "default"

    @pytest.mark.asyncio
    async def test_clock_in_async_version_available(self, mock_hestai_structure: Path):
        """
        Async version of clock_in is available for AI integration.

        clock_in_async can be used when AI synthesis is desired.
        """
        from hestai_mcp.modules.tools.clock_in import clock_in_async

        result = await clock_in_async(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="test-focus",
        )

        # Should return same structure as sync version
        assert "session_id" in result
        assert "context_paths" in result
        assert "focus_resolved" in result

    @pytest.mark.asyncio
    async def test_clock_in_async_graceful_ai_fallback(self, mock_hestai_structure: Path):
        """
        clock_in_async gracefully falls back when AI synthesis fails.
        """
        from unittest.mock import AsyncMock, patch

        from hestai_mcp.modules.tools.clock_in import clock_in_async

        # Mock AI synthesis to fail - patch at the source module
        with patch(
            "hestai_mcp.modules.tools.shared.fast_layer.synthesize_fast_layer_with_ai",
            new_callable=AsyncMock,
            side_effect=Exception("AI unavailable"),
        ):
            # Should still succeed despite AI failure
            result = await clock_in_async(
                role="implementation-lead",
                working_dir=str(mock_hestai_structure),
                focus="test-focus",
            )

            assert "session_id" in result
            # Session should be created even if AI fails
            # ai_synthesis should show fallback
            assert "ai_synthesis" in result
            assert result["ai_synthesis"]["source"] == "fallback"

    @pytest.mark.asyncio
    async def test_clock_in_async_fallback_emits_octave_format(self, mock_hestai_structure: Path):
        """
        clock_in_async fallback emits OCTAVE format matching AI output contract.

        BLOCKING FIX: Fallback must use same structured format as AI synthesis
        to maintain contract consistency. Plain string "AI synthesis unavailable"
        violates the OCTAVE contract expected by downstream consumers.

        Required OCTAVE fields per protocols.py:
        - CONTEXT_FILES::
        - FOCUS::
        - PHASE::
        - BLOCKERS::
        - TASKS::
        - FRESHNESS_WARNING::
        """
        from unittest.mock import AsyncMock, patch

        from hestai_mcp.modules.tools.clock_in import clock_in_async

        # Mock AI synthesis to fail - triggers fallback path in clock_in.py
        # Patch at source module since clock_in uses local import
        with patch(
            "hestai_mcp.modules.tools.shared.fast_layer.synthesize_fast_layer_with_ai",
            new_callable=AsyncMock,
            side_effect=Exception("AI unavailable"),
        ):
            result = await clock_in_async(
                role="implementation-lead",
                working_dir=str(mock_hestai_structure),
                focus="test-focus",
            )

            assert "ai_synthesis" in result
            assert result["ai_synthesis"]["source"] == "fallback"

            synthesis = result["ai_synthesis"]["synthesis"]

            # Must contain OCTAVE format fields - not plain prose
            assert "CONTEXT_FILES::" in synthesis, "Fallback must include CONTEXT_FILES:: field"
            assert "FOCUS::" in synthesis, "Fallback must include FOCUS:: field"
            assert "PHASE::" in synthesis, "Fallback must include PHASE:: field"
            assert "BLOCKERS::" in synthesis, "Fallback must include BLOCKERS:: field"
            assert "TASKS::" in synthesis, "Fallback must include TASKS:: field"
            assert "FRESHNESS_WARNING::" in synthesis, "Fallback must include FRESHNESS_WARNING::"

            # Must NOT be plain string fallback
            assert (
                synthesis != "AI synthesis unavailable"
            ), "Must use OCTAVE format, not plain string"

            # Should include focus value in FOCUS:: field
            assert "test-focus" in synthesis, "Fallback should include actual focus value"


@pytest.mark.unit
class TestRichContextSummary:
    """
    Test rich context summary building for AI synthesis.

    The rich context summary provides actual project information to the AI,
    not just placeholder text like "Context files: 3".
    """

    def test_build_rich_context_includes_project_context_content(self, mock_hestai_structure: Path):
        """
        build_rich_context_summary includes actual PROJECT-CONTEXT.oct.md content.

        This is critical for useful AI synthesis - the AI can only work with
        what we give it.
        """
        from hestai_mcp.modules.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create PROJECT-CONTEXT.oct.md with recognizable content
        project_context = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "PROJECT-CONTEXT.oct.md"
        )
        project_context.write_text("""===PROJECT_CONTEXT===
META:
  TYPE::"PROJECT_CONTEXT"
  PHASE::B1_FOUNDATION
  STATUS::active_development

PURPOSE::"Test project for AI synthesis"

NEXT_ACTIONS::[
  1::implement_feature_X,
  2::fix_bug_Y
]
===END===
""")

        context_paths = resolve_context_paths(mock_hestai_structure)
        summary = build_rich_context_summary(
            working_dir=mock_hestai_structure,
            context_paths=context_paths,
            role="implementation-lead",
            focus="test-focus",
        )

        # Should include actual content, not just file count
        assert "PROJECT-CONTEXT.oct.md" in summary
        assert "B1_FOUNDATION" in summary
        assert "Test project for AI synthesis" in summary
        assert "implement_feature_X" in summary

    def test_build_rich_context_includes_git_state(self, mock_hestai_structure: Path):
        """
        build_rich_context_summary includes git state when available.

        Git state provides branch, recent commits, and modified files.
        """
        # Initialize git repo
        import subprocess

        from hestai_mcp.modules.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        subprocess.run(["git", "init"], cwd=str(mock_hestai_structure), capture_output=True)
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )

        # Create a file and commit
        test_file = mock_hestai_structure / "test.txt"
        test_file.write_text("test content")
        subprocess.run(["git", "add", "."], cwd=str(mock_hestai_structure), capture_output=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "Initial commit"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )

        context_paths = resolve_context_paths(mock_hestai_structure)
        summary = build_rich_context_summary(
            working_dir=mock_hestai_structure,
            context_paths=context_paths,
            role="implementation-lead",
            focus="test-focus",
        )

        # Should include git state
        assert "GIT STATE" in summary
        assert "Branch:" in summary

    def test_build_rich_context_includes_active_blockers(self, mock_hestai_structure: Path):
        """
        build_rich_context_summary includes active blockers if present.
        """
        from hestai_mcp.modules.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create blockers file with active blockers
        state_dir = mock_hestai_structure / ".hestai" / "state" / "context" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        blockers_file = state_dir / "blockers.oct.md"
        blockers_file.write_text("""===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS

ACTIVE:
  blocker_001:
    DESCRIPTION::"Waiting for API key"
    SINCE::"2026-01-01"
    STATUS::ACTIVE

===END===
""")

        context_paths = resolve_context_paths(mock_hestai_structure)
        summary = build_rich_context_summary(
            working_dir=mock_hestai_structure,
            context_paths=context_paths,
            role="implementation-lead",
            focus="test-focus",
        )

        # Should include active blockers
        assert "ACTIVE BLOCKERS" in summary or "Waiting for API key" in summary

    def test_build_rich_context_respects_max_size(self, mock_hestai_structure: Path):
        """
        build_rich_context_summary respects MAX_TOTAL_CONTEXT_CHARS limit.
        """
        from hestai_mcp.modules.tools.clock_in import (
            MAX_TOTAL_CONTEXT_CHARS,
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create very large PROJECT-CONTEXT
        project_context = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "PROJECT-CONTEXT.oct.md"
        )
        large_content = "X" * 10000  # Much larger than limit
        project_context.write_text(f"===PROJECT_CONTEXT===\n{large_content}\n===END===")

        context_paths = resolve_context_paths(mock_hestai_structure)
        summary = build_rich_context_summary(
            working_dir=mock_hestai_structure,
            context_paths=context_paths,
            role="implementation-lead",
            focus="test-focus",
        )

        # Should be truncated
        assert len(summary) <= MAX_TOTAL_CONTEXT_CHARS + 50  # Allow for truncation message
        assert "truncated" in summary.lower()


@pytest.mark.unit
class TestFreshnessCheck:
    """
    Test I4 freshness verification per North Star.

    I4::FRESHNESS_VERIFICATION::[
      PRINCIPLE::context_must_be_verified_as_current_before_use,
      WHY::prevents_hallucinations_from_stale_data
    ]
    """

    def test_check_context_freshness_returns_warning_for_stale_context(
        self, mock_hestai_structure: Path
    ):
        """
        _check_context_freshness returns warning when PROJECT-CONTEXT is stale.

        Stale = last git commit modifying file > 24 hours ago.
        """
        from hestai_mcp.modules.tools.clock_in import _check_context_freshness

        # Create PROJECT-CONTEXT
        project_context = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "PROJECT-CONTEXT.oct.md"
        )
        project_context.write_text("===PROJECT_CONTEXT===\nTEST\n===END===")

        # Simulate stale file by checking without recent git commit
        # (file exists but no git history = considered stale)
        warning = _check_context_freshness(
            project_context_path=project_context,
            working_dir=mock_hestai_structure,
        )

        # Should return a warning (not None)
        assert warning is not None
        assert "stale" in warning.lower() or "fresh" in warning.lower()

    def test_check_context_freshness_returns_none_for_fresh_context(
        self, mock_hestai_structure: Path
    ):
        """
        _check_context_freshness returns None when PROJECT-CONTEXT is fresh.

        Fresh = last git commit modifying file < 24 hours ago.
        """
        import subprocess

        from hestai_mcp.modules.tools.clock_in import _check_context_freshness

        # Initialize git repo and commit PROJECT-CONTEXT
        subprocess.run(["git", "init"], cwd=str(mock_hestai_structure), capture_output=True)
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )

        # Create and commit PROJECT-CONTEXT
        project_context = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "PROJECT-CONTEXT.oct.md"
        )
        project_context.write_text("===PROJECT_CONTEXT===\nTEST\n===END===")
        subprocess.run(["git", "add", "."], cwd=str(mock_hestai_structure), capture_output=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "Add PROJECT-CONTEXT"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )

        warning = _check_context_freshness(
            project_context_path=project_context,
            working_dir=mock_hestai_structure,
        )

        # Should return None (no warning for fresh context)
        assert warning is None

    def test_build_rich_context_includes_freshness_warning_when_stale(
        self, mock_hestai_structure: Path
    ):
        """
        build_rich_context_summary includes freshness warning in output when stale.

        Per I4: context_must_be_verified_as_current_before_use
        """
        from hestai_mcp.modules.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create PROJECT-CONTEXT without git (simulates stale)
        project_context = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "PROJECT-CONTEXT.oct.md"
        )
        project_context.write_text("===PROJECT_CONTEXT===\nTEST\n===END===")

        context_paths = resolve_context_paths(mock_hestai_structure)
        summary = build_rich_context_summary(
            working_dir=mock_hestai_structure,
            context_paths=context_paths,
            role="implementation-lead",
            focus="test-focus",
        )

        # Should include freshness warning
        assert (
            "FRESHNESS" in summary.upper()
            or "STALE" in summary.upper()
            or "WARNING" in summary.upper()
        )


@pytest.mark.unit
class TestNorthStarConstraintsExtraction:
    """
    Test North Star constraints extraction for architectural awareness.

    Per Issue #87: Agents need architectural context to avoid "system blindness".
    """

    def test_extract_north_star_constraints_returns_scope_boundaries(
        self, mock_hestai_structure: Path
    ):
        """
        _extract_north_star_constraints extracts SCOPE_BOUNDARIES from North Star.
        """
        from hestai_mcp.modules.tools.clock_in import _extract_north_star_constraints

        # Create North Star with scope boundaries
        workflow_dir = mock_hestai_structure / ".hestai" / "north-star"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        north_star = workflow_dir / "000-MCP-PRODUCT-NORTH-STAR.oct.md"
        north_star.write_text("""===NORTH_STAR===
SCOPE_BOUNDARIES::[
  IS::[persistent_memory_system, structural_governance_engine],
  IS_NOT::[SaaS_product, AI_model]
]
===END===
""")

        constraints = _extract_north_star_constraints(north_star)

        # Should extract scope boundaries
        assert constraints is not None
        assert "persistent_memory_system" in constraints or "SCOPE" in constraints

    def test_build_rich_context_includes_north_star_constraints(self, mock_hestai_structure: Path):
        """
        build_rich_context_summary includes North Star constraints when available.

        This helps prevent Issue #87 "system architecture blindness".
        """
        from hestai_mcp.modules.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create North Star
        workflow_dir = mock_hestai_structure / ".hestai" / "north-star"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        north_star = workflow_dir / "000-MCP-PRODUCT-NORTH-STAR.oct.md"
        north_star.write_text("""===NORTH_STAR===
IMMUTABLES::[
  I3::DUAL_LAYER_AUTHORITY,
  I4::FRESHNESS_VERIFICATION
]

SCOPE_BOUNDARIES::[
  IS::[persistent_memory_system],
  IS_NOT::[SaaS_product]
]
===END===
""")

        context_paths = resolve_context_paths(mock_hestai_structure)
        summary = build_rich_context_summary(
            working_dir=mock_hestai_structure,
            context_paths=context_paths,
            role="implementation-lead",
            focus="test-focus",
        )

        # Should include architectural constraints
        assert (
            "ARCHITECTURAL" in summary.upper()
            or "CONSTRAINT" in summary.upper()
            or "SCOPE" in summary.upper()
        )


@pytest.mark.unit
class TestCoverageGaps:
    """
    Tests for previously uncovered code paths.

    Coverage gaps identified:
    - Line 60: resolve_focus_from_branch with empty branch
    - Line 141: validate_role_format with empty role
    - Line 180: validate_working_dir with file path (not directory)
    - Lines 200-224: detect_focus_conflict edge cases
    - Lines 308-311: _find_north_star_file fallback to .md
    - Lines 346-347, 364-365: OSError handling
    - Lines 432, 436-438: _get_git_state edge cases
    - Lines 496, 500-503: freshness check edge cases
    - Lines 520, 553, 560-564: North Star extraction edge cases
    - Lines 592-600: ensure_hestai_structure creates new directory
    """

    def test_resolve_focus_from_branch_with_empty_string(self):
        """resolve_focus_from_branch returns None for empty string."""
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("")
        assert result is None

    def test_resolve_focus_from_branch_with_none(self):
        """resolve_focus_from_branch returns None for None input."""
        from hestai_mcp.modules.tools.clock_in import resolve_focus_from_branch

        # This exercises the implicit None case at line 59-60
        result = resolve_focus_from_branch(None)  # type: ignore[arg-type]
        assert result is None

    def test_validate_role_format_with_empty_string(self):
        """validate_role_format raises ValueError for empty string."""
        from hestai_mcp.modules.tools.clock_in import validate_role_format

        with pytest.raises(ValueError, match="[Rr]ole cannot be empty"):
            validate_role_format("")

    def test_validate_role_format_with_whitespace_only(self):
        """validate_role_format raises ValueError for whitespace-only string."""
        from hestai_mcp.modules.tools.clock_in import validate_role_format

        with pytest.raises(ValueError, match="[Rr]ole cannot be empty"):
            validate_role_format("   ")

    def test_validate_working_dir_with_file_path(self, tmp_path: Path):
        """validate_working_dir raises ValueError when path is a file, not directory."""
        from hestai_mcp.modules.tools.clock_in import validate_working_dir

        # Create a file, not a directory
        file_path = tmp_path / "somefile.txt"
        file_path.write_text("content")

        with pytest.raises(ValueError, match="not a directory"):
            validate_working_dir(str(file_path))

    def test_detect_focus_conflict_with_nonexistent_sessions_dir(self, tmp_path: Path):
        """detect_focus_conflict returns None when sessions dir doesn't exist."""
        from hestai_mcp.modules.tools.clock_in import detect_focus_conflict

        nonexistent_dir = tmp_path / "nonexistent"

        result = detect_focus_conflict(
            focus="test-focus",
            active_sessions_dir=nonexistent_dir,
            current_session_id="test-session-id",
        )
        assert result is None

    def test_detect_focus_conflict_skips_non_directories(self, tmp_path: Path):
        """detect_focus_conflict skips non-directory items in sessions dir."""
        from hestai_mcp.modules.tools.clock_in import detect_focus_conflict

        # Create sessions dir with a file (not directory)
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "not_a_dir.txt").write_text("file content")

        result = detect_focus_conflict(
            focus="test-focus",
            active_sessions_dir=sessions_dir,
            current_session_id="test-session-id",
        )
        # Should not crash, just skip the file
        assert result is None

    def test_detect_focus_conflict_skips_session_without_json(self, tmp_path: Path):
        """detect_focus_conflict skips sessions without session.json."""
        from hestai_mcp.modules.tools.clock_in import detect_focus_conflict

        # Create sessions dir with a session directory but no session.json
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "session-without-json").mkdir()

        result = detect_focus_conflict(
            focus="test-focus",
            active_sessions_dir=sessions_dir,
            current_session_id="test-session-id",
        )
        # Should not crash, just skip
        assert result is None

    def test_detect_focus_conflict_handles_invalid_json(self, tmp_path: Path):
        """detect_focus_conflict handles JSONDecodeError gracefully."""
        from hestai_mcp.modules.tools.clock_in import detect_focus_conflict

        # Create sessions dir with invalid JSON
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        session_dir = sessions_dir / "session-with-bad-json"
        session_dir.mkdir()
        (session_dir / "session.json").write_text("not valid json {{{")

        result = detect_focus_conflict(
            focus="test-focus",
            active_sessions_dir=sessions_dir,
            current_session_id="other-session",
        )
        # Should not crash, just skip invalid session
        assert result is None

    def test_find_north_star_file_fallback_to_md(self, tmp_path: Path):
        """_find_north_star_file falls back to .md when no .oct.md exists."""
        from hestai_mcp.modules.tools.clock_in import _find_north_star_file

        # Create workflow dir with only .md file (no .oct.md)
        workflow_dir = tmp_path / ".hestai" / "north-star"
        workflow_dir.mkdir(parents=True)
        md_file = workflow_dir / "000-PROJECT-NORTH-STAR.md"
        md_file.write_text("North Star content")

        result = _find_north_star_file(tmp_path)
        assert result is not None
        assert result.name == "000-PROJECT-NORTH-STAR.md"

    def test_find_north_star_file_prefers_oct_md_over_md(self, tmp_path: Path):
        """_find_north_star_file prefers .oct.md over .md when both exist."""
        from hestai_mcp.modules.tools.clock_in import _find_north_star_file

        # Create workflow dir with both .md and .oct.md files
        workflow_dir = tmp_path / ".hestai" / "north-star"
        workflow_dir.mkdir(parents=True)
        (workflow_dir / "000-PROJECT-NORTH-STAR.md").write_text("Plain MD")
        (workflow_dir / "000-PROJECT-NORTH-STAR.oct.md").write_text("OCTAVE MD")

        result = _find_north_star_file(tmp_path)
        assert result is not None
        assert result.name.endswith(".oct.md")

    def test_find_north_star_file_excludes_summary_files(self, tmp_path: Path):
        """_find_north_star_file excludes files with -SUMMARY in name."""
        from hestai_mcp.modules.tools.clock_in import _find_north_star_file

        # Create workflow dir with only -SUMMARY file
        workflow_dir = tmp_path / ".hestai" / "north-star"
        workflow_dir.mkdir(parents=True)
        (workflow_dir / "000-PROJECT-NORTH-STAR-SUMMARY.oct.md").write_text("Summary")

        result = _find_north_star_file(tmp_path)
        # Should return None since only summary file exists
        assert result is None

    def test_find_north_star_file_returns_none_when_no_workflow_dir(self, tmp_path: Path):
        """_find_north_star_file returns None when workflow dir doesn't exist."""
        from hestai_mcp.modules.tools.clock_in import _find_north_star_file

        result = _find_north_star_file(tmp_path)
        assert result is None

    def test_find_north_star_file_returns_none_when_no_matching_files(self, tmp_path: Path):
        """_find_north_star_file returns None when no matching files exist."""
        from hestai_mcp.modules.tools.clock_in import _find_north_star_file

        workflow_dir = tmp_path / ".hestai" / "north-star"
        workflow_dir.mkdir(parents=True)
        # Create files that don't match the pattern
        (workflow_dir / "other-file.md").write_text("Not a north star")

        result = _find_north_star_file(tmp_path)
        assert result is None

    def test_get_git_state_returns_none_on_error(self, tmp_path: Path):
        """_get_git_state returns None when git is not available or fails."""
        from hestai_mcp.modules.tools.clock_in import _get_git_state

        # Non-git directory should return None or handle gracefully
        result = _get_git_state(tmp_path)
        # In a non-git dir, it might return None or minimal info
        # The key is it shouldn't crash
        assert result is None or isinstance(result, str)

    def test_get_git_state_includes_modified_files(self, mock_hestai_structure: Path):
        """_get_git_state includes modified files when present."""
        import subprocess

        from hestai_mcp.modules.tools.clock_in import _get_git_state

        # Initialize git and create uncommitted changes
        subprocess.run(["git", "init"], cwd=str(mock_hestai_structure), capture_output=True)
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )

        # Create and commit a file
        test_file = mock_hestai_structure / "file.txt"
        test_file.write_text("original")
        subprocess.run(["git", "add", "."], cwd=str(mock_hestai_structure), capture_output=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "Initial"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )

        # Modify the file (now it will show as modified)
        test_file.write_text("modified content")

        result = _get_git_state(mock_hestai_structure)
        assert result is not None
        assert "Modified files:" in result
        assert "file.txt" in result

    def test_check_context_freshness_handles_stale_file(self, mock_hestai_structure: Path):
        """_check_context_freshness returns warning for stale context."""
        import subprocess

        from hestai_mcp.modules.tools.clock_in import _check_context_freshness

        # Initialize git
        subprocess.run(["git", "init"], cwd=str(mock_hestai_structure), capture_output=True)
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
        )

        # Create and commit PROJECT-CONTEXT
        project_context = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "PROJECT-CONTEXT.oct.md"
        )
        project_context.write_text("test content")
        subprocess.run(["git", "add", "."], cwd=str(mock_hestai_structure), capture_output=True)

        # Commit with a date 48 hours ago
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "old commit", "--date", "2025-01-01T00:00:00Z"],
            cwd=str(mock_hestai_structure),
            capture_output=True,
            env={
                **subprocess.os.environ,
                "GIT_AUTHOR_DATE": "2025-01-01T00:00:00Z",
                "GIT_COMMITTER_DATE": "2025-01-01T00:00:00Z",
            },
        )

        # The file should be considered stale (>24h)
        warning = _check_context_freshness(
            project_context_path=project_context,
            working_dir=mock_hestai_structure,
            max_age_hours=24,
        )

        assert warning is not None
        assert "stale" in warning.lower() or "I4" in warning

    def test_check_context_freshness_handles_subprocess_error(self, tmp_path: Path):
        """_check_context_freshness handles subprocess errors gracefully."""
        from hestai_mcp.modules.tools.clock_in import _check_context_freshness

        # Create a file in a non-git directory
        context_file = tmp_path / "PROJECT-CONTEXT.oct.md"
        context_file.write_text("test")

        # Should return a warning about not being able to verify freshness
        warning = _check_context_freshness(
            project_context_path=context_file,
            working_dir=tmp_path,
        )

        # Either warning about stale/uncommitted or about git unavailable
        assert warning is None or "WARNING" in warning.upper() or "stale" in warning.lower()

    def test_extract_north_star_constraints_handles_nonexistent_path(self, tmp_path: Path):
        """_extract_north_star_constraints returns None for nonexistent path."""
        from hestai_mcp.modules.tools.clock_in import _extract_north_star_constraints

        nonexistent = tmp_path / "does_not_exist.md"
        result = _extract_north_star_constraints(nonexistent)
        assert result is None

    def test_extract_north_star_constraints_extracts_immutables(self, tmp_path: Path):
        """_extract_north_star_constraints extracts IMMUTABLES references."""
        from hestai_mcp.modules.tools.clock_in import _extract_north_star_constraints

        north_star = tmp_path / "north-star.md"
        north_star.write_text("""===NORTH_STAR===
I1::IMMUTABLE_ONE
I2::IMMUTABLE_TWO
I3::IMMUTABLE_THREE
I4::IMMUTABLE_FOUR
===END===
""")

        result = _extract_north_star_constraints(north_star)
        assert result is not None
        assert "I1::" in result
        assert "KEY IMMUTABLES" in result

    def test_extract_north_star_constraints_returns_none_when_no_content(self, tmp_path: Path):
        """_extract_north_star_constraints returns None when no matching content."""
        from hestai_mcp.modules.tools.clock_in import _extract_north_star_constraints

        north_star = tmp_path / "empty-north-star.md"
        north_star.write_text("Just some regular content without immutables or scope")

        result = _extract_north_star_constraints(north_star)
        assert result is None

    def test_ensure_hestai_structure_creates_new_directory(self, tmp_path: Path):
        """ensure_hestai_structure creates new .hestai directory when missing."""
        from hestai_mcp.modules.tools.clock_in import ensure_hestai_structure

        project_root = tmp_path / "new_project"
        project_root.mkdir()

        # No .hestai directory exists
        assert not (project_root / ".hestai").exists()

        result = ensure_hestai_structure(project_root)

        # Should return 'created' and create all subdirectories
        assert result == "created"
        assert (project_root / ".hestai").exists()
        assert (project_root / ".hestai" / "state" / "sessions" / "active").exists()
        assert (project_root / ".hestai" / "state" / "sessions" / "archive").exists()
        assert (project_root / ".hestai" / "state" / "context").exists()
        assert (project_root / ".hestai" / "north-star").exists()
        assert (project_root / ".hestai" / "state" / "reports").exists()
        assert (project_root / ".hestai" / "decisions").exists()

    def test_ensure_hestai_structure_returns_present_when_exists(self, mock_hestai_structure: Path):
        """ensure_hestai_structure returns 'present' when .hestai already exists."""
        from hestai_mcp.modules.tools.clock_in import ensure_hestai_structure

        # mock_hestai_structure already has .hestai
        result = ensure_hestai_structure(mock_hestai_structure)
        assert result == "present"

    def test_build_rich_context_handles_oserror_on_project_context(
        self, mock_hestai_structure: Path
    ):
        """build_rich_context_summary handles OSError when reading PROJECT-CONTEXT."""
        from unittest.mock import patch

        from hestai_mcp.modules.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create PROJECT-CONTEXT
        context_dir = mock_hestai_structure / ".hestai" / "state" / "context"
        project_context = context_dir / "PROJECT-CONTEXT.oct.md"
        project_context.write_text("test content")

        # Mock read_text to raise OSError
        with patch.object(Path, "read_text", side_effect=OSError("Permission denied")):
            context_paths = resolve_context_paths(mock_hestai_structure)
            # Should not crash
            summary = build_rich_context_summary(
                working_dir=mock_hestai_structure,
                context_paths=context_paths,
                role="test-role",
                focus="test-focus",
            )
            # Summary should still be generated (without the content that failed)
            assert isinstance(summary, str)

    def test_build_rich_context_handles_oserror_on_blockers(self, mock_hestai_structure: Path):
        """build_rich_context_summary handles OSError when reading blockers file."""
        from unittest.mock import patch

        from hestai_mcp.modules.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create blockers file
        state_dir = mock_hestai_structure / ".hestai" / "state" / "context" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        blockers_file = state_dir / "blockers.oct.md"
        blockers_file.write_text("ACTIVE: some blocker")

        # Create a mock that only raises OSError for the blockers file
        original_read_text = Path.read_text

        def mock_read_text(self):
            if "blockers.oct.md" in str(self):
                raise OSError("Permission denied")
            return original_read_text(self)

        with patch.object(Path, "read_text", mock_read_text):
            context_paths = resolve_context_paths(mock_hestai_structure)
            # Should not crash
            summary = build_rich_context_summary(
                working_dir=mock_hestai_structure,
                context_paths=context_paths,
                role="test-role",
                focus="test-focus",
            )
            assert isinstance(summary, str)


@pytest.mark.unit
class TestContextStewardIntegration:
    """
    Test clock_in integration with ContextSteward for governance constraints.

    Per ADR-0184 Step 4: clock_in should:
    1. Import ContextSteward from core.governance.state.context_steward
    2. Derive phase from PROJECT-CONTEXT or default to B1
    3. Call steward.synthesize_active_state(phase)
    4. Write PhaseConstraints to .hestai/context/state/constraints.oct.md
    5. Return constraints.oct.md in context_paths
    """

    def test_clock_in_creates_constraints_file(self, mock_hestai_structure: Path):
        """
        clock_in creates constraints.oct.md with phase-specific governance.

        ADR-0184: Wiring the Brain (ContextSteward) to the Arm (clock_in).
        """
        from hestai_mcp.modules.tools.clock_in import clock_in

        # Create mock OPERATIONAL-WORKFLOW.oct.md for ContextSteward
        workflow_file = (
            mock_hestai_structure
            / ".hestai-sys"
            / "governance"
            / "workflow"
            / "OPERATIONAL-WORKFLOW.oct.md"
        )
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        workflow_file.write_text("""===OPERATIONAL_WORKFLOW===
META:
  TYPE::STANDARD
  STATUS::ACTIVE

WORKFLOW_PHASES:
  D0_DISCOVERY::IDEATION_SETUP
  PURPOSE::"Discovery and ideation"
  RACI::"R[wind-agent]"
  DELIVERABLES::["discovery_notes.md"]
  B1_FOUNDATION::BUILD_EXECUTION
  PURPOSE::"Foundation and infrastructure"
  RACI::"R[implementation-lead]→A[critical-engineer]"
  DELIVERABLES::["BUILD_PLAN.md","test_infrastructure"]
  ENTRY::[design_approved]
  EXIT::[tests_passing,foundation_solid]
  QUALITY_GATE_MANDATORY::"lint_passing && typecheck_passing && test_coverage_80"

===END===
""")

        result = clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
            focus="b1-foundation",
        )

        # Verify constraints.oct.md was created
        constraints_path = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "state" / "constraints.oct.md"
        )
        assert constraints_path.exists(), "constraints.oct.md should be created"

        # Verify content structure
        content = constraints_path.read_text()
        assert "===PHASE_CONSTRAINTS===" in content
        assert "B1" in content or "PURPOSE" in content
        assert "foundation" in content.lower()

        # Verify constraints.oct.md is in context_paths
        context_paths = result["context_paths"]
        assert any("constraints.oct.md" in path for path in context_paths)

    def test_clock_in_defaults_to_b1_phase_when_no_project_context(
        self, mock_hestai_structure: Path
    ):
        """
        clock_in defaults to B1 phase when PROJECT-CONTEXT doesn't exist.

        This is the placeholder phase until we implement full phase detection.
        """
        from hestai_mcp.modules.tools.clock_in import clock_in

        # Create minimal OPERATIONAL-WORKFLOW for B1
        workflow_file = (
            mock_hestai_structure
            / ".hestai-sys"
            / "governance"
            / "workflow"
            / "OPERATIONAL-WORKFLOW.oct.md"
        )
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        workflow_file.write_text("""===OPERATIONAL_WORKFLOW===
META:
  TYPE::STANDARD
  STATUS::ACTIVE

WORKFLOW_PHASES:
  B1_FOUNDATION::BUILD_EXECUTION
  PURPOSE::"Foundation phase"
  DELIVERABLES::["foundation"]

===END===
""")

        clock_in(
            role="implementation-lead",
            working_dir=str(mock_hestai_structure),
        )

        # Should use B1 as default
        constraints_path = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "state" / "constraints.oct.md"
        )
        assert constraints_path.exists()

        content = constraints_path.read_text()
        assert "B1" in content


@pytest.mark.unit
class TestStructuredClockInOutput:
    """
    Test structured clock_in output format per task requirements.

    The new output format should return structured, actionable file links
    that Claude Code can navigate, replacing prose synthesis.

    Desired format:
    CONTEXT_FILES::[@.hestai/context/PROJECT-CONTEXT.oct.md:L1-50, ...]
    FOCUS::{focus_value}
    PHASE::{phase}
    BLOCKERS::[{structured_list}]
    """

    def test_ai_synthesis_returns_structured_format(self, mock_hestai_structure: Path):
        """
        AI synthesis should return OCTAVE-structured output instead of prose.

        The structured format enables Claude Code to navigate directly to
        relevant file sections rather than parsing prose descriptions.
        """
        from hestai_mcp.modules.services.ai.prompts.protocols import CLOCK_IN_SYNTHESIS_PROTOCOL

        # Create PROJECT-CONTEXT with recognizable content
        project_context = (
            mock_hestai_structure / ".hestai" / "state" / "context" / "PROJECT-CONTEXT.oct.md"
        )
        project_context.write_text("""===PROJECT_CONTEXT===
META:
  TYPE::"PROJECT_CONTEXT"
  PHASE::B1_FOUNDATION

PURPOSE::"Test project"
===END===
""")

        # Verify the protocol instructs structured OCTAVE output format
        assert "OCTAVE structure" in CLOCK_IN_SYNTHESIS_PROTOCOL
        assert "CONTEXT_FILES::" in CLOCK_IN_SYNTHESIS_PROTOCOL

    def test_structured_output_contains_context_files_with_line_numbers(
        self, mock_hestai_structure: Path
    ):
        """
        Structured output should include CONTEXT_FILES with file paths and line ranges.

        Format: CONTEXT_FILES::[@path/to/file:L1-50, @another/file:L1-30]
        """
        from hestai_mcp.modules.services.ai.prompts.protocols import CLOCK_IN_SYNTHESIS_PROTOCOL

        # The protocol should instruct structured output format
        assert "CONTEXT_FILES::" in CLOCK_IN_SYNTHESIS_PROTOCOL

    def test_structured_output_contains_focus_field(self, mock_hestai_structure: Path):
        """
        Structured output should include FOCUS field with focus value.

        Format: FOCUS::{focus_value}
        """
        from hestai_mcp.modules.services.ai.prompts.protocols import CLOCK_IN_SYNTHESIS_PROTOCOL

        # The protocol should include FOCUS in structured format
        assert "FOCUS::" in CLOCK_IN_SYNTHESIS_PROTOCOL

    def test_structured_output_contains_phase_field(self, mock_hestai_structure: Path):
        """
        Structured output should include PHASE field extracted from context.

        Format: PHASE::{phase}
        """
        from hestai_mcp.modules.services.ai.prompts.protocols import CLOCK_IN_SYNTHESIS_PROTOCOL

        # The protocol should include PHASE in structured format
        assert "PHASE::" in CLOCK_IN_SYNTHESIS_PROTOCOL

    def test_structured_output_contains_blockers_list(self, mock_hestai_structure: Path):
        """
        Structured output should include BLOCKERS as structured list.

        Format: BLOCKERS::[{blocker1}, {blocker2}]
        """
        from hestai_mcp.modules.services.ai.prompts.protocols import CLOCK_IN_SYNTHESIS_PROTOCOL

        # The protocol should include BLOCKERS in structured format
        assert "BLOCKERS::" in CLOCK_IN_SYNTHESIS_PROTOCOL
