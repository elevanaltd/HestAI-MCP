===CONSTRUCTIVE_FEEDBACK===
META:
  TYPE::PATTERN_DEFINITION
  VERSION::"1.0.0"
  PURPOSE::"Evidence-based review communication framework — structure findings for clarity and actionability"
§1::CORE_PRINCIPLE
ESSENTIAL::"Every review finding must be actionable — state what, where, why, and how to fix"
ANTI_PATTERN::"vague_criticism<'this looks wrong'⊕'consider refactoring'→developer_confusion⊕ignored_feedback>"
ENFORCEMENT::"Apply finding presentation structure and confidence-gated framing to every comment"
§2::DECISION_FRAMEWORK
FINDING_STRUCTURE::[
  WHAT::issue_description,
  WHERE::file_path⊕line_range,
  WHY::impact⊕risk⊕principle_violated,
  FIX::concrete_suggestion⊕code_snippet
]
CONFIDENCE_GATING:
  CERTAIN:
    EVIDENCE::spec_violation⊕test_failure⊕provable_bug
    FRAMING::"direct assertion — 'This will cause X because Y'"
    ACTION::BLOCKING⊕MUST_FIX
  MODERATE:
    EVIDENCE::pattern_match⊕best_practice⊕potential_risk
    FRAMING::"qualified — 'This pattern typically causes X. Consider Y.'"
    ACTION::ADVISORY⊕SHOULD_CONSIDER
  LOW:
    EVIDENCE::style_preference⊕minor_optimization
    FRAMING::"suggestion — 'Nit: consider X for readability'"
    ACTION::NIT⊕OPTIONAL
FIX_GUIDANCE::[
  provide_code_snippet_when_fix_is_clear,
  reference_documentation_when_pattern_based,
  suggest_approach_not_exact_code_when_design_level,
  link_to_existing_codebase_examples_when_available
]
§3::USED_BY
AGENTS::[code-review-specialist]
CONTEXT::PR_review_comments⊕finding_presentation⊕review_communication
§5::ANCHOR_KERNEL
TARGET::evidence_based_review_communication
NEVER::[
  post_vague_criticism,
  omit_fix_guidance,
  assert_without_evidence,
  mix_confidence_levels_in_single_finding
]
MUST::[
  structure_findings_as_what_where_why_fix,
  gate_communication_by_confidence_level,
  provide_actionable_fix_for_every_finding,
  use_direct_framing_for_CERTAIN_findings
]
GATE::"Does this finding clearly state what is wrong, where, why it matters, and how to fix it?"
===END===
