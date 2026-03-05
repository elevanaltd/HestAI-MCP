"""
Shared review format constants and pattern matching utilities.

Single source of truth for review comment formats used by both:
- scripts/validate_review.py (CI gate validation)
- submit_review MCP tool (programmatic review submission)

Extracted from validate_review.py to prevent format drift (I2 tension).
"""

import json
import re

# --- Review tier constants ---
TIER_0_EXEMPT = "TIER_0_EXEMPT"
TIER_1_SELF = "TIER_1_SELF"
TIER_2_STANDARD = "TIER_2_STANDARD"
TIER_3_STRICT = "TIER_3_STRICT"

# --- Valid roles and verdicts ---
VALID_ROLES: frozenset[str] = frozenset({"CRS", "CE", "IL", "HO"})
VALID_VERDICTS: frozenset[str] = frozenset({"APPROVED", "BLOCKED", "CONDITIONAL"})

# --- IL uses SELF-REVIEWED keyword instead of APPROVED ---
_IL_APPROVED_KEYWORD = "SELF-REVIEWED"

# --- HO uses REVIEWED keyword instead of APPROVED ---
_HO_APPROVED_KEYWORD = "REVIEWED"


def matches_approval_pattern(text: str, prefix: str, keyword: str) -> bool:
    """Check if text matches a flexible approval pattern.

    Matches patterns like:
      - 'CRS APPROVED:' (original exact format)
      - 'CRS (Gemini): APPROVED' (parenthetical model annotation with colon)
      - 'CRS (Gemini) --- APPROVED' (parenthetical with em dash separator)
      - 'CRS (Gemini) -- APPROVED' (parenthetical with en dash separator)
      - 'CRS (Gemini) - APPROVED' (parenthetical with hyphen separator)
      - 'CRS --- APPROVED' (em dash separator, no parenthetical)
      - 'CRS: APPROVED' (colon separator, no parenthetical)
      - 'CRS  APPROVED' (extra whitespace)
      - 'IL SELF-REVIEWED:' and 'IL (Claude): SELF-REVIEWED:'
      - '| CRS | Gemini | **APPROVED** |' (markdown table with bold)

    Uses word boundaries around both prefix and keyword to prevent false
    positives (e.g., 'XCRS' must not match 'CRS', 'APPROVEDLY' must not
    match 'APPROVED').

    Strips markdown bold/italic formatting before matching, then checks
    each line for both tokens in order with word boundaries.

    Args:
        text: The text to search for the approval pattern.
        prefix: The role prefix (e.g., 'CRS', 'CE', 'IL').
        keyword: The approval keyword (e.g., 'APPROVED', 'SELF-REVIEWED', 'GO').

    Returns:
        True if the pattern is found, False otherwise.
    """
    # Strip markdown bold/italic markers so **APPROVED** matches as APPROVED
    cleaned = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)

    prefix_re = re.compile(rf"\b{re.escape(prefix)}\b")
    keyword_re = re.compile(rf"\b{re.escape(keyword)}\b")

    for line in cleaned.splitlines():
        prefix_match = prefix_re.search(line)
        if not prefix_match:
            continue
        # Keyword must appear after the prefix on the same line
        keyword_match = keyword_re.search(line, prefix_match.end())
        if keyword_match:
            return True

    return False


def _has_approval(texts: list[str], prefix: str, keyword: str) -> bool:
    """Check if any text in the list matches the approval pattern."""
    return any(matches_approval_pattern(t, prefix, keyword) for t in texts)


def has_crs_approval(texts: list[str]) -> bool:
    """Check if any text contains a CRS approval (APPROVED or GO).

    Args:
        texts: List of comment/body texts to search.

    Returns:
        True if CRS approval found.
    """
    return _has_approval(texts, "CRS", "APPROVED") or _has_approval(texts, "CRS", "GO")


def has_crs_model_approval(texts: list[str], model: str) -> bool:
    """Check if any text contains a CRS approval from a specific model.

    Matches patterns like 'CRS (Gemini) APPROVED:' or 'CRS (Gemini): GO'.
    The model tag must be directly followed by the approval keyword with only
    separator characters (whitespace, colon, dashes) in between. This prevents
    spoofing where a single APPROVED keyword satisfies multiple model checks,
    or where intervening tokens like BLOCKED are ignored.

    Args:
        texts: List of comment/body texts to search.
        model: The model name to match (e.g., 'Gemini', 'Codex').

    Returns:
        True if model-specific CRS approval found.
    """
    # Strict pattern: CRS(model) followed by only separator chars then APPROVED|GO.
    # Allowed separators: whitespace, colon, em dash, en dash, hyphen (0 or more).
    # No arbitrary tokens (like "and CRS (Codex)" or "BLOCKED") permitted between.
    pattern = re.compile(
        rf"\bCRS\s*\(\s*{re.escape(model)}\s*\)\s*[:—–\-]*\s*(?:APPROVED|GO)\b",
        re.IGNORECASE,
    )

    for text in texts:
        # Strip markdown bold/italic markers
        cleaned = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
        for line in cleaned.splitlines():
            if pattern.search(line):
                return True
    return False


def has_ce_approval(texts: list[str]) -> bool:
    """Check if any text contains a CE approval (APPROVED or GO).

    Args:
        texts: List of comment/body texts to search.

    Returns:
        True if CE approval found.
    """
    return _has_approval(texts, "CE", "APPROVED") or _has_approval(texts, "CE", "GO")


def has_il_self_review(texts: list[str]) -> bool:
    """Check if any text contains an IL self-review.

    Args:
        texts: List of comment/body texts to search.

    Returns:
        True if IL SELF-REVIEWED found.
    """
    return _has_approval(texts, "IL", _IL_APPROVED_KEYWORD)


def has_ho_review(texts: list[str]) -> bool:
    """Check if any text contains an HO supervisory review.

    When HO delegates to IL and then reviews the work, this constitutes
    a supervisory review (higher authority than self-review) and satisfies T1.

    Matches patterns like:
      - 'HO REVIEWED: delegated to IL, verified output'
      - 'HO (Claude): REVIEWED: verified'

    Args:
        texts: List of comment/body texts to search.

    Returns:
        True if HO REVIEWED found.
    """
    return _has_approval(texts, "HO", "REVIEWED")


def format_review_comment(
    role: str,
    verdict: str,
    assessment: str,
    model_annotation: str | None = None,
    commit_sha: str | None = None,
) -> str:
    """Format a review comment that will clear the review gate.

    Produces comments in the canonical format that matches_approval_pattern()
    will accept. This ensures submit_review produces gate-clearing comments.

    For IL role with APPROVED verdict, the keyword is mapped to SELF-REVIEWED.
    For HO role with APPROVED verdict, the keyword is mapped to REVIEWED.
    For BLOCKED/CONDITIONAL verdicts, the comment uses the verdict directly
    (these don't clear the gate but are valid review comments).

    Appends a machine-readable metadata HTML comment on a second line for
    structured audit trail parsing.

    Args:
        role: Reviewer role (CRS, CE, IL, HO).
        verdict: Review verdict (APPROVED, BLOCKED, CONDITIONAL).
        assessment: Review assessment content.
        model_annotation: Optional model name (e.g., 'Gemini') for annotation.
        commit_sha: Optional PR head SHA the reviewer verified.

    Returns:
        Formatted review comment string with metadata on line 2.
    """
    # Map IL APPROVED to SELF-REVIEWED, HO APPROVED to REVIEWED
    if role == "IL" and verdict == "APPROVED":
        keyword = _IL_APPROVED_KEYWORD
    elif role == "HO" and verdict == "APPROVED":
        keyword = _HO_APPROVED_KEYWORD
    else:
        keyword = verdict

    # Build the prefix with optional model annotation
    prefix = f"{role} ({model_annotation})" if model_annotation else role

    human_line = f"{prefix} {keyword}: {assessment}"

    # Build metadata dict
    metadata: dict[str, str | None] = {
        "role": role,
        "provider": model_annotation.lower() if model_annotation else None,
        "verdict": keyword,
        "sha": commit_sha[:7] if commit_sha else None,
    }
    meta_json = json.dumps(metadata, separators=(",", ":"))
    meta_line = f"<!-- review: {meta_json} -->"

    return f"{human_line}\n{meta_line}"


# --- Metadata regex for parsing structured review metadata ---
_METADATA_RE = re.compile(r"<!-- review: (\{.*?\}) -->")


def parse_review_metadata(text: str) -> dict[str, str | None] | None:
    """Extract structured metadata from a review comment.

    Looks for ``<!-- review: {...} -->`` HTML comment and parses the JSON.

    Args:
        text: Review comment text to parse.

    Returns:
        Parsed metadata dict or None if not found or invalid.
    """
    # Strip markdown code blocks and inline code to avoid matching
    # example metadata in documentation (e.g., PR body with backtick-quoted examples).
    stripped = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    stripped = re.sub(r"`[^`]+`", "", stripped)
    match = _METADATA_RE.search(stripped)
    if not match:
        return None
    try:
        return json.loads(match.group(1))  # type: ignore[no-any-return]
    except (json.JSONDecodeError, ValueError):
        return None


def extract_review_metadata(texts: list[str]) -> list[dict[str, str | None]]:
    """Batch extraction of metadata from multiple comments.

    Args:
        texts: List of comment texts to scan.

    Returns:
        List of parsed metadata dicts (only for comments that have metadata).
    """
    results: list[dict[str, str | None]] = []
    for text in texts:
        meta = parse_review_metadata(text)
        if meta is not None:
            results.append(meta)
    return results
