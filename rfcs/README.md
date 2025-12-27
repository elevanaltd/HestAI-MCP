# RFC (Request for Comments) Directory

> ⚠️ **DEPRECATION NOTICE**: Per [ADR-0060](../docs/adr/adr-0060-rfc-adr-alignment.md), the RFC folder is deprecated.
>
> **New Process**: "The Discussion IS the Draft. The Synthesis IS the Law."
> - **Proposals/Debates** → GitHub Issues with label `rfc` or `adr`
> - **Ratified Decisions** → ADRs in `docs/adr/`
>
> These files are retained for historical reference. Future discussions should happen in GitHub Issues.

---

This directory contains proposals and experimental designs for the HestAI MCP system.

## RFC Migration Summary (Audit 2025-12-27)

| RFC | Status | Migrated To |
|-----|--------|-------------|
| 0031 | **MIGRATED** | [ADR-0031](../docs/adr/adr-0031-github-issue-based-numbering.md) |
| 0037 | PENDING | Discussion continues in [Issue #37](https://github.com/elevanaltd/HestAI-MCP/issues/37) |
| 0038 | PENDING | Discussion continues in [Issue #38](https://github.com/elevanaltd/HestAI-MCP/issues/38) |
| 0039 | **MIGRATED** | [ADR-0039](../docs/adr/adr-0039-agent-master-forge.md) |
| 0040 | **MIGRATED** | [ADR-0040](../docs/adr/adr-0040-agent-patterns-library.md) |
| 0054 | PENDING | Discussion continues in [Issue #54](https://github.com/elevanaltd/HestAI-MCP/issues/54) |
| 0060 | **MIGRATED** | [ADR-0060](../docs/adr/adr-0060-rfc-adr-alignment.md) |

## Remaining RFCs (Pending Decisions)

### [RFC-0037: Context Registry](active/0037-context-registry.md)
**Status**: PENDING (Future B2+ Feature)
**GitHub Issue**: [#37](https://github.com/elevanaltd/HestAI-MCP/issues/37)
Proposes a centralized context registry for managing session and agent contexts across the HestAI ecosystem.

### [RFC-0038: Hub as Application](active/0038-hub-as-application.md)
**Status**: PENDING (Future B3+ Feature)
**GitHub Issue**: [#38](https://github.com/elevanaltd/HestAI-MCP/issues/38)
Transform the HestAI Hub from static governance files into an active application with project registry, push capability, and version management.

### [RFC-0054: Universal Coordination Hub](active/0054-universal-coordination-hub.md)
**Status**: PENDING (Future Architecture)
**GitHub Issue**: [#54](https://github.com/elevanaltd/HestAI-MCP/issues/54)
A persistent, holistic coordination layer outside repository snapshots for cross-repository orchestration context.

## Structure

```
rfcs/
├── README.md                 # This file
├── 0000-template.md          # Template for new RFCs (legacy)
├── active/                   # RFCs pending decision
│   ├── 0037-context-registry.md              # PENDING
│   ├── 0038-hub-as-application.md            # PENDING
│   └── 0054-universal-coordination-hub.md    # PENDING
├── implemented/              # (empty - RFCs migrate to ADRs)
└── experimental/             # (empty - cleaned up 2025-12-27)
```

## Process (Deprecated)

Per ADR-0060, new proposals should be created as GitHub Issues, not RFC files.

When a decision is ratified:
1. Create ADR in `docs/adr/adr-{ISSUE_NUMBER:04d}-{topic}.md`
2. Delete the RFC file (if any)
3. Update this README

## Legacy RFCs Migrated to ADRs

- **RFC-0031** → [ADR-0031: GitHub Issue-Based Numbering](../docs/adr/adr-0031-github-issue-based-numbering.md) (Implemented)
- **RFC-0039** → [ADR-0039: Agent Master Forge](../docs/adr/adr-0039-agent-master-forge.md) (Implemented)
- **RFC-0040** → [ADR-0040: Agent Patterns Library](../docs/adr/adr-0040-agent-patterns-library.md) (Implemented)
- **RFC-0060** → [ADR-0060: RFC/ADR Alignment](../docs/adr/adr-0060-rfc-adr-alignment.md) (Accepted)
