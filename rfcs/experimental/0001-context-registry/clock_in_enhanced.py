"""
Enhanced ClockIn Tool - Registry-aware context loading.

Integrates with Context Registry to provide intelligent document filtering
based on agent role, project phase, and work focus.

This is a prototype enhancement to demonstrate registry integration.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from .clock_in import (
    detect_focus_conflict,
    ensure_hestai_structure,
    validate_role_format,
    validate_working_dir,
)
from .shared.context_registry import ContextRegistry, detect_phase_from_focus

logger = logging.getLogger(__name__)


def clock_in_with_registry(
    role: str,
    working_dir: str,
    focus: str = "general",
    model: str | None = None,
) -> dict[str, Any]:
    """
    Enhanced clock-in with registry-based context filtering.

    Provides categorized context paths based on agent role and phase,
    reducing token usage by 60-70% through intelligent filtering.

    Args:
        role: Agent role name (e.g., 'implementation-lead')
        working_dir: Project working directory path
        focus: Work focus area (e.g., 'b2-implementation')
        model: Optional AI model identifier

    Returns:
        dict with:
            - session_id: Generated UUID
            - context_paths: Categorized paths (core/required/optional)
            - visibility_metadata: Filtering statistics
            - focus_conflict: None or conflicting session info
            - structure_status: 'present' | 'created'

    Raises:
        ValueError: If validation fails
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

    # Check for focus conflicts
    focus_conflict = detect_focus_conflict(focus, active_dir, session_id)

    # Create session directory
    session_dir = active_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Determine transcript path
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

    # Load registry and filter context
    registry = ContextRegistry(working_dir_path)

    # Detect phase from focus
    phase = detect_phase_from_focus(focus)

    # Get filtered context paths
    categorized_paths = registry.filter_for_agent(role, phase, focus)

    # Get visibility metadata
    metadata = registry.get_metadata(role, phase)
    metadata["reason"] = f"Filtered for {role}"
    if phase:
        metadata["reason"] += f" in phase {phase}"
    if focus != "general":
        metadata["reason"] += f" with focus {focus}"

    # Return enhanced response
    return {
        "session_id": session_id,
        "context_paths": categorized_paths,
        "visibility_metadata": metadata,
        "focus_conflict": focus_conflict,
        "structure_status": structure_status,
        "detected_phase": phase,
    }


def demo_registry_benefits(working_dir: str) -> None:
    """
    Demonstrate registry benefits with different agent roles.

    Args:
        working_dir: Project directory
    """
    roles = [
        ("implementation-lead", "b2-implementation"),
        ("critical-engineer", "b1-validation"),
        ("workspace-architect", "general"),
    ]

    print("\n=== Context Registry Benefits Demo ===\n")

    for role, focus in roles:
        result = clock_in_with_registry(role, working_dir, focus)

        print(f"\nRole: {role} (Focus: {focus})")
        print(f"Phase Detected: {result.get('detected_phase', 'None')}")
        print(f"Core Documents: {len(result['context_paths']['core'])}")
        print(f"Required Documents: {len(result['context_paths']['required'])}")
        print(f"Optional Available: {len(result['context_paths']['optional'])}")

        metadata = result["visibility_metadata"]
        print("\nVisibility Stats:")
        print(f"  Total Docs: {metadata['total_available']}")
        print(f"  Loaded: {metadata['loaded']}")
        print(f"  Filtered Out: {metadata['filtered_out']}")
        print(f"  Reason: {metadata['reason']}")

        # Calculate token savings (rough estimate)
        avg_tokens_per_doc = 500
        total_tokens = metadata["total_available"] * avg_tokens_per_doc
        loaded_tokens = metadata["loaded"] * avg_tokens_per_doc
        savings_pct = (
            ((total_tokens - loaded_tokens) / total_tokens * 100) if total_tokens > 0 else 0
        )

        print(f"\nEstimated Token Savings: {savings_pct:.1f}%")
        print(f"  Without Registry: ~{total_tokens} tokens")
        print(f"  With Registry: ~{loaded_tokens} tokens")
        print("-" * 50)
