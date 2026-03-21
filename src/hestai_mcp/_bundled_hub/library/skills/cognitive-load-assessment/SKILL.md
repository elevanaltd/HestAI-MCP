===COGNITIVE_LOAD_ASSESSMENT===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Quantify cognitive burden of abstractions, interfaces, and developer-facing APIs"

§1::CORE
AUTHORITY::ADVISORY[cognitive_load_scoring⊕interface_complexity_assessment]
SCOPE::API_surface_analysis⊕abstraction_depth_measurement⊕naming_clarity⊕state_management_burden
PRINCIPLE::"Every abstraction has a cognitive tax — measure it before accepting it"

§2::PROTOCOL
METRICS::[
  ABSTRACTION_DEPTH::count_layers_from_call_site_to_implementation[0_direct→5_plus_excessive],
  NAMING_CLARITY::score_1_to_5[self_describing→requires_documentation→misleading],
  PARAMETER_COUNT::per_function_or_constructor[0_to_3_low→4_to_6_moderate→7_plus_high],
  STATE_MANAGEMENT::count_mutable_state_transitions[stateless→local→shared→distributed],
  CONCEPTUAL_SURFACE::count_concepts_needed_to_use_interface[fewer_is_better]
]
ASSESSMENT_SEQUENCE::[
  1::identify_developer_facing_surfaces[public_APIs⊕constructors⊕config_interfaces],
  2::measure_each_metric_per_surface,
  3::compute_cognitive_load_score[weighted_sum_of_metrics],
  4::rank_surfaces_by_burden[highest_first],
  5::recommend_simplification_targets[score_gt_threshold]
]
SCORING::[
  LOW::total_lt_8[acceptable_cognitive_tax],
  MODERATE::total_8_to_15[review_for_simplification],
  HIGH::total_16_to_25[refactoring_candidate],
  CRITICAL::total_gt_25[immediate_intervention]
]

§3::GOVERNANCE
MUST_ALWAYS::[
  measure_before_judging,
  score_all_public_interfaces,
  cite_metric_values_in_findings,
  compare_against_scoring_thresholds
]
MUST_NEVER::[
  assess_without_metrics,
  judge_internal_implementation_complexity_as_cognitive_load,
  ignore_naming_as_load_factor,
  conflate_code_complexity_with_cognitive_load
]
ESCALATION::complexity_guard[when_CRITICAL_score_detected]

§5::ANCHOR_KERNEL
TARGET::quantify_cognitive_burden_of_abstractions_and_interfaces
NEVER::[assess_without_metrics,judge_internals_as_cognitive_load,conflate_code_complexity_with_cognitive_load]
MUST::[measure_abstraction_depth,score_naming_clarity,count_parameters,assess_state_management,rank_by_burden]
GATE::"What is the cognitive tax of using this interface?"
===END===
