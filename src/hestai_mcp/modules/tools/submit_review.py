"""
Submit review MCP tool for programmatic review gate clearance.

Posts structured review comments on GitHub PRs that are formatted to
clear the review-gate CI check. Shares format constants with
scripts/validate_review.py via the shared review_formats module.

Fail-closed: validates format before posting. If validation fails,
the comment is NOT posted.
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
    matches_approval_pattern,
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
            f"Invalid verdict: '{verdict}'. "
            f"Must be one of: {', '.join(sorted(VALID_VERDICTS))}"
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
        "CRS": "TIER_2_CRS: CRS APPROVED comment required",
        "CE": "TIER_3_FULL: CE APPROVED comment required (alongside CRS)",
        "IL": "TIER_1_SELF: IL SELF-REVIEWED comment required",
    }
    return requirements.get(role, "Unknown tier requirement")


def _post_comment(repo: str, pr_number: int, comment: str) -> dict[str, Any]:
    """Post a comment on a GitHub PR using gh CLI.

    Args:
        repo: Repository in owner/name format.
        pr_number: PR number to comment on.
        comment: Comment body to post.

    Returns:
        Dict with success status and comment URL or error.
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return {
            "success": False,
            "error": "GITHUB_TOKEN or GH_TOKEN environment variable not set",
        }

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repo}/issues/{pr_number}/comments",
                "-f",
                f"body={comment}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"GitHub API error: {result.stderr or result.stdout}",
            }

        response_data = json.loads(result.stdout)
        return {
            "success": True,
            "comment_url": response_data.get("html_url", ""),
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "GitHub API request timed out (30s)"}
    except json.JSONDecodeError:
        return {"success": False, "error": f"Invalid JSON response: {result.stdout}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}


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
        formatted comment.
    """
    # Step 1: Validate inputs
    error = _validate_inputs(repo, pr_number, role, verdict, assessment)
    if error:
        return {"success": False, "error": error}

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
            "formatted_comment": formatted_comment,
            "validation": validation,
        }

    return {
        "success": True,
        "comment_url": post_result["comment_url"],
        "validation": validation,
        "formatted_comment": formatted_comment,
    }
