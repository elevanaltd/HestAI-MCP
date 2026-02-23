===SKILL:RCCAFP===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Root Cause, Corrective Action, and Future Proofing incident management protocol"

§1::PROTOCOL_OVERVIEW
RCCAFP::[
  FULL_NAME::"Root Cause, Corrective Action, and Future Proofing",
  ORIGIN::"Daedalus-era LLM Overreach incident (2025-05-26)",
  SCOPE::"Incident management for multi-agent AI systems with human orchestration oversight",
  PRINCIPLES::[
    "Systematic evidence collection with exact causality chains",
    "Multi-agent constraint validation via ETHOS boundary enforcement",
    "LLM-optimized structure for efficient cross-reference",
    "Prevention-focused learning transforms incidents into architectural improvements",
    "Human authority preservation throughout process"
  ]
]

§2::FIVE_PHASE_PROCESS
PHASES::[
  P1_DETECTION_TRIAGE::[
    ACTION::"Create incident directory YYYYMMDD-[incident-name]",
    STRUCTURE::"01-root-cause/ 02-corrective-action/ 03-future-proof/",
    OUTPUT::"Initial symptom documentation and severity assessment"
  ],
  P2_ROOT_CAUSE::[
    ACTION::"Systematic causality chain analysis with evidence collection",
    VALIDATION::"Cross-validation through multi-agent assessment",
    OUTPUT::"Causality chain documentation with artifacts"
  ],
  P3_CORRECTIVE_ACTION::[
    ACTION::"Immediate containment and mitigation",
    VALIDATION::"ETHOS constraint validation and gap identification",
    OUTPUT::"Process modification documentation and triage execution"
  ],
  P4_FUTURE_PROOFING::[
    ACTION::"Architectural learning extraction and prevention mechanism design",
    VALIDATION::"System improvement evidence synthesis",
    OUTPUT::"Prevention mechanisms and monitoring requirements"
  ],
  P5_CLOSURE::[
    ACTION::"Verification and synthesis gate processing",
    GATE::"Findings pass through synthesis gate before system integration",
    OUTPUT::"Organizational learning documentation and protocol refinement"
  ]
]

§3::INCIDENT_DIRECTORY
TEMPLATE::[
  ROOT::".hestai/state/incidents/YYYYMMDD-[incident-name]/",
  DIRS::[
    "01-root-cause/",
    "02-corrective-action/",
    "03-future-proof/"
  ],
  REQUIRED_FILES::[
    "01-root-cause/causality-chain.md",
    "02-corrective-action/constraint-validations.md",
    "02-corrective-action/triage-execution.md",
    "03-future-proof/prevention-mechanisms.md"
  ]
]

§4::SYNTHESIS_GATE
GATE::[
  PURPOSE::"Controlled integration of incident learnings into system documentation",
  FLOW::"findings → .hestai/state/incidents/pending/ → review → validated integration",
  REQUIREMENT::"All findings must pass synthesis gate before promotion to governance docs",
  ANTI_OVERREACH::[
    "Fixed document structure prevents documentation expansion",
    "Evidence-based requirement limits speculative content",
    "Synthesis gate controls integration of learnings"
  ]
]

§5::AGENT_MAPPING
ROLES::[
  HOLISTIC_ORCHESTRATOR::"Orchestrates RCCAFP process, owns gap accountability",
  CRITICAL_ENGINEER::"Leads root cause investigation (tactical analysis)",
  PRINCIPAL_ENGINEER::"Leads future proofing (strategic prevention)",
  IMPLEMENTATION_LEAD::"Executes corrective action implementations",
  REQUIREMENTS_STEWARD::"Validates learnings against North Star before integration"
]

§6::SUCCESS_METRICS
METRICS::[
  MTTD::"Mean Time to Detection of system boundary violations",
  MTTC::"Mean Time to Containment for incidents",
  COMPLETENESS::"Documentation accuracy and completeness score",
  VALIDATION::"Constraint validation effectiveness",
  RECURRENCE::"Incident recurrence rate for similar failures",
  IMPROVEMENT::"Architecture improvement rate from incident analysis"
]

§7::ANTI_PATTERNS
AVOID::[
  SILENT_FIX::"Fixing incidents without documenting root cause",
  SKIP_SYNTHESIS::"Promoting learnings without synthesis gate review",
  BLAME_CASCADE::"Attributing failures to agents rather than system gaps",
  SPECULATIVE_PREVENTION::"Creating prevention mechanisms without evidence",
  SCOPE_CREEP::"Expanding incident response beyond the specific failure"
]

===END===
