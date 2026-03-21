===ABSTRACTION_LAYER_MAPPING===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Layer count analysis, justification framework, and consolidation patterns"

§1::CORE
AUTHORITY::BLOCKING[unjustified_layers⊕layer_count_violations]
SCOPE::layer_inventory⊕justification_per_layer⊕consolidation_recommendations⊕anti_pattern_detection
PRINCIPLE::"Every layer must justify its existence — unjustified layers are accumulative complexity"

§2::PROTOCOL
LAYER_INVENTORY::[
  1::trace_request_path[entry_point→data_store_or_output],
  2::identify_each_boundary_crossing[interface⊕abstraction⊕indirection],
  3::name_each_layer[controller⊕service⊕repository⊕DAO⊕adapter⊕etc],
  4::count_total_layers_in_path
]
JUSTIFICATION_CRITERIA::[
  JUSTIFIED::layer_enforces_distinct_concern[security⊕validation⊕transformation⊕persistence],
  JUSTIFIED::layer_enables_independent_testing[mockable_boundary],
  JUSTIFIED::layer_serves_different_consumers[API⊕CLI⊕event],
  UNJUSTIFIED::layer_is_pure_passthrough[delegates_without_transformation],
  UNJUSTIFIED::layer_duplicates_adjacent_concern[same_validation_twice],
  UNJUSTIFIED::layer_exists_for_pattern_compliance_only[no_behavioral_value]
]
ANTI_PATTERNS::[
  controller_service_repository_DAO_for_CRUD::"4_layers_for_simple_data_access→consolidate_to_2",
  adapter_for_single_implementation::"interface_with_one_impl→remove_interface",
  manager_wrapping_manager::"delegation_chain_with_no_transformation→flatten",
  factory_for_single_type::"unnecessary_indirection→direct_construction"
]
CONSOLIDATION_PATTERNS::[
  passthrough_elimination::merge_layer_into_caller_or_callee,
  interface_collapse::remove_interface_when_single_implementation,
  layer_merge::combine_adjacent_layers_with_same_concern
]

§3::GOVERNANCE
MUST_ALWAYS::[
  inventory_all_layers_before_judging,
  apply_justification_criteria_per_layer,
  cite_anti_pattern_name_when_detected,
  recommend_specific_consolidation
]
MUST_NEVER::[
  accept_layers_without_justification,
  flag_layers_without_tracing_request_path,
  recommend_removal_without_consolidation_path,
  ignore_team_boundary_justification
]
ESCALATION::complexity_guard[when_layer_count_gt_5⊕systemic_over_layering]

§5::ANCHOR_KERNEL
TARGET::justify_or_eliminate_each_abstraction_layer
NEVER::[accept_unjustified_layers,flag_without_request_path_trace,recommend_removal_without_consolidation_path]
MUST::[inventory_all_layers,apply_justification_criteria,detect_anti_patterns,recommend_consolidation]
GATE::"Does this layer transform, enforce, or separate — or is it pure passthrough?"
===END===
