===SKILL:DEBATE_ORCHESTRATION===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Wind/Wall/Door multi-perspective debate orchestration"

§1::CORE_PATTERN
TRIAD::[
  WIND::PATHOS["What if..." | Expansive | Visionary],
  WALL::ETHOS["Yes, but..." | Grounding | Critical],
  DOOR::LOGOS["Therefore..." | Synthesizing | Decisive]
]
DYNAMIC::WIND ⇌ WALL → DOOR [Tension produces Emergence]

§2::MODES
FIXED::"WIND → WALL → DOOR → Repeat (Structured decisions)"
MEDIATED::"Dynamic speaker selection (Complex deadlock resolution)"

§3::PATTERNS
FLASH_DEBATE::"Quick 3-turn decision cycle (Init → Wind → Wall → Door → Close)"
SOCRATIC::"Premise clarification (Questions only) before positions"
MULTI_MODEL::"Claude(Wind) + GPT(Wall) + Gemini(Door) cognitive optimization"

§4::MCP_TOOLS
TOOLS::[
  init_debate,
  add_turn,
  get_debate,
  close_debate,
  force_close_debate
]

===END===
