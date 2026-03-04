---
type: NORTH_STAR
id: ecosystem-north-star
version: 1.0
status: DRAFT
purpose: Target state vision for the fully integrated HestAI ecosystem
inherits: 000-SYSTEM-HESTAI-NORTH-STAR[methodology]
approved_by: PENDING
approval_date: PENDING
NAMESPACE::SYS
# // REFERENCE: points-to-canonical (.hestai-sys/ runtime-injected copy; this is the _bundled_hub source)
---

# HESTAI ECOSYSTEM NORTH STAR

**Version:** 1.0
**Status:** DRAFT
**Created:** 2026-02-25
**Origin:** Project 15 ecosystem build order coordination (Wind/Wall/Door debate + HO assessment)
**Tracking:** [GitHub Project 15](https://github.com/orgs/elevanaltd/projects/15)

---

## COMMITMENT STATEMENT

This document describes the **target state** of the HestAI ecosystem — what it looks like when fully integrated. It is not a build plan (that is the Project 15 board), not an overview of what exists today (that is HESTAI-ECOSYSTEM-OVERVIEW), and not a methodology (that is the System North Star). It is the destination.

Every repo, every issue, every architectural decision should move the ecosystem closer to this state. When something doesn't, it should be questioned.

**Relationship to other governance documents:**
- **System North Star (000-SYSTEM-HESTAI-NORTH-STAR):** Establishes HOW we build — immutable methodology (I1-I6). This document establishes WHAT we're building toward.
- **Constitution:** The absolute laws. This North Star operates within constitutional authority.
- **Product North Stars:** Per-repo vision. Each must align with this ecosystem vision.
- **ECOSYSTEM-OVERVIEW:** Describes the current state. This document describes the future state.

---

## SECTION 1: THE VISION

### What We're Building

A unified system where a single developer can orchestrate multiple AI agents across multiple providers and models, with installed governance that prevents the drift, hallucination, and quality collapse that plague unstructured AI-assisted development.

The system is not a single application. It is an ecosystem of five cooperating systems, each owning a distinct concern, connected by shared protocols and a common governance framework.

### The End State in One Paragraph

An operator opens the Workbench, picks a role from the agent registry, selects a provider and model, and starts working. The agent binds its identity through the anchor ceremony, loads its constitution and skills, and operates within its authority boundaries. When it needs a decision, it opens a structured debate. When it needs another perspective, the Workbench dispatches a different agent on a different model. All communication uses OCTAVE format. All sessions are persistent. All decisions are auditable. The operator sees the whole system through one GUI — the Workbench — and never needs to configure MCP servers, manage worktrees, or remember which agent does what.

---

## SECTION 2: THE THREE-REPO TARGET ARCHITECTURE

The ecosystem converges from the current six repos to three MCP servers plus a control panel:

### Layer 0: OCTAVE MCP — The Language

**What it is:** A pure semantic compression protocol with zero governance dependencies.

**What it owns:**
- OCTAVE format specification and grammar
- Validation (syntactic and semantic)
- Generation and compression
- Grammar compilation (GBNF export)

**What it does NOT own:** Governance, agent identity, deliberation, or execution.

**Key properties:**
- Maximum community adoption potential — useful without HestAI
- Foundation layer — all other systems speak OCTAVE
- No dependencies on anything else in the ecosystem

**Target state:** Published on PyPI. Standalone community tool. Grammar supports agent definition schemas including the Chassis-Profile capability tier model.

---

### Layer 1: HestAI Core MCP — The Operating System

**What it is:** The single source of truth for agent identity, governance, and context management.

**What it owns:**
- Agent constitutions and skills library (one canonical source — P2)
- Anchor ceremony (identity binding via progressive interrogation)
- Context stewardship (session lifecycle, clock in/out)
- Governance rules and enforcement
- Permit system (tiered: micro/quick/default/deep)
- Capability profiles (Chassis-Profile architecture for context-aware skill loading)

**What it absorbs:**
- Odyssean Anchor MCP (currently separate, merger per ADR-0275) — the binding protocol, Steward state machine, proof validation, and permit system are rebuilt natively inside HestAI Core
- Agent prompts from PAL MCP (61 clink role definitions consolidated as canonical source)

**What it does NOT own:** Deliberation (that's debate-hall), execution/UI (that's the Workbench), model dispatch (that's the Workbench), OCTAVE format (that's octave-mcp).

**Key properties:**
- Provider-agnostic — knows WHO agents are and HOW they should behave, not which model runs them
- Single canonical source for all agent definitions (no duplication across repos)
- Every agent interaction starts with anchor ceremony (identity verification before execution)

**Target state:** Single `pip install hestai-mcp` gives you governance + identity + anchor ceremony. No separate OA server. Agent constitutions with Chassis-Profile support. Tiered permits for ceremony weight proportional to task complexity.

---

### Layer 2: Debate Hall MCP — The Deliberation Chamber

**What it is:** Standalone multi-perspective reasoning engine with hash-chain integrity.

**What it owns:**
- Wind/Wall/Door structured debates
- Governance Hall (persistent committee spaces, expert consultations)
- RACI governance mode (Turn Manifest Compiler)
- Decision records with SHA-256 hash chain
- Consult and convene operations
- RFC ratification, human interjection

**What it does NOT own:** Agent identity (that's HestAI Core), UI rendering (that's the Workbench), the OCTAVE format (that's octave-mcp).

**Key properties:**
- Standalone — works without HestAI for non-governance users (P6)
- Persistent transcripts — decisions are auditable, append-only, hash-chained
- Advisory, not authoritative — humans decide, debate-hall presents structured perspectives

**Target state:** Full Governance Hall with persistent committee spaces. RACI mode for formal governance decisions. Decision search across all past debates. Headless — all UI through the Workbench.

---

### Layer 3: HestAI Workbench — The Control Panel

**What it is:** The only GUI in the ecosystem. Desktop application for managing AI sessions, agent dispatch, and system visibility.

**What it owns:**
- Agent registry (role → provider → model mapping, UI-configurable)
- CLI dispatch (spawning agents on different providers/models, absorbed from PAL clink)
- Session management (worktrees, terminal multiplexing, session persistence)
- Governance Chat UI (rendering debate-hall transcripts as conversation threads)
- System dashboard (visibility into all active sessions, agents, debates)

**What it absorbs:**
- PAL MCP Server — clink dispatch moves to Workbench, workflow tools replaced by proper agent loading via anchor, agent prompts consolidated to HestAI Core
- Crystal Fresh — the original fork from which the Workbench evolved

**What it does NOT own:** Agent identity (that's HestAI Core), deliberation logic (that's debate-hall), document format (that's octave-mcp).

**Key properties:**
- Only system with a GUI (P5) — debate-hall and HestAI Core are headless MCP servers
- Knows WHICH provider and model each agent runs on (separation from WHO the agent is)
- The convergence point — where identity, deliberation, format, and execution meet

**Target state:** Operator opens Workbench, picks a role from registry, picks a provider/model, and works. Governance Chat panel shows debates as threaded conversation. Agent dispatch handles multi-provider orchestration. Session persistence across worktrees. No configuration of MCP servers required by the operator.

---

## SECTION 3: THE DAILY WORKFLOW (TARGET STATE)

This is what the operator's daily experience looks like when the ecosystem is complete:

1. **Open the Workbench.** The dashboard shows active sessions, recent decisions, system health.

2. **Pick a task.** The operator selects work to do — could be a feature, a bug, an architectural decision.

3. **Pick a role.** The agent registry shows available roles (Holistic Orchestrator, Implementation Lead, Technical Architect, etc.) with their provider/model assignments. The operator selects one.

4. **Workbench spawns the agent.** It creates a git worktree, connects MCP servers, and launches the CLI for the selected provider/model.

5. **Agent binds identity.** The anchor ceremony runs automatically — the agent proves it comprehends its role, the Constitution, and the current project context. The appropriate capability profile loads (standard for repo-level work, ecosystem for cross-repo coordination, advisory for read-only analysis).

6. **Agent works.** It calls HestAI Core for skills and context. It uses OCTAVE format for all documents. It operates within its authority boundaries.

7. **Agent hits an ambiguous decision.** It calls debate-hall for a structured Wind/Wall/Door debate. The debate produces a synthesis with a decision record. The Governance Chat panel in the Workbench shows the debate as a conversation thread.

8. **Agent needs another perspective.** The Workbench dispatches a different agent on a different provider/model. The new agent binds its own identity via anchor ceremony. Both agents see the shared project context.

9. **Session ends.** HestAI Core archives the transcript in OCTAVE format. The decision record is hash-chained and searchable. The worktree preserves the work.

10. **Operator reviews.** The Workbench dashboard shows what was done, what decisions were made, and what's next. All artifacts are persistent and discoverable (I4).

---

## SECTION 4: ECOSYSTEM IMMUTABLES

These are the non-negotiable principles of the ecosystem architecture. They sit below the System North Star's methodological immutables (I1-I6) and above any individual Product North Star.

### E1: SEPARATION OF CONCERNS

Each system owns exactly one concern. Identity is not deliberation. Deliberation is not execution. Format is not governance. These boundaries are not convenience — they are structural load-bearing walls. Violating them creates coupling that compounds across the ecosystem.

**Binding:** HestAI Core owns WHO. Workbench owns WHERE and HOW. Debate Hall owns GOVERNANCE DECISIONS. OCTAVE owns WHAT FORMAT.

### E2: ONE CANONICAL SOURCE

Agent definitions exist in exactly one place: HestAI Core. Not duplicated in PAL, not copied to the Workbench, not embedded in debate-hall. When an agent's constitution changes, it changes in one file. Everything else references that source.

**Binding:** Agent prompts in HestAI Core's bundled hub. PAL clink references, not copies. Workbench registry points to Core, not local files.

### E3: PROVIDER AGNOSTICISM

The governance layer (HestAI Core) knows nothing about which AI model runs an agent. The execution layer (Workbench) knows nothing about what an agent's authority boundaries are. This separation means switching from Claude to Gemini for a role requires changing one registry entry, not modifying governance.

**Binding:** HestAI Core: role → constitution, skills, authority. Workbench: role → provider, model, CLI config.

### E4: STANDALONE DELIBERATION

Debate Hall works without HestAI. A team that doesn't use HestAI governance can still use Wind/Wall/Door debates for their own decisions. This is not a nice-to-have — it is the adoption path that makes the ecosystem viable beyond the original developer.

**Binding:** Debate Hall has zero dependencies on HestAI Core. Its only dependency is OCTAVE (Layer 0).

### E5: CEREMONY PROPORTIONAL TO RISK

Not every task needs a full 5-stage anchor ceremony. Trivial read-only tasks get a micro permit (1 call). Standard work gets the full ceremony. Critical production decisions get deep tier with extra tensions. The weight of governance is proportional to the risk of the work.

**Binding:** Tiered permit model (micro/quick/default/deep). Chassis-Profile architecture loads appropriate capability sets per context.

### E6: THE WORKBENCH IS THE ONLY GUI

MCP servers are headless. The Workbench is the surface. Any feature that needs a UI (debate visualization, agent management, session overview) lives in the Workbench, not as a separate desktop app.

**Binding:** debate-hall#112 becomes a Workbench panel. HestAI-MCP#38 becomes a Workbench panel. No standalone Electron apps per MCP server.

---

## SECTION 5: SUCCESS CRITERIA

The ecosystem is "done" when:

### Functional Criteria

1. **Single-command agent dispatch.** Operator picks role + provider/model → agent is running with full identity binding in under 30 seconds.

2. **Cross-repo agent invocation.** An HO agent in repo A can convene agents in repos B and C for a structured debate, each running on different providers/models.

3. **No duplicate agent definitions.** `grep -r` across all repos finds exactly one canonical definition per agent role, in HestAI Core.

4. **Governance Chat as conversation.** Debates are visible as threaded conversations in the Workbench, not raw JSON in a terminal.

5. **Session continuity.** An agent can be stopped and resumed with full context restoration. A different agent can pick up where the first left off.

6. **Decision audit trail.** Any past decision can be found via `search_decisions`, with the full debate transcript, hash-chain proof, and synthesis.

### Quality Criteria

7. **All repos green.** Tests passing, coverage above thresholds, linters clean, type checking strict.

8. **Three MCP servers, not six.** OA absorbed into HestAI Core. PAL absorbed into Workbench + Core. Crystal replaced by Workbench.

9. **The Workbench is daily-driveable.** The operator uses it for real work, not as a demo. 2 months of daily use before any rebuild.

### Adoption Criteria

10. **Debate Hall has external users.** At least one person outside HestAI uses debate-hall-mcp for their own decisions.

11. **OCTAVE has community traction.** Published, documented, adopted by at least one project outside HestAI.

12. **A new developer can onboard.** Someone who has never seen the system can go from zero to running their first agent-assisted session in under 30 minutes, using only the Workbench and documentation.

---

## SECTION 6: WHAT DOES NOT NEED TO BE BUILT

Knowing what we're NOT building is as important as knowing what we are:

1. **Multi-tenant SaaS.** This is a single-developer tool. Scaling to teams is assumption A1, not a build target.

2. **Custom model training.** We use off-the-shelf models from providers. The value is in governance, not model performance.

3. **Perfect orchestration.** The cross-repo agent invocation (Step 6 on the critical path) is explicitly a prototype. "Try it and see" is the strategy, not "design the perfect system."

4. **Full PAL replacement immediately.** PAL works fine as-is today. Absorption is incremental — clink first (highest value), remaining tools later. No urgency for complete replacement.

5. **A coordination system before trying anything.** The dependency graph shows dependencies, not a waterfall. Steps can overlap. Prototype-first.

---

## SECTION 7: CURRENT DISTANCE FROM TARGET

As of 2026-02-25, this is how far each layer is from its target state:

| Layer | Current State | Distance | Key Blockers |
|-------|--------------|----------|-------------|
| **OCTAVE MCP** | v1.3.0, production, PyPI published, 2080 tests | Close | Chassis-Profile grammar (octave-mcp#283) not yet specified |
| **HestAI Core** | B1 foundation, 4 tools, OA merger decided but not executed | Far | OA rebuild (#279-282), capability tiers (#284), tiered permits (#285) |
| **Debate Hall** | v0.5.0, 18 tools, 1368+ tests, consult/convene shipped | Medium | Governance Hall phases 2-5 (#163), RACI mode (#159) |
| **Workbench** | Phase 2 complete (lint cleanup), prototype | Far | Agent registry (#32), clink extraction (#33), governance chat UI (#16/#34) |
| **OA (to be absorbed)** | Operational, 714 tests | Being replaced | Rebuild phases #279-282 |
| **PAL (to be absorbed)** | Operational, 19 tools, daily use | Being replaced | clink extraction (#33), then gradual absorption (#36) |

### The Critical Path

The shortest path to the target state runs through:

**Wave 100** (all unblocked, start now) → **Wave 200** (protocol + dispatch) → **Wave 300** (integration + UI) → **Wave 400** (convergence + archive) → **Wave 500** (post-convergence cleanup)

The convergence point is **Wave 400: Cross-repo agent orchestration prototype** — where identity (Core), deliberation (Debate Hall), format (OCTAVE), and execution (Workbench) all work together for the first time.

---

## SECTION 8: ASSUMPTIONS REGISTER

| ID | Assumption | Confidence | Impact | Validates By |
|----|-----------|-----------|--------|-------------|
| EA1 | Three-repo architecture is sufficient | 85% | CRITICAL | Wave 400 prototype |
| EA2 | Chassis-Profile schema handles all capability selection needs | 70% | HIGH | First agent with multiple profiles |
| EA3 | Tiered permits reduce ceremony overhead without sacrificing security | 75% | HIGH | Quick-tier usage in production |
| EA4 | The Workbench can absorb PAL clink without breaking daily workflow | 80% | HIGH | Wave 200 clink extraction |
| EA5 | Cross-repo agent invocation is technically feasible with MCP | 65% | CRITICAL | Wave 400 prototype |
| EA6 | Debate Hall Governance Hall replaces ad-hoc decision making | 70% | MEDIUM | 2 months daily use |
| EA7 | Single developer can maintain 3 MCP servers + Workbench | 75% | CRITICAL | Post Wave 400 assessment |

---

## PROTECTION CLAUSE

If ANY agent or work item moves the ecosystem away from this target state — adding a fourth MCP server, duplicating agent definitions, building a standalone GUI for a headless service, or creating provider-specific governance — it must be flagged.

1. **STOP** the divergent work
2. **CITE** the specific ecosystem principle being violated (E1-E6)
3. **ESCALATE** to the operator for a decision: conform, amend the North Star, or explicitly accept the deviation with rationale

This North Star is a living document. It can be amended. But amendments are deliberate, not accidental.
