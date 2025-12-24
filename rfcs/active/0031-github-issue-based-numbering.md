# RFC-0031: GitHub Issue-Based Document Numbering

- **Status**: Proposed
- **Author**: System Steward
- **Created**: 2025-12-24
- **Updated**: 2025-12-24
- **GitHub Issue**: [#31](https://github.com/elevanaltd/HestAI-MCP/issues/31)

## Summary

Adopt GitHub Issue numbers as the canonical identifier for numbered documents (ADRs, RFCs) to eliminate sequence clash conflicts in multi-worktree environments.

## Motivation

### The Problem

With 13+ active git worktrees, two branches can simultaneously create documents with the same sequence number (e.g., both creating `adr-0005-auth-changes.md`). This causes:

1. **Merge conflicts** at PR time
2. **Wasted work** when one branch must renumber
3. **Broken references** if other docs cite the conflicting number

### Why Current Architecture Doesn't Solve This

| Component | Role | Why It Fails |
|-----------|------|--------------|
| System Steward | Routes docs to locations | Per-worktree, no cross-worktree awareness |
| naming-standard.oct.md | Defines `adr-NNNN-topic.md` | No allocation mechanism |
| CI pipeline | Validates quality | No duplicate detection |

### The Insight

GitHub Issues already solve this problem. When you create an issue, GitHub allocates a globally unique, monotonically increasing number. Two worktrees creating issues simultaneously get #15 and #16, never #15 and #15.

## Detailed Design

### Core Principle

**Document Number = GitHub Issue Number**

The issue becomes the "ticket" for the document, providing:
- Unique identifier allocation
- Discussion thread
- Linkability (`Fixes #31`)
- GitHub Projects integration

### Workflow

```
1. Developer decides to write an ADR/RFC
2. Create GitHub Issue with title: "ADR: [Topic]" or "RFC: [Topic]"
3. GitHub assigns number (e.g., #31)
4. Create document: adr-0031-topic.md or 0031-topic.md
5. Link issue in document frontmatter
6. Discussion happens in issue comments
7. Document contains the formal decision/specification
8. PR references issue: "Implements #31"
```

### File Naming Convention

```
# ADRs
docs/adr/adr-{ISSUE_NUMBER:04d}-{topic}.md
Example: docs/adr/adr-0031-github-issue-numbering.md

# RFCs
rfcs/active/{ISSUE_NUMBER:04d}-{topic}.md
Example: rfcs/active/0031-github-issue-numbering.md
```

### Document Template Updates

Add GitHub Issue field to frontmatter:

```markdown
# RFC-0031: Title

- **Status**: Proposed
- **Author**: Name
- **Created**: YYYY-MM-DD
- **GitHub Issue**: [#31](https://github.com/org/repo/issues/31)
```

### Relationship Between Issue and Document

| Aspect | Issue | Document |
|--------|-------|----------|
| **Purpose** | Tracking, discussion, unique ID | Formal specification |
| **Content** | Summary, comments, status | Full design details |
| **Lifecycle** | Open → Closed | Draft → Active → Superseded |
| **Discovery** | GitHub search, Projects | Git grep, file system |

### Label Convention

Create labels to categorize document-related issues:

- `adr` - Architecture Decision Record
- `rfc` - Request for Comments
- `report` - Formal numbered report

### GitHub Projects Integration

Issues can be added to GitHub Projects for:
- Tracking related ADRs/RFCs together
- Kanban-style workflow (Draft → Review → Accepted)
- Cross-linking with feature work

## Examples

### Example 1: Creating an ADR

```bash
# 1. Create issue
gh issue create --title "ADR: Use PostgreSQL for persistence" --label "adr"
# Returns: https://github.com/org/repo/issues/42

# 2. Create document
cat > docs/adr/adr-0042-use-postgresql.md << 'EOF'
# ADR-0042: Use PostgreSQL for Persistence

- **Status**: Proposed
- **GitHub Issue**: [#42](https://github.com/org/repo/issues/42)
...
EOF

# 3. Commit with reference
git add docs/adr/adr-0042-use-postgresql.md
git commit -m "docs: ADR-0042 use postgresql for persistence

Implements #42"
```

### Example 2: This RFC

This RFC itself demonstrates the pattern:
- GitHub Issue: [#31](https://github.com/elevanaltd/HestAI-MCP/issues/31)
- Document: `rfcs/active/0031-github-issue-based-numbering.md`

### Example 3: Referencing in Code

```python
# See ADR-0042 for rationale (https://github.com/org/repo/issues/42)
DATABASE_URL = os.getenv("DATABASE_URL")
```

## Drawbacks

### Non-Sequential Numbers

ADRs may have gaps: ADR-0015, ADR-0023, ADR-0031.

**Mitigation**: This is actually a feature. The gaps tell a story - issues #16-22 were bugs, features, or discussions that didn't become formal documents. The number connects to the broader project history.

### Network Dependency

Creating a document requires network access to create the issue first.

**Mitigation**: We're always online when doing development work (using Claude, Codex, GitHub, etc.). This is already a constraint in the system.

### Issue Noise

Document-related issues appear alongside bugs and features.

**Mitigation**: Use labels (`adr`, `rfc`) and GitHub Projects to filter and organize.

## Alternatives

### Alternative 1: Git Tag-Based Allocation (Atomic Claims)

Use `git push` as atomic Compare-and-Swap to claim numbers via tags.

```bash
git push origin HEAD:refs/tags/claim/adr-0005
# Success = you own it, Failure = retry with 0006
```

**Rejected because**: More complex, requires cleanup workflow, doesn't provide discussion thread.

### Alternative 2: Timestamp-Based Identity

Use `adr-20251224-topic.md` instead of sequential numbers.

**Rejected because**: Loses human-readable sequence, harder to reference ("ADR from December 24th" vs "ADR-31").

### Alternative 3: Committed Registry File

Track allocations in `.hestai/workflow/sequences/registry.json`.

**Rejected because**: Merge conflicts become the coordination mechanism (ironic), more infrastructure.

### Alternative 4: Status Quo

Continue with manual sequence allocation.

**Rejected because**: Clashes will happen, especially with 13+ worktrees.

## Unresolved Questions

1. **Migration**: Should existing ADRs/RFCs be renumbered to match issues, or grandfathered?
   - **Proposal**: Grandfather existing (0001-0004 ADRs, 0001-0002 RFCs), new docs use issue numbers

2. **Cross-repo**: If multiple repos use HestAI, do they share issue namespace?
   - **Proposal**: No, each repo has its own issue numbers, which is fine

3. **Automation**: Should there be a CLI command to create issue + document together?
   - **Proposal**: Nice to have, not required for MVP

## Implementation Plan

### Phase 1: Process Update (This RFC)
- [x] Create RFC using issue-based numbering (demonstrating the pattern)
- [ ] Update RFC README with new process
- [ ] Update naming-standard.oct.md to document pattern

### Phase 2: Template Updates
- [ ] Update `rfcs/0000-template.md` to include GitHub Issue field
- [ ] Create ADR template with same pattern
- [ ] Add labels to GitHub repo (`adr`, `rfc`)

### Phase 3: Documentation
- [ ] Update hub-authoring-rules.oct.md
- [ ] Add examples to System Steward guidance

### Phase 4: Tooling (Optional)
- [ ] CLI helper: `hestai create-adr "Topic"` → creates issue + document
- [ ] CI check: Verify document number matches issue number in frontmatter

## Success Metrics

1. **Zero numbering clashes** in 3 months of multi-worktree development
2. **Adoption rate**: All new ADRs/RFCs use issue-based numbering
3. **Developer satisfaction**: Workflow feels natural, not burdensome

## References

- [ADR-0033: Dual-Layer Context Architecture](../../docs/adr/adr-0033-dual-layer-context-architecture.md)
- [RFC-0002: Hub as Application](./0002-hub-as-application.md)
- [naming-standard.oct.md](../../hub/governance/rules/naming-standard.oct.md)
- Edge Optimizer analysis (Gemini via PAL clink, 2025-12-24)
