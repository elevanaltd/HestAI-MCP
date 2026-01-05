===IMPLEMENTATION_PLAN===
META:
  TITLE::"Odyssean Anchor v5.0 Implementation Plan"
  TYPE::IMPLEMENTATION_PLAN
  STATUS::APPROVED
  AUTHOR::holistic-orchestrator
  DATE::2026-01-05
  SPEC_REF::"hub/library/specs/odyssean-anchor-protocol-v5.oct.md"
  DEBATE_REF::"debates/2026-01-05-oa-v5-protocol-design"

## Overview
Refactor the binding system from two separate tools (`clock_in` + `odyssean_anchor`) into a single staged `anchor()` tool implementing the three-stage handshake protocol.

## Current State
- `clock_in.py`: 823 lines - creates session, returns context_paths
- `odyssean_anchor.py`: 1174 lines - validates RAPH Vector v4.0
- Two-tool ceremony creates "limbo state" between session creation and binding

## Target State
Single `anchor(stage=...)` tool with:
- **IDENTITY** stage: Load constitution, create provisional session
- **CONTEXT** stage: Validate BIND, inject server ARM
- **PROOF** stage: Validate tensions+commit, promote session to active

## Implementation Tasks

### Phase 1: Core Tool Refactor

**1.1 Create `src/hestai_mcp/mcp/tools/anchor.py`**
- New staged tool entry point
- Stage dispatcher: identity → context → proof
- Token/state management via `handshake.json`

**1.2 Implement Stage 1 (IDENTITY)**
- Load role constitution from `.hestai-sys/agents/{role}.oct.md`
- Create `pending/{token}/handshake.json` (for tracked modes)
- Return: session_token + constitution_path + next-stage template

**1.3 Implement Stage 2 (CONTEXT)**
- Validate token exists and stage==IDENTITY
- Parse and validate BIND section (role, cognition, authority)
- Compute server-authoritative ARM (reuse `inject_arm_section` logic)
- Update handshake.json, advance stage to CONTEXT
- Return: SERVER_ARM + proof template

**1.4 Implement Stage 3 (PROOF)**
- Validate token exists and stage==CONTEXT
- Validate TENSIONS against strictness (quick=1, default=2, deep=3)
- Validate COMMIT (artifact + gate)
- Write `anchor.json`, atomic rename `pending/{token}` → `active/{token}`
- Return: canonical anchor + WORK_PERMIT

### Phase 2: Mode Support

**2.1 Implement mode=full**
- Full 3-stage flow, agent provides tensions

**2.2 Implement mode=express**
- 2-stage flow: identity → auto-proof
- Server generates default tensions from role constitution
- Agent just confirms with commit

**2.3 Implement mode=lite**
- 3-stage flow with quick strictness default

**2.4 Implement mode=untracked**
- No disk session, no handshake.json
- Return read-only context, no work permit

### Phase 3: Integration

**3.1 Internalize clock_in**
- Extract session creation logic to `_create_provisional_session()`
- Extract session activation to `_activate_session()`
- Keep `clock_in.py` as deprecated wrapper (backward compat)

**3.2 Update tool gating**
- `gating.py`: Check `active/{token}/anchor.json` exists
- Update `has_valid_anchor()` to use new directory structure

**3.3 Expose in MCP server**
- Add `anchor` tool to `server.py`
- Deprecate separate `odyssean_anchor` (or alias to `anchor(stage="proof")`)

### Phase 4: Command and Documentation

**4.1 Update `hub/library/commands/bind.md`**
- Simplify to kickoff wrapper calling `anchor(stage="identity")`
- Remove 7-step TODO sequence (tool is self-guiding)

**4.2 Update documentation**
- `docs/odyssean-anchor-terminology.md`: Add v5.0 stage mapping
- ADR for the migration

## Testing Strategy
- Unit tests for each stage in isolation
- Integration test for full 3-stage flow
- Mode-specific tests (full/express/lite/untracked)
- Backward compatibility test (old odyssean_anchor calls still work)

## Dependencies
- `.hestai-sys` governance layer ready (parallel work)
- Role constitutions accessible at `.hestai-sys/agents/{role}.oct.md`

## Quality Gates
- All existing 511 tests pass
- New tests for staged protocol
- mypy/ruff/black clean
- CRS + CE review before merge

===END===
