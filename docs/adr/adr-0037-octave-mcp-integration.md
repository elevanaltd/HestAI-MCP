# ADR-0037: OCTAVE-MCP Library Integration

**Status**: PROPOSED
**Date**: 2026-01-04
**Author**: holistic-orchestrator
**Supersedes**: Custom regex-based OCTAVE parsing
**Implements**: I2 (Structural Integrity Priority), I5 (Odyssean Identity Binding)
**GitHub Issue**: #37 (to be created)

---

## Context

### The Problem

The HestAI-MCP codebase currently implements custom regex-based parsing for OCTAVE documents across multiple modules:

1. **Fragmented Implementation**: 6+ separate modules implement their own OCTAVE parsing logic
2. **Regex Brittleness**: Pattern-based extraction is error-prone and doesn't understand OCTAVE semantics
3. **No Validation**: Current implementation lacks structural validation against OCTAVE spec
4. **Maintenance Burden**: Each update to OCTAVE spec requires updating multiple regex patterns
5. **Missing Features**: No access to tokenization, canonical emission, or schema validation

### The Solution: octave-mcp v0.3.0

OCTAVE-MCP v0.3.0 is now available on PyPI as the official OCTAVE parser library:
- **52 public API exports** for comprehensive OCTAVE operations
- **Semantic parsing** that understands OCTAVE structure, not just patterns
- **Canonical emission** for generating properly formatted OCTAVE
- **Schema validation** against official OCTAVE specifications
- **Loss accounting** system for LLM communication consistency

---

## Decision

Adopt octave-mcp v0.3.0 as a core dependency using a **hybrid 3-layer architecture** that preserves critical security boundaries while adding semantic parsing capabilities.

### Critical Architectural Concerns

#### RAPH Vector v4.0 Custom Extensions
The odyssean_anchor.py module implements custom OCTAVE extensions not in the base spec:
- **Multiple archetype synthesis**: `COGNITION::LOGOS::ATLAS⊕ODYSSEUS⊕DAEDALUS`
- **ASCII synthesis alias**: Accepts `+` as alternative to `⊕`
- **Custom validation rules**: GENERIC_ARTIFACTS, PLACEHOLDER_VALUES checks
- **Security-hardened extraction**: Prevents header smuggling attacks

**Requirement**: octave-mcp must support extension points for RAPH-specific semantics or we maintain a custom validation layer.

#### AI-Driven OCTAVE Generation
The compression.py module generates OCTAVE via AI prompts, not programmatic construction. We'll implement a **validation-in-the-middle** approach:

```python
# Phase 1: AI generates OCTAVE (preserve existing strength)
octave_content = await client.complete_text(request)

# Phase 2: Parse and validate with octave-mcp (add reliability)
doc = octave_mcp.parse(octave_content)
validation_errors = octave_mcp.validate(doc, schema="SESSION_LOG")

# Phase 3: Canonical re-emission if needed
if validation_errors:
    octave_content = octave_mcp.emit(doc)  # Fix formatting issues
```

### OCTAVE Compliance Strategy

**Key Principle**: OCTAVE is the authoritative specification. Our custom RAPH Vector format must align with OCTAVE standards.

#### Format Transformation Approach

We've identified that our RAPH Vector v4.0 format diverges from OCTAVE in several ways:
- Non-standard envelope suffix (::v4.0)
- Markdown-style headers (## BIND) instead of OCTAVE fields
- Custom micro-syntax that needs preservation

A transformation module (`octave_transform.py`) handles bidirectional conversion between formats during migration.

### Hybrid 3-Layer Architecture

Instead of wholesale replacement, implement graduated integration:

```
┌─────────────────────────────────────────────────────┐
│ Layer 3: Domain Logic (odyssean_anchor.py)         │
│ - RAPH Vector v4.0 validation                       │
│ - Custom extensions (⊕ synthesis, generic checks)   │
│ - Security boundaries                               │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│ Layer 2: OCTAVE Operations (NEW - octave-mcp)      │
│ - parse() → semantic AST                           │
│ - validate() → schema compliance                    │
│ - emit() → canonical formatting                     │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│ Layer 1: Text Operations (PRESERVE - regex)        │
│ - Security-hardened section extraction              │
│ - Fast filtering for small documents                │
│ - Fallback for octave-mcp failures                  │
└─────────────────────────────────────────────────────┘
```

### Integration Strategy with Graceful Degradation

#### Phase 0: Validation & Prototyping (BLOCKING GATE)
Before any code changes, validate octave-mcp compatibility:
```python
# tests/integration/octave_mcp/test_raph_compatibility.py
def test_octave_mcp_parses_raph_vector():
    """Verify octave-mcp handles RAPH Vector v4.0 extensions."""
    raph_vector = load_sample_raph_vector()  # With ⊕ synthesis
    doc = octave_mcp.parse(raph_vector)
    cognition = octave_mcp.get_field(doc, "BIND.COGNITION")
    assert "⊕" in cognition or "+" in cognition  # Must preserve
```

#### Phase 1: Add Dependency with Version Constraints
```toml
# pyproject.toml
dependencies = [
    "octave-mcp>=0.3.0,<1.0.0",  # Pin to minor version for stability
    # ... existing dependencies
]
```

#### Phase 2: Low-Risk Migration with Fallback

Implement hybrid parsing with graceful degradation:

```python
# Pattern: Try octave-mcp first, fallback to regex
def extract_section(octave_content: str, section_name: str) -> str | None:
    try:
        doc = octave_mcp.parse(octave_content)
        return octave_mcp.get_field(doc, section_name)
    except Exception as e:
        logger.warning(f"octave-mcp failed: {e}, using regex fallback")
        return _extract_section_regex(octave_content, section_name)
```

#### Phase 3: AI Output Validation

Use octave-mcp for generating OCTAVE documents:

```python
# Generate canonical OCTAVE
doc = octave_mcp.create_document("SESSION_LOG")
octave_mcp.set_field(doc, "DECISIONS", decisions)
octave_mcp.set_field(doc, "OUTCOMES", outcomes)
canonical = octave_mcp.emit(doc)  # Guaranteed valid OCTAVE
```

### Integration Points

1. **context_extraction.py**: Replace `_extract_section()` with `octave_mcp.parse()`
2. **odyssean_anchor.py**: Use `octave_mcp.get_section()` for BIND/COMMIT extraction
3. **compression.py**: Replace `compress_to_octave()` internals with `octave_mcp.emit()`
4. **octave-validator.py**: Delegate to `octave_mcp.validate()` for schema checking
5. **verification.py**: Use `octave_mcp.get_field()` for claim extraction
6. **learnings_index.py**: Parse with `octave_mcp.parse()` before key extraction

---

## Technical Specification

### API Usage Patterns

```python
import octave_mcp

# Discovery
octave_mcp.list_exports('functions')  # Available operations
octave_mcp.list_exports('schemas')    # Supported document types

# Parsing
doc = octave_mcp.parse(octave_string)
if octave_mcp.is_valid(doc):
    field = octave_mcp.get_field(doc, "DECISIONS")

# Emission
doc = octave_mcp.create_document("PROJECT_CONTEXT")
octave_mcp.set_field(doc, "PHASE", "B1_FOUNDATION")
canonical = octave_mcp.emit(doc)

# Validation
errors = octave_mcp.validate(octave_string, schema="SESSION_LOG")
```

### Migration Safety

1. **Parallel Implementation**: Keep regex fallbacks during transition
2. **Test Coverage**: Verify octave-mcp parsing matches expected behavior
3. **Performance Monitoring**: octave-mcp uses Rust core for speed
4. **Version Pinning**: Use `>=0.3.0,<1.0.0` to avoid breaking changes

---

## Consequences

### Positive

- **Correctness**: Semantic parsing eliminates regex edge cases
- **Maintainability**: Single source of truth for OCTAVE parsing
- **Features**: Access to tokenization, validation, transformation APIs
- **Performance**: Rust-based parser faster than Python regex for complex documents
- **Compliance**: Automatic alignment with OCTAVE spec updates

### Negative

- **Dependency**: External dependency adds supply chain consideration
- **Learning Curve**: Developers need to learn octave-mcp API (mitigated by good docs)
- **Migration Effort**: ~20 files need updating (systematic, not complex)

### Risks

- **RAPH Vector Incompatibility**: octave-mcp may not support custom extensions
  - *Mitigation*: Phase 0 validation gate, maintain custom validation layer
- **Version Compatibility**: octave-mcp API changes could break code
  - *Mitigation*: Pin to 0.3.x series, monitor changelog
- **Performance Regression**: External library overhead for small documents
  - *Mitigation*: Benchmark before migration, maintain regex for hot paths
- **Security Boundary Weakening**: Path traversal via malicious OCTAVE
  - *Mitigation*: Security testing, preserve hardened extraction functions
- **Test Migration Burden**: 3031 lines of odyssean_anchor tests
  - *Mitigation*: Parallel implementation, 100% behavioral equivalence required

---

## Implementation Plan (Revised: 10-12 Week Timeline)

### Phase 0: Validation & Prototyping (Week 1-2) - BLOCKING GATE
- [ ] Install octave-mcp>=0.3.0 in dev environment
- [ ] Create `tests/integration/octave_mcp/test_raph_compatibility.py`
- [ ] Verify RAPH Vector v4.0 parsing (⊕ synthesis, custom validations)
- [ ] Benchmark performance (requirement: <2x regex for small docs)
- [ ] Create security test for path traversal protection
- [ ] Document API patterns in `docs/octave-mcp-integration.md`

**GATE**: Proceed ONLY if all validations pass. If octave-mcp incompatible with RAPH → REJECT.

### Phase 1: Low-Risk Integration (Week 3-4)
- [ ] Migrate context_extraction.py (108 lines, simple regex)
- [ ] Add graceful degradation (regex fallback on failure)
- [ ] Update tests with parallel validation
- [ ] Monitor: Parse error rate (requirement: 0%)

### Phase 2: AI Validation Layer (Week 5-6)
- [ ] Add octave-mcp validation to compression.py output
- [ ] Implement auto-repair with `octave_mcp.emit()`
- [ ] Measure AI hallucination detection rate
- [ ] Update compression tests

### Phase 3: odyssean_anchor Migration (Week 7-10) - HIGH RISK
- [ ] Implement parallel validation (regex + octave-mcp)
- [ ] Feature flag: `HESTAI_OCTAVE_MCP_ENABLED` (default: false)
- [ ] Run 3031-line test suite with both implementations
- [ ] Verify 100% behavioral equivalence
- [ ] Benchmark: Performance comparison
- [ ] Gradual rollout: 10% → 50% → 100%

### Phase 4: Cleanup (Week 11-12)
- [ ] Remove deprecated regex patterns (ONLY if Phase 3 successful)
- [ ] Update documentation
- [ ] Final performance benchmarking
- [ ] Post-deployment monitoring (30 days)

---

## Success Metrics

1. **Zero Parsing Errors**: No OCTAVE parsing failures in production
2. **Performance**: <100ms parse time for 10KB OCTAVE documents
3. **Test Coverage**: 100% of OCTAVE operations covered by tests
4. **Code Reduction**: ~500 lines of regex code eliminated

---

## References

- [octave-mcp GitHub](https://github.com/elevanaltd/octave-mcp)
- [octave-mcp PyPI](https://pypi.org/project/octave-mcp/)
- [Public API Reference](https://github.com/elevanaltd/octave-mcp/blob/main/docs/public-api-reference.md)
- ADR-0036: Odyssean Anchor Binding (uses OCTAVE parsing)
- Issue #11: Odyssean Anchor Implementation
