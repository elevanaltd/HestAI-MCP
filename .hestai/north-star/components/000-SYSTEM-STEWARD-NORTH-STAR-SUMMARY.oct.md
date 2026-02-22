===SYSTEM_STEWARD_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"1.2-OCTAVE-SUMMARY"
  STATUS::ACTIVE
  PURPOSE::"Operational decision-logic for System Steward subsystem"
  FULL_DOC::".hestai/workflow/components/000-SYSTEM-STEWARD-NORTH-STAR.md"
  INHERITS::[System_NS,Product_NS]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS::6[meets_PROPHETIC_VIGILANCE]

SECTION_ORDER::[S1::IMMUTABLES,S2::ASSUMPTIONS,S3::VARIABLES,S4::SCOPE,S5::GATES,S6::ARCHITECTURE,S7::CHILDREN,S8::DEPENDENCIES,S9::ESCALATION,S10::TRIGGERS,S11::PROTECTION]

S1::IMMUTABLES[6_Total]

SS-I1::DUAL_CONTROL_PLANE_SEPARATION::[
  PRINCIPLE::AI_orchestration_and_OCTAVE_validation_are_separate_control_planes,
  WHY::deterministic_document_ops_cannot_depend_on_probabilistic_AI,
  STATUS::PENDING[implementation-lead@B1]
]

SS-I2::ASYNC_FIRST_ARCHITECTURE::[
  PRINCIPLE::all_provider_calls_and_MCP_invocations_must_be_async,
  WHY::blocking_degrades_entire_MCP_server_event_loop,
  STATUS::PENDING[implementation-lead@B1]
]

SS-I3::MCP_SERVER_CHAINING::[
  PRINCIPLE::HestAI-MCP_acts_as_both_server_and_client_with_namespaced_tools,
  WHY::enables_composition[OCTAVE+Memory+Git+Repomix],
  STATUS::PENDING[technical-architect@B1]
]

SS-I4::SINGLE_WRITER_PRESERVATION::[
  PRINCIPLE::only_System_Steward_MCP_tools_write_to_.hestai/,
  WHY::prevents_governance_drift+ensures_validated_atomic_mutations,
  STATUS::PENDING[implementation-lead@B1]
]

SS-I5::INTELLIGENCE_IN_PROMPTS_AND_MANIFESTS::[
  PRINCIPLE::AI_reasoning_in_versioned_prompts+manifests_not_opaque_runtime,
  WHY::codified_intelligence_is_auditable+testable+human_controllable,
  STATUS::PENDING[implementation-lead@B2]
]

SS-I6::GRACEFUL_DEGRADATION::[
  PRINCIPLE::if_AI_fails_fall_back_to_deterministic_behavior,
  WHY::reliability_critical_for_autonomous_systems[Product_I2],
  STATUS::PENDING[implementation-lead@B1]
]

S2::CRITICAL_ASSUMPTIONS[6_Total]

SS-A1::AI_CONTEXT_SELECTION[80%|High]->PENDING[implementation-lead@B1]
SS-A2::OCTAVE_MCP_ASYNC[90%|High]->PENDING[implementation-lead@B1]
SS-A3::MANIFEST_FILTERING[75%|Medium]->PENDING[implementation-lead@B2]
SS-A4::PROVIDER_FALLBACK_CHAIN[85%|High]->PENDING[technical-architect@B1]
SS-A5::MCP_CHAINING_MANAGEABLE[75%|High]->PENDING[technical-architect@B1]
SS-A6::MANIFEST_SCHEMA_COVERAGE[70%|Medium]->PENDING[implementation-lead@B2]

S3::CONSTRAINED_VARIABLES[Top_5]

AI_PROVIDER::[IMMUTABLE::must_use_async[SS-I2],FLEXIBLE::OpenRouter|OpenAI|Anthropic|local]
CONTROL_PLANES::[IMMUTABLE::separate[SS-I1],FLEXIBLE::which_tools_in_each]
MANIFEST_SCHEMA::[IMMUTABLE::must_exist[SS-I5],FLEXIBLE::schema_evolution]
UPSTREAM_MCP::[IMMUTABLE::namespaced[SS-I3],FLEXIBLE::which_servers]
CONTEXT_SELECTION::[IMMUTABLE::AI_preferred,FLEXIBLE::deterministic_fallback_acceptable]

S4::SCOPE_BOUNDARIES

IS::[
  AI-powered_context_orchestration,
  MCP_tool_execution_and_handling,
  OCTAVE_validation_routing,
  context_selection_and_synthesis,
  provider_fallback_management
]

IS_NOT::[
  direct_file_writes[octave_create_responsibility],
  identity_validation[odyssean_anchor_responsibility],
  session_management[clock_in/clock_out_responsibility],
  persistent_memory[Basic_Memory_MCP],
  git_operations[Git_MCP],
  codebase_packaging[Repomix_MCP]
]

S5::DECISION_GATES

GATES::D1[DONE]->B0[PENDING]->B1[PENDING]->B2[PENDING]->B3[PENDING]

S6::ARCHITECTURE_SUMMARY

LIVING_LENS_METAPHOR::[
  ORCHESTRA_MAP::BRAIN[relevance_graph],
  REPOMIX::RETINA[code_capture],
  OCTAVE::OPTIC_NERVE[validation+compression],
  AI_CLIENT::CORTEX[interpretation]
]

DUAL_CONTROL_PLANE::[
  AGENTIC::HestAI_MCP[clock_in+clock_out+context_update+document_submit],
  DOCUMENT::OCTAVE_MCP[octave_ingest+octave_create+octave_amend+octave_eject]
]

MVP_SEQUENCE::[
  Query_Orchestra_Map->Invoke_Repomix_MCP->Call_AIClient->Validate_octave_ingest->Write_octave_create
]

S7::CHILD_COMPONENTS

TOOLS::[
  clock_in::session_registration+context_synthesis[000-CLOCK-IN-NORTH-STAR.md],
  clock_out::session_archival+transcript_compression[TBD],
  odyssean_anchor::identity_validation+binding_ceremony[000-ODYSSEAN-ANCHOR-NORTH-STAR.md],
  context_update::mid-session_context_mutation[TBD],
  document_submit::document_routing+placement[TBD]
]

S8::DEPENDENCIES

BLOCKING::[]
RELATED::[#56,#87,#96,#102]|[ADR-0033,ADR-0035,ADR-0036,ADR-0046]

S9::AGENT_ESCALATION

requirements-steward::[violates_SS-I#,scope_question,NS_amendment]
technical-architect::[architecture_decisions,MCP_chaining_design]
implementation-lead::[assumption_validation,build_execution]

S10::TRIGGER_PATTERNS

LOAD_FULL_NORTH_STAR_IF::[
  "violates SS-I1-I6"::immutable_conflict,
  "control plane decision"::architecture_question,
  "MCP chaining design"::integration_pattern,
  "AI fallback policy"::degradation_strategy
]

S11::PROTECTION_CLAUSE

IF::work_contradicts_North_Star->STOP->CITE[SS-I#]->ESCALATE[requirements-steward]

THE_OATH::"6 Immutables (SS-I1-I6) bind System Steward implementation. Contradiction requires STOP, CITE, ESCALATE."

===END===
