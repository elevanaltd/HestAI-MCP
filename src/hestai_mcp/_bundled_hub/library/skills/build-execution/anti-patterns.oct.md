===ANTI_PATTERNS===
META:
  TYPE::"SUPPORTING_DOCUMENTATION"
  VERSION::"1.0"
  PURPOSE::"Build Anti-Patterns"
  SOURCE::"anti-patterns.oct.md"
  STATUS::ACTIVE

SECTION_ORDER::[§1::CONTENT, §2::1ISOLATEDEDITS_SYSTEMBLINDNESS, §3::2FEATUREBLOAT_SCOPECREEP, §4::3CONTEXTDESTRUCTION_HISTORYAMNESIA, §5::4PREMATUREOPTIMIZATION_OPTIMIZATIONWITHOUTEVIDENCE, §6::5TESTPROCRASTINATION_TEST_AFTERSYNDROME, §7::6ABSTRACTIONADDICTION, §8::7SNOWBALLCOMMITS_OVERSIZEDCHANGES, §9::8DEPENDENCYDRIFT_VERSIONCHAOS, §10::9ENVIRONMENTPARITYGAPS_WORKS_ON_MY_MACHINE, §11::DETECTIONFRAMEWORK, §12::WISDOM]

§1::CONTENT

CONTENT::[
  TEXT::"DEFINITION::Common_mistakes_that_degrade_quality + increase_maintenance + introduce_bugs"
]

§2::1ISOLATEDEDITS_SYSTEMBLINDNESS

CONTENT::[
  TEXT::"SYMPTOMS::\"I_just_changed_one_function\"->unexpected_failures_in_distant_components + integration_bugs_despite_unit_tests + ripple_effects_not_anticipated"
  TEXT::"EXAMPLE::\"processUser(id)->processUser(userId) | 15_call_sites + db_query_builder + GraphQL_resolver + type_defs -> 4hrs_debugging\""
  TEXT::"DETECT::[changes_without_grepping, skip_dependency_analysis, quick_fix_mentality, no_test_failures_but_prod_breaks]"
  TEXT::"PREVENT::[ripple_map_before_coding[git_grep_usage], run_full_suite[not_just_changed_file], check_types[python -m mypy|npm run typecheck], system_impact_analysis[what_imports + transitive + assumptions + what_breaks]]"
]

§3::2FEATUREBLOAT_SCOPECREEP

CONTENT::[
  TEXT::"SYMPTOMS::\"Since_I'm_here_I'll_also...\"->features_nobody_asked_for + increased_complexity_without_user_value + PRs_do_multiple_things"
  TEXT::"EXAMPLE::\"Task: email_validation | Also: disposable_check + DNS_verify + typo_suggestions + analytics -> 200_lines_instead_of_10 + 3_new_dependencies\""
  TEXT::"DETECT::[implementing_not_in_requirements, adding_abstractions_for_future, improving_unrelated_code, multiple_concerns_one_commit]"
  TEXT::"PREVENT::[scope_validation[explicitly_requested? + solves_user_problem? + solving_problem_that_doesnt_exist?], defer_until_needed[Rule_of_Three], separate_PRs[improvement->new_ticket], commit_discipline[one_concern_per_commit]]"
]

§4::3CONTEXTDESTRUCTION_HISTORYAMNESIA

CONTENT::[
  TEXT::"SYMPTOMS::\"Comment_is_obvious_removing_it\"->deleting_TODOs_without_addressing + removing_commit_history + stripping_architectural_rationale"
  TEXT::"EXAMPLE::\"setTimeout_comment[why_not_setInterval + issue#234]->deleted->future_dev_reintroduces_bug#234\""
  TEXT::"DETECT::[deleting_non-obvious_comments, removing_TODO_without_resolution, stripping_git_history, cleanup_PRs_remove_context]"
  TEXT::"PREVENT::[git_handles_versions_comments_explain_WHY≠WHAT, preserve_TODOs[document_why_not_fixed], architectural_decisions_in_docs[.coord/DECISIONS.md], commit_messages_explain_WHY]"
]

§5::4PREMATUREOPTIMIZATION_OPTIMIZATIONWITHOUTEVIDENCE

CONTENT::[
  TEXT::"SYMPTOMS::\"This_could_be_faster\"->optimization_without_profiling + added_complexity_for_theoretical_gains + micro-optimizations_while_real_bottlenecks_exist"
  TEXT::"EXAMPLE::\"Optimize_array_iteration | Real_bottleneck: N+1_database_queries -> wasted_2hrs_on_wrong_optimization\""
  TEXT::"DETECT::[optimizing_without_measuring, assuming_bottlenecks, complexity_added_for_speed, ignoring_profiler_results]"
  TEXT::"PREVENT::[profile_first_ALWAYS[measure≠intuit], optimize_algorithms_before_code[O(n²)->O(n)], benchmark_before_after[prove_improvement], complexity_cost_justified[measurable_gain]]"
]

§6::5TESTPROCRASTINATION_TEST_AFTERSYNDROME

CONTENT::[
  TEXT::"SYMPTOMS::\"I'll_add_tests_later\"->tests_fit_code≠requirements + missing_edge_cases + tests_don't_guide_design + coverage_theater"
  TEXT::"EXAMPLE::\"Implement_feature->write_tests_after -> tests_pass_but_feature_breaks_in_edge_cases\""
  TEXT::"DETECT::[tests_added_after_code, commit_message[\"Add_tests\"], single_commit_both_test_impl, test_timestamp_newer_than_impl]"
  TEXT::"PREVENT::[TDD_discipline[RED->GREEN->REFACTOR], git_history_enforcement[test_commit->feat_commit], failing_test_proof_required, no_merge_without_TDD_evidence]"
]

§7::6ABSTRACTIONADDICTION

CONTENT::[
  TEXT::"SYMPTOMS::\"Future_flexibility\"->abstractions_for_2_use_cases + generic_classes_for_specific_problems + frameworks_for_one-time_tasks + indirection_without_benefit"
  TEXT::"EXAMPLE::\"2_similar_functions->DataProcessor_class_with_generics -> only_2_call_sites + complex_config\""
  TEXT::"DETECT::[abstraction_before_3rd_use, generic_solutions_for_specific_problems, indirection_without_clarity, flexibility_nobody_needs]"
  TEXT::"PREVENT::[Rule_of_Three[1st_concrete->2nd_note_similarity->3rd_consider_abstracting], YAGNI[You_Aren't_Gonna_Need_It], abstractions_reduce_cognitive_load≠increase, understandable_without_docs]"
]

§8::7SNOWBALLCOMMITS_OVERSIZEDCHANGES

CONTENT::[
  TEXT::"SYMPTOMS::100+_files_one_PR->impossible_to_review + mixed_concerns + unclear_scope + rollback_nightmare"
  TEXT::"EXAMPLE::\"Refactor_user_service + add_feature + fix_bugs + update_deps -> 247_files_changed\""
  TEXT::"DETECT::[PRs_with_50+_files, multiple_unrelated_changes, commit_with_mixed_concerns, reviewer_comment[\"too_large_to_review\"]]"
  TEXT::"PREVENT::[atomic_commits[one_logical_change], feature_flags[for_gradual_rollout], separate_refactor_from_features, stacked_PRs[small_incremental]]"
]

§9::8DEPENDENCYDRIFT_VERSIONCHAOS

CONTENT::[
  TEXT::"SYMPTOMS::outdated_dependencies->security_vulnerabilities + compatibility_issues + breaking_changes_accumulate + dependency_hell"
  TEXT::"EXAMPLE::\"react@16.8->18.0_without_testing -> breaking_changes_in_hooks + concurrent_mode_issues\""
  TEXT::"DETECT::[dependencies_not_updated_6mo+, security_warnings_ignored, version_pinning_without_reason, no_dependency_audit]"
  TEXT::"PREVENT::[regular_updates[monthly_review], security_scanning[npm_audit + Dependabot], test_before_update[integration_suite], document_version_decisions[why_pinned]]"
]

§10::9ENVIRONMENTPARITYGAPS_WORKS_ON_MY_MACHINE

CONTENT::[
  TEXT::"SYMPTOMS::\"Works_locally\"->prod_failures + different_node_versions + missing_env_vars + DB_schema_drift"
  TEXT::"EXAMPLE::\"Local: node@18 + sqlite | Prod: node@16 + postgres -> crashes_on_deploy\""
  TEXT::"DETECT::[no_version_specification, different_DBs_dev_prod, missing_.env.example, manual_environment_setup]"
  TEXT::"PREVENT::[version_specification[.nvmrc + package.json_engines], docker_for_consistency, CI_matches_prod[same_node_version + same_DB], env_var_validation[startup_checks]]"
]

§11::DETECTIONFRAMEWORK

CONTENT::[
  TEXT::"QUESTION::\"Which_anti-pattern_am_I_falling_into?\""
  TEXT::"CHECK::[ changing_without_system_analysis?->ISOLATED_EDITS, adding_unrequested_features?->FEATURE_BLOAT, deleting_WHY_comments?->CONTEXT_DESTRUCTION, optimizing_without_profiling?->PREMATURE_OPTIMIZATION, writing_tests_after?->TEST_PROCRASTINATION, abstracting_for_2_cases?->ABSTRACTION_ADDICTION, PR_with_100+_files?->SNOWBALL_COMMITS, dependencies_6mo+_old?->DEPENDENCY_DRIFT, works_locally≠prod?->ENVIRONMENT_PARITY_GAPS ]"
]

§12::WISDOM

CONTENT::[
  TEXT::"PREVENTION>CURE::\"Recognize_pattern_early->apply_prevention_strategy->avoid_hours_debugging\""
  TEXT::"CORE_TRUTH::\"Anti-patterns_are_shortcuts_that_create_technical_debt->Pay_now_or_pay_later_with_interest\""
]

===END===
