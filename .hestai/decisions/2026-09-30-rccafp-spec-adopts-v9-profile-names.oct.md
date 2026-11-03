===DECISION_RECORD===
META:
  TYPE::DECISION_RECORD
  VERSION::"1.0"
  TOKEN::RCCAFP-SPEC-ADOPTS-V9-PROFILE-NAMES-20260930
  STATUS::RATIFIED
  TIER::TACTICAL
  DECISION::"Option B. The V9 profile names stay: error_diagnosis is implementation-lead's recovery profile and code_writing is its default. RCCAFP-ERROR-RECOVERY-SPEC.md (v1.1) and standards/workflow/OPERATIONAL-WORKFLOW.oct.md are amended to use them (build_failure_recovery becomes error_diagnosis; feature_implementation becomes code_writing). The vault does not change."
  BECAUSE::"V9 already implements the spec's section 6 content: in config/archetype-matrix.json, implementation-lead.profiles.error_diagnosis loads error-triage and diagnostic-protocols under APOLLO<analysis>."
  AUTHORED_AT::"2026-11-02T00:00:00Z"
  RATIFIED_BY::"human:shaun.buswell@elevana.com"
  RATIFIED_AT::"2026-09-30T00:00:00Z"
  SCOPE::implementation-lead
  ISSUE_REF::"https://github.com/elevanaltd/hestai-workbench-library/issues/5"
  CANONICAL::".hestai/decisions/2026-09-30-rccafp-spec-adopts-v9-profile-names.oct.md"
  SOURCE::".hestai/decisions/2026-09-30-rccafp-spec-adopts-v9-profile-names.oct.md"
  SUPERSEDES::"Replaces the unmerged token IL-BUILD-FAILURE-RECOVERY-PROFILE-SUPERSEDES-20260930, whose ruling (build_failure_recovery supersedes error_diagnosis; spec not amended) the operator overturned the same day. That token never merged and is retired with this record."
  RULING_1::"Operator words, verbatim: 'It was B. V9 names stay. The spec and workflow are amended.' (HestAI-MCP control room session, 2026-09-30, final; also quoted in the correction comment on hestai-workbench-library#5)."
  RULING_2::"The default profile stays code_writing; the spec's feature_implementation is renamed to it. Recorded in the control room ledger and the hestai-workbench-library#5 correction comment as part of option B."
  SCOPE_LIMIT::"Names the profiles only; does not author profile content. The vault hestai-workbench-library does not change."
  FILED_VIA::"Committed in-branch per the PR #440 and #447 precedent (operator ruling), not via submit_governance, because the linker's uppercase TOKEN filename fails naming-visibility-validate for .hestai/decisions/ (scripts/ci/validate_naming_visibility.py:79-92). The vault repo hestai-workbench-library has no .hestai governance structure; the spec this ruling amends lives in this repo."
===END===
