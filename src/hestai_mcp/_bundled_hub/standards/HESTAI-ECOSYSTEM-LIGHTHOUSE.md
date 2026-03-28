---
type: LIGHTHOUSE
id: ecosystem-lighthouse
version: 3.1
status: ACTIVE
purpose: Target state vision for the fully integrated HestAI ecosystem
created: 2026-02-25
revised: 2026-03-28
origin: Project 15 ecosystem build order coordination
tracking: https://github.com/orgs/elevanaltd/projects/15
# // REFERENCE: points-to-canonical (.hestai-sys/ runtime-injected copy; this is the _bundled_hub source)
---

# HESTAI ECOSYSTEM LIGHTHOUSE

**Version:** 3.1
**Status:** ACTIVE
**Revised:** 2026-03-28

---

## WHAT THIS DOCUMENT IS

This describes **where we're headed** — the target state of the HestAI ecosystem when fully integrated. It is the destination, not the law.

It is **not** a system standard (that's the System North Star), **not** a build plan (that's Project 15), **not** a snapshot of current state (that's the Ecosystem Overview), and **not** a methodology (that's the System North Star I1-I6).

**This document will change.** When reality contradicts this vision, update the document. When a better architecture emerges, rewrite the section. The value is in having a shared picture of where we're going, not in defending a frozen plan.

> **SUPERSESSION NOTE (2026-03-28):** The Ecosystem Overview v3.0 and Dependency Graph v3.0 now describe a Thick Client architecture where hestai-workbench absorbs hestai-mcp and odyssean-anchor-mcp. This Lighthouse predates that decision and still references the federation model. Sections describing HestAI Core as a separate server, OA rebuilding into hestai-mcp, and the old critical path are superseded by the v3.0 TARGET docs. This Lighthouse will be updated to align in a future PR.

**Relationship to other documents:**
- **System North Star:** Immutable methodology (I1-I6). The Lighthouse operates within those laws.
- **Ecosystem Overview:** v3.0 (STATUS::TARGET) describes the approved Thick Client architecture. Supersedes this Lighthouse for architectural direction.
- **Ecosystem Dependency Graph:** The sequenced build order for ecosystem migration. See Overview v3.0 for current target architecture.
- **Product North Stars:** Per-repo vision. Each should move toward this ecosystem vision.

---

## SECTION 1: THE VISION

### What We're Building

A unified system where a single developer can orchestrate multiple AI agents across multiple providers and models, with installed governance that prevents the drift, hallucination, and quality collapse that plague unstructured AI-assisted development.

The system is not a single application. It is an ecosystem of cooperating systems, each owning a distinct concern, connected by shared protocols and a common governance framework.

### The End State in One Paragraph

An operator opens the Workbench, picks a role from the agent registry, selects a provider and model, and starts working. The agent binds its identity through the anchor ceremony, loads its definition and skills, and operates within its authority boundaries. When it needs a decision, it opens a structured debate. When it needs another perspective, the Workbench dispatches a different agent on a different model. All communication uses OCTAVE format. All sessions are persistent. All decisions are auditable. The operator sees the whole system through one GUI and never needs to configure MCP servers, manage worktrees, or remember which agent does what.

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
- Agent definitions and skills library (one canonical source)
- Anchor ceremony (identity binding via progressive interrogation)
- Context stewardship (session lifecycle, clock in/out)
- Governance rules and enforcement
- Permit system (tiered: micro/quick/default/deep)
- Capability profiles for context-aware skill loading

**What it absorbs:**
- Odyssean Anchor MCP — the binding protocol, Steward state machine, proof validation, and permit system rebuilt natively inside HestAI Core (ADR-0275 accepted, rebuild phases #279-282 not yet started)
- Agent prompts from PAL MCP (61 clink role definitions consolidated as canonical source). PAL itself is eliminated — dispatch moves natively to Workbench, agent prompts and role definitions consolidate here as the canonical source

**What it does NOT own:** Deliberation (debate-hall), execution/UI/dispatch (Workbench), OCTAVE format (octave-mcp).

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
- Agent registry (role -> provider -> model -> dispatch mode, UI-configurable)
- Multi-CLI dispatch (spawning agents via Claude, Codex, Gemini, or Goose CLIs)
- API dispatch (lightweight agent calls via OpenRouter for advisory/consultation roles)
- Session management (worktrees, terminal multiplexing, session persistence)
- Governance Chat UI (rendering debate-hall transcripts as conversation threads)
- System dashboard (visibility into all active sessions, agents, debates)

**What it eliminates:**
- PAL MCP Server — ceases to exist. CLI dispatch is natively owned by the Workbench agent registry. Agent prompts consolidated to HestAI Core. No intermediate bridge layer.
- Crystal Fresh — the original fork from which the Workbench evolved

**What it does NOT own:** Agent identity (HestAI Core), deliberation logic (debate-hall), document format (octave-mcp).

**Key properties:**
- Only system with a GUI — debate-hall and HestAI Core are headless MCP servers
- Knows WHICH provider, model, and dispatch mode each agent uses (separation from WHO the agent is)
- The convergence point — where identity, deliberation, format, and execution meet
- Two-tier dispatch: CLI for interactive sessions (Claude, Codex, Gemini, Goose), API for lightweight calls (OpenRouter)

**Agent Registry schema (conceptual):**

Each agent registry entry maps identity to execution:

| Field | Description | Examples |
|-------|-------------|---------|
| **role** | Agent role from HestAI Core | `holistic-orchestrator`, `implementation-lead`, `critical-engineer` |
| **provider** | AI provider | `anthropic`, `google`, `openai`, `openrouter` |
| **model** | Specific model | `claude-opus-4-6`, `gemini-2.5-pro`, `codex-mini`, `moonshotai/kimi-k2.5` |
| **dispatch** | CLI or API | `cli:claude`, `cli:codex`, `cli:gemini`, `cli:goose`, `api:openrouter` |

The registry replaces all of PAL's configuration (e.g., `goose.json` provider configs) with a unified, UI-configurable mapping. Switching an agent's model is a registry edit, not a code change.

**Cross-provider bridge:** CLIs are designed for human-to-AI interaction — an agent running in Claude CLI cannot natively signal the Workbench to spawn a Codex panel. The bridge is an MCP tool (e.g., `dispatch_colleague(role, task)`) that the Workbench provides. See the "Dual-path delegation" principle in Section 4 for the full mechanism (Pattern B).

**Target state:** Operator opens Workbench, picks a role from registry, and works. The Workbench spawns the correct CLI or makes the correct API call based on the registry entry. Governance Chat panel shows debates as threaded conversations. Session persistence across worktrees.

---

## SECTION 3: THE DAILY WORKFLOW (TARGET STATE)

This is what the operator's daily experience looks like when the ecosystem is complete:

1. **Open the Workbench.** Dashboard shows active sessions, recent decisions, system health.

2. **Pick a task.** Select work — a feature, a bug, an architectural decision.

3. **Pick a role.** Agent registry shows available roles (Holistic Orchestrator, Implementation Lead, Technical Architect, etc.) with their provider/model/dispatch assignments. Select one.

4. **Workbench spawns the agent.** Creates a git worktree, connects MCP servers, launches the appropriate CLI (Claude, Codex, Gemini, or Goose) based on the registry entry.

5. **Agent binds identity.** Anchor ceremony runs automatically — the agent proves it comprehends its role, the System Standard, and the current project context. Appropriate capability profile loads based on task scope.

6. **Agent works.** Calls HestAI Core for skills and context. Uses OCTAVE format for all documents. Operates within its authority boundaries.

7. **Agent hits an ambiguous decision.** Calls debate-hall for a structured Wind/Wall/Door debate. The debate produces a synthesis with a decision record. The Governance Chat panel shows the debate as a conversation thread.

8. **Agent needs lightweight advisory.** Calls an API-dispatched agent (e.g., ho-liaison on OpenRouter) for quick consultation. The response comes back within the same session — no CLI spawn needed.

9. **Agent delegates implementation work.** The agent calls a subagent mapped in the registry — possibly on a different CLI and provider entirely. For example, HO on Claude Opus delegates to an implementation-lead on Goose CLI (configured to use an OpenRouter model like Kimi K2.5). The subagent spawns with full MCP access, binds its own identity via anchor ceremony, does the work, and returns results.

10. **Work needs review.** The agent dispatches review agents from the registry. CRS might be mapped to Codex CLI, CE to Gemini CLI. Each reviewer binds, reviews the PR, and submits their assessment via `submit_review`. Different models provide genuine multi-perspective review.

11. **Session ends.** HestAI Core archives the transcript in OCTAVE format. The decision record is hash-chained and searchable. The worktree preserves the work.

12. **Operator reviews.** The dashboard shows what was done, what decisions were made, and what's next. All artifacts are persistent and discoverable.

---

## SECTION 4: ARCHITECTURAL PRINCIPLES

These are the current best thinking about how the ecosystem should be structured. They are strong preferences, not immutable laws. If experience proves one wrong, change it.

### Separation of concerns

Each system owns exactly one concern. Identity is not deliberation. Deliberation is not execution. Format is not governance. HestAI Core owns WHO. Workbench owns WHERE and HOW. Debate Hall owns GOVERNANCE DECISIONS. OCTAVE owns WHAT FORMAT.

### One canonical source

Agent definitions exist in exactly one place: HestAI Core. Not duplicated in the Workbench, not embedded in debate-hall. When an agent's definition changes, it changes in one file. The Workbench's agent registry maps roles to providers — it references identity, never duplicates it.

### Provider agnosticism

The governance layer (HestAI Core) knows nothing about which AI model runs an agent. The execution layer (Workbench) knows nothing about what an agent's authority boundaries are. Switching providers for a role is a registry change, not a governance change.

This is not theoretical. Goose CLI agents have been verified with full MCP access to all four ecosystem servers (HestAI, OCTAVE, Debate Hall, Odyssean Anchor), including anchor ceremony binding, debate participation, and OCTAVE read/write. Provider agnosticism is proven across Claude, Codex, Gemini, and Goose.

### Standalone deliberation

Debate Hall works without HestAI. A team that doesn't use HestAI governance can still use Wind/Wall/Door debates. This is the adoption path that makes the ecosystem viable beyond the original developer.

### Ceremony proportional to risk

Not every task needs a full anchor ceremony. Trivial read-only tasks get a micro permit. Standard work gets the full ceremony. Critical decisions get extra scrutiny. Governance weight scales with risk.

In the Workbench, ceremony streamlines via **hybrid injection**: the Workbench pre-injects raw governance context (System Standard, agent definition, North Star, project context) into the system prompt, then the agent writes a short synthesis proving comprehension — one tool call instead of six. The Odyssean Anchor / HestAI Core binding and proof validation still execute and are server-validated; the optimization only reduces round-trips and prompt I/O, not the verification itself. This preserves the cognitive alignment that makes the ceremony valuable (the agent generates its own proof, engaging its reasoning) while collapsing the I/O overhead. Inject the data, force the agent to write the synthesis.

For **API-dispatched agents** (advisory roles via OpenRouter), ceremony further streamlines via **assistant prefilling**: the Workbench constructs the full system prompt (agent definition + skill kernels + governance context), then injects a prefilled assistant turn that demonstrates cognitive alignment before the actual task is delivered. This avoids attention decay — simply dumping governance context into a system prompt and hoping for compliance is insufficient. The prefilled synthesis primes the model into the correct operating mode zero-shot. The Workbench's `ApiDispatcher` constructs this server-side; the calling agent never sees the priming exchange. Provider-aware message construction is required, as not all OpenRouter backends handle prefilling identically.

### Dual-path delegation

Agent delegation operates through two coexisting patterns:

- **Pattern A (intra-session):** A CLI agent uses its native delegation mechanism (e.g., Claude's `Task()` tool) to spawn a subagent within the same worktree. The subagent inherits MCP server connections and can bind via micro-tier anchor. This is fast, same-provider delegation governed by the subagent-rules skill.

- **Pattern B (cross-provider):** The Workbench spawns a new panel with a different CLI tool, selected from the agent registry. The LLM signals the Workbench via an MCP tool (e.g., `dispatch_colleague`), the Workbench intercepts the call, spawns the target CLI panel, passes the task, waits for completion, and returns the result. To the calling agent, it looks like a normal tool call that took longer to respond.

Both patterns are intentional. Pattern A is efficient for same-model work. Pattern B is the provider-agnostic path that makes multi-model orchestration invisible to the LLMs.

**`dispatch_colleague` MCP tool contract (Pattern B):** The bridge between CLI agents and the Workbench's dispatch system. When any agent calls `dispatch_colleague(role, task)`, the Workbench intercepts the call, looks up the role in the agent registry, and either spawns a CLI panel or makes an API call depending on the dispatch mode. The result returns to the calling agent as a normal tool response.

Key mechanics:
- **Continuation model:** Every dispatch returns a `dispatch_id`. To continue a conversation with the same dispatched agent (e.g., for rework loops or clarifying questions), the caller passes the `dispatch_id` back: `dispatch_colleague(dispatch_id="disp_7f8a9", task="Fix line 42")`. The Workbench's `ContinuationStore` maps each `dispatch_id` to the provider-specific identifier (Claude session ID, Goose conversation, OpenRouter thread, etc.).
- **Recursive delegation:** Any agent spawned via `dispatch_colleague` itself has access to `dispatch_colleague`. An Implementation Lead dispatched on Goose can dispatch a Test Methodology Guardian on a different provider for test review. Dispatch depth is configurable (default 3) with human approval required beyond the threshold.
- **Registry snapshot:** The agent registry mapping is captured at dispatch time and stored with the dispatch record. Mid-chain registry changes do not affect running dispatches.

### Rebuild-portable dispatch

The Workbench is a Crystal fork that will eventually be rebuilt. Dispatch logic must survive that rebuild. The `dispatch_colleague` MCP tool is hosted inside the Workbench (not a separate server — three repos, not four), but the dispatch logic is implemented as a clean `DispatchService` module with a well-defined interface:

- `AgentRegistryLookup` — resolves role to provider/model/dispatch mode
- `CliDispatcher` — spawns CLI panels via existing `AbstractCliManager` abstraction
- `ApiDispatcher` — makes OpenRouter API calls with assistant-prefilled mini-ceremony
- `ContinuationStore` — maps `dispatch_id` to provider-specific conversation identifiers
- `IdentityInjector` — constructs system prompts from agent definitions and skill kernels

When the Workbench is rebuilt, the MCP tool contract (`dispatch_colleague` signature) and the `DispatchService` interface port directly. Only the Electron/UI layer changes.

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

8. **Three MCP servers, not six.** OA absorbed into HestAI Core. PAL eliminated — dispatch natively owned by Workbench agent registry, identity consolidated to HestAI Core.

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

4. **A PAL bridge layer.** PAL is eliminated, not absorbed. The Workbench agent registry natively owns multi-CLI dispatch (Claude, Codex, Gemini, Goose) and API dispatch (OpenRouter). There is no intermediate dispatch server.

5. **A coordination system before trying anything.** The dependency graph shows dependencies, not a waterfall. Prototype-first.

---

## SECTION 7: CURRENT DISTANCE FROM TARGET

As of 2026-03-20:

| Layer | Current State | Distance | Key Blockers |
|-------|--------------|----------|-------------|
| **OCTAVE MCP** | v1.8.0, production, PyPI published | Close | Chassis-Profile grammar (octave-mcp#283) at RFC stage |
| **HestAI Core** | B1 foundation, 4 tools, OA merger decided (ADR-0275) but not started | Far | OA rebuild phases (#279-282), capability tiers (#284), tiered permits (#285) |
| **Debate Hall** | v0.4.0, 17 tools, consult/convene shipped | Medium | Governance Hall (#163), RACI mode (#159) |
| **Workbench** | Phase 2 complete, Phase 3 (agent registry) open | Far | Agent registry (#32) must support multi-CLI dispatch (Claude/Codex/Gemini/Goose) + API dispatch (OpenRouter), governance chat UI (#16/#34) |
| **OA (to be absorbed)** | Operational, ADR-0275 accepted | Being replaced | Rebuild phases not started |
| **PAL (to be eliminated)** | Operational, used daily via `pal clink` | Being eliminated | Workbench agent registry replaces all PAL dispatch. Goose via `pal clink` validates that multi-provider dispatch works — the registry must natively own this capability |

### The Critical Path

Per Project 15 (Order field) and the Ecosystem Dependency Graph (STEP numbering):

**Order 10** (merger decision — DONE, ADR-0275) -> **Order 20** (OA rebuild + agent registry with multi-CLI/API dispatch) -> **Order 30** (governance chat UI) -> **Order 40** (cross-repo agent orchestration) -> **Order 50** (blind assessor + PAL decommission)

The convergence point is **Order 40: Cross-repo agent orchestration prototype** — where identity, deliberation, format, and execution work together for the first time.

### Validated Early

Goose CLI integration via `pal clink` has proven that non-Claude agents can participate as first-class ecosystem citizens — full MCP access to all 4 servers (46 tools), anchor ceremony binding, debate-hall participation, OCTAVE read/write, and agent/skill delegation. This validates provider agnosticism ahead of the Workbench agent registry build.

---

## SECTION 8: ASSUMPTIONS

| ID | Assumption | Confidence | Impact | Validates By |
|----|-----------|-----------|--------|-------------|
| EA1 | Three-repo architecture is sufficient | 85% | CRITICAL | Order 40 prototype |
| EA2 | Chassis-Profile schema handles all capability selection needs | 70% | HIGH | First agent with multiple profiles |
| EA3 | Tiered permits reduce ceremony overhead without sacrificing security | 75% | HIGH | Quick-tier usage in production |
| EA4 | Workbench agent registry can natively replace all PAL dispatch (multi-CLI + API) | 80% | HIGH | Agent registry prototype with Goose + Claude + Codex + Gemini dispatch |
| EA5 | Cross-repo agent invocation is technically feasible with MCP | 75% | CRITICAL | Order 40 prototype. Confidence raised from 65%: Goose full MCP access validates multi-provider feasibility |
| EA6 | Debate Hall Governance Hall replaces ad hoc decision-making | 70% | MEDIUM | 2 months daily use |
| EA7 | Single developer can maintain 3 MCP servers + Workbench | 80% | CRITICAL | Post Order 40 assessment. Confidence raised from 75%: PAL elimination (not absorption) reduces maintenance to 3 servers not 4 |
| EA8 | Assistant prefilling achieves sufficient cognitive alignment for API-dispatched agents | 70% | HIGH | First API dispatch with prefilled mini-ceremony on 3+ OpenRouter backends |
| EA9 | Recursive `dispatch_colleague` calls (depth 2-3) remain coherent without context degradation | 65% | HIGH | IL dispatching TMG dispatching back — full chain test with continuation |

---

## DIVERGENCE CHECK

If work moves the ecosystem away from this vision — adding a fourth MCP server, duplicating agent definitions, building standalone GUIs for headless services — it's worth asking: does the vision need updating, or does the work need redirecting?

This is a question, not an order. Sometimes the vision is wrong.
