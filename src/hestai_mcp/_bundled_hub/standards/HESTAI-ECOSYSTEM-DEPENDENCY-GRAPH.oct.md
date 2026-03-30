===DEPENDENCY_GRAPH===
META:
  TYPE::ECOSYSTEM_DEPENDENCY_GRAPH
  VERSION::"3.0"
  STATUS::TARGET
  PURPOSE::"Cross-system build sequence, blocking relationships, and phase alignment"
  CREATED::"2026-02-22"
  REVISED::"2026-03-30"
  FORMAT::octave
  RESOLVES::"#265 (Cross-repo ecosystem dependency graph)"
  SUPPLEMENTS::HESTAI-ECOSYSTEM-OVERVIEW.oct.md
§0::PREAMBLE
CONTEXT::"Single developer + AI agents. Thick Client architecture — workbench absorbs hestai-mcp and odyssean-anchor-mcp. Three target systems: workbench, debate-hall-mcp, octave-mcp."
ARCHITECTURE_DECISION::"Federation model (v2.1) replaced by Thick Client model (v3.0). See dream-team-architecture.md and HO assessment session 2026-03-28."
CURRENT_REALITY::"Until workbench migration is complete, the current federation (hestai-mcp + odyssean-anchor-mcp as separate MCP servers) remains operational. This graph describes the approved build sequence toward the target state."
§1::CURRENT_STATE
OCTAVE_MCP::[
  VERSION::"1.9.6",
  PHASE::B5_DOCUMENTATION,
  HEALTH::PRODUCTION_READY,
  PYPI::published,
  BLOCKERS::none,
  KEY_FACT::"Foundation layer. Zero dependencies. debate-hall-mcp consumes it (>=1.2.1). Workbench will consume it for format validation."
]
DEBATE_HALL_MCP::[
  VERSION::"0.5.0",
  PHASE::"OPERATIONAL, Layer 2 complete",
  HEALTH::PRODUCTION_READY,
  TESTS::"496 passing (491 unit + 5 e2e), 92 percent coverage",
  TOOLS::17,
  BLOCKERS::none,
  KEY_FACT::"Standalone (P6). consult + convene shipped. Depends on octave-mcp>=1.2.1."
]
HESTAI_WORKBENCH::[
  VERSION::pre-release,
  PHASE::PHASE_2_COMPLETE,
  HEALTH::COMPILES,
  CODEBASE::"65,792 LOC TypeScript/TSX (Electron + React)",
  BLOCKERS::"none technical, paused at agent registry",
  KEY_FACT::"Target platform for unified Engine + Glass + Library. Phase 2 (strip dead features) complete. Phase 3 (agent registry) is the critical path for the entire ecosystem.",
  ABSORBING::[hestai-mcp,odyssean-anchor-mcp]
]
HESTAI_MCP::[
  VERSION::pre-release,
  PHASE::B1_FOUNDATION,
  HEALTH::FUNCTIONAL,
  TESTS::"705 passing, 92 percent coverage",
  TOOLS::[
    clock_in,
    clock_out,
    bind,
    submit_review
  ],
  STATUS::being_absorbed_into_workbench,
  KEY_FACT::"Library content (52+ skills, 20+ agents, standards, cognitions) migrating to workbench. Repository remains source-of-truth during migration, archived after."
]
ODYSSEAN_ANCHOR_MCP::[
  VERSION::"0.1.1",
  PHASE::ALPHA,
  HEALTH::OPERATIONAL,
  TESTS::"714 passing, 88 percent coverage",
  TOOLS::[
    anchor_request,
    anchor_lock,
    anchor_commit,
    anchor_micro,
    verify_permit
  ],
  STATUS::being_absorbed_into_workbench,
  KEY_FACT::"5-stage KEAPH ceremony. 2144-line Steward state machine. Logic will be rebuilt in TypeScript inside workbench Engine. ADR-0275 decided merger into hestai-mcp; HO assessment (2026-03-28) redirected target to workbench (human-approved). Full ceremony remains mandatory until port complete."
]
PAL_MCP_SERVER::[
  VERSION::"1.0.3",
  PHASE::"OPERATIONAL, being eliminated",
  HEALTH::STABLE,
  TOOLS::19,
  KEY_FACT::"Multi-CLI dispatch validates patterns ahead of workbench registry build. Being eliminated — workbench natively replaces all dispatch."
]
§2::DEPENDENCY_ARROWS
ARROWS::[
  "workbench --[mcp_client]--> debate-hall-mcp (deliberation calls)",
  "workbench --[mcp_client_or_cli]--> octave-mcp (format validation)",
  "debate-hall-mcp --[python_import]--> octave-mcp (pyproject.toml: octave-mcp>=1.2.1)",
  "workbench --[absorbing]--> hestai-mcp (library content migration)",
  "workbench --[absorbing]--> odyssean-anchor-mcp (anchor ceremony rebuild in TypeScript)"
]
§3::LAYER_MODEL_WITH_STATE
LAYER_0::"FOUNDATION — octave-mcp: SOLID, v1.9.6, production. ACTION: Update deps when releases happen. No structural changes needed."
LAYER_1::"DELIBERATION — debate-hall-mcp: SOLID, v0.5.0, production, 17 tools. ACTION: Continue independently. Issue 163 (Governance Hall), Issue 159 (RACI mode)."
LAYER_2::"UNIFIED_PLATFORM — hestai-workbench: PROTOTYPE, Phase_2_complete, absorbing hestai-mcp and OA. ACTION: Build Engine + Glass + Library Manager. Critical path for entire ecosystem."
§4::SEQUENCED_BUILD_ORDER
STEP_1::[
  WHAT::"Comprehensive Agent Registry in workbench",
  RATIONALE::"Foundation of everything. Visual agent cards with role, cognition, model, fallback, tier defaults. Initially reads from existing hestai-mcp bundled hub until Step 2 migrates content into the workbench library. Enhanced version of current rudimentary registry.",
  EFFORT::"medium — DB schema, UI, library migration",
  BLOCKS::[
    STEP_2,
    STEP_3,
    STEP_4
  ]
]
STEP_2::[
  WHAT::"Library Manager — migrate hestai-mcp content into workbench",
  RATIONALE::"Move canonical agent definitions, skills, standards, cognitions from hestai-mcp _bundled_hub into workbench library directory. Workbench writes .hestai-sys/ to worktrees at spawn. Same files, different writer.",
  EFFORT::"medium — content migration, .hestai-sys writer, Glass editors",
  PREREQ::STEP_1,
  BLOCKS::[STEP_5]
]
STEP_3::[
  WHAT::"Native multi-CLI + API dispatch",
  RATIONALE::"Workbench spawns CLIs (Claude, Codex, Gemini, Goose) and calls APIs (OpenRouter) directly. Registry maps role to provider to model to dispatch mode. Replaces PAL.",
  EFFORT::"medium — cli spawning, api dispatch, provider configs",
  PREREQ::STEP_1,
  BLOCKS::[STEP_6,STEP_7]
]
STEP_4::[
  WHAT::"Payload Compiler — pre-compiled anchor payloads",
  RATIONALE::"Engine reads agent file, cognition, skills from library. Compiles full governance payload. Injects into CLI system prompt at spawn. Eliminates 50k-token ceremony overhead for Colleague path.",
  EFFORT::"medium — compiler logic, payload format, loading path selection",
  PREREQ::STEP_1,
  BLOCKS::[STEP_5]
]
STEP_5::[
  WHAT::"Anchor Validator — TypeScript port of OA ceremony",
  RATIONALE::"Formal loading path (T3-T4) still needs full ceremony. Port 5-stage KEAPH from Python Steward (2144 lines) into workbench Engine. Colleague path uses pre-compiled payloads (Step 4). Both paths produce valid permits. Until this step is complete, full ceremony via odyssean-anchor-mcp remains mandatory.",
  EFFORT::"large — 2144-line state machine, 714 tests, TypeScript port",
  PREREQ::[STEP_2,STEP_4],
  BLOCKS::[STEP_6]
]
STEP_6::[
  WHAT::"Pipeline Runner — multi-agent orchestration",
  RATIONALE::"B3 REINTEGRATE, D2 EXPLORE, tiered review — all are multi-agent pipelines. Same engine, different config. Workbench dispatches agents in sequence with BLOCK signal enforcement.",
  EFFORT::"large — pipeline engine, config schema, BLOCK signals",
  PREREQ::[STEP_3,STEP_5]
]
STEP_7::[
  WHAT::"Glass UI — session dashboard + dispatch chain + workflow editor",
  RATIONALE::"Visual control panel. Session dashboard shows active agents. Dispatch chain shows HO to IL to UTE routing. Workflow editor configures phases and tiers. Review pipeline shows TMG/CRS/CE status.",
  EFFORT::"large — React panels, real-time updates, config editors",
  PREREQ::[STEP_3,STEP_1]
]
STEP_8::[
  WHAT::"debate-hall integration in Glass",
  RATIONALE::"debate-hall is headless (P5/P6). Glass wraps it with chat panel UI. consult+convene tools already shipped.",
  EFFORT::"medium — React chat panel, MCP client, polling",
  PREREQ::STEP_7
]
STEP_9::[
  WHAT::"PAL decommission + hestai-mcp archive",
  RATIONALE::"After workbench fully replaces all capabilities: dispatch (Step 3), library (Step 2), anchor ceremony (Step 5), pipelines (Step 6), and Glass observability (Step 7). Only then are PAL and hestai-mcp redundant. Archive repos.",
  EFFORT::"small — decommission and archive",
  PREREQ::[
    STEP_2,
    STEP_3,
    STEP_5,
    STEP_6,
    STEP_7
  ]
]
§5::CRITICAL_PATH
CRITICAL_PATH::"STEP_1 then STEP_2+STEP_4 (parallel, STEP_3 parallel but feeds STEP_6) then STEP_5 then STEP_6"
EXPLANATION::"Agent registry (1) unlocks three parallel tracks: library (2), dispatch (3), and payload compiler (4). Library + payload compiler unlock anchor validator port (5). Dispatch + anchor validator unlock multi-agent pipelines (6). Glass (7) builds in parallel once dispatch exists. Archive (9) waits for full capability replacement."
VISUAL::[
  "     octave-mcp (solid, no action)      debate-hall (solid, own pace)",
  "            |                                  |",
  "     STEP 1: Agent Registry                    |",
  "        /       |        \\                     |",
  "  STEP 2:   STEP 3:    STEP 4:                 |",
  "  Library   Dispatch   Payload                  |",
  "  Manager              Compiler                 |",
  "       \\       |       /                        |",
  "     STEP 5: Anchor Validator    STEP 7: Glass UI",
  "            |                        |",
  "     STEP 6: Pipeline Runner   STEP 8: debate-hall",
  "            |                    in Glass",
  "            |                        |",
  "         STEP 9: PAL decommission",
  "                + hestai-mcp archive"
]
PARALLEL_TRACKS::[
  TRACK_A::"octave-mcp roadmap (independent, Chassis-Profile RFC #283)",
  TRACK_B::"debate-hall Issue 163 (Governance Hall) + Issue 159 (RACI mode) (independent)",
  TRACK_C::"Dream-team library content (phase files, roster, agent rewrites) — feeds Step 2"
]
§6::KEY_DECISIONS_MAPPED
DECISION_1::[
  QUESTION::"Should odyssean-anchor-mcp merge into hestai-mcp?",
  STATUS::"SUPERSEDED — originally ADR-0275",
  ANSWER::"ADR-0275 decided merger into hestai-mcp. HO assessment (2026-03-28) redirected target to workbench (human-approved). Same logic, different target platform.",
  RATIONALE::[
    "Workbench controls PTY and sessions — headless session management is redundant",
    "Glass UI changes should immediately affect the system (no IPC hop)",
    "Pre-compiled payloads eliminate ceremony overhead",
    "Single debug target vs multi-process debugging"
  ]
]
DECISION_2::[
  QUESTION::"What happens to PAL?",
  STATUS::unchanged,
  ANSWER::"PAL is eliminated, not absorbed. Workbench agent registry natively owns all dispatch."
]
DECISION_3::[
  QUESTION::"What happens to hestai-mcp?",
  STATUS::NEW,
  ANSWER::"Library content migrates to workbench. Repository remains source-of-truth during migration, archived after. Its 705 tests and patterns inform the TypeScript port."
]
DECISION_4::[
  QUESTION::"Does the on-disk structure change?",
  STATUS::NEW,
  ANSWER::"No. .hestai-sys/ (governance, read-only), .hestai/ (project context, committed), .hestai/state/ (working state including sessions, context, reports, research) all persist. Writer changes from hestai-mcp to workbench. Format stays OCTAVE."
]
§7::ISSUE_MAPPING
ISSUES::[
  "#265 (this graph)::meta_coordination",
  "#263 (blind assessor)::STEP_6 needs_pipeline_runner",
  "#262 (governance chat)::STEP_8",
  "#279-282 (OA rebuild phases)::STEP_5 target_changed_to_workbench",
  "#284 (capability tiers)::STEP_4 payload_compiler",
  "#285 (tiered permits)::STEP_5 anchor_validator",
  "workbench#1 (evolve crystal)::STEPS_1_through_9",
  "workbench#16 (governance chat UI)::STEP_8",
  "workbench#32 (agent registry)::STEP_1",
  "workbench#33 (native dispatch)::STEP_3",
  "debate-hall#163 (governance hall)::TRACK_B parallel",
  "debate-hall#159 (RACI mode)::TRACK_B parallel",
  "octave-mcp#283 (Chassis-Profile RFC)::TRACK_A parallel",
  "Project 15 (Ecosystem Build Order)::this_graph full_coordination"
]
§8::OPERATOR_INSIGHT
DIRECTION::"Thick Client model reflects user confirmed direction: put everything in the workbench so it is all in one place. The dream-team Engine+Glass architecture (2026-03-22) provides the specification. The critical path is: make the agent registry comprehensive first (Step 1), then build dispatch, library, and payload compilation in parallel (Steps 2-4), then port the anchor ceremony (Step 5), then multi-agent pipelines (Step 6)."
ANTI_PATTERN::"Continuing to build into hestai-mcp Python when the target platform is TypeScript/Electron workbench. New governance and engine features should target the workbench."
===END===
