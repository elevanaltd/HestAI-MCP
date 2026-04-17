===SKILL:REVIEW_PREFLIGHT===
META:
  TYPE::SKILL
  VERSION::"1.2.0"
  STATUS::ACTIVE
  PURPOSE::"Mechanical prep delegation before review. Collects structured context brief via pal_chat so CRS spends tokens on judgement, not grunt work."

§1::CORE
AUTHORITY::ADVISORY[preflight_brief_structure]
PHASE::PRE_REVIEW[runs_BEFORE_review-discipline⊕review-prioritization]
COMPLEMENTS::[review-discipline<confidence>,review-prioritization<triage>]

§2::PROTOCOL
// CRS delegates preflight collection via mcp__pal__chat
// CRS runs as subagent (no Task tool) — PAL MCP tools are the delegation path
DETECT_CONTEXT::[
  PR::"gh_pr_view→has_diff⊕has_CI⊕has_tier",
  STANDALONE::"file_list_provided→no_PR_metadata",
  AUDIT::"explicit_audit_scope→security_focus"
]
COLLECT::[
  CONTEXT_TYPE::PR∨STANDALONE∨AUDIT,
  FILE_SUMMARY::"files_changed⊕line_delta⊕languages_touched",
  CI_STATUS::"pipeline_result[PR_only]",
  TIER::"T0_through_T4_classification[PR_only]",
  SECURITY_PATHS::"auth∨crypto∨secrets∨permissions∨.env∨tokens",
  TEST_MAP::"changed_files→existing_test_files[presence_only]",
  BOT_FINDINGS::"extracted_bot_review_comments[PR_only∧ADVISORY]"
]
// BOT_FINDINGS extraction protocol
BOT_AUTHORS::[
  PRIORITY_1::cubic-dev-ai[bot]<structured_confidence⊕P0-P2_tiers⊕agent_prompts>,
  PRIORITY_2::github-copilot[bot]<inline_suggestions∧auto_review>
]
// LOGIN_NORMALIZATION: GitHub APIs return different login formats for the same
// bot accounts.  `gh pr view --json comments` returns logins WITHOUT the [bot]
// suffix (e.g., "cubic-dev-ai"), while `gh api
// repos/{owner}/{repo}/pulls/{pr}/comments` preserves the [bot] suffix (e.g.,
// "cubic-dev-ai[bot]").  Additionally, some bots use legacy login variants
// that differ from their canonical name:
//   - github-copilot[bot] may appear as "Copilot" or "copilot" (no [bot] suffix)
//   - cubic-dev-ai[bot] may appear as "cubic-bot"
//   - github-actions is the CI automation account (not a [bot]-suffixed account);
//     its comments are excluded from gate validation because CI status comments
//     contain approval-like text that would falsely clear review gates.
// The validate_review.py _BOT_LOGIN_SET handles this by stripping [bot] from
// ADVISORY_BOTS and adding known legacy variant logins.  When scanning for bot
// comments, match against the normalized set, not the canonical names.
BOT_EXTRACT::[
  SCAN_ISSUE_COMMENTS::"gh_pr_view_--json_comments→filter_by_normalized_BOT_LOGINS[strips_bot_suffix⊕includes_github-actions]",
  SCAN_REVIEW_COMMENTS::"gh_api_repos/{repo}/pulls/{pr}/comments→filter_by_NORMALIZED_BOT_LOGINS[match_user.login_against:cubic-dev-ai|cubic-bot|github-copilot|Copilot|copilot|github-actions⊕also_match_[bot]_suffix]",
  CUBIC::"extract_P0_P1_findings⊕confidence_metadata⊕agent_prompt_sections",
  COPILOT::"extract_inline_suggestions[ADVISORY_context_only]",
  CLASSIFY::ADVISORY[bot_findings_NEVER_block_merge]
]
OUTPUT::STRUCTURED_BRIEF[consumed_by_CRS⊕CE_before_review_begins]

§3::GOVERNANCE
DELEGATION::[
  TOOL::mcp__pal__chat[or_mcp__pal__clink_for_CLI_providers],
  PROVIDER_AGNOSTIC::no_model_specification[runtime_selects],
  FILE_PATHS::pass_absolute_file_paths_parameter[not_inline_code]
]
BUDGET::[
  BRIEF_ONLY::collect_facts_not_judgements,
  NO_REVIEW::delegate_NEVER_evaluates_code_quality,
  CONCISE::brief_fits_in_500_tokens_max
]

§5::ANCHOR_KERNEL
TARGET::structured_preflight_brief_with_bot_findings_before_review
NEVER::[evaluate_code_quality_in_preflight,specify_model_or_provider,skip_context_detection,produce_findings_or_verdicts,treat_bot_findings_as_blocking]
MUST::[detect_review_context_type,collect_file_summary_and_languages,map_security_sensitive_paths,map_changed_files_to_tests,scan_both_issue_comments_AND_review_comments_for_bot_findings,normalize_bot_logins_before_matching,classify_bot_findings_as_ADVISORY,delegate_via_pal_tools]
GATE::"Is a structured preflight brief (including bot findings marked ADVISORY) collected via PAL delegation before CRS begins review judgement?"

===END===
