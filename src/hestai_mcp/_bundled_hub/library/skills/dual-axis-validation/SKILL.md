===SKILL:DUAL_AXIS_VALIDATION===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Validation framework for both Requirements (WHAT) and Process (HOW)"

§1::AXIS_1_REQUIREMENTS
DIMENSION::"WHAT we build - North Star alignment"
VALIDATION::"Every feature/component traces to North Star requirements"
DEVIATION_TYPES::[feature_creep, scope_expansion, architecture_inflation, creative_replacement]
ENFORCEMENT::"No implementation without North Star reference"

§2::AXIS_2_PROCESS
DIMENSION::"HOW we build - Documented strategy adherence"
VALIDATION::"Every phase follows documented approach (UI-First, TDD, phase boundaries)"
DEVIATION_TYPES::[phase_skipping, strategy_deviation, validation_bypass, process_improvisation]
ENFORCEMENT::"No deviation without explicit justification and approval"

§3::ACCOUNTABILITY_PROTOCOL
CHECKPOINTS::[
  PHASE_ENTRY::"Validate previous phase completion with North Star alignment evidence",
  STRATEGY_CONFIRMATION::"Verify documented approach being followed",
  NORTH_STAR_CHECK::"Confirm alignment with core vision",
  DEVIATION_REVIEW::"Assess any divergence with justification",
  PHASE_EXIT::"Certify both requirements fidelity AND process adherence"
]

===END===
