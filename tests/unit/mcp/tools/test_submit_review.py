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
        """Successful post returns comment URL from HTTP response."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "HTTP/2 201 Created\r\n"
            "content-type: application/json\r\n"
            "x-ratelimit-remaining: 4999\r\n"
            "\r\n"
            '{"html_url": "https://github.com/elevanaltd/HestAI-MCP/pull/123#issuecomment-456"}'
        )

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

        # Verify --include flag was added
        call_args = mock_run.call_args[0][0]
        assert "--include" in call_args

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
class TestHTTPResponseParsing:
    """Test HTTP response parsing from gh api --include output.

    The gh api --include flag returns HTTP headers + body in stdout:
    HTTP/2 {status_code} {reason}\r\n
    {headers}\r\n
    \r\n
    {json_body}
    """

    def test_parse_success_response(self) -> None:
        """Parse 201 Created response with headers and body."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        raw_output = (
            "HTTP/2 201 Created\r\n"
            "content-type: application/json\r\n"
            "x-ratelimit-remaining: 4999\r\n"
            "\r\n"
            '{"html_url": "https://github.com/elevanaltd/HestAI-MCP/pull/123#issuecomment-456"}'
        )

        status, headers, body = _parse_http_response(raw_output)

        assert status == 201
        assert headers["x-ratelimit-remaining"] == "4999"
        assert "html_url" in body

    def test_parse_rate_limit_response(self) -> None:
        """Parse 429 Too Many Requests response."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        raw_output = (
            "HTTP/2 429 Too Many Requests\r\n"
            "x-ratelimit-remaining: 0\r\n"
            "retry-after: 60\r\n"
            "\r\n"
            '{"message": "API rate limit exceeded"}'
        )

        status, headers, body = _parse_http_response(raw_output)

        assert status == 429
        assert headers["x-ratelimit-remaining"] == "0"
        assert headers["retry-after"] == "60"

    def test_parse_auth_error_response(self) -> None:
        """Parse 401 Unauthorized response."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        raw_output = (
            "HTTP/2 401 Unauthorized\r\n"
            "content-type: application/json\r\n"
            "\r\n"
            '{"message": "Bad credentials"}'
        )

        status, headers, body = _parse_http_response(raw_output)

        assert status == 401

    def test_parse_forbidden_with_rate_limit(self) -> None:
        """Parse 403 Forbidden with x-ratelimit-remaining: 0 (secondary rate limit)."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        raw_output = (
            "HTTP/2 403 Forbidden\r\n"
            "x-ratelimit-remaining: 0\r\n"
            "\r\n"
            '{"message": "You have exceeded a secondary rate limit"}'
        )

        status, headers, body = _parse_http_response(raw_output)

        assert status == 403
        assert headers["x-ratelimit-remaining"] == "0"

    def test_parse_server_error_response(self) -> None:
        """Parse 500 Internal Server Error response."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        raw_output = (
            "HTTP/2 500 Internal Server Error\r\n"
            "content-type: text/html\r\n"
            "\r\n"
            "<html>Server Error</html>"
        )

        status, headers, body = _parse_http_response(raw_output)

        assert status == 500

    def test_parse_validation_error_response(self) -> None:
        """Parse 422 Unprocessable Entity response."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        raw_output = (
            "HTTP/2 422 Unprocessable Entity\r\n"
            "content-type: application/json\r\n"
            "\r\n"
            '{"message": "Validation Failed"}'
        )

        status, headers, body = _parse_http_response(raw_output)

        assert status == 422

    def test_parse_headers_case_insensitive(self) -> None:
        """Header names should be lowercased for consistent access."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        raw_output = (
            "HTTP/2 200 OK\r\n"
            "X-RateLimit-Remaining: 5000\r\n"
            "Content-Type: application/json\r\n"
            "\r\n"
            "{}"
        )

        status, headers, body = _parse_http_response(raw_output)

        # Headers should be accessible via lowercase keys
        assert headers["x-ratelimit-remaining"] == "5000"
        assert headers["content-type"] == "application/json"

    def test_parse_empty_response(self) -> None:
        """Empty response returns fail-safe values."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        status, headers, body = _parse_http_response("")
        assert status == 0
        assert headers == {}
        assert body == ""

    def test_parse_no_separator(self) -> None:
        """Response without double CRLF returns fail-safe."""
        from hestai_mcp.modules.tools.submit_review import (
            _map_status_to_action,
            _parse_http_response,
        )

        status, headers, body = _parse_http_response("HTTP/2 200 OK")
        assert status == 0
        assert _map_status_to_action(0, {}) == "validation"

    def test_parse_invalid_status(self) -> None:
        """Invalid status code returns fail-safe."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        status, headers, body = _parse_http_response("HTTP/2 NOTANUMBER\r\n\r\n{}")
        assert status == 0

    def test_parse_malformed_status_line(self) -> None:
        """Malformed status line returns fail-safe."""
        from hestai_mcp.modules.tools.submit_review import _parse_http_response

        status, headers, body = _parse_http_response("BROKEN\r\n\r\n{}")
        assert status == 0


@pytest.mark.unit
class TestStatusToActionMapping:
    """Test HTTP status code to error_type mapping."""

    def test_status_429_maps_to_rate_limit(self) -> None:
        """HTTP 429 explicitly maps to rate_limit."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        error_type = _map_status_to_action(429, {})
        assert error_type == "rate_limit"

    def test_status_403_with_zero_remaining_maps_to_rate_limit(self) -> None:
        """HTTP 403 with x-ratelimit-remaining: 0 maps to rate_limit (secondary rate limit)."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        error_type = _map_status_to_action(403, {"x-ratelimit-remaining": "0"})
        assert error_type == "rate_limit"

    def test_status_403_without_rate_limit_maps_to_auth(self) -> None:
        """HTTP 403 without rate limit indicator maps to auth (permissions)."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        error_type = _map_status_to_action(403, {"x-ratelimit-remaining": "4999"})
        assert error_type == "auth"

    def test_secondary_rate_limit_mixed_case_header(self) -> None:
        """403 with X-RateLimit-Remaining: 0 (mixed case) detected as rate_limit."""
        from hestai_mcp.modules.tools.submit_review import (
            _map_status_to_action,
            _parse_http_response,
        )

        raw_output = (
            "HTTP/2 403 Forbidden\r\n"
            "X-RateLimit-Remaining: 0\r\n"  # Mixed case
            "\r\n"
            '{"message": "Rate limit"}'
        )
        status, headers, body = _parse_http_response(raw_output)
        assert _map_status_to_action(status, headers) == "rate_limit"

    def test_status_401_maps_to_auth(self) -> None:
        """HTTP 401 maps to auth."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        error_type = _map_status_to_action(401, {})
        assert error_type == "auth"

    def test_status_5xx_maps_to_network(self) -> None:
        """HTTP 5xx server errors map to network (retryable)."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        assert _map_status_to_action(500, {}) == "network"
        assert _map_status_to_action(502, {}) == "network"
        assert _map_status_to_action(503, {}) == "network"
        assert _map_status_to_action(504, {}) == "network"

    def test_status_404_maps_to_validation(self) -> None:
        """HTTP 404 Not Found maps to validation (fail-fast)."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        error_type = _map_status_to_action(404, {})
        assert error_type == "validation"

    def test_status_422_maps_to_validation(self) -> None:
        """HTTP 422 Unprocessable Entity maps to validation (fail-fast)."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        error_type = _map_status_to_action(422, {})
        assert error_type == "validation"

    def test_status_400_maps_to_validation(self) -> None:
        """HTTP 400 Bad Request maps to validation (fail-fast)."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        error_type = _map_status_to_action(400, {})
        assert error_type == "validation"

    def test_unknown_status_maps_to_validation(self) -> None:
        """Unknown status codes map to validation (fail-closed)."""
        from hestai_mcp.modules.tools.submit_review import _map_status_to_action

        # Fail-closed: unknown status = don't retry
        error_type = _map_status_to_action(999, {})
        assert error_type == "validation"


@pytest.mark.unit
class TestErrorClassification:
    """Test error_type field for intelligent retry strategies using HTTP status codes."""

    @pytest.mark.asyncio
    async def test_rate_limit_error_classified(self) -> None:
        """HTTP 429 classified as rate_limit error."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "HTTP/2 429 Too Many Requests\r\n"
            "x-ratelimit-remaining: 0\r\n"
            "\r\n"
            '{"message": "API rate limit exceeded"}'
        )

        with (
            patch("subprocess.run", return_value=mock_result),
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="Should detect rate limit",
            )

        assert result["success"] is False
        assert result["error_type"] == "rate_limit"

    @pytest.mark.asyncio
    async def test_secondary_rate_limit_classified(self) -> None:
        """HTTP 403 with x-ratelimit-remaining: 0 classified as rate_limit."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "HTTP/2 403 Forbidden\r\n"
            "x-ratelimit-remaining: 0\r\n"
            "\r\n"
            '{"message": "You have exceeded a secondary rate limit"}'
        )

        with (
            patch("subprocess.run", return_value=mock_result),
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="Should detect secondary rate limit",
            )

        assert result["success"] is False
        assert result["error_type"] == "rate_limit"

    @pytest.mark.asyncio
    async def test_auth_error_classified(self) -> None:
        """HTTP 401 classified as auth error."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "HTTP/2 401 Unauthorized\r\n"
            "content-type: application/json\r\n"
            "\r\n"
            '{"message": "Bad credentials"}'
        )

        with (
            patch("subprocess.run", return_value=mock_result),
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="Should detect auth error",
            )

        assert result["success"] is False
        assert result["error_type"] == "auth"

    @pytest.mark.asyncio
    async def test_permission_error_classified(self) -> None:
        """HTTP 403 without rate limit classified as auth error."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "HTTP/2 403 Forbidden\r\n"
            "x-ratelimit-remaining: 4999\r\n"
            "\r\n"
            '{"message": "Resource not accessible by integration"}'
        )

        with (
            patch("subprocess.run", return_value=mock_result),
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="Should detect permissions error",
            )

        assert result["success"] is False
        assert result["error_type"] == "auth"

    @pytest.mark.asyncio
    async def test_server_error_classified(self) -> None:
        """HTTP 500 classified as network error (retryable)."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "HTTP/2 500 Internal Server Error\r\n"
            "content-type: text/html\r\n"
            "\r\n"
            "<html>Server Error</html>"
        )

        with (
            patch("subprocess.run", return_value=mock_result),
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="Should detect server error",
            )

        assert result["success"] is False
        assert result["error_type"] == "network"

    @pytest.mark.asyncio
    async def test_validation_error_classified(self) -> None:
        """HTTP 422 classified as validation error (fail-fast)."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "HTTP/2 422 Unprocessable Entity\r\n"
            "content-type: application/json\r\n"
            "\r\n"
            '{"message": "Validation Failed"}'
        )

        with (
            patch("subprocess.run", return_value=mock_result),
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=123,
                role="CRS",
                verdict="APPROVED",
                assessment="Should detect validation error",
            )

        assert result["success"] is False
        assert result["error_type"] == "validation"

    @pytest.mark.asyncio
    async def test_not_found_classified(self) -> None:
        """HTTP 404 classified as validation error (fail-fast)."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "HTTP/2 404 Not Found\r\n"
            "content-type: application/json\r\n"
            "\r\n"
            '{"message": "Not Found"}'
        )

        with (
            patch("subprocess.run", return_value=mock_result),
            patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}),
        ):
            result = await submit_review(
                repo="elevanaltd/HestAI-MCP",
                pr_number=999,
                role="CRS",
                verdict="APPROVED",
                assessment="Should detect not found",
            )

        assert result["success"] is False
        assert result["error_type"] == "validation"

    @pytest.mark.asyncio
    async def test_input_validation_error_classified(self) -> None:
        """Input validation errors still return error_type='validation'."""
        from hestai_mcp.modules.tools.submit_review import submit_review

        result = await submit_review(
            repo="elevanaltd/HestAI-MCP",
            pr_number=123,
            role="INVALID_ROLE",
            verdict="APPROVED",
            assessment="Should detect validation error",
        )

        assert result["success"] is False
        assert result["error_type"] == "validation"


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
