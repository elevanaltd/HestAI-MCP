===REVIEW_REQUIREMENTS===
META:
  TYPE::RULE
  VERSION::"1.0"
  STATUS::ENFORCED
  PURPOSE::"Mandatory review requirements with automated enforcement"
  ENFORCEMENT::PRE_COMMIT+CI+PR_MERGE

§1::REVIEW_TIERS
TIER_0_EXEMPT::[
  docs/**/*.md[except:**/ARCHITECTURE.md,**/API.md],
  .hestai/context/*.md,
  tests/**/*[when:no_src_changes],
  **/*.json[when:generated_file],
  **/*.lock
]

TIER_1_SELF_REVIEW::[
  TRIGGER::lines_changed<50 AND single_file AND no_architecture,
  PROOF::PR_comment["IL SELF-REVIEWED: {rationale}"],
  ENFORCEMENT::check_pr_comment_exists
]

TIER_2_CRS_REVIEW::[
  TRIGGER::src/**/*.py[lines:50-500] AND single_component,
  PROOF::PR_comment["CRS APPROVED: {assessment}"],
  ENFORCEMENT::check_crs_approval
]

TIER_3_FULL_REVIEW::[
  TRIGGER::[
    src/*/architecture/**,
    **/*.sql,
    lines_changed>500,
    crosses_component_boundary,
    adds_external_dependency
  ],
  PROOF::[
    PR_comment["CRS APPROVED: {assessment}"],
    PR_comment["CE APPROVED: {assessment}"]
  ],
  ENFORCEMENT::check_both_approvals
]

§2::ENFORCEMENT_MECHANISM
PR_COMMENT_MAGIC::[
  IL_SELF_REVIEWED::"IL SELF-REVIEWED:",
  CRS_APPROVED::"CRS APPROVED:",
  CE_APPROVED::"CE APPROVED:",
  BLOCKING_PREFIX::"BLOCKED:",
  CONDITIONAL_PREFIX::"APPROVED WITH CONDITIONS:"
]

VALIDATION_SCRIPT::scripts/validate_review.py
CI_WORKFLOW::.github/workflows/review-gate.yml
PRE_COMMIT_HOOK::.pre-commit-config.yaml[review-validator]

§3::BYPASS_CONDITIONS
EMERGENCY_BYPASS::[
  TRIGGER::commit_message_contains["EMERGENCY:"],
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
