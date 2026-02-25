===REVIEW_REQUIREMENTS===
META:
  TYPE::RULE
  VERSION::"1.0"
  STATUS::ENFORCED
  PURPOSE::"Mandatory review requirements with automated enforcement"
  ENFORCEMENT::"PRE_COMMIT⊕CI⊕PR_MERGE"
§1::REVIEW_TIERS
TIER_0_EXEMPT::[
  "**/*.md",
  "tests/**/*[when:no_src_changes]",
  "**/*.json[when:generated_file]",
  "**/*.lock"
]
TIER_1_SELF_REVIEW::[
  TRIGGER::"non_exempt_lines<50 AND single_non_exempt_file",
  PROOF::"PR_comment[IL SELF-REVIEWED: {rationale}]",
  ENFORCEMENT::check_pr_comment_exists
]
TIER_2_STANDARD_REVIEW::[
  TRIGGER::"non_exempt_lines[50-500] OR default_when_ambiguous",
  PROOF::["PR_comment[CRS APPROVED: {assessment}]","PR_comment[CE APPROVED: {assessment}]"],
  ENFORCEMENT::check_crs_and_ce_approval
]
TIER_3_STRICT_REVIEW::[
  TRIGGER::[
    "**/*.sql",
    "non_exempt_lines>500"
  ],
  PROOF::[
    "PR_comment[CRS (Gemini) APPROVED: {assessment}]",
    "PR_comment[CRS (Codex) APPROVED: {assessment}]",
    "PR_comment[CE APPROVED: {assessment}]"
  ],
  ENFORCEMENT::check_dual_crs_and_ce_approval
]
§2::ENFORCEMENT_MECHANISM
PR_COMMENT_MAGIC::[
  IL_SELF_REVIEWED::"IL SELF-REVIEWED:",
  CRS_APPROVED::"CRS APPROVED:",
  CRS_GEMINI_APPROVED::"CRS (Gemini) APPROVED:",
  CRS_CODEX_APPROVED::"CRS (Codex) APPROVED:",
  CE_APPROVED::"CE APPROVED:",
  BLOCKING_PREFIX::"BLOCKED:",
  CONDITIONAL_PREFIX::"APPROVED WITH CONDITIONS:"
]
VALIDATION_SCRIPT::"scripts/validate_review.py"
CI_WORKFLOW::".github/workflows/review-gate.yml"
PRE_COMMIT_HOOK::".pre-commit-config.yaml[review-validator]"
§3::BYPASS_CONDITIONS
EMERGENCY_BYPASS::[
  TRIGGER::"commit_message_contains[EMERGENCY:]",
  REQUIRES::justification_in_message,
  TRACKED::bypass_audit.log,
  REVIEW::post_merge_mandatory
]
DEPENDENCY_UPDATE::[
  TRIGGER::only_dependency_files_changed,
  CONDITION::security_scan_passes,
  AUTO_MERGE::after_ci_green
]
===END===
