===HESTAI_ECOSYSTEM_OVERVIEW===
META:
  TYPE::ECOSYSTEM_MAP
  VERSION::"3.0"
  STATUS::TARGET
  PURPOSE::"How every system in the HestAI ecosystem connects and what each owns"
  CANONICAL::"src/hestai_mcp/_bundled_hub/standards/HESTAI-ECOSYSTEM-OVERVIEW.oct.md"
  CREATED::"2026-02-18"
  REVISED::"2026-03-28"
  FORMAT::octave
§0::ARCHITECTURE_NOTE
DESCRIPTION::"This document describes the APPROVED TARGET three-system Thick Client architecture. The workbench will absorb hestai-mcp and odyssean-anchor-mcp into a unified platform (Engine + Glass + Library). debate-hall-mcp and octave-mcp remain standalone. See docs/dream-team-architecture.md for the specification."
CURRENT_REALITY::"Until workbench migration is complete, the current system (hestai-mcp + odyssean-anchor-mcp as separate MCP servers) remains operational. Current-state docs (HESTAI-SYSTEM-REFERENCE, HESTAI-REPO-DIRECTORY) describe the running system. HESTAI-ECOSYSTEM-LIGHTHOUSE describes prior target-state vision and is superseded by this document for architectural direction. This document describes the approved destination."
PREVIOUS_MODEL::"Six-repo federation (v2.1) where hestai-mcp, odyssean-anchor-mcp, debate-hall-mcp, octave-mcp, workbench, and pal-mcp operated as separate servers. Converging to three systems."
DECISION_SOURCE::"HO assessment session 2026-03-28. dream-team-architecture.md (2026-03-22). Human-approved direction."
THICK_CLIENT_RATIONALE::[
  "Solo developer + desktop app — federation is accumulative complexity",
  "Glass UI changes should immediately affect the system without IPC hop to separate server",
  "Workbench controls PTY and sessions — headless session management is redundant",
  "Pre-compiled anchor payloads eliminate 50k-token ceremony overhead per agent spawn",
  "Single debug target vs multi-process debugging"
]
§1::WHAT_THIS_IS
HESTAI::"Design-and-build system for AI-assisted software development with installed operating discipline"
OPERATOR::"Single developer + laptop + multiple terminals + multi-model AI orchestration"
ECOSYSTEM::"Three target systems that together will provide agent identity, governance, deliberation, semantic compression, and a unified control panel"
§2::THE_THREE_SYSTEMS
SYSTEM_1::"HESTAI_WORKBENCH[REPO::elevanaltd/hestai-workbench, ROLE::The Unified Platform, OWNS::[agent_definitions, skills_library, anchor_ceremony, context_steward, session_lifecycle, governance_rules, agent_registry, worktree_orchestration, cli_spawning, terminal_ui, agent_dispatch, payload_compilation, pipeline_runner], ABSORBS::[hestai-mcp(library+governance+session_lifecycle), odyssean-anchor-mcp(anchor_ceremony+identity_binding)], ARCHITECTURE::Engine (Node/TS backend with payload compiler + dispatcher + pipeline runner + anchor validator) + Glass (React frontend with agent registry + session dashboard + workflow editor + dispatch chain visibility) + Library Manager (reads/writes .hestai-sys/ and .hestai/ directly), KEY_PROPERTY::Unified center. Knows WHO agents are, HOW they behave, WHICH provider runs them, WHERE sessions run. Single process, single debug target., DEPENDS_ON::[debate-hall-mcp, octave-mcp], DATA::[~/.hestai-workbench/library/ (agent definitions, skills, standards — canonical after migration Step 2), SQLite database (sessions, agent registry, UI state), git worktrees per session, .hestai-sys/ (written to worktrees at spawn — same pattern, workbench is writer), .hestai/ (project context, committed, read by workbench), .hestai/state/ (working state, written by workbench)]]"
SYSTEM_2::"DEBATE_HALL_MCP[REPO::elevanaltd/debate-hall-mcp, ROLE::The Deliberation Chamber, VERSION::0.4.0, OWNS::[wind_wall_door_debates, governance_operations, decision_records, hash_chain_integrity], TOOLS::17, KEY_PROPERTY::Standalone deliberation (P6). Works without HestAI for non-governance users. Persistent transcripts with hash-chain integrity., DEPENDS_ON::[octave-mcp], DATA::[debates/ directory with JSON state, OCTAVE-compressed transcripts, decision records with SHA-256 hash chain]]"
SYSTEM_3::"OCTAVE_MCP[REPO::elevanaltd/octave-mcp, ROLE::The Language, VERSION::1.9.2, OWNS::[octave_format_spec, validation, generation, compression], TOOLS::[octave_validate, octave_write, octave_eject], KEY_PROPERTY::Pure protocol. Zero dependencies on governance. Maximum community adoption potential. 54-68 percent token reduction., DEPENDS_ON::[nothing], DATA::[v6 grammar specification, GHC (Generative Holographic Contracts)]]"
§3::SYSTEMS_BEING_ABSORBED
CANONICAL_SOURCE_DURING_MIGRATION::"During migration, hestai-mcp repository remains the source-of-truth for library content (agents, skills, standards, cognitions). After workbench Library Manager (dependency graph Step 2) is complete and verified, canonical source moves to workbench library. Both repos must not diverge during this period."
HESTAI_MCP_ABSORPTION::[STATUS::being_absorbed_into_workbench,REPO::"elevanaltd/HestAI-MCP",WHAT_TRANSFERS::[
  "Library content (52+ skills, 20+ agents, standards docs, cognitions) to workbench library",
  "Governance delivery (.hestai-sys/ injection) to workbench Library Manager",
  "Session lifecycle (clock_in/clock_out) to workbench session management",
  "Context steward tools to workbench Engine"
],WHAT_REMAINS::"Repository remains source-of-truth for library content during migration. Archived only after full capability replacement gates are met (dependency graph Step 9 prerequisites: dispatch, library, anchor, pipelines, Glass).",EVIDENCE::"705 tests, 92 percent coverage. Patterns and logic to be studied during TypeScript port."]
ODYSSEAN_ANCHOR_ABSORPTION::[
  STATUS::being_absorbed_into_workbench,
  REPO::"elevanaltd/odyssean-anchor-mcp",
  WHAT_TRANSFERS::[
    "5-stage anchor ceremony (KEAPH) to workbench Engine anchor validator",
    "Steward state machine (2144 lines) as TypeScript port in workbench backend",
    "Proof validation + permit system to workbench Engine",
    "714 tests as equivalent TypeScript test coverage"
  ],
  EVIDENCE::"ADR-0275 decided merger into hestai-mcp. HO assessment (2026-03-28) redirected target to workbench backend (human-approved)."
]
PAL_ELIMINATION::[
  STATUS::being_eliminated,
  REPO::"elevanaltd/pal-mcp-server",
  DISPOSITION::[
    "CLI dispatch (clink) to workbench native multi-CLI dispatch",
    "API dispatch to workbench OpenRouter dispatch",
    "Agent prompts canonical source moves to workbench library",
    "continuation_id to workbench session persistence"
  ]
]
§4::HOW_THEY_CONNECT
DAILY_WORKFLOW::[
  STEP_1::"Open workbench. See agent registry with role/model/tier cards.",
  STEP_2::"Click agent (e.g. Implementation Lead). Select tier. Workbench compiles payload from library.",
  STEP_3::"Workbench writes .hestai-sys/ to worktree, spawns CLI with governance pre-loaded.",
  STEP_4::"Agent starts with context injected. Lighter verification (Colleague path) or full ceremony (Formal path for T3+).",
  STEP_5::"Agent works. Reads .hestai/ for project context. Uses octave-mcp for documents.",
  STEP_6::"Agent needs deliberation — workbench routes to debate-hall-mcp.",
  STEP_7::"Agent needs another agent — workbench dispatches directly (knows registry, compiles payload, spawns CLI).",
  STEP_8::"Full dispatch chain visible in Glass UI — HO to IL to UTE with status per agent.",
  STEP_9::"Session ends. Workbench archives transcript, updates session dashboard."
]
DATA_FLOW::"User to workbench(compile payload+spawn CLI) to agent(work with octave format) to debate-hall(if deliberation needed) to workbench(archive+display)"
THREE_LOADING_PATHS::[
  FORMAL::"Full 5-stage anchor ceremony. For T3-T4 high-stakes work. Agent proves comprehension. PROD::I5 fully satisfied.",
  COLLEAGUE::"Workbench pre-compiles payload. Agent gets lightweight verification. Default for T1-T2. Requires Anchor Validator port (dependency graph Step 5) before operational.",
  DEBATE::"Cognition + identity injection only. For deliberation sessions. Requires Anchor Validator port (dependency graph Step 5) before operational."
]
SECURITY_NOTE::"Until the Anchor Validator port (dependency graph Step 5) is complete, the full formal ceremony via odyssean-anchor-mcp remains mandatory for all tiers. Colleague and Debate paths are target features, not current reality. PROD::I5 (Odyssean Identity Binding) is not relaxed — it is satisfied differently per loading path."
§5::OWNERSHIP_BOUNDARIES
CLEAR_SEPARATIONS::[
  "WHO agents are + HOW they behave + WHERE sessions run + WHICH provider — workbench (unified)",
  "HOW to make governance decisions — debate-hall-mcp (standalone deliberation)",
  "WHAT format documents use — octave-mcp (standalone protocol)",
  "Agent library — ONE canonical source. Currently hestai-mcp repo during migration, then workbench library."
]
§6::ON_DISK_STRUCTURE
PERSISTENCE::"The three-directory structure persists. What changes is the writer, not the format."
DIRECTORIES::[
  ".hestai-sys/ — written by workbench at spawn, read-only for agents, governance layer",
  ".hestai/ — committed project context, north stars and specs, read by workbench and agents",
  ".hestai/state/ — working state (sessions, context, reports, research), written by workbench, displayed in Glass UI"
]
§7::CURRENT_STATE_AND_ROADMAP
WORKBENCH_STATUS::[
  STATUS::"prototype_phase, Phase_2_complete",
  NEXT::"Build Engine (anchor validator + payload compiler + dispatcher + pipeline runner) + enhance Glass (comprehensive agent registry + session dashboard + dispatch chain visibility). Absorb hestai-mcp library content and OA ceremony logic."
]
DEBATE_HALL_STATUS::[
  STATUS::"operational, v0.4.0, 17 tools",
  NEXT::"Continue at own pace. Issue 163 (Governance Hall), Issue 159 (RACI mode). Independent of workbench migration."
]
OCTAVE_STATUS::[
  STATUS::"operational, v1.9.2, PyPI published",
  NEXT::"Standalone community adoption. Chassis-Profile grammar RFC. No governance dependencies."
]
HESTAI_MCP_STATUS::[
  STATUS::being_absorbed,
  NEXT::"Library content migrates to workbench. Repository archived after migration complete."
]
§8::KEY_PRINCIPLES
P1::"The workbench is the target unified platform. Identity, governance, execution, and UI under one roof."
P2::"One canonical source for agent definitions and skills. Currently hestai-mcp repo, migrating to workbench library."
P3::"Pre-compiled payloads by default once Anchor Validator port is complete. Full ceremony remains mandatory until then."
P4::"OCTAVE is the universal format. All systems read and write it."
P5::"The workbench is the only GUI. debate-hall and octave-mcp are headless."
P6::"Deliberation is standalone. debate-hall-mcp works without HestAI for non-governance users."
P7::"On-disk structure (.hestai-sys/, .hestai/, .hestai/state/) persists. Writer changes, format does not."
===END===
