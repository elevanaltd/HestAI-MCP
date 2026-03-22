# Dream Team Architecture

**Date**: 2026-03-22
**Status**: SPECIFICATION
**Scope**: Agent ecosystem architecture for AI-augmented systems building
**Implementation**: Target platform TBD (likely hestai-workbench). This spec is implementation-agnostic.

This document specifies WHAT to build and WHY. It does not specify WHERE (which server, which repository) or specific file paths. Physical location is an implementation decision. For exploration history and decision reasoning, see `dream-team-proposal.md`.

---

## 1. Workflow

### 1.1 Phase Structure

8 phases. Any-entry. All mandatory phases tiered. D-Space (design) flows through B0 Rubicon to B-Space (build), then B3 Memory feeds back.

```
D0 ORIENT (ambient — human selects tier + entry)
    |
D-SPACE: D1 UNDERSTAND - D2 EXPLORE - D3 ARCHITECT (fluid, any order)
    |
B0 VALIDATE (The Rubicon — recursive diagnosis on failure)
    |
B-SPACE: B1 PLAN - B2 BUILD (core execution with tiered review)
    |
B3 REINTEGRATE (automated memory engine — no human attendance)
    \-> feeds back to D1 constraints
```

| Phase | Name | Always? | Tiered | Purpose |
|---|---|---|---|---|
| D0 | ORIENT | Yes (ambient) | IS the tier selector | Human as ROUTER_PRIME. Selects tier, entry phase, provides context. Not a sequential step — the meta-cognitive anchor. |
| D1 | UNDERSTAND | No | T1-T3 | Explore problem space, formalize requirements. Skip when you know what you want. |
| D2 | EXPLORE | No | T1-T3 | Explore solution space — debate, research, comparison, spikes. Skip for obvious solutions. |
| D3 | ARCHITECT | Yes | T1-T3 | Think before coding. Even small features benefit (done organically at T1, formally at T3). |
| B0 | VALIDATE | Yes | T1-T3 | The Rubicon. When it blocks, it diagnoses WHERE the failure originated (D1/D2/D3) and routes back. |
| B1 | PLAN | Yes | T1-T3 | Decompose before coding. Even self-planning helps. |
| B2 | BUILD | Yes | T0-T4 | Core phase. RED tests, GREEN implementation, tiered review, merge. |
| B3 | REINTEGRATE | Yes (auto) | No | Memory Engine. Automated 3-step cognitive pipeline. Human doesn't attend. |

**Any-entry rules**: Work enters at whatever phase matches its scope. A bug fix enters at B2. A new feature starts at D1. A refactor at B1. When entering mid-workflow, the entering agent must declare what prerequisite information exists (even if informal) to satisfy downstream phases — e.g., entering at B2 requires stating the design intent that would have come from D3, however briefly.

**No B4/B5**: Integration = CI. Delivery = merge PR. Enhancement = re-enter workflow at appropriate phase.

### 1.2 B0 Rubicon — Recursive Diagnosis

When B0 blocks, it doesn't just say NO. It outputs:

```
Verdict: FAIL
Dissolve_Target: [D1 | D2 | D3]
Justification: "<specific gap identified>"
```

This routes the system back to the exact D-Space coordinate where the problem originated. Validation becomes structural diagnosis, not a checkbox.

### 1.3 B2 BUILD — Tiered Review

Evidence: M016 study (builder handles RED phase). Multi-model experiment (role diversity finds distinct issues; model diversity finds overlapping issues).

| Tier | Trigger | Flow |
|---|---|---|
| T0 | 0 code lines changed (docs-only, config-only). Agent prompt .md files count as code. | Exempt |
| T1 | <10 lines, single file, no security paths touched | Self-review |
| T2 | 10-500 lines, or multiple files, or new test files | RED → Test Validator → GREEN → Reviewers → Merge |
| T3 | >500 lines, or architecture changes, or security-touching code | RED → Test Validator → GREEN → Reviewers + Implementation Validator → Merge |
| T4 | Manual invocation only (strategic) | RED → Test Validator → GREEN → Reviewers + Implementation Validator + Strategic Reviewer → Merge |

**Reviewers per tier** (role types, not specific agent names — agent assignments TBD):
- **Test Validator** (ETHOS): Reviews failing tests ONLY — are these the right tests? What's missing?
- **Code Quality Reviewer** (ETHOS): Patterns, quality, regex/logic correctness
- **Production Readiness Reviewer** (ETHOS): Architecture, security, error handling
- **Implementation Validator** (ETHOS/LOGOS): Does implementation match spec? Structural mismatches? Right abstractions?
- **Strategic Reviewer** (ETHOS): 6-month architectural viability. Debt accumulation. Refactor-now-or-pay-later.

**Refinements**:
- Line count alone is brittle. Add cognitive density modifier (50-line auth change → T3).
- Different ROLES find different issues. Same role on different models finds overlapping issues. Optimize for role diversity.
- Rework loop: if any reviewer BLOCKS, fixes return to builder, then ONLY re-reviewed by blocking agent(s).

### 1.4 B3 REINTEGRATE — Multi-Agent Cognitive Pipeline

Headless, automated, no human attendance. Each step gets pure cognition from the triad and optimal model routing. One cognition per prompt.

| Step | Job | Cognition | Why This Cognition |
|---|---|---|---|
| 1. AUDIT | Compare blueprint to reality. What's the delta? | ETHOS | "Reveal what breaks" — deviation detection |
| 2. EXTRACT | Identify reusable patterns from the build cycle | PATHOS | "Reveal what could be" — pattern recognition |
| 3. SYNTHESIZE | Compress findings into updated constraints and context | LOGOS | "Reveal what connects" — structural compression |

Structurally similar to a debate (sequential multi-perspective analysis). Evolution path: governance-hall retrospective mode.

---

## 2. Component Library

### 2.1 Structure

6 component types, all served from a single library. Physical location is implementation-dependent.

```
library/
  constitution/     Laws of the system (SEA)
  cognitions/       How agents think (SHANK) — 3 files: logos, ethos, pathos
  agents/           Who agents are (Identity) — archetype tiers, authority, triggers
  phases/           Where agents operate (ARM) — phase context payloads
  skills/           What agents do: procedures (FLUKES)
  patterns/         What agents do: principles (FLUKES)
```

### 2.2 Component Definitions

**constitution/** — Immutable system laws. Loaded by all three paths. Includes §0.5::PHILOSOPHY carrying the Philosopher-Engineer DNA:
- "Understand fully, shape patterns, act minimally"
- "Elegance = Impact / Complexity"
- "Remove accumulative complexity before adding essential complexity"
- "The conductor never plays an instrument — diagnose and delegate"

**cognitions/** — 3 lean execution kernels (~35 lines each). Define HOW an agent thinks. Loaded by all three paths. Each contains:
- NATURE: FORCE, ESSENCE, ELEMENT
- RULES: MODE, PRIME_DIRECTIVE, CRAFT (philosopher-engineer DNA), THINK[], THINK_NEVER[]
- MUST_USE grammar patterns (used for Applied Cognitive Grammar validation)

**agents/** — Identity files. Define WHO an agent is. Contains:
- Role name, cognition type, archetype set
- Mission, principles, authority model (ultimate/blocking/advisory)
- Archetype scaling per tier (which archetypes activate at T1 vs T3)
- Triggers (what work activates this agent)
- Relationships (who it works with)
- NO pre-declared skills (skills resolve dynamically)

**phases/** — Phase context payloads (revived ARM files). Define WHERE an agent is operating. Contains:
- COGNITIVE_ADAPTATION: how each cognition type (LOGOS/ETHOS/PATHOS) emphasizes differently in this phase
- Deliverables expected from this phase
- Exit criteria
- Anti-patterns
- Tiering definitions (T1/T2/T3 for this phase)

**skills/** — Procedural capabilities. HOW to do the job. Step-by-step protocols, workflows, tool configurations. Loaded on-demand based on agent + phase + task.

**patterns/** — Principle capabilities. HOW to constrain the job. Cross-cutting lenses applied while executing any skill. (e.g., tdd-discipline, mip-build, verification-protocols).

### 2.3 Locked Design Decisions

| Decision | Answer | Evidence |
|---|---|---|
| Cognition schema | 35-line lean kernels + CRAFT line. No NATURE blocks, no PHILOSOPHY blocks. | Prose dilutes constraints. Anchor only extracts FORCE/ESSENCE/ELEMENT/MODE/PRIME_DIRECTIVE/CRAFT/THINK/THINK_NEVER. Dead tokens waste context. |
| Scope activation | In agent file (archetype tiers), not phase file. | Agent-specific: CE at T3 needs different archetypes than Ideator at T3. |
| File references | Direct paths relative to library root. No URI aliases. | Filesystem = API. LLMs read paths natively. lib:// resolvers are tech debt. |
| Skills vs patterns | Separate directories. Skills = procedures, patterns = principles. | Different purposes warrant distinct organisation. |
| Pre-declared skills | None in agent files. Skills resolve dynamically at bind time. | Prevents phantom skill references (50-80% found in agent interviews). |

---

## 3. Cognitive Loading

### 3.1 The Cognitive Stack (Loading Order)

6 components loaded in strict sequence. The order implements LLM attention physics:

| Order | Component | LLM Physics | Purpose |
|---|---|---|---|
| 1 | Cognition | State Collapse | Kills "Helpful Assistant." Forces LOGOS/ETHOS/PATHOS mode. |
| 2 | Constitution | Primacy Anchoring | Immutable laws embed into already-structured brain. |
| 3 | Identity | Role Prompting | Name, mission, authority boundaries within those laws. |
| 4 | Phase | Contextual Calibration | Calibrates identity to current environment. |
| 5 | Patterns | Negative Constraint Priming | Philosophical safety goggles before using tools. |
| 6 | Skills | Recency Bias | Procedural steps dominate immediate action selection. |

### 3.2 Three Loading Paths

All paths draw from the same library. Difference is depth, ceremony, and proof requirements.

**Path 1: FORMAL (The Anchor)**

Full binding ceremony. Agent proves comprehension at each stage.

| Stage | Loads | Proves | Mechanism |
|---|---|---|---|
| Stage 0 | Cognition + Constitution pointers | — | Pointers delivered |
| Stage 1 (SEA) | — | Cognition + Constitution | Applied Cognitive Grammar: agent formats Constitution proof THROUGH its cognitive lens. LOGOS: [TENSION]→[INSIGHT]→[SYNTHESIS]. ETHOS: [VERDICT]→[EVIDENCE]. PATHOS: [STIMULUS]→[CONNECTIONS]→[POSSIBILITIES]. Server regex-validates framing. |
| Stage 2 (SHANK) | Agent identity | Identity | Agent cites MISSION and AUTHORITY from its identity file. |
| Stage 3 (ARM) | Phase context | Work context | Agent maps current phase to reality, identifies tension. |
| Stage 4 (FLUKES) | Patterns + Skills | Capabilities | Agent declares which patterns and skills it will use. |

**Cost**: ~10-15k tokens. **Permit**: FULL (all capabilities).
**When**: Deep work sessions — implementation, architecture, critical reviews.

**Path 2: COLLEAGUE (The Dispatch)**

Lightweight injection. No proof ceremony. Speed over ceremony, but not over cognitive mode.

| What's Loaded | How |
|---|---|
| Cognition | Injected (agent still needs to THINK correctly) |
| Constitution | Injected or summarized |
| Identity | Injected (agent file extract) |
| Phase context | Task-scoped (not full project context) |
| Skill | One targeted skill for the dispatch task |
| Patterns | Optional (for longer dispatches) |

**Cost**: ~3-5k tokens. **Permit**: MICRO (scoped to task).
**When**: Quick advisory, review dispatch, consult calls, error resolution delegation, B3 pipeline steps.

**Path 3: DEBATE (The Debate)**

Cognition-focused loading for multi-perspective analysis. Identity is the cognitive lens, not the full agent.

| What's Loaded | How |
|---|---|
| Cognition | Loaded and proven (via Applied Cognitive Grammar at SEA) |
| Constitution | Proven alongside cognition |
| Identity | Minimal — role name + core authority only |
| Phase context | Debate TOPIC serves as ARM context |
| Patterns | Not loaded (debate methodology embedded) |
| Skills | Not loaded (no procedural execution in debates) |

**Cost**: ~2-3k tokens per turn. **Permit**: DEBATE (cognition + identity, no execution).
**When**: D2 exploration debates, B3 REINTEGRATE pipeline, architectural tension resolution, contested decisions at B0.
**Exit point**: After identity proof. No ARM/FLUKES stages.

### 3.3 Applied Cognitive Grammar (The Fulcrum)

The key anti-theater mechanism. At Stage 1, the agent must prove Constitution comprehension formatted strictly through its cognitive lens:
- If LOGOS: output must contain [TENSION], [INSIGHT], [SYNTHESIS] blocks
- If ETHOS: output must contain [VERDICT], [EVIDENCE] blocks
- If PATHOS: output must contain [STIMULUS], [CONNECTIONS], [POSSIBILITIES] blocks

The binding system validates using the MUST_USE regex patterns defined in the cognition files. If the agent hasn't absorbed the cognition, it doesn't know the syntax, and validation fails.

This is **mechanical enforcement**, not trust. Zero additional API calls. Zero token overhead.

### 3.4 Component Ownership Matrix

For each library component, which path loads it, how it's proven, and what "skip" means:

| Component | Formal Path | Colleague Path | Debate Path |
|---|---|---|---|
| **Cognition** | Loaded at Stage 0. Proven via grammar at Stage 1. | Injected (no proof). | Loaded at Stage 0. Proven via grammar at Stage 1. |
| **Constitution** | Proven at Stage 1 (citations). | Injected or summarized (no proof). | Proven at Stage 1 (citations). |
| **Identity** | Proven at Stage 2 (MISSION + AUTHORITY). | Injected (identity file extract, no proof). | Minimal identity at Stage 2. Early-exit after. |
| **Phase** | Proven at Stage 3 (tension mapping). | Task-scoped context injected. | Topic serves as context. Not formally loaded. |
| **Patterns** | Declared at Stage 4. | Optional injection for longer dispatches. | Not loaded. |
| **Skills** | Declared at Stage 4. | One targeted skill injected. | Not loaded. |

---

## 4. Delivery

### 4.1 Implementation Approach

The target platform for the rebuilt anchor and loading paths is the **hestai-workbench** (or equivalent orchestration layer). The workbench assembles injection payloads for each loading path from the shared library.

What the orchestration layer must provide:
1. **Payload assembly** — compose the right library components for each loading path
2. **Phase resolution** — determine which phase file to load based on current work
3. **Skill resolution** — determine which skills to load based on agent + phase + task topic
4. **Grammar validation** — validate Applied Cognitive Grammar at the formal path's SEA stage
5. **Permit management** — issue FULL, MICRO, or DEBATE permits based on loading path

### 4.2 Implementation Sequence

| Order | What | Depends On | Outcome |
|---|---|---|---|
| 1 | Write phase files | Library structure defined | ARM payloads exist |
| 2 | Update cognition files (CRAFT + rescued SHANK behaviours) | Cognition decision locked | Enhanced lean kernels |
| 3 | Update Constitution (§0.5 PHILOSOPHY) | Human approved | Philosopher-engineer DNA in law |
| 4 | Define Dream Team roster | Phases defined, cognitive types mapped | Agent list finalized |
| 5 | Write/update agent files (archetype tier scaling) | Roster decided | Identity files in library |
| 6 | Audit skills and patterns | Roster finalized | Clean FLUKES inventory |
| 7 | Build formal loading path (grammar validation) | Cognition files complete | Formal path operational |
| 8 | Build colleague loading path (dispatch injection) | Library complete | Colleague path operational |
| 9 | Build debate loading path (cognition file loading) | Cognition files complete | Debate path unified |
| 10 | Write OPERATIONAL-WORKFLOW v2 | All above complete | Authoritative workflow reference |

Steps 1-4 can run in parallel. Steps 5-6 depend on 4. Steps 7-9 can run in parallel after their dependencies. Step 10 is last.

---

## 5. Roles & Content — PENDING

### 5.1 Dream Team Roster

**Status**: Not finalized. Cognitive types per phase are defined (see proposal Part 9). Mapping to actual agents requires:
1. Review of all current agents (bundled + global)
2. Empirical testing of contested merges
3. Possible hybrid role creation

**Confirmed unique identities** (14):
Holistic Orchestrator (LOGOS), Implementation Lead (LOGOS), Critical Engineer (ETHOS), Code Review Specialist (ETHOS), Requirements Steward (ETHOS), Design Architect (LOGOS), Universal Test Engineer (ETHOS), System Steward (ETHOS), Ideator (PATHOS), Task Decomposer (LOGOS), Agent Expert (LOGOS), Skills Expert (ETHOS), Synthesizer (LOGOS), Octave Specialist (LOGOS).

**Requiring empirical testing** (7):
Technical Architect, HO Liaison, Test Methodology Guardian, Validator, Principal Engineer, Error Architect, Test Infrastructure Steward.

**Domain specialists** (conditional):
Supabase Expert, SmartSuite Expert.

### 5.2 Phase File Schema

Each phase file defines how cognitions adapt to that phase:

```
PHASE: <phase_id>
NAME: <phase_name>

COGNITIVE_ADAPTATION:
  LOGOS_EMPHASIS: <how convergent thinking serves this phase>
  ETHOS_EMPHASIS: <how validation thinking serves this phase>
  PATHOS_EMPHASIS: <how divergent thinking serves this phase>

DELIVERABLES: [<what comes out>]
EXIT_CRITERIA: [<how you know it's done>]
ANTI_PATTERNS: [<what goes wrong>]

TIERING:
  T1: <lightweight>
  T2: <moderate>
  T3: <formal>
```

Concrete phase definitions exist in the proposal (Part 9) for all 8 phases.

### 5.3 Outstanding Work

1. Finalize Dream Team roster (empirical testing of 7 contested agents)
2. Write all 6 phase files (D1, D2, D3, B0, B1, B2 — D0 is ambient, B3 is pipeline)
3. Audit all skills and patterns against roster needs
4. Write OPERATIONAL-WORKFLOW v2

---

## Appendix: Decision Trail

| Decision | Source | Evidence |
|---|---|---|
| 8-phase workflow | Debates (standard + premium tier) | Both independently found B3 + D0 |
| Lean kernels + CRAFT | Research + user directive | LOGOS 8/8 optimized; prose dilutes constraints; anchor only extracts specific fields |
| Scope in agent file | External assessment (Gemini) | Agent-specific archetype scaling ≠ phase-specific |
| Direct file paths | External assessment (Gemini) | Filesystem = API; lib:// resolver = tech debt |
| Patterns separate from skills | HO analysis | Procedures ≠ principles |
| Applied Cognitive Grammar | Fulcrum Anchorage debate | Semantic Stacking; zero API breakage; mechanical enforcement |
| B3 as multi-agent pipeline | User + HO synthesis | One cognition per prompt; model optimization |
| ARM files revived | Historical library analysis | Original library independently discovered phase payloads |
| Constitution amendment | Human authority | Solo developer owns the constitution |
| B2 reviewer diversity | M016 study | Role diversity > model diversity for defect detection |
