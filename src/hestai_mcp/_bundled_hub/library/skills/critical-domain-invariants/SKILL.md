===SKILL:CRITICAL_DOMAIN_INVARIANTS===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Enumerated 12-domain production-readiness invariant sweep — per domain the invariant that must hold, the evidence that proves it, and the failure mode if absent"
§1::CORE
AUTHORITY::"BLOCKING<unproven_invariant⊕missing_evidence_on_critical_path⊕silent_failure_mode>"
SCOPE::"Production-readiness lens: a fixed-order sweep of 12 operational domains, each evidence-gated. Distinct from evidence-review<review_methodology> and security-audit<OWASP_threat_lens> — this enumerates production invariants per domain, not findings-by-confidence nor threats-by-category."
// Each domain asks one question: what MUST hold in production, what EVIDENCE proves it holds, what BREAKS if it does not.
// ETHOS cognition: assume failure until evidence proves the invariant. No domain passes on assertion alone.
// ABSORB (MIP): observability folds into LOGGING⊕ERROR; disaster-recovery⊕runbook validation folds into STATE⊕DATA. These are sub-sections here, never standalone skills.
§2::PROTOCOL
SWEEP_ORDER::[AUTH→SECRETS→DB→API→STATE→CONFIG→DEPS→PERF→ERROR→LOGGING→ACCESS→DATA]
// Run in order. A later domain may depend on an earlier one holding (e.g. ACCESS presumes AUTH).
D01_AUTH::[
  INVARIANT::"every protected path authenticates before authorizing⊕sessions expire⊕rotate⊕invalidate",
  EVIDENCE::"auth middleware on each protected route⊕session lifecycle test⊕token scope check",
  FAILURE::"unauthenticated access⊕stale session reuse⊕privilege confusion"
]
D02_SECRETS::[
  INVARIANT::"no secret in source⊕logs⊕client bundle — all secrets from environment∨vault",
  EVIDENCE::"secret-scan clean⊕env-injection confirmed⊕no secret in build artifact",
  FAILURE::"credential leak⊕key exfiltration via logs∨git history"
]
D03_DB::[
  INVARIANT::"migrations forward-only⊕reversible∨documented⊕constraints enforce referential integrity⊕transactions wrap multi-write",
  EVIDENCE::"migration up∧down test⊕FK∧unique constraints present⊕transaction boundary on critical writes",
  FAILURE::"orphaned rows⊕partial-write corruption⊕unrecoverable schema drift"
]
D04_API::[
  INVARIANT::"inputs validated at boundary⊕versioned contract⊕idempotency on retryable mutations⊕rate limits on public surface",
  EVIDENCE::"schema validation on every endpoint⊕contract test⊕idempotency-key handling⊕rate-limit config",
  FAILURE::"malformed-input crash⊕breaking-change to consumers⊕duplicate-effect on retry"
]
D05_STATE::[
  INVARIANT::"persistent state survives restart⊕recovers from interruption mid-operation⊕no orphaned locks∨leases",
  EVIDENCE::"restart-recovery test⊕interrupted-operation replay⊕lease-expiry verification // disaster-recovery: documented recovery procedure∧tested restore path",
  FAILURE::"state loss on crash⊕deadlock from orphaned lock⊕unrecoverable mid-operation halt"
]
D06_CONFIG::[
  INVARIANT::"config validated at startup⊕fail-fast on missing-required⊕no environment-coupled defaults that mask misconfig",
  EVIDENCE::"startup config-validation⊕missing-required aborts boot⊕config schema documented",
  FAILURE::"silent misconfiguration⊕prod running on dev defaults⊕late-runtime config crash"
]
D07_DEPS::[
  INVARIANT::"dependencies pinned⊕free of known CVEs⊕transitive risk assessed⊕no abandoned-critical dependency",
  EVIDENCE::"lockfile present⊕audit-scan clean∨triaged⊕license∧maintenance check on new deps",
  FAILURE::"supply-chain compromise⊕unpatched CVE in prod⊕unreproducible build"
]
D08_PERF::[
  INVARIANT::"hot paths bounded⊕no N+1∨unbounded query⊕resource limits set⊕graceful degradation under load",
  EVIDENCE::"load test at expected peak⊕query-plan review on hot paths⊕timeout∧connection-pool limits",
  FAILURE::"latency collapse under load⊕resource exhaustion⊕cascading timeout"
]
D09_ERROR::[
  INVARIANT::"errors caught at boundaries⊕fail-closed on critical paths⊕no swallowed exception⊕retries bounded with backoff",
  EVIDENCE::"error-path test⊕fail-closed assertion on critical handler⊕bounded-retry config // observability: alert fires on critical-error-rate breach",
  FAILURE::"silent failure⊕unbounded retry storm⊕fail-open on a path that must fail-closed"
]
D10_LOGGING::[
  INVARIANT::"critical paths emit structured telemetry⊕logs free of secrets∧PII⊕alerting wired on critical signals⊕traceable request lineage",
  EVIDENCE::"structured-log assertion on critical paths⊕no-secret-in-log scan⊕alert rule on critical metric // observability: telemetry∧alerting coverage on every critical path",
  FAILURE::"blind production incident⊕secret leak via logs⊕no alert on outage"
]
D11_ACCESS::[
  INVARIANT::"authorization enforces least-privilege⊕no IDOR⊕admin∧mutation surfaces gated⊕deny-by-default",
  EVIDENCE::"authz test per role⊕IDOR probe on resource access⊕deny-by-default confirmed",
  FAILURE::"horizontal∨vertical privilege escalation⊕unauthorized data access⊕open admin surface"
]
D12_DATA::[
  INVARIANT::"backups taken⊕restore tested⊕retention∧deletion honored⊕integrity verifiable⊕PII handled per policy",
  EVIDENCE::"backup schedule⊕restore-drill evidence⊕integrity checksum⊕retention policy enforced // disaster-recovery: tested restore-from-backup within target RTO∧RPO",
  FAILURE::"unrecoverable data loss⊕untested backup that fails on restore⊕retention∨privacy violation"
]
DOMAIN_RULE::"A domain PASSES only when its EVIDENCE is produced. Absent evidence on a critical path → BLOCKING. Absent evidence off critical path → ADVISORY with explicit risk note."
§3::GOVERNANCE
MUST_ALWAYS::[
  sweep_all_12_domains_in_order,
  state_invariant_evidence_and_failure_mode_per_domain,
  require_evidence_before_passing_a_domain,
  fold_observability_into_LOGGING_and_ERROR,
  fold_disaster_recovery_and_runbook_into_STATE_and_DATA,
  classify_missing_evidence_on_critical_path_as_BLOCKING
]
MUST_NEVER::[
  pass_a_domain_on_assertion_without_evidence,
  skip_a_domain_silently,
  create_standalone_observability_or_disaster_recovery_skill,
  downgrade_a_critical_path_gap_to_advisory_without_risk_note,
  reorder_the_sweep_to_avoid_a_failing_domain
]
ESCALATION::"critical_engineer<when_critical_path_invariant_unproven⊕data_loss_risk⊕fail_open_on_must_fail_closed_path>"
§4::EXAMPLES
DOMAIN_FINDING::[
  DOMAIN::D09_ERROR,
  INVARIANT::"fail-closed on critical payment-capture path",
  EVIDENCE_FOUND::"none — handler catches and returns success on downstream timeout",
  FAILURE_MODE::"fail-open: payment marked captured while gateway never confirmed",
  VERDICT::BLOCKING,
  FIX::"on downstream timeout, mark PENDING and surface for reconciliation; assert via error-path test that timeout never yields CAPTURED"
]
OBSERVABILITY_ABSORPTION::"telemetry∧alerting are NOT a separate sweep — they are the EVIDENCE clause of D10_LOGGING and the alert clause of D09_ERROR. A path with no alert on critical-error-rate fails D09⊕D10, not a phantom observability skill."
DISASTER_RECOVERY_ABSORPTION::"restore-drill∧RTO∧RPO are the EVIDENCE clause of D12_DATA; mid-operation recovery is the EVIDENCE clause of D05_STATE. Runbook validation is the documented-recovery-procedure evidence in D05∧D12, not a phantom disaster-recovery skill."
EDGE_CASE::"A read-only reporting service legitimately has no D03_DB transaction invariant and no D12_DATA backup-of-derived-data invariant — mark NOT_APPLICABLE with reason, never silently skip."
§5::ANCHOR_KERNEL
TARGET::evidence_gated_12_domain_production_readiness_invariant_sweep
NEVER::[
  pass_domain_without_evidence,
  skip_domain_silently,
  split_observability_or_disaster_recovery_into_standalone_skill,
  downgrade_critical_path_gap_without_risk_note,
  reorder_sweep_to_dodge_failure
]
MUST::[
  sweep_AUTH→SECRETS→DB→API→STATE→CONFIG→DEPS→PERF→ERROR→LOGGING→ACCESS→DATA,
  state_invariant⊕evidence⊕failure_per_domain,
  require_evidence_to_pass,
  fold_observability_into_LOGGING⊕ERROR,
  fold_disaster_recovery_into_STATE⊕DATA,
  BLOCK_on_unproven_critical_path_invariant
]
GATE::"Has every applicable domain produced the evidence that proves its invariant holds in production?"
===END===
