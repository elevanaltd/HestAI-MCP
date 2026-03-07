---
name: skill-creator
description: Create and validate OCTAVE hub skills with spec-compliant structure, YAML frontmatter, canonical sections, anchor kernels, and size constraints. Use when creating new skills, validating skill structure, checking spec compliance, or authoring anchor kernels. Triggers on create skill, skill structure, skill validation, spec compliance, anchor kernel, YAML frontmatter, skill template, hub skill.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob"]
triggers: ["create skill", "new skill", "skill structure", "skill validation", "spec compliance", "anchor kernel", "YAML frontmatter", "skill template", "hub skill", "skill creator"]
version: "1.0.0"
---

===SKILL_CREATOR===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Create and validate OCTAVE hub skills per octave-skills-spec v8"
  SPEC_REFERENCE::octave-skills-spec.oct.md

§1::CORE
MISSION::"Produce spec-compliant skills with correct structure, compression, and discovery metadata"
SPEC_VERSION::v8[YAML_frontmatter⊕OCTAVE_envelope⊕ANCHOR_KERNEL_optional]
AUTHORITY::"Skills-expert BLOCKING authority on spec violations applies to all output"

§2::PROTOCOL
CREATION_SEQUENCE::[
  1::YAML_FRONTMATTER[name,description,allowed-tools,triggers,version],
  2::OCTAVE_ENVELOPE[===SKILL_NAME===,META,body,===END===],
  3::META_REQUIRED[TYPE::SKILL,VERSION,STATUS],
  4::META_OPTIONAL[PURPOSE,TIER,SPEC_REFERENCE],
  5::CANONICAL_SECTIONS[§1::CORE,§2::PROTOCOL,§3::GOVERNANCE,§4::EXAMPLES],
  6::ANCHOR_KERNEL[TARGET,NEVER,MUST,GATE]
]

COMPRESSION_MANDATE::[
  BODY::AGGRESSIVE[dense_KEY::value⊕operators,preserve_examples⊕causal_chains,drop_narrative],
  YAML::LOSSLESS[natural_language_for_BM25⊕embedding_retrieval],
  KERNEL::ULTRA[atoms_only_no_prose]
]

SIZE_CONSTRAINTS::[
  TARGET::500_lines_max,
  HARD_LIMIT::600_lines_NEVER_exceed,
  TOKEN_TARGET::300-700[body_excluding_YAML_and_kernel],
  KERNEL::50_lines_max
]

DESCRIPTION_ROLE::retrieval_only[NOT_behavioral_constraint]
ENFORCEMENT_SOURCE::OCTAVE_body[§2::PROTOCOL⊕§3::GOVERNANCE]

TRIGGER_DESIGN::[
  PATTERN::"Use when [actions]. Triggers on [keywords].",
  DENSITY::3-5_keywords_per_trigger_category,
  KEYWORDS::[action_verbs,domain_terms,problem_patterns]
]

§3::GOVERNANCE
VALIDATION_CHECKLIST::[
  STRUCTURE::YAML_frontmatter_present⊕OCTAVE_envelope_valid,
  META::TYPE_SKILL⊕VERSION⊕STATUS_present,
  ENVELOPE::name_matches_YAML_name,
  SYNTAX::passes_octave_validation,
  SIZE::under_constraint_limits,
  KERNEL::recommended[warn_if_missing]
]

MUST_NEVER::[
  "Use markdown headers in OCTAVE body (breaks parser)",
  "Create auxiliary files (README.md, CHANGELOG.md)",
  "Duplicate TRIGGERS or TOOLS in META (source of truth is YAML)",
  "Put prose in anchor kernel (atoms only)",
  "Exceed 600 lines (hard limit)",
  "Use line number references (stale and fragile)"
]

CASCADING_FALLBACK::[
  PRIORITY_1::§ANCHOR_KERNEL[explicit_export_interface],
  PRIORITY_2::§BEHAVIOR.CONDUCT[MUST_NEVER⊕MUST_ALWAYS],
  PRIORITY_3::SIGNALS_or_PATTERNS_blocks,
  PRIORITY_4::WARN_UNSTRUCTURED[skill_name]
]

§ANCHOR_KERNEL
TARGET::spec_compliant_skill_creation
NEVER::[markdown_headers_in_body,auxiliary_files,duplicate_meta_triggers,prose_in_kernel,exceed_600_lines]
MUST::[yaml_frontmatter_first,octave_envelope_with_META,canonical_sections,compression_mandate,validate_before_commit]
GATE::"Does this skill have valid YAML frontmatter, OCTAVE envelope with required META, and body under 600 lines?"

===END===
