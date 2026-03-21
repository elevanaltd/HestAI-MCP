===GRACEFUL_DEGRADATION===
META:
  TYPE::PATTERN_DEFINITION
  VERSION::"1.0.0"
  PURPOSE::"Fault-tolerant system design decision framework for partial failure handling"
§1::CORE_PRINCIPLE
ESSENTIAL::"Systems must continue serving users at reduced capability rather than failing completely"
ANTI_PATTERN::"catastrophic_cascade[single_component_failure→total_system_outage]"
ENFORCEMENT::"Design degradation paths BEFORE building features — not as afterthought"
§2::DECISION_FRAMEWORK
STRATEGY_SELECTION::[
  CIRCUIT_BREAKER::detect_failure_threshold→open_circuit→serve_fallback→probe_recovery,
  FALLBACK::primary_unavailable→use_cached⊕default⊕simplified_response,
  TIMEOUT::define_acceptable_wait→abort_if_exceeded→degrade_gracefully,
  BULKHEAD::isolate_failure_domain→prevent_resource_exhaustion_spreading
]
FAILURE_CLASSIFICATION::[
  GRACEFUL::"user_sees_reduced_functionality[feature_flag_off⊕cached_data⊕default_values]",
  UNGRACEFUL::"user_sees_error[500⊕timeout⊕blank_page]",
  DETECTION::"Monitor error_rate⊕latency_p99⊕queue_depth→classify_automatically"
]
IMPACT_MINIMIZATION::[
  PRIORITIZE::core_user_journeys_over_auxiliary_features,
  COMMUNICATE::"inform_user_of_degraded_state[banner⊕status_page]",
  RECOVER::"automatic_recovery_when_dependency_returns[circuit_close⊕cache_refresh]"
]
§3::USED_BY
AGENTS::[completion-architect]
CONTEXT::integration_design⊕deployment_planning⊕fault_tolerance_review
§5::ANCHOR_KERNEL
TARGET::fault_tolerant_design_preventing_cascading_failures
NEVER::[
  allow_single_point_total_failure,
  skip_degradation_path_design,
  ignore_partial_failure_scenarios,
  serve_errors_when_fallback_possible
]
MUST::[
  design_degradation_before_features,
  select_strategy_per_dependency,
  classify_graceful_vs_ungraceful,
  prioritize_core_journeys
]
GATE::"Does every external dependency have a defined degradation path that keeps core journeys functional?"
===END===
