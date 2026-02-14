"""
Tests for submit_review MCP tool.

TDD RED phase: Tests define the contract for submit_review.
Tests written FIRST before implementation exists.

Coverage:
- Input validation (invalid role, invalid verdict)
- Dry-run returns validation without posting
- Fail-closed: bad format does not post
- Mock subprocess.run for gh CLI calls
- Successful post returns comment URL
- Error handling for GitHub API failures
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestInputValidation:
    """Test that invalid inputs are rejected."""

    @pytest.mark.asyncio
    async def test_invalid_role_rejected(self) -> None:
        """Invalid role returns error without posting."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="INVALID",
            verdict="APPROVED",
            assessment="Should not post",
        )
        assert result["success"] is False
        assert "role" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_invalid_verdict_rejected(self) -> None:
        """Invalid verdict returns error without posting."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CRS",
            verdict="INVALID",
            assessment="Should not post",
        )
        assert result["success"] is False
        assert "verdict" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_empty_assessment_rejected(self) -> None:
        """Empty assessment returns error without posting."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CRS",
            verdict="APPROVED",
            assessment="",
        )
        assert result["success"] is False
        assert "assessment" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_negative_pr_number_rejected(self) -> None:
        """Negative PR number returns error."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=-1,
            role="CRS",
            verdict="APPROVED",
            assessment="Some assessment",
        )
        assert result["success"] is False


@pytest.mark.unit
class TestDryRun:
    """Test dry-run mode returns validation without posting."""

    @pytest.mark.asyncio
    async def test_dry_run_returns_validation(self) -> None:
        """Dry run returns result with validation info."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CRS",
            verdict="APPROVED",
            assessment="All tests pass",
            dry_run=True,
        )
        assert result["success"] is True
        assert result["validation"]["would_clear_gate"] is True
        assert result["formatted_comment"] is not None
        assert result["comment_url"] is None  # Not posted

    @pytest.mark.asyncio
    async def test_dry_run_does_not_call_gh(self) -> None:
        """Dry run never calls subprocess (gh CLI)."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        with patch("subprocess.run") as mock_run:
            await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="All tests pass",
                dry_run=True,
            )
            mock_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_dry_run_blocked_verdict(self) -> None:
        """Dry run with BLOCKED verdict reports would_clear_gate=False."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CRS",
            verdict="BLOCKED",
            assessment="Security vulnerability",
            dry_run=True,
        )
        assert result["success"] is True
        assert result["validation"]["would_clear_gate"] is False

    @pytest.mark.asyncio
    async def test_dry_run_conditional_verdict(self) -> None:
        """Dry run with CONDITIONAL verdict reports would_clear_gate=False."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CE",
            verdict="CONDITIONAL",
            assessment="Needs perf testing",
            dry_run=True,
        )
        assert result["success"] is True
        assert result["validation"]["would_clear_gate"] is False

    @pytest.mark.asyncio
    async def test_dry_run_with_model_annotation(self) -> None:
        """Dry run with model annotation includes it in formatted comment."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CRS",
            verdict="APPROVED",
            assessment="LGTM",
            model_annotation="Gemini",
            dry_run=True,
        )
        assert result["success"] is True
        assert "Gemini" in result["formatted_comment"]

    @pytest.mark.asyncio
    async def test_dry_run_il_maps_to_self_reviewed(self) -> None:
        """Dry run IL APPROVED maps to SELF-REVIEWED in formatted comment."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="IL",
            verdict="APPROVED",
            assessment="Fixed typo",
            dry_run=True,
        )
        assert result["success"] is True
        assert "SELF-REVIEWED" in result["formatted_comment"]
        assert result["validation"]["would_clear_gate"] is True


@pytest.mark.unit
class TestGitHubPosting:
    """Test GitHub API posting via gh CLI."""

    @pytest.mark.asyncio
    async def test_successful_post(self) -> None:
        """Successful post returns comment URL."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"html_url": "https://github.com/elevanaltd/HestAI-MCP/pull/123#issuecomment-456"}'

        with (
            patch("subprocess.run", return_value=mock_result) as mock_run,
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="All quality gates pass",
            )

        assert result["success"] is True
        assert "github.com" in result["comment_url"]
        mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_github_api_failure(self) -> None:
        """GitHub API failure returns error without crashing."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "gh: Not Found (HTTP 404)"
        mock_result.stdout = ""

        with (
            patch("subprocess.run", return_value=mock_result),
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=999,
                role="CRS",
                verdict="APPROVED",
                assessment="Should fail",
            )

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_no_github_token(self) -> None:
        """Missing GITHUB_TOKEN returns error."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        with patch.dict("os.environ", {}, clear=True):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="Should fail",
            )

        assert result["success"] is False
        assert "token" in result["error"].lower() or "GITHUB_TOKEN" in result["error"]


@pytest.mark.unit
class TestFailClosed:
    """Test fail-closed behavior: invalid format must not post."""

    @pytest.mark.asyncio
    async def test_format_validation_before_post(self) -> None:
        """Comment is validated against gate patterns before posting."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        # Valid inputs should produce a gate-clearing comment
        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CRS",
            verdict="APPROVED",
            assessment="Code looks good",
            dry_run=True,
        )
        assert result["validation"]["would_clear_gate"] is True

    @pytest.mark.asyncio
    async def test_result_contains_formatted_comment(self) -> None:
        """Result always includes the formatted comment for transparency."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CE",
            verdict="APPROVED",
            assessment="Architecture is sound",
            dry_run=True,
        )
        assert "formatted_comment" in result
        assert "CE" in result["formatted_comment"]
        assert "APPROVED" in result["formatted_comment"]

    @pytest.mark.asyncio
    async def test_result_contains_tier_info(self) -> None:
        """Result validation includes tier requirement information."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="CRS",
            verdict="APPROVED",
            assessment="LGTM",
            dry_run=True,
        )
        assert "tier_requirements" in result["validation"]
