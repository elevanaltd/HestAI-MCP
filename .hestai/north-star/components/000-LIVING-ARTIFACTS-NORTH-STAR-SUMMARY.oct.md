===LIVING_ARTIFACTS_NORTH_STAR_SUMMARY===
META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"2.0-UPOG"
  STATUS::ACTIVE
  NAMESPACE::PROD
  PURPOSE::"Operational decision-logic for Living Artifacts pattern"
  FULL_DOC::".hestai/workflow/components/000-LIVING-ARTIFACTS-NORTH-STAR.md"
  INHERITS::[System_NS,Product_NS]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS_COUNT::6
  ASSUMPTIONS_NOTE::meets_PROPHETIC_VIGILANCE
  CONTRACT::HOLOGRAPHIC<parse_only_governance>
  CANONICAL::".hestai/north-star/components/000-LIVING-ARTIFACTS-NORTH-STAR-SUMMARY.oct.md"
  SOURCE::".hestai/north-star/components/000-LIVING-ARTIFACTS-NORTH-STAR-SUMMARY.oct.md"
§1::IMMUTABLES
  COUNT::5
  LA_I1<SPLIT_ARTIFACT_AUTHORITY>:
    PRINCIPLE::"strict separation between Audit Trail and Operational State"
    WHY::"log and state have distinct update cycles and truth sources"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  LA_I2<QUERY_DRIVEN_FRESHNESS>:
    PRINCIPLE::"operational state generated at runtime, not from stale files"
    WHY::"stored state rots — generated state is environmental truth"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  LA_I3<SINGLE_BRANCH_CI_WRITES>:
    PRINCIPLE::"CI processes ONLY write to branch they run on"
    WHY::"cross-branch writes introduce race conditions and merge conflicts"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  LA_I4<BLOCKING_STALENESS>:
    PRINCIPLE::"stale context artifacts must block or flag AT_RISK"
    WHY::"bad data worse than no data — see Product I4"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  LA_I5<PERSISTENT_AUDIT_TRACE>:
    PRINCIPLE::"every significant change leaves permanent trace in Audit Trail"
    WHY::"automated state is ephemeral — need permanent evolution history"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
§2::CRITICAL_ASSUMPTIONS
  COUNT::6
  LA_A1<RUNTIME_GENERATION_FAST>:
    CONFIDENCE::"85%"
    RISK::High
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  LA_A2<CHANGELOG_FORMAT_PARSEABLE>:
    CONFIDENCE::"80%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  LA_A3<GIT_LOGS_SUFFICIENT>:
    CONFIDENCE::"70%"
    RISK::High
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  LA_A4<CHANGELOG_MERGE_SAFE>:
    CONFIDENCE::"80%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  LA_A5<STALENESS_THRESHOLD_APPROPRIATE>:
    CONFIDENCE::"75%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  LA_A6<GIT_LOGS_METADATA_SUFFICIENT>:
    CONFIDENCE::"70%"
    RISK::High
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
§3::CONSTRAINED_VARIABLES
  STATE_SOURCE:
    IMMUTABLE::"environment query — see LA-I2"
    FLEXIBLE::specific_queries_run
  AUDIT_LOCATION:
    IMMUTABLE::"in-repo file — see LA-I5"
    FLEXIBLE::file_name_plus_path
  STALENESS_THRESHOLD:
    IMMUTABLE::"must exist — see LA-I4"
    FLEXIBLE::"duration — 24h or 12h"
§4::SCOPE_BOUNDARIES
  IS::[
    audit_trail_maintenance_CHANGELOG,
    operational_state_generation_JIT_current_state,
    query_driven_freshness_runtime_generation,
    staleness_detection_and_blocking_precommit_hooks,
    CI_integration_automated_CHANGELOG_entries
  ]
  IS_NOT::[
    context_file_writing_OCTAVE_MCP_responsibility,
    session_management_clock_in_clock_out_responsibility,
    identity_validation_odyssean_anchor_responsibility,
    manual_documentation_human_activity,
    schema_enforcement_OCTAVE_parser_responsibility,
    context_selection_System_Steward_responsibility
  ]
§5::DECISION_GATES
  GATES::[D1_DONE→B0_PENDING→B1_PENDING→B2_PENDING→B3_PENDING]
§6::ARTIFACT_PATTERN
  SPLIT_ARTIFACT:
    AUDIT_TRAIL::"CHANGELOG.md — immutable history"
    OPERATIONAL_STATE::"current_state.oct — JIT snapshot"
  FRESHNESS_RULES:
    clock_in::"executes generation logic — git query plus test count"
    staleness::"threshold based — configurable"
    blocking::"pre-commit hooks or tool guards"
  CI_PATTERN:
    WRITES_TO::"HEAD — current branch only"
    NEVER::"cross-branch writes — no orphan magic"
    APPENDS::"CHANGELOG.md on merge"
§7::DEPENDENCIES
  BLOCKING::[]
  RELATED_ISSUES::["#35"]
  RELATED_ADRS::[ADR-0035]
§8::AGENT_ESCALATION
  requirements_steward::[
    immutable_violation,
    scope_question,
    NS_amendment
  ]
  technical_architect::[architecture_decisions,CI_integration_design]
  implementation_lead::[assumption_validation,build_execution]
§9::TRIGGER_PATTERNS
  LOAD_FULL_NORTH_STAR_IF:
    IMMUTABLE_CONFLICT::"violates LA-I1-I5"
    AUDIT_VS_STATE::"split artifact question"
    STALENESS_POLICY::"threshold decision"
    CI_WRITE_PATTERN::"branch strategy"
§10::PROTECTION_CLAUSE
  TRIGGER::"work contradicts North Star"
  ACTION::[STOP→CITE_LA_I→ESCALATE_REQUIREMENTS_STEWARD]
  THE_OATH::"5 Immutables LA-I1-I5 bind Living Artifacts implementation. Contradiction requires STOP, CITE, ESCALATE."
===END===
