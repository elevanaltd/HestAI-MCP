===DECISION_RECORD===
META:
  TYPE::DECISION_RECORD
  VERSION::"1.0"
  TOKEN::IL-BUILD-FAILURE-RECOVERY-PROFILE-SUPERSEDES-20260930
  STATUS::RATIFIED
  TIER::TACTICAL
  DECISION::"implementation-lead's recovery profile is build_failure_recovery as defined by RCCAFP-ERROR-RECOVERY-SPEC.md (section 2.1 Reanchoring Upload; section 6 loads error-triage and diagnostic-protocols). It supersedes the vault's error_diagnosis task profile. Agents align to the spec; the spec is not amended."
  BECAUSE::"error_diagnosis dates from the initial vault (2026-03-31, hestai-workbench-library 2628d2a). The spec, added to the bundled hub on 2026-04-06 (c0a4fe6), introduced build_failure_recovery and declares itself the single source of truth for error recovery, superseding earlier approaches. The operator ruled that the newer profile supersedes."
  AUTHORED_AT::"2026-09-30T00:00:00Z"
  RATIFIED_BY::"human:shaun.buswell@elevana.com"
  RATIFIED_AT::"2026-09-30T00:00:00Z"
  SCOPE::implementation-lead
  ISSUE_REF::"https://github.com/elevanaltd/hestai-workbench-library/issues/5"
  CANONICAL::".hestai/decisions/2026-09-30-il-build-failure-recovery-profile-supersedes.oct.md"
  SOURCE::".hestai/decisions/2026-09-30-il-build-failure-recovery-profile-supersedes.oct.md"
  RULING_1::"Operator words, verbatim: 'IL profile = the new profile supersedes so we dshould align with this' (HestAI-MCP control room session, 2026-09-30). Applied as option 1 of hestai-workbench-library#5."
  RULING_2::"The spec's return profile, feature_implementation, follows the same rule over the vault default code_writing. APPLIED BY INFERENCE from 'align with this', not stated separately by the operator. The operator may narrow it."
  SCOPE_LIMIT::"Names the profile only; does not author the profile content. Vault edits happen in hestai-workbench-library. Bundled-hub library edits stay under AGENT-LOADING-90-DAY-IN-FLOW-EVIDENCE-RULE-20260929 (hand edits ruled out until 2026-12-28) unless the operator directs otherwise. After alignment, HestAI-MCP replaces the interim B2_04 route in standards/workflow/OPERATIONAL-WORKFLOW.oct.md and removes RECOVERY_PROFILE_STATUS."
  FILED_VIA::"Committed in-branch per the PR #440 and #447 precedent (operator ruling), not via submit_governance, because the linker's uppercase TOKEN filename fails naming-visibility-validate for .hestai/decisions/ (scripts/ci/validate_naming_visibility.py:79-92). The vault repo hestai-workbench-library has no .hestai governance structure; the spec this ruling aligns to lives in this repo."
===END===
