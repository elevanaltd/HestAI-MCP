"""
Submit RCCAFP record MCP tool.

Records structured error recovery data (Root Cause, Corrective Action,
Future Proofing) to `.hestai/state/error-metrics.jsonl`.

Specified by RCCAFP-ERROR-RECOVERY-SPEC.md sections 2.2 and 3B.

The tool records and returns. It does NOT dispatch -- dispatch is the
Workbench's responsibility.

Safety:
- Path validation: canonicalizes working_dir, rejects traversal.
- Append safety: O_APPEND mode for atomic writes under PIPE_BUF (4096 bytes).
- Directory creation: ensures .hestai/state/ exists.
"""

import json
import logging
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _validate_working_dir(working_dir: str) -> tuple[Path | None, str | None]:
    """Canonicalize and validate working_dir.

    Resolves symlinks, normalizes '..' segments, and validates that the
    resolved path is an existing directory without traversal attempts.

    Args:
        working_dir: Raw working directory path string.

    Returns:
        Tuple of (resolved_path, error_message). If error_message is not None,
        resolved_path is None and the error should be returned to the caller.
    """
    if not working_dir or not working_dir.strip():
        return None, "working_dir must not be empty"

    # Reject path traversal patterns in the raw input
    if ".." in working_dir:
        return None, "Path traversal detected in working_dir: '..' segments are not allowed"

    try:
        path = Path(working_dir).expanduser().resolve()
    except (OSError, ValueError) as e:
        return None, f"Invalid working_dir path: {e}"

    if not path.exists():
        return None, f"working_dir does not exist: {path}"

    if not path.is_dir():
        return None, f"working_dir is not a directory: {path}"

    return path, None


def _validate_inputs(
    context_summary: str,
    root_cause_analysis: str,
    fix_attempt_1: str,
    future_proofing_rule: str,
) -> str | None:
    """Validate required string fields are non-empty.

    Args:
        context_summary: Implementation intent before the failure.
        root_cause_analysis: What actually broke.
        fix_attempt_1: First hypothesis -- what was tried, why it failed.
        future_proofing_rule: Prevention rule or specialist constraints.

    Returns:
        Error message string if validation fails, None if all valid.
    """
    required_fields = {
        "context_summary": context_summary,
        "root_cause_analysis": root_cause_analysis,
        "fix_attempt_1": fix_attempt_1,
        "future_proofing_rule": future_proofing_rule,
    }

    for field_name, value in required_fields.items():
        if not value or not value.strip():
            return f"Required field '{field_name}' must not be empty"

    return None


def _detect_active_session(
    project_root: Path,
) -> tuple[str | None, str | None]:
    """Detect the most recent active session and return (session_id, agent_role).

    Looks in .hestai/state/sessions/active/ for session directories
    containing session.json with session_id and role fields.

    Args:
        project_root: Resolved project root path.

    Returns:
        Tuple of (session_id, agent_role). Both None if no active session found.
    """
    active_dir = project_root / ".hestai" / "state" / "sessions" / "active"
    if not active_dir.exists():
        return None, None

    # Find session directories and pick the most recent one
    session_dirs = [d for d in active_dir.iterdir() if d.is_dir()]
    if not session_dirs:
        return None, None

    # Sort by modification time, most recent first
    session_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)

    for session_dir in session_dirs:
        session_file = session_dir / "session.json"
        if not session_file.exists():
            continue
        try:
            data = json.loads(session_file.read_text())
            session_id = data.get("session_id")
            role = data.get("role")
            if session_id:
                return session_id, role
        except (json.JSONDecodeError, OSError):
            continue

    return None, None


async def submit_rccafp_record(
    working_dir: str,
    context_summary: str,
    root_cause_analysis: str,
    fix_attempt_1: str,
    escalation_required: bool,
    future_proofing_rule: str,
    fix_attempt_2: str | None = None,
) -> dict[str, Any]:
    """Submit an RCCAFP error recovery record.

    Records structured error recovery data to
    ``{working_dir}/.hestai/state/error-metrics.jsonl`` with a
    server-generated envelope (record_id, timestamp, session_id, agent_role).

    The tool records and returns. It does NOT dispatch -- dispatch is
    the Workbench's responsibility.

    Args:
        working_dir: Project root path. Canonicalized and validated.
        context_summary: Implementation intent before the failure.
        root_cause_analysis: What actually broke.
        fix_attempt_1: First hypothesis -- what was tried, why it failed.
        escalation_required: Binary structural gate.
        future_proofing_rule: Prevention rule or specialist constraints.
        fix_attempt_2: Optional second hypothesis.

    Returns:
        Dict with success status and record_id for dispatch reference.
    """
    # Step 1: Validate working_dir
    project_root, path_error = _validate_working_dir(working_dir)
    if path_error:
        return {"success": False, "error": path_error}

    assert project_root is not None  # guaranteed by path_error check

    # Step 2: Validate required string fields
    field_error = _validate_inputs(
        context_summary=context_summary,
        root_cause_analysis=root_cause_analysis,
        fix_attempt_1=fix_attempt_1,
        future_proofing_rule=future_proofing_rule,
    )
    if field_error:
        return {"success": False, "error": field_error}

    # Step 3: Detect active session (best-effort, never fails the tool)
    session_id, agent_role = _detect_active_session(project_root)

    # Step 4: Build record with server-generated envelope
    record_id = f"rccafp-{uuid.uuid4()}"
    record: dict[str, Any] = {
        "record_id": record_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "session_id": session_id,
        "agent_role": agent_role,
        "working_dir": str(project_root),
        "context_summary": context_summary,
        "root_cause_analysis": root_cause_analysis,
        "fix_attempt_1": fix_attempt_1,
        "fix_attempt_2": fix_attempt_2,
        "escalation_required": escalation_required,
        "future_proofing_rule": future_proofing_rule,
    }

    # Step 5: Ensure .hestai/state/ directory exists
    state_dir = project_root / ".hestai" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Step 6: Append to error-metrics.jsonl with O_APPEND for atomic writes
    metrics_path = state_dir / "error-metrics.jsonl"
    json_line = json.dumps(record, separators=(",", ":")) + "\n"

    # O_APPEND: writes under PIPE_BUF (4096 bytes) are atomic on POSIX
    fd = os.open(str(metrics_path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, json_line.encode("utf-8"))
    finally:
        os.close(fd)

    logger.info("RCCAFP record %s written to %s", record_id, metrics_path)

    return {"success": True, "record_id": record_id}
