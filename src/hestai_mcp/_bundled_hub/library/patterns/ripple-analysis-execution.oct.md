===RIPPLE_ANALYSIS_EXECUTION===
META:
  TYPE::PATTERN_DEFINITION
  VERSION::"1.0"
  PURPOSE::"Pre-modification dependency mapping, impact classification, and modification order for safe file changes"
  CANONICAL::".hestai-sys/library/patterns/ripple-analysis-execution.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/patterns/ripple-analysis-execution.oct.md"
§1::CORE_PRINCIPLE
ESSENTIAL::"Every file change has a ripple radius. Map the waves before you throw the stone."
ANTI_PATTERN::"unanalyzed_modification[change_interface_without_consumer_audit→cascade_failures]"
ENFORCEMENT::"Execute full analysis sequence BEFORE writing any implementation code"
§2::EXECUTION_SEQUENCE
ANALYSIS_SEQUENCE::[
  1::IDENTIFY_TARGET<which_files_or_interfaces_will_change>,
  2::"TRACE_CONSUMERS<grep_imports⊕check_barrel_exports⊕check_type_refs⊕check_config_refs⊕check_test_files>",
  3::TRACE_DEPENDENCIES<what_does_target_import_or_depend_on>,
  4::MAP_RADIUS<count_affected_files_and_modules>,
  5::"CLASSIFY_IMPACT<BREAKING∨COMPATIBLE∨INTERNAL>",
  6::"PLAN_ORDER<leaves_first→root_last>"
]
IMPACT_CLASSIFICATION::[
  BREAKING::signature_change∨removed_export∨renamed_type∨changed_return_type→audit_every_consumer,
  COMPATIBLE::added_optional_param∨new_export∨extended_interface→verify_spread_operators_and_length_checks,
  INTERNAL::implementation_change_same_interface→only_tests_affected
]
MODIFICATION_ORDER::[
  RULE::"Fix leaves of dependency tree first, work toward root",
  RATIONALE::"Modifying root first creates cascading broken imports across all consumers"
]
ORDER_SEQUENCE::[
  step_1::update_type_definitions_and_interfaces,
  step_2::update_implementation_files,
  step_3::update_consumers_of_changed_interfaces,
  step_4::update_tests_last
]
THRESHOLDS::[
  radius_gt_5_files::document_analysis_explicitly,
  radius_gt_10_files::consider_phased_implementation,
  breaking_interface_change::audit_every_consumer,
  radius_gt_15_or_cross_module_breaking::"escalate<critical-engineer>"
]
ANALYSIS_OUTPUT::[
  TARGET::"{file_or_interface_changing}",
  CONSUMERS::"[{importing_files}]",
  DEPENDENCIES::"[{files_target_imports}]",
  RADIUS::"{N}_files_across_{M}_modules",
  IMPACT::BREAKING∨COMPATIBLE∨INTERNAL,
  ORDER::"[{modification_sequence_leaves_first}]"
]
§3::ANTI_PATTERNS
AVOID::[
  ASSUME_INTERNAL::"Skipping analysis for seemingly small changes — deceptive scope is the primary failure mode",
  DYNAMIC_BLIND_SPOT::"Static grep misses dynamic imports and string-based registry lookups — check config files manually",
  ROOT_FIRST::"Modifying root before leaves creates cascade of broken imports across all consumers"
]
§4::USED_BY
AGENTS::[implementation-lead]
CONTEXT::pre_modification_planning⊕interface_change⊕refactoring
§5::ANCHOR_KERNEL
TARGET::map_dependency_chains_and_impact_radius_before_modification
NEVER::[
  modify_interface_without_consumer_audit,
  remove_export_without_checking_imports,
  rename_without_tracing_all_references,
  assume_internal_without_verification,
  skip_for_seemingly_small_changes
]
MUST::[
  trace_consumers_and_dependencies_before_change,
  "classify_impact<BREAKING∨COMPATIBLE∨INTERNAL>",
  "plan_modification_order<leaves_first→root_last>",
  report_affected_file_count
]
GATE::"Are all consumers and dependencies mapped, impact classified, and modification order planned before any code change?"
===END===
