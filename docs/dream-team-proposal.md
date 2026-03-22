# Dream Team Agent Review: Ground-Up Redesign Proposal

**Date**: 2026-03-21
**Author**: Holistic Orchestrator (LOGOS cognition, anchored session 8df7505c)
**Status**: PROPOSAL — requires human approval before implementation
**Scope**: Complete agent ecosystem redesign for solo-developer AI orchestration

---

## Executive Summary

The current 31-agent ecosystem grew organically over a year of iteration. Batch 1 interviews (PR #327) revealed 50-80% phantom skill references, overlapping missions, and aspirational capabilities. This proposal redesigns from first principles, informed by:

- **Philosophical DNA**: Philosopher-Engineer, MIP, PEF — "understand fully, shape patterns, act minimally"
- **Empirical evidence**: 243 research documents, cognitive lens optimization tests, role assessment failures
- **Evolution context**: Daedalus (4) → Thymos (6) → Zeus Orchestra (3 core) → HestAI Framework (SHANK+ARM+FLUKE) → Current (31)
- **Key research finding**: Protocol loading ≠ enforcement. Fewer, deeper roles outperform many shallow ones.

**Proposal**: Reduce from 31 agents to **13 core agents + 3 domain specialists** = **16 total**.

---

## Part 1: Constitution Assessment

### Current State
The Constitution (v2.1) captures structural mechanics well but is **missing the philosopher-engineer soul**. It has:
- MOTTO: "Structural integrity over velocity"
- Universal laws (context integrity, source fidelity, etc.)
- State management (LOBBY → BOUND → VOID)
- Enforcement protocols
- Governance hierarchy

### What's Missing
The Constitution does NOT carry these proven philosophical atoms:

1. **"Understand fully, shape patterns, act minimally"** (PEF) — the core methodology
2. **"Elegance = Impact / Complexity"** (MIP) — the quality metric
3. **"Remove accumulative complexity before adding essential complexity"** (MIP) — the intervention principle
4. **"Engineering is philosophy at 1ms resolution"** (PEF) — the identity
5. **Solution proportionality** — match complexity to problem significance
6. **"The conductor never plays an instrument"** — delegation discipline
7. **KEAPH pipeline heritage** — KNOWLEDGE→ESTABLISH→ABSORB→PERCEIVE→HARMONIZE as cognitive processing model

### Recommendation
Add a new section to the Constitution:

```
§0.5::PHILOSOPHY [The_Seal_of_Craft]
IDENTITY::"Engineer-philosophers: we build with understanding, not just instructions"
METHODOLOGY::"Understand fully → Shape patterns → Act minimally"
QUALITY::"Elegance = Impact ÷ Complexity"
INTERVENTION::"Remove accumulative complexity before adding essential complexity"
PROPORTIONALITY::"Match solution complexity to problem significance"
DELEGATION::"The conductor never plays an instrument — diagnose and delegate"
```

---

## Part 2: Cognition Assessment

### Current State
Three cognition files, each ~35 lines. Clean, minimal, effective kernels:
- **LOGOS** (The Door): CONVERGENT, "Reveal what connects." Tension→Insight→Synthesis
- **ETHOS** (The Wall): VALIDATION, "Reveal what breaks." Verdict→Evidence→Constraint
- **PATHOS** (The Wind): DIVERGENT, "Reveal what could be." Stimulus→Connections→Possibilities

### Assessment
The cognitions are **adequate as kernels** — the research proved that optimized cognitive lens definitions produce measurable performance improvements. The tension-insight-synthesis framework for LOGOS achieved 8/8 issue detection. PATHOS improved from 3/8 to 6/8 when given structured boundaries.

### Recommendation
Keep the three cognitions as-is. They are **empirically validated**. The richness should come from the agent file (how the cognition is applied to a specific mission), not from inflating the cognition files.

However, add one line to each cognition to carry the philosopher-engineer DNA:

- LOGOS: Add `CRAFT::"Understand fully, shape patterns, act minimally"`
- ETHOS: Add `CRAFT::"Prove the structure holds before declaring victory"`
- PATHOS: Add `CRAFT::"Explore widely before the wall narrows the path"`

---

## Part 3: The Key Design Question — Skills vs. Chassis-Profile

### Current Model (Chassis-Profile)
Each agent has CAPABILITIES with CHASSIS (always-loaded skills) and PROFILES (context-triggered skill groups). This creates:
- Phantom skill references (skills listed but never created)
- Aspirational capabilities that don't exist
- Coupling between agent identity and skill availability
- Every agent change requires updating skill references

### Proposed Model (On-Demand Skill Loading)
Skills are loaded by the anchor ceremony based on **what the task needs**, not what the agent file claims. The agent file defines:
1. **Identity** (who am I?)
2. **Cognition** (how do I think?)
3. **Authority** (what can I block?)
4. **Triggers** (when am I activated?)
5. **Relationships** (who do I work with?)

Skills are discovered and loaded at anchor time based on the topic/task, not pre-declared.

### Recommendation
**Hybrid approach**: Keep a minimal CHASSIS (1-2 skills that define the agent's core competency) but remove PROFILES entirely. Let skill loading be dynamic based on task context. This means:
- Agent files are about **identity**, not **capability inventory**
- Skills are first-class objects managed by skills-expert
- The anchor ceremony resolves skills at bind time
- No more phantom skill references

---

## Part 4: The Dream Team

### Design Principles
1. **Each agent must be a genuinely distinct cognitive identity** — not a profile of a shared identity
2. **The MIP test**: "What specific capability would be lost if this agent were removed?"
3. **The proportionality test**: Does a solo developer need this role?
4. **The enforcement test**: Can this role actually be enforced, or is it advisory theater?
5. **Evolution evidence**: Daedalus proved 4 works, Zeus proved 3 core works, 31 is regression

### The 13 Core Agents

#### 1. HOLISTIC ORCHESTRATOR (LOGOS) — Keep, refined
**Why it exists**: The conductor — thinks about work systemically, delegates to specialists. The developer's proxy.
**Cognition**: LOGOS — convergent synthesis required for routing decisions.
**Authority**: ULTIMATE — system-wide coherence, constitutional enforcement.
**Triggers**: System entry point, cross-boundary work, quality gate decisions, complex coordination.
**Relationships**: Routes to ALL other agents via oa-router. Receives from user.
**Core skills**: holistic-orchestration, subagent-rules
**What changed**: Already at v8.2 — lean, honest, conductor role. Keep as-is.

#### 2. IMPLEMENTATION LEAD (LOGOS) — Keep, refined
**Why it exists**: The primary builder. Writes code, runs tests, debugs. The hands of the system.
**Cognition**: LOGOS — synthesis of requirements into working code.
**Authority**: ULTIMATE over B2 execution — owns the build.
**Triggers**: Code changes, bug fixes, feature implementation, TDD cycles.
**Relationships**: Receives from HO/task-decomposer. Sends to code-review for review.
**Core skills**: build-execution
**What changed**: Consolidates what was spread across implementation-lead + error-architect. Error triage becomes a skill, not a separate agent.

#### 3. CRITICAL ENGINEER (ETHOS) — Keep, essential
**Why it exists**: The absolute production safety gate. Veto power. No one else can block a merge.
**Cognition**: ETHOS — validation, constraint enforcement, evidence-based verdicts.
**Authority**: BLOCKING (absolute veto) — production risk, constitutional violations.
**Triggers**: PR reviews (CE in CRS→CE chain), GO/NO-GO gates, production incidents.
**Relationships**: Final gate before merge. Consulted by HO on all significant decisions.
**Core skills**: constitutional-enforcement
**What changed**: Unchanged. This role is empirically proven and essential.

#### 4. CODE REVIEW SPECIALIST (ETHOS) — Keep, essential
**Why it exists**: First-pass structural review in the CRS→CE gate chain. Catches issues before CE.
**Cognition**: ETHOS — validation of code quality, security patterns, test coverage.
**Authority**: BLOCKING — can block PRs pending fixes.
**Triggers**: PR creation, code changes needing review.
**Relationships**: CRS[gemini] → CE[codex] chain. Reports findings to HO.
**Core skills**: review-discipline (to be created)
**What changed**: Simplified from v8.1 — removed aspirational skills. Focus on what it actually does: review code against standards.

#### 5. REQUIREMENTS STEWARD (ETHOS) — Keep, essential
**Why it exists**: Prevents scope drift and ensures North Star alignment. The "are we building the right thing?" check.
**Cognition**: ETHOS — validation of alignment, not creation of requirements.
**Authority**: ULTIMATE over North Star compliance — can block work that contradicts immutables.
**Triggers**: Scope questions, North Star amendments, requirement conflicts, phase transitions.
**Relationships**: Consulted by all phases. Works with ideator on D1-D2.
**Core skills**: constitutional-enforcement
**What changed**: Absorbs north-star-architect's D0/D1 extraction duties. One agent for requirements, not two.

#### 6. DESIGN ARCHITECT (LOGOS) — Keep, but TA absorption DEFERRED pending testing
**Why it exists**: Translates validated requirements into technical blueprints (D3).
**Cognition**: LOGOS — synthesis of constraints into architecture.
**Authority**: ULTIMATE over D3 specifications.
**Triggers**: D3 phase — blueprint creation, specification writing.
**Relationships**: Receives from D2 synthesis. Sends to B0 validation.
**Core skills**: None beyond cognition — skills loaded on-demand.
**DEFERRED DECISION**: TA absorption is deferred. TA is used as a senior technical ADVISOR (guidance role), which is fundamentally different from DA's specification-writing role. Empirical testing needed: invoke both agents on the same architecture decision scenario via oa-router and compare outputs. Adding PROMETHEUS archetype to DA's existing 3 risks dilution (C001 archetype study). Options: keep both, merge into hybrid, or confirm one covers the other. Test first.

#### 7. UNIVERSAL TEST ENGINEER (ETHOS) — Keep, essential
**Why it exists**: Writes tests. The only agent that generates test code.
**Cognition**: ETHOS — validation mindset essential for testing.
**Authority**: BLOCKING — test coverage and methodology.
**Triggers**: Test strategy (B2_00), test suite creation (B2_02), integration testing (B3_02).
**Relationships**: Works alongside implementation-lead. Consulted by code-review.
**Core skills**: test-generation (to be created)
**What changed**: Absorbs test-infrastructure-steward. TMG absorption DEFERRED pending testing — TMG's integrity-guarding discipline ("Truth Over Convenience", VIOLATION markers, anti-manipulation detection) may be genuinely distinct from test writing. Two testing agents may be over-engineering for solo dev, but test first.

#### 8. SYSTEM STEWARD (ETHOS) — Keep, refined
**Why it exists**: Maintains documentation, git history, and system patterns. The librarian.
**Cognition**: ETHOS — preservation, accuracy, completeness.
**Authority**: ULTIMATE over documentation integrity — NO code modification.
**Triggers**: Documentation updates, context freshness, pattern preservation, delivery (B4).
**Relationships**: Receives from HO. Updates .hestai/ state documents.
**Core skills**: documentation-placement
**What changed**: Absorbs solution-steward's B4 delivery documentation duties.

#### 9. IDEATOR (PATHOS) — Keep, essential
**Why it exists**: Generates creative possibilities. The "what could be" voice.
**Cognition**: PATHOS — divergent exploration, possibility expansion.
**Authority**: ADVISORY — generates options, never decides.
**Triggers**: D2 ideation, creative exploration, alternative generation, debate (Wind role).
**Relationships**: Feeds into design-architect. Wind in debates.
**Core skills**: None — pure cognition application.
**What changed**: Absorbs edge-optimizer's boundary exploration. One explorer, not two.

#### 10. TASK DECOMPOSER (LOGOS) — Keep, essential
**Why it exists**: Breaks validated designs into atomic implementation tasks (B1).
**Cognition**: LOGOS — structural decomposition requires synthesis thinking.
**Authority**: ULTIMATE over B1 task breakdown.
**Triggers**: B1 phase — after design validation, before implementation.
**Relationships**: Receives from B0 gate. Sends to implementation-lead.
**Core skills**: task-decomposition
**What changed**: Unchanged. Critical bridge between design and build.

#### 11. AGENT EXPERT (LOGOS) — Keep, essential
**Why it exists**: Domain authority for agent file creation and validation. Meta-agent.
**Cognition**: LOGOS — structural synthesis of agent definitions.
**Authority**: BLOCKING — on agent file commits.
**Triggers**: Agent creation, agent modification, agent interviews.
**Relationships**: Works with skills-expert. Receives from HO.
**Core skills**: agent-interview, agent-creation
**What changed**: Already at v8.1. Keep as-is.

#### 12. SKILLS EXPERT (ETHOS) — Keep, essential
**Why it exists**: Domain authority for skill/pattern creation and validation.
**Cognition**: ETHOS — spec compliance, validation of skill correctness.
**Authority**: BLOCKING — on skill/pattern file commits.
**Triggers**: Skill creation, trigger collision detection, skill restructuring.
**Relationships**: Works with agent-expert. Receives from HO.
**Core skills**: skill-creator
**What changed**: Already at v8.2. Keep as-is.

#### 13. SYNTHESIZER (LOGOS) — Keep, essential (REINSTATED)
**Why it exists**: Transforms either/or tensions into both/and innovations through emergent third-way solutions. The Door in debates.
**Cognition**: LOGOS — but applied specifically to TENSION RESOLUTION, not general synthesis.
**Authority**: ADVISORY — creates third ways, never decides which side wins.
**Triggers**: Debate hall (Door role), architectural tensions, opposing requirements, trade-off resolution.
**Relationships**: Receives from ideator (Wind) and critical-engineer (Wall). Produces resolved positions.
**Core skills**: synthesis-foundation
**Why reinstated**: The Synthesizer has unique operational protocols (TENSION_ANALYSIS, EMERGENCE_PROOF, anti-tiebreaker constraint, "1+1=3" emergence requirement) that NO other LOGOS agent possesses. Design Architect creates blueprints from requirements. Implementation Lead builds code. Neither transforms opposing positions into emergent third-way solutions. The LOGOS cognition provides the philosophical foundation, but the Synthesizer's operational behavior provides the mechanisms: structured tension decomposition, emergence verification, and the explicit prohibition against compromise or tiebreaking. This is a genuinely distinct cognitive identity, not a profile of LOGOS.

### The 3 Domain Specialists

#### 14. SUPABASE EXPERT (LOGOS) — Conditional
**Why it exists**: Database schema governance, RLS optimization, migration safety.
**Authority**: BLOCKING on schema changes.
**When to keep**: Only if the project actively uses Supabase.

#### 15. SMARTSUITE EXPERT (LOGOS) — Conditional
**Why it exists**: SmartSuite API field format validation, UUID corruption prevention.
**Authority**: BLOCKING on SmartSuite operations.
**When to keep**: Only if the project actively uses SmartSuite.

#### 16. OCTAVE SPECIALIST (LOGOS) — Keep, essential
**Why it exists**: Authority on OCTAVE format specification. No other agent can adjudicate OCTAVE questions.
**Authority**: ULTIMATE on OCTAVE spec interpretation.
**Triggers**: OCTAVE format questions, compression decisions, schema validation.

### Agents with Confirmed Overlap (can be absorbed — test to verify)

| Agent | Overlap With | User Context | Absorption Target |
|---|---|---|---|
| **quality-observer** | code-review-specialist + critical-engineer | Checks build quality; sometimes gives different results than CRS/CE (looks at overall excellence). Likely redundant. | CRS or CE, test first |
| **edge-optimizer** | ideator | Finds different solutions at edges — not demonstrably better (see debate-hall evidence). Ideator with add-ons could cover it. | Ideator, with optimization skill on-demand |
| **north-star-architect** | requirements-steward | D0/D1 extraction can be requirements-steward's job | Requirements-steward |

### Agents Embedded in Constitutional Workflows (CANNOT be paper-cut)

| Agent | Why It Can't Be Cut on Paper | Workflow Reference |
|---|---|---|
| **error-architect** | Embedded in ERROR_RESOLUTION.md as Phase 3 specialist for system-wide errors. The `/error` command constitutionally delegates to error-architect. Cutting it breaks the error resolution workflow. | ERROR_RESOLUTION.md Phase 3, error.md RACI |
| **test-methodology-guardian** | MANDATORILY invoked in ERROR_RESOLUTION.md Phase 2 before ANY error fix. Prevents test manipulation. Different job than writing tests (UTE) or maintaining CI (TIS). | ERROR_RESOLUTION.md Phase 2 |
| **test-infrastructure-steward** | Owns CI pipeline and testing infrastructure — a gap no other agent fills. Different approach than TMG (methodology) and UTE (test writing). | OPERATIONAL-WORKFLOW B2_00 |

### Agents That Serve Specific Workflow Phases (need workflow-first analysis)

| Agent | Workflow Role | User Experience |
|---|---|---|
| **complexity-guard** | Not in workflow — used ad-hoc as MIP enforcer | "If things feel over-engineered, I'd refer to CG." Could be a skill loaded by any ETHOS agent. |
| **visual-architect** | D3_02 — mockups + user validation | Purpose-built for visual focus. Could be DA with visual skill, but workflow has it as distinct phase. |
| **solution-steward** | B4_01 — package + docs + handoff | Has a workflow place. Could be system-steward with delivery skill. |
| **completion-architect** | B3_01 — integration + coherence | Owns integration orchestration. Could be IL with integration skill. |
| **security-specialist** | D3_04 + B3_03 + B4_04 | Three distinct workflow phases. Depth of security knowledge may warrant agent vs skill. |
| **validator** | D2_02 — feasibility constraints | Has unique fantasy enumeration (F1-Fn). Different from CE's production focus. |
| **principal-engineer** | B0_03 consulted + post-mortem strategic analysis | 6-month horizon, architectural decay detection. Different from CE tactical. |
| **ho-liaison** | Not in workflow — deep-analysis proxy for HO | Genuine analytical value for complex codebase analysis. |
| **technical-architect** | B0_03 + B1 consulted + B2 consulted + B5_02 | Used as senior technical ADVISOR for guidance — fundamentally different from DA spec writing. |

### The Fundamental Problem: Paper Analysis Was Wrong

The v1 proposal cut agents based on comparing agent FILES. This missed:

1. **Workflow embedding**: error-architect and TMG are constitutionally required by ERROR_RESOLUTION.md
2. **Usage vs definition**: TA is used as a senior advisor, not a spec writer. CG is a MIP enforcer.
3. **Phase ownership**: visual-architect, solution-steward, completion-architect each own specific workflow phases
4. **Different jobs, same cognition**: TMG (guards methodology), TIS (owns CI), UTE (writes tests) — three genuinely different jobs sharing ETHOS cognition

**Conclusion**: We cannot determine the right agent count from agent files alone. We must start from the OPERATIONAL WORKFLOW, define what tasks need doing, and then determine what roles serve them.

---

## Part 5: Skills Strategy

### Current Problem
Skills are declared in agent files but many don't exist. This creates "phantom capabilities."

### New Strategy: Skills as First-Class Objects

1. **Skills that exist and are proven** — keep and maintain
2. **Skills that are needed but don't exist** — create them (via skills-expert)
3. **Skills that are declared but not needed** — remove references
4. **New pattern: on-demand loading** — anchor ceremony resolves skills based on task, not agent declaration

### Priority Skills to Create/Validate
| Skill | For Agent | Status |
|---|---|---|
| review-discipline | code-review-specialist | CREATE |
| test-generation | universal-test-engineer | CREATE |
| security-analysis | On-demand (loaded by CE/CRS) | CREATE as skill |
| error-triage | On-demand (loaded by IL) | EXISTS |
| build-execution | implementation-lead | EXISTS |
| task-decomposition | task-decomposer | EXISTS |
| constitutional-enforcement | HO, CE, RS | EXISTS |
| holistic-orchestration | HO | EXISTS |
| subagent-rules | HO | EXISTS |
| agent-interview | agent-expert | EXISTS |
| skill-creator | skills-expert | EXISTS |
| documentation-placement | system-steward | EXISTS |

---

## Part 6: Workflow Impact

### Phase Structure v2 (LOCKED — agreed with human)

**Design principles:**
- **Any-entry**: Enter at whatever phase matches the work. A bug fix enters at B2. A new feature might start at D1. A refactor at B1.
- **All phases are tiered**: Effort scales to scope. T1 = lightweight/self. T3+ = formal/multi-agent.
- **No B3, B4, B5**: Integration = CI. Delivery = merge PR. Enhancement = re-enter at appropriate phase.
- **B2 is always executed**: Every piece of work goes through BUILD with tiered review.

| Phase | Name | Always Done? | Tiered? | Description |
|---|---|---|---|---|
| **D1** | UNDERSTAND | No — skip when you know what you want | Yes — T1: just formalize what you know. T2: research existing options. T3: deep exploration, debates, unknowns. | Explore the problem space, research, formalize requirements |
| **D2** | EXPLORE | No — skip for obvious solutions | Yes — could be a debate, market research, comparison analysis, or just structured discussion | Explore SOLUTION space — not just debate-hall. Research, compare, ideate. |
| **D3** | ARCHITECT | Yes — always done | Yes — T1: organic/conversational for small features. T2: documented design. T3: formal blueprint with specs. | Even small features benefit from thinking before coding. Done organically for small work, formally for complex. |
| **B0** | VALIDATE | Yes — always done | Yes — T1: quick consult or HO check. T2: consult tool with specialist. T3: formal GO/NO-GO with multiple agents. | Deliberate pause. Stopping for validation saves rework. Use consult/dispatch_colleague. |
| **B1** | PLAN | Yes — always done | Yes — T1: IL self-plans what they'll do. T2: task list with estimates. T3: atomic task decomposition with dependencies. | Even "plan what you'll do before doing it" helps. |
| **B2** | BUILD | Yes — always | Yes — T0: exempt (docs-only). T1: self-review. T2: TMG+CRS+CE. T3: +CIV. T4: +PE (strategic). | Core phase. IL(RED) → TMG → IL(GREEN) → Tiered Review → Merge. Most refined phase. |
| — | **SHIP** | Not a phase | — | Merge PR → CI → Deploy. Rework loop until all reviewers APPROVED. |

**Key insight: the old D0→D1→D2→D3→B0→B1→B2→B3→B4→B5 (10 phases, 42+ subphases) reduces to 6 phases with tiered execution. No work is lost — it's just not forced into a linear enterprise pipeline.**

### Debate Hall Integration
- **Wind (PATHOS)**: ideator (explores possibilities, generates paths)
- **Wall (ETHOS)**: critical-engineer (validates constraints, delivers verdicts)
- **Door (LOGOS)**: synthesizer (transforms tensions into emergent third-way solutions)

---

## Part 7: Methodology Correction (v3) — Workflow-First

### Why v1 and v2 Were Both Insufficient

**v1** (paper analysis): Compared agent files, declared overlaps, proposed cuts. Missed lived experience, workflow embedding, and constitutional dependencies.

**v2** (task-first): Better — start from tasks, not roles. But still didn't anchor to the OPERATIONAL WORKFLOW as the source of truth for what tasks actually exist.

**v3** (workflow-first): Start from the OPERATIONAL-WORKFLOW.oct.md, which defines every phase (D0→B5), every subphase, every RACI assignment, and every deliverable. This is the authoritative map of what work needs doing. Then ask: what TYPES of cognitive work do those tasks require? Then: can fewer roles serve those types?

### The KEAPH Insight

The 5-stage MCP binding ceremony (REQUEST→SEA→SHANK→ARM→FLUKES) implements KEAPH sequential loading science:

| KEAPH Phase | Anchor Stage | What It Does | Scientific Purpose |
|---|---|---|---|
| **K**nowledge | REQUEST | Receives pointers to Constitution, North Star, Cognition | Semantic priming before identity |
| **E**stablish | SEA | Proves comprehension of Constitution | Loads absolute laws without role-confusion |
| **A**bsorb | SHANK | Loads Agent Identity + Cognition overlay | Identity formation on stable foundation |
| **P**rocess | ARM | Reads PROJECT-CONTEXT and git state | Applies identity to real-world problem |
| **H**armonise | FLUKES | Receives skill atoms via COMMIT payload | On-demand capabilities AFTER identity is secure |

This means we have MORE FREEDOM than static agent files imply. The ceremony forces sequential cognitive loading — the agent digests constraints one by one. This raises the question: is there a CORE identity model (like the 3 cognitions) that composes dynamically, or do the specific archetype combinations in each agent file genuinely matter?

### The Correct Next Steps

**Step 1: Audit the OPERATIONAL WORKFLOW**
Go through D0→B5 and extract every distinct task that requires a specialist agent. The workflow is the source of truth, but it's also out of date — some agents referenced don't exist, some phases reference roles that have evolved.

**Step 2: Classify tasks by cognitive TYPE**
For each task, what TYPE of cognitive work is it?
- Divergent exploration (PATHOS)
- Constraint validation (ETHOS)
- Structural synthesis (LOGOS)
- Domain expertise (specialist knowledge)

**Step 3: Identify where multiple agents serve the same cognitive type on the same task**
These are the candidates for merging or hybrid creation.

**Step 4: Test empirically**
For contested merges, invoke both agents via oa-router on the same representative scenario. Compare outputs. Where a hybrid is proposed, create it and test it against the originals.

**Step 5: Consider whether to run a debate**
A Wind/Wall/Door debate on "What is the optimal agent ecosystem for a solo developer?" might surface genius solutions we're overlooking through pure analysis. The debate-hall evidence shows that multi-model debates find emergent solutions that single-model exploration misses.

### Open Questions for the Debate or Next Phase

1. **Is there a CORE identity model?** Like we reduced to 3 cognitions, is there a set of 5-7 core agent IDENTITIES that compose with skills to cover all tasks?
2. **Do archetype combinations genuinely matter?** Or does the cognition type carry 80% of the value with archetypes being marginal?
3. **Should the OPERATIONAL WORKFLOW be redesigned first?** The current workflow references 30+ agents. If the workflow is simplified, the agent count may naturally fall.
4. **Does KEAPH ceremony freedom change the design?** If skills load dynamically at FLUKES stage, maybe we need fewer fixed agent files and more dynamic composition.

---

## Part 8: Key Questions Answered

### Is the constitution complete?
**No.** It captures mechanics but misses the philosopher-engineer soul. Add philosophy section.

### Does it carry the philosopher-engineer stance?
**Not yet.** The philosopher-engineer DNA is scattered across archived documents. It needs to be crystallized into the Constitution and cognition files.

### Are the cognition files rich enough?
**Yes, as kernels.** Research proved that optimized, focused cognitive definitions outperform verbose ones. Add one CRAFT line each, no more.

### Should we have on-demand skill loading instead of chassis-profile?
**Hybrid.** Keep minimal CHASSIS (1-2 core skills), remove PROFILES. Let anchor ceremony resolve additional skills dynamically.

### What's the right number of agents for a solo developer?
**13 core + 3 domain specialists = 16.** Every iteration in the evolution reduced count while increasing depth. 31 was regression.

### Which current agents are profiles of a shared identity?

**Likely absorbable** (test to confirm):
- **quality-observer** — probably redundant with CRS/CE, but user notes it sometimes gives different results
- **edge-optimizer** — debate-hall evidence shows it finds different (not better) solutions. Ideator with on-demand skill likely covers it.
- **north-star-architect** — requirements-steward can handle extraction + validation

**Embedded in constitutional workflows** (cannot paper-cut):
- **error-architect** — constitutionally required by ERROR_RESOLUTION.md
- **test-methodology-guardian** — mandatorily invoked before any error fix (Phase 2)
- **test-infrastructure-steward** — owns CI pipeline, distinct from TMG and UTE

**Has specific workflow phase ownership** (need workflow audit first):
- **complexity-guard** — user uses as MIP enforcer (not just code review)
- **visual-architect** — D3_02 visual phase. Could be DA + skill, but purpose-built.
- **solution-steward** — B4_01 delivery. Could be SS + skill.
- **completion-architect** — B3_01 integration. Could be IL + skill.
- **security-specialist** — three distinct workflow phases (D3_04, B3_03, B4_04)
- **validator** — D2_02 feasibility. Fantasy enumeration unique.
- **principal-engineer** — strategic horizon, post-mortem analysis
- **ho-liaison** — deep-analysis proxy, genuine value
- **technical-architect** — senior advisor, different from DA spec writing

**Reinstated after analysis**:
- **synthesizer** — TENSION_ANALYSIS, EMERGENCE_PROOF, anti-tiebreaker are genuinely distinct

**Bottom line**: The answer isn't a number yet. It's a methodology — start from the workflow, classify the tasks, test the candidates.

### What's missing that no current agent covers?
**Nothing critical is missing.** The current system over-provisions. The gap is not in coverage but in depth — agents are too shallow because identity is spread across 31 files.

---

## Part 9: Phase Definitions (Workflow-First)

### Methodology
Each phase is defined by: ACTIVITIES → DELIVERABLES → COGNITIVE TYPES → TIERING → EXIT CRITERIA → ANTI-PATTERNS. Cognitive types are GENERIC (e.g., "Problem Explorer"), not agent-specific. Agent mapping comes after all phases are defined.

Analysis method: HO assessment + ho-liaison analysis (via PAL clink to Gemini), synthesized.

### D1: UNDERSTAND

**Purpose**: Transition from "I want to build X" to "I understand why X matters and what constraints govern it." An externalized pre-frontal cortex. Not a bureaucratic hurdle.

**Activities** (in order, not all mandatory):
1. **Map the problem space** — without solution bias. What is the actual problem?
2. **Research prior art** — what exists? What can we learn from? Market options, libraries, approaches.
3. **Extract assumptions** — surface implicit beliefs for future validation
4. **Formalize intent** — distill scattered needs into immutable requirements
5. **Define anti-scope** — explicitly declare what will NOT be built

**Deliverable**: North Star document (scaled to tier):
- Immutable core (5-9 unbreakable requirements)
- Constrained variables (flexible elements within boundaries)
- Assumption register (unvalidated beliefs requiring proof)
- Anti-scope (explicit non-requirements)

**Cognitive Types Needed** (generic):

| Cognitive Type | What It Does | When Needed |
|---|---|---|
| **Problem Explorer** (divergent) | Challenges initial framing. "Is this the REAL problem?" Maps edges. | T2, T3 |
| **Researcher** (analytical) | Investigates prior art, existing solutions, market landscape | T2, T3 |
| **Requirements Crystallizer** (convergent) | Distills scattered needs into immutable requirements | All tiers |
| **Assumption Challenger** (validating) | Pressure-tests stated and implicit assumptions | T2, T3 |

**Tiering**:

| Tier | When | What Happens | Deliverable |
|---|---|---|---|
| **T1** | Problem is known, intent is clear | Formalize what you know into bullet points. Quick exercise. | Simple requirements list, anti-scope notes |
| **T2** | Problem needs clarification, prior art exists | Structured research + formal North Star document | Full North Star with immutables, assumptions, anti-scope |
| **T3** | High complexity, high risk, unknown space | Multi-perspective debate (Wind/Wall/Door) + assumption audit | North Star + debate record + validated assumptions |

**Exit Criteria**:
- Immutables defined and locked
- Assumptions extracted and documented
- Anti-scope explicitly stated
- Problem space understood WITHOUT premature solution bias (no architecture in D1)

**Anti-Patterns**:
- **Solution jumping** — defining architecture in D1 (violates "understand fully first")
- **Coordination theater** — forcing T3 process on a T1 problem (violates MIP)
- **Vague immutables** — requirements that can't be empirically tested
- **Assumption cascade** — implicit beliefs treated as facts (causes late-stage failure)

---

*Phases D2, D3, B0, B1, B2 to follow — same methodology.*

---

## Appendix: Agent Count Through History

| Era | System | Core Agents | Key Insight |
|---|---|---|---|
| 2024 | Daedalus | 4 | PATHOS/ETHOS/LOGOS/HERMES — classical quartet works |
| 2024 | Thymos | 6 | Dual RAPH pathways, boundary management |
| 2025 | Zeus Orchestra | 3 core | Design to Build to Check with tiered intelligence |
| 2025 | HestAI Framework | Components | SHANK+ARM+FLUKE — solved role explosion |
| 2025 | HestAI Orchestrator | 12 | Phase-mapped roles D1 to B4 |
| 2026 | Current MCP | 31 | Organic growth — regression to complexity |
| 2026 | **Dream Team** | **16** | **Evidence-based reduction** |

---

*"Preserve what sings; silence what clutters." — MIP*
