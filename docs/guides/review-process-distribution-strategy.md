# Review Process Distribution Strategy

## Current Situation

We've developed a tiered review enforcement system that currently requires copying 4 files across repositories:
1. `scripts/validate_review.py` (228 lines, stdlib only)
2. `.github/workflows/review-gate.yml` (182 lines)
3. `.hestai-sys/governance/rules/review-requirements.oct.md` (governance doc)
4. `.pre-commit-config.yaml` update (6 lines)

**Current Pain Points:**
- Changes must be manually propagated across repos
- Bug fixes (like fork support) require coordinated updates
- No single source of truth for the review logic
- Version drift risk between implementations

## Distribution Options Analysis

### Option 1: Continue Manual Copy (Current Approach)

**Pros:**
- Simple to understand
- Full control per-repo
- Easy to customize for specific needs
- No external dependencies

**Cons:**
- ❌ Manual propagation of fixes
- ❌ Version drift across repos
- ❌ Coordination overhead
- ❌ Bug fixes need multiple PRs

**Best For:** Initial development phase (where we are now)

**Verdict:** ✅ **Acceptable for now, but needs evolution**

---

### Option 2: Reusable GitHub Actions Workflow

Package the workflow as a **composite action** or **reusable workflow**.

**Implementation:**
```yaml
# In HestAI-MCP repo: .github/actions/review-gate/action.yml
name: 'HestAI Review Gate'
description: 'Tiered review enforcement for HestAI projects'
inputs:
  pr_number:
    required: true
runs:
  using: 'composite'
  steps:
    - uses: actions/checkout@v4
    - run: ${{ github.action_path }}/validate_review.py
```

**Usage in other repos:**
```yaml
# In other-repo/.github/workflows/review-gate.yml
jobs:
  check-review:
    steps:
      - uses: elevanaltd/HestAI-MCP/.github/actions/review-gate@v1
```

**Pros:**
- ✅ Single source of truth for workflow
- ✅ Automatic updates via version tags
- ✅ Standard GitHub approach
- ✅ Can version with git tags (v1, v1.1, etc.)

**Cons:**
- ❌ Still need to copy validation script
- ❌ Requires public repo or GitHub Enterprise
- ❌ Customization harder (must fork action)

**Verdict:** ✅ **Good for workflow, partial solution**

---

### Option 3: Python Package (PyPI or Git)

Create `hestai-review-gate` package with CLI entry point.

**Structure:**
```
hestai-review-gate/
├── pyproject.toml
├── src/
│   └── hestai_review_gate/
│       ├── __init__.py
│       ├── cli.py           # Entry point
│       ├── validator.py     # Core logic
│       └── config.py        # Tier definitions
```

**Installation:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/elevanaltd/hestai-review-gate
    rev: v1.0.0
    hooks:
      - id: review-gate
```

**Or via pip:**
```bash
pip install hestai-review-gate
hestai-review-gate validate --pr-number 123
```

**Pros:**
- ✅ Professional distribution
- ✅ Version management via pip/uv
- ✅ Easy updates (`pip install --upgrade`)
- ✅ Can include config validation
- ✅ Testable in isolation

**Cons:**
- ❌ Overhead for small tool (228 lines)
- ❌ Deployment complexity (PyPI or private registry)
- ❌ Still need workflow file per-repo
- ❌ Dependency management in CI

**Verdict:** ⚠️ **Over-engineered for current scale**

---

### Option 4: Git Subtree/Submodule

Include review-gate as a subtree/submodule in each repo.

**Subtree approach:**
```bash
git subtree add --prefix tools/review-gate \
  https://github.com/elevanaltd/HestAI-MCP.git \
  main --squash
```

**Pros:**
- ✅ Single source of truth
- ✅ Git-native versioning
- ✅ Can pull updates easily

**Cons:**
- ❌ Subtree merge conflicts
- ❌ Pollutes git history
- ❌ Still need workflow integration
- ❌ Not common pattern for this use case

**Verdict:** ❌ **Not recommended for tooling**

---

### Option 5: Centralized Script Repository + Pre-commit Remote Hook

Use pre-commit's remote hook feature to fetch script directly.

**Setup:**
```yaml
# .pre-commit-config.yaml in consuming repo
repos:
  - repo: https://github.com/elevanaltd/HestAI-MCP
    rev: v1.0.0  # Git tag
    hooks:
      - id: review-validator
        name: Check review requirements
        entry: scripts/validate_review.py
        language: script
        pass_filenames: false
```

**In HestAI-MCP, add:**
```yaml
# .pre-commit-hooks.yaml
- id: review-validator
  name: HestAI Review Gate
  entry: scripts/validate_review.py
  language: script
  pass_filenames: false
  always_run: true
```

**Pros:**
- ✅ Single source of truth
- ✅ Version control via git tags
- ✅ Automatic updates when repos update pre-commit
- ✅ Minimal overhead
- ✅ Standard pre-commit pattern

**Cons:**
- ❌ Still need to copy workflow file
- ❌ Requires public repo access in CI
- ❌ Pre-commit auto-update might break things

**Verdict:** ✅ **Good for pre-commit hook portion**

---

## Recommended Strategy (Hybrid Approach)

### Phase 1: Current (Stabilization - 1-2 months)
**Status:** You are here ✅

Continue manual copy approach while:
- Gathering feedback from multiple repos
- Finding bugs (like fork support issue)
- Understanding customization needs
- Determining if tier thresholds are universal

**Actions:**
- ✅ Keep updating implementation guide
- ✅ Track issues centrally in HestAI-MCP repo
- ✅ Document all customizations made per-repo

---

### Phase 2: Consolidation (When >3 repos use it)
**Triggers:**
- More than 3 repos using review gate
- OR first external contributor blocked by old version
- OR second major bug fix needed across repos

**Implement:**

1. **Reusable GitHub Action** (for workflow)
   ```
   HestAI-MCP/.github/actions/review-gate/
   ├── action.yml
   ├── validate_review.py
   └── README.md
   ```

2. **Pre-commit Hook Definition** (for local validation)
   ```yaml
   # HestAI-MCP/.pre-commit-hooks.yaml
   - id: review-gate
     name: HestAI Review Validator
     entry: scripts/validate_review.py
     language: script
   ```

3. **Consuming repos use:**
   ```yaml
   # .github/workflows/review-gate.yml
   jobs:
     review:
       steps:
         - uses: elevanaltd/HestAI-MCP/.github/actions/review-gate@v1

   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/elevanaltd/HestAI-MCP
       rev: review-gate-v1.0.0
       hooks:
         - id: review-gate
   ```

---

### Phase 3: Productization (If becomes widely used)
**Triggers:**
- >10 repos using it
- OR external organizations want to use it
- OR significant feature additions needed

**Consider:**
- Separate `hestai-review-gate` repository
- PyPI package for broader distribution
- Configuration file support (`.reviewgate.yml`)
- Plugin system for custom tier logic

---

## Migration Path

### From Manual Copy → Reusable Action

**Step 1: Create composite action in HestAI-MCP**
```yaml
# .github/actions/review-gate/action.yml
name: 'Review Gate'
description: 'Tiered review enforcement'
runs:
  using: 'composite'
  steps:
    - run: python3 ${{ github.action_path }}/validate_review.py
      shell: bash
```

**Step 2: Update one repo as pilot**
```yaml
# Old: Run script directly
- run: python3 scripts/validate_review.py

# New: Use action
- uses: elevanaltd/HestAI-MCP/.github/actions/review-gate@main
```

**Step 3: Tag releases**
```bash
git tag -a review-gate-v1.0.0 -m "Review gate v1.0.0 with fork support"
git push --tags
```

**Step 4: Migrate other repos to pinned version**
```yaml
- uses: elevanaltd/HestAI-MCP/.github/actions/review-gate@review-gate-v1.0.0
```

---

## Decision Framework

**Use Manual Copy When:**
- ✅ Fewer than 3 repos
- ✅ Still iterating on core logic
- ✅ Frequent breaking changes expected
- ✅ Heavy customization per-repo

**Move to Reusable Action When:**
- ✅ Logic is stable
- ✅ >3 repos using it
- ✅ Bug fixes need coordination
- ✅ Customization is mostly in config

**Create Separate Package When:**
- ✅ >10 repos using it
- ✅ External users want it
- ✅ Complex configuration needed
- ✅ Needs testing infrastructure

---

## Immediate Recommendation

**For Now (Next 1-2 months):**

1. ✅ **Keep manual copy approach** - You're in active development
2. ✅ **Centralize issues** - Create "review-gate" label in HestAI-MCP
3. ✅ **Document deviations** - Track per-repo customizations
4. ✅ **Version the artifacts** - Add version comments to files

**Add to files:**
```python
# scripts/validate_review.py
"""
Review validation script - enforces review requirements based on PR changes.
Version: 2.0.0 (SECURITY: Fail-closed error handling)
Source: https://github.com/elevanaltd/HestAI-MCP
Breaking Change: Now exits non-zero on CI failures
"""
```

```yaml
# .github/workflows/review-gate.yml
# HestAI Review Gate v2.0.0
# Source: https://github.com/elevanaltd/HestAI-MCP
# Last updated: 2026-01-19
```

**When to evolve:**
- ✅ After 3rd repo adopts it
- ✅ After 2nd bug fix cycle
- ✅ When coordination pain exceeds setup cost

---

## Conclusion

**Your situation is normal** ✅ - Manual coordination during development is standard.

**The fix propagation you experienced** (fork support) is exactly the signal that tells you when to evolve your distribution strategy. But you're not there yet.

**Next milestone:** After 1-2 more repos adopt this AND you have one more bug fix cycle, revisit this document and implement Phase 2 (Reusable Action).

**Current status:** ✅ Appropriate for development phase
**Evolution trigger:** 3+ repos OR 2+ coordinated bug fixes
**Target state:** Reusable GitHub Action + Pre-commit hook definition
