===SKILL:REVIEW_PREFLIGHT===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Mechanical prep delegation before review. Collects structured context brief via subagent so CRS spends tokens on judgement, not grunt work."

§1::CORE
AUTHORITY::ADVISORY[preflight_brief_structure]
PHASE::PRE_REVIEW[runs_BEFORE_review-discipline⊕review-prioritization]
COMPLEMENTS::[review-discipline<confidence>,review-prioritization<triage>]

§2::PROTOCOL
// CRS delegates preflight collection to a lightweight subagent
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
  TEST_MAP::"changed_files→existing_test_files[presence_only]"
]
OUTPUT::STRUCTURED_BRIEF[consumed_by_CRS_before_review_begins]

§3::GOVERNANCE
DELEGATION::[
  SPAWN::lightweight_subagent_for_mechanical_collection,
  PROVIDER_AGNOSTIC::no_model_specification[runtime_selects],
  TOOLS::gh_CLI⊕file_search⊕grep[available_to_subagent]
]
BUDGET::[
  BRIEF_ONLY::collect_facts_not_judgements,
  NO_REVIEW::subagent_NEVER_evaluates_code_quality,
  CONCISE::brief_fits_in_500_tokens_max
]

§5::ANCHOR_KERNEL
TARGET::structured_preflight_brief_before_review
NEVER::[evaluate_code_quality_in_preflight,specify_model_or_provider,skip_context_detection,produce_findings_or_verdicts]
MUST::[detect_review_context_type,collect_file_summary_and_languages,map_security_sensitive_paths,map_changed_files_to_tests,delegate_to_subagent]
GATE::"Is a structured preflight brief collected via delegation before CRS begins review judgement?"

===END===
