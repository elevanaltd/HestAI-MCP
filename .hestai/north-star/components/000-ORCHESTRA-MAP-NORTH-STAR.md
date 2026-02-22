---
component: orchestra_map
scope: subsystem
phase: D1
created: 2025-12-27
status: approved
approved_by: requirements-steward
approved_date: 2025-12-28
parent_north_star: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
version: 1.2
---

# COMPONENT NORTH STAR: ORCHESTRA MAP

**Component**: Orchestra Map (Dependency Analysis)
**Parent**: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
**Status**: ACTIVE
**Version**: 1.2
**Date**: 2025-12-28
**Reviewed By**: requirements-steward
**Review Date**: 2025-12-28

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **Orchestra Map** component.

**Inheritance Chain**:
- System North Star (.hestai-sys/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md) - Constitutional Authority
- HestAI-MCP Product North Star (.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md) - Product Binding
- This Component North Star - Subsystem Specifics

**Authority**: All work on Orchestra Map must align with these requirements AND all parent requirements.
Any deviation requires formal amendment through the requirements-steward.

**Protection Clause**: If ANY agent detects misalignment between work and this Component North Star:
1. **STOP** current work immediately
2. **CITE** the specific requirement (OM-I1 through OM-I5, or parent I1-I6)
3. **ESCALATE** to requirements-steward for resolution

---

## SECTION 1: THE UNCHANGEABLES (5 Immutables)

### OM-I1: ANCHOR PATTERN INVERSION
**Requirement**: Concepts must claim Code (via imports/links in Spec files), not vice versa. Code must remain unaware of the governance layer.
**Rationale**: Annotations in code (`@implements X`) rot immediately. Specs importing code (`import {X} from src`) are active, verifiable links.
**Validation**: CI fails if `src/` imports `anchors/`.

### OM-I2: ONE-WAY BUILD ISOLATION
**Requirement**: Governance artifacts (anchors, specs) must be strictly excluded from production builds. The dependency arrow points ONLY from Governance -> Production.
**Rationale**: Governance metadata should not bloat or break the shipping product.
**Validation**: Build configuration explicitly excludes `anchors/` and `specs/`.

### OM-I3: ALGORITHMIC STALENESS
**Requirement**: Staleness is a binary, computable function of Version Control timestamps. `LastCommit(Spec) < LastCommit(Impl) == STALE`. No subjective "health scores."
**Rationale**: Agents need binary signals ("Stop/Go"), not nuanced probabilities.
**Validation**: `staleness_check` script uses git logs to flag drift.

### OM-I4: POLYGLOT UNIVERSALITY
**Requirement**: The mapping architecture must rely only on universal concepts (Files, Imports/References), not language-specific features (e.g., Java Annotations).
**Rationale**: HestAI must work for Python, TS, Rust, Go, etc.
**Validation**: Architecture proven in Python and TypeScript implementations.

### OM-I5: AST-BASED TRUTH
**Requirement**: Dependencies must be derived from Abstract Syntax Tree (AST) analysis or rigorous parsing, not regex/text search.
**Rationale**: `grep` is brittle. True dependency graphs require understanding the language structure.
**Validation**: Tooling uses `dependency-cruiser`, `ast` module, or equivalent.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **Link Direction** | Spec -> Code (OM-I1) | File naming convention |
| **Staleness Logic** | Time-based (OM-I3) | "Grace period" parameters |
| **Tooling** | AST-based (OM-I5) | Specific libraries used |
| **Build Exclusion** | Governance excluded (OM-I2) | Exclusion mechanism (gitignore, build config) |
| **Language Support** | Universal concepts (OM-I4) | Priority order for language rollout |

---

## SECTION 2B: SCOPE BOUNDARIES

### What This Component IS

| Scope | Description |
|-------|-------------|
| Dependency Graph Analysis | Extracting and representing relationships between files |
| Anchor Pattern Inversion Enforcement | Validating that Spec->Code direction is maintained |
| Staleness Detection (Algorithmic) | Binary freshness computation via git timestamps |
| AST-Based Relationship Extraction | Parsing imports/references from source files |
| Build Isolation Verification | Ensuring governance artifacts stay out of production |

### What This Component IS NOT

| Out of Scope | Responsible Component |
|--------------|----------------------|
| Code Generation | Implementation domain (not mapping) |
| Context Synthesis | System Steward |
| File Watching | Living Artifacts subsystem |
| Documentation Authoring | Documentation tools consume Orchestra Map output |
| IDE Integration | IDE plugins are consumers (not Orchestra Map) |
| Governance Rule Definition | North Stars (Orchestra Map enforces) |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Confidence | Impact | Validation Plan | Owner | Timing |
|----|------------|------------|--------|-----------------|-------|--------|
| OM-A1 | "Spec imports Code" is valid in all target langs | 85% | High | Language survey (Go/Rust/Python/TS checks) | technical-architect | Before B1 |
| OM-A2 | Git timestamp is sufficient proxy for change | 80% | Medium | Monitor false positives in real usage | implementation-lead | During B2 |
| OM-A3 | Build tools can reliably exclude specific folders | 90% | High | Verification in CI configs for all build tools | technical-architect | Before B1 |
| OM-A4 | AST-based tooling (dependency-cruiser) available for all target languages | 75% | High | Test with Python, TypeScript, Go, Rust | technical-architect | Before B1 |
| OM-A5 | Spec-imports-Code pattern doesn't break IDE tooling | 80% | Medium | Test with VS Code, JetBrains IDEs | implementation-lead | During B2 |
| OM-A6 | Staleness check performance is acceptable (<1s for 1000 files) | 70% | Medium | Benchmark with large repos | implementation-lead | Before B1 |

### CRITICAL ASSUMPTIONS (Must validate before B2)
- **OM-A1 (Spec Imports Code)**: If major languages don't support this pattern, architecture fails
- **OM-A4 (AST Tooling)**: If AST tools aren't available, we fall back to brittle regex (violates OM-I5)

### ASSUMPTION DEPENDENCIES
- OM-A1 + OM-A5: If Spec->Code imports work but break IDEs, developer experience suffers
- OM-A4 + OM-A6: AST tooling must exist AND be performant; availability without speed is insufficient

---

## SECTION 4: DECISION LOG

| ID | Decision | Date | Rationale | Alternatives Considered |
|----|----------|------|-----------|-------------------------|
| OM-D1 | Spec->Code direction (not Code->Spec) | 2025-12-27 | Code annotations rot; active imports are verifiable | Annotations, comments, external registries |
| OM-D2 | Git timestamps for staleness (not content hashing) | 2025-12-27 | Simpler implementation, aligned with VCS workflow | Content hashing, semantic diffing |
| OM-D3 | AST-based parsing (not regex) | 2025-12-27 | Reliability over simplicity; regex false positives unacceptable | Regex patterns, language-specific plugins |
| OM-D4 | Build exclusion (not runtime filtering) | 2025-12-27 | Prevention over detection; governance never ships | Runtime checks, size monitoring |
| OM-D5 | Align with ns-component-create | 2025-12-28 | Standard format compliance | - |

---

## COMMITMENT CEREMONY

**Status**: APPROVED
**Reviewer**: requirements-steward
**Review Date**: 2025-12-28

**The Oath**:
> "These 5 Immutables (OM-I1 through OM-I5) are the binding requirements for Orchestra Map implementation. Any contradiction requires STOP, CITE, ESCALATE."

**Inheritance Acknowledgment**:
> This Component North Star operates under the authority of:
> - System North Star: I1 (TDD), I2 (Phase Gates), I3 (Human Primacy), I4 (Artifact Persistence), I5 (Quality Verification), I6 (Explicit Accountability)
> - Product North Star: I1 (Cognitive Continuity), I2 (Structural Integrity), I3 (Dual-Layer Authority), I4 (Freshness Verification), I5 (Odyssean Identity), I6 (Universal Scope)

**Binding Authority**: This Component North Star is now the authoritative requirements document for Orchestra Map development.

---

## EVIDENCE SUMMARY

### Constitutional Compliance
- **Total Immutables**: 5 (within 5-9 range per Miller's Law)
- **System-Agnostic**: 5/5 passed Technology Change Test (no technology-specific language)
- **Assumptions Tracked**: 6 (6+ required per PROPHETIC_VIGILANCE)
- **Critical Assumptions**: 2 requiring pre-B2 validation (OM-A1, OM-A4)
- **Commitment Ceremony**: Completed 2025-12-28

### Quality Gates
- **YAML Front-Matter**: Present
- **Inheritance Chain**: Documented (System NS + Product NS)
- **Miller's Law**: 5 immutables (within 5-9 range)
- **PROPHETIC_VIGILANCE**: 6 assumptions with validation plans
- **Scope Boundaries**: IS/IS NOT documented
- **Evidence Trail**: requirements-steward review documented

### Readiness Status
- **D1 Gate**: PASSED - Ready for implementation
- **Blocking Dependencies**: None (subsystem, not tool)

---

## PROTECTION CLAUSE

Any work contradicting these immutables must STOP, CITE the specific requirement, and ESCALATE to requirements-steward.

**The Protection Oath**:
> "These 5 Immutables (OM-I1 through OM-I5) are the binding requirements for Orchestra Map implementation. Any contradiction requires STOP, CITE, ESCALATE."
