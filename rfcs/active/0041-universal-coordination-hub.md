# RFC-0041: Universal Coordination Hub

- **Status**: Draft
- **Author**: User (documented by AI)
- **Created**: 2025-12-25
- **Updated**: 2025-12-25
- **GitHub Issue**: TBD (create issue with title "RFC: Universal Coordination Hub" and label `rfc`)

## Summary

A persistent, holistic coordination layer that exists outside individual repository snapshots, providing cross-repository context for orchestrating AI agents.

## Motivation

The `.hestai/` folder in each repository is:
- A **point-in-time snapshot** generated at session start
- **Repository-scoped** - knows nothing about other projects
- **Ephemeral context** - regenerated each session, committed for audit

This works well for single-repo operations but creates a gap:

**There is no persistent, holistic view across all coordinated work.**

When a controlling AI (e.g., the Holistic Orchestrator) needs to:
- Understand state across multiple repositories
- Track long-running initiatives spanning projects
- Maintain persistent memory that survives session boundaries
- See the "big picture" without loading every repo's context

...there is currently no designated home for this meta-coordination.

## Detailed Design

### Core Concept

A **Universal Coordination Hub** is a persistent, external coordination layer that:

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

### Relationship to Existing Components

| Component | Scope | Persistence | Purpose |
|-----------|-------|-------------|---------|
| `.hestai/context/` | Single repo | Snapshot (session) | Worker agent context |
| **Universal Hub** | All repos | Persistent | Orchestrator context |
| Living Artifacts | Single repo | Generated | Freshness verification |
| Orchestra Map | Single repo | Static | Dependency analysis |

The Universal Hub is the **orchestrator's persistent memory** while `.hestai/` folders are **worker agents' session context**.

### Proposed Immutables

#### I1: EXTERNAL PERSISTENCE
The Universal Hub must persist outside of individual repository snapshot cycles.

#### I2: ORCHESTRATOR-ONLY ACCESS
Worker agents should not directly read/write the Universal Hub. The orchestrator mediates access.

#### I3: REPOSITORY REFERENCE, NOT DUPLICATION
The Hub references repo state, not duplicates it. Single source of truth.

#### I4: AUDIT TRAIL
Changes to the Universal Hub must be logged and traceable.

## Examples

### Example 1: Cross-Repository Initiative Tracking

```
# Universal Hub state
INITIATIVES:
  - id: auth-migration
    status: in_progress
    repositories:
      - hestai-mcp: B2 (auth module)
      - web-app: waiting (depends on hestai-mcp)
      - mobile-app: not_started
    decisions:
      - 2025-12-20: Chose JWT over sessions
      - 2025-12-22: Added refresh token rotation
```

### Example 2: Orchestrator Query

HO agent asks: "What's blocking the mobile app work?"

Hub responds: "Auth module in hestai-mcp is at B2. Web-app is waiting. Mobile-app cannot start until web-app completes integration."

## Drawbacks

- **Complexity**: Adds another layer to the system
- **Sync challenges**: Keeping Hub and repo `.hestai/` folders coherent
- **Single point of failure**: If Hub corrupts, orchestration breaks
- **Access control**: Determining who/what can write to the Hub

## Alternatives

### Option A: Hub Repository
A dedicated `hestai-coordination` repository that:
- Contains cross-project state in OCTAVE format
- Is referenced by the MCP server
- Provides the "uber controlling hub" for orchestration

**Pros**: Git-based, auditable, familiar tooling
**Cons**: Another repo to manage, potential sync issues

### Option B: User-Level Directory
A `~/.hestai/hub/` directory that:
- Lives outside any specific project
- Contains persistent orchestration state
- Is maintained by the MCP server

**Pros**: Simple, local, no additional repos
**Cons**: Not version-controlled, machine-specific

### Option C: MCP Server State
The HestAI-MCP server itself maintains:
- Persistent state in its own storage
- Exposed via dedicated tools (not file-based)
- Accessible only to authorized orchestrators

**Pros**: Centralized, tool-mediated access
**Cons**: Server becomes stateful, harder to inspect

## Unresolved Questions

1. **Where should the Hub physically live?** (Repository? Directory? Server state?)
2. **What format should Hub state use?** (OCTAVE? JSONL? Both?)
3. **How does the Hub discover repositories it coordinates?** (Config? Auto-discovery?)
4. **What happens when the Hub and a repo's `.hestai/` diverge?** (Hub is authoritative? Merge?)
5. **How does this relate to RFC-0038 (Hub as Application)?** (Are they the same thing?)

## Implementation Plan

- [ ] Phase 1: Validate need through user research / HO agent usage patterns
- [ ] Phase 2: Choose implementation option (A/B/C)
- [ ] Phase 3: Define Hub schema and state format
- [ ] Phase 4: Prototype minimal Hub with HO integration
- [ ] Phase 5: Production implementation with full audit trail
