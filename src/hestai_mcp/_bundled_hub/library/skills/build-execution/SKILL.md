===SKILL:BUILD_EXECUTION===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Core philosophy and discipline for systematic build execution"

§1::PHILOSOPHY
BUILD_PHILOSOPHY::[
  SYSTEM_AWARENESS::"Every code change ripples through system - map impact before coding",
  MINIMAL_CODE::"Essential complexity serves users, accumulative complexity serves maintenance burden",
  TEST_FIRST::"RED (failing test) → GREEN (minimal code) → REFACTOR (essential simplification)",
  EVIDENCE_BASED::"Claims require reproducible artifacts - no validation theater"
]

§2::TDD_DISCIPLINE
PROTOCOL::[
  STEP_1::"Write failing test demonstrating missing behavior (RED)",
  STEP_2::"Verify test fails for expected reason",
  STEP_3::"Write minimal code to pass test (GREEN)",
  STEP_4::"Refactor for clarity and pattern consistency (REFACTOR)",
  STEP_5::"Verify all quality gates pass"
]

§3::ANTI_PATTERNS
AVOID::[
  ISOLATED_EDITS::"Changing code without system impact analysis",
  FEATURE_BLOAT::"Adding unrequested functionality 'while I'm here'",
  CONTEXT_DESTRUCTION::"Removing comments or structure that explains 'why'",
  PREMATURE_OPTIMIZATION::"Optimizing before measuring or requiring"
]

===END===
