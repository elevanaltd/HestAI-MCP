===DEPENDENCY_GRAPH===
META:
  TYPE::ECOSYSTEM_DEPENDENCY_GRAPH
  VERSION::"4.3"
  STATUS::TARGET
  PURPOSE::"Cross-system build sequence, blocking relationships, and phase alignment"
  CREATED::"2026-02-22"
  REVISED::"2026-04-20"
  FORMAT::octave
  RESOLVES::"#265 (Cross-repo ecosystem dependency graph)"
  SUPPLEMENTS::HESTAI-ECOSYSTEM-OVERVIEW.oct.md
  ARCHITECTURE::"THREE_SERVICE_MODEL<ADR-0353>"
§0::PREAMBLE
CONTEXT::"Single developer + AI agents. Three-Service Model architecture (ADR-0353) — Workbench (Eyes and Hands), Vault (DNA), hestai-context-mcp (Memory and Environment). Two standalone MCP servers: debate-hall, octave-mcp. Legacy systems (hestai-mcp, OA, PAL) stay for A/B comparison."
ARCHITECTURE_DECISION::"Thick Client model (v3.0) replaced by Three-Service Model (v4.0). See ADR-0353 (2026-04-06). Identity injection via Alley-Oop pattern in Payload Compiler. Context management via hestai-context-mcp stdio MCP."
PREVIOUS_MODEL::"v3.0 described 9-step absorption build sequence where workbench absorbs hestai-mcp and OA. CORRECTED: Workbench owns dispatch only. Governance engine harvested into hestai-context-mcp. Agent identity moves to Vault."
ONTOLOGY_AMENDMENT::"ADR-0002 I1 amendment (accepted 2026-04-20 via workbench commit 077ea0a): Session/Dispatch ontology separation. API_DISPATCH is I1-by-exemption — API-dispatched agents inherit I1 (Persistent Cognitive Continuity) semantics through their parent session context rather than owning an independent session, because they are stateless advisory calls routed via OpenRouter. See §3 LAYER_4 and §6 DECISION_5 for application."
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
  PHASE::"3A+3B Phase 2 shipped 2026-04-20; 3B Phase 3 in progress (egress DAL, dispatch_colleague recursion, dispatch-chain UI #82)",
  HEALTH::COMPILES,
  CODEBASE::"65,792 LOC TypeScript/TSX (Electron + React)",
  WHAT_EXISTS::[
    "Matrix resolver (v_resolved_matrix with kernel_only column)",
    "5 V9 agents (IL, CRS, HO, ideator, ho-control-room via #147) with skills/patterns/kernel_only assignments",
    "16 V9 skills with S5 ANCHOR_KERNEL sections",
    "System Standard in vault (AP4 resolved)",
    "Multi-session management with Claude, Codex, Goose CLI support",
    "Git worktree isolation per session",
    "Agent Registry: DB schema, parser (V8+V9), sync, IPC, Glass UI",
    "Library Vault: LIBRARY_ROOT config, bootstrap service, auto-commit on Glass save",
    "Payload Compiler (Step 3A) operational",
    "DispatchService Phase 1 merged: CA-BCE + unlock_work gate (#134)",
    "DispatchService Phase 2 merged 2026-04-20: ApiDispatcher + ContinuationStore (#137), subagent-discipline (#147)",
    "ADR-0002 I1 amendment integrated (Session/Dispatch ontology, commit 077ea0a)"
  ],
  BLOCKERS::none_technical,
  KEY_FACT::"Target platform for dispatch and UI. Step 3B Phase 2 complete 2026-04-20. Phase 3 in progress: egress DAL validation, recursive dispatch_colleague, dispatch-chain UI (#82)."
]
VAULT::[
  LOCATION::"~/.hestai-workbench/library/",
  HEALTH::POPULATED,
  CONTENTS::[
    "5 V9 agents (IL, CRS, HO, ideator, ho-control-room — ho-control-room landed via PR #147 on 2026-04-20)",
    "16 V9 skills with ANCHOR_KERNEL sections",
    "3 cognitions (ETHOS, PATHOS, LOGOS)",
    "System Standard (AP4 resolved)"
  ],
  KEY_FACT::"Git-backed, immutable at runtime. Workbench reads directly. Glass Agent Editor provides CRUD with auto-commit."
]
HESTAI_CONTEXT_MCP::[
  STATUS::"Phase 1 COMPLETE — elevanaltd/hestai-context-mcp repo created and shipped 2026-04-17. 4 MCP tools operational (clock_in, clock_out, get_context, submit_review). TranscriptParser ABC + ClaudeTranscriptParser adapter. ADR-0353 accepted. Interface contract done.",
  REPO::"elevanaltd/hestai-context-mcp (IMPLEMENTED)",
  VERSION::"1.0.0",
  PHASE::B1_FOUNDATION_COMPLETE,
  HEALTH::FUNCTIONAL,
  TESTS::"361 passing, 89 percent coverage",
  TOOLS::[
    clock_in,
    clock_out,
    get_context,
    submit_review
  ],
  PRE_AB_WORK::"Phase 1.5 integration-viability gaps tracked in elevanaltd/hestai-context-mcp issues #4 (P0a ai_synthesis field + phase normalisation), #5 (P0b AIClient port), #6 (P1 North Star structured constraint extraction), #7 (P-side conflicts field). Required so the Payload Compiler can read both backends' responses. NOT structural-parity work — outcome-quality A/B is the goal.",
  AI_SYNTHESIS_FRAMING::"Legacy has working AI synthesis when configured; new repo currently lacks the path entirely (covered by P0b/issue #5). Without API keys, both produce structured non-AI output.",
  PHANTOMS_NOT_GAPS::["ContextSteward and dynamic phase constraints (core/context_steward.py:36-184 + tests) — implemented","Focus conflict detection (core/session.py:91-128 + 4 behavioural tests) — implemented"],
  KEY_FACT::"Harvested from hestai-mcp (clock_in harvested, clock_out redesigned with provider adapter pattern). Owns clock_in, clock_out, get_context, submit_review, ContextSteward, RedactionEngine. Stdio MCP transport. Legacy hestai-mcp stays intact for outcome-quality A/B comparison."
]
HESTAI_MCP_LEGACY::[
  VERSION::"1.2.0",
  PHASE::B1_FOUNDATION,
  HEALTH::FUNCTIONAL,
  TESTS::"1033 passing, maintenance mode",
  TOOLS::[
    clock_in,
    clock_out,
    bind,
    submit_review,
    submit_rccafp_record
  ],
  STATUS::legacy_stays_for_AB_comparison,
  DEPRECATION_CRITERION::"DECIDED 2026-04-20 — A/B cutover via Workbench. Same agent role + same real task; run once with legacy backend, run once with hestai-context-mcp backend; measure judged agent output quality + total session token cost. Repeat across N tasks. Whichever wins consistently triggers swift cutover.",
  KEY_FACT::"NOT being absorbed. Governance engine logic harvested into hestai-context-mcp (Phase 1 complete 2026-04-17). Legacy stays for outcome-quality A/B comparison."
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
LAYER_2::"IDENTITY — Vault: POPULATED, git-backed, 5 V9 agents (ho-control-room added 2026-04-20 via PR #147). ACTION: Populate as Payload Compiler demands content."
LAYER_3::"CONTEXT — hestai-context-mcp: Phase 1 COMPLETE (2026-04-17). 4 tools operational, 361 tests, 89 percent coverage. ACTION: Phase 1.5 Pre-A/B Work (issues #4 P0a, #5 P0b, #6 P1, #7 P-side) closes integration-viability gaps so the Payload Compiler can read both backends' responses. Then Phase 2 — workbench Payload Compiler integration via stdio at KVAEPH Position 3 (blocked on workbench Step 3B Phase 3). Framing: outcome-quality A/B, NOT structural-parity A/B — backends are allowed to differ; that difference is the variable being tested."
LAYER_4::"DISPATCH — hestai-workbench: Step 3A COMPLETE (Payload Compiler). Step 3B Phase 1 MERGED (#134 CA-BCE + unlock_work gate). Step 3B Phase 2 MERGED 2026-04-20 (#137 ApiDispatcher + ContinuationStore, #147 subagent-discipline, 077ea0a ADR-0002 I1 amendment). I1-BY-EXEMPTION: API_DISPATCH inherits I1 semantics through the parent session's continuity rather than owning an independent Session — accepted in ADR-0002 Session/Dispatch ontology amendment. Step 3B Phase 3 IN PROGRESS: egress DAL validation, recursive dispatch_colleague, dispatch-chain UI (#82)."
§3b::PRE_AB_WORK_FOR_HESTAI_CONTEXT_MCP
PURPOSE::"Phase 1.5 integration-viability gaps that block meaningful outcome-quality A/B testing"
FRAMING::"Outcome-quality A/B (judged agent output + token cost), NOT structural-parity A/B. Systems are explicitly allowed to differ in actual content; that difference is the variable being tested. Parity work is limited to what the Payload Compiler needs to read both backends' responses."
ITEMS::[
  "P0a::issue#4 — add ai_synthesis field with fallback OCTAVE; normalise phase string to legacy's full format",
  "P0b::issue#5 — port AIClient + synthesize_fast_layer_with_ai from legacy src/hestai_mcp/modules/services/ai/",
  "P1::issue#6 — harvest _extract_north_star_constraints (legacy clock_in.py:525-583); tests must exercise real Vault North Star format",
  "P-side::issue#7 — surface distinct conflicts field rather than only active_sessions"
]
PHANTOMS_NOT_GAPS::["ContextSteward and dynamic phase constraints (core/context_steward.py:36-184 + tests) — implemented","Focus conflict detection (core/session.py:91-128 + 4 behavioural tests) — implemented"]
ISSUE_TRACKER::"elevanaltd/hestai-context-mcp issues #4, #5, #6, #7"
DECIDED::"2026-04-20"
§4::SEQUENCED_BUILD_ORDER
STEP_3A::[
  WHAT::"Payload Compiler in workbench",
  STATUS::COMPLETE,
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
  STATUS::"Phase 1 MERGED (#134); Phase 2 MERGED 2026-04-20 (#137, #147, 077ea0a); Phase 3 IN PROGRESS",
  RATIONALE::"dispatch_colleague MCP tool uses Payload Compiler to spawn agents with identity via any CLI tool. Dispatch service validates dynamic anchor output (regex on cognitive grammar headers). Continuation model with dispatch_id. Phase 2 shipped CA-BCE, ApiDispatcher, ContinuationStore, subagent-discipline skill, and ADR-0002 I1-by-exemption ontology.",
  EFFORT::"medium — dispatch service, CLI spawning, API dispatch, continuation store",
  PHASE_1::"MERGED — #134 CA-BCE + unlock_work gate",
  PHASE_2::"MERGED 2026-04-20 — #137 ApiDispatcher + ContinuationStore; #147 subagent-discipline; 077ea0a ADR-0002 I1 Session/Dispatch ontology (API_DISPATCH I1-by-exemption)",
  PHASE_3::"IN PROGRESS — egress DAL validation, recursive dispatch_colleague, dispatch-chain UI (workbench #82)",
  PREREQ::STEP_3A,
  BLOCKS::[STEP_4,HARVEST_PHASE_2]
]
STEP_4::[
  WHAT::"Testing Lab — empirical validation",
  RATIONALE::"Measures exact threshold where baseline focus collapses. Proves synthetic threading recovery efficacy. Validates Alley-Oop vs OA ceremony A/B.",
  EFFORT::"medium — test harness, measurement framework, empirical analysis",
  PREREQ::STEP_3B,
  WORKBENCH_ISSUE::"#98"
]
HARVEST_PHASE_1::[
  WHAT::"Create hestai-context-mcp repo and harvest clock_in — DONE 2026-04-17",
  STATUS::COMPLETE,
  RATIONALE::"New repo (elevanaltd/hestai-context-mcp) created. clock_in harvested from hestai-mcp. clock_out REDESIGNED with provider adapter pattern (TranscriptParser ABC + ClaudeTranscriptParser) rather than harvested as-is. get_context built. Legacy hestai-mcp stays intact for A/B comparison. Delivered: 4 tools, 361 tests, 89% coverage in 8 days — validates EA10.",
  EVIDENCE::"~20 commits, 4 PRs merged. git log verified 2026-04-17.",
  PARALLEL_WITH::STEP_3A,
  BLOCKS::[HARVEST_PHASE_1_5]
]
HARVEST_PHASE_1_5::[
  WHAT::"Pre-A/B integration-viability work in hestai-context-mcp",
  STATUS::"PLANNED — issues #4, #5, #6, #7 created 2026-04-20",
  RATIONALE::"Close integration-viability gaps (ai_synthesis field, AIClient port, North Star constraint extraction, conflicts field) so the Payload Compiler can read both backends' responses and the outcome-quality A/B test becomes meaningful. NOT structural parity — backends are allowed to differ in content.",
  EFFORT::"small-to-medium — 4 issues, mostly harvest from legacy",
  PARALLEL_WITH::STEP_3B,
  BLOCKS::[HARVEST_PHASE_2]
]
HARVEST_PHASE_2::[
  WHAT::"Workbench Payload Compiler calls hestai-context-mcp for Position 3 — NEXT",
  STATUS::PENDING,
  RATIONALE::"Thin stdio MCP client in Payload Compiler. Spawn python -m hestai_context_mcp via stdio. Inject clock_in output at KVAEPH Position 3. BLOCKED on workbench Step 3B Phase 3 completion AND hestai-context-mcp Phase 1.5 Pre-A/B Work.",
  EFFORT::"small — stdio MCP client (~30 lines), integration",
  PREREQ::[
    STEP_3A,
    HARVEST_PHASE_1,
    HARVEST_PHASE_1_5,
    STEP_3B
  ]
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
  PARALLEL_WITH::STEP_3B
]
PAL_DECOMMISSION::[
  WHAT::"PAL decommission + legacy deprecation",
  RATIONALE::"After workbench fully replaces all PAL dispatch capabilities. hestai-mcp deprecated (not archived) after outcome-quality A/B proves new system wins consistently across N tasks.",
  EFFORT::"small — decommission and deprecation",
  PREREQ::[
    STEP_3B,
    HARVEST_PHASE_2,
    AB_TEST_VICTORY
  ]
]
§5::CRITICAL_PATH
CRITICAL_PATH::"STEP_3A (Payload Compiler, COMPLETE) then STEP_3B (dispatch_colleague: Phase 1+2 MERGED 2026-04-20, Phase 3 IN PROGRESS) then STEP_4 (Testing Lab). In parallel: HARVEST_PHASE_1 (hestai-context-mcp, COMPLETE) then HARVEST_PHASE_1_5 (Pre-A/B integration viability) feeds into HARVEST_PHASE_2 which integrates with STEP_3A."
EXPLANATION::"Step 3A complete. Step 3B Phase 1 and Phase 2 both merged 2026-04-20, landing CA-BCE + unlock_work gate (#134), ApiDispatcher + ContinuationStore (#137), subagent-discipline (#147), and ADR-0002 I1 Session/Dispatch ontology amendment (commit 077ea0a). Phase 3 now in progress: egress DAL validation, recursive dispatch_colleague, dispatch-chain UI (#82). HARVEST_PHASE_1_5 closes integration-viability gaps (issues #4/#5/#6/#7), HARVEST_PHASE_2 wires hestai-context-mcp into the Payload Compiler at Position 3."
VISUAL::[
  "  octave-mcp (solid)          debate-hall (solid, own pace)",
  "       |                            |",
  "  VAULT (populated, 5 agents)       |",
  "       |                            |",
  "  STEP 3A: Payload Compiler    GLASS UI (parallel)",
  "       |         \\                   |",
  "  STEP 3B:    HARVEST Phase 1       |",
  "  dispatch     (hestai-context-mcp) |",
  "  _colleague        |               |",
  "  P1+P2 MERGED HARVEST Phase 1.5    |",
  "  P3 IN PROG   (Pre-A/B issues      |",
  "       |        #4 #5 #6 #7)        |",
  "       |            |               |",
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
  TRACK_C::"Glass UI panels (parallel with 3B Phase 3, feeds governance chat)",
  TRACK_D::"hestai-context-mcp harvest (parallel with 3B Phase 3, feeds Position 3 integration)"
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
  STATUS::"RESOLVED by ADR-0353; deprecation criterion DECIDED 2026-04-20",
  ANSWER::"Legacy stays for outcome-quality A/B comparison via Workbench. Same agent role + same real task: run once with legacy backend, run once with hestai-context-mcp backend; measure judged agent output quality + total session token cost. Repeat across N tasks. Whichever wins consistently triggers swift cutover. Governance engine logic harvested into hestai-context-mcp. Library content (_bundled_hub) moves to Vault. NOT being absorbed into Workbench. Worktree pattern confirmed (Workbench + worktrees, same as legacy workflow). PyPI publication is internal-first — publish externally only after A/B proves the system."
]
DECISION_4::[
  QUESTION::"Does the on-disk structure change?",
  STATUS::unchanged,
  ANSWER::"No. .hestai-sys/ (governance, read-only), .hestai/ (project context, committed), .hestai/state/ (working state) all persist. .hestai-sys/ writer changes from hestai-mcp to Workbench (from Vault). .hestai/state/ writer changes from hestai-mcp to hestai-context-mcp. Format stays OCTAVE."
]
DECISION_5::[
  QUESTION::"How does identity injection work without the anchor ceremony?",
  STATUS::"RESOLVED — Alley-Oop pattern (AP3); ADR-0002 I1 amendment ACCEPTED 2026-04-20",
  ANSWER::"Payload Compiler reads Vault, assembles KVAEPH, constructs synthetic threading with prefilled proof, demands Dynamic Anchor Lock. Agent must emit cognitive grammar headers. MCP_NOT_REQUIRED — validation is regex on output, not server round-trip. OA MCP remains for Claude-with-MCP sessions. ADR-0002 I1 Session/Dispatch ontology amendment (commit 077ea0a): API_DISPATCH is I1-by-exemption — stateless advisory API calls inherit I1 continuity semantics through their parent session rather than owning a separate Session; CLI_DISPATCH remains I1-owning. This resolves the ontological ambiguity raised when ApiDispatcher landed via #137."
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
  "workbench#99 (Payload Compiler)::STEP_3A_COMPLETE",
  "workbench#33 (native dispatch)::STEP_3B",
  "workbench#82 (dispatch-chain UI + recursive dispatch_colleague)::STEP_3B_PHASE_3_IN_PROGRESS",
  "workbench#98 (Testing Lab)::STEP_4",
  "workbench#36 (PAL decommission)::PAL_DECOMMISSION",
  "workbench#104 (matrix resolver)::DONE_PR_107",
  "workbench#111 (git status fixes)::DONE_PR_111",
  "workbench#112 (IL coverage gap)::DONE_PR_112",
  "workbench#134 (CA-BCE + unlock_work gate)::STEP_3B_PHASE_1_MERGED",
  "workbench#137 (ApiDispatcher + ContinuationStore)::STEP_3B_PHASE_2_MERGED_2026-04-20",
  "workbench#147 (subagent-discipline; ho-control-room V9 agent)::STEP_3B_PHASE_2_MERGED_2026-04-20",
  "workbench@077ea0a (ADR-0002 I1 Session/Dispatch ontology amendment)::ACCEPTED_2026-04-20",
  "debate-hall#163 (governance hall)::TRACK_B parallel",
  "hestai-context-mcp#4 (P0a ai_synthesis + phase normalisation)::HARVEST_PHASE_1_5",
  "hestai-context-mcp#5 (P0b AIClient port)::HARVEST_PHASE_1_5",
  "hestai-context-mcp#6 (P1 North Star structured constraint extraction)::HARVEST_PHASE_1_5",
  "hestai-context-mcp#7 (P-side conflicts field)::HARVEST_PHASE_1_5",
  "Project 15 (Ecosystem Build Order)::this_graph full_coordination"
]
§8::OPERATOR_INSIGHT
DIRECTION::"Three-Service Model (ADR-0353) reflects the resolved architecture: Workbench compiles and dispatches (Eyes and Hands), Vault stores identity (DNA), hestai-context-mcp manages session lifecycle and context (Memory and Environment). Step 3A is COMPLETE; Step 3B Phase 1 and Phase 2 both merged 2026-04-20; Phase 3 now in progress (egress DAL, recursive dispatch_colleague, dispatch-chain UI #82). In parallel, hestai-context-mcp Phase 1.5 closes Pre-A/B integration-viability gaps (issues #4/#5/#6/#7)."
ANTI_PATTERN::"Building governance logic into the Workbench. Governance belongs in hestai-context-mcp (proven Python, stdio transport, survives rebuilds). The Workbench is volatile — it will be rebuilt. Keep it thin: compile, dispatch, display."
===END===
