"""
FAST Layer Operations - Per ADR-0046 and ADR-0056.

The FAST layer at .hestai/state/context/state/ contains session-specific state
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
from datetime import UTC, datetime
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
    Ensure .hestai/state/context/state/ directory exists.

    Args:
        working_dir: Project root directory

    Returns:
        Path to state directory
    """
    state_dir = working_dir / ".hestai" / "state" / "context" / "state"
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

    # Derive working_dir from state_dir (.hestai/state/context/state -> project root)
    # state_dir is: working_dir / ".hestai" / "state" / "context" / "state"
    working_dir = state_dir.parent.parent.parent.parent
    branch = get_current_branch(working_dir=working_dir)

    # Sanitize branch as well (could contain special chars from git)
    safe_branch = sanitize_octave_scalar(branch)

    timestamp = datetime.now(UTC).isoformat()

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

    timestamp = datetime.now(UTC).isoformat()

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
    state_dir = working_dir / ".hestai" / "state" / "context" / "state"
    if not state_dir.exists():
        logger.info("State directory does not exist, skipping FAST layer update")
        return

    clear_current_focus(state_dir, session_id)
    update_checklist_on_close(state_dir, session_id)
    persist_blockers_on_close(state_dir, session_id)


# AI Synthesis - Using Layered Constitutional Injection pattern
# Architecture: debate 2026-01-02-context-steward-prompt-architecture
# - Identity Kernel (~30 lines): WHO the agent IS - always loaded
# - Operation Protocol (~50 lines): WHAT this call does - per-tool
# Key insight: IDENTITY ≠ OPERATION. Layer them, don't blend them.

# Import the layered prompt components
try:
    from hestai_mcp.modules.services.ai.prompts import (
        CLOCK_IN_SYNTHESIS_PROTOCOL,
        compose_prompt,
    )

    SYNTHESIS_SYSTEM_PROMPT = compose_prompt(CLOCK_IN_SYNTHESIS_PROTOCOL)
except ImportError:
    # Fallback for when prompts module not available (e.g., during testing)
    # Uses structured OCTAVE format per issue #140
    SYNTHESIS_SYSTEM_PROMPT = """You are Context Steward, the internal AI agent for HestAI-MCP.

OPERATION: Session Context Synthesis (clock_in)

Generate structured, actionable context for Claude Code agent session.

OUTPUT FORMAT (use exactly this OCTAVE structure):
CONTEXT_FILES::[@.hestai/state/context/PROJECT-CONTEXT.oct.md:L1-50]
FOCUS::{focus_value_from_input}
PHASE::{phase_from_context_or_UNKNOWN}
BLOCKERS::[]
TASKS::[{task_from_context}]
FRESHNESS_WARNING::NONE

CRITICAL: Only include information from provided context. Do NOT invent details.
Use OCTAVE :: syntax for all fields.
"""

SYNTHESIS_USER_PROMPT_TEMPLATE = """Role: {role}
Focus: {focus}

PROJECT CONTEXT:
{context_summary}

Synthesize this into actionable session context. Only reference information explicitly provided above."""

# Required OCTAVE fields per protocols.py CLOCK_IN_SYNTHESIS_PROTOCOL
REQUIRED_OCTAVE_FIELDS = [
    "CONTEXT_FILES::",
    "FOCUS::",
    "PHASE::",
    "BLOCKERS::",
    "TASKS::",
    "FRESHNESS_WARNING::",
]


def _validate_octave_synthesis(response: str) -> bool:
    """
    Validate AI response contains all required OCTAVE fields.

    Anti-fragility check: ensures AI output meets structural contract.
    If ANY field is missing, returns False to trigger fallback.

    Args:
        response: AI-generated synthesis text

    Returns:
        True if all required fields present, False otherwise
    """
    return all(field in response for field in REQUIRED_OCTAVE_FIELDS)


async def synthesize_fast_layer_with_ai(
    session_id: str,
    role: str,
    focus: str,
    context_summary: str,
) -> dict[str, str]:
    """
    Synthesize FAST layer content using AI (SS-I2 async, SS-I6 fallback).

    Per North Star Section 5 STEP_5+6:
    1. Creates a CompletionRequest with synthesis prompt
    2. Calls AIClient.complete_text()
    3. Parses AI response into synthesis result
    4. Falls back to template if AI fails (SS-I6)

    Args:
        session_id: Current session ID
        role: Agent role (e.g., "implementation-lead")
        focus: Resolved focus (e.g., "issue-56")
        context_summary: Summary of available context

    Returns:
        Dict with "synthesis" and "source" keys:
        - synthesis: The synthesized content string
        - source: "ai" if AI succeeded, "fallback" if using template
    """
    try:
        # Import here to avoid circular dependencies and make fallback possible
        from hestai_mcp.modules.services.ai.client import AIClient
        from hestai_mcp.modules.services.ai.config import load_config
        from hestai_mcp.modules.services.ai.providers.base import CompletionRequest

        # Load AI config
        config = load_config()

        # Get tier for this operation (configurable via YAML)
        tier = config.get_operation_tier("clock_in_synthesis")

        # Build the user prompt
        user_prompt = SYNTHESIS_USER_PROMPT_TEMPLATE.format(
            role=role,
            focus=focus,
            context_summary=context_summary,
        )

        # Create completion request
        request = CompletionRequest(
            system_prompt=SYNTHESIS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=1024,
            temperature=0.3,  # Lower temperature for more consistent output
            timeout_seconds=15,  # Quick timeout to not block session start
        )

        # Call AI using async context manager with explicit tier
        async with AIClient(config) as client:
            ai_response = await client.complete_text(request, tier=tier)

        logger.info(f"AI synthesis completed for session {session_id}")

        # Anti-fragility: Validate AI response has all required OCTAVE fields
        # If any field missing, swap to validated fallback
        if _validate_octave_synthesis(ai_response):
            return {
                "synthesis": ai_response,
                "source": "ai",
            }
        else:
            logger.warning(f"AI generated invalid OCTAVE for session {session_id}, using fallback")
            # Fall through to fallback synthesis below

    except Exception as e:
        # SS-I6 Fallback: Use OCTAVE format matching AI output contract
        # Per CRS issue #140: Fallback must emit same structured format as AI synthesis
        logger.warning(f"AI synthesis failed for session {session_id}, using fallback: {e}")

    # OCTAVE format matching CLOCK_IN_SYNTHESIS_PROTOCOL in protocols.py
    # Used for both AI failure AND invalid AI output (anti-fragility)
    fallback_synthesis = f"""CONTEXT_FILES::[@.hestai/state/context/PROJECT-CONTEXT.oct.md, @.hestai/north-star/000-MCP-PRODUCT-NORTH-STAR.md]
FOCUS::{focus}
PHASE::UNKNOWN
BLOCKERS::[]
TASKS::[Review context for {role}, Complete {focus} objectives]
FRESHNESS_WARNING::AI_SYNTHESIS_UNAVAILABLE"""

    return {
        "synthesis": fallback_synthesis,
        "source": "fallback",
    }
