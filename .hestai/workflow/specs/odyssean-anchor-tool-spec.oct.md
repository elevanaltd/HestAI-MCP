===ODYSSEAN_ANCHOR_TOOL_SPEC===

META:
  TYPE::"IMPLEMENTATION_SPEC"
  ID::"odyssean-anchor-mcp-tool"
  VERSION::"1.0"
  STATUS::PROPOSED
  PRIORITY::PHASE_3
  GITHUB_ISSUE::TBD
  CREATED::"2025-12-27"
  AUTHOR::"holistic-orchestrator"
  DEBATE_SOURCE::"docs/debates/2025-12-27-load-command-architecture.oct.md"

## PURPOSE

Replace legacy `anchor_submit` with `odyssean_anchor` MCP tool that provides:
- Server-side RAPH vector validation (not client-side)
- Retry guidance on failure (not silent acceptance)
- Challenge-response validation layer
- ARM context injection (authoritative, not agent-generated)

## CONTEXT

CURRENT_STATE::[
  anchor_submit::EXISTS[returns_enforcement_rules_no_vector_validation],
  clock_in::EXISTS[returns_session_id_context_paths],
  clock_out::EXISTS[archives_session]
]

PROBLEM::[
  "anchor_submit accepts any structure without validation",
  "Agent can generate invalid/hallucinated ARM",
  "No retry guidance on malformed vectors",
  "Validation theater continues"
]

DEBATE_CONSENSUS::[
  "odyssean_anchor MCP tool is essential (client-side validation insufficient)",
  "MCP holds authoritative ARM state",
  "TENSION is cognitive proof (agent interprets, not copies)",
  "4-section schema: BIND, ARM, TENSION, COMMIT"
]

## SPECIFICATION

### Tool Signature

SIGNATURE::
  FUNCTION::odyssean_anchor
  PARAMS::[
    session_id::str[Session_ID_from_clock_in],
    role::str[Agent_role_name],
    vector_candidate::str[Raw_RAPH_VECTOR_block],
    tier::str[quick|default|deep]
  ]
  RETURNS::OdysseanAnchorResult[
    validated::bool,
    canonical_anchor::str,
    errors::list[str],
    guidance::str,
    enforcement::dict
  ]

### Validation Logic

SCHEMA_VALIDATION::[
  has_markers::"===RAPH_VECTOR::v4.0===" and "===END_RAPH_VECTOR===",
  has_sections::[BIND, ARM, TENSION, COMMIT],
  no_extra_sections::"SOURCES, HAZARD, FLUKE rejected as separate sections"
]

BIND_VALIDATION::[
  has_role::"ROLE:: field present",
  has_cognition::"COGNITION:: field present",
  has_authority::"AUTHORITY:: field present (RESPONSIBLE or DELEGATED[session])"
]

ARM_VALIDATION::[
  // ARM is MCP-ENRICHED, not agent-generated
  // Tool compares agent-submitted ARM against authoritative state
  phase_matches_context::"PHASE matches PROJECT-CONTEXT.oct.md",
  branch_matches_git::"BRANCH matches current git branch",
  files_plausible::"FILES count within reasonable range of git status"
]

TENSION_VALIDATION::[
  count_meets_tier::"QUICK>=1, DEFAULT>=2, DEEP>=3",
  has_line_citation::"Each tension includes L{N}",
  has_ctx_citation::"Each tension includes CTX:{path}",
  ctx_is_falsifiable::"CTX path exists or refers to known context"
]

COMMIT_VALIDATION::[
  artifact_is_concrete::"Not 'response', 'thoughts', or abstract",
  gate_is_specified::"Validation method present"
]

### Retry Behavior

RETRY_PROTOCOL::[
  MAX_RETRIES::2,
  ON_FAIL::"Return specific errors with guidance",
  GUIDANCE_FORMAT::"VALIDATION FAILED: [Error1, Error2]. RETRY: [Specific fix instructions]",
  HARD_FAIL::"After 2 retries, block further action (human intervention required)"
]

GUIDANCE_EXAMPLES::[
  arm_mismatch::"ARM shows PHASE::B2 but PROJECT-CONTEXT.oct.md shows B1. Update PHASE to match context.",
  tension_missing_ctx::"TENSION 1 has L315 but no CTX citation. Add CTX:{path}[{state}] to prove context awareness.",
  commit_abstract::"COMMIT artifact is 'my response'. Name a concrete file (e.g., src/main.py) or tool output.",
  tension_count::"TIER_DEFAULT requires 2 tensions, found 1. Add another tension."
]

### ARM Injection

ARM_INJECTION::[
  SOURCE::"clock_in session + git state + PROJECT-CONTEXT.oct.md",
  AUTHORITATIVE::"MCP-generated ARM is truth, not agent-submitted",
  COMPARISON::"Agent ARM vs MCP ARM - warn on mismatch, fail on gross hallucination"
]

## IMPLEMENTATION

FILE_LOCATION::"src/hestai_mcp/mcp/tools/odyssean_anchor.py"

DEPENDENCIES::[
  clock_in::"Session must exist",
  PROJECT-CONTEXT::"For phase verification",
  git::"For branch/files verification"
]

INTEGRATION_POINT::[
  ID::"odyssean_anchor",
  STAGE::"SOON->NOW (when implemented)",
  REFERENCE_TOKEN::"INTEGRATION_POINT::odyssean_anchor",
  CONTRACT_TEST::"tests/contracts/odyssean_anchor/test_*.py",
  INTEGRATION_TEST::"tests/integration/odyssean_anchor/test_*.py"
]

## MIGRATION

FROM_ANCHOR_SUBMIT::[
  STEP_1::"Build odyssean_anchor with validation logic",
  STEP_2::"Update /bind command to call odyssean_anchor",
  STEP_3::"Deprecate anchor_submit (keep for backwards compat)",
  STEP_4::"Update subagent protocols to use odyssean_anchor"
]

BACKWARDS_COMPAT::[
  anchor_submit::"Keep working for existing integrations",
  enforcement::"odyssean_anchor returns same enforcement fields"
]

## SUCCESS_CRITERIA

VALIDATION::[
  "Rejects vectors with missing sections",
  "Rejects tensions without CTX citations",
  "Rejects abstract COMMIT artifacts",
  "Provides specific retry guidance",
  "Detects ARM hallucination vs git reality"
]

PERFORMANCE::[
  latency_target::"<500ms validation",
  retry_total::"<2s for full retry cycle"
]

## REFERENCES

ADR_0036::"docs/adr/adr-0036-odyssean-anchor-binding.md"
DEBATE_RECORD::"docs/debates/2025-12-27-load-command-architecture.oct.md"
BIND_COMMAND::"/Users/shaunbuswell/.claude/commands/bind.md"
NORTH_STAR_I5::"ODYSSEAN_IDENTITY_BINDING"

===END===
