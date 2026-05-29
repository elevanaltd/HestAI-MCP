===REVIEW_REQUIREMENTS===
META:
  TYPE::RULE
  VERSION::"3.1"
  STATUS::ENFORCED
  PURPOSE::"Facet-based content-aware review requirements with automated enforcement"
  ENFORCEMENT::PRE_COMMIT⊕CI⊕PR_MERGE
  CANONICAL::"src/hestai_mcp/_bundled_hub/standards/rules/review-requirements.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/standards/rules/review-requirements.oct.md"
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
  REQUIRED_REVIEWERS::"{CE, CRS, SR}",
  RATIONALE::"Executable governance specs need code quality, code review, and standards review"
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
DEPENDENCY_UPDATE::"PLANNED[manual_merge_during_bedding_in_phase→auto_merge_future]"
§8::CONTENT_AWARE_ESCALATION
  // Issue #412: a change can declare "this needs DEEPER review than the diff
  // shape suggests" and the org-shared gate honours it with ZERO per-repo config.
  // The mechanism is ESCALATION-ONLY: it can only ADD required reviewers, never
  // remove them. This is enforced structurally by set-union, not procedurally.
PRINCIPLE::"declared_reviewers ∪ diff_computed_reviewers → escalation_only[set_union_cannot_subtract]"
CANONICAL_FIELD::REQUIRED_REVIEWERS
// Reuses the EXISTING vocabulary already declared per-facet in §1. A document
// declares an explicit REQUIRED_REVIEWERS override; it is unioned with the
// diff-computed floor — it can raise the floor but never lower it.
DECLARATION_SURFACES::[
  OCTAVE_BLOCK_FIELD::"REQUIRED_REVIEWERS::\"{CE, CRS, SR}\" in any .oct.md (canonical, preferred path)",
  HTML_COMMENT_ROLES::"<!-- review-requirements: [TMG, CRS, CE, CIV, SR] --> in plain .md or PR body",
  HTML_COMMENT_TIER::"<!-- review-tier: TIER_3_CRITICAL: reason --> mapped through the tier→role table",
  FRONTMATTER::"review-requirements: [CE, CRS] in YAML frontmatter"
]
BITEMPORAL_UNION::[
  SOURCES::"Diff_Roles ∪ Base_Roles ∪ Head_Roles ∪ PR_Body_Roles",
  BASE_READ::"declarations in changed files at pr.base.sha (git show <base>:<path>)",
  HEAD_READ::"declarations in changed files at pr.head.sha (git show <head>:<path>)",
  RATCHET::"a declaration present in BASE but removed in HEAD is RETAINED — set-union cannot subtract, closing the downgrade-by-deletion footgun",
  MISSING_BLOB::"new file has no BASE blob, deleted file has no HEAD blob → that source contributes nothing, never crashes"
]
WHITELIST::[
  ALLOWED_ESCALATION_ROLES::"{TMG, CRS, CE, CIV, PE, SR} = VALID_ROLES − {IL, HO}",
  RATIONALE::"IL and HO are SELF-review roles and cannot be REQUIRED reviewers via escalation",
  INTERSECTION::"declared set is intersected with ALLOWED_ESCALATION_ROLES before enforcement",
  NON_FATAL::"out-of-set tokens (typos, [GOD_MODE]) are dropped + logged, never block or crash the gate"
]
ORDERING::[
  RULE::"declaration collection + union runs BEFORE both early returns in classify_pr_facets",
  SUPPRESS_TIER_0::"a non-empty declared set suppresses the TIER_0_EXEMPT (all-exempt) short-circuit",
  SUPPRESS_TIER_1::"a non-empty declared set suppresses the TIER_1_SELF (small single-file) short-circuit",
  WHY::"the originating all-markdown PR is all-exempt and would otherwise return TIER_0_EXEMPT before roles are ever computed"
]
PROVENANCE::[
  EMIT::"validate_review.py emits a per-role source map {ROLE:[DIFF|HEAD|BASE|PR_BODY]} in the REVIEW_GATE_JSON payload",
  RENDER::"review-gate.yml renders the source map as a status-comment audit table",
  AUDIT_TRAIL::"a role contributed only by BASE displays BASE alone — a visible record of an attempted downgrade that set-union refused"
]
===END===
