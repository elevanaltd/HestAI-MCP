===DEPENDENCY_GRAPH===
META:
  TYPE::ECOSYSTEM_DEPENDENCY_GRAPH
  VERSION::"1.0"
  STATUS::DRAFT
  PURPOSE::"Cross-repo build sequence, blocking relationships, and phase alignment"
  CREATED::"2026-02-22"
  FORMAT::octave
  RESOLVES::"#265 (Cross-repo ecosystem dependency graph)"
  SUPPLEMENTS::"HESTAI-ECOSYSTEM-OVERVIEW.oct.md"
§0::PREAMBLE
CONTEXT::"Single developer + AI agents. Greenfield except octave-mcp (PyPI) and debate-hall-mcp (small external audience). Prototype-first approach."
DISCOVERY::"No cross-repo coordination plan existed. Four repos have North Stars; none had a sequenced build order. GitHub Project 14 provides some coordination for Governance Chat but doesn't cover the full ecosystem."
§1::CURRENT_STATE
OCTAVE_MCP::[
  VERSION::"1.5.0",
  PHASE::B5_DOCUMENTATION,
  HEALTH::PRODUCTION_READY,
  TESTS::"2258 passing, constitutional compliance verified",
  PYPI::published,
  BLOCKERS::none,
  OPEN_ISSUES::8,
  [all_v1.1.0_roadmap],
  KEY_FACT::"Foundation layer. Zero dependencies on anything else. debate-hall-mcp actively consumes it (>=1.2.1). odyssean-anchor-mcp consumes it (==1.2.1)."
]
HESTAI_MCP::[
  VERSION::"pre-release",
  PHASE::B1_FOUNDATION,
  HEALTH::FUNCTIONAL,
  TOOLS::[
    clock_in,
    clock_out,
    bind,
    submit_review
  ],
  BLOCKERS::none_technical<discovery_phase>,
  OCTAVE_DEP::"octave-mcp dependency updated to >=1.5.0",
  KEY_FACT::"Operational but still discovering what to build. Calls odyssean-anchor at runtime via MCP tool names (not Python imports). Bundles agent constitutions, skills, governance docs."
]
ODYSSEAN_ANCHOR_MCP::[
  VERSION::"0.1.1",
  PHASE::ALPHA,
  HEALTH::OPERATIONAL,
  TESTS::"714 passing, 88% coverage",
  TOOLS::[
    anchor_request,
    anchor_lock,
    anchor_commit,
    anchor_micro,
    verify_permit
  ],
  ACTIVE_WORKTREES::9,
  BLOCKERS::none,
  KEY_FACT::"Separate MCP server. Merger into hestai-mcp planned but not started. Depends on octave-mcp==1.2.1. Has 2144-line Steward class implementing the full protocol state machine."
]
DEBATE_HALL_MCP::[
  VERSION::"0.5.0",
  PHASE::OPERATIONAL<LAYER_3_COMPLETE>,
  HEALTH::PRODUCTION_READY,
  TESTS::"1096 passing (1091 unit + 5 e2e), 90% coverage",
  TOOLS::18,
  BLOCKERS::none,
  KEY_FACT::"Standalone (P6). consult + convene tools shipped. #173 (governance chat API) closed. Depends on octave-mcp>=1.2.1."
]
HESTAI_WORKBENCH::[
  VERSION::"pre-release",
  PHASE::"PHASE_2_STRIP<90_percent_complete>",
  HEALTH::"COMPILES<6_test_type_errors_frontend>",
  CODEBASE::"65,792 LOC TypeScript/TSX (Electron + React)",
  BLOCKERS::none_technical<paused_at_agent_registry>,
  KEY_FACT::"Crystal fork. Phases 1-2 done. Phase 3 (agent registry) ready to start but paused because it requires cross-repo coordination."
]
PAL_MCP_SERVER::[
  VERSION::"1.0.3",
  PHASE::OPERATIONAL,
  HEALTH::STABLE,
  TOOLS::19,
  ["7 _enabled_by_default"],
  TESTS::"109 test files",
  BLOCKERS::none,
  KEY_FACT::"Fully used daily. Zero hestai-mcp dependencies. Has 61 clink role prompts. Absorption into workbench+core planned but timeline unclear. The most mature multi-provider orchestration layer."
]
§2::DEPENDENCY_ARROWS
  // Format: SOURCE --[type]--> TARGET (evidence)
ARROWS::[
  "hestai-mcp --[runtime_MCP_call]--> odyssean-anchor-mcp (bind.py:184 calls mcp__odyssean-anchor__anchor_request)",
  "hestai-mcp --[python_import]--> octave-mcp (bundled governance docs use OCTAVE format, >=1.5.0)",
  "debate-hall-mcp --[python_import]--> octave-mcp (pyproject.toml: octave-mcp>=1.2.1)",
  "odyssean-anchor-mcp --[python_import]--> octave-mcp (pyproject.toml: octave-mcp==1.2.1, AST parsing via Parser/tokenize)",
  "hestai-workbench --[planned]--> hestai-mcp (agent identity loading)",
  "hestai-workbench --[planned]--> debate-hall-mcp (governance chat UI, #16)",
  "hestai-workbench --[planned]--> octave-mcp (document format)",
  "pal-mcp-server --[none]--> anything (fully independent, references hestai in prompts only)",
  "pal-mcp-server --[absorption_target]--> hestai-workbench+hestai-mcp (clink->workbench, prompts->core)"
]
§3::LAYER_MODEL_WITH_STATE
  // Each layer must be solid before the layer above can fully depend on it
LAYER_0::"FOUNDATION<octave-mcp::[SOLID,v1.5.0,production,noactionneeded],ACTION::\"Just update deps when releases happen\">"
LAYER_1::"IDENTITY_AND_GOVERNANCE<hestai-mcp::[FUNCTIONAL,B1,discoveringscope],odyssean-anchor-mcp::[OPERATIONAL,alpha,mergerquestionopen],COMBINED_STATE::\"Both work independently. Together they provide identity binding. Merger would simplify deployment and eliminate runtime MCP-to-MCP call overhead.\",ACTION::\"Decide merger question. Continue B1 discovery.\">"
LAYER_2::"DELIBERATION<debate-hall-mcp::[SOLID,v0.5.0,production,18tools],ACTION::\"No blockers. Continue with #163 (Governance Hall) and RACI mode (#159) at own pace.\">"
LAYER_3::"EXECUTION<hestai-workbench::[PROTOTYPE,Phase290_percent,paused],pal-mcp-server::[OPERATIONAL,beingabsorbed],COMBINED_STATE::\"Workbench needs agent registry (Phase 3) to advance. PAL provides the multi-provider dispatch that workbench will eventually own.\",ACTION::\"Start Phase 3 agent registry. Absorb PAL clink as part of it or immediately after.\">"
§4::SEQUENCED_BUILD_ORDER
  // CRITICAL PATH: What must happen in what order
SEQUENCE::[
  STEP_1::"DECIDE: Odyssean Anchor merger (yes/no/later)",
  RATIONALE::"Unblocks how Layer 1 is structured. If merging, Phase 3 agent registry talks to one server not two. If not merging, workbench config needs two MCP server entries.",
  EFFORT::investigation_1_hour,
  BLOCKS::[STEP_2,STEP_3],
  STEP_2::"IF merger YES -> Execute anchor merger into hestai-mcp",
  RATIONALE::"Consolidates 5 anchor tools + Steward into hestai-mcp. Eliminates runtime MCP-to-MCP hop. Simplifies deployment (one pip install, not two).",
  EFFORT::"medium<2144_line_steward⊕5_tools⊕714_tests>",
  BLOCKS::[STEP_4],
  PREREQ::STEP_1,
  STEP_3::"Workbench Phase 3 — Agent Registry prototype",
  RATIONALE::"The workbench is paused waiting for this. Bridge between agent identity (Layer 1) and execution (Layer 3). Can prototype with current 2-server setup while merger is decided/executed.",
  EFFORT::"medium<DB_schema⊕IPC⊕UI⊕tests>",
  BLOCKS::[STEP_5,STEP_6],
  PREREQ::STEP_1<decision_only_not_execution>,
  STEP_4::"PAL clink extraction -> workbench dispatch",
  RATIONALE::"clink is modular and self-contained. Extracting the CLI-dispatch pattern into workbench gives it the ability to spawn agents on different providers/models. Highest-value PAL extraction.",
  EFFORT::"medium<clink.py⊕cli_configs⊕provider_registry>",
  BLOCKS::[STEP_6],
  PREREQ::STEP_3<agent_registry_exists>,
  STEP_5::"Workbench <-> debate-hall integration (Governance Chat UI)",
  RATIONALE::"debate-hall is headless (P5). workbench#16 adds the chat panel. consult+convene tools already shipped. Mostly frontend work.",
  EFFORT::"medium<React_chat_panel⊕polling⊕UI>",
  PREREQ::STEP_3<agent_registry_for_role_display>,
  STEP_6::"Cross-repo agent invocation prototype",
  RATIONALE::"Agents invoking agents in different directories via convene, each HO in its own repo. Requires agent registry + clink dispatch + debate-hall convene. This is the convergence point.",
  EFFORT::exploratory<prototype_first>,
  PREREQ::[
    STEP_3,
    STEP_4,
    STEP_5
  ],
  STEP_7::"Blind assessor agent + test suite (#263)",
  RATIONALE::"Needs agents that can be dispatched, identity binding, multi-model invocation. Can be manually invoked as Claude Code subagent earlier for spot-testing.",
  EFFORT::"medium<agent_def⊕rubrics⊕scenarios>",
  PREREQ::[STEP_3,STEP_4],
  STEP_8::"PAL full absorption — remaining tools",
  RATIONALE::"After clink extracted (Step 4), remaining PAL tools (codereview, consensus, thinkdeep, etc.) absorbed or deprecated. Low urgency since PAL works fine as-is.",
  EFFORT::"large<19_tools⊕61_prompts⊕config_unification>",
  PREREQ::[STEP_4,STEP_6]
]
§5::CRITICAL_PATH
CRITICAL_PATH::"STEP_1 -> STEP_3 -> STEP_4 -> STEP_6"
EXPLANATION::"Merger decision (1) unblocks agent registry design (3), which unblocks clink extraction (4), which enables cross-repo agent invocation (6). Everything else can happen in parallel around this spine."
VISUAL::[
  "                octave-mcp (solid, no action)     debate-hall (solid, own pace)",
  "                       |                                |",
  "        STEP 1: Merger Decision                         |",
  "           /                \\                            |",
  "  STEP 2: Merger     STEP 3: Agent Registry -----> STEP 5: Gov Chat UI",
  "  (if yes)                  |                           |",
  "                     STEP 4: clink extraction            |",
  "                            |                           |",
  "                     STEP 6: Cross-repo agent invocation",
  "                       /              \\",
  "               STEP 7: Blind       STEP 8: PAL full",
  "               Assessor            absorption"
]
PARALLEL_TRACKS::[
  TRACK_A::"octave-mcp v1.1.0 roadmap (independent, no blockers)",
  TRACK_B::"debate-hall #163 + #159 (independent, enhances Layer 2)",
  TRACK_C::"hestai-mcp B1 continued discovery (feeds into Steps 2-3)",
  TRACK_D::"Workbench Phase 2 lint cleanup (low priority, non-blocking)"
]
§6::KEY_DECISIONS_MAPPED
DECISION_1::[
  QUESTION::"Should odyssean-anchor-mcp merge into hestai-mcp?",
  POSITION::STEP_1<critical_path_start>,
  FOR_MERGE::[
    "Simpler deployment (one pip install not two)",
    "No MCP-to-MCP runtime hop",
    "Unified testing and versioning",
    "Nobody would use OA without hestai — deeply intertwined (references .hestai-sys/, HestAI agent formats, OCTAVE docs)"
  ],
  AGAINST_MERGE::[
    "2144-line Steward is complex to absorb",
    "714 tests to integrate",
    "9 active worktrees suggest ongoing independent dev",
    "Alpha status (0.1.1) vs hestai-mcp B1 stability"
  ]
]
DECISION_2::[
  QUESTION::"When does PAL get absorbed into workbench?",
  POSITION::"STEP_4[clink_first]⊕STEP_8",
  ANSWER::"Incrementally. clink first (highest value, modular). Remaining tools later. PAL works fine as-is — no urgency for full absorption."
]
DECISION_3::[
  QUESTION::"What's the actual critical path to cross-repo agent invocation?",
  POSITION::STEP_6,
  ANSWER::"Agent registry (Step 3) + clink dispatch (Step 4) + debate-hall convene (already shipped). Step 6 is where they converge."
]
DECISION_4::[
  QUESTION::"Where does the blind-assessor test suite (#263) sit?",
  POSITION::STEP_7,
  ANSWER::"After dispatch infrastructure exists. Can be manually invoked as subagent earlier for spot-testing."
]
§7::ISSUE_MAPPING
ISSUES::[
  "#265 (this graph)",
  "::",
  STEP_0<meta_coordination>,
  "#263 (blind assessor)",
  "::",
  STEP_7,
  "#262 (governance chat / decision gravity)",
  "::",
  STEP_5,
  "#87 (system architecture blindness)",
  "::",
  addressed_by_this_document,
  "workbench#1 (evolve crystal)",
  "::",
  STEPS_3_through_6,
  "workbench#16 (governance chat UI)",
  "::",
  STEP_5,
  "debate-hall#163 (governance hall)",
  "::",
  TRACK_B<parallel>,
  "debate-hall#159 (RACI mode)",
  "::",
  TRACK_B<parallel>,
  "Project 14 (Governance Chat)",
  "::",
  "STEPS_3⊕",
  5,
  [partial_coordination]
]
§8::OPERATOR_INSIGHT
NOTE::"User expressed concern about hesitancy vs. prototyping. The sequence above is designed for prototype-first: each step produces something usable, not just a plan. Step 3 produces a working agent registry. Step 4 produces working CLI dispatch. Step 6 is an explicit 'try it and see' prototype."
ANTI_PATTERN::"Building the perfect coordination system before trying anything. The graph shows dependencies, not a waterfall. Steps can overlap. The merger decision (Step 1) can be a 1-hour investigation, not a 2-week design doc."
===END===
