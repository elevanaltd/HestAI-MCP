===SPECIFICATION===
META:
  TITLE::"Odyssean Anchor Protocol v5.0"
  TYPE::PROTOCOL_SPEC
  STATUS::DRAFT
  AUTHOR::holistic-orchestrator
  DATE::2026-01-04
  PURPOSE::"Define the interactive binding protocol for agent identity and session initiation"

CONCEPT::[
  "The Odyssean Anchor is not just a validation tool; it is the **State Transition Protocol**.",
  "It guides an agent from the LOBBY (unbound) to BOUND state through an interactive dialogue.",
  "It removes reliance on platform-specific command files (~/.claude/commands) by embedding the protocol in the tool itself."
]

TIERS::[
  FULL::[
    PURPOSE::"Production work, critical changes, architectural decisions",
    REQ::[Strict_Constitution_Read, Full_Session_Creation, Deep_Context_Injection, Tension_Validation],
    STATE::"Persisted Session + Git Tracking"
  ],
  LITE::[
    PURPOSE::"Quick queries, minor tasks, status checks",
    REQ::[Streamlined_Identity, Fast_Session_Creation, Lite_Context, Minimal_Validation],
    STATE::"Persisted Session + Git Tracking"
  ],
  UNTRACKED::[
    PURPOSE::"One-off questions, dry-runs, capability checks",
    REQ::[Identity_Check, No_Session_Disk_Write, No_Git_Tracking],
    STATE::"Ephemeral (Memory Only)"
  ]
]

PROTOCOL_FLOW::[
  STATE_MACHINE::[LOBBY → IDENTIFYING → CONTEXTUALIZING → BOUND],

  STEP_1_INITIATION::[
    ACTOR::Agent (or User via Proxy)
    ACTION::`odyssean_anchor(stage="init", role="{role}", tier="{tier}", topic="{topic}")`
    TOOL_RESPONSE::[
      "Retrieves constitution from .hestai-sys/agents/{role}.oct.md",
      "Returns: CONSTITUTION_TEXT + INSTRUCTION('Extract Core Identity')"
    ]
    TRANSITION::LOBBY → IDENTIFYING
  ],

  STEP_2_IDENTITY_COMMIT::[
    ACTOR::Agent
    ACTION::`odyssean_anchor(stage="commit_identity", payload="{PARTIAL_IDENTITY_BLOCK}")`
    PAYLOAD_FORMAT::[
      "===IDENTITY===",
      "BIND:",
      "  ROLE::{role}",
      "  COGNITION::{cognition}",
      "  ARCHETYPES::{archetypes}",
      "  AUTHORITY::{authority}",
      "===END==="
    ]
    TOOL_LOGIC::[
      "Validates BIND section against schema",
      "Creates Session (Clock In) [if FULL/LITE]",
      "Computes Context (ARM) [if FULL/LITE]",
      "Returns: ARM_CONTEXT + INSTRUCTION('Bind Identity to Context')"
    ]
    TRANSITION::IDENTIFYING → CONTEXTUALIZING
  ],

  STEP_3_BINDING_PROOF::[
    ACTOR::Agent
    ACTION::`odyssean_anchor(stage="bind", payload="{FULL_IDENTITY_BLOCK}")`
    PAYLOAD_FORMAT::[
      "===IDENTITY===",
      "BIND::{...}",
      "ARM::{injected_by_server}",
      "TENSIONS::{...}",
      "COMMIT::{...}",
      "===END==="
    ]
    TOOL_LOGIC::[
      "Validates full schema (BIND+ARM+TENSIONS+COMMIT)",
      "Validates Tensions against ARM Context",
      "Validates Commit contract",
      "Persists Anchor State [if FULL/LITE]",
      "Returns: SUCCESS + WORK_PERMIT"
    ]
    TRANSITION::CONTEXTUALIZING → BOUND
  ]
]

DATA_STRUCTURES::[
  PARTIAL_IDENTITY_BLOCK::[
    "Standard OCTAVE block containing only BIND section.",
    "Proves agent read the constitution and extracted identity."
  ],
  ARM_CONTEXT::[
    "Server-injected reality (OCTAVE ARM section).",
    "FULL: Phase + Branch + Files + Hash + Skills + Blockers",
    "LITE: Phase + Branch + Files",
    "UNTRACKED: Phase only"
  ],
  FULL_IDENTITY_BLOCK::[
    "The final cryptographic identity structure (Identity Schema v5.0).",
    "Combines Agent Identity (BIND) + Server Reality (ARM) + Cognitive Tensions."
  ]
]

UX_IMPROVEMENTS::[
  "Self-Guiding": "Tool returns next_step instructions in every response.",
  "Platform Agnostic": "Works in any CLI that supports tool use.",
  "No Pre-Knowledge": "Agent doesn't need to know the schema beforehand; tool provides templates."
]

===END===
