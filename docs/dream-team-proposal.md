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

*Note: These were the original CRAFT proposals. They have been superseded by the debate-derived v2.2.0 values shown in Part 11, which are now implemented in the cognition files.*

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
**Triggers**: Documentation updates, context freshness, pattern preservation, pre-merge delivery documentation.
**Relationships**: Receives from HO. Updates .hestai/ state documents.
**Core skills**: documentation-placement
**What changed**: Absorbs solution-steward's delivery documentation duties (in the new workflow, delivery = merge PR, documentation happens before merge).

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
- **D0 is ambient**: The human is always D0 — selecting tier, choosing entry point, providing context. Not a sequential step.
- **B3 is automated**: Learning/reflection runs asynchronously after BUILD — no human overhead.
- **B0 is recursive**: When it blocks, it diagnoses WHERE the failure originated and routes back.
- **Tiering changes cognitive DEPTH, not just process weight**: T3 sidecars adversarial/exploratory cognition alongside primary.

| Phase | Name | Always Done? | Tiered? | Description |
|---|---|---|---|---|
| **D0** | ORIENT | Yes — ambient | No — it IS the tier selector | The human as ROUTER_PRIME. Selects tier, chooses entry phase, provides grounding context. The conductor selects the score. Not a sequential step — the meta-cognitive anchor that envelops the whole workflow. |
| **D1** | UNDERSTAND | No — skip when you know what you want | Yes — T1: formalize known. T2: research. T3: debate + assumption audit. | Explore the problem space, research, formalize requirements |
| **D2** | EXPLORE | No — skip for obvious solutions | Yes — could be a debate, market research, comparison analysis, or just structured discussion | Explore SOLUTION space — not just debate-hall. Research, compare, ideate. |
| **D3** | ARCHITECT | Yes — always done | Yes — T1: organic/conversational. T2: documented design. T3: formal blueprint with specs. | Even small features benefit from thinking before coding. Done organically for small work, formally for complex. |
| **B0** | VALIDATE | Yes — always done | Yes — T1: quick consult. T2: specialist consult. T3: formal GO/NO-GO committee. | **The Rubicon.** Deliberate pause between D-Space (design) and B-Space (build). When it blocks, it diagnoses WHERE the failure originated (D1? D2? D3?) and routes back — not just "NO" but "NO because D2 exploration was insufficient." |
| **B1** | PLAN | Yes — always done | Yes — T1: self-plan. T2: task list. T3: atomic decomposition. | Even "plan what you'll do before doing it" helps. |
| **B2** | BUILD | Yes — always | Yes — T0: exempt. T1: self-review. T2: TMG+CRS+CE. T3: +CIV. T4: +PE. | Core phase. IL(RED) → TMG → IL(GREEN) → Tiered Review → Merge. At T3+, secondary cognitions (PATHOS/ETHOS) sidecar alongside primary LOGOS — the execution environment becomes a creative crucible. |
| **B3** | REINTEGRATE | Yes — automated | No — always runs | **The Memory Engine.** Automated, asynchronous reflection after BUILD. Compresses what was learned, updates context documents, feeds back to D1 constraints. Solves LLM persistent memory problem. The human doesn't attend this meeting. |
| — | **SHIP** | Not a phase | — | Merge PR → CI → Deploy. Rework loop until all reviewers APPROVED. |

**Structure: D-Space → Rubicon → B-Space → Memory**
```
D-SPACE (Possibility)          B-SPACE (Actuality)         M-SPACE (Memory)
[D1 Understand]                [B1 Plan]                   [B3 Reintegrate]
[D2 Explore]     → B0 RUBICON → [B2 Build] → SHIP →       ↺ feeds back to D1
[D3 Architect]                                              constraints
```

D0 ORIENT is ambient — the human sets tier and entry point before anything begins. The phases within D-Space and B-Space are fluid (you can move between D1/D2/D3 freely without formal gates). B0 is the ONE hard gate between design and build.

### Debate-Derived Insights (from standard + premium tier debates)

**1. Living Harmonise / Dynamic Skill Forge**
Skills aren't loaded once at anchor time and frozen. When a blocker is encountered mid-phase, the system triggers micro-KEAPH: unbind current skills → bind adversarial/exploratory skills → resolve blocker → restore original identity. The agent dynamically mutates to handle the anomaly without losing phase context. This eliminates the need for many specialist agents — instead, core agents dynamically recompose.

**2. Tier-as-Cognitive-Depth**
Tiering doesn't just add more review agents — it changes the cognitive environment:
- **T1**: Zero-impedance. Implicit validation. Single cognition.
- **T2**: Standard gates. Primary cognition per phase.
- **T3+**: Creative escalation. B2_BUILD automatically sidecars SECONDARY PATHOS (Ideator) and SECONDARY ETHOS (Critical Engineer) alongside primary LOGOS. Code is actively challenged and evolved AS it is written.

**3. Inter-Phase Resonance**
The transition between phases is not an instant handoff — it's an active negotiation. D2(PATHOS) → D3(LOGOS) is a "resonance chamber" that checks: "Did divergent exploration generate enough velocity to survive convergent scrutiny?" If not, the transition rejects and reflects back to D2 without failing the workflow.

**4. Cognitive Alloys**
Core agents keep immutable base cognition (e.g., Critical Engineer = ETHOS). But when crossing a boundary (e.g., D2→D3), the KEAPH Harmonise stage alloys the agent's base with the phase's vector. ETHOS(Agent) + PATHOS(D2 Phase) = "Adversarial Explorer" (emergent). The liminal space GENERATES the required hybrid cognition.

**5. Phase Fusion at T3+**
Under extreme complexity, D3_ARCHITECT and B0_VALIDATE can fuse into a single concurrent node. Synthesis and Attack happen simultaneously rather than sequentially. This is the "architect while validating" mode.

**6. B3 Cognition: No New Type Needed**
The debate proposed a "WITNESS" 4th cognition — but analysis of what B3 actually does (compare blueprint to reality, extract deltas, update constraints, identify patterns) reveals it is primarily LOGOS synthesis with ETHOS validation. The Wind/Wall/Door triad is structurally complete and philosophically sound. B3's core job is convergent compression of build evidence — pure "Reveal what connects." No 4th cognition file needed.

### Debate Comparison: Standard vs Premium Tier
Both debates converged on the same 5 core insights (B3, D0, recursive B0, tier-as-depth, living Harmonise). Premium went deeper theoretically (resonance engines, gravitational attractors, artifact event horizons) but standard was more actionable. Key finding: **role diversity produces the same core insights across tiers**, supporting the M016 evidence that role diversity matters more than model diversity.

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
**Yes, as execution kernels. DECISION LOCKED.** Prose dilutes constraints. The anchor ceremony currently extracts FORCE, ESSENCE, ELEMENT, MODE, PRIME_DIRECTIVE, THINK, THINK_NEVER — anything else is dead tokens. CRAFT is now part of the cognition schema (v2.2.0) and the extraction list will be updated to include CRAFT when the anchor ceremony is rebuilt (see Part 11 for the v2.2.0 values). Old SHANK behaviours rescued into THINK/THINK_NEVER arrays. Do NOT inflate the schema with narrative blocks. See Part 11 for full reasoning.

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

### D2: EXPLORE

**Purpose**: Explore the SOLUTION space. Not just debate-hall — could be market research, comparison analysis, empirical spikes, or structured discussion. Answers: "How should we solve this?"

**Activities** (not all mandatory):
1. **Landscape scan** — evaluate existing prior art, libraries, market options
2. **Structured deliberation** — Wind/Wall/Door debate for complex decisions
3. **Expert consultation** — targeted Q&A with specialist cognitions (via consult tool)
4. **Empirical spikes** — throwaway prototypes to validate assumptions (NOT production code)
5. **Trade-off mapping** — cost vs benefit vs complexity matrices

**Deliverable** (scaled to tier):
- Decision record (ADR) capturing WHY the selected path was chosen
- Anti-goals log — explicitly rejected approaches with reasons (mandatory T2+)
- Refined hypothesis — clear direction ready for D3

**Cognitive Types Needed** (generic):

| Cognitive Type | What It Does | When Needed |
|---|---|---|
| **Possibility Expander** (divergent) | Generates options, challenges status quo, explores alternatives | T2, T3 |
| **Constraint Tester** (validating) | Tests feasibility, identifies friction, blocks fantasy | T2, T3 |
| **Option Synthesizer** (convergent) | Integrates competing options into coherent path | T2, T3 |
| **Empirical Validator** (pragmatic) | Builds throwaway spikes to validate abstract concepts | T3 |

**Tiering**:

| Tier | When | What Happens | Deliverable |
|---|---|---|---|
| **T1** | Solution is obvious, low risk | Quick mental check or informal chat. "Is there a reason NOT to do it this way?" | Decision note |
| **T2** | Multiple valid approaches, moderate complexity | Structured debate or comparison matrix | Lightweight ADR + anti-goals log |
| **T3** | High complexity, unknown solution space, high risk | Multi-perspective debate + empirical spikes + formal risk analysis | Comprehensive exploration record + ADRs |

**Exit Criteria**:
- Solution path selected — primary approach identified for D3
- Alternatives explicitly rejected with rationale documented
- Critical unknowns derisked (via spikes or research)
- Proposed solution satisfies Elegance = Impact / Complexity

**Anti-Patterns**:
- **Analysis paralysis** — infinite exploration without convergence (violates "act minimally")
- **Confirmation bias** — exploring only to justify pre-decided conclusion
- **Premature building** — writing production code instead of throwaway spikes (creates sunk cost)
- **Silent skipping** — bypassing D2 for complex problems due to impatience (leads to brittle architecture)

---

### D3: ARCHITECT

**Purpose**: Think before coding. The "hinge" between problem space (D-phases) and solution space (B-phases). Proportional thinking — rigor scales to complexity.

**Activities** (not all mandatory):
1. **Structure mapping** — define component boundaries and responsibilities
2. **Interface design** — establish data contracts between boundaries
3. **Constraint resolution** — balance tradeoffs discovered in D2
4. **Dependency planning** — sequence build order, identify blockers
5. **Failure anticipation** — map edge cases and error handling strategies

**Deliverable** (scaled to tier):
- T1: Chat consensus — shared mental model before coding
- T2: Design doc + component diagram + explicit assumptions
- T3: Blueprint + API contracts + failure cascade matrix + security model

**Cognitive Types Needed** (generic):

| Cognitive Type | What It Does | When Needed |
|---|---|---|
| **Structural Synthesizer** (convergent) | Integrates parts into cohesive whole via relational logic | All tiers |
| **Constraint Validator** (validating) | Ensures design respects boundaries and invariants | T2, T3 |
| **Prophetic Projector** (anticipatory) | Anticipates future states, failure modes, and friction | T2, T3 |

**Tiering**:

| Tier | When | What Happens | Deliverable |
|---|---|---|---|
| **T1** | Small feature, low risk | Brief AI dialogue. "Here's what I'm thinking, any issues?" Organic, conversational. | Shared understanding before coding |
| **T2** | Standard feature, multiple components | Draft core structures, document key decisions | Design doc committed to repo |
| **T3** | System core, high risk, multiple integrations | Rigorous specification with all tensions resolved | Comprehensive blueprint |

**Exit Criteria**:
- **No magic boxes** — all components have defined mechanisms and owners
- **Interfaces locked** — data shapes crossing boundaries are explicit and typed
- **Tradeoffs decided** — ambiguity from D2 resolved into concrete choices
- **Proportionality check** — design depth matches problem tier

**Anti-Patterns**:
- **Under-tiering** — coding before thinking for complex features (architectural debt)
- **Over-tiering** — formal blueprints for trivial changes (velocity death)
- **Implicit assumptions** — failing to state invariants across boundaries (integration failure)
- **Happy-path obsession** — designing without failure modes (brittle production)

---

### B0: VALIDATE

**Purpose**: Deliberate pause. "Is the design ready to build?" Stopping for validation, however small, prevents exponential rework cascades.

**Activities**:
1. **Design interrogation** — challenge assumptions against constraints
2. **Feasibility check** — verify technical viability with current context
3. **Alignment verification** — ensure solution meets original intent (D1 immutables)
4. **Peer review simulation** — use AI as proxy for peer validation (consult/dispatch_colleague)

**Deliverable**: GO/NO-GO decision (recorded)

**Cognitive Types Needed** (generic):

| Cognitive Type | What It Does | When Needed |
|---|---|---|
| **Critical Evaluator** (validating) | Challenges constraints, security, boundaries | All tiers |
| **Feasibility Assessor** (analytical) | Checks structural consistency and viability | T2, T3 |

**Tiering**:

| Tier | When | What Happens | Deliverable |
|---|---|---|---|
| **T1** | Small feature, clear design | Quick consult: "Any obvious flaws?" Informal GO. | Verbal/chat GO |
| **T2** | Standard feature | Submit design artifact for targeted critique against specific risks | Documented feedback + GO |
| **T3** | High risk, architectural change | Multi-perspective committee validation (convene tool). Explicit approval from defined cognitive roles. | Formal GO/NO-GO record |

**Exit Criteria**:
- Explicit GO decision exists (recorded)
- Identified risks either mitigated or consciously accepted

**Anti-Patterns**:
- **Momentum blindness** — skipping B0 because the idea "feels right" without external validation
- **Validation theater** — asking for validation but ignoring warnings to maintain velocity
- **Over-validation** — T3 rigor for trivial changes (violates MIP)

---

### B1: PLAN

**Purpose**: Decompose validated design into actionable execution steps. Even "plan what you'll do before doing it" helps.

**Activities**:
1. **Task decomposition** — break design into atomic implementation steps
2. **Dependency mapping** — identify execution sequence and blockers
3. **Context scoping** — determine exactly which files/functions need modification
4. **Verification design** — define how each step will be tested (Red/Green prep)

**Deliverable**: Execution plan (step-by-step checklist, scaled to tier)

**Cognitive Types Needed** (generic):

| Cognitive Type | What It Does | When Needed |
|---|---|---|
| **Tactical Planner** (convergent) | Sequences, orders, decomposes into actionable steps | All tiers |
| **Implementation Specialist** (practical) | Knows which files, functions, dependencies are involved | All tiers |

**Tiering**:

| Tier | When | What Happens | Deliverable |
|---|---|---|---|
| **T1** | Small change, single file | Executing agent outputs bulleted next-steps before writing code | Inline plan |
| **T2** | Standard feature, multiple files | Dedicated planning step generates written checklist | Task checklist |
| **T3** | Complex, multi-component, dependencies | Formal task breakdown with dependencies, context paths, validation criteria per step | Atomic task manifest |

**Exit Criteria**:
- A sequence of actions is defined
- The immediate next action is unambiguous and unblocked

**Anti-Patterns**:
- **Planning while coding** — writing implementation before deciding the full sequence (tangled state)
- **Monolithic tasks** — steps too large to validate independently
- **Context bloat** — planning to load entire codebase rather than targeting specific files

---

### B2: BUILD

**Purpose**: The core execution phase. Most refined, most used. Every piece of work goes through this.

**Evidence base**: M016 study proves IL should handle RED phase (not separate test engineer). Multi-model experiment proves different ROLES find different issues; same role on different models finds overlapping issues.

**Activities** (sequential):
1. **RED** — translate requirements into failing executable assertions (tests)
2. **TEST VALIDATION** — adversarial review of test coverage and alignment
3. **GREEN** — implement code to satisfy test constraints
4. **REFACTOR** — structural optimization maintaining green state
5. **TIERED REVIEW** — code routed to review agents based on T0-T4 classification
6. **REWORK LOOP** — address BLOCK verdicts with targeted fixes, re-review only by blocking agents
7. **MERGE** — integration into mainline

**Deliverables**:
- Validated test suite (proof of requirements)
- Production code (passing all tests)
- Review assessments (structured verdicts from tiered agents)
- Merge commit (traceable integration point)

**Cognitive Types Needed** (generic):

| Sub-step | Cognitive Type | What It Does |
|---|---|---|
| RED | **Translation Cognition** | Converts intent/requirements to executable logic |
| TEST VALIDATION | **Adversarial Cognition** | Finds gaps in verification boundaries, prevents rubber-stamping |
| GREEN | **Constructive Cognition** | Builds logic to satisfy constraints |
| REFACTOR | **Structural Cognition** | Optimizes patterns and readability |
| REVIEW | **Critical Cognition** | Evaluates against security, performance, architecture standards |
| REWORK | **Adaptive Cognition** | Resolves critiques without breaking invariants |

**Tiering**:

| Tier | Trigger | Review Flow |
|---|---|---|
| **T0** | 0 code lines (docs-only, config-only) | Exempt |
| **T1** | <10 lines, single file, no security paths | Self-review |
| **T2** | 10-500 lines, or multiple files | RED → TMG → GREEN → CRS + CE → merge |
| **T3** | >500 lines, or architecture changes, or security-touching | RED → TMG → GREEN → CRS + CE + CIV → merge |
| **T4** | Manual invocation (strategic) | RED → TMG → GREEN → CRS + CE + CIV + PE → merge |

**Tier refinement insight** (from ho-liaison): Line count alone is brittle. A 50-line security/auth change should trigger T3, while a 400-line boilerplate data model can stay T2. Consider adding a "Cognitive Density" modifier and semantic complexity overrides. Also: agent prompt markdown files (.md instructions) should be treated as code, not docs — they alter system behavior.

**Exit Criteria**:
- All tests passing + test validation agent approved
- No coverage regression in critical paths
- All required tier agents return APPROVED
- All BLOCK verdicts resolved and cleared by original blocker

**Anti-Patterns**:
- **Validation theater** — writing tests AFTER implementation (defeats RED/GREEN discipline)
- **Review fatigue** — sending rework to agents that already approved (waste)
- **Model redundancy** — using different models for same role expecting novel insights (evidence shows role diversity matters more)
- **Tier bypass** — splitting large PR into small T1s to evade T3 review
- **Test rubber-stamping** — approving tests that lack meaningful assertions

---

### D0: ORIENT (Debate-Derived Addition)

**Purpose**: The human as ROUTER_PRIME. Not a sequential phase — the ambient meta-cognitive anchor. Selects the score; doesn't play an instrument.

**Activities**:
1. **Problem recognition** — identify what needs to be done
2. **Tier selection** — how much cognitive depth does this deserve? (T1 typo fix vs T3 architecture change)
3. **Entry point selection** — which phase to enter (D1 for new idea, B2 for known fix)
4. **Context injection** — provide the grounding intent for agents

**Deliverable**: None explicit — D0 is the act of DECIDING to begin. The tier and entry point are the output.

**Cognitive Types Needed**: None — this is the HUMAN'S cognitive act. The orchestrating agent (HO) may assist with tier classification, but the decision is human.

**Why it matters**: Without D0, agents lack grounding context. The human's intent, tier selection, and entry point choice are the "Knowledge" stage of macro-KEAPH. Every workflow begins here, whether consciously or not.

---

### B0: VALIDATE — Updated with Recursive Rubicon

*Note: B0 is defined above but updated here with the debate-derived insight.*

**Critical addition — Recursive Diagnosis**: When B0 blocks, it doesn't just say "NO." It diagnoses WHERE the failure originated:
- "BLOCKED: D1 understanding insufficient — immutables are vague"
- "BLOCKED: D2 exploration incomplete — untested assumption about API capability"
- "BLOCKED: D3 blueprint has undefined failure mode for auth timeout"

The output is: `Verdict::FAIL → Dissolve_Target::[D1|D2|D3] → Justification`

This turns B0 from a binary checkpoint into a diagnostic prism that routes the system back to the exact D-Space coordinate where the problem originated.

---

### B3: REINTEGRATE (Debate-Derived Addition)

**Purpose**: The Memory Engine. Automated, asynchronous reflection after BUILD. Solves the fundamental LLM problem: no persistent memory. Ensures the system LEARNS from what it built.

**Architecture**: B3 is NOT a single agent's job. It is a **multi-agent cognitive pipeline** — a headless, sequential chain where each step gets pure cognition from the triad. This preserves "one cognition per prompt" and enables optimal model routing per step.

**The B3 Pipeline** (all automated, no human attendance):

| Step | Job | Cognition | Agent (tbc) | Model Routing |
|---|---|---|---|---|
| **1. AUDIT** | Compare D3 blueprint to B2 reality. What's the delta? | ETHOS — "Reveal what breaks" | Critical Engineer or CRS | Fast/strict model (e.g. Codex, Gemini Flash) |
| **2. EXTRACT** | Identify reusable patterns from this build cycle | PATHOS — "Reveal what could be" | Ideator (re-tasked as Pattern Seeker) | Creative model (e.g. Claude Opus) |
| **3. SYNTHESIZE** | Compress findings into updated constraints and context docs | LOGOS — "Reveal what connects" | System Steward or HO | Powerful synthesis model (e.g. Gemini Pro) |

**Step 1 Output**: Delta Report — "D3 specified 3 endpoints, B2 built 5. 2 endpoints are undocumented drift."
**Step 2 Output**: Pattern Candidate List — "The retry-logic in the new API handler is novel; extract as universal pattern."
**Step 3 Output**: Committed updates to PROJECT-CONTEXT.oct.md, North Star deltas (if requirements shifted), new pattern files.

**Why multi-agent pipeline is superior**:
1. **Model optimization** — route each cognitive step to the model that excels at it
2. **Cognitive purity** — no agent simultaneously critiques (ETHOS) AND brainstorms (PATHOS)
3. **Infrastructure exists** — this is a headless version of the D2 debate pattern. DispatchService / workbench can run this 3-step chain via API calls, making it cheap and fast.
4. **Evolution path** — this is structurally similar to run_debate. B3 could evolve into a specialized debate-hall mode for retrospective synthesis.

**No new cognition needed** — the Wind/Wall/Door triad is structurally complete and philosophically sound. B3 uses all three in sequence, not a hybrid.

**Why it matters**: Without B3, the system is structurally amnesiac. LLM agents with no persistent memory need learning to be an explicit, automated phase — not an afterthought. B3 converts ephemeral task-learning into durable artifacts. The human doesn't attend this meeting — learning becomes compounding and invisible.

**Anti-Patterns**:
- **Skipping B3** — "we shipped, we're done" (guarantees re-learning the same lessons)
- **Manual B3** — requiring human involvement defeats the purpose (overhead kills adoption)
- **B3 bloat** — capturing everything instead of only constraint-relevant deltas (noise)
- **Single-agent B3** — trying to do audit + extraction + synthesis in one prompt violates cognitive purity

---

*All 8 phases defined (D0, D1, D2, D3, B0, B1, B2, B3).*

---

## Part 10: The Three Loading Paths

### The Insight
All agent loading draws from the SAME component library (cognitions, agent files, skills). The difference is DEPTH and CEREMONY COST. Three distinct paths exist, each with different KEAPH coverage:

### Path 1: FORMAL Loading (Full KEAPH — "The Anchor")

**What it is**: The full Odyssean Anchor ceremony. 5-stage progressive interrogation where the agent PROVES comprehension at each stage.

**KEAPH mapping**:

| KEAPH | Anchor Stage | What's Loaded | Cost |
|---|---|---|---|
| **K**nowledge | REQUEST | Pointers to Constitution, North Star, Cognition file | ~1k |
| **E**stablish | SEA | Agent proves Constitution comprehension (cites MOTTO, immutables) | ~3k |
| **A**bsorb | SHANK | Agent reads its own identity file + cognition overlay | ~3k |
| **P**rocess | ARM | Agent reads PROJECT-CONTEXT, git state, maps tensions | ~3k |
| **H**armonise | FLUKES | Skills loaded via compressed anchor kernel atoms | ~2k |

**Total cost**: ~10-15k tokens per ceremony.

**When to use**: Deep work requiring full identity + context + capabilities. Implementation sessions, architecture work, critical reviews. When the agent needs to UNDERSTAND the project, PROVE identity, and HOLD context across a long session.

**Current mechanisms**: Odyssean Anchor (anchor_request → anchor_lock → anchor_commit), oa-router subagent delegation, bind command bootstrap.

### Path 2: COLLEAGUE Loading (Lightweight Identity — "The Dispatch")

**What it is**: A quicker binding that injects identity and context WITHOUT the full proof ceremony. The agent gets SEA + SHANK + relevant ARM + skill, but in a single injection rather than staged interrogation. More depth than a raw system prompt, less than formal anchor.

**KEAPH mapping**:

| KEAPH | What's Loaded | How |
|---|---|---|
| **K**nowledge | Skipped or implicit (agent already running) | — |
| **E**stablish | SEA (Constitution) — injected, not proven | Single-shot injection |
| **A**bsorb | SHANK (Identity + Cognition) — injected, not proven | From library |
| **P**rocess | Relevant ARM context — scoped to task | Task-specific |
| **H**armonise | Specific skill for the job | On-demand |

**Total cost**: ~3-5k tokens.

**When to use**: Quick advisory, delegation to colleagues, consult calls. When speed matters but quality must exceed raw prompting. B0 validation consults, B1 planning advice, error resolution delegation, colleague dispatch.

**Current mechanisms**: PAL clink (with role), consult tool, convene tool, clock_in. **Planned**: dispatch_colleague (workbench), enhanced consult with identity injection.

**Key gap**: Currently, clink sends a role name to an external CLI which loads its OWN copy of the system prompt. The colleague path should inject SHANK + ARM from the SAME library the formal path uses — this is where unification happens.

### Path 3: DEBATE Loading (Cognitive Lens — "The Debate")

**What it is**: Agents loaded purely for multi-perspective analysis. Identity is the COGNITION (Wind/Wall/Door), not the full agent file. ARM becomes the debate TOPIC. FLUKES aren't relevant beyond debate methodology.

**KEAPH mapping**:

| KEAPH | What's Loaded | How |
|---|---|---|
| **K**nowledge | Skipped | — |
| **E**stablish | SEA (possibly) — constitutional grounding optional | Injected if needed |
| **A**bsorb | SHANK (Cognition ONLY) — PATHOS/ETHOS/LOGOS kernel | Hardcoded prompts currently |
| **P**rocess | ARM = debate topic + prior turns | Injected per turn |
| **H**armonise | Debate methodology skill only | Embedded in prompt |

**Total cost**: ~2-3k tokens per agent per turn.

**When to use**: Governance hall debates, multi-perspective analysis, architectural decisions. When you need cognitive DIVERSITY (different thinking styles) applied to a shared problem. D2 exploration, B3 REINTEGRATE pipeline, architectural tension resolution.

**Current mechanisms**: run_debate (auto-orchestration), Wind/Wall/Door hardcoded prompts, debate-hall consult/convene.

**Key gap**: Debate prompts are currently hardcoded. They should pull from the SAME cognition library files (logos.oct.md, ethos.oct.md, pathos.oct.md) so any improvement to cognition definitions propagates to debates automatically.

### The Unification Principle

All three paths draw from the same component library:

```
LIBRARY (Single Source of Truth)
├── cognitions/          ← SHANK source for all 3 paths
│   ├── logos.oct.md
│   ├── ethos.oct.md
│   └── pathos.oct.md
├── agents/              ← Full identity for Formal path, SHANK extraction for Colleague
│   ├── implementation-lead.oct.md
│   ├── critical-engineer.oct.md
│   └── ...
├── skills/              ← FLUKES source for Formal + Colleague paths
│   ├── build-execution/
│   ├── constitutional-enforcement/
│   └── ...
└── constitution/        ← SEA source for all 3 paths
    └── CONSTITUTION.md
```

**What changes per path is not WHAT is loaded but HOW MUCH and HOW**:

| Component | Formal | Colleague | Debate |
|---|---|---|---|
| **Constitution (SEA)** | Full, proven | Injected | Optional |
| **Identity (SHANK)** | Full agent file, proven | Injected (agent file extract) | Cognition file only |
| **Context (ARM)** | Full PROJECT-CONTEXT + git state | Task-scoped context | Debate topic + prior turns |
| **Skills (FLUKES)** | Dynamic from anchor kernel | Task-specific skill | Debate methodology only |
| **Proof required?** | Yes — 4-stage interrogation | No — injected on trust | No — stateless |
| **Token cost** | 10-15k | 3-5k | 2-3k per turn |
| **Session persistence** | Full session (permit) | Ephemeral (response) | Turn-by-turn |

### Loading Path × Workflow Phase Matrix

| Phase | Primary Loading Path | Secondary | Why |
|---|---|---|---|
| **D0 ORIENT** | None (human) | — | Human selects tier and entry. No agent loaded. |
| **D1 UNDERSTAND** | T1: None. T2: Colleague. T3: Debate. | Formal (if starting fresh session) | T1 is self-directed. T2 consults for research. T3 runs debates for exploration. |
| **D2 EXPLORE** | T1: Colleague. T2-T3: Debate. | Formal (if exploring within a bound session) | Exploration is debate territory — Wind/Wall/Door shine here. |
| **D3 ARCHITECT** | T1: Colleague. T2-T3: Formal. | Debate (for architectural tensions) | Architecture needs full context (ARM). Formal loading provides it. |
| **B0 VALIDATE** | T1: Colleague (quick consult). T2-T3: Formal or Debate. | — | Quick consults for T1. Formal CE review for T3. Debate for contested decisions. |
| **B1 PLAN** | T1: None (self-plan). T2-T3: Formal. | Colleague (task decomposer consult) | Planning needs project context → formal loading. |
| **B2 BUILD** | Formal (IL bound for session). | Colleague (TMG, CRS, CE reviews). | Builder is formally loaded. Reviewers are colleagues dispatched per PR. |
| **B3 REINTEGRATE** | Colleague pipeline (3-step). | Debate (if complex reflection needed). | Headless pipeline — each step is a lightweight colleague dispatch. |

### Key Gaps to Close

1. **Colleague path needs library unification**: PAL clink currently uses its own system prompts. It should inject SHANK from the same library.
2. **Debate path needs cognition file loading**: Debate prompts are hardcoded. They should pull from `library/cognitions/*.oct.md`.
3. **dispatch_colleague needs implementation**: Workbench plans this as the colleague loading mechanism — it should implement the SEA+SHANK+ARM+Skill injection pattern.
4. **Micro-KEAPH for Living Harmonise**: When an agent hits a blocker mid-phase and needs to rebind skills, this is a colleague-weight reload within a formal session. The mechanism doesn't exist yet.

---

## Part 11: Historical Library Patterns (What Worked Before)

Five distinct library architectures were attempted over a year. Key patterns to carry forward:

### The Evolution

| Version | Structure | Key Innovation | Outcome |
|---|---|---|---|
| **Original Library** | 01-foundation / 02-cognitions / 03-contexts / 04-capabilities | ARM files as phase context; rich SHANK files (47 lines with NATURE block) | Clean separation, proven concept |
| **New Library** | Same but 03-archetypes replaced 03-contexts | Archetype database + weaving promoted to own layer | ARM files dropped — loss of phase context |
| **OCTAVE-AP** | Pattern inheritance engine | 30-line role defs INHERIT patterns, expand to 100-150 lines. Constitutional foundation +39% performance. | Proved composition works, but fragmented |
| **OCTAVE-AP-2** | 3 cognitive-cores + N capability-modules | "Matrix loading" — complete job modules like Neo downloading kung fu. 3 cores + N modules. 90-120 lines. | Simplest model. Closest to current. |
| **Role Factory** | lib:// URI aliases + weaving order | Scope Activation (archetypes scale with tier), Phase Hooks (outputs to phases), Weaving Assertions | Most sophisticated. Never finished. |

### Patterns to Carry Forward

**1. ARM Files as Phase Context (Original Library)**
The original `build-arm.oct.md` defined how cognition BEHAVES in build context — including COGNITIVE_ADAPTATION per cognition type (how LOGOS/ETHOS/PATHOS emphasis shifts per phase). This IS the "phase payload" concept from our debates. We should revive this.

**2. Richer Cognition Format (Original SHANKs)**
Our current cognition files (35 lines) are lean kernels. The originals had: NATURE block (PRIME_DIRECTIVE, CORE_GIFT, PHILOSOPHY, TRUTH_DEFINITION), 6-item MUST_ALWAYS/MUST_NEVER, and OPERATIONAL_NOTES. Question: should we enrich our current cognitions, or keep them lean and let agent files carry the depth?

**3. Scope Activation (Role Factory)**
Archetypes and capabilities scale with scope tier: SIMPLE gets 2 archetypes, COMPLEX gets 5. Maps directly to our T1/T2/T3 tiering — T1 loads minimal, T3 loads full capability set.

**4. Weaving Order (Role Factory)**
Composition sequence: FOUNDATION → COGNITION → ENHANCEMENTS → CAPABILITIES → OUTPUT → OVERRIDES. This IS our KEAPH order: SEA → SHANK → ARM → FLUKES. The Role Factory already discovered this independently.

**5. Phase Hooks (Role Factory)**
Agent outputs attach to specific workflow phases — IMPLEMENTATION_PATH goes to D2 design docs, FINDINGS_WITH_FLAGS goes to B2 build reports. We need this for traceability.

**6. Complete Capability Modules (OCTAVE-AP-2)**
3 immutable cognitive cores + N complete job modules. Each module contains everything for that specific job. This is the "formal loading" path: the agent file IS the capability module.

### The Unified Library Model (Proposed)

Drawing from all five approaches, the library should contain:

```
library/
├── constitution/          ← SEA (loaded by all 3 paths)
│   └── CONSTITUTION.md
├── cognitions/            ← SHANK (loaded by all 3 paths) — 35-line lean kernels + CRAFT
│   ├── logos.oct.md
│   ├── ethos.oct.md
│   └── pathos.oct.md
├── agents/                ← Full identity (Formal path loads full; Colleague extracts)
│   ├── implementation-lead.oct.md
│   ├── critical-engineer.oct.md
│   └── ...
├── phases/                ← ARM / Phase Context (NEW — revived from original library)
│   ├── d1-understand.oct.md
│   ├── d2-explore.oct.md
│   ├── d3-architect.oct.md
│   ├── b0-validate.oct.md
│   ├── b1-plan.oct.md
│   └── b2-build.oct.md
└── skills/                ← FLUKES (loaded on-demand by Formal + Colleague paths)
    ├── build-execution/
    ├── constitutional-enforcement/
    └── ...
```

**Key structural changes from current:**
- **phases/ directory is NEW** — revives ARM files as phase context payloads. Each phase file defines how cognitions behave in that phase, what deliverables are expected, and what exit criteria apply.
- **agents/ remain** but potentially slimmer — identity + cognition + authority + triggers. Capability details move to skills loaded at Harmonise.
- **cognitions/ stay LEAN** — 35-line execution kernels. CRAFT line added. No schema inflation. (Decision locked below.)
- **skills/ unchanged** — on-demand loading via anchor ceremony.

### RESOLVED: Lean Kernels Stay Lean (Decision Locked)

**Question**: Should we enrich current cognitions (35 lines) back to original richness (47 lines with NATURE block including CORE_GIFT, PHILOSOPHY, TRUTH_DEFINITION)?

**Answer**: **No. Protect the 35-line execution kernels fiercely.**

**Reasoning**:
1. **Prose dilutes constraints.** `PHILOSOPHY::"Constraints create excellence"` is passive narrative flavor. `THINK::["Assume failure is default until proven otherwise"]` is an executable instruction for token generation. The old NATURE blocks were translated into enforceable operational constraints — the depth wasn't lost, it was ACTIVATED.
2. **The anchor ceremony only extracts** `FORCE, ESSENCE, ELEMENT, MODE, PRIME_DIRECTIVE, THINK, THINK_NEVER`. Adding TRUTH_DEFINITION or CORE_GIFT back creates dead tokens — they take up space but never enter the agent's active cognitive proof.
3. **Empirical evidence** (Part 2 of this proposal): "optimized, focused cognitive definitions produce measurable performance improvements." LOGOS optimized achieved 8/8 vs other variants.
4. **Enrich the arrays, don't inflate the schema.** If a specific behaviour from the old SHANKs is missing (like ETHOS's brutal honesty), port it directly into THINK or THINK_NEVER as a strict command.

**The CRAFT field** (now implemented in v2.2.0 cognition files):
- LOGOS: `CRAFT::"Map the total structural dependencies before executing the minimal intervention."`
- ETHOS: `CRAFT::"Stress the limits to failure before endorsing the structural foundation."`
- PATHOS: `CRAFT::"Push the option space sideways before driving a single direction forward."`

**Implementation note**: CRAFT is now part of the cognition schema (v2.2.0). The anchor ceremony extraction list will be updated to include CRAFT alongside PRIME_DIRECTIVE when the ceremony is rebuilt — the current anchor does not yet extract CRAFT. Old SHANK behaviours have been rescued into THINK/THINK_NEVER arrays in the current cognition files.

### RESOLVED: Scope Activation Lives in Agent File (Decision Locked)

**Question**: Should scope activation (archetypes scaling with tier) be in the agent file or the phase file?

**Answer**: **Agent file.** Tier-based archetype scaling is identity-specific.

**Reasoning**: If scope activation lives in the phase file, every agent at T3 gets the same capability boost. But a critical-engineer (ETHOS) scaling to T3 needs entirely different archetypes than an ideator (PATHOS) at T3. The agent knows its own identity; the phase knows the environment. Archetype scaling belongs with identity.

**Separation of concerns**:
- **Archetype scaling per tier** → Agent file (identity-specific, lightweight)
- **Skill loading per tier** → Dynamic at anchor time (prevents phantom skill references)
- **Phase context** → Phase file (environment-specific, shared across agents)

This means the agent file declares WHICH archetypes activate at which tier, but does NOT pre-declare skills. Skills resolve dynamically via the anchor ceremony based on (agent identity + phase context + task topic).

### RESOLVED: Direct File Paths, Not lib:// URIs (Decision Locked)

**Question**: Should we use lib:// URI aliases (Role Factory pattern) or direct file paths?

**Answer**: **Direct file paths (relative to repo root).**

**Reasoning**:
1. **LLM native compatibility** — LLMs can read `.hestai-sys/library/cognitions/logos.oct.md` and use read_file tools autonomously. Custom URIs need resolver engines.
2. **No routing table maintenance** — lib:// URIs require a brittle indirection layer mapping aliases to real paths.
3. **"The Filesystem is the API"** — Direct paths keep the system transparent and browsable by both humans and AIs.
4. **The Role Factory was never finished** — precisely because building a custom URI resolver was a massive distraction from doing the actual work.

### Library Structure (LOCKED)

```
.hestai-sys/library/
├── constitution/     ← CONSTITUTION.md (SEA — loaded by all 3 paths)
├── cognitions/       ← logos, ethos, pathos (SHANK — 35-line lean kernels + CRAFT)
├── phases/           ← d1-understand, d2-explore, etc. (ARM — phase context payloads)
├── agents/           ← identity files (archetype scaling per tier, no pre-declared skills)
├── skills/           ← procedural capabilities (FLUKES — HOW to do the job)
└── patterns/         ← principle capabilities (FLUKES — HOW to constrain the job)
```

**Skills vs Patterns** (both load at Harmonise/FLUKES stage):
- **Skills** = procedures ("do these steps") — e.g., build-execution, agent-interview, error-triage
- **Patterns** = principles ("apply this lens while working") — e.g., tdd-discipline, mip-build, verification-protocols

An agent doing build work loads `build-execution` (skill: what steps) + `tdd-discipline` (pattern: what discipline) + `mip-build` (pattern: what principle). Skills tell it WHAT to do; patterns tell it HOW to think while doing it.

**All decisions locked. Validated by HO analysis + independent external assessment (Gemini via workbench).**

### RESOLVED: The Fulcrum Anchorage — Anchor Ceremony Redesign (Decision Locked)

**Decision record**: `docs/decisions/2026-03-22-anchor-ceremony-redesign.oct.md`
**Debate verdict**: SUBTRACTIVE_HYBRID — "Applied Cognitive Grammar"

The 6-step cognitive loading sequence maps to the 4-stage anchor ceremony via Semantic Stacking:

```
COGNITIVE STACK              ANCHOR STAGE           MECHANISM
1. cognitions/ (BIOS)     → REQUEST (loads)    +   Cognition delivered as pointer
2. constitution/ (Laws)   → SEA (proves)           Agent proves Constitution THROUGH
                                                    cognitive grammar. Cannot fake it.
3. agents/ (Ego)          → SHANK (proves)         Agent cites MISSION + AUTHORITY
4. phases/ (Environment)  → ARM (proves)           Agent maps phase + tension
5. patterns/ (Principles) → FLUKES (proves)        Agent declares what it will use
6. skills/ (Tools)        → FLUKES (bundled)       Patterns + Skills both at FLUKES
```

**The key innovation — Applied Cognitive Grammar (TARGET-STATE)**: At SEA stage, the agent will format its Constitution proof strictly through its Cognitive lens. LOGOS must output `[TENSION] → [INSIGHT] → [SYNTHESIS]`. ETHOS must output `[VERDICT] → [EVIDENCE]`. If the cognition file wasn't absorbed, the agent won't know the syntax. Server will regex-validate the framing when the ceremony is rebuilt. Targets anti-theater through mechanism, not trust.

**LLM Attention Physics**:
- **Primacy** (Stages 0-1): Cognition + Constitution load first → heaviest conditioning weight
- **Middle** (Stages 2-3): Identity + Context → attention sag safe (self-anchoring concepts)
- **Recency** (Stage 4): Patterns + Skills load last → dominates immediate action selection

**Three-Path Support**:

| Path | Flow | Permit | Components |
|---|---|---|---|
| **Formal** | request → sea → shank → arm → flukes | FULL_PERMIT | All 6 loaded and proven |
| **Colleague** | anchor_micro() | MICRO_PERMIT | Cognition + Identity injected (no proof) |
| **Debate** | request → sea (early-exit) | DEBATE_PERMIT | Cognition + Constitution + Identity only |

**Implementation note**: Server needs cognition MUST_USE grammar loaded server-side at REQUEST time to validate at SEA time. Role → agent file → COGNITION type → load regex patterns into session state. This is an odyssean-anchor-mcp change.

**Colleague path**: Yes, inject cognition (agent still needs to THINK correctly). Skip proof (speed over ceremony). Workbench injects cognition file content alongside identity before API call.

**Debate path**: Halts at SHANK. Debate agents need Cognition (how to think) + Identity (who they are). No ARM (no filesystem). No FLUKES (debate methodology embedded). `early_exit=shank` issues DEBATE_PERMIT.

---

*Next step: map cognitive types per phase to actual agent roles, then determine final roster.*

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
