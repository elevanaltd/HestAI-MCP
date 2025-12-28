"""
ClockOut Tool - Extract and archive session transcript.

This tool enables agents to "clock out" when ending a work session,
extracting the Claude session JSONL transcript and archiving it.

Part of the Context Steward session lifecycle management system.

SS-I2 Compliance: All I/O operations are async. No blocking calls
in the MCP server event loop.

Key Integration Points:
- Uses ClaudeJsonlLens for schema-on-read JSONL parsing
- Replaces hardcoded _parse_session_transcript from hestai-mcp-server
- Security: Path traversal prevention, secret redaction
- Preserves raw JSONL for complete session history
- OCTAVE compression for knowledge extraction
- Learnings index for searchable session wisdom
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from hestai_mcp.events.jsonl_lens import (
    AssistantMessage,
    ClaudeJsonlLens,
    UserMessage,
)

logger = logging.getLogger(__name__)


def validate_session_id(session_id: str) -> str:
    """
    Validate session_id to prevent path traversal attacks.

    Args:
        session_id: Session ID to validate

    Returns:
        Validated session ID (stripped)

    Raises:
        ValueError: If session_id is empty or contains path separators
    """
    if not session_id or not session_id.strip():
        raise ValueError("Session ID cannot be empty")

    # Path traversal prevention
    if ".." in session_id or "/" in session_id or "\\" in session_id:
        raise ValueError("Invalid session_id format - path separators not allowed")

    return session_id.strip()


def redact_sensitive_params(params: dict[str, Any]) -> dict[str, Any]:
    """
    Redact sensitive parameters from tool invocations.

    Security: Prevents exposure of API keys, passwords, tokens in session archives.

    Args:
        params: Raw tool parameters

    Returns:
        Sanitized parameters with sensitive values redacted
    """
    if not isinstance(params, dict):
        return {}

    # Patterns for sensitive keys
    sensitive_patterns = [
        "key",
        "password",
        "token",
        "secret",
        "auth",
        "bearer",
        "credential",
        "api_key",
        "access_token",
    ]

    redacted: dict[str, Any] = {}
    for key, value in params.items():
        key_lower = key.lower()

        # Check if key contains sensitive pattern
        if any(pattern in key_lower for pattern in sensitive_patterns):
            redacted[key] = "***REDACTED***"
        # Recursively redact nested dictionaries
        elif isinstance(value, dict):
            redacted[key] = redact_sensitive_params(value)
        # Check if value looks like a secret (long alphanumeric string)
        elif isinstance(value, str) and len(value) > 20 and any(c.isalnum() for c in value):
            # Could be a secret - redact if it has key-like patterns
            if any(pattern in value.lower() for pattern in ["sk-", "bearer ", "token "]):
                redacted[key] = "***REDACTED***"
            else:
                # Truncate long values to prevent bloat
                redacted[key] = value[:100] + "..." if len(value) > 100 else value
        else:
            # Safe to include
            redacted[key] = value

    return redacted


async def clock_out(
    session_id: str,
    description: str,
    project_root: Path,
) -> dict[str, Any]:
    """
    Extract and archive session transcript with OCTAVE compression.

    SS-I2 Compliance: Async function for non-blocking I/O operations.

    Finds Claude session JSONL, parses messages using ClaudeJsonlLens,
    creates readable archive, applies OCTAVE compression, and updates
    learnings index.

    Args:
        session_id: Session ID from clock_in
        description: Optional session summary (used in compression)
        project_root: Project root directory

    Returns:
        dict with:
            - status: "success" or "error"
            - archive_path: Path to primary archive file
            - redacted_jsonl_path: Path to redacted JSONL archive
            - octave_path: Path to OCTAVE compression (if successful)
            - message_count: Number of messages parsed
            - session_id: Session ID
            - compression_status: "success" | "failed" | "skipped"

    Raises:
        FileNotFoundError: If session or transcript not found
        ValueError: If session_id is invalid
    """
    # Validate session_id
    session_id = validate_session_id(session_id)

    # Verify .hestai directory structure
    hestai_dir = project_root / ".hestai"
    sessions_dir = hestai_dir / "sessions"
    active_dir = sessions_dir / "active"
    archive_dir = sessions_dir / "archive"

    if not active_dir.exists():
        raise FileNotFoundError(f"Active sessions directory not found: {active_dir}")

    # Verify session exists
    session_dir = active_dir / session_id
    if not session_dir.exists():
        raise FileNotFoundError(f"Session {session_id} not found in active sessions")

    # Load session metadata
    session_file = session_dir / "session.json"
    if not session_file.exists():
        raise FileNotFoundError(f"Session metadata not found: {session_file}")

    session_data = json.loads(session_file.read_text())

    # Get transcript path using TranscriptPathResolver (enforces path containment)
    from hestai_mcp.mcp.tools.shared.path_resolution import TranscriptPathResolver

    resolver = TranscriptPathResolver()
    jsonl_path = resolver.resolve(session_data, project_root)

    # Parse session transcript using ClaudeJsonlLens
    lens = ClaudeJsonlLens()
    events = list(lens.parse_file(jsonl_path))

    # Count messages (UserMessage and AssistantMessage only for backward compatibility)
    # Note: ToolUse and ToolResult are events but not counted in original implementation
    message_count = sum(1 for event in events if isinstance(event, (UserMessage, AssistantMessage)))

    # Generate timestamp and sanitize focus for archive naming
    timestamp = datetime.now().strftime("%Y-%m-%d")
    focus = session_data.get("focus", "general")
    safe_focus = focus.replace("/", "-").replace("\\", "-").replace("\n", "-").strip("-")

    # Create archive directory
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Preserve redacted JSONL (security requirement)
    # Note: Named "redacted" to clarify it's NOT raw - RedactionEngine has processed it
    redacted_jsonl_filename = f"{timestamp}-{safe_focus}-{session_id}-redacted.jsonl"
    redacted_jsonl_path = archive_dir / redacted_jsonl_filename

    # Apply RedactionEngine to prevent credential leakage
    from hestai_mcp.mcp.tools.shared.security import RedactionEngine

    try:
        RedactionEngine.copy_and_redact(jsonl_path, redacted_jsonl_path)
        logger.info(f"Preserved redacted JSONL to {redacted_jsonl_path}")
    except Exception as e:
        # BLOCKING: Fail-closed enforcement
        # If redaction fails, archive is BLOCKED - do NOT continue
        logger.error(f"SECURITY: Redaction failed, blocking archive: {e}")
        raise RuntimeError(f"Archive blocked: redaction failed - {str(e)}") from e

    # Feature 2: OCTAVE Compression (graceful degradation)
    # SS-I2: Properly await async function - no asyncio.run() anti-pattern
    octave_path = None
    compression_status = "skipped"

    try:
        from hestai_mcp.mcp.tools.shared.compression import compress_to_octave

        # Await async compression function (SS-I2 compliance)
        octave_content = await compress_to_octave(
            transcript_path=redacted_jsonl_path,
            session_data=session_data,
            description=description,
        )

        if octave_content:
            # Save OCTAVE compression
            octave_filename = f"{timestamp}-{safe_focus}-{session_id}.oct.md"
            octave_path = archive_dir / octave_filename
            octave_path.write_text(octave_content)
            logger.info(f"Saved OCTAVE compression to {octave_path}")
            compression_status = "success"

            # Feature 4: Verify context claims before extraction
            from hestai_mcp.mcp.tools.shared.verification import verify_context_claims

            verification_result = verify_context_claims(octave_content, project_root)

            if verification_result["passed"]:
                # Feature 3: Extract context for PROJECT-CONTEXT update
                from hestai_mcp.mcp.tools.shared.context_extraction import (
                    extract_context_from_octave,
                )

                context_content = extract_context_from_octave(octave_content)
                if context_content:
                    logger.info("Extracted context from OCTAVE (ready for context_update)")
                    # Note: Actual PROJECT-CONTEXT update happens via separate context_update tool

                # Feature 5: Append to learnings index
                from hestai_mcp.mcp.tools.shared.learnings_index import (
                    append_to_learnings_index,
                    extract_learnings_keys,
                )

                learnings_keys = extract_learnings_keys(octave_content)
                append_to_learnings_index(session_data, learnings_keys, archive_dir)

            else:
                logger.warning(f"Context verification failed: {verification_result['issues']}")

        else:
            compression_status = "failed"
            logger.warning("OCTAVE compression returned None (graceful degradation)")

    except Exception as e:
        # Non-blocking: Log warning but continue with raw JSONL archive
        compression_status = "failed"
        logger.warning(f"OCTAVE compression failed (non-blocking): {e}")

    # Remove active session directory
    shutil.rmtree(session_dir)
    logger.info(f"Removed active session directory: {session_dir}")

    # Create response
    response = {
        "status": "success",
        "archive_path": str(redacted_jsonl_path),
        "redacted_jsonl_path": str(redacted_jsonl_path),
        "message_count": message_count,
        "session_id": session_id,
        "compression_status": compression_status,
    }

    if octave_path:
        response["octave_path"] = str(octave_path)

    return response
