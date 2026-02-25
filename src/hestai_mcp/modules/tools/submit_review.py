"""
Submit review MCP tool for programmatic review gate clearance.

Posts structured review comments on GitHub PRs that are formatted to
clear the review-gate CI check. Shares format constants with
scripts/validate_review.py via the shared review_formats module.

Fail-closed: validates format before posting. If validation fails,
the comment is NOT posted.

CONSULTATION EVIDENCE:
- critical-engineer (CE): Required 5 additional tests for HTTP response
  parsing edge cases (Issue #225):
  * 4 malformed HTTP response tests (empty, no separator, invalid status, malformed line)
  * 1 mixed-case header + 403 rate limit detection test
  Tests added to tests/unit/mcp/tools/test_submit_review.py.
"""

import json
import os
import subprocess
from typing import Any

from hestai_mcp.modules.tools.shared.review_formats import (
    VALID_ROLES,
    VALID_VERDICTS,
    format_review_comment,
    has_ce_approval,
    has_crs_approval,
    has_il_self_review,
)


def _validate_inputs(
    repo: str,
    pr_number: int,
    role: str,
    verdict: str,
    assessment: str,
) -> str | None:
    """Validate submit_review inputs. Returns error message or None if valid."""
    if role not in VALID_ROLES:
        return f"Invalid role: '{role}'. Must be one of: {', '.join(sorted(VALID_ROLES))}"

    if verdict not in VALID_VERDICTS:
        return (
            f"Invalid verdict: '{verdict}'. " f"Must be one of: {', '.join(sorted(VALID_VERDICTS))}"
        )

    if not assessment or not assessment.strip():
        return "Assessment must not be empty"

    if pr_number < 1:
        return f"Invalid PR number: {pr_number}. Must be a positive integer"

    if not repo or "/" not in repo:
        return f"Invalid repo format: '{repo}'. Must be in owner/name format"

    return None


def _check_would_clear_gate(comment: str, role: str, verdict: str) -> bool:
    """Check if the formatted comment would clear the review gate.

    Only APPROVED verdicts can clear gates. BLOCKED and CONDITIONAL
    are valid review comments but do not clear the gate.

    Args:
        comment: The formatted review comment.
        role: The reviewer role.
        verdict: The review verdict.

    Returns:
        True if the comment would clear the gate.
    """
    if verdict != "APPROVED":
        return False

    if role == "CRS":
        return has_crs_approval([comment])
    elif role == "CE":
        return has_ce_approval([comment])
    elif role == "IL":
        return has_il_self_review([comment])

    return False


def _get_tier_requirements(role: str) -> str:
    """Get human-readable tier requirement description for a role."""
    requirements = {
        "CRS": "TIER_2_STANDARD+: CRS APPROVED comment required (with CE at TIER_2, dual CRS at TIER_3)",
        "CE": "TIER_2_STANDARD+: CE APPROVED comment required (alongside CRS)",
        "IL": "TIER_1_SELF: IL SELF-REVIEWED comment required",
    }
    return requirements.get(role, "Unknown tier requirement")


def _parse_http_response(raw_output: str) -> tuple[int, dict[str, str], str]:
    """Parse HTTP response from gh api --include output.

    The gh api --include flag returns HTTP headers + body in stdout:
    HTTP/2 {status_code} {reason}\r\n
    {headers}\r\n
    \r\n
    {json_body}

    Args:
        raw_output: Raw HTTP response from gh api --include.

    Returns:
        Tuple of (status_code, headers_dict, body_string).
        Header keys are lowercased for consistent access.
    """
    # Split response into status line + headers + body
    # Handle both Windows (\r\n) and Unix (\n) line endings
    # subprocess.run(..., text=True) normalizes to \n on Unix platforms
    if "\r\n\r\n" in raw_output:
        parts = raw_output.split("\r\n\r\n", 1)
        line_separator = "\r\n"
    elif "\n\n" in raw_output:
        parts = raw_output.split("\n\n", 1)
        line_separator = "\n"
    else:
        # Malformed response - treat as unknown error
        return 0, {}, raw_output

    if len(parts) != 2:
        # Malformed response - treat as unknown error
        return 0, {}, raw_output

    header_section, body = parts
    lines = header_section.split(line_separator)

    # Parse status line: "HTTP/2 201 Created"
    status_line = lines[0]
    status_parts = status_line.split()
    if len(status_parts) < 2:
        return 0, {}, raw_output

    try:
        status_code = int(status_parts[1])
    except (ValueError, IndexError):
        return 0, {}, raw_output

    # Parse headers (lowercase keys for consistent access)
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key.lower()] = value

    return status_code, headers, body


def _map_status_to_action(status: int, headers: dict[str, str]) -> str:
    """Map HTTP status code to error_type for intelligent retry strategies.

    Args:
        status: HTTP status code from GitHub API.
        headers: HTTP headers (lowercase keys).

    Returns:
        Error type classification:
        - "rate_limit": Rate limit exceeded (429 or 403 with zero remaining)
        - "auth": Authentication/authorization failed (401, 403 without rate limit)
        - "network": Server error (5xx) - retryable
        - "validation": Client error (4xx) or unknown - fail-fast, no retry
    """
    # Explicit rate limit (HTTP 429)
    if status == 429:
        return "rate_limit"

    # Secondary rate limit (HTTP 403 with x-ratelimit-remaining: 0)
    if status == 403 and headers.get("x-ratelimit-remaining") == "0":
        return "rate_limit"

    # Authentication/authorization errors (401, 403 without rate limit)
    if status in (401, 403):
        return "auth"

    # Server errors (5xx) are retryable - but only standard 500-599 range
    if 500 <= status < 600:
        return "network"

    # Fail-closed: all other status codes (4xx, unknown, >599) -> validation (no retry)
    return "validation"


def _post_comment(repo: str, pr_number: int, comment: str) -> dict[str, Any]:
    """Post a comment on a GitHub PR using gh CLI with HTTP status code parsing.

    Uses gh api --include to get HTTP headers for protocol-level error classification.

    Args:
        repo: Repository in owner/name format.
        pr_number: PR number to comment on.
        comment: Comment body to post.

    Returns:
        Dict with success status and comment URL or error.
        Error responses include error_type for intelligent retry strategies:
        - "rate_limit": HTTP 429 or 403 with x-ratelimit-remaining: 0
        - "auth": HTTP 401 or 403 (without rate limit)
        - "network": HTTP 5xx server errors
        - "validation": HTTP 4xx client errors or unknown
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return {
            "success": False,
            "error": "GITHUB_TOKEN or GH_TOKEN environment variable not set",
            "error_type": "auth",
        }

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "--include",  # Get HTTP headers in stdout
                f"repos/{repo}/issues/{pr_number}/comments",
                "-f",
                f"body={comment}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check for gh CLI errors first (non-zero exit code)
        if result.returncode != 0:
            # gh CLI failed - classify error from stderr
            error_msg = result.stderr.strip()
            error_lower = error_msg.lower()

            # Determine error type from stderr patterns
            if "rate limit" in error_lower or "429" in error_msg:
                error_type = "rate_limit"
            elif "authentication" in error_lower or "401" in error_msg or "403" in error_msg:
                error_type = "auth"
            elif any(
                term in error_lower for term in ["timeout", "connection", "network", "unreachable"]
            ):
                error_type = "network"
            else:
                # Default to network for unknown gh CLI errors (retryable)
                error_type = "network"

            return {
                "success": False,
                "error": f"GitHub CLI error: {error_msg}",
                "error_type": error_type,
            }

        # Parse HTTP response (status, headers, body) from stdout
        status, headers, body = _parse_http_response(result.stdout)

        # Success: 2xx status codes
        if 200 <= status < 300:
            try:
                response_data = json.loads(body)
                return {
                    "success": True,
                    "comment_url": response_data.get("html_url", ""),
                }
            except json.JSONDecodeError:
                # Even if JSON parsing fails, HTTP 2xx means success
                # This is defensive: GitHub should always return valid JSON for 2xx
                return {
                    "success": True,
                    "comment_url": "",
                }

        # Error: non-2xx status
        error_type = _map_status_to_action(status, headers)
        return {
            "success": False,
            "error": f"GitHub API error: HTTP {status}",
            "error_type": error_type,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "GitHub API request timed out (30s)",
            "error_type": "network",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "error_type": "network",
        }


async def submit_review(
    repo: str,
    pr_number: int,
    role: str,
    verdict: str,
    assessment: str,
    model_annotation: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Submit a structured review comment on a GitHub PR.

    Formats the comment to clear the review-gate CI check.
    Supports dry-run validation without posting.

    Fail-closed: if format validation fails, the comment is NOT posted.

    Args:
        repo: Repository in owner/name format (e.g., 'elevanaltd/HestAI-MCP').
        pr_number: PR number to comment on.
        role: Reviewer role (CRS, CE, IL).
        verdict: Review verdict (APPROVED, BLOCKED, CONDITIONAL).
        assessment: Review assessment content.
        model_annotation: Optional model name (e.g., 'Gemini') for annotation.
        dry_run: If True, validate format without posting.

    Returns:
        Dict with success status, comment URL, validation info, and
        formatted comment. Error responses include error_type field for
        intelligent retry strategies.
    """
    # Step 1: Validate inputs
    error = _validate_inputs(repo, pr_number, role, verdict, assessment)
    if error:
        return {"success": False, "error": error, "error_type": "validation"}

    # Step 2: Format the comment using shared module
    formatted_comment = format_review_comment(
        role=role,
        verdict=verdict,
        assessment=assessment,
        model_annotation=model_annotation,
    )

    # Step 3: Self-validate against gate patterns
    would_clear = _check_would_clear_gate(formatted_comment, role, verdict)

    # For APPROVED verdicts, the formatted comment MUST clear the gate
    # This is a fail-closed check: if format is broken, do not post
    if verdict == "APPROVED" and not would_clear:
        return {
            "success": False,
            "error": "Format validation failed: APPROVED comment does not match gate pattern",
            "error_type": "validation",
            "formatted_comment": formatted_comment,
            "validation": {
                "would_clear_gate": False,
                "tier_requirements": _get_tier_requirements(role),
            },
        }

    validation = {
        "would_clear_gate": would_clear,
        "tier_requirements": _get_tier_requirements(role),
    }

    # Step 4: If dry_run, return without posting
    if dry_run:
        return {
            "success": True,
            "comment_url": None,
            "validation": validation,
            "formatted_comment": formatted_comment,
        }

    # Step 5: Post via GitHub API
    post_result = _post_comment(repo, pr_number, formatted_comment)

    if not post_result["success"]:
        return {
            "success": False,
            "error": post_result["error"],
            "error_type": post_result["error_type"],
            "formatted_comment": formatted_comment,
            "validation": validation,
        }

    return {
        "success": True,
        "comment_url": post_result["comment_url"],
        "validation": validation,
        "formatted_comment": formatted_comment,
    }
