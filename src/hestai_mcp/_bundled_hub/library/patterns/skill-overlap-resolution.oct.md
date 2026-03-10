===SKILL_OVERLAP_RESOLUTION===
META:
  TYPE::PATTERN_DEFINITION
  VERSION::"1.0.0"
  PURPOSE::"Detect and resolve functional overlap between skills in the ecosystem"
§1::CORE_PRINCIPLE
ESSENTIAL::"Each skill occupies a unique capability niche — overlap wastes context tokens and creates ambiguity"
ANTI_PATTERN::"capability_sprawl<multiple_skills_serving_same_function→agent_confusion⊕token_waste>"
ENFORCEMENT::"Compare PURPOSE, ANCHOR_KERNEL atoms, and SPEC_REFERENCE before approving new skills"
§2::DETECTION_SIGNALS
OVERLAP_INDICATORS::[
  "similar_PURPOSE_fields<\"70_percent_plus_semantic_overlap\">",
  shared_NEVER_or_MUST_atoms_in_kernels,
  same_SPEC_REFERENCE<two_skills_referencing_same_spec>,
  "overlapping_triggers<see_trigger-collision-detection>",
  identical_AUTHORITY_scope
]
§3::RESOLUTION_STRATEGIES
ON_OVERLAP::[
  MERGE::combine_into_single_skill<when_scope_is_subset>,
  SPLIT::separate_by_concern<when_partial_overlap_with_distinct_cores>,
  DEPENDENCY::establish_REQUIRES_chain<when_one_extends_the_other>,
  DEPRECATE::retire_weaker_skill<when_superseded_by_newer_with_broader_scope>,
  ESCALATE::ecosystem_review<when_overlap_is_systemic_across_3_plus_skills>
]
§4::USED_BY
AGENTS::[skills-expert]
CONTEXT::skill_creation⊕ecosystem_audit⊕capability_review
§5::ANCHOR_KERNEL
TARGET::unique_capability_niche_per_skill
NEVER::[
  approve_redundant_skills,
  ignore_PURPOSE_similarity,
  skip_kernel_comparison
]
MUST::[
  compare_PURPOSE_fields,
  compare_ANCHOR_KERNEL_atoms,
  check_SPEC_REFERENCE_overlap,
  recommend_merge_or_split_or_deprecate
]
GATE::"Does this new skill duplicate capability already provided by an existing skill?"
===END===
