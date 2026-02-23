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

Odyssean Anchor MCP (`odyssean-anchor-mcp`) is a standalone MCP server implementing the agent identity binding protocol. It consists of:

- **Steward class**: 2,158 lines — protocol state machine, proof validation orchestration, capability resolution
- **Proof validation**: 1,039 lines — tier-aware cognitive proof validators (SEA/SHANK/ARM/FLUKES)
- **ARM computation**: 388 lines — git state reading, PHASE extraction, security validation
- **MCP server**: 649 lines — 5 tool handlers
- **Storage layer**: 242 lines — session and permit persistence
- **Total**: ~4,476 lines across core modules, with 1,235 tests

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

The `bind` tool returns a 7-step TODO list where step T5 is "call anchor_request." The two systems are already one workflow split across two process boundaries.

**3. ~40% of OA's code is standalone scaffolding**

| Category | LOC | Disposition |
|----------|-----|-------------|
| Protocol state machine | ~400 | **Essential** — the core innovation |
| Proof validation | ~1,039 | **Essential** — anti-theater enforcement |
| ARM computation | ~388 | **Duplicated** — clock_in does this |
| Agent file parsing | ~200 | **Duplicated** — OA's is better than bind.py's |
| Context file discovery | ~100 | **Duplicated** |
| Skill/pattern loading | ~300 | **Partially duplicated** |
| Session/permit storage | ~242 | **Accidental** — standalone storage model |
| Config loading | ~150 | **Accidental** — separate config system |
| Path security | ~200 | **Duplicated** |
| Legacy three-stage handshake | ~300 | **Dead code** — superseded by ADR-0003 |

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

**Option B: Naive Code Merge** — Copy the 4,476 lines of OA source + 1,235 tests into hestai-mcp.
- Pro: Fast execution, proven code moves intact.
- Con: Carries ~300 lines of dead code, perpetuates duplication (two git readers, two agent parsers, two config loaders), creates a Franken-codebase with two mental models.

**Option C: Rebuild Inside hestai-mcp** — Port the essential protocol (~1,200-1,400 lines), create shared infrastructure modules, eliminate duplication.
- Pro: Clean architecture, shared modules, ~70% less code, unified mental model.
- Con: Slower execution, new code needs new tests, risk of regression on edge cases.

## Decision

**We will rebuild the Odyssean Anchor binding protocol natively inside hestai-mcp (Option C).**

The protocol state machine and proof validation are the essential innovations. Everything else is scaffolding that hestai-mcp already provides or should provide as shared infrastructure.

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
                             # Ported from: OA Steward (essential ~400 lines)
                             # Provides: ProgressiveSession, stage transitions, nonce generation
                             # State: In-memory dict (progressive sessions are ephemeral)

    proof_validation.py      # Cognitive proof validators
                             # Ported from: OA proof_validation.py (~800 lines, trimmed)
                             # Provides: validate_sea_proof, validate_shank_proof,
                             #           validate_arm_proof, validate_flukes_proof
                             # Removes: Legacy three-stage validation code

    permit_store.py          # Simplified permit persistence
                             # Replaces: OA PermitStore + HandshakeStore
                             # Storage: .hestai/state/permits/ (project-local, not ~/.odyssean-anchor/)

  modules/tools/
    anchor_request.py        # MCP tool: Start binding ceremony
    anchor_lock.py           # MCP tool: Progressive stage validation (SEA/SHANK/ARM)
    anchor_commit.py         # MCP tool: Finalize binding, issue permit
    anchor_micro.py          # MCP tool: Lightweight permit for trivial tasks
    verify_permit.py         # MCP tool: Tool gating check

    clock_in.py              # SIMPLIFIED: calls git_context instead of inline git ops
    bind.py                  # SIMPLIFIED: calls agent_parser, ceremony is now internal
```

### What Gets Cut

- ~300 lines: Legacy three-stage handshake (superseded by progressive interrogation)
- ~388 lines: arm.py (replaced by shared git_context.py)
- ~200 lines: agent_loader.py (replaced by shared agent_parser.py)
- ~150 lines: Independent config loading (uses hestai-mcp's config)
- ~242 lines: HandshakeStore + PermitStore (simplified to single permit_store.py)
- ~200 lines: Duplicated path security (shared module)
- **Total cut: ~1,480 lines of duplication/dead code**

### What Ports Intact

- Protocol state machine: stage ordering, nonce chain, I2 enforcement (~400 lines)
- Proof validation: SEA/SHANK/ARM/FLUKES validators, anti-theater checks (~800 lines)
- Permit model: session_id, role, tier, validated, timestamp
- Tool gating: verify_permit check before work tools execute
- Capability tier selection: capability_mode parameter, §3::CAPABILITIES extraction

### Execution Phases

**Phase 1 — Shared Infrastructure**
- Create `git_context.py` (unified git state)
- Create `agent_parser.py` (OA's AST parser)
- Create `path_security.py` (shared validation)
- Refactor `clock_in.py` to use `git_context`
- Tests for all shared modules

**Phase 2 — Port the Protocol**
- Port `binding_protocol.py` (state machine + nonce chain)
- Port `proof_validation.py` (cognitive proof validators)
- Register 5 anchor tools
- Write tests referencing OA's 1,235 tests as specification

**Phase 3 — Unify Sessions**
- Permits stored in `.hestai/state/permits/`
- Ceremony sessions ephemeral (in-memory dict)
- Simplify `bind.py` to orchestrate the now-internal ceremony

**Phase 4 — Archive OA Repo**
- Archive odyssean-anchor-mcp (keep for reference + git history)
- Update ecosystem docs and dependency graph
- Update MCP server configurations

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

## Consequences

### Positive

- **~70% code reduction**: ~1,200-1,400 lines vs 4,476 in standalone OA
- **Eliminates MCP-to-MCP latency**: Ceremony becomes internal function calls
- **Single git context module**: clock_in and binding ceremony share one implementation
- **Single agent parser**: OA's superior AST parser replaces bind.py's minimal parsing
- **Unified storage**: Permits in `.hestai/state/` alongside sessions
- **Simpler deployment**: One MCP server, one pip install, one config
- **Unblocks critical path**: Ecosystem Build Order Steps 2-6 can proceed

### Negative

- **Test migration effort**: 1,235 OA tests must be referenced (not blindly ported) to write new tests
- **Regression risk**: New code may miss edge cases that battle-tested OA code handles
- **Temporary feature gap**: During rebuild, the standalone OA remains operational. Transition period requires both to work.
- **ADR-0036 partially superseded**: The protocol design is preserved but the deployment architecture changes

### Neutral

- **odyssean-anchor-mcp repo archived, not deleted**: Git history preserved for reference
- **Issue migration**: 6 OA issues transfer/redesign, 2 closed, 1 likely superseded
- **OA's 16 worktrees**: Become irrelevant once rebuild is complete. Active development moves to hestai-mcp.

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
