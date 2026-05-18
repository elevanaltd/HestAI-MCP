===NAMING_STANDARD===
META:
  TYPE::RULE
  NAME::"Naming Standard"
  VERSION::"1.4"
  PURPOSE::"Conventions for file naming and discoverability in system governance (.hestai-sys)"
  CANONICAL::".hestai-sys/standards/rules/naming-standard.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/standards/rules/naming-standard.oct.md"
METADATA::[
  type::standard,
  domain::governance,
  status::active,
  owners::[system-steward],
  created::"2025-12-18",
  updated::"2026-05-16",
  id::naming-standard,
  canonical::".hestai-sys/standards/rules/naming-standard.oct.md",
  source::"src/hestai_mcp/_bundled_hub/standards/rules/naming-standard.oct.md",
  format::octave
]
§1::CORE_PRINCIPLE
  FLOW::CONTENT→STRUCTURE→METADATA→FILENAME
  LLM_RETRIEVAL_HIERARCHY::[
    R1::chunked_content<highest_weight>,
    R2::headings_structure<high_weight>,
    R3::frontmatter_metadata<medium_weight>,
    R4::filenames<weak_context_signal>
  ]
  THEREFORE::[
    frontmatter→carries_semantics_for_LLM_retrieval,
    folders→carry_context,
    filenames→topic_focused⊕stable⊕human_readable,
    numbers→reserved_for_ordered_sequences_only,
    oct_md_suffix→indicates_OCTAVE_compressed⊕LLM_canonical
  ]
§2::THREE_RULES
  RULE_1::"lowercase_with_hyphens — auth-architecture.md NOT Auth_Architecture.md"
  RULE_2::"no_status_versions_in_filename — use_frontmatter, avoid auth-v1.md or auth-draft.md"
  RULE_3::"topic_focused — short⊕stable, avoid 101-DOC-PLATFORM-AUTH-ARCHITECTURE-V1.md"
  EXCEPTIONS::[
    ADRs::adr-0031-topic.md,
    dates::"2025-12-18-topic.md",
    reports::report-001-topic.md,
    whitelisted_system_files
  ]
  RFC_NOTE::RFCs_deprecated_per_ADR-0060<proposals_use_GitHub_Issues_only>
  ENFORCEMENT::hook_blocks_violations→helpful_error_messages
§3::ISSUE_BASED_ALLOCATION
  PRINCIPLE::"GitHub Issue number = Document number (prevents multi-worktree clashes)"
  WORKFLOW::[
    STEP_1::"create_GitHub_issue titled ADR: Topic",
    STEP_2::GitHub_assigns_unique_number,
    STEP_3::"create_document_using_issue_number adr-0031-topic.md",
    STEP_4::"link_issue_in_frontmatter GitHub Issue 31",
    STEP_5::discussion_in_issue_comments,
    STEP_6::"PR_references_issue Implements 31"
  ]
  LABELS::"[adr] → GitHub_repo_labels"
  REFERENCE::"docs/adr/adr-0031-github-issue-based-numbering.md"
  RFC_NOTE::RFCs_deprecated_per_ADR-0060<use_GitHub_Issues_for_proposals>
§4::FILENAME_PATTERNS
  PATTERN_MATRIX::[
    STANDARD::"topic.md → auth-architecture.md [most_documents]",
    OCTAVE::"topic.oct.md → agent-binding.oct.md [compressed_canonical]",
    TEMPORAL::"YYYY-MM-DD-topic.md → 2025-12-18-audit.md [session_artifacts⊕incidents]",
    ADR::"adr-NNNN-topic.md → adr-0031-use-postgresql.md [architecture_decisions]",
    REPORT::"report-NNN-topic.md → report-001-assessment.md [formal_indexed_reports]"
  ]
  RFC_NOTE::RFC_pattern_removed_per_ADR-0060<proposals_now_in_GitHub_Issues>
  ISSUE_BASED_NOTE::[
    ADR_numbers::come_from_GitHub_Issue_numbers,
    legacy_documents::migrated_adrs_renamed_to_issue_numbers,
    new_documents::MUST_use_issue_number_allocation,
    RFCs::deprecated_per_ADR-0060
  ]
  DECISION_TREE::[
    IF::architecture_decision_record→create_GitHub_issue→adr_NNNN_topic_md,
    IF::proposal_or_discussion→create_GitHub_issue_with_label,
    IF::formal_indexed_report→report_NNN_topic_md,
    IF::session_artifact_or_incident→YYYY_MM_DD_topic_md,
    IF::well_known_conventional→exact_name,
    IF::hestai_system_file→exact_CAPS_name,
    IF::"north_star_document→000-PROJECT-NORTH-STAR.md",
    DEFAULT→lowercase_topic_with_hyphens
  ]
§5::GOOD_FILENAMES
  GOOD_EXAMPLES::[
    auth-architecture.md,
    jwt-key-rotation.md,
    incident-api-timeouts.md,
    agent-binding-protocol.md
  ]
§6::FORBIDDEN_IN_FILENAMES
  VIOLATIONS_BLOCKED::[
    uppercase_letters::"Auth-Architecture.md → auth-architecture.md",
    underscores::"auth_architecture.md → auth-architecture.md",
    status_markers::"avoid auth-draft.md or auth-final.md → use_frontmatter_status",
    version_suffixes::"avoid auth-v1.md or auth-v2.md → use_git_history",
    categories_in_filename::"docs/standards/doc-standards.md → docs/standards/standards.md",
    legacy_numeric_prefixes::"101-DOC-AUTH.md → auth.md (except ADRs, reports, dates)"
  ]
  WHY_SHORT_TOPIC_FOCUSED::[
    llm_friendly::reduces_noise_in_retrieval_contexts,
    stable::topics_dont_change_status_versions_do,
    referable::agents_cite_filename_directly,
    human_scannable::meaningful_at_a_glance
  ]
§7::OCTAVE_FORMAT
  DECISION::"oct_md_suffix → explicitly_indicates_OCTAVE_compressed ⊕ LLM_canonical"
  RULES::[
    oct_md→preferred_canonical_for_AI_agents,
    plain_md→acceptable_for_human_facing_prose,
    parallel_md_and_oct_md→PERMITTED_no_archival_requirement,
    oct_md_is_final_intended_form→NOT_generated_artifact
  ]
  RATIONALE_LLM_FIRST::[
    signals_compressed_form_to_LLMs_without_forcing_eviction_of_human_md,
    aligns_with_tooling_that_consumes_OCTAVE_META_block_not_YAML_frontmatter,
    makes_OCTAVE_visible_to_humans_and_agents,
    filename_signaling_aligns_with_actual_canonical_usage
  ]
  OPTIONAL_REINFORCEMENT::[
    header_marker::"===NAME=== envelope in document body",
    meta_block_fields::[
      TYPE,
      NAME,
      VERSION,
      PURPOSE
    ],
    REINFORCEMENT_NOTE::"OCTAVE META: block is the authoritative metadata source — not YAML frontmatter"
  ]
§8::ORDERED_SEQUENCES
  WHEN_NUMBERS_NEEDED::[
    ADRs::"adr-NNNN-topic.md → GitHub_issue_allocation ⊕ stable_identity ⊕ decision_graphs",
    INCIDENT_TIMELINES::"YYYY-MM-DD-topic.md → chronological_sorting ⊕ temporal_context",
    SESSION_ARTIFACTS::"YYYY-MM-DD-topic.md → session_scoped ⊕ audit_trail",
    GOVERNANCE_REPORTS::"report-NNN-topic.md → cross_project_reference ⊕ formal_IDs"
  ]
  RFC_NOTE::RFCs_removed_per_ADR-0060<proposals_in_GitHub_Issues>
  SEQUENCE_EXAMPLES::[
    adr-0031-use-postgresql.md,
    "2025-12-18-api-timeout-incident.md",
    "2025-12-17-auth-failure-postmortem.md",
    report-001-architecture-assessment.md
  ]
§9::FOLDER_BASED_CONTEXT
  PRINCIPLE::folders_carry_semantic_context→DO_NOT_repeat_in_filenames
  STANDARD_STRUCTURE::[
    ".hestai-sys/standards/rules/ → visibility-rules.oct.md, naming-standard.oct.md",
    ".hestai-sys/standards/workflow/ → 000-SYSTEM-HESTAI-NORTH-STAR.md",
    ".hestai/north-star/ → 000-PROJECT-NORTH-STAR.md ⊕ components/",
    ".hestai/decisions/ → architectural_decision_records",
    ".hestai/state/context/ → PROJECT-CONTEXT.md ⊕ PROJECT-CHECKLIST.md",
    ".hestai/state/sessions/active/ → gitignored",
    ".hestai/state/sessions/archive/ → shared",
    ".hestai/state/reports/ → temporal_or_indexed_reports"
  ]
  FOLDER_SEMANTICS::[
    "standards/rules/ → standards⊕enforcement → topic e.g. naming-standard.md",
    "workflow/ → processes⊕methodology → purpose e.g. north-star.md",
    "context/ → operational_state → entity e.g. PROJECT-CONTEXT.md",
    "reports/ → evidence⊕audits → event_finding e.g. api-timeout-incident.md",
    "sessions/archive/ → historical_records → date_topic e.g. 2025-12-18-session.md"
  ]
§10::EXCEPTIONS_WHITELISTED
  CONVENTIONAL_FILES::[
    README.md,
    LICENSE,
    CONTRIBUTING.md,
    CHANGELOG.md,
    SECURITY.md,
    CODE_OF_CONDUCT.md,
    CLAUDE.md,
    CODEOWNERS,
    ARCHITECTURE.md
  ]
  HESTAI_SYSTEM_FILES::[
    PROJECT-CONTEXT.md,
    PROJECT-CHECKLIST.md,
    PROJECT-HISTORY.md,
    PROJECT-ROADMAP.md,
    APP-CONTEXT.md,
    APP-CHECKLIST.md,
    DECISIONS.md,
    VISIBILITY-RULES.md,
    NAMING-STANDARD.md,
    TEST-STRUCTURE-STANDARD.md,
    SYSTEM-STANDARD.md,
    "current_state.oct.md (underscore for MCP compatibility)"
  ]
  STANDARDS_RULES_DIRECTORY::"ALL files in .hestai-sys/standards/rules/ → whitelisted_CAPS [system_level_standards]"
  STANDARDS_WORKFLOW_DIRECTORY::"ALL files in .hestai-sys/standards/workflow/ → whitelisted_CAPS [system_level_standards ⊕ process_methodology]"
  NORTH_STAR_PATTERN::[
    format::"000-PROJECT-NORTH-STAR.md",
    reason::"governance_file ⊕ CAPS_treatment ⊕ 000_prefix_sorts_first",
    hook_pattern::"NORTH-STAR substring match",
    NORTH_STAR_EXAMPLES::[
      "000-LIVING-ORCHESTRA-NORTH-STAR.md",
      "000-LIVING-ORCHESTRA-NORTH-STAR-SUMMARY.oct.md",
      "000-ODYSSEAN-ANCHOR-NORTH-STAR.md"
    ]
  ]
  PRE_EXISTING_FILES::[
    rule::naming_standard_applies_to_new_files_only,
    rationale::edits_to_legacy_files_must_not_be_blocked_by_filename,
    enforcement::hook_skips_validation_when_file_already_exists
  ]
§11::VALIDATION_PATTERNS
  REGEX_STANDARD_TOPIC::"^[a-z0-9]+(-[a-z0-9]+)*(\\.oct)?\\.md$"
  REGEX_DATE_PREFIXED::"^\\d{4}-\\d{2}-\\d{2}-[a-z0-9-]+\\.md$"
  REGEX_ADR::"^adr-\\d{4}-[a-z0-9-]+\\.md$"
  REGEX_REPORT::"^report-\\d{3}-[a-z0-9-]+\\.md$"
  REGEX_RFC_NOTE::REGEX_RFC_removed_per_ADR-0060
  REGEX_WHITELIST::"^(README|LICENSE|CONTRIBUTING|CHANGELOG|SECURITY|CODE_OF_CONDUCT|CLAUDE|CODEOWNERS|ARCHITECTURE|PROJECT-CONTEXT|PROJECT-CHECKLIST|PROJECT-HISTORY|PROJECT-ROADMAP|APP-CONTEXT|APP-CHECKLIST|DECISIONS|VISIBILITY-RULES|NAMING-STANDARD|SYSTEM-STANDARD)(\\.md)?$"
  REGEX_NORTH_STAR::"^000-[A-Z0-9-]+-NORTH-STAR(-SUMMARY)?(\\.oct)?\\.md$"
  FILENAME_MUST::[
    lowercase_letters_numbers_hyphens_or_match_whitelist,
    topic_focused_noun_based,
    stable_over_lifecycle
  ]
  FILENAME_MUST_NOT::[
    status_markers_draft_or_final,
    version_suffixes_v1_or_v2,
    repeat_folder_context,
    use_underscores_instead_of_hyphens
  ]
§12::COMPATIBILITY
  WITH_VISIBILITY_RULES::[VISIBILITY_RULES_md→answers_WHERE_does_artifact_belong,NAMING_STANDARD_md→answers_HOW_to_name_once_placed]
  DECISION_FLOW::[
    STEP_1::determine_artifact_type→VISIBILITY_RULES→folder_placement,
    STEP_2::determine_if_ordered→ADR_or_temporal_or_indexed→number_or_date_prefix,
    STEP_3::choose_topic_name→short⊕noun_focused⊕stable,
    STEP_4::use_OCTAVE_META_block→for_oct_md_files
  ]
§13::MIGRATION_LEGACY
  OLD_PATTERN_DEPRECATED::NNN-CONTEXT-QUALIFIER-NAME.EXT
  EXAMPLE_OLD::"101-DOC-STRUCTURE-AND-NAMING-STANDARDS.oct.md"
  NEW_PATTERN::"topic-focused-name.md + frontmatter"
  EXAMPLE_NEW::"naming-standard.md (with type:standard in frontmatter)"
  LEGACY_FILE_HANDLING::[
    edits_to_legacy_nonconformant_files→PERMITTED,
    new_files_or_renames→MUST_match_current_standard,
    opportunistic_rename→encouraged_when_touching_file_substantively
  ]
§14::AUTHORITY
  SOURCE::"system_steward_analysis ⊕ LLM_first_research [2025-12-18]"
  SUPERSEDES::"101-DOC-STRUCTURE-AND-NAMING-STANDARDS.oct.md [for_new_artifacts]"
  COMPANION::"VISIBILITY-RULES.md [placement_logic]"
  AUTHORITY_VERSION::"1.4"
§15::CHANGELOG
  v1_4::"2026-05-16 → removed FRONTMATTER_STRUCTURE section ⊕ softened OCTAVE_FORMAT (parallel files PERMITTED) ⊕ added PRE_EXISTING_FILES clause ⊕ added LEGACY_FILE_HANDLING ⊕ quoted META timestamps"
  v1_3::"2026-01-13 → added STANDARDS_WORKFLOW_DIRECTORY rule (whitelists CAPS in .hestai-sys/standards/workflow/, fixes naming gap for process methodology docs)"
  v1_2::"2025-12-24 → issue based document numbering (RFC-0031) ⊕ RFC pattern added ⊕ grandfathering legacy docs"
  v1_1b::"2025-12-19 → bundled in HestAI MCP Hub ⊕ OCTAVE format conversion"
  v1_1a::"2025-12-18 → lifecycle statuses ⊕ controlled vocabulary ⊕ oct_md canonical ⊕ whitelist ⊕ stable references ⊕ regex patterns"
  v1_0::"2025-12-18 → initial LLM first naming standard"
===END===
