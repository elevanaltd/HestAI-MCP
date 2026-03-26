===VISIBILITY_RULES===

META:
  TYPE::STANDARD
  ID::visibility-rules
  VERSION::"1.8"
  STATUS::ACTIVE
  PURPOSE::"Placement and lifecycle rules for artifacts to ensure discoverability"
  DOMAIN::governance
  OWNERS::[system-steward]
  CREATED::2025-12-09
  UPDATED::2026-03-04
  CANONICAL::.hestai-sys/standards/rules/visibility-rules.oct.md
  SOURCE::src/hestai_mcp/_bundled_hub/standards/rules/visibility-rules.oct.md
  TAGS::[placement, visibility, documentation, lifecycle, hestai-sys, bundled-hub]

===CORE_PRINCIPLE===

LOCATION_RULE::VISIBILITY+PERMANENCE

PLACEMENT_LOGIC::[
  developer_docs→git_visibility[committed],
  coordination_artifacts→ephemeral[gitignored],
  placement→determines_audience+lifecycle
]

===PLACEMENT_RULES===

RULE_0::SYSTEM_STANDARDS→.hestai-sys/::[
  AUDIENCE::all_HestAI_products+agents,
  LIFECYCLE::committed_in_source+read_only_when_injected,
  TRACKING::git_history+MCP_injection_as_.hestai-sys/,

  WHAT_GOES_HERE::[
    system_north_star[universal_immutables],
    agent_definition_templates[.oct.md],
    standards_rules[naming+visibility+test_standards],
    project_templates[north_star_templates],
    reference_libraries[octave_pointers+guides],
    system_skills[ecosystem_wide_operational_knowledge],
    system_tools[validators+checkers]
  ],

  STRUCTURE::[
    .hestai-sys/standards/workflow/→[000-SYSTEM-HESTAI-NORTH-STAR.md],
    .hestai-sys/standards/rules/→[naming-standard.oct.md|visibility-rules.oct.md],
    .hestai-sys/templates/→[project_templates],
    .hestai-sys/library/skills/→[ecosystem_wide_skills],
    .hestai-sys/library/agents/→[agent_definitions+agent_definition_templates],
    .hestai-sys/library/patterns/→[reusable_patterns],
    .hestai-sys/library/schemas/→[schema_definitions],
    .hestai-sys/library/octave/→[octave_usage_guides],
    .hestai-sys/tools/→[system_utilities]
  ],

  WHY_system_governance_layer::[
    universal_governance≠product_specific,
    authored_in_src/hestai_mcp/_bundled_hub/_and_injected_as_.hestai-sys/[read_only],
    agents_cannot_modify_their_own_rules,
    single_source_of_truth_across_products,
    I3_DUAL_LAYER_AUTHORITY_enforcement
  ],

  INJECTION_MECHANISM::[
    MCP_server→copies_src/hestai_mcp/_bundled_hub/→.hestai-sys/[runtime],
    .hestai-sys/→gitignored[not_committed_per_product],
    agents→read_.hestai-sys/[cannot_write]
  ]
]

RULE_1::PERMANENT_ARCHITECTURAL→docs/::[
  AUDIENCE::developers[via_git+GitHub+IDEs],
  LIFECYCLE::committed+reviewed+permanent,
  TRACKING::git_history_provides_versioning,

  WHAT_GOES_HERE::[
    architecture_decision_records[ADRs],
    system_design_documents,
    API_documentation,
    database_schema_documentation,
    deployment_guides,
    development_setup_guides,
    technical_reference_material
  ],

  STRUCTURE::[
    docs/adr/→[adr-NNNN-topic.md|per_ADR-0031_issue_based_numbering],
    docs/development/→SETUP.md,
    docs/deployment/→DEPLOYMENT.md
  ],

  WHY_docs::[
    visible_in_git_diffs+pull_requests,
    searchable_in_GitHub_IDEs,
    appears_in_repository_browsing,
    versioned_alongside_code,
    part_of_code_review_process
  ]
]

RULE_2::OPERATIONAL_STATE→.hestai/state/context/::[
  AUDIENCE::AI_agents+human_coordination,
  LIFECYCLE::living_documents+high_churn,
  TRACKING::shared_across_worktrees[symlinked_to_.hestai-state/],

  WHAT_GOES_HERE::[
    PROJECT-CONTEXT.md[system_dashboard],
    PROJECT-CHECKLIST.md[high_level_tasks],
    PROJECT-HISTORY.md[significant_events],
    app_specific_contexts[APP-CONTEXT.md|APP-CHECKLIST.md|APP-HISTORY.md]
  ],

  STRUCTURE::[
    .hestai/state/context/→[PROJECT-CONTEXT.md|PROJECT-CHECKLIST.md|PROJECT-HISTORY.md],
    .hestai/state/context/apps/{app}/→[APP-CONTEXT.md|APP-CHECKLIST.md|APP-HISTORY.md],
    .hestai/state/context/.archive/→deprecated_docs
  ],

  WHY_.hestai_state::[
    agents_need_fresh_context_per_invocation,
    dashboard_pattern[PROJECT→APP_details],
    high_update_frequency→no_PR_overhead,
    shared_via_symlink→all_worktrees_see_same_state,
    separate_from_developer_docs
  ]
]

RULE_3::SESSION_ARTIFACTS→.hestai/state/sessions/::[
  AUDIENCE::session_continuity+audit_trail,
  LIFECYCLE::active→archived,
  TRACKING::shared_across_worktrees[symlinked_to_.hestai-state/],

  WHAT_GOES_HERE::[
    active_session_working_state[in_progress],
    archived_session_transcripts[durable],
    derived_artifacts[durable]
  ],

  STRUCTURE::[
    .hestai/state/sessions/active/{session_id}/→[session.json|anchor.json],
    .hestai/state/sessions/archive/→[
      YYYY-MM-DD-{focus}-{id}-raw.jsonl,
      YYYY-MM-DD-{focus}-{id}-octave.oct.md,
      YYYY-MM-DD-{focus}-{id}.verification.json
    ]
  ],

  WHY_shared_state::[
    active→high_churn+partial_inconsistent_state,
    archive→durable_record[continuity+auditability],
    shared_via_symlink→visibility_across_worktrees
  ]
]

RULE_4::PROJECT_GOVERNANCE→.hestai/::[
  AUDIENCE::AI_agents+system_governance,
  LIFECYCLE::committed+PR_controlled+stable_patterns,
  TRACKING::git_history_tracks_governance_evolution,

  WHAT_GOES_HERE::[
    north_star_documents[immutable_requirements],
    compiled_governance_decisions[debate_outcomes],
    project_rules_and_schemas,
    test_infrastructure_standards,
    methodology_guides_and_workflow_standards
  ],

  STRUCTURE::[
    .hestai/north-star/→000-{PROJECT}-NORTH-STAR.md+components/[ONLY_north_stars],
    .hestai/decisions/→compiled_governance_decisions[debate_outcomes],
    .hestai/rules/→project_standards+methodology+workflow_guidance,
    .hestai/schemas/→schema_definitions
  ],

  WHY_.hestai_governance::[
    methodology_governance≠implementation_docs,
    binding_patterns→agents_must_follow,
    stable_enough_for_git_tracking,
    cross_project_patterns_standards
  ],

  NOTE::[
    .hestai/decisions/≠docs/adr/,
    .hestai/decisions/→compiled_debate_decisions[governance_level_outcomes],
    docs/adr/→formal_ADRs[developer_facing_architecture_records]
  ]
]

RULE_5::CLAUDE_CODE_CONFIG→.claude/::[
  AUDIENCE::Claude_Code_CLI_infrastructure,
  LIFECYCLE::committed+synchronized_across_projects,
  TRACKING::git+sync_commands[cfg-config-sync],

  WHAT_GOES_HERE::[
    agent_definitions[.oct.md_files],
    slash_commands[/activate|/role],
    skills[operational_knowledge_modules],
    hooks[git_workflow_automation]
  ],

  STRUCTURE::[
    .claude/agents/→[implementation-lead.oct.md|critical-engineer.oct.md],
    .claude/commands/→activate.md,
    .claude/skills/build-execution/,
    .claude/hooks/→pre-commit
  ],

  WHY_.claude::[
    Claude_Code_CLI_convention,
    isolated_per_project[or_global_~/.claude/],
    synchronized_via_cfg-config-sync,
    infrastructure≠documentation
  ],

  NOTE::[
    .claude/skills/→project_specific_skills[per_repo],
    .hestai-sys/library/skills/→ecosystem_wide_skills[system_governance_injected]
  ]
]

RULE_6::REPORTS→.hestai/state/reports/::[
  AUDIENCE::humans+reviewers+governance,
  LIFECYCLE::durable+time_scoped_evidence,
  TRACKING::shared_across_worktrees[symlinked_to_.hestai-state/],

  WHAT_GOES_HERE::[
    phase_gate_evidence[B0_validation|B1-B3_reports|implementation_logs],
    audit_reports[anchor_audits|gate_failures|integrity_checks],
    security_scan_outputs[redaction_summaries|findings],
    operational_diagnostics["why_clock_out_failed"],
    quality_gate_evidence[retained_beyond_single_session]
  ],

  STRUCTURE::[
    .hestai/state/reports/→[
      YYYY-MM-DD-anchor-audit-clockout-clean-on-success.md,
      YYYY-MM-DD-jsonl-secrets-scan-findings.json
    ]
  ],

  WHY_.hestai_state_reports::[
    evidence_discoverable≠polluting_docs,
    separates_durable_evidence≠living_dashboard[.hestai/state/context/],
    shared_via_symlink→visibility_across_worktrees
  ]
]

===DECISION_MATRIX===

// KEY DISTINCTION: .hestai-sys/ vs .hestai/
//   .hestai-sys/ = SYSTEM governance (universal, injected as read-only)
//   .hestai/     = PRODUCT context (specific to this repo, mutable within rules)
// Source (maintainers): src/hestai_mcp/_bundled_hub/ is injected to .hestai-sys/

PLACEMENT_TABLE::[
  // SYSTEM GOVERNANCE (.hestai-sys/)
  system_north_star→.hestai-sys/standards/workflow/[committed_in_source|all_products|read_only_injection],
  governance_rules→.hestai-sys/standards/rules/[committed_in_source|all_products|read_only_injection],
  agent_templates→.hestai-sys/library/agents/[committed_in_source|all_products|read_only_injection],
  project_templates→.hestai-sys/templates/[committed_in_source|all_products|read_only_injection],
  reference_libraries→.hestai-sys/library/[committed_in_source|all_products|read_only_injection],
  system_skills→.hestai-sys/library/skills/[committed_in_source|all_products|read_only_injection],
  system_tools→.hestai-sys/tools/[committed_in_source|all_products|read_only_injection],

  // DEVELOPER DOCUMENTATION (docs/)
  ADRs→docs/adr/[committed|developers|permanent],
  API_docs→docs/api/[committed|developers|permanent],
  setup_guides→docs/development/[committed|developers|permanent],

  // PROJECT GOVERNANCE (.hestai/ - committed, PR-controlled)
  product_north_star→.hestai/north-star/[committed|governance|stable],
  governance_decisions→.hestai/decisions/[committed|governance|stable],
  project_rules→.hestai/rules/[committed|governance|stable],
  project_schemas→.hestai/schemas/[committed|governance|stable],
  phase_specs[D2+D3+B1]→.hestai/rules/specs/[committed|governance|phase_scoped],
  phase_reports[B0-B3]→.hestai/state/reports/[shared|evidence|timestamped],
  phase_docs[B4_graduated]→docs/[committed|developers|permanent],
  implementation_specs[superseded]→.hestai/state/context/.archive/specs/[shared|ephemeral|archived],

  // PROJECT WORKING STATE (.hestai/state/ - shared via symlink, no PR)
  PROJECT-CONTEXT→.hestai/state/context/[shared|agents+human|living],
  APP-CONTEXT→.hestai/state/context/apps/{app}/[shared|agents+human|living],
  session_notes→.hestai/state/sessions/active/[shared|session_only|ephemeral],
  reports→.hestai/state/reports/[shared|humans+governance|durable_evidence],

  // DEBATE ARTIFACTS (debates/)
  debate_transcripts→debates/[split_tracking:json_ignored|octave_committed|cognitive_evidence|durable],

  // CLAUDE CODE INFRASTRUCTURE (.claude/)
  agent_definitions→.claude/agents/[committed|Claude_Code|infrastructure],
  project_skills→.claude/skills/[committed|Claude_Code|infrastructure]
]

===PHASE_DELIVERABLES===

// Lifecycle model: Spec (the plan) → Report (the evidence) → Doc (the product)
// Artifacts graduate through the lifecycle as phases progress

LIFECYCLE_PRIMITIVE::[
  SPEC[the_plan]→.hestai/rules/specs/[active_mutable_guidance],
  REPORT[the_evidence]→.hestai/state/reports/[timestamped_immutable_evidence],
  DOC[the_product]→docs/[permanent_developer_facing]
]

PHASE_MAPPING::[
  D1_NORTH_STAR→.hestai/north-star/[immutable_anchor],
  D2_IDEAS_CONSTRAINTS_DESIGN→.hestai/rules/specs/[active_spec],
  D3_BLUEPRINT→.hestai/rules/specs/[spec_MIGRATES_to_docs/_at_B1_gate],
  B0_VALIDATION→.hestai/state/reports/[gate_evidence|architectural_reasoning→docs/adr/],
  B1_BUILD_PLAN→.hestai/rules/specs/[task_breakdown_for_B2],
  B2_IMPLEMENTATION_LOG→.hestai/state/reports/[evidence_stream],
  B3_QA_SECURITY→.hestai/state/reports/[audit_trail],
  B4_HANDOFF_USER_GUIDE→docs/[graduated_permanent_documentation]
]

GRADUATION_RULES::[
  D3_blueprint→migrates_from_.hestai/rules/specs/_to_docs/_at_B1_gate,
  B0_architectural_decisions→recorded_as_ADRs_in_docs/adr/,
  B4_handoff_docs→graduate_from_draft_to_docs/_at_delivery
]

ADR_SUPREMACY::[
  RULE::"When in doubt between .hestai/decisions/ and docs/adr/ → choose docs/adr/",
  .hestai/decisions/→compiled_debate_decisions[agent_facing_OCTAVE_format_governance_outcomes],
  docs/adr/→all_architecture_implementation_design_decisions[developer_facing_markdown],
  .hestai/state/reports/→gate_passage_evidence[B0-B3],
  DISTINCTION::"debate-hall exports→.hestai/decisions/[.oct.md] | developer decisions→docs/adr/[.md]"
]

===ANTI_PATTERNS===

AVOID::[
  DUPLICATE_CONTENT::[
    problem::ADR_in_both_docs_and_.hestai,
    fix::ADRs_ONLY_in_docs/adr/
  ],

  MIX_ABSTRACTION_LEVELS::[
    problem::implementation_details_in_PROJECT-CONTEXT,
    fix::dashboard[PROJECT]→guides_to→detail[APP]
  ],

  COMMIT_EPHEMERAL::[
    problem::session_handoffs_cluttering_git_history,
    fix::.hestai/state/sessions/active/→shared_state
  ],

  DEVELOPER_DOCS_IN_HESTAI::[
    problem::developers_wont_find_setup_guides_in_.hestai,
    fix::developer_facing_docs→docs/
  ],

  NON_NORTH_STAR_IN_NORTH_STAR_FOLDER::[
    problem::workflow_specs_methodology_docs_in_.hestai/north-star/,
    fix::only_000-*-NORTH-STAR*_files_and_components/_subfolder_belong_in_north-star/
  ],

  CONFUSE_DECISIONS_WITH_ADRS::[
    problem::governance_decisions_placed_in_docs/adr/_or_ADRs_placed_in_.hestai/decisions/,
    fix::.hestai/decisions/→compiled_debate_decisions[governance]+docs/adr/→formal_ADRs[architecture]
  ]
]

===TIMELINE_TEST===

QUESTION::"Was_this_needed_BEFORE_code_existed_or_discovered_AFTER?"

TIMELINE_LOGIC::[
  BEFORE_code::design_decisions+architecture→docs/|.hestai/north-star/,
  AFTER_code::operational_state+progress_tracking→.hestai/state/context/,
  DURING_session::handoffs+resumption→.hestai/state/sessions/
]

===MIGRATION_GUIDANCE===

FROM_OLD→TO_THREE_TIER::[
  ADRs::.hestai/architecture-decisions/→docs/adr/,
  contexts::.hestai/context/→.hestai/state/context/[shared_via_symlink],
  north_star::.hestai/workflow/→.hestai/north-star/[committed_PR_controlled],
  decisions::.hestai/workflow/decisions/→.hestai/decisions/[committed_PR_controlled],
  sessions::.hestai/sessions/→.hestai/state/sessions/[shared_via_symlink],
  reports::.hestai/reports/→.hestai/state/reports/[shared_via_symlink],
  research::.hestai/research/→.hestai/state/research/[shared_via_symlink]
]

===FORMAT_RULES===

// When to use OCTAVE (.oct.md) vs Markdown (.md)

OCTAVE_FORMAT[.oct.md]::[
  agent_definitions,
  governance_rules,
  north_star_summaries[agent_consumed_compressed],
  methodology_docs,
  context_files[PROJECT-CONTEXT_etc],
  session_archives,
  compiled_debate_decisions
]

MARKDOWN_FORMAT[.md]::[
  north_star_full[human_authored_strategic_vision],
  developer_guides[setup_deployment],
  ADRs[architecture_decisions],
  READMEs[navigation_pointers],
  human_first_documentation
]

NOTE_NORTH_STAR_FORMAT::[
  000-*-NORTH-STAR.md→.md[human_authored_founding_document],
  000-*-NORTH-STAR-SUMMARY.oct.md→.oct.md[agent_optimized_extraction],
  RATIONALE::"Full North Stars are strategic vision prose written by humans; summaries are compressed for agent consumption"
]

FORMAT_DECISION_TREE::[
  "Primary audience AI agents?"→YES→.oct.md,
  "Standards/methodology/system-standard?"→YES→.oct.md,
  "Primary audience human developers?"→YES→.md,
  "ADR or setup guide?"→YES→.md
]

===FILE_RETENTION_POLICY===

// Ratified by ADR-0060: JSON ephemeral, OCTAVE permanent
// See: docs/adr/adr-0060-rfc-adr-alignment.md

CORE_PRINCIPLE::"Raw machine formats are ephemeral; semantic compressions are permanent"

RETENTION_TABLE::[
  FORMAT                  | GIT_STATUS  | RATIONALE
  ------------------------|-------------|------------------------------------------
  .json/.jsonl[raw]       | GITIGNORED  | Machine_format+large+reconstructible
  .oct.md[compressed]     | COMMITTED   | Semantic_density+human_readable+audit_trail
]

SESSION_ARCHIVES::[
  LOCATION::.hestai/state/sessions/archive/,
  GITIGNORED::[
    *-raw.jsonl[full_transcript_machine_format],
    *.verification.json[validation_metadata]
  ],
  COMMITTED::[
    *-octave.oct.md[compressed_semantic_transcript]
  ],
  WHY::raw_transcripts_are_large+reconstructible_from_octave_if_needed
]

DEBATE_TRANSCRIPTS::[
  LOCATION::debates/,
  GITIGNORED::[
    *.json[full_debate_machine_format]
  ],
  COMMITTED::[
    *.oct.md[compressed_debate_synthesis]
  ],
  WHY::debate_json_is_working_state+synthesis_captures_decision_value
]

RETENTION_DECISION_TREE::[
  "Is it raw machine format (.json/.jsonl)?"→YES→GITIGNORE,
  "Is it semantic compression (.oct.md)?"→YES→COMMIT,
  "Is it human-authored documentation?"→YES→COMMIT,
  "Is it active session state?"→YES→GITIGNORE
]

FUTURE_EVOLUTION::[
  EXTERNAL_ARTIFACT_STORE::Issue_#65[planned],
  RATIONALE::large_artifacts_may_move_to_cloud_storage,
  INTERIM_PATTERN::gitignore_now+external_store_later
]

===COMPATIBILITY===

WITH_NAMING_STANDARD::[
  .hestai-sys/standards/rules/visibility-rules.oct.md→answers["WHERE does artifact belong?"],
  .hestai-sys/standards/rules/naming-standard.oct.md→answers["HOW to name once placed?"]
]

WITH_HUB_AUTHORING_RULES::[
  .hestai-sys/standards/rules/visibility-rules.oct.md→answers["WHERE in PRODUCT?"],
  .hestai/rules/hub-authoring-rules.oct.md→answers["WHERE in SYSTEM governance payload?" ]
]

===AUTHORITY===

SOURCE::holistic-orchestrator_decision[2025-12-09]
RATIONALE::separate_developer_docs[git_visible]≠coordination_artifacts[agent_focused]
PATTERN::follows_HestAI_three_tier[ADMIN|DESIGN|BUILD_separation]
COMPANION::naming-standard.md[naming+frontmatter_logic]

===CHANGELOG===

v1.8::2026-03-04→clarified_north_star_format[full_.md_summary_.oct.md]+harmonized_RULE_4_and_ADR_SUPREMACY[.hestai/decisions/_is_compiled_debate_decisions_not_system_standard_amendments_only]+added_DISTINCTION_to_ADR_SUPREMACY[debate-hall_exports_vs_developer_ADRs]
v1.7::2026-03-04→added_PHASE_DELIVERABLES_section[lifecycle_model:Spec→Report→Doc]+phase_mapping_D1-B4+graduation_rules+ADR_SUPREMACY_policy+phase_deliverables_in_PLACEMENT_TABLE+phase_gate_evidence_in_RULE_6
v1.6::2026-02-26→fixed_ADR_path_to_docs/adr/[per_ADR-0031]+clarified_.hestai/decisions/_as_compiled_governance_decisions[not_ADRs]+expanded_.hestai-sys/library/_structure[skills/agents/patterns/schemas/octave]+added_system_skills_to_RULE_0+added_skill_distinction_NOTE_to_RULE_5+added_CONFUSE_DECISIONS_WITH_ADRS_anti-pattern+added_system_skills_to_PLACEMENT_TABLE
v1.5::2026-02-23→clarified_north-star_folder_strict_contents+expanded_rules_folder_scope+added_implementation_spec_placement+anti-pattern_for_north-star_contamination
v1.4::2025-12-27→added_FILE_RETENTION_POLICY_section[ADR-0060_ratification]
v1.3::2025-12-23→added_FORMAT_RULES_section+linked_HUB_AUTHORING_RULES
v1.2::2025-12-23→added_RULE_0_hub/_system_governance+clarified_hub_vs_.hestai_distinction
v1.1::2025-12-19→bundled_in_HestAI_MCP_Hub+OCTAVE_format_conversion
v1.1::2025-12-18→added_frontmatter+linked_companion_NAMING-STANDARD
v1.0::2025-12-09→initial_visibility_rules

===END===
