# ADR-0036: Odyssean Anchor Binding Architecture

**Status**: ACCEPTED (Amended 2026-01-01)
**Date**: 2025-12-19 (Amendment 01: 2026-01-01)
**Author**: holistic-orchestrator (consolidated from Odyssean Anchor Project ADRs 001-003)
**Supersedes**: Legacy `anchor_submit` and `load2.md` patterns
**Implements**: I1 (Verifiable Behavioral Specification), I3 (Structural Enforcement)
**GitHub Issue**: [#36](https://github.com/elevanaltd/HestAI-MCP/issues/36)

---

## Context

### The Problem

The legacy agent binding process was redundant, asymmetric, and unverifiable:
1.  **Redundancy**: Agents extracted their identity (T1) and then separately submitted a structure (T4), duplicating work.
2.  **Asymmetry**: Main agents used a 7-step `load2.md` ceremony, while subagents used a manual, unverified prompt instruction.
3.  **Validation Theater**: "Anchors" were generated but never structurally validated. Invalid anchors were silently accepted.
4.  **No Self-Correction**: If an agent generated a bad anchor, it had no mechanism to know or fix it.

### The Solution: Odyssean Anchor

We introduce **Odyssean Anchor**, a unified binding mechanism and MCP tool that:
1.  **Unifies Paths**: Main agents and subagents use the exact same binding ceremony.
2.  **Validates Structurally**: A strict schema enforces identity, context awareness (ARM), and authority (FLUKE).
3.  **Enforces Self-Correction**: The tool rejects invalid anchors with specific error messages, forcing the agent to retry.

---

## Decision

Implement the **Odyssean Anchor** pattern as the exclusive method for agent identity binding.

### 1. The Unified Binding Ceremony (`/bind`)

All agents (main or sub) bind via a standardized sequence, orchestrated by the `/bind` command (or equivalent subagent protocol):

```octave
BINDING_SEQUENCE::[
  1::READ_PROMPT[Constitution loaded],
  2::CLOCK_IN[Session registered, context paths returned],
  3::READ_CONTEXT[Git state + Project context absorbed],
  4::ODYSSEAN_ANCHOR[
      role,
      vector_candidate,
      context,
      tier
  ]→{validated_anchor | failure_guidance},
  5::DASHBOARD[Show validated anchor as proof]
]
```

### 2. The `odyssean_anchor` MCP Tool

A new tool replacing `anchor_submit`.

**Signature:**
```python
def odyssean_anchor(
    role: str,
    vector_candidate: str,  # The raw ODYSSEAN_ANCHOR block
    tier: str = "default"   # quick | default | deep
) -> str:
    # Returns validated block or error message with retry guidance
```

**Validation Tiers:**
*   **QUICK**: 1 Tension min. For status checks.
*   **DEFAULT**: 2 Tensions min. For feature work (Standard).
*   **DEEP**: 3 Tensions min. For architecture/North Star changes.

### 3. The Anchor Schema (RAPH Vector)

> **⚠️ SUPERSEDED**: The 6-section schema below is historical. See **Amendment 01** for the current 4-section v4.0 schema.

<details>
<summary>Original 6-Section Schema (SUPERSEDED by Amendment 01)</summary>

```octave
===ODYSSEAN_ANCHOR===
## BIND (Identity Lock)
ROLE::{agent_name}
COGNITION::{type}::{archetype}

## ARM (Context Proof)
PHASE::{current_phase}
BRANCH::{name}[{ahead}↑{behind}↓]
FILES::{modified_count}[{top_files}]

## FLUKE (Authority Gate)
SKILLS::[{loaded_skills}]
AUTHORITY::RESPONSIBLE[policy_blocked:{paths}|delegate:{agents}]

## TENSION (The Engine)
TENSION::[{constraint}]↔[{context_state}]→{implication}::TRIGGER[{strategy}]
  // Must include CTX:{filename}:{line} citation

## HAZARD (Drift Detector)
HAZARD::[{cognition}]→NEVER[{anti_patterns}]

## COMMIT (Falsifiable Contract)
COMMIT::[{action}]→[{artifact}]→[{validation_gate}]
===END_ODYSSEAN_ANCHOR===
```

</details>

---

## Technical Specification

### Validation Logic (Updated for v4.0)

The MCP tool enforces strict rules. If any rule fails, it returns a formatted error message to the agent.

1.  **Structure**: Must have all headers (BIND, ARM, TENSION, COMMIT) per v4.0 schema.
2.  **No Placeholders**: `FILES::0[]` is rejected if git status shows changes. `PHASE::TODO` is rejected.
3.  **Citations**: TENSIONs must cite actual files (`CTX:src/main.py:10-15`).
4.  **Commitment**: COMMIT must name a concrete artifact (file, test), not "response" or "thoughts".

### Retry Loop

1.  Agent submits `vector_candidate`.
2.  **Pass**: Tool returns "Canonical Anchor Accepted".
3.  **Fail**: Tool returns "VALIDATION FAILED: [Reason 1, Reason 2]. RETRY: [Guidance]".
4.  Agent reads guidance, regenerates vector, resubmits (Max 2 retries).
5.  **Hard Fail**: If 2 retries fail, tool blocks further action (requires human intervention).

---

## Consequences

### Positive
*   **Symmetry**: Single code path for all agent bindings.
*   **Quality**: Impossible to have a "bound" agent that ignores context or authority.
*   **Audit**: Every session has a cryptographically strict anchor record.
*   **Resilience**: Agents fix their own hallucinations during binding.

### Negative
*   **Latency**: Binding takes 5-10 seconds (generation + validation + potential retry).
*   **Strictness**: Agents may get stuck if they genuinely cannot satisfy the schema (e.g., in an empty repo). *Mitigation: "Quick" tier relaxes some checks.*

### Risks
*   **MCP Availability**: If the tool crashes, agents cannot bind. *Mitigation: Tool is core to HestAI-MCP.*
*   **Infinite Loops**: Retry logic must strictly enforce the 2-attempt limit.

---

## Migration Guide

1.  **Agents**: Update `system-steward`, `implementation-lead`, etc., to use `odyssean_anchor` tool instead of `anchor_submit`.
2.  **Commands**: Update `/bind` command to use `odyssean_anchor` MCP tool (see hub/library/commands/bind.md).
3.  **Subagents**: Update `Task()` prompt wrapper to instruct subagents to call `odyssean_anchor` first.

---

## Amendments

### Amendment 01: Schema Simplification to v4.0 (2026-01-01)

**Decision Source**: debates/2026-01-01-agent-format-oa.oct.md

**Summary**: Wind/Wall/Door debate synthesized schema simplification from 6 sections to 4 sections with Server-Authoritative ARM pattern.

**Changes**:

1. **Schema Reduction**: From 6 sections (BIND, ARM, FLUKE, TENSION, HAZARD, COMMIT) to 4 sections (BIND, ARM, TENSION, COMMIT)
   - FLUKE absorbed into BIND.AUTHORITY
   - HAZARD absorbed into TENSION anti-patterns
   - SOURCES redundant with CTX citations

2. **Server-Authoritative ARM**: Tool INJECTS ARM from server state rather than validating agent claims
   - Prevents context hallucination
   - ARM derived from: git state, PROJECT-CONTEXT.oct.md, clock_in session

3. **Terminology Resolution**:
   - SHANK (legacy) → BIND section
   - FLUKE (legacy) → absorbed into COMMIT/AUTHORITY
   - RAPH Vector → Complete 4-section structure

4. **Updated Tool Signature**:
```python
def odyssean_anchor(
    role: str,
    vector_candidate: str,  # Agent's BIND+TENSION+COMMIT (not ARM)
    session_id: str,        # For ARM injection
    tier: str = "default"
) -> OdysseanAnchorResult:
```

5. **Updated Canonical Schema (v4.0)**:
```octave
===RAPH_VECTOR::v4.0===
## BIND (Identity Lock)
ROLE::{agent_name}
COGNITION::{type}::{archetype}
AUTHORITY::RESPONSIBLE[{scope_description}]
// OR: AUTHORITY::DELEGATED[{parent_session_id}]
// NOTE: Brackets with scope/session are REQUIRED

## ARM (Context Proof - SERVER INJECTED)
PHASE::{current_phase}
BRANCH::{name}[{ahead}↑{behind}↓]
FILES::{count}[{top_modified}]
FOCUS::{focus_topic}

## TENSION (Cognitive Proof - AGENT GENERATED)
L{N}::[{constraint}]⇌CTX:{path}[{state}]→TRIGGER[{action}]
// Uses OCTAVE operators per octave-5-llm-core.oct.md:
// ⇌ = tension (binary opposition), → = flow (progression)
// ASCII aliases (<-> and ->) accepted for input

## COMMIT (Falsifiable Contract)
ARTIFACT::{file_path}
GATE::{validation_method}
===END_RAPH_VECTOR===
```

**Syntax Notes**:
- AUTHORITY requires brackets: `RESPONSIBLE[scope]` or `DELEGATED[parent_session]`
- TENSION uses OCTAVE operators: `⇌` (tension) and `→` (flow) per octave-5-llm-core.oct.md
- ASCII aliases (`<->` and `->`) accepted for input, normalized to Unicode canonical form

**Implementation Phases**:
- Phase 0: This amendment (schema freeze) - COMPLETE
- Phase 1: Implement odyssean_anchor tool with v4.0 + ARM injection - COMPLETE (PR #126)
- Phase 2: Implement OA-I6 tool gating - COMPLETE (gating.py, has_valid_anchor)
- Phase 3: Update /bind command - COMPLETE (hub/library/commands/bind.md)
- Phase 4: Documentation alignment - COMPLETE (2026-01-03)

**Implementation Evidence** (Issue #11):
- MCP Tool: src/hestai_mcp/mcp/tools/odyssean_anchor.py (949 lines)
- Gating: src/hestai_mcp/mcp/tools/shared/gating.py (has_valid_anchor)
- Server: src/hestai_mcp/mcp/server.py (odyssean_anchor exposed)
- Command: hub/library/commands/bind.md (v4.0 ceremony reference)
- Tests: 511 passing (as of 2026-01-03)
- Quality Gates: CRS (Codex) APPROVE, CE (Gemini) GO

---

## References

- Derived from Odyssean Anchor Project (ADRs 001, 002, 003)
- Living Orchestra North Star: I1 (Behavioral Spec), I3 (Structural Enforcement)
- debates/2026-01-01-agent-format-oa.oct.md (Amendment 01 synthesis)
- debates/2025-12-31-odyssean-anchor-strategy.oct.md (Prior decision)
