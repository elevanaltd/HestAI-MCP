===HESTAI_ECOSYSTEM_OVERVIEW===
META:
  TYPE::ECOSYSTEM_MAP
  VERSION::"2.1"
  STATUS::ACTIVE
  PURPOSE::"How every system in the HestAI ecosystem connects and what each owns"
  CANONICAL::"src/hestai_mcp/_bundled_hub/standards/HESTAI-ECOSYSTEM-OVERVIEW.oct.md"
  CREATED::"2026-02-18"
  REVISED::"2026-03-19"
  FORMAT::octave
§0::ARCHITECTURE_NOTE
NOTE::"This document describes the CURRENT six-repo architecture and the TARGET three-repo MCP architecture. odyssean-anchor-mcp (elevanaltd/odyssean-anchor-mcp) is currently a separate MCP server providing the anchor ceremony (identity binding). Merger into hestai-core-mcp is decided (ADR-0275) with rebuild tracked in HestAI-MCP #279-282."
CURRENT_SEPARATION::[
  "hestai-mcp: governance, memory, context steward, session lifecycle",
  "odyssean-anchor-mcp: anchor ceremony (anchor_request, anchor_lock, anchor_commit, verify_permit)",
  "DECIDED: merge into single hestai-core-mcp (ADR-0275 accepted, rebuild not yet started)"
]
§1::WHAT_THIS_IS
HESTAI::"Design-and-build system for AI-assisted software development with installed governance"
OPERATOR::"Single developer + laptop + multiple terminals + multi-model AI orchestration"
ECOSYSTEM::"Six systems (converging to four) that together provide agent identity, governance, deliberation, semantic compression, and a unified control panel"
§2::THE_SIX_SYSTEMS
SYSTEM_1::"HESTAI_CORE_MCP<REPO::\"elevanaltd/HestAI-MCP\",NOTE::\"odyssean-anchor-mcp is currently a separate server (elevanaltd/odyssean-anchor-mcp). Merger decided per ADR-0275, rebuild tracked in #279-282.\",ROLE::\"The Operating System\",OWNS::[agent_constitutions,skills_library,anchor_ceremony,context_steward,session_lifecycle,governance_rules],TOOLS::[clock_in,clock_out,bind,submit_review],PLANNED_TOOLS::[document_submit,context_update],ANCHOR_NOTE::\"Anchor ceremony tools (anchor_request, anchor_lock, anchor_commit, anchor_micro, verify_permit) are currently provided by odyssean-anchor-mcp. Will be rebuilt natively per ADR-0275.\",KEY_PROPERTY::\"Provider-agnostic. Knows WHO agents are and HOW they should behave. Does NOT spawn CLIs or know about models.\",DEPENDS_ON::[octave-mcp],DATA::[\".hestai-sys/[read-only governance]\",\".hestai/[mutable project context]\",\"agent constitutions in .oct.md format\",\"skills library\"]>"
SYSTEM_2::"DEBATE_HALL_MCP<REPO::\"elevanaltd/debate-hall-mcp\",ROLE::\"The Deliberation Chamber\",VERSION::\"0.4.0\",OWNS::[wind_wall_door_debates,governance_operations,decision_records,hash_chain_integrity],TOOLS::[init_debate,add_turn,get_debate,close_debate,pick_next_speaker,force_close_debate,tombstone_turn,github_sync_debate,ratify_rfc,human_interject,run_debate,resume_debate,extract_decision_record,resolve_question,search_decisions,consult,convene],TOOL_COUNT::17,PLANNED_TOOLS::[governance_committee_operations],KEY_PROPERTY::\"Standalone deliberation. Others can use for non-HestAI reasoning. Persistent transcripts with hash-chain integrity.\",DEPENDS_ON::[octave-mcp],DATA::[\"debates/ directory with JSON state\",\"OCTAVE-compressed transcripts\",\"decision records with SHA-256 hash chain\"]>"
SYSTEM_3::"OCTAVE_MCP<REPO::\"elevanaltd/octave-mcp\",ROLE::\"The Language\",VERSION::\"1.8.0\",OWNS::[octave_format_spec,validation,generation,compression],TOOLS::[octave_validate,octave_write,octave_eject],KEY_PROPERTY::\"Pure protocol. Zero dependencies on governance. Maximum community adoption potential. 54-68% token reduction.\",DEPENDS_ON::[nothing],DATA::[\"v6 grammar specification\",\"GHC (Generative Holographic Contracts)\"]>"
SYSTEM_4::"HESTAI_WORKBENCH<REPO::\"elevanaltd/hestai-workbench (evolved from crystal-fresh)\",ROLE::\"The Control Panel\",OWNS::[agent_registry,session_management,worktree_orchestration,cli_spawning,terminal_ui,agent_dispatch],CURRENT_STATE::\"Phase 2 (strip dead features) complete. Phase 3 (agent registry) open but not started.\",KEY_PROPERTY::\"Execution layer. Knows WHICH provider, model, and dispatch mode each agent runs on. Spawns CLIs, manages worktrees, shows output. The only system with a GUI.\",DEPENDS_ON::[\"hestai-core-mcp (agent identity)\",\"debate-hall-mcp (governance decisions)\",\"octave-mcp (document format)\"],DATA::[\"SQLite database (sessions, agent registry, UI state)\",\"git worktrees per session\",\"~/.crystal/ config directory\"],AGENT_REGISTRY::\"role | dispatch mode (CLI/API) | provider | model — UI-configurable mapping that all dispatch reads from\">"
SYSTEM_5::"PAL_MCP<REPO::\"elevanaltd/pal-mcp-server (based on BeehiveInnovations/pal-mcp-server)\",ROLE::\"Transport Layer (actively used, being eliminated per Lighthouse v3.0)\",CURRENT_STATE::\"Ahead of stalled upstream. Actively used daily via clink (including Goose CLI with full MCP access to all ecosystem servers). Agent prompts duplicated from hestai-core.\",DISPOSITION::[\"CLI dispatch (clink) → natively owned by workbench agent registry (multi-CLI: Claude, Codex, Gemini, Goose)\",\"API dispatch → natively owned by workbench agent registry (OpenRouter for lightweight calls)\",\"workflow tools (codereview, debug, thinkdeep) → replaced by proper agent loading via anchor\",\"consensus → debate-hall-mcp vote operation\",\"agent prompt files → canonical source is hestai-core-mcp\",\"apilookup → evaluate for workbench or deprecate\",\"continuation_id → workbench session persistence\"],KEY_PROPERTY::\"Actively used daily. PAL is being eliminated (not absorbed) — the Workbench agent registry natively replaces all dispatch. Goose via pal clink validates multi-provider dispatch ahead of registry build.\">"
SYSTEM_6::"ODYSSEAN_ANCHOR_MCP<REPO::\"elevanaltd/odyssean-anchor-mcp\",ROLE::\"Identity Binding (merger target)\",CURRENT_STATE::\"Operational. Merger into hestai-core-mcp decided (ADR-0275). Rebuild phases #279-282 not yet started.\",TOOLS::[anchor_request,anchor_lock,anchor_commit,anchor_micro,verify_permit],KEY_PROPERTY::\"Separate MCP server providing identity binding protocol. Will be rebuilt natively inside hestai-core-mcp.\",DEPENDS_ON::[octave-mcp]>"
§3::HOW_THEY_CONNECT
DAILY_WORKFLOW::[
  STEP_1::"Open workbench. Pick agent from registry (e.g. holistic-orchestrator → claude → opus-4.6)",
  STEP_2::"Workbench spawns CLI in a git worktree, connects MCP servers",
  STEP_3::"CLI starts. Agent binds identity via hestai-core-mcp anchor ceremony",
  STEP_4::"Agent works. Calls hestai-core for skills/context. Uses octave-mcp for documents.",
  STEP_5::"Agent hits ambiguous decision → calls debate-hall-mcp for structured deliberation",
  STEP_6::"Agent needs another perspective → workbench dispatches to different agent/provider",
  STEP_7::"Session ends. hestai-core-mcp archives transcript in OCTAVE format"
]
DATA_FLOW::"User→workbench[spawn CLI]→hestai-core[anchor bind+load context]→work[octave format throughout]→debate-hall[if decision needed]→hestai-core[clock_out+archive]"
DEPENDENCY_DIRECTION::[
  "octave-mcp depends on: nothing (foundation layer)",
  "hestai-core-mcp depends on: octave-mcp",
  "debate-hall-mcp depends on: octave-mcp (standalone, NOT dependent on hestai-core)",
  "odyssean-anchor-mcp depends on: octave-mcp (merger target, will cease to exist)",
  "hestai-workbench depends on: all three MCP servers",
  "pal-mcp: actively used daily, being eliminated — dispatch natively owned by workbench agent registry"
]
§4::OWNERSHIP_BOUNDARIES
CLEAR_SEPARATIONS::[
  "WHO agents are (constitutions, skills, identity) → hestai-core-mcp",
  "WHICH provider/model runs each agent → workbench agent registry",
  "HOW to make governance decisions → debate-hall-mcp",
  "WHAT format documents use → octave-mcp",
  "WHERE sessions run (worktrees, terminals, UI) → workbench",
  "Agent prompts: ONE canonical source in hestai-core. Not duplicated elsewhere."
]
§5::LAYER_MODEL
LAYER_0::OCTAVE_MCP<semantics,validation,compression>
LAYER_1::HESTAI_CORE_MCP<identity,governance,memory,agent_knowledge>
LAYER_1_NOTE::"Currently spans two repos (hestai-mcp + odyssean-anchor-mcp). Merger decided per ADR-0275, rebuild tracked in #279-282."
LAYER_2::DEBATE_HALL_MCP<deliberation,decisions,consensus>
LAYER_3::HESTAI_WORKBENCH<execution,ui,dispatch,session_management>
INTEGRATION::"Each layer serves the one above. OCTAVE is foundation. Workbench is the surface."
§6::CURRENT_STATE_AND_ROADMAP
HESTAI_CORE::[
  STATUS::operational,
  NEXT::"Execute OA merger (ADR-0275 rebuild phases #279-282). Consolidate agent prompts as single source of truth. Capability tiers (#284), tiered permits (#285)."
]
DEBATE_HALL::[
  STATUS::"operational<v0.4.0_17_tools>",
  NEXT::"Issue #163 — Governance Hall (persistent committee spaces). Issue #159 — RACI governance mode. consult + convene already shipped."
]
OCTAVE::[
  STATUS::"operational<v1.8.0_PyPI_published>",
  NEXT::"Standalone community adoption. Chassis-Profile grammar RFC (octave-mcp#283). No governance dependencies."
]
WORKBENCH::[
  STATUS::prototype_phase<Phase_2_complete>,
  NEXT::"Phase 3 (agent registry + TDD) → Phase 4 (2 months daily use) → Phase 5 (rebuild properly). See hestai-workbench#32."
]
PAL::[
  STATUS::operational<actively_used_daily_being_eliminated>,
  NEXT::"PAL eliminated per Lighthouse v3.0. Workbench agent registry natively owns multi-CLI dispatch (Claude, Codex, Gemini, Goose) and API dispatch (OpenRouter). Agent prompts consolidated to hestai-core. Goose via pal clink validates multi-provider dispatch ahead of registry build."
]
§7::KEY_PRINCIPLES
P1::"Agent identity is separate from agent execution. hestai-core knows who. Workbench knows how."
P2::"One canonical source for agent prompts. No duplication across repos."
P3::"Provider-agnostic governance. hestai-core works regardless of which CLI or model runs underneath."
P4::"OCTAVE is the universal format. All systems read and write it."
P5::"The workbench is the only GUI. MCP servers are headless. Debate-hall#112 and HestAI-MCP#38 become workbench panels, not separate apps."
P6::"Deliberation is standalone. debate-hall-mcp works without HestAI for non-governance users."
===END===
