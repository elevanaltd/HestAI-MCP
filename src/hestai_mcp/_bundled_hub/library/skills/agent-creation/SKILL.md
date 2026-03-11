===SKILL:AGENT_CREATION===
META:
  TYPE::SKILL
  VERSION::"2.0.0"
  STATUS::ACTIVE
  PURPOSE::"v8.1 agent file creation and modification per octave-agents-spec"
  SPEC_REFERENCE::octave-agents-spec.oct.md

§1::CORE
AUTHORITY::BLOCKING[agent_file_commits⊕phantom_references⊕spec_violations]
SCOPE::"Create and modify agent .oct.md files per octave-agents-spec v8.1"
// Agent-expert owns WHAT goes in agent files; octave-specialist owns HOW OCTAVE is structured

§2::PROTOCOL

CREATION_SEQUENCE::[
  1::read_octave-agents-spec,
  2::read_interview_assessment[from_agent-interview_skill],
  3::select_cognition[LOGOS∨ETHOS∨PATHOS]→read_cognition_master_file,
  4::select_2-3_archetypes_with_behavioral_emphasis[see_archetype-database.oct.md],
  5::author_v8.1_agent_file[§1::IDENTITY→§2::OPERATIONAL_BEHAVIOR→§3::CAPABILITIES→§4::INTERACTION_RULES],
  6::verify_all_skill_and_pattern_references_exist_on_disk,
  7::request_subject_agent_signoff,
  8::write_via_octave_write
]

V8_1_STRUCTURE::[
  META::[TYPE::AGENT_DEFINITION,VERSION,PURPOSE,CONTRACT],
  "§1::IDENTITY"::[ROLE,COGNITION,ARCHETYPE,MODEL_TIER,MISSION,PRINCIPLES,AUTHORITY_*],
  "§2::OPERATIONAL_BEHAVIOR"::[CONDUCT→TONE⊕PROTOCOL⊕OUTPUT⊕VERIFICATION⊕INTEGRATION],
  "§3::CAPABILITIES"::[CHASSIS∨flat_SKILLS,PROFILES∨flat_PATTERNS],
  "§4::INTERACTION_RULES"::[GRAMMAR→MUST_USE⊕MUST_NOT]
]

CHASSIS_VS_PROFILE::[
  CHASSIS::"Skills loaded EVERY ceremony regardless of context",
  PROFILES::"Context-specific skill sets with match conditions",
  "match::[default]"::"Fallback profile (sole condition only)",
  "match::[context::X]"::"Documentation-as-schema (not runtime logic)",
  kernel_only::"§5::ANCHOR_KERNEL extraction only (not full body)"
]

YAML_RULES::[
  PLATFORM_AGENTS[".claude/agents/"]::YAML_REQUIRED,
  HUB_AGENTS[".hestai-sys/library/agents/"]::YAML_NOT_REQUIRED,
  // Per octave-agents-spec §6: anchor reads OCTAVE META not YAML
]

COGNITION_RULES::[
  single_cognition_only[LOGOS∨ETHOS∨PATHOS],
  cognition_master_provides[NATURE⊕MODE⊕PRIME_DIRECTIVE⊕THINK⊕THINK_NEVER],
  agent_files_do_NOT_duplicate_cognition_properties,
  COGNITION_field_in_§1_is_link_key_to_library_cognitions_TYPE_oct_md
]

§3::GOVERNANCE

NEVER::[
  author_without_interview_assessment,
  include_phantom_references[skills_or_patterns_not_on_disk],
  duplicate_cognition_properties_in_agent_files,
  embed_SHANK_overlays[cognition_masters_are_separate_files],
  use_old_section_numbering["§1-§13 is pre-v7; current is §1-§4"],
  Write∨Edit_for_.oct.md[use_octave_write]
]

RESOURCES::[archetype-database.oct.md]

§5::ANCHOR_KERNEL
TARGET::v8_1_compliant_agent_file_creation
NEVER::[phantom_references,authoring_without_assessment,cognition_duplication,old_section_numbering,Write∨Edit_for_oct_md]
MUST::[read_spec_first,interview_evidence,verify_disk_references,subject_agent_signoff,octave_write_for_oct_md]
GATE::"v8.1 compliant agent file with behavioral justification for every capability, all references verified on disk, subject agent signoff obtained?"

===END===
