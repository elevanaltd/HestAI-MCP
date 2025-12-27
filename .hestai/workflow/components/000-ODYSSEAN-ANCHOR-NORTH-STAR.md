// REFERENCE: points-to-canonical
# COMPONENT NORTH STAR: ODYSSEAN ANCHOR

**Component**: Odyssean Anchor (Identity Binding Protocol)
**Parent**: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
**Status**: ACTIVE
**Version**: 1.0

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **Odyssean Anchor** component.
It inherits all requirements from the **System North Star** and **HestAI-MCP Product North Star**.
Any deviation requires formal amendment.

---

## SECTION 1: THE UNCHANGEABLES (7 Immutables)

### I1: UNIFIED BINDING PATH
**Requirement**: A single, universal binding protocol must be used for ALL agents (main, sub-agents, tools). "Special paths" for different agent types are prohibited.
**Rationale**: Fragmentation in binding logic creates security holes where "dumb" agents bypass controls.
**Validation**: `/bind` (or its API equivalent) is the exclusive entry point.

### I2: STRUCTURAL VALIDATION (RAPH VECTOR)
**Requirement**: Identity is not a string; it is a cryptographic structure (RAPH Vector) containing Role, Context Proof (ARM), and Authority (FLUKE). This structure must be machine-validated.
**Rationale**: Text-based identity ("I am X") is hallucinatable. Structure proves cognitive processing.
**Validation**: The `odyssean_anchor` tool rejects any input failing the RAPH schema.

### I3: MANDATORY SELF-CORRECTION
**Requirement**: The system must reject invalid anchors with specific guidance, and the agent must be architected to catch this rejection and retry. Silent failure or "good enough" acceptance is prohibited.
**Rationale**: Agents hallucinate. The protocol must force them to "think again" rather than accepting garbage.
**Validation**: Test suite verifies the "Reject → Guidance → Retry → Success" loop.

### I4: CONTEXTUAL PROOF (THE ARM)
**Requirement**: Binding cannot occur in a vacuum. The anchor must contain proof of awareness of the current environment (ARM - Phase, Branch, Files).
**Rationale**: An identity bound without context is a dangerous "brain in a jar."
**Validation**: Anchor submission fails if `ARM` section does not match actual git state.

### I5: AUTHORITY INHERITANCE (THE FLUKE)
**Requirement**: Sub-agents must explicitly cite the authority/task delegated by the parent. They cannot generate their own authority.
**Rationale**: Prevents "rogue sub-agents" drifting from the main objective.
**Validation**: `FLUKE` section must link to a parent session or task ID.

### I6: TOOL GATING ENFORCEMENT
**Requirement**: Work tools MUST check for a valid anchor before executing. Validation alone is insufficient; enforcement is mandatory.
**Rationale**: Agents can bypass binding via direct tool calls if the tools themselves do not check for identity.
**Validation**: `has_valid_anchor(session_id)` check gates all work tool execution.

### I7: COGNITIVE BINDING PERSISTENCE
**Requirement**: The validated vector MUST be returned to the agent's active conversation context, not just written to a log file.
**Rationale**: File output alone doesn't create cognitive binding; the agent must "see" its identity in working memory to act on it.
**Validation**: MCP returns the canonical vector to the conversation history upon success.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **Schema** | RAPH structure (I2) | Specific field names (can evolve) |
| **Retry Limit** | Must exist (I3) | Exact count (currently 2) |
| **Validation Strictness** | Must validate ARM/FLUKE (I4, I5) | "Quick" vs "Deep" tier rules |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Validation Plan |
|----|------------|-----------------|
| C-A1 | Agents can self-correct JSON/YAML after 1 error | A/B Testing with different models |
| C-A2 | 5-10s binding latency is acceptable | User feedback monitoring |
| C-A3 | Git state is always readable for ARM proof | Edge case testing (bare repo) |

---
