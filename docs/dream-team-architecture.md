# Dream Team Architecture

**Date**: 2026-03-22
**Status**: SPECIFICATION — locked decisions from dream-team-proposal.md
**Scope**: Complete agent ecosystem architecture for solo-developer AI orchestration

This document contains ONLY locked decisions. For exploration history, debate transcripts, and decision reasoning, see `dream-team-proposal.md`.

---

## Part A: The Architecture (What We Know)

### A1: Workflow — 8 Phases, Tiered, Any-Entry

```
D0 ORIENT (ambient — human selects tier + entry)
    ↓
D-SPACE: D1 UNDERSTAND → D2 EXPLORE → D3 ARCHITECT (fluid)
    ↓
B0 VALIDATE (The Rubicon — recursive diagnosis on failure)
    ↓
B-SPACE: B1 PLAN → B2 BUILD (core execution with tiered review)
    ↓
B3 REINTEGRATE (automated memory engine — no human attendance)
    ↺ feeds back to D1 constraints
```

| Phase | Name | Always? | Tiered? | Purpose |
|---|---|---|---|---|
| D0 | ORIENT | Yes (ambient) | No — IS the tier selector | Human as ROUTER_PRIME. Selects tier, entry phase, provides context. |
| D1 | UNDERSTAND | No | T1: formalize known. T2: research. T3: debate. | Explore problem space, formalize requirements. |
| D2 | EXPLORE | No | T1: quick check. T2: debate/research. T3: spikes+risk. | Explore solution space. |
| D3 | ARCHITECT | Yes | T1: organic. T2: documented. T3: formal blueprint. | Think before coding. Hinge between D-Space and B-Space. |
| B0 | VALIDATE | Yes | T1: quick consult. T2: specialist. T3: committee. | The Rubicon. Recursive diagnosis on failure (routes back to D1/D2/D3). |
| B1 | PLAN | Yes | T1: self-plan. T2: checklist. T3: atomic decomposition. | Decompose before coding. |
| B2 | BUILD | Yes | T0-T4 review tiers. | Core phase. IL(RED) → TMG → IL(GREEN) → Tiered Review → Merge. |
| B3 | REINTEGRATE | Yes (auto) | No | Memory Engine. 3-step cognitive pipeline: ETHOS audit → PATHOS extraction → LOGOS synthesis. |

**Properties**: Any-entry. All mandatory phases tiered. No B4/B5 — integration=CI, delivery=merge, enhancement=re-enter.

### A2: Library — 6 Directories, Single Source of Truth

```
.hestai-sys/library/
├── constitution/     ← SEA (loaded by all 3 paths)
├── cognitions/       ← SHANK (35-line lean kernels + CRAFT line)
├── agents/           ← Identity (archetype scaling per tier, no pre-declared skills)
├── phases/           ← ARM (phase context payloads — revived from original library)
├── skills/           ← FLUKES: procedures (HOW to do the job)
└── patterns/         ← FLUKES: principles (HOW to constrain the job)
```

**Locked decisions**:
- Cognitions stay **35-line lean kernels** + CRAFT line. No schema inflation.
- Scope activation (archetype scaling) lives in **agent file**, not phase file.
- **Direct file paths**, not lib:// URIs. Filesystem is the API.
- Skills and patterns are **separate directories** (procedures vs principles).
- Phase files define **how cognitions behave per phase** (COGNITIVE_ADAPTATION block).

### A3: Cognitive Stack — 6 Steps Mapped to 4 Anchor Stages

The Fulcrum Anchorage (from debate decision `2026-03-22-anchor-ceremony-redesign.oct.md`):

```
COGNITIVE STACK              ANCHOR STAGE           LLM PHYSICS
1. cognitions/ (BIOS)     → REQUEST (loads)         State Collapse — kills "Helpful Assistant"
2. constitution/ (Laws)   → SEA (proves)            Primacy Anchoring — laws embed deepest
3. agents/ (Ego)          → SHANK (proves)          Role Prompting — name + mission + authority
4. phases/ (Environment)  → ARM (proves)            Contextual Calibration — ego meets reality
5. patterns/ (Principles) → FLUKES (proves)         Negative Constraint Priming — safety goggles
6. skills/ (Tools)        → FLUKES (bundled)        Recency Bias — procedural steps dominate action
```

**Key mechanism — Applied Cognitive Grammar**: At SEA stage, agent proves Constitution THROUGH its cognitive lens format. LOGOS must output `[TENSION] → [INSIGHT] → [SYNTHESIS]`. ETHOS must output `[VERDICT] → [EVIDENCE]`. Server regex-validates using MUST_USE grammar from cognition file. Cannot fake cognition absorption.

### A4: Three Loading Paths — Same Library, Different Depth

| Path | Name | Flow | Cost | Components |
|---|---|---|---|---|
| **Formal** | The Anchor | request → sea → shank → arm → flukes | 10-15k tokens | All 6 loaded and proven |
| **Colleague** | The Dispatch | anchor_micro() or injection | 3-5k tokens | Cognition + Identity injected (no proof) |
| **Debate** | The Debate | request → sea (early-exit) | 2-3k per turn | Cognition + Constitution + Identity only |

**Loading Path × Phase Matrix**:

| Phase | Formal | Colleague | Debate |
|---|---|---|---|
| D0 ORIENT | — | — | — |
| D1 UNDERSTAND | Fresh session | T2: research consult | T3: exploration debate |
| D2 EXPLORE | Within bound session | Quick consult | Wind/Wall/Door |
| D3 ARCHITECT | Architecture needs full context | Specialist consult | Architectural tensions |
| B0 VALIDATE | Formal CE review (T3) | Quick consult (T1) | Contested decisions |
| B1 PLAN | Planning needs project context | Task decomposer consult | — |
| B2 BUILD | IL bound for session | TMG, CRS, CE reviews | — |
| B3 REINTEGRATE | — | 3-step pipeline (ETHOS→PATHOS→LOGOS) | Complex reflection |

### A5: B2 BUILD — Tiered Review System

Evidence: M016 study (IL handles RED phase). Multi-model experiment (role diversity > model diversity).

| Tier | Trigger | Flow | Reviewers |
|---|---|---|---|
| T0 | 0 code lines (docs-only) | Exempt | None |
| T1 | <10 lines, single file | Self-review | Author |
| T2 | 10-500 lines, or multiple files | RED → TMG → GREEN → Review → Merge | TMG(Goose) + CRS(Gemini) + CE(Claude) |
| T3 | >500 lines, or arch changes, or security | RED → TMG → GREEN → Review → Merge | TMG + CRS + CE + CIV(Goose) |
| T4 | Manual invocation (strategic) | RED → TMG → GREEN → Review → Merge | TMG + CRS + CE + CIV + PE(Goose) |

**Refinement**: Line count alone is brittle. Add cognitive density modifier (50-line auth change → T3). Agent prompt .md files = code, not docs.

### A6: B3 REINTEGRATE — Multi-Agent Cognitive Pipeline

Headless, automated, no human attendance. Each step gets pure cognition and optimal model routing.

| Step | Job | Cognition | Model Routing |
|---|---|---|---|
| 1. AUDIT | Compare D3 blueprint to B2 reality | ETHOS | Fast/strict (Codex, Gemini Flash) |
| 2. EXTRACT | Identify reusable patterns | PATHOS | Creative (Claude Opus) |
| 3. SYNTHESIZE | Compress into updated constraints | LOGOS | Powerful synthesis (Gemini Pro) |

Evolution path: structurally similar to run_debate. Could evolve into governance-hall retrospective mode.

### A7: Constitution Enhancement

Add §0.5::PHILOSOPHY to carry Philosopher-Engineer DNA:

```
§0.5::PHILOSOPHY [The_Seal_of_Craft]
IDENTITY::"Engineer-philosophers: we build with understanding, not just instructions"
METHODOLOGY::"Understand fully → Shape patterns → Act minimally"
QUALITY::"Elegance = Impact ÷ Complexity"
INTERVENTION::"Remove accumulative complexity before adding essential complexity"
PROPORTIONALITY::"Match solution complexity to problem significance"
DELEGATION::"The conductor never plays an instrument — diagnose and delegate"
```

### A8: Cognition Enhancement

Add CRAFT line to each cognition file. Rescue useful old SHANK behaviours into THINK/THINK_NEVER arrays.

- LOGOS: `CRAFT::"Understand fully, shape patterns, act minimally."`
- ETHOS: `CRAFT::"Prove the structure holds before declaring victory."`
- PATHOS: `CRAFT::"Explore widely before the wall narrows the path."`

Update anchor ceremony to extract CRAFT alongside PRIME_DIRECTIVE.

---

## Part B: Delivery Plan (How To Build It)

### B1: Where Does the Anchor Rebuild Live?

**Target: hestai-workbench**

The workbench becomes the unified orchestration layer with injection payloads for each loading path:

| Path | Mechanism | Payload Assembly |
|---|---|---|
| **Formal** | Rebuilt anchor ceremony (5 MCP calls) | Server loads cognition grammar at REQUEST, validates at SEA via regex |
| **Colleague** | dispatch_colleague / enhanced consult | Workbench assembles: cognition + identity + phase context + task skill → single injection |
| **Debate** | Governance hall (evolved debate-hall) | Workbench assembles: cognition + constitution → debate agent prompt |

**Key implementation change**: The current odyssean-anchor-mcp stays operational but the workbench wraps it with:
1. Injection payload assembly for colleague and debate paths
2. Phase context resolution (which phase file to load based on current work)
3. Skill resolution (which skills to load based on agent + phase + task topic)

### B2: Implementation Sequence

| Order | What | Depends On | Outcome |
|---|---|---|---|
| 1 | **Write phase files** (d1-understand.oct.md through b2-build.oct.md) | Library structure locked | ARM payloads exist |
| 2 | **Update cognition files** (add CRAFT, rescue old SHANK behaviours) | Cognition decision locked | Enhanced lean kernels |
| 3 | **Update Constitution** (add §0.5::PHILOSOPHY) | Philosophy atoms identified | Philosopher-engineer DNA in law |
| 4 | **Define Dream Team roster** | Workflow phases defined, cognitive types mapped | Agent files to create/update |
| 5 | **Write/update agent files** (v9.0 with archetype tier scaling) | Roster decided | Identity files in library |
| 6 | **Audit skills and patterns** | Agent roster finalized | Clean FLUKES inventory |
| 7 | **Update anchor server** (regex validation for Applied Cognitive Grammar) | Cognition files + MUST_USE grammar | SEA proves cognition |
| 8 | **Build colleague injection** in workbench (dispatch_colleague) | Library complete | Colleague path operational |
| 9 | **Update governance hall** (load from cognition files, not hardcoded) | Cognition files updated | Debate path unified |
| 10 | **Write OPERATIONAL-WORKFLOW v2** | All above complete | Authoritative workflow reference |

### B3: Dependencies

```
Phase files (1) ──────────────────────────────────────────────┐
Cognition update (2) ─────────────────────────────────────────┤
Constitution update (3) ──────────────────────────────────────┤
                                                              ├→ Agent files (5) → Skill audit (6)
Dream Team roster (4) ────────────────────────────────────────┘
                                                                    │
Anchor server update (7) ← Cognition files (2)                     │
Colleague injection (8) ← Library complete (1-6)                   │
Governance hall update (9) ← Cognition files (2)                   │
Operational Workflow v2 (10) ← Everything (1-9)                    │
```

Steps 1-3 can happen in parallel. Step 4 (roster) can happen in parallel with 1-3. Steps 5-6 depend on 4. Steps 7-9 can happen in parallel after their dependencies. Step 10 is last.

---

## Part C: Roles & Content (What To Build) — PENDING

### C1: Dream Team Roster

**Status**: Not yet determined. The proposal identified cognitive types per phase but mapping to actual agents requires:

1. Review of all 31 current agents + 30 agents in ~/.claude/agents/
2. Empirical testing of contested merges (TA, ho-liaison, TMG, validator, PE)
3. Possible hybrid role creation
4. Testing via oa-router on representative scenarios

**What we know so far**:

Agents with confirmed unique identity (keep):
- Holistic Orchestrator (LOGOS) — conductor
- Implementation Lead (LOGOS) — builder
- Critical Engineer (ETHOS) — production gate
- Code Review Specialist (ETHOS) — CRS in review chain
- Requirements Steward (ETHOS) — North Star guardian
- Design Architect (LOGOS) — blueprint maker (TA absorption deferred)
- Universal Test Engineer (ETHOS) — test writer (TMG absorption deferred)
- System Steward (ETHOS) — librarian
- Ideator (PATHOS) — explorer
- Task Decomposer (LOGOS) — B1 planner
- Agent Expert (LOGOS) — meta-agent
- Skills Expert (ETHOS) — skill authority
- Synthesizer (LOGOS) — Door in debates, tension resolution
- Octave Specialist (LOGOS) — format authority

Agents requiring empirical testing before decision:
- Technical Architect — senior advisor, different from DA
- HO Liaison — deep analysis proxy
- Test Methodology Guardian — integrity guarding ≠ test writing
- Validator — fantasy enumeration, pure cold truth
- Principal Engineer — 6-month strategic horizon
- Error Architect — embedded in ERROR_RESOLUTION protocol
- Test Infrastructure Steward — owns CI pipeline

Agents embedded in constitutional workflows:
- Error Architect — ERROR_RESOLUTION.md Phase 3
- Test Methodology Guardian — ERROR_RESOLUTION.md Phase 2 (mandatory)

Domain specialists (conditional):
- Supabase Expert — if actively using Supabase
- SmartSuite Expert — if actively using SmartSuite

### C2: Phase File Content

Each phase file should contain (based on original ARM file format):

```octave
===PHASE_D2_EXPLORE===
META:
  TYPE::PHASE_CONTEXT
  PHASE::D2
  NAME::EXPLORE

COGNITIVE_ADAPTATION:
  LOGOS_EMPHASIS::"<how LOGOS behaves in this phase>"
  ETHOS_EMPHASIS::"<how ETHOS behaves in this phase>"
  PATHOS_EMPHASIS::"<how PATHOS behaves in this phase>"

DELIVERABLES::[<what comes out of this phase>]
EXIT_CRITERIA::[<how you know this phase is done>]
ANTI_PATTERNS::[<what goes wrong when done poorly>]

TIERING:
  T1::<lightweight version>
  T2::<moderate version>
  T3::<formal version>
===END===
```

### C3: Skill and Pattern Audit

Current inventory: 40+ skills, 13 patterns. Many are phantom references or aspirational. Audit needed to:
1. Confirm which skills actually exist and work
2. Identify which skills are needed by the Dream Team roster
3. Create missing skills for confirmed roster agents
4. Archive unused skills

### C4: Operational Workflow v2

Final deliverable: a clean OPERATIONAL-WORKFLOW.oct.md that replaces the current 10-phase, 42-subphase, 30-agent version with the 8-phase tiered architecture defined here.

---

## Appendix: Decision Trail

All locked decisions trace back to specific evidence:

| Decision | Source | Evidence |
|---|---|---|
| 6 phases → 8 phases | Debates (standard + premium) | Both independently found B3 + D0 |
| Lean kernels + CRAFT | Research + debate | LOGOS 8/8 optimized; prose dilutes constraints |
| Scope in agent file | External assessment (Gemini) | Agent-specific ≠ phase-specific |
| Direct file paths | External assessment (Gemini) | Filesystem = API; Role Factory never finished |
| Patterns separate from skills | HO analysis | Procedures ≠ principles |
| Applied Cognitive Grammar | Fulcrum Anchorage debate | Semantic Stacking; zero API breakage |
| B3 as multi-agent pipeline | User + HO synthesis | One cognition per prompt; model optimization |
| ARM files revived | Historical library analysis | Original library independently discovered phase payloads |
