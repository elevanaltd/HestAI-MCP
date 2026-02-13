"""Operation Protocols - WHAT each specific AI call does.

Each protocol is task-scoped (~50 lines) and composed with the identity kernel
at runtime. This separation enables:
- Constitutional coherence (identity always loaded)
- Task-specific behavior (protocol varies per operation)
- Modularity (add new protocols without changing identity)

Architecture Decision: debate 2026-01-02-context-steward-prompt-architecture
"""

from hestai_mcp.modules.services.ai.prompts.identity_kernel import CONTEXT_STEWARD_IDENTITY

# clock_in synthesis protocol (~50 lines)
# Enhanced with structured OCTAVE output format per issue #140
CLOCK_IN_SYNTHESIS_PROTOCOL = """OPERATION: Session Context Synthesis (clock_in)

PURPOSE: Generate structured, actionable context for Claude Code agent session.

INPUT YOU WILL RECEIVE:
- Role: The agent's designated role (e.g., "implementation-lead")
- Focus: Their work focus for this session
- Project Context: Content from PROJECT-CONTEXT.oct.md (if available)
- Git State: Branch, recent commits, modified files

OUTPUT FORMAT (use exactly this OCTAVE structure):
CONTEXT_FILES::[@.hestai/context/PROJECT-CONTEXT.oct.md:L1-50, @.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md:L1-30]
FOCUS::{focus_value_from_input}
PHASE::{phase_from_context_or_UNKNOWN}
BLOCKERS::[{blocker1}, {blocker2}] or BLOCKERS::[]
TASKS::[{task1_from_context}, {task2_from_context}]
FRESHNESS_WARNING::{warning_if_stale_or_NONE}

FIELD DEFINITIONS:
- CONTEXT_FILES: File paths with line ranges for Claude Code navigation (@path:L#-#)
- FOCUS: Echo the focus value from input
- PHASE: Extract from PROJECT-CONTEXT META.PHASE or use "UNKNOWN"
- BLOCKERS: List of active blockers or empty list
- TASKS: Actionable tasks derived from context (cite source)
- FRESHNESS_WARNING: I4 warning if context is stale, otherwise "NONE"

CRITICAL RULES:
- Use OCTAVE :: syntax for all fields (not colons)
- Only include tasks that appear in the provided context
- Extract PHASE from PROJECT-CONTEXT if available
- Do NOT invent tasks, deadlines, or project details
- Keep output compact and navigable
"""

# clock_out compression protocol (~45 lines)
CLOCK_OUT_COMPRESSION_PROTOCOL = """OPERATION: Session Transcript Compression (clock_out)

PURPOSE: Compress session transcript to OCTAVE format for archival.

COMPRESSION TARGETS:
- Reduction: 60-80% of original size
- Preserve: Decisions, blockers, outcomes, learnings, BECAUSE chains
- Remove: Verbose explanations, repeated context, tool output noise

OUTPUT FORMAT:
===SESSION_SUMMARY===
META:
  SESSION_ID::"{session_id}"
  ROLE::{role}
  FOCUS::"{focus}"
  DURATION::{duration_estimate}

OUTCOMES::[
  <completed items with evidence>
]

DECISIONS::[
  <key decisions made with rationale>
]

BLOCKERS::[
  <unresolved blockers for next session>
]

LEARNINGS::[
  <insights worth preserving>
]

NEXT_SESSION::[
  <carry-forward items>
]
===END===

CRITICAL RULES:
- Semantic fidelity over token savings - preserve meaning
- Include BECAUSE chains that explain rationale
- Flag incomplete work honestly
- Do NOT fabricate outcomes not in transcript
"""


def compose_prompt(protocol: str) -> str:
    """Compose identity kernel with operation protocol.

    This is the core of the LAYERED CONSTITUTIONAL INJECTION pattern:
    - Identity kernel provides WHO (always loaded, ~30 lines)
    - Protocol provides WHAT (task-specific, ~50 lines)
    - Combined stays under 90-line ADR-0039 target

    Args:
        protocol: The operation-specific protocol string

    Returns:
        Combined system prompt with identity + protocol
    """
    return f"{CONTEXT_STEWARD_IDENTITY}\n\n---\n\n{protocol}"
