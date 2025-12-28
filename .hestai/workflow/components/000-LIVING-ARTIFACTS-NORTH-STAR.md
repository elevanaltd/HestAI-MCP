---
component: living_artifacts
scope: pattern
phase: D1
created: 2025-12-27
status: approved
approved_by: requirements-steward
approved_date: 2025-12-28
parent_north_star: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
version: 1.2
---

# COMPONENT NORTH STAR: LIVING ARTIFACTS

**Component**: Living Artifacts (Context Freshness Engine)
**Parent**: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
**Status**: ACTIVE
**Version**: 1.2
**Date**: 2025-12-28
**Reviewed By**: requirements-steward
**Review Date**: 2025-12-28

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **Living Artifacts** component.

**Inheritance Chain**:
- **System North Star**: `hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md` (Constitutional Authority)
- **Product North Star**: `.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md` (Product Immutables I1-I6)
- **This Component**: Living Artifacts (Pattern-Level Requirements LA-I1 through LA-I5)

**Authority**: All work on Living Artifacts must align with these requirements AND all parent requirements.
Any deviation requires formal amendment through the requirements-steward.

---

## SECTION 1: THE UNCHANGEABLES (5 Immutables)

### LA-I1: SPLIT-ARTIFACT AUTHORITY
**Requirement**: A strict separation exists between **Audit Trail** (Immutable History, e.g., CHANGELOG) and **Operational State** (Current Snapshot, e.g., `current_state.oct`).
**Rationale**: "What happened" (Log) and "Where are we" (State) have different distinct update cycles and truth sources.
**Validation**: Distinct files for log vs. state.

### LA-I2: QUERY-DRIVEN FRESHNESS
**Requirement**: Operational state is generated at runtime (JIT) by querying the environment, not by reading a potentially stale file.
**Rationale**: Stored state rots. Generated state is always true to the environment.
**Validation**: `clock_in` executes generation logic (git query, test count) rather than just reading.

### LA-I3: SINGLE-BRANCH CI WRITES
**Requirement**: CI processes must ONLY write to the branch they are running on. Cross-branch writes (e.g., to an orphan `state` branch) are prohibited.
**Rationale**: Cross-branch writes introduce race conditions and merge conflicts that break automation.
**Validation**: CI workflows use `git push origin HEAD` (or equivalent current-branch logic).

### LA-I4: BLOCKING STALENESS
**Requirement**: Usage of context artifacts detected as stale (older than threshold or matching "stale" hash) must be blocked or explicitly flagged as "AT_RISK".
**Rationale**: Inherited from Product I4 (FRESHNESS VERIFICATION). Bad data is worse than no data.
**Validation**: Pre-commit hooks or tool guards check timestamps/hashes.

### LA-I5: PERSISTENT AUDIT TRACE
**Requirement**: Every significant change (Merge, Release) must leave a permanent, human-readable trace in the Audit Trail artifact.
**Rationale**: Automated state generation is ephemeral; we need a permanent history of evolution.
**Validation**: CI appends to `CHANGELOG.md` on every merge.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **State Source** | Environment Query (LA-I2) | Specific queries run |
| **Audit Location** | In-repo file (LA-I5) | File name/path |
| **Staleness Threshold** | Must exist (LA-I4) | Duration (e.g., 24h vs 12h) |

---

## SECTION 2B: SCOPE BOUNDARIES

### What This Component IS

| Scope | Description |
|-------|-------------|
| Audit Trail Maintenance | CHANGELOG updates on merges and releases |
| Operational State Generation | JIT creation of current_state.oct via environment queries |
| Query-Driven Freshness | Runtime generation rather than cached file reads |
| Staleness Detection and Blocking | Pre-commit hooks and tool guards for stale artifacts |
| CI Integration | Automated CHANGELOG entries on merge events |

### What This Component IS NOT

| Out of Scope | Responsible Component |
|--------------|----------------------|
| Context File Writing | OCTAVE MCP (octave_create) |
| Session Management | clock_in / clock_out tools |
| Identity Validation | odyssean_anchor tool |
| Manual Documentation Authoring | Human activity (not automated) |
| Schema Enforcement | OCTAVE MCP (octave_ingest) |
| Context Selection | System Steward |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Confidence | Impact | Validation Plan | Owner | Timing |
|----|------------|------------|--------|-----------------|-------|--------|
| LA-A1 | Runtime generation is fast enough (<5s) | 85% | High | Performance benchmarking against target latency | implementation-lead | Before B2 |
| LA-A2 | CHANGELOG format is parseable by humans and automation | 80% | Medium | Review samples with 5+ developers | implementation-lead | During B1 |
| LA-A3 | Git logs provide sufficient state data | 70% | High | Verify against rich metadata needs for 10+ session scenarios | implementation-lead | Before B1 |
| LA-A4 | CHANGELOG merge conflicts don't block CI | 80% | Medium | Monitor CI failure rates over 30 days | implementation-lead | During B2 |
| LA-A5 | 24-hour staleness threshold is appropriate for most workflows | 75% | Medium | Gather user feedback on staleness blocking frequency | implementation-lead | During B2 |
| LA-A6 | Git logs provide sufficient metadata for state reconstruction | 70% | High | Test with 10+ real sessions covering edge cases | implementation-lead | Before B1 |

### CRITICAL ASSUMPTIONS (Must validate before B2)

- **LA-A1 (Performance)**: If generation takes >5s, users will bypass the freshness system.
- **LA-A3/LA-A6 (Git Sufficiency)**: If git logs are insufficient, we need alternative metadata storage.

---

## SECTION 4: COMMITMENT CEREMONY RECORD

**Initial Approval**:
- **Date**: 2025-12-27
- **Approver**: requirements-steward
- **Status**: APPROVED
- **Version**: 1.0

**Current Revision**:
- **Date**: 2025-12-28
- **Approver**: requirements-steward
- **Status**: APPROVED
- **Version**: 1.1

**Ceremony Transcript**:
> **Requirements Steward**: "Do you approve these 5 Immutables (LA-I1 through LA-I5) as the binding Component North Star for Living Artifacts?"
> **User**: "Yes, approve these."
> **Requirements Steward**: "Do you approve the v1.1 refinements including scope boundaries and expanded assumption register?"
> **User**: "Yes, approve these refinements."

**Binding Authority**: This Component North Star inherits authority from the Product North Star and is binding for all Living Artifacts implementation work.

---

## SECTION 5: DECISION LOG

| ID | Date | Decision | Rationale | Made By |
|----|------|----------|-----------|---------|
| LA-D1 | 2025-12-27 | Adopt split-artifact pattern | Separating audit from state prevents coupling and enables independent update cycles | requirements-steward |
| LA-D2 | 2025-12-27 | Mandate query-driven freshness | Static files rot; JIT generation guarantees environmental truth | requirements-steward |
| LA-D3 | 2025-12-27 | Prohibit cross-branch CI writes | Previous orphan-branch approach caused race conditions | requirements-steward |
| LA-D4 | 2025-12-28 | Rename immutables to LA-I* prefix | Consistency with component naming convention | requirements-steward |
| LA-D5 | 2025-12-28 | Add scope boundaries section | Clarify what Living Artifacts owns vs. delegates | requirements-steward |
| LA-D6 | 2025-12-28 | Expand assumption register | More rigorous risk tracking with confidence and timing | requirements-steward |
| LA-D7 | 2025-12-28 | Align with ns-component-create | Standard format compliance | requirements-steward |

---

## EVIDENCE SUMMARY

### Constitutional Compliance
- **Total Immutables**: 5 (within 5-9 range per Miller's Law)
- **System-Agnostic**: 5/5 passed Technology Change Test (no technology-specific language)
- **Assumptions Tracked**: 6 (6+ required per PROPHETIC_VIGILANCE)
- **Critical Assumptions**: 3 requiring pre-B2 validation (LA-A1, LA-A3, LA-A6)
- **Commitment Ceremony**: Completed 2025-12-28

### Quality Gates
- **YAML Front-Matter**: Present
- **Inheritance Chain**: Documented (System NS + Product NS)
- **Miller's Law**: 5 immutables (within 5-9 range)
- **PROPHETIC_VIGILANCE**: 6 assumptions with validation plans
- **Scope Boundaries**: IS/IS NOT documented
- **Evidence Trail**: requirements-steward review documented

### Readiness Status
- **D1 Gate**: PASSED - Ready for implementation
- **Blocking Dependencies**: None (pattern, not tool)

---

## PROTECTION CLAUSE

Any work contradicting these immutables must STOP, CITE the specific requirement, and ESCALATE to requirements-steward.

**The Protection Oath**:
> "These 5 Immutables (LA-I1 through LA-I5) are the binding requirements for Living Artifacts implementation. Any contradiction requires STOP, CITE, ESCALATE."
