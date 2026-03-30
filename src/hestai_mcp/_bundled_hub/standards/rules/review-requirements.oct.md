===REVIEW_REQUIREMENTS===
META:
  TYPE::RULE
  VERSION::"2.1"
  STATUS::ENFORCED
  PURPOSE::"5-tier mandatory review requirements with facet-based content-aware routing and automated enforcement"
  ENFORCEMENT::PRE_COMMIT⊕CI⊕PR_MERGE
§1::REVIEW_TIERS
TIER_0_EXEMPT::[
  "**/*.md[except:*.oct.md]",
  "tests/**/*[when:no_src_changes]",
  "**/*.json[when:generated_file]",
  "**/*.lock"
]
TIER_1_SELF_REVIEW::[
  TRIGGER::"non_exempt_lines<10 AND single_non_exempt_file AND no_security_paths AND no_new_test_files",
  PROOF::"PR_comment[{role} SELF-REVIEWED: {rationale}] OR PR_comment[HO REVIEWED: {rationale}]",
  ENFORCEMENT::check_pr_comment_exists
]
TIER_2_STANDARD_REVIEW::[
  TRIGGER::"non_exempt_lines[10-500] OR multiple_non_exempt_files OR includes_new_test_files",
  FLOW::"RED→TMG→GREEN→CRS+CE→merge",
  PROOF::[
    "PR_comment[TMG APPROVED: {assessment}]",
    "PR_comment[CRS APPROVED: {assessment}]",
    "PR_comment[CE APPROVED: {assessment}]"
  ],
  ENFORCEMENT::check_tmg_and_crs_and_ce_approval
]
TIER_3_CRITICAL_REVIEW::[
  TRIGGER::[
    "non_exempt_lines>500",
    "architecture_changes[base_class_mods,new_hooks]",
    "security_touching_code[auth,path_handling,session_management,env_vars]",
    "new_tools_or_runners[tools/**,clink/agents/**]",
    "new_mcp_endpoints[mcp/tools/**]",
    "**/*.sql"
  ],
  FLOW::"RED→TMG→GREEN→CRS+CE+CIV→merge",
  PROOF::[
    "PR_comment[TMG APPROVED: {assessment}]",
    "PR_comment[CRS APPROVED: {assessment}]",
    "PR_comment[CE APPROVED: {assessment}]",
    "PR_comment[CIV APPROVED: {assessment}]"
  ],
  ENFORCEMENT::check_tmg_and_crs_and_ce_and_civ_approval
]
TIER_4_STRATEGIC_REVIEW::[
  TRIGGER::"manual_only[/review --strategic OR explicit_tier_override]",
  FLOW::"RED→TMG→GREEN→CRS+CE+CIV+PE→merge",
  PROOF::[
    "PR_comment[TMG APPROVED: {assessment}]",
    "PR_comment[CRS APPROVED: {assessment}]",
    "PR_comment[CE APPROVED: {assessment}]",
    "PR_comment[CIV APPROVED: {assessment}]",
    "PR_comment[PE APPROVED: {assessment}]"
  ],
  ENFORCEMENT::check_tmg_and_crs_and_ce_and_civ_and_pe_approval
]
§2::ENFORCEMENT_MECHANISM
PR_COMMENT_MAGIC::[
  IL_SELF_REVIEWED::"IL SELF-REVIEWED:",
  HO_REVIEWED::"HO REVIEWED:",
  TMG_APPROVED::"TMG APPROVED:",
  TMG_GO::"TMG GO:",
  CRS_APPROVED::"CRS APPROVED:",
  CRS_GO::"CRS GO:",
  CRS_GEMINI_APPROVED::"CRS (Gemini) APPROVED:",
  CRS_CODEX_APPROVED::"CRS (Codex) APPROVED:",
  CE_APPROVED::"CE APPROVED:",
  CE_GO::"CE GO:",
  CIV_APPROVED::"CIV APPROVED:",
  CIV_GO::"CIV GO:",
  PE_APPROVED::"PE APPROVED:",
  PE_GO::"PE GO:",
  SR_APPROVED::"SR APPROVED:",
  SR_GO::"SR GO:",
  BLOCKING_PREFIX::"BLOCKED:",
  CONDITIONAL_PREFIX::"APPROVED WITH CONDITIONS:"
]
VALIDATION_SCRIPT::"scripts/validate_review.py"
CI_WORKFLOW::".github/workflows/review-gate.yml"
PRE_COMMIT_HOOK::".pre-commit-config.yaml[review-validator]"
§3::ROLE_MODEL_DISPATCH
TMG::[
  "cli:goose",
  "role:test-methodology-guardian",
  fallback,
  ":",
  ["cli:codex","role:test-methodology-guardian"]
]
CRS::[
  "cli:gemini",
  "role:code-review-specialist",
  fallback,
  ":",
  ["cli:codex","role:code-review-specialist"]
]
CE::[
  "cli:codex",
  "role:critical-engineer",
  fallback,
  ":",
  ["cli:gemini","role:critical-engineer"]
]
CIV::[
  "cli:goose",
  "role:critical-implementation-validator",
  fallback,
  ":",
  ["cli:codex","role:critical-implementation-validator"]
]
PE::[
  "cli:goose",
  "role:principal-engineer",
  fallback,
  ":",
  ["cli:codex","role:principal-engineer"]
]
SR::[
  "cli:goose",
  "role:standards-reviewer",
  fallback,
  ":",
  ["cli:codex","role:standards-reviewer"]
]
§4::TIER_DETERMINATION
THRESHOLDS::[
  T1_MAX_LINES::10,
  T2_MAX_LINES::500,
  T1_MAX_FILES::1
]
T3_TRIGGERS::[
  "**/*.sql",
  "non_exempt_lines>500",
  "touches_base_class[**/base.py,**/shared/**,abstract_classes]",
  "touches_security[auth,path_handling,session_management,env_vars]",
  "is_new_tool[tools/**,clink/agents/**]",
  "is_new_mcp_endpoint[mcp/tools/**]"
]
T4_TRIGGER::"manual_only[/review --strategic OR explicit_tier_override]"
§5::TMG_PHASE
PURPOSE::"Test quality gate between RED (tests written) and GREEN (implementation)"
TRIGGER::"TIER_2+ with tests present but no TMG approval"
SCOPE::"TMG reviews test FILES only — not implementation"
FOCUS::[
  "Are these the right tests?",
  "What tests are missing?",
  "Do tests actually assert behavior or pass vacuously?",
  "Are edge cases covered?"
]
VERDICTS::[TMG_APPROVED→proceed_to_GREEN,TMG_BLOCKED→fix_tests_before_implementing]
§6::BYPASS_CONDITIONS
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
