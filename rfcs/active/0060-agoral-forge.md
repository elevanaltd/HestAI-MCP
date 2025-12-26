# RFC-0060: Agoral Forge - GitHub Discussions + debate-hall-mcp Integration

- **Status**: Draft
- **Type**: RFC
- **Author**: holistic-orchestrator (synthesized from debate-hall session)
- **Created**: 2025-12-26
- **Updated**: 2025-12-26
- **GitHub Issue**: [#60](https://github.com/elevanaltd/HestAI-MCP/issues/60)
- **Phase**: D1 (Requirements)

## Summary

Transform RFCs from static repository files into GitHub Discussions with structured AI-assisted debate via debate-hall-mcp integration. ADRs remain as immutable artifacts in `docs/adr/`.

**Core Concept**: "The Discussion IS the Draft. The Synthesis IS the Law."

## Motivation

### Current Problems

1. **Location Inconsistency**: ADRs in `docs/adr/`, RFCs in root `rfcs/`
2. **Template Parity Gap**: RFCs have a template, ADRs don't
3. **Status Tracking Burden**: Manual README.md updates duplicate GitHub Issue state
4. **Stale Draft Graveyard**: `rfcs/` folder accumulates unmerged proposals
5. **Hidden Ideation Logic**: PRs hide the reasoning; Discussions broadcast intent
6. **Git Overhead for Rough Drafts**: Committing exploration is cognitive friction

### Why This Matters

The current RFC/ADR split treats "proposal" and "decision" as separate categories when they're actually lifecycle stages of the same intellectual artifact. Files move between folders, links rot, and the journey from idea to law is obscured.

## Detailed Design

### The Agoral Forge Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Discussions                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Discussion: "RFC: Feature X"                         │    │
│  │ Category: RFC                                        │    │
│  │ Labels: debate-requested                             │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ 💨 WIND (PATHOS): "Here's the possibility..."       │    │
│  │ 🧱 WALL (ETHOS): "Here's what constrains..."        │    │
│  │ 🚪 DOOR (LOGOS): "Here's the synthesis..."          │    │
│  │ 👤 Human: "What about edge case Y?"                 │    │
│  │ 🧱 WALL (ETHOS): "Good point, adjusting..."         │    │
│  │ 🚪 DOOR (LOGOS): "Final synthesis..."               │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                     /ratify command                          │
│                           ▼                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    docs/adr/                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ADR-0060: Feature X Decision                         │    │
│  │ Status: Accepted                                     │    │
│  │ From-RFC: Discussion #123                            │    │
│  │ [Immutable artifact with full provenance]            │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### State Machine

```octave
STATE_1::HUMAN_CREATES_DISCUSSION[
  category: "RFC",
  body: "Proposed idea with context"
]

STATE_2::TRIGGER_DEBATE[
  trigger: label("debate-requested") OR slash_command("/debate"),
  action: debate-hall-mcp.init_debate()
]

STATE_3::AGENTS_DESCEND[
  Wind: posts_expansion_comment(cognition: PATHOS),
  Wall: posts_constraint_comment(cognition: ETHOS),
  Door: posts_synthesis_comment(cognition: LOGOS)
]

STATE_4::HUMAN_INTERVENTION[
  mechanism: reply_to_agent_comment,
  effect: injected_into_next_debate_round
]

STATE_5::RATIFICATION[
  trigger: slash_command("/ratify"),
  action: generate_ADR_from_synthesis,
  side_effect: lock_discussion + mark_answered
]
```

### New debate-hall-mcp Tools

#### 1. `github_sync_debate`

```python
def github_sync_debate(thread_id: str, discussion_id: str) -> SyncResult:
    """
    Post debate turns as GitHub Discussion comments.

    - Maps cognition to emoji header (PATHOS=💨, ETHOS=🧱, LOGOS=🚪)
    - Idempotent by turn_index (skips if already posted)
    - Stores mapping: {turn_index: comment_node_id}
    """
```

#### 2. `ratify_rfc`

```python
def ratify_rfc(thread_id: str, discussion_id: str) -> RatifyResult:
    """
    Generate ADR from Door synthesis and finalize Discussion.

    1. Extract final Door synthesis from debate
    2. Format as ADR template with metadata
    3. Create PR to docs/adr/{issue}-{slug}.md
    4. Lock Discussion + mark as answered
    5. Update docs/adr/rfc-index.md
    """
```

#### 3. `human_interject`

```python
def human_interject(discussion_id: str, comment_id: str) -> InjectResult:
    """
    Inject human reply into ongoing debate.

    - Triggered by webhook on human reply to agent comment
    - Classifies as WALL evidence or WIND expansion
    - Next debate round considers human input
    """
```

### GitHub Integration Requirements

| Component | Requirement |
|-----------|-------------|
| **GitHub App** | Scopes: `discussions:write`, `contents:write` |
| **Discussion Category** | "RFC" with pinned template |
| **Labels** | `debate-requested`, `ratified`, `rejected` |
| **Webhook Events** | `discussion`, `discussion_comment` |

### Acceptance Criteria (From Wall)

- **A1**: Trigger spec + idempotent processing (by `discussion_id` + `turn_index`)
- **A2**: Canonicality spec (ADR supersedes; Discussion locked after ratify)
- **A3**: Repo index present (`docs/adr/rfc-index.md`) maintained automatically
- **A4**: Prototype policy (experiments stay in git, linked from Discussion)

## Examples

### Manual Trial (This RFC)

1. **Issue #60 created** as Discussion proxy
2. **Debate turns** posted as Issue comments (simulating Discussion flow)
3. **Human feedback** incorporated via replies
4. **Ratification** creates ADR-0060 when consensus reached

### Automated Flow (Future)

```bash
# Human creates Discussion via GitHub UI
# System detects label "debate-requested"

# debate-hall-mcp initiates
mcp__debate-hall__init_debate(
  thread_id="rfc-0060",
  topic="Should we implement feature X?",
  mode="mediated"
)

# Agents debate via clink
mcp__pal__clink(cli_name="gemini", role="edge-optimizer", ...)  # Wind
mcp__pal__clink(cli_name="codex", role="critical-engineer", ...) # Wall

# Turns sync to Discussion
github_sync_debate(thread_id="rfc-0060", discussion_id="D_kwDON...")

# Human approves
/ratify

# ADR generated, Discussion locked
```

## Drawbacks

1. **Platform Dependency**: Ties governance to GitHub Discussions availability
2. **Webhook Instability**: Discussion webhooks in public preview (schema may change)
3. **Offline Discoverability**: Knowledge leaves the repo (mitigated by index + ADR)
4. **Migration Effort**: Existing RFCs need import/redirect stubs

## Alternatives

### Alternative 1: Lifecycle-as-Metadata (Round 1 Synthesis)

Keep `rfcs/` and `docs/adr/` directories, unify via shared frontmatter schema. Rejected because it doesn't eliminate the file-management overhead or enable human-agent threaded dialogue.

### Alternative 2: Unified Governance Folder

Rename to `governance/records/` with lifecycle field. Rejected because it collides with `hub/governance/` namespace and breaks existing CI.

### Alternative 3: Keep Current Structure

Continue with separate `rfcs/` and `docs/adr/`. Rejected because the problems (stale drafts, hidden ideation, manual tracking) persist.

## Unresolved Questions

1. **Organization-Level RFCs**: GitHub Discussions API is repo-scoped. How do we handle cross-repo governance?
2. **Voting Weight**: Should upvotes on Wind vs Wall comments quantitatively influence Door synthesis?
3. **Debate Resumption**: If a Discussion is edited after initial debate, does it trigger re-debate?
4. **External Agent Role Injection**: How do agents without debate-hall-mcp context adopt roles?

## External Agent Participation

### The Problem

When tagging external AI agents (`@codex`, `@copilot`, `@claude`) in GitHub Discussions, they lack:
- Access to debate-hall-mcp's cognition definitions
- Knowledge of Wind/Wall/Door roles
- OCTAVE format expectations

### Solutions (Phased)

#### Manual Phase (Now)

**Pinned Role Reference**: Add a pinned comment to each RFC Discussion with compact role definitions. Any agent can read this context and adopt a role.

Example invitation:
```
@codex Can you review this as WALL?
Your job: Find constraints, cite evidence, render verdict.
See the pinned role reference above.
```

#### Automated Phase (Phase 1+)

**Bot Intermediary**: The debate-hall-mcp GitHub App handles role injection:
1. Human adds `debate-requested` label
2. Bot invokes agents via clink with role parameter pre-set
3. Bot posts turns with full cognition context
4. External agents don't need prior role knowledge

### Role Reference Template

For manual trials, include this pinned comment in RFC Discussions:

```markdown
## 📌 DEBATE ROLES REFERENCE

### 💨 WIND (PATHOS) - The Explorer
Job: Expand possibility, push boundaries
Format: VISION → EXPLORATION → EMERGENT CAPABILITIES

### 🧱 WALL (ETHOS) - The Guardian
Job: Validate claims, identify constraints
Format: VERDICT → EVIDENCE → CONSTRAINTS → RISKS

### 🚪 DOOR (LOGOS) - The Synthesizer
Job: Integrate Wind + Wall into third-way solution
Format: TENSION RESOLUTION → EMERGENT PATH → IMPLEMENTATION
```

## Implementation Plan

### Phase 0: Foundation (Week 1)
- [ ] Create GitHub App with required scopes
- [ ] Create "RFC" Discussion category with template
- [ ] Define labels (`debate-requested`, `ratified`, `rejected`)

### Phase 1: Core Tools (Weeks 2-3)
- [ ] Implement `github_sync_debate` MCP tool
- [ ] Implement `ratify_rfc` MCP tool
- [ ] Add `docs/adr/rfc-index.md` maintenance

### Phase 2: Automation (Week 4)
- [ ] GitHub Actions workflow for `discussion` events
- [ ] Human intervention detection (reply injection)
- [ ] Webhook reliability (fallback polling)

### Phase 3: Migration (Weeks 5-6)
- [ ] Bulk import existing RFCs to Discussions
- [ ] Create redirect stubs in `rfcs/`
- [ ] Delete `rfcs/` folder after 100% migration

## Origin: debate-hall-mcp Session

This RFC was synthesized from debate thread `adr-rfc-alignment-v2-2025-12-26`:

| Role | Agent | Model | Contribution |
|------|-------|-------|--------------|
| Wind | edge-optimizer | gemini-3-pro-preview | "Agoral Forge" vision, emergent capabilities |
| Wall | critical-engineer | codex | Acceptance criteria A1-A4, migration path |
| Door | synthesizer | claude-opus-4-5 | Implementation synthesis, phased plan |

---

🤖 Generated with [Claude Code](https://claude.ai/claude-code) via debate-hall-mcp

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
