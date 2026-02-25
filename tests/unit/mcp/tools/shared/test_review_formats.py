"""
Tests for shared review format constants and pattern matching.

TDD RED phase: These tests define the contract for review_formats module.
Tests written FIRST before implementation exists.

Coverage:
- Review tier constants
- matches_approval_pattern() with all supported formats
- Format generation produces valid patterns
- Edge cases: markdown bold, extra whitespace, model annotations
- Helper functions: has_crs_approval, has_ce_approval, has_il_self_review
"""

import pytest


@pytest.mark.unit
class TestReviewTierConstants:
    """Test that tier constants are defined correctly."""

    def test_tier_0_exempt_value(self) -> None:
        """TIER_0_EXEMPT constant exists and has correct value."""
        from hestai_mcp.modules.tools.shared.review_formats import TIER_0_EXEMPT

        assert TIER_0_EXEMPT == "TIER_0_EXEMPT"

    def test_tier_1_self_value(self) -> None:
        """TIER_1_SELF constant exists and has correct value."""
        from hestai_mcp.modules.tools.shared.review_formats import TIER_1_SELF

        assert TIER_1_SELF == "TIER_1_SELF"

    def test_tier_2_crs_value(self) -> None:
        """TIER_2_STANDARD constant exists and has correct value."""
        from hestai_mcp.modules.tools.shared.review_formats import TIER_2_STANDARD

        assert TIER_2_STANDARD == "TIER_2_STANDARD"

    def test_tier_3_full_value(self) -> None:
        """TIER_3_STRICT constant exists and has correct value."""
        from hestai_mcp.modules.tools.shared.review_formats import TIER_3_STRICT

        assert TIER_3_STRICT == "TIER_3_STRICT"

    def test_valid_roles_contains_expected(self) -> None:
        """VALID_ROLES includes CRS, CE, IL."""
        from hestai_mcp.modules.tools.shared.review_formats import VALID_ROLES

        assert "CRS" in VALID_ROLES
        assert "CE" in VALID_ROLES
        assert "IL" in VALID_ROLES

    def test_valid_verdicts_contains_expected(self) -> None:
        """VALID_VERDICTS includes APPROVED, BLOCKED, CONDITIONAL."""
        from hestai_mcp.modules.tools.shared.review_formats import VALID_VERDICTS

        assert "APPROVED" in VALID_VERDICTS
        assert "BLOCKED" in VALID_VERDICTS
        assert "CONDITIONAL" in VALID_VERDICTS


@pytest.mark.unit
class TestMatchesApprovalPattern:
    """Test the pattern matching function extracted from validate_review.py."""

    def test_exact_crs_approved(self) -> None:
        """Matches 'CRS APPROVED: assessment text'."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("CRS APPROVED: Looks good", "CRS", "APPROVED")

    def test_exact_ce_approved(self) -> None:
        """Matches 'CE APPROVED: assessment text'."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("CE APPROVED: Architecture sound", "CE", "APPROVED")

    def test_il_self_reviewed(self) -> None:
        """Matches 'IL SELF-REVIEWED: rationale'."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("IL SELF-REVIEWED: Fixed typo", "IL", "SELF-REVIEWED")

    def test_parenthetical_model_annotation_with_colon(self) -> None:
        """Matches 'CRS (Gemini): APPROVED' format."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("CRS (Gemini): APPROVED - all good", "CRS", "APPROVED")

    def test_parenthetical_model_with_em_dash(self) -> None:
        """Matches 'CRS (Gemini) \u2014 APPROVED' format."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern(
            "CRS (Gemini) \u2014 APPROVED: assessment", "CRS", "APPROVED"
        )

    def test_parenthetical_model_with_en_dash(self) -> None:
        """Matches 'CRS (Gemini) \u2013 APPROVED' format."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern(
            "CRS (Gemini) \u2013 APPROVED: assessment", "CRS", "APPROVED"
        )

    def test_parenthetical_model_with_hyphen(self) -> None:
        """Matches 'CRS (Gemini) - APPROVED' format."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("CRS (Gemini) - APPROVED: assessment", "CRS", "APPROVED")

    def test_em_dash_no_parenthetical(self) -> None:
        """Matches 'CRS \u2014 APPROVED' without model annotation."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("CRS \u2014 APPROVED: assessment", "CRS", "APPROVED")

    def test_colon_separator(self) -> None:
        """Matches 'CRS: APPROVED' format."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("CRS: APPROVED: assessment", "CRS", "APPROVED")

    def test_extra_whitespace(self) -> None:
        """Matches 'CRS  APPROVED' with extra whitespace."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("CRS  APPROVED: assessment", "CRS", "APPROVED")

    def test_markdown_bold_keyword(self) -> None:
        """Matches '**APPROVED**' with markdown bold stripped."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("| CRS | Gemini | **APPROVED** |", "CRS", "APPROVED")

    def test_markdown_table_format(self) -> None:
        """Matches markdown table row format."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern(
            "| CE | Claude | **APPROVED** | Architecture is sound |", "CE", "APPROVED"
        )

    def test_crs_go_keyword(self) -> None:
        """Matches 'CRS GO' format (alternative to APPROVED)."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert matches_approval_pattern("CRS GO: Ship it", "CRS", "GO")

    def test_no_match_wrong_prefix(self) -> None:
        """Does NOT match when prefix is wrong."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert not matches_approval_pattern("XCRS APPROVED: nope", "CRS", "APPROVED")

    def test_no_match_wrong_keyword(self) -> None:
        """Does NOT match when keyword is wrong."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert not matches_approval_pattern("CRS REJECTED: no", "CRS", "APPROVED")

    def test_no_match_keyword_before_prefix(self) -> None:
        """Does NOT match when keyword appears before prefix."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert not matches_approval_pattern("APPROVED CRS: wrong order", "CRS", "APPROVED")

    def test_multiline_matches_correct_line(self) -> None:
        """Matches when pattern is on one line of multiline text."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        text = "Some preamble\nCRS APPROVED: Looks good\nMore text"
        assert matches_approval_pattern(text, "CRS", "APPROVED")

    def test_empty_text_no_match(self) -> None:
        """Empty text does not match."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            matches_approval_pattern,
        )

        assert not matches_approval_pattern("", "CRS", "APPROVED")


@pytest.mark.unit
class TestHelperFunctions:
    """Test convenience helper functions."""

    def test_has_crs_approval_with_approved(self) -> None:
        """has_crs_approval returns True for CRS APPROVED."""
        from hestai_mcp.modules.tools.shared.review_formats import has_crs_approval

        assert has_crs_approval(["CRS APPROVED: Good code"])

    def test_has_crs_approval_with_go(self) -> None:
        """has_crs_approval returns True for CRS GO."""
        from hestai_mcp.modules.tools.shared.review_formats import has_crs_approval

        assert has_crs_approval(["CRS GO: Ship it"])

    def test_has_crs_approval_false(self) -> None:
        """has_crs_approval returns False when no CRS approval."""
        from hestai_mcp.modules.tools.shared.review_formats import has_crs_approval

        assert not has_crs_approval(["CE APPROVED: Not CRS"])

    def test_has_ce_approval_with_approved(self) -> None:
        """has_ce_approval returns True for CE APPROVED."""
        from hestai_mcp.modules.tools.shared.review_formats import has_ce_approval

        assert has_ce_approval(["CE APPROVED: Architecture sound"])

    def test_has_ce_approval_with_go(self) -> None:
        """has_ce_approval returns True for CE GO."""
        from hestai_mcp.modules.tools.shared.review_formats import has_ce_approval

        assert has_ce_approval(["CE GO: Proceed"])

    def test_has_ce_approval_false(self) -> None:
        """has_ce_approval returns False when no CE approval."""
        from hestai_mcp.modules.tools.shared.review_formats import has_ce_approval

        assert not has_ce_approval(["CRS APPROVED: Not CE"])

    def test_has_il_self_review_true(self) -> None:
        """has_il_self_review returns True for IL SELF-REVIEWED."""
        from hestai_mcp.modules.tools.shared.review_formats import has_il_self_review

        assert has_il_self_review(["IL SELF-REVIEWED: Fixed typo"])

    def test_has_il_self_review_false(self) -> None:
        """has_il_self_review returns False when missing."""
        from hestai_mcp.modules.tools.shared.review_formats import has_il_self_review

        assert not has_il_self_review(["CRS APPROVED: Not IL"])


@pytest.mark.unit
class TestFormatReviewComment:
    """Test comment formatting that produces gate-clearable comments."""

    def test_format_crs_approved(self) -> None:
        """Format CRS APPROVED comment."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            matches_approval_pattern,
        )

        comment = format_review_comment(
            role="CRS", verdict="APPROVED", assessment="Code quality is excellent"
        )
        assert matches_approval_pattern(comment, "CRS", "APPROVED")
        assert "Code quality is excellent" in comment

    def test_format_ce_approved(self) -> None:
        """Format CE APPROVED comment."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            matches_approval_pattern,
        )

        comment = format_review_comment(
            role="CE", verdict="APPROVED", assessment="Architecture is sound"
        )
        assert matches_approval_pattern(comment, "CE", "APPROVED")
        assert "Architecture is sound" in comment

    def test_format_il_self_reviewed(self) -> None:
        """Format IL with APPROVED verdict produces SELF-REVIEWED."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            matches_approval_pattern,
        )

        comment = format_review_comment(
            role="IL", verdict="APPROVED", assessment="Fixed typo in error message"
        )
        assert matches_approval_pattern(comment, "IL", "SELF-REVIEWED")
        assert "Fixed typo in error message" in comment

    def test_format_with_model_annotation(self) -> None:
        """Format comment with model annotation included."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            matches_approval_pattern,
        )

        comment = format_review_comment(
            role="CRS",
            verdict="APPROVED",
            assessment="All tests pass",
            model_annotation="Gemini",
        )
        assert matches_approval_pattern(comment, "CRS", "APPROVED")
        assert "Gemini" in comment
        assert "All tests pass" in comment

    def test_format_blocked_verdict(self) -> None:
        """Format BLOCKED verdict comment."""
        from hestai_mcp.modules.tools.shared.review_formats import format_review_comment

        comment = format_review_comment(
            role="CRS", verdict="BLOCKED", assessment="Security vulnerability found"
        )
        assert "BLOCKED" in comment
        assert "Security vulnerability found" in comment

    def test_format_conditional_verdict(self) -> None:
        """Format CONDITIONAL verdict comment."""
        from hestai_mcp.modules.tools.shared.review_formats import format_review_comment

        comment = format_review_comment(
            role="CE", verdict="CONDITIONAL", assessment="Needs performance testing"
        )
        assert "CONDITIONAL" in comment
        assert "Needs performance testing" in comment

    def test_formatted_approved_clears_gate(self) -> None:
        """Formatted APPROVED comment would clear the review gate."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            has_crs_approval,
        )

        comment = format_review_comment(role="CRS", verdict="APPROVED", assessment="All good")
        assert has_crs_approval([comment])

    def test_formatted_ce_approved_clears_gate(self) -> None:
        """Formatted CE APPROVED comment would clear the CE gate."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            has_ce_approval,
        )

        comment = format_review_comment(
            role="CE", verdict="APPROVED", assessment="Sound architecture"
        )
        assert has_ce_approval([comment])

    def test_formatted_il_self_review_clears_gate(self) -> None:
        """Formatted IL APPROVED comment would clear the IL self-review gate."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            has_il_self_review,
        )

        comment = format_review_comment(role="IL", verdict="APPROVED", assessment="Trivial fix")
        assert has_il_self_review([comment])

    def test_formatted_with_model_clears_gate(self) -> None:
        """Formatted comment with model annotation still clears gate."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            has_crs_approval,
        )

        comment = format_review_comment(
            role="CRS",
            verdict="APPROVED",
            assessment="Tests pass",
            model_annotation="Claude",
        )
        assert has_crs_approval([comment])

    def test_ho_approved_formats_as_ho_reviewed(self) -> None:
        """Format HO with APPROVED verdict produces HO REVIEWED."""
        from hestai_mcp.modules.tools.shared.review_formats import (
            format_review_comment,
            has_ho_review,
            matches_approval_pattern,
        )

        comment = format_review_comment(
            role="HO", verdict="APPROVED", assessment="Delegated to IL, verified output"
        )
        assert matches_approval_pattern(comment, "HO", "REVIEWED")
        assert has_ho_review([comment])
        assert "Delegated to IL, verified output" in comment
