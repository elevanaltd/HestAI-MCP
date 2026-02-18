===HESTAI_ECOSYSTEM_OVERVIEW===
META:
  TYPE::ECOSYSTEM_MAP
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"How every system in the HestAI ecosystem connects and what each owns"
  CANONICAL::"src/hestai_mcp/_bundled_hub/governance/HESTAI-ECOSYSTEM-OVERVIEW.oct.md"
  CREATED::"2026-02-18"
  FORMAT::octave

§1::WHAT_THIS_IS
HESTAI::"Design-and-build system for AI-assisted software development with installed governance"
OPERATOR::"Single developer + laptop + multiple terminals + multi-model AI orchestration"
ECOSYSTEM::"Five systems that together provide agent identity, governance, deliberation, semantic compression, and a unified control panel"

§2::THE_FIVE_SYSTEMS

SYSTEM_1::HESTAI_CORE_MCP[
  REPO::"elevanaltd/HestAI-MCP (merging with odyssean-anchor-mcp)",
  ROLE::"The Operating System",
  OWNS::[agent_constitutions,skills_library,anchor_ceremony,context_steward,session_lifecycle,governance_rules],
  TOOLS::[clock_in,clock_out,anchor_request,anchor_lock,anchor_commit,document_submit,context_update],
  KEY_PROPERTY::"Provider-agnostic. Knows WHO agents are and HOW they should behave. Does NOT spawn CLIs or know about models.",
  DEPENDS_ON::[octave-mcp],
  DATA::[".hestai-sys/[read-only governance]",".hestai/[mutable project context]","agent constitutions in .oct.md format","skills library"]
]

SYSTEM_2::DEBATE_HALL_MCP[
  REPO::"elevanaltd/debate-hall-mcp",
  ROLE::"The Deliberation Chamber",
  OWNS::[wind_wall_door_debates,governance_operations,decision_records,hash_chain_integrity],
  TOOLS::[init_debate,add_turn,close_debate,run_debate,resolve_question,search_decisions],
  PLANNED_TOOLS::[governance_consult,governance_gate,governance_inform,governance_vote],
  KEY_PROPERTY::"Standalone deliberation. Others can use for non-HestAI reasoning. Persistent transcripts with hash-chain integrity.",
  DEPENDS_ON::[octave-mcp],
  CONSUMES::[hestai-core-mcp"for agent resolution when needed"],
  DATA::["debates/ directory with JSON state","OCTAVE-compressed transcripts","decision records with SHA-256 hash chain"]
]

SYSTEM_3::OCTAVE_MCP[
  REPO::"elevanaltd/octave-mcp (or OCTAVE/octave-mcp)",
  ROLE::"The Language",
  OWNS::[octave_format_spec,validation,generation,compression],
  TOOLS::[octave_validate,octave_write,octave_eject],
  KEY_PROPERTY::"Pure protocol. Zero dependencies on governance. Maximum community adoption potential. 54-68% token reduction.",
  DEPENDS_ON::[nothing],
  DATA::["v6 grammar specification","GHC (Generative Holographic Contracts)"]
]

SYSTEM_4::HESTAI_WORKBENCH[
  REPO::"elevanaltd/hestai-workbench (evolved from crystal-fresh)",
  ROLE::"The Control Panel",
  OWNS::[agent_registry,session_management,worktree_orchestration,cli_spawning,terminal_ui,agent_dispatch],
  CURRENT_STATE::"Prototype phase. Stripped Crystal fork with agent registry being added.",
  KEY_PROPERTY::"Execution layer. Knows WHICH provider and model each agent runs on. Spawns CLIs, manages worktrees, shows output. The only system with a GUI.",
  DEPENDS_ON::["hestai-core-mcp (agent identity)","debate-hall-mcp (governance decisions)","octave-mcp (document format)"],
  DATA::["SQLite database (sessions, agent registry, UI state)","git worktrees per session","~/.crystal/ config directory"],
  AGENT_REGISTRY::"role | provider | model — UI-configurable mapping that all dispatch reads from"
]

SYSTEM_5::PAL_MCP[
  REPO::"elevanaltd/pal-mcp-server (fork of BeehiveInnovations)",
  ROLE::"Transport Layer (being absorbed)",
  CURRENT_STATE::"45 commits ahead of stalled upstream. Agent prompts duplicated from hestai-core. Being phased out.",
  DISPOSITION::[
    "clink (CLI dispatch) → moves to hestai-workbench",
    "chat (model API calls) → moves to hestai-workbench or hestai-core",
    "workflow tools (codereview, debug, thinkdeep) → replaced by proper agent loading via anchor",
    "consensus → debate-hall-mcp vote operation",
    "agent prompt files → canonical source is hestai-core-mcp",
    "apilookup → keep as utility",
    "continuation_id → workbench session persistence"
  ],
  KEY_PROPERTY::"Temporary. Useful today for multi-provider calls. Will be fully absorbed once workbench dispatch and core agent loading are complete."
]

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
  "debate-hall-mcp depends on: octave-mcp, optionally consumes hestai-core",
  "hestai-workbench depends on: all three MCP servers",
  "pal-mcp: temporary, being absorbed into workbench + core"
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

LAYER_0::OCTAVE_MCP[semantics,validation,compression]
LAYER_1::HESTAI_CORE_MCP[identity,governance,memory,agent_knowledge]
LAYER_2::DEBATE_HALL_MCP[deliberation,decisions,consensus]
LAYER_3::HESTAI_WORKBENCH[execution,ui,dispatch,session_management]
INTEGRATION::"Each layer serves the one above. OCTAVE is foundation. Workbench is the surface."

§6::CURRENT_STATE_AND_ROADMAP

HESTAI_CORE::[
  STATUS::operational,
  NEXT::"Merge odyssean-anchor-mcp into single repo. Consolidate agent prompts as single source of truth."
]
DEBATE_HALL::[
  STATUS::operational,
  NEXT::"Issue #163 — five governance operations (consult, gate, inform, vote, defend). Issue #112 — desktop app becomes workbench panel instead."
]
OCTAVE::[
  STATUS::operational,
  NEXT::"Standalone community adoption. No governance dependencies."
]
WORKBENCH::[
  STATUS::prototype_phase,
  NEXT::"Phase 2 (strip dead features) → Phase 3 (agent registry + TDD) → Phase 4 (2 months daily use) → Phase 5 (rebuild properly). See crystal-fresh#20."
]
PAL::[
  STATUS::operational_but_being_absorbed,
  NEXT::"CLI dispatch moves to workbench. Workflow tools replaced by agent loading. Agent prompts consolidated to hestai-core."
]

§7::KEY_PRINCIPLES

P1::"Agent identity is separate from agent execution. hestai-core knows who. Workbench knows how."
P2::"One canonical source for agent prompts. No duplication across repos."
P3::"Provider-agnostic governance. hestai-core works regardless of which CLI or model runs underneath."
P4::"OCTAVE is the universal format. All systems read and write it."
P5::"The workbench is the only GUI. MCP servers are headless. Debate-hall#112 and HestAI-MCP#38 become workbench panels, not separate apps."
P6::"Deliberation is standalone. debate-hall-mcp works without HestAI for non-governance users."

===END===
