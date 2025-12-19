<!-- HestAI-Doc-Steward: consulted for document-creation-and-placement -->
<!-- Approved: HDS-2025-12-05 [constitutional-governance] [multi-model-consensus] [zero-redundancy] -->
<!-- Relationship: COMPLEMENT to 001-WORKFLOW-NORTH-STAR.oct.md (constitutional→operational hierarchy) -->
<!-- Note: This is the foundational System North Star. All other workflow documents must satisfy these immutables. -->

# HESTAI SYSTEM NORTH STAR

**Version:** 1.0
**Status:** APPROVED
**Approval Date:** 2025-12-05
**Approved By:** Shaun Buswell (Human Primacy Authority)
**Validation:** Multi-model consensus (Codex GO + Gemini GO)

---

## COMMITMENT STATEMENT

This document represents the immutable requirements for HestAI. All work must align with these requirements. Any detected misalignment will trigger escalation. Changes to immutables require formal amendment process via requirements-steward.

**Authority:** This North Star was extracted through the full Immutability Funnel (HERMES → PSYCHE → APOLLO), pressure-tested via What-If Gauntlet, crystallized via Immutability Oath, and validated by multi-model consensus.

**Relationship to 001-WORKFLOW-NORTH-STAR:** This document establishes constitutional principles that 001-WORKFLOW-NORTH-STAR.oct.md must satisfy. This is the "WHAT cannot change"; 001 is the "HOW it works operationally."

---

## SECTION 1: THE UNCHANGEABLES (6 Immutables)

### I1: VERIFIABLE BEHAVIORAL SPECIFICATION FIRST (TDD Discipline)

**PRINCIPLE (Technology-Neutral):**
> Behavioral specification must exist before implementation. The specification must be verifiable. Deviation from specification-first requires explicit documented justification.

**CURRENT BINDING IMPLEMENTATION:**
- Verifiable specification = executable test
- TDD discipline: RED (failing test) → GREEN (minimal pass) → REFACTOR
- Git evidence: TEST commits precede FEAT commits
- "Mental verification" or "type safety alone" are NOT acceptable justifications

**Evolution of this implementation requires formal amendment.**

**Rationale:** "Done right the first time IS faster." Trivial exceptions accumulate into systemic drift.

**Validation Criteria:** Git evidence shows TEST commits before FEAT commits, OR explicit justification documented in DECISIONS.md with accountability owner.

---

### I2: PHASE-GATED PROGRESSION

**PRINCIPLE (Technology-Neutral):**
> Work progresses through defined stages: understanding, validation, execution, confirmation. Stages may compress to single statements for simple work but cannot be omitted. Evidence of stage completion is required.

**Rationale:** "A circle design validated in one sentence is still D1→B0→B2." The gate exists; the ceremony adapts. Skipping validation pays 5x in rework.

**Validation Criteria:** Every completed work item has evidence of: (1) what was intended, (2) that it could work, (3) that it was built, (4) that it's done.

---

### I3: HUMAN PRIMACY

**PRINCIPLE (Technology-Neutral):**
> Human judgment determines direction and retains override authority. Automated systems advise, recommend, and execute; they do not autonomously decide strategic direction.

**Rationale:** AI presents cases and convinces; humans decide. Capability in one domain doesn't transfer to all domains.

**Validation Criteria:** Every strategic decision has human approval documented. AI recommendations are labeled as recommendations.

---

### I4: DISCOVERABLE ARTIFACT PERSISTENCE

**PRINCIPLE (Technology-Neutral):**
> Work produces persistent, addressable, and discoverable records enabling communication across time and team boundaries. Records must survive session termination and be accessible to future participants.

**BINDING IMPLEMENTATION:**
- "If it isn't written and addressable, it didn't happen"
- Artifacts must be located in predictable, accessible paths
- Format is flexible; persistence AND discoverability are required

**Rationale:** Addressability solves the reference problem. Discoverability solves the transparency problem. A system with perfect persistence but 50% discoverability is 50% broken.

**Validation Criteria:** After any session, a new participant can locate and understand what happened without asking the original participant.

---

### I5: QUALITY VERIFICATION BEFORE PROGRESSION

**PRINCIPLE (Technology-Neutral):**
> Quality must be verified before work progresses to next stage. Verification may be automated, manual, or hybrid. Verification must block progression when quality criteria are not met.

**INTERPRETIVE CLAUSE:**
> Quality verification includes enforcement of constitutional controls (tests, gates, RACI evidence) and blocks progression if any control is bypassed.

**Rationale:** Gates block, not warn. The mechanism may evolve; the blocking behavior is constant.

**Validation Criteria:** No work progresses to next stage without documented verification passing.

---

### I6: EXPLICIT ACCOUNTABILITY

**PRINCIPLE (Technology-Neutral):**
> Every decision has identifiable, traceable accountability. When asked "who is responsible for this decision?" there must be a clear answer. Accountability may be individual or collective, but must be explicit.

**Rationale:** Distributed responsibility equals no responsibility. The failure mode to prevent is "no one is responsible," not "more than one is responsible."

**Validation Criteria:** Every decision in DECISIONS.md has an owner field. Orphan decisions trigger escalation.

---

## SECTION 2: CONSTRAINED VARIABLES

### V1: GOVERNANCE ENVELOPE

**Definition:** The specific mechanisms, meetings, and tracking tools used to manage work.

**Inviolable Constraints:** Mechanisms may evolve, but must always satisfy:
- **I2** (Explicit Phasing) — Gate evidence required
- **I5** (Blocking Verification) — Quality checks must block
- **I6** (Explicit Accountability) — Ownership records required

**Anti-Drift Clause:** Under pressure, ceremony density may decrease, but **Gate Evidence** and **Accountability Records** cannot be omitted. Erosion of these elements constitutes violation of I2, I5, and I6.

**Rationale:** Governance is mechanism, not truth. Success criterion is "does the built thing work properly," not "did we follow the process." But minimum ceremonies are constitutionally protected.

---

### Other Constrained Variables

| Area | Immutable Aspect | Flexible Aspect | Negotiable Aspect |
|------|------------------|-----------------|-------------------|
| **Ceremony Intensity** | Phases exist (I2) | Duration per phase | Specific artifacts |
| **Documentation Depth** | Discoverable persistence (I4) | Format and length | Storage location |
| **Model Implementation** | Governance applies | Which AI provider | Specific model versions |
| **Agent Architecture** | Constitutional binding | Number of agents | Specific role definitions |
| **Coordination Structure** | Accountability required (I6) | RACI vs other models | Role naming conventions |

---

## SECTION 3: ARCHITECTURAL FOUNDATIONS

These are definitional elements of what HestAI IS, not assumptions to validate:

### Cognitive Lenses (ETHOS / LOGOS / PATHOS)

Agents operate through one of three cognitive modes that shape reasoning approach:
- **ETHOS** — Boundary validation, constraint enforcement, integrity focus
- **LOGOS** — Relational synthesis, structural coherence, systematic analysis
- **PATHOS** — Possibility exploration, empathetic understanding, creative expansion

### Archetypes (Greek Mythology)

Mythological elements enhance semantic binding:
- Archetypes (HERMES, APOLLO, ATHENA, etc.) encode behavioral patterns
- Mythological naming creates consistent mental models across sessions

### OCTAVE (Domain-Specific Language)

HestAI's compressed notation system:
- Semantic compression achieving 60-80% token reduction
- Structured syntax for machine-parseable governance
- Enables efficient transmission across context boundaries

---

## SECTION 4: BOUNDARY CLARITY

### What HestAI IS

- A governance envelope for AI-assisted development
- A design-and-build system with mandatory quality gates
- A coordination methodology spanning D0→B4 phases
- A constitutional framework binding agent behavior
- A bridge between "vibe coding" and reliable AI-assisted development

### What HestAI is NOT

- NOT a commercial product (currently personal productivity tool)
- NOT multi-team coordination (single developer + AI agents, scaling is assumption A1)
- NOT model-specific (Claude preferred for ethics, not required)
- NOT a library of agents (governance system, not capability collection)
- NOT bureaucratic overhead (streamlined governance, not red tape)
- NOT a replacement for human judgment on problem selection (HestAI governs HOW to build; humans determine WHAT to build)

---

## SECTION 5: ASSUMPTION REGISTER

| ID | Assumption | Confidence | Impact | Priority |
|----|------------|------------|--------|----------|
| A0 | This methodology produces better North Stars | 70% | LOW | Post-cycle |
| A1 | Multi-agent coordination scales | 70% | CRITICAL | **Before B0** |
| A2 | Constitutional binding affects behavior | 75% | HIGH | Quarterly |
| A3 | Single developer can maintain system | 85% | MEDIUM | Monthly |
| A4 | OCTAVE compression preserves meaning | 65% | HIGH | **Before B0** |
| A5 | Phase gates add more value than overhead | 80% | MEDIUM | Per-project |
| A6 | AI model capabilities remain sufficient | 90% | CRITICAL | Quarterly |
| A7 | Artifact discoverability works | 50% | HIGH | **IMMEDIATE** |
| A8 | TDD discipline improves AI code quality | 85% | MEDIUM | Milestone |
| A9 | Cognitive lenses map to real distinctions | 60% | MEDIUM | Before new agents |
| A10 | Quality gates catch real defects | 80% | MEDIUM | Per-release |

**Critical Validation Required:** A1, A4, A7 (before B0)

---

## SECTION 6: EVIDENCE SUMMARY

| Metric | Value |
|--------|-------|
| Total Immutables | 6 (within 5-9 range) |
| Pressure Tested | 7/7 passed What-If Gauntlet |
| System-Agnostic | 6/6 passed Technology Change Test |
| Assumptions Tracked | 11 (exceeds 6 minimum) |
| Critical Assumptions | 3 requiring pre-B0 validation |
| Multi-Model Validation | Codex GO + Gemini GO |
| Consensus Amendments | 2 (I4 discoverability + V1 anti-drift clause) |

---

## SECTION 7: PROTECTION CLAUSE

If ANY agent detects misalignment between work and this North Star:

1. **STOP** current work immediately
2. **CITE** specific North Star requirement being violated
3. **ESCALATE** to requirements-steward for resolution

**Options:** CONFORM to North Star | USER AMENDS (rare, formal process) | ABANDON incompatible path

---

## COMMITMENT CEREMONY RECORD

**Ceremony Conducted:** 2025-12-05
**Methodology:** Full Immutability Funnel (HERMES → PSYCHE → APOLLO)
**Pressure Testing:** What-If Gauntlet (5 scenarios, all passed)
**Crystallization:** Immutability Oath (3 questions per candidate)
**Translation:** Technology Change Test (all 6 passed)
**Validation:** Multi-model consensus (Codex + Gemini ho-liaison)

**The Oath (Administered):**
> "These are your North Star. If you approve, I commit to defending them throughout HestAI's development. Future-you may want to change these, but present-you is making a commitment to future-you."

**Response:** APPROVED

**Binding Authority:** This North Star now governs all HestAI development. Misalignment triggers Protection Clause. Amendment requires formal process.

---

<!-- Constitutional Authority: north-star-architect (PATHOS cognition) -->
<!-- Approval Authority: Human (I3 Human Primacy) -->
<!-- Validation: Multi-model consensus (Codex + Gemini) -->
<!-- Date: 2025-12-05 -->
<!-- SUBAGENT_AUTHORITY: hestai-doc-steward 2025-12-05T18:43:21+11:00 -->
