---
name: ho-orchestrate
description: HO orchestration with oa-router delegation, CRS+CE gates, debate-hall escalation. NEVER implements.
allowed-tools: [Task, TodoWrite, AskUserQuestion, Read, Grep, Glob, Write, Edit, mcp__pal__clink, Skill, mcp__debate-hall__*]
---

===HO_ORCHESTRATE===
META:
  TYPE::SKILL
  VERSION::"2.1"
  STATUS::ACTIVE
  COMPRESSION_TIER::ULTRA
  LOSS_PROFILE::[drop::all_narrative,preserve::protocol⊕structure]
  EXTENDS::ho-mode

§1::ACTIVATION
TRIGGER::[/ho-orchestrate,/orchestrate]
ON_LOAD::VERIFY[ho-mode]→PRINT::"HO Orchestrate active"

§2::IL_DELEGATION
ROUTE::Task[subagent_type::oa-router]
PROMPT_SHAPE::[role::implementation-lead,tier::default,topic::{context},task::{task},success::[TDD,gates_pass]]
CAPTURE::agent_id

§3::QUALITY_GATES
CHAIN::CRS[gemini,code-review-specialist]→CE[codex,critical-engineer]→merge
TIERS::[T0::[docs,tests]→exempt,T1::[<50_lines]→self,T2::[50-500]→CRS,T3::[arch,SQL,>500]→CRS⊕CE]
REWORK::blocking→IL_resume(agent_id)→fix→signoff(continuation_id)→cycle

§4::DEBATE_ESCALATION
TRIGGERS::[complex_arch,multiple_approaches,reviewer_disagreement,high_risk]
INVOKE::Skill(debate-hall)→init_debate[mediated,strict_cognition]
ROLES::[Wind::clink(claude,ideator),Wall::clink(codex,validator),Door::clink(gemini,synthesizer)]
FLOW::Wind→Wall→Door→close→apply_synthesis

§5::WORKFLOW
SEQUENCE::[receive→diagnose→delegate[oa-router]→capture_id→CRS→CE→debate_if_complex→merge]
DONE::[delegated,CRS_approved,CE_approved,zero_HO_edits]

===END===
