===SYSTEM_HESTAI_NORTH_STAR_SUMMARY===
META:
  TYPE::NORTH_STAR_SUMMARY
  ID::system-hestai-north-star-summary
  VERSION::"2.0-UPOG"
  STATUS::APPROVED
  NAMESPACE::SYS
  PURPOSE::"Operating discipline and standards for all HestAI projects"
  INHERITS::NONE_ROOT_DOCUMENT
  FULL_DOC::".hestai-sys/standards/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md"
  SOURCE_FULL_DOC::"src/hestai_mcp/_bundled_hub/standards/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md"
  CONTRACT::HOLOGRAPHIC<parse_only_governance>
  CANONICAL::".hestai-sys/standards/workflow/000-SYSTEM-HESTAI-NORTH-STAR-SUMMARY.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/standards/workflow/000-SYSTEM-HESTAI-NORTH-STAR-SUMMARY.oct.md"
§1::IMMUTABLES
  COUNT::6
  I1<VERIFIABLE_BEHAVIORAL_SPECIFICATION_FIRST>:
    PRINCIPLE::"behavioral spec must exist before implementation"
    WHY::"prevents drift and ensures testability"
    STATUS::PROVEN
    EVIDENCE::TDD_discipline
  I2<PHASE_GATED_PROGRESSION>:
    PRINCIPLE::"work progresses through defined stages D0 to B5"
    WHY::"prevents skipping validation and ensures completeness"
    STATUS::PROVEN
    EVIDENCE::phase_definitions
  I3<HUMAN_PRIMACY>:
    PRINCIPLE::"human judgment determines direction and retains override authority"
    WHY::"AI advises and executes, human decides"
    STATUS::PROVEN
    EVIDENCE::approval_gates
  I4<DISCOVERABLE_ARTIFACT_PERSISTENCE>:
    PRINCIPLE::"work produces persistent addressable discoverable records"
    WHY::"solves context loss and enables async collaboration"
    STATUS::PROVEN
    EVIDENCE::artifact_rules
  I5<QUALITY_VERIFICATION_BEFORE_PROGRESSION>:
    PRINCIPLE::"quality must be verified before work progresses"
    WHY::"gates block defects from compounding"
    STATUS::PROVEN
    EVIDENCE::blocking_gates
  I6<EXPLICIT_ACCOUNTABILITY>:
    PRINCIPLE::"every decision has identifiable traceable accountability"
    WHY::"prevents orphan decisions and distributed responsibility failure"
    STATUS::PROVEN
    EVIDENCE::decision_logs
§2::CRITICAL_ASSUMPTIONS
  COUNT::3
  A1<MULTI_AGENT_SCALING>:
    CONFIDENCE::"70%"
    STATUS::PENDING
    GATE::before_B0
  A4<OCTAVE_COMPRESSION>:
    CONFIDENCE::"95%"
    STATUS::RESOLVED
    EVIDENCE::proven_in_B1
  A7<ARTIFACT_DISCOVERABILITY>:
    CONFIDENCE::"90%"
    STATUS::RESOLVED
    EVIDENCE::[ADR-0001,ADR-0003]
§3::CONSTRAINED_VARIABLES
  GOVERNANCE_ENVELOPE:
    IMMUTABLE::phase_gates_and_accountability_evidence
    FLEXIBLE::ceremony_density_adapts_to_pressure
    NEGOTIABLE::specific_artifacts_if_evidence_exists
  DOCUMENTATION_DEPTH:
    IMMUTABLE::discoverable_persistence_required
    FLEXIBLE::format_and_length
    NEGOTIABLE::storage_location_within_reason
  COORDINATION_STRUCTURE:
    IMMUTABLE::accountability_ownership_required
    FLEXIBLE::"RACI or other models"
    NEGOTIABLE::role_naming_conventions
§4::SCOPE_BOUNDARIES
  IS::[
    governance_envelope_for_AI_development,
    design_and_build_system_with_quality_gates,
    coordination_methodology_D0_to_B5,
    standards_framework_binding_agents
  ]
  IS_NOT::[
    commercial_product_currently_personal_productivity,
    multi_team_coordination_single_developer_focus,
    model_specific_Claude_preferred_but_not_required,
    library_of_agents_governance_system_not_capability_collection
  ]
§5::DECISION_GATES
  GATES::[D0→D1→D2→D3→B0→B1→B2→B3→B4→B5]
§6::AGENT_ESCALATION
  requirements_steward::[
    immutable_violation,
    scope_boundary_question,
    amendment_request
  ]
  critical_engineer::[reality_validation,gate_approval]
  north_star_architect::[immutability_extraction,assumption_validation]
§7::TRIGGER_PATTERNS
  LOAD_FULL_NORTH_STAR_IF:
    IMMUTABLE_CONFLICT::"violates I1-I6"
    GOVERNANCE_CHANGE::"amendment process initiated"
    GATE_VERIFICATION::"phase transition check"
    ASSUMPTION_VALIDATION::"evidence review required"
§8::PROTECTION_CLAUSE
  TRIGGER::"agent detects misalignment between work and North Star"
  ACTION::[STOP_CURRENT_WORK→CITE_SPECIFIC_REQUIREMENT_VIOLATED→ESCALATE_TO_REQUIREMENTS_STEWARD]
===END===
