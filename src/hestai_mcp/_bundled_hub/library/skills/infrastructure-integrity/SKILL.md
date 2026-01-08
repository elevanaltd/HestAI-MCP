===SKILL:INFRASTRUCTURE_INTEGRITY===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Protocol for maintaining test infrastructure reliability and reproducibility"

§1::CORE_CONSTRAINTS
CONSTRAINTS::[
  CI_REPRODUCIBILITY::"Local test execution must match CI environment exactly",
  STANDARDS_OBSERVABILITY::"Violations must be detectable through automated quality gates",
  ENVIRONMENT_ISOLATION::"Test credentials must never touch production systems",
  CROSS_APP_CONSISTENCY::"Shared test patterns must work identically across workspace"
]

§2::ANTI_PATTERNS
VIOLATIONS::[
  VALIDATION_THEATER::"CI passes but tests don't actually run",
  CONFIGURATION_DRIFT::"Local works but CI fails due to environment differences",
  CREDENTIAL_EXPOSURE::"Test credentials leaked to git",
  STANDARDS_EROSION::"Test files scattered without naming consistency"
]

===END===
