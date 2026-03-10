---
name: skill-creator
description: Create and validate OCTAVE hub skills and patterns with spec-compliant structure. Skills use OCTAVE envelope with optional YAML frontmatter based on deployment context; patterns use OCTAVE envelope only. Use when creating new skills or patterns, validating structure, checking spec compliance, or authoring anchor kernels. Triggers on create skill, create pattern, skill structure, pattern structure, skill validation, spec compliance, anchor kernel, skill template, hub skill, hub pattern.
allowed-tools: ["Read", "Grep", "Glob"]
triggers: ["create skill", "new skill", "create pattern", "new pattern", "skill structure", "pattern structure", "skill validation", "spec compliance", "anchor kernel", "skill template", "hub skill", "hub pattern", "skill creator"]
version: "3.0.0"
---

===SKILL_CREATOR===
META:
  TYPE::SKILL
  VERSION::"3.0.0"
  STATUS::ACTIVE
  PURPOSE::"Create and validate OCTAVE hub skills and patterns per octave-skills-spec v9.1 and octave-patterns-spec v2"
  SPEC_REFERENCE::[octave-skills-spec.oct.md,octave-patterns-spec.oct.md]

§1::CORE
MISSION::"Produce spec-compliant skills and patterns with correct structure, compression, and discovery metadata"
AUTHORITY::"Skills-expert BLOCKING authority on spec violations applies to all output"
SCOPE::[
  SKILLS::OCTAVE_envelope⊕§5::ANCHOR_KERNEL⊕YAML_optional[octave-skills-spec],
  PATTERNS::OCTAVE_envelope_only⊕§5::ANCHOR_KERNEL_required[octave-patterns-spec]
]
DISTINCTION::"Skills define WHAT agents do; Patterns define HOW agents decide"

§2::PROTOCOL

YAML_FRONTMATTER_RULES::[
  PLATFORM_SKILLS::[location::.claude/skills/∨.codex/skills/,YAML::REQUIRED,reason::platforms_parse_YAML_for_discovery⊕triggers⊕tool_gating],
  HUB_SKILLS::[location::.hestai-sys/library/skills/,YAML::OPTIONAL,reason::anchor_ceremony_reads_OCTAVE_META_not_YAML],
  DUAL_DEPLOYED::[YAML::PRESENT_IN_BOTH,reason::serves_the_platform_copy],
  WHEN_YAML_PRESENT::no_duplicate_TRIGGERS_or_TOOLS_in_OCTAVE_META[YAML_is_source_of_truth_for_discovery],
  WHEN_YAML_ABSENT::OCTAVE_META_is_sole_source_of_truth
]

SKILL_CREATION_SEQUENCE::[
  1::YAML_FRONTMATTER[name,description,allowed-tools,triggers,version]::OPTIONAL[required_for_platform_skills],
  2::OCTAVE_ENVELOPE[===SKILL_NAME===,META,body_§1_to_§4,§5::ANCHOR_KERNEL,===END===],
  3::META_REQUIRED[TYPE::SKILL,VERSION,STATUS],
  4::META_OPTIONAL[PURPOSE,TIER,SPEC_REFERENCE],
  5::CANONICAL_SECTIONS[§1::CORE,§2::PROTOCOL,§3::GOVERNANCE,§4::EXAMPLES],
  6::§5::ANCHOR_KERNEL[TARGET,NEVER,MUST,GATE]
]

PATTERN_CREATION_SEQUENCE::[
  1::OCTAVE_ENVELOPE[===PATTERN_NAME===,META,body,§5::ANCHOR_KERNEL,===END===],
  2::META_REQUIRED[TYPE::PATTERN_DEFINITION,VERSION,PURPOSE],
  3::META_OPTIONAL[REPLACES,TIER,SPEC_REFERENCE],
  4::BODY_SECTIONS[§1::CORE_PRINCIPLE,§2::METRICS_OR_TARGETS,§3::DECISION_FRAMEWORK,§4::USED_BY],
  5::§5::ANCHOR_KERNEL_required[TARGET,NEVER,MUST,GATE]
]
// Patterns NEVER have YAML frontmatter — they are not trigger-discoverable

COMPRESSION_MANDATE::[
  BODY::AGGRESSIVE[dense_KEY::value⊕operators,preserve_examples⊕causal_chains,drop_narrative],
  YAML::LOSSLESS[natural_language_for_BM25⊕embedding_retrieval,ONLY_when_present],
  KERNEL::ULTRA[atoms_only_no_prose]
]

SIZE_CONSTRAINTS:
  SKILLS::[TARGET::500_lines,HARD_LIMIT::600_lines,TOKEN_TARGET::300-700]
  PATTERNS::[TARGET::100_lines,HARD_LIMIT::150_lines]
  KERNEL::50_lines_max

DESCRIPTION_ROLE::retrieval_only[NOT_behavioral_constraint]
ENFORCEMENT_SOURCE::OCTAVE_body[§2::PROTOCOL⊕§3::GOVERNANCE]

TRIGGER_DESIGN::[
  PATTERN::"Use when [actions]. Triggers on [keywords].",
  DENSITY::3-5_keywords_per_trigger_category,
  KEYWORDS::[action_verbs,domain_terms,problem_patterns]
]

§3::GOVERNANCE

OCTAVE_WRITE_GATE::[
  RULE::".oct.md files MUST be written using mcp__octave__octave_write",
  NEVER::Write_tool_for_.oct.md,
  NEVER::Edit_tool_for_.oct.md,
  USE::octave_write_with_content_param[new_files],
  USE::octave_write_with_changes_param[modifications],
  RATIONALE::"octave_write enforces normalization, schema validation, and audit automatically"
]
// NOTE: SKILL.md files (.md extension) use Write/Edit tools. The gate applies to .oct.md only.

VALIDATION_CHECKLIST::[
  STRUCTURE::envelope_valid⊕YAML_if_platform_skill,
  META::required_fields_present,
  ENVELOPE::name_matches_YAML_name[when_YAML_present]∨name_matches_filename[patterns],
  SYNTAX::passes_octave_validation,
  SIZE::under_constraint_limits,
  KERNEL::§5_section_header_required[not_§ANCHOR_KERNEL_freestanding]
]

MUST_NEVER::[
  "Use markdown headers in OCTAVE body (breaks parser)",
  "Create auxiliary files (README.md, CHANGELOG.md)",
  "Duplicate TRIGGERS or TOOLS in OCTAVE META when YAML frontmatter is present",
  "Put prose in anchor kernel (atoms only)",
  "Exceed size hard limits (600 skills, 150 patterns)",
  "Use line number references (stale and fragile)",
  "Use Write or Edit tools for .oct.md files (use octave_write)",
  "Add YAML frontmatter to patterns (patterns are not trigger-discoverable)",
  "Omit YAML frontmatter from platform-deployed skills (.claude/skills/, .codex/skills/)"
]

CASCADING_FALLBACK::[
  PRIORITY_1::§5::ANCHOR_KERNEL[primary_source],
  PRIORITY_2::§3::GOVERNANCE[fallback_MUST_NEVER⊕ALLOWED],
  PRIORITY_3::SIGNALS_or_PATTERNS_blocks,
  PRIORITY_4::WARN_UNSTRUCTURED[skill_name]
]

§5::ANCHOR_KERNEL
TARGET::spec_compliant_skill_and_pattern_creation
NEVER::[markdown_headers_in_body,auxiliary_files,duplicate_meta_when_yaml_present,prose_in_kernel,exceed_size_limits,Write_or_Edit_for_oct_md_files,yaml_frontmatter_on_patterns,omit_yaml_from_platform_skills]
MUST::[read_spec_before_creating,octave_envelope_with_META,§5_ANCHOR_KERNEL_section_header,compression_mandate,octave_write_for_oct_md_files,yaml_for_platform_skills_only,validate_before_commit]
GATE::"Does this artifact have correct structure per its spec, §5::ANCHOR_KERNEL, correct YAML presence for deployment context, and was .oct.md written via octave_write?"

===END===
