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
import re
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Maximum characters to include from each context file
MAX_CONTEXT_FILE_CHARS = 2000
# Maximum total context characters to send to AI
MAX_TOTAL_CONTEXT_CHARS = 4000


# Issue pattern regex: matches #XX, issue-XX, issues-XX
ISSUE_PATTERN = re.compile(r"(?:issues?-|#)(\d+)", re.IGNORECASE)

# Feature prefix patterns: feat/, fix/, chore/, refactor/, docs/
FEATURE_PREFIX_PATTERN = re.compile(r"^(feat|fix|chore|refactor|docs)/(.+)$")


def resolve_focus_from_branch(branch: str) -> dict[str, str] | None:
    """
    Resolve focus from branch name based on patterns.

    Priority within branch patterns:
    1. Issue number pattern: #XX, issue-XX, issues-XX -> "issue-XX"
    2. Feature prefix: feat/, fix/, chore/, etc. -> "prefix: description"

    Args:
        branch: Git branch name

    Returns:
        Dict with "value" and "source" keys, or None if no pattern matches.
        - value: The resolved focus string
        - source: "github_issue" for issue patterns, "branch" for feature prefixes
    """
    if not branch:
        return None

    # First priority: issue number patterns
    issue_match = ISSUE_PATTERN.search(branch)
    if issue_match:
        issue_number = issue_match.group(1)
        return {
            "value": f"issue-{issue_number}",
            "source": "github_issue",
        }

    # Second priority: feature prefix patterns
    prefix_match = FEATURE_PREFIX_PATTERN.match(branch)
    if prefix_match:
        prefix = prefix_match.group(1)
        description = prefix_match.group(2)
        return {
            "value": f"{prefix}: {description}",
            "source": "branch",
        }

    # No recognizable pattern
    return None


def resolve_focus(
    explicit_focus: str | None = None,
    branch: str | None = None,
) -> dict[str, str]:
    """
    Resolve focus with priority chain per North Star Section 5 STEP_4.

    Priority order:
    1. Explicit focus (if provided)
    2. GitHub issue from branch name (if matches issue pattern)
    3. Branch inference (if matches feature prefix pattern)
    4. Default: "general"

    Args:
        explicit_focus: Explicitly provided focus (highest priority)
        branch: Git branch name to infer focus from

    Returns:
        Dict with "value" and "source" keys:
        - value: The resolved focus string
        - source: "explicit", "github_issue", "branch", or "default"
    """
    # Priority 1: Explicit focus
    if explicit_focus is not None and explicit_focus.strip():
        return {
            "value": explicit_focus.strip(),
            "source": "explicit",
        }

    # Priority 2-3: Infer from branch
    if branch:
        branch_result = resolve_focus_from_branch(branch)
        if branch_result:
            return branch_result

    # Priority 4: Default
    return {
        "value": "general",
        "source": "default",
    }


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
        "PROJECT-CONTEXT.oct.md",
        "PROJECT-ROADMAP.oct.md",
        "PROJECT-CHECKLIST.oct.md",
        "PROJECT-HISTORY.oct.md",
        "context-negatives.oct.md",
    ]

    for file_name in standard_files:
        path = hestai_context / file_name
        if path.exists():
            context_paths.append(str(path))

    # Also check for project north star in workflow/
    # Support multiple naming patterns per naming-standard.oct.md
    north_star_path = _find_north_star_file(working_dir)
    if north_star_path:
        context_paths.append(str(north_star_path))

    return context_paths


def _find_north_star_file(working_dir: Path) -> Path | None:
    """
    Find the North Star file in .hestai/workflow/ using flexible naming patterns.

    Per naming-standard.oct.md, North Star files follow pattern:
    000-{PROJECT}-NORTH-STAR(-SUMMARY)?(.oct)?.md

    This supports:
    - 000-PROJECT-NORTH-STAR.oct.md (generic)
    - 000-MCP-PRODUCT-NORTH-STAR.oct.md (project-specific)
    - 000-MCP-PRODUCT-NORTH-STAR.md (without .oct)

    Returns the first matching file, preferring .oct.md over .md.
    """
    workflow_dir = working_dir / ".hestai" / "workflow"
    if not workflow_dir.exists():
        return None

    # Priority order: .oct.md first, then .md
    # Exclude -SUMMARY files (those are compressed versions)
    try:
        candidates = []
        for path in workflow_dir.iterdir():
            name = path.name
            if (
                name.startswith("000-")
                and "NORTH-STAR" in name
                and "-SUMMARY" not in name
                and name.endswith(".md")
            ):
                candidates.append(path)

        if not candidates:
            return None

        # Prefer .oct.md over .md
        for candidate in candidates:
            if candidate.name.endswith(".oct.md"):
                return candidate

        # Fall back to first .md
        return candidates[0]

    except OSError:
        return None


def build_rich_context_summary(
    working_dir: Path,
    context_paths: list[str],
    role: str,
    focus: str,
) -> str:
    """
    Build a rich context summary for AI synthesis by reading actual file contents.

    This is the key to useful AI synthesis - the AI can only work with what we give it.
    We read PROJECT-CONTEXT.oct.md and git state to provide real project information.

    Args:
        working_dir: Project root directory
        context_paths: List of context file paths to read
        role: Agent role for context
        focus: Session focus for context

    Returns:
        Rich context string with actual project information
    """
    sections = []

    # 1. Read PROJECT-CONTEXT.oct.md (most important)
    project_context_path = working_dir / ".hestai" / "context" / "PROJECT-CONTEXT.oct.md"
    if project_context_path.exists():
        try:
            content = project_context_path.read_text()
            # Truncate if too long
            if len(content) > MAX_CONTEXT_FILE_CHARS:
                content = content[:MAX_CONTEXT_FILE_CHARS] + "\n... [truncated]"
            sections.append(f"=== PROJECT-CONTEXT.oct.md ===\n{content}")
        except OSError as e:
            logger.warning(f"Could not read PROJECT-CONTEXT: {e}")

    # 2. Get git state (branch, recent commits, modified files)
    git_state = _get_git_state(working_dir)
    if git_state:
        sections.append(f"=== GIT STATE ===\n{git_state}")

    # 3. Check for blockers in state/ (if exists)
    blockers_path = working_dir / ".hestai" / "context" / "state" / "blockers.oct.md"
    if blockers_path.exists():
        try:
            content = blockers_path.read_text()
            if "ACTIVE:" in content and content.split("ACTIVE:")[1].strip():
                # Only include if there are actual blockers
                active_section = content.split("ACTIVE:")[1].split("===")[0].strip()
                if active_section:
                    sections.append(f"=== ACTIVE BLOCKERS ===\n{active_section}")
        except OSError:
            pass

    # 4. Check I4 freshness and add warning if stale
    freshness_warning = _check_context_freshness(project_context_path, working_dir)
    if freshness_warning:
        sections.insert(0, f"=== I4 FRESHNESS WARNING ===\n{freshness_warning}")

    # 5. Extract North Star constraints for architectural awareness (Issue #87)
    # Use flexible finder to support multiple naming patterns
    north_star_path = _find_north_star_file(working_dir)
    if north_star_path:
        constraints = _extract_north_star_constraints(north_star_path)
        if constraints:
            sections.append(f"=== ARCHITECTURAL CONSTRAINTS ===\n{constraints}")

    # 6. Build summary with role and focus context
    header = f"SESSION CONTEXT for {role}\nFOCUS: {focus}\n"

    # Combine sections, respecting max total size
    combined = header + "\n\n".join(sections)
    if len(combined) > MAX_TOTAL_CONTEXT_CHARS:
        combined = combined[:MAX_TOTAL_CONTEXT_CHARS] + "\n... [context truncated]"

    return combined


def _get_git_state(working_dir: Path) -> str | None:
    """
    Get git state for context (branch, recent commits, modified files).

    Returns None if git is not available or fails.
    """
    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(working_dir),
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        # Get recent commits (last 3)
        log_result = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(working_dir),
        )
        recent_commits = log_result.stdout.strip() if log_result.returncode == 0 else ""

        # Get modified files
        status_result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(working_dir),
        )
        modified = status_result.stdout.strip() if status_result.returncode == 0 else ""

        parts = [f"Branch: {branch}"]
        if recent_commits:
            parts.append(f"Recent commits:\n{recent_commits}")
        if modified:
            parts.append(f"Modified files:\n{modified}")

        return "\n".join(parts)

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.debug(f"Could not get git state: {e}")
        return None


def _check_context_freshness(
    project_context_path: Path,
    working_dir: Path,
    max_age_hours: int = 24,
) -> str | None:
    """
    Check if PROJECT-CONTEXT.oct.md is stale per I4 freshness verification.

    I4::FRESHNESS_VERIFICATION::[
      PRINCIPLE::context_must_be_verified_as_current_before_use,
      WHY::prevents_hallucinations_from_stale_data
    ]

    Stale = last git commit modifying the file > max_age_hours ago,
    or file exists but has never been committed (no git history).

    Args:
        project_context_path: Path to PROJECT-CONTEXT.oct.md
        working_dir: Project root directory (for git commands)
        max_age_hours: Maximum age in hours before considered stale (default: 24)

    Returns:
        Warning message if stale, None if fresh
    """
    if not project_context_path.exists():
        return None  # No file = no freshness check needed

    try:
        # Get the last commit date for this specific file
        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%ct",  # Unix timestamp
                "--",
                str(project_context_path.relative_to(working_dir)),
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(working_dir),
        )

        if result.returncode != 0 or not result.stdout.strip():
            # File exists but has never been committed - considered stale
            return "I4 WARNING: PROJECT-CONTEXT.oct.md has never been committed to git (freshness unknown)"

        # Parse timestamp and check age
        commit_timestamp = int(result.stdout.strip())
        commit_time = datetime.fromtimestamp(commit_timestamp, tz=UTC)
        now = datetime.now(UTC)
        age_hours = (now - commit_time).total_seconds() / 3600

        if age_hours > max_age_hours:
            return f"I4 WARNING: PROJECT-CONTEXT.oct.md is stale ({age_hours:.1f}h since last commit, threshold: {max_age_hours}h)"

        return None  # Fresh

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError, ValueError) as e:
        logger.debug(f"Could not check context freshness: {e}")
        # If we can't check, assume stale (fail-safe for I4)
        return "I4 WARNING: Could not verify PROJECT-CONTEXT.oct.md freshness (git unavailable)"


def _extract_north_star_constraints(north_star_path: Path) -> str | None:
    """
    Extract SCOPE_BOUNDARIES and IMMUTABLES from North Star for architectural awareness.

    Per Issue #87: Agents need architectural context to avoid "system blindness".
    This helps the AI understand what the project IS and IS_NOT.

    Args:
        north_star_path: Path to North Star file

    Returns:
        Extracted constraints string, or None if not available
    """
    if not north_star_path.exists():
        return None

    try:
        content = north_star_path.read_text()

        # Extract relevant sections
        extracted_parts = []

        # Look for SCOPE_BOUNDARIES section
        if "SCOPE_BOUNDARIES" in content:
            # Find the section and extract it
            start_idx = content.find("SCOPE_BOUNDARIES")
            if start_idx != -1:
                # Find the end (next section or file end)
                section_content = content[start_idx:]
                # Take up to next major section or 500 chars
                end_markers = ["IMMUTABLES", "ASSUMPTIONS", "CONSTRAINED_VARIABLES", "===END"]
                end_idx = len(section_content)
                for marker in end_markers:
                    if marker in section_content[20:]:  # Skip past "SCOPE_BOUNDARIES" itself
                        pos = section_content.find(marker, 20)
                        if pos < end_idx:
                            end_idx = pos
                extracted_parts.append(section_content[: min(end_idx, 500)])

        # Look for key IMMUTABLES mentions
        if "IMMUTABLES" in content or "I3::" in content or "I4::" in content:
            # Extract just the immutable references (compact)
            immutable_refs = []
            for line in content.split("\n"):
                if "I1::" in line or "I2::" in line or "I3::" in line or "I4::" in line:
                    immutable_refs.append(line.strip())
                    if len(immutable_refs) >= 4:  # Limit to first 4
                        break
            if immutable_refs:
                extracted_parts.append("KEY IMMUTABLES:\n" + "\n".join(immutable_refs))

        if extracted_parts:
            return "\n\n".join(extracted_parts)

        return None

    except OSError as e:
        logger.debug(f"Could not extract North Star constraints: {e}")
        return None


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
    focus: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """
    Register session start, create session directory, return context paths.

    ADR-0007: Uses direct .hestai/ directory structure (no symlinks/worktrees).

    Args:
        role: Agent role name (e.g., 'implementation-lead')
        working_dir: Project working directory path
        focus: Work focus area (optional - will infer from branch if not provided)
        model: Optional AI model identifier

    Returns:
        dict with:
            - session_id: Generated UUID
            - context_paths: List of OCTAVE context file paths to load
            - focus_conflict: None or conflicting session info
            - structure_status: 'present' | 'created'
            - focus_resolved: Dict with 'value' and 'source' keys

    Raises:
        ValueError: If validation fails (path traversal, invalid role)
        FileNotFoundError: If working_dir doesn't exist
    """
    # Validate inputs
    role = validate_role_format(role)
    working_dir_path = validate_working_dir(working_dir)

    # Ensure .hestai/ directory structure exists
    structure_status = ensure_hestai_structure(working_dir_path)

    # Get current branch for focus resolution
    from hestai_mcp.mcp.tools.shared.fast_layer import get_current_branch

    branch = get_current_branch(working_dir=working_dir_path)

    # Resolve focus with priority chain: explicit > github_issue > branch > default
    focus_resolved = resolve_focus(explicit_focus=focus, branch=branch)
    resolved_focus_value = focus_resolved["value"]

    # Get active sessions directory
    active_dir = working_dir_path / ".hestai" / "sessions" / "active"

    # Generate session ID
    session_id = str(uuid.uuid4())

    # Check for focus conflicts BEFORE creating session
    focus_conflict = detect_focus_conflict(resolved_focus_value, active_dir, session_id)

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
        "focus": resolved_focus_value,
        "focus_source": focus_resolved["source"],
        "model": model,
        "started_at": datetime.now(UTC).isoformat(),
        "transcript_path": transcript_path,
    }

    # Write session.json
    session_file = session_dir / "session.json"
    session_file.write_text(json.dumps(session_data, indent=2))

    logger.info(
        f"Created session {session_id} for role {role} with focus {resolved_focus_value} "
        f"(source: {focus_resolved['source']})"
    )

    # Update FAST layer (ADR-0046, ADR-0056)
    from hestai_mcp.mcp.tools.shared.fast_layer import update_fast_layer_on_clock_in

    update_fast_layer_on_clock_in(working_dir_path, session_id, role, resolved_focus_value)

    # Resolve context paths (OCTAVE files from .hestai/context/)
    context_paths = resolve_context_paths(working_dir_path)

    # Return response
    return {
        "session_id": session_id,
        "context_paths": context_paths,
        "focus_conflict": focus_conflict,
        "structure_status": structure_status,
        "focus_resolved": focus_resolved,
    }


async def clock_in_async(
    role: str,
    working_dir: str,
    focus: str | None = None,
    model: str | None = None,
    enable_ai_synthesis: bool = True,
) -> dict[str, Any]:
    """
    Async version of clock_in with optional AI synthesis.

    This version can call AI synthesis for FAST layer content.
    SS-I2 compliant: Fully async for MCP tool integration.
    SS-I6 compliant: Graceful fallback if AI fails.

    Args:
        role: Agent role name (e.g., 'implementation-lead')
        working_dir: Project working directory path
        focus: Work focus area (optional - will infer from branch if not provided)
        model: Optional AI model identifier
        enable_ai_synthesis: Whether to attempt AI synthesis (default True)

    Returns:
        dict with:
            - session_id: Generated UUID
            - context_paths: List of OCTAVE context file paths to load
            - focus_conflict: None or conflicting session info
            - structure_status: 'present' | 'created'
            - focus_resolved: Dict with 'value' and 'source' keys
            - ai_synthesis: Dict with 'synthesis' and 'source' keys (if enabled)

    Raises:
        ValueError: If validation fails (path traversal, invalid role)
        FileNotFoundError: If working_dir doesn't exist
    """
    # Validate inputs
    role = validate_role_format(role)
    working_dir_path = validate_working_dir(working_dir)

    # Ensure .hestai/ directory structure exists
    structure_status = ensure_hestai_structure(working_dir_path)

    # Get current branch for focus resolution
    from hestai_mcp.mcp.tools.shared.fast_layer import get_current_branch

    branch = get_current_branch(working_dir=working_dir_path)

    # Resolve focus with priority chain: explicit > github_issue > branch > default
    focus_resolved = resolve_focus(explicit_focus=focus, branch=branch)
    resolved_focus_value = focus_resolved["value"]

    # Get active sessions directory
    active_dir = working_dir_path / ".hestai" / "sessions" / "active"

    # Generate session ID
    session_id = str(uuid.uuid4())

    # Check for focus conflicts BEFORE creating session
    focus_conflict = detect_focus_conflict(resolved_focus_value, active_dir, session_id)

    # Create session directory
    session_dir = active_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Determine transcript path (will be populated by Claude Code)
    transcript_path = f"~/.claude/projects/{working_dir_path.name}/*.jsonl"

    # Create session metadata
    session_data = {
        "session_id": session_id,
        "role": role,
        "working_dir": str(working_dir_path),
        "focus": resolved_focus_value,
        "focus_source": focus_resolved["source"],
        "model": model,
        "started_at": datetime.now(UTC).isoformat(),
        "transcript_path": transcript_path,
    }

    # Write session.json
    session_file = session_dir / "session.json"
    session_file.write_text(json.dumps(session_data, indent=2))

    logger.info(
        f"Created session {session_id} for role {role} with focus {resolved_focus_value} "
        f"(source: {focus_resolved['source']})"
    )

    # Update FAST layer (sync version for now)
    from hestai_mcp.mcp.tools.shared.fast_layer import (
        synthesize_fast_layer_with_ai,
        update_fast_layer_on_clock_in,
    )

    update_fast_layer_on_clock_in(working_dir_path, session_id, role, resolved_focus_value)

    # Attempt AI synthesis if enabled
    ai_synthesis_result = None
    if enable_ai_synthesis:
        try:
            # Build RICH context summary with actual file contents and git state
            # This is key to useful AI synthesis - the AI can only work with what we give it
            context_paths = resolve_context_paths(working_dir_path)
            context_summary = build_rich_context_summary(
                working_dir=working_dir_path,
                context_paths=context_paths,
                role=role,
                focus=resolved_focus_value,
            )

            ai_synthesis_result = await synthesize_fast_layer_with_ai(
                session_id=session_id,
                role=role,
                focus=resolved_focus_value,
                context_summary=context_summary,
            )
            logger.info(f"AI synthesis completed for session {session_id}")
        except Exception as e:
            # SS-I6 Fallback: Use OCTAVE format matching AI output contract
            # Per CRS issue #140: Fallback must emit same structured format as AI synthesis
            logger.warning(f"AI synthesis failed for session {session_id}: {e}")

            # OCTAVE format matching CLOCK_IN_SYNTHESIS_PROTOCOL in protocols.py
            fallback_synthesis = f"""CONTEXT_FILES::[@.hestai/context/PROJECT-CONTEXT.oct.md, @.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md]
FOCUS::{resolved_focus_value}
PHASE::UNKNOWN
BLOCKERS::[]
TASKS::[Review context for {role}, Complete {resolved_focus_value} objectives]
FRESHNESS_WARNING::AI_SYNTHESIS_UNAVAILABLE"""

            ai_synthesis_result = {
                "synthesis": fallback_synthesis,
                "source": "fallback",
            }

    # Resolve context paths (OCTAVE files from .hestai/context/)
    context_paths = resolve_context_paths(working_dir_path)

    # Build response
    response: dict[str, Any] = {
        "session_id": session_id,
        "context_paths": context_paths,
        "focus_conflict": focus_conflict,
        "structure_status": structure_status,
        "focus_resolved": focus_resolved,
    }

    if ai_synthesis_result:
        response["ai_synthesis"] = ai_synthesis_result

    return response
