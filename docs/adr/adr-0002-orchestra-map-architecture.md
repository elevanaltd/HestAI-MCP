# ADR-0002: Orchestra Map Architecture

**Status**: ✅ VALIDATED (MVP Complete)
**Date**: 2025-12-15
**Author**: technical-architect (Claude Opus 4.5)
**Reviewers**: edge-optimizer (Gemini), holistic-orchestrator, User
**Validates**: A8 (Orchestra Map Feasibility - **65% → 85%** ✅)
**Unblocks**: B0 Gate (pending critical-engineer final review)

---

## Context

Living Orchestra requires **I4: System Boundary Awareness** — agents must prove awareness of impact sets before executing changes. This requires an "Orchestra Map" that tracks dependencies across ALL artifact types (code, docs, concepts, agents), not just code imports.

### The Problem

Traditional tools (dependency-cruiser, ArchUnit) only map code→code dependencies. They miss:
- **Doc→Code**: "This code implements that requirement"
- **Concept→Code**: "This rule constrains that behavior"
- **Agent→Domain**: "This role governs that area"

Result: "Locally correct, globally wrong" — changes that pass all tests but silently break invariants elsewhere.

### Research Summary

See `.hestai/research/dependency-mapping-beyond-code-to-code.oct.md`:
- No single tool covers doc→code + concept→code at dependency-cruiser depth
- Enterprise ALM (Helix, Jama) proves feasibility but with heavy process overhead
- Emerging: "Knowledge Graph as Code" approaches (Basic Memory, StrictDoc)

---

## Decision

### Core Architecture: Anchor Pattern Inversion

**Breakthrough Insight** (Edge-Optimizer): Instead of Code citing Concepts (scattered annotations that rot), make **Concepts claim Code** through import statements.

```
BEFORE (High Friction, Rots):
  src/auth/service.ts → // @implements AUTH-POLICY-001  (annotation in code)

AFTER (Low Friction, Verifiable):
  anchors/auth.spec.ts → import { AuthService } from '../src/auth/service'  (spec claims code)
```

**Why This Works**:
1. Import statements are **active code** — standard AST tools graph them natively
2. **Language-agnostic pattern** — works in any language with import analysis tooling
3. **One-way anchors** — Specs import Code, Code never imports Specs
4. Staleness is **computable** — git log comparison reveals drift

### Polyglot Implementation (Universal Pattern)

The Anchor Pattern Inversion is **language-agnostic**. The pattern (Specs import Code) works in any language; only the tooling differs.

| Language | Spec File Pattern | Import Analysis Tool |
|----------|-------------------|---------------------|
| **TypeScript/JS** | `anchors/auth.spec.ts` | `dependency-cruiser` |
| **Python** | `anchors/test_auth_compliance.py` | `findimports` or `pydeps` |
| **Go** | `anchors/auth_spec.go` | `go list -json` or `godepgraph` |
| **Rust** | `anchors/auth_spec.rs` | `cargo-depgraph` |

**Example (Python):**
```python
# anchors/test_clockin_compliance.py
from src.hestai_mcp_server.tools.clockin import clock_in_tool
from src.hestai_mcp_server.context.session import SessionManager

# Concept: SESSION-LIFECYCLE-001 (Clock-in/out session management)
# This spec anchors the session management domain
```

**Orchestra Map Generator** must be a **Composite Tool**:
1. Run language-specific import analyzer per file type
2. Merge outputs into unified graph JSON
3. Apply staleness detection (git-based, language-agnostic)

This strengthens the architecture by proving it isn't tied to one ecosystem

### Layer 3: Semantic Knowledge (Core Component)

**Decision**: Adopt **Basic Memory MCP** (Knowledge Graph) as the definitive Layer 3.

**Clarification (Read-Side Projection, Not Structural Source of Truth)**:
Basic Memory is the *query surface* for semantics (governance, meaning, relationships), but it is not the write-side authority for structural dependencies. Structural truth is produced from Layers 1–2 (code/spec anchors) into `unified-graph.json`, then hydrated downstream into machine-managed Basic Memory content; any human-authored enrichment lives separately and links into generated nodes to avoid split-brain drift.

**Rationale**:
Layers 1 & 2 provide structural facts ("Code A imports Code B", "Spec C anchors Code A"), but lack *meaning* ("Role X is responsible for Spec C").
We need a **Semantic Knowledge Graph** to answer "Who governs this?", "What business goal does this serve?".
Vector/RAG approaches were rejected (hallucination risk). We require **Explicit Semantic Modeling** (Entities/Relations).

**Architecture**:
*   **Store**: Markdown files (local-first) managed by Basic Memory MCP.
*   **Structure**: Knowledge Graph (Entities, Observations, Relations).
*   **Integration**: The Orchestra Map Generator merges this Semantic Graph with the Structural Graph (Layers 1 & 2).

**Join Key**:
*   The `concept_id` (e.g., `SESSION-LIFECYCLE-001`) exists in:
    1.  **Layer 2**: Defined in `anchors/clockin_spec.py` metadata.
    2.  **Layer 3**: Defined as an Entity in Basic Memory (`[[SESSION-LIFECYCLE-001]]`).
*   This common key allows joining the graphs.

### Node Types

| Type | Description | Example |
|------|-------------|---------|
| `CONCEPT` | Rule, Pattern, Requirement, Invariant | `AUTH-POLICY-001` |
| `CODE` | Source file, module, function | `src/auth/service.ts` |
| `DOC` | Documentation, ADR, Spec | `docs/adr/ADR-001.md` |
| `AGENT` | Role, Authority | `holistic-orchestrator` |

### Edge Types

| Type | Direction | Meaning |
|------|-----------|---------|
| `IMPLEMENTS` | Concept → Code | "This spec verifies this implementation" |
| `GOVERNS` | Agent → Domain | "This role has authority over this area" |
| `DEPENDS_ON` | Code → Code | "This module imports that module" |
| `CONSTRAINS` | Concept → Code | "This rule limits this behavior" |

### Staleness Detection (Simplified)

**Rule**: `LastCommit(Spec) < LastCommit(Implementation) == STALE`

```python
def is_stale(spec_file: Path, impl_file: Path) -> bool:
    spec_commit = git_last_commit_date(spec_file)
    impl_commit = git_last_commit_date(impl_file)
    return spec_commit < impl_commit
```

**Why Not Decay Scores?** Floating-point health metrics are "Metric Theater." Agents need a binary: "Is this stale? Y/N" with actionable guidance: "Update the Spec to re-verify the implementation."

---

## Build Isolation (Critical)

**Risk**: Concept Specs treated as regular code → bundled in production or create circular dependencies.

**Mandate**:

1. **Location**: All Concept Specs live in `/anchors/` root directory (or `/compliance/`)
2. **Exclusion**: Build configs must exclude `anchors/**/*`
3. **One-Way Rule**: Specs import Code; Code **NEVER** imports Specs
4. **CI Enforcement**: Build fails if production code imports from `/anchors/`

### TypeScript/JS

```jsonc
// tsconfig.build.json
{
  "exclude": [
    "anchors/**/*",     // Concept anchors - verification only
    "**/*.spec.ts",     // Test files
    "**/*.test.ts"      // Test files
  ]
}
```

### Python

```ini
# pyproject.toml
[tool.setuptools]
packages = ["src"]  # Explicitly include only src, excludes anchors/

# Or in setup.py
exclude_package_data = {"": ["anchors/*"]}
```

```python
# .coveragerc or pyproject.toml coverage section
[tool.coverage.run]
omit = ["anchors/*", "tests/*"]
```

### CI Enforcement (All Languages)

```yaml
# .github/workflows/build.yml
- name: Check for spec imports in production code
  run: |
    # Fail if any src/ file imports from anchors/
    ! grep -r "from anchors" src/ && ! grep -r "import anchors" src/
```

---

## Graph Generation

### Orchestra Map Generator (Composite Tool)

The generator runs language-specific analyzers and merges outputs:

```python
# orchestra_map_generator.py (pseudocode)
def generate_orchestra_map(project_root: Path) -> dict:
    edges = []

    # Layer 1: TypeScript/JS (if present)
    if (project_root / "package.json").exists():
        ts_graph = run_dependency_cruiser(project_root / "src")
        edges.extend(parse_cruiser_output(ts_graph))

    # Layer 1: Python (if present)
    if (project_root / "pyproject.toml").exists():
        py_graph = run_findimports(project_root / "src")
        edges.extend(parse_findimports_output(py_graph))

    # Layer 2: Concept Anchors (all specs)
    for spec_file in (project_root / "specs").glob("*"):
        concept_edges = extract_spec_imports(spec_file)
        edges.extend(concept_edges)

    # Layer 3: Staleness detection
    for edge in edges:
        if edge["type"] == "IMPLEMENTS":
            edge["stale"] = is_stale(edge["from_file"], edge["to_file"])

    return {"edges": edges, "generated_at": datetime.utcnow()}
```

### Layer 1: Code Dependencies (Language-Specific)

**TypeScript/JS:**
```bash
npx depcruise src --output-type json > cruiser-output.json
```

**Python:**
```bash
findimports src/ --json > findimports-output.json
# Or using pydeps
pydeps src/ --no-show --json > pydeps-output.json
```

### Layer 2: Concept Anchors (Automated via AST)

**TypeScript Example:**
```typescript
// anchors/auth.spec.ts
import { AuthService } from '../src/auth/service';
import { UserRepository } from '../src/auth/repository';

// Concept: AUTH-POLICY-001 (Security authentication requirements)
// This spec anchors the authentication domain
```

**Python Example:**
```python
# anchors/test_clockin_compliance.py
from src.hestai_mcp_server.tools.clockin import clock_in_tool
from src.hestai_mcp_server.context.session import SessionManager

# Concept: SESSION-LIFECYCLE-001 (Clock-in/out session management)
# This spec anchors the session management domain
```

Extract edges:
```json
{
  "from": { "type": "CONCEPT", "id": "AUTH-POLICY-001", "file": "anchors/auth.spec.ts" },
  "to": { "type": "CODE", "id": "src/auth/service.ts" },
  "edge": "IMPLEMENTS",
  "stale": false
}
```

### Layer 3: Temporal Coupling (Git Analysis)

```bash
git log --format='%H' --follow -- src/auth/service.ts | head -100
# Cross-reference with co-changed files
```

Edges with `co_change_frequency > 0.7` indicate hidden coupling.

### Merge: Unified Graph

```json
{
  "nodes": [
    { "type": "CONCEPT", "id": "AUTH-POLICY-001", "file": "anchors/auth.spec.ts" },
    { "type": "CODE", "id": "src/auth/service.ts" },
    { "type": "CODE", "id": "src/auth/repository.ts" }
  ],
  "edges": [
    { "from": "AUTH-POLICY-001", "to": "src/auth/service.ts", "type": "IMPLEMENTS", "stale": false },
    { "from": "src/auth/service.ts", "to": "src/auth/repository.ts", "type": "DEPENDS_ON", "stale": null }
  ]
}
```

---

## MVP: Proof of Concept

**Objective**: Validate A8 (Orchestra Map Feasibility)

**Status**: ✅ **VALIDATED** (2025-12-15)

### Scope

This MVP started as a TypeScript-first plan, then moved to Python when we validated that the active `clock_in` implementation lived in a Python repo, and then settled on the system being **polyglot by design**.

Map the **Clock-in Feature** (Python MVP in hestai-mcp-server) using the Anchor Pattern:

1. Create a Spec anchor in `anchors/` that imports clock-in implementation files (Python example: `anchors/test_clockin_compliance.py`)
2. Run the appropriate import analysis (Python AST / findimports / etc.) across `/anchors/` + `/src/`
3. Generate unified graph
4. Compute staleness for each anchor edge

### Target Repository

**hestai-mcp-server** (Python MVP) — per ADR-002 MVP Trial Strategy

This validates the architecture is a **polyglot template**: Specs import Code is universal; only the import analysis tooling differs per language.

### Success Criteria

- [x] Import analyzer (AST-based) successfully graphs Spec→Code edges
- [x] Staleness detection works (git timestamp comparison)
- [x] No production build pollution (specs excluded from package)
- [x] Graph is queryable via unified JSON output

### MVP Implementation (hestai-mcp-server)

| File | Purpose |
|------|---------|
| `anchors/clockin_spec.py` | Concept anchor importing `tools.clockin.ClockInTool` |
| `scripts/orchestra_map_generator.py` | AST parser → dependency graph JSON |
| `scripts/staleness_check.py` | Git timestamp comparison for drift detection |

### Validation Results

**HO Assessment**: "The implementation successfully proves the Anchor Pattern Inversion in Python."

Key validations:
- ✅ Hard AST link via imports (not annotations)
- ✅ `CONCEPT_METADATA` with `anchored_implementations` for explicit tracking
- ✅ Violation detection (Code importing Specs → blocked)
- ✅ Simplified Git Timestamp Rule (`LastCommit(Spec) < LastCommit(Impl) == STALE`)

### A8 Confidence Update

| Before MVP | After MVP | Evidence |
|------------|-----------|----------|
| 65% | **85%** | Pattern validated in Python, tooling works, staleness detection functional |

### Deliverables

`unified-graph.json` proving:
- Code→Code edges (AST analysis)
- Concept→Code edges (spec imports)
- Staleness flags (git comparison)
- Violation detection (one-way anchor enforcement)

---

## Alternatives Considered

### Alternative 1: Concept Grep (`[CNT-xxx]` tags in code)

**Rejected**: Contradicts Anchor Pattern Inversion. If Specs import Code, we don't need text tags in application code. Grepping is the "legacy" approach; Inversion uses AST.

### Alternative 2: Complex Decay Scoring

**Rejected**: `Health = 1.0 * (1 / (Months_Since_Verification + 1))` is Metric Theater. Binary staleness (spec older than code = stale) is actionable.

### Alternative 3: Knowledge Graph Database (Neo4j)

**Deferred**: Adds infrastructure complexity. JSON files + dependency-cruiser sufficient for MVP. Revisit if scale requires.

### Alternative 4: Vector Embeddings / RAG

**Rejected**: For Layer 3. Dependency graphs require explicit, verifiable links ("A depends on B"). Vector similarity is probabilistic and prone to hallucination. We chose **Explicit Knowledge Graphs** (Basic Memory) instead.

---

## Consequences

### Positive

- **Verifiable Architecture**: Concept→Code links are testable, not just documented
- **Native Tooling**: dependency-cruiser handles graph generation
- **Actionable Staleness**: Binary "stale/fresh" enables clear remediation
- **Build Safety**: Strict isolation prevents production pollution

### Negative

- **Spec Maintenance**: Teams must create/update specs when concepts change
- **Learning Curve**: Anchor Pattern Inversion is non-obvious
- **Initial Overhead**: Creating `/anchors/` structure requires upfront work

### Risks

| Risk | Mitigation |
|------|------------|
| Specs become stale anyway | CI gate: "Stale specs block merge" |
| Circular dependency (Code imports Spec) | Lint rule: "No imports from /anchors/ in /src/" |
| Over-specification (too many specs) | Guidelines: Only anchor "critical invariants" |

---

## Implementation Plan

### Phase 1: MVP (Technical Architect) ✅ COMPLETE

**Target**: hestai-mcp-server (Python)

1. ✅ Create `/anchors/` directory structure
2. ✅ Write `anchors/clockin_spec.py` anchoring clock-in feature
3. ✅ Configure package to exclude anchors
4. ✅ Implement AST-based graph generator (`orchestra_map_generator.py`)
5. ✅ Implement staleness detection script (`staleness_check.py`)
6. ✅ Document results → A8 validated (65% → 85%)
7. ✅ Document friction points → informs hestai-core build

**Friction Points Documented**:
- Python AST parsing required adaptation from TS approach
- `findimports` less suitable than custom AST parser
- CONCEPT_METADATA pattern emerged as useful addition

### Phase 2: Layer 3 Semantic Spike (Methodical Path)

**Objective**: Validate Semantic Integration (Basic Memory) *before* automation.

1.  **Install Basic Memory**: Configure `basicmachines-co/basic-memory` in `hestai-mcp-server`.
2.  **Define Graph**: Create semantic links in Markdown (`[[holistic-orchestrator]]` → `[[SESSION-LIFECYCLE-001]]`).
3.  **Implement Merge**: Create `scripts/merge_layers.py` to join Layer 1/2 JSON with Layer 3 Graph.
4.  **Proof**: Generate `unified-graph.json` showing `Agent -> Concept -> Spec -> Code`.

### Phase 3: Automation (CI & Enforcement)

1.  CI integration: Stale specs block merge
2.  Lint rule: No `/anchors/` imports in `/src/`
3.  Graph visualization (Design-Architect input)

### Phase 4: Expansion

1. Agent→Domain anchors (governance specs)
2. Temporal coupling analysis
3. Impact set queries: "What breaks if X changes?"

---

## References

- `.hestai/research/dependency-mapping-beyond-code-to-code.oct.md`
- `docs/001-DOC-ORCHESTRA-MAP-IMPACT-SET-PLAN.md`
- North Star I4: System Boundary Awareness
- Edge-Optimizer Analysis (2025-12-15)

---

## Decision Record

| Date | Actor | Action |
|------|-------|--------|
| 2025-12-15 | technical-architect | Drafted ADR based on research + EO analysis |
| 2025-12-15 | edge-optimizer | Provided Anchor Pattern Inversion breakthrough |
| 2025-12-15 | User | Refined: Build isolation, AST-only MVP, simplified staleness |
| 2025-12-15 | User | Generalized to polyglot (Python MVP proves language-agnostic) |
| 2025-12-15 | technical-architect | Added Basic Memory MCP as Layer 3 investigation option |
| 2025-12-15 | hestai-mcp-server | MVP implemented: clockin_spec.py, orchestra_map_generator.py, staleness_check.py |
| 2025-12-15 | holistic-orchestrator | MVP validated: "Successfully proves the Anchor Pattern Inversion in Python" |
| 2025-12-15 | technical-architect | A8 confidence updated: 65% → 85% (MVP evidence) |
| TBD | critical-engineer | Final validation before B0 gate passage |

---

**END OF ADR-001**
