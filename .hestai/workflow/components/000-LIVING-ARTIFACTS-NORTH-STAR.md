# COMPONENT NORTH STAR: LIVING ARTIFACTS

**Component**: Living Artifacts (Context Freshness Engine)
**Parent**: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
**Status**: ACTIVE
**Version**: 1.0

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **Living Artifacts** component.
It inherits all requirements from the **System North Star** and **HestAI-MCP Product North Star**.
Any deviation requires formal amendment.

---

## SECTION 1: THE UNCHANGEABLES (5 Immutables)

### I1: SPLIT-ARTIFACT AUTHORITY
**Requirement**: A strict separation exists between **Audit Trail** (Immutable History, e.g., CHANGELOG) and **Operational State** (Current Snapshot, e.g., `current_state.oct`).
**Rationale**: "What happened" (Log) and "Where are we" (State) have different distinct update cycles and truth sources.
**Validation**: Distinct files for log vs. state.

### I2: QUERY-DRIVEN FRESHNESS
**Requirement**: Operational state is generated at runtime (JIT) by querying the environment, not by reading a potentially stale file.
**Rationale**: Stored state rots. Generated state is always true to the environment.
**Validation**: `clock_in` executes generation logic (git query, test count) rather than just reading.

### I3: SINGLE-BRANCH CI WRITES
**Requirement**: CI processes must ONLY write to the branch they are running on. Cross-branch writes (e.g., to an orphan `state` branch) are prohibited.
**Rationale**: Cross-branch writes introduce race conditions and merge conflicts that break automation.
**Validation**: CI workflows use `git push origin HEAD` (or equivalent current-branch logic).

### I4: BLOCKING STALENESS
**Requirement**: Usage of context artifacts detected as stale (older than threshold or matching "stale" hash) must be blocked or explicitly flagged as "AT_RISK".
**Rationale**: Inherited from Product I4. Bad data is worse than no data.
**Validation**: Pre-commit hooks or tool guards check timestamps/hashes.

### I5: PERSISTENT AUDIT TRACE
**Requirement**: Every significant change (Merge, Release) must leave a permanent, human-readable trace in the Audit Trail artifact.
**Rationale**: Automated state generation is ephemeral; we need a permanent history of evolution.
**Validation**: CI appends to `CHANGELOG.md` on every merge.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **State Source** | Environment Query (I2) | Specific queries run |
| **Audit Location** | In-repo file (I5) | File name/path |
| **Staleness Threshold** | Must exist (I4) | Duration (e.g., 24h vs 12h) |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Validation Plan |
|----|------------|-----------------|
| C-A1 | Runtime generation is fast enough (<5s) | Performance benchmarking |
| C-A2 | CHANGELOG merge conflicts are manageable | Monitor CI failure rates |
| C-A3 | Git logs provide sufficient state data | Verify against rich metadata needs |

---
