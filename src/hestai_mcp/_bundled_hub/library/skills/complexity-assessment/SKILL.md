===COMPLEXITY_ASSESSMENT===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"ESSENTIAL vs ACCUMULATIVE complexity taxonomy with SUBTRACT_UNTIL_BREAKS detection"

§1::CORE
AUTHORITY::BLOCKING[complexity_misclassification⊕false_positive_flagging]
SCOPE::codebase_complexity_analysis⊕component_justification⊕simplification_triage
TAXONOMY::[
  ESSENTIAL::"Atlas_burden<justified_by_requirements⊕regulatory⊕domain_inherent>",
  ACCUMULATIVE::"Sisyphean_work<future_proofing⊕pattern_theater⊕framework_for_one_time_task>"
]

§2::PROTOCOL
SUBTRACT_UNTIL_BREAKS::[
  1::inventory_all_components[layers⊕abstractions⊕patterns⊕dependencies],
  2::for_each_component→hypothetically_remove,
  3::does_system_break→ESSENTIAL[Atlas_burden_justified],
  4::system_still_works→ACCUMULATIVE[candidate_for_removal]
]
TRIGGER_THRESHOLDS::[
  layers_gt_3::investigate_justification,
  patterns_before_problems::premature_abstraction_signal,
  framework_for_one_time_task::over_engineering_signal,
  12_components_needing_fewer::consolidation_candidate
]
FALSE_POSITIVE_PREVENTION::[
  CHECK::system_context_before_flagging[microservice_vs_monolith],
  CHECK::enterprise_justification[compliance⊕audit⊕team_boundaries],
  CHECK::regulatory_requirements[healthcare⊕finance⊕government],
  CHECK::scale_requirements[traffic⊕data_volume⊕team_size],
  IF::justified_by_context→ESSENTIAL[not_ACCUMULATIVE]
]

§3::GOVERNANCE
MUST_ALWAYS::[
  run_SUBTRACT_UNTIL_BREAKS_before_classifying,
  check_false_positive_prevention_before_flagging,
  cite_evidence_for_each_classification,
  distinguish_Atlas_from_Sisyphean
]
MUST_NEVER::[
  flag_without_evidence,
  skip_context_check,
  classify_by_intuition_alone,
  ignore_regulatory_justification
]
ESCALATION::technical_architect[when_classification_disputed⊕systemic_accumulative_detected]

§5::ANCHOR_KERNEL
TARGET::classify_complexity_as_ESSENTIAL_or_ACCUMULATIVE
NEVER::[flag_without_SUBTRACT_UNTIL_BREAKS,skip_false_positive_prevention,classify_by_intuition,ignore_context_justification]
MUST::[subtract_each_component_test_if_breaks,check_enterprise_regulatory_scale_context,cite_evidence_per_classification,apply_trigger_thresholds]
GATE::"Does removing this component break the system, or does it survive?"
===END===
