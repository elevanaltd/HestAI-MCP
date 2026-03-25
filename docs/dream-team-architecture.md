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
  agents/           Who agents are (Identity) — core archetype, task profile names
  phases/           Where agents operate (ARM) — phase context payloads
  skills/           What agents do: procedures (FLUKES)
  patterns/         What agents do: principles (FLUKES)

config/
  archetype-matrix  Maps {agent × task_profile → archetype(s) + qualifiers + skills + patterns}
  pipelines         Multi-agent sequence definitions (B3, D2, reviews, error resolution)
  dispatch-rules    Automatic colleague dispatch triggers
  tier-definitions  Review tiers, debate tiers, phase tiers
  role-model-map    Role → primary model + fallback model
```

### 2.2 Component Definitions

**constitution/** — Immutable system laws. Loaded by all three paths. Includes §0.5::PHILOSOPHY carrying the Philosopher-Engineer DNA:
- "Understand fully, shape patterns, act minimally"
- "Elegance = Impact / Complexity"
- "Remove accumulative complexity before adding essential complexity"
- "The conductor never plays an instrument — diagnose and delegate"

**cognitions/** — 3 lean execution kernels (~35 lines each). Define HOW an agent thinks. Loaded by all three paths. Each contains:
- §1 COGNITIVE_IDENTITY: FORCE, ESSENCE, ELEMENT (lean identity fields — NOT the old narrative NATURE blocks with PHILOSOPHY/CORE_GIFT/TRUTH_DEFINITION)
- §2 COGNITIVE_RULES: MODE, PRIME_DIRECTIVE, CRAFT (philosopher-engineer DNA), THINK[], THINK_NEVER[]
- §4 GRAMMAR: MUST_USE regex patterns (used for Applied Cognitive Grammar validation)
- CRAFT field is part of the current cognition schema (v2.2.0)

**agents/** — Identity files (~50 lines). Define WHO an agent is. "Blank slate" — no archetypes. Contains:
- §1::IDENTITY: Role, cognition, mission, principles, authority. NO archetypes (blank slate principle — opposing vectors cancel to RLHF baseline).
- §2::OPERATIONAL_BEHAVIOR: Tone, MUST_ALWAYS, MUST_NEVER, deliverables, evidence, gates, handoff, escalation.
- §3::TASK_PROFILES: Named list of task modes + DEFAULT. Validation: DEFAULT must exist in PROFILES array.
- §4::GRAMMAR: MUST_USE regex (Applied Cognitive Grammar — TARGET-STATE, not yet implemented), MUST_NOT patterns.
- No archetypes. No skills. No patterns. Those live in the Archetype Matrix (§2.4).

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
| Cognition schema | 35-line lean kernels + CRAFT line. No narrative blocks (PHILOSOPHY/CORE_GIFT/TRUTH_DEFINITION). Keep lean identity fields (FORCE/ESSENCE/ELEMENT) which ARE extracted by anchor. | Prose dilutes constraints. Anchor extracts FORCE/ESSENCE/ELEMENT/MODE/PRIME_DIRECTIVE/CRAFT/THINK/THINK_NEVER. Anything not in extraction list is dead tokens. CRAFT is part of the current cognition schema (v2.2.0). |
| Archetype architecture | **Matrix Model**: agent file has identity + task profile names (NO archetypes — blank slate). External matrix maps {agent × profile → archetypes + qualifiers + skills}. Optional core_archetype per agent in matrix config. Injection timing EXPERIMENTAL (C047 needed). | C045/C046: archetypes are cost-functions. Qualifier words matter. Triads=stability, singles=steering. Matrix enables experimentation without rewriting agent files. Blank slate prevents opposing vector cancellation. |
| File references | Direct paths relative to library root. No URI aliases. | Filesystem = API. LLMs read paths natively. lib:// resolvers are tech debt. |
| Skills vs patterns | Separate directories. Skills = procedures, patterns = principles. | Different purposes warrant distinct organisation. |
| Pre-declared skills | None in agent files. Skills resolve dynamically at bind time. | Prevents phantom skill references (50-80% found in agent interviews). |

### 2.4 Archetype Architecture — The Matrix Model

**What's proven** (C045/C046, cross-model validated):
- Archetypes are mathematical cost-functions that alter trade-off weighting
- Triads produce stability (28.7 mean, lowest variance)
- Singles produce steering (peaks at 30, dips to 21)
- Context-fit matters: HEPHAESTUS is right for constrained work, wrong for rapid prototyping
- The effect operates through trade-off weighting, not issue detection
- The qualifier word matters: DAEDALUS<systemic_ingenuity> is meaningfully different from DAEDALUS<architectural_elegance>

**Attention physics insight** (from dual debates 2026-03-23): Storage location ≠ injection point. The compiler can extract archetypes from wherever they're stored and inject at optimal attention positions. This decouples file organisation from prompt compilation.

**Placement note**: ALL empirical data (C045/C046) used archetypes in §1::IDENTITY. Optimal injection timing requires C047 ablation study. The matrix model below is agnostic to placement — it defines WHAT gets loaded, not WHERE in the prompt it appears. The compiler handles attention physics.

#### Core Archetype: Optional Gravitational Center

**The competing models**:
- **Blank Slate**: NO archetypes in identity. Prevents opposing vector cancellation (HEPHAESTUS + PROMETHEUS → RLHF baseline). Maximum matrix freedom.
- **Gravitational Center**: ONE core archetype in identity provides psychological continuity. Matrix injects 1-2 complementary archetypes to dynamically form triads at runtime. Core + injected must be complementary, never opposing.

**Why this is unresolvable without empirical data**: C045/C046 tested FIXED archetype sets (all declared together). Neither "blank slate + full injection" nor "core + complementary injection" has been tested. Both have valid theoretical arguments. Neither has data.

**Resolution: Make core_archetype OPTIONAL in the matrix config.**

If present: the engine includes it alongside matrix-injected archetypes. The core provides a permanent gravitational center; the matrix injects complementary archetypes to form runtime triads. The matrix designer is responsible for ensuring core + injected are complementary, not opposing.

If absent (blank slate): the engine uses matrix archetypes only. Maximum flexibility but requires the matrix to provide the full archetype set for every profile.

C047 will test both: same scenario, same agent, same final archetype set, vary whether one is "core" or all are "injected." If there's a measurable difference, we lock the winner. If not, blank slate wins by simplicity (MIP principle).

**The agent file schema supports BOTH models** — §1::IDENTITY has no archetypes either way. The core_archetype, if used, lives in the matrix as a per-agent default. This preserves clean identity files regardless of which model wins.

#### The Two-Layer Separation

**Layer 1: Agent DNA** (in the agent file — stable, rarely changes)
- Role, cognition, mission, principles, authority
- NO archetypes in the file itself. Archetypes are glasses, not eyeballs.
- A short list of TASK PROFILE NAMES — the high-level types of work this agent does
- A DEFAULT profile name (the most common task type, used when context can't determine)
- Validation: DEFAULT must exist in the PROFILES array

**Layer 2: The Archetype Matrix** (external config — experimental, changes as we learn)
- A lookup table mapping `{agent} × {task_profile} → {archetype(s) + qualifiers + skills + patterns}`
- OPTIONAL `core_archetype` per agent — permanent gravitational center (omit for blank slate)
- Lives outside agent files. Editable from the Glass. One change propagates everywhere.
- Each matrix row can specify ONE OR MULTIPLE archetypes with specific qualifiers per profile
- The DEFAULT profile row provides the agent's everyday archetype configuration
- Examples for Implementation Lead: `code_writing`, `test_building`, `error_diagnosis`, `refactoring`
- Examples for Code Review Specialist: `system_coherence`, `flaw_detection`, `security_audit`

#### Agent File Structure (Lean — ~50 lines)

```
§1::IDENTITY
  ROLE::IMPLEMENTATION_LEAD
  COGNITION::LOGOS
  MISSION::"Translate requirements into robust, working code."
  PRINCIPLES::[
    "Thoughtful Action: Comprehension precedes execution",
    "Constraint Catalysis: Boundaries catalyze breakthroughs",
    "Empirical Development: Reality shapes rightness",
    "Emergent Excellence: Quality from component interactions",
    "Full lifecycle ownership: construction through failure recovery back to green"
  ]
  AUTHORITY::[
    ULTIMATE::[Code_implementation, Test_creation, Artifact_generation, Failure_diagnosis],
    BLOCKING::[Untested_code, CI_failures, Quality_gate_violations],
    MANDATE::"Prevent technical debt through rigorous TDD and system awareness"
  ]

§2::OPERATIONAL_BEHAVIOR
  TONE::"Technical, Precise, Systematic"
  MUST_ALWAYS::[
    "Map dependencies before coding (Ripple Analysis)",
    "Write failing test BEFORE implementation (TDD)",
    "Verify local assumptions against global codebase before modifying",
    "Invoke code-review-specialist for all changes",
    "Number reasoning steps for transparency",
    "Own failure recovery: diagnose, fix, verify green state"
  ]
  MUST_NEVER::[
    "Treat code changes as isolated edits",
    "Optimize locally while degrading system coherence",
    "Merge without passing all quality gates",
    "Code without preceding failing test",
    "Abandon debugging to another agent without explicit escalation"
  ]
  DELIVERABLES::[Code_artifacts, Test_coverage, Ripple_analysis]
  EVIDENCE::[Test_results, Build_logs, Lint_output]
  GATES::[NEVER<UNTESTED_CODE,TECHNICAL_DEBT>, ALWAYS<DESIGN_INTEGRITY>]
  HANDOFF::"Receives build tasks → Returns implemented code + test artifacts + passing CI"
  ESCALATION::"Architectural uncertainty → Critical Engineer"

§3::TASK_PROFILES
  PROFILES::[code_writing, test_building, error_diagnosis, refactoring]
  DEFAULT::code_writing

§4::GRAMMAR
  MUST_USE::[REGEX::"^\\[ANALYSIS\\]", REGEX::"^\\[IMPLEMENTATION\\]"]
  MUST_NOT::[PATTERN::"I will just fix it", PATTERN::"Skipping tests"]
```

No archetypes anywhere in the agent file. No skills. No patterns. Those live in the Archetype Matrix.

#### The Archetype Matrix (External Config)

```yaml
archetype-matrix:

  # Implementation Lead — with optional core archetype (gravitational center model)
  implementation-lead:
    core_archetype: HEPHAESTUS<implementation_craft>  # OPTIONAL — omit for blank slate
    profiles:
      code_writing:
        archetypes:                          # injected alongside core (if present)
          - ATLAS<structural_foundation>
        skills: [build-execution]
        patterns: [tdd-discipline, mip-build]

      test_building:
        archetypes:
          - DAEDALUS<systematic_verification>
        skills: [test-generation]
        patterns: [tdd-discipline]

      error_diagnosis:
        archetypes:
          - ASCLEPIUS<root_cause_analysis>
          - ATHENA<pattern_recognition>
        skills: [error-triage]
        patterns: [verification-protocols]

      refactoring:
        archetypes:
          - DAEDALUS<architectural_elegance>
        skills: [build-execution]
        patterns: [mip-build, progressive-simplification]

  # Code Review Specialist — blank slate model (no core archetype)
  code-review-specialist:
    # core_archetype: absent — full blank slate, matrix provides everything
    profiles:
      system_coherence:
        archetypes:
          - ATHENA<architectural_coherence>
          - ARGUS<systemic_observation>
        skills: [code-quality-standards]
        patterns: [verification-protocols]

      flaw_detection:
        archetypes:
          - ARGUS<defect_discovery>
        skills: [code-quality-standards]
        patterns: [verification-protocols]

      security_audit:
        archetypes:
          - ATHENA<threat_awareness>
          - ARGUS<vulnerability_detection>
        skills: [security-analysis]
        patterns: [verification-protocols]
```

Note: IL example shows gravitational center model (core + 1-2 injected = runtime triad). CRS example shows blank slate model (no core, matrix provides all archetypes per profile). Both are valid. C047 will determine which produces better results.

#### How It Works at Runtime

1. **Engine reads agent file** → gets identity + task profiles list + default
2. **Profile selector determines active profile** — from task context, explicit selection, or default
3. **Engine reads matrix** → gets core_archetype (if present) + profile archetype(s) + qualifier(s) + skills + patterns
4. **Payload compiler assembles injection** → core archetype (if present) + profile archetypes (from matrix) + skills + patterns, placed at optimal attention positions

The **profile selector** can be:
- Explicit: human or orchestrating agent specifies the profile name
- Rule-based: pattern matching on task description
- Intelligent: a lightweight LLM call determines the best profile
- Fallback: uses the DEFAULT profile from the agent file

#### Why This Is Better

| Problem | How Matrix Solves It |
|---|---|
| Changing an archetype requires rewriting agent file | Change one cell in the matrix config |
| Testing DAEDALUS vs HEPHAESTUS for test_building | Swap the matrix row, run the test, compare |
| Discovering a better qualifier word | Update one string in one config row |
| Same archetype works differently across agents | Matrix maps archetype+qualifier PER agent PER profile |
| Agent files are bloated with PROFILES blocks | Agent files are ~50 lines. Matrix lives externally. |
| Skills declared in agent files create phantom references | Skills live in matrix, resolved at runtime. No phantom refs. |
| Triads vs singles for different contexts | Matrix rows can have 1, 2, or 3 archetypes as appropriate |

#### What's Locked

- Archetypes are mathematical cost-functions (C045/C046 proven)
- The qualifier word is part of the cost function (not just decoration)
- Triads for stability, singles for steering, multiple archetypes per profile supported
- **NO archetypes in agent files** — agent files are always blank slate
- Archetypes live exclusively in the matrix config
- `core_archetype` per agent is **OPTIONAL** in the matrix — gravitational center or blank slate, per agent
- Agent files contain identity + operational behavior + profile names + grammar only
- Matrix is external, configurable, experimental
- DEFAULT profile in matrix provides everyday personality (hot-swappable)
- Compiler handles injection timing (storage ≠ injection point)
- Validation: agent file DEFAULT must exist in PROFILES array
- If core_archetype is used, matrix designer ensures core + injected are complementary, never opposing

#### What Requires C047

Two open questions for empirical testing:
1. **Injection timing**: WHERE in the prompt does the compiler place archetypes? Same scenario, same archetype set, vary only injection position.
2. **Core vs blank slate**: Does a permanent core_archetype + complementary injections outperform full injection? Same scenario, same final archetype set, vary whether one is "core" or all are "injected."

The matrix model works regardless of which model wins for either question.

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
| Stage 1 (SEA) | — | Cognition + Constitution | Applied Cognitive Grammar (TARGET-STATE — not yet implemented): agent formats Constitution proof THROUGH its cognitive lens. LOGOS: [TENSION]→[INSIGHT]→[SYNTHESIS]. ETHOS: [VERDICT]→[EVIDENCE]. PATHOS: [STIMULUS]→[CONNECTIONS]→[POSSIBILITIES]. Server will regex-validate framing. |
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
| Cognition | Loaded and proven via Applied Cognitive Grammar at SEA (TARGET-STATE — will be validated when ceremony is rebuilt) |
| Constitution | Proven alongside cognition (TARGET-STATE) |
| Identity | Minimal — role name + core authority only |
| Phase context | Debate TOPIC serves as ARM context |
| Patterns | Not loaded (debate methodology embedded) |
| Skills | Not loaded (no procedural execution in debates) |

**Cost**: ~2-3k tokens per turn. **Permit**: DEBATE (cognition + identity, no execution).
**When**: D2 exploration debates, architectural tension resolution, contested decisions at B0. Analysis-only — no direct execution.
**NOT for**: B3 REINTEGRATE pipeline (which requires skill execution for document updates — use Colleague path).
**Exit point**: After identity proof. No ARM/FLUKES stages.

### 3.3 Applied Cognitive Grammar (The Fulcrum)

> **TARGET-STATE**: Applied Cognitive Grammar is designed but not yet implemented. The regex validation mechanism described below will be built when the anchor ceremony is rebuilt. The current anchor ceremony does not perform grammar-based proof validation. See `docs/decisions/2026-03-22-anchor-ceremony-redesign.oct.md` §10::OPEN_QUESTIONS for outstanding implementation questions.

The key anti-theater mechanism. At Stage 1, the agent must prove Constitution comprehension formatted strictly through its cognitive lens:
- If LOGOS: output must contain [TENSION], [INSIGHT], [SYNTHESIS] blocks
- If ETHOS: output must contain [VERDICT], [EVIDENCE] blocks
- If PATHOS: output must contain [STIMULUS], [CONNECTIONS], [POSSIBILITIES] blocks

The binding system will validate using the MUST_USE regex patterns defined in the cognition files. If the agent hasn't absorbed the cognition, it doesn't know the syntax, and validation fails.

This targets **mechanical enforcement**, not trust. Zero additional API calls. Zero token overhead.

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

## 4. System Architecture

### 4.1 Two-Layer Model

The system is a **Dual-Faced Application**: an engine that executes and a glass that configures. OCTAVE stays external as a format dependency.

```
LAYER 1: THE ENGINE
├── Library Index        — watches library files, indexes components, detects semantic conflicts
├── Payload Compiler     — JIT assembles injection payloads from library
├── Dispatcher           — sends payloads to models (CLI, API, MCP) with fallback routing
├── Continuation Store   — tracks dispatch chains (dispatch_id, parent, result, state)
├── Anchor Validator     — validates cognitive grammar proofs (formal path)
├── Pipeline Runner      — executes multi-step agent chains with BLOCK signal enforcement
├── Session Manager      — permits, state, memory
└── Epistemic Gate       — structural claim verification (receipts before action)

LAYER 2: THE GLASS
├── Workflow Editor      — define phases, map agents to steps, set tiers
├── Library Browser      — view/edit cognitions, agents, skills, patterns, phases
├── Archetype Matrix     — map {agent × task_profile → archetypes + qualifiers + skills}
├── Tier Configurator    — map agents to roles per tier, set model routing + fallbacks
├── Pipeline Designer    — compose multi-agent sequences (B3, D2, reviews, error resolution)
├── Rule Editor          — "when X happens, dispatch Y with Z model"
├── Dispatch Chain View  — trace who dispatched whom, with what result, full chain visibility
└── Session Dashboard    — observe running sessions, phase tracking, system map (Living Orchestra)

EXTERNAL DEPENDENCY:
└── OCTAVE               — format tooling, validation, compression (standalone)
```

**Layer 1** is the machinery. It reads configuration and executes: compiles payloads from library, dispatches to providers, validates proofs, runs pipelines. It doesn't know what agents exist — it reads config.

**Layer 2** is the admin panel. Where you configure everything: which agents exist, what tiers look like, what pipelines do, which models to use. When you save, it writes config that Layer 1 reads.

**OCTAVE** stays external because it's a format specification used across projects.

### 4.2 Configuration-Driven Orchestration

Everything is the same engine pattern: **read config → compile payload from library → dispatch to model → collect response**. Different use cases are just different config.

**Pipelines** (multi-agent sequences — B3, reviews, error resolution):
```yaml
pipelines:
  b3-reintegrate:
    trigger: "after_b2_merge"
    automated: true
    steps:
      - role: "critical-engineer"
        task: "Compare D3 blueprint to B2 reality."
      - role: "ideator"
        task: "Identify reusable patterns."
      - role: "system-steward"
        task: "Compress findings into updated constraints."
```

**Dispatch rules** (automatic colleague dispatch):
```yaml
dispatch-rules:
  - trigger: "ho_needs_deep_analysis"
    action: dispatch_colleague
    role: "ho-liaison"
    loading: colleague
  - trigger: "error_system_wide"
    action: dispatch_colleague
    role: "error-architect"
    loading: colleague
```

**Tier definitions** (review tiers, debate tiers, phase tiers):
```yaml
review-tiers:
  t2-standard:
    steps:
      - role: "test-methodology-guardian"
      - role: "code-review-specialist"
      - role: "critical-engineer"
```

Note: all config examples reference ROLE only. Model resolution happens via `config/role-model-map` which maps each role to a primary + fallback model:

```yaml
role-model-map:
  critical-engineer:
    primary: { provider: anthropic, model: claude-sonnet-4-6 }
    fallback: { provider: openai, model: codex-mini }
  ideator:
    primary: { provider: anthropic, model: claude-opus-4-6 }
    fallback: { provider: google, model: gemini-2.5-pro }
```

Pipelines, dispatch rules, and tier definitions don't hardcode models — the role-model-map is the single source of truth for model assignment. Change the model for any role in one place.

**All configurable from Layer 2.** Adding a new pipeline, dispatch rule, or tier means editing config in the admin panel — not writing code.

### 4.3 How Current Systems Map

| Current Thing | Destination | Rationale |
|---|---|---|
| Anchor ceremony (odyssean-anchor-mcp) | Layer 1: Anchor Validator | Binding is core engine. Proof validation is engine work. |
| Debate orchestration (debate-hall-mcp) | Layer 1: Pipeline Runner + Dispatcher | Multi-agent orchestration is engine work. tiers.yaml becomes Layer 2 config. |
| Session management (hestai-mcp clock_in/bind) | Layer 1: Session Manager | State is core engine. |
| Workbench UI | Layer 2: The Glass | Admin panel and dashboard. |
| OCTAVE tooling (octave-mcp) | External dependency | Format spec, reusable across projects. |
| .oct.md library files | Indexed by Layer 1, edited via Layer 2 | Library is data, not code. |

### 4.4 Engine Capabilities (from P15/P7 Gap Analysis)

**Continuation Store** (P15 #81)
When the dispatcher sends a payload to a model, the response chain must be traceable. Each dispatch gets a `dispatch_id`. The store tracks: who dispatched, which agent was invoked, what loading path was used, what the result was, and whether it was part of a chain (parent dispatch_id). This enables the Glass to show full dispatch chain visibility and enables resumed/continued dispatches.

**Provider Fallback** (P15 #45)
Each role→model mapping in config gets a `fallback` field. When the primary model is unavailable (rate limit, timeout, outage), the dispatcher automatically routes to the fallback. Example: if Opus rate-limits during B3 EXTRACT step, fallback to Gemini Pro. Config-driven, not code-driven.

```yaml
role-model-map:
  ideator:
    primary: { provider: anthropic, model: claude-opus-4-6 }
    fallback: { provider: google, model: gemini-2.5-pro }
  critical-engineer:
    primary: { provider: openai, model: codex-mini }
    fallback: { provider: anthropic, model: claude-sonnet-4-6 }
```

**BLOCK Signal Enforcement** (P7 #16)
When a pipeline step returns a BLOCK signal, the pipeline runner mechanically halts — not just text saying "BLOCKED" but actual process termination. The runner then routes to diagnosis (B0 Rubicon pattern for design failures, rework loop for review failures). This converts linguistic enforcement into functional enforcement.

**Semantic Conflict Detection** (P7 #17)
The Library Index doesn't just track files — it knows component dependencies. When changes to one component violate constraints of another, the index flags it. Example: if an agent file references a skill that was just deleted, or if two agents claim the same authority domain, the index detects the semantic conflict before it causes runtime failure.

**Epistemic Gate** (P15 #322)
Structural prevention of agents making confident claims without evidence. Three layers:
1. Tool schema enforcement — dispatch payloads include an `epistemic_receipt` field
2. Oracle verification — a `verify_artifact_state` capability checks claims against reality
3. Pattern — `epistemic-action-gate` loaded as a cross-cutting principle for high-stakes operations

**D2 EXPLORE as Pipeline** (P7 #2)
D2 is not just "run a debate." At T2-T3, it can be a configurable multi-agent pipeline: problem statement → ideation (PATHOS) → critique (ETHOS) → synthesis (LOGOS). Same engine as B3 REINTEGRATE and review tiers — different config. The Pipeline Designer in the Glass lets you compose this.

### 4.5 Modularity Note

Layer 1 (engine) and Layer 2 (glass) should be architecturally separable even if deployed together. If the engine needs to be rebuilt, the glass wraps the new engine. If the glass needs to be rebuilt, the engine keeps running. This is internal modularity within a single application — not microservice fragmentation.

### 4.6 Implementation Sequence

| Order | What | Layer | Depends On | Outcome |
|---|---|---|---|---|
| 1 | Write phase files | Library (data) | Library structure defined | ARM payloads exist |
| 2 | Update cognition files (CRAFT + THINK rescues) | Library (data) | Cognition decision locked | Enhanced lean kernels |
| 3 | Update Constitution (§0.5 PHILOSOPHY) | Library (data) | Human approved | Philosopher-engineer DNA |
| 4 | Define Dream Team roster | Library (data) | Phases + cognitive types mapped | Agent list finalized |
| 5 | Write/update agent files | Library (data) | Roster decided | Identity files in library |
| 6 | Audit skills and patterns | Library (data) | Roster finalized | Clean FLUKES inventory |
| 7 | Build engine: payload compiler + dispatcher | Layer 1 | Library complete | Core engine operational |
| 8 | Build engine: anchor validator (grammar validation) | Layer 1 | Cognition files | Formal path operational |
| 9 | Build engine: pipeline runner | Layer 1 | Dispatcher working | Multi-agent pipelines work |
| 10 | Build glass: workflow editor + tier configurator | Layer 2 | Engine operational | Config-driven orchestration |
| 11 | Write OPERATIONAL-WORKFLOW v2 | Documentation | All above | Authoritative reference |

Steps 1-6 (library content) can mostly run in parallel. Steps 7-9 (engine) depend on library. Step 10 (glass) depends on engine. Step 11 is last.

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
| Two-layer Engine+Glass | Consolidation analysis + user direction | Fragmentation was organic not designed; same engine pattern for all use cases |
| Continuation store | P15 #81 gap analysis | Dispatch chain traceability required for multi-agent orchestration |
| Provider fallback | P15 #45 gap analysis | Config-driven resilience for model availability |
| BLOCK signal enforcement | P7 #16 gap analysis | Linguistic enforcement must become mechanical enforcement |
| Semantic conflict detection | P7 #17 gap analysis | Library-level awareness of component dependencies |
| Epistemic gate | P15 #322 gap analysis | Structural prevention of claims without evidence |
| Archetype Matrix model | C045/C046 + dual debates + user design | Archetypes are cost-functions. Qualifier words matter. Matrix externalises mapping. Agent files are blank slates (~50 lines, zero archetypes). |
| Core archetype optional | Blank slate vs gravitational center analysis | Both models valid, neither tested. core_archetype OPTIONAL in matrix config. Agent files always blank slate. C047 decides winner. If no difference, blank slate wins by MIP. |
| Agent file schema v9 | Field-by-field analysis (HO vs IL) | §1 IDENTITY + §2 OPERATIONAL_BEHAVIOR + §3 TASK_PROFILES + §4 GRAMMAR. MODEL_TIER removed (deployment config). OUTPUT FORMAT merged into §4. Authority sub-fields merged. |
| D2 as configurable pipeline | P7 #2 gap analysis | Same engine as B3/reviews — different config |
| Living Orchestra = Glass | P7 #40 mapping | Session Dashboard + system map IS the living orchestra vision |
