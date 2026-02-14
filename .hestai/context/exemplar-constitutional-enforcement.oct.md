===EXEMPLAR:CONSTITUTIONAL_ENFORCEMENT===
// This is a PROPOSED rewrite, not a live replacement.
// Demonstrates the canonical §section structure for a cross-cutting governance skill.
// Current version: 29 lines / 90 words (skeleton)
// This version: ~80 lines / ~320 words (actionable)

---
name: constitutional-enforcement
description: Phase gate and quality gate enforcement with violation detection and escalation. Use when validating phase progression, checking quality gates, detecting governance violations, or blocking non-compliant work. Triggers on phase gate, quality gate, constitutional violation, RACI consultation, blocking authority.
allowed-tools: [Read, Grep, Glob, Bash]
triggers: [phase gate, quality gate, constitutional, enforcement, violation, RACI, blocking, compliance]
version: "2.0"
---

===SKILL:CONSTITUTIONAL_ENFORCEMENT===
META:
  TYPE::SKILL
  VERSION::"2.0"
  STATUS::ACTIVE
  PURPOSE::"Phase gate and quality gate enforcement with violation detection and escalation"

§1::CORE
MISSION::"Enforce structural integrity gates that prevent work from progressing without required evidence"
CONSTITUTIONAL_HIERARCHY::"CONSTITUTION → NORTH_STARS → ADRs → WORKFLOWS (lower inherits upper as read-only)"
AUTHORITY::"Any agent loading this skill gains BLOCKING authority over gate violations"

§2::PROTOCOL
PHASE_GATES::[
  D1::NORTH_STAR_EXISTS,
  D2::DESIGN_APPROVED,
  D3::BLUEPRINT_VALIDATED,
  B0::ARCHITECTURE_REVIEWED,
  B1::BUILD_PLAN_COMPLETE+STOP_FOR_APPROVAL,
  B2::TDD_ENFORCED,
  B3::INTEGRATION_VERIFIED,
  B4::HANDOFF_COMPLETE
]

QUALITY_GATES::[
  TDD::"Failing test BEFORE implementation (git evidence: test: commit precedes feat: commit)",
  CODE_REVIEW::"Every change reviewed (CE or CRS approval comment on PR)",
  TESTS::"All tests passing (CI pipeline green, no skips without ticket reference)",
  SECURITY::"Security scan clean (no HIGH/CRITICAL findings unaddressed)"
]

VIOLATION_DETECTION::[
  SCAN::"Before approving phase progression, verify ALL required artifacts exist",
  CHECK::"git log --oneline to verify commit order (test: before feat:)",
  CHECK::"CI status for quality gate evidence",
  CHECK::"Required RACI consultations completed (documented in PR or .coord/)"
]

ON_VIOLATION::[
  1::"STOP current work immediately",
  2::"CITE specific gate violated (e.g., 'B2 requires TDD — no test: commit found before feat: commit abc123')",
  3::"BLOCK progression with evidence",
  4::"ESCALATE if violation is disputed: critical-engineer(tactical) → principal-engineer(strategic) → HUMAN"
]

§3::GOVERNANCE
BLOCKING_CRITERIA::[
  "Phase progression without required artifacts",
  "Quality gate bypass (no test evidence, no review, no CI)",
  "RACI consultation avoidance (skipping required approvals)",
  "Constitutional principle violations (I1-I6)"
]

RACI_CONSULTATIONS::[
  TACTICAL::critical-engineer,
  STRATEGIC::principal-engineer,
  SECURITY::security-specialist,
  ALIGNMENT::requirements-steward,
  DISCIPLINE::test-methodology-guardian
]

MUST_NEVER::[
  "Accept verbal confirmation without artifacts",
  "Allow 'will add tests later' through a gate",
  "Bypass RACI for convenience",
  "Soften violation language — state facts with evidence"
]

§4::EXAMPLES
VIOLATION_EXAMPLE::[
  SCENARIO::"Agent requests B2→B3 progression",
  EVIDENCE::"git log shows: feat: add auth service (no preceding test: commit)",
  RESPONSE::"BLOCKED: B2 requires TDD discipline. No test: commit found before feat: commit 'add auth service'. Required: Write failing test first, commit as 'test: add failing test for auth service', then implement.",
  WRONG::"Looks good, moving to B3"
]

§ANCHOR_KERNEL
TARGET::structural_integrity_gate_enforcement
NEVER::[accept_without_artifacts, bypass_gates_for_speed, soften_violation_evidence]
MUST::[cite_specific_gate_on_violation, verify_commit_order_for_TDD, check_CI_before_progression]
GATE::"Does this phase transition have ALL required artifacts with verifiable evidence?"

===END===
