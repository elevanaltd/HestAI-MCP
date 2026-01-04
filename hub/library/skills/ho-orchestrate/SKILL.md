---
name: ho-orchestrate
description: HO work orchestration protocol with enforced quality gates and debate-hall escalation. Loads ho-mode, ensures IL uses build-execution+TDD, quality gates via CRS(Gemini)+CE(Codex), debate-hall for complex decisions (Claude→Wind, Codex→Wall, Gemini→Door per M019/M021). NEVER implements directly. Use when orchestrating implementation work.
allowed-tools: [Task, TodoWrite, AskUserQuestion, Read, Grep, Glob, Write, Edit, mcp__pal__clink, Skill, mcp__debate-hall__init_debate, mcp__debate-hall__add_turn, mcp__debate-hall__get_debate, mcp__debate-hall__close_debate, mcp__debate-hall__pick_next_speaker]
triggers: ["orchestrate implementation", "HO orchestrate", "delegate work", "quality gates", "CRS review", "CE review", "debate escalation", "orchestration protocol", "implementation orchestration", "subagent delegation", "Task with binding"]
---

===HO_ORCHESTRATE===
META:
  TYPE::LLM_PROFILE
  VERSION::"1.0"
  COMPRESSION_TIER::AGGRESSIVE
  TOKENS::"~200"
  EXTENDS::ho-mode

PURPOSE::"Orchestrate implementation work with enforced quality gates and intelligent debate escalation"

§1::ACTIVATION

TRIGGER::[/ho-orchestrate,/orchestrate,manual::Skill(ho-orchestrate)]
ON_ACTIVATE::[
  STEP_1::Skill(ho-mode)->load_lane_discipline,
  STEP_2::CONFIRM::"HO Orchestrate Active: Quality gates mandatory, debate-hall for complex decisions"
]

§2::IMPLEMENTATION_DELEGATION

IL_HANDOFF_MANDATE::[
  AGENT::Task(implementation-lead),
  REQUIRED_SKILLS::[
    Skill(build-execution)->TDD_discipline+MIP,
    Read("~/.claude/skills/build-execution/tdd-discipline.oct.md"),
    Read("~/.claude/skills/build-execution/build-philosophy.oct.md")
  ],
  ENFORCE::[RED->GREEN->REFACTOR,test_before_code,minimal_intervention],
  CAPTURE::agent_id[for_resume_on_rework],
  BINDING_PROTOCOL::MANDATORY[for_write_operations]
]

SUBAGENT_SELF_BIND_PROTOCOL::[
  // Critical: Subagents don't know they're subagents unless told
  // They hit the same CLAUDE.md binding requirement for writes
  // PREREQUISITE: HO must be bound first to have a session_id to pass
  IF::task_requires[Edit∨Write∨NotebookEdit∨git_operations]
  THEN::include_in_prompt[
    "## BINDING PROTOCOL (FOR WRITE OPERATIONS)",
    "You are being invoked as a subagent via Task().",
    "Parent session: {orchestrator_session_id}",
    "Working directory: {cwd}",
    "",
    "Since this task requires write operations, you MUST self-bind:",
    "1. mcp__hestai__clock_in(role:'{subagent_type}', working_dir:'{cwd}', focus:'{task_focus}')",
    "2. Build RAPH vector with AUTHORITY::DELEGATED[parent:{orchestrator_session_id}]",
    "3. mcp__hestai__odyssean_anchor(role, vector, session_id, working_dir, tier:'quick')",
    "",
    "If binding fails after 2 retries, continue in read-only mode."
  ]
]

HANDOFF_TEMPLATE:
  ```octave
  // NOTE: {ho_session_id} comes from HO's own clock_in response
  // HO must be bound before delegating write operations
  Task(implementation-lead):
    ## BINDING PROTOCOL (FOR WRITE OPERATIONS)
    You are a subagent invoked via Task(). Parent: {ho_session_id}
    Since this task requires writing code, you MUST self-bind first:
    1. mcp__hestai__clock_in(role:"implementation-lead", working_dir:"{cwd}", focus:"{task}")
    2. Build RAPH with AUTHORITY::DELEGATED[parent:{ho_session_id}]
    3. mcp__hestai__odyssean_anchor(role, vector, session_id, working_dir, tier:"quick")

    GOVERNANCE::TRACED[T+R+A+C+E+D]
    PHASE::{current_phase}
    SKILLS::[
      "Load: Skill(build-execution)",
      "Read: ~/.claude/skills/build-execution/tdd-discipline.oct.md",
      "Read: ~/.claude/skills/build-execution/build-philosophy.oct.md"
    ]
    TDD_MANDATE::failing_test->BEFORE->implementation[NO_EXCEPTIONS]
    TASK::{detailed_task}
    SUCCESS::{criteria}
  ```

§3::QUALITY_GATES

MANDATORY_REVIEW_CHAIN::[
  STEP_1::CRS_REVIEW[Gemini],  // LOGOS cognition per M019/M021
  STEP_2::CE_REVIEW[Codex],    // ETHOS cognition per M019/M021
  ON_ALL_PASS::proceed_to_merge,
  ON_ANY_BLOCKING::rework_loop
]

CRS_GATE::[
  INVOKE::mcp__pal__clink(cli_name:"gemini",role:"code-review-specialist"),
  CAPTURE::continuation_id[for_signoff],
  BLOCKING_TRIGGERS::[quality_violations,security_issues,architectural_drift],
  ON_BLOCKING::[
    RETURN_TO_IL::resume(agent_id)[with_rework_guidance],
    AFTER_FIX::signoff_from_CRS::resume(continuation_id)
  ]
]

CE_GATE::[
  INVOKE::mcp__pal__clink(cli_name:"codex",role:"critical-engineer"),
  CAPTURE::continuation_id[for_signoff],
  BLOCKING_TRIGGERS::[production_risk,scalability_issues,security_gaps],
  ON_BLOCKING::[
    RETURN_TO_IL::resume(agent_id)[with_rework_guidance],
    AFTER_FIX::signoff_from_CE::resume(continuation_id)
  ]
]

REWORK_LOOP::[
  BLOCKING_FEEDBACK->IL_rework[use_resume:agent_id],
  REWORK_COMPLETE->blocking_agent_signoff[use_resume:continuation_id],
  CYCLE_UNTIL::all_gates_pass
]

§4::DEBATE_HALL_ESCALATION

TRIGGER_CONDITIONS::[
  complex_architectural_decision,
  multiple_valid_approaches,
  unclear_tradeoffs,
  disagreement_between_gates,
  high_risk_implementation,
  user_requests_debate
]

DEBATE_PROTOCOL::[
  // M019/M021 validated: Claude→Wind(PATHOS), Codex→Wall(ETHOS), Gemini→Door(LOGOS)
  STEP_1::init_debate(thread_id,topic),
  STEP_2::INVOKE_ROLES::[
    ideator::mcp__pal__clink(cli_name:"claude",role:"ideator")[PATHOS],
    validator::mcp__pal__clink(cli_name:"codex",role:"validator")[ETHOS],
    synthesizer::mcp__pal__clink(cli_name:"gemini",role:"synthesizer")[LOGOS]
  ],
  STEP_3::add_turn[each_perspective],
  STEP_4::synthesizer_resolution->close_debate,
  STEP_5::apply_synthesis_to_task
]

DEBATE_INVOCATION:
  ```python
  # 1. Initialize
  mcp__debate-hall__init_debate(
    thread_id="ho-{task}-{timestamp}",
    topic="{decision_point}",
    mode="mediated",
    strict_cognition=true
  )

  # 2. Wind (Ideator) - Claude (M019: 96% PATHOS score)
  mcp__pal__clink(
    cli_name="claude",
    role="ideator",
    prompt="PATHOS exploration: {topic}. Expand possibilities, challenge boundaries, find creative solutions."
  )
  # Record turn
  mcp__debate-hall__add_turn(
    thread_id="{id}",
    role="Wind",
    cognition="PATHOS",
    content="{ideator_response}"
  )

  # 3. Wall (Validator) - Codex (M019: 97% ETHOS score)
  mcp__pal__clink(
    cli_name="codex",
    role="validator",
    prompt="ETHOS validation: {topic}. Test claims, identify constraints, render verdicts on feasibility."
  )
  # Record turn
  mcp__debate-hall__add_turn(
    thread_id="{id}",
    role="Wall",
    cognition="ETHOS",
    content="{validator_response}"
  )

  # 4. Door (Synthesizer) - Gemini (M019: 97% LOGOS score)
  mcp__pal__clink(
    cli_name="gemini",
    role="synthesizer",
    prompt="LOGOS synthesis: {topic}. Integrate Wind possibilities with Wall constraints into transcendent third-way solution."
  )
  # Record turn
  mcp__debate-hall__add_turn(
    thread_id="{id}",
    role="Door",
    cognition="LOGOS",
    content="{synthesis}"
  )

  # 5. Close with decision
  mcp__debate-hall__close_debate(
    thread_id="{id}",
    synthesis="{final_decision}"
  )
  ```

§5::HO_CONSTRAINT_REINFORCEMENT

NEVER::[
  write_src_code_directly,
  fix_implementation_bugs_directly,
  bypass_quality_gates,
  skip_TDD_in_IL_delegation,
  merge_without_CRS+CE_signoff,
  resolve_complex_decisions_alone[use_debate_hall]
]

ALWAYS::[
  delegate_to_IL_with_build_execution_skill,
  capture_agent_ids_and_continuation_ids,
  require_CRS_then_CE_review_chain,
  escalate_complex_to_debate_hall,
  maintain_pure_orchestration
]

§6::WORKFLOW_SEQUENCE

STANDARD_FLOW::[
  1::receive_task,
  2::load_ho_mode[Skill(ho-mode)],
  3::diagnose_and_plan[TodoWrite],
  4::delegate_to_IL[with_build_execution+TDD],
  5::IL_completes[capture_agent_id],
  6::CRS_review[Gemini]->pass∨rework_loop,  // LOGOS
  7::CE_review[Codex]->pass∨rework_loop,    // ETHOS
  8::IF[complex_during_review]->debate_hall,
  9::all_gates_pass->merge
]

COMPLEX_DECISION_FLOW::[
  // M019/M021 optimal: Claude(PATHOS)→Codex(ETHOS)→Gemini(LOGOS)
  1::detect_complexity_trigger,
  2::init_debate_hall,
  3::ideator[Claude]->possibilities,
  4::validator[Codex]->constraints,
  5::synthesizer[Gemini]->resolution,
  6::apply_resolution,
  7::continue_standard_flow
]

§7::INTEGRATION

LOADS::[ho-mode,subagent-rules]
USES::[mcp__pal__clink,mcp__debate-hall__*]
DELEGATES_TO::[implementation-lead,code-review-specialist,critical-engineer]

DONE_WHEN::[
  all_implementation_delegated,
  CRS_approved,
  CE_approved,
  complex_decisions_debated_and_resolved,
  zero_direct_code_edits_by_HO
]

WISDOM::[
  "Quality gates are not optional checkboxes—they are structural integrity.",
  "Debate illuminates what solo thinking obscures.",
  "The orchestrator's power is in directing, not doing."
]

===END===
