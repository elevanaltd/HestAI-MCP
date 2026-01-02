===BIND===
// /bind {role} ["topic"] [--quick|--deep]
// Agent identity binding v4.0 - Odyssean Anchor Protocol
// Uses odyssean_anchor MCP tool for server-side validation
//
// USAGE:
//   /bind ho                      - Bind as holistic-orchestrator with general focus
//   /bind ho "implement feature"  - Bind with specific topic/focus
//   /bind il --quick              - Quick bind (1 tension minimum)
//   /bind ta "review ADR" --deep  - Deep bind with topic (3 tensions minimum)
//
// INSTALLATION:
//   Copy this file to ~/.claude/commands/bind.md
//   Or use as project-specific command in .claude/commands/

CRITICAL::[
  TodoWrite_FIRST->enforces_sequential,
  EXACT_tool_names->no_hallucination,
  NO_PROSE->silent_execution_between_steps,
  AUDITABLE_REGIONS->machine_sliceable_blocks_only,
  AUTHORITY_GATE->HALT_on_blocked_touch,
  TENSION_IS_PROOF->agent_interprets_not_copies
]

ALIASES::[
  ho->holistic-orchestrator,ce->critical-engineer,il->implementation-lead,
  ta->technical-architect,ea->error-architect,ca->completion-architect,
  wa->workspace-architect,ss->system-steward,rs->requirements-steward,
  td->task-decomposer,cr->code-review-specialist,crs->code-review-specialist,
  tmg->test-methodology-guardian,testguard->test-methodology-guardian,
  tis->test-infrastructure-steward,test-steward->test-infrastructure-steward,
  ute->universal-test-engineer,test->universal-test-engineer
]

FLAGS::[
  --quick->TIER_QUICK[1_tension_min],
  --deep->TIER_DEEP[3_tensions_min],
  DEFAULT->TIER_DEFAULT[2_tensions_min]
]

PARSE_RULES::[
  ROLE_TOKEN::first_non_flag_non_quoted_token,
  TOPIC_TOKEN::first_quoted_string_or_null,
  TIER_TOKEN::flag_if_present_else_DEFAULT,
  FOCUS::TOPIC_TOKEN_or_"general"
]

AUDITABLE_REGIONS::[
  VECTOR_REGION::"===RAPH_VECTOR::v4.0==="->"===END_RAPH_VECTOR===",
  BIND_END::"===END_BIND_SEQUENCE==="
]

---

FLOW[DEFAULT]:
  TODOS::[
    {content:"T0: TodoWrite",status:"in_progress",activeForm:"Sequencing"},
    {content:"T1: Constitution -> BIND",status:"pending",activeForm:"Extracting identity"},
    {content:"T2: clock_in -> ARM",status:"pending",activeForm:"Injecting context"},
    {content:"T3: Generate TENSION",status:"pending",activeForm:"Interpreting context"},
    {content:"T4: Declare COMMIT",status:"pending",activeForm:"Stating contract"},
    {content:"T5: Odyssean Anchor",status:"pending",activeForm:"MCP validation"},
    {content:"T6: Dashboard",status:"pending",activeForm:"Summary"}
  ]

  T0_TODOWRITE:
    DO::TodoWrite(TODOS)
    DO::TodoMarkComplete("T0: TodoWrite")

  T1_CONSTITUTION_BIND:
    DO::Read(".claude/agents/{role}.oct.md")
    EXTRACT::[COGNITION,ARCHETYPES,MUST_ALWAYS[2],MUST_NEVER[2]]
    // Determine AUTHORITY based on invocation context
    IF[main_agent]->SET::AUTHORITY="RESPONSIBLE"
    IF[subagent]->SET::AUTHORITY="DELEGATED[{parent_session}]"
    EMIT::="BIND: {role} | {COGNITION}::{ARCHETYPES} | {AUTHORITY}"
    DO::TodoMarkComplete("T1: Constitution -> BIND")

  T2_CLOCKIN_ARM:
    // FOCUS comes from quoted topic or defaults to "general"
    DO::mcp__hestai__clock_in(role:{ROLE},focus:{FOCUS},working_dir:"{cwd}")
    CAPTURE::[SESSION_ID,CONTEXT_PATHS]
    IF[FAIL]->STOP:"ERR: CLOCK_IN FAILED"

    // MCP injects ARM context - agent does NOT generate this
    DO::Read("{CONTEXT_PATHS.project_context}")
    DO::Bash("git log --oneline -3 && git status -s && git branch --show-current")
    DO::Bash("echo AHEAD:$(git rev-list --count origin/main..HEAD 2>/dev/null||echo 0) BEHIND:$(git rev-list --count HEAD..origin/main 2>/dev/null||echo 0)")
    EXTRACT::[PHASE,BRANCH,AHEAD,BEHIND,FILES_MODIFIED]

    EMIT::="ARM: {PHASE} | {BRANCH}[{AHEAD}↑{BEHIND}↓] | {FILES_MODIFIED} files"
    IF[FOCUS!="general"]->EMIT::="FOCUS: {FOCUS}"
    DO::TodoMarkComplete("T2: clock_in -> ARM")

  T3_GENERATE_TENSION:
    // KEY INSIGHT: Agent INTERPRETS ARM->constraints, does not copy
    // This citation IS the cognitive proof
    // If FOCUS is set, tensions should relate to that focus
    INSTRUCTION::"Generate TENSION section. Requirements:
      - QUICK: MIN 1 tension; DEFAULT: MIN 2 tensions; DEEP: MIN 3 tensions
      - Format: L{N}::[{constraint_from_constitution}]↔CTX:{path}[{state}]->TRIGGER[{action}]
      - Must cite ACTUAL files/state from ARM (T2)
      - Must reference constitutional line numbers (L{N})
      - If FOCUS is set, tensions should relate to that work focus
      - Proves you understand constraint↔reality implications"
    EXECUTE::GENERATE_TENSIONS
    DO::TodoMarkComplete("T3: Generate TENSION")

  T4_DECLARE_COMMIT:
    // Falsifiable contract: what artifact will be produced?
    // If FOCUS is set, COMMIT should align with that focus
    INSTRUCTION::"Declare COMMIT. Requirements:
      - ARTIFACT: Concrete file path or tool output (not 'response' or 'thoughts')
      - GATE: Validation method (test command, lint, manual review)
      - If FOCUS is set, COMMIT should address that work focus"
    EXECUTE::DECLARE_COMMIT
    DO::TodoMarkComplete("T4: Declare COMMIT")

  T5_ODYSSEAN_ANCHOR:
    // Server-side validation via odyssean_anchor MCP tool
    // Build vector_candidate from T1 (BIND), T3 (TENSION), T4 (COMMIT)
    BUILD::VECTOR_CANDIDATE::[
      "## BIND (Identity + Authority Lock)",
      "ROLE::{role}",
      "COGNITION::{cognition}::{archetypes}",
      "AUTHORITY::{authority}",
      "",
      "## TENSION (Cognitive Proof - Agent Generated)",
      "{tensions_from_T3}",
      "",
      "## COMMIT (Falsifiable Contract)",
      "ARTIFACT::{artifact_from_T4}",
      "GATE::{gate_from_T4}"
    ]

    DO::mcp__hestai__odyssean_anchor(
      role:{ROLE},
      vector_candidate:{VECTOR_CANDIDATE},
      session_id:{SESSION_ID},
      working_dir:"{cwd}",
      tier:{TIER}
    )
    CAPTURE::[success,anchor,errors,guidance,retry_count,terminal]

    IF[success==false && terminal==false]::[
      EMIT::={guidance},
      INSTRUCTION::"Fix errors per guidance and regenerate",
      RETRY::T3_GENERATE_TENSION[max_2_retries]
    ]
    IF[success==false && terminal==true]::[
      EMIT::="BINDING FAILED (max retries exceeded)",
      STOP::human_intervention_required
    ]
    IF[success==true]::[
      CAPTURE::VALIDATED_ANCHOR={anchor}
    ]
    DO::TodoMarkComplete("T5: Odyssean Anchor")

  T6_DASHBOARD:
    EMIT::VECTOR_BLOCK[see_format_below]
    EMIT::DASHBOARD_BLOCK[see_format_below]
    DO::TodoMarkComplete("T6: Dashboard")

---

VECTOR_FORMAT:
  // 4-Section Minimum Viable Anchor (debate consensus)
  STRUCTURE::
    ===RAPH_VECTOR::v4.0===

    ## BIND (Identity + Authority Lock)
    ROLE::{agent_name}
    COGNITION::{type}::{archetype}
    AUTHORITY::{RESPONSIBLE|DELEGATED[parent_session]}

    ## ARM (Context Proof - MCP Injected)
    // Server-authoritative - injected by odyssean_anchor
    PHASE::{current_phase}
    BRANCH::{name}[{ahead}↑{behind}↓]
    FILES::{count}[{top_modified}]
    FOCUS::{focus_topic_or_general}

    ## TENSION (Cognitive Proof - Agent Generated)
    L{N}::[{constitutional_constraint}]↔CTX:{path}[{state}]->TRIGGER[{action}]

    ## COMMIT (Falsifiable Contract)
    ARTIFACT::{file_path|tool_output}
    GATE::{validation_method}

    ===END_RAPH_VECTOR===

  VALIDATION_RULES::[
    has_all_sections([BIND,ARM,TENSION,COMMIT]),
    tension_count_meets_tier,
    each_tension_has("L"),
    each_tension_has("CTX:"),
    commit_artifact_is_concrete
  ]

DASHBOARD_FORMAT:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK BIND COMPLETE
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ROLE:    {role} ({cognition}) | {archetypes}
  SESSION: {session_id}
  PROJECT: {phase} | {branch} ({ahead}↑{behind}↓)
  FOCUS:   {focus}
  ANCHOR:  VALIDATED (MCP)
  TIER:    {TIER_QUICK? "QUICK" : (TIER_DEEP? "DEEP":"DEFAULT")}
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ===END_BIND_SEQUENCE===

---

NEVER::[
  prose_between_steps,
  transition_commentary,
  copy_paste_git_status_as_proof,
  generic_tensions_without_CTX_citation,
  COMMIT_artifact_as_response_or_thoughts,
  generate_ARM_section[server_authoritative]
]

ALWAYS::[
  TodoWrite_before_execution,
  mark_complete_immediately_after_step,
  TENSION_interprets_ARM_not_copies,
  COMMIT_names_concrete_artifact,
  silent_progression_between_steps,
  use_mcp__hestai__odyssean_anchor_for_validation
]

PHILOSOPHY::
  // From "Form to Fill" -> "Handshake of Truth"
  // Identity carries authority
  // Context is injected (ARM from MCP)
  // Cognition is proven through interpretation (TENSION)
  // Commitment is falsifiable (COMMIT)

REFERENCES::[
  ADR_0036::"docs/adr/adr-0036-odyssean-anchor-binding.md",
  MCP_TOOL::"src/hestai_mcp/mcp/tools/odyssean_anchor.py",
  NORTH_STAR::".hestai/workflow/components/000-ODYSSEAN-ANCHOR-NORTH-STAR.md"
]

===END===

**Execute bind for: $ARGUMENTS**
