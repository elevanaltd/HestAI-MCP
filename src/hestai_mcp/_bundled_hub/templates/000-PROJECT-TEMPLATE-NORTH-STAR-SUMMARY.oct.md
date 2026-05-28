===PROJECT_NAME_NORTH_STAR_SUMMARY===
META:
  TYPE::NORTH_STAR_SUMMARY
  ID::project-name-north-star-summary
  VERSION::"2.0-UPOG"
  STATUS::DRAFT
  NAMESPACE::PROD
  PURPOSE::"Operational decision-logic for [PROJECT_NAME]"
  INHERITS::".hestai-sys/standards/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md"
  CONTRACT::HOLOGRAPHIC<parse_only_governance>
  CANONICAL::".hestai-sys/templates/000-PROJECT-TEMPLATE-NORTH-STAR-SUMMARY.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/templates/000-PROJECT-TEMPLATE-NORTH-STAR-SUMMARY.oct.md"
// UPOG template — see octave-literacy §8::UNIVERSAL_GOVERNANCE_GRAMMAR.
// Replace [BRACKETED] placeholders. Each immutable is its own block: I#<NAME>: + indented children.
// Reasoning values (PRINCIPLE, WHY) use telegraphic operator form per §4::R3a (→ ⊕ ⇌ ∨).
// On save: octave_validate STRICT MUST return warnings:[], errors:[], repairs:[].
§1::IMMUTABLES
  COUNT::5
  I1<IMMUTABLE_NAME_1>:
    PRINCIPLE::"[one-sentence principle — telegraphic, operators carry connectives]"
    WHY::"[technical ∨ business justification]"
    STATUS::PENDING
    OWNER::[role]
    GATE::[phase]
  I2<IMMUTABLE_NAME_2>:
    PRINCIPLE::"[one-sentence principle]"
    WHY::"[justification]"
    STATUS::PENDING
    OWNER::[role]
    GATE::[phase]
  // Add I3..I9 as own blocks (5-9 immutables total). PROVEN status carries EVIDENCE:: instead of GATE::.
§2::CRITICAL_ASSUMPTIONS
  COUNT::2
  A1<ASSUMPTION_NAME_1>:
    CONFIDENCE::"[NN%]"
    RISK::[High∨Medium∨Low∨Critical]
    STATUS::PENDING
    OWNER::[role]
    GATE::[phase]
  A2<ASSUMPTION_NAME_2>:
    CONFIDENCE::"[NN%]"
    RISK::[High∨Medium∨Low∨Critical]
    STATUS::PENDING
    OWNER::[role]
    GATE::[phase]
§3::CONSTRAINED_VARIABLES
  VARIABLE_NAME_1:
    IMMUTABLE::"[hard boundary]"
    FLEXIBLE::"[range of options]"
    NEGOTIABLE::"[open for discussion]"
§4::SCOPE_BOUNDARIES
  IS::[core_feature_1,core_feature_2]
  IS_NOT::[explicit_exclusion_1,explicit_exclusion_2]
§5::DECISION_GATES
  GATES::[D0→D1→D2→D3→B0→B1→B2→B3→B4→B5]
§6::AGENT_ESCALATION
  requirements_steward::[immutable_violation,scope_question]
  technical_architect::[architecture_decision]
  implementation_lead::[build_execution]
§7::TRIGGER_PATTERNS
  LOAD_FULL_NORTH_STAR_IF:
    IMMUTABLE_CONFLICT::"violates I#"
    SCOPE_QUESTION::"scope boundary"
    ASSUMPTION_VALIDATION::"assumption A#"
§8::PROTECTION_CLAUSE
  TRIGGER::"agent detects work contradicting North Star"
  ACTION::[STOP_CURRENT_WORK→CITE_VIOLATED_IMMUTABLE→ESCALATE_TO_PROJECT_LEAD]
===END===
