#!/usr/bin/env python3
"""
Review validation script - enforces review requirements based on PR changes.
Called by pre-commit hooks and CI pipeline.

Version: 2.0.0 (SECURITY: Fail-closed error handling)
Source: https://github.com/elevanaltd/HestAI-MCP
Last updated: 2026-01-19
Breaking Change: Now exits non-zero on CI failures (was: fail-open)
"""

# Critical-Engineer: consulted for Review-gate fail-closed validation
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def get_changed_files() -> list[dict[str, Any]]:
    """Get list of changed files with line counts."""
    try:
        # In CI, compare against base branch; locally use cached
        if "CI" in os.environ:
            # Get the base branch (usually main)
            base_ref = os.environ.get("GITHUB_BASE_REF", "origin/main")
            cmd = ["git", "diff", f"{base_ref}...HEAD", "--numstat"]
        else:
            # Local: check staged files
            cmd = ["git", "diff", "--cached", "--numstat"]

        # Get diff stats
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        files = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) == 3:
                added, deleted, filename = parts
                files.append(
                    {
                        "path": filename,
                        "added": int(added) if added != "-" else 0,
                        "deleted": int(deleted) if deleted != "-" else 0,
                        "total_changed": (int(added) if added != "-" else 0)
                        + (int(deleted) if deleted != "-" else 0),
                    }
                )
        return files
    except subprocess.CalledProcessError as e:
        # SECURITY FIX: Fail closed in CI, permissive locally
        if "CI" in os.environ:
            print(f"❌ Git command failed in CI: {e}", file=sys.stderr)
            sys.exit(1)
        return []


def determine_review_tier(files: list[dict[str, Any]]) -> tuple[str, str]:
    """Determine required review tier based on changed files."""

    # Exempt patterns - files that don't count toward review requirements
    exempt_patterns = [
        r".*\.md$",  # All markdown files exempt (including architecture docs)
        r"^tests/.*$",
        r".*\.lock$",
        r".*\.json$",
    ]

    # Filter out exempt files for tier calculation
    non_exempt_files = [
        f for f in files if not any(re.match(pattern, f["path"]) for pattern in exempt_patterns)
    ]

    # If only exempt files changed, no review needed
    if not non_exempt_files:
        return "TIER_0_EXEMPT", "No review required - only exempt files changed"

    # Calculate totals based on non-exempt files only
    total_lines = sum(f["total_changed"] for f in non_exempt_files)
    changed_paths = [f["path"] for f in non_exempt_files]

    # Check for Tier 3 triggers (highest priority)
    tier3_triggers = [
        any(path.endswith(".sql") for path in changed_paths),
        total_lines > 500,
    ]

    if any(tier3_triggers):
        return "TIER_3_STRICT", f"Strict review required - {total_lines} lines, critical paths"

    # Check for Tier 2
    if 50 <= total_lines <= 500:
        return "TIER_2_STANDARD", f"CRS + CE review required - {total_lines} lines changed"

    # Check for Tier 1
    if total_lines < 50 and len(non_exempt_files) == 1:
        return "TIER_1_SELF", f"Self-review sufficient - {total_lines} lines in single file"

    # Default to Tier 2 if unsure
    return "TIER_2_STANDARD", "CRS + CE review required - default tier"


# Import shared review format utilities (single source of truth).
# In CI, the package may not be installed, so we use importlib to load
# the module file directly without triggering the package's __init__.py.
try:
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_ce_approval as _has_ce_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_crs_approval as _has_crs_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_crs_model_approval as _has_crs_model_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        matches_approval_pattern as _matches_approval_pattern,
    )
except (ImportError, ModuleNotFoundError):
    # CI fallback: load the module file directly via importlib
    import importlib.util

    _module_path = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "hestai_mcp"
        / "modules"
        / "tools"
        / "shared"
        / "review_formats.py"
    )
    _spec = importlib.util.spec_from_file_location("review_formats", _module_path)
    assert _spec is not None and _spec.loader is not None
    _review_formats = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_review_formats)
    _matches_approval_pattern = _review_formats.matches_approval_pattern
    _has_crs_approval = _review_formats.has_crs_approval
    _has_crs_model_approval = _review_formats.has_crs_model_approval
    _has_ce_approval = _review_formats.has_ce_approval


def _has_approval(texts: list[str], prefix: str, keyword: str) -> bool:
    """Check if any text in the list matches the approval pattern."""
    return any(_matches_approval_pattern(t, prefix, keyword) for t in texts)


def check_pr_comments(tier: str) -> tuple[bool, str]:
    """Check if required review comments and PR body contain approval patterns.

    Scans both PR comments and the PR description body for approval patterns.
    Supports flexible matching including parenthetical model annotations
    (e.g., 'CRS (Gemini): APPROVED') in addition to the original exact format.
    """

    # In pre-commit context, we can't check PR comments
    # This would be called from CI with PR number
    if "CI" not in os.environ:
        return True, "Skipping comment check in local context"

    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        return False, "❌ PR_NUMBER not set in environment"

    print(f"   Checking PR #{pr_number} for review comments...")

    # Use gh CLI to get comments and PR body
    try:
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--json", "comments,body"],
            capture_output=True,
            text=True,
            check=True,
        )
        pr_data = json.loads(result.stdout)

        # Collect all searchable text: PR body + comment bodies
        # Exclude bot status comments to prevent self-referencing approval
        # (the bot's guidance text contains "CRS APPROVED:" which would falsely match)
        searchable_texts: list[str] = []
        pr_body = pr_data.get("body")
        if pr_body:
            searchable_texts.append(pr_body)
        searchable_texts.extend(
            c["body"]
            for c in pr_data.get("comments", [])
            if "<!-- review-gate-status -->" not in c["body"]
        )

        # Check for required approvals based on tier.
        # Higher-tier reviews satisfy lower-tier requirements (hierarchy rule):
        #   TIER_1_SELF: IL SELF-REVIEWED OR CRS OR CRS+CE
        #   TIER_2_STANDARD:  CRS + CE
        #   TIER_3_STRICT: CRS(Gemini) + CRS(Codex) + CE
        if tier == "TIER_1_SELF":
            if _has_approval(searchable_texts, "IL", "SELF-REVIEWED"):
                return True, "✓ Self-review found"
            if _has_crs_approval(searchable_texts):
                return True, "✓ CRS approval satisfies self-review requirement"
            return False, "❌ Missing: IL SELF-REVIEWED comment"

        elif tier == "TIER_2_STANDARD":
            has_crs = _has_crs_approval(searchable_texts)
            has_ce = _has_ce_approval(searchable_texts)

            if has_crs and has_ce:
                return True, "✓ CRS and CE approvals found"

            missing = []
            if not has_crs:
                missing.append("CRS APPROVED or CRS GO")
            if not has_ce:
                missing.append("CE APPROVED or CE GO")
            return False, f"❌ Missing: {', '.join(missing)}"

        elif tier == "TIER_3_STRICT":
            has_crs_gemini = _has_crs_model_approval(searchable_texts, "Gemini")
            has_crs_codex = _has_crs_model_approval(searchable_texts, "Codex")
            has_ce = _has_ce_approval(searchable_texts)

            if has_crs_gemini and has_crs_codex and has_ce:
                return True, "✓ Dual CRS (Gemini + Codex) and CE approvals found"

            missing = []
            if not has_crs_gemini:
                missing.append("CRS (Gemini) APPROVED or CRS (Gemini) GO")
            if not has_crs_codex:
                missing.append("CRS (Codex) APPROVED or CRS (Codex) GO")
            if not has_ce:
                missing.append("CE APPROVED or CE GO")
            return False, f"❌ Missing: {', '.join(missing)}"

    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        # SECURITY FIX: Fail closed in CI, permissive locally
        if "CI" in os.environ:
            return False, f"❌ Error checking PR comments: {e}"
        return True, "Unable to check PR comments (local mode)"

    return True, "No review required for this tier"


def log_emergency_bypass() -> None:
    """Create audit trail for emergency bypass."""
    # Create audit directory
    audit_dir = Path.cwd() / ".hestai" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_log = audit_dir / "bypass-log.jsonl"

    # Get metadata
    pr_number = os.environ.get("PR_NUMBER", "unknown")

    # Get git user info
    try:
        user_name = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, check=True
        ).stdout.strip()
        user_email = subprocess.run(
            ["git", "config", "user.email"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except subprocess.CalledProcessError:
        user_name = "unknown"
        user_email = "unknown"

    # Get commit SHA
    try:
        commit_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except subprocess.CalledProcessError:
        commit_sha = "unknown"

    # Create audit entry
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "reason": "EMERGENCY_BYPASS",
        "pr_number": pr_number,
        "commit": commit_sha,
        "user_name": user_name,
        "user_email": user_email,
    }

    # Append to audit log
    with open(audit_log, "a") as f:
        f.write(json.dumps(entry) + "\n")


def check_emergency_bypass() -> bool:
    """Check if this is an emergency bypass commit."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True
        )
        return "EMERGENCY:" in result.stdout
    except subprocess.CalledProcessError:
        return False


def main() -> int:
    """Main validation logic."""

    # Check for emergency bypass
    if check_emergency_bypass():
        print("⚠️  EMERGENCY BYPASS - Review required post-merge")
        log_emergency_bypass()
        return 0

    # Get changed files
    files = get_changed_files()
    if not files:
        print("✓ No files changed")
        return 0

    # Show changed files summary
    total_lines = sum(int(f["total_changed"]) for f in files)
    print(f"📊 Changed Files: {len(files)} files, {total_lines} lines")
    for f in files[:5]:  # Show first 5
        print(f"   - {f['path']} (+{f['added']}/-{f['deleted']})")
    if len(files) > 5:
        print(f"   ... and {len(files) - 5} more")

    # Determine review tier
    tier, reason = determine_review_tier(files)
    print(f"\n📋 Review Tier: {tier}")
    print(f"   Reason: {reason}")

    # Check if tier is exempt
    if tier == "TIER_0_EXEMPT":
        print("✓ Review not required")
        return 0

    # Check for required approvals
    approved, message = check_pr_comments(tier)
    print(f"   {message}")

    if not approved:
        print("\n⚠️  Review Requirements:")
        if tier == "TIER_1_SELF":
            print("   Add comment: 'IL SELF-REVIEWED: [your rationale]'")
            print("   Example: 'IL SELF-REVIEWED: Fixed typo in error message'")
        elif tier == "TIER_2_STANDARD":
            print("   Need comments:")
            print("   - 'CRS APPROVED: [assessment]' (or CRS (Gemini) APPROVED:)")
            print("   - 'CE APPROVED: [critical assessment]'")
            print("   Example: 'CRS APPROVED: Logic correct, tests pass, no security issues'")
        elif tier == "TIER_3_STRICT":
            print("   Need comments:")
            print("   - 'CRS (Gemini) APPROVED: [assessment]'")
            print("   - 'CRS (Codex) APPROVED: [assessment]'")
            print("   - 'CE APPROVED: [critical assessment]'")
            print("   Example: 'CRS (Gemini) APPROVED: Logic verified, patterns sound'")

        # Only block in CI context
        if "CI" in os.environ:
            print("\n❌ Blocking merge - reviews required")
            return 1
        else:
            print("\n   ℹ️  Local check only - not blocking")
            return 0

    print("\n✓ Review requirements satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
