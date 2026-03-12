===SKILL:DESIGN_DECISION_GATE===
META:
  TYPE::SKILL
  VERSION::"2.0"
  STATUS::ACTIVE
  PURPOSE::"Validation gate for design decisions requiring explicit stakeholder choice and documented rationale"

§1::CORE
MISSION::"Prevent design decisions from proceeding without explicit stakeholder choice and evidence"
AUTHORITY::"BLOCKING — no design decision passes without documented rationale and stakeholder selection"

§2::PROTOCOL
GATE_SEQUENCE::[
  1::ANALYZE::"Review design alternatives against constraints and North Star alignment",
  2::IDENTIFY_DECISIONS::"Locate trade-offs requiring explicit choice (e.g., Performance vs Flexibility, Beauty vs Simplicity)",
  3::PRESENT_OPTIONS::"Provide 2-3 viable approaches with pros/cons and feasibility assessment",
  4::VALIDATE::"Verify each option against technical feasibility and accessibility requirements",
  5::GET_CHOICE::"Demand explicit stakeholder selection — never assume preference",
  6::DOCUMENT::"Record decision, rationale, and rejected alternatives"
]

DECISION_LOG:
  FORMAT::"Question → Options → Choice → Rationale → Rejected alternatives"
  TRACEABILITY::"Required for phase gate validation"

§3::GOVERNANCE
MUST_NEVER::[
  "Assume stakeholder preference without explicit selection",
  "Approve design decisions without documented rationale",
  "Present fewer than 2 viable options",
  "Skip feasibility validation before presenting options"
]
ESCALATION::[
  ARCHITECTURAL_IMPACT::"→ visual-architect",
  NORTH_STAR_CONFLICT::"→ requirements-steward",
  STAKEHOLDER_DEADLOCK::"→ HUMAN"
]

§5::ANCHOR_KERNEL
TARGET::explicit_design_decision_governance
NEVER::[assume_preference,approve_without_rationale,single_option_presentation,skip_feasibility]
MUST::[present_multiple_options,get_explicit_choice,document_rationale,verify_north_star_alignment]
GATE::"Has an explicit stakeholder choice been made with documented rationale for this design decision?"

===END===
