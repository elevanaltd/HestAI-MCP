"""
Tests for FAST Layer Operations - Per ADR-0046 and ADR-0056.

This test suite follows TDD discipline and addresses three blocking issues
from code review:

1. OCTAVE Injection Sanitization (SECURITY)
   - sanitize_octave_scalar must prevent control character injection
   - Quote escaping for double-quoted fields

2. Multi-Worktree Branch Resolution (CORRECTNESS)
   - get_current_branch must use working_dir, not process cwd

3. Blocker Block Removal (DATA INTEGRITY)
   - persist_blockers_on_close must remove entire blocker block including extra fields
"""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.unit
class TestOctaveScalarSanitization:
    """
    Test OCTAVE injection prevention via sanitize_octave_scalar.

    BLOCKING ISSUE 1: focus, role, and branch are interpolated directly
    into OCTAVE content without sanitization.
    """

    def test_sanitize_octave_scalar_rejects_newline(self):
        """
        Rejects input containing newline character.

        Attack vector: focus='x"\nSESSION::NONE\n===END==='
        """
        from hestai_mcp.mcp.tools.shared.fast_layer import sanitize_octave_scalar

        with pytest.raises(ValueError, match="[Cc]ontrol character|[Ii]nvalid"):
            sanitize_octave_scalar('x"\nSESSION::NONE')

    def test_sanitize_octave_scalar_rejects_carriage_return(self):
        """Rejects input containing carriage return."""
        from hestai_mcp.mcp.tools.shared.fast_layer import sanitize_octave_scalar

        with pytest.raises(ValueError, match="[Cc]ontrol character|[Ii]nvalid"):
            sanitize_octave_scalar("value\rwith\rCR")

    def test_sanitize_octave_scalar_rejects_tab(self):
        """Rejects input containing tab character."""
        from hestai_mcp.mcp.tools.shared.fast_layer import sanitize_octave_scalar

        with pytest.raises(ValueError, match="[Cc]ontrol character|[Ii]nvalid"):
            sanitize_octave_scalar("value\twith\ttab")

    def test_sanitize_octave_scalar_escapes_quotes(self):
        """Escapes double quotes in scalar values."""
        from hestai_mcp.mcp.tools.shared.fast_layer import sanitize_octave_scalar

        # Input with quotes should be escaped
        result = sanitize_octave_scalar('value with "quotes"')
        assert '\\"' in result or '"' not in result.replace('\\"', "")
        # The original unescaped quotes should not remain
        assert result != 'value with "quotes"'

    def test_sanitize_octave_scalar_allows_safe_input(self):
        """Allows safe alphanumeric and hyphen input."""
        from hestai_mcp.mcp.tools.shared.fast_layer import sanitize_octave_scalar

        # Normal role/focus names should pass through
        assert sanitize_octave_scalar("implementation-lead") == "implementation-lead"
        assert sanitize_octave_scalar("b2-implementation") == "b2-implementation"
        assert sanitize_octave_scalar("main") == "main"
        assert sanitize_octave_scalar("feature/my-branch") == "feature/my-branch"

    def test_sanitize_octave_scalar_handles_empty_string(self):
        """Handles empty string input."""
        from hestai_mcp.mcp.tools.shared.fast_layer import sanitize_octave_scalar

        # Empty string should be allowed (or raise specific error, not crash)
        result = sanitize_octave_scalar("")
        assert result == ""

    def test_populate_current_focus_sanitizes_inputs(self, tmp_path: Path):
        """
        populate_current_focus sanitizes role, focus, and branch.

        Verifies that injection attempts are blocked when writing OCTAVE content.
        """
        from hestai_mcp.mcp.tools.shared.fast_layer import (
            ensure_state_directory,
            populate_current_focus,
        )

        state_dir = ensure_state_directory(tmp_path)

        # Attempt injection via focus parameter
        with pytest.raises(ValueError, match="[Cc]ontrol character|[Ii]nvalid"):
            populate_current_focus(
                state_dir=state_dir,
                session_id="test-session",
                role="implementation-lead",
                focus='malicious"\nSESSION::NONE\n===END===',
            )

    def test_populate_current_focus_sanitizes_role(self, tmp_path: Path):
        """populate_current_focus sanitizes role parameter."""
        from hestai_mcp.mcp.tools.shared.fast_layer import (
            ensure_state_directory,
            populate_current_focus,
        )

        state_dir = ensure_state_directory(tmp_path)

        # Attempt injection via role parameter
        with pytest.raises(ValueError, match="[Cc]ontrol character|[Ii]nvalid"):
            populate_current_focus(
                state_dir=state_dir,
                session_id="test-session",
                role="evil\nROLE::hacker\n",
                focus="normal-focus",
            )


def _init_git_repo(repo_path: Path, branch_name: str) -> None:
    """
    Initialize a git repo with proper config for CI environments.

    CI environments (e.g., GitHub Actions) often lack global git user config,
    causing git commit to fail. This helper sets up local repo config.

    Additionally, disables global hooks to ensure hermeticity - tests must pass
    regardless of user's global git configuration (e.g., core.hooksPath policies).
    """
    subprocess.run(["git", "init"], cwd=str(repo_path), capture_output=True, check=True)
    # Disable global hooks for test hermeticity (prevents global core.hooksPath interference)
    subprocess.run(
        ["git", "config", "core.hooksPath", ""],
        cwd=str(repo_path),
        capture_output=True,
        check=True,
    )
    # Set local user config (required for commits in CI where no global config exists)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo_path),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo_path),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=str(repo_path),
        capture_output=True,
        check=True,
    )
    # Create an empty commit so HEAD exists
    subprocess.run(
        ["git", "commit", "--no-verify", "--allow-empty", "-m", "initial"],
        cwd=str(repo_path),
        capture_output=True,
        check=True,
    )


@pytest.mark.unit
class TestMultiWorktreeBranchResolution:
    """
    Test branch resolution uses target working_dir, not process cwd.

    BLOCKING ISSUE 2: get_current_branch uses subprocess without cwd parameter,
    returning branch of process working directory, NOT target worktree.
    """

    def test_get_current_branch_uses_working_dir(self, tmp_path: Path):
        """
        get_current_branch must use the provided working_dir.

        Creates two git repos with different branches, verifies that
        get_current_branch returns the branch from working_dir, not cwd.
        """
        from hestai_mcp.mcp.tools.shared.fast_layer import get_current_branch

        # Create first repo (will be the target)
        target_repo = tmp_path / "target_repo"
        target_repo.mkdir()
        _init_git_repo(target_repo, "target-branch")

        # Create second repo (different branch)
        other_repo = tmp_path / "other_repo"
        other_repo.mkdir()
        _init_git_repo(other_repo, "other-branch")

        # Call get_current_branch with target_repo as working_dir
        # Should return "target-branch" regardless of process cwd
        result = get_current_branch(working_dir=target_repo)

        assert result == "target-branch"

    def test_get_current_branch_returns_unknown_on_failure(self, tmp_path: Path):
        """get_current_branch returns 'unknown' when git fails."""
        from hestai_mcp.mcp.tools.shared.fast_layer import get_current_branch

        # Directory without git repo
        no_git = tmp_path / "no_git"
        no_git.mkdir()

        result = get_current_branch(working_dir=no_git)
        assert result == "unknown"

    def test_populate_current_focus_uses_correct_branch(self, tmp_path: Path):
        """
        populate_current_focus uses branch from working_dir, not process cwd.

        This is the integration test that verifies the fix propagates through.
        """
        # Create a git repo with a specific branch
        git_repo = tmp_path / "git_project"
        git_repo.mkdir()
        _init_git_repo(git_repo, "my-feature-branch")

        # Import and call functions
        from hestai_mcp.mcp.tools.shared.fast_layer import (
            ensure_state_directory,
            populate_current_focus,
        )

        state_dir = ensure_state_directory(git_repo)

        populate_current_focus(
            state_dir=state_dir,
            session_id="test-session",
            role="implementation-lead",
            focus="test-focus",
        )

        # Read the generated file
        content = (state_dir / "current-focus.oct.md").read_text()

        # Should contain the branch from the target repo
        assert "BRANCH::my-feature-branch" in content


@pytest.mark.unit
class TestBlockerRemovalWithExtraFields:
    """
    Test blocker block removal handles extra fields properly.

    BLOCKING ISSUE 3: Parser only accumulates DESCRIPTION::, SINCE::, STATUS::
    fields. Extra fields like OWNER::, LINKS:: are not properly handled.
    """

    def test_persist_blockers_removes_entire_block_with_extra_fields(self, tmp_path: Path):
        """
        persist_blockers_on_close removes entire blocker block including extra fields.

        Blocker with OWNER::, LINKS::, or other extra fields must be fully removed
        when STATUS::RESOLVED.
        """
        from hestai_mcp.mcp.tools.shared.fast_layer import persist_blockers_on_close

        state_dir = tmp_path / "state"
        state_dir.mkdir(parents=True)

        # Create blockers file with extra fields
        blockers_content = """===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS
  VELOCITY::HOURLY_DAILY
  SESSION::"test-session"

ACTIVE:
  blocker_001:
    DESCRIPTION::"Resolved issue with extra fields"
    SINCE::"2025-12-28T10:00:00Z"
    OWNER::"developer-1"
    LINKS::"https://github.com/org/repo/issues/123"
    PRIORITY::HIGH
    STATUS::RESOLVED
  blocker_002:
    DESCRIPTION::"Still pending"
    SINCE::"2025-12-28T11:00:00Z"
    STATUS::UNRESOLVED

===END===
"""
        blockers_path = state_dir / "blockers.oct.md"
        blockers_path.write_text(blockers_content)

        # Execute
        persist_blockers_on_close(state_dir, "test-session")

        # Read result
        result_content = blockers_path.read_text()

        # Resolved blocker should be completely removed
        assert "blocker_001" not in result_content
        assert "OWNER::" not in result_content
        assert "LINKS::" not in result_content
        assert "PRIORITY::HIGH" not in result_content
        assert "Resolved issue with extra fields" not in result_content

        # Unresolved blocker should remain
        assert "blocker_002" in result_content
        assert "Still pending" in result_content
        assert "STATUS::UNRESOLVED" in result_content

    def test_persist_blockers_handles_nested_extra_fields(self, tmp_path: Path):
        """
        persist_blockers_on_close handles deeply nested extra fields.
        """
        from hestai_mcp.mcp.tools.shared.fast_layer import persist_blockers_on_close

        state_dir = tmp_path / "state"
        state_dir.mkdir(parents=True)

        # Create blockers with nested structure
        blockers_content = """===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS

ACTIVE:
  blocker_001:
    DESCRIPTION::"Nested resolved"
    SINCE::"2025-12-28T10:00:00Z"
    METADATA:
      CREATED_BY::"system"
      TAGS::["urgent", "security"]
    STATUS::RESOLVED
  blocker_002:
    DESCRIPTION::"Unresolved stays"
    STATUS::UNRESOLVED

===END===
"""
        blockers_path = state_dir / "blockers.oct.md"
        blockers_path.write_text(blockers_content)

        persist_blockers_on_close(state_dir, "test-session")

        result_content = blockers_path.read_text()

        # All of blocker_001 should be gone
        assert "blocker_001" not in result_content
        assert "Nested resolved" not in result_content
        assert "CREATED_BY" not in result_content
        assert "TAGS::" not in result_content

        # blocker_002 should remain
        assert "blocker_002" in result_content
        assert "Unresolved stays" in result_content

    def test_persist_blockers_preserves_non_blocker_content(self, tmp_path: Path):
        """
        persist_blockers_on_close preserves META and other non-blocker content.
        """
        from hestai_mcp.mcp.tools.shared.fast_layer import persist_blockers_on_close

        state_dir = tmp_path / "state"
        state_dir.mkdir(parents=True)

        blockers_content = """===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS
  VELOCITY::HOURLY_DAILY
  SESSION::"test-session"

ACTIVE:
  blocker_001:
    DESCRIPTION::"To remove"
    STATUS::RESOLVED

===END===
"""
        blockers_path = state_dir / "blockers.oct.md"
        blockers_path.write_text(blockers_content)

        persist_blockers_on_close(state_dir, "test-session")

        result_content = blockers_path.read_text()

        # Structure should remain
        assert "===BLOCKERS===" in result_content
        assert "META:" in result_content
        assert "TYPE::FAST_BLOCKERS" in result_content
        assert "ACTIVE:" in result_content
        assert "===END===" in result_content

        # Resolved blocker should be gone
        assert "blocker_001" not in result_content

    def test_persist_blockers_handles_multiple_resolved_blockers(self, tmp_path: Path):
        """
        persist_blockers_on_close correctly removes multiple resolved blockers.
        """
        from hestai_mcp.mcp.tools.shared.fast_layer import persist_blockers_on_close

        state_dir = tmp_path / "state"
        state_dir.mkdir(parents=True)

        blockers_content = """===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS

ACTIVE:
  blocker_001:
    DESCRIPTION::"First resolved"
    OWNER::"dev-1"
    STATUS::RESOLVED
  blocker_002:
    DESCRIPTION::"Keep this one"
    STATUS::UNRESOLVED
  blocker_003:
    DESCRIPTION::"Second resolved"
    LINKS::"http://example.com"
    STATUS::RESOLVED
  blocker_004:
    DESCRIPTION::"Also keep"
    PRIORITY::LOW
    STATUS::UNRESOLVED

===END===
"""
        blockers_path = state_dir / "blockers.oct.md"
        blockers_path.write_text(blockers_content)

        persist_blockers_on_close(state_dir, "test-session")

        result_content = blockers_path.read_text()

        # Resolved blockers should be gone
        assert "blocker_001" not in result_content
        assert "First resolved" not in result_content
        assert "blocker_003" not in result_content
        assert "Second resolved" not in result_content

        # Unresolved blockers should remain with their extra fields
        assert "blocker_002" in result_content
        assert "Keep this one" in result_content
        assert "blocker_004" in result_content
        assert "Also keep" in result_content
        assert "PRIORITY::LOW" in result_content


@pytest.mark.unit
class TestAISynthesisIntegration:
    """
    Test AI-powered FAST layer synthesis per North Star Section 5 STEP_5+6.

    The synthesize_fast_layer_with_ai function:
    1. Creates a CompletionRequest with synthesis prompt
    2. Calls AIClient.complete_text()
    3. Parses AI response into synthesis result
    4. Falls back to template if AI fails (SS-I6)
    """

    @pytest.mark.asyncio
    async def test_synthesize_fast_layer_with_ai_success(self, tmp_path: Path):
        """
        AI synthesis returns structured FAST layer content on success.

        AI response must contain all required OCTAVE fields to be accepted.
        """
        from unittest.mock import AsyncMock, MagicMock, patch

        from hestai_mcp.mcp.tools.shared.fast_layer import synthesize_fast_layer_with_ai

        # Mock a successful AI response with valid OCTAVE format (all required fields)
        mock_ai_response = """CONTEXT_FILES::[@.hestai/context/PROJECT-CONTEXT.oct.md:L1-50]
FOCUS::issue-56
PHASE::B2
BLOCKERS::[]
TASKS::[Wire AIClient into FAST layer synthesis, Add focus resolution from branch patterns]
FRESHNESS_WARNING::NONE"""

        # Patch at the import location inside the function
        with (
            patch("hestai_mcp.ai.client.AIClient") as mock_ai_client_cls,
            patch("hestai_mcp.ai.config.load_config") as mock_load_config,
        ):
            # Mock config loading
            mock_load_config.return_value = MagicMock()
            mock_config = mock_load_config.return_value
            mock_config.get_operation_tier = MagicMock(return_value="fast")

            # Mock the async context manager and complete_text
            mock_client = AsyncMock()
            mock_client.complete_text = AsyncMock(return_value=mock_ai_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_ai_client_cls.return_value = mock_client

            result = await synthesize_fast_layer_with_ai(
                session_id="test-session-123",
                role="implementation-lead",
                focus="issue-56",
                context_summary="Working on clock_in AI integration",
            )

            # Should return synthesis result
            assert result is not None
            assert "synthesis" in result
            assert "source" in result
            assert result["source"] == "ai"

    @pytest.mark.asyncio
    async def test_synthesize_fast_layer_fallback_on_ai_failure(self, tmp_path: Path):
        """
        Falls back to template approach when AI fails (SS-I6 compliance).
        """
        from unittest.mock import AsyncMock, MagicMock, patch

        from hestai_mcp.mcp.tools.shared.fast_layer import synthesize_fast_layer_with_ai

        with (
            patch("hestai_mcp.ai.client.AIClient") as mock_ai_client_cls,
            patch("hestai_mcp.ai.config.load_config") as mock_load_config,
        ):
            # Mock config loading
            mock_load_config.return_value = MagicMock()

            # Simulate AI failure during complete_text
            mock_client = AsyncMock()
            mock_client.complete_text = AsyncMock(side_effect=Exception("AI unavailable"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_ai_client_cls.return_value = mock_client

            result = await synthesize_fast_layer_with_ai(
                session_id="test-session-123",
                role="implementation-lead",
                focus="issue-56",
                context_summary="Working on clock_in AI integration",
            )

            # Should fall back gracefully
            assert result is not None
            assert "synthesis" in result
            assert "source" in result
            assert result["source"] == "fallback"

    @pytest.mark.asyncio
    async def test_synthesize_fast_layer_with_ai_no_config(self, tmp_path: Path):
        """
        Returns fallback when no AI config is available.
        """
        from unittest.mock import patch

        from hestai_mcp.mcp.tools.shared.fast_layer import synthesize_fast_layer_with_ai

        # Simulate no AI config (load_config raises)
        with patch(
            "hestai_mcp.ai.config.load_config",
            side_effect=FileNotFoundError("No config"),
        ):
            result = await synthesize_fast_layer_with_ai(
                session_id="test-session-123",
                role="implementation-lead",
                focus="general",
                context_summary="General work session",
            )

            # Should fall back gracefully
            assert result is not None
            assert result["source"] == "fallback"

    @pytest.mark.asyncio
    async def test_synthesize_fast_layer_respects_async(self, tmp_path: Path):
        """
        Synthesis function is properly async (SS-I2 compliance).
        """
        import inspect
        from unittest.mock import AsyncMock, MagicMock, patch

        from hestai_mcp.mcp.tools.shared.fast_layer import synthesize_fast_layer_with_ai

        # Verify the function is a coroutine function
        assert inspect.iscoroutinefunction(synthesize_fast_layer_with_ai)

        # Mock successful response
        with (
            patch("hestai_mcp.ai.client.AIClient") as mock_ai_client_cls,
            patch("hestai_mcp.ai.config.load_config") as mock_load_config,
        ):
            mock_load_config.return_value = MagicMock()

            mock_client = AsyncMock()
            mock_client.complete_text = AsyncMock(return_value="AI synthesis result")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_ai_client_cls.return_value = mock_client

            # Should be awaitable
            coro = synthesize_fast_layer_with_ai(
                session_id="test",
                role="test",
                focus="test",
                context_summary="test",
            )
            assert inspect.iscoroutine(coro)
            result = await coro
            assert result is not None

    @pytest.mark.asyncio
    async def test_fallback_synthesis_uses_octave_format(self, tmp_path: Path):
        """
        Fallback synthesis emits OCTAVE format matching AI output contract.

        BLOCKING FIX: Fallback must use same structured format as AI synthesis
        to maintain contract consistency. Legacy prose format (FOCUS_SUMMARY,
        KEY_TASKS) breaks structured navigation.

        Required OCTAVE fields per protocols.py:
        - CONTEXT_FILES::
        - FOCUS::
        - PHASE::
        - BLOCKERS::
        - TASKS::
        - FRESHNESS_WARNING::
        """
        from unittest.mock import AsyncMock, MagicMock, patch

        from hestai_mcp.mcp.tools.shared.fast_layer import synthesize_fast_layer_with_ai

        with (
            patch("hestai_mcp.ai.client.AIClient") as mock_ai_client_cls,
            patch("hestai_mcp.ai.config.load_config") as mock_load_config,
        ):
            mock_load_config.return_value = MagicMock()

            # Force AI failure to trigger fallback
            mock_client = AsyncMock()
            mock_client.complete_text = AsyncMock(side_effect=Exception("AI unavailable"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_ai_client_cls.return_value = mock_client

            result = await synthesize_fast_layer_with_ai(
                session_id="test-session-123",
                role="implementation-lead",
                focus="crs-blocking-fixes",
                context_summary="Fixing CRS blocking issues",
            )

            synthesis = result["synthesis"]

            # Must contain OCTAVE format fields
            assert "CONTEXT_FILES::" in synthesis, "Fallback must include CONTEXT_FILES:: field"
            assert "FOCUS::" in synthesis, "Fallback must include FOCUS:: field"
            assert "PHASE::" in synthesis, "Fallback must include PHASE:: field"
            assert "BLOCKERS::" in synthesis, "Fallback must include BLOCKERS:: field"
            assert "TASKS::" in synthesis, "Fallback must include TASKS:: field"
            assert "FRESHNESS_WARNING::" in synthesis, "Fallback must include FRESHNESS_WARNING::"

            # Must NOT contain legacy prose format
            assert "FOCUS_SUMMARY" not in synthesis, "Fallback must not use legacy FOCUS_SUMMARY"
            assert "KEY_TASKS" not in synthesis, "Fallback must not use legacy KEY_TASKS"

    @pytest.mark.asyncio
    async def test_fallback_synthesis_includes_role_and_focus_values(self, tmp_path: Path):
        """
        Fallback synthesis correctly interpolates role and focus into OCTAVE fields.
        """
        from unittest.mock import patch

        from hestai_mcp.mcp.tools.shared.fast_layer import synthesize_fast_layer_with_ai

        # Trigger fallback via config load failure
        with patch(
            "hestai_mcp.ai.config.load_config",
            side_effect=FileNotFoundError("No config"),
        ):
            result = await synthesize_fast_layer_with_ai(
                session_id="test-session",
                role="code-review-specialist",
                focus="pr-review",
                context_summary="Reviewing pull request",
            )

            synthesis = result["synthesis"]

            # Focus value should appear in FOCUS:: field
            assert "pr-review" in synthesis
            # Role should appear somewhere in context (tasks or notes)
            assert "code-review-specialist" in synthesis

    @pytest.mark.asyncio
    async def test_ai_response_missing_octave_fields_triggers_fallback(self, tmp_path: Path):
        """
        AI response missing required OCTAVE fields triggers fallback.

        Anti-fragility: AI synthesis must contain all required OCTAVE fields.
        If ANY field is missing, swap to validated fallback to guarantee output contract.

        Required OCTAVE fields per protocols.py:
        - CONTEXT_FILES::
        - FOCUS::
        - PHASE::
        - BLOCKERS::
        - TASKS::
        - FRESHNESS_WARNING::
        """
        from unittest.mock import AsyncMock, MagicMock, patch

        from hestai_mcp.mcp.tools.shared.fast_layer import synthesize_fast_layer_with_ai

        # AI returns incomplete OCTAVE (missing BLOCKERS::, TASKS::, FRESHNESS_WARNING::)
        incomplete_ai_response = """CONTEXT_FILES::[@.hestai/context/PROJECT-CONTEXT.oct.md]
FOCUS::test-focus
PHASE::B2
This is an incomplete response that lacks required fields."""

        with (
            patch("hestai_mcp.ai.client.AIClient") as mock_ai_client_cls,
            patch("hestai_mcp.ai.config.load_config") as mock_load_config,
        ):
            mock_load_config.return_value = MagicMock()
            mock_config = mock_load_config.return_value
            mock_config.get_operation_tier = MagicMock(return_value="fast")

            mock_client = AsyncMock()
            mock_client.complete_text = AsyncMock(return_value=incomplete_ai_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_ai_client_cls.return_value = mock_client

            result = await synthesize_fast_layer_with_ai(
                session_id="test-session-123",
                role="implementation-lead",
                focus="test-focus",
                context_summary="Testing OCTAVE validation",
            )

            # Should use fallback due to missing fields
            assert result["source"] == "fallback", "Incomplete AI response should trigger fallback"

            synthesis = result["synthesis"]

            # Fallback must have ALL required fields
            assert "CONTEXT_FILES::" in synthesis
            assert "FOCUS::" in synthesis
            assert "PHASE::" in synthesis
            assert "BLOCKERS::" in synthesis
            assert "TASKS::" in synthesis
            assert "FRESHNESS_WARNING::" in synthesis

    @pytest.mark.asyncio
    async def test_ai_response_with_all_octave_fields_succeeds(self, tmp_path: Path):
        """
        AI response with all required OCTAVE fields returns AI source.

        When AI produces valid OCTAVE with all required fields,
        the AI response should be returned as-is with source="ai".
        """
        from unittest.mock import AsyncMock, MagicMock, patch

        from hestai_mcp.mcp.tools.shared.fast_layer import synthesize_fast_layer_with_ai

        # AI returns complete OCTAVE with all required fields
        complete_ai_response = """CONTEXT_FILES::[@.hestai/context/PROJECT-CONTEXT.oct.md]
FOCUS::test-focus
PHASE::B2
BLOCKERS::[]
TASKS::[Complete implementation, Run tests]
FRESHNESS_WARNING::NONE"""

        with (
            patch("hestai_mcp.ai.client.AIClient") as mock_ai_client_cls,
            patch("hestai_mcp.ai.config.load_config") as mock_load_config,
        ):
            mock_load_config.return_value = MagicMock()
            mock_config = mock_load_config.return_value
            mock_config.get_operation_tier = MagicMock(return_value="fast")

            mock_client = AsyncMock()
            mock_client.complete_text = AsyncMock(return_value=complete_ai_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_ai_client_cls.return_value = mock_client

            result = await synthesize_fast_layer_with_ai(
                session_id="test-session-123",
                role="implementation-lead",
                focus="test-focus",
                context_summary="Testing OCTAVE validation",
            )

            # Should use AI response since all fields present
            assert result["source"] == "ai", "Complete AI response should return source=ai"
            assert result["synthesis"] == complete_ai_response
