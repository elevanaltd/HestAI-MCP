# ADR-0275: Rebuild Odyssean Anchor Protocol Inside hestai-mcp

- **Status**: Proposed
- **Type**: ADR
- **Author**: holistic-orchestrator (HO session, PERMIT_SID: 5a38555c)
- **Created**: 2026-02-23
- **Updated**: 2026-02-23
- **GitHub Issue**: [#275](https://github.com/elevanaltd/HestAI-MCP/issues/275)
- **Phase**: B1
- **Supersedes**: ADR-0036 (deployment assumption only — protocol design preserved)
- **Superseded-By**: (none)
- **From-RFC**: (none)

## Context

### The Current State

Odyssean Anchor MCP (`odyssean-anchor-mcp`) is a standalone MCP server implementing the agent identity binding protocol. The codebase contains **two co-existing protocol implementations**:

1. **Legacy three-stage handshake** (`REQUEST → LOCK → COMMIT`) — the original protocol from ADR-0036, still present in steward.py methods but superseded.
2. **Progressive interrogation** (`REQUEST → SEA → SHANK → ARM → COMMIT`) — the active protocol since ADR-0003, with four focused proof stages. **This is the protocol we will port.**

Core module breakdown:

- **Steward class**: 2,158 lines — protocol state machine, proof validation orchestration, capability resolution (includes both legacy and progressive paths)
- **Proof validation**: 1,039 lines — tier-aware cognitive proof validators (SEA/SHANK/ARM/FLUKES)
- **ARM computation**: 388 lines — git state reading, PHASE extraction, security validation
- **MCP server**: 649 lines — 5 tool handlers
- **Storage layer**: 242 lines — session and permit persistence

Additional modules not in the critical path but part of the total codebase:

| Module | LOC | Disposition |
|--------|-----|-------------|
| extraction.py | ~1,030 | Context extraction logic — evaluate for shared use |
| config.py | ~783 | Standalone config — replaced by hestai-mcp config |
| validator.py | ~569 | Input validation — port relevant validators |
| models.py | ~267 | Data models — port protocol-relevant models |
| protocol_models.py | ~182 | Progressive protocol types — **essential, port intact** |
| skill_loader.py | ~252 | Skill loading — partially duplicated in hestai-mcp |
| instruction_generator.py | ~173 | Instruction generation — evaluate for port |
| middleware.py | ~144 | MCP middleware — not needed (native integration) |
| instruction_loader.py | ~116 | Instruction loading — evaluate for port |
| constants.py | ~106 | Constants — merge into hestai-mcp constants |
| north_star_loader.py | ~89 | NS loading — duplicated in hestai-mcp |
| constitution_loader.py | ~80 | Constitution loading — partially duplicated |
| primer_reference.py | ~82 | Primer refs — evaluate for port |
| startup_primer_sync.py | ~130 | Primer sync — evaluate for port |

**Total codebase**: ~9,148 lines across all `src/` modules, with **987 tests** across 61 test files.

### Forces Driving This Decision

**1. Significant code duplication between OA and hestai-mcp**

Both systems independently implement:

| Concern | clock_in (hestai-mcp) | ARM (OA) |
|---------|----------------------|----------|
| Get branch | `git rev-parse --abbrev-ref HEAD` | `git rev-parse --abbrev-ref HEAD` |
| Get modified files | `git status --short` | `git status --porcelain` |
| Extract PHASE | Reads PROJECT-CONTEXT.oct.md | Reads PROJECT-CONTEXT.oct.md |
| Read agent files | bind.py (minimal string parsing) | agent_loader.py (full AST via octave_mcp) |
| List context files | resolve_context_paths() | list_context_files() |
| Path security | Role format validation, `..` checks | Symlink detection, TOCTOU, toplevel matching |

**2. HestAI-MCP's bind.py already orchestrates the OA ceremony**

The `bind` tool is a bootstrap sequencer/placeholder: it discovers the agent's `.oct.md` file, lightly parses cognition/archetype metadata, and returns a 7-step TODO list where step T5 is "call `mcp__odyssean-anchor__anchor_request`." It performs zero actual identity binding — it exists solely because the ceremony lives in a separate server and needs an instruction bridge. The two systems are already one workflow split across two process boundaries, with bind.py as the duct tape between them.

**3. ~50% of OA's code is standalone scaffolding or duplication**

| Category | LOC | Disposition |
|----------|-----|-------------|
| Protocol state machine (progressive) | ~400 | **Essential** — the core innovation |
| Proof validation | ~1,039 | **Essential** — anti-theater enforcement |
| Protocol models | ~182 | **Essential** — progressive protocol types |
| Instruction generation | ~173 | **Essential** — anchor output formatting |
| ARM computation | ~388 | **Duplicated** — clock_in does this |
| Agent file parsing | ~200 | **Duplicated** — OA's is better than bind.py's |
| Context file discovery | ~100 | **Duplicated** |
| Skill/pattern loading | ~252 | **Partially duplicated** |
| Extraction logic | ~1,030 | **Evaluate** — may be partially needed |
| Input validators | ~569 | **Evaluate** — port protocol-relevant subset |
| Session/permit storage | ~242 | **Accidental** — standalone storage model |
| Config loading | ~783 | **Accidental** — separate config system |
| Path security | ~200 | **Duplicated** |
| Middleware | ~144 | **Not needed** — native integration replaces this |
| Legacy three-stage handshake | ~430-500 | **Dead code** — superseded by progressive interrogation |
| Loaders (constitution, NS, primer) | ~299 | **Duplicated** — hestai-mcp already has these |

**4. MCP-to-MCP runtime hop adds latency**

The binding ceremony requires 5 tool calls (REQUEST → 3x LOCK → COMMIT). Each crosses the MCP transport boundary twice (hestai-mcp → OA server → response). Assumption A1 (LATENCY_ACCEPTABILITY) at 80% confidence reflects this concern.

**5. Nobody uses OA without hestai-mcp**

OA reads `.hestai-sys/` agent files, `.hestai/` context files, and the CONSTITUTION. These are all hestai-mcp managed artifacts. There is zero standalone use case.

**6. Ecosystem governance assumes convergence**

The Ecosystem Overview (v1.0) describes the target as three repos: hestai-core-mcp, debate-hall-mcp, octave-mcp. OA is absorbed into hestai-core-mcp. The Ecosystem Build Order (Project #15) places this decision at Order 10 on the critical path.

### Options Considered

**Option A: Keep Standalone** — Continue maintaining OA as a separate MCP server.
- Pro: No migration work required.
- Con: Perpetuates duplication, latency, deployment complexity. Blocks ecosystem convergence.

**Option B: Naive Code Merge** — Copy the ~9,148 lines of OA source + 987 tests into hestai-mcp.
- Pro: Fast execution, proven code moves intact.
- Con: Carries ~500 lines of dead code, perpetuates duplication (two git readers, two agent parsers, two config loaders), creates a Franken-codebase with two mental models.

**Option C: Rebuild Inside hestai-mcp** — Port the essential protocol, create shared infrastructure modules, eliminate duplication.
- Pro: Clean architecture, shared modules, ~40-55% code reduction, unified mental model.
- Con: Slower execution, new code needs new tests, risk of regression on edge cases.

**Option D: Library Import** — Make OA a Python package dependency, import `Steward` directly: `from odyssean_anchor.core.steward import Steward`.
- Pro: Eliminates MCP-to-MCP hop immediately. Zero regression risk. All 987 tests stay in place.
- Con: **Rejected.** This is a velocity optimization that perpetuates the fundamental problem: two separate codebases with duplicated infrastructure, separate config systems, and separate mental models. Per I2 (STRUCTURAL_INTEGRITY_PRIORITY), correctness and clean architecture take precedence over velocity. Option D would create a hidden coupling — hestai-mcp would depend on OA's internal class structure while OA continues to maintain its own standalone scaffolding. The right answer is to do this properly and thoroughly, not to bridge with shortcuts.

## Decision

**We will rebuild the Odyssean Anchor binding protocol natively inside hestai-mcp (Option C).**

Specifically, we port the **progressive interrogation protocol** (REQUEST → SEA → SHANK → ARM → COMMIT) as defined in OA's `protocol_models.py` and the progressive path through `Steward`. The legacy three-stage handshake is **not ported** — it is dead code superseded by ADR-0003.

The protocol state machine and proof validation are the essential innovations. Everything else is scaffolding that hestai-mcp already provides or should provide as shared infrastructure.

**Guiding principle**: Structural integrity over velocity (I2). This rebuild will be done thoroughly and completely. No short-term bridges, no MVP-to-migrate-later. The target architecture is the final architecture.

### Shared Infrastructure Location

The existing codebase has shared modules at `src/hestai_mcp/modules/tools/shared/` (containing `path_resolution.py`, `security.py`, `context_extraction.py`). The new shared infrastructure modules (`git_context.py`, `agent_parser.py`, `path_security.py`) are placed in `src/hestai_mcp/core/` to establish a clear architectural boundary:

- **`core/`** — foundational modules consumed by multiple tools and the binding protocol. These are infrastructure, not tool-specific helpers.
- **`modules/tools/shared/`** — tool-specific shared utilities (formatting, extraction patterns).

Phase 1 will begin with confirming this boundary. If analysis reveals that existing `shared/` modules should migrate to `core/`, or vice versa, that consolidation happens in Phase 1 before new modules are created.

### Target Architecture

```
src/hestai_mcp/
  core/
    git_context.py           # Unified git state module
                             # Replaces: OA arm.py + clock_in inline git ops
                             # Provides: branch, status, ahead/behind, PHASE extraction
                             # Security: symlink detection, toplevel validation, timeouts

    agent_parser.py          # Full AST-based agent file parser
                             # Replaces: OA agent_loader.py + bind.py minimal parsing
                             # Provides: IDENTITY, CONDUCT, CAPABILITIES extraction
                             # Uses: octave_mcp.Parser for AST parsing

    path_security.py         # Shared path validation module
                             # Replaces: OA + hestai-mcp independent path checks
                             # Provides: traversal prevention, symlink detection, TOCTOU protection

    binding_protocol.py      # Protocol state machine + nonce chain
                             # Ported from: OA Steward progressive path (~400 lines)
                             # Provides: ProgressiveSession, stage transitions, nonce generation
                             # State: In-memory dict (see Session Durability below)
                             # Does NOT port: legacy three-stage handshake

    proof_validation.py      # Cognitive proof validators
                             # Ported from: OA proof_validation.py (~800 lines, trimmed)
                             # Provides: validate_sea_proof, validate_shank_proof,
                             #           validate_arm_proof, validate_flukes_proof
                             # Enhancement: ARM validation strengthened (see Improvements)
                             # Removes: Legacy three-stage validation code

    permit_store.py          # Simplified permit persistence
                             # Replaces: OA PermitStore + HandshakeStore
                             # Storage: .hestai/state/permits/ (project-local, not ~/.odyssean-anchor/)

    anchor_generator.py      # Pre-filled anchor artifact generation
                             # Enhancement: Server generates complete anchor alongside template
                             # Eliminates: Agent template-filling as a failure point

  modules/tools/
    anchor_request.py        # MCP tool: Start binding ceremony
    anchor_lock.py           # MCP tool: Progressive stage validation (SEA/SHANK/ARM)
    anchor_commit.py         # MCP tool: Finalize binding, issue permit + pre-filled anchor
    anchor_micro.py          # MCP tool: Lightweight permit for trivial tasks
    anchor_renew.py          # MCP tool: Permit renewal for stable sessions (see Improvements)
    verify_permit.py         # MCP tool: Tool gating check

    clock_in.py              # SIMPLIFIED: calls git_context instead of inline git ops
                             # bind.py is REMOVED — see "What Gets Replaced" below
```

> **bind.py disposition**: The `bind` tool is **removed**, not simplified. Its agent file discovery moves into `anchor_request.py` (via `agent_parser.py`). Its 7-step TODO list is no longer needed — the anchor tools ARE the workflow. The `bind` MCP tool name is retired; agents call `anchor_request` directly to start the ceremony.

### Design Decisions

#### Session Durability

Progressive ceremony sessions are stored in an **in-memory dict**. This means a server restart mid-ceremony destroys in-progress bindings. This is **explicitly acceptable** because:

- Ceremonies are short-lived (5 tool calls in rapid succession)
- A server restart already disrupts the agent's context window
- The agent simply re-starts the ceremony — no data loss, just re-validation
- Persisting ephemeral ceremony state adds complexity without security benefit

Issued **permits** are persisted to disk (`.hestai/state/permits/`) and survive restarts.

#### Permit Storage and Worktrees

Permits are stored in `.hestai/state/permits/`. Since `.hestai/state/` is symlinked across worktrees (confirmed in clock_in.py), permits are **shared across worktrees by default**. This is correct because:

- A permit is bound to a role + project, not a worktree
- The agent's identity doesn't change across worktrees of the same project
- The git state in the permit (branch, commit) is worktree-specific and validated at `verify_permit` time

#### Permit Directory Security

The `.hestai/state/permits/` directory stores identity permits that gate tool access. File-system security is enforced:

- Directory permissions: `0700` (owner read/write/execute only)
- Permit file permissions: `0600` (owner read/write only)
- `permit_store.py` enforces these permissions on creation and validates them on read
- If permissions are found to be too open, `verify_permit` warns and optionally rejects the permit

This prevents unauthorized modification of permits by other processes or users on the same system.

#### Parallel Run Strategy (Phase 1-3)

During the rebuild, both standalone OA and the in-progress native implementation exist. To prevent developer confusion:

- **Routing**: Standalone OA remains the active implementation until Phase 3 integration tests pass. The native implementation is exercised only via its own test suite until cutover.
- **Divergence policy**: If outputs differ between OA and native, native must match OA unless a deliberate design improvement (documented in this ADR's Improvements section) explains the difference.
- **No dual-server operation**: At no point do both implementations serve anchor_* tools simultaneously. The MCP config points to exactly one implementation at a time.

### Improvements Over Standalone OA

**1. Pre-filled anchor generation** — `anchor_commit` returns both the template AND a pre-filled anchor artifact. The agent receives the complete anchor ready to use, eliminating template-filling as a failure point. The template is still provided for agents that need to customize.

**2. Permit renewal** (`anchor_renew`) — A new tool that validates an existing recent permit against the current git state. If the role hasn't changed and the project state is stable, it issues a renewed permit without requiring a full ceremony. This addresses the common "terminal restart" case where the agent has the same role and context but lost its in-memory permit reference. Security constraints:
  - Original permit must be less than 4 hours old (configurable)
  - Renewal preserves the original tier (no escalation)
  - Maximum 3 renewals per original ceremony — after that, full ceremony required
  - Git branch must match the original permit's branch
  - These constraints prevent anti-theater bypass: renewal is a convenience for continuity, not a substitute for cognitive proof
  - I7-compliant: renewal preserves the original tier's rigor level
  - I2-compliant: the original cognitive proof remains valid — only the permit reference is refreshed, not the identity binding

**Session cache disposition**: OA's current implementation includes a session cache (Issue #88) that fast-tracks past SEA+SHANK for repeated ceremonies with the same role within a 600-second TTL. This is distinct from `anchor_renew` — the cache optimizes fresh ceremonies, while renewal refreshes existing permits. Decision: defer session cache to post-rebuild. `anchor_renew` covers the most common restart case. If ceremony latency proves problematic without the cache, it can be added as a follow-up without architectural changes.

**3. Strengthened ARM validation** — OA's current ARM validation uses keyword matching (checking for words like "rule" and "phase") which is trivially gameable. The rebuild requires citing specific `context_selectors` file paths and referencing actual project state values from git_context.

**4. bind.py identity sequencing fix** — Current bind.py leaks the agent's role and file path before the ceremony starts (line 179: `T1::CONSTITUTION->Read(".hestai-sys/library/agents/{role}.oct.md")`). The rebuild fixes this: the SEA proof validates constitutional comprehension at the project level (CONSTITUTION.md is shared, not role-specific). The role is provided to `anchor_request` to initiate the ceremony, but role-specific agent file content (identity, conduct, capabilities) is only revealed after SEA passes. The agent reads the CONSTITUTION first (T1), proves comprehension (SEA), and only then receives its agent-specific instructions. This preserves the anti-theater property: constitutional understanding is proven before identity-specific information could influence the proof.

### What Gets Replaced

- **bind.py** (~290 lines in hestai-mcp): Removed entirely. Agent file discovery moves into `anchor_request` via `agent_parser.py`. The 7-step TODO orchestration list is replaced by the native ceremony tools themselves. The `bind` MCP tool is retired.

### What Gets Cut (from OA codebase)

- ~430-500 lines: Legacy three-stage handshake (superseded by progressive interrogation)
- ~388 lines: arm.py (replaced by shared git_context.py)
- ~200 lines: agent_loader.py (replaced by shared agent_parser.py)
- ~783 lines: Independent config loading (uses hestai-mcp's config)
- ~242 lines: HandshakeStore + PermitStore (simplified to single permit_store.py)
- ~200 lines: Duplicated path security (shared module)
- ~144 lines: MCP middleware (not needed for native integration)
- ~299 lines: Loaders (constitution, NS, primer — duplicated in hestai-mcp)
- **Total eliminated: ~2,700-2,800 lines of duplication/dead code/standalone scaffolding**

### What Ports (With Adaptation)

- Protocol state machine (progressive path only): stage ordering, nonce chain, I2 enforcement (~400 lines)
- Protocol models: ProgressiveSession, stage types, proof requirements (~182 lines)
- Proof validation: SEA/SHANK/ARM/FLUKES validators, anti-theater checks (~800 lines, with ARM strengthening)
- Permit model: session_id, role, tier, validated, timestamp
- Tool gating: verify_permit check before work tools execute
- Capability tier selection: capability_mode parameter, §3::CAPABILITIES extraction
- Instruction generation: anchor artifact formatting (~173 lines, enhanced with pre-fill)
- Input validators: protocol-relevant subset (~200 lines from validator.py)
- Constants: merged into hestai-mcp constants (~106 lines)

### What Gets Evaluated During Phase 1

These modules require hands-on analysis during implementation to determine what subset is needed:

- extraction.py (~1,030 lines) — may overlap with hestai-mcp context resolution
- skill_loader.py (~252 lines) — may overlap with hestai-mcp skill loading
- primer_reference.py (~82 lines) — evaluate relevance to rebuilt protocol
- startup_primer_sync.py (~130 lines) — evaluate relevance

### Execution Phases

**Phase 1 — Shared Infrastructure**
- **Task Zero (time-boxed: 1-2 days max)**: Evaluate the 4 "evaluate" modules (extraction.py, skill_loader.py, primer_reference.py, startup_primer_sync.py). Method: trace which functions are called by the progressive path in `steward.py` — if a function isn't on the progressive call path, it's discarded without further analysis. Deliverable: written checklist with `{module → decision: port|partial|discard, rationale, test note}`. Also confirm the `core/` vs `modules/tools/shared/` boundary decision. Exit criteria: if no clear win after timebox, default to discard and create follow-up issues for anything deferred — do not block Phase 1 infrastructure creation.
- Define `git_context.py` public API contract first (data structures and method signatures), reviewed against both clock_in needs and Phase 2 ARM proof requirements. This prevents disruptive mid-build API changes.
- Create `git_context.py` (unified git state)
- Create `agent_parser.py` (OA's AST parser, using octave_mcp.Parser). Dependency check: verify octave-mcp version alignment between OA (pins 1.2.1) and hestai-mcp before building against the Parser API.
- Create `path_security.py` (shared validation with TOCTOU protection)
- Refactor `clock_in.py` to use `git_context`
- Performance benchmark: `git_context.py` must perform within 110% of the combined individual implementations it replaces
- Tests for all shared modules (behavioral tests, not unit-for-unit ports)

**Phase 2 — Port the Protocol**
- Port `binding_protocol.py` (progressive interrogation state machine + nonce chain)
- Port `proof_validation.py` (cognitive proof validators, with ARM strengthening)
- Port `protocol_models.py` (progressive session types)
- Create `anchor_generator.py` (pre-filled anchor generation)
- Create `permit_store.py` (simplified permit persistence)
- Register 6 anchor tools (5 existing + anchor_renew)
- Write tests using OA's 987 tests as behavioral specification

**Phase 3 — Integration and Unification**
- Permits stored in `.hestai/state/permits/`
- Remove `bind.py` — its agent file discovery moves into `anchor_request`, its TODO orchestration is replaced by the native ceremony tools
- Ensure identity sequencing: `anchor_request` provides constitutional context first, role-specific content only after SEA passes
- End-to-end ceremony tests (full REQUEST → SEA → SHANK → ARM → COMMIT flow)
- Verify permit renewal flow (anchor_renew)
- **Tool name migration** (breaking change): all references to `mcp__odyssean-anchor__anchor_request`, `mcp__odyssean-anchor__anchor_lock`, etc. become `mcp__hestai__anchor_request`, `mcp__hestai__anchor_lock`, etc. This affects:
  - `~/.claude/CLAUDE.md` — ODYSSEAN_ANCHOR_DIRECTIVES section
  - `.hestai-sys/library/skills/subagent-rules/SKILL.md`
  - `.hestai-sys/library/agents/*.oct.md` — any agent files referencing OA tool names
  - `oa-router` subagent type invocation patterns
  - Any documentation referencing the old tool prefix
- Update CLAUDE.md and agent instructions to reference `anchor_request` instead of `bind`

**Phase 4 — Archive OA Repo**
- Verify downstream consumer compatibility before archival:
  - All MCP server configs (e.g., `claude_mcp_config.json`) referencing standalone `odyssean-anchor`
  - Cross-check tool name migration completeness: grep all repos for `mcp__odyssean-anchor__` — must return zero results
  - Note: `debate-hall-mcp` and `hestai-workbench` do **not** currently consume OA permits (verified). Future permit-gated tool access in those repos is a separate feature, not a rebuild dependency.
- Update Ecosystem Build Order (Project #15): mark Order 10 (#269) as Done, update Order 20 (#270) scope
- Archive odyssean-anchor-mcp (keep for reference + git history)
- Update ecosystem docs and dependency graph
- Update MCP server configurations
- Final verification: all anchor ceremony flows produce equivalent permits

### North Star Alignment

All seven immutables (I1-I7) are preserved:

| Immutable | Impact |
|-----------|--------|
| I1: UNIFIED_BINDING_PATH | Preserved — single protocol, now inside hestai-mcp |
| I2: COGNITIVE_PROOF_CEREMONY | Preserved — multi-stage handshake ports intact |
| I3: MANDATORY_SELF_CORRECTION | Preserved — retry logic ports intact |
| I4: SERVER_AUTHORITATIVE_CONTEXT | **Strengthened** — shared git_context.py is more reliable |
| I5: TOOL_GATING_ENFORCEMENT | Preserved — verify_permit ports intact |
| I6: COGNITIVE_BINDING_PERSISTENCE | Preserved — anchor returned to agent context |
| I7: TIERED_RIGOR | Preserved — micro/quick/default/deep tiers port intact |

**Constrained variable BINDING_SCHEMA**: The North Star defines `BINDING_SCHEMA::IMMUTABLE::RAPH_Structure_Request_Lock_Commit`. The progressive protocol (REQUEST → SEA → SHANK → ARM → COMMIT) uses four stages between Request and Commit. This is already an accepted interpretation per ADR-0003: SEA/SHANK/ARM are sub-stages of the "Lock" phase, each validating a different proof dimension. No North Star amendment required.

**Assumption A1 (LATENCY_ACCEPTABILITY)**: Currently at 80% confidence, PENDING. This rebuild directly addresses A1 by eliminating the MCP-to-MCP transport hop. Post-rebuild, A1 confidence should increase significantly and can be moved toward VALIDATED once Phase 3 performance benchmarks confirm latency improvement.

## Consequences

### Positive

- **~40-55% effective code reduction**: Rebuilt anchor protocol is ~2,000-2,500 lines vs ~9,148 in standalone OA. The reduction is honest: it accounts for all modules, not just the 5 largest.
- **Eliminates MCP-to-MCP latency**: Ceremony becomes internal function calls
- **Single git context module**: clock_in and binding ceremony share one implementation
- **Single agent parser**: OA's superior AST parser replaces bind.py's minimal parsing
- **Unified storage**: Permits in `.hestai/state/` alongside sessions
- **Simpler deployment**: One MCP server, one pip install, one config
- **Unblocks critical path**: Ecosystem Build Order Steps 2-6 can proceed
- **Protocol improvements**: Pre-filled anchors, permit renewal, strengthened ARM validation, identity sequencing fix

### Negative

- **Test effort**: OA's 987 tests must be studied as behavioral specification to write new tests. This is deliberate — we test the rebuilt behavior, not port test code.
- **Regression risk**: New code may miss edge cases that battle-tested OA code handles. Mitigated by using OA tests as specification and Phase 4 equivalence verification.
- **Criticality concentration**: The new `core/` modules become shared critical infrastructure. A bug in `git_context.py` affects both clock_in and the binding ceremony. Mitigated by rigorous testing and Phase 1 performance benchmarks.
- **Temporary dual operation**: During rebuild, the standalone OA remains operational. Both must work until Phase 4 archival.
- **ADR-0036 partially superseded**: The protocol design is preserved but the deployment architecture changes.

### Neutral

- **odyssean-anchor-mcp repo archived, not deleted**: Git history preserved for reference
- **Issue migration**: 6 OA issues transfer/redesign, 2 closed, 1 likely superseded
- **OA's worktrees**: Become irrelevant once rebuild is complete. Active development moves to hestai-mcp.

## Success Metrics

The rebuild is correct when:

1. **Functional equivalence**: All progressive interrogation ceremony flows (anchor_request → anchor_lock x3 → anchor_commit) produce equivalent permits and anchors to standalone OA.
2. **Permit structure equivalence**: A permit generated by the rebuilt implementation contains at minimum the same fields as standalone OA (`session_id`, `role`, `tier`, `validated`, `timestamp`) and is accepted by all existing `verify_permit` consumers without modification. New fields (e.g., `branch`, `renewed_from`) may be added but must not break existing consumers.
3. **Shared infrastructure adoption**: clock_in.py uses git_context.py (no inline git operations remain).
4. **Test coverage**: Behavioral tests cover all proof validation paths, tier variations, and error conditions documented in OA's 987 tests.
5. **Quality gates green**: ruff, black, mypy, pytest all pass with ≥89% coverage threshold.
6. **Performance parity**: `git_context.py` performs within 110% of the combined individual implementations it replaces (clock_in inline git ops + OA arm.py).
7. **No standalone dependency**: hestai-mcp's `claude_mcp_config.json` no longer references `odyssean-anchor` as a separate server.

## Rollback Plan

**Phase 1-3**: Standalone OA remains fully operational throughout. If the rebuild fails at any phase, we simply continue using OA as-is. No user-facing impact.

**Phase 4 (archival)**: Only executed after Phase 3 passes all success metrics. If post-archival issues are discovered, OA can be unarchived and re-enabled in MCP config within minutes.

**Risk assessment**: Low. The rebuild is additive until Phase 4. At no point is functionality removed before its replacement is verified.

## Related Documents

- **ADR**: [ADR-0036: Odyssean Anchor Binding](./adr-0036-odyssean-anchor-binding.md) — original design (partially superseded)
- **Issues**:
  - [#269](https://github.com/elevanaltd/HestAI-MCP/issues/269) — DECIDE merger (this ADR records the decision)
  - [#270](https://github.com/elevanaltd/HestAI-MCP/issues/270) — Execute rebuild (scope updated)
  - [#275](https://github.com/elevanaltd/HestAI-MCP/issues/275) — This ADR's tracking issue
  - [odyssean-anchor-mcp#118](https://github.com/elevanaltd/odyssean-anchor-mcp/issues/118) — Tiered permit model (redesign natively)
  - [odyssean-anchor-mcp#116](https://github.com/elevanaltd/odyssean-anchor-mcp/issues/116) — Capability tiers tracking (transfer)
  - [odyssean-anchor-mcp#113](https://github.com/elevanaltd/odyssean-anchor-mcp/issues/113) — P2 Pilot (transfer)
  - [odyssean-anchor-mcp#96](https://github.com/elevanaltd/odyssean-anchor-mcp/issues/96) — FLUKES enforcement (redesign)
  - [odyssean-anchor-mcp#64](https://github.com/elevanaltd/odyssean-anchor-mcp/issues/64) — Skills auto-loading (likely superseded)
- **Projects**:
  - [Ecosystem Build Order](https://github.com/orgs/elevanaltd/projects/15) — Order 10 (decision), Order 20 (execution)
  - [Agent Capability Tiers Migration](https://github.com/orgs/elevanaltd/projects/12)
