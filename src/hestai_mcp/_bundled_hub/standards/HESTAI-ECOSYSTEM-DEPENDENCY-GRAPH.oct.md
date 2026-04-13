===DEPENDENCY_GRAPH===
META:
  TYPE::ECOSYSTEM_DEPENDENCY_GRAPH
  VERSION::"4.0"
  STATUS::TARGET
  PURPOSE::"Cross-system build sequence, blocking relationships, and phase alignment"
  CREATED::"2026-02-22"
  REVISED::"2026-04-09"
  FORMAT::octave
  RESOLVES::"#265 (Cross-repo ecosystem dependency graph)"
  SUPPLEMENTS::HESTAI-ECOSYSTEM-OVERVIEW.oct.md
  ARCHITECTURE::"THREE_SERVICE_MODEL<ADR-0353>"
§0::PREAMBLE
CONTEXT::"Single developer + AI agents. Three-Service Model architecture (ADR-0353) — Workbench (Eyes and Hands), Vault (DNA), hestai-context-mcp (Memory and Environment). Two standalone MCP servers: debate-hall, octave-mcp. Legacy systems (hestai-mcp, OA, PAL) stay for A/B comparison."
ARCHITECTURE_DECISION::"Thick Client model (v3.0) replaced by Three-Service Model (v4.0). See ADR-0353 (2026-04-06). Identity injection via Alley-Oop pattern in Payload Compiler. Context management via hestai-context-mcp stdio MCP."
PREVIOUS_MODEL::"v3.0 described 9-step absorption build sequence where workbench absorbs hestai-mcp and OA. CORRECTED: Workbench owns dispatch only. Governance engine harvested into hestai-context-mcp. Agent identity moves to Vault."
§1::CURRENT_STATE
OCTAVE_MCP::[
  VERSION::"1.9.6",
  PHASE::B5_DOCUMENTATION,
  HEALTH::PRODUCTION_READY,
  PYPI::published,
  BLOCKERS::none,
  KEY_FACT::"Foundation layer. Zero dependencies. debate-hall-mcp consumes it (>=1.2.1). All other systems speak OCTAVE."
]
DEBATE_HALL_MCP::[
  VERSION::"0.5.0",
  PHASE::"OPERATIONAL, Layer 2 complete",
  HEALTH::PRODUCTION_READY,
  TESTS::"496 passing (491 unit + 5 e2e), 92 percent coverage",
  TOOLS::17,
  BLOCKERS::none,
  KEY_FACT::"Standalone (P6). consult + convene + RACI shipped. Depends on octave-mcp>=1.2.1."
]
HESTAI_WORKBENCH::[
  VERSION::v0.6.0,
  PHASE::"3A-prep substantially complete",
  HEALTH::COMPILES,
  CODEBASE::"65,792 LOC TypeScript/TSX (Electron + React)",
  WHAT_EXISTS::[
    "Matrix resolver (v_resolved_matrix with kernel_only column)",
    "4 V9 agents (IL, CRS, HO, ideator) with skills/patterns/kernel_only assignments",
    "16 V9 skills with S5 ANCHOR_KERNEL sections",
    "System Standard in vault (AP4 resolved)",
    "Multi-session management with Claude, Codex, Goose CLI support",
    "Git worktree isolation per session",
    "Agent Registry: DB schema, parser (V8+V9), sync, IPC, Glass UI",
    "Library Vault: LIBRARY_ROOT config, bootstrap service, auto-commit on Glass save"
  ],
  BLOCKERS::none_technical,
  KEY_FACT::"Target platform for dispatch and UI. All 3A prerequisites met. Next: Payload Compiler (Step 3A)."
]
VAULT::[
  LOCATION::"~/.hestai-workbench/library/",
  HEALTH::POPULATED,
  CONTENTS::[
    "4 V9 agents (IL, CRS, HO, ideator)",
    "16 V9 skills with ANCHOR_KERNEL sections",
    "3 cognitions (ETHOS, PATHOS, LOGOS)",
    "System Standard (AP4 resolved)"
  ],
  KEY_FACT::"Git-backed, immutable at runtime. Workbench reads directly. Glass Agent Editor provides CRUD with auto-commit."
]
HESTAI_CONTEXT_MCP::[
  STATUS::"ADR-0353 accepted. Interface contract done. Feature-parity matrix done.",
  REPO::"elevanaltd/hestai-context-mcp (NEW, not yet created)",
  KEY_FACT::"Will be harvested from hestai-mcp. Owns clock_in, clock_out, ContextSteward, RedactionEngine, submit_review, submit_rccafp_record, submit_friction_record. Stdio MCP transport."
]
HESTAI_MCP_LEGACY::[
  VERSION::pre-release,
  PHASE::B1_FOUNDATION,
  HEALTH::FUNCTIONAL,
  TESTS::"930 passing, 92 percent coverage",
  TOOLS::[
    clock_in,
    clock_out,
    bind,
    submit_review,
    submit_rccafp_record
  ],
  STATUS::legacy_stays_for_AB_comparison,
  KEY_FACT::"NOT being absorbed. Governance engine logic harvested into hestai-context-mcp. Legacy stays for A/B comparison."
]
ODYSSEAN_ANCHOR_MCP::[
  VERSION::"0.1.1",
  PHASE::ALPHA,
  HEALTH::OPERATIONAL,
  TESTS::"714 passing, 88 percent coverage",
  STATUS::legacy_for_claude_with_mcp_sessions,
  KEY_FACT::"5-stage KEAPH ceremony remains for Claude-with-MCP sessions. Replaced by Alley-Oop for headless dispatch. NOT being rebuilt in TypeScript."
]
PAL_MCP_SERVER::[
  VERSION::"1.0.3",
  PHASE::"OPERATIONAL, being eliminated",
  HEALTH::STABLE,
  STATUS::being_eliminated,
  KEY_FACT::"Workbench natively replaces all dispatch. No intermediate bridge layer."
]
§2::DEPENDENCY_ARROWS
ARROWS::[
  "workbench --[reads]--> vault (agent definitions, skills, cognitions, standards for KVAEPH Positions 0-2)",
  "workbench --[stdio_mcp]--> hestai-context-mcp (clock_in for KVAEPH Position 3, clock_out for session archival)",
  "workbench --[mcp_client]--> debate-hall-mcp (deliberation calls)",
  "workbench --[mcp_client_or_cli]--> octave-mcp (format validation)",
  "debate-hall-mcp --[python_import]--> octave-mcp (pyproject.toml: octave-mcp>=1.2.1)",
  "hestai-context-mcp --[reads]--> .hestai/ (project context, north stars)",
  "hestai-context-mcp --[writes]--> .hestai/state/ (sessions, context, reports)"
]
§3::LAYER_MODEL_WITH_STATE
LAYER_0::"FOUNDATION — octave-mcp: SOLID, v1.9.6, production. ACTION: Update deps when releases happen. No structural changes needed."
LAYER_1::"DELIBERATION — debate-hall-mcp: SOLID, v0.5.0, production, 17 tools. ACTION: Continue independently. Issue 163 (Governance Hall)."
LAYER_2::"IDENTITY — Vault: POPULATED, git-backed. ACTION: Populate as Payload Compiler demands content."
LAYER_3::"CONTEXT — hestai-context-mcp: PLANNED, ADR-0353 accepted. ACTION: Phase 1 harvest from hestai-mcp."
LAYER_4::"DISPATCH — hestai-workbench: 3A-PREP COMPLETE. ACTION: Build Payload Compiler (Step 3A), then dispatch_colleague (Step 3B)."
§4::SEQUENCED_BUILD_ORDER
STEP_3A::[
  WHAT::"Payload Compiler in workbench",
  RATIONALE::"KVAEPH stacker reads Vault for Positions 0-2 (BIOS/AXIOMS, IDENTITY, CAPABILITIES). Calls hestai-context-mcp for Position 3 (CONTEXT). Builds Alley-Oop pattern for reliability pipeline. Single-step grammar for baseline pipeline. All prerequisites met: matrix resolver, V9 skills, System Standard, archetype assignments.",
  EFFORT::"medium — compiler logic, KVAEPH stacking, Alley-Oop pattern builder, stratified conditioning",
  PREREQS_MET::[
    "Matrix resolver (v_resolved_matrix, PR #107)",
    "V9 agents with skills/patterns assignments (PR #108)",
    "System Standard in vault (AP4, PR #108)",
    "16 V9 skills with ANCHOR_KERNEL sections (AP6, PR #112)",
    "IL coverage gap filled (PR #112)"
  ],
  WORKBENCH_ISSUE::"#99",
  BLOCKS::[STEP_3B]
]
STEP_3B::[
  WHAT::"dispatch_colleague uses Payload Compiler",
  RATIONALE::"dispatch_colleague MCP tool uses Payload Compiler to spawn agents with identity via any CLI tool. Dispatch service validates dynamic anchor output (regex on cognitive grammar headers). Continuation model with dispatch_id.",
  EFFORT::"medium — dispatch service, CLI spawning, API dispatch, continuation store",
  PREREQ::STEP_3A,
  BLOCKS::[STEP_4]
]
STEP_4::[
  WHAT::"Testing Lab — empirical validation",
  RATIONALE::"Measures exact threshold where baseline focus collapses. Proves synthetic threading recovery efficacy. Validates Alley-Oop vs OA ceremony A/B.",
  EFFORT::"medium — test harness, measurement framework, empirical analysis",
  PREREQ::STEP_3B,
  WORKBENCH_ISSUE::"#98"
]
HARVEST_PHASE_1::[
  WHAT::"Create hestai-context-mcp repo and harvest clock_in",
  RATIONALE::"New repo (elevanaltd/hestai-context-mcp). Harvest clock_in logic from hestai-mcp. Redesign clock_out with TDD (ClaudeJsonlLens is broken, needs provider adapter pattern). Build get_context. Legacy hestai-mcp stays intact for A/B comparison.",
  EFFORT::"medium — new repo setup, clock_in harvest, clock_out redesign, get_context",
  PARALLEL_WITH::STEP_3A,
  BLOCKS::[HARVEST_PHASE_2]
]
HARVEST_PHASE_2::[
  WHAT::"Workbench Payload Compiler calls hestai-context-mcp for Position 3",
  RATIONALE::"Thin stdio MCP client in Payload Compiler. Spawn python -m hestai_context_mcp via stdio. Inject clock_in output at KVAEPH Position 3.",
  EFFORT::"small — stdio MCP client (~30 lines), integration",
  PREREQ::[STEP_3A,HARVEST_PHASE_1]
]
HARVEST_PHASE_3::[
  WHAT::"Unify North Star injection",
  RATIONALE::"System NS from Vault (static, Position 0). Product NS from hestai-context-mcp during clock_in (dynamic, Position 3). Remove load-north-star-summary.sh hook.",
  EFFORT::"small — injection unification, hook removal",
  PREREQ::HARVEST_PHASE_2
]
HARVEST_PHASE_4::[
  WHAT::"Git hooks for .hestai/ enforcement",
  RATIONALE::"Deploy .githooks/pre-commit for .hestai/ OCTAVE validation. Enforcement through repository physics (git hooks), not synthetic bureaucracy. Formally deprecate ADR-0033 Phase 3 tools.",
  EFFORT::"small — git hook, validation rules",
  PREREQ::HARVEST_PHASE_3
]
GLASS_UI::[
  WHAT::"Glass UI — session dashboard + dispatch chain + governance chat",
  RATIONALE::"Visual control panel. Session dashboard shows active agents. Dispatch chain shows routing. Governance chat wraps debate-hall with chat panel UI.",
  EFFORT::"large — React panels, real-time updates",
  PARALLEL_WITH::STEP_3A
]
PAL_DECOMMISSION::[
  WHAT::"PAL decommission + legacy deprecation",
  RATIONALE::"After workbench fully replaces all PAL dispatch capabilities. hestai-mcp deprecated (not archived) after new system proven in daily use.",
  EFFORT::"small — decommission and deprecation",
  PREREQ::[STEP_3B,HARVEST_PHASE_2]
]
§5::CRITICAL_PATH
CRITICAL_PATH::"STEP_3A (Payload Compiler) then STEP_3B (dispatch_colleague) then STEP_4 (Testing Lab). In parallel: HARVEST_PHASE_1 (hestai-context-mcp) feeds into HARVEST_PHASE_2 which integrates with STEP_3A."
EXPLANATION::"All 3A prerequisites are met. The Payload Compiler is the next build step. It unlocks dispatch_colleague (3B) which unlocks empirical testing (4). The harvest of hestai-context-mcp runs in parallel — Phase 1 creates the repo, Phase 2 wires it into the Payload Compiler at Position 3."
VISUAL::[
  "  octave-mcp (solid)          debate-hall (solid, own pace)",
  "       |                            |",
  "  VAULT (populated)                 |",
  "       |                            |",
  "  STEP 3A: Payload Compiler    GLASS UI (parallel)",
  "       |         \\                   |",
  "  STEP 3B:    HARVEST Phase 1       |",
  "  dispatch     (hestai-context-mcp) |",
  "  _colleague        |               |",
  "       |       HARVEST Phase 2      |",
  "       |       (wire into 3A)       |",
  "       |            |               |",
  "  STEP 4: Testing Lab               |",
  "       |                            |",
  "  PAL decommission                  |",
  "  + legacy deprecation        governance chat"
]
PARALLEL_TRACKS::[
  TRACK_A::"octave-mcp roadmap (independent, standalone community adoption)",
  TRACK_B::"debate-hall Issue 163 (Governance Hall) (independent)",
  TRACK_C::"Glass UI panels (parallel with 3A/3B, feeds governance chat)",
  TRACK_D::"hestai-context-mcp harvest (parallel with 3A, feeds Position 3 integration)"
]
§6::KEY_DECISIONS_MAPPED
DECISION_1::[
  QUESTION::"What happens to governance/context management?",
  STATUS::"RESOLVED by ADR-0353",
  ANSWER::"Governance engine logic (clock_in, clock_out, ContextSteward, RedactionEngine, submit_review) is harvested into hestai-context-mcp (NEW repo). NOT absorbed into Workbench. Workbench absorbs UX/dispatch only.",
  SUPERSEDES::[
    "ADR-0275 (OA merger into hestai-mcp — target changed)",
    "Ecosystem Overview v3.0 (Thick Client absorption model — corrected)",
    "dream-team-architecture.md (absorption spec — superseded)"
  ]
]
DECISION_2::[
  QUESTION::"What happens to PAL?",
  STATUS::unchanged,
  ANSWER::"PAL is eliminated, not absorbed. Workbench agent registry natively owns all dispatch."
]
DECISION_3::[
  QUESTION::"What happens to hestai-mcp?",
  STATUS::"RESOLVED by ADR-0353",
  ANSWER::"Legacy stays for A/B comparison. Governance engine logic harvested into hestai-context-mcp. Library content (_bundled_hub) moves to Vault. NOT being absorbed into Workbench. Deprecated only after new system proven."
]
DECISION_4::[
  QUESTION::"Does the on-disk structure change?",
  STATUS::unchanged,
  ANSWER::"No. .hestai-sys/ (governance, read-only), .hestai/ (project context, committed), .hestai/state/ (working state) all persist. .hestai-sys/ writer changes from hestai-mcp to Workbench (from Vault). .hestai/state/ writer changes from hestai-mcp to hestai-context-mcp. Format stays OCTAVE."
]
DECISION_5::[
  QUESTION::"How does identity injection work without the anchor ceremony?",
  STATUS::"RESOLVED — Alley-Oop pattern (AP3)",
  ANSWER::"Payload Compiler reads Vault, assembles KVAEPH, constructs synthetic threading with prefilled proof, demands Dynamic Anchor Lock. Agent must emit cognitive grammar headers. MCP_NOT_REQUIRED — validation is regex on output, not server round-trip. OA MCP remains for Claude-with-MCP sessions."
]
DECISION_6::[
  QUESTION::"What happens to odyssean-anchor-mcp?",
  STATUS::"RESOLVED by ADR-0353",
  ANSWER::"Legacy for Claude-with-MCP sessions. NOT being rebuilt in TypeScript inside Workbench (previous plan per ADR-0275 superseded). Replaced by Alley-Oop for headless dispatch."
]
§7::ISSUE_MAPPING
ISSUES::[
  "#265 (this graph)::meta_coordination",
  "#353 (ADR-0353 Three-Service Model)::architectural_pivot",
  "#364 (ecosystem doc updates)::documentation_alignment",
  "workbench#1 (evolve crystal)::STEPS_3A_through_4",
  "workbench#99 (Payload Compiler)::STEP_3A_READY",
  "workbench#33 (native dispatch)::STEP_3B",
  "workbench#98 (Testing Lab)::STEP_4",
  "workbench#36 (PAL decommission)::PAL_DECOMMISSION",
  "workbench#104 (matrix resolver)::DONE_PR_107",
  "workbench#111 (git status fixes)::DONE_PR_111",
  "workbench#112 (IL coverage gap)::DONE_PR_112",
  "debate-hall#163 (governance hall)::TRACK_B parallel",
  "Project 15 (Ecosystem Build Order)::this_graph full_coordination"
]
§8::OPERATOR_INSIGHT
DIRECTION::"Three-Service Model (ADR-0353) reflects the resolved architecture: Workbench compiles and dispatches (Eyes and Hands), Vault stores identity (DNA), hestai-context-mcp manages session lifecycle and context (Memory and Environment). The critical path is: build the Payload Compiler (Step 3A, all prerequisites met), then dispatch_colleague (3B), then Testing Lab (4). In parallel, harvest hestai-context-mcp from the proven hestai-mcp codebase."
ANTI_PATTERN::"Building governance logic into the Workbench. Governance belongs in hestai-context-mcp (proven Python, stdio transport, survives rebuilds). The Workbench is volatile — it will be rebuilt. Keep it thin: compile, dispatch, display."
===END===
