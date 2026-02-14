===EXEMPLAR:TDD_DISCIPLINE===
// This is a PROPOSED update to the existing pattern.
// Demonstrates §ANCHOR_KERNEL authoring on an already-good pattern.
// Current version: 30 lines / 115 words (good)
// This version: ~40 lines / ~140 words (adds kernel only)

===PATTERN:TDD_DISCIPLINE===
META:
  TYPE::PATTERN
  VERSION::"1.1"
  PURPOSE::"Red-Green-Refactor discipline enforcement for implementation"

§1::CORE_PRINCIPLE
CYCLE::[
  RED::"Write test describing behavior → MUST FAIL → Verify fails for right reason",
  GREEN::"Write minimal code to pass test → MUST PASS → Resist feature creep",
  REFACTOR::"Identify complexity → Refactor small steps → Run tests → Revert if fail"
]

§2::DECISION_FRAMEWORK
GIT_WORKFLOW::[
  "test: Add failing test for X" (RED),
  "feat: Implement X" (GREEN),
  "refactor: Simplify X" (REFACTOR)
]
VALIDATION::"Reviewer verifies commit order: test: commit precedes feat: commit in git log"
PRAGMATIC_EXCEPTIONS::"When spec provides exact code+tests, trivial config changes, exploratory spikes (must be marked as such)"

§3::ANTI_PATTERNS
AVOID::[
  TEST_AFTER::"Writing tests after code fits tests to implementation, not requirements",
  SINGLE_COMMIT::"Squashing Red/Green states hides the discipline evidence",
  MOCKING_EVERYTHING::"Tests pass but integration fails — balance unit/integration",
  TESTING_INTERNALS::"Tests break on safe refactoring — test public API only"
]

§ANCHOR_KERNEL
TARGET::test_before_implementation_discipline
NEVER::[implement_before_test, squash_red_green_into_single_commit, test_implementation_internals]
MUST::[write_failing_test_first, verify_failure_reason, commit_test_separately_from_implementation]
GATE::"Does the git log show test: commit BEFORE the corresponding feat: commit?"

===END===
