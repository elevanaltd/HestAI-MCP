# Namespace Migration Guide: Relativity Governance Protocol

**Version:** 1.0
**Effective Date:** 2026-02-16
**Grace Period:** Until 2024-04-01
**Authority:** Constitution §3.5 (Relativity Protocol)

---

## Executive Summary

The HestAI system now supports two orthogonal namespace domains for immutables:

- **SYS (System):** Constitutional methodology (HOW to build)
- **PROD (Product):** MCP operational requirements (WHAT to build)

This guide provides step-by-step migration instructions to adopt namespace-qualified immutable references across the codebase.

---

## Problem Statement

Two North Star documents both used I1-I6 numbering for their immutables, creating namespace collision:

- **System North Star (SYS):** I1=TDD, I2=Phase-Gated, I3=Human Primacy, I4=Artifact Persistence, I5=Quality Verification, I6=Explicit Accountability
- **Product North Star (PROD):** I1=Cognitive Continuity, I2=Structural Integrity, I3=Dual Layer Authority, I4=Freshness Verification, I5=Odyssean Identity, I6=Universal Scope

**Before Relativity Protocol:**
```
Problem: "This violates I5"
Ambiguous: Could mean SYS::I5 (Quality Verification) OR PROD::I5 (Odyssean Identity)
```

**After Relativity Protocol:**
```
Clear: "This violates SYS::I5" (Quality Verification)
Clear: "This violates PROD::I5" (Odyssean Identity)
```

---

## Solution: The Relativity Governance Protocol

### Core Principles

1. **Namespace Declaration:** Files declare their namespace in the META block
2. **Local Resolution:** Bare I# references resolve to the declared namespace
3. **Cross-Namespace Qualification:** References to other namespaces MUST use prefixes
4. **Derivation Traceability:** TRACES_TO shows how PROD immutables derive from SYS

### Namespace Definitions

| Namespace | Domain | Example Immutables |
|-----------|--------|-------------------|
| SYS | System methodology (HOW to build) | I1::TDD, I5::Quality_Verification |
| PROD | Product requirements (WHAT to build) | I1::Cognitive_Continuity, I5::Odyssean_Identity |

---

## Migration Steps

### Step 1: Identify Your Document's Namespace

Ask: "Which North Star does this document primarily serve?"

- **Governance/workflow documents:** Usually SYS
- **Product/feature specifications:** Usually PROD
- **Agent identities:** Usually PROD
- **Constitutional documents:** Usually SYS
- **Mixed-context documents:** No declaration (requires full qualification)

### Step 2: Add Namespace Declaration

#### For Markdown Files (YAML frontmatter)

**Before:**
```yaml
---
type: WORKFLOW
version: 1.0
---
```

**After:**
```yaml
---
type: WORKFLOW
version: 1.0
namespace: SYS
---
```

#### For OCTAVE Files (META block)

**Before:**
```octave
===WORKFLOW===
META:
  TYPE::WORKFLOW
  VERSION::"1.0"
```

**After:**
```octave
===WORKFLOW===
META:
  TYPE::WORKFLOW
  VERSION::"1.0"
  NAMESPACE::SYS
```

### Step 3: Audit Immutable References

Scan your document for all I1-I6 references:

```bash
# Find all immutable references
grep -E 'I[1-6]' your-document.md
```

**Example findings:**
```
Line 45: "This process ensures I2 compliance"
Line 78: "Agents must satisfy I5 before proceeding"
Line 102: "Cross-references PROD::I1 for context persistence"
```

### Step 4: Apply Qualification Rules

#### Rule 1: Same-Namespace References (Bare OK)

**Within a NAMESPACE::SYS document:**
```markdown
❌ Before: "This violates SYS::I2"
✅ After:  "This violates I2"

Rationale: Bare I2 resolves to SYS::I2 within a SYS namespace document
```

#### Rule 2: Cross-Namespace References (Prefix REQUIRED)

**Within a NAMESPACE::SYS document referencing Product:**
```markdown
❌ Before: "This supports I1 (cognitive continuity)"
✅ After:  "This supports PROD::I1 (cognitive continuity)"

Rationale: Referencing Product immutable from System document requires PROD:: prefix
```

#### Rule 3: No Declaration (All Refs Must Be Qualified)

**Document without NAMESPACE declaration:**
```markdown
❌ Before: "Satisfies I2 and I5"
✅ After:  "Satisfies SYS::I2 and PROD::I5"

Rationale: Without namespace declaration, all references must be explicit
```

### Step 5: Add Traceability (Product Documents Only)

For PROD namespace documents, add TRACES_TO relationships:

**Before:**
```octave
I1::PERSISTENT_COGNITIVE_CONTINUITY::[
  PRINCIPLE::system_must_persist_context_decisions_learnings_across_sessions,
  WHY::prevents_costly_re-learning+amnesia_is_system_failure
]
```

**After:**
```octave
I1::PERSISTENT_COGNITIVE_CONTINUITY::[
  PRINCIPLE::system_must_persist_context_decisions_learnings_across_sessions,
  WHY::prevents_costly_re-learning+amnesia_is_system_failure,
  TRACES_TO::[SYS::I4,SYS::I6],
  DERIVATION::"Extends artifact_persistence[SYS::I4] to cognitive_state"
]
```

---

## Validation Rules

### Rule V1: Declaration Consistency

**Validation:**
```
IF document contains NAMESPACE::X declaration
THEN all bare I# references resolve to X::I#
ELSE all I# references MUST be qualified (SYS::I# or PROD::I#)
```

**Example violations:**
```
❌ Document declares NAMESPACE::SYS but contains PROD::I1 written as I1
❌ Document has no NAMESPACE but contains bare I2 reference
```

### Rule V2: Cross-Namespace Qualification

**Validation:**
```
IF document namespace is X
AND reference is to namespace Y (where X ≠ Y)
THEN reference MUST use Y:: prefix
```

**Example violations:**
```
❌ NAMESPACE::SYS document references PROD::I5 as just I5
❌ NAMESPACE::PROD document references SYS::I2 as just I2
```

### Rule V3: TRACES_TO Completeness

**Validation (PROD namespace only):**
```
IF document NAMESPACE::PROD
THEN each I# definition MUST include TRACES_TO:[list of SYS::I# dependencies]
```

**Example violation:**
```
❌ PROD::I5 definition missing TRACES_TO field
```

### Rule V4: Namespace Value Validation

**Validation:**
```
NAMESPACE value MUST be in [SYS, PROD]
```

**Example violations:**
```
❌ NAMESPACE::PRODUCT (incorrect name)
❌ NAMESPACE::SYSTEM (incorrect name)
❌ NAMESPACE::SYS|PROD (multiple namespaces)
```

---

## Migration Timeline

| Phase | Date | Requirement | Enforcement |
|-------|------|-------------|-------------|
| **Grace Period** | 2026-02-16 to 2024-04-01 | Documents MAY use bare refs | Warnings only |
| **Transition** | 2024-04-01 to 2024-04-15 | New documents MUST qualify | Errors for new docs |
| **Full Enforcement** | 2024-04-15+ | All documents MUST qualify | Errors for all docs |

### Grace Period Behavior

**During grace period (until 2024-04-01):**
- Bare I# references generate **warnings** but do not block operations
- Validators attempt to infer namespace from context
- Cross-namespace refs without prefix generate **warnings**

**After grace period (2024-04-01+):**
- Bare I# references in undeclared namespace documents = **ERROR**
- Cross-namespace refs without prefix = **ERROR**
- Missing TRACES_TO in PROD namespace = **ERROR**

---

## Common Migration Patterns

### Pattern 1: Agent Identity Files

**Context:** Agent identities typically reference PROD immutables but exist in governance space

**Decision:** Declare NAMESPACE::PROD

**Example:**
```octave
===IMPLEMENTATION_LEAD_AGENT===
META:
  TYPE::AGENT_IDENTITY
  NAMESPACE::PROD

CONSTRAINTS:
  MUST_SATISFY::[I5,I2]  // Resolves to PROD::I5, PROD::I2
  FOUNDATION::SYS::I1    // Explicit SYS reference
```

### Pattern 2: Workflow Documents

**Context:** Workflow guides enforce System methodology

**Decision:** Declare NAMESPACE::SYS

**Example:**
```octave
===BUILD_WORKFLOW===
META:
  TYPE::WORKFLOW
  NAMESPACE::SYS

PHASES:
  DESIGN::satisfies_I2[phase_gates]     // Resolves to SYS::I2
  BUILD::enforces_I1[TDD_discipline]    // Resolves to SYS::I1
  PRODUCT_CONTEXT::requires_PROD::I4    // Explicit PROD reference
```

### Pattern 3: Mixed-Context Documents

**Context:** Document references both System and Product immutables equally

**Decision:** NO namespace declaration, qualify all refs

**Example:**
```markdown
# Integration Guide

This guide bridges System methodology and Product requirements:

- Follow SYS::I1 (TDD discipline) for all code
- Ensure PROD::I5 (identity binding) before agent work
- Satisfy SYS::I2 (phase gates) and PROD::I2 (structural integrity)
```

### Pattern 4: ADRs and Decision Records

**Context:** ADRs may reference immutables from both domains

**Decision:** Declare primary namespace, qualify cross-refs

**Example:**
```markdown
---
type: ADR
namespace: SYS
---

# ADR-0047: Test Structure Standard

**Status:** Accepted

**Context:**
This ADR enforces I1 (TDD discipline) and I5 (quality verification).
It also supports PROD::I5 (Odyssean identity) by providing test infrastructure.
```

---

## Validation Examples

### Example 1: Correct SYS Namespace Usage

```octave
===BUILD_CHECKLIST===
META:
  NAMESPACE::SYS

CHECKLIST:
  VERIFY_TDD::I1_compliance           ✅ Resolves to SYS::I1
  VERIFY_GATES::I2_evidence           ✅ Resolves to SYS::I2
  VERIFY_QUALITY::I5_checks           ✅ Resolves to SYS::I5
  SUPPORT_PRODUCT::PROD::I1_context   ✅ Explicit PROD reference
```

**Validation:** PASS

### Example 2: Incorrect Mixed References

```octave
===BUILD_CHECKLIST===
META:
  NAMESPACE::SYS

CHECKLIST:
  VERIFY_TDD::I1_compliance           ✅ SYS::I1
  VERIFY_IDENTITY::I5_binding         ❌ ERROR: I5 resolves to SYS::I5 (Quality Verification)
                                         but context implies PROD::I5 (Odyssean Identity)
```

**Validation:** FAIL - Cross-namespace reference missing prefix

**Fix:**
```octave
VERIFY_IDENTITY::PROD::I5_binding   ✅ Explicit PROD::I5
```

### Example 3: Missing Declaration

```markdown
# Agent Workflow

Agents must satisfy I5 before work begins.    ❌ ERROR: No NAMESPACE declared, bare I5 invalid
```

**Validation:** FAIL - Bare reference without namespace declaration

**Fix Option 1 (Add declaration):**
```markdown
---
namespace: PROD
---

Agents must satisfy I5 before work begins.    ✅ Resolves to PROD::I5
```

**Fix Option 2 (Qualify reference):**
```markdown
Agents must satisfy PROD::I5 before work begins.    ✅ Explicit PROD reference
```

---

## Automated Migration Tools

### Tool 1: Namespace Declaration Suggester

```bash
# Suggest namespace based on document content
python scripts/suggest_namespace.py path/to/document.md

# Example output:
# Suggested namespace: SYS
# Rationale: Document references primarily System immutables (I1::TDD, I2::Phase_Gated)
```

### Tool 2: Reference Auditor

```bash
# Find all immutable references and check qualification
python scripts/audit_namespace_refs.py path/to/document.md

# Example output:
# Line 23: I2 - OK (same namespace)
# Line 45: I5 - WARNING (cross-namespace, missing prefix)
# Line 67: PROD::I1 - OK (explicit cross-namespace)
```

### Tool 3: Batch Migration Script

```bash
# Auto-add namespace declarations to files in directory
python scripts/migrate_namespace.py --namespace SYS --directory .hestai-sys/governance/
```

---

## FAQs

### Q1: What if I'm unsure which namespace to use?

**Answer:** Use no namespace declaration and qualify all references explicitly. This is always safe but more verbose.

### Q2: Can a document belong to both namespaces?

**Answer:** No. A document declares one namespace or none. If referencing both equally, don't declare a namespace.

### Q3: What happens if I reference the wrong namespace?

**Answer:** During grace period: warnings. After grace period: validation errors blocking operations.

### Q4: How do TRACES_TO relationships work?

**Answer:** PROD immutables show which SYS immutables they derive from. Example:
```
PROD::I1 TRACES_TO [SYS::I4, SYS::I6]
Meaning: Cognitive Continuity derives from Artifact Persistence and Explicit Accountability
```

### Q5: Do I need to update old ADRs?

**Answer:** During grace period (until 2024-04-01), old ADRs continue to work with warnings. Budget time to migrate them before full enforcement.

### Q6: Can I add new namespaces later?

**Answer:** Yes, but requires constitutional amendment. Currently only SYS and PROD are defined.

---

## Validation Checklist

Use this checklist when migrating a document:

- [ ] Document has NAMESPACE declaration in META/frontmatter (or intentionally omitted)
- [ ] All bare I# references are to declared namespace
- [ ] All cross-namespace references use prefix (SYS:: or PROD::)
- [ ] If NAMESPACE::PROD, all I# definitions include TRACES_TO
- [ ] TRACES_TO values reference valid SYS::I# immutables
- [ ] Validation script passes without errors
- [ ] No ambiguous I# references in prose/comments

---

## Example Complete Migration

**Before (ambiguous):**
```markdown
# Agent Binding Workflow

All agents must satisfy I5 before performing work.
This ensures I2 compliance and supports I1.
```

**After (PROD namespace):**
```markdown
---
namespace: PROD
---

# Agent Binding Workflow

All agents must satisfy I5 (Odyssean Identity Binding) before performing work.
This ensures I2 (Structural Integrity) compliance and supports I1 (Cognitive Continuity).

The binding ceremony enforces SYS::I6 (Explicit Accountability) by establishing
traceable agent identity.
```

**After (no namespace, explicit):**
```markdown
# Agent Binding Workflow

All agents must satisfy PROD::I5 (Odyssean Identity Binding) before performing work.
This ensures PROD::I2 (Structural Integrity) compliance and supports PROD::I1 (Cognitive Continuity).

The binding ceremony enforces SYS::I6 (Explicit Accountability) by establishing
traceable agent identity.
```

---

## Support and Questions

- **Namespace ambiguity:** Escalate to requirements-steward
- **Migration blockers:** Create issue with label `namespace-migration`
- **Validation failures:** Check migration checklist above
- **Tool issues:** Report to implementation-lead

---

**Document Authority:** Constitution §3.5 (Relativity Protocol)
**Approval:** Shaun Buswell (Human Primacy Authority)
**Effective:** 2026-02-16
**Next Review:** 2024-04-15 (post-grace period)

---
