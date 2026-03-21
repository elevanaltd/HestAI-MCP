===PROGRESSIVE_SIMPLIFICATION===
META:
  TYPE::PATTERN_DEFINITION
  VERSION::"1.0.0"
  PURPOSE::"Incremental simplification with rollback-safe progressive removal strategy"
§1::CORE_PRINCIPLE
ESSENTIAL::"Simplify one component at a time — verify between each removal to preserve system integrity"
ANTI_PATTERN::"big_bang_simplification<remove_multiple_components_simultaneously→cascading_failures⊕unclear_root_cause>"
ENFORCEMENT::"Remove lowest-risk component first, verify, then proceed to next"
§2::DECISION_FRAMEWORK
REMOVAL_STRATEGY::[
  1::rank_candidates_by_risk_and_impact<low_risk_high_impact_first>,
  2::remove_single_component,
  3::"verify_system_integrity<tests⊕integration⊕behavior>",
  4::if_broken→rollback_immediately⊕reclassify_as_ESSENTIAL,
  5::if_intact→commit_removal⊕proceed_to_next
]
PATH_RANKING::[
  PRIORITY_1::"dead_code<zero_risk⊕immediate_clarity>",
  PRIORITY_2::"unused_abstractions<low_risk⊕reduced_cognitive_load>",
  PRIORITY_3::"passthrough_layers<moderate_risk⊕structural_simplification>",
  PRIORITY_4::"redundant_patterns<higher_risk⊕requires_consolidation>"
]
ROLLBACK_SAFETY::[
  one_change_per_commit::atomic_reversibility,
  verify_between_each::no_assumption_stacking,
  preserve_tests::tests_are_verification_not_removal_targets
]
§3::USED_BY
AGENTS::[complexity-guard]
CONTEXT::simplification_recommendations⊕refactoring_guidance⊕complexity_reduction
§5::ANCHOR_KERNEL
TARGET::safe_incremental_complexity_reduction
NEVER::[
  remove_multiple_components_simultaneously,
  skip_verification_between_removals,
  remove_tests_as_simplification,
  assume_stacked_removals_are_safe
]
MUST::[
  rank_by_risk_and_impact,
  remove_one_at_a_time,
  verify_after_each_removal,
  rollback_if_broken
]
GATE::"Is this removal atomic, verified, and independently reversible?"
===END===
