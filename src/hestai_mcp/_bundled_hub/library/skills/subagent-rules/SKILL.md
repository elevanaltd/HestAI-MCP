---
name: subagent-rules
description: Proper delegation patterns for Task() invocations with governance context injection
allowed-tools: ["Task", "Read", "Bash"]
triggers: ["subagent", "oa-router", "Task delegation", "anchor ceremony", "subagent rules", "delegate task", "spawn agent", "tier selection"]
---

===SKILL:SUBAGENT_RULES===
META:
  TYPE::SKILL
  VERSION::"2.1.0"
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
  BEFORE ANY WORK: Complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.
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
  NEVER::["Skip/bypass anchor ceremony", "Pre-assign identity (e.g., 'You are an implementation-lead')", "Omit role from prompt", "Include pre-ceremony instructions that bypass binding", "Launch fresh Task() for same role when previous agent_id exists in session"]
  INVALID_WORK::"IF subagent produces output without valid PERMIT_SID THEN work is INVALID per I5 → discard and re-delegate"

§5::RESUME_RULE
  RULE::"When delegating to a role previously invoked in the same session, MUST use Task({resume: agent_id}) instead of launching fresh"
  RATIONALE::"Fresh launch forces full re-anchor (~50k+ tokens). Resume preserves anchor context, governance state, and loaded capabilities."
  PATTERN::[
    FIRST_CALL::Task({subagent_type: "oa-router", prompt: "role: X ..."})→store_agent_id,
    SUBSEQUENT::Task({resume: stored_agent_id, prompt: "continue: ..."})→reuse_context
  ]
  EXCEPTION::"Launch fresh only when role changes OR context has fundamentally shifted (different branch, different project)"
  RELATED::"External model tools (PAL continuation_id, future equivalents) follow same principle — preserve conversation thread via tool-native continuation IDs. This rule covers Task() delegation; tool-level continuation is tool-specific."
===END===
