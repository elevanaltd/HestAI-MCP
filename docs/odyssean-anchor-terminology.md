# Odyssean Anchor Terminology Guide

> **Trademark Notice**: "Odyssean Anchor" is a registered trademark of Shaun Buswell (UK00004198373). See [trademarks.md](trademarks.md) for usage guidelines.

**Status**: AUTHORITATIVE
**Date**: 2026-01-05
**Source**: debates/2026-01-05-oa5-terminology (debate synthesis)

---

## What this document standardizes

This document defines two things, and **keeps them separate**:

1. **Nautical anatomy** (SHANK / ARMS / FLUKES) as a *human mnemonic* for thinking about composition.
2. The **canonical runtime proof artifact** validated by tooling.

### The rule

- Nautical terms are allowed in explanations.
- Nautical terms **MUST NOT** be used as *runtime schema headers*.

---

## Canonical runtime artifact (OA5): Odyssean Anchor Proof

The **Odyssean Anchor Proof** is the canonical structured submission intended to be validated server-side by the `odyssean_anchor` tool.

It has three top-level sections:

- **IDENTITY** — who the agent is (agent-declared)
- **CONTEXT** — where/when the agent is (authoritative; MCP-enriched)
- **PROOF** — how the agent demonstrates it actually perceived context (agent-generated)
  - **TENSIONS** — 1..N cognitive proof lines (keystone)
  - **COMMIT** — falsifiable contract (artifact + gate)

### Minimal template

```
===ODYSSEAN_ANCHOR_PROOF::v5.0===

IDENTITY::
  ROLE::...
  COGNITION::...
  AUTHORITY::RESPONSIBLE[scope_description]  # or DELEGATED[parent_session_id]

CONTEXT::  # MCP-enriched (canonical output is authoritative; candidate values are checked for hallucination)
  PHASE::...
  BRANCH::...
  FILES::...

PROOF::
  TENSIONS::[
    L1::[constraint]⇌CTX:{path}[state]→TRIGGER[action]
  ]
  COMMIT::
    ARTIFACT::...
    GATE::...

===END_ODYSSEAN_ANCHOR_PROOF===
```

### Cognitive proof (keystone)

`L{N}::[constraint]⇌CTX:{path}[state]→TRIGGER[action]` is required because it forces a binding between:

- a *specific constitutional line* (`L{N}`),
- a *falsifiable piece of runtime context* (`CTX:{path}[state]`), and
- a concrete *action trigger* (`TRIGGER[...]`).

This is the anti-theater mechanism: it’s hard to fake consistently and easy to challenge.

---

## Nautical anatomy (mnemonic only)

Correct terms:

- **SHANK** — the main long part of an anchor.
- **ARMS** — the parts that extend out from the bottom of the shank.
- **FLUKES** — the curved ends of the arms that dig into the seabed.

Optional (available for future alignment if needed):

- **HEAD** — the top attachment point (where the chain/rope connects).
- **CROWN** — the lower junction where the shank and arms meet.

### Mnemonic mapping (conceptual)

- SHANK ↔ IDENTITY (static identity shaft)
- ARMS ↔ CONTEXT (reach into reality)
- FLUKES ↔ PROOF (the “bite”: tensions + commitment)

This framing can be useful as a teaching aid:

> SHANK (static identity) + ARMS (dynamic context reach) ⇒ FLUKES (holding power / commitment)

---

## RAPH: keep as a process, not an artifact

**RAPH** (Read–Absorb–Perceive–Harmonise) is a sequential processing directive (a *workflow*).

- RAPH may be used as an optional thinking protocol for complex / high-risk work.
- RAPH must **not** be used to name or label the runtime proof artifact.

The artifact is the **Odyssean Anchor Proof**; RAPH is a way an agent may process inputs before producing it.

---

## Deprecated terms (OA4)

The following terms are deprecated and should not appear in new examples:

- "RAPH Vector v4.0" (rename to **Odyssean Anchor Proof**)
- runtime schema headers: **BIND / ARM / TENSION / COMMIT**
  - use **IDENTITY / CONTEXT / PROOF** (TENSIONS + COMMIT)

Note: `ARM` is intentionally removed from runtime headers to avoid collision with nautical ARM.

---

## Quick reference

- **Designing an agent prompt / identity composition?** Use the nautical mnemonic.
- **Implementing or validating binding?** Use the OA5 Odyssean Anchor Proof schema.

---

## References

- ADR-0036: Odyssean Anchor Binding Architecture
- `.hestai/north-star/specs/odyssean-anchor-tool-spec.oct.md`
