# ADR-0353: Three-Service Model — Governance Engine via Stdio

**Status**: ACCEPTED
**Date**: 2026-04-06
**Author**: Human + Claude Opus 4.6 (analysis + debate orchestration)
**Reviewers**: Wind/Wall/Door debates (standard + premium tier)
**GitHub Issue**: [#353](https://github.com/elevanaltd/HestAI-MCP/issues/353)
**Supersedes**: Ecosystem Overview v3.0 §0 ARCHITECTURE_NOTE (Thick Client absorption model)
**Upholds**: Lighthouse v3.1 §2 Layer 1 (standalone governance service)
**Validates**: Workbench PROJECT-CONTEXT v1.3 clean break (for identity injection only)

---

## Context

### The Problem: Three Documents, Three Directions

Three authoritative ecosystem documents gave contradictory answers to "what happens to governance/context management":

| Document | Direction | Claim |
|----------|-----------|-------|
| **Lighthouse v3.1** | Standalone service | HestAI Core owns context stewardship, session lifecycle, governance rules as an independent MCP server |
| **Ecosystem Overview v3.0** | Thick Client absorption | Workbench absorbs hestai-mcp entirely — session lifecycle, context steward, governance delivery all transfer to Workbench Engine |
| **Workbench PROJECT-CONTEXT v1.3** | Clean break replacement | New system is "completely independent from OA/hestai-mcp" — Vault + Payload Compiler replaces everything |

This contradiction blocked the Payload Compiler build (Step 3A) because Position 3 (CONTEXT) of the KVAEPH stack had no authoritative source.

### The Root Cause: Conflating Identity with Context

The Workbench clean break correctly solved **Identity Injection** — a stateless string-compilation problem (vault reads agent file → compiler assembles KVAEPH → CLI receives prompt). This works.

But the clean break mistakenly assumed this also solved **State Management** — a highly stateful, cross-session orchestration problem (session lifecycle, knowledge extraction, transcript redaction, learnings indexing, context synthesis, focus conflict detection). These are fundamentally different concerns:

| Concern | Nature | Example | Solved By |
|---------|--------|---------|-----------|
| Identity Injection | Stateless compilation | "Compile agent def + skills into prompt" | Vault + Payload Compiler |
| State Management | Stateful orchestration | "Extract learnings from session, detect focus conflicts, redact credentials" | ??? (this ADR) |

### What hestai-mcp Actually Provides

Beyond identity injection, hestai-mcp provides 1500+ lines of proven Python logic:

- **clock_in** (955 lines): Session creation, focus resolution from git branches, AI-synthesized context summaries, focus conflict detection across concurrent sessions
- **clock_out** (260 lines): Transcript parsing (ClaudeJsonlLens), credential redaction (RedactionEngine), OCTAVE compression, structured learnings indexing (DECISION/BLOCKER/LEARNING keys)
- **ContextSteward** (~200 lines): Dynamic PhaseConstraints synthesis from operational workflow
- **submit_review**: Structured code review verdicts with CI gate clearing, 8 reviewer roles, dry-run validation, commit SHA pinning
- **Governance integrity**: .hestai-sys/ SHA-256 hashing, chmod 444/555, tamper detection, self-healing

The Workbench has session create/run/continue/archive but NONE of the intelligence layer: no knowledge extraction, no learnings indexing, no credential redaction, no context synthesis, no focus conflict detection.

### Evidence: Two Parallel Debates

Two Wind/Wall/Door debates were run (standard + premium tier) with the full decision map as context. Both converged on the Governance Engine model, with debates ending in "stalemate" status. Vote record: Wind voted YES, Wall voted NO (CONDITIONAL — requiring mitigations M1-M6), Door produced syntheses favouring the Governance Engine but did not formally vote (per debate-hall protocol, Door synthesizes rather than votes). Human judgment accepted the architectural direction based on directional alignment across all synthesis attempts, despite Wall's implementation-readiness conditions remaining unmet at time of decision.

- Standard tier: "Stateless Stdio Orchestration (The Git/VS Code Model)"
- Premium tier: "The Adapter Pattern Data Plane (Strict Governance Isolation)"
- Debate records: `2026-04-06-d1-thick-client-vs-governance-engine-standard` and `premium`

---

## Decision

### The Three-Service Model

The HestAI ecosystem adopts a three-service architecture where each service owns exactly one concern:

```text
┌─────────────────────────────────────────────────┐
│ WORKBENCH (Node/Crystal → future TypeScript)    │
│                                                  │
│ Role: The Eyes and Hands                        │
│ Owns: UI, dispatch, Payload Compiler (KVAEPH)   │
│ Authority: NONE over governance state            │
│ Volatility: HIGH (planned framework rebuild)     │
│                                                  │
│ Spawns via stdio ────────────────────────┐      │
└──────────────────────────────────────────┼──────┘
                                           │
                              ┌─────────── ▼ ──────────────┐
                              │ hestai-context-mcp (Python) │
                              │                             │
                              │ Role: The Memory and        │
                              │       Environment           │
                              │ Owns: Session lifecycle,    │
                              │   context synthesis,        │
                              │   learnings extraction,     │
                              │   submit_review,            │
                              │   .hestai/ state mgmt       │
                              │ Authority: ABSOLUTE over    │
                              │   project state             │
                              │ Volatility: LOW (proven     │
                              │   Python, 92% coverage)     │
                              │ Transport: stdio MCP        │
                              └─────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ VAULT (Git-backed, ~/.hestai-workbench/library/)         │
│                                                           │
│ Role: The DNA                                            │
│ Owns: Agent definitions, skills, cognitions, standards   │
│ Authority: ABSOLUTE over identity (read-only at runtime) │
│ Volatility: ZERO (git-backed, immutable at runtime)      │
└──────────────────────────────────────────────────────────┘
```

### How It Works

**Dispatch flow (Workbench-initiated):**
1. User selects agent + task in Glass UI
2. Payload Compiler reads vault for Positions 0-2 (BIOS, IDENTITY, CAPABILITIES)
3. Payload Compiler calls `hestai-context-mcp` via stdio for Position 3 (CONTEXT) — clock_in returns context synthesis, Product North Star, project state
4. Compiler assembles full KVAEPH payload
5. Workbench dispatches to CLI tool with compiled prompt
6. On session end, Workbench calls `hestai-context-mcp` clock_out — learnings extracted, transcript redacted, index updated

**Terminal flow (direct CLI):**
1. User configures `hestai-context-mcp` as stdio MCP server in their CLI config
2. Agent calls clock_in directly — identical context synthesis
3. Agent works with full governance
4. Agent calls clock_out — knowledge extraction (currently Claude-only transcript parsing; provider adapters needed for Codex/Gemini/Goose — see §Known Gap)
5. No Workbench required. Context injection is provider-agnostic; transcript extraction requires provider adapters.

### Key Properties

**Stdio transport eliminates federation concerns.** This is not a networked daemon. The Workbench spawns `python -m hestai_context_mcp` as a subprocess communicating over stdin/stdout — identical to how VS Code spawns Git. Zero network ports, zero daemon lifecycle, zero monitoring overhead. The process dies when the session closes.

**Harvest, not rewrite.** `hestai-context-mcp` is a new repo that harvests the proven System Steward code from `hestai-mcp`. The legacy system stays intact for A/B comparison:

| NOT harvested (stays in legacy / moves to Vault) | Harvested (System Steward core) |
|--------------------------------------------------|-------------------------------|
| `_bundled_hub/` (144 files) → Vault | `clock_in` (session/context logic) |
| `.hestai-sys/` injection → Vault/Workbench | `clock_out` (knowledge extraction) |
| `.hestai-sys/` integrity enforcement (SHA-256, chmod) → Vault | `ContextSteward` (phase constraints) |
| Agent definition serving → Vault | `RedactionEngine` (credential safety) |
| Anchor ceremony support (`bind`) → Alley-Oop | `learnings-index.jsonl` pipeline |
| | `submit_review` |
| | `pending_sessions` conflict detection |

**Implementation**: Create `elevanaltd/hestai-context-mcp` as a new repo, harvest the proven code, build with clean TDD. Legacy `hestai-mcp` stays intact — enabling A/B testing of old ceremony vs new engine until the new system is proven.

**Rebuild survival is structural.** When the Workbench migrates Crystal → TypeScript, only a ~30-line stdio MCP client adapter needs rewriting. The 1500+ lines of Python governance logic survive untouched. The existing 930 tests and 92% coverage continue to protect the pipeline.

**Terminal parity is automatic.** Because governance is a standard MCP server, CLI users get identical governance by adding one entry to their MCP config. No Workbench required. This preserves the current workflow where `hestai-mcp` provides governance regardless of entry point.

---

## Document Contradiction Resolution

| Document | Verdict | Explanation |
|----------|---------|-------------|
| **Lighthouse v3.1** | **UPHELD** | HestAI Core (now `hestai-context-mcp`) remains a standalone service owning context stewardship, session lifecycle, governance rules. The Lighthouse's vision was correct. |
| **Ecosystem Overview v3.0** | **CORRECTED** | The Workbench absorbs UX routing and dispatch (correct), but NOT the governance engine. §0 ARCHITECTURE_NOTE's "Thick Client absorption" is superseded. The on-disk structure (§6) remains unchanged — only the writer changes for identity (.hestai-sys/ written by Workbench from vault), while state (.hestai/state/) continues to be managed by the governance engine. |
| **Workbench PROJECT-CONTEXT v1.3** | **VALIDATED** | The clean break is correct for identity injection — Vault + Payload Compiler replaces the bundled hub and anchor ceremony. But the clean break does NOT extend to state management. The Workbench consumes governance state from `hestai-context-mcp`, it does not replace it. |

---

## The Two North Stars

This ADR resolves the dual North Star injection problem:

| North Star | Source | KVAEPH Position | Served By |
|------------|--------|-----------------|-----------|
| System North Star | `vault/standards/000-SYSTEM-HESTAI-NORTH-STAR.md` | Position 0 (AXIOMS) | Vault (static, read by Payload Compiler) |
| Product North Star | `.hestai/north-star/000-*-NORTH-STAR*.md` | Position 3 (CONTEXT) | `hestai-context-mcp` (dynamic, served during clock_in) |

The `load-north-star-summary.sh` hook becomes dead code once the Payload Compiler handles Position 3 via the governance engine.

## Universal Standards in the Vault

Universal governance rules (naming-standard, test-structure-standard, visibility-rules) currently live in `.hestai-sys/standards/rules/` (injected by hestai-mcp's bundled hub). In the new system, these move to the **Vault** at `~/.hestai-workbench/library/standards/`.

The Payload Compiler reads `vault/standards/` and injects everything at KVAEPH Position 0 (AXIOMS) alongside the System Standard and System North Star. Agents receive universal rules in their compiled prompt — no separate injection mechanism needed. This requires populating the vault's `standards/` directory as part of AP4 prep (currently empty with `.gitkeep`).

## Known Gap: clock_out Provider Parity

`clock_out` currently parses only Claude JSONL transcripts via `ClaudeJsonlLens`. Terminal parity for clock_in (context injection) is immediate — any CLI tool can call clock_in and receive identical context. But clock_out's knowledge extraction pipeline is Claude-specific.

**Future work**: Abstract transcript parsing via adapter pattern to support Codex, Gemini, and Goose transcript formats. The Workbench stores its own session logs at `~/.hestai-workbench/logs/` but these are application-level logs (Electron process events), not agent session transcripts. Each CLI tool stores transcripts in its own format and location. The adapter pattern for multi-provider transcript parsing is a Phase 2 concern, not a blocker for Phase 1.

---

## Enforcement Model

### ADR-0033 Single-Writer: Abandoned as Runtime Gatekeeper

ADR-0033's `document_submit` and `context_update` tools were never built (listed as "Phase 3", never reached). The pre-commit hook to block direct `.hestai/` writes was never implemented. Agents write to `.hestai/` directly today — the system works.

**New enforcement model: Git hooks, not runtime gatekeepers.**

- `.hestai-sys/` enforcement: **Moves to the Vault/Workbench.** The Workbench writes `.hestai-sys/` from the vault at session spawn (same files, different writer). Integrity is guaranteed by the vault being git-backed and the Workbench controlling the write. `hestai-context-mcp` will NOT manage `.hestai-sys/` — that responsibility will transfer in Phase 2 when the Workbench Payload Compiler is operational. (Current `hestai-mcp` still manages `.hestai-sys/` until the harvest is complete.)
- `.hestai/` enforcement: Git pre-commit validation (detect malformed OCTAVE, validate naming conventions) — uses repository physics, not synthetic bureaucracy
- Single-writer is a recommendation, not a runtime lock. Validation-on-read catches corruption.

This follows the MIP principle: enforcement through the native physics of the repository (git hooks) rather than adding layers of synthetic software.

---

## Implementation Phases

| Phase | Action | Description | Blocks |
|-------|--------|-------------|--------|
| **1. Harvest** | Create `hestai-context-mcp` | New repo (`elevanaltd/hestai-context-mcp`). Harvest System Steward code from hestai-mcp. Build with clean TDD. Legacy hestai-mcp stays intact for A/B comparison. | Phase 2 |
| **2. Orchestration** | Workbench as consumer | Thin stdio MCP client in Payload Compiler. Spawn `python -m hestai_context_mcp` via stdio. Inject clock_in output at KVAEPH Position 3. | Phase 3 |
| **3. North Star** | Unify injection | System NS from vault (static). Product NS from `hestai-context-mcp` during clock_in (dynamic). Remove `load-north-star-summary.sh`. | Phase 4 |
| **4. Enforcement** | Git, not services | Deploy `.githooks/pre-commit` for `.hestai/` OCTAVE validation. Formally deprecate ADR-0033 Phase 3 tools. | — |

**Why harvest, not subtract**: Modifying hestai-mcp in place destroys the comparison baseline. Creating a new repo preserves the legacy system for A/B testing (same agent, same task, old ceremony vs new engine). Legacy hestai-mcp is deprecated only after the new system is proven in daily use — matching the "two parallel systems" approach already established in the Workbench PROJECT-CONTEXT.

### Wall's Conditions (Required Before Production Commitment)

Per both debate outcomes, the following mitigations must be satisfied:

| ID | Condition | Status |
|----|-----------|--------|
| M1 | Formal ADR resolving document contradiction | **This ADR** |
| M2 | Stable interface contract for governance MCP endpoints | **DONE** (`docs/planning/hestai-context-mcp-interface-contract.md`) |
| M3 | Feature-parity matrix with tests | **DONE** (interface contract §7, annotated with test status) |
| M4 | Terminal parity proof (full lifecycle via CLI without Workbench) | Pending (requires Phase 1 harvest) |
| M5 | Credential-redaction equivalence test corpus | Existing (RedactionEngine tests) |
| M6 | Explicit ADR-0033 Phase 3 deprecation | **This ADR §Enforcement** |

---

## Alternatives Considered

### Alternative 1: Thick Client (Ecosystem Overview v3.0)

Workbench absorbs all of hestai-mcp including session lifecycle and context steward.

**Rejected because:**
- Governance only works through Workbench — terminal users lose all governance
- Workbench is a Crystal fork with planned rebuild — governance logic must survive the rewrite
- TypeScript port of 1500+ lines of proven Python (credential redaction, OCTAVE compression) introduces regression risk
- "Single debug target" advantage is negated by stdio subprocess (same DX, structural isolation)

### Alternative 2: Full Clean Break (Workbench PROJECT-CONTEXT v1.3)

Vault + Payload Compiler replaces everything. hestai-mcp retires completely.

**Rejected because:**
- The clean break only solves identity injection (stateless compilation)
- It has no answer for state management (session intelligence, learnings, context synthesis)
- 13 capabilities identified in the decision map have no planned home
- I1 (Persistent Cognitive Continuity) — the first North Star immutable — would be unimplemented

### Alternative 3: Library Pattern (Wind Path 2)

Governance logic as an importable library consumed by any host.

**Deferred because:**
- The language boundary (Python → TypeScript Workbench) recreates the subprocess bridge anyway
- If a bridge is needed regardless, MCP over stdio is strictly better (standardized protocol, no custom FFI)
- No repo evidence of existing shared-library boundary or packaging proof
- Can be revisited if the governance engine is eventually ported to TypeScript

### Alternative 4: Governance as Compiler Phase (Wind Path 3)

Clock_in is really just pre-session payload compilation. Merge it into the Payload Compiler.

**Noted for future investigation because:**
- Conceptually plausible — clock_in output and KVAEPH Position 3 may overlap >80%
- But clock_out, learnings indexing, and credential redaction are definitively NOT compile-time operations
- The temporal decomposition (compile-time vs post-session vs write-time) should be tested
- If overlap is confirmed, Phase 1 compile-time operations could migrate to the Payload Compiler in future

---

## Consequences

### Positive

- **Architectural clarity**: Each service owns exactly one concern. No overlap, no ambiguity
- **Rebuild immunity**: Workbench can be rebuilt without touching governance logic
- **Terminal parity**: CLI users get identical governance via standard MCP config
- **Zero net complexity**: Subtraction from hestai-mcp, not addition of new service
- **Proven code preserved**: 1500+ lines of Python with 92% coverage stays in production
- **Document alignment**: Three contradictory documents now have one authoritative resolution

### Negative

- **Two languages**: Python governance engine alongside TypeScript Workbench
- **Subprocess lifecycle**: Workbench must manage stdio process lifecycle (spawn, monitor, restart on crash)
- **Cross-process debugging**: Errors may span Workbench ↔ governance engine boundary

### Risks

| Risk | Mitigation |
|------|------------|
| Stdio process crashes | Workbench detects exit, respawns. Stateless design means no state loss. |
| Two-language maintenance | Python codebase is SHRINKING (subtraction). Maintenance cost decreases. |
| State sync confusion | Clear ownership: `.hestai/state/` is governance engine's domain. Workbench reads, never writes. |
| IPC latency | Stdio is local pipes, not network. Measured latency for MCP stdio is <10ms per call. |

---

## References

- Decision map: `docs/planning/governance-context-decision-map.md`
- D1 debate (standard): `2026-04-06-d1-thick-client-vs-governance-engine-standard`
- D1 debate (premium): `2026-04-06-d1-thick-client-vs-governance-engine-premium`
- Ecosystem Lighthouse: `src/hestai_mcp/_bundled_hub/standards/HESTAI-ECOSYSTEM-LIGHTHOUSE.md`
- Ecosystem Overview v3.0: `src/hestai_mcp/_bundled_hub/standards/HESTAI-ECOSYSTEM-OVERVIEW.oct.md`
- Workbench PROJECT-CONTEXT: `hestai-workbench/.hestai-state/context/PROJECT-CONTEXT.oct.md`
- ADR-0033: Dual-Layer Context Architecture
- ADR-0034: Orchestra Map Architecture
- ADR-0275: Rebuild Odyssean Anchor Inside HestAI-MCP (superseded for target platform)

---

## Decision Record

| Date | Actor | Action |
|------|-------|--------|
| 2026-04-06 | Human | Identified three-document contradiction and the five governance gaps |
| 2026-04-06 | Claude Opus 4.6 | Created decision map with 7 decisions and dependency graph |
| 2026-04-06 | Wind/Wall/Door (standard) | Proposed "Stateless Stdio Orchestration" — governance via subprocess |
| 2026-04-06 | Wind/Wall/Door (premium) | Proposed "Adapter Pattern Data Plane" — strict governance isolation |
| 2026-04-06 | Both debates | Converged on Governance Engine direction. Wall issued CONDITIONAL (mitigations required). Stalemate status — architectural agreement, not production approval. Human judgment accepted direction based on all three roles agreeing on architecture despite Wall's implementation conditions. |
| 2026-04-06 | Human | Endorsed Three-Service Model. Authorized ADR creation. |

---

**END OF ADR-0353**
