===ODYSSEAN_ANCHOR_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"1.2-OCTAVE-SUMMARY"
  STATUS::ACTIVE
  PURPOSE::"Operational decision-logic for Odyssean Anchor MCP tool"
  FULL_DOC::".hestai/workflow/components/000-ODYSSEAN-ANCHOR-NORTH-STAR.md"
  INHERITS::[System_NS,Product_NS,System_Steward_NS]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS::6[meets_PROPHETIC_VIGILANCE]

SECTION_ORDER::[S1::IMMUTABLES,S2::ASSUMPTIONS,S3::VARIABLES,S4::SCOPE,S5::GATES,S6::RAPH_VECTOR,S7::BINDING_FLOW,S8::DEPENDENCIES,S9::ESCALATION,S10::TRIGGERS,S11::PROTECTION]

S1::IMMUTABLES[7_Total]

OA-I1::UNIFIED_BINDING_PATH::[
  PRINCIPLE::single_universal_protocol_for_ALL_agents[main+sub+tools],
  WHY::fragmentation_creates_security_holes_where_dumb_agents_bypass,
  STATUS::PENDING[implementation-lead@B1]
]

OA-I2::STRUCTURAL_VALIDATION::[
  PRINCIPLE::identity_is_RAPH_Vector_structure_not_string,
  WHY::text_identity_is_hallucinatable[structure_proves_cognition],
  STATUS::PENDING[implementation-lead@B1]
]

OA-I3::MANDATORY_SELF_CORRECTION::[
  PRINCIPLE::reject_invalid_anchors_with_guidance+force_retry,
  WHY::agents_hallucinate[must_force_think_again],
  STATUS::PENDING[implementation-lead@B1]
]

OA-I4::CONTEXTUAL_PROOF::[
  PRINCIPLE::ARM_must_contain_proof_of_environment_awareness,
  WHY::identity_without_context_is_dangerous_brain_in_jar,
  STATUS::PENDING[implementation-lead@B1]
]

OA-I5::AUTHORITY_INHERITANCE::[
  PRINCIPLE::sub-agents_must_cite_delegated_authority_from_parent,
  WHY::prevents_rogue_sub-agents_drifting_from_objective,
  STATUS::PENDING[implementation-lead@B2]
]

OA-I6::TOOL_GATING_ENFORCEMENT::[
  PRINCIPLE::work_tools_MUST_check_valid_anchor_before_executing,
  WHY::validation_without_enforcement_is_theater,
  STATUS::PENDING[implementation-lead@B1]
]

OA-I7::COGNITIVE_BINDING_PERSISTENCE::[
  PRINCIPLE::validated_vector_returned_to_conversation_context,
  WHY::file_output_alone_doesnt_create_working_memory_binding,
  STATUS::PENDING[implementation-lead@B1]
]

S2::CRITICAL_ASSUMPTIONS[6_Total]

OA-A1::SELF_CORRECTION_SUCCESS[75%|High]->PENDING[implementation-lead@B2]
OA-A2::BINDING_LATENCY_ACCEPTABLE[85%|Medium]->PENDING[implementation-lead@B2]
OA-A3::GIT_STATE_READABLE[90%|High]->PENDING[implementation-lead@B1]
OA-A4::TOOL_GATING_PERFORMANT[80%|High]->PENDING[implementation-lead@B1]
OA-A5::RAPH_SCHEMA_STABLE[75%|High]->PENDING[technical-architect@B1]
OA-A6::COGNITIVE_PERSISTENCE_CROSS_MODEL[70%|Medium]->PENDING[implementation-lead@B2]

S3::CONSTRAINED_VARIABLES[Top_3]

RAPH_SCHEMA::[IMMUTABLE::SHANK+ARM+FLUKE_structure[OA-I2],FLEXIBLE::field_names_can_evolve]
RETRY_LIMIT::[IMMUTABLE::must_exist[OA-I3],FLEXIBLE::count[currently_2]]
VALIDATION_STRICTNESS::[IMMUTABLE::must_validate_ARM+FLUKE[OA-I4,OA-I5],FLEXIBLE::Quick_vs_Deep_tiers]

S4::SCOPE_BOUNDARIES

IS::[
  agent_identity_validation[RAPH_Vector],
  RAPH_Vector_schema_enforcement,
  self-correction_protocol[reject+guidance+retry],
  contextual_proof_verification[ARM],
  authority_inheritance_tracking[FLUKE],
  tool_gating_enforcement[has_valid_anchor]
]

IS_NOT::[
  session_management[clock_in/clock_out_responsibility],
  context_synthesis[System_Steward_responsibility],
  file_writing[OCTAVE_MCP_responsibility],
  session_archival[clock_out_responsibility],
  context_selection[clock_in_responsibility],
  document_routing[document_submit_responsibility]
]

S5::DECISION_GATES

GATES::D1[DONE]->B0[BLOCKED:clock_in]->B1[PENDING]->B2[PENDING]->B3[PENDING]

S6::RAPH_VECTOR_STRUCTURE

RAPH_VECTOR::[
  SHANK::[ROLE,COGNITION,ARCHETYPES,CONSTRAINTS],
  ARM::[PHASE,BRANCH,FILES,BLOCKERS],
  FLUKE::[PARENT_SESSION,DELEGATED_TASK,SKILLS,AUTHORITY_LEVEL]
]

VALIDATION_RULES::[
  ARM_must_match_git_state,
  FLUKE_must_link_parent_or_task,
  SHANK_must_have_valid_role
]

S7::BINDING_FLOW

ODYSSEAN_SEQUENCE::[
  Agent_LOBBY->Read_constitution->CLOCK_IN[session_id]->Read_context->
  Construct_RAPH->ODYSSEAN_ANCHOR[validate]->
  ON_VALID::LOBBY->BOUND[tools_unlocked]|
  ON_REJECT::guidance->retry[max_2]|
  ON_FAIL::FAIL_HARD[no_bypass]
]

TOOL_GATING::[
  Agent_calls_work_tool->has_valid_anchor(session_id)->
  ON_YES::execute_tool|
  ON_NO::return_error_with_binding_instructions
]

S8::DEPENDENCIES

BLOCKING::[clock_in[provides_session_id]]
RELATED::[#102,#36]|[ADR-0036]

S9::AGENT_ESCALATION

requirements-steward::[violates_OA-I#,scope_question,NS_amendment]
technical-architect::[RAPH_schema_decisions,architecture]
implementation-lead::[assumption_validation,build_execution]

S10::TRIGGER_PATTERNS

LOAD_FULL_NORTH_STAR_IF::[
  "violates OA-I1-I7"::immutable_conflict,
  "RAPH schema question"::structure_unclear,
  "binding ceremony"::flow_decision,
  "tool gating design"::enforcement_pattern
]

S11::PROTECTION_CLAUSE

IF::work_contradicts_North_Star->STOP->CITE[OA-I#]->ESCALATE[requirements-steward]

THE_OATH::"7 Immutables (OA-I1-I7) bind Odyssean Anchor implementation. Contradiction requires STOP, CITE, ESCALATE."

===END===
