===MCP_TOOLS===
META:
  TYPE::"SUPPORTING_DOCUMENTATION"
  VERSION::"1.0"
  PURPOSE::"MCP Tools for Build Execution"
  SOURCE::"mcp-tools.oct.md"
  STATUS::ACTIVE

SECTION_ORDER::[§1::CONTENT, §2::CONTEXT7_LIBRARYDOCUMENTATIONAUTHORITY, §3::REPOMIX_CODEBASEANALYSISAUTHORITY, §4::INTEGRATIONWITHBUILDPHILOSOPHY, §5::TOOLSELECTIONMATRIX, §6::CHECKPOINTS, §7::PRODUCTIONPATTERNS]

§1::CONTENT

CONTENT::[
  TEXT::"MANDATE::\"MCP_tools_MANDATORY_references_before_implementation->ensure_system_awareness + proper_library_usage\""
]

§2::CONTEXT7_LIBRARYDOCUMENTATIONAUTHORITY

CONTENT::[
  TEXT::"PURPOSE::real-time_library_documentation_retrieval[validate_API_usage, understand_patterns, ensure_correct_implementation]"
  TEXT::"WHEN_TO_USE::[ BEFORE_IMPL::[starting_third_party_library, implementing_framework_APIs, validating_patterns, checking_deprecations], DURING_IMPL::[confirming_signatures, understanding_return_types_and_errors, verifying_best_practices, security_considerations], DURING_DEBUG::[validating_assumptions, checking_known_issues, understanding_error_messages] ]"
  TEXT::"WORKFLOW::[ resolve::\"mcp__context7__resolve-library-id({libraryName})->returns_Context7_ID\", get_docs::\"mcp__context7__get-library-docs({context7CompatibleLibraryID, topic?, tokens?})->returns_current_docs\" ]"
  TEXT::"ALWAYS_USE_FOR::[React_hooks, Next.js_routing, Supabase_operations, authentication, any_third_party_library]"
  TEXT::"VERIFICATION_PATTERN::\"Check_Context7->implement_based_on_current_docs->verify_matches_documentation\""
  TEXT::"ANTI_PATTERNS::[ DONT::[assume_API_from_memory[APIs_change], use_outdated_StackOverflow[without_verification], implement_without_checking_docs, skip_for_simple_usage[simple_breaks_too]], DO::[check_Context7_before_every_implementation, verify_signatures_match_current, understand_error_handling_from_docs, check_deprecation_warnings] ]"
]

§3::REPOMIX_CODEBASEANALYSISAUTHORITY

CONTENT::[
  TEXT::"PURPOSE::package_and_analyze_codebase[understand_system_context, identify_patterns, prevent_isolated_edits]"
  TEXT::"WHEN_TO_USE::[ BEFORE_CHANGES::[understand_structures, find_similar_patterns, identify_usage_sites, analyze_system_impact], DURING_ANALYSIS::[architectural_patterns, code_organization, related_functionality, dependency_relationships], BEFORE_REFACTOR::[find_all_instances, understand_cross-file_dependencies, identify_integration_points, assess_scope] ]"
  TEXT::"WORKFLOW::[ pack::\"mcp__repomix__pack_codebase({directory, compress?, includePatterns?, ignorePatterns?})->returns_outputId\", search::\"mcp__repomix__grep_repomix_output({outputId, pattern, contextLines?, ignoreCase?})->returns_matches\", read::\"mcp__repomix__read_repomix_output({outputId, startLine, endLine})->returns_content\" ]"
  TEXT::"SYSTEM_AWARENESS_WORKFLOW::[ BEFORE_CHANGING_SIGNATURE::[pack_codebase->grep_function_usage->analyze_call_sites->map_ripple_effects->plan_migration_strategy], EXAMPLE::\"processUser(id)->processUser(user) | Pack->Grep(15_sites)->Analyze(10_have_user, 5_need_fetch)->Decision[keep_both_signatures_for_gradual_migration]\" ]"
  TEXT::"COMPRESSION::[ WHEN::[repo>500_files, need_overview≠full_content, analyzing_structure≠implementation, token_budget_concerns], USE::\"compress:true->tree-sitter_compression(~70%_reduction)\", TRADEOFF::[PRESERVES[structure, signatures, exports, imports], REMOVES[implementation_details, comments], USE_COMPRESSED[initial_exploration], USE_UNCOMPRESSED[detailed_analysis]] ]"
  TEXT::"ANTI_PATTERNS::[ DONT::[make_changes_without_grepping, assume_know_all_sites, skip_for_simple_changes, rely_on_IDE_search_only[misses_dynamic]], DO::[pack_and_grep_before_signature_changes, use_context_lines_for_patterns, analyze_systematically, document_migration_strategy] ]"
]

§4::INTEGRATIONWITHBUILDPHILOSOPHY

CONTENT::[
  TEXT::"SYSTEM_AWARENESS::\"Code_change->system_ripple->map_impact_before_coding\""
  TEXT::"MCP_ENABLES::[Context7::external_system_contracts, Repomix::internal_system_structure]"
  TEXT::"WORKFLOW_MANDATORY::[ understand_requirements->check_Context7[library_docs]->pack_Repomix[codebase]->analyze_ripple_effects->write_failing_test->implement_minimal->verify_with_tests->code_review ]"
  TEXT::"DECISION_FRAMEWORK::[ BEFORE_CODE::[user_problem?, Context7_says?, Repomix_pattern?, maintenance_cost?, extend_existing?], BEFORE_REFACTOR::[current_pattern?, instance_count?, usage_contexts?, safe_to_change?, migration_strategy?] ]"
]

§5::TOOLSELECTIONMATRIX

CONTENT::[
  TEXT::"TASK_TO_TOOL::[ implement_library_feature->Context7, change_function_signature->Repomix, add_third_party_integration->BOTH, refactor_internal_pattern->Repomix, debug_library_error->Context7, understand_codebase_structure->Repomix, validate_API_usage->Context7, find_all_usages->Repomix, architectural_decision->BOTH ]"
]

§6::CHECKPOINTS

CONTENT::[
  TEXT::"BEFORE_IMPL::[Context7_consulted_for_libraries, Repomix_packed_for_system, ripple_effects_mapped, migration_strategy_documented, similar_patterns_identified]"
  TEXT::"DURING_IMPL::[library_usage_matches_Context7, code_follows_Repomix_patterns, changes_account_for_all_sites, tests_validate_actual_contracts]"
  TEXT::"BEFORE_REVIEW::[Context7_citations, Repomix_analysis_for_impact, ripple_mapping_evidence, migration_plan_if_applicable]"
]

§7::PRODUCTIONPATTERNS

CONTENT::[
  TEXT::"HOOK_IMPLEMENTATION::\"Context7[current_React_patterns]->Repomix[existing_hook_patterns]->implement_following_both->tests_validate_contracts->structure_matches_patterns\""
  TEXT::"DATABASE_MIGRATION::\"Repomix[grep_all_queries(43_sites_found)]->Context7[Supabase_migration_patterns]->plan_phased_migration[add_column->migrate_data->update_sites->remove_old]->execute_systematically->zero_downtime\""
  TEXT::"WISDOM::\"Context7_understands_libraries | Repomix_understands_codebase | Use_both_for_system_awareness | NOT_optional->ESSENTIAL\""
]

===END===
