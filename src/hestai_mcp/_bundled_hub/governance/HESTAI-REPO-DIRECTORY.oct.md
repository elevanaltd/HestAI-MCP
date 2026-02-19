===HESTAI_REPO_DIRECTORY===
META:
  TYPE::REPO_DIRECTORY
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"What each repo is, what it does, where it lives, and its current state"
  UPDATED::"2026-02-19"
  RELATED::"HESTAI-ECOSYSTEM-OVERVIEW.oct.md (how they connect)"

§1::ACTIVE_REPOS

HESTAI_MCP::[
  WHAT::"Governance, context management, and session lifecycle for AI-assisted development",
  GITHUB::"elevanaltd/HestAI-MCP",
  LOCAL::"/Volumes/HestAI-MCP",
  LANG::Python,
  PACKAGE::"hestai-mcp (PyPI)",
  VERSION::"1.2.0",
  TOOLS::[clock_in,clock_out,bind,submit_review],
  STATUS::operational,
  NOTES::"Planned merge with odyssean-anchor-mcp into hestai-core-mcp. Hosts agent constitutions, skills library, governance rules in .hestai-sys/"
]

ODYSSEAN_ANCHOR_MCP::[
  WHAT::"Agent identity binding via 3-stage cryptographic-style ceremony (REQUEST→LOCK→COMMIT)",
  GITHUB::"elevanaltd/odyssean-anchor-mcp",
  LOCAL::"/Volumes/HestAI-Projects/odyssean-anchor-mcp",
  LANG::Python,
  PACKAGE::"odyssean-anchor-mcp (PyPI)",
  VERSION::"0.1.1",
  TOOLS::[anchor_request,anchor_lock,anchor_commit,anchor_micro,verify_permit],
  STATUS::operational,
  NOTES::"Will merge into hestai-core-mcp. Prevents generic drift by requiring agents prove role comprehension before operating."
]

DEBATE_HALL_MCP::[
  WHAT::"Multi-perspective reasoning via structured Wind/Wall/Door debates with hash-chain integrity",
  GITHUB::"elevanaltd/debate-hall-mcp",
  LOCAL::"/Volumes/HestAI-Projects/debate-hall-mcp",
  LANG::Python,
  PACKAGE::"debate-hall-mcp (PyPI)",
  VERSION::"0.5.0",
  TOOLS::[init_debate,add_turn,close_debate,run_debate,resume_debate,resolve_question,search_decisions,extract_decision_record,force_close_debate,tombstone_turn,github_sync_debate,ratify_rfc,human_interject,pick_next_speaker],
  STATUS::operational,
  ACTIVE_WORK::"Issue #163 (governance hall: convene/consult operations). Issue #112 (desktop app → becomes workbench panel).",
  NOTES::"Standalone. Works without HestAI for non-governance users. 800+ tests."
]

OCTAVE_MCP::[
  WHAT::"Semantic compression format for AI documents. 54-68% token reduction. Validation-before-generation.",
  GITHUB::"elevanaltd/octave-mcp",
  LOCAL::"/Volumes/OCTAVE/octave-mcp",
  LANG::Python,
  PACKAGE::"octave-mcp (PyPI)",
  VERSION::"1.2.1",
  TOOLS::[octave_validate,octave_write,octave_eject],
  STATUS::operational,
  NOTES::"Pure protocol. Zero governance dependencies. Foundation layer — all other systems use OCTAVE format."
]

HESTAI_WORKBENCH::[
  WHAT::"Desktop control panel for managing AI sessions, agent registry, worktrees, and MCP server integration",
  GITHUB::"elevanaltd/hestai-workbench",
  SOURCE::"Evolved from elevanaltd/crystal-fresh (fork of stravu/crystal)",
  LOCAL::"TBD (being set up from crystal-fresh clone)",
  LANG::"TypeScript (Electron + React + SQLite)",
  VERSION::"0.3.4 (inherited from Crystal)",
  STATUS::prototype_phase,
  ACTIVE_WORK::"Issue #1 (crystal-fresh#20): Phase 2 strip → Phase 3 agent registry → Phase 4 daily use → Phase 5 rebuild",
  NOTES::"Only GUI in the ecosystem. Manages worktrees, spawns CLIs, will host agent registry (role → provider → model)."
]

§2::TRANSITIONAL_REPOS

PAL_MCP_SERVER::[
  WHAT::"Multi-model AI orchestration bridge. Calls other AI CLIs and APIs from within a session.",
  GITHUB::"elevanaltd/pal-mcp-server (based on BeehiveInnovations/pal-mcp-server)",
  LOCAL::"/Volumes/HestAI-Tools/pal-mcp-server",
  LANG::Python,
  VERSION::"1.0.3",
  TOOLS::[chat,clink,challenge,thinkdeep,codereview,debug,planner,consensus,anchor,apilookup,precommit,listmodels,version],
  STATUS::operational_but_being_absorbed,
  DISPOSITION::"CLI dispatch → workbench. Workflow tools → replaced by agent loading. Agent prompts → hestai-core. See HESTAI-ECOSYSTEM-OVERVIEW.oct.md §2 SYSTEM_5.",
  NOTES::"45 commits ahead of stalled upstream. Currently useful for multi-provider calls via clink. 55+ agent prompt files duplicated from hestai-core."
]

CRYSTAL_FRESH::[
  WHAT::"Original Crystal fork with 74 custom commits. Being replaced by hestai-workbench.",
  GITHUB::"elevanaltd/crystal-fresh",
  LOCAL::"/Volumes/HestAI-Tools/crystal-fresh",
  LANG::"TypeScript (Electron + React + SQLite)",
  VERSION::"0.3.4",
  STATUS::being_replaced,
  NOTES::"Still in daily use during workbench prototype phase. Upstream (stravu/crystal) abandoned — authors moved to closed-source Nimbalyst. 74 commits ahead of upstream. Issues tracked here until workbench repo is primary."
]

§3::QUICK_LOOKUP

BY_CONCERN::[
  "Agent identity/prompts/skills → hestai-mcp + odyssean-anchor-mcp (merging)",
  "Debates/decisions → debate-hall-mcp",
  "Document format → octave-mcp",
  "Desktop UI/sessions/worktrees → hestai-workbench (crystal-fresh during transition)",
  "Multi-provider model calls → pal-mcp-server (temporary)"
]

BY_LOCAL_PATH::[
  "/Volumes/HestAI-MCP → hestai-mcp",
  "/Volumes/HestAI-Projects/odyssean-anchor-mcp → odyssean-anchor-mcp",
  "/Volumes/HestAI-Projects/debate-hall-mcp → debate-hall-mcp",
  "/Volumes/OCTAVE/octave-mcp → octave-mcp",
  "/Volumes/HestAI-Tools/pal-mcp-server → pal-mcp-server",
  "/Volumes/HestAI-Tools/crystal-fresh → crystal-fresh (→ hestai-workbench)"
]

===END===
