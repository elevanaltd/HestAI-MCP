===REVIEW_REQUIREMENTS===
META:
  TYPE::RULE
  VERSION::"3.0"
  STATUS::ENFORCED
  PURPOSE::"Facet-based content-aware review requirements with automated enforcement"
  ENFORCEMENT::PRE_COMMIT⊕CI⊕PR_MERGE
§1::CONTENT_FACETS
  // Reviewer assignment is content-aware, not just line-count based.
  // Each file emits a facet based on its content. Required reviewers = union of all facets.
  // Tiers (T0-T4) are backward-computed display labels, not routing inputs.
META_CONTROL_PLANE::[
  TRIGGER::"Changes to review system itself (validate_review.py, review-gate.yml, review-requirements.oct.md)",
  REQUIRED_REVIEWERS::"{CIV, CE, CRS, SR, TMG}",
  RATIONALE::"Review system changes affect all gate integrity"
]
EXECUTABLE_SPEC::[
  TRIGGER::".oct.md files with TYPE::AGENT_DEFINITION or TYPE::SKILL, or SKILL.md/pattern .md in bundled hub",
  REQUIRED_REVIEWERS::"{CE, SR}",
  RATIONALE::"Executable governance specs need both code and standards review"
]
GOVERNANCE::[
  TRIGGER::".oct.md files with TYPE::RULE, TYPE::STANDARD, TYPE::NORTH_STAR_SUMMARY, or unknown type",
  REQUIRED_REVIEWERS::"{SR}",
  RATIONALE::"Governance documents need standards alignment review only"
]
SECURITY::[
  TRIGGER::"Code in auth/, session/, config/env, path_utils, base.py, shared/, hooks/, tools/, mcp/tools/, clink/agents/, or .sql",
  REQUIRED_REVIEWERS::"{CIV, CE, CRS, TMG}",
  RATIONALE::"Security-touching and architectural code needs full review chain"
]
LINE_COUNT_ESCALATION::[
  TRIGGER::">500 non-exempt lines changed (any content type)",
  EFFECT::"Adds CIV to existing required_reviewers (does NOT replace facet roles)",
  RATIONALE::"Large changes need implementation validation regardless of content type"
]
ROUTINE_CODE::[
  TRIGGER::"Standard code files (.py, .ts, .js, .yml, .toml, non-generated .json)",
  REQUIRED_REVIEWERS::"{CE, CRS, TMG}",
  RATIONALE::"Regular code needs code quality, critical, and test methodology review"
]
§2::TIER_DISPLAY_LABELS
  // Tiers are backward-computed from the reviewer set for display/reporting only.
  // They do NOT determine which reviewers are assigned — facets do.
TIER_0_EXEMPT::[
  CONDITION::"No non-exempt files changed",
  EXEMPT_PATTERNS::[
    "**/*.md[except:*.oct.md]",
    "tests/**/*[when:no_src_changes]",
    "**/*.json[when:generated_file]",
    "**/*.lock"
  ]
]
TIER_1_SELF::[
  CONDITION::"non_exempt_lines<10 AND single_non_exempt_file AND no_new_test_files AND facets exclude SECURITY, META_CONTROL_PLANE, EXECUTABLE_SPEC (GOVERNANCE and ROUTINE_CODE allow self-review at small scale)",
  PROOF::"{role} SELF-REVIEWED: {rationale} OR HO REVIEWED: {rationale}"
]
TIER_2_STANDARD::"When required reviewers do NOT include CIV or PE"
TIER_3_CRITICAL::"When required reviewers include CIV"
TIER_4_STRATEGIC::"When required reviewers include PE (manual invocation only)"
§3::ENFORCEMENT_MECHANISM
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
§4::ROLE_MODEL_DISPATCH
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
§5::SEMANTIC_SNIFFING
  // For .oct.md files, the CI reads the first 50 lines to find TYPE:: in the META block.
  // This determines whether the file is an executable spec or a governance rule.
EXECUTABLE_SPEC_TYPES::[AGENT_DEFINITION,SKILL]
GOVERNANCE_TYPES::[
  RULE,
  STANDARD,
  NORTH_STAR_SUMMARY
]
PATH_OVERRIDES::[
  "library/agents/**/*.oct.md→EXECUTABLE_SPEC[even_if_deleted]",
  "library/skills/**/*.oct.md→EXECUTABLE_SPEC[even_if_deleted]",
  "library/skills/**/SKILL.md→EXECUTABLE_SPEC[not_exempt_despite_.md]",
  "library/patterns/**/*.md→EXECUTABLE_SPEC[not_exempt_despite_.md]"
]
FALLBACK::"Unknown .oct.md TYPE→GOVERNANCE[safe_fallback_to_SR_review]"
§6::TMG_PHASE
PURPOSE::"Test quality gate between RED (tests written) and GREEN (implementation)"
TRIGGER::"TMG in required_reviewers AND tests present but no TMG approval"
SCOPE::"TMG reviews test FILES only — not implementation"
FOCUS::[
  "Are these the right tests?",
  "What tests are missing?",
  "Do tests actually assert behavior or pass vacuously?",
  "Are edge cases covered?"
]
VERDICTS::[TMG_APPROVED→proceed_to_GREEN,TMG_BLOCKED→fix_tests_before_implementing]
§7::BYPASS_CONDITIONS
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
