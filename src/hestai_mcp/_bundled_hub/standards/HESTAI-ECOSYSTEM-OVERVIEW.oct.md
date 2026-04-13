===HESTAI_ECOSYSTEM_OVERVIEW===
META:
  TYPE::ECOSYSTEM_MAP
  VERSION::"4.0"
  STATUS::TARGET
  PURPOSE::"How every system in the HestAI ecosystem connects and what each owns"
  CANONICAL::"src/hestai_mcp/_bundled_hub/standards/HESTAI-ECOSYSTEM-OVERVIEW.oct.md"
  CREATED::"2026-02-18"
  REVISED::"2026-04-09"
  FORMAT::octave
  ARCHITECTURE::"THREE_SERVICE_MODEL<ADR-0353>"
§0::ARCHITECTURE_NOTE
DESCRIPTION::"This document describes the APPROVED TARGET architecture per ADR-0353 (Three-Service Model). The ecosystem comprises three services: Workbench (Eyes and Hands), Vault (DNA), hestai-context-mcp (Memory and Environment), plus two standalone MCP servers (debate-hall, octave-mcp). Identity injection uses the Alley-Oop pattern via the Payload Compiler. Context management uses hestai-context-mcp via stdio MCP transport."
PREVIOUS_MODEL::"v3.0 described Thick Client absorption where workbench absorbs hestai-mcp and odyssean-anchor-mcp. CORRECTED by ADR-0353: Workbench absorbs UX/dispatch only. Governance engine is harvested into hestai-context-mcp. Agent identity moves to Vault."
DECISION_SOURCE::"ADR-0353 (2026-04-06). Wind/Wall/Door debates (standard + premium tier). Human-approved direction."
CLEAN_BREAK_RATIONALE::[
  "Conflating identity injection (stateless) with state management (stateful) was the root error",
  "Governance logic (1500+ lines proven Python, 92% coverage) must survive Workbench rebuild",
  "Stdio MCP transport is the Git/VS Code pattern — zero network ports, zero daemon lifecycle",
  "Terminal parity is automatic — any CLI gets identical governance via one MCP config entry",
  "Harvest not rewrite — legacy stays intact for A/B comparison"
]
§1::WHAT_THIS_IS
HESTAI::"Design-and-build system for AI-assisted software development with installed operating discipline"
OPERATOR::"Single developer + laptop + multiple terminals + multi-model AI orchestration"
ECOSYSTEM::"Three services plus two standalone MCP servers that together provide agent identity, governance, session lifecycle, context synthesis, deliberation, semantic compression, and a unified control panel"
§2::THE_THREE_SERVICES
SYSTEM_1::"HESTAI_WORKBENCH[REPO::elevanaltd/hestai-workbench, ROLE::The Eyes and Hands, OWNS::[payload_compiler(KVAEPH), alley_oop_pattern, agent_registry, stratified_conditioning(baseline+reliability), multi_cli_dispatch, api_dispatch, session_management(worktrees+terminals), governance_chat_ui, system_dashboard, dispatch_chain_visibility, precedence_locked_materialized_resolver(matrix_defaults+matrix_overrides+v_resolved_matrix)], ARCHITECTURE::Payload Compiler (reads Vault + calls hestai-context-mcp) + Glass (React frontend) + Dispatch Service (CLI + API), KEY_PROPERTY::HIGH volatility. Planned Crystal-to-TypeScript rebuild. Governance logic survives in hestai-context-mcp untouched. Only ~30-line stdio MCP client adapter needs rewriting., DEPENDS_ON::[vault(identity reads), hestai-context-mcp(Position 3 context via stdio), debate-hall-mcp(deliberation calls), octave-mcp(format validation)]]"
SYSTEM_2::"VAULT[LOCATION::~/.hestai-workbench/library/(git-backed+configurable_via_LIBRARY_ROOT), ROLE::The DNA, OWNS::[v9_agent_definitions, v9_skills_with_anchor_kernels, cognitions(ETHOS+PATHOS+LOGOS), standards(System_Standard+naming+visibility), patterns], KEY_PROPERTY::ZERO volatility. Git-backed, immutable at runtime. Workbench reads directly and compiles system prompts with no filesystem intermediate. Glass Agent Editor provides CRUD with auto-commit on save., DATA::[starter-library in Workbench resources/ for first-run bootstrap, agent definitions (~50 lines each blank-slate V9), 16 V9 skills with S5 ANCHOR_KERNEL sections]]"
SYSTEM_3::"HESTAI_CONTEXT_MCP[REPO::elevanaltd/hestai-context-mcp(NEW-harvested_from_hestai-mcp), ROLE::The Memory and Environment, OWNS::[clock_in(session_creation+focus_resolution+AI_context_synthesis+conflict_detection), clock_out(transcript_parsing+credential_redaction+OCTAVE_compression+learnings_indexing), ContextSteward(dynamic_PhaseConstraints), submit_review(structured_review_verdicts+CI_gate+8_roles+dry_run+SHA_pinning), submit_rccafp_record(error_recovery+root_cause_analysis), submit_friction_record(F2D_governance_feedback), product_north_star_injection(KVAEPH_Position_3), dotHestai_state_management], KEY_PROPERTY::LOW volatility. Proven Python, 92% coverage. Stdio MCP transport (subprocess not daemon). Survives Workbench rebuilds untouched. Terminal parity automatic., TRANSPORT::stdio_JSON_RPC, DEPENDS_ON::[nothing_at_runtime]]"
STANDALONE_1::"DEBATE_HALL_MCP[REPO::elevanaltd/debate-hall-mcp, ROLE::The Deliberation Chamber, VERSION::0.5.0, OWNS::[wind_wall_door_debates, governance_operations, decision_records, hash_chain_integrity, RACI_mode, consult_convene], TOOLS::17, KEY_PROPERTY::Standalone deliberation (P6). Works without HestAI for non-governance users. Persistent transcripts with hash-chain integrity., DEPENDS_ON::[octave-mcp]]"
STANDALONE_2::"OCTAVE_MCP[REPO::elevanaltd/octave-mcp, ROLE::The Language, VERSION::1.9.6, OWNS::[octave_format_spec, validation, generation, compression, grammar_compilation], KEY_PROPERTY::Pure protocol. Zero dependencies on governance. Maximum community adoption potential. 54-68 percent token reduction., DEPENDS_ON::[nothing]]"
§3::LEGACY_SYSTEMS
HESTAI_MCP::[
  STATUS::legacy_stays_for_AB_comparison,
  REPO::"elevanaltd/HestAI-MCP",
  DISPOSITION::[
    "Library content (_bundled_hub: agents, skills, standards, cognitions) moves to Vault",
    ".hestai-sys/ injection mechanism moves to Vault/Workbench",
    "clock_in, clock_out, ContextSteward, RedactionEngine, submit_review, submit_rccafp_record harvested into hestai-context-mcp",
    "bind tool replaced by Alley-Oop for headless dispatch",
    "Legacy system stays intact for A/B comparison until new system proven"
  ],
  NOT_BEING_ABSORBED::"ADR-0353 resolved: hestai-mcp is NOT being absorbed into the Workbench. Governance engine logic is harvested into a NEW repo (hestai-context-mcp). Legacy stays for comparison.",
  EVIDENCE::"930 tests, 92 percent coverage. Proven patterns inform the harvest."
]
ODYSSEAN_ANCHOR_MCP::[
  STATUS::legacy_for_claude_with_mcp_sessions,
  REPO::"elevanaltd/odyssean-anchor-mcp",
  DISPOSITION::[
    "5-stage KEAPH ceremony remains operational for Claude-with-MCP sessions",
    "Replaced by Alley-Oop pattern for Workbench headless dispatch",
    "NOT being rebuilt in TypeScript inside Workbench (previous plan per ADR-0275 was superseded)"
  ]
]
PAL_MCP_SERVER::[
  STATUS::being_eliminated,
  REPO::"elevanaltd/pal-mcp-server",
  DISPOSITION::[
    "CLI dispatch (clink) replaced by Workbench native multi-CLI dispatch",
    "API dispatch replaced by Workbench OpenRouter dispatch",
    "Agent prompts canonical source moves to Vault"
  ]
]
§4::HOW_THEY_CONNECT
DISPATCH_FLOW::[
  STEP_1::"User selects agent + task in Glass UI",
  STEP_2::"Payload Compiler reads Vault for Positions 0-2 (BIOS/AXIOMS, IDENTITY, CAPABILITIES)",
  STEP_3::"Payload Compiler calls hestai-context-mcp via stdio for Position 3 (CONTEXT: clock_in returns context synthesis, Product North Star, project state)",
  STEP_4::"Compiler assembles full KVAEPH payload",
  STEP_5::"Workbench dispatches to CLI tool with compiled prompt (Alley-Oop for reliability pipeline, single-step grammar for baseline)",
  STEP_6::"Agent works. Reads .hestai/ for project context. Uses octave-mcp for documents.",
  STEP_7::"Agent needs deliberation — routes to debate-hall-mcp",
  STEP_8::"Agent needs another agent — calls dispatch_colleague, Workbench compiles fresh KVAEPH and spawns",
  STEP_9::"Session ends. Agent optionally calls submit_friction_record. Workbench calls hestai-context-mcp clock_out — learnings extracted, transcript redacted, index updated."
]
TERMINAL_FLOW::[
  STEP_1::"User configures hestai-context-mcp as stdio MCP server in their CLI config",
  STEP_2::"Agent calls clock_in directly — identical context synthesis",
  STEP_3::"Agent works with full governance",
  STEP_4::"Agent calls clock_out — knowledge extraction",
  STEP_5::"No Workbench required. Identical governance via standard MCP config."
]
DATA_FLOW::"User to Workbench(compile KVAEPH from Vault + hestai-context-mcp) to agent(work with octave format) to debate-hall(if deliberation needed) to hestai-context-mcp(clock_out: archive+extract)"
TWO_CONDITIONING_PIPELINES::[
  BASELINE::"For simple low-complexity dispatch. U-Curve prompt topology plus single-step enforced grammar. KVAEPH core plus task with MUST_USE grammar requirement.",
  RELIABILITY::"For T2+ tasks. Alley-Oop pattern: (1) system: dense OCTAVE KVAEPH core, (2) user[synthetic]: acknowledge constraints, (3) assistant[synthetic]: Workbench-constructed static proof from Vault, (4) user[real]: task + Dynamic Anchor Lock demand. Agent MUST emit cognitive grammar headers before proceeding."
]
LEGACY_PATH::"OA ceremony (5-stage KEAPH) remains for Claude-with-MCP sessions. Alley-Oop is for headless/non-MCP dispatch."
§5::OWNERSHIP_BOUNDARIES
CLEAR_SEPARATIONS::[
  "WHO agents are (identity, skills, cognitions) — Vault (git-backed, read-only at runtime)",
  "MEMORY and ENVIRONMENT (sessions, context synthesis, learnings, review) — hestai-context-mcp (stdio MCP)",
  "EYES and HANDS (UI, dispatch, Payload Compiler) — Workbench",
  "HOW to make governance decisions — debate-hall-mcp (standalone deliberation)",
  "WHAT format documents use — octave-mcp (standalone protocol)"
]
§6::ON_DISK_STRUCTURE
PERSISTENCE::"The three-directory structure persists. What changes is the writer, not the format."
DIRECTORIES::[
  ".hestai-sys/ — written by Workbench from Vault at spawn, read-only for agents, governance layer",
  ".hestai/ — committed project context, north stars and specs, read by Workbench and agents",
  ".hestai/state/ — working state (sessions, context, reports, research), written by hestai-context-mcp, displayed in Glass UI"
]
§7::CURRENT_STATE_AND_ROADMAP
WORKBENCH_STATUS::[
  STATUS::"v0.6.0, 3A-prep substantially complete",
  WHAT_EXISTS::"Matrix resolver (v_resolved_matrix), 4 V9 agents (IL, CRS, HO, ideator), 16 V9 skills, System Standard in vault, multi-session management, git worktree isolation, agent registry with Glass UI",
  NEXT::"Build Payload Compiler (Step 3A, issue #99). All prerequisites met: matrix resolver, V9 skills, System Standard, archetype assignments."
]
VAULT_STATUS::[
  STATUS::"starter library populated",
  WHAT_EXISTS::"4 V9 agents, 16 V9 skills with ANCHOR_KERNEL sections, 3 cognitions, System Standard",
  NEXT::"Populate as Payload Compiler demands content. Glass Agent Editor provides CRUD."
]
HESTAI_CONTEXT_MCP_STATUS::[
  STATUS::"ADR-0353 accepted. Interface contract done. Feature-parity matrix done.",
  NEXT::"Phase 1: Create repo (elevanaltd/hestai-context-mcp). Harvest clock_in. Redesign clock_out with TDD. Build get_context. Legacy hestai-mcp stays intact."
]
DEBATE_HALL_STATUS::[
  STATUS::"operational, v0.5.0, 17 tools",
  NEXT::"Continue at own pace. Issue 163 (Governance Hall). Independent of other systems."
]
OCTAVE_STATUS::[
  STATUS::"operational, v1.9.6, PyPI published",
  NEXT::"Standalone community adoption. No governance dependencies."
]
HESTAI_MCP_LEGACY_STATUS::[
  STATUS::"operational, 930 tests, 92 percent coverage",
  DISPOSITION::"Stays for A/B comparison. Eventually deprecated after new system proven."
]
§8::KEY_PRINCIPLES
P1::"The Workbench is the Eyes and Hands. It compiles and dispatches. It does NOT own governance state or agent identity."
P2::"One canonical source for agent identity — the Vault. Git-backed, immutable at runtime."
P3::"hestai-context-mcp is the Memory and Environment. It owns session lifecycle, context synthesis, learnings, and review infrastructure. Proven Python via stdio."
P4::"OCTAVE is the universal format. All systems read and write it."
P5::"The Workbench is the only GUI. debate-hall, octave-mcp, and hestai-context-mcp are headless."
P6::"Deliberation is standalone. debate-hall-mcp works without HestAI for non-governance users."
P7::"On-disk structure (.hestai-sys/, .hestai/, .hestai/state/) persists. Writer changes, format does not."
P8::"Harvest not rewrite. Legacy stays intact for A/B comparison. Deprecation only after new system proven."
P9::"Rebuild survival is structural. Governance in hestai-context-mcp survives Workbench rebuilds. Only ~30-line stdio adapter rewrites."
===END===
