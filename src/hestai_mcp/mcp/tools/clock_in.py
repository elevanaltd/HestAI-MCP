"""
ClockIn Tool - Register agent session start and return context paths.

This tool enables agents to "clock in" when starting a work session,
creating session metadata and returning context paths for initialization.

Part of the Context Steward session lifecycle management system.

Key Integration Points:
- Creates session directory structure in .hestai/sessions/active/
- Detects focus conflicts with active sessions
- Returns context paths from .hestai/context/ (OCTAVE files)
- Security: Path traversal prevention, role format validation

Note: Uses direct .hestai/ directory (ADR-0007), no symlinks or worktrees.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def validate_role_format(role: str) -> str:
    """
    Validate role name to prevent path traversal attacks and log forging.

    Args:
        role: Role name to validate

    Returns:
        Validated role name (stripped)

    Raises:
        ValueError: If role is empty, contains path separators, or control characters
    """
    if not role or not role.strip():
        raise ValueError("Role cannot be empty")

    # Path traversal prevention
    if ".." in role or "/" in role or "\\" in role:
        raise ValueError("Invalid role format - path separators not allowed")

    # Control character prevention (log forging security)
    if any(c in role for c in "\r\n\t"):
        raise ValueError("Invalid role format - control characters not allowed")

    return role.strip()


def validate_working_dir(working_dir: str) -> Path:
    """
    Validate working directory path.

    Args:
        working_dir: Working directory path to validate

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path traversal attempt detected
        FileNotFoundError: If directory doesn't exist
    """
    # Resolve to absolute path
    path = Path(working_dir).expanduser().resolve()

    # Check for path traversal patterns in original input
    if ".." in working_dir:
        raise ValueError("Path traversal attempt detected in working_dir")

    # Verify directory exists
    if not path.exists():
        raise FileNotFoundError(f"Working directory does not exist: {path}")

    if not path.is_dir():
        raise ValueError(f"Working directory path is not a directory: {path}")

    return path


def detect_focus_conflict(
    focus: str, active_sessions_dir: Path, current_session_id: str
) -> dict[str, Any] | None:
    """
    Detect if another active session has the same focus.

    Args:
        focus: Focus area to check
        active_sessions_dir: Path to active sessions directory
        current_session_id: Current session ID (to exclude from check)

    Returns:
        Conflict info dict if conflict detected, None otherwise
    """
    if not active_sessions_dir.exists():
        return None

    for session_dir in active_sessions_dir.iterdir():
        if not session_dir.is_dir():
            continue

        # Skip current session
        if session_dir.name == current_session_id:
            continue

        session_file = session_dir / "session.json"
        if not session_file.exists():
            continue

        try:
            session_data = json.loads(session_file.read_text())
            if session_data.get("focus") == focus:
                return {
                    "session_id": session_data["session_id"],
                    "role": session_data.get("role"),
                    "focus": session_data.get("focus"),
                }
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Error reading session file {session_file}: {e}")
            continue

    return None


def resolve_context_paths(working_dir: Path) -> list[str]:
    """
    Resolve context paths from .hestai/context/ directory.

    ADR-0007: Returns OCTAVE format context files from committed .hestai/ structure.

    Args:
        working_dir: Project root directory

    Returns:
        List of absolute paths to context files
    """
    context_paths = []
    hestai_context = working_dir / ".hestai" / "context"

    # Standard OCTAVE context files (ADR-0007)
    standard_files = [
        "PROJECT-CONTEXT.oct",
        "PROJECT-ROADMAP.oct",
        "PROJECT-CHECKLIST.oct",
        "PROJECT-HISTORY.oct",
        "context-negatives.oct",
    ]

    for file_name in standard_files:
        path = hestai_context / file_name
        if path.exists():
            context_paths.append(str(path))

    # Also check for project north star in workflow/
    workflow_path = working_dir / ".hestai" / "workflow" / "000-PROJECT-NORTH-STAR.oct.md"
    if workflow_path.exists():
        context_paths.append(str(workflow_path))

    return context_paths


def ensure_hestai_structure(working_dir: Path) -> str:
    """
    Ensure .hestai/ directory structure exists (ADR-0007).

    Creates direct .hestai/ directory with required subdirectories.
    No symlinks or worktrees - just plain directory structure.

    Args:
        working_dir: Project root directory

    Returns:
        Status: 'present' or 'created'
    """
    hestai_dir = working_dir / ".hestai"

    if hestai_dir.exists() and hestai_dir.is_dir():
        # Already exists - ensure subdirectories
        (hestai_dir / "sessions" / "active").mkdir(parents=True, exist_ok=True)
        (hestai_dir / "sessions" / "archive").mkdir(parents=True, exist_ok=True)
        (hestai_dir / "context").mkdir(parents=True, exist_ok=True)
        (hestai_dir / "workflow").mkdir(parents=True, exist_ok=True)
        (hestai_dir / "reports").mkdir(parents=True, exist_ok=True)
        return "present"

    # Create new structure
    hestai_dir.mkdir(parents=True, exist_ok=True)
    (hestai_dir / "sessions" / "active").mkdir(parents=True, exist_ok=True)
    (hestai_dir / "sessions" / "archive").mkdir(parents=True, exist_ok=True)
    (hestai_dir / "context").mkdir(parents=True, exist_ok=True)
    (hestai_dir / "workflow").mkdir(parents=True, exist_ok=True)
    (hestai_dir / "reports").mkdir(parents=True, exist_ok=True)

    logger.info(f"Created .hestai/ directory structure at {working_dir}")
    return "created"


def clock_in(
    role: str,
    working_dir: str,
    focus: str = "general",
    model: str | None = None,
) -> dict[str, Any]:
    """
    Register session start, create session directory, return context paths.

    ADR-0007: Uses direct .hestai/ directory structure (no symlinks/worktrees).

    Args:
        role: Agent role name (e.g., 'implementation-lead')
        working_dir: Project working directory path
        focus: Work focus area (e.g., 'b2-implementation')
        model: Optional AI model identifier

    Returns:
        dict with:
            - session_id: Generated UUID
            - context_paths: List of OCTAVE context file paths to load
            - focus_conflict: None or conflicting session info
            - structure_status: 'present' | 'created'

    Raises:
        ValueError: If validation fails (path traversal, invalid role)
        FileNotFoundError: If working_dir doesn't exist
    """
    # Validate inputs
    role = validate_role_format(role)
    working_dir_path = validate_working_dir(working_dir)

    # Ensure .hestai/ directory structure exists
    structure_status = ensure_hestai_structure(working_dir_path)

    # Get active sessions directory
    active_dir = working_dir_path / ".hestai" / "sessions" / "active"

    # Generate session ID
    session_id = str(uuid.uuid4())

    # Check for focus conflicts BEFORE creating session
    focus_conflict = detect_focus_conflict(focus, active_dir, session_id)

    # Create session directory
    session_dir = active_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Determine transcript path (will be populated by Claude Code)
    # Format matches Claude's project directory structure
    transcript_path = f"~/.claude/projects/{working_dir_path.name}/*.jsonl"

    # Create session metadata
    session_data = {
        "session_id": session_id,
        "role": role,
        "working_dir": str(working_dir_path),
        "focus": focus,
        "model": model,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "transcript_path": transcript_path,
    }

    # Write session.json
    session_file = session_dir / "session.json"
    session_file.write_text(json.dumps(session_data, indent=2))

    logger.info(f"Created session {session_id} for role {role} with focus {focus}")

    # Resolve context paths (OCTAVE files from .hestai/context/)
    context_paths = resolve_context_paths(working_dir_path)

    # Return response
    return {
        "session_id": session_id,
        "context_paths": context_paths,
        "focus_conflict": focus_conflict,
        "structure_status": structure_status,
    }
