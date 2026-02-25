"""
Shared review format constants and pattern matching utilities.

Single source of truth for review comment formats used by both:
- scripts/validate_review.py (CI gate validation)
- submit_review MCP tool (programmatic review submission)

Extracted from validate_review.py to prevent format drift (I2 tension).
"""

import re

# --- Review tier constants ---
TIER_0_EXEMPT = "TIER_0_EXEMPT"
TIER_1_SELF = "TIER_1_SELF"
TIER_2_CRS = "TIER_2_CRS"
TIER_3_FULL = "TIER_3_FULL"

# --- Valid roles and verdicts ---
VALID_ROLES: frozenset[str] = frozenset({"CRS", "CE", "IL"})
VALID_VERDICTS: frozenset[str] = frozenset({"APPROVED", "BLOCKED", "CONDITIONAL"})

# --- IL uses SELF-REVIEWED keyword instead of APPROVED ---
_IL_APPROVED_KEYWORD = "SELF-REVIEWED"


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
    # Allowed separators: whitespace, colon, em dash, en dash, hyphen.
    # No arbitrary tokens (like "and CRS (Codex)" or "BLOCKED") permitted between.
    pattern = re.compile(
        rf"\bCRS\s*\(\s*{re.escape(model)}\s*\)\s*[:—–\-]?\s*(?:APPROVED|GO)\b",
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


def format_review_comment(
    role: str,
    verdict: str,
    assessment: str,
    model_annotation: str | None = None,
) -> str:
    """Format a review comment that will clear the review gate.

    Produces comments in the canonical format that matches_approval_pattern()
    will accept. This ensures submit_review produces gate-clearing comments.

    For IL role with APPROVED verdict, the keyword is mapped to SELF-REVIEWED.
    For BLOCKED/CONDITIONAL verdicts, the comment uses the verdict directly
    (these don't clear the gate but are valid review comments).

    Args:
        role: Reviewer role (CRS, CE, IL).
        verdict: Review verdict (APPROVED, BLOCKED, CONDITIONAL).
        assessment: Review assessment content.
        model_annotation: Optional model name (e.g., 'Gemini') for annotation.

    Returns:
        Formatted review comment string.
    """
    # Map IL APPROVED to SELF-REVIEWED keyword
    keyword = _IL_APPROVED_KEYWORD if role == "IL" and verdict == "APPROVED" else verdict

    # Build the prefix with optional model annotation
    prefix = f"{role} ({model_annotation})" if model_annotation else role

    return f"{prefix} {keyword}: {assessment}"
