---
type: LIGHTHOUSE
id: ecosystem-lighthouse
version: 4.2
status: ACTIVE
purpose: Target state vision for the fully integrated HestAI ecosystem
created: 2026-02-25
revised: 2026-04-20
origin: Project 15 ecosystem build order coordination
tracking: https://github.com/orgs/elevanaltd/projects/15
architecture: ADR-0353 Three-Service Model
# // REFERENCE: points-to-canonical (.hestai-sys/ runtime-injected copy; this is the _bundled_hub source)
---

# HESTAI ECOSYSTEM LIGHTHOUSE

**Version:** 4.2
**Status:** ACTIVE
**Revised:** 2026-04-20

---

## WHAT THIS DOCUMENT IS

This describes **where we're headed** — the target state of the HestAI ecosystem when fully integrated. It is the destination, not the law.

It is **not** a system standard (that's the System North Star), **not** a build plan (that's Project 15), **not** a snapshot of current state (that's the Ecosystem Overview), and **not** a methodology (that's the System North Star I1-I6).

**This document will change.** When reality contradicts this vision, update the document. When a better architecture emerges, rewrite the section. The value is in having a shared picture of where we're going, not in defending a frozen plan.

**Relationship to other documents:**
- **ADR-0353:** Canonical architectural decision. Established the Three-Service Model (Workbench + hestai-context-mcp + Vault). This Lighthouse reflects that decision.
- **System North Star:** Immutable methodology (I1-I6). The Lighthouse operates within those laws.
- **Ecosystem Overview v4.0:** System map reflecting the current architecture. Companion to this vision.
- **Ecosystem Dependency Graph v4.0:** Build sequence aligned to workbench PROJECT-CONTEXT v1.7.
- **Product North Stars:** Per-repo vision. Each should move toward this ecosystem vision.

---

## SECTION 1: THE VISION

### What We're Building

A unified system where a single developer can orchestrate multiple AI agents across multiple providers and models, with installed governance that prevents the drift, hallucination, and quality collapse that plague unstructured AI-assisted development.

The system is not a single application. It is an ecosystem of cooperating systems, each owning a distinct concern, connected by shared protocols and a common governance framework.

### The End State in One Paragraph

An operator opens the Workbench, picks a role from the agent registry, selects a provider and model, and starts working. The Payload Compiler reads the agent's identity from the Vault, assembles the KVAEPH payload, calls hestai-context-mcp for project context (Position 3), and dispatches via the appropriate CLI or API. The agent operates within its authority boundaries, enforced by the Alley-Oop pattern (synthetic acknowledgment + prefilled proof + dynamic anchor lock). When it needs a decision, it opens a structured debate. When it needs another perspective, the Workbench dispatches a different agent on a different model. All communication uses OCTAVE format. All sessions are persistent via hestai-context-mcp. All decisions are auditable. The operator sees the whole system through one GUI and never needs to configure MCP servers, manage worktrees, or remember which agent does what.

---

## SECTION 2: THE THREE-SERVICE TARGET ARCHITECTURE

The ecosystem comprises three services with clear ownership boundaries (ADR-0353 "Three-Service Model"), plus two standalone MCP servers:

### System 1: HestAI Workbench — The Eyes and Hands

**Repo:** `elevanaltd/hestai-workbench`

**What it is:** The only GUI in the ecosystem. Desktop application for agent dispatch, session management, and system visibility. Contains the Payload Compiler (KVAEPH) that assembles agent prompts from the Vault and context engine.

**What it owns:**
- Payload Compiler (KVAEPH stacking: BIOS + AXIOMS + IDENTITY + CAPABILITIES + CONTEXT + TASK)
- Alley-Oop pattern (synthetic acknowledgment + prefilled proof + dynamic anchor lock) for identity injection
- Agent registry (role -> provider -> model -> dispatch mode, UI-configurable)
- Stratified conditioning (baseline pipeline for simple tasks, reliability pipeline for T2+ work)
- Multi-CLI dispatch (spawning agents via Claude, Codex, Gemini, or Goose CLIs)
- API dispatch (lightweight agent calls via OpenRouter for advisory/consultation roles)
- Session management (worktrees, terminal multiplexing)
- Governance Chat UI (rendering debate-hall transcripts as conversation threads)
- System dashboard (visibility into all active sessions, agents, debates)
- Precedence-Locked Materialized Resolver (matrix_defaults / matrix_overrides / v_resolved_matrix)

**What it does NOT own:** Agent identity definitions (Vault), session lifecycle and context synthesis (hestai-context-mcp), deliberation logic (debate-hall), document format (octave-mcp).

**Key properties:**
- HIGH volatility — planned Crystal-to-TypeScript rebuild. Governance logic survives in hestai-context-mcp untouched; only a ~30-line stdio MCP client adapter needs rewriting.
- The convergence point — where identity (from Vault), deliberation (from debate-hall), context (from hestai-context-mcp), and execution meet.
- MCP_NOT_REQUIRED for dispatch validation — Alley-Oop is regex on output, not server round-trip.

**Agent Registry schema (conceptual):**

| Field | Description | Examples |
|-------|-------------|---------|
| **role** | Agent role from Vault | `holistic-orchestrator`, `implementation-lead`, `critical-engineer` |
| **provider** | AI provider | `anthropic`, `google`, `openai`, `openrouter` |
| **model** | Specific model | `claude-opus-4-6`, `gemini-2.5-pro`, `codex-mini`, `moonshotai/kimi-k2.5` |
| **dispatch** | CLI or API | `cli:claude`, `cli:codex`, `cli:gemini`, `cli:goose`, `api:openrouter` |

**Target state:** Operator opens Workbench, picks a role from registry, and works. The Payload Compiler assembles the full KVAEPH prompt, calls hestai-context-mcp for Position 3 context, and dispatches. Governance Chat panel shows debates as threaded conversations.

---

### System 2: The Vault — The DNA

**Location:** `~/.hestai-workbench/library/` (git-backed, configurable via LIBRARY_ROOT)

**What it is:** The single canonical source for all agent identity artifacts. Read-only at runtime.

**What it owns:**
- V9 agent definitions (~50 lines each, blank-slate schema)
- V9 skills with ANCHOR_KERNEL sections (S5) for injection depth control
- Cognitions (ETHOS, PATHOS, LOGOS)
- Standards (System Standard, naming rules, visibility rules)
- Patterns for structured workflows

**What it does NOT own:** Runtime state, session lifecycle, dispatch logic, deliberation.

**Key properties:**
- ZERO volatility — git-backed, immutable at runtime
- The Workbench reads the Vault directly and compiles system prompts with no filesystem intermediate
- Glass Agent Editor provides CRUD with auto-commit on save
- Starter library ships in Workbench `resources/` for first-run bootstrap

**Target state:** All agent identity artifacts live here. No duplication. A change to an agent's definition is a single edit in one file, auto-committed to the vault repo.

---

### System 3: hestai-context-mcp — The Memory and Environment

**Repo:** `elevanaltd/hestai-context-mcp` (IMPLEMENTED — Phase 1 complete 2026-04-17, harvested from hestai-mcp)

**What it is:** A standalone governance engine providing session lifecycle, context synthesis, learnings extraction, and review infrastructure via stdio MCP transport.

**What it owns (Phase 1 delivered):**
- clock_in (session creation, focus resolution, focus conflict detection; AI-synthesized context summaries currently deferred — see known gaps below)
- clock_out (transcript parsing via `TranscriptParser` ABC + `ClaudeTranscriptParser` adapter, credential redaction via RedactionEngine, OCTAVE compression, structured learnings indexing)
- get_context (read-only context synthesis tool)
- submit_review (structured code review verdicts with CI gate clearing, 8 reviewer roles, dry-run, commit SHA pinning)
- ContextSteward (dynamic PhaseConstraints synthesis)
- `.hestai/state/` management (sessions, context, reports, research)
- Product North Star injection at KVAEPH Position 3 (planned — Phase 3)

**TranscriptParser adapter pattern:** `clock_out` was redesigned (not harvested as-is) around a provider-agnostic `TranscriptParser` ABC. `ClaudeTranscriptParser` is implemented; Codex/Gemini/Goose adapters are pending Phase 2+.

**What it does NOT own:** Agent identity (Vault), dispatch/UI (Workbench), deliberation (debate-hall), document format (octave-mcp), `bind` tool (legacy-only, replaced by Alley-Oop).

**Key properties:**
- LOW volatility — Python codebase, 361 tests, 89% coverage at Phase 1 close. Survives Workbench rebuilds untouched.
- Stdio transport (subprocess, not daemon) — the "Git/VS Code" pattern. Zero network ports, zero monitoring overhead.
- Harvest not rewrite: clock_in harvested from hestai-mcp; clock_out redesigned; legacy hestai-mcp stays intact (1033 tests) for A/B comparison.
- Terminal parity is automatic — any CLI tool gets identical governance by adding one MCP config entry.

**Known gap — AI synthesis feature parity:** Legacy hestai-mcp has a working AI synthesis path in `clock_in` when API keys are configured; the new repo currently lacks the path entirely. Without API keys, both produce structured non-AI output. Closing this is tracked as Pre-A/B Work item P0b (issue #5) — see "Pre-A/B Work" below — and must land before the outcome-quality A/B test is meaningful.

**Target state:** `pip install hestai-context-mcp` gives you session lifecycle + context synthesis + learnings + review. Works with or without the Workbench.

**PyPI publication plan (DECIDED):** Internal-first. Build, prove via A/B internally, then publish externally only after the new system wins consistently. Not publishing early.

---

### Standalone: OCTAVE MCP — The Language

**Repo:** `elevanaltd/octave-mcp`

**What it is:** A pure semantic compression protocol with zero governance dependencies.

**What it owns:**
- OCTAVE format specification and grammar
- Validation (syntactic and semantic)
- Generation and compression
- Grammar compilation (GBNF export)

**Key properties:**
- Maximum community adoption potential — useful without HestAI
- Foundation layer — all other systems speak OCTAVE
- No dependencies on anything else in the ecosystem

**Target state:** Published on PyPI. Standalone community tool. Grammar supports agent definition schemas.

---

### Standalone: Debate Hall MCP — The Deliberation Chamber

**Repo:** `elevanaltd/debate-hall-mcp`

**What it is:** Standalone multi-perspective reasoning engine with hash-chain integrity.

**What it owns:**
- Wind/Wall/Door structured debates
- Governance Hall (persistent committee spaces, expert consultations)
- RACI governance mode
- Decision records with SHA-256 hash chain
- Consult and convene operations
- RFC ratification, human interjection

**Key properties:**
- Standalone — works without HestAI for non-governance users
- Persistent transcripts — decisions are auditable, append-only, hash-chained
- Advisory, not authoritative — humans decide, debate-hall presents structured perspectives

**Target state:** Full Governance Hall with persistent committee spaces. RACI mode for formal governance decisions. Decision search across all past debates. Headless — all UI through the Workbench.

---

## SECTION 3: THE DAILY WORKFLOW (TARGET STATE)

This is what the operator's daily experience looks like when the ecosystem is complete:

1. **Open the Workbench.** Dashboard shows active sessions, recent decisions, system health.

2. **Pick a task.** Select work — a feature, a bug, an architectural decision.

3. **Pick a role.** Agent registry shows available roles (Holistic Orchestrator, Implementation Lead, Technical Architect, etc.) with their provider/model/dispatch assignments and tier. Select one.

4. **Workbench compiles and dispatches.** The Payload Compiler reads the Vault for Positions 0-2 (BIOS/AXIOMS, IDENTITY, CAPABILITIES), calls hestai-context-mcp via stdio for Position 3 (CONTEXT — clock_in returns context synthesis, Product North Star, project state), assembles the full KVAEPH payload, creates a git worktree, and launches the appropriate CLI or API based on the registry entry.

5. **Agent identity is injected via Alley-Oop.** For the reliability pipeline (T2+ tasks): the Workbench constructs a synthetic acknowledgment turn, prefills a static proof from Vault data, and delivers the task with a Dynamic Anchor Lock demand. The agent must emit cognitive grammar headers (TENSION/INSIGHT/SYNTHESIS) before proceeding. For the baseline pipeline (simple tasks): KVAEPH core plus single-step enforced grammar.

6. **Agent works.** Reads `.hestai/` for project context. Uses OCTAVE format for all documents. Operates within its authority boundaries.

7. **Agent hits an ambiguous decision.** Calls debate-hall for a structured Wind/Wall/Door debate. The debate produces a synthesis with a decision record. The Governance Chat panel shows the debate as a conversation thread.

8. **Agent needs lightweight advisory.** Calls an API-dispatched agent (e.g., ho-liaison on OpenRouter) for quick consultation with assistant-prefilled mini-ceremony. The response comes back within the same session — no CLI spawn needed.

9. **Agent delegates implementation work.** The agent calls `dispatch_colleague(role, task)`. The Workbench intercepts, looks up the role in the registry, compiles a fresh KVAEPH payload from the Vault, and spawns the target CLI panel or makes an API call. The subagent gets full identity injection via Alley-Oop. To the calling agent, it looks like a normal tool call.

10. **Work needs review.** The agent dispatches review agents from the registry. CRS might be mapped to Codex CLI, CE to Gemini CLI. Each reviewer receives identity-injected prompts, reviews the PR, and submits their assessment via `submit_review` (routed through hestai-context-mcp). Different models provide genuine multi-perspective review.

11. **Session ends.** The agent optionally calls `submit_friction_record` for governance feedback. Then hestai-context-mcp's clock_out archives the transcript, extracts learnings, redacts credentials, and updates the learnings index. The worktree preserves the work.

12. **Operator reviews.** The dashboard shows what was done, what decisions were made, and what's next. All artifacts are persistent and discoverable.

---

## SECTION 4: ARCHITECTURAL PRINCIPLES

These are the current best thinking about how the ecosystem should be structured. They are strong preferences, not immutable laws. If experience proves one wrong, change it.

### Separation of concerns

Each system owns exactly one concern. Identity is not context. Context is not execution. Format is not governance. The Vault owns WHO agents are (definitions, skills, cognitions). hestai-context-mcp owns MEMORY and ENVIRONMENT (sessions, context, learnings). The Workbench owns EYES and HANDS (UI, dispatch, Payload Compiler). Debate Hall owns GOVERNANCE DECISIONS. OCTAVE owns WHAT FORMAT.

### One canonical source

Agent definitions exist in exactly one place: the Vault (`~/.hestai-workbench/library/`). Not duplicated in the Workbench codebase, not embedded in hestai-context-mcp, not in debate-hall. When an agent's definition changes, it changes in one file. The Workbench's agent registry maps roles to providers — it references identity from the Vault, never duplicates it.

### Provider agnosticism

The identity layer (Vault) knows nothing about which AI model runs an agent. The context layer (hestai-context-mcp) knows nothing about providers. The execution layer (Workbench) knows nothing about what an agent's authority boundaries are. Switching providers for a role is a registry change, not a governance change.

This is not theoretical. Goose CLI agents have been verified with full MCP access across the ecosystem, including debate participation and OCTAVE read/write. Provider agnosticism is proven across Claude, Codex, Gemini, and Goose.

### Standalone deliberation

Debate Hall works without HestAI. A team that doesn't use HestAI governance can still use Wind/Wall/Door debates. This is the adoption path that makes the ecosystem viable beyond the original developer.

### Ceremony proportional to risk (Stratified Conditioning)

Not every task needs heavy governance injection. The Workbench uses two conditioning pipelines:

**Baseline pipeline** (simple, low-complexity dispatch — advisory, single-file tasks): U-Curve prompt topology plus single-step enforced grammar. System prompt contains KVAEPH core, user message contains task with MUST_USE grammar requirement. Partial benefit with initial formatting focus, no durability guarantee.

**Reliability pipeline** (T2+ tasks — multi-file refactors, TDD cycles, governance decisions): Alley-Oop pattern. The Workbench constructs synthetic conversation threading:
1. system: Dense OCTAVE KVAEPH core (identity + skills + context compiled from Vault and hestai-context-mcp)
2. user[synthetic]: Acknowledge operating constraints, authority limits, cognitive lens
3. assistant[synthetic]: Workbench-constructed static proof from Vault data (mission, authority, skills loaded)
4. user[real]: Task context + Dynamic Anchor Lock demand
5. agent[real]: MUST emit cognitive grammar headers (TENSION/INSIGHT/SYNTHESIS with skill mapping) before proceeding

The Workbench validates cognitive grammar compliance (regex) before releasing the task. This preserves the cognitive alignment that makes identity binding valuable — the agent computes strategy, engaging its reasoning — while eliminating the multi-round-trip overhead of the legacy anchor ceremony. Inject the data, force the agent to write the synthesis.

For **API-dispatched agents** (advisory roles via OpenRouter), identity injection uses **assistant prefilling**: the Workbench constructs the full system prompt, then injects a prefilled assistant turn that demonstrates cognitive alignment before the actual task is delivered. Provider-aware message construction is required, as not all OpenRouter backends handle prefilling identically.

**Legacy path**: The Odyssean Anchor MCP ceremony (5-stage KEAPH) remains operational for Claude-with-MCP sessions where agents have direct MCP access. The Alley-Oop pattern is for headless/non-MCP dispatch via the Workbench.

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

The Workbench is a Crystal fork that will eventually be rebuilt in TypeScript. The critical insight from ADR-0353: governance logic lives in hestai-context-mcp (proven Python, 92% coverage) and survives the Workbench rebuild untouched. Only a ~30-line stdio MCP client adapter needs rewriting. The dispatch logic is implemented as a clean `DispatchService` module:

- `AgentRegistryLookup` — resolves role to provider/model/dispatch mode via v_resolved_matrix
- `PayloadCompiler` — assembles KVAEPH from Vault reads + hestai-context-mcp clock_in
- `CliDispatcher` — spawns CLI panels via existing `AbstractCliManager` abstraction
- `ApiDispatcher` — makes OpenRouter API calls with assistant-prefilled mini-ceremony
- `ContinuationStore` — maps `dispatch_id` to provider-specific conversation identifiers

When the Workbench is rebuilt, the MCP tool contract (`dispatch_colleague` signature) and the `DispatchService` interface port directly. Only the Electron/UI layer changes. The 1500+ lines of governance Python in hestai-context-mcp remain untouched.

---

## SECTION 5: SUCCESS CRITERIA

The ecosystem is "done" when:

### Functional

1. **Single-command agent dispatch.** Operator picks role + provider/model -> Payload Compiler assembles KVAEPH + Alley-Oop -> agent is running with full identity injection in under 30 seconds.

2. **Cross-repo agent invocation.** An HO agent in repo A can convene agents in repos B and C for a structured debate, each on different providers/models.

3. **No duplicate agent definitions.** Exactly one canonical definition per agent role, in the Vault.

4. **Governance Chat as conversation.** Debates visible as threaded conversations in the Workbench, not raw JSON.

5. **Session continuity.** hestai-context-mcp provides persistent context across sessions via clock_in context synthesis and clock_out learnings extraction. A different agent can pick up where the first left off.

6. **Decision audit trail.** Any past decision findable via `search_decisions`, with full transcript, hash-chain proof, and synthesis.

### Quality

7. **All repos green.** Tests passing, coverage above thresholds, linters clean, type checking strict.

8. **Clean architecture.** Workbench (dispatch) + Vault (identity) + hestai-context-mcp (context) + debate-hall (deliberation) + octave-mcp (format). PAL eliminated. Legacy hestai-mcp deprecated after new system proven.

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

As of 2026-04-20:

| System | Current State | Distance | Next Step |
|--------|--------------|----------|-----------|
| **OCTAVE MCP** | v1.9.6, production, PyPI published | Close | Standalone community adoption |
| **Debate Hall** | v0.5.0, 17 tools, consult/convene/RACI shipped | Medium | Governance Hall (#163) |
| **Workbench** | v0.6.0, Step 3B Phase 2 COMPLETE 2026-04-20 (CA-BCE + unlock_work gate via #134, ApiDispatcher + ContinuationStore via #137, subagent-discipline via #147, ADR-0002 I1 Session/Dispatch ontology via 077ea0a). Phase 3 in progress: egress DAL validation, recursive dispatch_colleague, dispatch-chain UI (#82). | Medium | Complete Step 3B Phase 3 (unblocks hestai-context-mcp Phase 2 integration) |
| **Vault** | Populated library: 5 V9 agents, 16 V9 skills, 3 cognitions, System Standard | Medium | Populate as Payload Compiler demands content |
| **hestai-context-mcp** | Phase 1 COMPLETE (2026-04-17). 4 tools shipped (clock_in, clock_out, get_context, submit_review). 361 tests, 89% coverage. TranscriptParser ABC + ClaudeTranscriptParser adapter. | Medium | Phase 2: workbench Payload Compiler integration via stdio at KVAEPH Position 3 (blocked on workbench Step 3B Phase 3) |
| **hestai-mcp (legacy)** | Operational, v1.2.0, 1033 tests, maintenance mode | Maintenance | Stays for A/B comparison. NOT being absorbed. **Deprecation criterion (DECIDED):** A/B cutover via Workbench — same agent role + same real task, run once with legacy backend and once with hestai-context-mcp backend; measure judged agent output quality + total session token cost; whichever wins consistently across N tasks triggers a swift cutover. |
| **OA (legacy)** | Operational for Claude-with-MCP sessions | Maintenance | Replaced by Alley-Oop for headless dispatch |
| **PAL (legacy)** | Being eliminated | Elimination | Workbench natively replaces all dispatch |

### The Critical Path

Per workbench PROJECT-CONTEXT v1.7 build sequence:

**Step 3A** (Payload Compiler — NEXT, all prerequisites met) -> **Step 3B** (dispatch_colleague uses Payload Compiler) -> **Step 4** (Testing Lab measures baseline collapse threshold)

The convergence point is **Step 3B: dispatch_colleague** — where identity (from Vault), context (from hestai-context-mcp), and execution (Workbench dispatch) work together for the first time.

In parallel: **hestai-context-mcp Phase 1** (harvest clock_in, redesign clock_out) provides the context engine that the Payload Compiler calls at KVAEPH Position 3.

### Validated Early

- Provider agnosticism proven: Goose, Claude, Codex, Gemini all tested with full MCP ecosystem access.
- Matrix resolver (v_resolved_matrix) implemented with kernel_only column and headless experiment IPC.
- 16 V9 skills with ANCHOR_KERNEL sections created and assigned in archetype matrix.
- System Standard in vault (AP4 resolved).

### Pre-A/B Work for hestai-context-mcp (Phase 1.5)

Before the outcome-quality A/B test against legacy hestai-mcp can be meaningful, four integration-viability gaps must close. **Framing:** this is integration viability work — the Payload Compiler must be able to read both backends' responses. The systems are explicitly *allowed* to differ in their actual content; the differences are the variable being tested. This is **outcome-quality A/B**, not structural-parity A/B.

| Issue | Priority | Scope |
|-------|----------|-------|
| [#4](https://github.com/elevanaltd/hestai-context-mcp/issues/4) | P0a | Integration viability shape: add `ai_synthesis` field with fallback OCTAVE; normalise phase string to legacy's full format |
| [#5](https://github.com/elevanaltd/hestai-context-mcp/issues/5) | P0b | Port `AIClient` + `synthesize_fast_layer_with_ai` from legacy `src/hestai_mcp/modules/services/ai/` |
| [#6](https://github.com/elevanaltd/hestai-context-mcp/issues/6) | P1 | Harvest `_extract_north_star_constraints` (legacy `clock_in.py:525-583`); tests must exercise real Vault North Star format |
| [#7](https://github.com/elevanaltd/hestai-context-mcp/issues/7) | P-side | Surface distinct `conflicts` field rather than only `active_sessions` (small standalone) |

**Already implemented (NOT gaps):** ContextSteward and dynamic phase constraints (`core/context_steward.py:36-184` + tests); focus conflict detection (`core/session.py:91-128` + 4 behavioural tests).

---

## SECTION 8: ASSUMPTIONS

| ID | Assumption | Confidence | Impact | Validates By |
|----|-----------|-----------|--------|-------------|
| EA1 | Three-Service Model (Workbench + Vault + hestai-context-mcp + standalones) is sufficient | 85% | CRITICAL | Step 3B dispatch prototype |
| EA2 | Alley-Oop pattern achieves cognitive alignment equivalent to full anchor ceremony | 75% | CRITICAL | Step 3A Payload Compiler + reliability pipeline testing |
| EA3 | Stratified conditioning (baseline vs reliability) provides the right governance weight per task | 70% | HIGH | Testing Lab (Step 4) empirical measurement |
| EA4 | Workbench agent registry can natively replace all PAL dispatch (multi-CLI + API) | 80% | HIGH | Agent registry prototype with Goose + Claude + Codex + Gemini dispatch |
| EA5 | Cross-repo agent invocation is technically feasible with MCP | 75% | CRITICAL | Step 3B prototype |
| EA6 | Debate Hall Governance Hall replaces ad hoc decision-making | 70% | MEDIUM | 2 months daily use |
| EA7 | Single developer can maintain the ecosystem | 80% | CRITICAL | Post Step 3B assessment |
| EA8 | Assistant prefilling achieves sufficient cognitive alignment for API-dispatched agents | 70% | HIGH | First API dispatch with prefilled mini-ceremony on 3+ OpenRouter backends |
| EA9 | Recursive `dispatch_colleague` calls (depth 2-3) remain coherent without context degradation | 65% | HIGH | IL dispatching TMG dispatching back — full chain test with continuation |
| EA10 | Harvest approach (new repo from proven code) is faster than in-place modification | VALIDATED (95%) | HIGH | hestai-context-mcp Phase 1 delivered 4 tools + 361 tests / 89% coverage in 8 days (2026-04-09 → 2026-04-17); TranscriptParser ABC redesign proved safer than in-place patching of the broken ClaudeJsonlLens |

---

## SECTION 9: LEGACY SYSTEMS

### hestai-mcp (this repo)

**Status:** Legacy. v1.2.0, 1033 tests, maintenance mode. Stays operational for A/B comparison.

hestai-mcp is NOT being absorbed into the Workbench. ADR-0353 resolved this: the governance engine logic (clock_in, clock_out, ContextSteward, RedactionEngine, submit_review) was harvested into a NEW repo (`hestai-context-mcp`, Phase 1 complete 2026-04-17), not subtracted from here. The legacy system remains intact so the same agent + same task can be tested under both the old ceremony and the new engine.

The `_bundled_hub/` content (agent definitions, skills, standards, cognitions) moves to the Vault. The `.hestai-sys/` injection mechanism moves to the Vault/Workbench. The `bind` tool is replaced by Alley-Oop for headless dispatch; the Odyssean Anchor ceremony remains for Claude-with-MCP sessions.

**Pre-A/B blocker:** Before the outcome-quality A/B test against legacy can be meaningful, the four Pre-A/B Work items (#4, #5, #6, #7 — see Section 7) must close so the Payload Compiler can read both backends' responses. The systems are *allowed* to differ in their actual content; that difference is the variable being tested.

**Decisions (locked):**
- **Deprecation criterion:** A/B cutover via Workbench measuring outcome quality (judged) + total session token cost. Cut when the new system wins consistently across N tasks.
- **PyPI publication:** Internal-first. Publish externally only after A/B proves the system. Not publishing early.
- **Worktree pattern:** Confirmed — Workbench + worktrees, same as the current hestai-mcp workflow.

### odyssean-anchor-mcp

**Status:** Legacy for Claude-with-MCP sessions. Replaced by Alley-Oop for headless dispatch.

The 5-stage KEAPH ceremony and Steward state machine remain operational for sessions where agents have direct MCP access. For Workbench-dispatched agents (headless), the Alley-Oop pattern in the Payload Compiler provides equivalent cognitive alignment with zero round-trip overhead.

### PAL

**Status:** Being eliminated. Workbench natively replaces all dispatch.

---

## DIVERGENCE CHECK

If work moves the ecosystem away from this vision — merging context into the Workbench, duplicating agent definitions outside the Vault, building standalone GUIs for headless services, or creating new dispatch intermediaries — it's worth asking: does the vision need updating, or does the work need redirecting?

This is a question, not an order. Sometimes the vision is wrong.
