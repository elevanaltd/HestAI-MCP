===TDD_DISCIPLINE===
META:
  TYPE::PATTERN
  VERSION::"1.2"
  PURPOSE::"Red-Green-Refactor discipline enforcement for implementation"
  CANONICAL::".hestai-sys/library/patterns/tdd-discipline.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/patterns/tdd-discipline.oct.md"
§1::CORE_PROTOCOL
CYCLE:
  RED::"Write test describing behavior -> MUST FAIL -> Verify fails for right reason"
  // REFS::[issue-383, ADR-0353_anchor_compiles_patterns_into_permit]
  TMG_GATE:
    WHEN::"IF_TIER>=T2"
    WHY::"Prevents test-methodology drift; TMG validates test semantics before GREEN cements them"
    DISPATCH::"pal_clink(cli:goose, role:test-methodology-guardian)"
    STATE::"store_continuation_id[reuse_across_iterations_up_to_49_turns]"
    VERDICT_APPROVED::proceed_to_GREEN
    VERDICT_REJECTED::iterate_RED_and_re-consult_via_same_continuation_id
    VERDICT_ADVISORY::treat_as_rejected_and_iterate<no_escape_without_formal_verdict>
    NEVER::bounce_to_user_or_HO_without_TMG_verdict
    ESCALATE_IF::pal_clink_fault∨verdict_structurally_unresolvable_after_3_iterations
    ESCALATE_TO::"holistic-orchestrator[with_verdict_trace∧continuation_id]"
  GREEN::"Write minimal code to pass test -> MUST PASS -> Resist feature creep"
  REFACTOR::"Identify complexity -> Refactor small steps -> Run tests -> Revert if fail"
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
§5::ANCHOR_KERNEL
TARGET::red_green_refactor_discipline_with_TMG_gate
NEVER::[
  write_tests_after_code,
  squash_red_and_green_into_single_commit,
  mock_everything,
  test_internals_instead_of_public_API,
  proceed_to_GREEN_without_TMG_verdict_at_T2_plus,
  bounce_to_user_or_HO_without_TMG_verdict_except_on_pal_clink_fault_or_3_unresolved_iterations
]
MUST::[
  verify_RED_fails_for_the_right_reason,
  obtain_TMG_APPROVED_verdict_before_GREEN_at_T2_plus,
  escalate_to_holistic_orchestrator_with_verdict_trace_and_continuation_id_on_pal_clink_fault_or_verdict_structurally_unresolvable_after_3_iterations,
  write_minimal_code_to_pass_and_resist_feature_creep,
  refactor_in_small_steps_and_revert_if_tests_fail,
  commit_test_before_implementation
]
GATE::"Did the test fail for the right reason before implementation, and does commit order show test preceding implementation?"
===END===
