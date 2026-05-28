===MCP_PRODUCT_NORTH_STAR_SUMMARY===
META:
  TYPE::NORTH_STAR_SUMMARY
  ID::mcp-product-north-star-summary
  VERSION::"2.0-UPOG"
  STATUS::ACTIVE
  NAMESPACE::PROD
  PURPOSE::"Operational decision-logic for HestAI-MCP product development"
  INHERITS::".hestai-sys/standards/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md"
  CONTRACT::HOLOGRAPHIC<parse_only_governance>
  CANONICAL::".hestai/north-star/000-MCP-PRODUCT-NORTH-STAR-SUMMARY.oct.md"
  SOURCE::".hestai/north-star/000-MCP-PRODUCT-NORTH-STAR-SUMMARY.oct.md"
§1::IMMUTABLES
  COUNT::6
  I1<PERSISTENT_COGNITIVE_CONTINUITY>:
    PRINCIPLE::"system must persist context, decisions, learnings across sessions"
    WHY::"prevents costly re-learning — amnesia is system failure"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  I2<STRUCTURAL_INTEGRITY_PRIORITY>:
    PRINCIPLE::"correctness and compliance take precedence over velocity"
    WHY::"reliability is critical for autonomous systems"
    STATUS::PROVEN
    EVIDENCE::architectural_mandate
  I3<DUAL_LAYER_AUTHORITY>:
    PRINCIPLE::"strict separation between read-only governance and mutable context"
    WHY::"prevents governance drift and agent rule rewriting"
    STATUS::PROVEN
    EVIDENCE::ADR-0001
  I4<FRESHNESS_VERIFICATION>:
    PRINCIPLE::"context must be verified as current before use"
    WHY::"prevents hallucinations from stale data"
    STATUS::PENDING
    GATE::B1_freshness_check
  I5<ODYSSEAN_IDENTITY_BINDING>:
    PRINCIPLE::"agents must undergo structural identity verification to operate"
    WHY::"prevents generic drift and enforces role constraints"
    STATUS::PENDING
    GATE::bind_command
  I6<UNIVERSAL_SCOPE>:
    PRINCIPLE::"system must function on any repository structure"
    WHY::"ensures broad adoption and handles legacy diversity"
    STATUS::PENDING
    GATE::multi_repo_testing
§2::CRITICAL_ASSUMPTIONS
  COUNT::2
  A4<OCTAVE_READABILITY>:
    CONFIDENCE::"85%"
    OWNER::AI-Lead
    GATE::B1
    STATUS::PENDING
  A6<RAPH_EFFICACY>:
    CONFIDENCE::"70%"
    OWNER::AI-Lead
    GATE::B1
    STATUS::PENDING
§3::CONSTRAINED_VARIABLES
  WORKFLOW_LATENCY:
    IMMUTABLE::"integrity checks cannot be skipped for speed"
    FLEXIBLE::"startup latency up to 2m acceptable"
    NEGOTIABLE::specific_optimization_targets
  TECHNOLOGY_SUBSTRATE:
    IMMUTABLE::Git_as_coordination_substrate
    FLEXIBLE::"MCP or other agent protocols"
    NEGOTIABLE::specific_CLI_implementations
  STORAGE_MODEL:
    IMMUTABLE::persistent_memory_guarantee
    FLEXIBLE::local_first_preferred_but_not_mandatory
    NEGOTIABLE::"storage_format<JSONL∨OCTAVE>"
§4::SCOPE_BOUNDARIES
  IS::[
    persistent_memory_system,
    structural_governance_engine,
    orchestra_conductor_ambient_awareness,
    dual_layer_context_protocol
  ]
  IS_NOT::[
    SaaS_product_local_first_primary,
    grab_bag_tool_library_coherent_system,
    monorepo_exclusive,
    AI_model_context_provider_only
  ]
§5::DECISION_GATES
  GATES::[D0_DONE→B0_DONE→B1_IN_PROGRESS→B2_PENDING→B3_PENDING→B4_PENDING→B5_PENDING]
§6::AGENT_ESCALATION
  requirements_steward::[
    immutable_violation,
    scope_question,
    NS_amendment
  ]
  technical_architect::[architecture_decisions,integration_design]
  implementation_lead::[assumption_validation,build_execution]
§7::TRIGGER_PATTERNS
  LOAD_FULL_NORTH_STAR_IF:
    IMMUTABLE_CONFLICT::"violates I1-I6"
    SCOPE_QUESTION::"scope boundary"
    DECISION_GATE::"B1-B5 gate"
    ASSUMPTION_VALIDATION::"assumption A#"
§8::PROTECTION_CLAUSE
  TRIGGER::"agent detects work contradicting North Star"
  ACTION::[STOP_CURRENT_WORK→CITE_VIOLATED_IMMUTABLE→ESCALATE_TO_REQUIREMENTS_STEWARD]
===END===
