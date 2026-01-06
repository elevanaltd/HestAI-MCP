# RAPH Vector and OCTAVE: Understanding the Distinction

**Date**: 2026-01-04
**Context**: Extracted from PR #152 analysis

## The Two-Layer Model

After comprehensive analysis, we've identified that RAPH Vector and OCTAVE agent documents serve different purposes:

### Layer 1: Design-Time (Agent Constitutions)
- **Format**: Standard OCTAVE agent documents (8 sections)
- **Location**: `.hestai-sys/agents/{role}.oct.md` (source: `src/hestai_mcp/_bundled_hub/agents/{role}.oct.md`)
- **Purpose**: Define HOW TO BUILD agents
- **Content**: Full constitution with behavioral mandates, archetypes, etc.

### Layer 2: Runtime (RAPH Vector / Identity Binding)
- **Format**: OCTAVE-compliant IDENTITY blocks (4 sections)
- **Location**: Generated during binding, stored in session
- **Purpose**: Prove agent HAS ABSORBED its constitution
- **Content**: Binding proof with role, tensions, and commit

## Why Both Exist

1. **Constitution** (Design-Time): The blueprint for an agent's behavior
2. **RAPH Vector** (Runtime): The proof that the agent understood and bound to that blueprint

This is analogous to:
- A driver's license manual (constitution) vs. the actual license (RAPH/binding proof)
- A job description (constitution) vs. signing the employment contract (RAPH/binding proof)

## Implementation Approach

Instead of trying to eliminate RAPH Vector or force it to be a full agent document, we:

1. **Keep RAPH Vector** as the runtime binding proof format
2. **Make it OCTAVE-compliant** by following standard syntax
3. **Define it as a schema** (`identity.oct.schema`)
4. **Use octave-mcp** to parse and validate both layers

This preserves the valuable architectural pattern while aligning with OCTAVE standards.
