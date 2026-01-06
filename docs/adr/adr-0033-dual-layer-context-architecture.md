# ADR-0033: Dual-Layer Context Architecture

**Status**: ACCEPTED
**Date**: 2025-12-19
**Author**: holistic-orchestrator (adapted from hestai-core ADR-0007)
**Implements**: HestAI-MCP foundational architecture
**GitHub Issue**: [#33](https://github.com/elevanaltd/HestAI-MCP/issues/33)

---

## Context

### The Problem

Traditional AI agent workflows lose context between sessions. When working on complex projects:
- Context is lost between conversations
- Agents can't access project history or decisions
- Multiple agents create conflicting files
- System governance rules drift across projects
- Symlinks and worktrees cause visibility issues

### Evidence from Previous Architecture

The legacy `hestai-core` worktree+symlink architecture caused:
- **Symlink commit failures**: "symbolic link restrictions" errors
- **Agent visibility problems**: Files invisible to `git ls-files`, can't `@tag`
- **Multi-agent conflicts**: No single writer enforcement
- **Governance drift**: System rules duplicated and diverging across projects

### Core Insight

The worktree architecture traded **visibility for isolation** - but visibility is essential for AI agents, while the isolation benefits never materialized.

**Solution**: Separate concerns into two distinct layers with different delivery mechanisms.

---

## Decision

Implement a **Dual-Layer Context Architecture**:

| Layer | Content | Delivery | Git Status | Writer |
|-------|---------|----------|------------|--------|
| **System Governance** | Rules, agents, methodology | MCP server injection | NOT committed | HestAI system |
| **Project Documentation** | Context, sessions, reports | Direct files | Committed | System Steward only |

### Layer 1: System Governance (Delivered Package)

System governance is treated as **installed software**, not editable files:

```
.hestai-sys/                          # Delivered by MCP server at activation
├── governance/
│   ├── rules/
│   │   ├── naming-standard.oct.md
│   │   ├── visibility-rules.oct.md
│   │   └── workflow-methodology.oct.md
│   └── workflow/
│       └── 001-workflow-north-star.oct.md
├── agents/                            # All agent prompts
│   ├── implementation-lead.oct.md
│   ├── critical-engineer.oct.md
│   ├── system-steward.oct.md
│   └── ... (50+ agents)
├── templates/                         # System templates
│   └── octave-micro-primer.oct.md
└── .version                           # Hub version marker
```

**Properties:**
- **Not git committed** in project repo - delivered at runtime
- **Immutable during work** - agents read, never modify
- **Versioned in Hub** - updating HestAI updates governance
- **No symlinks** - direct file injection by MCP server

### Layer 2: Project Documentation (Living, Single Writer)

Project documentation lives **directly in the repository**, fully visible to agents:

```
.hestai/
├── context/                         # Living operational state
│   ├── project-context.oct.md       # Project dashboard
│   ├── project-roadmap.oct.md       # Future direction
│   ├── project-history.oct.md       # Significant events
│   ├── project-checklist.oct.md     # Current tasks
│   └── context-negatives.oct.md     # Anti-patterns to avoid
├── workflow/                        # Project-specific governance
│   ├── 000-project-north-star.oct.md    # Project immutables
│   └── decisions/
│       └── decisions.oct.md         # Architectural rationale
├── sessions/
│   ├── active/                      # GITIGNORED (ephemeral)
│   └── archive/                     # Committed (durable)
│       ├── 2025-12-19-SESSION_ID.oct.md
│       └── learnings-index.jsonl
├── reports/                         # Audit artifacts
│   └── YYYY-MM-DD-{topic}.oct.md
```

System governance is injected to `.hestai-sys/` (top-level, gitignored) by the MCP server.

**Properties:**
- **Git committed** - visible to agents, `@taggable`, PR reviewable
- **OCTAVE format** - compressed, structured, parseable
- **Single writer: System Steward** - all modifications via MCP tools
- **No direct agent edits** - prevents conflicts

### The Single Writer Pattern

**Critical**: No agent writes to `.hestai/` directly. All writes go through System Steward MCP tools:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Agent A   │     │   Agent B   │     │   Agent C   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ clock_in          │ document_submit   │ context_update
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    System Steward      │
              │                        │
              │  1. Validates request  │
              │  2. Checks visibility- │
              │     rules.oct.md       │
              │  3. Routes to location │
              │  4. Writes via         │
              │     octave_create or   │
              │     octave_amend       │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │  .hestai/context/      │
              │  .hestai/workflow/     │
              │  .hestai/sessions/     │
              │  .hestai/reports/      │
              └────────────────────────┘
```

### Tool Flow Details

| Tool | Agent Calls | System Steward Does |
|------|-------------|---------------------|
| `clock_in` | Request session start | Validate, create session.json, return context paths to read |
| `clock_out` | Request session end | Compress transcript to OCTAVE via `octave_create`, archive, **update `.hestai/context/` with learnings** |
| `document_submit` | Submit a document | Check `visibility-rules.oct.md` for routing, write via `octave_create` |
| `context_update` | Request context change | Validate, write via `octave_create` or `octave_amend` |

**Key principle**: System Steward always uses `octave_create` or `octave_amend` MCP tools for all writes—never raw file operations.

---

## Implementation Status

### Current Implementation (Phase 2.5 Complete)

| Component | Status | Details |
|-----------|--------|---------|
|| Dual-layer structure | ✅ Complete | .hestai/ direct, .hestai-sys/ planned |
| Bundled Hub | ✅ Complete | Governance files included in package |
| MCP Server | ✅ Partial | clock_in/out working, document_submit pending |
| Single Writer | 🚧 Phase 3 | System Steward tools in progress |
| Governance Injection | 🚧 Phase 4 | Runtime delivery planned |

### MCP Tools

| Tool | Purpose | Status |
|------|---------|--------|
| `clock_in` | Session start, context loading | ✅ Complete |
| `clock_out` | Session archival, OCTAVE compression | ✅ Complete |
| `anchor_submit` | Agent identity validation | ✅ Complete |
| `document_submit` | Route documents to correct location | 🚧 Phase 3 |
| `context_update` | Merge context changes | 🚧 Phase 3 |

---

## Consequences

### Positive

- **Agent visibility restored**: All project docs in git, taggable
- **No symlink issues**: Direct files, normal git operations
- **Conflict prevention**: Single writer pattern eliminates races
- **Clear mental model**: System = delivered, Project = committed
- **Governance consistency**: Hub is single source, pushed to projects
- **OCTAVE standardization**: Compressed, structured, parseable

### Negative

- **Breaking change**: Requires migration from worktree architecture
- **MCP dependency**: Agents must use tools, not direct writes
- **Hub requirement**: Bundled governance must be maintained

### Risks

| Risk | Mitigation |
|------|------------|
| Agents bypass System Steward | Pre-commit hook blocks direct `.hestai/` writes |
| Hub unavailable | Bundled with package, no external dependency |
| OCTAVE learning curve | System Steward validates and assists |

---

## Validation Criteria

1. **Symlink Issues Resolved**
   - Agents can commit to `.hestai/` without errors
   - No "symbolic link restrictions" messages

2. **Agent Visibility**
   - Files discoverable via `git ls-files`
   - Can `@tag` files in conversation
   - Appear in PR diffs

3. **Single Writer Enforced**
   - All writes go through MCP tools
   - Pre-commit hook blocks direct writes
   - No multi-agent conflicts

4. **Governance Delivery**
   - `.hestai-sys/` populated on MCP start
   - Agents can read governance without symlinks
   - Version tracking works

---

## Future Evolution

### Phase 5+: Hub as Application

Transform the Hub from bundled files to an active management system:

1. **Project Registry** - Track all projects using HestAI
2. **Push Governance** - Update projects from central Hub
3. **Version Management** - Semantic versioning with breaking change notifications
4. **Dashboard UI** - Visual project health monitoring

See RFC-0002 for detailed Hub as Application design.

---

## References

- ADR-0002: Orchestra Map Architecture (Layer 3 semantic integration)
- OCTAVE usage guide (bundled governance): `src/hestai_mcp/_bundled_hub/library/octave/octave-usage-guide.oct.md`
- Project Roadmap: `.hestai/context/project-roadmap.oct.md`

---

## Decision Record

| Date | Actor | Action |
|------|-------|--------|
| 2025-12-19 | User | Identified need for dual-layer architecture |
| 2025-12-19 | holistic-orchestrator | Adapted ADR-0007 to ADR-0001 |
| 2025-12-19 | Project Team | ACCEPTED for HestAI-MCP |

---

**END OF ADR-0033**
