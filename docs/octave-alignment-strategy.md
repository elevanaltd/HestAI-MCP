# OCTAVE Alignment Strategy

**Date**: 2026-01-04
**Author**: holistic-orchestrator
**Purpose**: Align HestAI-MCP with official OCTAVE v5.1.0 specification

## Executive Summary

OCTAVE is the authoritative specification. Our custom extensions (RAPH Vector, odyssean anchor) have diverged from standard OCTAVE syntax. This document identifies divergences and provides a migration path to full OCTAVE compliance.

## Key Principle

> "OCTAVE is the law. Anything we have done in attempts to build something before (RAPH, odyssean anchor, etc) - if there's bits that don't align, that's a fault of our own. We should have followed OCTAVE's syntax." - User directive

## Identified Divergences

### 1. Custom Document Types

**Current (Non-compliant)**:
```octave
===RAPH_VECTOR::v4.0===
```

**OCTAVE Standard**:
```octave
===RAPH_VECTOR===
META:
  TYPE::RAPH_VECTOR
  VERSION::4.0
```

**Issue**: We're using `::version` suffix in the envelope, which isn't standard OCTAVE.

### 2. Section Headers

**Current (Non-compliant)**:
```octave
## BIND
## TENSION
## COMMIT
## ARM
```

**OCTAVE Standard**: OCTAVE doesn't use markdown-style headers. Sections are just fields at the top level:
```octave
BIND::[
  ROLE::holistic-orchestrator,
  COGNITION::LOGOS::ATHENA,
  AUTHORITY::RESPONSIBLE[main]
]
```

### 3. Multi-Value Synthesis

**Current (Questionable)**:
```octave
COGNITION::LOGOS::ATHENA⊕ODYSSEUS⊕DAEDALUS
```

**OCTAVE Standard**: The `⊕` operator exists in OCTAVE for synthesis, but our usage might be non-standard. Standard OCTAVE would likely use:
```octave
COGNITION::LOGOS::[ATHENA, ODYSSEUS, DAEDALUS]
```
Or potentially:
```octave
COGNITION::LOGOS::ATHENA⊕ODYSSEUS⊕DAEDALUS  # If synthesis is semantically correct
```

### 4. TENSION Line Format

**Current (Custom)**:
```octave
L1::[Constraint]⇌CTX:file.py:123[state]→TRIGGER[action]
```

**OCTAVE Standard**: This appears to be a custom micro-syntax. Standard OCTAVE would be:
```octave
TENSIONS::[
  {
    LINE::1,
    CONSTRAINT::description,
    CONTEXT::file.py:123,
    STATE::current_state,
    TRIGGER::action
  }
]
```

### 5. Custom Operators in Context

**Current**:
- `⇌` (bidirectional tension)
- `→` (flow/trigger)
- Custom bracketing: `[state]`, `TRIGGER[action]`

**OCTAVE Standard**: OCTAVE supports these Unicode operators, but our specific usage pattern appears custom.

## Migration Strategy

### Phase 1: Preserve Backward Compatibility (Immediate)

1. **Dual Parser Support**: Maintain both parsers during transition
   ```python
   def parse_vector(content: str) -> dict:
       try:
           # Try standard OCTAVE first
           return octave_mcp.parse(content)
       except:
           # Fall back to custom RAPH parser
           return parse_raph_custom(content)
   ```

2. **Version Detection**: Check document format version
   ```python
   if "===RAPH_VECTOR::v4.0===" in content:
       # Legacy format
   elif "VERSION::4.0" in content:
       # New OCTAVE-compliant format
   ```

### Phase 2: Transform to OCTAVE-Compliant Format

Create transformation functions to convert our custom format to standard OCTAVE:

```python
def raph_to_octave(raph_content: str) -> str:
    """Convert RAPH Vector v4.0 to OCTAVE-compliant format."""

    # 1. Fix envelope
    content = raph_content.replace(
        "===RAPH_VECTOR::v4.0===",
        "===RAPH_VECTOR===\nMETA:\n  TYPE::RAPH_VECTOR\n  VERSION::4.0"
    )

    # 2. Convert ## headers to top-level fields
    content = content.replace("## BIND\n", "BIND::[\n")
    content = content.replace("## TENSION\n", "TENSIONS::[\n")
    content = content.replace("## COMMIT\n", "COMMIT::[\n")

    # 3. Convert TENSION lines to structured format
    # L1::[X]⇌CTX:Y[Z]→TRIGGER[A] becomes:
    # {LINE::1, CONSTRAINT::X, CONTEXT::Y, STATE::Z, TRIGGER::A}

    return content
```

### Phase 3: Update Generation Code

Modify our code to generate OCTAVE-compliant output:

```python
# Old (non-compliant)
vector = f"""===RAPH_VECTOR::v4.0===
## BIND
ROLE::{role}
"""

# New (OCTAVE-compliant)
doc = octave_mcp.create_document("RAPH_VECTOR")
octave_mcp.set_field(doc, "META.TYPE", "RAPH_VECTOR")
octave_mcp.set_field(doc, "META.VERSION", "4.0")
octave_mcp.set_field(doc, "BIND.ROLE", role)
vector = octave_mcp.emit(doc)
```

### Phase 4: Semantic Decisions

#### 4.1 Synthesis Operator Usage

**Decision Required**: Is `COGNITION::LOGOS::ATHENA⊕ODYSSEUS` semantically correct?

- If these are **combined/synthesized** archetypes (agent embodies all three): Keep `⊕`
- If these are **alternative** archetypes (agent can be any of three): Use list `[ATHENA, ODYSSEUS, DAEDALUS]`
- If these are **primary + secondary** archetypes: Use structured format

**Recommendation**: Based on OCTAVE semantics, synthesis (`⊕`) implies merging/combining. Our usage appears correct.

#### 4.2 TENSION Micro-Syntax

**Decision Required**: Should we preserve our TENSION line format?

**Options**:
1. Keep as custom micro-syntax within string value (OCTAVE allows this)
2. Expand to full OCTAVE structure (more verbose but standard)
3. Create OCTAVE schema extension for TENSION format

**Recommendation**: Keep as micro-syntax initially (Option 1), as OCTAVE allows domain-specific micro-syntaxes within string values.

## Implementation Checklist

### Immediate Actions
- [x] Document divergences from OCTAVE spec
- [ ] Create `raph_to_octave()` transformation function
- [ ] Add OCTAVE-compliant generation option
- [ ] Update tests to accept both formats

### Week 1-2
- [ ] Implement dual parser in odyssean_anchor.py
- [ ] Create migration script for existing RAPH vectors
- [ ] Update documentation to show OCTAVE-compliant examples

### Week 3-4
- [ ] Modify all generation code to emit OCTAVE-compliant format
- [ ] Add deprecation warnings for v4.0 format
- [ ] Update all tests to use new format

### Week 5-6
- [ ] Remove support for non-compliant format
- [ ] Full validation against octave-mcp parser
- [ ] Performance benchmarking

## Benefits of Alignment

1. **Standardization**: Align with broader OCTAVE ecosystem
2. **Tool Support**: Use octave-mcp for parsing/validation
3. **Maintainability**: Remove custom parsing code
4. **Interoperability**: Other OCTAVE tools can process our documents
5. **Future-Proofing**: Automatic compatibility with OCTAVE spec updates

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing RAPH vectors | High | Dual parser support during transition |
| Performance regression | Medium | Benchmark before/after |
| Loss of semantic information | Low | Careful mapping of custom syntax |
| octave-mcp limitations | Medium | Contribute back to octave-mcp project |

## Success Criteria

1. All RAPH vectors parse successfully with `octave_mcp.parse()`
2. Zero custom OCTAVE parsing code (100% delegation to octave-mcp)
3. Performance within 2x of current implementation
4. All tests pass with OCTAVE-compliant format

## Next Steps

1. **Immediate**: Implement transformation function
2. **This Week**: Test octave-mcp with our use cases
3. **Next Sprint**: Begin migration of generation code
4. **End of Month**: Deprecate v4.0 format

---

## Appendix: Format Comparison

### Before (RAPH v4.0 - Non-compliant)
```octave
===RAPH_VECTOR::v4.0===
## BIND
ROLE::holistic-orchestrator
COGNITION::LOGOS::ATHENA⊕ODYSSEUS
AUTHORITY::RESPONSIBLE[main]

## TENSION
L1::[Manual parsing]⇌CTX:parser.py:86[regex]→TRIGGER[migrate]

## COMMIT
ARTIFACT::test.md
GATE::validation
===END_RAPH_VECTOR===
```

### After (OCTAVE-compliant)
```octave
===RAPH_VECTOR===
META:
  TYPE::RAPH_VECTOR
  VERSION::5.0
  SCHEMA::ODYSSEAN_ANCHOR

BIND:
  ROLE::holistic-orchestrator
  COGNITION::LOGOS::ATHENA⊕ODYSSEUS
  AUTHORITY::RESPONSIBLE[main]

TENSIONS::[
  L1::[Manual parsing]⇌CTX:parser.py:86[regex]→TRIGGER[migrate]
]

COMMIT:
  ARTIFACT::test.md
  GATE::validation

===END===
```

Note: The TENSIONS section keeps the micro-syntax as a string value, which is valid OCTAVE.
