# Namespace Migration Guide

**Status:** ACTIVE
**ADR:** ADR-0240
**Namespace:** SYS

---

## Why Namespaces Are Needed

The System North Star (SYS) and Product North Star (PROD) each define six immutables (I1-I6). The same index refers to different principles in each document:

| Index | SYS Immutable | PROD Immutable |
|-------|---------------|----------------|
| I1 | Verifiable Behavioral Specification First (TDD) | Persistent Cognitive Continuity |
| I2 | Phase-Gated Progression | Structural Integrity Priority |
| I3 | Human Primacy | Dual Layer Authority |
| I4 | Discoverable Artifact Persistence | Freshness Verification |
| I5 | Quality Verification Before Progression | Odyssean Identity Binding |
| I6 | Explicit Accountability | Universal Scope |

A bare citation like "violates I2" is ambiguous. SYS::I2 and PROD::I2 describe different constraints.

---

## The Two Namespaces

**SYS::** — System-level governance documents
- `000-SYSTEM-HESTAI-NORTH-STAR.md`
- `CONSTITUTION.md`
- System ADRs (governance methodology)

**PROD::** — Product-level context documents
- `000-MCP-PRODUCT-NORTH-STAR-SUMMARY.oct.md`
- Product ADRs (implementation decisions)
- Workflow documents for specific products

---

## How to Adopt the Convention

### New Documents

Add `NAMESPACE::SYS` or `NAMESPACE::PROD` to the META section (OCTAVE) or front matter (YAML):

```
# OCTAVE
META:
  NAMESPACE::SYS

# YAML front matter
NAMESPACE::SYS
```

### Citations

Use the fully-qualified form when cross-namespace ambiguity exists:

```
# Correct — unambiguous
CITE[SYS::I2]   → Phase-Gated Progression
CITE[PROD::I2]  → Structural Integrity Priority

# Incorrect — ambiguous when both North Stars are in scope
CITE[I2]
```

Within a single-namespace context (e.g., inside a SYS document citing only SYS immutables), the short form `I2` remains valid when context is unambiguous.

---

## Examples

**Correct:**

```
IF(phase_gate_bypass) → BLOCK + CITE[SYS::I2] + ESCALATE[requirements-steward]
IF(context_drift)     → RE_ANCHOR + CITE[PROD::I4] + VALIDATE_FRESHNESS
```

**Incorrect (ambiguous):**

```
IF(phase_gate_bypass) → BLOCK + CITE[I2]   # Which I2?
```

**Correct (intra-namespace, context clear):**

```
# Inside a SYS document — short form valid
CITE[I2]  # unambiguous: Phase-Gated Progression
```

---

## Existing Documents

Existing documents without a `NAMESPACE::` declaration are treated as follows:
- System governance documents → assumed SYS::
- Product context documents → assumed PROD::

Add the declaration on next edit to make namespace explicit. Priority: documents that are frequently cited in enforcement protocols.
