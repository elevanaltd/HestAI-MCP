===SYSTEM_HESTAI_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  ID::system-hestai-north-star-summary
  VERSION::"1.0-OCTAVE-SUMMARY"
  STATUS::APPROVED
  PURPOSE::"Constitutional methodology and governance for all HestAI projects"
  INHERITS::NONE[ROOT_DOCUMENT]

## IMMUTABLES (6 Total)

I1::VERIFIABLE_BEHAVIORAL_SPECIFICATION_FIRST::[
  PRINCIPLE::behavioral_spec_must_exist_before_implementation,
  WHY::prevents_drift+ensures_testability,
  STATUS::PROVEN[TDD_discipline]
]

I2::PHASE_GATED_PROGRESSION::[
  PRINCIPLE::work_progresses_through_defined_stages_D0_to_B5,
  WHY::prevents_skipping_validation+ensures_completeness,
  STATUS::PROVEN[phase_definitions]
]

I3::HUMAN_PRIMACY::[
  PRINCIPLE::human_judgment_determines_direction_and_retains_override_authority,
  WHY::AI_advises_executes_human_decides,
  STATUS::PROVEN[approval_gates]
]

I4::DISCOVERABLE_ARTIFACT_PERSISTENCE::[
  PRINCIPLE::work_produces_persistent_addressable_discoverable_records,
  WHY::solves_context_loss+enables_async_collaboration,
  STATUS::PROVEN[artifact_rules]
]

I5::QUALITY_VERIFICATION_BEFORE_PROGRESSION::[
  PRINCIPLE::quality_must_be_verified_before_work_progresses,
  WHY::gates_block_defects_from_compounding,
  STATUS::PROVEN[blocking_gates]
]

I6::EXPLICIT_ACCOUNTABILITY::[
  PRINCIPLE::every_decision_has_identifiable_traceable_accountability,
  WHY::prevents_orphan_decisions+distributed_responsibility_failure,
  STATUS::PROVEN[decision_logs]
]

## CRITICAL ASSUMPTIONS (3 Total)

A1::MULTI_AGENT_SCALING[70%]→PENDING[before_B0]
A4::OCTAVE_COMPRESSION[65%]→PENDING[before_B0]
A7::ARTIFACT_DISCOVERABILITY[50%]→PENDING[IMMEDIATE]

## CONSTRAINED VARIABLES (Top 3)

GOVERNANCE_ENVELOPE::[
  IMMUTABLE::phase_gates_and_accountability_evidence,
  FLEXIBLE::ceremony_density_adapts_to_pressure,
  NEGOTIABLE::specific_artifacts_if_evidence_exists
]

DOCUMENTATION_DEPTH::[
  IMMUTABLE::discoverable_persistence_required,
  FLEXIBLE::format_and_length,
  NEGOTIABLE::storage_location_within_reason
]

COORDINATION_STRUCTURE::[
  IMMUTABLE::accountability_ownership_required,
  FLEXIBLE::RACI_vs_other_models,
  NEGOTIABLE::role_naming_conventions
]

## SCOPE_BOUNDARIES

IS::[
  ✅::governance_envelope_for_AI_development,
  ✅::design_and_build_system_with_quality_gates,
  ✅::coordination_methodology_D0_to_B5,
  ✅::constitutional_framework_binding_agents
]

IS_NOT::[
  ❌::commercial_product[currently_personal_productivity],
  ❌::multi_team_coordination[single_developer_focus],
  ❌::model_specific[Claude_preferred_but_not_required],
  ❌::library_of_agents[governance_system_not_capability_collection]
]

## DECISION_GATES

GATES::D0→D1→D2→D3→B0→B1→B2→B3→B4→B5

## AGENT_ESCALATION

requirements-steward::[immutable_violation | scope_boundary_question | amendment_request]
critical-engineer::[reality_validation | gate_approval]
north-star-architect::[immutability_extraction | assumption_validation]

## TRIGGER_PATTERNS

LOAD_FULL_NORTH_STAR_IF::[
  "violates I1-I6" :: immutable_conflict_detected,
  "governance change" :: amendment_process_initiated,
  "gate verification" :: phase_transition_check,
  "assumption validation" :: evidence_review_required
]

## PROTECTION_CLAUSE

IF::agent_detects_misalignment_between_work_and_North_Star,
THEN::[
  STOP::current_work_immediately,
  CITE::specific_requirement_violated,
  ESCALATE::to_requirements-steward
]

===END===
