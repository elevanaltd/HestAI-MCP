---
component: odyssean_anchor
scope: tool
phase: D1
created: 2025-12-27
status: approved
approved_by: requirements-steward
approved_date: 2025-12-28
parent_north_star: .hestai/workflow/components/000-SYSTEM-STEWARD-NORTH-STAR.md
version: 1.2
---

# COMPONENT NORTH STAR: ODYSSEAN ANCHOR

**Component**: Odyssean Anchor (Identity Binding Protocol)
**Parent**: .hestai/workflow/components/000-SYSTEM-STEWARD-NORTH-STAR.md
**Status**: ACTIVE
**Version**: 1.2
**Date**: 2025-12-28
**Reviewed By**: requirements-steward
**Review Date**: 2025-12-28

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **Odyssean Anchor** component.
It inherits all requirements from:
- **System North Star** (I1 through I6) - Constitutional principles
- **HestAI-MCP Product North Star** (I1 through I6) - Product requirements
- **System Steward North Star** (SS-I1 through SS-I6) - Parent component requirements

The Odyssean Anchor is the identity binding protocol that validates agent cognitive binding,
enforces the RAPH Vector structure, and gates tool access based on validated identity.

Any deviation requires formal amendment.

---

## SECTION 1: THE UNCHANGEABLES (7 Immutables)

### OA-I1: UNIFIED BINDING PATH
**Requirement**: A single, universal binding protocol must be used for ALL agents (main, sub-agents, tools). "Special paths" for different agent types are prohibited.
**Rationale**: Fragmentation in binding logic creates security holes where "dumb" agents bypass controls.
**Validation**: `/oa-load` (or its API equivalent) is the exclusive entry point.

### OA-I2: STRUCTURAL VALIDATION (RAPH VECTOR)
**Requirement**: Identity is not a string; it is a cryptographic structure (RAPH Vector) containing Role, Context Proof (ARM), and Authority (FLUKE). This structure must be machine-validated.
**Rationale**: Text-based identity ("I am X") is hallucinatable. Structure proves cognitive processing.
**Validation**: The `odyssean_anchor` tool rejects any input failing the RAPH schema.

### OA-I3: MANDATORY SELF-CORRECTION
**Requirement**: The system must reject invalid anchors with specific guidance, and the agent must be architected to catch this rejection and retry. Silent failure or "good enough" acceptance is prohibited.
**Rationale**: Agents hallucinate. The protocol must force them to "think again" rather than accepting garbage.
**Validation**: Test suite verifies the "Reject -> Guidance -> Retry -> Success" loop.

### OA-I4: CONTEXTUAL PROOF (THE ARM)
**Requirement**: Binding cannot occur in a vacuum. The anchor must contain proof of awareness of the current environment (ARM - Phase, Branch, Files).
**Rationale**: An identity bound without context is a dangerous "brain in a jar."
**Validation**: Anchor submission fails if `ARM` section does not match actual git state.

### OA-I5: AUTHORITY INHERITANCE (THE FLUKE)
**Requirement**: Sub-agents must explicitly cite the authority/task delegated by the parent. They cannot generate their own authority.
**Rationale**: Prevents "rogue sub-agents" drifting from the main objective.
**Validation**: `FLUKE` section must link to a parent session or task ID.

### OA-I6: TOOL GATING ENFORCEMENT
**Requirement**: Work tools MUST check for a valid anchor before executing. Validation alone is insufficient; enforcement is mandatory.
**Rationale**: Agents can bypass binding via direct tool calls if the tools themselves do not check for identity.
**Validation**: `has_valid_anchor(session_id)` check gates all work tool execution.

### OA-I7: COGNITIVE BINDING PERSISTENCE
**Requirement**: The validated vector MUST be returned to the agent's active conversation context, not just written to a log file.
**Rationale**: File output alone doesn't create cognitive binding; the agent must "see" its identity in working memory to act on it.
**Validation**: MCP returns the canonical vector to the conversation history upon success.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **Schema** | RAPH structure (OA-I2) | Specific field names (can evolve) |
| **Retry Limit** | Must exist (OA-I3) | Exact count (currently 2) |
| **Validation Strictness** | Must validate ARM/FLUKE (OA-I4, OA-I5) | "Quick" vs "Deep" tier rules |

---

## SECTION 2B: SCOPE BOUNDARIES

### What This Component IS

| Scope | Description |
|-------|-------------|
| Agent Identity Validation | Validates RAPH Vector structure and content correctness |
| RAPH Vector Enforcement | Enforces schema compliance for SHANK+ARM+FLUKE structure |
| Self-Correction Protocol | Rejects invalid anchors with specific guidance for retry |
| Contextual Proof Verification (ARM) | Validates awareness of git state, phase, and branch |
| Authority Inheritance Tracking (FLUKE) | Validates parent session linkage and delegated authority |
| Tool Gating Enforcement | Provides `has_valid_anchor()` check for work tool access control |

### What This Component IS NOT

| Out of Scope | Responsible Component |
|--------------|----------------------|
| Session Management | clock_in / clock_out tools |
| Context Synthesis | System Steward |
| File Writing | OCTAVE MCP (octave_create) |
| Session Archival | clock_out tool |
| Context Selection | clock_in tool |
| Document Routing | document_submit tool |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Confidence | Impact | Validation Plan | Owner | Timing |
|----|------------|------------|--------|-----------------|-------|--------|
| OA-A1 | Agents can self-correct JSON/YAML after 1 error | 75% | High | A/B Testing with different models (Claude, GPT, Gemini) | implementation-lead | During B2 |
| OA-A2 | 5-10s binding latency is acceptable | 85% | Medium | User feedback monitoring and UX testing | implementation-lead | During B2 |
| OA-A3 | Git state is always readable for ARM proof | 90% | High | Edge case testing (bare repo, detached HEAD, no git) | implementation-lead | Before B1 |
| OA-A4 | Tool gating enforcement is implementable without performance degradation | 80% | High | Benchmark tool call overhead (<50ms per check) | implementation-lead | Before B1 |
| OA-A5 | RAPH Vector schema is stable enough for v1.0 | 75% | High | Schema review with 3+ use cases (main agent, sub-agent, tool) | technical-architect | Before B1 |
| OA-A6 | Cognitive binding persistence works across all LLM providers | 70% | Medium | Test with Claude, GPT, Gemini returning vector to context | implementation-lead | During B2 |

---

## SECTION 4: ARCHITECTURE SUMMARY

### RAPH Vector Structure

```
RAPH_VECTOR = {
  SHANK: {               # Constitutional Identity
    ROLE: string,        # Agent role name
    COGNITION: enum,     # ETHOS | LOGOS | PATHOS
    ARCHETYPES: list,    # e.g., [ATLAS, ATHENA]
    CONSTRAINTS: list    # Behavioral boundaries
  },
  ARM: {                 # Contextual Proof
    PHASE: string,       # Current workflow phase
    BRANCH: string,      # Git branch name
    FILES: list,         # Key files read
    BLOCKERS: list       # Known impediments
  },
  FLUKE: {               # Authority Gate
    PARENT_SESSION: string,  # Parent session ID (if sub-agent)
    DELEGATED_TASK: string,  # Task delegated by parent
    SKILLS: list,            # Loaded skills
    AUTHORITY_LEVEL: enum    # FULL | SCOPED | READONLY
  }
}
```

### Binding Flow

```
[Agent enters LOBBY state]
    -> [Reads constitution (CLAUDE.md)]
    -> [Calls clock_in -> receives session_id + context_paths]
    -> [Reads context files]
    -> [Constructs RAPH Vector from understanding]
    -> [Calls odyssean_anchor with vector]
    -> [IF valid: LOBBY -> BOUND, tools unlocked]
    -> [IF invalid: Receive guidance, retry (max 2)]
    -> [IF still invalid: FAIL HARD, no bypass]
```

### Tool Gating Integration

```
[Agent calls work tool (e.g., edit_file)]
    -> [Tool checks: has_valid_anchor(session_id)?]
    -> [IF yes: Execute tool normally]
    -> [IF no: Return error with binding instructions]
```

---

## SECTION 5: INTEGRATION POINTS

### Inherits From
- **System North Star** (I1 through I6): TDD, phase gates, human primacy, artifacts, quality verification, accountability
- **Product North Star** (I1 through I6): Cognitive continuity, structural integrity, dual-layer authority, freshness, Odyssean binding, universal scope
- **System Steward North Star** (SS-I1 through SS-I6): Dual control plane, async-first, MCP chaining, single writer, intelligence in manifests, graceful degradation

### Sibling Components
- **clock_in**: Provides session_id that odyssean_anchor validates against
- **clock_out**: Archives sessions that odyssean_anchor has validated
- **context_update**: May re-trigger ARM validation after context changes

### Upstream Dependencies
- **Session Store**: Must track valid anchors for tool gating queries
- **Git State Reader**: Provides branch, commit for ARM validation

### Downstream Consumers
- **All Work Tools**: Call `has_valid_anchor()` before execution
- **Sub-agent Delegation**: Parent anchor flows to FLUKE inheritance

---

## SECTION 6: IMPLEMENTATION PHASES

### Phase 1 (MVP)
- RAPH Vector schema definition and validation
- Basic odyssean_anchor MCP tool with reject/retry flow
- Session store integration for anchor persistence
- Return validated vector to conversation context

### Phase 2 (Tool Gating)
- Implement `has_valid_anchor(session_id)` helper
- Integrate gating check into all work tools
- Add metrics for gating failures

### Phase 3 (Advanced)
- Tiered validation (Quick vs Deep)
- Multi-model self-correction testing
- Authority inheritance for sub-agents
- Anchor refresh for long-running sessions

---

## DECISION LOG

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-27 | RAPH Vector structure (SHANK+ARM+FLUKE) | Captures identity, context, and authority in machine-validatable form |
| 2025-12-27 | Mandatory self-correction protocol | Agents hallucinate; must force "think again" loop |
| 2025-12-27 | Tool gating as immutable requirement | Validation without enforcement is theater |
| 2025-12-27 | Cognitive binding persistence requirement | File output alone doesn't create working memory binding |
| 2025-12-28 | Renamed immutables to OA-I1 through OA-I7 | Consistency with component naming pattern |
| 2025-12-28 | Added scope boundaries | requirements-steward review: clarity on component responsibility |
| 2025-12-28 | Enhanced assumption register | requirements-steward review: PROPHETIC_VIGILANCE compliance |
| 2025-12-28 | Parent changed to System Steward | Correct inheritance chain: System -> Product -> System Steward -> Odyssean Anchor |

---

## COMMITMENT CEREMONY

**Status**: APPROVED
**Reviewer**: requirements-steward
**Review Date**: 2025-12-28

**The Oath**:
> "These 7 Immutables (OA-I1 through OA-I7) are the binding requirements for Odyssean Anchor implementation. Any contradiction requires STOP, CITE, ESCALATE."

**Inheritance Chain**:
1. System North Star (I1-I6) - Constitutional principles
2. HestAI-MCP Product North Star (I1-I6) - Product requirements
3. System Steward North Star (SS-I1-SS-I6) - Parent component requirements
4. **This Document** (OA-I1-OA-I7) - Tool-level requirements

**Amendments Applied (v1.1)**:
1. Added YAML front-matter
2. Renamed immutables I1-I7 to OA-I1 through OA-I7
3. Added Scope Boundaries section (IS/IS NOT)
4. Enhanced Assumption Register with OA-A4, OA-A5, OA-A6
5. Added Confidence, Impact, Owner, Timing columns to assumptions
6. Updated parent_north_star to System Steward
7. Added Architecture Summary section
8. Added Integration Points section
9. Added Implementation Phases section
10. Updated to v1.2: Aligned with ns-component-create standard

---

## EVIDENCE SUMMARY

### Constitutional Compliance
- **Total Immutables**: 7 (within 5-9 range per Miller's Law)
- **System-Agnostic**: 7/7 passed Technology Change Test (no technology-specific language)
- **Assumptions Tracked**: 6 (6+ required per PROPHETIC_VIGILANCE)
- **Critical Assumptions**: 4 requiring pre-B1 validation (OA-A3, OA-A4, OA-A5, OA-A6 partially)
- **Commitment Ceremony**: Completed 2025-12-28

### Quality Gates
- **YAML Front-Matter**: Present
- **Inheritance Chain**: Documented (System NS -> Product NS -> System Steward NS -> This)
- **Miller's Law**: 7 immutables (within 5-9 range)
- **PROPHETIC_VIGILANCE**: 6 assumptions with validation plans
- **Scope Boundaries**: IS/IS NOT documented
- **Evidence Trail**: requirements-steward review documented

### Readiness Status
- **D1 Gate**: PASSED - Ready for implementation
- **Blocking Dependencies**: clock_in tool (provides session_id)

---

## PROTECTION CLAUSE

Any work contradicting these immutables must STOP, CITE the specific requirement, and ESCALATE to requirements-steward.

**The Protection Oath**:
> "These 7 Immutables (OA-I1 through OA-I7) are the binding requirements for Odyssean Anchor implementation. Any contradiction requires STOP, CITE, ESCALATE."
