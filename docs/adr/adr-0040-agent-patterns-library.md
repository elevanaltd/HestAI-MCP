# ADR-0040: Agent Patterns Library

- **Status**: Implemented
- **Type**: ADR
- **Author**: holistic-orchestrator
- **Created**: 2025-12-24
- **Updated**: 2025-12-27
- **GitHub Issue**: [#40](https://github.com/elevanaltd/HestAI-MCP/issues/40)
- **Phase**: B2
- **From-RFC**: RFC-0040

## Context

Agent creation needed a comprehensive pattern library that:
- Provides reusable transformation patterns
- Defines anti-pattern detection
- Establishes quality assurance checklists
- Demonstrates true modularity (vs fake 1:1 mappings)

The pattern library complements ADR-0039 (Agent Master Forge) by providing the specific patterns used during agent forging.

## Decision

### Pattern Taxonomy

1. **Immutable Patterns**: Cognitive foundations (shanks) - never change
2. **Accumulative Patterns**: Archetypes - combine through capability requirements
3. **Weavable Patterns**: Capabilities - integrate at semantic insertion points
4. **Universal Patterns**: Enhancements - apply to any role type

### Transformation Patterns (P0-P5)

| Pattern | Purpose | Mandatory |
|---------|---------|-----------|
| P0 | Technical-to-Structured Risk (PANDORA) | Yes |
| P0 | RAPH Sequential Processing | Yes (v4.0) |
| P1 | Process-to-Systemic Engine | Yes |
| P2 | Reliability-to-Verification Protocol | Yes |
| P3 | Dimensions-to-Analysis Matrix | Yes |
| P4 | Behavior-to-Quality Gates | Yes |
| P5 | Governance-to-Constitutional Foundation | Conditional |

### Anti-Pattern Library

Structured as: `{TRIGGER, SCOPE, IMPACT, SYMPTOM}`

- **PANDORA_PATTERNS**: Small change → systemic cascade
- **ICARIAN_DESIGNS**: Premature optimization → brittle complexity
- **SISYPHEAN_LOOPS**: Superficial fix → recurring effort
- **TROJAN_DEPENDENCIES**: Dependency update → hidden vulnerability

### Fatal Compilation Errors (E01-E13)

Critical failures that produce unreliable agents, including:
- E01: Verification absence
- E07: Framework contamination (OCTAVE in output)
- E08: Missing RAPH processing
- E12: Constitutional misapplication

## Consequences

### Positive

- **Consistent quality** through mandatory patterns
- **Error prevention** via anti-pattern detection
- **True modularity** - patterns genuinely reusable across role types
- **Evidence-based**: Patterns validated through C035-C039 testing

### Negative

- **Complexity**: 19 mandatory components + conditional
- **Maintenance**: Pattern library requires updates with learnings

## Implementation

**Status**: COMPLETE

**Evidence**:
- C038: 49% size reduction with improved performance
- C039: 96%+ token efficiency with RAPH processing
- C035: Fake modularity underperforms by 7-10%

**Location**: Patterns applied via `hub/governance/agents/` agent definitions

## Related Documents

- [ADR-0039: Agent Master Forge](./adr-0039-agent-master-forge.md)
- [GitHub Issue #40](https://github.com/elevanaltd/HestAI-MCP/issues/40)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
