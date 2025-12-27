# COMPONENT NORTH STAR: SYSTEM STEWARD

**Component**: System Steward (AI-Powered Context Orchestrator)
**Parent**: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
**Status**: ACTIVE
**Version**: 1.0
**Date**: 2025-12-27

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **System Steward** component.
It inherits all requirements from the **System North Star** and **HestAI-MCP Product North Star**.
Any deviation requires formal amendment.

The System Steward is the AI-powered brain that orchestrates context management, document operations,
and governance enforcement through the HestAI-MCP server.

---

## SECTION 1: THE UNCHANGEABLES (6 Immutables)

### SS-I1: DUAL CONTROL PLANE SEPARATION
**Requirement**: AI orchestration (HestAI-MCP) and document structure (OCTAVE MCP) must remain separate control planes. AI reasons; OCTAVE validates and structures.
**Rationale**: Deterministic document operations cannot depend on probabilistic AI output. AI should generate intent; OCTAVE should enforce correctness.
**Validation**: No OCTAVE tool bypasses validation. All AI-generated content passes through octave_ingest before commit.

| Control Plane | Responsibility | Tools |
|---------------|----------------|-------|
| **Agentic** (HestAI-MCP) | AI reasoning, orchestration, context selection | clock_in, clock_out, context_update, document_submit |
| **Document** (OCTAVE MCP) | Validation, canonicalization, auditability | octave_ingest, octave_create, octave_amend, octave_eject |

### SS-I2: ASYNC-FIRST ARCHITECTURE
**Requirement**: All provider calls, MCP tool invocations, and I/O operations must be async. No blocking calls in the MCP server event loop.
**Rationale**: MCP servers handle concurrent tool calls. Blocking on AI provider responses degrades the entire system.
**Validation**: AIClient uses httpx.AsyncClient. All tool handlers are async def.

### SS-I3: MCP SERVER CHAINING (TOOL FEDERATION)
**Requirement**: HestAI-MCP must act as both MCP Server (outward) and MCP Client (inward to OCTAVE and other MCP servers). Upstream tools are namespaced.
**Rationale**: Enables composition of capabilities. System Steward can leverage OCTAVE, Basic Memory, Git MCP, Repomix MCP as needed.
**Validation**: Connection manager for upstream servers. Explicit allowlist of callable upstream tools.

**Namespacing**:
- octave.ingest, octave.create, octave.amend
- memory.query, memory.write
- git.status, git.diff
- repomix.pack, repomix.grep

### SS-I4: SINGLE WRITER PRESERVATION
**Requirement**: Only System Steward MCP tools may write to .hestai/ directory. Agents never write directly.
**Rationale**: Prevents governance drift. All context mutations are validated, logged, and atomic.
**Validation**: Pre-commit hook blocks direct .hestai/ writes outside MCP tool context.

### SS-I5: INTELLIGENCE IN PROMPTS AND MANIFESTS
**Requirement**: AI reasoning is captured in prompts (for generation) and manifests (for filtering). Runtime execution is deterministic.
**Rationale**: Codified intelligence (manifest schema) is auditable, testable, and human-controllable. Opaque AI is not.
**Validation**: Context filtering uses context-manifest.oct.md. Steward prompts are versioned.

### SS-I6: GRACEFUL DEGRADATION
**Requirement**: If AI provider fails, System Steward falls back to deterministic behavior. AI enhances but is not required.
**Rationale**: Reliability is critical for autonomous systems (inherited I2 from Product North Star).
**Validation**: All AI-dependent operations have fallback paths. Tested via provider mock failures.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **AI Provider** | Must use async (SS-I2) | OpenRouter, OpenAI, Anthropic, local |
| **Control Planes** | Separate (SS-I1) | Which tools in each plane |
| **Manifest Schema** | Must exist (SS-I5) | Schema evolution over time |
| **Upstream MCP Servers** | Namespaced (SS-I3) | Which servers to connect to |
| **Context Selection** | AI-assisted preferred | Deterministic fallback acceptable |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Confidence | Validation Plan |
|----|------------|------------|-----------------|
| SS-A1 | AI can reliably select relevant context given role+focus | 80% | POC with clock_in context selection |
| SS-A2 | OCTAVE MCP can be called from within HestAI-MCP async | 90% | Integration test with octave_ingest |
| SS-A3 | Manifest-driven filtering covers 80%+ of use cases | 75% | Track AI fallback frequency |
| SS-A4 | Provider fallback chain (3+ providers) prevents downtime | 85% | Load test with provider failure injection |

---

## SECTION 4: ARCHITECTURE SUMMARY

### Living Lens Metaphor
```
ORCHESTRA_MAP  = BRAIN   (graph of concepts→code→docs→people)
REPOMIX        = RETINA  (captures code at requested resolution)
OCTAVE         = OPTIC_NERVE (validates and compresses for consumption)
AI_CLIENT      = CORTEX  (interprets meaning from structured input)
```

### MVP Clock-In Sequence
```
STEP_1: Query Orchestra Map for relevant context graph
STEP_2: Invoke Repomix MCP to pack identified files
STEP_3: Call AIClient.complete_text() to generate FAST context
STEP_4: Validate via octave_ingest, write via octave_create
STEP_5: Return context_paths to agent
```

### Orchestration Flow
```
[Agent Request]
    → [System Steward receives via MCP tool]
    → [Query Orchestra Map for dependencies]
    → [AIClient reasons about context/action]
    → [OCTAVE validates output structure]
    → [Write to .hestai/ via octave_create]
    → [Return result to agent]
```

---

## SECTION 5: INTEGRATION POINTS

### Inherits From
- **System North Star** (I1-I6): TDD, phase gates, human primacy, artifacts, quality verification, accountability
- **Product North Star** (I1-I6): Cognitive continuity, structural integrity, dual-layer authority, freshness, Odyssean binding, universal scope

### Sibling Components
- **Orchestra Map**: Provides the dependency graph that System Steward queries
- **Living Artifacts**: Pattern that System Steward generates/updates
- **Odyssean Anchor**: Identity verification that System Steward enforces

### Downstream Consumers
- All HestAI agents use System Steward via MCP tools
- Context files produced by System Steward are read by agents

---

## SECTION 6: IMPLEMENTATION PHASES

### Phase 1 (MVP)
- Wire Repomix MCP into clock_in for whole-repo visibility
- Wire OCTAVE MCP for output validation
- Make AI model configurable via ~/.hestai/config/ai.json
- Implement async AIClient with provider fallback

### Phase 2 (Context Intelligence)
- Implement context-manifest.oct.md for role-based filtering
- Add Orchestra Map stub with typed interface
- Implement context_update and document_submit tools

### Phase 3 (Advanced Features)
- Role-based dynamic context selection
- File watcher for proactive context updates
- Git diff integration for differential OCTAVE streams

---

## DECISION LOG

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-27 | Dual Control Plane architecture | Debates concluded AI reasons, OCTAVE validates |
| 2025-12-27 | Async-first requirement | MCP server cannot block on provider calls |
| 2025-12-27 | MCP Server Chaining pattern | Enables OCTAVE/Memory/Git tool federation |
| 2025-12-27 | Intelligence in manifests | Auditable, testable, human-controllable |

---

**Protection Clause**: Any work contradicting these immutables must STOP, CITE the specific requirement, and ESCALATE to requirements-steward.
