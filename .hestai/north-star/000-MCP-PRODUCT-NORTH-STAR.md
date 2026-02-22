# HESTAI-MCP - PRODUCT NORTH STAR

**Project**: HestAI-MCP Server & Tool Ecosystem
**Purpose**: The cognitive backbone for AI-assisted development
**Phase**: Implementation (B1)
**Status**: ✅ APPROVED — 2025-12-19
**Approved By**: System Architect

---

## COMMITMENT STATEMENT

This North Star document establishes the immutable requirements for the **HestAI-MCP Product**.

**Authority**: All work on the `hestai-mcp` codebase must align with these requirements. Any detected misalignment triggers immediate escalation.

**Amendment Process**: Changes to immutables require formal review and re-approval. This is a binding commitment, not a living suggestion.

---

## PROTECTION CLAUSE

If ANY agent detects misalignment between work and this North Star:

1.  **STOP** current work immediately
2.  **CITE** the specific North Star requirement being violated
3.  **ESCALATE** to requirements-steward for resolution

**Resolution Options**:
-   CONFORM work to North Star requirements
-   USER AMENDS North Star (formal process)
-   ABANDON incompatible implementation path

---

## SECTION 1: IDENTITY

### What HestAI-MCP IS

HestAI-MCP is **Cognitive Infrastructure**.

It is:
-   **A Persistent Memory System** that cures AI session amnesia.
-   **A Structural Governance Engine** that enforces rules via the environment.
-   **An Orchestra Conductor** that makes system context ambient and discoverable.
-   **A Dual-Layer Protocol** separating immutable rules from mutable project state.

**Core Metaphor**: The "Operating System" for the AI agent—providing memory, I/O (tools), and permission boundaries (governance).

---

### What HestAI-MCP IS NOT

HestAI-MCP is NOT:
-   ❌ **A SaaS Product**: It is a local-first server (though cloud-capable).
-   ❌ **Just a Tool Library**: It is a coherent system, not a grab-bag of scripts.
-   ❌ **Monorepo-Exclusive**: It optimizes for complexity but serves all structures.
-   ❌ **An AI Model**: It is the *context provider* for models, not the model itself.

---

## SECTION 2: THE UNCHANGEABLES (6 IMMUTABLES)

These requirements are **binding for the entire project**. Each has passed the Immutability Oath and is technology-neutral.

---

### I1: PERSISTENT COGNITIVE CONTINUITY

**Requirement**: The system must persist session context, decisions, and learnings across disjointed sessions. "Amnesia" is a system failure state.

**Technology-Neutral Expression**: No session starts blank. Every session inherits the sum total of previous relevant knowledge.

**Evidence (Oath Passage)**:
-   **Q1 (Immutable?)**: YES — "Storage costs/complexity < Continuity value"
-   **Q2 (Faster without?)**: NO — Amnesia forces expensive re-learning every run
-   **Q3 (True in 3 years?)**: YES — Context continuity is the eternal problem of AI

**Rationale**: Without persistence, HestAI is just another CLI wrapper. Memory is the product.

**Validation Plan**:
-   ✅ `clock_in` must load previous session context
-   ✅ `clock_out` must save new learnings
-   ✅ Regression tests must prove knowledge transfer between sessions

---

### I2: STRUCTURAL INTEGRITY PRIORITY

**Requirement**: Correctness and structural compliance always take precedence over execution velocity. We accept startup latency if required for integrity.

**Technology-Neutral Expression**: If the choice is "Fast & Loose" vs "Slow & Right," we choose Right.

**Evidence (Oath Passage)**:
-   **Q1 (Immutable?)**: YES — User explicitly stated "Integrity over Velocity"
-   **Q2 (Faster without?)**: NO — Speed gained by skipping integrity is technical debt
-   **Q3 (True in 3 years?)**: YES — Reliability > Raw Speed for autonomous systems

**Rationale**: An agent that runs fast but breaks the architecture is a virus, not a helper.

**Validation Plan**:
-   ✅ Benchmarks allow latency (e.g., 2m startup) for integrity checks
-   ✅ "Skip checks" flags are prohibited in production profiles

---

### I3: DUAL-LAYER AUTHORITY

**Requirement**: A strict separation must exist between **Immutable System Governance** (Read-Only/Injected) and **Mutable Project Context** (Read/Write).

**Technology-Neutral Expression**: Agents can write to the project, but they cannot rewrite the laws that govern them.

**Evidence (Oath Passage)**:
-   **Q1 (Immutable?)**: YES — Core architectural invariant (ADR-0001)
-   **Q2 (Faster without?)**: NO — Merging layers leads to governance drift
-   **Q3 (True in 3 years?)**: YES — Separation of Powers is timeless

**Rationale**: Prevents "rogue agent" scenarios where an AI rewrites its constraints to bypass them.

**Validation Plan**:
-   ✅ Tooling enforces Read-Only access to governance layer
-   ✅ Context injection keeps layers distinct

---

### I4: FRESHNESS VERIFICATION

**Requirement**: Context artifacts must be verified as "Current" before use. Using stale context is prohibited.

**Technology-Neutral Expression**: Data has a "Best Before" date. If expired, it must be refreshed or rejected.

**Evidence (Oath Passage)**:
-   **Q1 (Immutable?)**: YES — Stale context = Hallucination trigger
-   **Q2 (Faster without?)**: NO — Faster implementation of wrong context is useless
-   **Q3 (True in 3 years?)**: YES — Staleness problem does not age out

**Rationale**: "Live" generation is preferred, but "Verified Cached" is acceptable. "Stale" is never acceptable.

**Validation Plan**:
-   ✅ Artifacts must have timestamp/hash signatures
-   ✅ Usage checks verify signatures against current state
-   ✅ Stale artifacts trigger blocking errors

---

### I5: ODYSSEAN IDENTITY BINDING

**Requirement**: Agents must undergo a structural identity verification ceremony (RAPH) to operate. Generic/unbound agent operation is prohibited.

**Technology-Neutral Expression**: "Who are you?" is the first question. "I am [Role] bound by [Constitution]" is the only acceptable answer.

**Evidence (Oath Passage)**:
-   **Q1 (Immutable?)**: YES — User stated standard roles perform poorly
-   **Q2 (Faster without?)**: NO — Unbound agents drift and hallucinate
-   **Q3 (True in 3 years?)**: YES — Identity/Role alignment remains critical

**Rationale**: Prevents "generic assistant" drift. Enforces persona and capability constraints.

**Validation Plan**:
-   ✅ `odyssean_anchor` tool must run successfully before other tools
-   ✅ Tooling rejects commands from unbound sessions

---

### I6: UNIVERSAL SCOPE

**Requirement**: The system must function on any project repository structure. It must not be exclusive to specific architectures (e.g., monorepos).

**Technology-Neutral Expression**: We build for the universal developer. Complexity is handled, not required.

**Evidence (Oath Passage)**:
-   **Q1 (Immutable?)**: YES — User explicitly requested inclusion
-   **Q2 (Faster without?)**: NO — Niche tools die; universal tools survive
-   **Q3 (True in 3 years?)**: YES — Repo diversity will always exist

**Rationale**: Ensures HestAI can spread to any project, regardless of its legacy structure.

**Validation Plan**:
-   ✅ Test suite includes monorepo, polyrepo, and flat structures
-   ✅ Path resolution logic handles varying roots

---

## SECTION 3: ASSUMPTION REGISTER

These assumptions underpin the North Star. **Critical/High impact assumptions must be validated.**

| ID | Assumption | Source | Risk if False | Validation Plan | Owner | Confidence | Impact |
|----|-----------|--------|---------------|-----------------|-------|-----------|--------|
| A1 | MCP Protocol remains stable standard | Industry Trend | Rewrite of transport layer | Monitor Anthropic/Industry specs | System Architect | 90% | High |
| A2 | 2-min startup latency is acceptable | User Interview | User rejection/bypass | User Acceptance Testing | Product Owner | 80% | High |
| A3 | Local storage is sufficient (no cloud needed) | Privacy Stance | Multi-device friction | Feedback monitoring | System Architect | 75% | Medium |
| A4 | Agents can effectively "read" Octave format | Methodology | Context is illegible to AI | Compression benchmarks | AI Lead | 85% | Critical |
| A5 | Git is the universal substrate | Architecture | Non-git projects excluded | Market analysis | System Architect | 95% | Low |
| A6 | RAPH vectors effectively constrain behavior | Research | Identity binding fails | A/B testing agents | AI Lead | 70% | Critical |
| A7 | Dual-layer injection doesn't consume too much context | Architecture | Context window overflow | Token usage profiling | System Architect | 80% | High |
| A8 | Users will perform the "Commitment Ceremony" | Methodology | Governance ignored | UX testing | Product Owner | 60% | Medium |

### CRITICAL ASSUMPTIONS (Must validate before B2)
-   **A4 (Octave Readability)**: If agents can't read our context format, the product fails.
-   **A6 (RAPH Efficacy)**: If identity binding doesn't improve performance, it's just overhead.

---

## SECTION 4: COMMITMENT CEREMONY RECORD

**Date**: 2025-12-19
**Approver**: System Architect
**Status**: ✅ APPROVED

**Ceremony Transcript**:
> **Architect**: "Do you approve these 6 Immutables (Continuity, Integrity, Dual-Layer, Freshness, Identity, Universality) as the binding North Star for HestAI-MCP?"
> **User**: "Yes, approve these."

**Binding Authority**: This North Star is now the authoritative requirements document for HestAI-MCP.

---

**END OF NORTH STAR**
