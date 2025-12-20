# COMPONENT NORTH STAR: ORCHESTRA MAP

**Component**: Orchestra Map (Dependency Analysis)
**Parent**: .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
**Status**: ACTIVE
**Version**: 1.0

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **Orchestra Map** component.
It inherits all requirements from the **System North Star** and **HestAI-MCP Product North Star**.
Any deviation requires formal amendment.

---

## SECTION 1: THE UNCHANGEABLES (5 Immutables)

### I1: ANCHOR PATTERN INVERSION
**Requirement**: Concepts must claim Code (via imports/links in Spec files), not vice versa. Code must remain unaware of the governance layer.
**Rationale**: Annotations in code (`@implements X`) rot immediately. Specs importing code (`import {X} from src`) are active, verifiable links.
**Validation**: CI fails if `src/` imports `anchors/`.

### I2: ONE-WAY BUILD ISOLATION
**Requirement**: Governance artifacts (anchors, specs) must be strictly excluded from production builds. The dependency arrow points ONLY from Governance → Production.
**Rationale**: Governance metadata should not bloat or break the shipping product.
**Validation**: Build configuration explicitly excludes `anchors/` and `specs/`.

### I3: ALGORITHMIC STALENESS
**Requirement**: Staleness is a binary, computable function of Version Control timestamps. `LastCommit(Spec) < LastCommit(Impl) == STALE`. No subjective "health scores."
**Rationale**: Agents need binary signals ("Stop/Go"), not nuanced probabilities.
**Validation**: `staleness_check` script uses git logs to flag drift.

### I4: POLYGLOT UNIVERSALITY
**Requirement**: The mapping architecture must rely only on universal concepts (Files, Imports/References), not language-specific features (e.g., Java Annotations).
**Rationale**: HestAI must work for Python, TS, Rust, Go, etc.
**Validation**: Architecture proven in Python and TypeScript implementations.

### I5: AST-BASED TRUTH
**Requirement**: Dependencies must be derived from Abstract Syntax Tree (AST) analysis or rigorous parsing, not regex/text search.
**Rationale**: `grep` is brittle. True dependency graphs require understanding the language structure.
**Validation**: Tooling uses `dependency-cruiser`, `ast` module, or equivalent.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **Link Direction** | Spec → Code (I1) | File naming convention |
| **Staleness Logic** | Time-based (I3) | "Grace period" parameters |
| **Tooling** | AST-based (I5) | Specific libraries used |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Validation Plan |
|----|------------|-----------------|
| C-A1 | "Spec imports Code" is valid in all target langs | Language survey (Go/Rust checks) |
| C-A2 | Git timestamp is sufficient proxy for change | Monitor false positives |
| C-A3 | Build tools can reliably exclude specific folders | Verification in CI configs |

---
