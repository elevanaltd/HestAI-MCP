# North Star Format Decision - Decision Record
**Phase**: D1 (Requirements)
**Decision Date**: 2025-12-25
**Authority**: system-steward (ETHOS - integrity guardian)
**Finding**: Dual-format (.md + -SUMMARY.oct.md) is INTENTIONAL and DOCUMENTED

---

## DECISION STATEMENT

North Star documents use a **dual-format pattern by design**:

- **Primary**: `000-{PROJECT}-NORTH-STAR.md` (human-readable, constitutional authority)
- **Optional**: `000-{PROJECT}-NORTH-STAR-SUMMARY.oct.md` (agent-optimized, compressed)

This pattern is **NOT a violation** but an **intentional design decision** documented in governance rules.

---

## EVIDENCE BASE

### Evidence 1: naming-standard.oct.md

**Authority**: `hub/governance/rules/naming-standard.oct.md`

```
NORTH_STAR_PATTERN::[
  format::000-{PROJECT}-NORTH-STAR.md,
  reason::governance_file+CAPS_treatment+000_prefix_sorts_first,
  examples::[
    "000-LIVING-ORCHESTRA-NORTH-STAR.md",
    "000-LIVING-ORCHESTRA-NORTH-STAR-SUMMARY.oct.md",
    "000-ODYSSEAN-ANCHOR-NORTH-STAR.md"
  ]
]

REGEX_NORTH_STAR::"^000-[A-Z0-9-]+-NORTH-STAR(-SUMMARY)?(\.oct)?\.md$"
```

**Conclusion**: Regex explicitly validates both formats as correct

### Evidence 2: hub-authoring-rules.oct.md

**Authority**: `hub/governance/rules/hub-authoring-rules.oct.md`

Section §4 (FORMAT_RULES) lists "north_stars" under both:
- OCTAVE_FORMAT (for -SUMMARY.oct.md variants)
- MARKDOWN_FORMAT implied (for primary .md files)

Section §5 (EXAMPLES) shows:
- "System North Star" → `hub/governance/workflow/[consumer_needs_it]`
- Primary audience: human developers (hence .md format)

**Conclusion**: Dual format is architecturally designed choice

### Evidence 3: CLAUDE.md

**Authority**: `/Users/shaunbuswell/.claude/CLAUDE.md` (constitutional governance)

```
FEDERATED_NORTH_STAR::[
  STRATEGY::"Separation of System Governance from Product Implementation"
]

NORTH_STAR_REFERENCES::[
  SYSTEM::"hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md"[...],
  PRODUCT_MCP::".hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md"[...]
]
```

**Conclusion**: Primary North Stars established as .md (constitutional authority)

---

## DESIGN RATIONALE

### Problem

North Stars serve dual purposes:
1. **Human consumption**: Developers must read and understand constitutional requirements
2. **Machine consumption**: AI agents must parse and enforce governance rules

Single-format solution inadequate:
- `.md` only: Agents struggle with unstructured parsing
- `.oct.md` only: Developers find markdown more readable in GitHub/IDE

### Solution

**Dual format with clear separation**:

1. **Primary North Star (.md)**
   - Audience: Humans (developers, architects, decision-makers)
   - Format: Markdown (GitHub renders beautifully)
   - Purpose: Constitutional authority, human understanding
   - Example: `000-SYSTEM-HESTAI-NORTH-STAR.md`

2. **Summary North Star (-SUMMARY.oct.md)**
   - Audience: AI agents (optional)
   - Format: OCTAVE (machine-parseable, compressed)
   - Purpose: Agent-optimized rule extraction
   - Example: `000-SYSTEM-HESTAI-NORTH-STAR-SUMMARY.oct.md`

### Authority for This Decision

Follows immutables:
- **I2: Structural Integrity Priority** - Design preserves both human and machine readability
- **I3: Dual-Layer Authority** - Governance (human-first) + agent consumption (optional)

---

## CURRENT COMPLIANT FILES

All following correct design:

✅ `hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md` (primary .md)
✅ `hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR-SUMMARY.oct.md` (optional .oct.md)
✅ `hub/templates/000-PROJECT-TEMPLATE-NORTH-STAR.md` (primary .md)
✅ `hub/templates/000-PROJECT-TEMPLATE-NORTH-STAR-SUMMARY.oct.md` (optional .oct.md)
✅ `.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md` (primary .md)
✅ `.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR-SUMMARY.oct.md` (optional .oct.md)

---

## AUDIT CORRECTION REQUIRED

### Items to Remove from Outstanding List

Files incorrectly flagged as violations in 2025-12-25-audit-findings-status-review.md:

**REMOVE**:
- ❌ System North Star using .md (INCORRECT FINDING - this is correct design)
- ❌ Template North Star using .md (INCORRECT FINDING - this is correct design)

**KEEP**:
- ✅ ci-progressive-testing.oct.md location (LEGITIMATE - wrong folder)
- ✅ Clock-in readiness assessment format (LEGITIMATE - should be .oct.md)

**New Count**: 4 outstanding → 2 outstanding

---

## GOVERNANCE DECISION

**Decision**: North Stars intentionally use dual format
- Primary: .md (human-readable constitutional authority)
- Optional: -SUMMARY.oct.md (agent-optimized compressed)

**Compliance**: ✅ Documented in naming-standard.oct.md, hub-authoring-rules.oct.md, CLAUDE.md

**Status**: ✅ COMPLIANT - No violations, working as designed

---

**Decision Authority**: system-steward (ETHOS)
**Decision Date**: 2025-12-25
**Record Location**: .hestai/reports/2025-12-25-north-star-format-decision.md (decision evidence archive)
