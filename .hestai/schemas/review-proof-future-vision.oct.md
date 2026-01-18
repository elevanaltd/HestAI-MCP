===REVIEW_PROOF===
META:
  TYPE::SCHEMA
  VERSION::"1.0"
  STATUS::FUTURE_VISION
  PURPOSE::"Future enhancement: Full artifact-centric orchestration schema for self-documenting review compliance"
  NOTE::"Currently using simpler PR comment magic. This represents the eventual goal."
  AUTHORITY::FUTURE[Will require all code reviews to generate valid REVIEW_PROOF]
  ENFORCEMENT::FUTURE[Will gate merges on artifact validation]

§1::IDENTITY
SCHEMA_CONTRACT::[
  ROLE::"Review compliance artifact replacing active orchestration",
  COGNITION::"Declarative compliance through structured evidence",
  BINDING::"Reviewers bind to this schema via odyssean_anchor",
  OUTPUT::"Self-documenting governance artifact"
]

§2::MANDATORY_FIELDS
REQUIREMENTS_CHECKED::[
  north_star_alignment::BOOLEAN[verified_against_immutables],
  acceptance_criteria::BOOLEAN[all_criteria_met],
  scope_boundaries::BOOLEAN[no_scope_creep_detected],
  citations::ARRAY[specific_requirements_verified]
]

TESTS_VERIFIED::[
  coverage_threshold::NUMBER[percentage_achieved],
  test_execution::ENUM[all_passing|failures_documented|blocked],
  test_types::ARRAY[unit|integration|e2e|performance|security],
  evidence::ARRAY[test_output_references]
]

RISKS_ASSESSED::[
  security_review::ENUM[no_issues|issues_mitigated|blocking_issues],
  performance_impact::ENUM[none|acceptable|needs_optimization|blocking],
  architectural_drift::BOOLEAN[no_drift_detected],
  technical_debt::ENUM[none_added|documented|excessive],
  failure_modes::ARRAY[identified_failure_scenarios]
]

DECISION_RATIONALE::[
  verdict::ENUM[approved|approved_with_conditions|rejected|needs_rework],
  blocking_issues::ARRAY[specific_blockers_if_any],
  conditions::ARRAY[requirements_for_conditional_approval],
  recommendations::ARRAY[improvement_suggestions],
  reviewer_confidence::ENUM[high|medium|low]
]

§3::METADATA
REVIEW_CONTEXT::[
  reviewer_role::ENUM[code-review-specialist|critical-engineer|technical-architect],
  review_type::ENUM[implementation|architecture|security|performance],
  complexity_assessment::ENUM[trivial|standard|complex|critical],
  time_invested::NUMBER[minutes_spent],
  debate_triggered::BOOLEAN[required_multi-model_consensus]
]

TRACEABILITY::[
  commit_range::STRING[git_sha_range_reviewed],
  files_reviewed::ARRAY[file_paths_examined],
  pr_reference::STRING[github_pr_number_or_issue],
  timestamp::DATETIME[review_completion_time],
  session_id::STRING[odyssean_anchor_session]
]

§4::VALIDATION_RULES
COMPLETENESS::[
  ALL_MANDATORY_FIELDS::MUST_BE_POPULATED,
  EVIDENCE_REQUIREMENTS::MIN_3_CITATIONS_PER_CLAIM,
  RATIONALE_DEPTH::MIN_100_CHARS_FOR_DECISION
]

CONSISTENCY::[
  VERDICT_ALIGNMENT::"verdict must align with identified issues",
  EVIDENCE_CORRELATION::"test results must support risk assessment",
  SCOPE_VERIFICATION::"requirements_checked must reference actual requirements"
]

§5::GENERATION_PROTOCOL
REVIEWER_WORKFLOW::[
  1::BIND_TO_SCHEMA[odyssean_anchor_binding],
  2::EXECUTE_REVIEW[systematic_evaluation],
  3::POPULATE_FIELDS[evidence_based_filling],
  4::VALIDATE_ARTIFACT[schema_compliance_check],
  5::SUBMIT_PROOF[git_commit_with_artifact]
]

AUTOMATION_HOOKS::[
  PRE_COMMIT::"Validate REVIEW_PROOF exists for changes",
  CI_PIPELINE::"Parse and verify artifact completeness",
  MERGE_GATE::"Block if artifact missing or invalid",
  METRICS_COLLECTION::"Extract review metrics for analysis"
]

§6::INTEGRATION
REPLACES::[
  "Active HO monitoring of individual review steps",
  "IL/HO orchestration ambiguity",
  "Undocumented review decisions"
]

PRESERVES::[
  "Mandatory review gates (CRS→CE chain)",
  "Evidence-based compliance",
  "Audit trail requirements",
  "System governance constraints"
]

COMPATIBLE_WITH::[
  debate-hall::"Complex reviews trigger debates",
  github_issues::"PR references maintain linkage",
  mcp_tools::"Review automation via MCP",
  ci_systems::"Artifact validation in pipelines"
]

§7::EXAMPLES
APPROVED_REVIEW:
  ```octave
  REQUIREMENTS_CHECKED::[
    north_star_alignment::true,
    acceptance_criteria::true,
    scope_boundaries::true,
    citations::["I2:structural_integrity","REQ-001","REQ-017"]
  ]
  TESTS_VERIFIED::[
    coverage_threshold::92,
    test_execution::all_passing,
    test_types::[unit,integration],
    evidence::["pytest.log:L45-67","ci/build/123"]
  ]
  RISKS_ASSESSED::[
    security_review::no_issues,
    performance_impact::none,
    architectural_drift::false,
    technical_debt::none_added,
    failure_modes::[]
  ]
  DECISION_RATIONALE::[
    verdict::approved,
    blocking_issues::[],
    conditions::[],
    recommendations::["Consider adding e2e test for edge case"],
    reviewer_confidence::high
  ]
  ```

CONDITIONAL_APPROVAL:
  ```octave
  DECISION_RATIONALE::[
    verdict::approved_with_conditions,
    blocking_issues::[],
    conditions::["Add missing test for error path","Update documentation"],
    recommendations::["Refactor for clarity in v2"],
    reviewer_confidence::medium
  ]
  ```

§8::MIGRATION_PATH
PHASE_1::"Define schema and educate reviewers"
PHASE_2::"Soft enforcement - generate artifacts alongside current process"
PHASE_3::"Hard enforcement - CI gates require artifacts"
PHASE_4::"Retire active orchestration - schema-driven only"

===END===
