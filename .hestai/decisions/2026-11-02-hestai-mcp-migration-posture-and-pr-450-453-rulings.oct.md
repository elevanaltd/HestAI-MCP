===DECISION_RECORD===
META:
  TYPE::DECISION_RECORD
  VERSION::"1.0"
  TOKEN::HESTAI-MCP-MIGRATION-POSTURE-AND-PR-450-453-RULINGS-20261102
  STATUS::RATIFIED
  TIER::TACTICAL
  DECISION::"Three operator rulings of 2026-11-02: (1) HestAI-MCP is winding down, its function migrating to hestai-workbench, possibly hestai-context and maybe elsewhere, and it remains a secondary source until the operator says otherwise. (2) PR #453 is approved on the route in RULING_2. (3) PR #450 proceeds, including a three-line octave_write waiver and this ruling record."
  AUTHORED_AT::"2026-11-02T00:00:00Z"
  RATIFIED_BY::"human:shaun.buswell@elevana.com"
  RATIFIED_AT::"2026-11-02T10:55:50Z"
  SCOPE::"HestAI-MCP repository posture; PR #450; PR #453; src/hestai_mcp/_bundled_hub/standards/workflow/OPERATIONAL-WORKFLOW.oct.md (three lines only)"
  CANONICAL::".hestai/decisions/2026-11-02-hestai-mcp-migration-posture-and-pr-450-453-rulings.oct.md"
  SOURCE::".hestai/decisions/2026-11-02-hestai-mcp-migration-posture-and-pr-450-453-rulings.oct.md"
  RULING_1::"Operator words, verbatim, in the control room session: 'Wind-down - The plan would be to migrate everyhting that this repo does into hestai-workbench, possibly hestai-context and maybe somewhere else. It's still in progress, so it remains as a secondary source until I say otherwise.'"
  RULING_2::"Operator words, verbatim, in the control room session: '453 = I approve'. It approves this #453 route: octave-expert fixes the upstream defects in a small octave-mcp PR ahead of P2-8b and #453 re-copies; agent-expert ports hub octave-secretary; skills-expert updates the North Star template and test wording; implementation-lead bumps uv.lock. The bypass call at the final head stays with the HO under the operator's instruction in the HO's own session (ho-hmcp-1): 'We may not require a review of these, especially as hestai-mcp is winding down, so I'm happy to bypass if you deem it ok'."
  RULING_3::"Operator words, verbatim, in the control room session: '450 = Yes, get ho-hmcp-1 to work on this'. Confirmed in the HO's own session: 'Go ahead with #450, including the three-line waiver and the ruling record'. It waives octave_write for exactly three lines of OPERATIONAL-WORKFLOW.oct.md (B2_04 in SUBPHASES, COMPONENT_ERRORS, RECOVERY_PROFILE_STATUS) and for nothing else."
  SCOPE_LIMIT::"Sets no migration destination or date; retires nothing; does not itself authorize a merge."
  FILED_VIA::"Committed in-branch per the PR #440 precedent (operator ruling), not via submit_governance, because the control room's real submit_governance call on 2026-11-02 failed at commit on canonical-paths-validate (missing META.CANONICAL and META.SOURCE) and naming-visibility-validate (uppercase token filename), and the second cannot be fixed from the content."
===END===
