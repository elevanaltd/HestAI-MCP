===SKILL:DRIFT_DETECTION===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Early warning system for requirements and process drift"

§1::REQUIREMENTS_DRIFT
SIGNALS::[
  FEATURE_ADDITION_WITHOUT_NORTH_STAR_REFERENCE::{INDICATOR:"New functionality proposed without traceability", RESPONSE:"North Star validation demand"},
  SCOPE_BOUNDARY_BLUR::{INDICATOR:"Adjacent problems being solved without approval", RESPONSE:"Boundary enforcement"},
  COMPLEXITY_INCREASE::{INDICATOR:"Architecture growing beyond simplicity principles", RESPONSE:"Completion-through-subtraction"},
  CREATIVE_REPLACEMENT::{INDICATOR:"'Better' ideas overriding requirements", RESPONSE:"Requirements primacy enforcement"}
]

§2::PROCESS_DRIFT
SIGNALS::[
  VALIDATION_SKIP_ATTEMPTS::{INDICATOR:"Suggestions to bypass checkpoints", RESPONSE:"Process discipline enforcement"},
  STRATEGY_ABANDONMENT::{INDICATOR:"Abandoning planned approaches (e.g. UI-First)", RESPONSE:"Strategy restoration"},
  AD_HOC_WORKFLOW::{INDICATOR:"Custom workflows replacing documented ones", RESPONSE:"Process consolidation"},
  PHASE_JUMP_RATIONALIZATION::{INDICATOR:"Skipping phases without completion", RESPONSE:"Accountability checkpoint"}
]

§3::INTERVENTION_STRATEGY
STRATEGIES::[
  PREEMPTIVE::"Challenge deviations at first signal",
  PROPHETIC::"Predict drift trajectories",
  CORRECTIVE::"Issue specific return-to-documented-approach directives",
  ESCALATORY::"Elevate repeated patterns to human judgment"
]

===END===
