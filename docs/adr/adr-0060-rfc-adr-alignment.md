# ADR-0060: RFC/ADR Alignment - Issues as Drafts, ADRs as Law

- **Status**: Accepted
- **Type**: ADR
- **Author**: holistic-orchestrator (synthesized from debate-hall session)
- **Created**: 2025-12-27
- **Updated**: 2025-12-27
- **GitHub Issue**: [#60](https://github.com/elevanaltd/HestAI-MCP/issues/60)
- **Phase**: D1
- **Supersedes**: (none)
- **Superseded-By**: (none)
- **From-RFC**: Issue #60 (Agoral Forge debate)

## Context

The RFC/ADR workflow had structural problems:

1. **Location Inconsistency**: ADRs in `docs/adr/`, RFCs in root `rfcs/`
2. **Stale Draft Graveyard**: `rfcs/` folder accumulated unmerged proposals
3. **Hidden Ideation Logic**: PRs hide reasoning; Issues/Discussions broadcast intent
4. **Git Overhead for Rough Drafts**: Committing exploration is cognitive friction
5. **Lifecycle Confusion**: RFCs and ADRs treated as separate categories instead of lifecycle stages

The current structure treats "proposal" and "decision" as distinct when they're actually lifecycle stages of the same intellectual artifact.

## Decision

### Core Principle

> **"The Discussion IS the Draft. The Synthesis IS the Law."**

### Policy

1. **GitHub Issues are for drafts/debates**
   - All proposals, RFCs, and debates happen in GitHub Issues
   - Mutable, conversational, AI-assisted
   - Label `rfc` for formal proposals requiring deliberation

2. **ADRs are for ratified decisions only**
   - Created only when a decision is accepted
   - Immutable once merged (status changes allowed: Accepted → Implemented → Superseded)
   - Must link to source Issue for provenance

3. **The `rfcs/` folder has been deleted**
   - No new RFC files created
   - Existing RFCs migrated to Issues or ADRs
   - Folder deleted 2025-12-27 (Issue #63)

4. **ADR creation requirements**
   - Every ADR must have a linked GitHub Issue
   - ADR number matches Issue number (ADR-0060 ↔ Issue #60)
   - No ADR without prior deliberation in Issue

### File Retention Policy

| Format | Git Status | Rationale |
|--------|------------|-----------|
| `.json` / `.jsonl` (raw) | GITIGNORED | Machine format, large, reconstructible |
| `.oct.md` (compressed) | COMMITTED | Semantic density, human-readable, audit trail |

This applies to:
- Session archives: `.jsonl` gitignored, `.oct.md` committed
- Debate transcripts: `.json` gitignored, `.oct.md` committed

## Consequences

### Positive

- **Single source of truth**: Issues are the canonical draft location
- **Reduced file churn**: No more committing rough exploration
- **Clear lifecycle**: Draft (Issue) → Ratified (ADR)
- **Better discoverability**: GitHub Issues have search, labels, assignees
- **AI-friendly**: Agents can participate in Issue discussions

### Negative

- **Platform dependency**: Ties governance to GitHub Issues availability
- **Migration effort**: Existing RFCs need import to Issues
- **Offline access**: Issues require network (mitigated by ADR snapshots)

### Neutral

- GitHub Discussions remain optional for announcements/Q&A
- ADR template unchanged (just stricter creation criteria)

## Related Documents

- **GitHub Issue**: [#60 - RFC: Agoral Forge](https://github.com/elevanaltd/HestAI-MCP/issues/60)
- **GitHub Issue**: [#63 - Bootstrap Resolution](https://github.com/elevanaltd/HestAI-MCP/issues/63)
- **ADR**: [ADR-0033 - Dual-Layer Context Architecture](./adr-0033-dual-layer-context-architecture.md)
- **Debate**: `debates/adr-rfc-alignment-v2-2025-12-26.json` (Wind/Wall/Door session)

## Implementation Notes

The following automation tools are **out of scope** for this ADR and belong to debate-hall-mcp's roadmap:

- `github_sync_debate` - Post debate turns to GitHub
- `ratify_rfc` - Auto-generate ADR from synthesis
- `human_interject` - Inject human feedback into debates

These are implementation details, not policy decisions. See debate-hall-mcp Issue tracker for progress.

---

🤖 Generated with [Claude Code](https://claude.ai/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
