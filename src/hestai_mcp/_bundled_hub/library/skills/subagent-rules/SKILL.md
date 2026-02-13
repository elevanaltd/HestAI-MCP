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
  ALWAYS::Task(subagent_type:"oa-router", prompt:"role: {role}\ntier: {tier}\ntopic: {topic}\n\n## YOUR TASK\n{task}")
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

RIGHT::Task(subagent_type:"oa-router", prompt:"role: technical-architect\ntopic: auth review\n\n## YOUR TASK\nReview auth module")
