===PATTERN:PHASE_TRANSITION_CLEANUP===
META:
  TYPE::PATTERN
  VERSION::"1.0"
  PURPOSE::"Protocol for maintaining system hygiene at phase boundaries"
  CANONICAL::".hestai-sys/library/patterns/phase-transition-cleanup.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/patterns/phase-transition-cleanup.oct.md"
§1::TRIGGER_POINTS
TRIGGERS::[
  B1_02_complete,
  B2_04_complete,
  B3_04_complete,
  B4_05_complete
]
§2::EXECUTION
CLEANUP_SEQUENCE::"INVOKE directory-curator → RECEIVE violations report → DELEGATE workspace-architect → VALIDATE clean state"
ENFORCEMENT::"BLOCK phase progression if violations exist after workspace-architect remediation"
§3::REFERENCE
PROTOCOL_REFERENCE::".hestai-sys/standards/rules/visibility-rules.oct.md"
§5::ANCHOR_KERNEL
TARGET::phase_boundary_system_hygiene
NEVER::[progress_phase_while_violations_exist_after_workspace_architect_remediation,skip_cleanup_at_trigger_points]
MUST::[
  run_cleanup_at_B1_02_B2_04_B3_04_B4_05_completion,
  at_trigger_points_invoke_directory_curator_then_receive_violations_report,
  at_trigger_points_delegate_workspace_architect_to_remediate,
  at_trigger_points_validate_clean_state_before_phase_progression
]
GATE::"After workspace-architect remediation, is the state clean of violations so the phase may progress?"
===END===
