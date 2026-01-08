===SKILL:INTEGRITY_DEFENSE===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Methodology for defending test integrity against manipulation"

§1::DETECTION_PROTOCOL
TRIGGER_PHRASES::[
  "workaround", "let me fix the test", "run a simpler test",
  "try a simpler fix", "adjust the expectation", "make the test pass",
  "skip this test", "comment out", "lower the bar"
]

§2::INTERVENTION_PROTOCOL
STEPS::[
  DETECT::"Pattern matching on trigger phrases and anti-pattern recognition",
  HALT::"Immediate blocking authority - stop development",
  ANALYZE::"Evidence-based assessment of integrity violation",
  EDUCATE::"Principle-based teaching on why manipulation fails",
  REDIRECT::"Concrete guidance on proper TDD approaches"
]

§3::ANTI_PATTERNS
VIOLATIONS::[
  "Modifying assertions to match broken code",
  "Reducing coverage to avoid failures",
  "Adding workarounds instead of fixes",
  "Commenting failing tests",
  "Lowering quality thresholds"
]

===END===
