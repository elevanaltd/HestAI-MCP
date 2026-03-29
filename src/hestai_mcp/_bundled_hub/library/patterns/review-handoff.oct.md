===REVIEW_HANDOFF===
META:
  TYPE::PATTERN_DEFINITION
  VERSION::"1.0.0"
  PURPOSE::"Define the exact handoff contract between CRS and CE in the review gate chain"
§1::CORE_PRINCIPLE
ESSENTIAL::"CRS and CE must exchange structured, machine-readable metadata — implicit contracts cause integration failures"
ANTI_PATTERN::"implicit_handoff<CRS_produces_prose⊕CE_parses_by_convention→brittle_chain⊕missed_findings>"
ENFORCEMENT::"CRS output must contain all fields CE requires; CE must validate metadata presence before proceeding"
CHAIN::"CRS[gemini,code-review-specialist] → CE[codex,critical-engineer] → merge"
TRIGGER_CONDITION::"T2+ PRs (10-500+ lines) — CE reviews both T2 and T3 per gate chain"
§2::DECISION_FRAMEWORK
CRS_PRODUCES::[
  PR_COMMENT::[
    STRUCTURE::"EXECUTIVE_SUMMARY → CRITICAL_ISSUES → QUALITY_RECOMMENDATIONS → CODE_EXAMPLES",
    METADATA_COMMENT::"<!-- review: {role,provider,verdict,sha,tier,findings,blocking,priority_distribution,triaged,findings_omitted} -->",
    VERDICT_DECLARATION::"'CRS APPROVED: [assessment]' or 'BLOCKED: [issues]'",
    LINE_REFERENCES::"Every finding cites file path, line number, and confidence level",
    CONFIDENCE_LABELS::"CONFIDENCE::(CERTAIN|HIGH|MODERATE) on each finding"
  ],
  STRUCTURED_FIELDS::[
    tier::"T0|T1|T2|T3 classification of PR scope",
    verdict::"APPROVED|BLOCKED",
    provider::"AI provider used for review (lowercase)",
    role::"Short-form role identifier (CRS, CE, TMG, etc.)",
    findings::"total finding count (integer)",
    blocking::"blocking finding count (integer)",
    sha::"First 7 characters of PR head commit SHA for audit trail",
    priority_distribution::"P0:N P1:N P2:N P3:N P4:N P5:N (when review-prioritization skill loaded)"
  ]
]
CE_EXPECTS::[
  REQUIRED::[
    metadata_comment_present::"<!-- review: {...} --> must exist in PR comment",
    verdict_field::"APPROVED or BLOCKED must be extractable",
    tier_field::"must be T2+ for CE engagement",
    findings_count::"integer count of total findings",
    blocking_count::"integer count of blocking findings"
  ],
  OPTIONAL::[
    priority_distribution::"P0-P5 counts for severity awareness",
    findings_omitted::"count of triaged-out findings"
  ],
  VALIDATION::[
    "IF[metadata_comment_missing]→CE_BLOCKS_with_INSUFFICIENT_DATA",
    "IF[tier_below_T2]→CE_skips_review",
    "IF[verdict_is_BLOCKED]→CE_validates_blocking_issues_first",
    "IF[verdict_is_APPROVED]→CE_performs_independent_deep_review"
  ]
]
HANDOFF_SEQUENCE::[
  STEP_1::"CRS completes review and posts PR comment with metadata",
  STEP_2::"review-gate.yml CI extracts metadata via scripts/validate_review.py",
  STEP_3::"CE is invoked for T2+ PRs regardless of CRS verdict",
  STEP_4::"CE reads CRS comment, extracts metadata, validates required fields",
  STEP_5::"CE performs independent review with CRS findings as context",
  STEP_6::"CE posts own verdict: 'CE APPROVED: [assessment]' or 'BLOCKED: [risks]'",
  STEP_7::"Both CRS and CE verdicts required for T2+ merge approval"
]
METADATA_TEMPLATE::[
  CRS_FORMAT::"<!-- review: {\"role\":\"CRS\",\"provider\":\"$MODEL\",\"verdict\":\"APPROVED\",\"sha\":\"$SHA\",\"tier\":\"T2\",\"findings\":12,\"blocking\":2,\"priority_distribution\":\"P0:1 P1:3 P2:5 P3:2 P4:1 P5:0\",\"triaged\":true,\"findings_omitted\":3} -->",
  CE_FORMAT::"<!-- review: {\"role\":\"CE\",\"provider\":\"$MODEL\",\"verdict\":\"APPROVED\",\"sha\":\"$SHA\",\"tier\":\"T2\",\"findings\":N,\"blocking\":N} -->"
]
§3::USED_BY
AGENTS::[code-review-specialist,critical-engineer]
CONTEXT::review_gate_chain⊕T2_plus_PR_validation⊕CRS_CE_handoff
SCRIPTS::"scripts/validate_review.py"
§5::ANCHOR_KERNEL
TARGET::structured_CRS_to_CE_handoff_contract
NEVER::[
  omit_metadata_comment_from_CRS_output,
  engage_CE_without_CRS_metadata,
  merge_T2_plus_without_both_verdicts,
  parse_CRS_output_by_convention_without_metadata,
  skip_metadata_validation_in_CE
]
MUST::[
  include_metadata_comment_in_every_CRS_PR_comment,
  validate_required_fields_before_CE_proceeds,
  block_on_missing_metadata_not_missing_approval,
  treat_CRS_findings_as_context_not_authority_for_CE,
  extract_tier_to_determine_CE_engagement
]
GATE::"Does CRS output contain machine-readable metadata that CE can validate and consume?"
===END===
