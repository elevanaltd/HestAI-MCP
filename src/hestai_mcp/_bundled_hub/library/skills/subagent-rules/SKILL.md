---
name: subagent-rules
description: Proper delegation patterns for Task() invocations with governance context injection
allowed-tools: ["Task", "Read", "Bash"]
---

===SKILL:SUBAGENT_RULES===
META:
  TYPE::SKILL
  VERSION::"2.0"
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
    micro::trivial_read_only_tasks[0_tensions,bypass],
    quick::fast_iteration_single_constraint[1_tension],
    default::standard_work[2_tensions],
    deep::critical_decisions_production_impact[3_tensions]
  ]

§4::CALLER_RULES
  MUST::["Include anchor-first instruction in every prompt (baked into §2 template)", "Include role field (oa-router cannot bind without it)"]
  NEVER::["Skip/bypass anchor ceremony", "Pre-assign identity (e.g., 'You are an implementation-lead')", "Omit role from prompt", "Include pre-ceremony instructions that bypass binding"]
  INVALID_WORK::"IF subagent produces output without valid PERMIT_SID THEN work is INVALID per I5 → discard and re-delegate"
===END===
