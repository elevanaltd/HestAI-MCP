===SKILL:ERROR_TRIAGE===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Systematic error resolution preventing cascade failures"

§1::PRIORITY_MATRIX
LAYERS::[
  1_BUILD::"Compilation/Syntax/Import errors (Must fix first)",
  2_TYPES::"Type mismatches/Interface violations (Cascades)",
  3_UNUSED::"Unused vars/imports (Noise reduction)",
  4_ASYNC::"Async/Await issues (Architectural)",
  5_LOGIC::"Nullish/Truthiness checks (Consistency)",
  6_TESTS::"Unit/Integration failures (Fix last)"
]

§2::TRIAGE_LOOP
CYCLE::[
  EXTRACT::"Get all error categories from CI/Local",
  SORT::"Order by Priority Matrix",
  FIX::"Resolve highest priority category",
  VALIDATE::"Run full validation suite",
  DECISION::"If new errors -> Loop; Else -> Commit"
]

§3::ANTI_PATTERNS
AVOID::[
  WHACK_A_MOLE::"Fixing one by one without priority sorting",
  PARTIAL_FIX::"Ignoring warnings (warnings become errors)",
  BLIND_PUSH::"Pushing to CI without local validation",
  TYPE_SAFETY_THEATER::"Using 'as any' to silence errors without fixing root cause"
]

===END===
