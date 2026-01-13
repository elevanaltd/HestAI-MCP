"""
Context Extraction - Parse OCTAVE content for PROJECT-CONTEXT updates.

Implements Feature 3: Extract DECISIONS/OUTCOMES/BLOCKERS from OCTAVE
compression for updating PROJECT-CONTEXT.md via context_update tool.

Design:
- Parse OCTAVE sections with regex
- Format for PROJECT-CONTEXT consumption
- Extract only high-signal content (decisions, outcomes, blockers)
- Preserve causal chains (BECAUSE statements)
"""

import logging
import re

logger = logging.getLogger(__name__)


def extract_context_from_octave(octave_content: str) -> str | None:
    """
    Extract DECISIONS/OUTCOMES/BLOCKERS for PROJECT-CONTEXT update.

    Parses OCTAVE compressed session content and extracts high-signal
    information suitable for project context updates.

    Args:
        octave_content: OCTAVE formatted session compression

    Returns:
        Formatted context content for PROJECT-CONTEXT, or None if no content

    Example Output:
        DECISIONS:
        - DECISION_1::BECAUSE[constraint]→choice→outcome
        - DECISION_2::BECAUSE[evidence]→choice→outcome

        OUTCOMES:
        - outcome_1[metric_with_context]

        BLOCKERS:
        - blocker_1⊗resolved[how]
    """
    if not octave_content or not octave_content.strip():
        return None

    extracted_sections = []

    # Extract DECISIONS section
    decisions = _extract_section(octave_content, "DECISIONS")
    if decisions:
        extracted_sections.append(f"DECISIONS:\n{decisions}")

    # Extract OUTCOMES section
    outcomes = _extract_section(octave_content, "OUTCOMES")
    if outcomes:
        extracted_sections.append(f"OUTCOMES:\n{outcomes}")

    # Extract BLOCKERS section (high priority for context)
    blockers = _extract_section(octave_content, "BLOCKERS")
    if blockers:
        extracted_sections.append(f"BLOCKERS:\n{blockers}")

    # Return combined content or None
    if extracted_sections:
        return "\n\n".join(extracted_sections)
    return None


def _extract_section(octave_content: str, section_name: str) -> str | None:
    """
    Extract a specific OCTAVE section by name.

    Args:
        octave_content: Full OCTAVE content
        section_name: Section to extract (e.g., "DECISIONS", "BLOCKERS")

    Returns:
        Formatted section content, or None if section not found

    Implementation:
        Uses regex to find section between ::[ and ]
        Preserves OCTAVE operators and formatting
        Converts to markdown list format for readability
    """
    # Pattern: SECTION_NAME::[...content...]
    # Handle both single-line and multi-line sections
    pattern = rf"{section_name}::\[(.*?)\]"

    match = re.search(pattern, octave_content, re.DOTALL)
    if not match:
        return None

    section_content = match.group(1).strip()
    if not section_content:
        return None

    # Convert OCTAVE list items to markdown
    # Split on commas (OCTAVE list separator)
    items = [item.strip() for item in section_content.split(",") if item.strip()]

    if not items:
        return None

    # Format as markdown list
    formatted_items = [f"- {item}" for item in items]
    return "\n".join(formatted_items)
