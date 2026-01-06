# North Star Hook vs Governance Rules Audit
**Date**: 2025-12-25
**Auditor**: system-steward
**Finding**: Hook enforcement pattern differs from documented governance rules
**Status**: ⚠️ DISCREPANCY IDENTIFIED - Hook is overly restrictive

---

## EXECUTIVE SUMMARY

The hook `/Users/shaunbuswell/.claude/hooks/enforce-north-star-location.sh` enforces a North Star naming convention that is **stricter than** what the governance rules define.

**Hook Pattern**: `000-{PROJECT}-D1-NORTH-STAR.md`
**Governance Pattern**: `000-{PROJECT}-NORTH-STAR.md` (optional `-SUMMARY.oct.md`)

**Issue**: Hook rejects valid North Stars that don't have the `D1` phase marker.

---

## GOVERNANCE RULES REFERENCE

### visibility-rules.oct.md § RULE_4 (WORKFLOW_METHODOLOGY)

```octave
WHAT_GOES_HERE::[
  north_star_documents[immutable_requirements],
  ...
]

STRUCTURE::[
  .hestai/workflow/→000-{PROJECT}-NORTH-STAR.md,
  ...
]
```

**Pattern**: `000-{PROJECT}-NORTH-STAR.md`
**No D1 marker required**

---

### naming-standard.oct.md § NORTH_STAR_PATTERN

```octave
NORTH_STAR_PATTERN::[
  format::000-{PROJECT}-NORTH-STAR.md,
  hook_pattern::"*NORTH-STAR*",
  examples::[
    "000-LIVING-ORCHESTRA-NORTH-STAR.md",
    "000-LIVING-ORCHESTRA-NORTH-STAR-SUMMARY.oct.md",
    "000-ODYSSEAN-ANCHOR-NORTH-STAR.md"
  ]
]

REGEX_NORTH_STAR::"^000-[A-Z0-9-]+-NORTH-STAR(-SUMMARY)?(\.oct)?\.md$"
```

**Pattern**: `000-{PROJECT}-NORTH-STAR[optional -SUMMARY][optional .oct].md`
**No D1 marker mentioned**
**Supports both .md and -SUMMARY.oct.md**

---

### hub-authoring-rules.oct.md § DIRECTORY_PURPOSE

```octave
.hestai-sys/governance/::[\
  PURPOSE::"Constitutional rules and North Stars",
  CONTENT::[\
    workflow/→system_north_star[000-SYSTEM-HESTAI-NORTH-STAR.md],
    ...
  ]
]
```

**Reference**: `000-SYSTEM-HESTAI-NORTH-STAR.md`
**No D1 marker**

---

## ACTUAL NORTH STAR FILES IN REPOSITORY

### Files that PASS governance rules but FAIL hook validation

1. **src/hestai_mcp/_bundled_hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md**
   - ✅ Matches: `naming-standard.oct.md` regex
   - ✅ In correct location per `visibility-rules.oct.md`
   - ❌ Hook would reject: Missing `D1` marker
   - ❌ Would suggest: `.hestai/workflow/000-SYSTEM-HESTAI-D1-NORTH-STAR.md`

2. **src/hestai_mcp/_bundled_hub/templates/000-PROJECT-TEMPLATE-NORTH-STAR.md**
   - ✅ Matches: `naming-standard.oct.md` regex
   - ✅ Follows: `hub-authoring-rules.oct.md` structure
   - ❌ Hook would reject: Missing `D1` marker
   - ❌ Would suggest: `.hestai/workflow/000-PROJECT-TEMPLATE-D1-NORTH-STAR.md`

3. **.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md**
   - ✅ In correct location per `visibility-rules.oct.md` RULE_4
   - ✅ Matches: `naming-standard.oct.md` regex
   - ❌ Hook would reject: Missing `D1` marker
   - ❌ Would suggest: `.hestai/workflow/000-MCP-PRODUCT-D1-NORTH-STAR.md`

4. **.hestai/workflow/000-REPORTS-D1-NORTH-STAR.md** (newly created)
   - ✅ In correct location
   - ✅ HAS D1 marker (accidental compliance)
   - ✅ Hook would accept this

---

## ROOT CAUSE ANALYSIS

**Hook Source**: `/Users/shaunbuswell/.claude/hooks/enforce-north-star-location.sh`

**Lines with D1 requirement**:
```bash
# Line 60: Pattern check
[[ "$file_path" =~ (^|/).*D1-NORTH-STAR\.md$ ]] || \

# Line 78-79: Canonical patterns
canonical_pattern_hestai=".hestai/workflow/000-*-D1-NORTH-STAR.md"
canonical_pattern_coord=".coord/workflow-docs/000-*-D1-NORTH-STAR.md"

# Line 82-83: Location validation
if [[ ! "$file_path" =~ \.hestai/workflow/000-.*-D1-NORTH-STAR\.md$ ]] && \
   [[ ! "$file_path" =~ \.coord/workflow-docs/000-.*-D1-NORTH-STAR\.md$ ]]; then
```

**Where does D1 come from?**
- Hook references: "ADR-004 Cascading Overlay Governance" (line 2-3)
- CV3 Resolution (line 8)
- No reference to governance rules in comments

**Problem**: Hook was designed based on different design decision (D1 phase marker as naming requirement), but governance rules don't enforce this.

---

## IMPACT ASSESSMENT

### Current Behavior

The hook blocks attempts to create North Star files that don't match its pattern:

```
🎯 NORTH STAR LOCATION VIOLATION

WRONG_LOCATION: /path/to/000-MCP-PRODUCT-NORTH-STAR.md
CANONICAL_LOCATION (preferred): .hestai/workflow/000-MCP-PRODUCT-D1-NORTH-STAR.md
```

### Who Does This Affect?

1. **Developers creating new North Stars**: Must add `-D1` suffix even though rules don't require it
2. **Existing North Stars**: Would need renaming to comply with hook
3. **Cross-project consistency**: North Star naming inconsistent between hook-enforced and governance-documented patterns

---

## RECOMMENDATIONS

### Option A: Update Hook to Match Governance Rules (RECOMMENDED)

**Rationale**: Hook should enforce what governance rules define, not add extra constraints

**Changes Required**:
1. Remove D1 phase marker requirement
2. Update canonical patterns to match `naming-standard.oct.md` regex
3. Support both `-SUMMARY.oct.md` variants

**New Pattern**: `000-[A-Z0-9-]+-NORTH-STAR(-SUMMARY)?(\.oct)?\.md`

**Files to Rename** (if hook is enforced strictly):
- None currently - existing files already follow governance rules

### Option B: Update Governance Rules to Match Hook

**Rationale**: Establish D1 phase marker as required convention

**Changes Required**:
1. Add D1 phase marker to `naming-standard.oct.md` NORTH_STAR_PATTERN
2. Add D1 marker to `visibility-rules.oct.md` examples
3. Update `hub-authoring-rules.oct.md` system North Star reference

**Files to Rename**:
- `src/hestai_mcp/_bundled_hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md` → `000-SYSTEM-HESTAI-D1-NORTH-STAR.md`
- `src/hestai_mcp/_bundled_hub/templates/000-PROJECT-TEMPLATE-NORTH-STAR.md` → `000-PROJECT-TEMPLATE-D1-NORTH-STAR.md`
- `.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md` → `000-MCP-PRODUCT-D1-NORTH-STAR.md`

---

## DETAILED COMPARISON

### Hook Pattern vs Governance Pattern

| Aspect | Hook | Governance Rules | Match? |
|--------|------|------------------|--------|
| **Location** | `.hestai/workflow/` or `.coord/workflow-docs/` | `.hestai/workflow/` | ✅ |
| **Prefix** | `000-` | `000-` | ✅ |
| **Project Name** | `{PROJECT}` (UPPERCASE) | `{PROJECT}` | ✅ |
| **Phase Marker** | `-D1-` (REQUIRED) | Not mentioned | ❌ |
| **Suffix** | `-NORTH-STAR.md` | `-NORTH-STAR[optional -SUMMARY][optional .oct].md` | ⚠️ |
| **Format** | `.md` only | `.md` or `.oct.md` | ⚠️ |

---

## GOVERNANCE COMPLIANCE

**Current State**: Hook is MORE restrictive than governance rules
- Rules say: `000-{PROJECT}-NORTH-STAR.md`
- Hook says: `000-{PROJECT}-D1-NORTH-STAR.md`

**Immutables Affected**:
- **I2: Structural Integrity Priority** - Inconsistency between documentation and enforcement
- **I3: Dual-Layer Authority** - Hook is not derived from governance rules

---

## DECISION REQUIRED

**Question**: Is the D1 phase marker intentional design or unintended divergence?

### Path A: Hook is Overly Strict
- Conclusion: Hook should be updated to match `naming-standard.oct.md` regex
- Action: Modify hook to accept patterns without D1 marker
- Files affected: None (existing files already compliant with governance)

### Path B: D1 Marker is Required Convention
- Conclusion: Governance rules need updating to document D1 requirement
- Action: Update `naming-standard.oct.md` + `visibility-rules.oct.md` + rename 3 files
- Files affected: 3 North Stars need renaming

---

## RECOMMENDATION

**Recommend: Option A (Update Hook)**

**Rationale**:
1. Governance rules are "source of truth" for placement/naming
2. Hook enforces governance rules, not creates new ones
3. Existing North Stars follow governance rules correctly
4. No breaking changes required
5. Simpler implementation

**Action**: Fix hook to accept `naming-standard.oct.md` REGEX_NORTH_STAR pattern

---

**End of Hook Audit**
**Auditor**: system-steward
**Finding Date**: 2025-12-25
**Governance Authority**: naming-standard.oct.md, visibility-rules.oct.md, hub-authoring-rules.oct.md (injected as `.hestai-sys/governance/rules/hub-authoring-rules.oct.md`)
