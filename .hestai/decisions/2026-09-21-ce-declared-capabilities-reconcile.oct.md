===DECISION_RECORD===
META:
  TYPE::DECISION_RECORD
  VERSION::"1.1"
  TOKEN::CE-DECLARED-CAPABILITIES-RECONCILE-20260921
  STATUS::RATIFIED
  TIER::TACTICAL
  DECISION::"critical-engineer only: HestAI-MCP is source of truth for its bundled hub; PORT critical-domain-invariants from workbench seed; REMOVE observability-validation-standards, disaster-recovery-validation, incident-response from declared capabilities."
  BECAUSE::"Hub is authored/shipped from HestAI-MCP (cmp exit 0 vs workbench); ported skill's own header says observability/disaster-recovery fold into other domains, never standalone; incident-response exists nowhere else — rccafp is the hub's incident protocol."
  AUTHORED_AT::"2026-09-21T00:00:00Z"
  ISSUE_REF::"https://github.com/elevanaltd/HestAI-MCP/issues/431"
  RATIFIED_BY::"human:shaun.buswell@elevana.com"
  RATIFIED_AT::"2026-09-21T00:00:00Z"
  SCOPE::critical-engineer
  CANONICAL::".hestai/decisions/2026-09-21-ce-declared-capabilities-reconcile.oct.md"
  SOURCE::".hestai/decisions/2026-09-21-ce-declared-capabilities-reconcile.oct.md"
  RULING_1::"Bundled hub home: src/hestai_mcp/_bundled_hub/library is authored and shipped from HestAI-MCP, which remains its source of truth despite the repo's legacy_maintenance posture. Evidence: cmp of the hub's critical-engineer.oct.md against hestai-workbench's deployed .hestai-sys copy exited 0."
  RULING_2::"critical-engineer declared capabilities made true without speculative authoring: PORT critical-domain-invariants from the hestai-workbench starter-library seed (byte-identical to the V9 vault copy); REMOVE observability-validation-standards and disaster-recovery-validation from SKILLS, because the ported skill states in its own header that observability folds into LOGGING/ERROR and disaster-recovery/runbook validation into STATE/DATA, never standalone skills; REMOVE incident-response from PATTERNS, because it exists nowhere in the ecosystem outside the CE declaration, and rccafp, already in the hub, is the incident protocol."
  SCOPE_LIMIT::"This covers critical-engineer ONLY. It is NOT a ruling on #431's reconcile-vs-migrate question for the remaining 43 unresolved selectors across 12 other hub agents; that stays open."
  SUPPORTING_FINDING::"At HEAD 6ed6547, 204 capability declarations across all 34 hub agents, 47 unresolved, all in the legacy top-level SKILLS/PATTERNS scheme; profile-nested, kernel_only, and CHASSIS schemes resolve fully."
  FILED_VIA::"Committed in-branch by operator ruling (Option A, 2026-09-21), not via submit_governance. Blocker: hestai-context-mcp linker.py:305 commit path has no hook handling, and its throwaway worktree lacks .venv, which HestAI-MCP hooks octave-validate and validate-namespaces require."
===END===
