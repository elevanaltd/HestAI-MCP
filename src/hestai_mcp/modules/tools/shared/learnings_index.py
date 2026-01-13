"""
Learnings Index - Extract and index learnings from OCTAVE compression.

Implements Feature 5: Parse DECISION_*/BLOCKER_*/LEARNING_* keys and append
to learnings-index.jsonl for searchable knowledge base.

Design:
- Extract structured keys from OCTAVE content
- Create JSONL entries with session metadata
- Atomic append to learnings-index.jsonl
- Enable future search/retrieval of session wisdom
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def extract_learnings_keys(octave_content: str) -> dict[str, list[str]]:
    """
    Parse DECISION_*/BLOCKER_*/LEARNING_* keys from OCTAVE content.

    Extracts structured knowledge markers for indexing:
    - DECISION_N: Architectural/implementation decisions
    - BLOCKER_N: Issues encountered and resolutions
    - LEARNING_N: Wisdom extracted from session

    Args:
        octave_content: OCTAVE formatted session compression

    Returns:
        dict with:
            - decisions: List[str] (decision descriptions)
            - blockers: List[str] (blocker descriptions)
            - learnings: List[str] (learning insights)

    Example:
        {
            "decisions": ["DECISION_1::BECAUSE[...]→choice→outcome"],
            "blockers": ["blocker_1⊗resolved[...]"],
            "learnings": ["problem→solution→wisdom"]
        }
    """
    keys: dict[str, list[str]] = {"decisions": [], "blockers": [], "learnings": []}

    # Extract DECISION_N patterns
    decision_pattern = r"DECISION_\d+::(.*?)(?=DECISION_\d+::|$)"
    decision_matches = re.findall(decision_pattern, octave_content, re.DOTALL)
    keys["decisions"] = [d.strip() for d in decision_matches if d.strip()]

    # Extract blocker patterns (blocker_name⊗status[details])
    blocker_pattern = r"(\w+)⊗(resolved|blocked)\[([^\]]+)\]"
    blocker_matches = re.findall(blocker_pattern, octave_content)
    keys["blockers"] = [f"{name}⊗{status}[{details}]" for name, status, details in blocker_matches]

    # Extract learnings from LEARNINGS section
    learnings_section_pattern = r"LEARNINGS::\[(.*?)\]"
    learnings_match = re.search(learnings_section_pattern, octave_content, re.DOTALL)

    if learnings_match:
        learnings_content = learnings_match.group(1).strip()
        # Split on commas (OCTAVE list separator)
        learning_items = [item.strip() for item in learnings_content.split(",")]
        keys["learnings"] = [item for item in learning_items if item]

    return keys


def append_to_learnings_index(
    session_data: dict[str, Any], keys: dict[str, list[str]], archive_dir: Path
) -> None:
    """
    Append learnings to learnings-index.jsonl (atomic write).

    Creates searchable index of session wisdom for future retrieval.

    Args:
        session_data: Session metadata (session_id, role, duration, etc.)
        keys: Extracted keys from extract_learnings_keys()
        archive_dir: Archive directory containing learnings-index.jsonl

    Implementation:
        - One JSONL entry per session
        - Atomic append (open with 'a' mode)
        - Include timestamp for temporal search
        - Include session_id for linking to full archive

    JSONL Schema:
        {
            "timestamp": "2025-12-16T10:30:00",
            "session_id": "abc123",
            "role": "implementation-lead",
            "duration": "2h 15m",
            "decisions": [...],
            "blockers": [...],
            "learnings": [...]
        }
    """
    # Create learnings index path
    index_path = archive_dir / "learnings-index.jsonl"

    # Build index entry
    index_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_data.get("session_id", "unknown"),
        "role": session_data.get("role", "unknown"),
        "duration": session_data.get("duration", "unknown"),
        "focus": session_data.get("focus", "general"),
        "decisions": keys.get("decisions", []),
        "blockers": keys.get("blockers", []),
        "learnings": keys.get("learnings", []),
    }

    # Atomic append to JSONL
    try:
        with index_path.open("a") as f:
            f.write(json.dumps(index_entry) + "\n")

        logger.info(f"Appended learnings index for session {session_data.get('session_id')}")

    except Exception as e:
        # Non-blocking: Log warning but don't fail clock_out
        logger.warning(f"Failed to append to learnings index: {e}")
