# ADR-0031: GitHub Issue-Based Document Numbering

- **Status**: Implemented
- **Type**: ADR
- **Author**: system-steward
- **Created**: 2025-12-24
- **Updated**: 2025-12-27
- **GitHub Issue**: [#31](https://github.com/elevanaltd/HestAI-MCP/issues/31)
- **Phase**: B1
- **From-RFC**: RFC-0031 (ratified through adoption)

## Context

Multi-worktree environments create sequence clash conflicts when two branches simultaneously create documents with the same number (e.g., both creating `adr-0005-*.md`). This causes:

1. **Merge conflicts** at PR time
2. **Wasted work** when one branch must renumber
3. **Broken references** if other docs cite the conflicting number

**Key Insight**: GitHub Issues already solve this problem. When you create an issue, GitHub allocates a globally unique, monotonically increasing number.

## Decision

### Core Principle

**Document Number = GitHub Issue Number**

### Workflow

1. Create GitHub Issue with title "ADR: [Topic]" or "RFC: [Topic]"
2. GitHub assigns unique number (e.g., #31)
3. Create document as `adr-{ISSUE_NUMBER:04d}-topic.md`
4. Link issue in document frontmatter
5. PR references issue: "Implements #31"

### File Naming Convention

- **ADRs**: `docs/adr/adr-{ISSUE_NUMBER:04d}-{topic}.md`

> **Note**: Per ADR-0060, RFC files are no longer created. Proposals use GitHub Issues.

### Labels

Use GitHub labels to categorize: `adr`, `rfc`, `report`

## Consequences

### Positive

- **Zero numbering clashes** in multi-worktree development
- **Discussion thread** included with every document
- **GitHub Projects integration** for tracking
- **Linkability** via "Fixes #N" syntax

### Negative

- **Non-sequential numbers** (gaps tell project history - this is a feature)
- **Network dependency** for issue creation (acceptable given always-online workflow)
- **Issue noise** (mitigated by labels and Projects filtering)

## Implementation

**Status**: COMPLETE

**Evidence**:
- All ADRs 0033+ use issue-based numbering
- All RFCs 0031+ use issue-based numbering
- Zero numbering conflicts since adoption (2025-12-24)

## Related Documents

- [ADR-0033: Dual-Layer Context Architecture](./adr-0033-dual-layer-context-architecture.md)
- [ADR-0060: RFC/ADR Alignment](./adr-0060-rfc-adr-alignment.md)
- [GitHub Issue #31](https://github.com/elevanaltd/HestAI-MCP/issues/31)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
