===BIND===
// /bind {role} ["topic"] [--quick|--deep]
// Odyssean Anchor binding v4.0 - MCP server-side validation
// INSTALL: cp hub/library/commands/bind.md ~/.claude/commands/bind.md

META:
  VERSION::"4.0"
  PATTERN::ODYSSEAN[identity_binding→server_validation→cognitive_proof]

ALIASES::[ho→holistic-orchestrator,ce→critical-engineer,il→implementation-lead,ta→technical-architect,ea→error-architect,ca→completion-architect,wa→workspace-architect,ss→system-steward,rs→requirements-steward,td→task-decomposer,crs→code-review-specialist,tmg→test-methodology-guardian,tis→test-infrastructure-steward,ute→universal-test-engineer]

FLAGS::[--quick→QUICK[1_tension],--deep→DEEP[3_tensions],DEFAULT→[2_tensions]]

PARSE::[ROLE::first_token,TOPIC::quoted_or_null→"general",TIER::flag_or_DEFAULT]

CRITICAL::[TodoWrite_FIRST,NO_PROSE_between_steps,TENSION_interprets_not_copies]

---

FLOW::
  T0::TodoWrite(TODOS)→mark_complete
  T1::CONSTITUTION→Read(".claude/agents/{role}.oct.md")→EXTRACT[COGNITION,ARCHETYPES,MUST[2],NEVER[2]]→SET_AUTHORITY[main→RESPONSIBLE|sub→DELEGATED]→EMIT
  T2::CLOCK_IN→mcp__hestai__clock_in(role,focus,working_dir)→CAPTURE[SESSION_ID,CONTEXT_PATHS]→IF[FAIL]→STOP
  T2b::ARM_CONTEXT→Read(project_context)→Bash(git_log+status+branch+ahead_behind)→EXTRACT[PHASE,BRANCH,FILES]→EMIT
  T3::TENSION→GENERATE[L{N}::[constraint]↔CTX:{path}[state]→TRIGGER[action]]→MIN_COUNT_PER_TIER→mark_complete
  T4::COMMIT→DECLARE[ARTIFACT::concrete_path,GATE::validation_method]→mark_complete
  T5::ANCHOR→BUILD_VECTOR[BIND+TENSION+COMMIT]→mcp__hestai__odyssean_anchor(role,vector,session_id,working_dir,tier)→HANDLE_RESULT
  T6::DASHBOARD→EMIT[VECTOR_BLOCK+DASHBOARD_BLOCK]→mark_complete

TODOS::[
  {content:"T0: TodoWrite",status:"in_progress",activeForm:"Sequencing"},
  {content:"T1: Constitution",status:"pending",activeForm:"Identity"},
  {content:"T2: clock_in + ARM",status:"pending",activeForm:"Context"},
  {content:"T3: TENSION",status:"pending",activeForm:"Cognitive proof"},
  {content:"T4: COMMIT",status:"pending",activeForm:"Contract"},
  {content:"T5: Odyssean Anchor",status:"pending",activeForm:"MCP validation"},
  {content:"T6: Dashboard",status:"pending",activeForm:"Summary"}
]

---

T5_DETAIL::
  BUILD::VECTOR_CANDIDATE::[
    "## BIND",
    "ROLE::{role}","COGNITION::{cognition}::{archetypes}","AUTHORITY::{authority}",
    "## TENSION","{tensions_from_T3}",
    "## COMMIT",
    "ARTIFACT::{artifact}","GATE::{gate}"
  ]
  DO::mcp__hestai__odyssean_anchor(role:{ROLE},vector_candidate:{VECTOR},session_id:{SESSION_ID},working_dir:"{cwd}",tier:{TIER})
  CAPTURE::[success,anchor,errors,guidance,terminal]
  IF[!success∧!terminal]→EMIT(guidance)→RETRY::T3[max_2]
  IF[!success∧terminal]→STOP::"BINDING FAILED"
  IF[success]→CAPTURE::VALIDATED_ANCHOR

---

VECTOR_SCHEMA::v4.0
  ===RAPH_VECTOR::v4.0===
  ## BIND
  ROLE::{name}
  COGNITION::{type}::{archetype}
  AUTHORITY::{RESPONSIBLE|DELEGATED[parent]}

  ## ARM (MCP-INJECTED)
  PHASE::{phase}
  BRANCH::{name}[{ahead}↑{behind}↓]
  FILES::{count}[{top}]
  FOCUS::{topic}

  ## TENSION (AGENT-GENERATED)
  L{N}::[{constraint}]↔CTX:{path}[{state}]→TRIGGER[{action}]

  ## COMMIT
  ARTIFACT::{path}
  GATE::{method}
  ===END_RAPH_VECTOR===

VALIDATION::[sections[BIND,ARM,TENSION,COMMIT],tension_count≥tier_min,L{N}_present,CTX_present,artifact_concrete]

---

DASHBOARD::
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK BIND COMPLETE
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ROLE:    {role} ({cognition}) | {archetypes}
  SESSION: {session_id}
  PROJECT: {phase} | {branch} ({ahead}↑{behind}↓)
  FOCUS:   {focus}
  ANCHOR:  VALIDATED
  TIER:    {tier}
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ===END_BIND_SEQUENCE===

---

NEVER::[prose_between_steps,generic_tensions,COMMIT_as_"response",generate_ARM[server_does_this]]
ALWAYS::[TodoWrite_first,mark_complete_per_step,TENSION_cites_L{N}+CTX,silent_between_steps]

REFS::[ADR_0036,src/hestai_mcp/mcp/tools/odyssean_anchor.py,.hestai/workflow/components/000-ODYSSEAN-ANCHOR-NORTH-STAR.md]

===END===

**Execute bind for: $ARGUMENTS**
