===WORKFLOW_NORTH_STAR===

META:
  NAME::"Workflow North Star"
  VERSION::"1.0"
  PURPOSE::"Defines HestAI phase-gated workflow and governance anchors"

METADATA::[
  type::workflow,
  domain::governance,
  status::active,
  owners::[system-steward],
  created::2025-12-19,
  updated::2025-12-19,
  id::workflow-north-star,
  canonical::hub/governance/workflow/001-workflow-north-star.oct.md,
  format::octave,
  tags::[workflow|phases|methodology]
]

===MISSION===

GOAL::structured_AI_assisted_development_with_integrated_governance

PROBLEM_SOLVED::cognitive_continuity_crisis[AI_no_persistent_memory|projects_need_months_context]

OPERATOR::single_developer+laptop+multiple_terminals+multi_model_AI_orchestration

===PHASE_STRUCTURE===

PHASES::D0→D1→D2→D3→B0→B1→B2→B3→B4→B5

PHASE_DEFINITIONS::[
  D0::discovery_exploration[understand_problem_space],
  D1::requirements_north_star[define_immutable_requirements],
  D2::architecture_design[system_structure_decisions],
  D3::implementation_plan[detailed_build_tasks],
  B0::workspace_setup[environment_dependencies],
  B1::foundation_infrastructure[core_systems],
  B2::feature_implementation[TDD_cycle],
  B3::integration_validation[system_coherence],
  B4::deployment_preparation[production_ready],
  B5::delivery_handoff[transfer_ownership]
]

===GATE_ENFORCEMENT===

PROGRESSION::phase_gated[compress_not_skip]

QUALITY_GATES::[
  no_merge_without_tests,
  CI_must_pass[lint+typecheck+test],
  artifacts_required[reproducible_evidence],
  human_approval_for_phase_transition
]

===SIX_IMMUTABLES===

I1::VERIFIABLE_BEHAVIORAL_SPECIFICATION_FIRST[TDD:RED→GREEN→REFACTOR→git_evidence]
I2::PHASE_GATED_PROGRESSION[D0→D1→D2→D3→B0→B1→B2→B3→B4→compress_not_skip]
I3::HUMAN_PRIMACY[AI_advises+executes≠decides_strategy→human_approval_required]
I4::DISCOVERABLE_ARTIFACT_PERSISTENCE["If_not_written_and_addressable→didn't_happen"]
I5::QUALITY_VERIFICATION_BEFORE_PROGRESSION[gates_BLOCK_not_warn→no_bypass]
I6::EXPLICIT_ACCOUNTABILITY[every_decision→identifiable_owner→orphans_escalate]

===TDD_DISCIPLINE===

CYCLE::RED→GREEN→REFACTOR

RED::write_failing_test→verify_failure
GREEN::minimal_implementation→verify_pass
REFACTOR::improve_while_green→maintain_passing_tests

EVIDENCE::git_commits[TEST:X→FEAT:X]→reproducible_sequence

NEVER::[skip_tests|fix_tests_not_code|implementation_before_test]

===ROLE_BASED_EXECUTION===

ACCOUNTABILITY::RACI_matrix[Responsible|Accountable|Consulted|Informed]

KEY_AGENTS::[
  requirements-steward::immutable_requirements_guardian,
  critical-engineer::architectural_GO_NO-GO_authority,
  implementation-lead::build_phase_hub+TDD_enforcer,
  code-review-specialist::mandatory_code_review,
  test-methodology-guardian::test_strategy_authority,
  error-architect::systematic_error_resolution
]

===ARTIFACT_PERSISTENCE===

DISCOVERABILITY::"If_not_written_and_addressable→didn't_happen"

ARTIFACT_LOCATIONS::[
  docs/→permanent_architectural[ADRs|system_design|API_docs],
  .hestai/context/→operational_state[PROJECT-CONTEXT|APP-CONTEXT],
  .hestai/workflow/→methodology[north_star|DECISIONS.md],
  .hestai/sessions/archive/→durable_audit_trail,
  .hestai/reports/→evidence_findings
]

===HUMAN_PRIMACY===

AUTHORITY::human_judgment→final_arbiter

AI_ROLE::augment+execute≠override_strategy

APPROVAL_REQUIRED::[
  phase_transitions,
  architectural_decisions,
  scope_changes,
  quality_gate_exceptions[none_allowed]
]

===COMPANION_STANDARDS===

REFERENCES::[
  naming-standard.oct.md::HOW_to_name_artifacts,
  visibility-rules.oct.md::WHERE_to_place_artifacts,
  test-structure-standard.oct.md::TEST_organization
]

===AUTHORITY===

SOURCE::HestAI_system_methodology
VERSION::1.0
SUPERSEDES::none[foundational]

===END===
