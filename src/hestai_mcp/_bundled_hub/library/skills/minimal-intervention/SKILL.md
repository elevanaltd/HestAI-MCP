===SKILL:MINIMAL_INTERVENTION===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Philosophy for preventing architectural over-engineering"

§1::CORE_PRINCIPLES
PRINCIPLES::[
  ESSENTIAL_ARCHITECTURE::"Structure that directly enables system goals - user-facing capabilities",
  ACCUMULATIVE_ARCHITECTURE::"Layers that add complexity without measurable user benefit",
  SIMPLIFICATION_TEST::"Remove architectural components until functionality breaks, restore last essential layer",
  DAEDALIAN_PATH::"Between over-architecting (labyrinth) and under-architecting (chaos) lies elegant sufficiency"
]

§2::DECISION_FRAMEWORK
FRAMEWORK::[
  BEFORE_ADDING_LAYER::"What capability does this layer enable? Can existing layers be extended?",
  BEFORE_ABSTRACTIONS::"Is this abstraction hiding essential complexity or accidental complexity?",
  BEFORE_PATTERNS::"Does this pattern solve a real problem or just look professional?",
  BEFORE_SCALING::"Is this a measured constraint? Profile then scale",
  QUALITY_GATE::"Does this architecture make the system more essential or more accumulative?"
]

===END===
