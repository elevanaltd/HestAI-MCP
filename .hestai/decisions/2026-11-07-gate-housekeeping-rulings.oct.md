===DECISION_RECORD===
META:
  TYPE::DECISION_RECORD
  VERSION::"1.0"
  TOKEN::GATE-HOUSEKEEPING-RULINGS-20261107
  STATUS::RATIFIED
  TIER::TACTICAL
  DECISION::"Retire HestAI-MCP's own review-gate.yml; ruleset 12626210 stays on hestai-context-mcp main, unpinned; SECURITY trigger gains redaction, provenance and clock_out segments; ho-hmcp-1 posts PR #453's post-merge bypass record."
  BECAUSE::"The ruleset-injected gate is proven to require SR in this repo, so the local workflow is redundant. Main moves because the gate is updated frequently. The trigger matches the hestai-context-mcp classifier."
  AUTHORED_AT::"2026-11-07T02:51:03Z"
  RATIFIED_BY::"human:shaun.buswell@elevana.com"
  RATIFIED_AT::"2026-11-07T02:51:03Z"
  SCOPE::"HestAI-MCP .github/workflows/review-gate.yml retirement; ruleset 12626210 pin posture; review-requirements.oct.md v3.2 to v3.3 SECURITY TRIGGER; PR #453 post-merge bypass record ownership."
  CANONICAL::".hestai/decisions/2026-11-07-gate-housekeeping-rulings.oct.md"
  SOURCE::".hestai/decisions/2026-11-07-gate-housekeeping-rulings.oct.md"
  RULING_1::"Operator words, HestAI-MCP control room session, 2026-11-07, answering numbered question 1 (retire the local review-gate.yml): '1.Yes, retire'"
  RULING_2::"Operator words, HestAI-MCP control room session, 2026-11-07, answering numbered question 2 (ruleset 12626210 stays on hestai-context-mcp main, no SHA pin): '2. I am fine with main movig the gate as we update it frequently at present'"
  RULING_3::"Operator words, HestAI-MCP control room session, 2026-11-07, answering numbered question 3 (add the SECURITY trigger paths redaction, provenance, clock_out): '3. yes, open it'"
  RULING_4::"Operator words, HestAI-MCP control room session, 2026-11-07, answering numbered question 4 (PR #453 post-merge bypass record): '4. agree, ho-hmcp-1 should post it. I'll let them know.'"
  EVIDENCE::"Proof PR HestAI-MCP #455, injected run 42330299493, shows the ruleset-injected gate requires SR in HestAI-MCP. Proof PR hestai-workbench #711, run 42330324450."
  INTERIM_HOLD_LIFTED::"The interim hold in REVIEW-REQUIREMENTS-MD-RECORDS-20261102 was lifted on 2026-11-07 on the evidence of proof PRs HestAI-MCP #455 and hestai-workbench #711."
  FILED_VIA::"Committed in-branch per the PR #440 precedent, not via submit_governance, because the linker's uppercase TOKEN filename fails naming-visibility-validate for .hestai/decisions/ (measured failing 2026-11-02)."
===END===
