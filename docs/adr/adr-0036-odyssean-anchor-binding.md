# ADR-0036: Odyssean Anchor Binding Architecture

**Status**: ACCEPTED
**Date**: 2025-12-19
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

### 1. The Unified Binding Ceremony (`/oa-load`)

All agents (main or sub) bind via a standardized sequence, orchestrated by the `/oa-load` command (or equivalent subagent protocol):

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

Agents must generate and submit this exact structure. The tool validates every field.

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

---

## Technical Specification

### Validation Logic

The MCP tool enforces strict rules. If any rule fails, it returns a formatted error message to the agent.

1.  **Structure**: Must have all headers (BIND, ARM, FLUKE, TENSION, HAZARD, COMMIT).
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
2.  **Commands**: Create `/oa-load` alias to trigger the 5-step sequence.
3.  **Subagents**: Update `Task()` prompt wrapper to instruct subagents to call `odyssean_anchor` first.

---

## References

- Derived from Odyssean Anchor Project (ADRs 001, 002, 003)
- Living Orchestra North Star: I1 (Behavioral Spec), I3 (Structural Enforcement)
