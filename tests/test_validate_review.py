#!/usr/bin/env python3
"""
Test suite for scripts/validate_review.py

Validates fail-closed behavior in CI, local mode permissiveness,
fork PR support, and emergency bypass audit trail.

SECURITY: Tests marked with @pytest.mark.security validate critical
fail-closed behavior - failures indicate security vulnerabilities.
"""

import json
import subprocess

# Import the module under test
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import validate_review


@pytest.fixture
def ci_environment(monkeypatch):
    """Set up CI environment variables."""
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("GITHUB_BASE_REF", "origin/main")
    monkeypatch.setenv("PR_NUMBER", "123")


@pytest.fixture
def local_environment(monkeypatch):
    """Set up local development environment."""
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_BASE_REF", raising=False)
    monkeypatch.delenv("PR_NUMBER", raising=False)


@pytest.mark.security
class TestFailClosedBehavior:
    """Critical security tests - validate fail-closed behavior in CI."""

    def test_get_changed_files_git_failure_in_ci_exits_nonzero(self, ci_environment, monkeypatch):
        """SECURITY: Git failures in CI must exit non-zero, not return empty list."""

        # Mock subprocess.run to raise CalledProcessError
        def mock_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, "git diff")

        monkeypatch.setattr(subprocess, "run", mock_run)

        # In CI context, git failures should raise, not return []
        with pytest.raises(SystemExit) as exc_info:
            validate_review.get_changed_files()
        assert exc_info.value.code == 1, "Git failure in CI must exit code 1"

    def test_check_pr_comments_failure_in_ci_blocks(self, ci_environment, monkeypatch):
        """SECURITY: PR comment check failures in CI must return False, not True."""

        # Mock gh CLI to raise CalledProcessError
        def mock_run(*args, **kwargs):
            if "gh" in args[0]:
                raise subprocess.CalledProcessError(1, "gh pr view")
            # Allow other git commands to succeed
            return MagicMock(stdout="", returncode=0)

        monkeypatch.setattr(subprocess, "run", mock_run)

        # In CI context, comment check failures should return False
        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is False, "Comment check failure in CI must return False"
        assert "error" in message.lower() or "failed" in message.lower()

    def test_main_blocks_on_missing_review_in_ci(self, ci_environment, monkeypatch):
        """SECURITY: main() must exit 1 when reviews missing in CI."""
        # Mock get_changed_files to return non-exempt files
        monkeypatch.setattr(
            validate_review,
            "get_changed_files",
            lambda: [{"path": "src/core.py", "added": 10, "deleted": 5, "total_changed": 15}],
        )

        # Mock check_pr_comments to return False (missing review)
        monkeypatch.setattr(
            validate_review, "check_pr_comments", lambda tier: (False, "Missing review")
        )

        # Mock check_emergency_bypass to return False
        monkeypatch.setattr(validate_review, "check_emergency_bypass", lambda: False)

        # main() should exit 1 in CI when reviews missing
        exit_code = validate_review.main()
        assert exit_code == 1, "main() must exit 1 when reviews missing in CI"


@pytest.mark.behavior
class TestLocalModePermissiveness:
    """Validate that local mode remains permissive for developer UX."""

    def test_get_changed_files_git_failure_local_returns_empty(
        self, local_environment, monkeypatch
    ):
        """Local mode: Git failures return empty list (permissive)."""

        # Mock subprocess.run to raise CalledProcessError
        def mock_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, "git diff")

        monkeypatch.setattr(subprocess, "run", mock_run)

        # In local context, git failures should return empty list
        files = validate_review.get_changed_files()
        assert files == [], "Git failure in local mode should return empty list"

    def test_check_pr_comments_skips_in_local_mode(self, local_environment):
        """Local mode: PR comment checks are skipped."""
        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, "Local mode should skip PR comment checks"
        assert "local" in message.lower() or "skip" in message.lower()

    def test_main_permits_without_review_locally(self, local_environment, monkeypatch):
        """Local mode: main() exits 0 even without reviews (permissive)."""
        # Mock get_changed_files to return non-exempt files
        monkeypatch.setattr(
            validate_review,
            "get_changed_files",
            lambda: [{"path": "src/core.py", "added": 10, "deleted": 5, "total_changed": 15}],
        )

        # Mock check_emergency_bypass to return False
        monkeypatch.setattr(validate_review, "check_emergency_bypass", lambda: False)

        # main() should exit 0 in local mode even without reviews
        exit_code = validate_review.main()
        assert exit_code == 0, "main() should exit 0 in local mode (permissive)"


@pytest.mark.behavior
class TestForkPRSupport:
    """Validate fork PR support (already fixed in PR #193)."""

    def test_get_changed_files_uses_base_ref_in_ci(self, ci_environment, monkeypatch):
        """CI mode: Uses GITHUB_BASE_REF for fork PRs."""
        calls = []

        def mock_run(cmd, *args, **kwargs):
            calls.append(cmd)
            return MagicMock(
                stdout="10\t5\tsrc/core.py\n", stderr="", returncode=0, check=lambda: None
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        validate_review.get_changed_files()

        # Verify git diff command uses base_ref
        assert len(calls) > 0
        assert any("origin/main...HEAD" in " ".join(cmd) for cmd in calls)

    def test_get_changed_files_uses_cached_locally(self, local_environment, monkeypatch):
        """Local mode: Uses --cached for staged files."""
        calls = []

        def mock_run(cmd, *args, **kwargs):
            calls.append(cmd)
            return MagicMock(
                stdout="10\t5\tsrc/core.py\n", stderr="", returncode=0, check=lambda: None
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        validate_review.get_changed_files()

        # Verify git diff command uses --cached
        assert len(calls) > 0
        assert any("--cached" in cmd for cmd in calls)


@pytest.mark.security
class TestEmergencyBypassAudit:
    """Validate emergency bypass creates audit trail."""

    def test_emergency_bypass_creates_audit_log(self, ci_environment, monkeypatch, tmp_path):
        """SECURITY: Emergency bypass must create audit log entry."""
        # Set up temporary audit directory
        audit_dir = tmp_path / ".hestai" / "audit"
        audit_log = audit_dir / "bypass-log.jsonl"

        # Mock get_changed_files
        monkeypatch.setattr(
            validate_review,
            "get_changed_files",
            lambda: [{"path": "src/core.py", "added": 10, "deleted": 5, "total_changed": 15}],
        )

        # Mock check_emergency_bypass to return True
        monkeypatch.setattr(validate_review, "check_emergency_bypass", lambda: True)

        # Mock Path.cwd() to return tmp_path
        monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

        # Run main() - should create audit log
        exit_code = validate_review.main()
        assert exit_code == 0, "Emergency bypass should exit 0"

        # Verify audit log was created
        assert audit_log.exists(), "Audit log must be created for emergency bypass"

        # Verify audit log content
        with open(audit_log) as f:
            entries = [json.loads(line) for line in f]
            assert len(entries) > 0, "Audit log must contain at least one entry"
            entry = entries[-1]
            assert "timestamp" in entry
            assert "pr_number" in entry or "commit" in entry
            assert "reason" in entry
            assert entry["reason"] == "EMERGENCY_BYPASS"

    def test_emergency_bypass_audit_includes_metadata(self, ci_environment, monkeypatch, tmp_path):
        """Emergency bypass audit log includes PR number and user metadata."""
        audit_dir = tmp_path / ".hestai" / "audit"
        audit_log = audit_dir / "bypass-log.jsonl"

        # Mock functions
        monkeypatch.setattr(
            validate_review,
            "get_changed_files",
            lambda: [{"path": "src/core.py", "added": 10, "deleted": 5, "total_changed": 15}],
        )
        monkeypatch.setattr(validate_review, "check_emergency_bypass", lambda: True)
        monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

        # Mock git user info
        def mock_run(cmd, *args, **kwargs):
            if "config" in cmd and "user.name" in cmd:
                return MagicMock(stdout="Test User\n")
            if "config" in cmd and "user.email" in cmd:
                return MagicMock(stdout="test@example.com\n")
            return MagicMock(stdout="", returncode=0)

        monkeypatch.setattr(subprocess, "run", mock_run)

        validate_review.main()

        # Verify audit log includes metadata
        with open(audit_log) as f:
            entry = json.loads(f.read())
            assert "pr_number" in entry or "commit" in entry
            assert entry.get("pr_number") == "123" or "commit" in entry


@pytest.mark.behavior
class TestReviewTierLogic:
    """Validate review tier determination logic."""

    def test_tier_0_exempt_for_markdown_only(self):
        """TIER_0_EXEMPT for markdown-only changes."""
        files = [
            {"path": "README.md", "added": 10, "deleted": 5, "total_changed": 15},
            {"path": "docs/guide.md", "added": 20, "deleted": 10, "total_changed": 30},
        ]
        tier, reason = validate_review.determine_review_tier(files)
        assert tier == "TIER_0_EXEMPT"
        assert "exempt" in reason.lower()

    def test_tier_1_self_for_small_single_file(self):
        """TIER_1_SELF for <50 lines in single file."""
        files = [{"path": "src/utils.py", "added": 20, "deleted": 10, "total_changed": 30}]
        tier, reason = validate_review.determine_review_tier(files)
        assert tier == "TIER_1_SELF"

    def test_tier_2_crs_for_medium_changes(self):
        """TIER_2_STANDARD for 50-500 lines."""
        files = [{"path": "src/core.py", "added": 100, "deleted": 50, "total_changed": 150}]
        tier, reason = validate_review.determine_review_tier(files)
        assert tier == "TIER_2_STANDARD"

    def test_tier_3_full_for_large_changes(self):
        """TIER_3_STRICT for >500 lines."""
        files = [{"path": "src/core.py", "added": 400, "deleted": 200, "total_changed": 600}]
        tier, reason = validate_review.determine_review_tier(files)
        assert tier == "TIER_3_STRICT"

    def test_tier_0_exempt_for_architecture_markdown(self):
        """TIER_0_EXEMPT for architecture markdown (all .md exempt)."""
        files = [
            {"path": "docs/architecture/system.md", "added": 10, "deleted": 5, "total_changed": 15}
        ]
        tier, reason = validate_review.determine_review_tier(files)
        assert tier == "TIER_0_EXEMPT"
        assert "exempt" in reason.lower()


@pytest.mark.behavior
class TestPRCommentValidation:
    """Validate PR comment checking logic."""

    def test_tier_1_requires_self_review_comment(self, ci_environment, monkeypatch):
        """TIER_1_SELF requires 'IL SELF-REVIEWED:' or 'HO REVIEWED:' comment."""

        # Mock gh CLI to return comments without self-review
        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps({"body": "", "comments": [{"body": "Some other comment"}]}),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is False
        assert "SELF-REVIEWED" in message or "HO REVIEWED" in message

    def test_tier_2_requires_crs_and_ce_approval(self, ci_environment, monkeypatch):
        """TIER_2_STANDARD requires both 'CRS APPROVED:' and 'CE APPROVED:' comments."""

        # Mock gh CLI to return comments with both CRS and CE approval
        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS APPROVED: Logic correct, tests pass"},
                            {"body": "CE APPROVED: Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True
        assert "CRS and CE approvals found" in message

    def test_tier_2_missing_ce_fails(self, ci_environment, monkeypatch):
        """TIER_2_STANDARD with only CRS approval (no CE) should fail."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {"body": "", "comments": [{"body": "CRS APPROVED: Logic correct, tests pass"}]}
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is False
        assert "CE APPROVED" in message or "CE GO" in message

    def test_tier_3_requires_dual_crs_and_ce(self, ci_environment, monkeypatch):
        """TIER_3_STRICT requires CRS (Gemini) + CRS (Codex) + CE approvals."""

        # Mock gh CLI to return comments with only one CRS approval
        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS (Gemini) APPROVED: Logic correct"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_STRICT")
        assert approved is False
        assert "CRS (Codex)" in message or "CE" in message


@pytest.mark.behavior
class TestPRBodyScanning:
    """Validate that PR body is scanned for approval patterns in addition to comments."""

    def test_crs_and_ce_approval_in_pr_body_is_accepted(self, ci_environment, monkeypatch):
        """Approval patterns in PR body should satisfy the review gate."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "## Review Summary\nCRS APPROVED: Logic correct, tests pass\nCE APPROVED: Architecture sound",
                        "comments": [],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, "CRS and CE approval in PR body should be accepted"
        assert "CRS and CE approvals found" in message

    def test_self_review_in_pr_body_is_accepted(self, ci_environment, monkeypatch):
        """Self-review pattern in PR body should satisfy TIER_1_SELF."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "IL SELF-REVIEWED: Small config change",
                        "comments": [],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is True, "Self-review in PR body should be accepted"
        assert "Self-review found" in message

    def test_tier_3_approvals_split_between_body_and_comments(self, ci_environment, monkeypatch):
        """TIER_3: Dual CRS + CE approvals split between body and comments should pass."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "CRS (Gemini) APPROVED: Architecture sound\nCRS (Codex) APPROVED: Logic verified",
                        "comments": [{"body": "CE APPROVED: Performance acceptable"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_STRICT")
        assert approved is True, "Approvals split between body and comments should pass"
        assert "Dual CRS" in message and "CE" in message

    def test_gh_cli_fetches_body_and_comments(self, ci_environment, monkeypatch):
        """The gh CLI call should request both 'body' and 'comments' fields."""
        captured_cmds = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmds.append(cmd)
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS APPROVED: ok"},
                            {"body": "CE APPROVED: ok"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        validate_review.check_pr_comments("TIER_2_STANDARD")

        # Verify gh pr view fetches both body and comments
        assert len(captured_cmds) > 0
        gh_cmd = captured_cmds[0]
        assert (
            "comments,body" in gh_cmd or "body,comments" in gh_cmd
        ), f"gh CLI should fetch both comments and body, got: {gh_cmd}"

    def test_empty_pr_body_still_checks_comments(self, ci_environment, monkeypatch):
        """Empty or null PR body should not break comment checking."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": None,
                        "comments": [
                            {"body": "CRS APPROVED: Looks good"},
                            {"body": "CE APPROVED: Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, "Null PR body should not block comment-based approval"


@pytest.mark.behavior
class TestHOSupervisoryReview:
    """Validate that HO REVIEWED is accepted as an alternative T1 approval.

    When HO delegates to IL and then reviews the work, it's a supervisory
    review (higher authority than self-review) and should satisfy T1.
    """

    def test_tier_1_ho_reviewed_passes(self, ci_environment, monkeypatch):
        """'HO REVIEWED: delegated to IL, verified output' should pass T1."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [{"body": "HO REVIEWED: delegated to IL, verified output"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is True, "'HO REVIEWED' should satisfy T1"
        assert "HO supervisory review found" in message

    def test_tier_1_ho_reviewed_with_model_format(self, ci_environment, monkeypatch):
        """'HO (Claude): REVIEWED: verified' should also pass T1."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [{"body": "HO (Claude): REVIEWED: verified"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is True, "'HO (Claude): REVIEWED' should satisfy T1"
        assert "HO supervisory review found" in message

    def test_tier_1_il_self_reviewed_still_passes(self, ci_environment, monkeypatch):
        """Existing IL SELF-REVIEWED must still pass T1 after HO REVIEWED addition."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [{"body": "IL SELF-REVIEWED: Fixed typo in error message"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is True, "IL SELF-REVIEWED must still pass T1"
        assert "Self-review found" in message

    def test_tier_1_ho_reviewed_in_pr_body(self, ci_environment, monkeypatch):
        """HO REVIEWED in PR body should also satisfy T1."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "HO REVIEWED: delegated implementation verified",
                        "comments": [],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is True, "HO REVIEWED in PR body should satisfy T1"

    def test_tier_1_crs_still_satisfies_after_ho_addition(self, ci_environment, monkeypatch):
        """CRS approval should still satisfy T1 (hierarchy rule preserved)."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [{"body": "CRS APPROVED: Logic correct, tests pass"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is True, "CRS approval should still satisfy T1"
        assert "CRS approval satisfies" in message


@pytest.mark.behavior
class TestFlexiblePatternMatching:
    """Validate flexible approval pattern matching beyond exact string match."""

    def test_crs_parenthetical_model_format(self, ci_environment, monkeypatch):
        """'CRS (Gemini): APPROVED' format should be recognized at TIER_2."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "CRS (Gemini): APPROVED - Logic correct, tests pass",
                        "comments": [{"body": "CE APPROVED: Architecture sound"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, "'CRS (Gemini): APPROVED' + CE should be recognized"

    def test_ce_parenthetical_model_format(self, ci_environment, monkeypatch):
        """'CE (Claude): APPROVED' format should be recognized at TIER_3."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS (Gemini) APPROVED: ok"},
                            {"body": "CRS (Codex) APPROVED: verified"},
                            {"body": "CE (Claude): APPROVED - Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_STRICT")
        assert approved is True, "'CE (Claude): APPROVED' with dual CRS should be recognized"

    def test_crs_with_extra_whitespace(self, ci_environment, monkeypatch):
        """Patterns with varied whitespace should still match."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "CRS  APPROVED: Logic correct",
                        "comments": [{"body": "CE APPROVED: Sound"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, "CRS APPROVED with extra whitespace should match"

    def test_il_parenthetical_model_format(self, ci_environment, monkeypatch):
        """'IL (Claude): SELF-REVIEWED' format should be recognized."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "IL (Claude): SELF-REVIEWED: Quick fix",
                        "comments": [],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is True, "'IL (Claude): SELF-REVIEWED' should be recognized"

    def test_original_exact_format_still_works(self, ci_environment, monkeypatch):
        """Original exact format 'CRS APPROVED:' must continue to work at TIER_2."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS APPROVED: Logic correct, tests pass"},
                            {"body": "CE APPROVED: Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, "Original exact format must continue to work"


@pytest.mark.behavior
class TestSubstringFalsePositivePrevention:
    """Regression tests for CRS MEDIUM finding: keyword substring false positive.

    The keyword 'APPROVED' could match as a substring of longer words like
    'APPROVEDLY' or 'APPROVEDISH'. The approval regex must use word boundaries
    after the keyword to prevent such false positives. Note: prefix substrings
    like 'DISAPPROVED' are already prevented by the regex structure (the prefix
    must be followed by whitespace then the keyword), but suffix substrings
    require an explicit word boundary.
    """

    def test_approved_suffix_word_does_not_match(self):
        """REGRESSION: 'CRS APPROVEDLY' must NOT match as 'CRS APPROVED'."""
        result = validate_review._matches_approval_pattern(
            "CRS APPROVEDLY noted", "CRS", "APPROVED"
        )
        assert (
            result is False
        ), "APPROVEDLY must not match as APPROVED - suffix substring false positive"

    def test_approved_suffix_compound_does_not_match(self):
        """REGRESSION: 'CRS APPROVEDISH' must NOT match as approval."""
        result = validate_review._matches_approval_pattern(
            "CRS APPROVEDISH maybe", "CRS", "APPROVED"
        )
        assert (
            result is False
        ), "APPROVEDISH must not match as APPROVED - suffix substring false positive"

    def test_disapproved_does_not_match_as_approval(self):
        """REGRESSION: 'CRS DISAPPROVED' must NOT match as 'CRS APPROVED'."""
        result = validate_review._matches_approval_pattern(
            "CRS DISAPPROVED: This change has issues", "CRS", "APPROVED"
        )
        assert result is False, "DISAPPROVED must not match as APPROVED"

    def test_disapproved_with_parenthetical_does_not_match(self):
        """REGRESSION: 'CRS (Gemini): DISAPPROVED' must NOT match as approval."""
        result = validate_review._matches_approval_pattern(
            "CRS (Gemini): DISAPPROVED - Rejected", "CRS", "APPROVED"
        )
        assert result is False, "Parenthetical DISAPPROVED must not match as APPROVED"

    def test_approved_still_matches_after_fix(self):
        """Sanity check: 'CRS APPROVED' must still match after word boundary fix."""
        result = validate_review._matches_approval_pattern(
            "CRS APPROVED: Logic correct", "CRS", "APPROVED"
        )
        assert result is True, "APPROVED must still match after word boundary fix"

    def test_approved_with_colon_suffix_still_matches(self):
        """Sanity check: 'APPROVED:' (with colon) must still match with word boundary."""
        result = validate_review._matches_approval_pattern(
            "CRS APPROVED: tests pass", "CRS", "APPROVED"
        )
        assert result is True, "APPROVED followed by colon must still match"

    def test_approved_at_end_of_line_still_matches(self):
        """Sanity check: 'CRS APPROVED' at end of string must still match."""
        result = validate_review._matches_approval_pattern("CRS APPROVED", "CRS", "APPROVED")
        assert result is True, "APPROVED at end of string must still match"

    def test_ce_disapproved_does_not_match(self):
        """REGRESSION: 'CE DISAPPROVED' must NOT match as 'CE APPROVED'."""
        result = validate_review._matches_approval_pattern(
            "CE DISAPPROVED: Architecture concerns", "CE", "APPROVED"
        )
        assert result is False, "CE DISAPPROVED must not match as CE APPROVED"


@pytest.mark.behavior
class TestGoKeywordApproval:
    """Validate that 'GO' is accepted as an approval synonym alongside 'APPROVED'.

    Agents sometimes write 'CRS (Gemini): GO (9/10)' or 'CE (Codex): GO after fix'
    instead of the standard 'APPROVED' keyword. Both must be accepted for CRS and CE
    tiers. TIER_1_SELF (IL SELF-REVIEWED) is NOT affected.
    """

    def test_crs_go_matches_as_crs_approval(self, ci_environment, monkeypatch):
        """'CRS (Gemini): GO' should match as CRS approval at TIER_2."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "CRS (Gemini): GO",
                        "comments": [{"body": "CE APPROVED: Sound"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, "'CRS (Gemini): GO' + CE should be recognized"

    def test_ce_go_after_fix_matches_as_ce_approval(self, ci_environment, monkeypatch):
        """'CE (Codex): GO after fix' should match as CE approval at TIER_3."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS (Gemini) APPROVED: ok"},
                            {"body": "CRS (Codex) APPROVED: verified"},
                            {"body": "CE (Codex): GO after fix"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_STRICT")
        assert approved is True, "'CE (Codex): GO after fix' with dual CRS should pass"

    def test_crs_go_with_score_matches(self, ci_environment, monkeypatch):
        """'CRS (Gemini): GO (9/10)' should match -- the real-world failing case."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "CRS (Gemini): GO (9/10)",
                        "comments": [{"body": "CE APPROVED: Sound"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, "'CRS (Gemini): GO (9/10)' + CE should pass"

    def test_tier_3_dual_crs_go_plus_ce_approved_passes(self, ci_environment, monkeypatch):
        """TIER_3_STRICT with dual CRS GO + CE APPROVED should pass."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS (Gemini): GO (9/10)"},
                            {"body": "CRS (Codex): GO (8/10)"},
                            {"body": "CE APPROVED: Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_STRICT")
        assert approved is True, "Dual CRS GO + CE APPROVED should satisfy TIER_3_STRICT"
        assert "Dual CRS" in message

    def test_tier_3_dual_crs_approved_plus_ce_go_passes(self, ci_environment, monkeypatch):
        """TIER_3_STRICT with dual CRS APPROVED + CE GO should pass."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS (Gemini) APPROVED: Logic correct"},
                            {"body": "CRS (Codex) APPROVED: Verified"},
                            {"body": "CE (Codex): GO - looks good"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_STRICT")
        assert approved is True, "Dual CRS APPROVED + CE GO should satisfy TIER_3_STRICT"
        assert "Dual CRS" in message

    def test_go_substring_does_not_false_positive(self):
        """'CRS GOING' must NOT match as 'CRS GO' -- word boundary enforcement."""
        result = validate_review._matches_approval_pattern("CRS GOING ahead", "CRS", "GO")
        assert result is False, "GOING must not match as GO - suffix substring false positive"

    def test_tier_3_missing_all_mentions_models_in_error(self, ci_environment, monkeypatch):
        """Error message for TIER_3_STRICT missing approvals should mention model names."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [{"body": "Some other comment"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_STRICT")
        assert approved is False
        assert "Gemini" in message, "Error message should mention Gemini model"
        assert "Codex" in message, "Error message should mention Codex model"
        assert "CE" in message, "Error message should mention CE"

    def test_tier_2_missing_mentions_go_in_error(self, ci_environment, monkeypatch):
        """Error message for TIER_2_STANDARD missing approval should mention GO as alternative."""

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [{"body": "Some other comment"}],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is False
        assert "GO" in message, "Error message should mention GO as an accepted format"


@pytest.mark.behavior
class TestFlexibleSeparatorMatching:
    """Validate that em dash, en dash, hyphen, and colon separators are accepted.

    Real-world approval text uses varied separators between the prefix/parenthetical
    and the keyword. For example:
      - 'CRS (Gemini) \u2014 APPROVED (98/100)' (em dash U+2014)
      - 'CE (Codex) \u2014 APPROVED (GO)' (em dash)
      - 'CRS (Gemini) \u2013 APPROVED' (en dash U+2013)
      - 'CRS (Gemini) - APPROVED' (hyphen)
      - 'CRS \u2014 APPROVED' (em dash, no parenthetical)
      - 'CRS: APPROVED' (colon, no parenthetical)

    The regex must handle any mix of whitespace, colons, and dashes as separators.
    """

    # --- Em dash separator (the actual failing case from issue #213) ---

    def test_crs_em_dash_with_parenthetical_approved(self):
        """'CRS (Gemini) \u2014 APPROVED (98/100)' must match -- the real-world failing case."""
        result = validate_review._matches_approval_pattern(
            "CRS (Gemini) \u2014 APPROVED (98/100)", "CRS", "APPROVED"
        )
        assert result is True, "Em dash separator with parenthetical must match"

    def test_ce_em_dash_with_parenthetical_approved_go(self):
        """'CE (Codex) \u2014 APPROVED (GO)' must match for APPROVED keyword."""
        result = validate_review._matches_approval_pattern(
            "CE (Codex) \u2014 APPROVED (GO)", "CE", "APPROVED"
        )
        assert result is True, "Em dash separator CE with parenthetical must match"

    def test_crs_em_dash_no_parenthetical(self):
        """'CRS \u2014 APPROVED' must match (no model annotation, em dash separator)."""
        result = validate_review._matches_approval_pattern("CRS \u2014 APPROVED", "CRS", "APPROVED")
        assert result is True, "Em dash separator without parenthetical must match"

    def test_crs_em_dash_go_keyword(self):
        """'CRS (Gemini) \u2014 GO (9/10)' must match for GO keyword."""
        result = validate_review._matches_approval_pattern(
            "CRS (Gemini) \u2014 GO (9/10)", "CRS", "GO"
        )
        assert result is True, "Em dash separator with GO keyword must match"

    # --- En dash separator (defensive) ---

    def test_crs_en_dash_with_parenthetical(self):
        """'CRS (Gemini) \u2013 APPROVED' must match (en dash separator)."""
        result = validate_review._matches_approval_pattern(
            "CRS (Gemini) \u2013 APPROVED", "CRS", "APPROVED"
        )
        assert result is True, "En dash separator with parenthetical must match"

    def test_crs_en_dash_no_parenthetical(self):
        """'CRS \u2013 APPROVED' must match (en dash, no parenthetical)."""
        result = validate_review._matches_approval_pattern("CRS \u2013 APPROVED", "CRS", "APPROVED")
        assert result is True, "En dash separator without parenthetical must match"

    # --- Hyphen separator (defensive) ---

    def test_crs_hyphen_with_parenthetical(self):
        """'CRS (Gemini) - APPROVED' must match (hyphen separator)."""
        result = validate_review._matches_approval_pattern(
            "CRS (Gemini) - APPROVED", "CRS", "APPROVED"
        )
        assert result is True, "Hyphen separator with parenthetical must match"

    def test_crs_hyphen_no_parenthetical(self):
        """'CRS - APPROVED' must match (hyphen, no parenthetical)."""
        result = validate_review._matches_approval_pattern("CRS - APPROVED", "CRS", "APPROVED")
        assert result is True, "Hyphen separator without parenthetical must match"

    # --- Colon separator without parenthetical ---

    def test_crs_colon_no_parenthetical(self):
        """'CRS: APPROVED' must match (colon separator, no parenthetical)."""
        result = validate_review._matches_approval_pattern("CRS: APPROVED", "CRS", "APPROVED")
        assert result is True, "Colon separator without parenthetical must match"

    # --- IL / SELF-REVIEWED with dash separators ---

    def test_il_em_dash_self_reviewed(self):
        """'IL (Claude) \u2014 SELF-REVIEWED' must match."""
        result = validate_review._matches_approval_pattern(
            "IL (Claude) \u2014 SELF-REVIEWED: quick fix", "IL", "SELF-REVIEWED"
        )
        assert result is True, "IL with em dash separator must match SELF-REVIEWED"

    # --- Negative cases: separators must not cause false positives ---

    def test_approved_suffix_with_em_dash_does_not_false_positive(self):
        """'CRS (Gemini) \u2014 APPROVEDLY' must NOT match (word boundary still enforced)."""
        result = validate_review._matches_approval_pattern(
            "CRS (Gemini) \u2014 APPROVEDLY noted", "CRS", "APPROVED"
        )
        assert result is False, "Word boundary must still prevent suffix false positives"

    def test_going_with_em_dash_does_not_false_positive(self):
        """'CRS \u2014 GOING' must NOT match as GO."""
        result = validate_review._matches_approval_pattern("CRS \u2014 GOING ahead", "CRS", "GO")
        assert result is False, "Word boundary must still prevent GOING matching as GO"


@pytest.mark.security
class TestCRSModelApprovalSpoofing:
    """Regression tests for CE review finding: approval-spoofing bypass.

    has_crs_model_approval() must not allow:
    1. Single-line dual-model spoof: one APPROVED keyword satisfying two model checks
    2. BLOCKED-then-APPROVED on same line: intervening BLOCKED before APPROVED
    """

    def test_single_line_dual_model_spoof_does_not_satisfy_both(self):
        """SECURITY: 'CRS (Gemini) and CRS (Codex) APPROVED' must NOT satisfy both models.

        A single APPROVED keyword at the end of a line must not count as approval
        for both CRS (Gemini) and CRS (Codex) when both appear earlier on that line.
        """
        texts = ["CRS (Gemini) and CRS (Codex) APPROVED"]
        gemini_approved = validate_review._has_crs_model_approval(texts, "Gemini")
        codex_approved = validate_review._has_crs_model_approval(texts, "Codex")
        assert not (
            gemini_approved and codex_approved
        ), "Single APPROVED must not satisfy both CRS (Gemini) and CRS (Codex)"

    def test_blocked_then_approved_on_same_line_does_not_pass(self):
        """SECURITY: 'CRS (Gemini) BLOCKED but later APPROVED' must NOT pass.

        If BLOCKED appears between the model tag and APPROVED, the function must
        not treat this as an approval. Only direct CRS(model) -> APPROVED with
        separator-only tokens in between should count.
        """
        texts = ["CRS (Gemini) BLOCKED but later APPROVED"]
        result = validate_review._has_crs_model_approval(texts, "Gemini")
        assert result is False, "BLOCKED-then-APPROVED must not count as model approval"

    def test_legitimate_separate_line_approvals_still_work(self):
        """Sanity: Separate per-model approval lines must still pass."""
        texts = [
            "CRS (Gemini) APPROVED: Logic correct",
            "CRS (Codex) APPROVED: Verified",
        ]
        assert validate_review._has_crs_model_approval(
            texts, "Gemini"
        ), "Separate Gemini approval line must pass"
        assert validate_review._has_crs_model_approval(
            texts, "Codex"
        ), "Separate Codex approval line must pass"

    def test_model_approval_with_separator_still_works(self):
        """Sanity: 'CRS (Gemini): APPROVED' with colon separator must still pass."""
        texts = ["CRS (Gemini): APPROVED - Logic verified"]
        assert validate_review._has_crs_model_approval(
            texts, "Gemini"
        ), "Colon-separated model approval must pass"

    def test_model_approval_with_go_keyword_still_works(self):
        """Sanity: 'CRS (Gemini) GO' must still pass."""
        texts = ["CRS (Gemini) GO (9/10)"]
        assert validate_review._has_crs_model_approval(
            texts, "Gemini"
        ), "GO keyword model approval must pass"

    def test_model_approval_with_dash_separator_still_works(self):
        """Sanity: 'CRS (Gemini) - APPROVED' with dash separator must still pass."""
        texts = ["CRS (Gemini) - APPROVED: Architecture sound"]
        assert validate_review._has_crs_model_approval(
            texts, "Gemini"
        ), "Dash-separated model approval must pass"

    def test_model_approval_with_em_dash_still_works(self):
        """Sanity: 'CRS (Gemini) \u2014 APPROVED' with em dash must still pass."""
        texts = ["CRS (Gemini) \u2014 APPROVED (98/100)"]
        assert validate_review._has_crs_model_approval(
            texts, "Gemini"
        ), "Em dash-separated model approval must pass"

    def test_model_approval_with_double_dash_still_works(self):
        """Sanity: 'CRS (Gemini) -- APPROVED' with double dash must still pass."""
        texts = ["CRS (Gemini) -- APPROVED: Logic verified"]
        assert validate_review._has_crs_model_approval(
            texts, "Gemini"
        ), "Double-dash-separated model approval must pass"
