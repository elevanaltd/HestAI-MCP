===DECISION_RECORD===
META:
  TYPE::DECISION_RECORD
  VERSION::"1.0"
  TOKEN::OPERATIONAL-WORKFLOW-HAND-EDIT-REFRESH-20260929
  STATUS::RATIFIED
  TIER::TACTICAL
  DECISION::"One-off: refresh src/hestai_mcp/_bundled_hub/standards/workflow/OPERATIONAL-WORKFLOW.oct.md by hand edit, NOT octave_write, so it is current and still parsed correctly by the hestai-context-mcp line-based phase reader."
  BECAUSE::"The file is stale against current governance, and octave_write's canonical output explodes inline lists across lines, which makes hestai-context-mcp ContextSteward return B1 deliverables as a bare bracket (reproduced at context-mcp 06aac8c). B1 is the phase every consumer serves."
  AUTHORED_AT::"2026-09-29T00:00:00Z"
  RATIFIED_BY::"human:shaun.buswell@elevana.com"
  RATIFIED_AT::"2026-09-29T00:00:00Z"
  SCOPE::"src/hestai_mcp/_bundled_hub/standards/workflow/OPERATIONAL-WORKFLOW.oct.md"
  CANONICAL::".hestai/decisions/2026-09-29-operational-workflow-hand-edit-refresh.oct.md"
  SOURCE::".hestai/decisions/2026-09-29-operational-workflow-hand-edit-refresh.oct.md"
  RULING_1::"The octave_write-only rule for .oct.md is waived for this one edit of this one file. Operator words in the HestAI-MCP control room session, 2026-09-29: 'Don't use octave write on this occasion and I'm fine with this.'"
  RULING_2::"Editing this bundled-hub standards file proceeds now. The operator asked for the edit while the repo is otherwise parked until after 2026-10-08. This is NOT a general ruling on whether _bundled_hub/standards is inside the 90-day freeze; that question stays open on HestAI-MCP issue 446."
  SCOPE_LIMIT::"Covers this edit of this file only. Subsequent edits return to octave_write once the hestai-context-mcp reader parses OCTAVE structurally instead of by line regex. It does not authorise hand edits of any other .oct.md, nor a byte copy into hestai-workbench .hestai/workflow."
  CONSTRAINT::"The edit must preserve the reader contract: one phase-marker key per phase with a scalar value, no other key starting with a phase prefix, single-line values for PURPOSE RACI DELIVERABLE(S) ENTRY EXIT QUALITY_GATE(S) SUBPHASES, B1 PURPOSE containing architecture or implementation, and the ERROR_HANDLING_TAXONOMY key."
  FILED_VIA::"Committed in-branch per the PR #440 precedent (operator ruling), not via submit_governance, because the linker's uppercase TOKEN filename fails naming-visibility-validate for .hestai/decisions/ (scripts/ci/validate_naming_visibility.py:79-92)."
===END===
