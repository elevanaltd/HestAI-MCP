---
component: system_steward
scope: subsystem
phase: B1
created: 2025-12-27
status: in_progress
approved_by: requirements-steward
approved_date: 2025-12-28
parent_north_star: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
version: 1.3
---

# COMPONENT NORTH STAR: SYSTEM STEWARD

**Component**: System Steward (AI-Powered Context Orchestrator)
**Parent**: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
**Status**: IN_PROGRESS (SS-I2, SS-I3, SS-I6 complete)
**Version**: 1.3
**Date**: 2025-12-28
**Reviewed By**: requirements-steward
**Review Date**: 2025-12-28

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **System Steward** component.
It inherits all requirements from:
- **System North Star** (I1 through I6) - Constitutional principles
- **HestAI-MCP Product North Star** (I1 through I6) - Product requirements

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

## SECTION 2B: SCOPE BOUNDARIES

### What This Component IS

| Scope | Description |
|-------|-------------|
| AI-Powered Context Orchestration | Intelligent selection and synthesis of relevant context for agent roles |
| MCP Tool Execution | Handles tool invocations from agents through the MCP protocol |
| OCTAVE Validation Routing | Routes AI-generated content through OCTAVE MCP for validation |
| Context Selection and Synthesis | Curates context based on role, focus, and project state |
| Provider Fallback Management | Manages AI provider chains with graceful degradation |

### What This Component IS NOT

| Out of Scope | Responsible Component |
|--------------|----------------------|
| Direct File Writes | octave_create via OCTAVE MCP |
| Identity Validation | odyssean_anchor tool |
| Session Management | clock_in / clock_out tools |
| Persistent Memory Storage | Basic Memory MCP |
| Git Operations | Git MCP or direct git CLI |
| Codebase Packaging | Repomix MCP |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Confidence | Impact | Validation Plan | Owner | Timing |
|----|------------|------------|--------|-----------------|-------|--------|
| SS-A1 | AI can reliably select relevant context given role+focus | 80% | High | POC with clock_in context selection | implementation-lead | Before B1 |
| SS-A2 | OCTAVE MCP can be called from within HestAI-MCP async | 90% | High | Integration test with octave_ingest | implementation-lead | Before B1 |
| SS-A3 | Manifest-driven filtering covers 80%+ of use cases | 75% | Medium | Track AI fallback frequency | implementation-lead | During B2 |
| SS-A4 | Provider fallback chain (3+ providers) prevents downtime | 85% | High | Load test with provider failure injection | technical-architect | Before B1 |
| SS-A5 | MCP server chaining complexity manageable | 75% | High | Integration test with 3+ upstream servers | technical-architect | Before B1 |
| SS-A6 | Context manifest schema covers role filtering needs | 70% | Medium | Test with 5+ roles | implementation-lead | During B2 |

---

## SECTION 4: ARCHITECTURE SUMMARY

### Living Lens Metaphor
```
ORCHESTRA_MAP  = BRAIN   (graph of concepts->code->docs->people)
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
    -> [System Steward receives via MCP tool]
    -> [Query Orchestra Map for dependencies]
    -> [AIClient reasons about context/action]
    -> [OCTAVE validates output structure]
    -> [Write to .hestai/ via octave_create]
    -> [Return result to agent]
```

---

## SECTION 5: INTEGRATION POINTS

### Inherits From
- **System North Star** (I1 through I6): TDD, phase gates, human primacy, artifacts, quality verification, accountability
- **Product North Star** (I1 through I6): Cognitive continuity, structural integrity, dual-layer authority, freshness, Odyssean binding, universal scope

### Sibling Components
- **Orchestra Map**: Provides the dependency graph that System Steward queries
- **Living Artifacts**: Pattern that System Steward generates/updates
- **Odyssean Anchor**: Identity verification that System Steward enforces

### Downstream Consumers
- All HestAI agents use System Steward via MCP tools
- Context files produced by System Steward are read by agents

### Child Components (Tools)
| Tool | Purpose | North Star |
|------|---------|------------|
| clock_in | Session registration, context synthesis | 000-CLOCK-IN-NORTH-STAR.md |
| clock_out | Session archival, transcript compression | (TBD) |
| odyssean_anchor | Identity validation, binding ceremony | (TBD) |
| context_update | Mid-session context mutation | (TBD) |
| document_submit | Document routing and placement | (TBD) |

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
| 2025-12-28 | Added scope boundaries | requirements-steward review: clarity on component responsibility |
| 2025-12-28 | Enhanced assumption register | requirements-steward review: PROPHETIC_VIGILANCE compliance |

---

## COMMITMENT CEREMONY

**Status**: ACTIVE
**Reviewer**: requirements-steward
**Review Date**: 2025-12-28

**The Oath**:
> "These 6 Immutables (SS-I1 through SS-I6) are the binding requirements for System Steward implementation. Any contradiction requires STOP, CITE, ESCALATE."

**Amendments Applied**:
1. Added YAML front-matter
2. Added Scope Boundaries section (IS/IS NOT)
3. Enhanced Assumption Register with SS-A5 and SS-A6
4. Added Impact, Owner, Timing columns to assumptions
5. Added Child Components table
6. Added Evidence Summary section
7. Updated to v1.2: Aligned with ns-component-create standard

---

## EVIDENCE SUMMARY

### Constitutional Compliance
- **Total Immutables**: 6 (within 5-9 range per Miller's Law)
- **System-Agnostic**: 6/6 passed Technology Change Test (no technology-specific language)
- **Assumptions Tracked**: 6 (6+ required per PROPHETIC_VIGILANCE)
- **Critical Assumptions**: 4 requiring pre-B1 validation (SS-A1, SS-A2, SS-A4, SS-A5)
- **Commitment Ceremony**: Completed 2025-12-28

### Quality Gates
- **YAML Front-Matter**: Present
- **Inheritance Chain**: Documented (System NS + Product NS)
- **Miller's Law**: 6 immutables (within 5-9 range)
- **PROPHETIC_VIGILANCE**: 6 assumptions with validation plans
- **Scope Boundaries**: IS/IS NOT documented
- **Evidence Trail**: requirements-steward review documented

### Readiness Status
- **D1 Gate**: PASSED - Ready for implementation
- **Blocking Dependencies**: None (this is the parent component)

### Implementation Status (Updated 2025-12-28)

| Immutable | Status | Evidence |
|-----------|--------|----------|
| SS-I1 | PENDING | Control plane separation designed, not yet wired |
| SS-I2 | ✅ COMPLETE | AIClient async-first (PR #106) |
| SS-I3 | ✅ COMPLETE | MCPClientManager with MCP SDK (PR #106) |
| SS-I4 | PENDING | Pre-commit hook not yet implemented |
| SS-I5 | PENDING | context-manifest.oct.md not yet implemented |
| SS-I6 | ✅ COMPLETE | Graceful degradation in MCPClientManager (PR #106) |

**PR #106 Commits**:
- `d41a6ea`: feat(ai): convert AIClient to async-first architecture
- `5bd8a63`: feat(mcp): implement real MCP client connections for SS-I3 federation
- `f159ef5`: feat(mcp): externalize server config to environment variables
- `2ca7829`: fix(ai): handle NoKeyringError in CI environments
- `02f7192`: fix(ai): use correct keyring service name 'hestai-mcp'

---

## PROTECTION CLAUSE

Any work contradicting these immutables must STOP, CITE the specific requirement, and ESCALATE to requirements-steward.

**The Protection Oath**:
> "These 6 Immutables (SS-I1 through SS-I6) are the binding requirements for System Steward implementation. Any contradiction requires STOP, CITE, ESCALATE."
