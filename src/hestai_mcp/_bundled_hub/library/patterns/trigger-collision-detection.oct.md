===TRIGGER_COLLISION_DETECTION===
META:
  TYPE::PATTERN_DEFINITION
  VERSION::"1.2.0"
  PURPOSE::"Detect and resolve trigger keyword collisions across the skill registry"
§1::CORE_PRINCIPLE
ESSENTIAL::"Each skill must have unique trigger surface — collisions cause ambiguous skill loading"
ANTI_PATTERN::"silent_overlap<two_skills_triggered_by_same_keyword→unpredictable_selection>"
ENFORCEMENT::"Scan full registry BEFORE approving new triggers"
§2::DECISION_FRAMEWORK
SCAN_SEQUENCE::[
  1::"collect_all_triggers_from_registry<glob_SKILL.md_files>",
  2::collect_new_skill_triggers,
  3::"compare<exact_match→BLOCKING,substring_overlap→ADVISORY,semantic_proximity→ADVISORY>"
]
SEVERITY::[
  BLOCKING::exact_match<same_keyword_in_two_skills>,
  ADVISORY::"substring_overlap<create_skill⇌skill_creator>",
  ADVISORY::"semantic_proximity<compress_octave⇌octave_compression>"
]
ON_COLLISION::[
  rename_trigger<make_more_specific>,
  "merge_skills<if_functionally_overlapping→see_skill-overlap-resolution>",
  split_triggers<assign_distinct_keyword_domains>,
  escalate<ecosystem_review_if_systemic>
]
§3::USED_BY
AGENTS::[skills-expert]
CONTEXT::skill_creation⊕skill_validation⊕ecosystem_audit
§5::ANCHOR_KERNEL
TARGET::unique_trigger_surface_per_skill
NEVER::[
  approve_duplicate_triggers,
  skip_registry_scan,
  ignore_substring_overlap,
  ignore_semantic_proximity
]
MUST::[
  scan_full_registry_before_approval,
  flag_exact_matches_as_BLOCKING,
  flag_semantic_proximity_as_ADVISORY,
  recommend_specific_renames
]
GATE::"Does any existing skill already trigger on these keywords?"
===END===
