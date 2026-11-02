===DECISION_RECORD===
META:
  TYPE::DECISION_RECORD
  VERSION::"1.0"
  TOKEN::REVIEW-REQUIREMENTS-MD-RECORDS-20261102
  STATUS::RATIFIED
  TIER::TACTICAL
  DECISION::"Markdown decision records and ADRs under .hestai/decisions/** and docs/adr/** are reviewed as GOVERNANCE (SR required), no longer exempt as plain .md; GOVERNANCE no longer qualifies for TIER_1 self-review."
  BECAUSE::"Gate exempts **/*.md unless .oct.md, so quoted-YAML <token>.md decision records got no review (elevanaltd/hestai-context-mcp#259). hestai-context-mcp PR #260 fixes the classifier, but this rule outranks the code, so the rule changes first."
  AUTHORED_AT::"2026-11-02T15:23:57Z"
  RATIFIED_BY::"human:shaun.buswell@elevana.com"
  RATIFIED_AT::"2026-11-02T15:23:57Z"
  SCOPE::"src/hestai_mcp/_bundled_hub/standards/rules/review-requirements.oct.md v3.1 to v3.2: GOVERNANCE TRIGGER, TIER_0_EXEMPT EXEMPT_PATTERNS, PATH_OVERRIDES, TIER_1_SELF CONDITION. Other .md incl. .hestai/MANIFEST.md stay exempt."
  CANONICAL::".hestai/decisions/2026-11-02-review-requirements-md-records.oct.md"
  SOURCE::".hestai/decisions/2026-11-02-review-requirements-md-records.oct.md"
  RULING_1::"Operator words, HestAI-MCP control room session, 2026-11-02: 'I'm happy for you to go ahead with the review-requirements amendment as long as it's not a lot of retroactive work'"
  RETROACTIVITY::"None. The gate classifies only files changed in a PR, so existing .md decision records and ADRs are not re-reviewed; the control room confirmed no retroactive work."
  ORDER::"This amendment precedes hestai-context-mcp #260 and the move of ruleset 12626210."
  FILED_VIA::"Committed in-branch per the PR #440 and #447 precedent, not via submit_governance, because the linker's uppercase TOKEN filename fails naming-visibility-validate for .hestai/decisions/ (measured failing 2026-11-02)."
===END===
