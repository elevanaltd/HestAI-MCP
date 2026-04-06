===TDD_DISCIPLINE===
META:
  TYPE::PATTERN
  VERSION::"1.1"
  PURPOSE::"Red-Green-Refactor discipline enforcement for implementation"
§1::CORE_PROTOCOL
CYCLE::[
  RED::"Write test describing behavior -> MUST FAIL -> Verify fails for right reason",
  TMG_GATE::"[IF_TIER>=T2] MUST HALT -> Load review-red skill -> TMG MUST APPROVE tests before GREEN proceeds",
  GREEN::"Write minimal code to pass test -> MUST PASS -> Resist feature creep",
  REFACTOR::"Identify complexity -> Refactor small steps -> Run tests -> Revert if fail"
]
§2::GIT_WORKFLOW
PATTERN::[
  "test: Add failing test for X (RED)",
  "feat: Implement X (GREEN)",
  "refactor: Simplify X (REFACTOR)"
]
VALIDATION::"Reviewer verifies commit order: implementation preceded by test"
§3::ANTI_PATTERNS
AVOID::[
  TEST_AFTER::"Writing tests after code fits tests to implementation, not requirements",
  SINGLE_COMMIT::"Squashing Red/Green states hides the discipline",
  MOCKING_EVERYTHING::"Tests pass but integration fails - balance unit/integration",
  TESTING_INTERNALS::"Tests break on safe refactoring - test public API only"
]
===END===
