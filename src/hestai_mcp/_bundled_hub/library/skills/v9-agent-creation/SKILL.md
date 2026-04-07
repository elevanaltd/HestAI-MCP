===SKILL:V9_AGENT_CREATION===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"V9 blank-slate agent file creation per dream-team-architecture.md §2.2"
  SPEC_REFERENCE::docs/dream-team-architecture.md

§1::CORE
AUTHORITY::BLOCKING[v9_agent_file_commits⊕blank_slate_violations⊕phantom_task_profile_references<when_matrix_exists>]
SCOPE::"Create and modify V9 agent .oct.md files per dream-team-architecture §2.2 blank-slate schema"
// V9 agent files are ~50 line identity-only documents
// Skills, patterns, and archetypes resolve dynamically via archetype-matrix config

§2::PROTOCOL

CREATION_SEQUENCE::[
  1::read_dream-team-architecture_§2.2[V9_schema_spec],
  2::read_interview_assessment[from_agent-interview_skill_or_structured_equivalent],
  // agent-interview skill uses v8.1 terminology but its behavioral questions are schema-agnostic.
  // Interpret assessment findings through V9 lens (profiles not capabilities, identity not chassis).
  3::select_cognition[LOGOS∨ETHOS∨PATHOS]→read_cognition_master_file,
  4::author_v9_agent_file[§1::IDENTITY→§2::OPERATIONAL_BEHAVIOR→§3::TASK_PROFILES→§4::GRAMMAR],
  5::author_archetype_matrix_entry[map_PROFILES_to_json_node⊕assign_archetypes_per_triad_physics_N1_or_N3⊕assign_skill_keys⊕assign_pattern_keys],
  6::enforce_blank_slate[no_archetypes⊕no_skills⊕no_patterns_in_agent_file],
  7::request_subject_agent_signoff,
  8::write_via_octave_write
]

V9_STRUCTURE::[
  META::[TYPE::AGENT_DEFINITION,VERSION,PURPOSE,CONTRACT],
  "§1::IDENTITY"::[ROLE,COGNITION,MISSION,PRINCIPLES[],AUTHORITY{ULTIMATE,BLOCKING,MANDATE}],
  "§2::OPERATIONAL_BEHAVIOR"::[TONE,MUST_ALWAYS[],MUST_NEVER[],DELIVERABLES[],EVIDENCE[],GATES[],HANDOFF,ESCALATION],
  "§3::TASK_PROFILES"::[PROFILES::[],DEFAULT::name],
  "§4::GRAMMAR"::[MUST_USE::[REGEX],MUST_NOT::[PATTERN]]
]
// NO ARCHETYPE in §1 (blank slate — lives in archetype-matrix config)
// NO MODEL_TIER (deployment config, not identity)
// NO §3::CAPABILITIES (V9 uses §3::TASK_PROFILES)
// NO §4::INTERACTION_RULES (V9 uses §4::GRAMMAR)
// §2 is flat (no CONDUCT wrapper)

BLANK_SLATE_RULES::[
  NO_ARCHETYPES::"§1::IDENTITY must NOT contain ARCHETYPE field — archetypes resolve via archetype-matrix",
  NO_SKILLS::"Agent file must NOT contain skill references — skills resolve via archetype-matrix profiles",
  NO_PATTERNS::"Agent file must NOT contain pattern references — patterns resolve via archetype-matrix profiles",
  NO_MODEL_TIER::"Agent file must NOT contain MODEL_TIER — deployment config is external",
  PROFILE_NAMES_ONLY::"§3::TASK_PROFILES contains profile NAME list + DEFAULT — no capability bindings"
]

TASK_PROFILE_RULES::[
  PROFILES_is_array_of_names[string_identifiers_not_objects],
  DEFAULT_must_exist_in_PROFILES_array,
  each_name_should_map_to_archetype-matrix_entry<when_matrix_exists>,
  names_use_snake_case[code_writing∨test_building∨error_diagnosis]
]

ARCHETYPE_MATRIX_EDITING::[
  PROTOCOL::[
    1::read_archetype-matrix_json[resources/starter-library/config/archetype-matrix.json],
    2::identify_agent_role_key[snake-case_matching_agent_file_name],
    3::create_profiles_object_with_one_entry_per_TASK_PROFILE,
    4::per_profile_assign[archetypes⊕skills⊕patterns],
    5::write_modified_json_preserving_existing_entries[Edit_tool_for_json],
    6::validate_json_syntax[python3_json_load_check]
  ],
  JSON_SCHEMA::"matrix → agent-role → profiles → { profile_name: { archetypes: [], skills: [], patterns: [] } }",
  DATA_ENTRY_RULE::"Read file → Edit specific node → Write back. NEVER rewrite entire file. Preserve all other agent entries.",
  TRIAD_PHYSICS::[
    "N=1::Single archetype with behavioral emphasis for tactical focus profiles (code_writing, gating, security_review)",
    "N=3::Triad of archetypes with behavioral emphasis for multi-objective profiles (orchestration, refactoring, strategic_planning)",
    "N=2::FORBIDDEN — binary deadlock creates unresolvable tension without synthesis axis",
    "FORMAT::Each archetype entry is a string with behavioral emphasis: ARCHETYPE<behavioral_application>"
  ],
  ARCHETYPE_FORMAT_EXAMPLES::[
    "N=1_EXAMPLE::\"HEPHAESTUS<implementation_craft>\"",
    "N=3_EXAMPLE::[\"ODYSSEUS<cross_boundary_navigation>\", \"ATLAS<ultimate_accountability>\", \"APOLLO<system_foresight>\"]"
  ]
]

AUTHORITY_STRUCTURE::[
  ULTIMATE::"Capabilities this agent owns exclusively (list of domains)",
  BLOCKING::"Conditions that MUST be blocked (list of violations)",
  MANDATE::"Single sentence: what this agent prevents from happening"
]

COGNITION_RULES::[
  single_cognition_only[LOGOS∨ETHOS∨PATHOS],
  cognition_master_provides[FORCE⊕ESSENCE⊕ELEMENT⊕MODE⊕PRIME_DIRECTIVE⊕CRAFT⊕THINK⊕THINK_NEVER],
  agent_files_do_NOT_duplicate_cognition_properties,
  COGNITION_field_in_§1_is_link_key_to_library_cognitions_TYPE_oct_md
]

SIZE_TARGET::"~50 lines — lean identity only. Everything that resolves dynamically is excluded."

§3::GOVERNANCE

NEVER::[
  author_without_interview_assessment,
  include_ARCHETYPE_in_§1[blank_slate_violation],
  include_skills_or_patterns_in_agent_file[blank_slate_violation],
  include_MODEL_TIER[deployment_config_not_identity],
  use_§3::CAPABILITIES[V9_uses_§3::TASK_PROFILES],
  use_§4::INTERACTION_RULES[V9_uses_§4::GRAMMAR],
  include_CONDUCT_wrapper_in_§2[V9_§2_is_flat],
  phantom_task_profile_references<when_matrix_exists>,
  Write∨Edit_for_oct_md[use_octave_write],
  exceed_50_line_target_without_justification
]

VALIDATION::[
  V9_structure_compliance[all_4_sections_present],
  blank_slate_verified[no_archetypes⊕no_skills⊕no_patterns],
  DEFAULT_profile_exists_in_PROFILES_array,
  AUTHORITY_has_ULTIMATE⊕BLOCKING⊕MANDATE,
  §2_is_flat[no_CONDUCT_wrapper],
  cognition_is_link_key_only[no_duplicated_properties],
  file_approximately_50_lines[~50_target_with_justification_for_exceptions]
]

§5::ANCHOR_KERNEL
TARGET::v9_blank_slate_agent_file_creation
NEVER::[archetypes_in_agent_file,skills_in_agent_file,patterns_in_agent_file,MODEL_TIER_in_agent_file,§3::CAPABILITIES_structure,§4::INTERACTION_RULES_structure,CONDUCT_wrapper,phantom_task_profile_references<when_matrix_exists>,authoring_without_assessment,Write∨Edit_for_oct_md]
MUST::[read_dream-team-architecture_first,interview_evidence,enforce_blank_slate,author_matrix_entry[archetypes_N1_or_N3⊕skills⊕patterns],subject_agent_signoff,~50_line_target,flat_§2_structure,AUTHORITY{ULTIMATE⊕BLOCKING⊕MANDATE},octave_write_for_oct_md]
GATE::"V9 compliant blank-slate agent file with §1::IDENTITY→§2::OPERATIONAL_BEHAVIOR→§3::TASK_PROFILES→§4::GRAMMAR, archetype-matrix entry authored with triad physics, subject agent signoff obtained?"

===END===
