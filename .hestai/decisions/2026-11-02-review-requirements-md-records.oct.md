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
  RULING_2::"Operator words, HestAI-MCP control room session, 2026-11-03: 'Yes to the interim rule, all nine repos.'"
  RETROACTIVITY::"None. The gate classifies only files changed in a PR, so existing .md decision records and ADRs are not re-reviewed; the control room confirmed no retroactive work."
  INTERIM_HOLD::"Until the proof run passes, no Markdown decision record or ADR merges without an SR review, or while its latest SR at the head commit is BLOCKED. Scope: all nine repos on ruleset 12626210. Reason: pinned validator 7153bfd1 still exempts these Markdown paths, so the rule is not yet enforced by the gate."
  ACTIVATION_OWNERS::"The context-mcp room merges hestai-context-mcp #260 and the review-gate.yml re-pin PR within 24 hours of this amendment merging; the operator then moves ruleset 12626210 when able."
  ACTIVATION_PROOF::"After the ruleset move, a throwaway PR containing only a small .hestai/decisions/*.md record, in a repo the ruleset covers, must show SR required and stay red without an SR approval, then be closed unmerged. The context-mcp room reports the run link."
  ORDER::"This amendment, then hestai-context-mcp #260, then the review-gate.yml re-pin PR, then the move of ruleset 12626210, then the proof run."
  FILED_VIA::"Committed in-branch per the PR #440 and #447 precedent, not via submit_governance, because the linker's uppercase TOKEN filename fails naming-visibility-validate for .hestai/decisions/ (measured failing 2026-11-02)."
===END===
