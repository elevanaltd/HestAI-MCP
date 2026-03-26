===OPERATIONAL_WORKFLOW===
META:
  TYPE::STANDARD
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"Consolidated D0→B5 workflow methodology with RACI+coordination+error handling"
  DOMAIN::workflow
  OWNERS::["system-steward"]
  CREATED::"2026 -01 -08"
  UPDATED::"2026-03-04"
  CANONICAL::".hestai-sys/standards/workflow/OPERATIONAL-WORKFLOW.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/standards/workflow/OPERATIONAL-WORKFLOW.oct.md"
  FORMAT::octave
  ID::"operational-workflow"
RACI_FOUNDATION:
  R_RESPONSIBLE::"Agent performs work+owns execution"
  A_ACCOUNTABLE::"Agent with final decision authority+overall accountability"
  C_CONSULTED::"Domain experts provide input before decisions"
  I_INFORMED::"Agents kept informed of outcomes"
WORKFLOW_MYTHOLOGY:
  PHASE_ARCHETYPES::["D0_IDEATION_SETUP→MNEMOSYNE_GENESIS",[session_establishment],"D1_UNDERSTANDING→APOLLO_ORACLE",["clarification→research→synthesis→validation"],"D2_IDEATION→ATHENA_INNOVATION",["creation→constraint→synthesis"],"D3_ARCHITECTURE→DAEDALUS_CONSTRUCTION",["design→visual→technical→security"],"B0_VALIDATION→THEMIS_JUDGMENT",["critical→requirements→technical→decision"],"B1_PLANNING→HERMES_COORDINATION",["decomposition→workspace→sequencing→validation"],"B2_IMPLEMENTATION→HEPHAESTUS_FORGE",["methodology→lead→test→review→resolve"],"B3_INTEGRATION→HARMONIA_UNIFICATION",["orchestration→testing→security→coherence"],"B4_DELIVERY→IRIS_HANDOFF",["solution→system→workspace→security→final"],"B5_ENHANCEMENT→PROMETHEUS_EVOLUTION",["requirements→architecture→implementation→validation"]]
SCOPE_GATE_CLASSIFICATION:
  ENTRY_REQUIREMENT::"Successful ideation+graduation→formal D1 requires scope classification"
  AUTHORITY::"R[idea-clarifier:initial]→A[critical-engineer:final]→C[requirements-steward:alignment, principal-engineer:long_term_viability_for_COMPLEX+ENTERPRISE]"
  CALIBRATION_CHECKPOINTS::"MANDATORY workflow-scope-calibrator invocation at: D1_start, B0_00, B1_00, B2_00, B3_00, B4_00, ANY >20_task_threshold"
  SCOPE_MATRIX::[[[SIMPLE::["<100_users",single_component,low_risk,minimal_integrations]]],"→",[consolidated_docs,bullet_specs,informal_reviews,essential_testing],[[STANDARD::["100-10K_users","2-5_components",moderate_impact,standard_integrations]]],"→",[standard_doc_set,"structured_docs⊕rationale",formal_gates,comprehensive_testing],[[COMPLEX::["10K+_users","5+_components",high_impact,complex_integrations,regulatory]]],"→",["enhanced_docs⊕appendices",ADRs_all_decisions,"extended_security⊕compliance","comprehensive⊕performance⊕security_testing"],[[ENTERPRISE::[">100K_users","system-of-systems",mission_critical,extensive_integrations]]],"→",["full_suite⊕detailed_specs",formal_review_boards,comprehensive_security_audit,"full_compliance_docs⊕audit_trails","extended_validation⊕formal_gates"]]
WORKFLOW_PHASES:
  D0_MNEMOSYNE_GENESIS::IDEATION_SETUP
  SUBPHASES::"D0_01[sessions-manager]→session_structure+exploration_framework+graduation_assessment"
  NATURAL_ENTRY_PATTERN::[[[ENTRY::"User→idea-clarifier for natural conversation"]],[[FLOW::"idea-clarifier engages naturally→calls sessions-manager when structure needed"]],[[SESSIONS_MANAGER::"Creates session structure via D0-IDEATION-SETUP protocol"]],[[CONTINUATION::"idea-clarifier continues within established session"]]]
  RACI::"R[sessions-manager:complete_setup+graduation_assessment]→A[sessions-manager:quality+approval]→C[none:pre-formal]→I[potential_stakeholders:context]"
  DELIVERABLE::"Complete ideation session with graduation readiness assessed for B1_02[workspace-architect]"
  PROTOCOL_REF::"D0-IDEATION-SETUP protocol"
  ENTRY::[new_project_concept,systematic_investigation_needed]
  EXIT::[graduation_criteria_met,graduation_readiness_assessed,ready_for_D1]
D1_APOLLO_ORACLE::UNDERSTANDING_ESTABLISHMENT
SUBPHASES::"D1_01[idea-clarifier:exploration]:OPTIONAL→D1_02[research-analyst:investigation]:OPTIONAL→D1_03[requirements-architect:North_Star_formalization]:MANDATORY→D1_04[requirements-steward:validate]"
ENTRY_PATTERNS::[[[FULL_DISCOVERY::"idea-clarifier→research-analyst→requirements-architect (user needs exploration)"]],[[DIRECT_ENTRY::"requirements-architect only (user knows requirements, skip exploration)"]]]
NATURAL_FLOW::"D1 maintains natural conversational flow rather than artificial subdivisions"
RACI::"R[phase_specialists]→A[critical-engineer:North_Star_complete+correct]→C[none:not_building_yet]→I[none:no_implementation_teams]"
DELIVERABLE::"0xx-PROJECT[-NAME]-NORTH-STAR.md+immutable_requirements[7±2]+assumption_audit+commitment_ceremony_approval"
NORTH_STAR_ARCHITECTURE::"4-layer structure: immutable_core[5-9] + constrained_variables + assumption_register + explicit_non-requirements"
LOCATION::".hestai/north-star/"
D2_ATHENA_INNOVATION::SOLUTION_APPROACHES
SUBPHASES::"D2_01[ideator+edge-optimizer:creative_breakthrough]→D2_02[validator:feasibility_constraints]→D2_02B[edge-optimizer:additional_exploration:OPTIONAL]→D2_03[synthesizer:unified_approach]"
DUAL_ROLE_EDGE::"edge-optimizer contributes to D2_01 for breakthrough creative exploration AND D2_02B for boundary exploration"
RACI::"R[phase_specialists, edge-optimizer:D2_01+D2_02B_optional]→A[critical-engineer:synthesis_completeness+feasibility]→C[requirements-steward:North_Star, technical-architect:feasibility]→I[none:design_phase]"
DELIVERABLES::["D2_01-IDEAS.md","D2_02-CONSTRAINTS.md","D2_02B-EDGE_DISCOVERIES.md:optional","D2_03-DESIGN.md"]
EDGE_INTEGRATION::"D2_02B_discoveries→optional_input_to_D2_03_synthesis"
LOCATION::".hestai/rules/specs/"
SIGNOFF_REQUIRED::"D2_01[ideator]+D2_02[validator] approve D2_03[synthesis] before D3"
D3_DAEDALUS_CONSTRUCTION::TECHNICAL_BLUEPRINT
SUBPHASES::"D3_01[design-architect:technical_architecture]→D3_02[visual-architect:mockups+user_validation]→D3_03[technical-architect:validation]→D3_04[security-specialist:security+compliance]"
VISUAL_VALIDATION::"create_mockups→user_validation→IF[significant_changes]→CONSULT[design-architect+requirements-steward]→iterate→approval"
RACI::"R[phase_specialists]→A[critical-engineer:completeness+production_readiness]→C[requirements-steward:alignment, design-architect:changes]→I[implementation-lead:build_prep]"
DELIVERABLES::["D3-BLUEPRINT.md⊕complete_spec","D3-MOCKUPS.md⊕validation","D3-VISUAL-DECISIONS.md⊕rationale"]
LOCATION::".hestai/rules/specs/[migrates_to_docs/_at_B1_gate]"
B0_THEMIS_JUDGMENT::VALIDATION_GATE
PURPOSE::"Critical design validation→GO/NO-GO decision for build phase"
SUBPHASES::"B0_01[critical-design-validator:completeness+failure_modes]→B0_02[requirements-steward:North_Star_alignment]→B0_03[technical-architect:feasibility+scalability]→B0_04[critical-engineer:GO/NO-GO_decision]"
RACI::"R[validation_specialists]→A[critical-engineer:final_GO/NO-GO_authority]→C[security-specialist:security, error-architect:failure_modes, principal-engineer:long_term_viability]→I[implementation-lead, solution-steward, task-decomposer]"
ENTRY_REQUIREMENTS::["NORTH-STAR.md⊕approved⊕immutable","D2-DESIGN.md⊕validated","D3-BLUEPRINT.md⊕complete",assumption_audits_complete]
DELIVERABLE::"B0-VALIDATION.md+GO/NO-GO_decision"
LOCATION::".hestai/state/reports/[gate_evidence|architectural_decisions→docs/adr/]"
VALIDATION_CRITERIA::[North_Star_alignment,"architecture_sound⊕scalable⊕implementable",security_addressed,assumptions_validated,resources_realistic,no_blocking_risks]
EXIT::"GO[proceed_B1] | NO-GO[return_D-phase]"
B1_HERMES_COORDINATION::BUILD_EXECUTION_ROADMAP
PURPOSE::"Validated architecture→actionable implementation plan"
SUBPHASES::"B1_01[task-decomposer:atomic_tasks+dependencies]→B1_02[workspace-architect:project_migration_execution+structure+environments+CI/CD_pipeline+QUALITY_GATES_MANDATORY]→MIGRATION_GATE→B1_03[workspace-architect:build_directory_validation]→B1_04[implementation-lead:task_sequencing]→B1_05[build-plan-checker:completeness+feasibility]"
RACI::"R[planning_specialists]→A[critical-engineer:final_build_plan_approval]→C[technical-architect:guidance, requirements-steward:scope, principal-engineer:tech_debt_strategy_at_B1_01]→I[solution-steward, code-review-specialist, universal-test-engineer]"
MIGRATION_GATE::"B1_02_completion→STOP→HUMAN_MIGRATION_POINT"
RESTART_IN_NEW_LOCATION::"cd ${PROJECT_ROOT}/build/VERIFY_pwd→RESUME_B1_03"
QUALITY_GATE_MANDATORY::"⚠️ Load workspace-setup skill for stack-specific gates. NO src/ FILES WITHOUT PASSING quality gates per project stack: python[ruff_check,black_check,mypy,pytest] | node[npm_run_lint,npm_run_typecheck,npm_test] | generic[lint,typecheck,test]"
DELIVERABLES::["B1-BUILD-PLAN.md⊕task_breakdown","B1-WORKSPACE.md⊕environment⊕CI/CD_setup⊕QUALITY_GATE_EVIDENCE","B1-DEPENDENCIES.md⊕critical_path",TRACED_artifacts]
LOCATION::".hestai/rules/specs/[build_plan]+.hestai/state/reports/[gate_evidence]"
CRITERIA::[all_components_have_tasks,"dependencies_mapped⊕sequenced",test_requirements_identified,QUALITY_GATES_OPERATIONAL,resources_defined,risks_mitigated,"timeline_realistic⊕buffered"]
CONTEXT7_LIBRARY_RESEARCH::[[[PATTERN::"mcp__Context7__resolve-library-id→mcp__Context7__get-library-docs"]],[[D1_USAGE::"Research for problem understanding and existing solutions"]],[[B0_USAGE::"Architecture validation against current library capabilities"]],[[B1_USAGE::"Dependency versions and integration patterns"]],[[B2_USAGE::"API references and implementation examples during TDD"]],[[B3_USAGE::"Integration best practices and compatibility validation"]]]
B2_HEPHAESTUS_FORGE::CODE_CONSTRUCTION
PURPOSE::"Execute build plan through disciplined development+quality validation"
SUBPHASES::"B2_00[universal-test-engineer:test_strategy+methodology]→B2_01[implementation-lead:coordinate_development]→B2_02[universal-test-engineer:test_suites]→B2_03[code-review-specialist:quality_review]→B2_04[error-resolver:integration_issues]"
RACI::"R[development_specialists]→A[critical-engineer:production_standards]→C[technical-architect:compliance, Context7:libraries, universal-test-engineer:methodology, principal-engineer:pattern_monitoring_OPTIONAL]→I[solution-steward, completion-architect, security-specialist]"
B2_00_REQUIREMENTS::[test_strategy_aligned,coverage_requirements_defined,compliance_validation_setup,frameworks_approved,integrity_monitoring]
IMPLEMENTATION_STANDARDS::["TEST_STRATEGY_FIRST→TEST_FIRST→TRACED_METHODOLOGY",Context7_consultation_libraries,code_review_every_change,CI_immediate_failure_resolution,architecture_compliance,security_scanning]
QUALITY_GATES::["coverage_80%+",tests_passing_CI,code_review_approval,no_critical_vulnerabilities,performance_benchmarks_met,docs_updated]
DELIVERABLES::["B2-IMPLEMENTATION-LOG.md","B2-TEST-STRATEGY.md","source_code⊕tests","CI_pipeline⊕quality_gates",TRACED_compliance_artifacts]
LOCATION::".hestai/state/reports/"
B3_HARMONIA_UNIFICATION::SYSTEM_UNIFICATION
PURPOSE::"Unify components→cohesive system+validate end-to-end functionality+production readiness"
SUBPHASES::"B3_01[completion-architect:integration+coherence]→B3_02[universal-test-engineer:integration+E2E+performance]→B3_02B[edge-optimizer:breakthrough_optimization:OPTIONAL]→B3_03[security-specialist:security_audit+penetration]→B3_04[coherence-oracle:cross-system_consistency]"
RACI::"R[integration_specialists, edge-optimizer:B3_02B_optional]→A[critical-engineer:production_readiness]→C[technical-architect:system_architecture, error-architect:failure_modes, requirements-steward:requirement_fulfillment, universal-test-engineer:integration_methodology, principal-engineer:architectural_coherence]→I[implementation-lead, solution-steward, system-steward]"
INTEGRATION_VALIDATION::[component_interface_compatibility,"data_flow⊕state_management","error_handling⊕recovery",performance_under_load,security_vulnerabilities_addressed,"cross-platform_compatibility"]
SYSTEM_TESTING::[integration_tests_all_interactions,E2E_user_journey_validation,performance_benchmarks_achieved,security_penetration_passed,disaster_recovery_validated,"monitoring⊕observability_confirmed"]
DELIVERABLES::["B3-INTEGRATION-REPORT.md","B3-PERFORMANCE.md","B3-BREAKTHROUGH_OPTIMIZATIONS.md:optional","B3-SECURITY.md","fully_integrated_system⊕E2E_tests"]
BREAKTHROUGH_INTEGRATION::"B3_02B_optimizations→evaluated_by_completion-architect_for_system_integration"
LOCATION::".hestai/state/reports/"
B4_IRIS_HANDOFF::PRODUCTION_HANDOFF
PURPOSE::"Complete solution preparation for production deployment+comprehensive documentation+operational readiness"
SUBPHASES::"B4_01[solution-steward:package+docs+handoff]→B4_02[system-steward:architecture+operations+maintenance]→B4_03[workspace-architect:cleanup+publication_readiness]→B4_04[security-specialist:final_review+hardening]→B4_05[critical-engineer:production_readiness+signoff]"
DEPLOY_PHASES::"B4_D1[staging+validation]→B4_D2[live+production]→B4_D3[post-deployment+monitoring]"
RACI::"R[delivery_specialists, critical-engineer:deployment_phases]→A[critical-engineer:production_release+deployment_authority]→C[technical-architect:architecture_docs, implementation-lead:knowledge_transfer, principal-engineer:operational_sustainability]→I[completion-architect, requirements-steward]"
DELIVERABLES::["B4-HANDOFF.md","B4-OPERATIONS.md⊕runbooks","B4-USER-GUIDE.md","B4-MAINTENANCE.md","B4-WORKSPACE.md⊕publication_ready","deployment_packages⊕config",training_materials]
LOCATION::"docs/[graduated_permanent_documentation]"
PRODUCTION_READINESS::["infrastructure_provisioned⊕tested",deployment_procedures_validated,rollback_tested,"monitoring⊕alerting_active",security_scanning_complete,load_testing_passed,docs_approved,support_trained]
B5_PROMETHEUS_EVOLUTION::POST_DELIVERY_ENHANCEMENT
PURPOSE::"Feature expansion+architectural enhancement without full D1→B4 restart"
TRIGGERS::["core_system_delivered⊕stable",new_features_build_existing,"performance⊕scalability_improvements",integration_new_systems,UX_enhancements]
DECISION_MATRIX::"B5_Enhancement[extends_existing_no_fundamental_changes] | New_D1→B4[architectural_pivot_or_separate_system]"
SUBPHASES::"B5_01[requirements-steward:enhancement_analysis+North_Star_validation]→B5_02[technical-architect:impact+integration]→B5_03[implementation-lead:execute+quality_standards]→B5_04[critical-engineer:integration+stability]"
RACI::"R[enhancement_specialists]→A[critical-engineer:enhancement_approval]→C[original-project-agents:context, security-specialist:impact, principal-engineer:strategic_impact_MANDATORY]→I[solution-steward, system-steward]"
STANDARDS::[maintain_architectural_principles,"preserve_stability⊕performance","follow_testing⊕quality_protocols","document_changes⊕impact",maintain_backward_compatibility]
DELIVERABLES::["B5-ENHANCEMENT-PLAN.md","B5-IMPLEMENTATION.md",updated_system_docs,integration_testing_results]
ERROR_HANDLING_TAXONOMY:
  COMPONENT_ERRORS::ERROR_RESOLVER_HERMES
  QUICK_FIX_ERRORS::"≤30_minutes[syntax/config, obvious_root_cause, single_file_fix, zero_architectural_implications]"
  COMPLEX_ERRORS::"30_min-4_hours[multi-component, performance_degradation, investigation_required]"
  SYSTEM_ERRORS::ERROR_ARCHITECT_ZEUS
  ESCALATION_ERRORS::">4_hours_or_high_risk[architectural_changes_required, multi-team_coordination, high_business_impact]"
  DESIGN_ERRORS::REQUIREMENTS_STEWARD_ATHENA
  RESOLUTION_PROCESS::"DETECTION+CLASSIFICATION[decision_tree]→COORDINATOR_ASSIGNMENT→RESOLUTION+EVIDENCE→SYSTEM_VALIDATION"
  EMERGENCY_PROTOCOL::"CRITICAL_ERRORS→STOP_work→CRITICAL-ENGINEER_incident_commander→SPECIALIST_TEAM→STABILIZATION_before_root_cause→MITIGATION+POST_MORTEM"
  USER_UNAVAILABILITY_PROTOCOL::">24_hours_no_response→[document_current_state+assumptions+questions, preserve_work+detailed_commits, status_WAITING_USER_INPUT, resume_instructions_for_continuity]"
POST_MORTEM_ANALYSIS:
  PURPOSE::"Extract systemic patterns from incidents for preventive architecture"
  DUAL_ANALYSIS::[[[TACTICAL::"critical-engineer analyzes immediate cause, root technical failure, remediation plan (What broke RIGHT NOW?)"]],[[STRATEGIC::"principal-engineer identifies systemic patterns, architectural decay signals, preventive measures (Why will this pattern repeat?)"]]]
  COLLABORATION_PATTERN::"critical-engineer produces incident analysis→principal-engineer consumes for pattern extraction→joint recommendations (tactical fixes + strategic prevention)"
  DELIVERABLE::"Post-mortem report with tactical remediation AND strategic architectural recommendations"
  INVOCATION::"MANDATORY for CRITICAL incidents, HIGH-priority recurring failures, architectural erosion signals"
ARTIFACT_PLACEMENT:
  LIFECYCLE_MODEL::"Spec[.hestai/rules/specs/]→Report[.hestai/state/reports/]→Doc[docs/]"
  DOCUMENT_PLACEMENT_PROTOCOL::"Load documentation-placement skill for placement rules and visibility protocols"
  CANONICAL_REFERENCE::".hestai-sys/standards/rules/visibility-rules.oct.md"
  PHASE_TRANSITION_CLEANUP::["B1_02, B2_04, B3_04, B4_05 require cleanup validation","holistic-orchestrator→directory-curator→workspace-architect pattern"]
SESSION_COORDINATION:
  IDEATION_GRADUATION_EXECUTION::[[[D0_IDEATION::".hestai/state/sessions/[structured_exploration+thread_messaging+manifest_tracking]"]],[[PROJECT_MIGRATION_EXECUTION::"workspace-architect[B1_02]→migration[ideation→project/sessions/]→MIGRATION_GATE[directory_change_required]→state_symlink[.hestai/state/]→using_graduation_assessment_from_D0"]],[[ARTIFACT_DISTRIBUTION::"D1→.hestai/north-star/, D2-D3→.hestai/rules/specs/, B0-B3→.hestai/state/reports/, B4→docs/"]]]
  LINK_STANDARDS::[[[LOCALITY_PRINCIPLE::"internal_links[relative_paths], external_links[full_paths_boundary_crossing_only]"]],[[MIGRATION_RESILIENCE::"links_survive_reorganization+repository_moves"]],[[VALIDATION_ENFORCEMENT::"automation_testable+broken_links_block_commits"]]]
ENHANCEMENT_CLASSIFICATION:
  B5_CRITERIA::[improves_existing_beyond_original,works_within_architectural_framework,completable_within_scope_limits,low_destabilization_risk]
  NEW_PROJECT_TRIGGERS::[architectural_changes_or_new_components,new_external_integrations_or_major_dependencies,core_business_logic_or_data_model_changes,timeline_exceeds_enhancement_capacity]
  ENHANCEMENT_PROCESS::"Requirements→Architectural_Assessment→Implementation→Integration_Validation"
CROSS_REFERENCE_INTEGRATION:
  CONSOLIDATED_FROM::"Documents[003,004,005,006,010,011]→unified_methodology[error_handling+directory_coordination+session_architecture+enhancement_lifecycle]→eliminate_redundancy+preserve_operational_wisdom"
OPERATIONAL_PATTERNS:
  PHASE_DEPENDENCIES::"Linear_progression+gate_enforcement+completeness_validation"
  RACI_ACCOUNTABILITY::"Clear_responsibility_chains+coordination_failures_prevention"
  SCOPE_CALIBRATION::"Proportional_effort_allocation+validation_theater_prevention"
  COORDINATION_SYMLINKS::"Easy_access+context_preservation+migration_resilience"
  ERROR_CLASSIFICATION::"Systematic_routing+evidence_requirements+escalation_triggers"
  ENHANCEMENT_LIFECYCLE::"Architectural_preservation+stability_maintenance+evolution_capability"
===END===
