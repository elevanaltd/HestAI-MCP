===CLOCK_IN_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"1.3-OCTAVE-SUMMARY"
  STATUS::ACTIVE
  PURPOSE::"Operational decision-logic for clock_in MCP tool"
  FULL_DOC::".hestai/workflow/components/000-CLOCK-IN-NORTH-STAR.md"
  INHERITS::[System_NS,Product_NS,System_Steward_NS]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS::6[meets_PROPHETIC_VIGILANCE]

§1::IMMUTABLES[6_Total]

CI-I1::SESSION_REGISTRATION_MANDATORY::[
  PRINCIPLE::every_agent_session_begins_with_clock_in,
  WHY::enables_audit_trails⊕conflict_detection⊕cognitive_continuity,
  STATUS::PENDING[implementation-lead@B1]
]

CI-I2::CONTEXT_MUST_BE_FRESH::[
  PRINCIPLE::generate_fresh_state_on_every_invocation,
  WHY::prevents_hallucinations_from_stale_data[Product_I4],
  STATUS::PENDING[implementation-lead@B1]
]

CI-I3::AI_ASSISTED_CONTEXT_SELECTION::[
  PRINCIPLE::AI_selects⊕synthesizes_context_by_role⊕focus,
  WHY::agents_need_curated_context[Issue_#87],
  STATUS::PENDING[implementation-lead@B1]
]

CI-I4::FAST_LAYER_LIFECYCLE::[
  PRINCIPLE::clock_in_updates_.hestai/context/state/,
  WHY::agents_need_current_focus⊕blockers⊕checklist[ADR-0056],
  STATUS::PENDING[implementation-lead@B1]
]

CI-I5::FOCUS_CONFLICT_DETECTION::[
  PRINCIPLE::detect_active_session_in_same_worktree,
  WHY::prevents_concurrent_agents_overwriting_context,
  STATUS::PENDING[implementation-lead@B1]
]

CI-I6::TDD_DISCIPLINE_ENFORCEMENT::[
  PRINCIPLE::RED→GREEN→REFACTOR_discipline_required,
  WHY::System_North_Star_I1[test-first_mandate],
  STATUS::PENDING[implementation-lead@B1]
]

§2::CRITICAL_ASSUMPTIONS[6_Total]

CI-A1::AI_CONTEXT_SYNTHESIS[80%|High]→PENDING[implementation-lead@B1]
CI-A2::GITHUB_ISSUE_SEARCH[85%|Medium]→PENDING[implementation-lead@B1]
CI-A3::CLEANUP_POLICY[90%|Low]→PENDING[implementation-lead@B2]
CI-A4::WORKSPACE_CONFIG[75%|Medium]→PENDING[implementation-lead@B2]
CI-A5::CONFLICT_DETECTION[95%|High]→PENDING[implementation-lead@B1]
CI-A6::SS_INFRA_READY[70%|Critical]→PENDING[technical-architect@B1]

§3::CONSTRAINED_VARIABLES[Top_4]

CONTEXT_SOURCES::[IMMUTABLE::must_gather_comprehensive,FLEXIBLE::Repomix|other_tools]
FOCUS_RESOLUTION::[IMMUTABLE::must_resolve,PRIORITY::explicit→GitHub→branch→default]
AI_MODEL::[IMMUTABLE::must_use_async[SS-I2],FLEXIBLE::~/.hestai/config/ai.json]
AI_PROMPTS::[IMMUTABLE::versioned⊕auditable[SS-I5],FLEXIBLE::prompt_content]

§4::SCOPE_BOUNDARIES

IS::[
  ✅::session_registration_and_tracking,
  ✅::FAST_layer_lifecycle_management,
  ✅::AI-assisted_context_synthesis,
  ✅::focus_conflict_detection
]

IS_NOT::[
  ❌::session_archival[clock_out_responsibility],
  ❌::identity_validation[odyssean_anchor_responsibility],
  ❌::context_file_writing[octave_create_responsibility],
  ❌::governance_enforcement[System_Steward_responsibility]
]

§5::DECISION_GATES

GATES::D1[DONE]→B0[BLOCKED:SS_infra]→B1[PENDING]→B2[PENDING]→B3[PENDING]

§6::INPUT_OUTPUT_CONTRACT

INPUT::[role::REQUIRED,focus::OPTIONAL,working_dir::REQUIRED,model::OPTIONAL]
OUTPUT::[session_id,context_paths,conflict,focus_resolved,github_context,instruction]

§7::EXECUTION_SEQUENCE

CLOCK_IN::[
  VALIDATE_INPUT→DETECT_CONFLICT→CREATE_SESSION→RESOLVE_FOCUS→
  GATHER_CONTEXT[AI]→SYNTHESIZE_FAST[AI]→WRITE_FAST→RETURN_RESPONSE
]
FALLBACK::deterministic_file_list_if_AI_fails[SS-I6]

§8::BINDING_CEREMONY_POSITION

ODYSSEAN_SEQUENCE::[READ_PROMPT→CLOCK_IN[THIS]→READ_CONTEXT→ODYSSEAN_ANCHOR→DASHBOARD]

§9::DEPENDENCIES

BLOCKING::[AIClient_async[SS-I2],MCP_client[SS-I3],OCTAVE_MCP[SS-I1]]
RELATED::[#56,#87,#102,#35,#36]|[ADR-0033,ADR-0035,ADR-0036,ADR-0046,ADR-0056]

§10::AGENT_ESCALATION

requirements-steward::[violates_CI-I#,scope_question,NS_amendment]
technical-architect::[architecture_decisions,integration_design]
implementation-lead::[assumption_validation,build_execution]

§11::TRIGGER_PATTERNS

LOAD_FULL_NORTH_STAR_IF::[
  "violates CI-I1-I6"::immutable_conflict,
  "session lifecycle"::state_transition_unclear,
  "FAST layer decision"::content_structure,
  "conflict resolution"::multi-session_scenario
]

§12::PROTECTION_CLAUSE

IF::work_contradicts_North_Star→STOP→CITE[CI-I#]→ESCALATE[requirements-steward]

THE_OATH::"6 Immutables (CI-I1-I6) bind clock_in implementation. Contradiction requires STOP, CITE, ESCALATE."

===END===
