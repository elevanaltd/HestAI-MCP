"""
OCTAVE Compression - Session transcript compression using AI.

Implements Feature 2: OCTAVE compression via AIClient with graceful degradation.
Uses session-compression.txt prompt to extract DECISIONS, BLOCKERS, LEARNINGS
into dense OCTAVE format achieving 60-80% compression with causal fidelity.

Integration with clock_out workflow:
1. clock_out() calls compress_to_octave() after redaction
2. Returns OCTAVE content or None (graceful degradation)
3. Content saved as {timestamp}-{focus}-{session_id}.oct.md
"""

import logging
from pathlib import Path
from typing import Any

from hestai_mcp.modules.services.ai.client import AIClient
from hestai_mcp.modules.services.ai.providers.base import CompletionRequest

logger = logging.getLogger(__name__)


def load_compression_prompt() -> str:
    """
    Load session compression prompt template.

    Returns:
        Compression prompt content from systemprompts/

    Raises:
        FileNotFoundError: If prompt template not found
    """
    # Prompt location in hestai-mcp-server (reference implementation)
    # For hestai-core, we embed the essential protocol inline
    prompt_template = """===SESSION_COMPRESSION_PROTOCOL===
ROLE::SYSTEM_STEWARD
TASK::TRANSCRIPT→OCTAVE_COMPRESSION
PURPOSE::"Extract decision_logic + blockers + learnings from session transcript into OCTAVE format"

EXTRACTION_ALGORITHM::
1. IDENTIFY_MARKERS::[decisions, blockers, learnings, outcomes, actions]
2. RECONSTRUCT_CAUSALITY::BECAUSE[reason]→choice→outcome
3. GROUND_WITH_SCENARIOS::concrete_examples_for_abstractions
4. PRESERVE_METRICS::include[context+baseline+validation]

OUTPUT_FORMAT::
===SESSION_COMPRESSION===

METADATA::[SESSION_ID::{{session_id}}, ROLE::{{role}}, DURATION::{{duration}}]

DECISIONS::[
  DECISION_1::BECAUSE[constraint_or_reason]→choice→outcome,
  DECISION_2::BECAUSE[evidence]→choice→outcome
]

BLOCKERS::[
  blocker_1⊗resolved[how],
  blocker_2⊗blocked[what_blocks_it]
]

LEARNINGS::[
  problem→solution→wisdom→transfer_guidance
]

OUTCOMES::[
  outcome_1[metric_with_context]
]

NEXT_ACTIONS::[
  ACTION_1::owner={{role}}→description→blocking[yes|no]
]

===END_SESSION_COMPRESSION===

CONSTRAINTS::
- Use OCTAVE operators (→, ⊗, ::, [])
- Include BECAUSE statements for decisions
- Ground abstractions with concrete scenarios
- Preserve metrics with context
- Extract transfer guidance from learnings
"""
    return prompt_template


async def compress_to_octave(
    transcript_path: Path, session_data: dict[str, Any], description: str = ""
) -> str | None:
    """
    Compress session transcript to OCTAVE format using AI.

    Implements graceful degradation: returns None on failure instead of raising.
    This allows clock_out to continue with raw JSONL archive if compression fails.

    Args:
        transcript_path: Path to raw JSONL transcript
        session_data: Session metadata (session_id, role, duration, etc.)
        description: Optional user-provided summary from clockout

    Returns:
        OCTAVE formatted content string, or None on failure

    Design Decision:
        Graceful degradation chosen over fail-fast because:
        - Raw JSONL archive is already preserved (primary goal achieved)
        - OCTAVE compression is enhancement, not critical requirement
        - User can manually compress later if needed
        - Prevents AI failures from blocking session archival
    """
    try:
        # Load transcript content
        if not transcript_path.exists():
            logger.error(f"Transcript not found: {transcript_path}")
            return None

        transcript_content = transcript_path.read_text()

        # Load compression prompt
        prompt_template = load_compression_prompt()

        # Build compression request with session context
        session_id = session_data.get("session_id", "unknown")
        role = session_data.get("role", "unknown")
        duration = session_data.get("duration", "unknown")

        # Construct prompt with context
        system_prompt = prompt_template.replace("{{session_id}}", session_id)
        system_prompt = system_prompt.replace("{{role}}", role)
        system_prompt = system_prompt.replace("{{duration}}", duration)

        user_prompt = f"""Session Transcript:
{transcript_content}

Clockout Summary (if provided by user):
{description if description else "None provided"}

Compress this session transcript according to the protocol above.
Extract DECISIONS, BLOCKERS, LEARNINGS, OUTCOMES, and NEXT_ACTIONS.
Use OCTAVE operators throughout.
"""

        # Create AI client and make request (SS-I2: async-first)
        async with AIClient() as client:
            request = CompletionRequest(system_prompt=system_prompt, user_prompt=user_prompt)

            # Get compression result (await async method)
            octave_content = await client.complete_text(request)

        logger.info(f"Successfully compressed session {session_id} to OCTAVE")
        return octave_content

    except Exception as e:
        # Graceful degradation - log error but don't raise
        logger.warning(f"OCTAVE compression failed (graceful degradation): {e}")
        return None
