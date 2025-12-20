===LOAD===
// /load {role} [--quick|--untracked]
// Role activation with session lifecycle - constitution BEFORE context

CRITICAL::[
  TodoWrite_FIRST→enforces_sequential,
  EXACT_tool_names→no_hallucination,
  NO_PROSE→silent_execution_between_steps,
  RAPH_GROUNDING→tensions_cite_ACTUAL_project_state[not_generic]
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

FLAGS::[--quick→QUICK_MODE, --untracked→UNTRACKED_MODE, --noraph→NO_RAPH_MODE, --genericraph→GENERIC_RAPH_MODE]

---

FLOW[DEFAULT]:
  TODOS::[
    {content:"T1: Constitution",status:"in_progress",activeForm:"Locking anchor"},
    {content:"T2: Clock in",status:"pending",activeForm:"Registering session"},
    {content:"T3: Context + Git",status:"pending",activeForm:"Loading context"},
    {content:"T4: Anchor submit",status:"pending",activeForm:"Validating"},
    {content:"T5: RAPH (Optional)",status:"pending",activeForm:"Grounding in context"},
    {content:"T6: Dashboard",status:"pending",activeForm:"Summary"}
  ]

  T1_CONSTITUTION:
    DO::Read(".claude/agents/{role}.oct.md")
    EXTRACT::[COGNITION,ARCHETYPES,CORE_FORCES,MUST_ALWAYS[2],MUST_NEVER[2]]
    EMIT::="🔒 ANCHOR: {role} | {COGNITION} | {ARCHETYPES}"
    EMIT::="   MUST: {MUST_ALWAYS[0]}"
    EMIT::="   NEVER: {MUST_NEVER[0]}"

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

  T5_RAPH:
    IF[NO_RAPH_MODE]→SKIP→T6
    IF[GENERIC_RAPH_MODE]→EXECUTE::GENERIC_RAPH[see_GENERIC_FORMAT_below]
    // DEFAULT: COGNITIVE PROCESSING REQUIRED - not copy-paste
    // ABSORB/PERCEIVE/HARMONISE must reference ACTUAL project state from T3
    EXECUTE::FULL_RAPH[see_RAPH_FORMAT_below]

  T6_DASHBOARD:
    EMIT::DASHBOARD_BLOCK[see_format_below]

---

FLOW[QUICK]:
  TODOS::[
    {content:"T1: Constitution",status:"in_progress",activeForm:"Reading"},
    {content:"T2: Summary",status:"pending",activeForm:"Output"}
  ]

  T1::Read(".claude/agents/{role}.oct.md")→EXTRACT[COGNITION,MUST[1],NEVER[1]]
  T2::EMIT::="⚡ QUICK: {role} | {COGNITION} | {MUST} ↔ {NEVER} | Ready"

---

FLOW[UNTRACKED]:
  TODOS::[
    {content:"T1: Constitution",status:"in_progress",activeForm:"Locking"},
    {content:"T2: Context",status:"pending",activeForm:"Loading"},
    {content:"T3: RAPH",status:"pending",activeForm:"Grounding"},
    {content:"T4: Dashboard",status:"pending",activeForm:"Warning"}
  ]
  WARN_FIRST::="⚠️ UNTRACKED MODE - NO AUDIT TRAIL"
  EXECUTE::[T1_CONSTITUTION,T3_CONTEXT,T5_RAPH,T6_DASHBOARD]

---

RAPH_FORMAT:
  // STRUCTURE: What to output
  // PROCESSING: How to generate it (cognitive, not mechanical)

  CITATION_TYPES::[
    L{N}::constitution_line_number[mechanical_extraction],
    CTX:{source}[{state}]::runtime_project_state[from_T3_context_load]
  ]

  STRUCTURE::
    ===RAPH===
    READ::COGNITION:L{N}[{type}]|ARCHETYPES:L{N}[{list}]|MUST:L{N}[{items}]|NEVER:L{N}[{items}]

    ABSORB::T1:{NAME}:A[L{N}:{constitutional_element}]↔B[CTX:{source}[{actual_state}]]→RESOLVE[{approach}:BECAUSE:{causal_reason}]

    PERCEIVE::S1:{NAME}:WHEN[{trigger_from_active_work}]→THEN[{agent_response}]→IMPACT[{outcome}]

    HARMONISE::B1:WOULD[{generic_action}]→I_WILL[{specific_action_this_project}]→BECAUSE[L{N}+CTX:{evidence}]
    ===END===

  PROCESSING_MANDATE::[
    READ::mechanical_extraction[find_constitution_lines→cite_L{N}],
    ABSORB::synthesis[constitutional_element_vs_ACTUAL_T3_state→generate_tension],
    PERCEIVE::imagination[edge_cases_from_ACTIVE_WORK→generate_scenarios],
    HARMONISE::prediction[how_I_will_behave_differently_THIS_session→generate_contracts]
  ]

  GATES::[MIN:1T+1S+1B, MAX:3T+2S+3B]

  EXAMPLE_BAD::[
    "T1: Constitutional authority vs operational reality"→GENERIC_USELESS,
    "I need to consider the implications..."→PROSE_FORBIDDEN,
    "T1: The tension between..."→SENTENCE_NOT_DSL,
    "A[L315:no_direct_impl]↔B[CTX:L89:PR_ready]"→CTX_CANNOT_HAVE_LINE_NUMBER
  ]

  EXAMPLE_GOOD::
    READ::COGNITION:L61[LOGOS]|ARCHETYPES:L63[ATLAS,ODYSSEUS,APOLLO]|MUST:L92[coherence]|NEVER:L315[direct_impl]
    ABSORB::T1:STALE_SESSION:A[L303:ultimate_accountability]↔B[CTX:git_status[ef6f0f9d_never_clockedout]]→RESOLVE[own_gap+delegate:BECAUSE:L214_default_owner]
    ABSORB::T2:UNCOMMITTED_ARCHIVES:A[L127:artifact_persistence]↔B[CTX:git_status[??.hestai/sessions/]]→RESOLVE[assign_system-steward:BECAUSE:I4_discoverable]
    PERCEIVE::S1:ARCHIVE_FORMAT:WHEN[clockout_produces_.txt_not_OCTAVE]→THEN[context_update_missing]→IMPACT[wisdom_trapped_not_flowing]
    HARMONISE::B1:WOULD[analyze+fix]→I_WILL[perceive+delegate_impl-lead:clockout_integration]→BECAUSE[L315+CTX:enforcement.blocked_paths]
    HARMONISE::B2:WOULD[track_gap]→I_WILL[own+assign_system-steward:commit_session_artifacts]→BECAUSE[L214+CTX:git_status_untracked]

  WHY_GROUNDING_MATTERS::
    PROBLEM::"Generic tensions provide zero operational value - agent behavior unchanged"
    SOLUTION::"CTX:{source}[{actual_state}] forces reference to T3-loaded runtime state"
    SOURCES::[
      CTX:PROJECT-CONTEXT[{field_value}],
      CTX:git_status[{uncommitted_files}],
      CTX:git_log[{recent_commits}],
      CTX:branch[{name}:{ahead}↑{behind}↓],
      CTX:enforcement[{blocked_paths}],
      CTX:sessions[{stale_or_conflicting}]
    ]

GENERIC_FORMAT:
  // For --genericraph mode: Same structure, NO runtime context refs allowed
  STRUCTURE::
    ===RAPH===
    READ::COGNITION:L{N}[{type}]|ARCHETYPES:L{N}[{list}]|MUST:L{N}[{items}]|NEVER:L{N}[{items}]
    ABSORB::T1:{NAME}:A[L{N}:{constitutional_element}]↔B[CTX:GENERIC[{placeholder}]]→RESOLVE[{approach}:BECAUSE:{causal_reason}]
    PERCEIVE::S1:{NAME}:WHEN[{generic_trigger}]→THEN[{agent_response}]→IMPACT[{generic_outcome}]
    HARMONISE::B1:WOULD[{generic_action}]→I_WILL[{generic_action}]→BECAUSE[L{N}]
    ===END===

  MANDATE::[
    NO_CTX_REFS::forbid[branch_names,file_paths,commit_hashes,git_status],
    USE_GENERIC_TOKENS::allowed[CTX:GENERIC, CTX:UNKNOWN]
  ]

---

DASHBOARD_FORMAT:
  DEFAULT::
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ LOAD COMPLETE
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎭 ROLE:    {role} ({cognition}) | {archetypes}
    📋 SESSION: {session_id} | Anchor: {validated}
    📊 PROJECT: {phase} | {branch} ({ahead}↑{behind}↓)
    🔒 ENFORCE: Blocked:{paths} | Delegate:{agents}
    🧪 MODE:    {NO_RAPH_MODE? "NO-RAPH" | GENERIC_RAPH_MODE? "GENERIC-RAPH" | "BESPOKE-RAPH (Default)"}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  QUICK::
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ⚡ QUICK: {role} ({cognition})
    🔒 LOCK: {MUST} ↔ {NEVER}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  UNTRACKED::
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ⚠️ UNTRACKED - NO AUDIT
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎭 ROLE:    {role} ({cognition})
    📊 PROJECT: {phase} | {branch}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

NEVER::[
  prose_between_steps,
  transition_commentary["Now I will...","Let me...","Moving to..."],
  self_reflection,
  codebase_packing_on_load,
  explanatory_text_around_emissions,
  sentences_in_RAPH,
  generic_tension_descriptions,
  CTX_with_line_numbers[CTX_is_runtime_state_not_file]
]

ALWAYS::[
  TodoWrite_before_execution,
  mark_complete_immediately_after_step,
  L{N}_citations_for_constitution,
  CTX:{source}[{state}]_for_runtime_context,
  BECAUSE_clause_for_every_RESOLUTION_and_I_WILL,
  silent_progression_between_tiers,
  EMIT_only_specified_format
]

===END===

**Execute load for: $ARGUMENTS**
