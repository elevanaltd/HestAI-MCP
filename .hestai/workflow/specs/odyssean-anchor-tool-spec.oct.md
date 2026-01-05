===ODYSSEAN_ANCHOR_TOOL_SPEC===

META:
  TYPE::"IMPLEMENTATION_SPEC"
  ID::"odyssean-anchor-mcp-tool"
  VERSION::"2.0"
  STATUS::APPROVED
  PRIORITY::NEXT
  TARGET::"OA5"
  GITHUB_ISSUE::#11
  CREATED::"2025-12-27"
  UPDATED::"2026-01-05"
  AUTHOR::"holistic-orchestrator"
  SUPERSEDES::"v1.2 (OA4: RAPH_VECTOR::v4.0)"

## PURPOSE

Define the `odyssean_anchor` MCP tool contract for validating the **Odyssean Anchor Proof (OA5)** server-side:
- Strong schema validation (not client-side)
- Retry guidance on failure (not silent acceptance)
- Challenge-response validation layer
- Authoritative CONTEXT enrichment (not agent-generated)

## STATUS

IMPLEMENTATION_STATUS::PENDING
NOTE::"v1.2 described OA4 (RAPH_VECTOR::v4.0). OA5 is the canonical forward spec."

## CONTEXT

CURRENT_STATE::[
  clock_in::EXISTS[returns_session_id_context_paths],
  clock_out::EXISTS[archives_session]
]

PROBLEM::[
  "Agents can fabricate or misread project state",
  "No retry guidance when proof artifacts are malformed",
  "Validation theater continues without falsifiable anchors"
]

DESIGN_CONSENSUS::[
  "Anchor proof must separate artifact vs process (RAPH is a process, not the proof name)",
  "MCP holds authoritative CONTEXT state",
  "TENSIONS are the cognitive proof keystone",
  "COMMIT is a falsifiable contract (artifact + gate)"
]

## SPECIFICATION

### Tool Signature

SIGNATURE::
  FUNCTION::odyssean_anchor
  PARAMS::[
    session_id::str[Session_ID_from_clock_in],
    role::str[Agent_role_name],
    proof_candidate::str[Raw_ODYSSEAN_ANCHOR_PROOF_block],
    tier::str[quick|default|deep]
  ]
  RETURNS::OdysseanAnchorResult[
    validated::bool,
    canonical_proof::str,
    errors::list[str],
    guidance::str,
    enforcement::dict
  ]

### Canonical Proof Format (OA5)

MARKERS::[
  START::"===ODYSSEAN_ANCHOR_PROOF::v5.0===",
  END::"===END_ODYSSEAN_ANCHOR_PROOF==="
]

SECTIONS::[
  TOP_LEVEL::[IDENTITY, CONTEXT, PROOF],
  PROOF_CONTAINS::[TENSIONS, COMMIT]
]

### Validation Logic

SCHEMA_VALIDATION::[
  has_markers::"OA5 START/END markers present",
  has_sections::[IDENTITY, CONTEXT, PROOF],
  proof_has_sections::[TENSIONS, COMMIT],
  no_unknown_top_level_sections::"Reject unknown top-level sections"
]

IDENTITY_VALIDATION::[
  has_role::"ROLE:: field present",
  has_cognition::"COGNITION:: field present",
  has_authority::"AUTHORITY:: field present with scope (RESPONSIBLE[scope] or DELEGATED[parent_session])"
]

CONTEXT_VALIDATION::[
  // CONTEXT is MCP-ENRICHED, not agent-authored truth
  // Tool compares candidate CONTEXT against authoritative state and emits canonical CONTEXT
  phase_matches_context::"PHASE matches PROJECT-CONTEXT.oct.md",
  branch_matches_git::"BRANCH matches current git branch",
  files_plausible::"FILES count within reasonable range of git status"
]

PROOF_VALIDATION::[
  tensions_valid::TENSION_VALIDATION,
  commit_valid::COMMIT_VALIDATION
]

TENSION_VALIDATION::[
  count_meets_tier::"QUICK>=1, DEFAULT>=2, DEEP>=3",
  has_line_citation::"Each tension includes L{N}",
  has_ctx_citation::"Each tension includes CTX:{path}",
  ctx_is_falsifiable::"CTX path exists or refers to allowed external context"
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
  context_mismatch::"CONTEXT shows PHASE::B2 but PROJECT-CONTEXT.oct.md shows B1. Update PHASE to match context.",
  tension_missing_ctx::"TENSION 1 has L315 but no CTX citation. Add CTX:{path}[{state}] to prove context awareness.",
  commit_abstract::"COMMIT artifact is 'my response'. Name a concrete file (e.g., src/main.py) or tool output.",
  tension_count::"TIER_DEFAULT requires 2 tensions, found 1. Add another tension."
]

### CONTEXT Enrichment

CONTEXT_ENRICHMENT::[
  SOURCE::"clock_in session + git state + PROJECT-CONTEXT.oct.md",
  AUTHORITATIVE::"MCP-enriched CONTEXT is truth; candidate CONTEXT is compared against it for mismatch detection only",
  OUTPUT_RULE::"Canonical output MUST use authoritative CONTEXT (never candidate CONTEXT)",
  COMPARISON::"Candidate CONTEXT vs authoritative CONTEXT - warn on mismatch, fail on gross hallucination"
]

## IMPLEMENTATION

FILE_LOCATION::"src/hestai_mcp/mcp/tools/odyssean_anchor.py"

DEPENDENCIES::[
  clock_in::"Session must exist",
  PROJECT-CONTEXT::"For phase verification",
  git::"For branch/files verification"
]

## SUCCESS_CRITERIA

VALIDATION::[
  "Rejects proofs with missing sections",
  "Rejects tensions without CTX citations",
  "Rejects abstract COMMIT artifacts",
  "Provides specific retry guidance",
  "Detects CONTEXT hallucination vs git reality"
]

PERFORMANCE::[
  latency_target::"<500ms validation",
  retry_total::"<2s for full retry cycle"
]

## REFERENCES

ADR_0036::"docs/adr/adr-0036-odyssean-anchor-binding.md"
TERMINOLOGY::"docs/odyssean-anchor-terminology.md"
BIND_COMMAND_REFERENCE::"hub/library/commands/bind.md"
NORTH_STAR_I5::"ODYSSEAN_IDENTITY_BINDING"

## SYNTAX_NOTES

TENSION_SYNTAX::[
  // OA5 TENSION lines use OCTAVE operators per octave-5-llm-core.oct.md
  FORMAT::"L{N}::[constraint]⇌CTX:{path}[state]→TRIGGER[action]"
  OPERATORS::[
    "⇌"::tension[binary_opposition_between_constraint_and_context],
    "→"::flow[progression_to_trigger_action]
  ]
  ASCII_ALIASES::[
    "<->"::accepted_normalized_to_⇌,
    "->"::accepted_normalized_to_→
  ]
  RECOMMENDATION::"Use Unicode (⇌, →) for canonical output; ASCII accepted for input"
]

AUTHORITY_FORMAT::[
  // Brackets with scope description REQUIRED
  RESPONSIBLE::"RESPONSIBLE[scope_description]",
  DELEGATED::"DELEGATED[parent_session_id]",
  EXAMPLE_RESPONSIBLE::"RESPONSIBLE[system_coherence_orchestration]",
  EXAMPLE_DELEGATED::"DELEGATED[parent_abc123::review_task]"
]

## DEPRECATIONS

OA4_DEPRECATED::[
  "RAPH Vector v4.0 is a deprecated name (RAPH is a process, not an artifact)",
  "BIND/ARM/TENSION/COMMIT headers are deprecated in favor of IDENTITY/CONTEXT/PROOF"
]

===END===
