"""Operation Protocols - WHAT each specific AI call does.

Each protocol is task-scoped (~50 lines) and composed with the identity kernel
at runtime. This separation enables:
- Constitutional coherence (identity always loaded)
- Task-specific behavior (protocol varies per operation)
- Modularity (add new protocols without changing identity)

Architecture Decision: debate 2026-01-02-context-steward-prompt-architecture
"""

from hestai_mcp.ai.prompts.identity_kernel import CONTEXT_STEWARD_IDENTITY

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


# Odyssean Anchor cognition appropriateness check protocol (~30 lines)
ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL = """OPERATION: Cognition Appropriateness Check (odyssean_anchor)

PURPOSE: Assess if a cognition type is appropriate for an agent role.

COGNITION TYPES AND ASSOCIATIONS:
- LOGOS (The Door/Structure): architects, coordinators, technical leads, implementation leads
- ETHOS (The Wall/Boundary): validators, guardians, reviewers, stewards, security specialists
- PATHOS (The Wind/Possibility): ideators, explorers, researchers, creative roles

INPUT YOU WILL RECEIVE:
- Role: The agent's designated role
- Cognition Type: ETHOS, LOGOS, or PATHOS

OUTPUT FORMAT (JSON only):
{"appropriate": true/false, "reason": "explanation"}

CRITICAL RULES:
- Be lenient - many roles can reasonably use different cognition types
- Only flag clear mismatches (e.g., validator using PATHOS for exploration-focused work)
- Respond with JSON only, no additional text
"""

# Odyssean Anchor tension relevance check protocol (~30 lines)
ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL = """OPERATION: Tension Constraint Validation (odyssean_anchor)

PURPOSE: Validate that constraint names in TENSION section reference real constraints.

COMMON VALID CONSTRAINT PATTERNS:
- TDD_MANDATE, MINIMAL_INTERVENTION, MIP, LANE_ENFORCEMENT
- QUALITY_GATES, HUMAN_PRIMACY, I1-I6 immutables, PHASE_GATED

INPUT YOU WILL RECEIVE:
- Constraints: List of constraint names from TENSION section
- Constitution excerpt: Reference text to validate against

OUTPUT FORMAT (JSON only):
{"all_valid": true/false, "invalid_constraints": ["list", "of", "hallucinated"]}

CRITICAL RULES:
- Be lenient - if a constraint could reasonably derive from the constitution, accept it
- Only flag constraints that appear completely hallucinated
- Respond with JSON only, no additional text
"""

# Odyssean Anchor commit feasibility check protocol (~30 lines)
ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL = """OPERATION: Commit Artifact Feasibility Check (odyssean_anchor)

PURPOSE: Assess if a commit artifact is achievable within a session.

ACHIEVABLE ARTIFACT EXAMPLES:
- src/validators/semantic.py (specific file)
- Updated test suite for anchor validation
- PR #123 with implementation

UNREALISTIC ARTIFACT EXAMPLES:
- Complete system rewrite
- All bugs fixed
- Perfect documentation

INPUT YOU WILL RECEIVE:
- Artifact: The artifact path/description from COMMIT section
- Focus: The session focus area

OUTPUT FORMAT (JSON only):
{"feasible": true/false, "reason": "explanation"}

CRITICAL RULES:
- Be lenient - most specific artifacts are achievable
- Only flag artifacts that are clearly unrealistic for a single session
- Respond with JSON only, no additional text
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
