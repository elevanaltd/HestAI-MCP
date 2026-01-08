===PATTERN:VERIFICATION_PROTOCOLS===
META:
  TYPE::PATTERN
  VERSION::"1.0"
  PURPOSE::"Evidence-based verification standards for all changes"

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
  "I ran tests" (No output),
  "Coverage looks good" (No report),
  "Passes locally" (CI not run),
  "This should work" (No verification)
]

===END===
