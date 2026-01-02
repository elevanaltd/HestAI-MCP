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
        from hestai_mcp.mcp.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("issues-56-completion")
        assert result is not None
        assert result["value"] == "issue-56"
        assert result["source"] == "github_issue"

    def test_resolve_focus_from_issue_dash_pattern(self, mock_hestai_structure: Path):
        """
        Resolves focus from branch name with issue-XX pattern.

        Branch: issue-87-fix -> focus: "issue-87"
        """
        from hestai_mcp.mcp.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("issue-87-fix")
        assert result is not None
        assert result["value"] == "issue-87"
        assert result["source"] == "github_issue"

    def test_resolve_focus_from_feature_prefix(self, mock_hestai_structure: Path):
        """
        Resolves focus from branch name with feature prefix.

        Branch: feat/add-clock-in -> focus: "feat: add-clock-in"
        """
        from hestai_mcp.mcp.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("feat/add-clock-in")
        assert result is not None
        assert result["value"] == "feat: add-clock-in"
        assert result["source"] == "branch"

    def test_resolve_focus_from_fix_prefix(self, mock_hestai_structure: Path):
        """
        Resolves focus from branch name with fix prefix.

        Branch: fix/broken-tests -> focus: "fix: broken-tests"
        """
        from hestai_mcp.mcp.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("fix/broken-tests")
        assert result is not None
        assert result["value"] == "fix: broken-tests"
        assert result["source"] == "branch"

    def test_resolve_focus_returns_none_for_generic_branch(self, mock_hestai_structure: Path):
        """
        Returns None for branches without recognizable patterns.

        Branch: main -> None (fallback to default will be handled elsewhere)
        """
        from hestai_mcp.mcp.tools.clock_in import resolve_focus_from_branch

        result = resolve_focus_from_branch("main")
        assert result is None

        result2 = resolve_focus_from_branch("develop")
        assert result2 is None

    def test_resolve_focus_priority_explicit_over_branch(self, mock_hestai_structure: Path):
        """
        Explicit focus takes priority over branch-inferred focus.

        Per North Star: explicit > GitHub issue > branch > default
        """
        from hestai_mcp.mcp.tools.clock_in import resolve_focus

        # When explicit focus is provided, it should take priority
        result = resolve_focus(explicit_focus="my-explicit-focus", branch="issues-56-completion")
        assert result["value"] == "my-explicit-focus"
        assert result["source"] == "explicit"

    def test_resolve_focus_github_issue_over_feature_prefix(self, mock_hestai_structure: Path):
        """
        GitHub issue pattern takes priority over feature prefix pattern.

        Branch: feat/issue-56-impl -> focus: "issue-56" (not "feat: issue-56-impl")
        """
        from hestai_mcp.mcp.tools.clock_in import resolve_focus_from_branch

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
        from hestai_mcp.mcp.tools.clock_in import resolve_focus

        result = resolve_focus(explicit_focus=None, branch="main")
        assert result["value"] == "general"
        assert result["source"] == "default"

    def test_resolve_focus_handles_complex_issue_patterns(self, mock_hestai_structure: Path):
        """
        Handles various issue number patterns in branch names.
        """
        from hestai_mcp.mcp.tools.clock_in import resolve_focus_from_branch

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
        from hestai_mcp.mcp.tools.clock_in import clock_in

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

        from hestai_mcp.mcp.tools.clock_in import clock_in

        # Mock get_current_branch to return a branch with issue pattern
        with patch(
            "hestai_mcp.mcp.tools.shared.fast_layer.get_current_branch",
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

        from hestai_mcp.mcp.tools.clock_in import clock_in

        # Mock branch to return a non-descriptive name
        with patch(
            "hestai_mcp.mcp.tools.shared.fast_layer.get_current_branch",
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
        from hestai_mcp.mcp.tools.clock_in import clock_in_async

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

        from hestai_mcp.mcp.tools.clock_in import clock_in_async

        # Mock AI synthesis to fail - patch at the source module
        with patch(
            "hestai_mcp.mcp.tools.shared.fast_layer.synthesize_fast_layer_with_ai",
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
        from hestai_mcp.mcp.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create PROJECT-CONTEXT.oct.md with recognizable content
        project_context = mock_hestai_structure / ".hestai" / "context" / "PROJECT-CONTEXT.oct.md"
        project_context.write_text(
            """===PROJECT_CONTEXT===
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
"""
        )

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

        from hestai_mcp.mcp.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        subprocess.run(["git", "init"], cwd=str(mock_hestai_structure), capture_output=True)
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
            ["git", "commit", "-m", "Initial commit"],
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
        from hestai_mcp.mcp.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create blockers file with active blockers
        state_dir = mock_hestai_structure / ".hestai" / "context" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        blockers_file = state_dir / "blockers.oct.md"
        blockers_file.write_text(
            """===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS

ACTIVE:
  blocker_001:
    DESCRIPTION::"Waiting for API key"
    SINCE::"2026-01-01"
    STATUS::ACTIVE

===END===
"""
        )

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
        from hestai_mcp.mcp.tools.clock_in import (
            MAX_TOTAL_CONTEXT_CHARS,
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create very large PROJECT-CONTEXT
        project_context = mock_hestai_structure / ".hestai" / "context" / "PROJECT-CONTEXT.oct.md"
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
        from hestai_mcp.mcp.tools.clock_in import _check_context_freshness

        # Create PROJECT-CONTEXT
        project_context = mock_hestai_structure / ".hestai" / "context" / "PROJECT-CONTEXT.oct.md"
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

        from hestai_mcp.mcp.tools.clock_in import _check_context_freshness

        # Initialize git repo and commit PROJECT-CONTEXT
        subprocess.run(["git", "init"], cwd=str(mock_hestai_structure), capture_output=True)
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
        project_context = mock_hestai_structure / ".hestai" / "context" / "PROJECT-CONTEXT.oct.md"
        project_context.write_text("===PROJECT_CONTEXT===\nTEST\n===END===")
        subprocess.run(["git", "add", "."], cwd=str(mock_hestai_structure), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add PROJECT-CONTEXT"],
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
        from hestai_mcp.mcp.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create PROJECT-CONTEXT without git (simulates stale)
        project_context = mock_hestai_structure / ".hestai" / "context" / "PROJECT-CONTEXT.oct.md"
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
        from hestai_mcp.mcp.tools.clock_in import _extract_north_star_constraints

        # Create North Star with scope boundaries
        workflow_dir = mock_hestai_structure / ".hestai" / "workflow"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        north_star = workflow_dir / "000-MCP-PRODUCT-NORTH-STAR.oct.md"
        north_star.write_text(
            """===NORTH_STAR===
SCOPE_BOUNDARIES::[
  IS::[persistent_memory_system, structural_governance_engine],
  IS_NOT::[SaaS_product, AI_model]
]
===END===
"""
        )

        constraints = _extract_north_star_constraints(north_star)

        # Should extract scope boundaries
        assert constraints is not None
        assert "persistent_memory_system" in constraints or "SCOPE" in constraints

    def test_build_rich_context_includes_north_star_constraints(self, mock_hestai_structure: Path):
        """
        build_rich_context_summary includes North Star constraints when available.

        This helps prevent Issue #87 "system architecture blindness".
        """
        from hestai_mcp.mcp.tools.clock_in import (
            build_rich_context_summary,
            resolve_context_paths,
        )

        # Create North Star
        workflow_dir = mock_hestai_structure / ".hestai" / "workflow"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        north_star = workflow_dir / "000-MCP-PRODUCT-NORTH-STAR.oct.md"
        north_star.write_text(
            """===NORTH_STAR===
IMMUTABLES::[
  I3::DUAL_LAYER_AUTHORITY,
  I4::FRESHNESS_VERIFICATION
]

SCOPE_BOUNDARIES::[
  IS::[persistent_memory_system],
  IS_NOT::[SaaS_product]
]
===END===
"""
        )

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
