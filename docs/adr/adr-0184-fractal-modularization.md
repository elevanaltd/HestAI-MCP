# ADR-0184: Fractal Modularization & Dynamic Governance

- **Status**: Accepted
- **Type**: ADR
- **Author**: Holistic Orchestrator (Door/Logos Synthesis)
- **Created**: 2026-01-13
- **Updated**: 2026-01-13
- **GitHub Issue**: [#184](https://github.com/elevanaltd/HestAI-MCP/issues/184)
- **Phase**: B1
- **Supersedes**: (none)
- **Superseded-By**: (none)
- **From-RFC**: (none)

## Context

The HestAI-MCP system has reached a level of complexity where the single-module structure is becoming entangled. There is a strong architectural tension between two needs:
1.  **Governance Separation (Wind/Pathos)**: The need to strictly isolate "Constitutional" logic (immutable rules, quality gates) from "Tooling" logic (agent capabilities) to prevent agents from bypassing governance.
2.  **Operational Simplicity (Wall/Ethos)**: The need to avoid the complexity of distributed microservices (Gall's Law), keeping deployment and configuration simple for a single developer.

Additionally, the "Protocol" for injecting governance constraints into agent context has historically been either too rigid (hardcoded rules) or too heavy (dumping full documents).

## Decision

We will adopt a **Fractal Modularization** architecture with **Dynamic Governance** injection.

### 1. Fractal Modularization (Directory Structure)
We will maintain `hestai-mcp` as a **single server process** but strictly separate its internal code into "Fractal Modules" that mirror the system's separation of concerns.

The new source tree will be:
```
src/hestai_mcp/
├── core/                  # The "Kernel" (Governance & Interfaces)
│   ├── governance/        # Policy Enforcement Engine
│   │   ├── policy/        # Constitutional Readers (I3)
│   │   ├── quality/       # Quality Gates & RCCAFP (I2)
│   │   └── state/         # Context State Machine (I1, I4)
│   └── interfaces/        # Internal Protocol Definitions
└── modules/               # The "Extensions" (Userland)
    ├── tools/             # Agent Capabilities (The 'Arms')
    └── services/          # External Integrations (GitHub, etc.)
```

**Constraint**: `modules/` cannot import `core/governance` internals directly. They must use defined `core/interfaces`.

### 2. Dynamic Governance (Mechanism vs. Policy)
We explicitly decouple the **Mechanism** (Python Code) from the **Policy** (OCTAVE Documents).
-   **Mechanism**: The `core/governance` code is a generic engine that knows *how* to enforce rules.
-   **Policy**: The rules themselves live in `.hestai-sys/` (e.g., `OPERATIONAL-WORKFLOW.oct.md`).

The Code will **read and parse** the Policy documents at runtime to determine behavior. It will not contain hardcoded "Phase B1 Rules."

### 3. Active State Synthesis (Protocol)
We define the "Context Injection" protocol as **Active State Synthesis**, triggered by the `clock_in` tool.
Instead of dumping full text, the `Governance/State` engine will:
1.  Read the Project Context to identify the `CURRENT_PHASE` (e.g., B1).
2.  Parse `OPERATIONAL-WORKFLOW.oct.md`.
3.  **Synthesize** a transient "Context Block" containing only the constraints relevant to that phase (RACI, Deliverables, Gates).
4.  Inject this block into the Agent's context via the `ARM` proof.

## Consequences

### Positive
-   **Strict Separation**: Governance logic is physically isolated from Tool logic, preventing accidental bypass.
-   **Zero Config Bloat**: Remains a single server/process, satisfying Gall's Law.
-   **Cognitive Efficiency**: Agents receive only relevant constraints, saving context window tokens.
-   **Auditability**: Policy changes (docs) are versioned separately from Mechanism changes (code).

### Negative
-   **Refactoring Cost**: Requires moving significant portions of `src/hestai_mcp`.
-   **Latency**: Parsing OCTAVE docs at `clock_in` adds a small startup cost (mitigated by caching).
-   **Complexity**: The "Internal Protocol" boundaries must be enforced by linters, or they will degrade over time.

### Neutral
-   **Library Dependency**: Relies heavily on `octave-mcp` (v0.6.1+) for reliable document parsing.

## Related Documents

-   **ADRs**:
    -   [ADR-0033: Dual Layer Context Architecture](adr-0033-dual-layer-context-architecture.md) (Foundation for separation)
    -   [ADR-0034: Orchestra Map Architecture](adr-0034-orchestra-map-architecture.md) (Governance map)
-   **Issues**:
    -   [#184: Architectural Decision: Fractal Modularization & Dynamic Governance](https://github.com/elevanaltd/HestAI-MCP/issues/184)
