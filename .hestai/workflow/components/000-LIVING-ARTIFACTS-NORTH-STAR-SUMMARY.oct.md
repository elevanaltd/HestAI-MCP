===LIVING_ARTIFACTS_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"1.2-OCTAVE-SUMMARY"
  STATUS::ACTIVE
  PURPOSE::"Operational decision-logic for Living Artifacts pattern"
  FULL_DOC::".hestai/workflow/components/000-LIVING-ARTIFACTS-NORTH-STAR.md"
  INHERITS::[System_NS,Product_NS]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS::6[meets_PROPHETIC_VIGILANCE]

SECTION_ORDER::[S1::IMMUTABLES,S2::ASSUMPTIONS,S3::VARIABLES,S4::SCOPE,S5::GATES,S6::ARTIFACT_PATTERN,S7::DEPENDENCIES,S8::ESCALATION,S9::TRIGGERS,S10::PROTECTION]

S1::IMMUTABLES[5_Total]

LA-I1::SPLIT_ARTIFACT_AUTHORITY::[
  PRINCIPLE::strict_separation_between_Audit_Trail_and_Operational_State,
  WHY::log_and_state_have_distinct_update_cycles+truth_sources,
  STATUS::PENDING[implementation-lead@B1]
]

LA-I2::QUERY_DRIVEN_FRESHNESS::[
  PRINCIPLE::operational_state_generated_at_runtime_not_from_stale_files,
  WHY::stored_state_rots[generated_state_is_environmental_truth],
  STATUS::PENDING[implementation-lead@B1]
]

LA-I3::SINGLE_BRANCH_CI_WRITES::[
  PRINCIPLE::CI_processes_ONLY_write_to_branch_they_run_on,
  WHY::cross-branch_writes_introduce_race_conditions+merge_conflicts,
  STATUS::PENDING[implementation-lead@B1]
]

LA-I4::BLOCKING_STALENESS::[
  PRINCIPLE::stale_context_artifacts_must_block_or_flag_AT_RISK,
  WHY::bad_data_worse_than_no_data[Product_I4],
  STATUS::PENDING[implementation-lead@B1]
]

LA-I5::PERSISTENT_AUDIT_TRACE::[
  PRINCIPLE::every_significant_change_leaves_permanent_trace_in_Audit_Trail,
  WHY::automated_state_is_ephemeral[need_permanent_evolution_history],
  STATUS::PENDING[implementation-lead@B1]
]

S2::CRITICAL_ASSUMPTIONS[6_Total]

LA-A1::RUNTIME_GENERATION_FAST[85%|High]->PENDING[implementation-lead@B2]
LA-A2::CHANGELOG_FORMAT_PARSEABLE[80%|Medium]->PENDING[implementation-lead@B1]
LA-A3::GIT_LOGS_SUFFICIENT[70%|High]->PENDING[implementation-lead@B1]
LA-A4::CHANGELOG_MERGE_SAFE[80%|Medium]->PENDING[implementation-lead@B2]
LA-A5::STALENESS_THRESHOLD_APPROPRIATE[75%|Medium]->PENDING[implementation-lead@B2]
LA-A6::GIT_LOGS_METADATA_SUFFICIENT[70%|High]->PENDING[implementation-lead@B1]

S3::CONSTRAINED_VARIABLES[Top_3]

STATE_SOURCE::[IMMUTABLE::environment_query[LA-I2],FLEXIBLE::specific_queries_run]
AUDIT_LOCATION::[IMMUTABLE::in-repo_file[LA-I5],FLEXIBLE::file_name+path]
STALENESS_THRESHOLD::[IMMUTABLE::must_exist[LA-I4],FLEXIBLE::duration[24h_vs_12h]]

S4::SCOPE_BOUNDARIES

IS::[
  audit_trail_maintenance[CHANGELOG],
  operational_state_generation[JIT_current_state.oct],
  query-driven_freshness[runtime_generation],
  staleness_detection_and_blocking[pre-commit_hooks],
  CI_integration[automated_CHANGELOG_entries]
]

IS_NOT::[
  context_file_writing[OCTAVE_MCP_responsibility],
  session_management[clock_in/clock_out_responsibility],
  identity_validation[odyssean_anchor_responsibility],
  manual_documentation[human_activity],
  schema_enforcement[OCTAVE_parser_responsibility],
  context_selection[System_Steward_responsibility]
]

S5::DECISION_GATES

GATES::D1[DONE]->B0[PENDING]->B1[PENDING]->B2[PENDING]->B3[PENDING]

S6::ARTIFACT_PATTERN

SPLIT_ARTIFACT::[
  AUDIT_TRAIL::CHANGELOG.md[immutable_history],
  OPERATIONAL_STATE::current_state.oct[JIT_snapshot]
]

FRESHNESS_RULES::[
  clock_in::executes_generation_logic[git_query+test_count],
  staleness::threshold_based[configurable],
  blocking::pre-commit_hooks_or_tool_guards
]

CI_PATTERN::[
  WRITES_TO::HEAD[current_branch_only],
  NEVER::cross-branch_writes[no_orphan_magic],
  APPENDS::CHANGELOG.md_on_merge
]

S7::DEPENDENCIES

BLOCKING::[]
RELATED::[#35]|[ADR-0035]

S8::AGENT_ESCALATION

requirements-steward::[violates_LA-I#,scope_question,NS_amendment]
technical-architect::[architecture_decisions,CI_integration_design]
implementation-lead::[assumption_validation,build_execution]

S9::TRIGGER_PATTERNS

LOAD_FULL_NORTH_STAR_IF::[
  "violates LA-I1-I5"::immutable_conflict,
  "audit vs state"::split_artifact_question,
  "staleness policy"::threshold_decision,
  "CI write pattern"::branch_strategy
]

S10::PROTECTION_CLAUSE

IF::work_contradicts_North_Star->STOP->CITE[LA-I#]->ESCALATE[requirements-steward]

THE_OATH::"5 Immutables (LA-I1-I5) bind Living Artifacts implementation. Contradiction requires STOP, CITE, ESCALATE."

===END===
