===NAMESPACE_MIGRATION_GUIDE===
META:
  TYPE::MIGRATION_GUIDE
  VERSION::"2.0"
  EFFECTIVE_DATE::"2026-02-16"
  GRACE_PERIOD::"until_2026-08-16"
  AUTHORITY::"Constitution §3.5 (Relativity Protocol)"
  COMPRESSION_TIER::CONSERVATIVE
  LOSS_PROFILE::"Preserved decision logic and procedures, compressed verbose examples"

§1::EXECUTIVE_SUMMARY
  PROBLEM::"Two North Stars collide on I1-I6 namespace"
  SOLUTION::"Namespace prefixing with file-level declaration (Relativity Governance Protocol)"
  NAMESPACES::[
    SYS::"System methodology (HOW to build) - I1::TDD, I2::Phase_Gated, I3::Human_Primacy, I4::Artifact_Persistence, I5::Quality_Verification, I6::Explicit_Accountability",
    PROD::"Product requirements (WHAT to build) - I1::Cognitive_Continuity, I2::Structural_Integrity, I3::Dual_Layer_Authority, I4::Freshness_Verification, I5::Odyssean_Identity, I6::Universal_Scope"
  ]

§2::CORE_PRINCIPLES
  DECLARATION::"Files declare namespace via META::NAMESPACE::[SYS|PROD] or YAML namespace: field"
  BARE_RESOLUTION::"Bare I# refs resolve to declared namespace"
  CROSS_NAMESPACE::"Cross-namespace refs MUST use prefix (SYS::I5, PROD::I1)"
  NO_DECLARATION::"Files without namespace declaration MUST qualify all refs"
  TRACEABILITY::"TRACES_TO shows how PROD immutables derive from SYS foundation"

§3::DECLARATION_PATTERNS

  YAML_FRONTMATTER::[
    BEFORE::"---\ntype: WORKFLOW\nversion: 1.0\n---",
    AFTER::"---\ntype: WORKFLOW\nversion: 1.0\nnamespace: SYS\n---"
  ]

  OCTAVE_META::[
    BEFORE::"META:\n  TYPE::WORKFLOW\n  VERSION::\"1.0\"",
    AFTER::"META:\n  TYPE::WORKFLOW\n  VERSION::\"1.0\"\n  NAMESPACE::SYS"
  ]

§4::QUALIFICATION_RULES

  RULE_1_SAME_NAMESPACE::[
    CONTEXT::"Within NAMESPACE::SYS document",
    CORRECT::"This violates I2" [bare_I2_resolves_to_SYS::I2],
    INCORRECT::"This violates SYS::I2" [redundant_prefix_within_namespace]
  ]

  RULE_2_CROSS_NAMESPACE::[
    CONTEXT::"Within NAMESPACE::SYS document referencing Product",
    CORRECT::"This supports PROD::I1 (cognitive continuity)" [prefix_required],
    INCORRECT::"This supports I1 (cognitive continuity)" [ambiguous_bare_ref]
  ]

  RULE_3_NO_DECLARATION::[
    CONTEXT::"Document without NAMESPACE declaration",
    CORRECT::"Satisfies SYS::I2 and PROD::I5" [all_refs_qualified],
    INCORRECT::"Satisfies I2 and I5" [bare_refs_without_namespace]
  ]

  RULE_4_TRACES_TO::[
    CONTEXT::"PROD namespace documents only",
    REQUIRED::"Each I# definition MUST include TRACES_TO:[list_of_SYS::I#_dependencies]",
    EXAMPLE::"I1::PERSISTENT_COGNITIVE_CONTINUITY::[..., TRACES_TO::[SYS::I4,SYS::I6], DERIVATION::\"Extends artifact_persistence[SYS::I4] to cognitive_state\"]"
  ]

§5::VALIDATION_RULES

  V1_DECLARATION_CONSISTENCY::[
    IF::"document contains NAMESPACE::X declaration",
    THEN::"all bare I# refs resolve to X::I#",
    ELSE::"all I# refs MUST be qualified"
  ]

  V2_CROSS_NAMESPACE_QUALIFICATION::[
    IF::"document namespace is X AND reference is to namespace Y (X ≠ Y)",
    THEN::"reference MUST use Y:: prefix"
  ]

  V3_TRACES_TO_COMPLETENESS::[
    IF::"document NAMESPACE::PROD",
    THEN::"each I# definition MUST include TRACES_TO:[list_of_SYS::I#]"
  ]

  V4_NAMESPACE_VALUES::[
    VALID::[SYS, PROD],
    INVALID::[SYSTEM, PRODUCT, "SYS|PROD", undefined]
  ]

§6::MIGRATION_TIMELINE

  PHASE_1_GRACE::[
    START::"2026-02-16",
    END::"2026-08-16",
    BEHAVIOR::"Bare refs permitted with warnings. Validators attempt context inference. Cross-namespace refs without prefix generate warnings.",
    ENFORCEMENT::WARN_ONLY
  ]

  PHASE_2_TRANSITION::[
    START::"2026-08-16",
    END::"2026-08-30",
    BEHAVIOR::"New documents MUST comply. Bare refs in undeclared namespace = ERROR. Cross-namespace refs without prefix = ERROR.",
    ENFORCEMENT::ERROR_NEW_DOCS
  ]

  PHASE_3_FULL::[
    START::"2026-08-30",
    BEHAVIOR::"All documents MUST comply. Missing TRACES_TO in PROD namespace = ERROR.",
    ENFORCEMENT::ERROR_ALL_DOCS
  ]

§7::COMMON_PATTERNS

  AGENT_IDENTITIES::[
    DECISION::"Declare NAMESPACE::PROD [agents reference operational immutables]",
    EXAMPLE::"===AGENT===\nMETA:\n  TYPE::AGENT\n  NAMESPACE::PROD\nCONSTRAINTS:\n  MUST_SATISFY::[I5,I2]  // PROD::I5, PROD::I2\n  FOUNDATION::SYS::I1    // Explicit SYS ref"
  ]

  WORKFLOW_DOCS::[
    DECISION::"Declare NAMESPACE::SYS [workflows enforce System methodology]",
    EXAMPLE::"===WORKFLOW===\nMETA:\n  NAMESPACE::SYS\nPHASES:\n  DESIGN::satisfies_I2[phase_gates]  // SYS::I2\n  PRODUCT_CONTEXT::requires_PROD::I4"
  ]

  MIXED_CONTEXT::[
    DECISION::"NO namespace declaration, qualify all refs [equal System+Product usage]",
    EXAMPLE::"# Integration Guide\n\nFollow SYS::I1 (TDD) for code.\nEnsure PROD::I5 (identity binding) before agent work.\nSatisfy SYS::I2 (phase gates) and PROD::I2 (structural integrity)."
  ]

  ADRS_DECISIONS::[
    DECISION::"Declare primary namespace, qualify cross-refs",
    EXAMPLE::"---\nnamespace: SYS\n---\n# ADR-0047: Test Structure\n\nEnforces I1 (TDD) and I5 (quality verification).\nSupports PROD::I5 (Odyssean identity) via test infrastructure."
  ]

§8::MIGRATION_PROCEDURE

  STEP_1::"Identify document's primary namespace (SYS for governance/workflows, PROD for product/agents, NONE for mixed)"
  STEP_2::"Add NAMESPACE declaration to META block or YAML frontmatter"
  STEP_3::"Audit all I# references: grep -E 'I[1-6]' document.md"
  STEP_4::"Apply qualification rules: same-namespace refs stay bare, cross-namespace refs get prefix"
  STEP_5::"For PROD docs: add TRACES_TO:[SYS::I#_list] to each I# definition"
  STEP_6::"Run validation: python scripts/audit_namespace_refs.py document.md"
  STEP_7::"Verify checklist: declaration present, bare refs match namespace, cross-refs prefixed, TRACES_TO complete"

§9::VALIDATION_EXAMPLES

  CORRECT_SYS_USAGE::[
    CODE::"===CHECKLIST===\nMETA:\n  NAMESPACE::SYS\nVERIFY_TDD::I1_compliance      // SYS::I1\nVERIFY_GATES::I2_evidence      // SYS::I2\nSUPPORT_PRODUCT::PROD::I1_ctx  // Explicit PROD",
    STATUS::PASS
  ]

  INCORRECT_MIXED_REFS::[
    CODE::"===CHECKLIST===\nMETA:\n  NAMESPACE::SYS\nVERIFY_TDD::I1_compliance      // SYS::I1 OK\nVERIFY_IDENTITY::I5_binding    // ERROR: I5 resolves to SYS::I5 but context implies PROD::I5",
    STATUS::FAIL,
    FIX::"VERIFY_IDENTITY::PROD::I5_binding"
  ]

  MISSING_DECLARATION::[
    CODE::"# Workflow\nAgents must satisfy I5 before work.",
    STATUS::FAIL,
    FIX_OPTION_1::"Add namespace: PROD to frontmatter",
    FIX_OPTION_2::"Change to 'Agents must satisfy PROD::I5 before work.'"
  ]

§10::VALIDATION_CHECKLIST

  PRE_SUBMISSION::[
    "Document has NAMESPACE declaration in META/frontmatter (or intentionally omitted)",
    "All bare I# refs are to declared namespace",
    "All cross-namespace refs use prefix (SYS:: or PROD::)",
    "If NAMESPACE::PROD, all I# definitions include TRACES_TO",
    "TRACES_TO values reference valid SYS::I# immutables",
    "Validation script passes without errors",
    "No ambiguous I# refs in prose/comments"
  ]

§11::COMPLETE_MIGRATION_EXAMPLE

  BEFORE::[
    CODE::"# Agent Binding Workflow\n\nAll agents must satisfy I5 before performing work.\nThis ensures I2 compliance and supports I1.",
    STATUS::"Ambiguous - no namespace context"
  ]

  AFTER_PROD_NAMESPACE::[
    CODE::"---\nnamespace: PROD\n---\n# Agent Binding Workflow\n\nAll agents must satisfy I5 (Odyssean Identity Binding) before work.\nThis ensures I2 (Structural Integrity) and supports I1 (Cognitive Continuity).\n\nBinding ceremony enforces SYS::I6 (Explicit Accountability) by establishing traceable identity.",
    STATUS::"Clear - PROD context declared, cross-ref to SYS::I6 prefixed"
  ]

  AFTER_NO_NAMESPACE::[
    CODE::"# Agent Binding Workflow\n\nAll agents must satisfy PROD::I5 (Odyssean Identity Binding) before work.\nThis ensures PROD::I2 (Structural Integrity) and supports PROD::I1 (Cognitive Continuity).\n\nBinding ceremony enforces SYS::I6 (Explicit Accountability) by establishing traceable identity.",
    STATUS::"Clear - all refs explicitly qualified"
  ]

§12::SUPPORT

  NAMESPACE_AMBIGUITY::"Escalate to requirements-steward"
  MIGRATION_BLOCKERS::"Create issue with label 'namespace-migration'"
  VALIDATION_FAILURES::"Check §10::VALIDATION_CHECKLIST"
  TOOL_ISSUES::"Report to implementation-lead"

§13::AUTHORITY

  DOCUMENT_AUTHORITY::"Constitution §3.5 (Relativity Protocol)"
  APPROVAL::"Shaun Buswell (Human Primacy Authority)"
  EFFECTIVE::"2026-02-16"
  NEXT_REVIEW::"2026-08-30 (post-grace period)"

===END===
