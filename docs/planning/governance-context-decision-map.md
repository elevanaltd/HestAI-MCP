# Governance & Context Architecture Decision Map

**Created**: 2026-04-05
**Purpose**: Map all unresolved architectural decisions for governance, context management, and session intelligence across the HestAI ecosystem — surface contradictions, identify gaps, and sequence decisions.
**Scope**: Cross-repo (hestai-mcp, hestai-workbench, ecosystem-wide)

---

## 1. THE DOCUMENT CONTRADICTION

Three authoritative documents give three different answers to "what happens to governance/context management":

| Document | Direction | Date | Key Claim |
|----------|-----------|------|-----------|
| **Lighthouse v3.1** | HestAI Core = standalone MCP server ("The Operating System") | 2026-03-28 | Owns context stewardship, session lifecycle, governance rules as a service |
| **Ecosystem Overview v3.0** | Thick Client = Workbench absorbs hestai-mcp | 2026-03-28 | "Governance delivery, session lifecycle, context steward tools TO workbench Engine" |
| **Workbench PROJECT-CONTEXT v1.3** | Clean Break = new system replaces hestai-mcp entirely | 2026-04-04 | "Completely independent from OA/hestai-mcp. Vault + Payload Compiler + Alley-Oop" |

The Lighthouse notes its own supersession: "Ecosystem Overview v3.0 supersedes this Lighthouse for architectural direction." But the Workbench's clean break model doesn't fully align with the Overview's absorption plan either — it envisions a vault-based system with no MCP server for governance, while the Overview envisions the Workbench *becoming* the MCP server.

**This contradiction must be resolved before building further.** Building the Payload Compiler (Step 3A) without knowing where governance/context lives means building half a system.

---

## 2. THE THREE LAYERS (AGREED)

All documents agree on what needs to exist. The disagreement is about WHO provides each layer:

| Layer | Content | Examples | Status |
|-------|---------|----------|--------|
| **Agent Identity** | Who the agent is, how it thinks | Agent defs, skills, cognitions, archetypes | DECIDED: Vault at `~/.hestai-workbench/library/` |
| **System Laws** | Immutable constitutional principles | System Standard, System North Star | DECIDED: Vault at `vault/standards/`, compiled at KVAEPH Position 0 |
| **Project Rules** | How THIS project works | Naming conventions, review requirements, coding standards | UNDECIDED: Where does this live and who serves it? |
| **Project State** | Dynamic context for THIS project right now | Current phase, active blockers, recent decisions, focus | UNDECIDED: Where does this live and who maintains it? |
| **Session Intelligence** | What happened in past sessions | Learnings, decision records, archived transcripts | UNDECIDED: Who extracts, indexes, and serves this? |

---

## 3. THE TWO NORTH STARS PROBLEM

There are two North Stars that agents need:

| North Star | Scope | Example | Current Location | Injection |
|------------|-------|---------|-----------------|-----------|
| **System North Star** | Universal, all projects | "Structural integrity over velocity", I1-I6 immutables | `.hestai-sys/standards/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md` | hestai-mcp bundled hub injection |
| **Product North Star** | Per-project | "This project is at B1 phase, these immutables apply" | `.hestai/north-star/000-MCP-PRODUCT-NORTH-STAR-SUMMARY.oct.md` | `load-north-star-summary.sh` hook (Claude-only) |

**Problems:**
1. The hook (`~/.claude/hooks/session_start/load-north-star-summary.sh`) only works for Claude
2. In the new system, System NS goes to vault at KVAEPH Position 0. Product NS goes to... ???
3. These are complementary (system = values, product = state), but no document describes how agents receive BOTH
4. The hook will need to be removed once the Workbench handles injection

**Resolution needed:** Product North Star injection at KVAEPH Position 3 (CONTEXT). The Payload Compiler must know to look for it. This means the "configurable project context path" (Option 2) must include the Product North Star path by convention or configuration.

---

## 4. UNRESOLVED DECISIONS

### Decision D1: Thick Client vs Governance Engine

**The core architectural question**: Does governance/context management live INSIDE the Workbench (Thick Client) or as a SEPARATE service (Governance Engine)?

| | Thick Client (Overview v3.0) | Governance Engine (Lighthouse concept) |
|---|---|---|
| **Architecture** | Workbench backend handles clock_in/out, context synthesis, governance injection | Standalone MCP server handles governance/context. Workbench calls it. |
| **Pro** | Single debug target. No IPC latency. Glass UI has direct data access. | Works without Workbench (terminal users). Provider-agnostic by nature. Survives Workbench rebuild. |
| **Pro** | Solo developer — federation complexity is unnecessary. | Composable — any system can call the governance engine. |
| **Con** | Governance ONLY works through Workbench. No terminal fallback. | Extra process to maintain. IPC overhead. |
| **Con** | Workbench is a Crystal fork with planned rebuild. Governance logic must survive. | Keeps Python codebase alive alongside TypeScript workbench. |
| **Con** | TypeScript port of 955-line clock_in + 260-line clock_out + ContextSteward. | "Federation is accumulative complexity" (Thick Client rationale). |

**The Rebuild Factor**: The Workbench is explicitly a Crystal fork that will be rebuilt. The Dependency Graph's "rebuild-portable dispatch" section acknowledges this — it designs the DispatchService interface to survive a rebuild. But governance/context is MORE complex than dispatch. If it's embedded in the Workbench, it must also survive the rebuild. If it's a separate service, it already survives.

**The Terminal Factor**: If governance ONLY works through the Workbench, then anyone using Claude CLI directly (without the workbench) gets nothing. Currently, with hestai-mcp as a separate MCP server, you get governance regardless of how you access Claude. The Thick Client model assumes ALL AI work goes through the Workbench.

**Recommendation**: This decision should go through a structured debate (Wind/Wall/Door). The tradeoffs are real and the current documents disagree. Neither option is obviously wrong.

---

### Decision D2: Where Does Project Governance Data Physically Live?

**Options:**

| Option | Data Location | Who Reads It | Who Writes It |
|--------|--------------|-------------|---------------|
| **A: In-repo `.hestai/`** | `.hestai/north-star/`, `.hestai/rules/`, `.hestai/state/context/` | Workbench reads paths, injects at KVAEPH 3 | System Steward tools (ADR-0033 pattern) or direct agent writes (current reality) |
| **B: Workbench SQLite** | Per-project settings in Workbench database | Workbench reads directly | Workbench UI (Glass) |
| **C: Hybrid** | Stable rules in `.hestai/` (committed). Dynamic state managed by a service. Workbench points to both. | Workbench reads `.hestai/` for rules, service for state | Rules via PRs, state via governance engine/workbench |

**Current reality**: Option A exists today. `.hestai/` directories live in project repos. But the "single writer" pattern from ADR-0033 was NEVER enforced — agents write directly to `.hestai/` all the time. The `document_submit` and `context_update` tools listed in ADR-0033 were never built (Phase 3, never reached).

**Recommendation**: Option C (Hybrid). Stable project governance (North Star, rules, decisions) stays in `.hestai/` — it IS the project, versioned in git. Dynamic state (sessions, context, focus) is managed by whichever system owns D1. The Workbench's project settings point to the governance paths.

---

### Decision D3: Session Intelligence Pipeline

**What hestai-mcp does today:**

| Capability | Implementation | Lines of Code |
|-----------|----------------|---------------|
| Session start with context synthesis | clock_in: focus resolution, conflict detection, AI synthesis | 955 |
| Session end with knowledge extraction | clock_out: transcript parsing, credential redaction, OCTAVE compression, learnings indexing | 260 |
| Learnings search | learnings-index.jsonl with structured DECISION/BLOCKER/LEARNING keys | ~100 |
| Context synthesis | ContextSteward: dynamic PhaseConstraints from operational workflow | ~200 |

**What the Workbench has today:**
- Session create, run, continue, archive
- No knowledge extraction
- No learnings indexing
- No credential redaction
- No context synthesis
- No focus conflict detection

**Gap**: The Workbench manages session LIFECYCLE (start/stop) but not session INTELLIGENCE (learn from sessions). This is I1 (Persistent Cognitive Continuity) — the first immutable in the North Star.

**Decision needed**: Build session intelligence in:
- (a) Workbench backend (TypeScript port of clock_in/clock_out intelligence)
- (b) Governance Engine MCP (refine existing Python implementation)
- (c) Shared library consumed by both

**Dependencies**: This decision depends on D1. If Thick Client, then (a). If Governance Engine, then (b).

---

### Decision D4: Single-Writer Enforcement

**Current state**: The single-writer pattern (ADR-0033) exists as architecture documentation but was NEVER implemented:
- `document_submit` tool: never built (Phase 3)
- `context_update` tool: never built (Phase 3)
- Pre-commit hook to block direct `.hestai/` writes: never implemented
- Agents write to `.hestai/` directly all the time

**The `.hestai-sys/` model IS enforced**: read-only permissions (chmod 444/555), SHA-256 integrity hashing, tamper detection with self-healing, runtime injection from bundled hub. This works because the MCP server controls the delivery.

**Decision needed**: Do we actually need single-writer enforcement for `.hestai/`?

| Option | Description | Tradeoff |
|--------|-------------|----------|
| **Enforce** | Build the tools, add pre-commit hooks, route all writes through a gatekeeper | Prevents conflicts, enables validation, but adds friction |
| **Accept direct writes** | Agents write to `.hestai/` freely. Tools exist for convenience, not enforcement | Simple, works today, but risks corruption and conflicts |
| **Soft enforcement** | Tools are the recommended path. Validation runs on read (detect corruption). No hard blocks | Pragmatic middle ground |

**Recommendation**: Soft enforcement. The current system works without hard enforcement. Add validation-on-read to detect issues rather than blocking writes.

---

### Decision D5: submit_review Location

**Current**: submit_review is an MCP tool in hestai-mcp. It posts structured review comments to GitHub PRs, clears CI review gates, supports 8 reviewer roles, dry-run validation, commit SHA pinning.

**Options:**

| Option | Where | Rationale |
|--------|-------|-----------|
| **A: Workbench** | Part of dispatch chain — when review agent finishes, Workbench submits | Natural integration with dispatch chain visibility (#82) |
| **B: Governance Engine** | MCP tool accessible to any agent | Provider-agnostic, works without Workbench |
| **C: Standalone** | Small dedicated MCP or CLI tool | Minimal, composable |

**Recommendation**: Depends on D1. If Thick Client then A. If Governance Engine then B.

---

### Decision D6: Orchestra Map Integration

**Current**: ADR-0034 validated (85% confidence). Python PoC exists. Anchor Pattern Inversion works. But:
- Not integrated into any workflow
- No slot in the Payload Compiler's KVAEPH stack
- No agent queries "what breaks if I change this?"
- No CI gate for stale specs

**Decision needed**: When and where does impact awareness get integrated?

**Recommendation**: Not now (Order 400+). But the Payload Compiler at Position 3 (CONTEXT) should have an EXTENSIBLE slot for "impact context" that can be populated later. Don't build the Orchestra Map integration yet, but don't design an architecture that precludes it.

---

### Decision D7: Project Rules UI in the Workbench

**User's question**: Should the Workbench have:
- A **global rules tab** (vault-level, all projects)
- A **project rules tab** (per-project, specific to this repo)

**Mapping:**

| Tab | Content | Data Source | KVAEPH Position |
|-----|---------|-------------|-----------------|
| **Global Rules** | System Standard, universal patterns, system North Star | Vault: `vault/standards/` | Position 0 (AXIOMS) |
| **Agent Library** | Agent defs, cognitions, skills, archetypes | Vault: `vault/agents/`, `vault/cognitions/`, etc. | Position 1-2 (IDENTITY, CAPABILITIES) |
| **Project Rules** | Coding standards, review requirements, naming conventions, Product North Star | Project repo: `.hestai/north-star/`, `.hestai/rules/` | Position 3 (CONTEXT) — stable |
| **Project State** | Current focus, phase, blockers, recent decisions | `.hestai/state/context/` or dynamic synthesis | Position 3 (CONTEXT) — dynamic |

**Recommendation**: The Workbench project settings should have a **"Governance" section** with:
1. A list of governance file paths for this project (defaults: `.hestai/north-star/`, `.hestai/rules/`, `CLAUDE.md`)
2. These paths get compiled into KVAEPH Position 3 at dispatch time
3. A future "Project Context" panel can show dynamic state

This is lightweight, doesn't require new file formats, and works with existing `.hestai/` conventions.

---

## 5. CAPABILITIES THAT NEED A HOME

Regardless of D1 (Thick Client vs Governance Engine), these capabilities must exist SOMEWHERE:

| Capability | North Star Immutable | hestai-mcp Today | New System Home | Status |
|-----------|---------------------|------------------|----------------|--------|
| Agent identity compilation | I5 | bundled_hub + .hestai-sys injection | Vault + Payload Compiler | DECIDED |
| System Standard injection | I2 | bundled_hub | Vault/standards/ | DECIDED (AP4 pending) |
| Product North Star injection | I2 | load-north-star-summary.sh hook | **NEEDS DECISION** (D2, D7) | Unresolved |
| Session start with context | I1, I4 | clock_in (955 lines) | **NEEDS DECISION** (D1) | Unresolved |
| Session end with learnings | I1 | clock_out (260 lines) | **NEEDS DECISION** (D1, D3) | Unresolved |
| Learnings search | I1 | learnings-index.jsonl | **NEEDS DECISION** (D3) | Unresolved |
| Context synthesis | I4 | ContextSteward | **NEEDS DECISION** (D1) | Unresolved |
| Focus conflict detection | I2 | pending_sessions.py | **NEEDS DECISION** (D1) | Unresolved |
| Credential redaction | Security | RedactionEngine | **NEEDS DECISION** (D3) | Unresolved |
| Review submission | Quality | submit_review | **NEEDS DECISION** (D5) | Unresolved |
| Governance enforcement | I3 | .hestai-sys integrity + (unenforced) single-writer | **NEEDS DECISION** (D4) | Unresolved |
| Impact awareness | I4 | ADR-0034 PoC | **NEEDS DECISION** (D6) | Unresolved (future) |
| Opt-in detection | I6 | .hestai/ exists or env var | **NEEDS DECISION** | Unresolved |

---

## 6. RECOMMENDED DECISION SEQUENCE

These decisions have dependencies. The recommended sequence:

```
D1: Thick Client vs Governance Engine        ← THE CRITICAL DECISION
 ├── Blocks: D3, D5 (where session intelligence and review live)
 ├── Informs: D4 (enforcement model)
 └── Independent of: D2, D6, D7

D2: Project Governance Data Location
 ├── Independent of D1
 ├── Informs: D7 (what the UI points to)
 └── Can be decided now → Hybrid (Option C)

D7: Project Rules UI
 ├── Depends on: D2
 └── Can be designed now, built during Step 3A

D3: Session Intelligence Pipeline
 ├── Depends on: D1
 └── Build after D1 is resolved

D4: Single-Writer Enforcement
 ├── Informed by: D1
 └── Can default to soft enforcement now

D5: submit_review Location
 ├── Depends on: D1
 └── Build after D1 is resolved

D6: Orchestra Map Integration
 └── Future (Order 400+). Just ensure extensible CONTEXT slot.
```

**Therefore: D1 is the critical decision.** Everything else either depends on it or can be resolved independently. D1 should be resolved through a structured debate before proceeding with Step 3A implementation.

---

## 7. THE HONEST ASSESSMENT

### Have we lost sight of the bigger picture?

**Partially, yes.**

The Workbench clean break correctly identified that the PROMPT PIPELINE needed rearchitecting (vault → engine → CLI dispatch). That's right. Keep it.

But the clean break treated hestai-mcp as primarily "identity injection + anchor ceremony" when it's ALSO:
1. A **knowledge accumulation system** (I1 — Persistent Cognitive Continuity)
2. A **dynamic context synthesizer** (I4 — Freshness Verification)
3. A **governance enforcement layer** (I3 — Dual-Layer Authority)
4. **Review infrastructure** (quality gates)
5. A future home for **impact awareness** (I4 — System Boundary Awareness)

The Ecosystem Overview v3.0 acknowledges these transfer to the Workbench, but the Workbench's own PROJECT-CONTEXT doesn't account for them in its build sequence. Step 3A (Payload Compiler) and Step 3B (dispatch_colleague) address the prompt pipeline. Steps for session intelligence, context synthesis, and governance enforcement don't appear.

### The gap in the Workbench build plan

The Workbench build sequence goes:
```
Step 1: Agent Registry ✅
Step 2: Library Manager ✅
Step 2B: Library Vault ✅
Step 3A: Payload Compiler ← NEXT
Step 3B: dispatch_colleague
Step 4: Testing Lab
```

Missing from this sequence:
- Session intelligence (knowledge extraction, learnings indexing)
- Context synthesis (dynamic project state for Position 3)
- Governance enforcement (single-writer or alternative)
- Review infrastructure (submit_review equivalent)

These aren't addressed in the Workbench build plan OR tracked as future steps. They exist only in hestai-mcp.

### What's safe to build now

Despite unresolved D1, some work is safe because it's needed regardless:

1. **Payload Compiler (Step 3A)** — compiles KVAEPH from vault. Position 3 slot should be EXTENSIBLE (accept multiple paths, not hardcoded to one file).
2. **Project Settings: Governance Paths** — UI for configuring which files get compiled at Position 3. Default: `.hestai/north-star/`, `.hestai/rules/`, `CLAUDE.md`.
3. **Remove load-north-star-summary.sh dependency** — once the Payload Compiler handles Position 3, the hook is dead code.
4. **Dispatch (Step 3B)** — uses Payload Compiler output. Independent of governance.

What's NOT safe to build without resolving D1:
- Session intelligence (where does knowledge extraction live?)
- Context synthesis (who synthesizes dynamic project state?)
- `.hestai/state/` writer (Workbench backend or external service?)

---

## 8. D1 DEBATE OUTCOME (2026-04-06)

Two parallel Wind/Wall/Door debates were run on D1 — standard tier and premium tier — with the full decision map as context.

### Result: Directional convergence on Governance Engine via Stdio (Wall CONDITIONAL)

**Both tiers converged on the Governance Engine architecture**, with Wall issuing CONDITIONAL (requiring mitigations before production commitment). Debates ended in stalemate — Wind voted YES, Wall voted NO (CONDITIONAL), and Door produced syntheses favouring the Governance Engine but did not formally vote (debate-hall protocol: Door synthesizes, does not vote). Human judgment accepted the architectural direction based on directional agreement across all synthesis attempts.

**Standard tier** named it: "Stateless Stdio Orchestration (The Git/VS Code Model)"
**Premium tier** named it: "The Adapter Pattern Data Plane (Strict Governance Isolation)"

Architecture: `hestai-context-mcp` (refined Python MCP over stdio) + Workbench (consumer adapter) + Vault (identity). The Workbench spawns the governance engine as a subprocess (like VS Code spawns Git) — zero network overhead, zero daemon management, same DX as a monolith but structurally decoupled.

### Key Arguments That Won

1. **Subtraction yields negative complexity.** Removing identity injection and anchor ceremony from hestai-mcp is LESS code, not more federation.
2. **Stdio eliminates federation concerns.** Not a networked daemon — a subprocess. No ports, no HTTP, no daemon lifecycle.
3. **Rebuild survival is structural.** When Workbench migrates Crystal→TS, only a ~30-line stdio MCP client adapter needs rewriting. The 1500+ LOC Python governance logic survives untouched.
4. **Terminal parity for clock_in is automatic.** CLI users configure `hestai-context-mcp` as a stdio MCP server — identical context injection regardless of entry point. clock_out transcript parsing is currently Claude-only; provider adapters needed for full lifecycle parity.

### Document Contradiction Resolution

- **Lighthouse v3.1**: Upheld — governance remains standalone System Steward
- **Ecosystem Overview v3.0**: Corrected — Workbench absorbs UX routing and dispatch, NOT the governance engine
- **PROJECT-CONTEXT v1.3**: Validated — Vault handles identity injection, enabling the clean break from that concern

### Wind's Heretical Insight: "D1 Is Three Decisions"

Wind (standard tier, Path 3) proposed that governance isn't one decision but three:
- **D1a** (compile-time): Context synthesis, focus resolution → Payload Compiler phase or MCP call
- **D1b** (post-session): Transcript parsing, redaction, learnings → async pipeline
- **D1c** (write-time): Single-writer enforcement → git hooks, not runtime

This decomposition was not fully validated by Wall but was acknowledged as "conceptually plausible." The overlap between clock_in output and KVAEPH Position 3 requirements should be tested.

### Wall's Conditions (Required Before Implementation)

Both Walls issued CONDITIONAL_GO, requiring:
1. Formal ADR resolving the three-document architectural contradiction
2. Stable interface contract for governance MCP tool endpoints
3. Feature-parity matrix with tests for all current hestai-mcp capabilities
4. Terminal parity proof (full lifecycle via CLI without Workbench)
5. Explicit abandonment of ADR-0033's never-built `document_submit` runtime gatekeeper
6. Credential-redaction equivalence test corpus before any migration

### Agreed Implementation Phases

| Phase | Action | Description |
|-------|--------|-------------|
| 1. Harvest | Create `hestai-context-mcp` | New repo. Harvest proven System Steward code from hestai-mcp. Build with clean TDD. Legacy stays intact for A/B comparison. |
| 2. Orchestration | Workbench as consumer | Thin subprocess adapter in Payload Compiler. Spawn `python -m hestai_context_mcp` via stdio. Inject `clock_in` output at KVAEPH Position 3. |
| 3. North Star | Unify injection | System NS from vault (static). Product NS from `hestai-context-mcp` during `clock_in` (dynamic). Kill `load-north-star-summary.sh`. |
| 4. Enforcement | Git, not services | Abandon ADR-0033 runtime gatekeeper. Deploy `.githooks/pre-commit` for `.hestai/` validation. |

### Debate Records

Thread IDs (files at `debates/{thread_id}.events.jsonl`):

- Standard: `2026-04-06-d1-thick-client-vs-governance-engine-standard`
- Premium: `2026-04-06-d1-thick-client-vs-governance-engine-premium`

---

## 9. NEXT MOVES (POST-DEBATE)

1. **Write ADR** resolving the three-document contradiction, adopting the Three-Service Model
2. **Resolve D2** — Hybrid (Option C) is safe and aligned with debate outcome
3. **Build Step 3A** with extensible Position 3 that queries `hestai-context-mcp` for dynamic context
4. **Begin Phase 1** (Subtraction) in hestai-mcp — strip identity injection, expose System Steward via stdio
5. **Update Ecosystem Overview and Lighthouse** to align with debate outcome
6. **Track Wall's mitigations** as blocking issues before production commitment
