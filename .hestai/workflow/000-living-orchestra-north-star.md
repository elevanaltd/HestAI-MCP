# LIVING ORCHESTRA - NORTH STAR

**Project**: Living Orchestra System
**Purpose**: Structural enforcement of orchestral awareness in AI-assisted development
**Phase**: D1 (Understanding Establishment)
**Status**: ✅ APPROVED — 2025-12-12
**Approved By**: Shaun Buswell (System Architect)

---

## COMMITMENT STATEMENT

This North Star document establishes the immutable requirements for Living Orchestra — a system that structurally enforces coordinated, context-aware work in HestAI projects.

**Authority**: All work on Living Orchestra (B0-B5 phases) must align with these requirements. Any detected misalignment triggers immediate escalation to requirements-steward.

**Amendment Process**: Changes to immutables require formal review and re-approval. This is not a living document — it is a binding commitment.

---

## PROTECTION CLAUSE

If ANY agent detects misalignment between work and this North Star:

1. **STOP** current work immediately
2. **CITE** the specific North Star requirement being violated
3. **ESCALATE** to requirements-steward for resolution

**Resolution Options**:
- CONFORM work to North Star requirements
- USER AMENDS North Star (rare, requires formal process)
- ABANDON incompatible implementation path

---

## SECTION 1: IDENTITY

### What Living Orchestra IS

Living Orchestra is **structural governance for systemic awareness**.

It is:
- **A coordination substrate** that makes system context ambient, not hunted
- **An enforcement layer** that prevents uncoordinated work by default
- **A living map** that exposes system boundaries, relationships, and active state
- **A workflow discipline** that makes correct process the easiest process

**Core Metaphor**: An orchestra where every musician knows the score, their part, and what everyone else is playing — and a conductor that enforces rehearsal discipline but never plays an instrument.

---

### What Living Orchestra IS NOT

Living Orchestra is NOT:
- ❌ A code quality system (does not prevent "bad code," prevents "uncoordinated work")
- ❌ A complete replacement for Crystal (extends/governs it, doesn't eliminate it)
- ❌ A guarantee of perfect outcomes (guarantees coherent process, not flawless results)
- ❌ A substitute for human judgment (elevates review to fewer, higher-quality checkpoints)
- ❌ A general-purpose project management tool (HestAI-specific, monorepo-optimized)

**Boundary Principle**: Living Orchestra prevents **systemic blindness** (agents acting without awareness of system-wide effects). It does not attempt to prevent all agent errors or enforce architectural taste.

---

## SECTION 2: THE UNCHANGEABLES (7 IMMUTABLES)

These requirements are **binding for the entire project**. Each has passed the Immutability Oath and is technology-neutral. Violating any of these is grounds for rejecting implementation work.

---

### I1: WORK TRACEABILITY

**Requirement**: Every unit of work must be traceable to a recorded decision or task identifier.

**Technology-Neutral Expression**: Work exists only when linked to an externally recorded work unit (issue, ticket, ADR reference, or formal task). Anonymous work is prohibited.

**Evidence (Oath Passage)**:
- **Q1 (Immutable?)**: YES — User stated "hard gate: no work without linked issue"
- **Q2 (Faster without?)**: NO — User rejected untraceable work as non-negotiable
- **Q3 (True in 3 years?)**: YES — Audit trails remain essential regardless of technology evolution

**Rationale**: Traceability enables retrospective analysis, prevents orphaned work, and supports accountability. Without it, "why does this exist?" becomes unanswerable.

**Validation Plan**:
- ✅ Pre-commit hooks verify work context linkage
- ✅ CI rejects commits without traceable work identifiers
- ✅ Tooling refuses to initialize work without recorded task reference

**Status**: 🟢 Testable through gate enforcement mechanisms

---

### I2: ISOLATED WORK CONTEXTS

**Requirement**: All work must occur in isolated, branch-linked contexts. Direct work on protected branches is prohibited.

**Technology-Neutral Expression**: Work must occur in ephemeral, isolated environments that are atomically mergeable and independently discardable. Shared/protected integration branches must be append-only through merge operations.

**Evidence (Oath Passage)**:
- **Q1 (Immutable?)**: YES — User stated worktree gate is "non-negotiable"
- **Q2 (Faster without?)**: NO — User identified bypass as "highest-risk failure mode"
- **Q3 (True in 3 years?)**: YES — Isolation principle survives implementation changes (worktrees → future mechanism)

**Rationale**: Isolation prevents concurrent work interference, enables safe experimentation, and maintains protected branch integrity. Bypass leads to "branching graveyard" and incoherent history.

**Validation Plan**:
- ✅ Tooling refuses operations outside isolated contexts
- ✅ Pre-commit hooks verify isolation context validity
- ✅ Main branch protection enforced at infrastructure level

**Status**: 🟢 Testable through context detection and gate enforcement

---

### I3: STRUCTURAL ENFORCEMENT

**Requirement**: Compliance with workflow and awareness requirements must be structurally enforced, not requested or advised.

**Technology-Neutral Expression**: Required behaviors must be impossible to bypass accidentally. Violations must produce hard failures, not warnings. Advisory systems are insufficient.

**Evidence (Oath Passage)**:
- **Q1 (Immutable?)**: YES — User stated "enforcement, not advice"
- **Q2 (Faster without?)**: NO — User explicitly rejected advisory approaches
- **Q3 (True in 3 years?)**: YES — Advisory systems decay; enforcement does not

**Rationale**: Warnings are ignored under pressure. Gates force compliance even when agents (or humans) are rushing or confused. "Easy to do wrong" systems fail.

**Validation Plan**:
- ✅ All gates must BLOCK operations, not warn
- ✅ Bypass attempts must produce failures with actionable error messages
- ✅ No workflow step can be "skipped with flag"

**Status**: 🟢 Testable through gate bypass attempts (should fail)

---

### I4: SYSTEM BOUNDARY AWARENESS

**Requirement**: Agents must prove awareness of system boundaries and ripple effects before executing changes.

**Technology-Neutral Expression**: Changes must be accompanied by evidence of impact analysis covering affected modules, services, workflows, and invariants. "I don't know what else this affects" is not acceptable.

**Evidence (Oath Passage)**:
- **Q1 (Immutable?)**: YES — Core of "orchestral awareness" vision
- **Q2 (Faster without?)**: NO — "Locally correct, globally wrong" is the problem being solved
- **Q3 (True in 3 years?)**: YES — System complexity only increases; awareness remains essential

**Rationale**: Isolated reasoning produces silent breakage. Agents must surface likely ripple effects even if perfect prediction is impossible. Goal is "no blind spots by default," not omniscience.

**Validation Plan**:
- ✅ Pre-change: Agent must produce or reference a ripple surface (affected areas)
- ✅ Tests must validate known effects
- ✅ Orchestra map must expose likely unknown effects for human review

**Status**: 🟡 Requires Living Orchestra map implementation to test fully

---

### I5: LIVING ARTIFACTS

**Requirement**: System awareness artifacts (maps, dependency graphs, state views) must reflect live system state, not point-in-time snapshots.

**Technology-Neutral Expression**: Awareness tools must derive state from current system reality, not cached/stale representations. Staleness renders artifacts untrustworthy and ignored.

**Evidence (Oath Passage)**:
- **Q1 (Immutable?)**: YES — User stated stale map = "confidence theater v2"
- **Q2 (Faster without?)**: NO — Static artifacts become "docs no one reads"
- **Q3 (True in 3 years?)**: YES — Staleness problem does not age out

**Rationale**: Developers trust fresh data, ignore stale data. A 2-week-old dependency graph is worse than no graph (false confidence). Living artifacts prevent regression to grep-driven development.

**Validation Plan**:
- ✅ Artifacts must include "last updated" timestamps
- ✅ Staleness >24 hours triggers rebuild or warnings
- ✅ Agents query live state, not cached snapshots

**Status**: 🟢 Testable through timestamp verification and rebuild triggers

---

### I6: ENFORCEMENT PRIORITY (GATES > AWARENESS)

**Requirement**: Hard gates (worktree + traceability enforcement) take priority over ambient awareness features (orchestra map).

**Technology-Neutral Expression**: Prevention mechanisms must be implemented before detection/visibility mechanisms. If resource constraints force prioritization, blocking bad actions precedes surfacing context.

**Evidence (Oath Passage)**:
- **Q1 (Immutable?)**: YES — Extracted from "What if budget cut 50%" scenario
- **Q2 (Faster without?)**: NO — User stated gates are "highest-risk failure mode" to prevent
- **Q3 (True in 3 years?)**: YES — Prevention > detection is timeless principle

**Rationale**: Gates without awareness is survivable (manual coordination). Awareness without gates allows bypass. Gates provide floor of safety; awareness provides ceiling of efficiency.

**Validation Plan**:
- ✅ B0-B2 phases must deliver functional gates before map features
- ✅ Regression testing must validate gates before acceptance
- ✅ Map failures degrade gracefully; gate failures block work

**Status**: 🟢 Testable through phase sequencing and failure mode analysis

---

### I7: PROTECTED MAIN BRANCH

**Requirement**: The main integration branch must be append-only (changes only through merge operations). Direct work on main is prohibited.

**Technology-Neutral Expression**: Protected branches receive changes only through controlled merge points. Direct commits, force pushes, or in-place modifications are structurally prevented.

**Evidence (Oath Passage)**:
- **Q1 (Immutable?)**: YES — Implicit in worktree gate requirements
- **Q2 (Faster without?)**: NO — User described main branch mutability as "graveyard" risk
- **Q3 (True in 3 years?)**: YES — Protected main = fundamental version control hygiene

**Rationale**: Main branch history must be trustworthy as source of truth. Direct work creates ambiguity about what was reviewed, tested, and approved. Append-only enables safe rollback and clear audit trails.

**Validation Plan**:
- ✅ GitHub branch protection rules enforce merge-only changes
- ✅ Local tooling refuses operations on main
- ✅ Worktree initialization fails if main is checked out

**Status**: 🟢 Testable through Git configuration and tooling checks

---

## SECTION 3: CONSTRAINED VARIABLES

These areas have **immutable boundaries** and **flexible ranges**. Implementation must respect the immutable aspects while allowing variance within defined limits.

---

### CV1: WORKFLOW FRICTION

**Immutable Boundary**: Compliance overhead must not make correct workflow slower than manual workarounds.

**Flexible Range**:
- Acceptable: 10-30 seconds overhead per work unit initialization
- Acceptable: Sub-second latency for map lookups during work
- Negotiable: Exact performance targets (will emerge from usage)

**Rationale**: Humans optimize for path of least resistance. If gates add 5 minutes per task, developers will find bypasses. "Easiest workflow = correct workflow" requires speed parity.

**Current Status**: No quantitative thresholds set; qualitative requirement only

---

### CV2: CRYSTAL INTEGRATION

**Immutable Boundary**: Living Orchestra must extend/govern Crystal's worktree model, not replace it outright.

**Flexible Range**:
- Crystal remains worktree isolation mechanism (currently)
- Living Orchestra adds governance hooks and awareness layers
- Exact coupling level (tight integration vs. loose wrapper) is open

**Negotiable**: Whether Crystal is eventually absorbed into Living Orchestra or remains separate tool

**Current Status**: Integration strategy deferred to D2/D3 phases

---

### CV3: COORDINATION STRUCTURE

**Immutable Boundary**: Living Orchestra artifacts must live in a discoverable, standardized location.

**Flexible Range**:
- `.hestai/` is the standard (RESOLVED 2025-12-12)
- Exact directory structure (open)
- Artifact naming conventions (open)

**Negotiable**: Structure details within `.hestai/`

**Current Status**: ✅ RESOLVED — `.hestai/` is the canonical coordination structure

---

### CV4: TECHNOLOGY SUBSTRATE

**Immutable Boundary**: Git remains the coordination substrate; GitHub remains task tracker (currently).

**Flexible Range**:
- Specific Git commands/tooling (worktrees vs. future mechanisms)
- GitHub Issues vs. Linear/Jira (interface abstraction possible)
- MCP vs. other agent tool protocols

**Negotiable**: Implementations, not principles

**Current Status**: Current technology is assumed stable but not guaranteed immutable

---

## SECTION 4: ASSUMPTION REGISTER

These assumptions underpin the North Star. Each has a validation plan and owner. **Critical/High impact assumptions must be validated before B0 gate.**

---

| ID | Assumption | Source | Risk if False | Validation Plan | Owner | Confidence | Impact |
|----|-----------|--------|---------------|-----------------|-------|-----------|--------|
| A1 | Git worktrees remain viable isolation mechanism | Current HestAI infrastructure | Must redesign isolation layer | Test at scale during B1 | System Architect | 85% | High |
| A2 | GitHub Issues remain task tracker | Current workflow | Must abstract work-unit interface | Monitor GitHub roadmap | System Architect | 70% | Medium |
| A3 | Agents have reliable MCP tool access | HestAI tooling | Gates cannot enforce | Test during B0 prototyping | System Architect | 90% | Critical |
| A4 | Monorepo structure remains stable | eav-monorepo architecture | Orchestra map scope changes | Review during D2 architecture | System Architect | 80% | Medium |
| A5 | Single-developer operation remains valid | Current team size | Concurrency/locking not designed for multi-dev | Document as known limitation | System Architect | 60% | Low |
| A6 | Crystal worktree model is sound | Existing Crystal implementation | Integration target is flawed | Audit Crystal during D2 | System Architect | 75% | High |
| A7 | `.coord/` or `.hestai/` location is universally writable | File system permissions | Artifacts cannot be persisted | Test during B0 | System Architect | 95% | Critical |
| A8 | Orchestra map can be built from static analysis + live queries | Technical feasibility | Core feature undeliverable | Proof-of-concept during B0 | System Architect | 65% | Critical |
| A9 | Agents will consult map if provided | Agent behavior | Map built but ignored (confidence theater) | Observability during B2 usage | System Architect | 70% | High |
| A10 | Ripple surface analysis is computationally feasible | Performance assumption | Map lookups too slow, adoption fails | Benchmark during B1 | System Architect | 75% | Medium |

---

### CRITICAL ASSUMPTIONS (Must validate before B0)

- **A3**: MCP tool access reliability → **BLOCKING**
- **A7**: Artifact persistence location → **BLOCKING**
- **A8**: Orchestra map technical feasibility → **BLOCKING**

All critical assumptions require proof-of-concept validation during B0 phase. Failure of any critical assumption requires North Star amendment or project pivot.

---

## SECTION 5: SUCCESS CRITERIA

### Qualitative Signals (Living Orchestra is Working)

✅ **Fewer "how did this happen?" moments**
→ Retroactive investigations decrease because work is traceable and context-aware

✅ **Fewer emergency context rebuilds**
→ Agents operate with ambient awareness, reducing "where am I?" moments

✅ **Less manual policing of branches/worktrees**
→ Gates enforce correct workflow; human review focuses on logic, not process

✅ **More confidence delegating work to agents**
→ "Orchestral awareness" prevents silent breakage, enabling higher trust

✅ **Increased reuse of existing decisions/invariants**
→ Agents consult ADRs, design docs, and system constraints during work

---

### Quantitative Signals (Measurable Improvements)

**Reduction targets** (baseline = pre-Living Orchestra):
- Work on wrong branch/worktree: **→ near-zero** (gate enforcement)
- Uncommitted work accumulation >24hrs: **→ <10%** (checkpoint nudges)
- Post-merge surprises (undetected conflicts): **→ 50% reduction** (ripple surface awareness)

**Increase targets**:
- Documentation referenced during work: **→ 3x baseline** (map-driven discovery)
- Reuse of existing patterns/decisions: **→ 2x baseline** (ADR/invariant surfacing)

**Operational Thresholds** (TBD, will emerge from B2+ usage):
- Acceptable dirty-state duration: OPEN
- Map update frequency: OPEN
- Documentation consumption rate: OPEN

---

### Failure Signals (Living Orchestra is NOT Working)

🚨 **Gates are bypassed regularly**
→ Structural enforcement has failed; agents or humans finding workarounds

🚨 **Orchestra map is stale >48 hours**
→ Living artifact requirement violated; regression to static docs

🚨 **Agents ignore map during work**
→ Awareness features not integrated into workflow; confidence theater

🚨 **Workflow friction causes manual bypasses**
→ Compliance overhead exceeded adoption threshold; process rejection

🚨 **Main branch receives direct commits**
→ Protected branch discipline broken; version control hygiene failure

---

## SECTION 6: EVIDENCE SUMMARY

**Immutability Engineering**:
- Total Immutables: **7** (within Miller's Law 7±2 range ✅)
- Pressure Tested: **7/7** passed Immutability Oath ✅
- System-Agnostic: **7/7** passed Technology Change Test ✅

**Assumption Audit**:
- Total Assumptions: **10** (exceeds 6+ minimum requirement ✅)
- Critical Assumptions: **3** (A3, A7, A8 require pre-B0 validation)
- Validation Owners: **All assigned** (System Architect) ✅

**Commitment Ceremony**:
- Completed: **YES** ✅
- Approved: **2025-12-12** ✅
- Approved By: **Shaun Buswell (System Architect)** ✅

---

## SECTION 7: COMMITMENT CEREMONY RECORD

**Date**: 2025-12-12
**Approver**: Shaun Buswell (System Architect)
**Status**: ✅ APPROVED

**Ceremony Transcript**:

> These are your North Star. The 7 immutable requirements represent the binding commitments for Living Orchestra. Once approved, these requirements gain authority to BLOCK work that violates them.
>
> Future-you may want to change these under pressure. Present-you is making a commitment to future-you: these are the principles worth defending, even when inconvenient.
>
> If you approve, all Living Orchestra work (B0-B5) must conform to these requirements. Misalignment triggers immediate escalation to requirements-steward.

**User Approval**: ✅ CONFIRMED

**Binding Authority**: This North Star is now the authoritative requirements document for Living Orchestra. All agents must reference and comply with these immutables throughout implementation.

---

## APPENDIX A: TECHNOLOGY CHANGE TEST RESULTS

Each immutable was tested: "If implemented with Technology A vs. Technology B, does the requirement still hold?"

| Immutable | Tech A | Tech B | Result |
|-----------|--------|--------|--------|
| I1: Work Traceability | GitHub Issues | Linear/Jira | ✅ Both satisfy (recorded work unit) |
| I2: Isolated Contexts | Git worktrees | Separate clones | ✅ Both satisfy (isolation principle) |
| I3: Structural Enforcement | Pre-commit hooks | CI gates | ✅ Both satisfy (blocking mechanism) |
| I4: Boundary Awareness | Static analysis | Runtime tracing | ✅ Both satisfy (impact visibility) |
| I5: Living Artifacts | Query-driven | Event-sourced | ✅ Both satisfy (live state) |
| I6: Enforcement Priority | N/A (sequencing) | N/A | ✅ Technology-independent |
| I7: Protected Main | GitHub branch protection | GitLab/Bitbucket | ✅ Both satisfy (append-only) |

All immutables are **technology-neutral** ✅

---

## APPENDIX B: CONVERSATION CITATIONS

**I1 (Work Traceability)**: User stated "Hard gate: no work without: a valid worktree, a linked issue. Agent tooling refuses to operate if: on main branch, in wrong directory, detached from issue context. This is enforcement, not advice."

**I2 (Isolated Contexts)**: User stated "What prevents starting work in wrong context: Hard gate... Agent tooling refuses to operate if on main branch... If agents bypass worktree gates: Main branch becomes mutable, branch ancestry becomes incoherent... This is one of the highest-risk failure modes."

**I3 (Structural Enforcement)**: User stated "Orchestral awareness means: System context is ambient, not hunted. Correct workflow is the easiest workflow. Global coherence is enforced structurally, not by vigilance."

**I4 (Boundary Awareness)**: User stated "Questions it asks itself: What part of the system am I in? What other parts connect to this? What assumptions or invariants exist here? What else might this affect downstream? Must produce or reference a ripple surface: affected modules/services, affected workflows, affected invariants or ADRs."

**I5 (Living Artifacts)**: User stated "If orchestra map becomes stale/ignored: Turns into confidence theater artifact, 'docs no one reads' v2. Agents resume grep-driven development, cargo-cult fixes. System regresses to pre-orchestral behavior."

**I6 (Enforcement Priority)**: User prioritized "Hard gate: no work without worktree + issue" and identified gate bypass as "highest-risk failure mode" above map staleness.

**I7 (Protected Main)**: User stated "If agents bypass worktree gates: Main branch becomes mutable... Worktrees fork from inconsistent states... Git degenerating into a branching graveyard instead of a coordination tool."

---

## DOCUMENT CONTROL

**Version**: 1.0
**Created**: 2025-12-12
**Author**: north-star-architect (Claude Sonnet 4.5)
**Phase**: D1_03 (Understanding Establishment)
**Next Gate**: D1_04 validation by requirements-steward
**Location**: `/Volumes/HestAI/.hestai/workflow/000-LIVING-ORCHESTRA-D1-NORTH-STAR.md`

**Validation Status**:
- ✅ Constitutional validation prompts applied
- ✅ 7 immutables with Oath passage evidence
- ✅ All immutables system-agnostic (Technology Change Test passed)
- ✅ 10 assumptions with risk assessment + validation plans
- ✅ Commitment Ceremony completed with timestamp
- ⏳ Awaiting requirements-steward validation (D1_04)
- ⏳ Awaiting critical-engineer reality validation (post-D1_04)

---

**END OF NORTH STAR**
