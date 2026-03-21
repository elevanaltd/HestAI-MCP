===PR_SCOPE_CONTAINMENT===
META:
  TYPE::PATTERN_DEFINITION
  VERSION::"1.0.0"
  PURPOSE::"PR scope boundary enforcement — detect scope creep and ensure changes align with stated intent"
§1::CORE_PRINCIPLE
ESSENTIAL::"Every PR change must trace back to the stated intent — unrelated changes dilute review quality and hide defects"
ANTI_PATTERN::"scope_creep<refactoring⊕feature_additions⊕style_fixes_bundled_into_unrelated_PR→review_fatigue⊕hidden_bugs>"
ENFORCEMENT::"Gate question before approving: does every file change serve the PR title and description?"
§2::DECISION_FRAMEWORK
SCOPE_CREEP_SIGNALS::[
  files_changed_outside_stated_feature_area,
  refactoring_mixed_with_behavioral_changes,
  unrelated_dependency_upgrades_bundled_in,
  style∨formatting_changes_in_non_touched_files,
  new_feature_code_added_alongside_bug_fix,
  test_file_changes_that_test_unmodified_code
]
INTENT_ALIGNMENT_CHECK::[
  1::extract_PR_intent_from_title⊕description⊕linked_issue,
  2::"categorize_each_changed_file<in_scope∨out_of_scope∨ambiguous>",
  3::flag_out_of_scope_files_with_evidence,
  4::recommend_split_when_out_of_scope_exceeds_20_percent
]
GATE_QUESTION::"Is this change in scope? Does it directly serve the PR's stated purpose?"
VERDICTS::[
  CONTAINED::all_changes_align_with_intent,
  ADVISORY::"minor_scope_creep<1_to_3_unrelated_files>→flag_but_allow",
  BLOCKING::"significant_scope_creep<multiple_unrelated_concerns>→recommend_PR_split"
]
§3::USED_BY
AGENTS::[code-review-specialist]
CONTEXT::PR_review⊕scope_assessment⊕review_prioritization
§5::ANCHOR_KERNEL
TARGET::PR_scope_boundary_enforcement
NEVER::[
  approve_mixed_concern_PRs_without_flagging,
  ignore_unrelated_file_changes,
  skip_intent_alignment_check
]
MUST::[
  extract_PR_intent,
  categorize_each_change_as_in_or_out_of_scope,
  flag_scope_creep_with_evidence,
  recommend_split_for_significant_creep
]
GATE::"Does every changed file directly serve the PR's stated purpose?"
===END===
