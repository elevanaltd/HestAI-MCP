===ODYSSEAN_ANCHOR_TOOL_SPEC===

META:
  TYPE::"IMPLEMENTATION_SPEC"
  ID::"odyssean-anchor-handshake-tool"
  VERSION::"5.0"
  STATUS::DRAFT
  PRIORITY::NOW
  CREATED::"2026-01-05"
  UPDATED::"2026-01-05"
  AUTHOR::"holistic-orchestrator"
  PARENT_PROTOCOL::".hestai-sys/library/specs/odyssean-anchor-protocol-v5.oct.md"
  SCOPE::"Greenfield: canonical contract only (no backwards-compat requirements)"

## PURPOSE

Implement the Odyssean Anchor v5.0 staged handshake as a single MCP tool.

Goals:
- Stage-based binding: identity → context → proof
- Governance injection + role constitution returned before binding progresses
- Server-authoritative ARM
- Durable multi-turn continuity (restart-safe) via on-disk pending state
- session_id == token (single identifier, directory name)
- Tool gating unlocked only after anchor.json exists under active/{token}

## DECISIONS

CANONICAL_TOOL::[
  NAME::"anchor",
  NOTE::"If implementation is initially exposed as 'odyssean_anchor', treat it as an alias and keep the staged handshake contract identical."
]

CANONICAL_KNOBS::[
  mode::[full|lite|untracked],
  strictness::[quick|default|deep]
]

STATE_PERSISTENCE::[
  RULE::"For mode in [full,lite], Stage 1 MUST write pending state under .hestai/sessions/ (no in-memory-only continuity).",
  RULE::"Promotion MUST be atomic (rename/move) to prevent half-written active sessions.",
  RULE::"mode=untracked MUST NOT write session state and MUST NOT unlock write tools."
]

## SPECIFICATION

### Tool Signature

SIGNATURE::
  FUNCTION::anchor
  PARAMS::[
    stage::str[identity|context|proof],
    working_dir::str[Project_root_required_for_governance+git+context],
    role::str[required_for_stage_identity],
    mode::str[full|lite|untracked],
    strictness::str[quick|default|deep],
    topic::str[optional],
    token::str[required_for_stage_context_and_stage_proof_in_tracked_modes],
    payload::str[OCTAVE_blocks_for_identity_and_proof]
  ]
  RETURNS::AnchorHandshakeResult[
    success::bool,
    stage::str,
    token::str|null,
    constitution_path::str|null,
    constitution_excerpt::str|null,
    server_arm::str|null,
    anchor::str|null,
    next_step::str,
    template::str|null,
    errors::list[str],
    guidance::str,
    terminal::bool
  ]

### On-Disk State Layout (Tracked Modes)

SESSION_LAYOUT::[
  PENDING_ROOT::".hestai/sessions/pending/{token}/",
  PENDING_HANDSHAKE_FILE::".hestai/sessions/pending/{token}/handshake.json",
  ACTIVE_ROOT::".hestai/sessions/active/{token}/",
  ACTIVE_ANCHOR_FILE::".hestai/sessions/active/{token}/anchor.json"
]

IDENTIFIER_RULE::[
  "token is the session_id.",
  "Directory name is the token.",
  "No token→session_id mapping table is permitted."
]

PROMOTION_RULE::[
  "Stage proof success promotes by atomic rename/move: .hestai/sessions/pending/{token}/ → .hestai/sessions/active/{token}/",
  "Atomic move prevents half-written active sessions."
]

PENDING_HANDSHAKE_SCHEMA::[
  token::uuid,
  stage::[IDENTITY|CONTEXT|BOUND],
  role::string,
  working_dir::string,
  mode::string,
  strictness::string,
  topic::string|null,
  constitution_path::string,
  created_at::timestamp,
  expires_at::timestamp,
  server_arm::string|null
]

### Stage Semantics

STAGE_IDENTITY::[
  INPUT::[stage,working_dir,role,mode,strictness,topic],
  DO::[
    "Ensure .hestai-sys injection is present for working_dir",
    "Load constitution from .hestai-sys/agents/{role}.oct.md",
    "If mode in [full,lite]: create pending/{token}/handshake.json with stage=IDENTITY",
    "Return: token + constitution_path (+ optional excerpt) + template for BIND-only payload"
  ],
  OUTPUT_TEMPLATE::"PARTIAL_IDENTITY_BLOCK (BIND-only)"
]

STAGE_CONTEXT::[
  INPUT::[stage,working_dir,token,payload=BIND_only],
  DO::[
    "Validate token exists and handshake.stage==IDENTITY (tracked modes)",
    "Validate BIND section against schema (proves agent extracted identity)",
    "Compute server-authoritative ARM (phase/branch/files/focus/context_hash)",
    "Persist ARM into handshake.json and advance stage=CONTEXT",
    "Return: server_arm + template for proof payload (tensions+commit)"
  ]
]

STAGE_PROOF::[
  INPUT::[stage,working_dir,token,payload=proof],
  DO::[
    "Validate token exists and handshake.stage==CONTEXT (tracked modes)",
    "Validate: TENSIONS meet strictness; COMMIT has concrete artifact+gate; CTX citations are falsifiable",
    "Write anchor.json under pending/{token}, then promote via atomic rename to active/{token}",
    "Return: canonical anchor + WORK_PERMIT"
  ]
]

### Strictness Rules

STRICTNESS_RULES::[
  quick::"min_tensions=1",
  default::"min_tensions=2",
  deep::"min_tensions=3 AND CTX citations require line ranges"
]

### Retry / Failure Model

RETRY_PROTOCOL::[
  MAX_RETRIES::2[per_stage_context_and_stage_proof],
  ON_FAIL::"Return specific errors + guidance + template for corrected payload",
  HARD_FAIL::"After max retries, return terminal=true and keep tools locked"
]

### Tool Gating Integration

GATING_MODEL::[
  LOCK_RULE::"No anchor.json under .hestai/sessions/active/{token} ⇒ privileged tools locked",
  UNLOCK_RULE::"anchor.json validated=true under active/{token} ⇒ privileged tools unlocked",
  UNTRACKED::"mode=untracked never unlocks write tools"
]

## REFERENCES

PROTOCOL::".hestai-sys/library/specs/odyssean-anchor-protocol-v5.oct.md"
SCHEMA::".hestai-sys/library/schemas/identity.oct.schema"
TERMINOLOGY::"docs/odyssean-anchor-terminology.md"

===END===
