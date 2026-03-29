===SKILL:GOVERNANCE_REVIEW_PRIORITIZATION===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Batch ordering and triage of governance review findings. Prevents alignment violations from being buried by completeness nitpicks. Adapts the review-prioritization pattern for governance-specific priority tiers (G0-G3)."

§1::CORE
AUTHORITY::ADVISORY[finding_ordering⊕batch_triage⊕diminishing_returns_detection]
SCOPE::GR_output_with_3_or_more_findings
COMPLEMENTS::[governance-review<review_dimensions>,review-discipline<confidence_levels>,constructive-feedback<finding_presentation>]
// governance-review classifies individual finding dimensions (alignment, contradiction, etc.)
// governance-review-prioritization orders the batch for maximum reviewer impact

§2::PROTOCOL

PRIORITY_TIERS::[
  G0_ALIGNMENT::[
    SCOPE::North_Star_contradiction⊕immutable_violation⊕precedence_hierarchy_breach⊕System_Standard_conflict,
    ACTION::ALWAYS_REPORT_FIRST,
    CONFIDENCE_FLOOR::MODERATE,
    BLOCKING::ALWAYS
  ],
  G1_CONTRADICTION::[
    SCOPE::cross_document_conflict⊕incompatible_decisions⊕rule_conflict⊕agent_definition_inconsistency,
    ACTION::REPORT_AFTER_G0,
    CONFIDENCE_FLOOR::HIGH,
    BLOCKING::WHEN_CERTAIN_OR_HIGH
  ],
  G2_COMPLETENESS::[
    SCOPE::missing_required_fields⊕OCTAVE_structural_invalidity⊕insufficient_justification⊕missing_traceability,
    ACTION::REPORT_AFTER_G1,
    CONFIDENCE_FLOOR::HIGH,
    BLOCKING::WHEN_STRUCTURALLY_INVALID
  ],
  G3_IMPACT::[
    SCOPE::undocumented_downstream_effects⊕scope_expansion_without_justification⊕agent_skill_pattern_breakage,
    ACTION::REPORT_IF_WITHIN_BUDGET,
    CONFIDENCE_FLOOR::HIGH,
    BLOCKING::WHEN_BREAKING_IMPACT
  ]
]

BATCH_TRIAGE::[
  STEP_1::classify_all_findings_into_G0_through_G3,
  STEP_2::within_each_tier_sort_by_confidence_descending[CERTAIN→HIGH→MODERATE],
  STEP_3::apply_diminishing_returns_threshold,
  STEP_4::emit_ordered_findings_in_GR_output_format
]

DIMINISHING_RETURNS::[
  BUDGET::10_findings_maximum_in_PR_comment,
  RULE_1::all_G0_and_G1_findings_always_included[no_budget_cap],
  RULE_2::G2_findings_included_up_to_remaining_budget,
  RULE_3::G3_findings_included_only_if_budget_remains,
  RULE_4::if_over_budget_append_summary_count["+N more G2/G3 findings omitted"],
  STOP_SIGNAL::"When remaining findings are all G3 advisory → stop adding"
]

§3::GOVERNANCE

GR_OUTPUT_INTEGRATION::[
  ALIGNMENT_VERDICT::G0_findings_determine_overall_alignment_status,
  CONTRADICTION_ANALYSIS::G1_findings_in_priority_order,
  COMPLETENESS_CHECK::G2_findings_in_priority_order,
  IMPACT_MAP::G3_findings_in_priority_order,
  RECOMMENDATIONS::consolidated_from_all_tiers
]

METADATA_ENRICHMENT::[
  EXISTING::"<!-- review: {role,provider,verdict,sha,tier,findings,blocking} -->",
  ADDED_FIELDS::"priority_distribution,triaged,findings_omitted",
  DISTRIBUTION_FORMAT::"G0:N G1:N G2:N G3:N"
]

NEVER::[
  report_G3_before_G0_or_G1,
  omit_G0_findings_for_any_reason,
  exceed_10_finding_budget_without_explicit_override,
  consolidate_G0_or_G1_findings[each_must_stand_alone],
  report_speculative_G3_findings
]

§4::EXAMPLES

TRIAGE_SCENARIO::[
  INPUT::"GR produces 14 findings: 1xG0, 2xG1, 5xG2, 6xG3",
  PROCESS::[
    "Include 1xG0 (budget: 9 remaining)",
    "Include 2xG1 (budget: 7 remaining)",
    "Include 5xG2 (budget: 2 remaining)",
    "Include 2xG3 (budget: 0 remaining)",
    "Omit 4xG3",
    "Append: '+4 more G3 impact findings omitted'"
  ],
  OUTPUT_SUMMARY::"G0:1 G1:2 G2:5 G3:2(+4)"
]

§5::ANCHOR_KERNEL
TARGET::batch_ordered_governance_review_findings_by_severity
NEVER::[report_impact_before_alignment,omit_G0_findings,exceed_finding_budget,consolidate_blocking_findings,report_speculative_impact]
MUST::[classify_into_G0_through_G3,sort_by_confidence_within_tier,apply_diminishing_returns,emit_tier_distribution_in_summary,include_all_G0_G1_regardless_of_budget]
GATE::"Are governance findings ordered by severity tier, confidence-sorted within tier, and budget-capped with omission summary?"

===END===
