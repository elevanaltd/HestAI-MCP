===HESTAI_SYSTEM_OVERVIEW===
META:
  TYPE::SYSTEM_OVERVIEW
  VERSION::"2.0-OCTAVE-UNIFIED"
  STATUS::ACTIVE
  PURPOSE::"Comprehensive reference for HestAI design-and-build system: phases, governance, quality gates, error handling, coordination patterns"
  DOMAIN::governance
  OWNERS::["requirements-steward"]
  CREATED::"2026-01-13"
  UPDATED::"2026-01-13"
  CANONICAL::".hestai-sys/governance/HESTAI-SYSTEM-REFERENCE.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/governance/HESTAI-SYSTEM-REFERENCE.oct.md"
  FORMAT::octave
  IMMUTABLES::6
  PHASES::10
D0::"D1→D2→D3→B0→B1→B2→B3→B4→B5"
FOUNDATION_LAYERS::4
§1::SYSTEM_DEFINITION
HESTAI_ESSENCE::[[PRIMARY_PURPOSE::"Design-and-build system for AI-assisted software development with installed governance"],[PROBLEM_SOLVED::"Cognitive continuity crisis—AI agents have no persistent memory yet complex software requires months of context, decisions, and accumulated understanding"],[CORE_INSIGHT::"Governance is the mechanism that makes design-and-build reliable by preventing drift into vibe coding through constitutional binding, phase gates, and quality enforcement"],[OPERATOR::"Single developer with one laptop, running multiple terminals, orchestrating multi-model AI governance"],[NOT_A::[commercial_product,multi_team_coordination_system,model_specific_tool,library_of_agents,bureaucratic_overhead,governance_first_system,replacement_for_human_judgment]]]
MOAT_DEFINITION::[[TECHNICAL_STRENGTH::"Integrated governance as mechanism for reliable building: TDD+phase_gates+RACI+constitutional_binding+OCTAVE semantics together creating coherence that no subset achieves"],[SWITCHING_COST::"Systems harder to replace than tools"],[SUCCESS_CRITERION::"Does the built artifact work properly with all audit trails and information needed for production-grade system?"]]
§2::FOUR_LAYER_FOUNDATION
FOUNDATION_ARCHITECTURE::[[LAYER_0_SEMANTICS::["OCTAVE-MCP[validation_precedes_generation]","prevents invalid documents at generation time","54-68 percent token reduction via semantic compression","Generative Holographic Contracts with v6 grammar compilation"]],[LAYER_1_IDENTITY::["odyssean-anchor-mcp[cognitive_proof_ceremony]","enforces agent role fidelity through 3-stage handshake","REQUEST→LOCK[SEA,SHANK,ARM]→COMMIT[FLUKES]","prevents generic drift via situational awareness validation"]],[LAYER_2_DECISIONS::["debate-hall-mcp[dialectical_orchestration]","enables multi-perspective reasoning via Wind→Wall→Door","hash chains make decisions auditable and non-repudiable","enforces hard resource bounds and turn sequencing"]],[LAYER_3_MEMORY::["hestai-mcp[cognitive_continuity_engine]","dual-layer architecture: System[read-only governance]⊕Product[mutable context]","persistent memory across sessions with conflict resolution","tool gating via identity permits from odyssean-anchor"]]]
LAYER_INTEGRATION::[[DATA_FLOW::"User→odyssean-anchor[prove_identity]→hestai-mcp[clock_in]→Load_context[OCTAVE-validated]→debate-hall[if_decision_needed]→OCTAVE_synthesis→hestai-mcp[clock_out_archive]"],[DEPENDENCY_CHAIN::"hestai-mcp[depends_on:octave-mcp,odyssean-anchor-mcp] | debate-hall-mcp[uses:octave-mcp] | all_systems[foundation:OCTAVE-MCP]"],[GOVERNANCE_MODEL::"OCTAVE_defines_contracts→odyssean-anchor_enforces_identity→debate-hall_enforces_decisions→hestai-mcp_persists_memory"]]
§3::THE_SIX_IMMUTABLES
I1::PERSISTENT_COGNITIVE_CONTINUITY
PRINCIPLE::"System must persist context, decisions, learnings across sessions"
WHY::"Prevents costly re-learning and amnesia which is system failure"
MECHANISM::"hestai-mcp[clock_in/clock_out,session_archives,PROJECT-CONTEXT]"
STATUS::ACTIVE
I2::STRUCTURAL_INTEGRITY_PRIORITY
PRINCIPLE::"Correctness and compliance take precedence over velocity"
WHY::"Reliability critical for autonomous systems"
MECHANISM::"Quality gates[BLOCKING:lint+typecheck+tests], phase gates[hard_stops]"
STATUS::ACTIVE
I3::DUAL_LAYER_AUTHORITY
PRINCIPLE::"Strict separation between read-only governance and mutable context"
WHY::"Prevents governance drift and agent rule rewriting"
MECHANISM::".hestai-sys/[system_injected]⊕.hestai/[product_committed]"
STATUS::ACTIVE
I4::FRESHNESS_VERIFICATION
PRINCIPLE::"Context must be verified current before use"
WHY::"Prevents hallucinations from stale data"
MECHANISM::"clock_in[loads_fresh_context], PROJECT-CONTEXT[timestamp_checked]"
STATUS::PENDING
I5::ODYSSEAN_IDENTITY_BINDING
PRINCIPLE::"Agents must undergo structural identity verification to operate"
WHY::"Prevents generic drift and enforces role constraints"
MECHANISM::"odyssean-anchor-mcp[3-stage_handshake_REQUEST→LOCK→COMMIT]"
STATUS::ACTIVE
I6::UNIVERSAL_SCOPE
PRINCIPLE::"System must function on any repository structure"
WHY::"Ensures broad adoption and handles legacy diversity"
MECHANISM::"configurable_paths[HESTAI_PROJECT_ROOT], relative_links[migration_resilient]"
STATUS::PENDING
§4::PHASE_WORKFLOW_D0_TO_B5
PHASE_MYTHOLOGY::[[ARCHETYPAL_BINDING::"Each phase bound to mythological archetype encoding behavior pattern"],[COMPRESSION_RULE::"Phases compress for simple work but cannot be omitted—gate exists, ceremony adapts"],[DOCUMENTATION_TIMELINE::"D-phase→coordination/docs/workflow/[planning], B-phase→dev/reports/[execution]"]]
D0::MNEMOSYNE_GENESIS
D1::APOLLO_ORACLE
D2::ATHENA_INNOVATION
D3::DAEDALUS_CONSTRUCTION
B0::THEMIS_JUDGMENT
B1::HERMES_COORDINATION
B2::HEPHAESTUS_FORGE
B3::HARMONIA_UNIFICATION
B4::IRIS_HANDOFF
B5::PROMETHEUS_EVOLUTION
§5::GOVERNANCE_MODEL_AND_RACI
RACI_FOUNDATION::[[R_RESPONSIBLE::"Agent performs work and owns execution"],[A_ACCOUNTABLE::"Agent with final decision authority and overall accountability"],[C_CONSULTED::"Domain experts provide input before decisions"],[I_INFORMED::"Agents kept informed of outcomes"]]
CORE_ROLES_AND_COGNITIONS::[[APOLLO::[PATHOS,"Possibility explorer","identifies patterns, reveals truth, sees breaking points"]],[ATHENA::[LOGOS,"Structure architect","strategic wisdom, elegant solutions, system synthesis"]],[HERMES::[ETHOS,"Boundary guardian","swift coordination, communication, verification"]],[HEPHAESTUS::[LOGOS,"Master craftsman","infrastructure, tooling, quality creation"]],[THEMIS::[ETHOS,"Critical evaluator","gatekeeping, validation, no-go authority"]],[ZEUS::[LOGOS,"Executive authority","strategic direction, final arbitration, escalation"]],[ARES::[ETHOS,"Security guardian","defense, stress testing, adversarial analysis"]],[ARTEMIS::[ETHOS,"Vigilant observer","monitoring, logging, precision issue targeting"]]]
ESCALATION_AUTHORITY::[[requirements-steward::"I1 violations | scope boundary | North Star amendment"],[technical-architect::"architecture decisions | integration design | B5 vs D1 boundary"],[critical-engineer::"production readiness | GO/NO-GO gates | incident command[CRITICAL]"],[principal-engineer::"long-term viability | strategic patterns | 6-month sustainability[MANDATORY_at_B1]"]]
§6::AGENT_IDENTITY_BINDING_CEREMONY
ODYSSEAN_ANCHOR_PROTOCOL::[[PURPOSE::"Prove agent understands role constraints and current project context before execution"],[STAGES::["REQUEST[nonce_challenge]","LOCK[3-substage_proof:SEA⊕SHANK⊕ARM]","COMMIT[FLUKES_final_proof]"]],[OUTCOME::"Permit[valid_for_session]⊕anchor[full_identity_document_returned_to_agent]"]]
BINDING_EVIDENCE::[[CONSTITUTION_COMPREHENSION::"Agent proves understanding of own role definition, boundaries, methodology"],[CONTEXTUAL_AWARENESS::"Agent proves knowledge of current phase[D0-B5], project focus, immutable constraints"],[SITUATIONAL_CAPABILITY::"Agent proves understanding of available skills and when to delegate"],[FLUKES_PROOF::"Agent acknowledges tensions between CONDUCT and CONTEXT and commits to framework"]]
PERMISSION_GATES::[[PRE_EXECUTION::"All work tools require valid permit before execution"],[PERMIT_SCOPE::"Tied to session_id; agent role; project_context"],[INVALIDATION::"Permit invalidated if context changed without re-binding"]]
§7::CONTEXT_MANAGEMENT_ARCHITECTURE
DUAL_LAYER_PERSISTENCE::[[SYSTEM_LAYER::[[LOCATION::".hestai-sys/[read-only, injected at runtime]"],[CONTENT::[governance_rules,agent_templates,reference_materials,immutable_standards]],[MUTABILITY::"Immutable—updated only via MCP server upgrade"],[VERSIONING::"Aligned with hestai-mcp version"]]],[PRODUCT_LAYER::[[LOCATION::".hestai/[committed, single-writer via MCP]"],[CONTENT::["PROJECT-CONTEXT",sessions,workflow,reports,decisions]],[MUTABILITY::"Mutable only via document_submit/context_update tools"],[VERSIONING::"Tracked in git; conflict resolution via AI merge"]]]]
SESSION_LIFECYCLE::[[CLOCK_IN::"Register session start→load_context_paths→return session_id"],[WORK_PHASE::"Agent operates within session context→tools check_permits→MCP_single-writer prevents conflicts"],[CLOCK_OUT::"Archive session transcript to OCTAVE format→compress via octave-mcp→store in .hestai/sessions/archive/"]]
CONTEXT_OBJECTS::[[PROJECT_CONTEXT::[[STRUCTURE::["STATUS::current_phase_and_progress","IMMUTABLES::[I1-I6_status]","ASSUMPTIONS::[A1-An_validation_state]","PHASE_ARTIFACTS::[living_references]"]],[UPDATE_MECHANISM::"Via context_update tool with conflict_detection"],[TIMESTAMP::"freshness_verified at clock_in"]]],[PROJECT_NORTH_STAR::[[STRUCTURE::["IMMUTABLES::[5-9_core_constraints]","CONSTRAINED_VARIABLES::[flexibility_points]","SCOPE_BOUNDARIES::[IS,IS_NOT]","DECISION_GATES::[phase_progression_rules]"]],[CREATED::D1_phase],[IMMUTABLE::once_approved]]],[OPERATIONAL_WORKFLOW::[[STRUCTURE::"Consolidated D0→B5 phases with RACI, error_handling, coordination_patterns"],[SOURCE::"/Users/shaunbuswell/.claude/protocols/OPERATIONAL-WORKFLOW.md"],[REFERENCE::"Agents consult for phase requirements, responsibilities, deliverables"]]]]
§8::QUALITY_ENFORCEMENT_AND_GATES
TRACED_PROTOCOL::[[T::test_first],[R::"code-review-specialist"],[A::"critical-engineer"],[C::consult_specialists],[E::quality_gates],[D::documented]]
BLOCKING_GATES::[[B1_GATE::"QUALITY_GATES_MANDATORY[npm_lint⊕npm_typecheck⊕npm_test] OR no_code_commits[workspace_not_ready]"],[B2_GATE::"Coverage_80plus⊕tests_passing⊕no_critical_vulnerabilities OR escalate_to_critical-engineer"],[B3_GATE::"Integration_tests_all_interactions⊕E2E_validation⊕performance_benchmarks_achieved OR NO-GO"],[B4_GATE::"Production_infrastructure_tested⊕rollback_validated⊕monitoring_active OR defer_deployment"]]
ANTI_VALIDATION_THEATER::[[EVIDENCE_REQUIRED::["test_execution_output[not_assertions]",code_review_artifacts,coverage_reports,git_commit_references]],[PREVENTION::[hollow_checkmarks_forbidden,tweaked_expectations_forbidden,workarounds_forbidden,assumptions_must_be_stated]]]
§9::COORDINATION_AND_DOCUMENTATION
REPOSITORY_BOUNDARY_PATTERN::[[COORDINATION_REPOSITORY::["planning_docs[D0-D2]","phase_reports[B0-B5]","workflow_artifacts[NORTH-STAR,DESIGN,BLUEPRINT]","ACTIVE-WORK.md[visibility_board]"]],[DEV_REPOSITORY::["source_code⊕tests","docs/architecture/[D3_BLUEPRINT_ORIGINAL⊕AS_BUILT⊕DEVIATIONS]","docs/adr/[ADRs_with_front_matter]","CI_pipelines⊕quality_gates"]]]
DOCUMENT_PLACEMENT_LOGIC::[[BEFORE_CODE_EXISTS::"coordination/workflow-docs/"],[DESCRIBES_IMPLEMENTATION::"dev/docs/"],[GUIDES_IMPLEMENTATION::"dev/docs/"]]
DOCUMENTATION_FIRST_WORKFLOW::[[STEP_1::"Write ADR or spec in dev/docs/"],[STEP_2::"Create PR, merge documentation FIRST"],[STEP_3::"Implementation PR references merged documentation[ADR-NNN]"],[BENEFIT::"Prevents annotation rot and ensures specs are binding contracts"]]
FRONT_MATTER_REQUIREMENTS::[[ARCHITECTURE_DOCS::[applies_to_tag,supersedes,superseded_by,schema_version,phase,status]],[ADRS::[adr_number,title,status,decision_date,implements,deviates_from]]]
§10::ERROR_HANDLING_AND_RESILIENCE
ERROR_TAXONOMY::[[QUICK_FIX_ERRORS::"≤30_minutes[syntax, obvious_cause, single_file, zero_architectural_impact]→error-resolver[HERMES]"],[COMPLEX_ERRORS::"30min_to_4hours[multi-component, investigation_required, performance_impact]→error-architect[coordination]"],[SYSTEM_ERRORS::">4_hours[architectural_changes, multi-team_impact, high_business_risk]→critical-engineer[INCIDENT_COMMAND]"]]
EMERGENCY_PROTOCOL::[[DETECTION::CRITICAL_ERROR_IDENTIFIED],[STOP_WORK::"All development halted"],[INCIDENT_COMMAND::"critical-engineer assumes commander role"],[STABILIZATION::"Specialist team stabilizes before root_cause analysis"],[MITIGATION::"Technical remediation plus strategic post-mortem"]]
POST_MORTEM_PATTERN::[[TACTICAL::["critical-engineer[analyzes_immediate_cause,remediation]","What broke RIGHT NOW?"]],[STRATEGIC::["principal-engineer[identifies_patterns,prevention]","Why will this repeat?"]],[JOINT::"Tactical fixes plus architectural prevention recommendations"]]
USER_UNAVAILABILITY::[[TRIGGER::">24_hours_no_user_response"],[ACTION::[document_state,preserve_work,detailed_commits,set_status,leave_resume_instructions]]]
§11::ASSUMPTION_REGISTRY
CRITICAL_ASSUMPTIONS::[[A1::OCTAVE_READABILITY],"→PENDING",[validation_at_B1],[A2::RAPH_EFFICACY],"→PENDING",[multi_model_testing],[A3::ARCHITECTURAL_COHERENCE],"→VALIDATED",[ADR_system],[A4::PHASE_COMPRESSION],"→PENDING",[edge_case_testing],[A5::SINGLE_DEVELOPER_SCALE],"→PENDING",[load_testing]]
ASSUMPTION_VALIDATION_GATES::[[D1_STAGE::"Assumptions collected and audited for feasibility"],[B0_STAGE::"Assumptions validated against design—any violated→NO-GO"],[B1_STAGE::"Assumptions revisited against implementation context"],[B4_STAGE::"Post-delivery validation of assumption accuracy"]]
§12::CONSTRAINED_VARIABLES
WORKFLOW_LATENCY::[[IMMUTABLE::Integrity_checks_cannot_be_skipped_for_speed],[FLEXIBLE::Startup_latency_up_to_2min_acceptable],[NEGOTIABLE::"Specific_optimization_targets[example:session_loading]"]]
TECHNOLOGY_SUBSTRATE::[[IMMUTABLE::Git_as_coordination_substrate],[FLEXIBLE::MCP_vs_other_agent_protocols],[NEGOTIABLE::"Specific_CLI_implementations[claude_code_vs_other]"]]
STORAGE_MODEL::[[IMMUTABLE::Persistent_memory_guarantee],[FLEXIBLE::Local_first_preferred_not_mandatory],[NEGOTIABLE::"Storage_format[JSONL_vs_OCTAVE_vs_hybrid]"]]
§13::SCOPE_BOUNDARIES
IS::[persistent_memory_system,structural_governance_engine,orchestra_conductor_ambient_awareness,dual_layer_context_protocol,multi_model_orchestration]
IS_NOT::[SaaS_product,grab_bag_tool_library,monorepo_exclusive,AI_model,replacement_for_human_judgment_on_problem_selection,commercial_product,multi_team_coordination_platform]
§14::INTEGRATION_SUMMARY
SYSTEM_STACK::[[LAYER_0::"OCTAVE-MCP[semantics,validation,compression]"],[LAYER_1::"odyssean-anchor-mcp[identity,binding,capabilities]"],[LAYER_2::"debate-hall-mcp[decisions,dialectic,synthesis]"],[LAYER_3::"hestai-mcp[memory,governance,orchestration]"]]
DATA_FLOW_MODEL::[[ENTRY::"Agent→clock_in[identity_binding_via_odyssean-anchor-mcp]"],[CONTEXT_LOAD::"Load fresh context via hestai-mcp[OCTAVE-validated]"],[WORK_PHASE::"Agent executes within D0-B5 phase with permit_gating"],[DECISION_NEEDED::["Initiate debate_hall[Wind→Wall→Door]","Export synthesis as OCTAVE"]],[SESSION_END::"clock_out[compress→archive→persist_to_disk]"]]
§15::QUICK_REFERENCE_FOR_AGENTS
STARTUP::[[/load_ho::"Full orchestration with RAPH activation"],[/load_il::"Direct implementation with governance"],[check_.hestai_sys/::"Read governance files[not_committed_but_available]"],[read_PROJECT_CONTEXT::"Understand current phase and status"]]
DURING_WORK::[[PHASE_BLOCK::"Use OPERATIONAL-WORKFLOW.oct.md for deliverables and RACI"],[QUESTION_SCOPE::"Escalate to requirements-steward if I1-I6 boundary unclear"],[ARCHITECTURAL_DECISION::"Consult technical-architect; may trigger debate_hall"],[ERROR_CLASSIFIED::"Follow ERROR_HANDLING_TAXONOMY for routing"]]
DOCUMENTATION::[[PLANNING::"coordination/workflow-docs/[D0-D2]"],[IMPLEMENTATION::"dev/docs/[D3+] via documentation_submit tool"],[ADRS::"Front_matter_required; numbering must match GitHub_Issue"],[SESSIONS::"Auto-archived by clock_out in OCTAVE format"]]
GATES::[[B0::"critical-engineer[GO/NO-GO]"],[B1::"Quality_gates_MANDATORY[lint+typecheck+test]"],[B2::"Code_review⊕coverage_80plus⊕"],[B3::"Integration_tests⊕E2E_validation⊕security_audit"],[B4::Production_readiness_signoff]]
§16::PROTECTION_CLAUSE
IF_AGENT_DETECTS::work_contradicting_immutables
THEN::[[STOP::current_work_immediately],[CITE::specific_requirement_violated],[ESCALATE::"to_requirements-steward"],[RESOLUTION::CONFORM_OR_FORMAL_AMENDMENT_PROCESS]]
MANDATE::"Any agent detecting misalignment with I1-I6 has authority and obligation to escalate. Do not proceed."
§17::KEY_INSIGHT
HestAI_is_NOT::[tool_library,governance_for_its_own_sake,monolithic_framework]
HestAI_IS::[design_and_build_system_with_installed_governance,moat_created_by_integrated_coherence,four_layer_foundation_providing_reliable_automation,persistent_memory_system_curing_AI_amnesia,TRACED_protocol_with_constitutional_binding]
SUCCESS_CRITERION::["Does the thing that is being built work properly?","With all audit trails and information needed?","For production-grade system delivery?","Built artifact is destination; governance is path"]
===END===
