===SKILL:CLARIFICATION_GATE===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Ambiguity detection and resolution protocol before implementation"

§1::GATE_TRIGGER
CONDITION::"Apply when ANY of the following are unclear in the build plan"

§2::AMBIGUITY_DETECTION
SIGNALS::[
  PRIORITY_CONFLICTS::"Multiple tasks could be started - which first?",
  DEPENDENCY_CHOICES::"Task specifies options without clear selection",
  INTEGRATION_UNCLEAR::"How should component X connect to existing system Y?",
  TEST_STRATEGY_GAPS::"What testing approach for this specific functionality?",
  SCOPE_BOUNDARIES::"Is edge case X in scope for this task?"
]

§3::PROTOCOL
EXECUTION::[
  1::SCAN::"Review assigned tasks for ambiguities before starting",
  2::IF_AMBIGUOUS::"List specific questions -> WAIT for clarification -> DOCUMENT decision",
  3::IF_CLEAR::"Proceed with implementation"
]

===END===
