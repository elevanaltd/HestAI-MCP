===VISIBILITY_RULES===

META:
  TYPE::STANDARD
  ID::visibility-rules
  VERSION::"1.1"
  STATUS::ACTIVE
  PURPOSE::"Placement and lifecycle rules for artifacts to ensure discoverability"
  DOMAIN::governance
  OWNERS::[system-steward]
  CREATED::2025-12-09
  UPDATED::2025-12-19
  CANONICAL::hub/governance/rules/visibility-rules.oct.md
  TAGS::[placement, visibility, documentation, lifecycle]

===CORE_PRINCIPLE===

LOCATION=VISIBILITY+PERMANENCE

PLACEMENT_LOGIC::[
  developer_docs→git_visibility[committed],
  coordination_artifacts→ephemeral[gitignored],
  placement→determines_audience+lifecycle
]

===PLACEMENT_RULES===

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
    docs/architecture-decisions/→[001-monorepo-structure.md|002-authentication-pattern.md],
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

RULE_2::OPERATIONAL_STATE→.hestai/context/::[
  AUDIENCE::AI_agents+human_coordination,
  LIFECYCLE::living_documents+high_churn,
  TRACKING::git_committed[agent_context_awareness],

  WHAT_GOES_HERE::[
    PROJECT-CONTEXT.md[system_dashboard],
    PROJECT-CHECKLIST.md[high_level_tasks],
    PROJECT-HISTORY.md[significant_events],
    app_specific_contexts[APP-CONTEXT.md|APP-CHECKLIST.md|APP-HISTORY.md]
  ],

  STRUCTURE::[
    .hestai/context/→[PROJECT-CONTEXT.md|PROJECT-CHECKLIST.md|PROJECT-HISTORY.md],
    .hestai/context/apps/{app}/→[APP-CONTEXT.md|APP-CHECKLIST.md|APP-HISTORY.md],
    .hestai/context/.archive/→gitignored[deprecated_docs]
  ],

  WHY_.hestai_context::[
    agents_need_fresh_context_per_invocation,
    dashboard_pattern[PROJECT→APP_details],
    high_update_frequency→would_pollute_commits,
    git_tracking→enables_agent_awareness,
    separate_from_developer_docs
  ]
]

RULE_3::SESSION_ARTIFACTS→.hestai/sessions/::[
  AUDIENCE::session_continuity+audit_trail,
  LIFECYCLE::active→archived,
  TRACKING::split_policy[active_ignored|archive_committed],

  WHAT_GOES_HERE::[
    active_session_working_state[in_progress],
    archived_session_transcripts[durable],
    derived_artifacts[durable]
  ],

  STRUCTURE::[
    .hestai/sessions/active/{session_id}/→gitignored[session.json|anchor.json],
    .hestai/sessions/archive/→committed[
      YYYY-MM-DD-{focus}-{id}-raw.jsonl,
      YYYY-MM-DD-{focus}-{id}-octave.oct.md,
      YYYY-MM-DD-{focus}-{id}.verification.json
    ]
  ],

  WHY_split_tracking::[
    active→high_churn+partial_inconsistent_state,
    archive→durable_record[continuity+auditability],
    prevents_commit_noise→keeps_immutable_trail
  ]
]

RULE_4::WORKFLOW_METHODOLOGY→.hestai/workflow/::[
  AUDIENCE::AI_agents+system_governance,
  LIFECYCLE::committed+stable_patterns,
  TRACKING::git_history_tracks_methodology_evolution,

  WHAT_GOES_HERE::[
    north_star_documents[immutable_requirements],
    workflow_phase_definitions,
    DECISIONS.md[architectural_rationale_tokens],
    test_infrastructure_standards,
    binding_patterns_protocols
  ],

  STRUCTURE::[
    .hestai/workflow/→000-{PROJECT}-NORTH-STAR.md,
    .hestai/workflow/decisions/→DECISIONS.md,
    .hestai/workflow/test-context/→[RULES.md|EXTRACTION-TESTING-POLICY.md|SUPABASE-HARNESS.md]
  ],

  WHY_.hestai_workflow::[
    methodology_governance≠implementation_docs,
    binding_patterns→agents_must_follow,
    stable_enough_for_git_tracking,
    cross_project_patterns_standards
  ]
]

RULE_5::CLAUDE_CODE_CONFIG→.claude/::[
  AUDIENCE::Claude_Code_CLI_infrastructure,
  LIFECYCLE::committed+synchronized_across_projects,
  TRACKING::git+sync_commands[cfg-config-sync],

  WHAT_GOES_HERE::[
    agent_constitutions[.oct.md_files],
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
  ]
]

RULE_6::REPORTS→.hestai/reports/::[
  AUDIENCE::humans+reviewers+governance,
  LIFECYCLE::durable+time_scoped_evidence,
  TRACKING::committed[optional_gitignored_scratch_subdir],

  WHAT_GOES_HERE::[
    audit_reports[anchor_audits|gate_failures|integrity_checks],
    security_scan_outputs[redaction_summaries|findings],
    operational_diagnostics["why_clock_out_failed"],
    quality_gate_evidence[retained_beyond_single_session]
  ],

  STRUCTURE::[
    .hestai/reports/→[
      YYYY-MM-DD-anchor-audit-clockout-clean-on-success.md,
      YYYY-MM-DD-jsonl-secrets-scan-findings.json
    ],
    .hestai/reports/scratch/→gitignored[local_experiments]
  ],

  WHY_.hestai_reports::[
    evidence_discoverable≠polluting_docs,
    separates_durable_evidence≠living_dashboard[.hestai/context/],
    stable_location["what_happened_and_why"]
  ]
]

===DECISION_MATRIX===

PLACEMENT_TABLE::[
  ADRs→docs/architecture-decisions/[committed|developers|permanent],
  API_docs→docs/api/[committed|developers|permanent],
  setup_guides→docs/development/[committed|developers|permanent],
  PROJECT-CONTEXT→.hestai/context/[committed|agents+human|living],
  APP-CONTEXT→.hestai/context/apps/{app}/[committed|agents+human|living],
  session_notes→.hestai/sessions/active/[ignored|session_only|ephemeral],
  north_star→.hestai/workflow/[committed|governance|stable],
  DECISIONS.md→.hestai/workflow/decisions/[committed|governance|stable],
  test_standards→.hestai/workflow/test-context/[committed|governance|stable],
  agent_constitutions→.claude/agents/[committed|Claude_Code|infrastructure],
  skills→.claude/skills/[committed|Claude_Code|infrastructure],
  reports→.hestai/reports/[committed|humans+governance|durable_evidence]
]

===ANTI_PATTERNS===

AVOID::[
  DUPLICATE_CONTENT::[
    problem::ADR_in_both_docs_and_.hestai,
    fix::ADRs_ONLY_in_docs/architecture-decisions/
  ],

  MIX_ABSTRACTION_LEVELS::[
    problem::implementation_details_in_PROJECT-CONTEXT,
    fix::dashboard[PROJECT]→guides_to→detail[APP]
  ],

  COMMIT_EPHEMERAL::[
    problem::session_handoffs_cluttering_git_history,
    fix::.hestai/sessions/active/→gitignored
  ],

  DEVELOPER_DOCS_IN_HESTAI::[
    problem::developers_wont_find_setup_guides_in_.hestai,
    fix::developer_facing_docs→docs/
  ]
]

===TIMELINE_TEST===

QUESTION::"Was_this_needed_BEFORE_code_existed_or_discovered_AFTER?"

TIMELINE_LOGIC::[
  BEFORE_code::design_decisions+architecture→docs/|.hestai/workflow/,
  AFTER_code::operational_state+progress_tracking→.hestai/context/,
  DURING_session::handoffs+resumption→.hestai/sessions/[gitignored]
]

===MIGRATION_GUIDANCE===

FROM_.hestai→TO_NEW_STRUCTURE::[
  ADRs::.hestai/architecture-decisions/→docs/architecture-decisions/,
  contexts::.hestai/PROJECT-CONTEXT.md→.hestai/context/PROJECT-CONTEXT.md,
  workflow::.hestai/workflow-docs/→.hestai/workflow/,
  decisions::.hestai/DECISIONS.md→.hestai/workflow/decisions/DECISIONS.md,
  sessions::.hestai/sessions/→.hestai/sessions/[keep_gitignored],
  reports::.hestai/reports/→.hestai/reports/
]

===COMPATIBILITY===

WITH_NAMING_STANDARD::[
  VISIBILITY_RULES.md→answers["WHERE does artifact belong?"],
  NAMING_STANDARD.md→answers["HOW to name once placed?"]
]

===AUTHORITY===

SOURCE::holistic-orchestrator_decision[2025-12-09]
RATIONALE::separate_developer_docs[git_visible]≠coordination_artifacts[agent_focused]
PATTERN::follows_HestAI_three_tier[ADMIN|DESIGN|BUILD_separation]
COMPANION::naming-standard.md[naming+frontmatter_logic]

===CHANGELOG===

v1.1::2025-12-19→bundled_in_HestAI_MCP_Hub+OCTAVE_format_conversion
v1.1::2025-12-18→added_frontmatter+linked_companion_NAMING-STANDARD
v1.0::2025-12-09→initial_visibility_rules

===END===
