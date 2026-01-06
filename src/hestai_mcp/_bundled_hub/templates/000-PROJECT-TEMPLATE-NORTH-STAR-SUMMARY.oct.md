===PROJECT_NAME_NORTH_STAR_SUMMARY===

META:
  TYPE::NORTH_STAR_SUMMARY
  ID::project-name-north-star-summary
  VERSION::"1.0-OCTAVE-SUMMARY"
  STATUS::DRAFT
  PURPOSE::"Operational decision-logic for [PROJECT_NAME]"
  INHERITS::".hestai-sys/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md"

## IMMUTABLES (5-9 Total)

I1::[IMMUTABLE_NAME]::[
  PRINCIPLE::[one_sentence_principle],
  WHY::[technical_or_business_justification],
  STATUS::[PENDING|PROVEN]
]

I2::[IMMUTABLE_NAME]::[
  PRINCIPLE::[one_sentence_principle],
  WHY::[technical_or_business_justification],
  STATUS::[PENDING|PROVEN]
]

// Add I3..I9 here

## CRITICAL ASSUMPTIONS (Top Risks)

A1::[ASSUMPTION_NAME][CONFIDENCE%]→[STATUS][owner@phase]
A2::[ASSUMPTION_NAME][CONFIDENCE%]→[STATUS][owner@phase]

## CONSTRAINED VARIABLES (Top 3)

[VARIABLE_NAME]::[
  IMMUTABLE::[hard_boundary],
  FLEXIBLE::[range_of_options],
  NEGOTIABLE::[open_for_discussion]
]

## SCOPE_BOUNDARIES

IS::[
  ✅::[core_feature_1],
  ✅::[core_feature_2]
]

IS_NOT::[
  ❌::[explicit_exclusion_1],
  ❌::[explicit_exclusion_2]
]

## DECISION_GATES

GATES::D0→D1→D2→D3→B0→B1→B2→B3→B4→B5

## AGENT_ESCALATION

requirements-steward::[immutable_violation | scope_question]
technical-architect::[architecture_decision]
implementation-lead::[build_execution]

## TRIGGER_PATTERNS

LOAD_FULL_NORTH_STAR_IF::[
  "violates I#" :: immutable_conflict_detected,
  "scope boundary" :: is_this_in_scope_question,
  "assumption A#" :: validation_evidence_required
]

## PROTECTION_CLAUSE

IF::agent_detects_work_contradicting_North_Star,
THEN::[
  STOP::current_work_immediately,
  CITE::specific_requirement_violated[I#],
  ESCALATE::to_project_lead
]

===END===
