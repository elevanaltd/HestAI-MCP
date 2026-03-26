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


def _is_generated_json(path: str) -> bool:
    """Check if a JSON file is a generated/lock file (exempt) vs hand-edited (not exempt).

    Generated JSON files (package-lock.json, coverage reports, etc.) are exempt.
    Hand-edited JSON config files (src/config/settings.json) are NOT exempt.
    """
    generated_patterns = [
        r"(^|/)package-lock\.json$",
        r"(^|/)package\.json$",
        r"(^|/)tsconfig\.json$",
        r"(^|/)\.eslintrc\.json$",
        r"(^|/)coverage/.*\.json$",
        r"(^|/)\.vscode/.*\.json$",
        r"(^|/)pyrightconfig\.json$",
    ]
    return any(re.search(pattern, path) for pattern in generated_patterns)


def determine_review_tier(files: list[dict[str, Any]]) -> tuple[str, str]:
    """Determine required review tier based on changed files.

    5-tier system (v2.0):
      T0: Only exempt files changed (docs, tests, locks, generated JSON)
      T1: <10 non-exempt lines, single file, no security paths, no new test files
      T2: 10-500 lines, no T3 triggers
      T3: >500 lines OR security/architecture triggers
      T4: Manual only (never auto-detected)
    """

    # Exempt patterns - files that don't count toward review requirements
    exempt_patterns = [
        r".*(?<!\.oct)\.md$",  # Markdown exempt, but NOT .oct.md (governance code)
        r"^tests/.*$",
        r".*\.lock$",
    ]

    def _is_exempt(path: str) -> bool:
        """Check if a file path is exempt from review."""
        # Check standard patterns
        if any(re.match(pattern, path) for pattern in exempt_patterns):
            return True
        # JSON files: only generated ones are exempt
        if path.endswith(".json"):
            return _is_generated_json(path)
        return False

    # Check if any test files are present (for T1 new_test_files guard)
    has_test_files = any(f["path"].startswith("tests/") for f in files)

    # Filter out exempt files for tier calculation
    non_exempt_files = [f for f in files if not _is_exempt(f["path"])]

    # If only exempt files changed, no review needed
    if not non_exempt_files:
        return "TIER_0_EXEMPT", "No review required - only exempt files changed"

    # Calculate totals based on non-exempt files only
    total_lines = sum(f["total_changed"] for f in non_exempt_files)
    changed_paths = [f["path"] for f in non_exempt_files]

    # --- Security path patterns (T3 triggers) ---
    security_patterns = [
        r"(^|/)auth/",  # Authentication code
        r"(^|/)session/",  # Session management
        r"(^|/)config/env",  # Environment variable handling
        r"(^|/)path_utils",  # Path handling utilities
    ]

    # --- Architecture/base class patterns (T3 triggers) ---
    architecture_patterns = [
        r"(^|/)base\.py$",  # Base class files
        r"/shared/",  # Shared modules
        r"(^|/)abstract/",  # Abstract classes
        r"(^|/)hooks/",  # Hook files (new_hooks trigger)
    ]

    # --- New tool/endpoint patterns (T3 triggers) ---
    new_tool_patterns = [
        r"(^|/)modules/tools/",  # Tool files
        r"(^|/)mcp/tools/",  # MCP endpoint files
        r"^clink/agents/",  # Agent config files
    ]

    def _has_security_path() -> bool:
        """Check if any changed path touches security-sensitive code."""
        return any(
            re.search(pattern, path) for path in changed_paths for pattern in security_patterns
        )

    def _has_architecture_path() -> bool:
        """Check if any changed path touches base classes or shared modules."""
        return any(
            re.search(pattern, path) for path in changed_paths for pattern in architecture_patterns
        )

    def _has_new_tool_path() -> bool:
        """Check if any changed path is a new tool or MCP endpoint."""
        return any(
            re.search(pattern, path) for path in changed_paths for pattern in new_tool_patterns
        )

    # Check for Tier 3 triggers (highest priority - checked before line count tiers)
    tier3_triggers = [
        any(path.endswith(".sql") for path in changed_paths),
        total_lines > 500,
        _has_security_path(),
        _has_architecture_path(),
        _has_new_tool_path(),
    ]

    if any(tier3_triggers):
        return "TIER_3_CRITICAL", (
            f"Critical review required - {total_lines} lines, critical paths"
        )

    # Check for Tier 2 (10-500 lines)
    if 10 <= total_lines <= 500:
        return "TIER_2_STANDARD", (f"TMG + CRS + CE review required - {total_lines} lines changed")

    # Check for Tier 1 (<10 lines, single non-exempt file, no security, no new tests)
    if total_lines < 10 and len(non_exempt_files) == 1 and not has_test_files:
        return "TIER_1_SELF", (f"Self-review sufficient - {total_lines} lines in single file")

    # Default to Tier 2 if unsure (multiple files, etc.)
    return "TIER_2_STANDARD", "TMG + CRS + CE review required - default tier"


# Import shared review format utilities (single source of truth).
# In CI, the package may not be installed, so we use importlib to load
# the module file directly without triggering the package's __init__.py.
try:
    from hestai_mcp.modules.tools.shared.review_formats import (
        VALID_ROLES as _VALID_ROLES,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_ce_approval as _has_ce_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_civ_approval as _has_civ_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_crs_approval as _has_crs_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_crs_model_approval as _has_crs_model_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_ho_review as _has_ho_review,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_pe_approval as _has_pe_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_tmg_approval as _has_tmg_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        matches_approval_pattern as _matches_approval_pattern,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        parse_review_metadata as _parse_review_metadata,
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
    _has_ho_review = _review_formats.has_ho_review
    _has_tmg_approval = _review_formats.has_tmg_approval
    _has_civ_approval = _review_formats.has_civ_approval
    _has_pe_approval = _review_formats.has_pe_approval
    _parse_review_metadata = _review_formats.parse_review_metadata
    _VALID_ROLES = _review_formats.VALID_ROLES


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

        # --- Metadata extraction and cross-validation ---
        # Extract structured metadata from all texts for machine-readable checks.
        # When metadata IS present, also run regex on the same comment.
        # If regex-extracted verdict contradicts metadata verdict, FAIL
        # (prevents spoofing: visible "BLOCKED" with hidden metadata "APPROVED").
        metadata_entries: list[dict[str, str | None]] = []
        for text in searchable_texts:
            meta = _parse_review_metadata(text)
            if meta is not None:
                metadata_entries.append(meta)
                # CROSS-VALIDATION: If metadata says a role gave an approval
                # verdict, the visible text in the same comment MUST also
                # match that approval via regex. Otherwise reject.
                meta_role = meta.get("role")
                meta_verdict = meta.get("verdict")
                if meta_role and meta_verdict:
                    # Only cross-validate recognized review roles.
                    # Unrecognized roles (e.g., agent names like
                    # "code-review-specialist") cannot satisfy any gate
                    # check, so mismatched metadata is irrelevant -- not
                    # a spoofing vector.
                    if meta_role not in _VALID_ROLES:
                        continue
                    # Only cross-validate approval verdicts (not BLOCKED/CONDITIONAL)
                    approval_keywords = {"APPROVED", "SELF-REVIEWED", "REVIEWED", "GO"}
                    if meta_verdict in approval_keywords:
                        # Strip metadata HTML comment lines before regex check so
                        # the hidden JSON tokens don't satisfy the pattern match.
                        visible_text = re.sub(r"<!--\s*review:.*?-->\s*", "", text)
                        # Strip fenced code blocks and inline code so that
                        # approval text inside code examples cannot spoof the
                        # cross-validation regex.
                        visible_text = re.sub(r"```.*?```", "", visible_text, flags=re.DOTALL)
                        visible_text = re.sub(r"`[^`]+`", "", visible_text)
                        regex_agrees = _matches_approval_pattern(
                            visible_text, meta_role, meta_verdict
                        )
                        if not regex_agrees:
                            return (
                                False,
                                f"❌ Cross-validation failure: metadata says "
                                f"{meta_role} {meta_verdict} but visible text "
                                f"does not match. Possible spoofing detected.",
                            )

        def _meta_has(
            role: str,
            verdict: str,
            provider: str | None = None,
        ) -> bool:
            """Check if metadata entries contain a matching approval."""
            for entry in metadata_entries:
                if (
                    entry.get("role") == role
                    and entry.get("verdict") == verdict
                    and (provider is None or entry.get("provider") == provider.lower())
                ):
                    return True
            return False

        # Check for required approvals based on tier.
        # 5-tier system (v2.0):
        #   TIER_1_SELF: IL SELF-REVIEWED OR HO REVIEWED OR CRS
        #   TIER_2_STANDARD: TMG + CRS + CE
        #   TIER_3_CRITICAL: TMG + CRS + CE + CIV
        #   TIER_4_STRATEGIC: TMG + CRS + CE + CIV + PE
        if tier == "TIER_1_SELF":
            # Try metadata first, then regex fallback
            if _meta_has("IL", "SELF-REVIEWED"):
                return True, "✓ Self-review found (metadata)"
            if _meta_has("HO", "REVIEWED"):
                return True, "✓ HO supervisory review found (metadata)"
            if _meta_has("CRS", "APPROVED"):
                return True, "✓ CRS approval satisfies self-review (metadata)"
            # Regex fallback for old comments without metadata
            if _has_approval(searchable_texts, "IL", "SELF-REVIEWED"):
                return True, "✓ Self-review found"
            if _has_approval(searchable_texts, "HO", "REVIEWED"):
                return True, "✓ HO supervisory review found"
            if _has_crs_approval(searchable_texts):
                return True, "✓ CRS approval satisfies self-review requirement"
            return False, "❌ Missing: IL SELF-REVIEWED or HO REVIEWED comment"

        elif tier == "TIER_2_STANDARD":
            # T2 requires TMG + CRS + CE
            meta_tmg = _meta_has("TMG", "APPROVED")
            meta_crs = _meta_has("CRS", "APPROVED")
            meta_ce = _meta_has("CE", "APPROVED")

            has_tmg = _has_tmg_approval(searchable_texts)
            has_crs = _has_crs_approval(searchable_texts)
            has_ce = _has_ce_approval(searchable_texts)

            got_tmg = meta_tmg or has_tmg
            got_crs = meta_crs or has_crs
            got_ce = meta_ce or has_ce

            if got_tmg and got_crs and got_ce:
                return True, "✓ TMG, CRS, and CE approvals found"

            missing = []
            if not got_tmg:
                missing.append("TMG APPROVED or TMG GO")
            if not got_crs:
                missing.append("CRS APPROVED or CRS GO")
            if not got_ce:
                missing.append("CE APPROVED or CE GO")
            return False, f"❌ Missing: {', '.join(missing)}"

        elif tier == "TIER_3_CRITICAL":
            # T3 requires TMG + CRS + CE + CIV
            meta_tmg = _meta_has("TMG", "APPROVED")
            meta_crs = _meta_has("CRS", "APPROVED")
            meta_ce = _meta_has("CE", "APPROVED")
            meta_civ = _meta_has("CIV", "APPROVED")

            has_tmg = _has_tmg_approval(searchable_texts)
            has_crs = _has_crs_approval(searchable_texts)
            has_ce = _has_ce_approval(searchable_texts)
            has_civ = _has_civ_approval(searchable_texts)

            got_tmg = meta_tmg or has_tmg
            got_crs = meta_crs or has_crs
            got_ce = meta_ce or has_ce
            got_civ = meta_civ or has_civ

            if got_tmg and got_crs and got_ce and got_civ:
                return True, "✓ TMG, CRS, CE, and CIV approvals found"

            missing = []
            if not got_tmg:
                missing.append("TMG APPROVED or TMG GO")
            if not got_crs:
                missing.append("CRS APPROVED or CRS GO")
            if not got_ce:
                missing.append("CE APPROVED or CE GO")
            if not got_civ:
                missing.append("CIV APPROVED or CIV GO")
            return False, f"❌ Missing: {', '.join(missing)}"

        elif tier == "TIER_4_STRATEGIC":
            # T4 requires TMG + CRS + CE + CIV + PE
            meta_tmg = _meta_has("TMG", "APPROVED")
            meta_crs = _meta_has("CRS", "APPROVED")
            meta_ce = _meta_has("CE", "APPROVED")
            meta_civ = _meta_has("CIV", "APPROVED")
            meta_pe = _meta_has("PE", "APPROVED")

            has_tmg = _has_tmg_approval(searchable_texts)
            has_crs = _has_crs_approval(searchable_texts)
            has_ce = _has_ce_approval(searchable_texts)
            has_civ = _has_civ_approval(searchable_texts)
            has_pe = _has_pe_approval(searchable_texts)

            got_tmg = meta_tmg or has_tmg
            got_crs = meta_crs or has_crs
            got_ce = meta_ce or has_ce
            got_civ = meta_civ or has_civ
            got_pe = meta_pe or has_pe

            if got_tmg and got_crs and got_ce and got_civ and got_pe:
                return True, "✓ TMG, CRS, CE, CIV, and PE approvals found"

            missing = []
            if not got_tmg:
                missing.append("TMG APPROVED or TMG GO")
            if not got_crs:
                missing.append("CRS APPROVED or CRS GO")
            if not got_ce:
                missing.append("CE APPROVED or CE GO")
            if not got_civ:
                missing.append("CIV APPROVED or CIV GO")
            if not got_pe:
                missing.append("PE APPROVED or PE GO")
            return False, f"❌ Missing: {', '.join(missing)}"

        # SECURITY: Fail closed for unrecognized tiers (no silent approval)
        return False, f"❌ Unrecognized tier: {tier}"

    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        # SECURITY FIX: Fail closed in CI, permissive locally
        if "CI" in os.environ:
            return False, f"❌ Error checking PR comments: {e}"
        return True, "Unable to check PR comments (local mode)"


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
            print("   -- or --")
            print("   Add comment: 'HO REVIEWED: [rationale after delegated implementation]'")
            print("   Example: 'IL SELF-REVIEWED: Fixed typo in error message'")
        elif tier == "TIER_2_STANDARD":
            print("   Need comments:")
            print("   - 'TMG APPROVED: [test assessment]' (or TMG GO:)")
            print("   - 'CRS APPROVED: [assessment]' (or CRS GO:)")
            print("   - 'CE APPROVED: [critical assessment]' (or CE GO:)")
        elif tier == "TIER_3_CRITICAL":
            print("   Need comments:")
            print("   - 'TMG APPROVED: [test assessment]' (or TMG GO:)")
            print("   - 'CRS APPROVED: [assessment]' (or CRS GO:)")
            print("   - 'CE APPROVED: [critical assessment]' (or CE GO:)")
            print("   - 'CIV APPROVED: [implementation assessment]' (or CIV GO:)")
        elif tier == "TIER_4_STRATEGIC":
            print("   Need comments:")
            print("   - 'TMG APPROVED: [test assessment]' (or TMG GO:)")
            print("   - 'CRS APPROVED: [assessment]' (or CRS GO:)")
            print("   - 'CE APPROVED: [critical assessment]' (or CE GO:)")
            print("   - 'CIV APPROVED: [implementation assessment]' (or CIV GO:)")
            print("   - 'PE APPROVED: [strategic assessment]' (or PE GO:)")

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
