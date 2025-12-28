"""
FAST Layer Operations - Per ADR-0046 and ADR-0056.

The FAST layer at .hestai/context/state/ contains session-specific state
that changes hourly to daily. These files should be dynamically populated
during clock_in and updated during clock_out.

Files managed:
- current-focus.oct.md: Active session focus
- checklist.oct.md: Session tasks with carry-forward
- blockers.oct.md: Active blockers (preserved across sessions)

Per ADR-0056: Velocity-Layered Fragments Architecture
"""

import logging
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def sanitize_octave_scalar(value: str) -> str:
    """
    Sanitize a scalar value for safe interpolation into OCTAVE content.

    Prevents OCTAVE injection attacks by:
    1. Rejecting control characters (newline, carriage return, tab)
    2. Escaping double quotes

    Args:
        value: The scalar value to sanitize (role, focus, branch, etc.)

    Returns:
        Sanitized value safe for OCTAVE interpolation.

    Raises:
        ValueError: If value contains control characters that cannot be safely escaped.
    """
    # Check for control characters that could break OCTAVE structure
    control_chars = {"\n": "newline", "\r": "carriage return", "\t": "tab"}
    for char, name in control_chars.items():
        if char in value:
            raise ValueError(
                f"Invalid value: contains {name} control character. "
                f"Control characters are not allowed in OCTAVE scalar values."
            )

    # Escape double quotes to prevent breaking quoted fields
    sanitized = value.replace('"', '\\"')

    return sanitized


def get_current_branch(working_dir: Path | None = None) -> str:
    """
    Get the current git branch name for the specified working directory.

    Args:
        working_dir: The directory to get the branch for. If None, uses process cwd.
                    IMPORTANT: For multi-worktree scenarios, always pass working_dir
                    to get the correct branch for the target repository.

    Returns:
        Branch name or 'unknown' if git command fails.
    """
    try:
        # Pass cwd to subprocess to ensure we get the branch for the target
        # directory, not the process working directory (critical for worktrees)
        cwd = str(working_dir) if working_dir else None
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return "unknown"


def ensure_state_directory(working_dir: Path) -> Path:
    """
    Ensure .hestai/context/state/ directory exists.

    Args:
        working_dir: Project root directory

    Returns:
        Path to state directory
    """
    state_dir = working_dir / ".hestai" / "context" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def populate_current_focus(
    state_dir: Path,
    session_id: str,
    role: str,
    focus: str,
) -> None:
    """
    Populate current-focus.oct.md with session info.

    ADR-0056 format:
    ===CURRENT_FOCUS===
    META:
      TYPE::SESSION_FOCUS
      VELOCITY::HOURLY_DAILY
    SESSION:
      ID::"{session_id}"
      ROLE::{role}
      FOCUS::"{focus}"
      BRANCH::{branch}
      STARTED::"{timestamp}"
    ===END===

    Raises:
        ValueError: If role or focus contain control characters (injection prevention).
    """
    # Sanitize inputs to prevent OCTAVE injection attacks
    safe_role = sanitize_octave_scalar(role)
    safe_focus = sanitize_octave_scalar(focus)

    # Derive working_dir from state_dir (.hestai/context/state -> project root)
    # state_dir is: working_dir / ".hestai" / "context" / "state"
    working_dir = state_dir.parent.parent.parent
    branch = get_current_branch(working_dir=working_dir)

    # Sanitize branch as well (could contain special chars from git)
    safe_branch = sanitize_octave_scalar(branch)

    timestamp = datetime.now(timezone.utc).isoformat()

    content = f"""===CURRENT_FOCUS===
META:
  TYPE::SESSION_FOCUS
  VELOCITY::HOURLY_DAILY

SESSION:
  ID::"{session_id}"
  ROLE::{safe_role}
  FOCUS::"{safe_focus}"
  BRANCH::{safe_branch}
  STARTED::"{timestamp}"

===END===
"""
    current_focus_path = state_dir / "current-focus.oct.md"
    current_focus_path.write_text(content)
    logger.info(f"Populated current-focus.oct.md for session {session_id}")


def populate_checklist(
    state_dir: Path,
    session_id: str,
    focus: str,
) -> None:
    """
    Populate checklist.oct.md with session task, carrying forward incomplete items.

    ADR-0056: Incomplete tasks from previous sessions should be preserved.
    """
    checklist_path = state_dir / "checklist.oct.md"

    # Check for existing checklist with incomplete items
    carried_forward = _extract_incomplete_items(checklist_path)

    # Build carried forward section if there are items
    carried_forward_section = ""
    if carried_forward:
        carried_forward_section = "\nCARRIED_FORWARD:\n"
        for item, status in carried_forward:
            carried_forward_section += f"  {item}::{status}[from_previous_session]\n"

    content = f"""===SESSION_CHECKLIST===
META:
  TYPE::FAST_CHECKLIST
  VELOCITY::HOURLY_DAILY
  SESSION::"{session_id}"

CURRENT_TASK::"{focus}"

ITEMS:
  session_task::IN_PROGRESS
{carried_forward_section}
===END===
"""
    checklist_path.write_text(content)
    logger.info(f"Populated checklist.oct.md for session {session_id}")


def _extract_incomplete_items(checklist_path: Path) -> list[tuple[str, str]]:
    """
    Extract incomplete items (PENDING, IN_PROGRESS) from existing checklist.

    Returns:
        List of (item_name, status) tuples
    """
    if not checklist_path.exists():
        return []

    content = checklist_path.read_text()
    incomplete = []

    # Match patterns like "  task_name::PENDING" or "  task_name::IN_PROGRESS"
    pattern = r"^\s+(\w+)::(PENDING|IN_PROGRESS)"
    for match in re.finditer(pattern, content, re.MULTILINE):
        item_name = match.group(1)
        status = match.group(2)
        # Don't carry forward the generic session_task
        if item_name != "session_task":
            incomplete.append((item_name, status))

    return incomplete


def populate_blockers(
    state_dir: Path,
    session_id: str,
) -> None:
    """
    Populate or update blockers.oct.md, preserving existing unresolved blockers.

    ADR-0056: Unresolved blockers should survive session transitions.
    """
    blockers_path = state_dir / "blockers.oct.md"

    if blockers_path.exists():
        # Preserve existing content, just update session reference
        content = blockers_path.read_text()
        # Update the SESSION field if present
        if 'SESSION::"' in content:
            content = re.sub(
                r'SESSION::"[^"]*"',
                f'SESSION::"{session_id}"',
                content,
            )
            blockers_path.write_text(content)
        logger.info(f"Preserved existing blockers, updated session to {session_id}")
    else:
        # Create new blockers file
        content = f"""===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS
  VELOCITY::HOURLY_DAILY
  SESSION::"{session_id}"

ACTIVE:

===END===
"""
        blockers_path.write_text(content)
        logger.info(f"Created blockers.oct.md for session {session_id}")


def clear_current_focus(
    state_dir: Path,
    session_id: str,
) -> None:
    """
    Clear current focus on session end, record last session info.

    ADR-0056 format after clock_out:
    SESSION::NONE
    LAST_SESSION:
      ID::"{session_id}"
      COMPLETED::"{timestamp}"
    """
    current_focus_path = state_dir / "current-focus.oct.md"
    if not current_focus_path.exists():
        return

    timestamp = datetime.now(timezone.utc).isoformat()

    content = f"""===CURRENT_FOCUS===
META:
  TYPE::SESSION_FOCUS
  VELOCITY::HOURLY_DAILY

SESSION::NONE

LAST_SESSION:
  ID::"{session_id}"
  COMPLETED::"{timestamp}"

===END===
"""
    current_focus_path.write_text(content)
    logger.info(f"Cleared current focus for session {session_id}")


def update_checklist_on_close(
    state_dir: Path,
    session_id: str,
) -> None:
    """
    Update checklist on session close, preserving incomplete items.

    ADR-0056: Incomplete tasks should be preserved for next session.
    """
    checklist_path = state_dir / "checklist.oct.md"
    if not checklist_path.exists():
        return

    # Read and preserve the content (incomplete items will be carried forward
    # on next clock_in)
    content = checklist_path.read_text()

    # Mark session as completed
    if 'SESSION::"' in content:
        content = re.sub(
            r'SESSION::"[^"]*"',
            f'SESSION::"{session_id}[COMPLETED]"',
            content,
        )
        checklist_path.write_text(content)

    logger.info(f"Updated checklist for session {session_id} completion")


def persist_blockers_on_close(
    state_dir: Path,
    session_id: str,
) -> None:
    """
    Persist unresolved blockers, clear resolved ones on session close.

    ADR-0056: Resolved blockers should be cleared, unresolved should persist.

    This function uses indent-based block detection to properly handle blockers
    with extra fields (OWNER::, LINKS::, PRIORITY::, etc.) beyond the basic
    DESCRIPTION::, SINCE::, STATUS:: fields.
    """
    blockers_path = state_dir / "blockers.oct.md"
    if not blockers_path.exists():
        return

    content = blockers_path.read_text()
    lines = content.split("\n")
    filtered_lines: list[str] = []
    current_blocker_lines: list[str] = []
    blocker_indent: int | None = None

    def _get_indent(line: str) -> int:
        """Get the indentation level of a line."""
        return len(line) - len(line.lstrip())

    def _finalize_blocker(blocker_lines: list[str], output: list[str]) -> None:
        """Check if blocker should be kept and add to output if unresolved."""
        if not blocker_lines:
            return
        blocker_text = "\n".join(blocker_lines)
        if "STATUS::RESOLVED" not in blocker_text:
            output.extend(blocker_lines)

    for line in lines:
        # Detect start of a blocker entry (e.g., "  blocker_001:")
        blocker_match = re.match(r"^(\s+)(blocker_\d+):", line)

        if blocker_match:
            # Finalize any previous blocker before starting a new one
            _finalize_blocker(current_blocker_lines, filtered_lines)

            # Start accumulating new blocker
            current_blocker_lines = [line]
            blocker_indent = _get_indent(line)

        elif current_blocker_lines and blocker_indent is not None:
            # We're inside a blocker block
            current_line_indent = _get_indent(line)

            # Check if this line is still part of the blocker block:
            # - Indented more than the blocker header (child content)
            # - Empty line (could be formatting within block)
            # - Or a line at exactly blocker_indent + some indentation for fields
            if line.strip() == "":
                # Empty line - could be end of block or just spacing
                # Look ahead would be complex, so we include it in current blocker
                # and let the next non-empty line determine if we're still in block
                current_blocker_lines.append(line)
            elif current_line_indent > blocker_indent:
                # More indented than blocker header = still in blocker
                current_blocker_lines.append(line)
            else:
                # Same or less indent = blocker block ended
                _finalize_blocker(current_blocker_lines, filtered_lines)
                current_blocker_lines = []
                blocker_indent = None
                filtered_lines.append(line)
        else:
            # Not in a blocker block
            filtered_lines.append(line)

    # Handle last blocker if any
    _finalize_blocker(current_blocker_lines, filtered_lines)

    new_content = "\n".join(filtered_lines)
    blockers_path.write_text(new_content)
    logger.info(f"Persisted unresolved blockers, cleared resolved for session {session_id}")


def update_fast_layer_on_clock_in(
    working_dir: Path,
    session_id: str,
    role: str,
    focus: str,
) -> None:
    """
    Update all FAST layer files during clock_in.

    Consolidated function called by clock_in tool.
    """
    state_dir = ensure_state_directory(working_dir)
    populate_current_focus(state_dir, session_id, role, focus)
    populate_checklist(state_dir, session_id, focus)
    populate_blockers(state_dir, session_id)


def update_fast_layer_on_clock_out(
    working_dir: Path,
    session_id: str,
) -> None:
    """
    Update all FAST layer files during clock_out.

    Consolidated function called by clock_out tool.
    """
    state_dir = working_dir / ".hestai" / "context" / "state"
    if not state_dir.exists():
        logger.info("State directory does not exist, skipping FAST layer update")
        return

    clear_current_focus(state_dir, session_id)
    update_checklist_on_close(state_dir, session_id)
    persist_blockers_on_close(state_dir, session_id)
