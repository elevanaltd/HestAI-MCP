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

**Proposal**: Reduce from 31 agents to **12 core agents + 3 domain specialists** = **15 total**.

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
7. **RAPH pipeline heritage** — READ→ABSORB→PERCEIVE→HARMONIZE as cognitive processing model

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

### The 12 Core Agents

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

#### 6. DESIGN ARCHITECT (LOGOS) — Keep, refined
**Why it exists**: Translates validated requirements into technical blueprints (D3).
**Cognition**: LOGOS — synthesis of constraints into architecture.
**Authority**: ULTIMATE over D3 specifications.
**Triggers**: D3 phase — blueprint creation, technical architecture, visual design.
**Relationships**: Receives from D2 synthesis. Sends to B0 validation.
**Core skills**: None beyond cognition — skills loaded on-demand.
**What changed**: Absorbs technical-architect's validation duties and visual-architect's design work. One architect for all design, not three.

#### 7. UNIVERSAL TEST ENGINEER (ETHOS) — Keep, essential
**Why it exists**: Writes tests. The only agent that generates test code.
**Cognition**: ETHOS — validation mindset essential for testing.
**Authority**: BLOCKING — test coverage and methodology.
**Triggers**: Test strategy (B2_00), test suite creation (B2_02), integration testing (B3_02).
**Relationships**: Works alongside implementation-lead. Consulted by code-review.
**Core skills**: test-generation (to be created)
**What changed**: Consolidates universal-test-engineer + test-methodology-guardian + test-infrastructure-steward into ONE testing agent. Three testing agents for a solo developer is over-engineering. One agent with testing discipline.

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

### The 3 Domain Specialists

#### 13. SUPABASE EXPERT (LOGOS) — Conditional
**Why it exists**: Database schema governance, RLS optimization, migration safety.
**Authority**: BLOCKING on schema changes.
**When to keep**: Only if the project actively uses Supabase.

#### 14. SMARTSUITE EXPERT (LOGOS) — Conditional
**Why it exists**: SmartSuite API field format validation, UUID corruption prevention.
**Authority**: BLOCKING on SmartSuite operations.
**When to keep**: Only if the project actively uses SmartSuite.

#### 15. OCTAVE SPECIALIST (LOGOS) — Keep, essential
**Why it exists**: Authority on OCTAVE format specification. No other agent can adjudicate OCTAVE questions.
**Authority**: ULTIMATE on OCTAVE spec interpretation.
**Triggers**: OCTAVE format questions, compression decisions, schema validation.

### Agents REMOVED (16 agents cut)

| Removed Agent | Reason | Where Its Work Goes |
|---|---|---|
| **validator** | Profile of ETHOS cognition, not distinct identity | Critical-engineer handles validation |
| **synthesizer** | Profile of LOGOS cognition, not distinct identity | Implementation-lead or design-architect synthesize |
| **principal-engineer** | Overlaps with critical-engineer (strategic vs tactical) | Critical-engineer does both — solo dev doesn't need two levels |
| **quality-observer** | Overlaps with code-review-specialist and critical-engineer | Code-review handles quality metrics |
| **security-specialist** | Skill, not agent — security checks are a skill loaded on-demand | Security becomes a skill loaded by critical-engineer or code-review |
| **edge-optimizer** | Profile of PATHOS cognition — advisory-only exploration | Ideator covers exploratory thinking |
| **completion-architect** | B3 integration is implementation-lead's responsibility | Implementation-lead handles integration |
| **solution-steward** | B4 delivery is system-steward's responsibility | System-steward handles documentation and handoff |
| **ho-liaison** | Advisory analysis for HO — but HO should think for itself | HO uses Explore agents directly instead of a dedicated liaison |
| **north-star-architect** | D0 extraction is requirements-steward's responsibility | Requirements-steward handles North Star creation |
| **visual-architect** | Skill, not agent — visual design is loaded on-demand | Design-architect loads visual skills when needed |
| **error-architect** | Skill, not agent — error triage is a methodology | Implementation-lead loads error-triage skill |
| **complexity-guard** | Profile of ETHOS cognition — complexity checking is a skill | Critical-engineer or code-review check complexity |
| **test-methodology-guardian** | Overlaps with universal-test-engineer | Universal-test-engineer guards its own methodology |
| **test-infrastructure-steward** | Overlaps with universal-test-engineer | Universal-test-engineer manages test infrastructure |
| **technical-architect** | Overlaps with design-architect | Design-architect handles both design and technical validation |

### The MIP Test Results

For each removed agent, the MIP question: "What specific capability would be lost?"

- **validator**: Nothing — critical-engineer and code-review already validate
- **synthesizer**: Nothing — LOGOS cognition IS synthesis; any LOGOS agent synthesizes
- **principal-engineer**: Strategic perspective — but a solo dev IS the principal engineer
- **quality-observer**: Metrics observation — but code-review already produces metrics
- **security-specialist**: Security depth — preserved as a SKILL, not an agent
- **edge-optimizer**: Boundary exploration — ideator already explores possibilities
- **completion-architect**: Integration authority — implementation-lead integrates what it builds
- **solution-steward**: Delivery docs — system-steward handles documentation
- **ho-liaison**: Deep analysis — HO uses Explore subagents for analysis
- **north-star-architect**: Immutable extraction — requirements-steward extracts AND validates
- **visual-architect**: Visual design — design-architect loads visual skills
- **error-architect**: Error triage — implementation-lead loads error-triage skill
- **complexity-guard**: Complexity gate — code-review checks complexity
- **test-methodology-guardian**: Test integrity — universal-test-engineer self-guards
- **test-infrastructure-steward**: CI integrity — universal-test-engineer manages its infra
- **technical-architect**: Architecture validation — design-architect validates its own work

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

### Phase-Agent Mapping (Updated)

| Phase | Agent | Role |
|---|---|---|
| D0 | requirements-steward | Ideation + graduation |
| D1 | requirements-steward | Understanding + North Star |
| D2 | ideator + requirements-steward | Ideation + validation |
| D3 | design-architect | Blueprint |
| B0 | critical-engineer | GO/NO-GO gate |
| B1 | task-decomposer | Build plan |
| B2 | implementation-lead + universal-test-engineer + code-review-specialist | Build + test + review |
| B3 | implementation-lead + critical-engineer | Integration + validation |
| B4 | system-steward + critical-engineer | Delivery + signoff |
| B5 | requirements-steward + implementation-lead | Enhancement |

### Debate Hall Integration
- **Wind (PATHOS)**: ideator
- **Wall (ETHOS)**: critical-engineer
- **Door (LOGOS)**: design-architect or implementation-lead (context-dependent)

---

## Part 7: Migration Strategy

### Approach: Gradual Replacement, Not Big Bang

1. **Phase 1**: Create the 15 dream team agent files as v9.0.0
2. **Phase 2**: Update workflow mapping to reference new agents
3. **Phase 3**: Create missing skills (review-discipline, test-generation, security-analysis)
4. **Phase 4**: Update oa-router to recognize new agent set
5. **Phase 5**: Archive removed agent files (don't delete — move to _archive/)
6. **Phase 6**: Update Constitution with philosophy section
7. **Phase 7**: Update cognitions with CRAFT line

### Risk Mitigation
- Removed agents are ARCHIVED, not deleted — can be restored
- Each phase is independently testable
- Existing skills remain — only agent routing changes
- Constitution changes are additive, not destructive

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
**12 core + 3 domain specialists = 15.** Every iteration in the evolution reduced count while increasing depth. 31 was regression.

### Which current agents are profiles of a shared identity?
- **validator** = ETHOS profile (critical-engineer already validates)
- **synthesizer** = LOGOS profile (any LOGOS agent synthesizes)
- **edge-optimizer** = PATHOS profile (ideator already explores)
- **complexity-guard** = ETHOS profile (code-review checks complexity)
- **quality-observer** = ETHOS profile (code-review observes quality)

### What's missing that no current agent covers?
**Nothing critical is missing.** The current system over-provisions. The gap is not in coverage but in depth — agents are too shallow because identity is spread across 31 files.

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
| 2026 | **Dream Team** | **15** | **Evidence-based reduction** |

---

*"Preserve what sings; silence what clutters." — MIP*
