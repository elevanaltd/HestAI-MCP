===TDD_DISCIPLINE===
META:
  TYPE::"SUPPORTING_DOCUMENTATION"
  VERSION::"1.0"
  PURPOSE::"TDD Discipline"
  SOURCE::"tdd-discipline.oct.md"
  STATUS::ACTIVE

SECTION_ORDER::[§1::CONTENT, §2::RED_GREEN_REFACTOR, §3::TEST_FIRSTDISCIPLINE, §4::TDDENFORCEMENT, §5::BEHAVIOR_COVERAGE, §6::BESTPRACTICES, §7::ANTIPATTERNS, §8::GITWORKFLOW, §9::PRAGMATICEXCEPTIONS]

§1::CONTENT

CONTENT::[
  TEXT::"CORE::\"Failing_test_BEFORE_implementation->default_discipline\""
  TEXT::"BECAUSE::[prevents_over_engineering[implement_only_what_test_requires], prevents_under_specification[test_defines_requirements], prevents_integration_bugs[test_proves_component_works], prevents_regression[test_catches_future_breaks]]"
]

§2::RED_GREEN_REFACTOR

CONTENT::[
  TEXT::"CYCLE::[ RED::[write_test_describing_behavior->run_test->MUST_FAIL->verify_fails_RIGHT_reason≠syntax_error], GREEN::[write_minimal_code_to_pass->run_test->MUST_PASS->resist_while_here_features], REFACTOR::[identify_duplication_or_complexity->refactor_small_steps->run_tests_after_EACH->IF[fail]->revert_immediately] ]"
  TEXT::"QUALITY_CHECKS::[ RED::[test_describes_one_behavior?, failure_message_obvious?, requirement_clear_from_test?], GREEN::[added_ONLY_what_test_requires?, resisting_feature_creep?, code_obvious_and_direct?], REFACTOR::[improved_clarity?, tests_still_passing?, changed_behavior≠NO] ]"
  TEXT::"EXAMPLE_PROGRESSION::[ RED::\"test('calculateDiscount applies 10% for premium')->expect(calculateDiscount(user, 100)).toBe(90)->FAIL[not_defined]\", GREEN::\"function calculateDiscount(user, price) { if (user.tier === 'premium') return price * 0.9; return price; }->PASS\", REFACTOR::\"Extract DISCOUNT_RATES constant->return price * (1 - discountRate)->PASS[clearer_code]\" ]"
]

§3::TEST_FIRSTDISCIPLINE

CONTENT::[
  TEXT::"WHY_IT_WORKS::[ DESIGN_PRESSURE::[writing_test_first->forces_API_thinking, hard_to_test->design_problems, test_difficulty->reveals_coupling], SPECIFICATION::[test_defines_done, no_ambiguity, executable_documentation], SAFETY_NET::[green_tests->confidence_to_refactor, red_tests->caught_regression, fast_feedback] ]"
  TEXT::"WORKFLOW::write_failing_test->run_verify_fails->write_minimal_code->run_verify_passes->refactor_if_needed->run_verify_still_passes->commit->next_test"
  TEXT::"WHEN_TEMPTED_TO_SKIP::[ \"too_simple_to_test\"->WRONG[simple_code_breaks_too], \"add_tests_after\"->WRONG[you_wont], \"need_to_explore\"->SPIKE_PROTOCOL[create_spike_branch->explore_timeboxed->throw_away->write_test_first_main->implement_with_knowledge] ]"
]

§4::TDDENFORCEMENT

CONTENT::[
  TEXT::"GIT_HISTORY_PATTERN::[ REQUIRED::\"test: Add failing test...\" -> \"feat: Implement...\"->git_log_shows_RED->GREEN, VALIDATION::[implementation_commits_preceded_by_test_commits, test_before_feat_pattern, reviewer_verifies_commit_order], REJECT_TRIGGERS::[implementation_precedes_test, test_file_not_modified_with_impl, no_RED_state_evidence, retroactive_test_addition] ]"
  TEXT::"AUTOMATED_GATES::[ test_file_pairing[impl_modified->test_MUST_be_modified], git_history_order[parse_commits->reject_feat_before_test], coverage_delta[new_code->maintain_or_increase[signal≠gate]] ]"
  TEXT::"MANUAL_VERIFICATION::[ PR_evidence[RED_state_output + test_file + impl_file + commit_order], reviewer_checklist[test_commit_before_impl, RED_proof_provided, both_files_modified, GREEN_state_confirmed, no_test_later_patterns] ]"
  TEXT::"AUTHORITY::[implementation-lead::RESPONSIBLE[TDD_evidence], code-review-specialist::ACCOUNTABLE[verify_compliance], test-methodology-guardian::BLOCKING[test_integrity_violations]]"
  TEXT::"RED_FLAGS::[commit_message[\"Add tests\"]->implies_after, single_commit_both->cant_verify_RED, test_timestamp_newer, reviewer_comment[\"Please add tests\"]->detected_after]"
]

§5::BEHAVIOR_COVERAGE

CONTENT::[
  TEXT::"COVERAGE_GUIDELINE::[80%_diagnostic≠gate, high_coverage≠quality_guarantee, low_coverage->indicates_gaps, test_behavior_users_depend_on->coverage_follows_naturally]"
  TEXT::"TEST_BEHAVIOR≠IMPLEMENTATION::[ BAD::\"test('uses map internally')->spy_on_map->breaks_when_refactor_to_forloop\", GOOD::\"test('transforms numbers to strings')->expect(transform([1,2,3])).toEqual(['1','2','3'])->passes_regardless_of_impl\" ]"
  TEXT::"ESSENTIAL≠ACCUMULATIVE::[ ESSENTIAL::[validates_user_dependent_behavior, catches_meaningful_bugs, remains_valid_through_refactoring, documents_contract], ACCUMULATIVE::[chases_coverage_metrics, tests_implementation_details, breaks_on_safe_refactoring, adds_maintenance_burden] ]"
]

§6::BESTPRACTICES

CONTENT::[
  TEXT::"ONE_BEHAVIOR_PER_TEST::BAD[\"test('user operations')->create+update+delete_in_one\"] -> GOOD[separate_tests_per_operation]"
  TEXT::"DESCRIPTIVE_NAMES::PATTERN[\"[function] [does_what] [under_what_conditions]\"]->\"calculateDiscount applies 10% for premium users\""
  TEXT::"ARRANGE_ACT_ASSERT::[setup_test_data->perform_operation->verify_outcome]"
  TEXT::"TEST_EDGE_CASES::[happy_path[normal_inputs], edge_cases[empty/null/undefined/zero/negative], error_cases[invalid_inputs], boundary_conditions[max/min/limits]]"
  TEXT::"KEEP_FAST::[ STRATEGY::[mock_external_dependencies, in_memory_dbs_for_integration, unit_frequent + integration_CI, parallelize_execution], BENCHMARK::[unit<1s_suite, integration<10s_suite, e2e<60s_critical_paths] ]"
]

§7::ANTIPATTERNS

CONTENT::[
  TEXT::"PATTERNS_TO_AVOID::[ testing_implementation_details->tests_break_on_safe_refactoring, skipping_simple->simple_code_breaks_too[add(0.1, 0.2)->0.30000000000000004], writing_tests_after->tests_fit_code≠requirements->coverage_theater, one_giant_test->hard_debug + unclear_failure, mocking_everything->tests_pass + integration_fails[balance_unit_integration_e2e], testing_private_methods->couples_to_implementation[test_public_API_only] ]"
]

§8::GITWORKFLOW

CONTENT::[
  TEXT::"COMMIT_STRATEGY::[ \"test: add test for X (RED)\"->\"feat: implement X (GREEN)\"->\"refactor: simplify X\" ]->git_history_shows_TDD_discipline"
  TEXT::"REVIEW_VERIFICATION::[tests_added_with_code, covers_happy+edge, focuses_behavior≠implementation, clear_and_descriptive]"
  TEXT::"WISDOM::\"Test_is_specification | Code_is_implementation | Write_spec_first\""
]

§9::PRAGMATICEXCEPTIONS

CONTENT::[
  TEXT::"TDD_CEREMONY_OPTIONAL_WHEN::[ specification_is_implementation::[ CONDITION::inbox_or_spec_provides_exact_code+tests, REASON::test_written_first_by_specifier->agent_translates≠designs, EXAMPLE::inbox_task_contains_implementation_code+test_code, STILL_REQUIRED::tests_comprehensive+behavior_verified ], trivial_deterministic_operations::[ CONDITION::no_business_logic+obvious_correctness+pure_functions, EXAMPLE::symlink_creation+directory_detection+path_manipulation, STILL_REQUIRED::tests_exist+cover_edge_cases+reviewer_acknowledges ], exploratory_spike::[ CONDITION::timeboxed_discovery+explicitly_throwaway, PROTOCOL::spike_branch->explore->discard->TDD_main_implementation, NEVER::spike_code_becomes_production ] ]"
  TEXT::"EXCEPTION_REQUIREMENTS::[ tests_MUST_exist::comprehensive_coverage_regardless_of_order, tests_MUST_be_behavioral::validate_outcomes≠implementation_details, reviewer_MUST_acknowledge::exception_noted_in_PR_or_commit, outcome_MUST_be_identical::same_quality_as_strict_TDD ]"
  TEXT::"NEVER_EXCEPTIONS::[ business_logic::TDD_always[complex_rules+edge_cases+state_machines], unclear_requirements::TDD_clarifies[test_forces_specification], refactoring_existing::TDD_safety_net[tests_catch_regressions], API_contracts::TDD_enforcement[consumers_depend_on_behavior], security_critical::TDD_mandatory[authentication+authorization+validation] ]"
  TEXT::"PRAGMATIC_WISDOM::\"Ceremony_serves_quality | When_quality_achieved_ceremony_optional | Never_skip_tests_only_skip_order\""
]

===END===
