===ORCHESTRA_MAP_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"1.2-OCTAVE-SUMMARY"
  STATUS::ACTIVE
  PURPOSE::"Operational decision-logic for Orchestra Map subsystem"
  FULL_DOC::".hestai/workflow/components/000-ORCHESTRA-MAP-NORTH-STAR.md"
  INHERITS::[System_NS,Product_NS]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS::6[meets_PROPHETIC_VIGILANCE]

SECTION_ORDER::[S1::IMMUTABLES,S2::ASSUMPTIONS,S3::VARIABLES,S4::SCOPE,S5::GATES,S6::DEPENDENCY_PATTERN,S7::DEPENDENCIES,S8::ESCALATION,S9::TRIGGERS,S10::PROTECTION]

S1::IMMUTABLES[5_Total]

OM-I1::ANCHOR_PATTERN_INVERSION::[
  PRINCIPLE::Specs_claim_Code_via_imports[not_vice_versa],
  WHY::code_annotations_rot[active_imports_are_verifiable],
  STATUS::PENDING[implementation-lead@B1]
]

OM-I2::ONE_WAY_BUILD_ISOLATION::[
  PRINCIPLE::governance_artifacts_excluded_from_production_builds,
  WHY::governance_metadata_must_not_bloat_or_break_shipping_product,
  STATUS::PENDING[implementation-lead@B1]
]

OM-I3::ALGORITHMIC_STALENESS::[
  PRINCIPLE::staleness_is_binary_computable_function_of_git_timestamps,
  WHY::agents_need_binary_signals[Stop/Go]_not_nuanced_probabilities,
  STATUS::PENDING[implementation-lead@B1]
]

OM-I4::POLYGLOT_UNIVERSALITY::[
  PRINCIPLE::architecture_relies_only_on_universal_concepts[Files+Imports],
  WHY::HestAI_must_work_for_Python+TS+Rust+Go+etc,
  STATUS::PENDING[implementation-lead@B1]
]

OM-I5::AST_BASED_TRUTH::[
  PRINCIPLE::dependencies_derived_from_AST_analysis_not_regex,
  WHY::grep_is_brittle[true_deps_require_language_structure_understanding],
  STATUS::PENDING[implementation-lead@B1]
]

S2::CRITICAL_ASSUMPTIONS[6_Total]

OM-A1::SPEC_IMPORTS_CODE_VALID[85%|High]->PENDING[technical-architect@B1]
OM-A2::GIT_TIMESTAMP_SUFFICIENT[80%|Medium]->PENDING[implementation-lead@B2]
OM-A3::BUILD_EXCLUSION_RELIABLE[90%|High]->PENDING[technical-architect@B1]
OM-A4::AST_TOOLING_AVAILABLE[75%|High]->PENDING[technical-architect@B1]
OM-A5::SPEC_PATTERN_IDE_SAFE[80%|Medium]->PENDING[implementation-lead@B2]
OM-A6::STALENESS_CHECK_PERFORMANT[70%|Medium]->PENDING[implementation-lead@B1]

S3::CONSTRAINED_VARIABLES[Top_5]

LINK_DIRECTION::[IMMUTABLE::Spec->Code[OM-I1],FLEXIBLE::file_naming_convention]
STALENESS_LOGIC::[IMMUTABLE::time-based[OM-I3],FLEXIBLE::grace_period_parameters]
TOOLING::[IMMUTABLE::AST-based[OM-I5],FLEXIBLE::specific_libraries_used]
BUILD_EXCLUSION::[IMMUTABLE::governance_excluded[OM-I2],FLEXIBLE::exclusion_mechanism]
LANGUAGE_SUPPORT::[IMMUTABLE::universal_concepts[OM-I4],FLEXIBLE::priority_order_rollout]

S4::SCOPE_BOUNDARIES

IS::[
  dependency_graph_analysis[file_relationships],
  anchor_pattern_inversion_enforcement[Spec->Code],
  staleness_detection[algorithmic_binary],
  AST-based_relationship_extraction[imports+references],
  build_isolation_verification[governance_excluded]
]

IS_NOT::[
  code_generation[implementation_domain],
  context_synthesis[System_Steward_responsibility],
  file_watching[Living_Artifacts_responsibility],
  documentation_authoring[doc_tools_consume_output],
  IDE_integration[IDE_plugins_are_consumers],
  governance_rule_definition[North_Stars_define+Orchestra_enforces]
]

S5::DECISION_GATES

GATES::D1[DONE]->B0[PENDING]->B1[PENDING]->B2[PENDING]->B3[PENDING]

S6::DEPENDENCY_PATTERN

ANCHOR_INVERSION::[
  DIRECTION::Spec_imports_Code[not_Code_annotates_Spec],
  VALIDATION::CI_fails_if_src/_imports_anchors/,
  RATIONALE::active_imports_are_verifiable+dont_rot
]

STALENESS_ALGORITHM::[
  FORMULA::LastCommit(Spec)<LastCommit(Impl)==STALE,
  BINARY::no_subjective_health_scores,
  SCRIPT::staleness_check_uses_git_logs
]

BUILD_ISOLATION::[
  EXCLUDED::[anchors/,specs/],
  ARROW::Governance->Production[one_way_only],
  VALIDATION::build_config_explicitly_excludes
]

AST_TOOLING::[
  REQUIRED::dependency-cruiser|ast_module|equivalent,
  PROHIBITED::regex_text_search_for_deps,
  RATIONALE::reliability_over_simplicity
]

S7::DEPENDENCIES

BLOCKING::[]
RELATED::[ADR-0046]

S8::AGENT_ESCALATION

requirements-steward::[violates_OM-I#,scope_question,NS_amendment]
technical-architect::[architecture_decisions,AST_tooling_selection]
implementation-lead::[assumption_validation,build_execution]

S9::TRIGGER_PATTERNS

LOAD_FULL_NORTH_STAR_IF::[
  "violates OM-I1-I5"::immutable_conflict,
  "Spec->Code pattern"::anchor_inversion_question,
  "staleness algorithm"::freshness_logic,
  "AST tooling"::parser_selection
]

S10::PROTECTION_CLAUSE

IF::work_contradicts_North_Star->STOP->CITE[OM-I#]->ESCALATE[requirements-steward]

THE_OATH::"5 Immutables (OM-I1-I5) bind Orchestra Map implementation. Contradiction requires STOP, CITE, ESCALATE."

===END===
