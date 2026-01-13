===NAMING_STANDARD===

META:
  TYPE::RULE
  NAME::"Naming Standard"
  VERSION::"1.0"
  PURPOSE::"Conventions for file naming and discoverability in system governance (.hestai-sys)"

METADATA::[
  type::standard,
  domain::governance,
  status::active,
  owners::[system-steward],
  created::2025-12-18,
  updated::2025-12-19,
  id::naming-standard,
  canonical::.hestai-sys/governance/rules/naming-standard.oct.md,
  source::src/hestai_mcp/_bundled_hub/governance/rules/naming-standard.oct.md,
  format::octave
]

===CORE_PRINCIPLE===

CONTENT→STRUCTURE→METADATA→FILENAME

LLM_RETRIEVAL_HIERARCHY::[
  1::chunked_content[highest_weight],
  2::headings_structure[high_weight],
  3::frontmatter_metadata[medium_weight],
  4::filenames[weak_context_signal]
]

THEREFORE::[
  frontmatter→carries_semantics_for_LLM_retrieval,
  folders→carry_context[no_repetition_in_filename],
  filenames→topic_focused+stable+human_readable,
  numbers→reserved_for_ordered_sequences_only,
  ".oct.md"→indicates_OCTAVE_compressed+LLM_canonical
]

===THREE_RULES===

RULE_1::lowercase_with_hyphens["auth-architecture.md"≠"Auth_Architecture.md"]
RULE_2::no_status_versions_in_filename[use_frontmatter≠"auth-v1.md"|"auth-draft.md"]
RULE_3::topic_focused[short+stable≠"101-DOC-PLATFORM-AUTH-ARCHITECTURE-V1.md"]

EXCEPTIONS::[ADRs["adr-0031-topic.md"],dates["2025-12-18-topic.md"],reports["report-001-topic.md"],whitelisted_system_files]
NOTE::RFCs_deprecated_per_ADR-0060[proposals_use_GitHub_Issues_only]

ISSUE_BASED_ALLOCATION::[
  PRINCIPLE::"GitHub Issue number = Document number (prevents multi-worktree clashes)",
  WORKFLOW::[
    1::create_GitHub_issue["ADR: Topic"],
    2::GitHub_assigns_unique_number[#31],
    3::create_document_using_issue_number["adr-0031-topic.md"],
    4::link_issue_in_frontmatter["GitHub Issue: [#31](url)"],
    5::discussion_in_issue_comments,
    6::PR_references_issue["Implements #31"]
  ],
  LABELS::["adr"]->GitHub_repo_labels,
  REFERENCE::docs/adr/adr-0031-github-issue-based-numbering.md,
  NOTE::RFCs_deprecated_per_ADR-0060[use_GitHub_Issues_for_proposals]
]

ENFORCEMENT::hook_blocks_violations→helpful_error_messages

===FILENAME_PATTERNS===

PATTERN_MATRIX::[
  STANDARD::{topic}.md→"auth-architecture.md"[most_documents],
  OCTAVE::{topic}.oct.md→"agent-binding.oct.md"[compressed_canonical],
  TEMPORAL::YYYY-MM-DD-{topic}.md→"2025-12-18-audit.md"[session_artifacts+incidents],
  ADR::adr-{ISSUE_NUMBER:04d}-{topic}.md→"adr-0031-use-postgresql.md"[architecture_decisions],
  REPORT::report-NNN-{topic}.md→"report-001-assessment.md"[formal_indexed_reports]
]
NOTE::RFC_pattern_removed_per_ADR-0060[proposals_now_in_GitHub_Issues]

NOTE_ISSUE_BASED::[
  ADR_numbers::come_from_GitHub_Issue_numbers[see_ISSUE_BASED_ALLOCATION],
  legacy_documents::migrated[adrs_renamed_to_issue_numbers],
  new_documents::MUST_use_issue_number_allocation,
  RFCs::deprecated_per_ADR-0060[use_GitHub_Issues_for_proposals]
]

DECISION_TREE::[
  IF::architecture_decision_record→create_GitHub_issue["ADR: Topic"]→adr-{ISSUE#:04d}-{topic}.md,
  IF::proposal_or_discussion→create_GitHub_issue_with_label["rfc"|"discussion"],
  IF::formal_indexed_report→report-NNN-{topic}.md,
  IF::session_artifact_or_incident→YYYY-MM-DD-{topic}.md,
  IF::well_known_conventional→exact_name[README.md|CHANGELOG.md],
  IF::hestai_system_file→exact_CAPS_name[PROJECT-CONTEXT.md|NAMING-STANDARD.md],
  IF::north_star_document→000-{PROJECT}-NORTH-STAR.md,
  DEFAULT→{lowercase-topic-with-hyphens}.md
]

===GOOD_FILENAMES===

EXAMPLES::[
  "auth-architecture.md",
  "jwt-key-rotation.md",
  "incident-api-timeouts.md",
  "agent-binding-protocol.md"
]

===FORBIDDEN_IN_FILENAMES===

VIOLATIONS→BLOCKED::[
  uppercase_letters::"Auth-Architecture.md"→"auth-architecture.md",
  underscores::"auth_architecture.md"→"auth-architecture.md",
  status_markers::"auth-draft.md"|"auth-final.md"→use_frontmatter["status: draft"],
  version_suffixes::"auth-v1.md"|"auth-v2.md"→use_git_history,
  categories_in_filename::"docs/standards/doc-standards.md"→"docs/standards/standards.md"[folder_provides_context],
  legacy_numeric_prefixes::"101-DOC-AUTH.md"→"auth.md"[except_ADRs+reports+dates]
]

WHY_SHORT_TOPIC_FOCUSED::[
  llm_friendly::reduces_noise_in_retrieval_contexts,
  stable::topics_dont_change[status_versions_do],
  referable::agents_cite["see `auth-architecture.md`"],
  human_scannable::meaningful_at_a_glance
]

===OCTAVE_FORMAT===

DECISION::".oct.md"→explicitly_indicates_OCTAVE_compressed+LLM_canonical

RULES::[
  ".oct.md"→first_class_canonical_documents,
  no_requirement→corresponding_.md_version,
  IF::uncompressed_source_exists→THEN[archival_only+non_discoverable+non_indexed]
]

IMPLICATIONS::[
  ".oct.md"≠generated_artifact→final_intended_form,
  original_markdown→IF_retained→THEN[.archive/|.sources/|_legacy/],
  visibility_rules→explicitly_exclude_source_folders
]

RATIONALE_LLM_FIRST::[
  eliminates_duplicate_semantic_embeddings,
  prevents_synthesis_collisions[compressed≠uncompressed],
  makes_OCTAVE_visible→humans+agents,
  aligns_filename_signaling→actual_canonical_usage
]

OPTIONAL_REINFORCEMENT::[
  header_marker::"===OCTAVE===" in_document_body,
  frontmatter_fields::format:octave+canonical:true
]

PROHIBITED::parallel_.md+.oct.md→same_discoverable_namespace[one_source_of_truth_per_topic]

===FRONTMATTER_STRUCTURE===

REQUIRED_FIELDS::[
  type::[architecture|guide|standard|decision|report|context],
  domain::[auth|platform|workflow|governance|agents|mcp|sessions|data|api],
  status::[proposed|draft|active|superseded|deprecated],
  owners::[owner-name],
  created::YYYY-MM-DD,
  updated::YYYY-MM-DD
]

REQUIRED_FOR_OCTAVE::[
  format::octave
]

RECOMMENDED_FIELDS::[
  id::stable_reference_slug,
  canonical::repo_relative_path,
  supersedes::previous_doc_name.md,
  tags::[additional_categorization]
]

STATUS_VOCABULARY::[
  proposed::under_review→exclude_from_synthesis[unless_history_requested],
  draft::work_in_progress→exclude_from_synthesis,
  active::current_authoritative→primary_retrieval_target,
  superseded::replaced_but_preserved→include_only_when_history_requested,
  deprecated::scheduled_for_removal→exclude_from_synthesis
]

DOMAIN_VOCABULARY::[
  auth::authentication+authorization+identity,
  platform::infrastructure+deployment+operations,
  workflow::processes+phases+methodology,
  governance::standards+rules+policies,
  agents::agent_definitions+binding+orchestration,
  mcp::MCP_tools+server_integration,
  sessions::session_lifecycle+context_management,
  data::schema+storage+migrations,
  api::external_interfaces+contracts
]

===ORDERED_SEQUENCES===

WHEN_NUMBERS_NEEDED::[
  ADRs::adr-{ISSUE#:04d}-{topic}.md→GitHub_issue_allocation+stable_identity+decision_graphs,
  INCIDENT_TIMELINES::YYYY-MM-DD-{topic}.md→chronological_sorting+temporal_context,
  SESSION_ARTIFACTS::YYYY-MM-DD-{topic}.md→session_scoped+audit_trail,
  GOVERNANCE_REPORTS::report-NNN-{topic}.md→cross_project_reference+formal_IDs
]
NOTE::RFCs_removed_per_ADR-0060[proposals_in_GitHub_Issues]

EXAMPLES::[
  "adr-0031-use-postgresql.md"[issue_#31],
  "2025-12-18-api-timeout-incident.md",
  "2025-12-17-auth-failure-postmortem.md",
  "report-001-architecture-assessment.md"
]

===FOLDER_BASED_CONTEXT===

PRINCIPLE::folders_carry_semantic_context→DO_NOT_repeat_in_filenames

STANDARD_STRUCTURE::[
  .hestai-sys/governance/rules/→visibility-rules.oct.md+naming-standard.oct.md,
  .hestai-sys/governance/workflow/→000-SYSTEM-HESTAI-NORTH-STAR.md,
  .hestai/context/→PROJECT-CONTEXT.md+PROJECT-CHECKLIST.md,
  .hestai/workflow/→north-star.md+decisions/DECISIONS.md,
  .hestai/sessions/active/→gitignored,
  .hestai/sessions/archive/→committed,
  .hestai/reports/→temporal_or_indexed_reports
]

FOLDER_SEMANTICS::[
  governance/rules/→standards+enforcement→topic["naming-standard.md"],
  workflow/→processes+methodology→purpose["north-star.md"],
  context/→operational_state→entity["PROJECT-CONTEXT.md"],
  reports/→evidence+audits→event_finding["api-timeout-incident.md"],
  sessions/archive/→historical_records→date_topic["2025-12-18-session.md"]
]

===EXCEPTIONS_WHITELISTED===

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
  CONSTITUTION.md,
  current_state.oct.md[underscore_for_MCP_compatibility]
]

GOVERNANCE_RULES_DIRECTORY::ALL_files_in[.hestai-sys/governance/rules/]→whitelisted_CAPS[system_level_governance]

GOVERNANCE_WORKFLOW_DIRECTORY::ALL_files_in[.hestai-sys/governance/workflow/]→whitelisted_CAPS[system_level_governance+process_methodology]

NORTH_STAR_PATTERN::[
  format::000-{PROJECT}-NORTH-STAR.md,
  reason::governance_file+CAPS_treatment+000_prefix_sorts_first,
  hook_pattern::"*NORTH-STAR*",
  examples::[
    "000-LIVING-ORCHESTRA-NORTH-STAR.md",
    "000-LIVING-ORCHESTRA-NORTH-STAR-SUMMARY.oct.md",
    "000-ODYSSEAN-ANCHOR-NORTH-STAR.md"
  ]
]

===VALIDATION_PATTERNS===

REGEX_STANDARD_TOPIC::"^[a-z0-9]+(-[a-z0-9]+)*(\.oct)?\.md$"
REGEX_DATE_PREFIXED::"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$"
REGEX_ADR::"^adr-\d{4}-[a-z0-9-]+\.md$"
REGEX_REPORT::"^report-\d{3}-[a-z0-9-]+\.md$"
NOTE::REGEX_RFC_removed_per_ADR-0060
REGEX_WHITELIST::"^(README|LICENSE|CONTRIBUTING|CHANGELOG|SECURITY|CODE_OF_CONDUCT|CLAUDE|CODEOWNERS|ARCHITECTURE|PROJECT-CONTEXT|PROJECT-CHECKLIST|PROJECT-HISTORY|PROJECT-ROADMAP|APP-CONTEXT|APP-CHECKLIST|DECISIONS|VISIBILITY-RULES|NAMING-STANDARD|CONSTITUTION)(\\.md)?$"
REGEX_NORTH_STAR::"^000-[A-Z0-9-]+-NORTH-STAR(-SUMMARY)?(\.oct)?\.md$"

FILENAME_MUST::[
  lowercase_letters+numbers+hyphens[or_match_whitelist],
  topic_focused[noun_based],
  stable_over_lifecycle
]

FILENAME_MUST_NOT::[
  status_markers[draft|final],
  version_suffixes[v1|v2],
  repeat_folder_context,
  use_underscores[use_hyphens_instead]
]

===COMPATIBILITY===

WITH_VISIBILITY_RULES::[
  VISIBILITY_RULES.md→answers["WHERE does artifact belong?"],
  NAMING_STANDARD.md→answers["HOW to name once placed?"]
]

DECISION_FLOW::[
  1::determine_artifact_type→VISIBILITY_RULES.md→folder_placement,
  2::determine_if_ordered→ADR|temporal|indexed→number_date_prefix,
  3::choose_topic_name→short+noun_focused+stable,
  4::add_frontmatter→type+domain+status+owners+dates
]

===MIGRATION_LEGACY===

OLD_PATTERN_DEPRECATED::{NNN}-{CONTEXT}[-{QUALIFIER}]-{NAME}.{EXT}
EXAMPLE_OLD::"101-DOC-STRUCTURE-AND-NAMING-STANDARDS.oct.md"

NEW_PATTERN::{topic-focused-name}.md+frontmatter
EXAMPLE_NEW::"naming-standard.md"[with_type:standard_in_frontmatter]

===AUTHORITY===

SOURCE::system_steward_analysis+LLM_first_research[2025-12-18]
SUPERSEDES::101-DOC-STRUCTURE-AND-NAMING-STANDARDS.oct.md[for_new_artifacts]
COMPANION::VISIBILITY-RULES.md[placement_logic]
VERSION::1.3[governance_workflow_directory_whitelist]

===CHANGELOG===

v1.3::2026-01-13→added_GOVERNANCE_WORKFLOW_DIRECTORY_rule[whitelists_CAPS_in_.hestai-sys/governance/workflow/+fixes_naming_gap_for_process_methodology_docs]
v1.2::2025-12-24→issue_based_document_numbering[RFC-0031]+RFC_pattern_added+grandfathering_legacy_docs
v1.1::2025-12-19→bundled_in_HestAI_MCP_Hub+OCTAVE_format_conversion
v1.1::2025-12-18→lifecycle_statuses+controlled_vocabulary+.oct.md_canonical+whitelist+stable_references+regex_patterns
v1.0::2025-12-18→initial_LLM_first_naming_standard

===END===
