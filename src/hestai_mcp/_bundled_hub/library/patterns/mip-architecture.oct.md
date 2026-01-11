===PATTERN:MIP_ARCHITECTURE===
META:
  TYPE::PATTERN
  VERSION::"1.0"
  PURPOSE::"Minimal Intervention for preventing architectural over-engineering"
  REPLACES::"Part of original minimal-intervention skill"

§1::CORE_PRINCIPLE
ARCHITECTURAL_MIP::[
  ESSENTIAL_ARCHITECTURE::"Structure that directly enables system goals - user-facing capabilities",
  ACCUMULATIVE_ARCHITECTURE::"Layers that add complexity without measurable user benefit",
  SIMPLIFICATION_TEST::"Remove architectural components until functionality breaks, restore last essential layer",
  DAEDALIAN_PATH::"Between over-architecting (labyrinth) and under-architecting (chaos) lies elegant sufficiency"
]

§2::DECISION_FRAMEWORK
BEFORE_ADDING_LAYER::"What capability does this layer enable? Can existing layers be extended?"
BEFORE_ABSTRACTIONS::"Is this abstraction hiding essential complexity or accidental complexity?"
BEFORE_PATTERNS::"Does this pattern solve a real problem or just look professional?"
BEFORE_SCALING::"Is this a measured constraint? Profile then scale"
QUALITY_GATE::"Does this architecture make the system more essential or more accumulative?"

§3::USED_BY
AGENTS::[technical-architect, design-architect, critical-engineer]
CONTEXT::"System design, architectural decisions, infrastructure planning"

===END===
