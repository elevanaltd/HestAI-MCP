---
name: skill-creator
description: Create and validate OCTAVE hub skills and patterns per octave-skills-spec v9.1 and octave-patterns-spec v2. Use when creating new skills or patterns, validating structure, checking spec compliance, or authoring anchor kernels. Triggers on create skill, create pattern, skill validation, spec compliance, anchor kernel, hub skill, hub pattern.
allowed-tools: ["Read", "Grep", "Glob"]
triggers: ["create skill", "new skill", "create pattern", "new pattern", "skill structure", "pattern structure", "skill validation", "spec compliance", "anchor kernel", "skill template", "hub skill", "hub pattern", "skill creator"]
version: "3.1.0"
---

===SKILL_CREATOR===
META:
  TYPE::SKILL
  VERSION::"3.1.0"
  STATUS::ACTIVE
  PURPOSE::"Spec-compliant skill and pattern creation per octave-skills-spec v9.1 and octave-patterns-spec v2"
  SPEC_REFERENCE::[octave-skills-spec.oct.md,octave-patterns-spec.oct.md]

§1::CORE
AUTHORITY::BLOCKING[spec_violations⊕missing_required_fields⊕malformed_envelopes]
SCOPE::[SKILLS::OCTAVE_envelope⊕§5::ANCHOR_KERNEL⊕YAML_optional, PATTERNS::OCTAVE_envelope_only⊕§5::ANCHOR_KERNEL_required]
// Skills define WHAT agents do; Patterns define HOW agents decide

§2::PROTOCOL

SKILL_SEQUENCE::[
  YAML[name,description,allowed-tools,triggers,version]::OPTIONAL[required_for_platform_skills],
  ENVELOPE[===SKILL_NAME===,META,body_§1_to_§4,§5::ANCHOR_KERNEL,===END===],
  META_REQUIRED[TYPE::SKILL,VERSION,STATUS],
  META_OPTIONAL[PURPOSE,TIER,SPEC_REFERENCE],
  SECTIONS[§1::CORE,§2::PROTOCOL,§3::GOVERNANCE,§4::EXAMPLES],
  §5::ANCHOR_KERNEL[TARGET,NEVER,MUST,GATE]
]

PATTERN_SEQUENCE::[
  ENVELOPE[===PATTERN_NAME===,META,body,§5::ANCHOR_KERNEL,===END===],
  META_REQUIRED[TYPE::PATTERN_DEFINITION,VERSION,PURPOSE],
  SECTIONS[§1::CORE_PRINCIPLE,§2::DECISION_FRAMEWORK,§3::USED_BY],
  §5::ANCHOR_KERNEL_required[TARGET,NEVER,MUST,GATE]
]
// Patterns NEVER have YAML frontmatter

YAML_RULES::[
  PLATFORM[.claude/skills/∨.codex/skills/]::REQUIRED[platforms_parse_for_discovery],
  HUB[.hestai-sys/library/skills/]::OPTIONAL[anchor_reads_OCTAVE_not_YAML],
  DUAL_DEPLOYED::YAML_in_both[serves_platform_copy],
  YAML_PRESENT::no_duplicate_triggers_in_OCTAVE_META,
  YAML_ABSENT::OCTAVE_META_is_sole_source
]

COMPRESSION::[BODY::AGGRESSIVE,YAML::LOSSLESS[when_present],KERNEL::ULTRA]

SIZE::[SKILLS::500_target∨600_hard,PATTERNS::100_target∨150_hard,KERNEL::50_max,TOKENS::300-700_body]

§3::GOVERNANCE

OCTAVE_WRITE_GATE::[
  .oct.md→mcp__octave__octave_write[NEVER_Write∨Edit],
  SKILL.md→Write∨Edit[normal_tools]
]

VALIDATION::[
  envelope_valid⊕YAML_if_platform,
  META_required_fields_present,
  name_matches[YAML_when_present∨filename_for_patterns],
  octave_syntax_valid,
  size_under_limits,
  §5_section_header[not_legacy_§ANCHOR_KERNEL]
]

NEVER::[
  markdown_headers_in_OCTAVE_body,
  auxiliary_files[README∨CHANGELOG],
  duplicate_triggers_when_YAML_present,
  prose_in_kernel,
  exceed_hard_limits[600_skills∨150_patterns],
  Write∨Edit_for_.oct.md,
  YAML_on_patterns,
  omit_YAML_from_platform_skills
]

FALLBACK::[§5::ANCHOR_KERNEL→§3::GOVERNANCE→SIGNALS→WARN_UNSTRUCTURED]

§5::ANCHOR_KERNEL
TARGET::spec_compliant_skill_and_pattern_creation
NEVER::[markdown_headers,auxiliary_files,duplicate_meta_with_yaml,prose_in_kernel,exceed_limits,Write∨Edit_for_oct_md,yaml_on_patterns,omit_yaml_from_platform]
MUST::[read_spec_first,octave_envelope_with_META,§5_section_header,compress_body_AGGRESSIVE,octave_write_for_oct_md,yaml_per_deployment_context,validate_before_commit]
GATE::"Correct structure per spec, §5::ANCHOR_KERNEL present, YAML correct for context, .oct.md via octave_write?"

===END===
