"""
RED phase tests for 5-tier review system expansion in validate_review.py.

These tests define the contract for:
- New T1 threshold (<10 lines, not <50)
- T1 security path and new test file guards
- T2 range change (10-500 lines)
- T3 trigger expansion (base class, security, tools, MCP endpoints)
- Tier name changes (TIER_3_CRITICAL, TIER_4_STRATEGIC)
- New approval requirements per tier (TMG, CIV, PE roles)

Source of truth: review-requirements.oct.md v2.0 (5-tier system)

Tests MUST FAIL until production code is updated.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import validate_review


@pytest.fixture
def ci_environment(monkeypatch):
    """Set up CI environment variables."""
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("GITHUB_BASE_REF", "origin/main")
    monkeypatch.setenv("PR_NUMBER", "999")


# ---------------------------------------------------------------------------
# 1. T1 threshold change: <10 lines (was <50)
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTier1ThresholdChange:
    """T1 threshold must be <10 lines (was <50 in old system)."""

    def test_9_lines_single_file_is_tier_1(self) -> None:
        """9 lines changed in single non-exempt file = TIER_1_SELF."""
        files = [{"path": "src/utils.py", "added": 5, "deleted": 4, "total_changed": 9}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_1_SELF", f"9 lines in single file should be T1, got {tier}"

    def test_10_lines_single_file_is_not_tier_1(self) -> None:
        """10 lines changed should be TIER_2_STANDARD, not TIER_1_SELF.

        The governance rule says T1 is non_exempt_lines<10, so 10 lines
        should NOT qualify for self-review.
        """
        files = [{"path": "src/utils.py", "added": 6, "deleted": 4, "total_changed": 10}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_2_STANDARD", f"10 lines should be T2, got {tier}"

    def test_30_lines_single_file_is_not_tier_1(self) -> None:
        """30 lines changed must NOT be TIER_1_SELF under new <10 threshold.

        This was previously T1 under the <50 threshold. Under the new system
        it must be T2 (10-500 lines).
        """
        files = [{"path": "src/utils.py", "added": 20, "deleted": 10, "total_changed": 30}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier != "TIER_1_SELF", f"30 lines must NOT be T1 under new threshold, got {tier}"
        assert tier == "TIER_2_STANDARD", f"30 lines should be T2, got {tier}"

    def test_49_lines_single_file_is_tier_2_not_tier_1(self) -> None:
        """49 lines was T1 under old system but must be T2 under new <10 threshold."""
        files = [{"path": "src/utils.py", "added": 30, "deleted": 19, "total_changed": 49}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_2_STANDARD", f"49 lines must be T2 under new threshold, got {tier}"

    def test_1_line_single_file_is_tier_1(self) -> None:
        """1 line changed in single file = TIER_1_SELF."""
        files = [{"path": "src/config.py", "added": 1, "deleted": 0, "total_changed": 1}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_1_SELF", f"1 line should be T1, got {tier}"


# ---------------------------------------------------------------------------
# 2. T1 with security paths -- must be upgraded
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTier1SecurityPathUpgrade:
    """T1 self-review must be denied when security-touching paths are changed."""

    def test_small_change_in_auth_path_not_tier_1(self) -> None:
        """<10 lines in auth path must NOT be TIER_1_SELF (security guard).

        The governance rule says T1 requires no_security_paths. Changes to
        auth-related files must always get a higher tier review.
        """
        files = [
            {"path": "src/hestai_mcp/auth/handler.py", "added": 3, "deleted": 2, "total_changed": 5}
        ]
        tier, _ = validate_review.determine_review_tier(files)
        assert (
            tier != "TIER_1_SELF"
        ), f"Security-touching path (auth) must NOT be T1 self-review, got {tier}"

    def test_small_change_in_session_management_not_tier_1(self) -> None:
        """<10 lines in session management must NOT be TIER_1_SELF."""
        files = [
            {
                "path": "src/hestai_mcp/session/manager.py",
                "added": 2,
                "deleted": 1,
                "total_changed": 3,
            }
        ]
        tier, _ = validate_review.determine_review_tier(files)
        assert (
            tier != "TIER_1_SELF"
        ), f"Security-touching path (session) must NOT be T1 self-review, got {tier}"

    def test_small_change_in_env_vars_handling_not_tier_1(self) -> None:
        """<10 lines changing env var handling must NOT be TIER_1_SELF."""
        files = [
            {"path": "src/hestai_mcp/config/env.py", "added": 3, "deleted": 0, "total_changed": 3}
        ]
        tier, _ = validate_review.determine_review_tier(files)
        assert (
            tier != "TIER_1_SELF"
        ), f"Security-touching path (env) must NOT be T1 self-review, got {tier}"


# ---------------------------------------------------------------------------
# 3. T1 with new test files -- must be upgraded
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTier1NewTestFileUpgrade:
    """T1 self-review must be denied when new test files are included.

    Per governance rule: T1 requires no_new_test_files. New test files
    indicate substantive changes that require TMG review at T2+.
    """

    def test_small_change_with_new_test_file_not_tier_1(self) -> None:
        """<10 lines but including a new test file must NOT be TIER_1_SELF.

        New tests indicate functional changes that need TMG review.
        """
        files = [
            {"path": "src/utils.py", "added": 3, "deleted": 0, "total_changed": 3},
            {"path": "tests/test_utils.py", "added": 5, "deleted": 0, "total_changed": 5},
        ]
        # Note: tests are exempt in the current system, but the governance rule
        # says "includes_new_test_files" should trigger T2. The file count check
        # for T1 already requires single_non_exempt_file, but the governance rule
        # also explicitly guards against new test files in non-exempt calculation.
        # This test checks the intent: new tests present -> not T1.
        tier, _ = validate_review.determine_review_tier(files)
        assert (
            tier != "TIER_1_SELF"
        ), f"PR with new test files must NOT be T1 self-review, got {tier}"


# ---------------------------------------------------------------------------
# 4. T2 range: 10-500 lines
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTier2Range:
    """T2 must cover 10-500 lines (was 50-500)."""

    def test_10_lines_is_tier_2(self) -> None:
        """10 lines = lower bound of T2."""
        files = [{"path": "src/core.py", "added": 6, "deleted": 4, "total_changed": 10}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_2_STANDARD", f"10 lines should be T2, got {tier}"

    def test_15_lines_is_tier_2(self) -> None:
        """15 lines = within T2 range."""
        files = [{"path": "src/core.py", "added": 10, "deleted": 5, "total_changed": 15}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_2_STANDARD", f"15 lines should be T2, got {tier}"

    def test_500_lines_is_tier_2(self) -> None:
        """500 lines = upper bound of T2."""
        files = [{"path": "src/core.py", "added": 300, "deleted": 200, "total_changed": 500}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_2_STANDARD", f"500 lines should be T2, got {tier}"

    def test_multiple_files_in_range_is_tier_2(self) -> None:
        """Multiple non-exempt files with total 10-500 lines = T2."""
        files = [
            {"path": "src/a.py", "added": 5, "deleted": 0, "total_changed": 5},
            {"path": "src/b.py", "added": 10, "deleted": 0, "total_changed": 10},
        ]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_2_STANDARD", f"Multiple files 15 lines should be T2, got {tier}"


# ---------------------------------------------------------------------------
# 5. T3 triggers
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTier3Triggers:
    """All T3 triggers from governance rule must produce TIER_3_CRITICAL."""

    def test_over_500_lines_is_tier_3_critical(self) -> None:
        """>500 lines must trigger TIER_3_CRITICAL."""
        files = [{"path": "src/core.py", "added": 400, "deleted": 200, "total_changed": 600}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_3_CRITICAL", f">500 lines should be TIER_3_CRITICAL, got {tier}"

    def test_base_class_change_is_tier_3(self) -> None:
        """Changes to base class files must trigger T3.

        Per governance: touches_base_class[**/base.py,**/shared/**,abstract_classes]
        """
        files = [{"path": "src/hestai_mcp/base.py", "added": 10, "deleted": 5, "total_changed": 15}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_3_CRITICAL", f"Base class change should be TIER_3_CRITICAL, got {tier}"

    def test_shared_module_change_is_tier_3(self) -> None:
        """Changes to shared modules must trigger T3.

        Per governance: touches_base_class[**/shared/**]
        """
        files = [
            {
                "path": "src/hestai_mcp/modules/tools/shared/utils.py",
                "added": 10,
                "deleted": 5,
                "total_changed": 15,
            }
        ]
        tier, _ = validate_review.determine_review_tier(files)
        assert (
            tier == "TIER_3_CRITICAL"
        ), f"Shared module change should be TIER_3_CRITICAL, got {tier}"

    def test_security_touching_code_is_tier_3(self) -> None:
        """Security-touching code must trigger T3.

        Per governance: touches_security[auth,path_handling,session_management,env_vars]
        """
        files = [
            {
                "path": "src/hestai_mcp/auth/handler.py",
                "added": 50,
                "deleted": 20,
                "total_changed": 70,
            }
        ]
        tier, _ = validate_review.determine_review_tier(files)
        assert (
            tier == "TIER_3_CRITICAL"
        ), f"Security-touching code should be TIER_3_CRITICAL, got {tier}"

    def test_new_tool_addition_is_tier_3(self) -> None:
        """New tool addition must trigger T3.

        Per governance: is_new_tool[tools/**,clink/agents/**]
        """
        files = [
            {
                "path": "src/hestai_mcp/modules/tools/new_tool.py",
                "added": 50,
                "deleted": 0,
                "total_changed": 50,
            }
        ]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_3_CRITICAL", f"New tool addition should be TIER_3_CRITICAL, got {tier}"

    def test_new_mcp_endpoint_is_tier_3(self) -> None:
        """New MCP endpoint must trigger T3.

        Per governance: is_new_mcp_endpoint[mcp/tools/**]
        """
        files = [
            {
                "path": "src/hestai_mcp/mcp/tools/new_endpoint.py",
                "added": 40,
                "deleted": 0,
                "total_changed": 40,
            }
        ]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_3_CRITICAL", f"New MCP endpoint should be TIER_3_CRITICAL, got {tier}"

    def test_sql_change_is_tier_3(self) -> None:
        """SQL file changes must trigger T3."""
        files = [{"path": "migrations/001.sql", "added": 20, "deleted": 5, "total_changed": 25}]
        tier, _ = validate_review.determine_review_tier(files)
        assert tier == "TIER_3_CRITICAL", f"SQL change should be TIER_3_CRITICAL, got {tier}"


# ---------------------------------------------------------------------------
# 6. Tier name changes
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTierNameChanges:
    """Tier names must match the new 5-tier system naming."""

    def test_tier_3_returns_critical_not_strict(self) -> None:
        """determine_review_tier must return TIER_3_CRITICAL, not TIER_3_STRICT.

        The old system used TIER_3_STRICT. The new 5-tier system renames
        this to TIER_3_CRITICAL per the governance rule.
        """
        files = [{"path": "src/core.py", "added": 400, "deleted": 200, "total_changed": 600}]
        tier, _ = validate_review.determine_review_tier(files)
        assert "STRICT" not in tier, f"TIER_3_STRICT is deprecated, got {tier}"
        assert tier == "TIER_3_CRITICAL", f"Must return TIER_3_CRITICAL, got {tier}"

    def test_tier_4_strategic_name(self) -> None:
        """TIER_4_STRATEGIC must be a recognized tier value.

        This tier is manual-only (triggered by /review --strategic or
        explicit tier override), so determine_review_tier won't auto-detect it.
        But the tier constant must exist and be usable.
        """
        from hestai_mcp.modules.tools.shared.review_formats import TIER_4_STRATEGIC

        assert TIER_4_STRATEGIC == "TIER_4_STRATEGIC"


# ---------------------------------------------------------------------------
# 7. T2 approval checking: TMG + CRS + CE
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTier2ApprovalRequirements:
    """TIER_2_STANDARD must require TMG + CRS + CE approval (was CRS + CE)."""

    def test_tier_2_with_tmg_crs_ce_passes(self, ci_environment, monkeypatch) -> None:
        """T2 with TMG + CRS + CE approvals must pass."""
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "TMG APPROVED: tests cover critical paths"},
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is True, f"T2 with TMG+CRS+CE should pass, got: {message}"

    def test_tier_2_without_tmg_fails(self, ci_environment, monkeypatch) -> None:
        """T2 with only CRS + CE (no TMG) must FAIL.

        Under the old system, CRS+CE was sufficient for T2.
        Under the new 5-tier system, TMG is also required.
        """
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_2_STANDARD")
        assert approved is False, f"T2 without TMG should fail under 5-tier system, got: {message}"
        assert "TMG" in message, f"Error message should mention missing TMG, got: {message}"


# ---------------------------------------------------------------------------
# 8. T3 approval checking: TMG + CRS + CE + CIV
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTier3ApprovalRequirements:
    """TIER_3_CRITICAL must require TMG + CRS + CE + CIV approval."""

    def test_tier_3_with_tmg_crs_ce_civ_passes(self, ci_environment, monkeypatch) -> None:
        """T3 with TMG + CRS + CE + CIV approvals must pass."""
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "TMG APPROVED: tests cover critical paths"},
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                            {"body": "CIV APPROVED: Implementation matches spec"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_CRITICAL")
        assert approved is True, f"T3 with TMG+CRS+CE+CIV should pass, got: {message}"

    def test_tier_3_without_civ_fails(self, ci_environment, monkeypatch) -> None:
        """T3 with TMG + CRS + CE but no CIV must FAIL."""
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "TMG APPROVED: tests cover critical paths"},
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_CRITICAL")
        assert approved is False, f"T3 without CIV should fail, got: {message}"
        assert "CIV" in message, f"Error message should mention missing CIV, got: {message}"

    def test_tier_3_without_tmg_fails(self, ci_environment, monkeypatch) -> None:
        """T3 with CRS + CE + CIV but no TMG must FAIL."""
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                            {"body": "CIV APPROVED: Implementation valid"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_3_CRITICAL")
        assert approved is False, f"T3 without TMG should fail, got: {message}"
        assert "TMG" in message, f"Error message should mention missing TMG, got: {message}"


# ---------------------------------------------------------------------------
# 9. T4 approval checking: TMG + CRS + CE + CIV + PE
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTier4ApprovalRequirements:
    """TIER_4_STRATEGIC must require TMG + CRS + CE + CIV + PE approval."""

    def test_tier_4_with_all_five_passes(self, ci_environment, monkeypatch) -> None:
        """T4 with TMG + CRS + CE + CIV + PE approvals must pass."""
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "TMG APPROVED: tests comprehensive"},
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                            {"body": "CIV APPROVED: Implementation matches spec"},
                            {"body": "PE APPROVED: Architecture sound for 6 months"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_4_STRATEGIC")
        assert approved is True, f"T4 with TMG+CRS+CE+CIV+PE should pass, got: {message}"

    def test_tier_4_without_pe_fails(self, ci_environment, monkeypatch) -> None:
        """T4 with TMG + CRS + CE + CIV but no PE must FAIL."""
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "TMG APPROVED: tests comprehensive"},
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                            {"body": "CIV APPROVED: Implementation matches spec"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_4_STRATEGIC")
        assert approved is False, f"T4 without PE should fail, got: {message}"
        assert "PE" in message, f"Error message should mention missing PE, got: {message}"

    def test_tier_4_without_civ_fails(self, ci_environment, monkeypatch) -> None:
        """T4 with TMG + CRS + CE + PE but no CIV must FAIL."""
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "TMG APPROVED: tests comprehensive"},
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                            {"body": "PE APPROVED: Sustainable"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_4_STRATEGIC")
        assert approved is False, f"T4 without CIV should fail, got: {message}"
        assert "CIV" in message, f"Error message should mention missing CIV, got: {message}"

    def test_tier_4_with_only_crs_ce_fails(self, ci_environment, monkeypatch) -> None:
        """T4 with only CRS + CE (no TMG, CIV, PE) must FAIL."""
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            return MagicMock(
                stdout=json.dumps(
                    {
                        "body": "",
                        "comments": [
                            {"body": "CRS APPROVED: Logic correct"},
                            {"body": "CE APPROVED: Architecture sound"},
                        ],
                    }
                ),
                returncode=0,
                check=lambda: None,
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        approved, message = validate_review.check_pr_comments("TIER_4_STRATEGIC")
        assert approved is False, f"T4 with only CRS+CE should fail, got: {message}"
