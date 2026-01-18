===GITHUB_LABEL_VALIDATION===

META:
  TYPE::RULE
  NAME::"GitHub Label Validation"
  VERSION::"1.0"
  PURPOSE::"Prevent processing waste from invalid GitHub labels in issue creation"

METADATA::[
  type::governance_rule,
  domain::developer_workflow,
  status::active,
  owners::[system-steward],
  created::2025-01-18,
  updated::2025-01-18,
  id::github-label-validation,
  canonical::.hestai-sys/governance/rules/github-label-validation.oct.md,
  source::src/hestai_mcp/_bundled_hub/governance/rules/github-label-validation.oct.md,
  format::octave
]

===PROBLEM===

SYMPTOM::agents_waste_processing_time_on_invalid_labels
COST::[
  failed_gh_issue_create,
  error_analysis,
  label_identification,
  command_rewrite,
  retry_operation
]
TYPICAL_ERROR::"could not add label: 'X' not found"

===SOLUTION===

ARCHITECTURE::two_layer_defense[
  LAYER_1::pre_submit_hook[automatic_validation],
  LAYER_2::skill_reference[educational_documentation]
]

§1::PRE_SUBMIT_HOOK

LOCATION::~/.claude/hooks/user_prompt_submit/validate-gh-labels.ts
MECHANISM::intercept_gh_issue_create_with_labels

PROCESS::[
  1::detect_command["gh issue create" + "--label"],
  2::extract_requested_labels[regex_parsing],
  3::fetch_valid_labels[gh_label_list + 5min_cache],
  4::filter_invalid_labels[comparison],
  5::rebuild_command[valid_labels_only],
  6::warn_agent[educational_feedback]
]

ERROR_HANDLING::[
  IF::validation_fails,
  THEN::pass_through_original[never_block_work]
]

EXAMPLE::[
  INPUT::"gh issue create --label 'invalid,enhancement,p1'",
  OUTPUT::"gh issue create --label 'enhancement'",
  WARNING::"Invalid labels removed: invalid, p1"
]

§2::SKILL_REFERENCE

LOCATION::.hestai-sys/library/skills/github-labels/SKILL.md
PURPOSE::educational_reference_for_valid_taxonomy

TRIGGER_PATTERNS::[
  "gh issue create",
  "create.*issue",
  "github.*label",
  "what labels",
  "valid labels"
]

LABEL_CATEGORIES::[
  STANDARD::[bug,enhancement,documentation,duplicate],
  PRIORITY::["priority:p0-critical","priority:p1-high","priority:p2-medium","priority:p3-low"],
  PHASE::["phase:b1","phase:b2","phase:future"],
  AREA::["area:mcp-tools","area:governance","area:ci-cd","area:agents"],
  STATUS::["status:blocked","status:needs-discussion","status:implementation-pending"],
  DOCUMENT::[adr,rfc_deprecated],
  MILESTONE::["milestone:b1-foundation","milestone:b2-features","milestone:b3-integration"]
]

COMMON_MISTAKES::[
  ❌::["p0","p1","p2"]→missing_prefix,
  ❌::["b1","b2"]→missing_prefix,
  ❌::["mcp-tools"]→missing_area_prefix,
  ✅::["priority:p1-high","phase:b1","area:mcp-tools"]→correct
]

===BENEFITS===

ELIMINATION::label_errors_prevented_before_execution
TIME_SAVINGS::no_retry_cycles_on_failed_issue_creation
EDUCATION::agents_learn_correct_taxonomy_over_time
MAINTENANCE::labels_fetched_dynamically_no_manual_updates
NON_INTRUSIVE::works_silently_warns_only_when_needed

===INTEGRATION===

HOOK_EXECUTION::[
  WHEN::agent_submits_gh_issue_create_with_labels,
  VALIDATE::labels_against_repository_taxonomy,
  STRIP::invalid_labels,
  WARN::agent_of_changes,
  SUGGEST::consult_github_labels_skill
]

SKILL_ACTIVATION::[
  WHEN::agent_mentions_github_issues_or_labels,
  PROVIDE::comprehensive_label_reference,
  DOCUMENT::naming_conventions_and_categories,
  INCLUDE::usage_examples_and_common_errors
]

===IMPLEMENTATION===

FILES::[
  HOOK::~/.claude/hooks/user_prompt_submit/validate-gh-labels.ts,
  SKILL::.hestai-sys/library/skills/github-labels/SKILL.md,
  GLOBAL::~/.claude/skills/github-labels/SKILL.md
]

DEPENDENCIES::[
  gh_cli::installed_and_authenticated,
  node::runtime_for_typescript_hook,
  tsx::typescript_execution
]

TESTING::[
  TEST_INVALID_LABEL::"echo '{\"text\":\"gh issue create --label invalid\"}' | tsx validate-gh-labels.ts",
  EXPECT::label_removed_and_warning_shown
]

===WORKFLOW===

AGENT_WORKFLOW::[
  1::CREATE_ISSUE["gh issue create --label X,Y,Z"],
  2::HOOK_VALIDATES[automatic_in_background],
  3::IF_INVALID::warning_shown,
  4::AGENT_REFERENCES_SKILL[if_correction_needed],
  5::COMMAND_EXECUTES[with_valid_labels_only]
]

RECOMMENDED_PRACTICE::[
  TRUST::hook_for_automatic_validation,
  REFERENCE::skill_when_warning_appears,
  VERIFY::uncertain_labels_with_gh_label_list,
  ESCALATE::need_new_label_to_team_discussion
]

===MAINTENANCE===

ADDING_LABELS::[
  1::create_label["gh label create NAME --description DESC --color HEX"],
  2::hook_auto_discovers[within_5min_cache],
  3::update_skill_documentation[manual_step]
]

MONITORING::[
  METRICS::how_often_invalid_labels_caught,
  PATTERNS::which_labels_most_commonly_misused,
  EFFECTIVENESS::skill_educating_agents_over_time
]

===FUTURE_ENHANCEMENTS===

FUZZY_MATCHING::suggest_closest_valid_label["p1"→"priority:p1-high"]
CATEGORY_VALIDATION::auto_suggest_missing_required_categories
HISTORICAL_ANALYSIS::track_error_prone_labels
SMART_DEFAULTS::auto_apply_common_label_combinations

===END===
