# ADR-0149: Unified Bind Tool via OCTAVE Identity Schema

- **Status**: Proposed
- **Type**: ADR
- **Author**: holistic-orchestrator
- **Created**: 2026-01-04
- **Updated**: 2026-01-04 (Revised to use octave-mcp)
- **GitHub Issue**: [#149](https://github.com/elevanaltd/HestAI-MCP/issues/149)
- **Phase**: B1
- **Supersedes**: (none)
- **Superseded-By**: (none)
- **From-RFC**: (none)

## Context

The current agent binding process has several pain points:

1. **Two-step ceremony**: Agents must call `clock_in` then `odyssean_anchor` separately, creating a "limbo" state
2. **Format divergence**: RAPH Vector v4.0 diverged from OCTAVE syntax unnecessarily (per octave-integration-summary.md)
3. **Custom parsing**: We're maintaining regex-based parsers when `octave-mcp` v0.3.0 provides full parsing/emission
4. **CLI fragmentation**: Different CLIs (Claude, Codex, Gemini) need different binding approaches
5. **Weak validation**: OA-I4 (contextual proof) accepts empty values; OA-I5 (authority) lacks parent verification

A multi-model debate using Wind/Wall/Door pattern with Claude Opus (Ideator), GPT-4o (Validator), and Gemini 3 Pro (Synthesizer) explored solutions while maintaining OA-I1 through OA-I7 immutable requirements.

### Key Insight from Analysis
RAPH Vector serves a valid **runtime validation** purpose (binding proof), distinct from the design-time agent constitution. It unnecessarily diverged from OCTAVE syntax but should be retained as an OCTAVE-compliant schema rather than eliminated.

## Decision

We will create a **unified `bind` MCP tool** that:
1. Uses `octave-mcp` v0.3.0 as the parsing/emission engine
2. Treats RAPH Vector as an OCTAVE Identity Schema
3. Leverages octave-mcp's operators and validation

### 1. Use octave-mcp for All OCTAVE Operations
Instead of custom regex parsing, we'll use the official library:

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

### 2. Implementation with octave-mcp
```python
import octave_mcp

async def bind(identity_block: str) -> dict:
    # Parse using octave-mcp instead of custom regex
    doc = octave_mcp.parse(identity_block)

    # Validate schema using octave-mcp's validation
    if not octave_mcp.validate_schema(doc, "identity"):
        return {"error": "Invalid IDENTITY schema"}

    # Extract fields using octave-mcp's accessors
    role = octave_mcp.get_field(doc, "BIND.ROLE")
    authority = octave_mcp.get_field(doc, "BIND.AUTHORITY")

    # Create session and return
    session_id = create_session(role, doc)
    return {"session_id": session_id, "identity": octave_mcp.emit(doc)}
```

### 3. Strengthen Validation
- **OA-I4**: Add `CONTEXT_HASH` requirement - agents must hash git status + phase to prove context processing
- **OA-I5**: Verify DELEGATED authority references real parent session
- **ARM**: Reject empty/unknown values (no more weak proofs)
- **Use octave-mcp operators**: The library handles ⇌, →, ⊕ correctly without custom parsing

### 4. Universal Discovery
- Agents read constitutions from `hub/agents/{role}.oct.md` (future: `.hestai-sys/agents/`)
- Schema documented at `hub/library/schemas/identity.oct.schema`
- **octave-mcp handles operators**: No need to worry about ASCII vs Unicode - the library manages it

## Consequences

### Positive
- **Simplified ceremony**: One tool instead of two (50% reduction in binding steps)
- **Universal compatibility**: Works for ANY agent from ANY CLI via MCP protocol
- **OCTAVE alignment**: RAPH becomes standard OCTAVE schema, not custom format
- **Stronger validation**: Context hash and parent verification close security gaps
- **No parsing issues**: octave-mcp handles all operator parsing correctly
- **Maintainability**: Remove 500+ lines of custom regex code
- **Future-proof**: Automatically support new OCTAVE features as library updates

### Negative
- **Breaking change**: Existing agents using two-step ceremony must update
- **Dependency**: Adds octave-mcp v0.3.0 as required dependency
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

1. **Phase 0: Add octave-mcp Dependency** (Immediate)
   - Add `octave-mcp>=0.3.0` to pyproject.toml
   - Verify compatibility with existing code
   - Test operator parsing (⇌, →, ⊕) works correctly

2. **Phase 1: Schema Definition** (2 days)
   - Create `hub/library/schemas/identity.oct.schema`
   - Document schema at `hub/library/schemas/identity.md`
   - Define validation rules for IDENTITY blocks using octave-mcp

3. **Phase 2: Tool Implementation** (3 days)
   - Create `src/hestai_mcp/mcp/tools/bind.py` using octave-mcp
   - Replace custom regex parsing with octave_mcp.parse()
   - Use octave_mcp.emit() for canonical output
   - Merge clock_in and odyssean_anchor logic
   - Add context hash generation and verification
   - Implement parent session verification

4. **Phase 3: Migration Support** (2 days)
   - Update existing agents to use new bind tool
   - Create migration guide for external consumers
   - Remove legacy regex parsing code

5. **Phase 4: Documentation** (1 day)
   - Update bind command at `hub/library/commands/bind.md`
   - Document that octave-mcp handles all operators
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
