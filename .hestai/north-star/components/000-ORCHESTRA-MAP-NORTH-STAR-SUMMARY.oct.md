===ORCHESTRA_MAP_NORTH_STAR_SUMMARY===
META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"2.1-UPOG-TELEGRAPHIC"
  STATUS::ACTIVE
  NAMESPACE::PROD
  PURPOSE::"Operational decision-logic for Orchestra Map subsystem"
  FULL_DOC::".hestai/workflow/components/000-ORCHESTRA-MAP-NORTH-STAR.md"
  INHERITS::[System_NS,Product_NS]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS_COUNT::6
  ASSUMPTIONS_NOTE::meets_PROPHETIC_VIGILANCE
  CONTRACT::HOLOGRAPHIC<parse_only_governance>
  CANONICAL::".hestai/north-star/components/000-ORCHESTRA-MAP-NORTH-STAR-SUMMARY.oct.md"
  SOURCE::".hestai/north-star/components/000-ORCHESTRA-MAP-NORTH-STAR-SUMMARY.oct.md"
§1::IMMUTABLES
  COUNT::5
  OM_I1<ANCHOR_PATTERN_INVERSION>:
    PRINCIPLE::"Specs → Code via imports ⇌ Code annotates Specs"
    WHY::"code annotations → rot ⇌ active imports → verifiable"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  OM_I2<ONE_WAY_BUILD_ISOLATION>:
    PRINCIPLE::"production builds ⇌ governance artifacts [excluded]"
    WHY::"governance metadata → shipping product safety [no bloat ⊕ no break]"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  OM_I3<ALGORITHMIC_STALENESS>:
    PRINCIPLE::"staleness → binary function over git timestamps"
    WHY::"agents → binary Stop/Go signals ⇌ nuanced probabilities"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  OM_I4<POLYGLOT_UNIVERSALITY>:
    PRINCIPLE::"architecture → Files ⊕ Imports universals only"
    WHY::"HestAI → Python ⊕ TS ⊕ Rust ⊕ Go ⊕ etc [universal]"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  OM_I5<AST_BASED_TRUTH>:
    PRINCIPLE::"dependencies → AST analysis ⇌ regex"
    WHY::"grep → brittle ⇌ true deps need language structure"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
§2::CRITICAL_ASSUMPTIONS
  COUNT::6
  OM_A1<SPEC_IMPORTS_CODE_VALID>:
    CONFIDENCE::"85%"
    RISK::High
    STATUS::PENDING
    OWNER::technical-architect
    GATE::B1
  OM_A2<GIT_TIMESTAMP_SUFFICIENT>:
    CONFIDENCE::"80%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  OM_A3<BUILD_EXCLUSION_RELIABLE>:
    CONFIDENCE::"90%"
    RISK::High
    STATUS::PENDING
    OWNER::technical-architect
    GATE::B1
  OM_A4<AST_TOOLING_AVAILABLE>:
    CONFIDENCE::"75%"
    RISK::High
    STATUS::PENDING
    OWNER::technical-architect
    GATE::B1
  OM_A5<SPEC_PATTERN_IDE_SAFE>:
    CONFIDENCE::"80%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  OM_A6<STALENESS_CHECK_PERFORMANT>:
    CONFIDENCE::"70%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
§3::CONSTRAINED_VARIABLES
  LINK_DIRECTION:
    IMMUTABLE::"Spec → Code [OM-I1]"
    FLEXIBLE::file_naming_convention
  STALENESS_LOGIC:
    IMMUTABLE::"time-based [OM-I3]"
    FLEXIBLE::grace_period_parameters
  TOOLING:
    IMMUTABLE::"AST-based [OM-I5]"
    FLEXIBLE::specific_libraries_used
  BUILD_EXCLUSION:
    IMMUTABLE::"governance excluded [OM-I2]"
    FLEXIBLE::exclusion_mechanism
  LANGUAGE_SUPPORT:
    IMMUTABLE::"universal concepts [OM-I4]"
    FLEXIBLE::priority_order_rollout
§4::SCOPE_BOUNDARIES
  IS::[
    dependency_graph_analysis_file_relationships,
    anchor_pattern_inversion_enforcement_Spec_to_Code,
    staleness_detection_algorithmic_binary,
    AST_based_relationship_extraction_imports_plus_references,
    build_isolation_verification_governance_excluded
  ]
  IS_NOT::[
    code_generation_implementation_domain,
    context_synthesis_System_Steward_responsibility,
    file_watching_Living_Artifacts_responsibility,
    documentation_authoring_doc_tools_consume_output,
    IDE_integration_IDE_plugins_are_consumers,
    governance_rule_definition_North_Stars_define_Orchestra_enforces
  ]
§5::DECISION_GATES
  GATES::[D1_DONE→B0_PENDING→B1_PENDING→B2_PENDING→B3_PENDING]
§6::DEPENDENCY_PATTERN
  ANCHOR_INVERSION:
    DIRECTION::"Spec imports Code ⇌ Code annotates Spec"
    VALIDATION::"CI fails if src/ imports anchors/"
    RATIONALE::"active imports → verifiable ⊕ no rot"
  STALENESS_ALGORITHM:
    FORMULA::"LastCommit(Spec) before LastCommit(Impl) → STALE"
    BINARY::"no subjective health scores"
    SCRIPT::"staleness check uses git logs"
  BUILD_ISOLATION:
    EXCLUDED::[anchors_dir,specs_dir]
    ARROW::"Governance → Production [one-way only]"
    VALIDATION::"build config explicitly excludes"
  AST_TOOLING:
    REQUIRED::"dependency-cruiser ∨ ast_module ∨ equivalent"
    PROHIBITED::"regex text search for deps"
    RATIONALE::"reliability ≻ simplicity"
§7::DEPENDENCIES
  BLOCKING::[]
  RELATED_ADRS::[ADR-0046]
§8::AGENT_ESCALATION
  requirements_steward::[
    immutable_violation,
    scope_question,
    NS_amendment
  ]
  technical_architect::[architecture_decisions,AST_tooling_selection]
  implementation_lead::[assumption_validation,build_execution]
§9::TRIGGER_PATTERNS
  LOAD_FULL_NORTH_STAR_IF:
    IMMUTABLE_CONFLICT::"violates OM-I1-I5"
    SPEC_TO_CODE_PATTERN::"anchor inversion question"
    STALENESS_ALGORITHM::"freshness logic"
    AST_TOOLING::"parser selection"
§10::PROTECTION_CLAUSE
  TRIGGER::"work contradicts North Star"
  ACTION::[STOP→CITE_OM_I→ESCALATE_REQUIREMENTS_STEWARD]
  THE_OATH::"5 Immutables OM-I1-I5 bind Orchestra Map. Contradiction → STOP⊕CITE⊕ESCALATE."
===END===
