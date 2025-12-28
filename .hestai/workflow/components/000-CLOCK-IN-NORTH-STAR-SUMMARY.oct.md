===CLOCK_IN_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  ID::clock-in-north-star-summary
  VERSION::"1.1-OCTAVE-SUMMARY"
  STATUS::ACTIVE
  PURPOSE::"Operational decision-logic for clock_in MCP tool implementation"
  INHERITS::[
    "hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md",
    ".hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md",
    ".hestai/workflow/components/000-SYSTEM-STEWARD-NORTH-STAR.md"
  ]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"

§1::IMMUTABLES

CI-I1::SESSION_REGISTRATION_MANDATORY::[
  PRINCIPLE::every_agent_session_begins_with_clock_in,
  BECAUSE::enables_audit_trails⊕conflict_detection⊕cognitive_continuity,
  VALIDATION::clock_in_returns_session_id→all_tool_calls_reference_it,
  STATUS::PENDING[implementation-lead@B1]
]

CI-I2::CONTEXT_MUST_BE_FRESH::[
  PRINCIPLE::generate_fresh_state_on_every_invocation,
  BECAUSE::prevents_hallucinations_from_stale_data[Product_I4],
  VALIDATION::staleness_>24h→BLOCKS[not_warns],
  STATUS::PENDING[implementation-lead@B1]
]

CI-I3::AI_ASSISTED_CONTEXT_SELECTION::[
  PRINCIPLE::AI_selects⊕synthesizes_context_by_role⊕focus,
  BECAUSE::agents_need_curated_context[Issue_#87_SISYPHEAN_blindness],
  CRITERIA::[role_affinity,focus_relevance,recency,ADR_constraints],
  FALLBACK::deterministic_file_list[SS-I6],
  STATUS::PENDING[implementation-lead@B1]
]

CI-I4::FAST_LAYER_LIFECYCLE::[
  PRINCIPLE::clock_in_updates_.hestai/context/state/_with_session_context,
  BECAUSE::agents_need_current_focus⊕blockers⊕checklist[ADR-0056],
  FILES::[current-focus.oct.md,checklist.oct.md,blockers.oct.md],
  STATUS::PENDING[implementation-lead@B1]
]

CI-I5::FOCUS_CONFLICT_DETECTION::[
  PRINCIPLE::detect_active_session_in_same_worktree,
  BECAUSE::prevents_concurrent_agents_overwriting_context,
  RESOLUTION::[continue,abort,take_over[mark_existing_STALE]],
  STATUS::PENDING[implementation-lead@B1]
]

CI-I6::TDD_DISCIPLINE_ENFORCEMENT::[
  PRINCIPLE::RED→GREEN→REFACTOR_discipline_required,
  BECAUSE::System_North_Star_I1[Verifiable_Behavioral_Specification_First],
  VALIDATION::git_history_shows_test-first_evidence,
  STATUS::PENDING[implementation-lead@B1]
]

§2::CRITICAL_ASSUMPTIONS

CI-A1::AI_CONTEXT_SYNTHESIS[80%]→PENDING[POC_with_real_sessions]
CI-A2::GITHUB_ISSUE_SEARCH[85%]→PENDING[test_with_Issue_#56]
CI-A3::CLEANUP_POLICY_SUFFICIENT[90%]→PENDING[monitor_disk_usage]
CI-A4::WORKSPACE_CONFIG_COVERAGE[75%]→PENDING[user_feedback]
CI-A5::CONFLICT_DETECTION_PREVENTS_COLLISION[95%]→PENDING[unit_tests]

§3::CONSTRAINED_VARIABLES

CONTEXT_SOURCES::[
  IMMUTABLE::must_gather_comprehensive_context[CI-I3],
  FLEXIBLE::which_tools_used[Repomix,Dependency_Cruiser,etc]
]

FOCUS_RESOLUTION::[
  IMMUTABLE::must_resolve_from_somewhere,
  PRIORITY::explicit_arg→GitHub_issue→branch_name→"general"
]

AI_MODEL::[
  IMMUTABLE::must_use_async[SS-I2],
  FLEXIBLE::configurable_via_~/.hestai/config/ai.json
]

AI_PROMPTS::[
  IMMUTABLE::must_be_versioned⊕auditable[SS-I5],
  FLEXIBLE::prompt_text_content
]

§4::INPUT_OUTPUT_CONTRACT

INPUT::[
  role::string[REQUIRED]::agent_role,
  focus::string[OPTIONAL]::work_focus_defaults_to_general,
  working_dir::string[REQUIRED]::absolute_path_to_project_root,
  model::string[OPTIONAL]::AI_model_override
]

OUTPUT::[
  session_id::uuid-v4,
  context_paths::{{
    project_context::.hestai/context/PROJECT-CONTEXT.oct.md,
    current_state::.hestai/context/state/current-state.oct.md,
    checklist::.hestai/context/state/checklist.oct.md,
    blockers::.hestai/context/state/blockers.oct.md,
    current_focus::.hestai/context/state/current-focus.oct.md,
    negatives::.hestai/context/CONTEXT-NEGATIVES.oct.md
  }},
  conflict::null_or_existing_session_info,
  focus_resolved::{{value,source}},
  github_context::{{related_issues,active_pr}},
  instruction::"Read context_paths. Produce Full RAPH. Submit anchor."
]

§5::EXECUTION_SEQUENCE

CLOCK_IN_SEQUENCE::[
  STEP_1::VALIDATE_INPUT→validated_params,
  STEP_2::DETECT_FOCUS_CONFLICT→conflict_status,
  STEP_3::CREATE_SESSION→session_id⊕session_dir,
  STEP_4::RESOLVE_FOCUS→resolved_focus,
  STEP_5::GATHER_CONTEXT[AI_ASSISTED]→gathered_context[FALLBACK::deterministic_file_list],
  STEP_6::SYNTHESIZE_FAST_LAYER[AI_ASSISTED]→fast_layer_content[FALLBACK::template_minimal],
  STEP_7::WRITE_FAST_LAYER→written_files[octave_ingest→octave_create],
  STEP_8::RESOLVE_CONTEXT_PATHS→context_paths,
  STEP_9::RETURN_RESPONSE→ClockInResponse
]

§6::SESSION_LIFECYCLE

STATES::[
  CREATED::clock_in_called→session.json_written,
  ACTIVE::agent_working→may_update_FAST_layer,
  COMPLETED::clock_out_called→archived_to_OCTAVE,
  STALE::no_activity_72h→eligible_for_cleanup,
  ARCHIVED::in_.hestai/sessions/archive/→retained_30_days
]

CLEANUP_POLICY::[
  inactive_>72h→mark_STALE→block_until_resolved,
  stale_on_clock_in→offer_cleanup_or_continue,
  archive_>30d→delete
]

HUMAN_AUTHORITY::cleanup_thresholds_configurable_via_.hestai_workspace.yaml

§7::BINDING_CEREMONY_POSITION

ODYSSEAN_ANCHOR_SEQUENCE::[
  STEP_1::READ_PROMPT→agent_loads_constitution,
  STEP_2::CLOCK_IN→[THIS_TOOL]session_registered⊕context_paths_returned,
  STEP_3::READ_CONTEXT→agent_reads_git_state⊕project_context,
  STEP_4::ODYSSEAN_ANCHOR→agent_submits_identity_proof,
  STEP_5::DASHBOARD→agent_shows_validated_binding
]

§8::DEPENDENCIES

BLOCKING::[
  AIClient_async::SS-I2,
  MCP_client_manager::SS-I3,
  OCTAVE_MCP::SS-I1
]

REQUIRED::[Git]
FALLBACK_AVAILABLE::[AIClient,OCTAVE_MCP,GitHub_CLI,Repomix]

RELATED_ISSUES::[#56,#87,#96,#102,#35,#36]
RELATED_ADRS::[ADR-0033,ADR-0035,ADR-0036,ADR-0046,ADR-0056]

§9::IMPLEMENTATION_PHASES

PHASE_1_MVP::[
  session_creation_with_UUID,
  focus_conflict_detection,
  context_path_resolution,
  basic_FAST_layer_update[template-based],
  GitHub_issue_search_for_focus,
  deterministic_fallback_for_AI_operations
]

PHASE_2_AI_ENHANCEMENT::[
  AI-powered_context_selection,
  AI-powered_FAST_layer_synthesis,
  Repomix_integration,
  workspace_configuration_support
]

PHASE_3_ADVANCED::[
  session_cleanup_automation,
  quality_gate_status_inclusion,
  ADR_constraint_extraction,
  Orchestra_Map_awareness
]

§10::AGENT_ESCALATION

requirements-steward::[violates_CI-I#,scope_question,NS_amendment]
technical-architect::[architecture_decisions,integration_design]
implementation-lead::[assumption_validation,build_execution]

§11::TRIGGER_PATTERNS

LOAD_FULL_NORTH_STAR_IF::[
  "violates CI-I1-I6"::immutable_conflict_detected,
  "session lifecycle question"::state_transition_unclear,
  "FAST layer decision"::content_structure_question,
  "conflict resolution"::multi-session_scenario
]

§12::PROTECTION_CLAUSE

IF::agent_detects_work_contradicting_North_Star,
THEN::[
  STOP::current_work_immediately,
  CITE::specific_requirement_violated[CI-I#],
  ESCALATE::to_requirements-steward
]

THE_OATH::"These 6 Immutables (CI-I1 through CI-I6) are the binding requirements for clock_in implementation. Any contradiction requires STOP, CITE, ESCALATE."

===END===
