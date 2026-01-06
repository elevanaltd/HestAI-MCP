# ADR-0039: Agent Master Forge

- **Status**: Implemented
- **Type**: ADR
- **Author**: holistic-orchestrator
- **Created**: 2025-12-24
- **Updated**: 2025-12-27
- **GitHub Issue**: [#39](https://github.com/elevanaltd/HestAI-MCP/issues/39)
- **Phase**: B2
- **From-RFC**: RFC-0039

## Context

Agent creation required a standardized methodology for producing high-performance OCTAVE agents with:
- Consistent cognitive foundations (LOGOS, ETHOS, PATHOS)
- True modularity through semantic weaving (not text block injection)
- Archetype accumulation for capability enhancement
- Size optimization (90-120 lines target)

Previous approaches suffered from "fake modularity" - 1:1 pattern-to-role mappings that underperformed by 7-10%.

## Decision

### Core Principle

**TRUE MODULARITY = Components that modify the whole, not add to the whole**

### Architecture

1. **Immutable Shanks**: Cognitive foundations (LOGOS/ETHOS/PATHOS) that never change
2. **Archetype Accumulation**: Capabilities bring required archetypes to cognitive foundation
3. **Semantic Weaving**: Patterns integrate at specific insertion points, not concatenate
4. **Emergent Properties**: Combinations create new capabilities

### Agent Templates

Two template types:
- **Governance Agent Template**: Constitutional foundation + 4-phase RAPH processing
- **Execution Agent Template**: 3-phase RAPH processing, minimal overhead

### Quality Validation

- RAPH sequential processing directive mandatory
- Size target: 90-120 lines, maximum 150 lines
- 96%+ token efficiency through RAPH processing
- No OCTAVE terminology in user-facing output

## Consequences

### Positive

- **Consistent agent quality** across all HestAI agents
- **True reusability** - capabilities enhance ANY compatible role
- **Performance gains**: 49% size reduction with improved performance (C038)
- **Token efficiency**: 96%+ through RAPH processing (C039)

### Negative

- **Learning curve** for semantic weaving concepts
- **Template complexity** requires understanding of OCTAVE internals

## Implementation

**Status**: COMPLETE

**Evidence**:
- All bundled agents in `src/hestai_mcp/_bundled_hub/agents/` use this methodology (injected to `.hestai-sys/agents/`)
- Empirical validation through C035/C036/C038/C039 testing
- Constitutional foundation provides +39% performance for governance roles

**Location**: `src/hestai_mcp/_bundled_hub/agents/` (injected to `.hestai-sys/agents/`; agent definitions follow this pattern)

## Related Documents

- [ADR-0040: Agent Patterns Library](./adr-0040-agent-patterns-library.md)
- [GitHub Issue #39](https://github.com/elevanaltd/HestAI-MCP/issues/39)
- Bundled agents: `src/hestai_mcp/_bundled_hub/agents/*.oct.md` (runtime: `.hestai-sys/agents/*.oct.md`)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
