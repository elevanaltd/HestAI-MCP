===SKILL:DIAGNOSTIC_PROTOCOLS===
META:
  TYPE::SKILL
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"Empirical root cause identification: isolate, reproduce, evidence-gather, and confirm fix for implementation failures"
  // Complements error-triage (which classifies WHAT to fix first) — this covers HOW to find WHY it fails

§1::SCOPE
BOUNDARY::"error-triage→prioritizes_error_category; diagnostic-protocols→identifies_root_cause_within_category"
AUTHORITY::BLOCKING[assumption_without_evidence⊕fix_without_reproduction⊕green_state_not_verified]
APPLIES_TO::"Test failures, CI failures, type errors with non-obvious source, regression introduced by a change"

§2::ROOT_CAUSE_PROTOCOL
DIAGNOSIS_SEQUENCE::[
  1::CAPTURE_FAILURE_STATE[exact_error_message+file+line+stack_trace+command_used],
  2::REPRODUCE_LOCALLY[confirm_failure_is_reproducible_before_any_changes],
  3::BISECT_OR_ISOLATE[narrow_scope_to_smallest_failing_unit],
  4::FORM_HYPOTHESIS[one_falsifiable_statement_per_candidate_cause],
  5::TEST_HYPOTHESIS[make_minimal_targeted_change+run_validation],
  6::CONFIRM_ROOT_CAUSE[failure_disappears+no_new_failures_introduced],
  7::VERIFY_GREEN_STATE[run_full_quality_gate_suite]
]
BISECT_TRIGGERS::[
  regression_with_known_good_state::use_git_bisect,
  failure_only_in_CI::check_environment_matrix_diff[python_version+os+deps],
  failure_non_deterministic::check_test_ordering_and_shared_state
]
ISOLATE_SEQUENCE::[
  1::run_single_failing_test_in_isolation[not_full_suite],
  2::remove_all_unrelated_code_from_scope,
  3::check_if_failure_exists_without_recent_changes[git_stash_test],
  4::identify_smallest_reproduction_case
]

§3::EVIDENCE_STANDARDS
CAPTURE_BEFORE::[
  exact_error_output[command+stdout+stderr],
  failing_test_name_and_file,
  git_blame_or_last_commit_touching_failing_code,
  dependency_versions_if_environment_related
]
CAPTURE_DURING::[
  hypothesis_statement[precise_not_vague],
  change_made_to_test_hypothesis[diff_or_description],
  result_after_change[pass_or_fail_with_output]
]
CAPTURE_AFTER::[
  confirmation_run[full_suite_output_showing_green],
  root_cause_statement[one_sentence_explanation],
  fix_description[what_changed_and_why_it_resolves_root_cause]
]

§4::HYPOTHESIS_TEST_VALIDATE
HYPOTHESIS_FORMAT::"IF [specific_cause] THEN [expected_behavior_change]"
TEST_DISCIPLINE::[
  one_hypothesis_at_a_time[multiple_changes_invalidate_causality],
  minimal_change_per_test[isolate_variable],
  record_outcome_before_reverting_if_wrong
]
VALIDATE_CYCLE::[
  hypothesis→change→run_targeted_test→PASS[proceed_to_green_state_check]∨FAIL[reject_hypothesis→next_candidate]
]
GREEN_STATE_GATE::[
  1::run_full_test_suite[not_just_failing_test],
  2::run_lint_and_typecheck[0_errors_required],
  3::check_coverage_threshold_not_regressed,
  4::confirm_no_new_failures_introduced
]

§5::ANCHOR_KERNEL
TARGET::empirical_root_cause_identification_and_confirmed_green_state
NEVER::[
  fix_without_reproducing_first,
  test_multiple_hypotheses_simultaneously,
  claim_fix_without_full_suite_output,
  assume_root_cause_without_evidence,
  skip_green_state_verification
]
MUST::[
  capture_exact_failure_state_before_changes,
  reproduce_locally_before_diagnosing,
  form_single_falsifiable_hypothesis,
  run_full_quality_gate_suite_to_confirm_green
]
GATE::"Is failure reproduced, root cause evidenced, and full suite green before declaring fix complete?"

===END===
