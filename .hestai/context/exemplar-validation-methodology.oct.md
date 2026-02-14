===EXEMPLAR:VALIDATION_METHODOLOGY===
// This is a PROPOSED rewrite, not a live replacement.
// Demonstrates the canonical §section structure for a domain-specific skill.
// Current version: 34 lines / 126 words (skeleton)
// This version: ~90 lines / ~370 words (actionable)

---
name: validation-methodology
description: 6-step reality enforcement protocol for production readiness assessment. Use when validating proposals, assessing production readiness, classifying constraints, or delivering GO/BLOCKED/CONDITIONAL verdicts. Triggers on validation, production readiness, constraint classification, feasibility assessment, reality check.
allowed-tools: [Read, Grep, Glob, Bash]
triggers: [validation, production readiness, constraint, feasibility, reality check, verdict, GO BLOCKED, hard constraint, soft constraint]
version: "2.0"
---

===SKILL:VALIDATION_METHODOLOGY===
META:
  TYPE::SKILL
  VERSION::"2.0"
  STATUS::ACTIVE
  PURPOSE::"6-step reality enforcement protocol with constraint classification and verdict delivery"

§1::CORE
MISSION::"Enforce reality over optimism through systematic evidence-based validation"
VERDICT_TYPES::[GO, BLOCKED, CONDITIONAL, INSUFFICIENT_DATA]
CONSTRAINT_TYPES::[
  HARD::"Non-negotiable — physics, security, compliance, immutable requirements. Cannot be traded.",
  SOFT::"Tradeable — quality vs speed, scope boundaries, approach preferences. Can be negotiated with evidence.",
  FANTASY::"Claims violating hard constraints or assumptions without evidence. Must be replaced with data."
]

§2::PROTOCOL
VALIDATION_SEQUENCE::[
  1_NATURAL_LAW::"Identify physics constraints, information theory bounds, mathematical limits. Example: 'Real-time sync across continents' → speed of light = 130ms minimum RTT.",
  2_RESOURCE_REALITY::"Inventory ACTUAL available resources with evidence. People (who, availability), tools (licensed, configured), budget (approved, remaining), time (calendar days minus holidays/meetings).",
  3_CAPABILITY_ASSESSMENT::"Validate team skills and tool readiness against requirements. Gap = BLOCKED or CONDITIONAL with mitigation plan.",
  4_TIMELINE_ANALYSIS::"Calculate critical path. Apply LLM acceleration factor (10-20x for AI-assisted tasks). Add risk buffers (1.5x for known-unknowns, 3x for unknown-unknowns).",
  5_EVIDENCE_VERIFICATION::"Confirm ALL claims with artifacts, measurements, or reproducible data. 'Works on my machine' → show CI pipeline. 'Handles load' → show load test report.",
  6_VERDICT_DELIVERY::"State verdict with unfiltered evidence. No hedging. No softening."
]

§3::GOVERNANCE
VERDICT_DECISION_TREE::[
  ANY_HARD_CONSTRAINT_VIOLATED::"→ BLOCKED (cite specific constraint + evidence)",
  ALL_HARD_MET_BUT_SOFT_CONCERNS::"→ CONDITIONAL (list conditions for GO with deadlines)",
  ALL_CONSTRAINTS_MET_WITH_EVIDENCE::"→ GO (cite evidence for each validated constraint)",
  INSUFFICIENT_EVIDENCE::"→ INSUFFICIENT_DATA (list what's missing, who provides it, deadline)"
]

MUST_NEVER::[
  "Accept hope-based assumptions without data",
  "Soften truth for rapport or politics",
  "Speculate when evidence is incomplete — state 'Insufficient Data'",
  "Use hedge language: 'probably', 'should be fine', 'likely works'"
]

OUTPUT_FORMAT::"VERDICT: [GO|BLOCKED|CONDITIONAL] → EVIDENCE: [citations] → CONSTRAINTS: [HARD|SOFT classification] → REASONING: [chain of evidence]"

§4::EXAMPLES
VALIDATION_EXAMPLE::[
  PROPOSAL::"Deploy new auth service to production this sprint",
  STEP_1::"No physics constraints violated",
  STEP_2::"Resources: 1 developer (available 60%), CI pipeline (configured), staging env (ready)",
  STEP_3::"Developer has JWT experience (confirmed via recent PR #189). Gap: no load testing expertise.",
  STEP_4::"Critical path: 3 days implementation + 1 day review + 1 day staging. With LLM assist: ~2 days total. Buffer: 3 days.",
  STEP_5::"Missing: load test report, security scan, rollback procedure documentation.",
  VERDICT::"CONDITIONAL — auth implementation feasible in sprint. Conditions: (1) load test before merge, (2) security scan clean, (3) rollback procedure documented. Deadline: end of sprint."
]

ANTI_EXAMPLE::[
  WRONG::"Looks good, should be fine for this sprint. The team is strong.",
  WHY_WRONG::"Hope-based. No resource inventory, no timeline analysis, no evidence citations, hedge language ('should be fine')."
]

§ANCHOR_KERNEL
TARGET::evidence_based_reality_enforcement
NEVER::[accept_hope_based_assumptions, soften_truth_for_rapport, speculate_without_evidence, use_hedge_language]
MUST::[classify_constraints_HARD_SOFT, cite_evidence_for_every_claim, deliver_verdict_with_reasoning_chain]
GATE::"Is every claim in this proposal backed by an artifact, measurement, or reproducible data?"

===END===
