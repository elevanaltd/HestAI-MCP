===SKILL:REVIEW_PRIORITIZATION===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Batch ordering and triage of large CRS finding sets. Prevents critical issues from being buried by low-severity nitpicks in reviews with 15+ findings."

§1::CORE
AUTHORITY::ADVISORY[finding_ordering⊕batch_triage⊕diminishing_returns_detection]
SCOPE::CRS_output_with_5_or_more_findings
COMPLEMENTS::[review-discipline<confidence_levels>,constructive-feedback<finding_presentation>]
// review-discipline classifies individual finding confidence
// review-prioritization orders the batch for maximum reviewer impact

§2::PROTOCOL

PRIORITY_TIERS::[
  P0_SECURITY::[
    SCOPE::injection⊕auth_bypass⊕secrets_exposure⊕XSS⊕CSRF⊕privilege_escalation,
    ACTION::ALWAYS_REPORT_FIRST,
    CONFIDENCE_FLOOR::MODERATE
  ],
  P1_CORRECTNESS::[
    SCOPE::logic_errors⊕data_loss⊕race_conditions⊕null_dereference⊕unchecked_errors,
    ACTION::REPORT_AFTER_P0,
    CONFIDENCE_FLOOR::HIGH
  ],
  P2_RELIABILITY::[
    SCOPE::missing_tests⊕error_handling_gaps⊕unvalidated_input⊕resource_leaks,
    ACTION::REPORT_AFTER_P1,
    CONFIDENCE_FLOOR::HIGH
  ],
  P3_ARCHITECTURE::[
    SCOPE::coupling⊕cohesion⊕abstraction_violations⊕API_design⊕scope_creep,
    ACTION::REPORT_IF_WITHIN_BUDGET,
    CONFIDENCE_FLOOR::HIGH
  ],
  P4_PERFORMANCE::[
    SCOPE::algorithmic_complexity⊕N_plus_1⊕memory_allocation⊕caching,
    ACTION::REPORT_IF_WITHIN_BUDGET,
    CONFIDENCE_FLOOR::HIGH
  ],
  P5_STYLE::[
    SCOPE::naming⊕formatting⊕documentation⊕convention_violations,
    ACTION::REPORT_ONLY_IF_SYSTEMATIC,
    CONFIDENCE_FLOOR::CERTAIN
  ]
]

BATCH_TRIAGE::[
  STEP_1::classify_all_findings_into_P0_through_P5,
  STEP_2::within_each_tier_sort_by_confidence_descending[CERTAIN→HIGH→MODERATE],
  STEP_3::apply_diminishing_returns_threshold,
  STEP_4::emit_ordered_findings_in_CRS_output_format
]

DIMINISHING_RETURNS::[
  BUDGET::15_findings_maximum_in_PR_comment,
  RULE_1::all_P0_and_P1_findings_always_included[no_budget_cap],
  RULE_2::P2_findings_included_up_to_remaining_budget,
  RULE_3::P3_through_P5_included_only_if_budget_remains,
  RULE_4::if_over_budget_append_summary_count["+N more P3/P4/P5 findings omitted"],
  RULE_5::if_P5_count_exceeds_5_consolidate_into_single_style_note,
  STOP_SIGNAL::"When remaining findings are all P5 → stop adding (P5 requires CERTAIN confidence per CONFIDENCE_FLOOR)"
]

§3::GOVERNANCE

CRS_OUTPUT_INTEGRATION::[
  EXECUTIVE_SUMMARY::include_tier_distribution["P0:N P1:N P2:N P3:N P4:N P5:N"],
  CRITICAL_ISSUES::P0_and_P1_findings_in_priority_order,
  QUALITY_RECOMMENDATIONS::P2_through_P4_findings_in_priority_order,
  CODE_EXAMPLES::attached_to_individual_findings_not_separate_section
]

METADATA_ENRICHMENT::[
  EXISTING::"<!-- review: {role,provider,verdict,sha,tier,findings,blocking} -->",
  ADDED_FIELDS::"priority_distribution,triaged,findings_omitted"
]

NEVER::[
  report_P5_before_P0_or_P1,
  omit_P0_findings_for_any_reason,
  exceed_15_finding_budget_without_explicit_override,
  consolidate_P0_or_P1_findings[each_must_stand_alone],
  report_SPECULATIVE_P5_findings
]

§4::EXAMPLES

TRIAGE_SCENARIO::[
  INPUT::"CRS produces 22 findings: 1xP0, 3xP1, 5xP2, 8xP3, 5xP5",
  PROCESS::[
    "Include 1xP0 (budget: 14 remaining)",
    "Include 3xP1 (budget: 11 remaining)",
    "Include 5xP2 (budget: 6 remaining)",
    "Include 6xP3 (budget: 0 remaining)",
    "Omit 2xP3, consolidate 5xP5 into style note",
    "Append: '+2 more P3 and 5 P5 findings omitted'"
  ],
  OUTPUT_SUMMARY::"P0:1 P1:3 P2:5 P3:6(+2) P5:0(+5)"
]

§5::ANCHOR_KERNEL
TARGET::batch_ordered_review_findings_by_severity
NEVER::[report_style_before_security,omit_P0_findings,exceed_finding_budget,consolidate_blocking_findings,report_speculative_style]
MUST::[classify_into_P0_through_P5,sort_by_confidence_within_tier,apply_diminishing_returns,emit_tier_distribution_in_summary,include_all_P0_P1_regardless_of_budget]
GATE::"Are findings ordered by severity tier, confidence-sorted within tier, and budget-capped with omission summary?"

===END===
