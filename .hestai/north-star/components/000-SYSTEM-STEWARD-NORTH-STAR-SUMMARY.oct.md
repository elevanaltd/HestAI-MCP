===SYSTEM_STEWARD_NORTH_STAR_SUMMARY===
META:
  TYPE::NORTH_STAR_SUMMARY
  VERSION::"2.0-UPOG"
  STATUS::ACTIVE
  NAMESPACE::PROD
  PURPOSE::"Operational decision-logic for System Steward subsystem"
  FULL_DOC::".hestai/workflow/components/000-SYSTEM-STEWARD-NORTH-STAR.md"
  INHERITS::[System_NS,Product_NS]
  REVIEWED_BY::requirements-steward
  REVIEW_DATE::"2025-12-28"
  ASSUMPTIONS_COUNT::6
  ASSUMPTIONS_NOTE::meets_PROPHETIC_VIGILANCE
  CONTRACT::HOLOGRAPHIC<parse_only_governance>
  CANONICAL::".hestai/north-star/components/000-SYSTEM-STEWARD-NORTH-STAR-SUMMARY.oct.md"
  SOURCE::".hestai/north-star/components/000-SYSTEM-STEWARD-NORTH-STAR-SUMMARY.oct.md"
§1::IMMUTABLES
  COUNT::6
  SS_I1<DUAL_CONTROL_PLANE_SEPARATION>:
    PRINCIPLE::"AI orchestration and OCTAVE validation are separate control planes"
    WHY::"deterministic document ops cannot depend on probabilistic AI"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  SS_I2<ASYNC_FIRST_ARCHITECTURE>:
    PRINCIPLE::"all provider calls and MCP invocations must be async"
    WHY::"blocking degrades entire MCP server event loop"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  SS_I3<MCP_SERVER_CHAINING>:
    PRINCIPLE::"HestAI-MCP acts as both server and client with namespaced tools"
    WHY::"enables composition — OCTAVE plus Memory plus Git plus Repomix"
    STATUS::PENDING
    OWNER::technical-architect
    GATE::B1
  SS_I4<SINGLE_WRITER_PRESERVATION>:
    PRINCIPLE::"only System Steward MCP tools write to .hestai/"
    WHY::"prevents governance drift, ensures validated atomic mutations"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  SS_I5<INTELLIGENCE_IN_PROMPTS_AND_MANIFESTS>:
    PRINCIPLE::"AI reasoning in versioned prompts and manifests, not opaque runtime"
    WHY::"codified intelligence is auditable, testable, human controllable"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  SS_I6<GRACEFUL_DEGRADATION>:
    PRINCIPLE::"if AI fails, fall back to deterministic behavior"
    WHY::"reliability critical for autonomous systems — see Product I2"
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
§2::CRITICAL_ASSUMPTIONS
  COUNT::6
  SS_A1<AI_CONTEXT_SELECTION>:
    CONFIDENCE::"80%"
    RISK::High
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  SS_A2<OCTAVE_MCP_ASYNC>:
    CONFIDENCE::"90%"
    RISK::High
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B1
  SS_A3<MANIFEST_FILTERING>:
    CONFIDENCE::"75%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
  SS_A4<PROVIDER_FALLBACK_CHAIN>:
    CONFIDENCE::"85%"
    RISK::High
    STATUS::PENDING
    OWNER::technical-architect
    GATE::B1
  SS_A5<MCP_CHAINING_MANAGEABLE>:
    CONFIDENCE::"75%"
    RISK::High
    STATUS::PENDING
    OWNER::technical-architect
    GATE::B1
  SS_A6<MANIFEST_SCHEMA_COVERAGE>:
    CONFIDENCE::"70%"
    RISK::Medium
    STATUS::PENDING
    OWNER::implementation-lead
    GATE::B2
§3::CONSTRAINED_VARIABLES
  AI_PROVIDER:
    IMMUTABLE::"must use async — see SS-I2"
    FLEXIBLE::"OpenRouter or OpenAI or Anthropic or local"
  CONTROL_PLANES:
    IMMUTABLE::"separate — see SS-I1"
    FLEXIBLE::which_tools_in_each
  MANIFEST_SCHEMA:
    IMMUTABLE::"must exist — see SS-I5"
    FLEXIBLE::schema_evolution
  UPSTREAM_MCP:
    IMMUTABLE::"namespaced — see SS-I3"
    FLEXIBLE::which_servers
  CONTEXT_SELECTION:
    IMMUTABLE::AI_preferred
    FLEXIBLE::deterministic_fallback_acceptable
§4::SCOPE_BOUNDARIES
  IS::[
    AI_powered_context_orchestration,
    MCP_tool_execution_and_handling,
    OCTAVE_validation_routing,
    context_selection_and_synthesis,
    provider_fallback_management
  ]
  IS_NOT::[
    direct_file_writes_octave_create_responsibility,
    identity_validation_odyssean_anchor_responsibility,
    session_management_clock_in_clock_out_responsibility,
    persistent_memory_Basic_Memory_MCP,
    git_operations_Git_MCP,
    codebase_packaging_Repomix_MCP
  ]
§5::DECISION_GATES
  GATES::[D1_DONE→B0_PENDING→B1_PENDING→B2_PENDING→B3_PENDING]
§6::ARCHITECTURE_SUMMARY
  LIVING_LENS_METAPHOR:
    ORCHESTRA_MAP::"BRAIN — relevance graph"
    REPOMIX::"RETINA — code capture"
    OCTAVE::"OPTIC_NERVE — validation plus compression"
    AI_CLIENT::"CORTEX — interpretation"
  DUAL_CONTROL_PLANE:
    AGENTIC::"HestAI_MCP — clock_in plus clock_out plus context_update plus document_submit"
    DOCUMENT::"OCTAVE_MCP — octave_ingest plus octave_create plus octave_amend plus octave_eject"
  MVP_SEQUENCE::[Query_Orchestra_Map→Invoke_Repomix_MCP→Call_AIClient→Validate_octave_ingest→Write_octave_create]
§7::CHILD_COMPONENTS
  TOOLS:
    clock_in::"session registration plus context synthesis — see 000-CLOCK-IN-NORTH-STAR.md"
    clock_out::"session archival plus transcript compression — TBD"
    odyssean_anchor::"identity validation plus binding ceremony — see 000-ODYSSEAN-ANCHOR-NORTH-STAR.md"
    context_update::"mid-session context mutation — TBD"
    document_submit::"document routing plus placement — TBD"
§8::DEPENDENCIES
  BLOCKING::[]
  RELATED_ISSUES::[
    "#56",
    "#87",
    "#96",
    "#102"
  ]
  RELATED_ADRS::[
    ADR-0033,
    ADR-0035,
    ADR-0036,
    ADR-0046
  ]
§9::AGENT_ESCALATION
  requirements_steward::[
    immutable_violation,
    scope_question,
    NS_amendment
  ]
  technical_architect::[architecture_decisions,MCP_chaining_design]
  implementation_lead::[assumption_validation,build_execution]
§10::TRIGGER_PATTERNS
  LOAD_FULL_NORTH_STAR_IF:
    IMMUTABLE_CONFLICT::"violates SS-I1-I6"
    CONTROL_PLANE_DECISION::"architecture question"
    MCP_CHAINING_DESIGN::"integration pattern"
    AI_FALLBACK_POLICY::"degradation strategy"
§11::PROTECTION_CLAUSE
  TRIGGER::"work contradicts North Star"
  ACTION::[STOP→CITE_SS_I→ESCALATE_REQUIREMENTS_STEWARD]
  THE_OATH::"6 Immutables SS-I1-I6 bind System Steward implementation. Contradiction requires STOP, CITE, ESCALATE."
===END===
