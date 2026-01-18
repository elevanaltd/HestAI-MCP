#!/usr/bin/env python3
"""
Review validation script - enforces review requirements based on PR changes.
Called by pre-commit hooks and CI pipeline.
"""

import json
import os
import re
import subprocess
import sys
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
    except subprocess.CalledProcessError:
        return []


def determine_review_tier(files: list[dict[str, Any]]) -> tuple[str, str]:
    """Determine required review tier based on changed files."""

    # Calculate totals
    total_lines = sum(f["total_changed"] for f in files)
    changed_paths = [f["path"] for f in files]

    # Check for exempt patterns
    exempt_patterns = [
        r".*\.md$",
        r"^tests/.*$",
        r".*\.lock$",
        r".*\.json$",
    ]

    all_exempt = all(
        any(re.match(pattern, path) for pattern in exempt_patterns) for path in changed_paths
    )

    if all_exempt:
        return "TIER_0_EXEMPT", "No review required - only exempt files changed"

    # Check for Tier 3 triggers (highest priority)
    tier3_triggers = [
        any("architecture" in path for path in changed_paths),
        any(path.endswith(".sql") for path in changed_paths),
        total_lines > 500,
        len({Path(p).parts[0] for p in changed_paths if "/" in p}) > 1,  # Multiple components
    ]

    if any(tier3_triggers):
        return "TIER_3_FULL", f"Full review required - {total_lines} lines, critical paths"

    # Check for Tier 2
    if 50 <= total_lines <= 500:
        return "TIER_2_CRS", f"CRS review required - {total_lines} lines changed"

    # Check for Tier 1
    if total_lines < 50 and len(files) == 1:
        return "TIER_1_SELF", f"Self-review sufficient - {total_lines} lines in single file"

    # Default to Tier 2 if unsure
    return "TIER_2_CRS", "CRS review required - default tier"


def check_pr_comments(tier: str) -> tuple[bool, str]:
    """Check if required review comments exist in PR."""

    # In pre-commit context, we can't check PR comments
    # This would be called from CI with PR number
    if "CI" not in os.environ:
        return True, "Skipping comment check in local context"

    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        return False, "❌ PR_NUMBER not set in environment"

    print(f"   Checking PR #{pr_number} for review comments...")

    # Use gh CLI to get comments
    try:
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--json", "comments"],
            capture_output=True,
            text=True,
            check=True,
        )
        comments_data = json.loads(result.stdout)
        comments = [c["body"] for c in comments_data.get("comments", [])]

        # Check for required approvals based on tier
        if tier == "TIER_1_SELF":
            if any("IL SELF-REVIEWED:" in c for c in comments):
                return True, "✓ Self-review found"
            return False, "❌ Missing: IL SELF-REVIEWED comment"

        elif tier == "TIER_2_CRS":
            if any("CRS APPROVED:" in c for c in comments):
                return True, "✓ CRS approval found"
            return False, "❌ Missing: CRS APPROVED comment"

        elif tier == "TIER_3_FULL":
            has_crs = any("CRS APPROVED:" in c for c in comments)
            has_ce = any("CE APPROVED:" in c for c in comments)

            if has_crs and has_ce:
                return True, "✓ Both CRS and CE approvals found"

            missing = []
            if not has_crs:
                missing.append("CRS APPROVED")
            if not has_ce:
                missing.append("CE APPROVED")
            return False, f"❌ Missing: {', '.join(missing)}"

    except (subprocess.CalledProcessError, json.JSONDecodeError):
        # If we can't check, be permissive
        return True, "Unable to check PR comments"

    return True, "No review required for this tier"


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
        elif tier == "TIER_2_CRS":
            print("   Need comment: 'CRS APPROVED: [assessment]'")
            print("   Example: 'CRS APPROVED: Logic correct, tests pass, no security issues'")
        elif tier == "TIER_3_FULL":
            print("   Need comments:")
            print("   - 'CRS APPROVED: [assessment]'")
            print("   - 'CE APPROVED: [critical assessment]'")
            print("   Example: 'CE APPROVED: Architecture sound, performance acceptable'")

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
