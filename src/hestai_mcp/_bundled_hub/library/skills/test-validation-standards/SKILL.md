===TEST_VALIDATION_STANDARDS===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Test coverage assessment framework for PR code reviews"

§1::CORE
AUTHORITY::ADVISORY[test_quality_findings⊕coverage_gap_detection]
SCOPE::PR_review_test_assessment[coverage⊕quality⊕TDD_compliance⊕missing_tests]
MISSION::"Evaluate test adequacy for changed code — detect gaps, verify quality signals, enforce TDD discipline"

§2::PROTOCOL

COVERAGE_ASSESSMENT::[
  1::identify_changed_production_files,
  2::map_changed_files_to_test_files[naming_convention⊕import_tracing],
  3::flag_untested_changes[new_functions⊕modified_branches⊕error_paths],
  4::assess_coverage_thresholds[project_configured∨80_percent_default]
]

TEST_QUALITY_SIGNALS::[
  GOOD::[tests_behavior_not_implementation,descriptive_names,single_assertion_focus,arrange_act_assert],
  BAD::[testing_private_internals,brittle_mock_chains,no_edge_cases,copy_paste_tests],
  CRITICAL::[no_tests_for_new_public_API,deleted_tests_without_replacement,test_passes_without_assertions]
]

MISSING_TEST_DETECTION::[
  new_public_function_without_test::BLOCKING,
  new_error_path_without_test::BLOCKING,
  modified_branch_logic_without_test::ADVISORY,
  config_change_without_validation_test::ADVISORY,
  "new_CLI_command∨API_endpoint_without_smoke_test"::BLOCKING
]

TDD_COMMIT_ORDER::[
  EXPECTED::"test(RED)→feat(GREEN)→refactor(OPTIONAL)",
  CHECK::git_log_commit_order[test_commit_before_feat_commit],
  VIOLATION::"feat_commit_without_preceding_test_commit→ADVISORY_finding"
]

§3::GOVERNANCE

THRESHOLDS::[
  MINIMUM_COVERAGE::project_configured∨80_percent,
  NEW_CODE_COVERAGE::90_percent_target,
  CRITICAL_PATH::100_percent[auth⊕payment⊕data_mutation]
]

MUST::[
  map_every_changed_file_to_tests,
  flag_untested_public_API_additions,
  check_test_quality_not_just_existence,
  verify_TDD_commit_ordering_when_commits_available
]

NEVER::[
  accept_tests_that_pass_without_assertions,
  approve_deleted_tests_without_replacement_coverage,
  count_test_file_existence_as_sufficient[must_cover_changed_code]
]

§5::ANCHOR_KERNEL
TARGET::test_coverage_and_quality_assessment_for_PR_reviews
NEVER::[approve_untested_public_API,accept_assertion_free_tests,ignore_deleted_test_coverage,count_existence_as_coverage]
MUST::[map_changes_to_tests,flag_coverage_gaps,assess_test_quality_signals,check_TDD_commit_order]
GATE::"Are all changed code paths covered by quality tests that verify behavior?"

===END===
