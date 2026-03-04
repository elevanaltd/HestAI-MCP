---
type: LIGHTHOUSE
id: ecosystem-lighthouse
version: 2.0
status: ACTIVE
purpose: Target state vision for the fully integrated HestAI ecosystem
created: 2026-02-25
revised: 2026-03-04
origin: Project 15 ecosystem build order coordination
tracking: https://github.com/orgs/elevanaltd/projects/15
# // REFERENCE: points-to-canonical (.hestai-sys/ runtime-injected copy; this is the _bundled_hub source)
---

# HESTAI ECOSYSTEM LIGHTHOUSE

**Version:** 2.0
**Status:** ACTIVE
**Revised:** 2026-03-04

---

## WHAT THIS DOCUMENT IS

This describes **where we're headed** — the target state of the HestAI ecosystem when fully integrated. It is the destination, not the law.

It is **not** a constitution (that's the System North Star), **not** a build plan (that's Project 15), **not** a snapshot of current state (that's the Ecosystem Overview), and **not** a methodology (that's the System North Star I1-I6).

**This document will change.** When reality contradicts this vision, update the document. When a better architecture emerges, rewrite the section. The value is in having a shared picture of where we're going, not in defending a frozen plan.

**Relationship to other documents:**
- **System North Star:** Immutable methodology (I1-I6). The Lighthouse operates within those laws.
- **Ecosystem Overview:** Describes what exists today. This describes what we're building toward.
- **Ecosystem Dependency Graph:** The sequenced build order. How we get from Overview to Lighthouse.
- **Product North Stars:** Per-repo vision. Each should move toward this ecosystem vision.

---

## SECTION 1: THE VISION

### What We're Building

A unified system where a single developer can orchestrate multiple AI agents across multiple providers and models, with installed governance that prevents the drift, hallucination, and quality collapse that plague unstructured AI-assisted development.

The system is not a single application. It is an ecosystem of cooperating systems, each owning a distinct concern, connected by shared protocols and a common governance framework.

### The End State in One Paragraph

An operator opens the Workbench, picks a role from the agent registry, selects a provider and model, and starts working. The agent binds its identity through the anchor ceremony, loads its constitution and skills, and operates within its authority boundaries. When it needs a decision, it opens a structured debate. When it needs another perspective, the Workbench dispatches a different agent on a different model. All communication uses OCTAVE format. All sessions are persistent. All decisions are auditable. The operator sees the whole system through one GUI and never needs to configure MCP servers, manage worktrees, or remember which agent does what.

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

**Target state:** Published on PyPI. Standalone community tool. Grammar supports agent definition schemas including capability tier models (Chassis-Profile RFC in progress at octave-mcp#283).

---

### Layer 1: HestAI Core MCP — The Operating System

**What it is:** The single source of truth for agent identity, governance, and context management.

**What it owns:**
- Agent constitutions and skills library (one canonical source)
- Anchor ceremony (identity binding via progressive interrogation)
- Context stewardship (session lifecycle, clock in/out)
- Governance rules and enforcement
- Permit system (tiered: micro/quick/default/deep)
- Capability profiles for context-aware skill loading

**What it absorbs:**
- Odyssean Anchor MCP — the binding protocol, Steward state machine, proof validation, and permit system rebuilt natively inside HestAI Core (ADR-0275 accepted, rebuild phases #279-282 not yet started)
- Agent prompts from PAL MCP (61 clink role definitions consolidated as canonical source)

**What it does NOT own:** Deliberation (debate-hall), execution/UI (Workbench), model dispatch (Workbench), OCTAVE format (octave-mcp).

**Key properties:**
- Provider-agnostic — knows WHO agents are and HOW they should behave, not which model runs them
- Single canonical source for all agent definitions (no duplication across repos)
- Every agent interaction starts with anchor ceremony (identity verification before execution)

**Target state:** Single `pip install hestai-mcp` gives you governance + identity + anchor ceremony. No separate OA server. Tiered permits for ceremony weight proportional to task complexity.

---

### Layer 2: Debate Hall MCP — The Deliberation Chamber

**What it is:** Standalone multi-perspective reasoning engine with hash-chain integrity.

**What it owns:**
- Wind/Wall/Door structured debates
- Governance Hall (persistent committee spaces, expert consultations)
- RACI governance mode
- Decision records with SHA-256 hash chain
- Consult and convene operations
- RFC ratification, human interjection

**What it does NOT own:** Agent identity (HestAI Core), UI rendering (Workbench), the OCTAVE format (octave-mcp).

**Key properties:**
- Standalone — works without HestAI for non-governance users
- Persistent transcripts — decisions are auditable, append-only, hash-chained
- Advisory, not authoritative — humans decide, debate-hall presents structured perspectives

**Target state:** Full Governance Hall with persistent committee spaces. RACI mode for formal governance decisions. Decision search across all past debates. Headless — all UI through the Workbench.

---

### Layer 3: HestAI Workbench — The Control Panel

**What it is:** The only GUI in the ecosystem. Desktop application for managing AI sessions, agent dispatch, and system visibility.

**What it owns:**
- Agent registry (role -> provider -> model mapping, UI-configurable)
- CLI dispatch (spawning agents on different providers/models, absorbed from PAL clink)
- Session management (worktrees, terminal multiplexing, session persistence)
- Governance Chat UI (rendering debate-hall transcripts as conversation threads)
- System dashboard (visibility into all active sessions, agents, debates)

**What it absorbs:**
- PAL MCP Server — clink dispatch moves to Workbench, workflow tools replaced by proper agent loading via anchor, agent prompts consolidated to HestAI Core
- Crystal Fresh — the original fork from which the Workbench evolved

**What it does NOT own:** Agent identity (HestAI Core), deliberation logic (debate-hall), document format (octave-mcp).

**Key properties:**
- Only system with a GUI — debate-hall and HestAI Core are headless MCP servers
- Knows WHICH provider and model each agent runs on (separation from WHO the agent is)
- The convergence point — where identity, deliberation, format, and execution meet

**Target state:** Operator opens Workbench, picks a role from registry, picks a provider/model, and works. Governance Chat panel shows debates as threaded conversations. Agent dispatch handles multi-provider orchestration. Session persistence across worktrees.

---

## SECTION 3: THE DAILY WORKFLOW (TARGET STATE)

This is what the operator's daily experience looks like when the ecosystem is complete:

1. **Open the Workbench.** Dashboard shows active sessions, recent decisions, system health.

2. **Pick a task.** Select work — a feature, a bug, an architectural decision.

3. **Pick a role.** Agent registry shows available roles (Holistic Orchestrator, Implementation Lead, Technical Architect, etc.) with their provider/model assignments. Select one.

4. **Workbench spawns the agent.** Creates a git worktree, connects MCP servers, launches the CLI for the selected provider/model.

5. **Agent binds identity.** Anchor ceremony runs automatically — the agent proves it comprehends its role, the Constitution, and the current project context. Appropriate capability profile loads based on task scope.

6. **Agent works.** Calls HestAI Core for skills and context. Uses OCTAVE format for all documents. Operates within its authority boundaries.

7. **Agent hits an ambiguous decision.** Calls debate-hall for a structured Wind/Wall/Door debate. The debate produces a synthesis with a decision record. The Governance Chat panel shows the debate as a conversation thread.

8. **Agent needs another perspective.** The Workbench dispatches a different agent on a different provider/model. The new agent binds its own identity. Both agents see the shared project context.

9. **Session ends.** HestAI Core archives the transcript in OCTAVE format. The decision record is hash-chained and searchable. The worktree preserves the work.

10. **Operator reviews.** The dashboard shows what was done, what decisions were made, and what's next. All artifacts are persistent and discoverable.

---

## SECTION 4: ARCHITECTURAL PRINCIPLES

These are the current best thinking about how the ecosystem should be structured. They are strong preferences, not immutable laws. If experience proves one wrong, change it.

### Separation of concerns

Each system owns exactly one concern. Identity is not deliberation. Deliberation is not execution. Format is not governance. HestAI Core owns WHO. Workbench owns WHERE and HOW. Debate Hall owns GOVERNANCE DECISIONS. OCTAVE owns WHAT FORMAT.

### One canonical source

Agent definitions exist in exactly one place: HestAI Core. Not duplicated in PAL, not copied to the Workbench, not embedded in debate-hall. When an agent's constitution changes, it changes in one file.

### Provider agnosticism

The governance layer (HestAI Core) knows nothing about which AI model runs an agent. The execution layer (Workbench) knows nothing about what an agent's authority boundaries are. Switching providers for a role is a registry change, not a governance change.

### Standalone deliberation

Debate Hall works without HestAI. A team that doesn't use HestAI governance can still use Wind/Wall/Door debates. This is the adoption path that makes the ecosystem viable beyond the original developer.

### Ceremony proportional to risk

Not every task needs a full anchor ceremony. Trivial read-only tasks get a micro permit. Standard work gets the full ceremony. Critical decisions get extra scrutiny. Governance weight scales with risk.

---

## SECTION 5: SUCCESS CRITERIA

The ecosystem is "done" when:

### Functional

1. **Single-command agent dispatch.** Operator picks role + provider/model -> agent is running with full identity binding in under 30 seconds.

2. **Cross-repo agent invocation.** An HO agent in repo A can convene agents in repos B and C for a structured debate, each on different providers/models.

3. **No duplicate agent definitions.** Exactly one canonical definition per agent role, in HestAI Core.

4. **Governance Chat as conversation.** Debates visible as threaded conversations in the Workbench, not raw JSON.

5. **Session continuity.** An agent can be stopped and resumed with full context. A different agent can pick up where the first left off.

6. **Decision audit trail.** Any past decision findable via `search_decisions`, with full transcript, hash-chain proof, and synthesis.

### Quality

7. **All repos green.** Tests passing, coverage above thresholds, linters clean, type checking strict.

8. **Three MCP servers, not six.** OA absorbed into HestAI Core. PAL absorbed into Workbench + Core.

9. **The Workbench is daily-driveable.** Used for real work, not as a demo. 2 months of daily use before any rebuild.

### Adoption

10. **Debate Hall has external users.** At least one person outside HestAI uses debate-hall-mcp.

11. **OCTAVE has community traction.** Published, documented, adopted by at least one external project.

12. **A new developer can onboard.** Zero to first agent-assisted session in under 30 minutes.

---

## SECTION 6: WHAT WE'RE NOT BUILDING

1. **Multi-tenant SaaS.** Single-developer tool. Scaling to teams is an assumption, not a build target.

2. **Custom model training.** Off-the-shelf models from providers. The value is in governance, not model performance.

3. **Perfect orchestration.** Cross-repo agent invocation is explicitly a prototype. "Try it and see."

4. **Full PAL replacement immediately.** PAL works fine today. Absorption is incremental — clink first, remaining tools later.

5. **A coordination system before trying anything.** The dependency graph shows dependencies, not a waterfall. Prototype-first.

---

## SECTION 7: CURRENT DISTANCE FROM TARGET

As of 2026-03-04:

| Layer | Current State | Distance | Key Blockers |
|-------|--------------|----------|-------------|
| **OCTAVE MCP** | v1.8.0, production, PyPI published | Close | Chassis-Profile grammar (octave-mcp#283) at RFC stage |
| **HestAI Core** | B1 foundation, 4 tools, OA merger decided (ADR-0275) but not started | Far | OA rebuild phases (#279-282), capability tiers (#284), tiered permits (#285) |
| **Debate Hall** | v0.4.0, 17 tools, consult/convene shipped | Medium | Governance Hall (#163), RACI mode (#159) |
| **Workbench** | Phase 2 complete, Phase 3 (agent registry) open | Far | Agent registry (#32), clink extraction (#33), governance chat UI (#16/#34) |
| **OA (to be absorbed)** | Operational, ADR-0275 accepted | Being replaced | Rebuild phases not started |
| **PAL (to be absorbed)** | Operational, actively used daily (clink, chat, apilookup) | Being replaced | clink extraction (#33), then gradual absorption (#36) |

### The Critical Path

Per Project 15 (Order field) and the Ecosystem Dependency Graph (STEP numbering):

**Order 10** (merger decision — DONE, ADR-0275) -> **Order 20** (OA rebuild + agent registry) -> **Order 30** (clink extraction + governance chat UI) -> **Order 40** (cross-repo agent orchestration) -> **Order 50** (blind assessor + PAL full absorption)

The convergence point is **Order 40: Cross-repo agent orchestration prototype** — where identity, deliberation, format, and execution work together for the first time.

---

## SECTION 8: ASSUMPTIONS

| ID | Assumption | Confidence | Impact | Validates By |
|----|-----------|-----------|--------|-------------|
| EA1 | Three-repo architecture is sufficient | 85% | CRITICAL | Order 40 prototype |
| EA2 | Chassis-Profile schema handles all capability selection needs | 70% | HIGH | First agent with multiple profiles |
| EA3 | Tiered permits reduce ceremony overhead without sacrificing security | 75% | HIGH | Quick-tier usage in production |
| EA4 | Workbench can absorb PAL clink without breaking daily workflow | 80% | HIGH | Order 30 clink extraction |
| EA5 | Cross-repo agent invocation is technically feasible with MCP | 65% | CRITICAL | Order 40 prototype |
| EA6 | Debate Hall Governance Hall replaces ad-hoc decision making | 70% | MEDIUM | 2 months daily use |
| EA7 | Single developer can maintain 3 MCP servers + Workbench | 75% | CRITICAL | Post Order 40 assessment |

---

## DIVERGENCE CHECK

If work moves the ecosystem away from this vision — adding a fourth MCP server, duplicating agent definitions, building standalone GUIs for headless services — it's worth asking: does the vision need updating, or does the work need redirecting?

This is a question, not an order. Sometimes the vision is wrong.
