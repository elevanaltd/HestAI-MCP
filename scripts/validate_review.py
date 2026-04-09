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

# --- Advisory bot accounts ---
# Bot comments are ADVISORY ONLY: they provide context for reviewers but NEVER
# satisfy or block review gates.  The canonical list uses GitHub's [bot] suffix
# convention; _BOT_LOGIN_SET is derived for comment filtering.
ADVISORY_BOTS: list[str] = [
    "cubic-dev-ai[bot]",
    "qodo-code-review[bot]",
    "coderabbitai[bot]",
    "github-copilot[bot]",
]

# --- Known bot account logins whose comments must be excluded from approval matching ---
# Derived from ADVISORY_BOTS (strip "[bot]" suffix) plus legacy login variants
# that GitHub may use for the same accounts.
_BOT_LOGIN_SET: frozenset[str] = frozenset(
    {name.removesuffix("[bot]") for name in ADVISORY_BOTS}
    | {
        "github-actions",
        "copilot",  # Legacy login variant for github-copilot[bot]
        "Copilot",  # GitHub API returns capital-C variant
        "cubic-bot",
        "qodo-merge-pro",
        "qodo-merge-pro-for-open-source",
    }
)


def get_changed_files() -> list[dict[str, Any]]:
    """Get list of changed files with line counts and file status.

    Each returned dict includes:
      - path: file path
      - added: lines added
      - deleted: lines deleted
      - total_changed: added + deleted
      - status: git status letter (A=added, M=modified, D=deleted, R=renamed)
    """
    try:
        # In CI, compare against base branch; locally use cached
        if "CI" in os.environ:
            # Get the base branch (usually main)
            base_ref = os.environ.get("GITHUB_BASE_REF", "origin/main")
            numstat_cmd = ["git", "diff", f"{base_ref}...HEAD", "--numstat"]
            status_cmd = ["git", "diff", f"{base_ref}...HEAD", "--name-status"]
        else:
            # Local: check staged files
            numstat_cmd = ["git", "diff", "--cached", "--numstat"]
            status_cmd = ["git", "diff", "--cached", "--name-status"]

        # Get diff stats (line counts)
        result = subprocess.run(numstat_cmd, capture_output=True, text=True, check=True)

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

        # Get file statuses (A=added, M=modified, D=deleted, R=renamed)
        status_result = subprocess.run(status_cmd, capture_output=True, text=True, check=True)
        status_map: dict[str, str] = {}
        for line in status_result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                # Status is first char of first field (e.g., "M", "A", "R100")
                status_letter = parts[0][0]
                filename = parts[-1]  # Last field is the path (handles renames)
                status_map[filename] = status_letter

        # Merge status into file dicts
        for f in files:
            f["status"] = status_map.get(f["path"], "M")  # Default to M if unknown

        return files
    except subprocess.CalledProcessError as e:
        # SECURITY FIX: Fail closed in CI, permissive locally
        if "CI" in os.environ:
            print(f"❌ Git command failed in CI: {e}", file=sys.stderr)
            sys.exit(1)
        return []


def _is_generated_json(path: str) -> bool:
    """Check if a JSON file is a generated/lock file (exempt) vs hand-edited (not exempt).

    Per governance rule ``**/*.json[when:generated_file]``, JSON is exempt ONLY
    when it is a generated file. Hand-edited config files (package.json,
    tsconfig.json, .eslintrc.json, pyrightconfig.json, .vscode/*.json) are NOT
    exempt because humans maintain them and changes can introduce bugs.

    Only truly auto-generated JSON (lock files, coverage reports) qualifies.
    """
    generated_patterns = [
        r"(^|/)package-lock\.json$",
        r"(^|/)coverage/.*\.json$",
    ]
    return any(re.search(pattern, path) for pattern in generated_patterns)


# --- Facet → Required Reviewers mapping ---
FACET_ROLE_MAP: dict[str, set[str]] = {
    "META_CONTROL_PLANE": {"CIV", "CE", "CRS", "SR", "TMG"},  # PE excluded: T4 is manual-only
    "EXECUTABLE_SPEC": {"CE", "SR"},
    "GOVERNANCE": {"SR"},
    "SECURITY": {"CIV", "CE", "CRS", "TMG"},
    "ROUTINE_CODE": {"CE", "CRS", "TMG"},
}

# Hardcoded paths that always trigger META_CONTROL_PLANE
_META_CONTROL_PLANE_PATHS = {
    "scripts/validate_review.py",
    ".github/workflows/review-gate.yml",
}

# Security path patterns
_SECURITY_PATTERNS = [
    r"(^|/)auth/",
    r"(^|/)session/",
    r"(^|/)config/env",
    r"(^|/)path_utils",
]

# OCTAVE types that classify as EXECUTABLE_SPEC
_EXECUTABLE_SPEC_TYPES = {"AGENT_DEFINITION", "SKILL"}


def _sniff_octave_type(path: str) -> str:
    """Read META.TYPE from an OCTAVE file. Max 50 lines, fail-safe.

    Args:
        path: File path to read.

    Returns:
        The TYPE value string (e.g., 'AGENT_DEFINITION', 'RULE') or empty string.
    """
    try:
        with open(path, encoding="utf-8") as f:
            for _ in range(50):
                line = f.readline()
                if not line:
                    break
                if "TYPE::" in line:
                    parts = line.split("::", 1)
                    if len(parts) == 2:
                        return parts[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""


def _classify_file_facet(path: str) -> str | None:
    """Classify a single file path into a content facet.

    Returns:
        Facet name string, or None if the file is exempt.
    """
    # Bundled hub skill/pattern files (.md but NOT exempt — governance artifacts)
    # These define agent behavior and must be classified before exempt check
    if "/library/skills/" in path and path.endswith("/SKILL.md"):
        return "EXECUTABLE_SPEC"
    if "/library/patterns/" in path and path.endswith(".md"):
        return "EXECUTABLE_SPEC"

    # Exempt patterns
    exempt_patterns = [
        r".*(?<!\.oct)\.md$",  # Markdown exempt, but NOT .oct.md
        r"^tests/.*$",
        r".*\.lock$",
    ]

    # Check standard exempt patterns
    if any(re.match(pattern, path) for pattern in exempt_patterns):
        return None

    # JSON: only generated ones are exempt
    if path.endswith(".json"):
        if _is_generated_json(path):
            return None
        # Non-generated JSON is ROUTINE_CODE
        return "ROUTINE_CODE"

    # META_CONTROL_PLANE: hardcoded paths
    if path in _META_CONTROL_PLANE_PATHS:
        return "META_CONTROL_PLANE"
    # Also match review-requirements.oct.md
    if "review-requirements.oct.md" in path:
        return "META_CONTROL_PLANE"

    # .oct.md files: classify by path or sniff TYPE
    if path.endswith(".oct.md"):
        # Agent/skill .oct.md files are always EXECUTABLE_SPEC by path
        # (even if deleted and can't be sniffed for TYPE)
        if "/library/agents/" in path or "/library/skills/" in path:
            return "EXECUTABLE_SPEC"
        # For other .oct.md files, sniff TYPE to distinguish
        octave_type = _sniff_octave_type(path)
        if octave_type in _EXECUTABLE_SPEC_TYPES:
            return "EXECUTABLE_SPEC"
        # All other .oct.md (RULE, STANDARD, NORTH_STAR_SUMMARY, unknown) -> GOVERNANCE
        return "GOVERNANCE"

    # Security paths
    if any(re.search(pattern, path) for pattern in _SECURITY_PATTERNS):
        return "SECURITY"

    # Architecture/infrastructure paths (base classes, shared modules, hooks, tools, MCP)
    architecture_patterns = [
        r"(^|/)base\.py$",
        r"/shared/",
        r"(^|/)abstract/",
        r"(^|/)hooks/",
        r"(^|/)modules/tools/",
        r"(^|/)mcp/tools/",
        r"^clink/agents/",
    ]
    if any(re.search(pattern, path) for pattern in architecture_patterns):
        return "SECURITY"  # Architecture changes require same elevated review as security

    # SQL files -> SECURITY (high-impact data changes)
    if path.endswith(".sql"):
        return "SECURITY"

    # Code files (.py, .ts, .js, etc.) -> ROUTINE_CODE
    code_extensions = {".py", ".ts", ".js", ".tsx", ".jsx", ".sh"}
    if any(path.endswith(ext) for ext in code_extensions):
        return "ROUTINE_CODE"

    # YAML, TOML, config files -> ROUTINE_CODE
    if any(path.endswith(ext) for ext in (".yml", ".yaml", ".toml", ".cfg", ".ini")):
        return "ROUTINE_CODE"

    # Default: treat as ROUTINE_CODE (fail-safe: gets reviewed)
    return "ROUTINE_CODE"


def classify_pr_facets(
    files: list[dict[str, Any]],
) -> tuple[set[str], set[str], str, str]:
    """Classify PR files into content facets and compute required reviewers.

    Each file is assigned a facet based on its path and content type.
    Required reviewers = union of all facets' role requirements.
    Tier label is backward-computed from the reviewer set.

    Args:
        files: List of changed file dicts with 'path' and 'total_changed' keys.

    Returns:
        Tuple of (facets, required_roles, tier_label, reason):
        - facets: Set of content facets found (e.g., {'ROUTINE_CODE', 'GOVERNANCE'})
        - required_roles: Set of reviewer roles needed (e.g., {'CE', 'CRS', 'TMG', 'SR'})
        - tier_label: Backward-computed display tier (TIER_0_EXEMPT .. TIER_4_STRATEGIC)
        - reason: Human-readable explanation
    """
    facets: set[str] = set()
    non_exempt_files = []

    for f in files:
        facet = _classify_file_facet(f["path"])
        if facet is not None:
            facets.add(facet)
            non_exempt_files.append(f)

    # If all files are exempt, no review needed
    if not facets:
        return set(), set(), "TIER_0_EXEMPT", "No review required - only exempt files changed"

    # Compute required roles from facets
    required_roles: set[str] = set()
    for facet in facets:
        required_roles |= FACET_ROLE_MAP.get(facet, set())

    # Line count escalation: >500 lines adds CIV for elevated review
    total_lines = sum(f["total_changed"] for f in non_exempt_files)
    if total_lines > 500 and "CIV" not in required_roles:
        required_roles.add("CIV")

    # Check for T1 self-review eligibility
    has_new_test_files = any(
        f.get("status") == "A" and f["path"].startswith("tests/") for f in files
    )

    if (
        total_lines < 10
        and len(non_exempt_files) == 1
        and not has_new_test_files
        and "SECURITY" not in facets
        and "META_CONTROL_PLANE" not in facets
        and "EXECUTABLE_SPEC" not in facets
    ):
        return (
            facets,
            set(),  # No external reviewers needed for T1
            "TIER_1_SELF",
            f"Self-review sufficient - {total_lines} lines in single file",
        )

    # Compute tier label from role set
    if "PE" in required_roles:
        tier_label = "TIER_4_STRATEGIC"
    elif "CIV" in required_roles:
        tier_label = "TIER_3_CRITICAL"
    else:
        tier_label = "TIER_2_STANDARD"

    facet_names = ", ".join(sorted(facets))
    role_names = ", ".join(sorted(required_roles))
    reason = f"Facets: [{facet_names}] -> Reviewers: [{role_names}]"
    return facets, required_roles, tier_label, reason


def determine_review_tier(files: list[dict[str, Any]]) -> tuple[str, str]:
    """Determine required review tier based on changed files.

    Backward-compatible wrapper around classify_pr_facets(). Returns
    (tier_label, reason) for callers that only need the tier string.
    """
    _, _, tier_label, reason = classify_pr_facets(files)
    return tier_label, reason


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
        has_gr_approval as _has_gr_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_ho_review as _has_ho_review,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_pe_approval as _has_pe_approval,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_self_review as _has_self_review,
    )
    from hestai_mcp.modules.tools.shared.review_formats import (
        has_sr_approval as _has_sr_approval,
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
    if not _module_path.exists():
        raise FileNotFoundError(
            f"review_formats.py not found at {_module_path}. "
            "Expected relative to scripts/ directory."
        ) from None
    _spec = importlib.util.spec_from_file_location("review_formats", _module_path)
    if _spec is None or _spec.loader is None:
        raise FileNotFoundError(
            f"review_formats.py not found at {_module_path}. "
            "Expected relative to scripts/ directory."
        ) from None
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
    _has_self_review = _review_formats.has_self_review
    _has_sr_approval = _review_formats.has_sr_approval
    _has_gr_approval = _review_formats.has_gr_approval
    _parse_review_metadata = _review_formats.parse_review_metadata
    _VALID_ROLES = _review_formats.VALID_ROLES


def _has_approval(texts: list[str], prefix: str, keyword: str) -> bool:
    """Check if any text in the list matches the approval pattern."""
    return any(_matches_approval_pattern(t, prefix, keyword) for t in texts)


def check_pr_comments(
    _tier_or_roles: set[str] | str | None = None,
    *,
    required_roles: set[str] | None = None,
    tier: str = "",
) -> tuple[bool, str]:
    """Check if required review comments and PR body contain approval patterns.

    Supports two calling conventions for backward compatibility:
    - New: check_pr_comments(required_roles={'CE', 'CRS'}, tier='TIER_2_STANDARD')
    - Old: check_pr_comments('TIER_2_STANDARD')  (string -> uses tier->roles mapping)

    For TIER_1_SELF with empty required_roles, falls back to self-review logic.
    For all other tiers, validates that ALL required_roles have posted approvals.
    """
    # Handle backward compat: positional string arg is the tier (old API)
    if isinstance(_tier_or_roles, str):
        tier = _tier_or_roles
    elif isinstance(_tier_or_roles, set):
        required_roles = _tier_or_roles

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
        # Exclude ALL bot comments to prevent false positive approval matches.
        # Bot review prose (CodeRabbit, Copilot, Cubic, github-actions) often
        # contains "APPROVED", "GO", etc. which would falsely clear the gate.
        def _is_bot_comment(comment: dict[str, Any]) -> bool:
            """Check if a comment is from a bot author."""
            login = comment.get("author", {}).get("login", "")
            if login in _BOT_LOGIN_SET:
                return True
            # Catch any other [bot]-suffixed accounts (GitHub convention)
            if login.endswith("[bot]"):
                return True
            # Legacy marker check for review-gate status comments
            return "<!-- review-gate-status -->" in comment.get("body", "")

        searchable_texts: list[str] = []
        pr_body = pr_data.get("body")
        if pr_body:
            searchable_texts.append(pr_body)

        # Filter comments, logging any bot comments that are skipped
        skipped_bots: list[str] = []
        for c in pr_data.get("comments", []):
            if _is_bot_comment(c):
                bot_login = c.get("author", {}).get("login", "unknown")
                skipped_bots.append(bot_login)
            else:
                searchable_texts.append(c.get("body", ""))

        if skipped_bots:
            print(
                f"   Skipped {len(skipped_bots)} bot comment(s) "
                f"(ADVISORY only, not counted for gate): "
                f"{', '.join(sorted(set(skipped_bots)))}"
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

        # --- Role-based approval checking ---
        # Role → approval checker dispatch
        _role_checkers: dict[str, Any] = {
            "TMG": lambda: _meta_has("TMG", "APPROVED") or _has_tmg_approval(searchable_texts),
            "CRS": lambda: _meta_has("CRS", "APPROVED") or _has_crs_approval(searchable_texts),
            "CE": lambda: _meta_has("CE", "APPROVED") or _has_ce_approval(searchable_texts),
            "CIV": lambda: _meta_has("CIV", "APPROVED") or _has_civ_approval(searchable_texts),
            "PE": lambda: _meta_has("PE", "APPROVED") or _has_pe_approval(searchable_texts),
            "SR": lambda: (
                _meta_has("SR", "APPROVED")
                or _has_sr_approval(searchable_texts)
                # Legacy GR visible-text check only (no _meta_has("GR") —
                # GR not in VALID_ROLES so metadata bypasses cross-validation)
                or _has_gr_approval(searchable_texts)
            ),
        }

        # TIER_1_SELF: self-review logic (no external reviewers required)
        if tier == "TIER_1_SELF" and (required_roles is None or len(required_roles) == 0):
            for entry in metadata_entries:
                if entry.get("verdict") == "SELF-REVIEWED":
                    return True, "✓ Self-review found (metadata)"
            if _meta_has("HO", "REVIEWED"):
                return True, "✓ HO supervisory review found (metadata)"
            if _meta_has("CRS", "APPROVED"):
                return True, "✓ CRS approval satisfies self-review (metadata)"
            if _has_self_review(searchable_texts):
                return True, "✓ Self-review found"
            if _has_approval(searchable_texts, "HO", "REVIEWED"):
                return True, "✓ HO supervisory review found"
            if _has_crs_approval(searchable_texts):
                return True, "✓ CRS approval satisfies self-review requirement"
            return False, "❌ Missing: SELF-REVIEWED or HO REVIEWED comment"

        # Determine effective roles to check
        effective_roles = required_roles if required_roles is not None else set()

        # DEPRECATED: Tier-only API cannot distinguish code vs governance PRs.
        # Use classify_pr_facets() + required_roles for accurate routing.
        # This fallback maps tiers to code-review roles only (no SR).
        if not effective_roles and tier:
            _tier_role_map: dict[str, set[str]] = {
                "TIER_2_STANDARD": {"TMG", "CRS", "CE"},
                "TIER_3_CRITICAL": {"TMG", "CRS", "CE", "CIV"},
                "TIER_4_STRATEGIC": {"TMG", "CRS", "CE", "CIV", "PE"},
            }
            effective_roles = _tier_role_map.get(tier, set())
            if not effective_roles:
                return False, f"❌ Unrecognized tier: {tier}"

        # Check each required role (SECURITY: fail-closed for unknown roles)
        missing = []
        for role in sorted(effective_roles):
            checker = _role_checkers.get(role)
            if checker is None or not checker():
                missing.append(f"{role} APPROVED or {role} GO")

        if not missing:
            role_names = ", ".join(sorted(effective_roles))
            return True, f"✓ All required approvals found ({role_names})"

        return False, f"❌ Missing: {', '.join(missing)}"

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


def _emit_json_summary(
    tier: str,
    reason: str,
    reviewers: list[str],
    status: str,
    required_count: int,
    found_count: int,
) -> None:
    """Emit a structured JSON summary as an HTML comment for machine parsing.

    The JSON is wrapped in an HTML comment so it doesn't appear in human-readable
    output but IS captured in the output variable by the CI workflow. The JS parser
    in review-gate.yml can extract this for structured data instead of relying on
    fragile regex patterns.

    Format: <!-- REVIEW_GATE_JSON:{"tier":"...","reason":"...",...} -->
    """
    summary = {
        "tier": tier,
        "reason": reason,
        "reviewers": reviewers,
        "status": status,
        "required_count": required_count,
        "found_count": found_count,
    }
    print(f"<!-- REVIEW_GATE_JSON:{json.dumps(summary)} -->")


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

    # Classify PR content into facets and compute required reviewers
    facets, required_roles, tier, reason = classify_pr_facets(files)
    print(f"\n📋 Review Tier: {tier}")
    print(f"   Reason: {reason}")

    # Check if tier is exempt
    if tier == "TIER_0_EXEMPT":
        print("✓ Review not required")
        _emit_json_summary(
            tier=tier,
            reason=reason,
            reviewers=[],
            status="pass",
            required_count=0,
            found_count=0,
        )
        return 0

    # Check for required approvals
    approved, message = check_pr_comments(required_roles=required_roles, tier=tier)
    print(f"   {message}")

    reviewers_list = sorted(required_roles)

    if not approved:
        # Compute actual found_count from the failure message.
        # check_pr_comments() returns missing roles as "{ROLE} APPROVED or {ROLE} GO".
        # Count how many required roles are listed as missing, then subtract.
        missing_count = sum(1 for role in required_roles if f"{role} APPROVED" in message)
        found_count = len(required_roles) - missing_count

        print("\n⚠️  Review Requirements:")
        if tier == "TIER_1_SELF":
            print("   Add comment: '{your-role} SELF-REVIEWED: [your rationale]'")
            print("   Any role or name accepted (e.g., IL, skills-expert, Shaun)")
            print("   -- or --")
            print("   Add comment: 'HO REVIEWED: [rationale after delegated work]'")
            print("   Example: 'skills-expert SELF-REVIEWED: Updated GATES section'")
        else:
            print("   Need comments:")
            for role in sorted(required_roles):
                print(f"   - '{role} APPROVED: [assessment]' (or {role} GO:)")

        _emit_json_summary(
            tier=tier,
            reason=reason,
            reviewers=reviewers_list,
            status="fail",
            required_count=len(required_roles),
            found_count=found_count,
        )

        # Only block in CI context
        if "CI" in os.environ:
            print("\n❌ Blocking merge - reviews required")
            return 1
        else:
            print("\n   ℹ️  Local check only - not blocking")
            return 0

    _emit_json_summary(
        tier=tier,
        reason=reason,
        reviewers=reviewers_list,
        status="pass",
        required_count=len(required_roles),
        found_count=len(required_roles),
    )
    print("\n✓ Review requirements satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
