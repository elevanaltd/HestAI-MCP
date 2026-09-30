===PATTERN:VERIFICATION_PROTOCOLS===
META:
  TYPE::PATTERN
  VERSION::"1.0"
  PURPOSE::"Evidence-based verification standards for all changes"
  CANONICAL::".hestai-sys/library/patterns/verification-protocols.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/patterns/verification-protocols.oct.md"
§1::MANDATORY_ARTIFACTS
ARTIFACTS::[
  TEST_RESULTS::"Command output showing pass/fail",
  BUILD_LOGS::"Lint + Typecheck + Test execution (0 errors)",
  COVERAGE_REPORTS::"Actual percentages with file paths",
  CI_LINKS::"Pipeline run URL with commit SHA"
]
§2::QUALITY_GATES
MANDATORY::[
  LINT::"0 errors + 0 warnings required",
  TYPECHECK::"0 errors required",
  TEST::"All passing required (no skips without ticket)"
]
§3::ANTI_VALIDATION_THEATER
REJECT::[
  "I ran tests (No output)",
  "Coverage looks good (No report)",
  "Passes locally (CI not run)",
  "This should work (No verification)"
]
§5::ANCHOR_KERNEL
TARGET::evidence_based_verification_of_changes
NEVER::[
  claim_tests_ran_without_output,
  claim_coverage_without_report,
  accept_passes_locally_without_CI_run,
  accept_this_should_work_without_verification,
  skip_tests_without_ticket
]
MUST::[
  attach_test_results_as_command_output,
  attach_build_logs_showing_0_errors_for_lint_typecheck_and_test,
  attach_coverage_reports_with_actual_percentages_and_file_paths,
  link_CI_pipeline_run_with_commit_SHA,
  require_0_lint_errors_and_warnings_and_0_typecheck_errors_and_all_tests_passing
]
GATE::"Is every verification claim backed by real command output, a report, or a CI run link?"
===END===
