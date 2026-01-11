===PATTERN:MIP_BUILD===
META:
  TYPE::PATTERN
  VERSION::"1.0"
  PURPOSE::"Minimal Intervention for preventing accumulative code complexity"
  SOURCE::"Extracted from build-philosophy.oct.md"

§1::CORE_PRINCIPLE
MINIMAL_INTERVENTION_PRINCIPLE::[
  ESSENTIAL_COMPLEXITY::"Code that directly serves user value with measurable outcomes",
  ACCUMULATIVE_COMPLEXITY::"Code adding maintenance burden without proportional user value",
  DECISION_QUESTION::"Could we achieve same outcome with simpler means?",
  SIMPLIFICATION_PROCESS::"Remove components until UX degrades → identify break point → restore last essential → minimal achieved"
]

§2::ENFORCEMENT_FRAMEWORK
MIP_ENFORCEMENT::[
  MANDATORY_ARTIFACTS::[
    MINIMALITY_JUSTIFICATION::"User problem solved? Why not extend existing? Simplification test result?",
    REMOVAL_TEST_EVIDENCE::"What removed? Break point identified? Minimal restoration performed?",
    REVIEWER_SIGNOFF::"code-review-specialist MUST verify: minimality credible, removal test genuine, no obvious bloat"
  ],
  AUTHORITY_CHAIN::"implementation-lead[RESPONSIBLE] → code-review-specialist[ACCOUNTABLE] → critical-engineer[BLOCKING if insufficient]"
]

§3::DECISION_GATES
SIMPLIFICATION_TESTS::[
  FEATURES::"Directly solve user problem? Users notice removal? Users care?",
  ABSTRACTIONS::"Pattern repeated 3+? Reduces cognitive load? Understandable without docs?",
  OPTIMIZATIONS::"Measured bottleneck? Profiled first? Complexity cost justified?"
]

§4::RED_FLAGS
REJECT_IF::[
  "Generic justifications: 'might need later', 'best practice', 'cleaner'",
  "No removal test performed",
  "Abstraction without 3+ use sites",
  "Nice-to-have without user demand"
]

§5::EXAMPLE
RIPPLE_MAP::"processUser(id)→processUser(user): DIRECT[10 files], INDIRECT[tests+API+cache], FLOW[db queries+N+1 risk] = 20 files + performance testing + staged migration for 'simple' change"

§6::USED_BY
AGENTS::[implementation-lead, completion-architect, code-review-specialist]
CONTEXT::"Feature implementation, refactoring decisions, code review gates"

===END===
