===SPECIFICATION===
META:
  TITLE::"Odyssean Anchor Protocol v5.0"
  TYPE::PROTOCOL_SPEC
  STATUS::DRAFT
  AUTHOR::holistic-orchestrator
  DATE::2026-01-05
  PURPOSE::"Define the staged (multi-turn) binding handshake for agent identity, governance injection, and tool gating"

CONCEPT::[
  "Odyssean Anchor is a **state transition protocol** (LOBBY→BOUND), not a single-shot validator.",
  "Agents are treated as stateless; continuity is enforced by **server-persisted state + a session_token**.",
  "Governance + role constitution must be loaded **before** any privileged work permit is granted.",
  "Tool gating is enforced by on-disk state: pending has no permit; active with anchor.json has permit.",
  "session_token is the session identifier: session_id == token == directory_name"
]

DECISIONS::[
  TOOL_SURFACE::"Single staged tool: anchor(stage=...) (may be implemented as odyssean_anchor internally; avoid competing contracts)",
  CANONICAL_KNOBS::[
    mode::[full|lite|untracked],
    strictness::[quick|default|deep]
  ],
  PERSISTENCE_RULE::"For mode in [full,lite], Stage 1 MUST persist pending handshake state under .hestai/sessions/ (restart-safe).",
  PROMOTION_RULE::"Stage 3 promotes by atomic rename/move: pending/{token} → active/{token} (no half-active sessions).",
  UNTRACKED_RULE::"mode=untracked MUST NOT write session state and MUST NOT unlock write tools."
]

MODELS::[
  full::[
    PURPOSE::"Production work, critical changes, architectural decisions",
    SESSION::"Persisted: pending→active promotion",
    GIT_TRACKING::true,
    WRITE_TOOLS::unlockable,
    FLOW::"3-stage: identity→context→proof (agent provides tensions)"
  ],
  express::[
    PURPOSE::"Fast tracked binding when role defaults suffice",
    SESSION::"Persisted: pending→active promotion",
    GIT_TRACKING::true,
    WRITE_TOOLS::unlockable,
    FLOW::"2-stage: identity→auto-proof (server generates tensions from role defaults)"
  ],
  lite::[
    PURPOSE::"Quick queries and minor work (still tracked)",
    SESSION::"Persisted: pending→active promotion",
    GIT_TRACKING::true,
    WRITE_TOOLS::unlockable,
    FLOW::"3-stage with quick strictness"
  ],
  untracked::[
    PURPOSE::"One-off questions and capability checks",
    SESSION::"No disk session",
    GIT_TRACKING::false,
    WRITE_TOOLS::locked,
    FLOW::"No stages - read-only context access only"
  ]
]

STRICTNESS::[
  quick::"Minimum tensions = 1",
  default::"Minimum tensions = 2",
  deep::"Minimum tensions = 3 (and CTX line ranges required)"
]

PROTOCOL_FLOW::[
  STATE_MACHINE::[LOBBY → IDENTITY → CONTEXT → BOUND],

  STAGE_1_IDENTITY::[
    ACTOR::Agent (or User via Proxy)
    ACTION::`anchor(stage="identity", role="{role}", working_dir="{cwd}", mode="{mode}", strictness="{strictness}", topic="{topic}")`
    TOOL_LOGIC::[
      "Ensure .hestai-sys governance is injected/available for {working_dir}",
      "Load role constitution from .hestai-sys/agents/{role}.oct.md",
      "If mode in [full,lite]: create .hestai/sessions/pending/{token}/handshake.json",
      "Return: session_token + constitution_path (+ optional excerpt) + template for next payload"
    ]
    TRANSITION::LOBBY → IDENTITY
  ],

  STAGE_2_CONTEXT::[
    ACTOR::Agent
    ACTION::`anchor(stage="context", token="{token}", working_dir="{cwd}", payload="{PARTIAL_IDENTITY_BLOCK}")`
    TOOL_LOGIC::[
      "Validate token exists (tracked modes) and handshake.stage==IDENTITY",
      "Validate BIND section against schema (agent proves it read constitution)",
      "Compute server-authoritative ARM (phase/branch/files/focus/context_hash)",
      "Persist ARM into pending/{token}/handshake.json and advance handshake.stage=CONTEXT",
      "Return: SERVER_ARM + template for proof payload"
    ]
    TRANSITION::IDENTITY → CONTEXT
  ],

  STAGE_3_PROOF::[
    ACTOR::Agent
    ACTION::`anchor(stage="proof", token="{token}", working_dir="{cwd}", payload="{PROOF_BLOCK}")`
    TOOL_LOGIC::[
      "Validate token exists and handshake.stage==CONTEXT (tracked modes)",
      "Validate proof: TENSIONS (strictness) + COMMIT (artifact+gate) against server ARM",
      "Write anchor.json under pending/{token}, then promote via atomic rename: pending/{token} → active/{token}",
      "Return: canonical anchor + WORK_PERMIT"
    ]
    TRANSITION::CONTEXT → BOUND
  ]
]

DATA_STRUCTURES::[
  SESSION_TOKEN::[
    "Opaque identifier returned by Stage 1.",
    "For tracked modes, token is the session_id and the directory name: .hestai/sessions/{pending|active}/{token}/"
  ],
  HANDSHAKE_FILE::[
    "Path: .hestai/sessions/pending/{token}/handshake.json",
    "Contains: role, working_dir, mode, strictness, topic, stage, timestamps, constitution_path, server_arm"
  ],
  PARTIAL_IDENTITY_BLOCK::[
    "Standard OCTAVE identity block containing only BIND section.",
    "Proves agent extracted identity from the constitution."
  ],
  PROOF_BLOCK::[
    "Standard OCTAVE identity block containing TENSIONS + COMMIT.",
    "ARM is server-authoritative; agent must not fabricate it."
  ]
]

TOOL_GATING::[
  RULE::"Privileged work tools must remain locked until anchor.json exists under .hestai/sessions/active/{token}/.",
  PENDING::"Stages 1/2 create pending state only; no active/{token}/anchor.json ⇒ locked.",
  ACTIVE::"Stage 3 promotion creates active/{token}/ with anchor.json ⇒ unlocked.",
  ATOMICITY::"Promotion is an atomic move to prevent half-written active sessions."
]

UX_IMPROVEMENTS::[
  "Self-Guiding": "Tool returns next_step instructions + templates in every response.",
  "Platform Agnostic": "Works in any CLI that supports MCP tool use.",
  "No Pre-Knowledge": "Agent doesn't need to know schema; tool provides canonical templates."
]

===END===
