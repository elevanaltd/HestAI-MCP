# ADR-003: Living Artifacts Auto-Refresh Mechanism

**Status:** APPROVED (Revised)
**Date:** 2025-12-17
**Revised:** 2025-12-17 (architectural simplification)
**Decision Makers:** holistic-orchestrator (HO session 943ae976)
**Consulted:** critical-engineer (Codex), edge-optimizer (Gemini)

## Context

On 2025-12-17, a major documentation drift was discovered:
- 6+ PRs merged but context files showed them as "pending" or "blocked"
- Test count increased 55→202 with no documentation update
- `BLOCKED::[]` items in `current_state.oct` were all false (work completed)

This violates **I5: Living Artifacts** from the Living Orchestra North Star:
> "awareness_artifacts_reflect_live_state[not_point_in_time_snapshots]"
> "stale_artifacts=confidence_theater[developers_trust_fresh_ignore_stale]"

**Failure Signal:** `map_stale>48hrs→living_artifact_violated`

### Root Cause

No automatic mechanism refreshes context when PRs merge. Context updates depend entirely on manual agent intervention, which drifts immediately under velocity pressure.

### Architectural Constraint

`.hestai/` is a **symlink** to the Anchor worktree (per CV3: `.hestai_is_canonical`):
- Gitignored in main repo (per-clone isolation by design)
- Lives on separate orphan branch (`hestai-state`)
- CI cannot directly update it (different git history)

## Decision

Implement a **split-artifact hybrid** architecture:

### Artifact Split

| Artifact | Location | Updated By | Purpose |
|----------|----------|------------|---------|
| `CHANGELOG.md` | `docs/` (main branch) | CI on merge | Audit trail, always visible in repo |
| `current_state.oct` | `.hestai/snapshots/` | clock_in (generated) | Live state, query-driven |
| `PROJECT-CONTEXT.md` | `.hestai/snapshots/` | Agents | Rich context, local |
| `PROJECT-CHECKLIST.md` | `.hestai/snapshots/` | Agents | Task tracking, local |

### Layer 1: CI-Updated CHANGELOG (Enforced)

**Purpose:** Persistent, visible audit trail in main branch.

```yaml
# .github/workflows/changelog-update.yml
name: Update CHANGELOG on merge
on:
  push:
    branches: [main, master]
```

**Behavior:**
1. Triggered on push to main/master
2. Appends PR summary to `docs/CHANGELOG.md`
3. Commits to same branch (no orphan branch complexity)
4. Deterministic, auditable, injection-safe

**Entry Format:**
```markdown
## [PR #XX] Title (YYYY-MM-DD)
- SHA: abc123
- Author: @username
- Files changed: N
```

### Layer 2: Query-Driven State (Generated)

**Purpose:** Fresh state on every session start.

**Behavior:**
- `clock_in` generates `current_state.oct` by querying:
  - `git log --oneline -10` (recent commits)
  - `docs/CHANGELOG.md` (recent PRs)
  - `pytest --co -q | wc -l` (test count)
  - File modification timestamps
- **Staleness impossible** - state is generated on demand
- Rich context files remain in `.hestai/` for agent use

### Layer 3: Local Staleness Warning (Advisory)

**Purpose:** Developer feedback on context currency.

**Behavior:**
- Pre-commit hook checks `current_state.oct` timestamp
- Warns (doesn't block) if >24h since last update
- Encourages context refresh before significant work

## Why This Architecture

### Problem with Original Design (CI → Orphan Branch)

The original ADR-003 proposed CI updating `.hestai/snapshots/` via the `hestai-state` orphan branch. Issues:

1. **CI can't see `.hestai/`** - symlink is gitignored, not in checkout
2. **Cross-branch complexity** - CI would need to checkout orphan branch, push separately
3. **Concurrency hazards** - merge storms cause non-fast-forward errors

### Solution: Split by Visibility

- **CHANGELOG in main** - always visible, CI can update same branch
- **Context in .hestai/** - rich, local, generated fresh by clock_in
- **No orphan branch writes from CI** - eliminates complexity

## Constraints & Validation

### From Critical-Engineer Assessment (Still Applicable)

| Constraint | Implementation |
|-----------|----------------|
| **Injection Hygiene** | Only structured fields (PR#, SHA, date), no PR body text |
| **Audit Trail** | CHANGELOG commit includes PR reference + CI run ID |
| **Determinism** | CHANGELOG format is fixed template, no AI |
| **Schema Validation** | clock_in validates generated state structure |

### From Edge-Optimizer Analysis (Incorporated)

| Insight | Incorporation |
|---------|---------------|
| **Query-Driven State** | clock_in generates fresh state on demand |
| **No Orphan Branch Writes** | CHANGELOG stays in main, eliminates concurrency issues |
| **Semantic Drift** | CHANGELOG captures PR facts; semantic context remains agent responsibility |

## Alternatives Considered

### A: CI Updates Orphan Branch (Original Design)
- **Pro:** Single source of truth in git
- **Con:** CI can't see `.hestai/`, cross-branch complexity, concurrency hazards
- **Verdict:** REJECTED - conflicts with Anchor architecture

### B: Everything in Main Branch
- **Pro:** Simplest, all visible
- **Con:** Violates CV3 (`.hestai` is canonical for context)
- **Verdict:** REJECTED - breaks per-clone isolation

### C: Split Artifacts (SELECTED)
- **Pro:** CHANGELOG visible + context isolated + no orphan branch CI writes
- **Con:** Two locations to understand
- **Verdict:** APPROVED - respects Anchor architecture while solving visibility

### D: Pure Query-Driven (No Persistent Artifacts)
- **Pro:** Nothing can go stale
- **Con:** No audit trail, no grep-able history
- **Verdict:** REJECTED - need persistent changelog for audit

## Consequences

### Positive
- CHANGELOG always visible in main branch (can't be missed)
- No CI complexity with orphan branches
- Context freshness guaranteed by query-driven generation
- Audit trail maintained for all merges
- Respects Anchor architecture (CV3)

### Negative
- Two artifact locations (docs/ and .hestai/)
- clock_in must implement state generation logic
- CHANGELOG grows unbounded (consider rotation later)

### Risks
- **CHANGELOG Bloat:** Mitigate with quarterly archival
- **Query Failures:** clock_in must handle gracefully (git/gh CLI unavailable)
- **Semantic Gap:** CHANGELOG captures facts, not meaning (acceptable)

## Implementation Plan

### Phase 1: CHANGELOG Infrastructure (Priority)
1. Create `docs/CHANGELOG.md` with initial structure
2. Create `.github/workflows/changelog-update.yml`
3. Test on next PR merge

### Phase 2: clock_in State Generation (Enhancement)
1. Add query logic to clock_in
2. Generate `current_state.oct` from git/changelog/tests
3. Add staleness warning for existing state files

### Phase 3: Local Hook (Optional)
1. Create pre-commit staleness check
2. Advisory only (warns, doesn't block)

## Specialist Consultations

### Critical-Engineer (Codex) - CONDITIONAL GO
> "CI workflow updates `hestai-state` on merge; concurrency lock; schema validation;
> safe-diff allowlist; staleness gate + alert/issue; audit-ready commit metadata"
>
> "NO-GO for AI-driven auto-merge until you have: formal schema, golden fixtures,
> idempotence tests, rollback procedure, injection-safe input rules"

**Note:** CE's concerns about orphan branch concurrency led to the architectural revision.

### Edge-Optimizer (Gemini)
> "Move verification to local hooks (simplification) and guard against orphan branch
> concurrency (edge case). Explore compilable context (opportunity) to prevent semantic rot."

**Note:** EO's insight about query-driven state incorporated into Layer 2.

## References

- Living Orchestra North Star: I5 (Living Artifacts), CV3 (Coordination Structure)
- PR #68, #76: clock_out, clock_in implementations
- Incident: 2025-12-17 context drift (6+ PRs undocumented)
- CE consultation: session 486c4987
- EO consultation: session 8fa65d02

---

*ADR-003 created by holistic-orchestrator session 943ae976*
*Revised 2025-12-17: Architectural simplification (split-artifact hybrid)*
