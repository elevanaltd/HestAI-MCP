# ADR-0046: Velocity-Layered Fragments Architecture

## Status

ACCEPTED

## Date

2024-12-24

## Context

The HestAI system requires a `.hestai/` directory structure that balances:
1. **Git visibility** - AI agents need to read and @tag context files
2. **Conflict prevention** - Multiple agents/humans working concurrently
3. **Operational simplicity** - Standard git workflows without esoteric knowledge

Two existing approaches were analyzed:

### OCTAVE Project (Symlink Approach)
```
.hestai → /Volumes/OCTAVE/.hestai-state-wt-octave-f44817b
```
- Symlink to external worktree directory
- Files invisible to `git ls-files`
- Low git footprint but broken visibility

### HestAI-MCP Project (Direct Files Approach)
```
.hestai/
├── context/
├── workflow/
├── reports/
└── sessions/
```
- Direct directory with committed files
- Full git visibility (19 tracked files)
- Concerns about commit frequency and conflicts

## Decision

A structured debate (Wind/Wall/Door pattern) was conducted to find optimal architecture.

### Proposals Evaluated

| Proposal | Source | Verdict |
|----------|--------|---------|
| Orthogonal Worktrees | Wind (Edge Optimizer) | REJECTED - 7x cognitive overhead, CI incompatible |
| Ledger/Event Sourcing | Wind (Pivot) | REJECTED - Incomplete implementation worse than none |
| Git Submodules | Wall (Critical Engineer) | REJECTED - Known pain points, overkill |
| Status Quo + Fragments | Wall | ACCEPTED as base |
| Velocity Layering | Wind (Final Edge) | ACCEPTED as refinement |

### Final Architecture: Velocity-Layered Fragments

Organize `.hestai/` by **change velocity**, not just topic:

```
.hestai/
├── workflow/                    # SLOW LAYER (monthly)
│   ├── 000-NORTH-STAR.md       # Human-curated constitutional docs
│   └── components/             # ADR summaries, methodology
│
├── context/                     # MEDIUM LAYER (daily-weekly)
│   ├── PROJECT-CONTEXT.oct.md  # Session-updated state
│   ├── PROJECT-ROADMAP.oct.md  # Phase planning
│   └── state/                  # FAST LAYER (hourly-daily)
│       ├── checklist.oct.md    # Current tasks
│       ├── blockers.oct.md     # Active blockers
│       └── current-focus.oct.md # Session focus
│
├── reports/                     # APPEND LAYER (per-session)
│   └── YYYY-MM-DD-{topic}.md   # Dated reports, unique filenames
│
└── sessions/
    └── active/                  # EPHEMERAL LAYER (gitignored)
        └── {session-id}/       # Transient session state
```

### Velocity Layer Definitions

| Layer | Velocity | Writers | Conflict Risk |
|-------|----------|---------|---------------|
| SLOW | Monthly | Human only | Minimal |
| MEDIUM | Daily-Weekly | System Steward MCP | Low |
| FAST | Hourly-Daily | Agents via MCP | Medium (mitigated) |
| APPEND | Per-session | Agents | Zero (unique names) |
| EPHEMERAL | Continuous | Agents | Zero (gitignored) |

## Consequences

### Positive

1. **Git Visibility Preserved**: All context files visible to `git ls-files`, agents can @tag
2. **Conflict Prevention**: Velocity isolation + fragmentation reduces collision surface 80%+
3. **Zero Cognitive Overhead**: Standard git workflow, no worktrees/submodules
4. **2AM Debuggability**: Just text files in directories - anyone can understand
5. **Audit Trail**: Reports layer provides history without event sourcing complexity

### Negative

1. **More Files to Commit**: ~20-30 files vs 1 symlink (acceptable trade-off)
2. **Migration Required**: OCTAVE project needs structure migration
3. **MCP Dependency**: Single-writer enforcement requires MCP tools

### Neutral

1. **OCTAVE Format**: Semantic compression optional but recommended
2. **Pre-commit Hooks**: Can add validation but not required

## Rejected Alternatives

### Orthogonal Worktrees (Wind Proposal 1)
- Mount `.hestai` as worktree tracking orphan branch
- **Rejected because**: `git status` blindness, clone ceremony, dual-push requirement, CI incompatible

### Ledger/Event Sourcing (Wind Proposal 2)
- Immutable events → projection to context
- **Rejected because**: No ordering mechanism, no snapshotting, deletion corrupts history

### Git Submodules (Wall Alternative)
- Separate repo for context
- **Rejected because**: Known UX pain, overkill for this problem

### Symlink to External (OCTAVE Status Quo)
- Current OCTAVE approach
- **Rejected because**: Files invisible to git, CI/CD broken, agent visibility lost

## Implementation

### Migration from Symlink

```bash
# 1. Remove symlink
rm .hestai

# 2. Create structure
mkdir -p .hestai/{workflow,context/state,reports,sessions/active}

# 3. Migrate content
cp -r /external/.hestai-state/* .hestai/

# 4. Update .gitignore
echo ".hestai/sessions/active/" >> .gitignore
echo ".hestai/reports/scratch/" >> .gitignore

# 5. Commit
git add .hestai
git commit -m "chore: migrate to velocity-layered .hestai structure"
```

### Single-Writer Enforcement

```python
# System Steward MCP validates writes
def validate_write(path: str, writer: str) -> bool:
    if "workflow/" in path:
        return writer == "human"
    if "context/" in path:
        return writer in ["system-steward", "mcp-tool"]
    return True  # Reports/sessions open to agents
```

## Debate Record

Full debate transcript available in debate-hall MCP:
- Thread ID: `hestai-context-architecture-2024-12-24`
- Participants: Wind (Gemini/Edge-Optimizer), Wall (Claude/Critical-Engineer), Door (Synthesizer)
- Turns: 6
- Outcome: APPROVED with synthesis

## References

- ADR-0033: Dual-Layer Context Architecture (foundational separation)
- ADR-0007: No Worktrees Policy (operational simplicity)
- Stewart Brand's "Shearing Layers" (velocity-based organization)
