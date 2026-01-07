===SKILL:REVIEW_DISCIPLINE===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Methodology for evidence-based code review and confidence categorization"

§1::CONFIDENCE_CATEGORIZATION
CATEGORIES::[
  CERTAIN::[
    DEFINITION::"Can point to exact failure mode with concrete evidence",
    EVIDENCE::"Line number + reproduction steps + failure scenario",
    REPORT::ALWAYS
  ],
  HIGH::[
    DEFINITION::"Strong evidence with minimal doubt",
    EVIDENCE::"Line number + reasoning + likely impact",
    REPORT::ALWAYS
  ],
  MODERATE::[
    DEFINITION::"Likely issue but context-dependent",
    EVIDENCE::"Line number + concern + conditions",
    REPORT::ONLY_IF_CRITICAL
  ],
  SPECULATIVE::[
    DEFINITION::"Worth noting but might be false positive",
    EVIDENCE::"Line number + observation",
    REPORT::NEVER_UNLESS_REQUESTED
  ]
]

§2::ANTI_THEATER_GATE
PROTOCOL::[
  CATEGORIZE::"Which confidence level does this fall into?",
  EVIDENCE_CHECK::"Do I have the required evidence for this category?",
  THRESHOLD_CHECK::"Does this meet reporting threshold (High/Certain)?",
  FILTER::"Omit if below threshold"
]

§3::REVIEW_METHODOLOGY
SCAN_DEPTH::[SURFACE→STRUCTURE→PATTERNS→IMPLICATIONS→FUTURES]
SYNTHESIS_ENGINE::[
  IDENTIFY_PURPOSE→UNDERSTAND_INTENT,
  SYSTEMATIC_SCAN→MULTI_DIMENSIONAL_ANALYSIS,
  PRIORITIZE_SEVERITY→RISK_BASED_ORDERING,
  SYNTHESIZE_RECOMMENDATIONS→INTEGRATED_GUIDANCE
]

===END===
