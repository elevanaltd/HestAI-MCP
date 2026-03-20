===DEPENDENCY_GRAPH===
META:
  TYPE::ECOSYSTEM_DEPENDENCY_GRAPH
  VERSION::"2.1"
  STATUS::ACTIVE
  PURPOSE::"Cross-repo build sequence, blocking relationships, and phase alignment"
  CREATED::"2026-02-22"
  REVISED::"2026-03-19"
  FORMAT::octave
  RESOLVES::"#265 (Cross-repo ecosystem dependency graph)"
  SUPPLEMENTS::HESTAI-ECOSYSTEM-OVERVIEW.oct.md
§0::PREAMBLE
CONTEXT::"Single developer + AI agents. Greenfield except octave-mcp (PyPI) and debate-hall-mcp (small external audience). Prototype-first approach."
DISCOVERY::"No cross-repo coordination plan existed. Four repos have North Stars; none had a sequenced build order. GitHub Project 14 provides some coordination for Governance Chat but doesn't cover the full ecosystem."
§1::CURRENT_STATE
OCTAVE_MCP::[
  VERSION::"1.8.0",
  PHASE::B5_DOCUMENTATION,
  HEALTH::PRODUCTION_READY,
  PYPI::published,
  BLOCKERS::none,
  KEY_FACT::"Foundation layer. Zero dependencies on anything else. debate-hall-mcp actively consumes it (>=1.2.1). odyssean-anchor-mcp consumes it (==1.2.1)."
]
HESTAI_MCP::[
  VERSION::pre-release,
  PHASE::B1_FOUNDATION,
  HEALTH::FUNCTIONAL,
  TOOLS::[
    clock_in,
    clock_out,
    bind,
    submit_review
  ],
  BLOCKERS::none_technical<discovery_phase>,
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
  BLOCKERS::none,
  KEY_FACT::"Separate MCP server. Merger into hestai-mcp decided (ADR-0275). Rebuild phases #279-282 tracked but not yet started. Depends on octave-mcp==1.2.1. Has 2144-line Steward class implementing the full protocol state machine."
]
DEBATE_HALL_MCP::[
  VERSION::"0.4.0",
  PHASE::OPERATIONAL<LAYER_3_COMPLETE>,
  HEALTH::PRODUCTION_READY,
  TESTS::"496 passing (491 unit + 5 e2e), 92% coverage",
  TOOLS::17,
  BLOCKERS::none,
  KEY_FACT::"Standalone (P6). consult + convene tools shipped. #173 (governance chat API) closed. Depends on octave-mcp>=1.2.1."
]
HESTAI_WORKBENCH::[
  VERSION::pre-release,
  PHASE::PHASE_2_COMPLETE,
  HEALTH::COMPILES,
  CODEBASE::"65,792 LOC TypeScript/TSX (Electron + React)",
  BLOCKERS::none_technical<paused_at_agent_registry>,
  KEY_FACT::"Crystal fork. Phase 2 (strip dead features) complete. Phase 3 (agent registry) open but not started — requires cross-repo coordination."
]
PAL_MCP_SERVER::[
  VERSION::"1.0.3",
  PHASE::OPERATIONAL<being_eliminated>,
  HEALTH::STABLE,
  TOOLS::19,
  ["7 _enabled_by_default"],
  TESTS::"109 test files",
  BLOCKERS::none,
  KEY_FACT::"Actively used daily (clink with Claude, Codex, Gemini, Goose CLIs). Zero hestai-mcp dependencies. Has 61 clink role prompts. Being eliminated per Lighthouse v3.0 — Workbench agent registry natively replaces all dispatch. Goose via pal clink validates multi-provider dispatch ahead of registry build."
]
§2::DEPENDENCY_ARROWS
  // Format: SOURCE --[type]--> TARGET (evidence)
ARROWS::[
  "hestai-mcp --[runtime_MCP_call]--> odyssean-anchor-mcp (bind.py:184 calls mcp__odyssean-anchor__anchor_request)",
  "hestai-mcp --[python_import]--> octave-mcp (bundled governance docs use OCTAVE format)",
  "debate-hall-mcp --[python_import]--> octave-mcp (pyproject.toml: octave-mcp>=1.2.1)",
  "odyssean-anchor-mcp --[python_import]--> octave-mcp (pyproject.toml: octave-mcp==1.2.1, AST parsing via Parser/tokenize)",
  "hestai-workbench --[planned]--> hestai-mcp (agent identity loading)",
  "hestai-workbench --[planned]--> debate-hall-mcp (governance chat UI, #16)",
  "hestai-workbench --[planned]--> octave-mcp (document format)",
  "pal-mcp-server --[none]--> anything (fully independent, references hestai in prompts only)",
  "pal-mcp-server --[elimination_target]--> hestai-workbench+hestai-mcp (dispatch->workbench registry, prompts->core, PAL decommissioned)"
]
§3::LAYER_MODEL_WITH_STATE
  // Each layer must be solid before the layer above can fully depend on it
LAYER_0::"FOUNDATION<octave-mcp::[SOLID,v1.8.0,production,no_action_needed],ACTION::\"Just update deps when releases happen\">"
LAYER_1::"IDENTITY_AND_GOVERNANCE<hestai-mcp::[FUNCTIONAL,B1,discovering_scope],odyssean-anchor-mcp::[OPERATIONAL,alpha,merger_decided],COMBINED_STATE::\"Both work independently. Together they provide identity binding. Merger decided (ADR-0275) — will simplify deployment and eliminate runtime MCP-to-MCP call overhead.\",ACTION::\"Execute merger rebuild (#279-282). Continue B1 discovery.\">"
LAYER_2::"DELIBERATION<debate-hall-mcp::[SOLID,v0.4.0,production,17_tools],ACTION::\"No blockers. Continue with #163 (Governance Hall) and RACI mode (#159) at own pace.\">"
LAYER_3::"EXECUTION<hestai-workbench::[PROTOTYPE,Phase_2_complete,Phase_3_open],pal-mcp-server::[OPERATIONAL,actively_used_daily,being_eliminated],COMBINED_STATE::\"Workbench needs agent registry (Phase 3) to advance. PAL provides multi-provider dispatch that the registry will natively replace. Goose via pal clink validates this works.\",ACTION::\"Start Phase 3 agent registry with native multi-CLI dispatch (Claude, Codex, Gemini, Goose) + API dispatch (OpenRouter). PAL decommissioned when registry is complete.\">"
§4::SEQUENCED_BUILD_ORDER
  // CRITICAL PATH: What must happen in what order
  // STEP 1 (merger decision) is DONE — ADR-0275 accepted
SEQUENCE::[
  STEP_1::"DECIDE: Odyssean Anchor merger (yes/no/later)",
  STATUS::"DONE<ADR-0275_accepted>",
  RESULT::"YES — merger approved. Rebuild (not copy) approach chosen.",
  BLOCKS::[STEP_2,STEP_3],
  STEP_2::"Execute anchor rebuild into hestai-mcp",
  RATIONALE::"Rebuilds binding protocol, Steward state machine, proof validation, and permit system natively inside hestai-mcp. Eliminates runtime MCP-to-MCP hop. Simplifies deployment (one pip install, not two).",
  EFFORT::"medium<2144_line_steward⊕5_tools⊕714_tests>",
  TRACKING::"#279 (Phase 1: shared infra), #280 (Phase 2: port protocol), #281 (Phase 3: integration), #282 (Phase 4: archive OA repo)",
  BLOCKS::[STEP_4],
  PREREQ::STEP_1<DONE>,
  STEP_3::"Workbench Phase 3 — Agent Registry prototype",
  RATIONALE::"The workbench is paused waiting for this. Bridge between agent identity (Layer 1) and execution (Layer 3). Can prototype with current 2-server setup while merger is executed.",
  EFFORT::"medium<DB_schema⊕IPC⊕UI⊕tests>",
  BLOCKS::[STEP_5,STEP_6],
  PREREQ::STEP_1<DONE>,
  STEP_4::"Native multi-CLI dispatch in workbench agent registry",
  RATIONALE::"Build dispatch natively into the agent registry — not extract from PAL. Registry entries map role→provider→model→dispatch mode (cli:claude, cli:codex, cli:gemini, cli:goose, api:openrouter). Goose via pal clink validates multi-provider dispatch works with full MCP access.",
  EFFORT::"medium<registry_schema⊕cli_spawning⊕api_dispatch⊕provider_configs>",
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
  STEP_8::"PAL decommission",
  RATIONALE::"After workbench agent registry owns all dispatch (Step 4) and cross-repo orchestration is proven (Step 6), PAL is decommissioned. Agent prompts already consolidated to hestai-core. Remaining PAL tools (codereview, consensus, thinkdeep) replaced by proper agent loading via anchor ceremony.",
  EFFORT::small<decommission_and_archive>,
  PREREQ::[STEP_4,STEP_6]
]
§5::CRITICAL_PATH
CRITICAL_PATH::"STEP_1[DONE] -> STEP_3 -> STEP_4 -> STEP_6"
EXPLANATION::"Merger decision (1, DONE) unblocks agent registry design (3), which unblocks native multi-CLI/API dispatch (4), which enables cross-repo agent invocation (6). Everything else can happen in parallel around this spine."
VISUAL::[
  "                octave-mcp (solid, no action)     debate-hall (solid, own pace)",
  "                       |                                |",
  "        STEP 1: Merger Decision [DONE]                  |",
  "           /                \\                            |",
  "  STEP 2: OA Rebuild  STEP 3: Agent Registry -----> STEP 5: Gov Chat UI",
  "  (#279-282)                |                           |",
  "                     STEP 4: Native multi-CLI dispatch    |",
  "                            |                           |",
  "                     STEP 6: Cross-repo agent invocation",
  "                       /              \\",
  "               STEP 7: Blind       STEP 8: PAL",
  "               Assessor            decommission"
]
PARALLEL_TRACKS::[
  TRACK_A::"octave-mcp roadmap (independent, Chassis-Profile RFC #283)",
  TRACK_B::"debate-hall #163 (Governance Hall) + #159 (RACI mode) (independent, enhances Layer 2)",
  TRACK_C::"hestai-mcp B1 continued discovery + OA rebuild (feeds into Steps 2-3)",
  TRACK_D::"Workbench Phase 2 lint cleanup (DONE, #37 closed)"
]
§6::KEY_DECISIONS_MAPPED
DECISION_1::[
  QUESTION::"Should odyssean-anchor-mcp merge into hestai-mcp?",
  STATUS::"DECIDED<ADR-0275>",
  ANSWER::"YES — rebuild natively inside hestai-mcp (not copy). Phases #279-282 tracked.",
  RATIONALE::[
    "Simpler deployment (one pip install not two)",
    "No MCP-to-MCP runtime hop",
    "Unified testing and versioning",
    "Nobody would use OA without hestai — deeply intertwined"
  ]
]
DECISION_2::[
  QUESTION::"What happens to PAL?",
  POSITION::"STEP_4[native_dispatch]⊕STEP_8[decommission]",
  ANSWER::"PAL is eliminated, not absorbed (Lighthouse v3.0). Workbench agent registry natively owns multi-CLI dispatch (Claude, Codex, Gemini, Goose) and API dispatch (OpenRouter). PAL decommissioned once registry is complete. Goose via pal clink validates multi-provider dispatch works."
]
DECISION_3::[
  QUESTION::"What's the actual critical path to cross-repo agent invocation?",
  POSITION::STEP_6,
  ANSWER::"Agent registry (Step 3) + native multi-CLI/API dispatch (Step 4) + debate-hall convene (already shipped). Step 6 is where they converge."
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
  "#279-282 (OA rebuild phases)",
  "::",
  STEP_2,
  "#284 (capability tiers)",
  "::",
  STEP_2<related>,
  "#285 (tiered permits)",
  "::",
  STEP_2<related>,
  "workbench#1 (evolve crystal)",
  "::",
  STEPS_3_through_6,
  "workbench#16 (governance chat UI)",
  "::",
  STEP_5,
  "workbench#32 (agent registry)",
  "::",
  STEP_3,
  "workbench#33 (native multi-CLI dispatch, was: clink extraction)",
  "::",
  STEP_4,
  "debate-hall#163 (governance hall)",
  "::",
  TRACK_B<parallel>,
  "debate-hall#159 (RACI mode)",
  "::",
  TRACK_B<parallel>,
  "octave-mcp#283 (Chassis-Profile RFC)",
  "::",
  TRACK_A<parallel>,
  "Project 14 (Governance Chat)",
  "::",
  "STEPS_3⊕",
  5,
  [partial_coordination],
  "Project 15 (Ecosystem Build Order)",
  "::",
  this_graph<full_coordination>
]
§8::OPERATOR_INSIGHT
NOTE::"User expressed concern about hesitancy vs. prototyping. The sequence above is designed for prototype-first: each step produces something usable, not just a plan. Step 3 produces a working agent registry. Step 4 produces working CLI dispatch. Step 6 is an explicit 'try it and see' prototype."
ANTI_PATTERN::"Building the perfect coordination system before trying anything. The graph shows dependencies, not a waterfall. Steps can overlap. Step 1 is already DONE (ADR-0275)."
===END===
