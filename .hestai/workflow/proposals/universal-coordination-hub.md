# PROPOSAL: Universal Coordination Hub

**Status**: DRAFT
**Author**: User (documented by AI)
**Date**: 2025-12-25
**Related**: Living Artifacts, Orchestra Map components

---

## Summary

A proposal for a persistent, holistic coordination layer that exists outside individual repository snapshots, providing cross-repository context for orchestrating AI agents.

---

## The Problem

### Current State: Snapshot Isolation

The `.hestai/` folder in each repository is:
- A **point-in-time snapshot** generated at session start
- **Repository-scoped** - knows nothing about other projects
- **Ephemeral context** - regenerated each session, committed for audit

This works well for single-repo operations but creates a gap:

**There is no persistent, holistic view across all coordinated work.**

### The Gap

When a controlling AI (e.g., the Holistic Orchestrator) needs to:
- Understand state across multiple repositories
- Track long-running initiatives spanning projects
- Maintain persistent memory that survives session boundaries
- See the "big picture" without loading every repo's context

...there is currently no designated home for this meta-coordination.

---

## The Proposal

### Universal Coordination Hub

A **persistent, external coordination layer** that:

1. **Lives Outside Repository Snapshots**
   - Not in `.hestai/` (which is repo-specific and ephemeral)
   - Could live in a dedicated coordination repository
   - Could live in a user-level directory (e.g., `~/.hestai/hub/`)
   - Could live in the MCP server itself

2. **Accessible Only to Orchestrating AI**
   - Not every agent needs access
   - The coordinating intelligence (HO) uses it to maintain continuity
   - Individual worker agents operate within their repo's `.hestai/` context

3. **Provides Holistic Context**
   - Cross-repository state awareness
   - Long-term initiative tracking
   - Persistent decision memory
   - Inter-project dependency awareness

---

## Relationship to Existing Components

| Component | Scope | Persistence | Purpose |
|-----------|-------|-------------|---------|
| `.hestai/context/` | Single repo | Snapshot (session) | Worker agent context |
| **Universal Hub** | All repos | Persistent | Orchestrator context |
| Living Artifacts | Single repo | Generated | Freshness verification |
| Orchestra Map | Single repo | Static | Dependency analysis |

The Universal Hub is the **orchestrator's persistent memory** while `.hestai/` folders are **worker agents' session context**.

---

## Potential Implementations

### Option A: Hub Repository
A dedicated `hestai-coordination` repository that:
- Contains cross-project state in OCTAVE format
- Is referenced by the MCP server
- Provides the "uber controlling hub" for orchestration

### Option B: User-Level Directory
A `~/.hestai/hub/` directory that:
- Lives outside any specific project
- Contains persistent orchestration state
- Is maintained by the MCP server

### Option C: MCP Server State
The HestAI-MCP server itself maintains:
- Persistent state in its own storage
- Exposed via dedicated tools (not file-based)
- Accessible only to authorized orchestrators

---

## Proposed Immutables (If Implemented)

### I1: EXTERNAL PERSISTENCE
The Universal Hub must persist outside of individual repository snapshot cycles.

### I2: ORCHESTRATOR-ONLY ACCESS
Worker agents should not directly read/write the Universal Hub. The orchestrator mediates access.

### I3: REPOSITORY REFERENCE, NOT DUPLICATION
The Hub references repo state, not duplicates it. Single source of truth.

### I4: AUDIT TRAIL
Changes to the Universal Hub must be logged and traceable.

---

## Open Questions

1. **Where should the Hub physically live?** (Repository? Directory? Server state?)
2. **What format should Hub state use?** (OCTAVE? JSONL? Both?)
3. **How does the Hub discover repositories it coordinates?** (Config? Auto-discovery?)
4. **What happens when the Hub and a repo's `.hestai/` diverge?** (Hub is authoritative? Merge?)

---

## Next Steps

This is a **conceptual proposal**. Before implementation:

1. **Validate the need** - Is cross-repo orchestration actually required?
2. **Choose implementation** - Which option (A/B/C) best fits the architecture?
3. **Define scope** - What exactly does the Hub contain?
4. **Prototype** - Build minimal version, test with HO agent

---

**END OF PROPOSAL**
