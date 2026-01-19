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
        approved, message = validate_review.check_pr_comments("TIER_2_CRS")
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
        approved, message = validate_review.check_pr_comments("TIER_2_CRS")
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
        """TIER_2_CRS for 50-500 lines."""
        files = [{"path": "src/core.py", "added": 100, "deleted": 50, "total_changed": 150}]
        tier, reason = validate_review.determine_review_tier(files)
        assert tier == "TIER_2_CRS"

    def test_tier_3_full_for_large_changes(self):
        """TIER_3_FULL for >500 lines."""
        files = [{"path": "src/core.py", "added": 400, "deleted": 200, "total_changed": 600}]
        tier, reason = validate_review.determine_review_tier(files)
        assert tier == "TIER_3_FULL"

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
        """TIER_1_SELF requires 'IL SELF-REVIEWED:' comment."""

        # Mock gh CLI to return comments without self-review
        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps({"comments": [{"body": "Some other comment"}]}),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_1_SELF")
        assert approved is False
        assert "SELF-REVIEWED" in message

    def test_tier_2_requires_crs_approval(self, ci_environment, monkeypatch):
        """TIER_2_CRS requires 'CRS APPROVED:' comment."""

        # Mock gh CLI to return comments with CRS approval
        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {"comments": [{"body": "CRS APPROVED: Logic correct, tests pass"}]}
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_CRS")
        assert approved is True
        assert "CRS approval found" in message

    def test_tier_3_requires_both_crs_and_ce(self, ci_environment, monkeypatch):
        """TIER_3_FULL requires both 'CRS APPROVED:' and 'CE APPROVED:' comments."""

        # Mock gh CLI to return comments with only CRS approval
        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps({"comments": [{"body": "CRS APPROVED: Logic correct"}]}),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_FULL")
        assert approved is False
        assert "CE APPROVED" in message
