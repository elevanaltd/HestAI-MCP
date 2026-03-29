===SKILL:GOVERNANCE_REVIEW===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Methodology for evidence-based governance documentation review. Provides structured analysis framework for reviewing architectural decisions, specs, rules, and governance artifacts against North Star alignment, cross-document consistency, structural completeness, and downstream impact."

§1::GOVERNANCE_REVIEW_DIMENSIONS
DIMENSIONS::[
  ALIGNMENT::[
    DEFINITION::"Does this artifact align with North Star immutables (I1-I6)?",
    CHECK::"Map each claim, rule, or decision to a specific immutable or justify its independence",
    EVIDENCE::"North Star clause reference + alignment reasoning",
    VERDICT::ALIGNED|MISALIGNED|JUSTIFIED_DEVIATION
  ],
  CONTRADICTION::[
    DEFINITION::"Does this artifact contradict any existing governance document?",
    CHECK::"Cross-reference against decisions/, specs/, rules/, agent definitions, and patterns",
    EVIDENCE::"Document reference + specific clause conflict + severity",
    VERDICT::NO_CONTRADICTION|MINOR_TENSION|BLOCKING_CONTRADICTION
  ],
  COMPLETENESS::[
    DEFINITION::"Does this artifact have all required fields and sufficient justification?",
    CHECK::"Validate OCTAVE structure, required sections, meta fields, and reasoning depth",
    EVIDENCE::"Missing field list + structural validation results",
    VERDICT::COMPLETE|INCOMPLETE|STRUCTURALLY_INVALID
  ],
  IMPACT::[
    DEFINITION::"What downstream effects does this governance change have?",
    CHECK::"Map impact on agents, skills, patterns, workflows, and CI pipelines",
    EVIDENCE::"Affected artifact list + impact severity per artifact",
    VERDICT::NO_IMPACT|LOW_IMPACT|HIGH_IMPACT|BREAKING_IMPACT
  ],
  PRECEDENCE::[
    DEFINITION::"Does this artifact respect the structural precedence hierarchy?",
    CHECK::"Verify System Standard > North Stars > ADRs > Workflows ordering",
    EVIDENCE::"Hierarchy position + any violations of lower-overrides-higher",
    VERDICT::COMPLIANT|VIOLATION
  ],
  SCOPE::[
    DEFINITION::"Is this artifact within the documented scope boundaries?",
    CHECK::"Validate against North Star IS/IS_NOT declarations",
    EVIDENCE::"Scope boundary reference + in/out determination",
    VERDICT::IN_SCOPE|OUT_OF_SCOPE|SCOPE_EXPANSION_PROPOSED
  ]
]

§2::GOVERNANCE_FILE_TYPE_CHECKLIST
FILE_TYPES::[
  ADR::[
    REQUIRED_FIELDS::[number,title,status,context,decision,consequences],
    NUMBERING::"Must follow ADR numbering convention (ADR-NNNN)",
    STATUS_VALUES::[PROPOSED,ACCEPTED,DEPRECATED,SUPERSEDED],
    TRACEABILITY::"Must reference triggering issue or discussion"
  ],
  NORTH_STAR::[
    REQUIRED_FIELDS::[immutables,assumptions,constrained_variables,scope_boundaries],
    IMMUTABLE_FORMAT::"I#::NAME::[PRINCIPLE,WHY,STATUS]",
    AMENDMENT_RULE::"Only human authority can modify immutables"
  ],
  AGENT_DEFINITION::[
    REQUIRED_SECTIONS::[IDENTITY,OPERATIONAL_BEHAVIOR,CAPABILITIES,INTERACTION_RULES],
    IDENTITY_FIELDS::[ROLE,COGNITION,ARCHETYPE,MISSION,AUTHORITY_BLOCKING],
    CHASSIS_VERSION::"Must match current chassis version (v8.2)",
    SKILL_EXISTENCE::"Referenced skills must exist in library/skills/"
  ],
  SKILL_DEFINITION::[
    REQUIRED_FIELDS::[META,PURPOSE,at_least_one_protocol_section],
    ANCHOR_KERNEL::"Should include §5::ANCHOR_KERNEL with TARGET, NEVER, MUST, GATE",
    NAMING::"Directory name must match skill identifier in agent CAPABILITIES"
  ],
  PATTERN_DEFINITION::[
    REQUIRED_SECTIONS::[CORE_PRINCIPLE,DECISION_FRAMEWORK,USED_BY,ANCHOR_KERNEL],
    ANTI_PATTERN::"Must declare the anti-pattern this pattern prevents",
    AGENT_BINDING::"USED_BY must list consuming agents"
  ],
  SPEC::[
    REQUIRED_FIELDS::[purpose,scope,requirements,acceptance_criteria],
    TRACEABILITY::"Must reference parent North Star requirement or ADR"
  ],
  RULE::[
    REQUIRED_FIELDS::[scope,rule_statement,enforcement,exceptions],
    AUTHORITY::"Must declare which authority level enforces the rule"
  ]
]

§3::REVIEW_PROTOCOL
SCAN_ORDER::[
  STEP_1_CLASSIFICATION::"Classify each changed file by governance type (ADR, North Star, Agent, Skill, Pattern, Spec, Rule)",
  STEP_2_ALIGNMENT::"For each file, validate North Star alignment across all six immutables",
  STEP_3_CONTRADICTION::"Cross-reference against existing governance corpus for conflicts",
  STEP_4_COMPLETENESS::"Validate structural completeness per file type checklist",
  STEP_5_IMPACT::"Map downstream impact on agents, skills, patterns, and CI",
  STEP_6_PRECEDENCE::"Verify hierarchy compliance",
  STEP_7_SCOPE::"Validate scope boundary compliance",
  STEP_8_VERDICT::"Synthesize findings into structured verdict with metadata"
]

ANTI_THEATER_GATE::[
  "Do NOT review governance documents for code quality, test coverage, or performance",
  "Do NOT flag style issues in prose unless they create ambiguity",
  "Do NOT require changes that are outside the scope of the PR's governance intent",
  "Do NOT apply code review heuristics (SOLID, DRY, etc.) to governance documents"
]

§4::GOVERNANCE_PRIORITY_TIERS
TIERS::[
  G0_ALIGNMENT::[
    SCOPE::North_Star_contradiction⊕immutable_violation⊕precedence_hierarchy_breach,
    ACTION::ALWAYS_REPORT_FIRST,
    CONFIDENCE_FLOOR::MODERATE,
    BLOCKING::ALWAYS
  ],
  G1_CONTRADICTION::[
    SCOPE::cross_document_conflict⊕incompatible_decisions⊕rule_conflict,
    ACTION::REPORT_AFTER_G0,
    CONFIDENCE_FLOOR::HIGH,
    BLOCKING::WHEN_CERTAIN_OR_HIGH
  ],
  G2_COMPLETENESS::[
    SCOPE::missing_required_fields⊕structural_invalidity⊕insufficient_justification,
    ACTION::REPORT_AFTER_G1,
    CONFIDENCE_FLOOR::HIGH,
    BLOCKING::WHEN_STRUCTURALLY_INVALID
  ],
  G3_IMPACT::[
    SCOPE::undocumented_downstream_effects⊕scope_expansion⊕agent_skill_pattern_breakage,
    ACTION::REPORT_IF_WITHIN_BUDGET,
    CONFIDENCE_FLOOR::HIGH,
    BLOCKING::WHEN_BREAKING_IMPACT
  ]
]

§5::ANCHOR_KERNEL
TARGET::evidence_based_governance_documentation_review
NEVER::[
  review_code_quality_in_governance_PRs,
  approve_North_Star_contradictions,
  skip_cross_document_contradiction_check,
  approve_incomplete_governance_artifacts_without_flagging,
  ignore_downstream_impact_on_agents_and_skills,
  report_speculative_findings_without_evidence
]
MUST::[
  validate_North_Star_alignment_for_every_governance_artifact,
  cross_reference_against_existing_governance_corpus,
  verify_structural_completeness_per_file_type,
  map_downstream_impact_on_agents_skills_patterns,
  verify_precedence_hierarchy_compliance,
  produce_structured_metadata_verdict_in_review_gate_format
]
GATE::"Does this governance artifact align with the North Star, avoid contradictions with existing documents, meet structural completeness requirements, and have documented downstream impact?"

===END===
