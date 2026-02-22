===MCP_PRODUCT_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  ID::mcp-product-north-star-summary
  VERSION::"1.0-OCTAVE-SUMMARY"
  STATUS::ACTIVE
  NAMESPACE::PROD
  PURPOSE::"Operational decision-logic for HestAI-MCP product development"
  INHERITS::".hestai-sys/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md"

## IMMUTABLES (6 Total)

I1::PERSISTENT_COGNITIVE_CONTINUITY::[
  PRINCIPLE::system_must_persist_context_decisions_learnings_across_sessions,
  WHY::prevents_costly_re-learning+amnesia_is_system_failure,
  STATUS::PENDING[implementation-lead@B1]
]

I2::STRUCTURAL_INTEGRITY_PRIORITY::[
  PRINCIPLE::correctness_and_compliance_take_precedence_over_velocity,
  WHY::reliability_is_critical_for_autonomous_systems,
  STATUS::PROVEN[architectural_mandate]
]

I3::DUAL_LAYER_AUTHORITY::[
  PRINCIPLE::strict_separation_between_read-only_governance_and_mutable_context,
  WHY::prevents_governance_drift+agent_rule_rewriting,
  STATUS::PROVEN[ADR-0001]
]

I4::FRESHNESS_VERIFICATION::[
  PRINCIPLE::context_must_be_verified_as_current_before_use,
  WHY::prevents_hallucinations_from_stale_data,
  STATUS::PENDING[B1_freshness_check]
]

I5::ODYSSEAN_IDENTITY_BINDING::[
  PRINCIPLE::agents_must_undergo_structural_identity_verification_to_operate,
  WHY::prevents_generic_drift+enforces_role_constraints,
  STATUS::PENDING[bind_command]
]

I6::UNIVERSAL_SCOPE::[
  PRINCIPLE::system_must_function_on_any_repository_structure,
  WHY::ensures_broad_adoption+handles_legacy_diversity,
  STATUS::PENDING[multi-repo_testing]
]

## CRITICAL ASSUMPTIONS (2 Total)

A4::OCTAVE_READABILITY[85%]→PENDING[AI-Lead@B1]
A6::RAPH_EFFICACY[70%]→PENDING[AI-Lead@B1]

## CONSTRAINED VARIABLES (Top 3)

WORKFLOW_LATENCY::[
  IMMUTABLE::integrity_checks_cannot_be_skipped_for_speed,
  FLEXIBLE::startup_latency_up_to_2m_acceptable,
  NEGOTIABLE::specific_optimization_targets
]

TECHNOLOGY_SUBSTRATE::[
  IMMUTABLE::Git_as_coordination_substrate,
  FLEXIBLE::MCP_vs_other_agent_protocols,
  NEGOTIABLE::specific_CLI_implementations
]

STORAGE_MODEL::[
  IMMUTABLE::persistent_memory_guarantee,
  FLEXIBLE::local-first_preferred_but_not_mandatory,
  NEGOTIABLE::storage_format[JSONL/OCTAVE]
]

## SCOPE_BOUNDARIES

IS::[
  ✅::persistent_memory_system,
  ✅::structural_governance_engine,
  ✅::orchestra_conductor_ambient_awareness,
  ✅::dual-layer_context_protocol
]

IS_NOT::[
  ❌::SaaS_product[local-first_primary],
  ❌::grab-bag_tool_library[coherent_system],
  ❌::monorepo-exclusive,
  ❌::AI_model[context_provider_only]
]

## DECISION_GATES

GATES::D0[DONE]→B0[DONE]→B1[IN_PROGRESS]→B2[PENDING]→B3[PENDING]→B4[PENDING]→B5[PENDING]

## AGENT_ESCALATION

requirements-steward::[violates_I# | scope_question | NS_amendment]
technical-architect::[architecture_decisions | integration_design]
implementation-lead::[assumption_validation | build_execution]

## TRIGGER_PATTERNS (Load Full North Star When...)

LOAD_FULL_NORTH_STAR_IF::[
  "violates I1-I6" :: immutable_conflict_detected,
  "scope boundary" :: is_this_in_scope_question,
  "B1-B5 gate" :: decision_gate_approaching,
  "assumption A#" :: validation_evidence_required
]

## PROTECTION_CLAUSE

IF::agent_detects_work_contradicting_North_Star,
THEN::[
  STOP::current_work_immediately,
  CITE::specific_requirement_violated[I#],
  ESCALATE::to_requirements-steward
]

===END===
