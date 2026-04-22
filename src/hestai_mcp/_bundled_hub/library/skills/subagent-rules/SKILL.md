---
name: subagent-rules
description: Proper delegation patterns for Task() invocations with governance context injection
allowed-tools: ["Task", "Read", "Bash"]
triggers: ["subagent", "oa-router", "Task delegation", "anchor ceremony", "subagent rules", "delegate task", "spawn agent", "tier selection"]
---

===SKILL:SUBAGENT_RULES===
META:
  TYPE::SKILL
  VERSION::"2.4.0"
  STATUS::ACTIVE
  PURPOSE::"Enforce oa-router delegation with anchor ceremony for all subagent Task() calls"

§1::ROUTING_RULE
  RULE::"ALL agent delegation MUST use subagent_type:'oa-router'. NEVER call role agents directly."
  RATIONALE::"oa-router runs anchor ceremony providing identity, governance, context, enforcement (I5)"

§2::TEMPLATE
  INVOCATION::Task({
    subagent_type: "oa-router",
    description: "{brief description}",
    prompt: `
  role: {role}
  tier: {tier|default}
  topic: {context for ARM computation}
  BEFORE ANY WORK: Load deferred MCP tool schemas via ToolSearch if needed (see §4d), then complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.
  YOUR TASK
  {detailed task description}
  SUCCESS CRITERIA
  {what done looks like}
    `
  })

§3::TIER_SELECTION
  TIERS::[
    micro::trivial_read_only_tasks[0_tensions,tension_bypass],
    quick::fast_iteration_single_constraint[1_tension],
    default::standard_work[2_tensions],
    deep::critical_decisions_production_impact[3_tensions]
  ]

§4::CALLER_RULES
  MUST::["Include anchor-first instruction in every prompt (baked into §2 template)", "Include role field (oa-router cannot bind without it)", "Store agent_id from Task() result for same-role reuse", "Use resume parameter with stored agent_id for subsequent calls to same role"]
  NEVER::["Skip/bypass anchor ceremony", "Pre-assign identity (e.g., 'You are an implementation-lead')", "Omit role from prompt", "Include pre-ceremony instructions that bypass binding", "Launch fresh Task() for same role when previous agent_id exists in session", "Use run_in_background:true for oa-router delegations"]
  BACKGROUND_RULE::[
    PROHIBITION::"oa-router Task() calls MUST run in foreground (run_in_background MUST be false or omitted)",
    RATIONALE::"Background execution hides the anchor ceremony — multi-stage identity proofs (I5) become unauditable. Foreground shows every sub-agent action (anchor_request, file reads, anchor_lock, anchor_commit) enabling real-time verification.",
    PARALLEL_ALTERNATIVE::"For throughput, use multiple foreground Task() calls in a single message — Claude Code executes independent calls concurrently while preserving visibility.",
    DETECTION::"IF oa-router output contains 'Async agent launched successfully' THEN ceremony auditability is lost → treat as governance concern"
  ]
  INVALID_WORK::"IF subagent produces output without valid PERMIT_SID THEN work is INVALID per I5 → discard and re-delegate"

§4b::RESUME_RULE
  RULE::"When delegating to a role previously invoked in the same session, MUST use Task({resume: agent_id}) instead of launching fresh"
  RATIONALE::"Fresh launch forces full re-anchor (~50k+ tokens). Resume preserves anchor context, governance state, and loaded capabilities."
  PATTERN::[
    FIRST_CALL::Task({subagent_type: "oa-router", prompt: "role: X ..."})→store_agent_id,
    SUBSEQUENT::Task({resume: stored_agent_id, prompt: "continue: ..."})→reuse_context
  ]
  EXCEPTION::"Launch fresh only when role changes OR context has fundamentally shifted (different branch, different project)"

§4c::CONTINUATION_RULE
  RULE::"Subagents using external tools with continuation/thread IDs (PAL continuation_id, future equivalents) MUST store and reuse the ID returned from the first call in ALL subsequent calls to the same tool within the session."
  RATIONALE::"Each call without continuation_id starts a fresh conversation — losing accumulated context, wasting tokens on re-explanation, and risking inconsistent responses across calls."
  SCOPE::[
    PAL_CHAT::continuation_id[returned_in_response→pass_in_next_call],
    PAL_CLINK::continuation_id[same_principle],
    FUTURE_TOOLS::"Any tool returning a thread/session/continuation identifier"
  ]
  PATTERN::[
    FIRST_CALL::mcp__pal__chat({prompt: "...", ...})→store_continuation_id_from_response,
    SUBSEQUENT::mcp__pal__chat({prompt: "...", continuation_id: stored_id, ...})→reuse_thread
  ]
  NEVER::["Discard continuation_id between calls to the same tool", "Start fresh PAL conversations when continuation_id is available"]

§4d::DEFERRED_TOOL_DISCOVERY
  RULE::"Before invoking any mcp__* tool (or any other deferred tool) for the first time in a session, MUST call ToolSearch with a select-query to load the tool schemas. Subagents receive a restricted initial tool set — MCP tools appear only by name in <system-reminder> messages until their schemas are loaded."
  RATIONALE::"Calling a deferred tool without loading its schema fails with InputValidationError. Agents that skip this step may falsely conclude 'MCP tools unavailable' and abort — producing a reproducible anchor-ceremony failure mode. Loading schemas via ToolSearch is a prerequisite for the anchor ceremony itself, because mcp__odyssean-anchor__* tools are deferred."
  PATTERN::[
    ANCHOR_TOOLCHAIN::"ToolSearch(query='select:mcp__odyssean-anchor__anchor_request,mcp__odyssean-anchor__anchor_lock,mcp__odyssean-anchor__anchor_commit,mcp__odyssean-anchor__verify_permit,mcp__odyssean-anchor__anchor_micro', max_results=5)",
    OCTAVE_WRITE_VALIDATE::"ToolSearch(query='select:mcp__octave__octave_write,mcp__octave__octave_validate', max_results=2)",
    OTHER_DEFERRED::"Use select:<comma,separated,names> for any MCP tool referenced in the task prompt that is not already in the initial tool list",
    KEYWORD_SEARCH::"Use a free-text query (e.g. 'notebook jupyter') when the exact tool name is unknown"
  ]
  TRIGGER::[
    on_deferred_tool_in_task_prompt::load_before_first_invocation,
    on_deferred_tool_in_system_reminder::load_before_first_invocation,
    on_tool_not_found_error::retry_after_ToolSearch_load,
    on_InputValidationError_for_mcp_tool::check_schema_loaded_then_retry
  ]
  NEVER::[
    "Conclude 'MCP tools unavailable' without first attempting ToolSearch",
    "Abort the anchor ceremony citing missing mcp__odyssean-anchor__* tools — load them via ToolSearch first",
    "Guess at deferred tool parameters without loading the schema",
    "Skip ToolSearch when a deferred tool is explicitly named in the task prompt or system-reminder"
  ]

§5::ANCHOR_KERNEL
TARGET::governance_compliant_oa-router_delegation
NEVER::[bypass_anchor_ceremony,pre_assign_identity,omit_role,run_in_background_for_oa-router,launch_fresh_when_agent_id_exists,discard_continuation_ids,conclude_mcp_tools_unavailable_without_ToolSearch]
MUST::[use_oa-router_subagent_type,include_anchor-first_instruction,store_and_reuse_agent_id,foreground_execution_for_ceremony_auditability,reuse_continuation_ids_across_tool_calls,load_deferred_tools_via_ToolSearch_before_first_mcp_call]
GATE::"Does this delegation use oa-router, run in foreground, include role, preserve agent_id for reuse, maintain continuation IDs, and load deferred MCP tool schemas via ToolSearch before first use?"
===END===
