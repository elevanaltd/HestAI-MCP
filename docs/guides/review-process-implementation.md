# Review Process Implementation Guide

## Overview

This guide explains how to implement the tiered review process in other projects. The system provides automated enforcement of code review requirements through local pre-commit hooks and GitHub Actions CI.

**Current Version:** 2.0.0 (SECURITY: fail-closed error handling)

> **Distribution Strategy**: Currently using manual copy approach during active development. See [review-process-distribution-strategy.md](review-process-distribution-strategy.md) for evolution plans and when to migrate to reusable GitHub Actions.
>
> **Security Note**: Version 2.0.0 implements fail-closed behavior in CI - git failures and comment validation failures now block PRs instead of allowing bypass. See PR #195 for details.

## Prerequisites

- Project has `.hestai-sys/` directory structure in place
- Python 3.11+ available
- GitHub repository with Actions enabled
- `gh` CLI installed for local/CI use

## Implementation Steps

### 1. Copy Required Files

Copy these four files from this repository to your target project:

```bash
# Core validation script
scripts/validate_review.py

# GitHub Actions workflow
.github/workflows/review-gate.yml

# Governance rule (OCTAVE format)
.hestai-sys/governance/rules/review-requirements.oct.md
```

### 2. Update Pre-commit Configuration

Add the review validator hook to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: review-validator
        name: Check review requirements
        entry: python3 scripts/validate_review.py
        language: system
        pass_filenames: false
        always_run: true
```

**Important**: The hook runs locally but is **non-blocking** (returns 0 exit code). It provides feedback but doesn't prevent commits. Enforcement happens in CI.

### 3. Verify File Locations

Ensure files are in the correct locations:

```
your-project/
├── .github/
│   └── workflows/
│       └── review-gate.yml              # CI workflow
├── .hestai-sys/
│   └── governance/
│       └── rules/
│           └── review-requirements.oct.md  # Governance rule
├── scripts/
│   └── validate_review.py              # Validation logic
└── .pre-commit-config.yaml             # Pre-commit config
```

### 4. Customize Review Tiers (Optional)

Edit `scripts/validate_review.py` to adjust tier thresholds:

**Line 60-66**: Exempt patterns
```python
exempt_patterns = [
    r".*\.md$",
    r"^tests/.*$",
    r".*\.lock$",
    r".*\.json$",
]
```

**Line 88-91**: Tier 3 triggers
```python
tier3_triggers = [
    any(path.endswith(".sql") for path in changed_paths),
    total_lines > 500,
]
```

**Line 92-100**: Tier thresholds
```python
if 50 <= total_lines <= 500:
    return "TIER_2_STANDARD", f"CRS + CE review required - {total_lines} lines changed"

if total_lines < 50 and len(non_exempt_files) == 1:
    return "TIER_1_SELF", f"Self-review sufficient - {total_lines} lines in single file"
```

### 5. Install Pre-commit Hooks

```bash
pre-commit install
```

## Review Tier System

### Tier 0: Exempt
- **Trigger**: Only Markdown docs (`*.md`, including `*.oct.md`), tests, lockfiles, or JSON changes
- **Review**: None required
- **Enforcement**: Automatic

### Tier 1: Self-Review
- **Trigger**: < 50 non-exempt lines in single non-exempt file
- **Review**: Implementation Lead (IL) self-review or HO supervisory review
- **Proof**: PR comment: `IL SELF-REVIEWED: [rationale]` or `HO REVIEWED: [rationale]`
- **Example**: `IL SELF-REVIEWED: Fixed typo in error message`
- **Alternative**: `HO REVIEWED: delegated to IL, verified output` (when HO delegates then reviews)

### Tier 2: Standard Review
- **Trigger**: 50-500 non-exempt lines, or default when ambiguous
- **Review**: CRS + Critical Engineer (CE) approval
- **Proof**:
  - `CRS APPROVED: [assessment]`
  - `CE APPROVED: [critical assessment]`
- **Example**: `CRS APPROVED: Logic correct, tests pass, no security issues`

### Tier 3: Strict Review
- **Trigger**:
  - \> 500 non-exempt lines changed
  - SQL files modified
- **Review**: Dual CRS (Gemini + Codex) + Critical Engineer (CE)
- **Proof**:
  - `CRS (Gemini) APPROVED: [assessment]`
  - `CRS (Codex) APPROVED: [assessment]`
  - `CE APPROVED: [critical assessment]`
- **Example**: `CE APPROVED: Architecture sound, performance acceptable`

## Emergency Bypass

For critical hotfixes, include `EMERGENCY:` in commit message:

```bash
git commit -m "fix: critical security patch

EMERGENCY: Production outage, full review required post-merge"
```

**Important**: Emergency commits require post-merge review tracking.

## How It Works

### Local Development
1. Developer makes changes and commits
2. Pre-commit hook runs `validate_review.py`
3. Script shows tier and requirements (non-blocking feedback)
4. Developer can proceed with commit

### Pull Request Flow
1. PR opened/updated → GitHub Actions workflow triggers
2. Workflow runs `validate_review.py` with `CI=true`
3. Script checks for required approval comments
4. **Blocks merge** if approvals missing
5. Bot posts status comment with requirements
6. Developer/reviewer adds required comment
7. Workflow re-runs on new comment (via `issue_comment` trigger)
8. Merge unblocked when approvals present

### Workflow Triggers
The GitHub Actions workflow responds to:
- `pull_request`: [opened, synchronize, reopened, edited]
- `issue_comment`: [created, edited]

This ensures re-validation when approval comments are added.

### Fork Support
The workflow uses GitHub's universal PR ref system (`refs/pull/<number>/head`) which works for:
- **Same-repository PRs**: Branch in same repo
- **Fork PRs**: Branch from external fork

This eliminates the need for fork detection logic and ensures external contributions work seamlessly.

## Testing the Implementation

### Local Testing
```bash
# Make a small change
echo "# test" >> docs/test.md
git add docs/test.md
git commit -m "test: verify review process"

# Should see tier detection but allow commit
```

### CI Testing
1. Create a test PR with > 50 lines changed
2. Verify workflow runs and blocks merge
3. Add required approval comment (e.g., `CRS APPROVED: test`)
4. Verify workflow re-runs and unblocks

## Project-Specific Customization

### Adjust Role Names
If your project uses different role names, update:
- `scripts/validate_review.py` lines 130, 135, 140 (comment patterns)
- `.hestai-sys/governance/rules/review-requirements.oct.md` section §2

### Change Thresholds
Adjust line count thresholds in `determine_review_tier()` function (line 52-100 in `validate_review.py`)

### Add Custom Triggers
Add project-specific tier 3 triggers (e.g., API changes, database schemas) around line 81-86

## Troubleshooting

### "Unable to check PR comments"
- Ensure `gh` CLI is installed and authenticated
- Verify GitHub Actions has `pull-requests: write` permission
- Check `GH_TOKEN` is set in workflow environment

### Workflow doesn't re-run on comments
- Verify workflow has `issue_comment` trigger enabled
- Check comment is on a PR (not regular issue)
- Ensure workflow has `issues: write` permission

### Wrong tier detected
- Check exempt patterns match your project structure
- Verify file paths in `changed_paths` list
- Add debug output: `print(f"DEBUG: {changed_paths}")`

### Fork PR failures
- **Not an issue**: The workflow uses GitHub's universal PR ref system
- Works automatically for both same-repo and fork PRs
- No fork detection logic needed
- If you see checkout failures, verify the PR number is correct

## Files Summary

| File | Purpose | Modify? |
|------|---------|---------|
| `scripts/validate_review.py` | Core tier detection and comment validation | **Yes** - Customize tiers, patterns, thresholds |
| `.github/workflows/review-gate.yml` | CI enforcement and PR status updates | **Rarely** - Only if changing workflow triggers |
| `.hestai-sys/governance/rules/review-requirements.oct.md` | Governance documentation | **Optional** - Update if changing role names |
| `.pre-commit-config.yaml` | Local hook registration | **Required** - Add review-validator hook |

## Next Steps

After implementation:
1. Test with a few PRs to calibrate thresholds
2. Adjust tier triggers based on team feedback
3. Document role assignments (IL, CRS, CE) for your team
4. Consider adding bypass audit logging
5. Integrate with project-specific governance rules
