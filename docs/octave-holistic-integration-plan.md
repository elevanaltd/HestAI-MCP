# Holistic OCTAVE Integration Plan: Complete System View

**Date**: 2026-01-04
**Author**: holistic-orchestrator
**Context**: Assessment of ADR-0149 and comprehensive octave-mcp integration

## Executive Summary

ADR-0149 proposes a unified `bind` tool that fully leverages octave-mcp v0.3.0. This is the right direction and aligns perfectly with our OCTAVE integration strategy. Here's the complete picture of where octave-mcp should be used and the optimal build order.

## Assessment of ADR-0149

### Strengths
1. **Simplification**: Merges `clock_in` + `odyssean_anchor` into single `bind` tool
2. **Full octave-mcp adoption**: Uses library for parsing, validation, and emission
3. **OCTAVE alignment**: Treats RAPH Vector as standard OCTAVE Identity Schema
4. **Removes custom code**: Eliminates 500+ lines of regex parsing

### Critical Insight
ADR-0149 represents the **convergence point** where all our OCTAVE alignment efforts come together. It's not just about the bind tool - it's about establishing octave-mcp as the single source of truth for all OCTAVE operations.

## Complete Map of OCTAVE Usage Areas

### 1. Identity & Binding (PRIORITY 1)
**Files Affected**:
- `src/hestai_mcp/mcp/tools/bind.py` (NEW - replaces below)
- `src/hestai_mcp/mcp/tools/odyssean_anchor.py` (DEPRECATE)
- `src/hestai_mcp/mcp/tools/clock_in.py` (MERGE INTO bind.py)
- `src/hestai_mcp/mcp/tools/clock_out.py` (UPDATE)

**Usage**: Parse/validate IDENTITY blocks, emit canonical binding proofs

### 2. Session Compression (PRIORITY 2)
**Files Affected**:
- `src/hestai_mcp/mcp/tools/shared/compression.py`
- `src/hestai_mcp/mcp/tools/shared/context_extraction.py`

**Usage**: Parse AI-generated OCTAVE session logs, validate structure, extract fields

### 3. Context Management (PRIORITY 3)
**Files Affected**:
- `.hestai/context/PROJECT-CONTEXT.oct.md`
- `.hestai/context/PROJECT-CHECKLIST.oct.md`
- `.hestai/context/PROJECT-ROADMAP.oct.md`

**Usage**: Parse/update OCTAVE context documents, maintain canonical format

### 4. Agent Constitutions (PRIORITY 4)
**Files Affected**:
- `hub/agents/*.oct.md` (future location)
- `.claude/agents/*.oct.md` (current location)

**Usage**: Parse agent documents (8-section format), validate against schema

### 5. Workflow Documents (PRIORITY 5)
**Files Affected**:
- `.hestai/workflow/**/*.oct.md`
- `hub/governance/**/*.oct.md`

**Usage**: Parse governance/workflow OCTAVE documents

### 6. Schema Validation (FOUNDATIONAL)
**Files Affected**:
- `hub/library/schemas/identity.oct.schema` (NEW)
- `hub/library/schemas/session-log.oct.schema` (NEW)
- `hub/library/schemas/agent.oct.schema` (NEW)

**Usage**: Define and validate OCTAVE document schemas

### 7. Transformation & Migration (TRANSITIONAL)
**Files Affected**:
- `src/hestai_mcp/mcp/tools/shared/octave_transform.py` (TEMPORARY)

**Usage**: Convert legacy RAPH v4.0 to OCTAVE format during transition

## Optimal Build Order

### Phase 0: Foundation (Week 1)
**Goal**: Establish octave-mcp as core dependency

1. **Add octave-mcp dependency** ✅ (DONE)
   ```toml
   octave-mcp>=0.3.0,<1.0.0
   ```

2. **Create base schemas**
   - `identity.oct.schema` - For binding proofs
   - `session-log.oct.schema` - For compression
   - `agent.oct.schema` - For constitutions

3. **Build shared utilities**
   ```python
   # src/hestai_mcp/mcp/tools/shared/octave_utils.py
   import octave_mcp

   def parse_with_fallback(content: str) -> dict:
       """Parse OCTAVE with graceful degradation"""
       try:
           return octave_mcp.parse(content)
       except Exception:
           # Fall back to legacy parser during transition
           return legacy_parse(content)

   def validate_schema(doc: dict, schema: str) -> bool:
       """Validate document against schema"""
       return octave_mcp.validate_schema(doc, schema)
   ```

### Phase 1: Unified Bind Tool (Week 2)
**Goal**: Implement ADR-0149

1. **Create unified bind tool**
   ```python
   # src/hestai_mcp/mcp/tools/bind.py
   async def bind(identity_block: str) -> dict:
       doc = octave_mcp.parse(identity_block)
       # Validate, create session, return
   ```

2. **Migrate existing bindings**
   - Update `/bind` command
   - Support both old and new format temporarily
   - Add feature flag: `USE_UNIFIED_BIND`

3. **Update tests**
   - Test octave-mcp parsing
   - Test operator handling (⇌, →, ⊕)
   - Test schema validation

### Phase 2: Session Compression (Week 3)
**Goal**: Replace regex in compression.py

1. **Update compression to use octave-mcp**
   ```python
   # Parse AI output
   doc = octave_mcp.parse(ai_response)

   # Validate and fix if needed
   if not octave_mcp.validate_schema(doc, "session-log"):
       doc = fix_common_issues(doc)

   # Emit canonical
   return octave_mcp.emit(doc)
   ```

2. **Update context extraction**
   ```python
   # Use octave-mcp for field extraction
   decisions = octave_mcp.get_field(doc, "DECISIONS")
   outcomes = octave_mcp.get_field(doc, "OUTCOMES")
   ```

### Phase 3: Context Documents (Week 4)
**Goal**: Standardize context management

1. **Parse context with octave-mcp**
   - PROJECT-CONTEXT.oct.md
   - PROJECT-CHECKLIST.oct.md
   - PROJECT-ROADMAP.oct.md

2. **Create context update tool**
   ```python
   def update_context(path: str, updates: dict):
       doc = octave_mcp.parse(read_file(path))
       for key, value in updates.items():
           octave_mcp.set_field(doc, key, value)
       write_file(path, octave_mcp.emit(doc))
   ```

### Phase 4: Agent Constitution Migration (Week 5)
**Goal**: Align agents with OCTAVE spec

1. **Convert agents to 8-section format**
   - From: Custom RAPH instructions
   - To: Standard OCTAVE agent format (§0-§7)

2. **Create agent loader**
   ```python
   def load_agent_constitution(role: str) -> dict:
       path = f"hub/agents/{role}.oct.md"
       return octave_mcp.parse(read_file(path))
   ```

### Phase 5: Cleanup & Optimization (Week 6)
**Goal**: Remove legacy code

1. **Remove deprecated files**
   - Delete custom regex parsers
   - Remove octave_transform.py (after migration)
   - Clean up legacy validation

2. **Performance optimization**
   - Benchmark octave-mcp vs regex
   - Cache parsed documents
   - Optimize hot paths

## Implementation Priority Matrix

| Component | Priority | Complexity | Impact | Dependencies |
|-----------|----------|------------|---------|--------------|
| Unified bind tool | HIGH | MEDIUM | HIGH | octave-mcp, schemas |
| Session compression | HIGH | LOW | MEDIUM | octave-mcp |
| Context extraction | MEDIUM | LOW | MEDIUM | octave-mcp |
| Agent migration | MEDIUM | HIGH | HIGH | schemas, bind tool |
| Workflow docs | LOW | LOW | LOW | octave-mcp |
| Legacy removal | LOW | LOW | HIGH | All above complete |

## Risk Mitigation

### 1. Backward Compatibility
- Keep transformation module during transition
- Support both RAPH v4.0 and OCTAVE formats
- Use feature flags for gradual rollout

### 2. Performance
- Benchmark before/after each phase
- Keep regex fallback if octave-mcp is slower
- Consider caching parsed documents

### 3. Schema Evolution
- Start with minimal schemas
- Add validation rules incrementally
- Version schemas for compatibility

## Success Criteria

1. **All OCTAVE parsing uses octave-mcp** (zero custom regex)
2. **Single bind tool** replaces two-step ceremony
3. **All documents validate** against schemas
4. **Performance within 2x** of current implementation
5. **500+ lines of code removed**

## Recommended Immediate Actions

1. **Approve ADR-0149** - It's the right approach
2. **Create identity.oct.schema** - Foundation for bind tool
3. **Implement bind.py** - Prove the concept works
4. **Update one module** - Start with context_extraction.py as pilot
5. **Measure performance** - Ensure octave-mcp meets needs

## Conclusion

ADR-0149 is not just about unifying the bind tool - it's the keystone that enables full OCTAVE alignment across the entire system. The unified bind tool should be built FIRST because:

1. It proves octave-mcp can handle our requirements
2. It establishes patterns for other integrations
3. It provides immediate value (simplified binding)
4. It forces schema definition (which everything else needs)

The build order follows a dependency chain:
```
octave-mcp → schemas → bind tool → compression → context → agents → cleanup
```

This ensures each phase builds on stable foundations from the previous phase.
