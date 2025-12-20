===LOAD2===
// /load2 {role} [--quick|--untracked]
// Role activation v2.1 - State-Vector Cognitive Attenuation

CRITICAL::[
  TodoWrite_FIRST→enforces_sequential,
  EXACT_tool_names→no_hallucination,
  NO_PROSE→silent_execution_between_steps,
  RAPH_VECTOR_MANDATE→force_tension_synthesis
]

ALIASES::[
  ho→holistic-orchestrator,ce→critical-engineer,il→implementation-lead,
  ta→technical-architect,ea→error-architect,ca→completion-architect,
  wa→workspace-architect,ss→system-steward,rs→requirements-steward,
  td→task-decomposer,cr→code-review-specialist,crs→code-review-specialist,
  tmg→test-methodology-guardian,testguard→test-methodology-guardian,
  tis→test-infrastructure-steward,test-steward→test-infrastructure-steward,
  ute→universal-test-engineer,test→universal-test-engineer
]

FLAGS::[--quick→QUICK_MODE, --untracked→UNTRACKED_MODE]

---

FLOW[DEFAULT]:
  TODOS::[
    {content:"T1: Constitution",status:"in_progress",activeForm:"Locking anchor"},
    {content:"T2: Clock in",status:"pending",activeForm:"Registering session"},
    {content:"T3: Context + Git",status:"pending",activeForm:"Loading context"},
    {content:"T4: Anchor submit",status:"pending",activeForm:"Validating"},
    {content:"T5: Skill Injection",status:"pending",activeForm:"Priming state machine"},
    {content:"T6: RAPH Vector",status:"pending",activeForm:"Generating cognitive binding"},
    {content:"T7: Dashboard",status:"pending",activeForm:"Summary"}
  ]

  T1_CONSTITUTION:
    DO::Read(".claude/agents/{role}.oct.md")
    EXTRACT::[COGNITION,ARCHETYPES,CORE_FORCES,MUST_ALWAYS[2],MUST_NEVER[2]]
    EMIT::="🔒 ANCHOR: {role} | {COGNITION} | {ARCHETYPES}"

  T2_CLOCKIN[FAIL_HARD]:
    IF[UNTRACKED]→SKIP+WARN:"⚠️ UNTRACKED: No session"→T3
    DO::mcp__hestai__clockin(role:{ROLE},focus:"general",working_dir:"{cwd}")
    CAPTURE::[SESSION_ID,CONTEXT_PATHS,CONFLICT]
    IF[CONFLICT]→WARN:"⚠️ Conflict: {conflict.existing_session}"
    IF[FAIL]→STOP:"❌ CLOCK_IN FAILED - Use '/load {role} --untracked'"
    EMIT::="📋 SESSION: {SESSION_ID}"

  T3_CONTEXT:
    DO::Read[CONTEXT_PATHS.project_context,CONTEXT_PATHS.checklist]
    DO::Bash("git log --oneline -5 && git status -s && git branch --show-current")
    DO::Bash("echo AHEAD:$(git rev-list --count origin/main..HEAD 2>/dev/null||echo 0) BEHIND:$(git rev-list --count HEAD..origin/main 2>/dev/null||echo 0)")
    EXTRACT::[CURRENT_PHASE,ACTIVE_WORK,BLOCKERS,UNCOMMITTED_FILES,STALE_SESSIONS]
    EMIT::="📄 CONTEXT: {CURRENT_PHASE} | 🌳 {branch} ({ahead}↑{behind}↓)"

  T4_ANCHOR[SOFT_FAIL]:
    IF[UNTRACKED]→SKIP→T5
    DO::mcp__hestai__anchorsubmit(session_id:{SESSION_ID},working_dir:"{cwd}",anchor:{SHANK:{role,cognition,archetypes,key_constraints},ARM:{phase_context,current_focus,blockers},FLUKE:{skills_loaded,patterns_active}})
    CAPTURE::[VALIDATED,ENFORCEMENT.blocked_paths,ENFORCEMENT.delegation_required]
    IF[FAIL]→WARN:"⚠️ Anchor failed - proceeding without enforcement"
    EMIT::="🔐 ENFORCE: Blocked:{blocked_paths} | Delegate:{delegation_required}"

  T5_SKILL_INJECTION:
    DO::Read(".claude/skills/raph-vector/SKILL.md")
    EMIT::="🧠 SKILL: RAPH_VECTOR v2.3 Protocol Loaded"

  T6_RAPH_VECTOR_GENERATION:
    INSTRUCTION::"GENERATE the `===RAPH_VECTOR::v2.3===` state machine block NOW. You MUST populate the ARM section with specific data. DO NOT output any text, summaries, or 'Key Focus' lists outside the vector block."
    EXECUTE::GENERATE_RAPH_VECTOR

  T7_DASHBOARD:
    EMIT::DASHBOARD_BLOCK[see_format_below]

---

DASHBOARD_FORMAT:
  DEFAULT::
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ LOAD v2.3 COMPLETE
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎭 ROLE:    {role} ({cognition}) | {archetypes}
    📋 SESSION: {session_id}
    📊 PROJECT: {phase} | {branch}
    🧠 RAPH:    VECTOR v2.3 ACTIVE (See block above)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

NEVER::[
  prose_between_steps,
  transition_commentary,
  self_reflection,
  codebase_packing_on_load,
  explanatory_text_around_emissions
]

ALWAYS::[
  TodoWrite_before_execution,
  mark_complete_immediately_after_step,
  silent_progression_between_tiers,
  EMIT_only_specified_format
]

===END===

**Execute load2 for: $ARGUMENTS**
