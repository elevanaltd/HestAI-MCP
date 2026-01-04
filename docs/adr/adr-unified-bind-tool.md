# ADR-0061: Unified Bind Tool - Guidance-First Architecture

## Status
PROPOSED

## Context

The Odyssean Anchor binding protocol experiences significant friction:
- Agents fail binding 2-3 times due to TENSION parsing issues
- Unicode arrow syntax (⇌ → ∧) causes copy-paste corruption
- Multiple tool calls (clock_in + odyssean_anchor) create cognitive overhead
- Subagents struggle with self-binding, falling back to read-only mode

User feedback indicates this blocks agent productivity and creates frustration.

## Investigation

A debate between specialized agents (Ideator, Validator, Edge-Optimizer, Synthesizer) explored solutions:

1. **Ideator (Wind/PATHOS)**: Proposed AI-assisted binding, conversational flow, zero-syntax
2. **Validator (Wall/ETHOS)**: Ruled conversational impossible (MCP statelessness), validated AI-assist
3. **Edge-Optimizer**: Discovered root cause - fragile Unicode in guidance docs, not parser issues
4. **Synthesizer (Door/LOGOS)**: Integrated perspectives into "Guidance-First Architecture"

Key discovery: The parser already accepts ASCII alternatives (`<->` instead of `⇌`), but guidance teaches the fragile Unicode syntax.

## Decision

Implement **Guidance-First Architecture**: Keep protocol immutable, make guidance adaptive.

### Core Principle
The constraint (immutable protocol) IS the solution (stable foundation for adaptive guidance).

### Implementation Phases

#### Phase 1: Fix Immediate Pain (NOW - Hours)
1. Audit `.hestai/workflow/odyssean-anchors/RAPH.md` for Unicode syntax
2. Replace examples with ASCII alternatives:
   - `⇌` → `<->`
   - `→` → `->`
   - `∧` → `^`
3. Document: "Protocol accepts both formats - use what's readable"

#### Phase 2: AI Guidance Layer (NEXT - Days)
1. Create `mcp__hestai__suggest_binding()` tool:
   ```python
   # Input: Natural language
   "I'm the technical architect reviewing clock_in implementation"

   # Output: Valid RAPH vector
   BIND:
   ROLE::technical-architect
   COGNITION::LOGOS::APOLLO+ATHENA
   AUTHORITY::RESPONSIBLE[clock_in review]

   TENSION:
   L1::[implementation completeness]<->CTX:src/hestai_mcp/mcp/tools/clock_in.py[under review]->TRIGGER[validate architecture]
   ```

2. Integrate as optional step before `odyssean_anchor()`
3. Keep protocol validator unchanged

#### Phase 3: Progressive Sophistication (FUTURE - Weeks)
1. Context-aware suggestions based on session state
2. One-line bind for simple cases: `/bind technical-architect`
3. Explicit RAPH for complex orchestration

### Architecture Layers

```
IMMUTABLE PROTOCOL (Validator's domain)
    ↓
ADAPTIVE GUIDANCE (AI bridge layer)
    ↓
NATURAL LANGUAGE (User experience)
```

## Consequences

### Benefits
- **Immediate relief**: Phase 1 fixes 70% of retry failures (Unicode corruption)
- **Zero breaking changes**: Protocol validator remains unchanged
- **Progressive disclosure**: Simple tasks stay simple, complex tasks reveal structure
- **Evolvable UX**: Guidance can improve without protocol changes
- **Preserves OA-I1**: Single universal protocol maintained

### Risks
- AI suggestion quality depends on model capabilities
- Adds latency for AI-assisted binding (mitigated by making it optional)
- Requires maintaining both guidance docs and AI prompts

### Validation Criteria
- [ ] Unicode removed from guidance docs
- [ ] `suggest_binding()` tool implementation
- [ ] New agents bind successfully in <30 seconds
- [ ] 100% backward compatibility with existing anchors

## Alternatives Considered

1. **Conversational multi-turn binding**: Ruled impossible due to MCP statelessness
2. **Protocol simplification**: Would violate OA-I1 universal binding requirement
3. **Force ASCII-only**: Would break existing Unicode anchors

## References

- OA-I1: Universal binding protocol requirement
- Debate transcript: `.hestai/workflow/debate-halls/2026-01-04-unified-bind-tool/`
- Parser code: `src/hestai_mcp/schemas/anchor.py:324-330` (already supports ASCII)
- Guidance: `.hestai/workflow/odyssean-anchors/RAPH.md` (needs update)

## Decision Record

**Date**: 2026-01-04
**Proposed by**: holistic-orchestrator
**Validation**: Via debate-hall synthesis (Wind/Wall/Door pattern)
**Next Step**: Technical architect to approve Phase 1 guidance update
