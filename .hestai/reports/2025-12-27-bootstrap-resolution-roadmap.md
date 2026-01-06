# Bootstrap Resolution Roadmap

**Date**: 2025-12-27
**Author**: holistic-orchestrator
**Purpose**: Break the circular bootstrap and establish HestAI-MCP as the canonical exemplar

---

## The Bootstrap Problem

HestAI-MCP, OCTAVE MCP, and debate-hall-mcp form a circular dependency:
- HestAI-MCP builds the coordination tools
- OCTAVE MCP defines the language
- debate-hall-mcp enables structured decisions
- All three need proper `.hestai/` setup to coordinate
- That setup requires the tools we're building

**Solution**: Manually organize HestAI-MCP as the reference implementation.

---

## Key Policy Decisions

### 1. RFC/ADR Alignment (Issue 60)

| Artifact | Where | Status |
|----------|-------|--------|
| Drafts/Debates | GitHub Issues | Mutable |
| Ratified Decisions | `docs/adr/` | Immutable |
| `rfcs/` folder | DEPRECATED | Delete after migration |

**Principle**: "The Discussion IS the Draft. The Synthesis IS the Law."

### 2. File Retention Policy

| Format | Git Status | Rationale |
|--------|------------|-----------|
| `.json` / `.jsonl` (raw) | GITIGNORED | Machine format, large, reconstructible |
| `.oct.md` (compressed) | COMMITTED | Semantic density, audit trail |

### 3. Debates Folder

- Add `debates/*.json` to `.gitignore`
- Enhance `close_debate` to generate OCTAVE compressed version
- Keep `debates/*.oct.md` committed as evidence

### 4. Session Archives

- Already correct: `.jsonl` should be gitignored (currently not)
- Keep `.oct.md` committed
- Update `.gitignore` to exclude `*-raw.jsonl`

---

## Directory Structure (Canonical)

```
project-root/
├── .hestai/                    # Product context (committed)
│   ├── context/                # Living state (MEDIUM velocity)
│   │   ├── PROJECT-CONTEXT.oct.md
│   │   ├── PROJECT-CHECKLIST.oct.md
│   │   ├── PROJECT-ROADMAP.oct.md
│   │   └── state/              # FAST velocity (hourly)
│   │       ├── checklist.oct.md
│   │       ├── blockers.oct.md
│   │       └── current-focus.oct.md
│   ├── workflow/               # Methodology (SLOW velocity)
│   │   ├── 000-*-NORTH-STAR.md
│   │   ├── components/
│   │   └── test-context/
│   ├── sessions/
│   │   ├── active/             # GITIGNORED
│   │   └── archive/            # .oct.md committed, .jsonl gitignored
│   └── reports/                # Evidence (committed)
│
├── .hestai-sys/                # GITIGNORED - MCP-injected governance
│
├── src/hestai_mcp/_bundled_hub/ # SOURCE for .hestai-sys (this project only)
│   ├── governance/
│   │   ├── workflow/           # System North Star
│   │   └── rules/              # visibility-rules, naming-standard, etc.
│   ├── agents/
│   ├── templates/
│   ├── library/
│   └── tools/
│
├── docs/                       # Developer documentation
│   ├── adr/                    # Architecture Decision Records
│   └── ARCHITECTURE.md
│
├── debates/                    # Debate transcripts
│   └── *.oct.md                # Committed (JSON gitignored)
│
└── .claude/                    # Claude Code configuration
    ├── agents/
    └── skills/
```

---

## Roadmap Phases

### Phase 1: Policy Finalization
- [ ] Create ADR-0060 from Issue 60 synthesis
- [ ] Update `src/hestai_mcp/_bundled_hub/governance/rules/visibility-rules.oct.md` with file retention policy
- [ ] Add debates/ handling to visibility-rules

### Phase 2: RFC Deprecation
- [ ] Review each RFC in `rfcs/active/`:
  - 0031 → Already has Issue? Check status
  - 0037 → Migrate to Issue or close
  - 0038 → Migrate to Issue or close
  - 0039 → Migrate to Issue or close
  - 0040 → Migrate to Issue or close
  - 0054 → Migrate to Issue or close
  - 0060 → Issue exists (#60), delete RFC file
- [ ] Create redirect stubs or delete `rfcs/` folder entirely
- [ ] Update any references to rfcs/ in docs

### Phase 3: Gitignore Updates
- [ ] Add `debates/*.json` to .gitignore
- [ ] Add `.hestai/sessions/archive/*-raw.jsonl` to .gitignore
- [ ] Verify all raw/ephemeral files are excluded

### Phase 4: Debates Compression
- [ ] Convert existing debate JSON to OCTAVE (4 files)
- [ ] Add OCTAVE output to `close_debate` tool (debate-hall-mcp enhancement)

### Phase 5: Directory Audit
- [ ] Review all files in `.hestai/reports/` - correct format?
- [ ] Review `.hestai/workflow/` - all components correct?
- [ ] Review `hub/` structure against hub-authoring-rules
- [ ] Delete orphaned/stale content
- [ ] Update PROJECT-CONTEXT with findings

### Phase 6: Documentation
- [ ] Create setup guide for new projects
- [ ] Document the file retention policy
- [ ] Update ARCHITECTURE.md with finalized structure

---

## Dependencies

| Task | Depends On |
|------|------------|
| ADR-0060 creation | Issue 60 finalized |
| RFC deletion | RFCs migrated to Issues |
| Debates compression | debate-hall-mcp enhancement (optional) |

---

## Success Criteria

1. **No `rfcs/` folder** - All proposals are Issues, all decisions are ADRs
2. **Clean .gitignore** - Raw JSON excluded, OCTAVE committed
3. **Visibility-rules compliance** - Every file in correct location
4. **src/hestai_mcp/_bundled_hub/ complete** - All governance artifacts present and consistent
5. **Setup guide exists** - New projects can follow documented process

---

## Quick Wins (Do Now)

1. Update .gitignore with raw file patterns
2. Create ADR-0060 from Issue 60
3. Delete `rfcs/active/0060-agoral-forge.md` (duplicate of Issue)
