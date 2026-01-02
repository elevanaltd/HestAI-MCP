"""
Gating Module - OA-I6 Tool Gating Enforcement.

This module implements the tool gating mechanism for HestAI agents,
checking if an agent session has a valid Odyssean Anchor before
allowing work tools to execute.

OA-I6: TOOL GATING ENFORCEMENT
"Work tools MUST check for a valid anchor before executing.
Validation alone is insufficient; enforcement is mandatory."

Key Features:
- GatingResult dataclass for structured responses
- has_valid_anchor() function for anchor state checks
- Path traversal prevention (security)
- Graceful error handling

GitHub Issue: #11
ADR: docs/adr/adr-0036-odyssean-anchor-binding.md Amendment 01
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


# =============================================================================
# Result Dataclass
# =============================================================================


@dataclass
class GatingResult:
    """Result from has_valid_anchor check.

    Attributes:
        valid: Whether the session has a valid anchor
        role: The agent's role if validated (None if invalid)
        tier: The validation tier if validated (None if invalid)
        validated_at: ISO8601 timestamp of validation (None if invalid)
        error: Error message if validation failed (None if valid)
    """

    valid: bool
    role: str | None = None
    tier: str | None = None
    validated_at: str | None = None
    error: str | None = None


# =============================================================================
# Session ID Validation (Security)
# =============================================================================


def _validate_session_id(session_id: str) -> tuple[bool, str]:
    """
    Validate session_id to prevent path traversal attacks.

    Reuses validation pattern from odyssean_anchor.py for consistency.

    Args:
        session_id: Session ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Reject empty session_id
    if not session_id:
        return False, "session_id cannot be empty"

    # Reject absolute paths (start with /)
    if session_id.startswith("/"):
        return False, "session_id contains invalid path characters (absolute path not allowed)"

    # Reject parent directory traversal (..)
    if ".." in session_id:
        return (
            False,
            "session_id contains invalid path characters (parent traversal not allowed)",
        )

    # Reject forward slashes (subdirectory traversal)
    if "/" in session_id:
        return False, "session_id contains invalid path characters (slash not allowed)"

    # Reject backslashes (Windows path separators)
    if "\\" in session_id:
        return False, "session_id contains invalid path characters (backslash not allowed)"

    return True, ""


# =============================================================================
# Main Gating Function
# =============================================================================


def has_valid_anchor(session_id: str, working_dir: str) -> GatingResult:
    """
    Check if an agent session has a valid Odyssean Anchor.

    This function is used by work tools to enforce OA-I6: tool gating.
    Tools MUST call this before executing privileged operations.

    Checks:
    1. Session ID format is valid (no path traversal)
    2. Session directory exists
    3. anchor.json file exists in session directory
    4. anchor.json contains validated=True

    Args:
        session_id: Session ID from clock_in
        working_dir: Project working directory path

    Returns:
        GatingResult with validation status and anchor metadata if valid

    Example:
        >>> result = has_valid_anchor("abc-123", "/path/to/project")
        >>> if not result.valid:
        ...     return {"error": result.error}
        >>> # Proceed with privileged operation
    """
    # 1. Validate session_id format (security)
    is_valid, error_msg = _validate_session_id(session_id)
    if not is_valid:
        return GatingResult(valid=False, error=error_msg)

    # 2. Check working directory exists
    working_path = Path(working_dir)
    if not working_path.exists():
        return GatingResult(valid=False, error=f"Working directory not found: {working_dir}")

    # 3. Check session directory exists
    session_dir = working_path / ".hestai" / "sessions" / "active" / session_id
    if not session_dir.exists():
        return GatingResult(valid=False, error=f"Session not found: {session_id}")

    # 4. Check anchor.json exists
    anchor_file = session_dir / "anchor.json"
    if not anchor_file.exists():
        return GatingResult(
            valid=False,
            error=f"Anchor not validated for session: {session_id}. "
            "Run odyssean_anchor to validate identity.",
        )

    # 5. Read and parse anchor.json
    try:
        anchor_data = json.loads(anchor_file.read_text())
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse anchor.json for session {session_id}: {e}")
        return GatingResult(valid=False, error=f"Invalid anchor.json format: {e}")
    except OSError as e:
        logger.warning(f"Failed to read anchor.json for session {session_id}: {e}")
        return GatingResult(valid=False, error=f"Failed to read anchor.json: {e}")

    # 6. Check validated field exists and is True
    validated = anchor_data.get("validated")
    if validated is None:
        return GatingResult(valid=False, error="anchor.json missing 'validated' field")

    if validated is not True:
        return GatingResult(
            valid=False,
            error=f"Anchor validation failed: validated={validated}",
        )

    # 7. Extract metadata and return success
    return GatingResult(
        valid=True,
        role=anchor_data.get("role"),
        tier=anchor_data.get("tier"),
        validated_at=anchor_data.get("timestamp"),
        error=None,
    )
