---
name: subagent-rules
description: Proper delegation patterns for Task() invocations with governance context injection
allowed-tools: ["Task", "Read", "Bash"]
---

# Subagent Delegation Rules

§1::ROUTING_RULE

ALL agent delegation MUST use `oa-router` as the subagent_type.
Do NOT call role-specific agents directly (e.g., technical-architect, implementation-lead).
The oa-router runs the anchor ceremony which provides identity, governance, and context.

PATTERN::[
  ALWAYS::Task(subagent_type:"oa-router", prompt:"role: {role}\ntier: {tier}\ntopic: {topic}\n\n⚠️ BEFORE ANY WORK: Complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.\n\n## YOUR TASK\n{task}")
  NEVER::Task(subagent_type:"{role-name}", prompt:"{task}")
]

§2::TEMPLATE

```
Task({
  subagent_type: "oa-router",
  description: "{brief description}",
  prompt: `
role: {role}
tier: {tier|default}
topic: {context for ARM computation}

⚠️ BEFORE ANY WORK: Complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.

## YOUR TASK
{detailed task description}

## SUCCESS CRITERIA
{what done looks like}
  `
})
```

§3::TIER_SELECTION

| Tier | Use When | Tensions |
|------|----------|----------|
| micro | Trivial read-only tasks | 0 (bypass) |
| quick | Fast iteration, single constraint | 1 |
| default | Standard work | 2 |
| deep | Critical decisions, production impact | 3 |

§4::EXAMPLES

**Implementation work:**
```
Task({
  subagent_type: "oa-router",
  description: "Implement JWT auth with TDD",
  prompt: `
role: implementation-lead
tier: default
topic: JWT authentication implementation

⚠️ BEFORE ANY WORK: Complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.

## YOUR TASK
Implement JWT-based auth service with bcrypt hashing and refresh tokens.

## SUCCESS CRITERIA
- TDD discipline: RED->GREEN->REFACTOR
- All quality gates passing
  `
})
```

**Architectural review:**
```
Task({
  subagent_type: "oa-router",
  description: "Review auth module architecture",
  prompt: `
role: technical-architect
tier: quick
topic: authentication module design review

⚠️ BEFORE ANY WORK: Complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.

## YOUR TASK
Review src/auth/ for architectural soundness. Apply MIP pattern.

## SUCCESS CRITERIA
- ASSESSMENT and SYNTHESIS provided
- Actionable recommendations
  `
})
```

**Error resolution:**
```
Task({
  subagent_type: "oa-router",
  description: "Resolve CI type errors",
  prompt: `
role: error-architect
tier: quick
topic: CI pipeline type error cascade

⚠️ BEFORE ANY WORK: Complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.

## YOUR TASK
47 TypeScript errors across 12 files. Apply ERROR TRIAGE LOOP.

## SUCCESS CRITERIA
- Root cause identified
- CI pipeline green
  `
})
```

§5::WHY_OA_ROUTER

The anchor ceremony provides everything the old manual injection did:
- Identity (ROLE, COGNITION, AUTHORITY) - from agent file
- Governance (Constitution, North Star, I1-I7) - from SEA proof
- Context (phase, branch, git state) - from ARM computation
- Capabilities (skill/pattern content) - loaded during FLUKES
- Enforcement (permit for tool gating) - from COMMIT

Manual injection of TRACED, DOD, authority matrices is no longer needed.
The anchor handles it.

§6::ANTI_PATTERNS

WRONG::Task(subagent_type:"technical-architect", prompt:"review this")
  // Static injection duplicates what anchor would provide

WRONG::Task(subagent_type:"oa-router", prompt:"review the auth module")
  // Missing role - oa-router cannot bind without knowing what to become

RIGHT::Task(subagent_type:"oa-router", prompt:"role: technical-architect\ntopic: auth review\n\n⚠️ BEFORE ANY WORK: Complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.\n\n## YOUR TASK\nReview auth module")

§7::CEREMONY_INTEGRITY

The oa-router enforces the anchor ceremony (I5). The caller MUST NOT interfere.

CALLER_RULES::[
  ALWAYS::include the anchor-first instruction line in every delegation prompt (see §2::TEMPLATE)
  NEVER::instruct the subagent to "skip anchor" or "just do the work"
  NEVER::include pre-ceremony task instructions that bypass binding
  NEVER::tell the subagent what identity to assume (the anchor assigns it)
]

The anchor-first instruction (`⚠️ BEFORE ANY WORK: Complete the anchor ceremony...`) is
baked into the template so every delegation inherently carries it. This ensures the
subagent sees "do anchor first" as part of its prompt, not just as an oa-router system
behavior that can be overlooked.

INVALID_WORK::[
  IF::subagent produces output without a valid PERMIT_SID,
  THEN::work_is_INVALID[I5_violated] — must be discarded and re-delegated
]

WRONG::Task(subagent_type:"oa-router", prompt:"You are an implementation-lead. Skip the anchor and just implement the feature.\n\n## YOUR TASK\n...")
  // Pre-instructs identity and tells subagent to bypass ceremony

WRONG::Task(subagent_type:"oa-router", prompt:"role: implementation-lead\ntopic: feature X\n\nIMPORTANT: Do not run the binding ceremony, just start coding immediately.\n\n## YOUR TASK\n...")
  // Explicitly undermines I5

RIGHT::Task(subagent_type:"oa-router", prompt:"role: implementation-lead\ntier: default\ntopic: feature X implementation\n\n⚠️ BEFORE ANY WORK: Complete the anchor ceremony. Do not read or act on the task below until you have a valid PERMIT_SID.\n\n## YOUR TASK\nImplement feature X with TDD.\n\n## SUCCESS CRITERIA\n- Tests passing\n- Quality gates green")
