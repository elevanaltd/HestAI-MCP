===CLOCK_IN_NORTH_STAR_SUMMARY===
META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"2.0-UPOG"
  STATUS::ACTIVE
  NAMESPACE::PROD
  PURPOSE::"Operational decision-logic for clock_in MCP tool"
  FULL_DOC::".hestai/workflow/components/000-CLOCK-IN-NORTH-STAR.md"
  INHERITS::[
    System_NS,
    Product_NS,
    System_Steward_NS
  ]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS_COUNT::6
  ASSUMPTIONS_NOTE::meets_PROPHETIC_VIGILANCE
  CONTRACT::HOLOGRAPHIC<parse_only_governance>
  CANONICAL::".hestai/north-star/components/000-CLOCK-IN-NORTH-STAR-SUMMARY.oct.md"
  SOURCE::".hestai/north-star/components/000-CLOCK-IN-NORTH-STAR-SUMMARY.oct.md"
§1::IMMUTABLES
  COUNT::6
  CI_I1<SESSION_REGISTRATION_MANDATORY>:
    PRINCIPLE::"every agent session begins with clock_in"
    WHY::"enables audit trails, conflict detection, cognitive continuity"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  CI_I2<CONTEXT_MUST_BE_FRESH>:
    PRINCIPLE::"generate fresh state on every invocation"
    WHY::"prevents hallucinations from stale data — see Product I4"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  CI_I3<AI_ASSISTED_CONTEXT_SELECTION>:
    PRINCIPLE::"AI selects and synthesizes context by role and focus"
    WHY::"agents need curated context — see Issue 87"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  CI_I4<FAST_LAYER_LIFECYCLE>:
    PRINCIPLE::"clock_in updates .hestai/context/state/"
    WHY::"agents need current focus, blockers, checklist — see ADR-0056"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  CI_I5<FOCUS_CONFLICT_DETECTION>:
    PRINCIPLE::"detect active session in same worktree"
    WHY::"prevents concurrent agents overwriting context"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  CI_I6<TDD_DISCIPLINE_ENFORCEMENT>:
    PRINCIPLE::"RED then GREEN then REFACTOR discipline required"
    WHY::"System North Star I1 — test-first mandate"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
§2::CRITICAL_ASSUMPTIONS
  COUNT::6
  CI_A1<AI_CONTEXT_SYNTHESIS>:
    CONFIDENCE::"80%"
    RISK::High
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  CI_A2<GITHUB_ISSUE_SEARCH>:
    CONFIDENCE::"85%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  CI_A3<CLEANUP_POLICY>:
    CONFIDENCE::"90%"
    RISK::Low
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  CI_A4<WORKSPACE_CONFIG>:
    CONFIDENCE::"75%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  CI_A5<CONFLICT_DETECTION>:
    CONFIDENCE::"95%"
    RISK::High
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  CI_A6<SS_INFRA_READY>:
    CONFIDENCE::"70%"
    RISK::Critical
    STATUS::PENDING
    OWNER::technical-architect
    GATE::B1
§3::CONSTRAINED_VARIABLES
  CONTEXT_SOURCES:
    IMMUTABLE::must_gather_comprehensive
    FLEXIBLE::"Repomix or other tools"
  FOCUS_RESOLUTION:
    IMMUTABLE::must_resolve
    PRIORITY::[explicit→GitHub→branch→default]
  AI_MODEL:
    IMMUTABLE::"must use async — see SS-I2"
    FLEXIBLE::"~/.hestai/config/ai.yaml or .env"
  AI_PROMPTS:
    IMMUTABLE::"versioned and auditable — see SS-I5"
    FLEXIBLE::prompt_content
§4::SCOPE_BOUNDARIES
  IS::[
    session_registration_and_tracking,
    FAST_layer_lifecycle_management,
    AI_assisted_context_synthesis,
    focus_conflict_detection
  ]
  IS_NOT::[
    session_archival_clock_out_responsibility,
    identity_validation_odyssean_anchor_responsibility,
    context_file_writing_octave_create_responsibility,
    governance_enforcement_System_Steward_responsibility
  ]
§5::DECISION_GATES
  GATES::[D1_DONE→B0_BLOCKED_SS_infra→B1_PENDING→B2_PENDING→B3_PENDING]
§6::INPUT_OUTPUT_CONTRACT
  INPUT:
    role::REQUIRED
    focus::OPTIONAL
    working_dir::REQUIRED
    model::OPTIONAL
  OUTPUT::[
    session_id,
    context_paths,
    conflict,
    focus_resolved,
    github_context,
    instruction
  ]
§7::EXECUTION_SEQUENCE
  CLOCK_IN::[VALIDATE_INPUT→DETECT_CONFLICT→CREATE_SESSION→RESOLVE_FOCUS→GATHER_CONTEXT_AI→SYNTHESIZE_FAST_AI→WRITE_FAST→RETURN_RESPONSE]
  FALLBACK::"deterministic file list if AI fails — see SS-I6"
§8::BINDING_CEREMONY_POSITION
  ODYSSEAN_SEQUENCE::[READ_PROMPT→CLOCK_IN_THIS→READ_CONTEXT→ODYSSEAN_ANCHOR→DASHBOARD]
§9::DEPENDENCIES
  BLOCKING::[
    AIClient_async_SS_I2,
    MCP_client_SS_I3,
    OCTAVE_MCP_SS_I1
  ]
  RELATED_ISSUES::[
    "#56",
    "#87",
    "#102",
    "#35",
    "#36"
  ]
  RELATED_ADRS::[
    ADR-0033,
    ADR-0035,
    ADR-0036,
    ADR-0046,
    ADR-0056
  ]
§10::AGENT_ESCALATION
  requirements_steward::[
    immutable_violation,
    scope_question,
    NS_amendment
  ]
  technical_architect::[architecture_decisions,integration_design]
  implementation_lead::[assumption_validation,build_execution]
§11::TRIGGER_PATTERNS
  LOAD_FULL_NORTH_STAR_IF:
    IMMUTABLE_CONFLICT::"violates CI-I1-I6"
    SESSION_LIFECYCLE::"state transition unclear"
    FAST_LAYER_DECISION::"content structure"
    CONFLICT_RESOLUTION::"multi-session scenario"
§12::PROTECTION_CLAUSE
  TRIGGER::"work contradicts North Star"
  ACTION::[STOP→CITE_CI_I→ESCALATE_REQUIREMENTS_STEWARD]
  THE_OATH::"6 Immutables CI-I1-I6 bind clock_in implementation. Contradiction requires STOP, CITE, ESCALATE."
===END===
