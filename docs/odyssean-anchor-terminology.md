# Odyssean Anchor Terminology Guide

> **Trademark Notice**: "Odyssean Anchor" is a registered trademark of Shaun Buswell (UK00004198373). See [trademarks.md](trademarks.md) for usage guidelines.

**Status**: AUTHORITATIVE
**Date**: 2026-01-01
**Source**: debates/2026-01-01-identity-vs-binding-terminology.oct.md

---

## Overview

The Odyssean Anchor system uses terminology at **two distinct abstraction layers**. Understanding this stratification prevents confusion when reading documentation or building agents.

---

## The Two Layers

### Layer 1: Identity Composition (Design-Time)

**Purpose**: Describes HOW TO BUILD agent constitutions

**Metaphor**: A nautical anchor's physical anatomy

```
ODYSSEAN ANCHOR (The Artifact)
       │
   [SHANK]          ← WHO: Core identity (cognition + archetype)
       │
   [ARM]            ← WHERE/WHEN: Phase context (operational environment)
       │
   [FLUKE]          ← WHAT: Capabilities (skills, patterns, authority)
```

**Use this when**: Designing agent prompts, composing agent identities, discussing agent architecture.

### Layer 2: Runtime Binding (Validation)

**Purpose**: Describes HOW TO VALIDATE agents absorbed context correctly

**Schema**: RAPH Vector v4.0

```
RAPH VECTOR (The Proof)
├── BIND      ← Identity lock (role + authority declaration)
├── ARM       ← Context proof (server-injected git state, phase, files)
├── TENSION   ← Cognitive proof (agent reasoning with citations)
└── COMMIT    ← Falsifiable contract (artifact + validation gate)
```

**Use this when**: Implementing binding validation, working with odyssean_anchor tool, debugging binding failures.

---

## Why ARM Appears in Both Layers

ARM is not a collision—it's the **same semantic concept** at different abstraction levels.

**Nautical meaning**: The arm (or "scope") is the cable connecting the anchor to the ship—the reach into reality.

| Layer | ARM Represents |
|-------|----------------|
| Identity Composition | The agent's contextual awareness capability |
| Runtime Binding | Proof of that contextual awareness (actual git state, phase, files) |

The runtime ARM is the **embodiment** of the identity ARM. One describes the capability; the other proves its use.

---

## Terminology Glossary

### Identity Composition Terms (SHANK/ARM/FLUKE)

| Term | Meaning | Example |
|------|---------|---------|
| **Odyssean Anchor** | Complete agent identity architecture | SHANK + ARM + FLUKE |
| **SHANK** | WHO the agent is | COGNITION::LOGOS, ARCHETYPE::HEPHAESTUS |
| **ARM** | WHERE/WHEN the agent operates | BUILD phase, code-focused context |
| **FLUKE** | WHAT the agent can do | Skills: TDD, security-analysis; Authority: RESPONSIBLE |

### Runtime Binding Terms (RAPH Vector v4.0)

| Term | Meaning | Example |
|------|---------|---------|
| **RAPH Vector** | Binding proof artifact | 4-section structured submission |
| **BIND** | Identity assertion (encompasses SHANK + FLUKE) | `ROLE::implementation-lead` |
| **ARM** | Context proof (server-injected, authoritative) | `BRANCH::feat/auth[2↑0↓]` |
| **TENSION** | Cognitive reasoning proof (agent-generated) | `[TDD_FIRST]↔CTX:tests/[empty]→TRIGGER[write_test]` |
| **COMMIT** | Falsifiable contract | `ARTIFACT::src/auth/service.ts` |

---

## Relationship Mapping

| Identity (Design) | Runtime (Binding) | Relationship |
|-------------------|-------------------|--------------|
| SHANK | BIND | BIND encompasses SHANK's identity declaration |
| ARM | ARM | Same semantic: contextual reach into reality |
| FLUKE | BIND.AUTHORITY | FLUKE's authority concept absorbed into BIND |
| *(none)* | TENSION | New in runtime: agent reasoning proof |
| *(none)* | COMMIT | New in runtime: falsifiable contract |

---

## Quick Reference

**Building an agent prompt?** Think SHANK (who) + ARM (where/when) + FLUKE (what).

**Validating agent binding?** Check BIND + ARM + TENSION + COMMIT in RAPH Vector.

**Confused about ARM?** Same concept, different layers. Identity ARM = capability. Runtime ARM = proof.

---

## References

- ADR-0036: Odyssean Anchor Binding Architecture
- debates/2026-01-01-identity-vs-binding-terminology.oct.md
- debates/2026-01-01-agent-format-oa.oct.md (Amendment 01 context)
