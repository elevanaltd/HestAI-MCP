# ADR-0149: Unified Bind Tool via OCTAVE Identity Schema

- **Status**: Proposed
- **Type**: ADR
- **Author**: holistic-orchestrator
- **Created**: 2026-01-04
- **Updated**: 2026-01-04
- **GitHub Issue**: [#149](https://github.com/elevanaltd/HestAI-MCP/issues/149)
- **Phase**: B1
- **Supersedes**: (none)
- **Superseded-By**: (none)
- **From-RFC**: (none)

## Context

The current agent binding process has several pain points:

1. **Two-step ceremony**: Agents must call `clock_in` then `odyssean_anchor` separately, creating a "limbo" state
2. **Format divergence**: RAPH Vector v4.0 diverged from OCTAVE syntax unnecessarily (per octave-integration-summary.md)
3. **Unicode fragility**: Unicode operators (⇌ → ∧) cause parsing failures despite parser supporting ASCII alternatives
4. **CLI fragmentation**: Different CLIs (Claude, Codex, Gemini) need different binding approaches
5. **Weak validation**: OA-I4 (contextual proof) accepts empty values; OA-I5 (authority) lacks parent verification

A multi-model debate using Wind/Wall/Door pattern with Claude Opus (Ideator), GPT-4o (Validator), and Gemini 3 Pro (Synthesizer) explored solutions while maintaining OA-I1 through OA-I7 immutable requirements.

## Decision

We will create a **unified `bind` MCP tool** that treats RAPH Vector as an OCTAVE Identity Schema:

### 1. Reframe RAPH as OCTAVE Schema
Instead of a competing format, RAPH v4.0 becomes the schema definition for `TYPE::IDENTITY` OCTAVE blocks:

```octave
===IDENTITY===
META:
  TYPE::IDENTITY
  VERSION::5.0
  SCHEMA::identity.oct.schema

BIND:
  ROLE::technical-architect
  COGNITION::LOGOS
  ARCHETYPES::[ATHENA, DAEDALUS]
  AUTHORITY::RESPONSIBLE[unified-bind-design]

ARM:
  PHASE::B1
  BRANCH::bind-tool
  FILES::3[odyssean_anchor.py, clock_in.py, bind.py]
  CONTEXT_HASH::sha256(git_status+phase+branch)

TENSIONS:
  L1::[simplicity]<->CTX:bind.py[creating]->TRIGGER[merge tools]
  L2::[security]<->CTX:OA-I4[strengthening]->TRIGGER[add hash]

COMMIT:
  ARTIFACT::src/hestai_mcp/mcp/tools/bind.py
  GATE::has_valid_identity(session_id)

===END===
```

### 2. Create Unified Tool
The new `bind()` tool will:
- Combine `clock_in` and `odyssean_anchor` into one atomic operation
- Accept IDENTITY blocks in standard OCTAVE format
- Create session and validate identity in single transaction
- Return session_id and validated identity to agent context

### 3. Strengthen Validation
- **OA-I4**: Add `CONTEXT_HASH` requirement - agents must hash git status + phase to prove context processing
- **OA-I5**: Verify DELEGATED authority references real parent session
- **ARM**: Reject empty/unknown values (no more weak proofs)

### 4. Universal Discovery
- Agents read constitutions from `hub/agents/{role}.oct.md` (future: `.hestai-sys/agents/`)
- Schema documented at `hub/library/schemas/identity.oct.schema`
- ASCII operators (`<->`, `->`) as primary, Unicode as legacy

## Consequences

### Positive
- **Simplified ceremony**: One tool instead of two (50% reduction in binding steps)
- **Universal compatibility**: Works for ANY agent from ANY CLI via MCP protocol
- **OCTAVE alignment**: RAPH becomes standard OCTAVE schema, not custom format
- **Stronger validation**: Context hash and parent verification close security gaps
- **No Unicode issues**: ASCII operators as primary eliminates parsing failures

### Negative
- **Breaking change**: Existing agents using two-step ceremony must update
- **Migration effort**: Need to create identity.oct.schema and unified tool
- **Backward compatibility**: May need transition period supporting both approaches

### Neutral
- **Same validation logic**: Core RAPH validation remains, just in OCTAVE format
- **Session storage unchanged**: Still uses `.hestai/sessions/` structure
- **Tool gating preserved**: `has_valid_identity()` replaces `has_valid_anchor()`

## Related Documents

- **Debate Transcript**: `.hestai/workflow/debate-halls/2026-01-04-unified-bind-v2/`
- **OCTAVE Integration**: `/Volumes/HestAI-MCP/worktrees/octave-dependency-update/docs/octave-integration-summary.md`
- **OA Requirements**: `.hestai/workflow/components/000-ODYSSEAN-ANCHOR-NORTH-STAR.md`
- **Current Implementation**: `src/hestai_mcp/mcp/tools/odyssean_anchor.py`
- **ADRs**:
  - ADR-0036: Odyssean Anchor Binding (current approach)
  - ADR-0037: OCTAVE-MCP Integration (alignment strategy)

## Implementation Plan

1. **Phase 1: Schema Definition** (2 days)
   - Create `hub/library/schemas/identity.oct.schema`
   - Document schema at `hub/library/schemas/identity.md`
   - Define validation rules for IDENTITY blocks

2. **Phase 2: Tool Implementation** (3 days)
   - Create `src/hestai_mcp/mcp/tools/bind.py`
   - Merge clock_in and odyssean_anchor logic
   - Add context hash generation and verification
   - Implement parent session verification

3. **Phase 3: Migration Support** (2 days)
   - Update existing agents to use new bind tool
   - Create migration guide for external consumers
   - Add compatibility layer if needed

4. **Phase 4: Documentation** (1 day)
   - Update bind command at `hub/library/commands/bind.md`
   - Document ASCII operators as primary
   - Update agent constitutions with new format

## Validation Criteria

The solution satisfies all OA immutables:
- ✅ **OA-I1**: Single universal protocol via unified bind tool
- ✅ **OA-I2**: Structural validation via OCTAVE schema
- ✅ **OA-I3**: Retry mechanism preserved
- ✅ **OA-I4**: Context hash proves awareness
- ✅ **OA-I5**: Parent session verification
- ✅ **OA-I6**: Tool gating via has_valid_identity()
- ✅ **OA-I7**: Returns validated identity to agent
