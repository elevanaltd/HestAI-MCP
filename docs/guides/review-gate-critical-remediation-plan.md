# Review Gate Critical Remediation Plan

## Status: 🚨 BLOCKING DEPLOYMENT FREEZE

**Created:** 2026-01-18
**Authority:** Critical Engineer (CE) + Code Review Specialist (CRS)
**Scope:** All repos using review-gate (3 active, 3 pending)

---

## Executive Summary

Critical security findings from CRS/CE review of eav-monorepo implementation have identified **fail-open patterns** that invalidate the entire review gate mechanism. This requires immediate coordinated remediation across all repositories.

**Current State:**
- ✅ 3 repos deployed: HestAI-MCP, odyssean-anchor-mcp, eav-monorepo
- 🚫 3 repos pending: (blocked until remediation)
- ❌ All existing deployments have fail-open vulnerabilities

**Critical Issues:**
1. **CRITICAL**: Git failures return empty list → bypass review gates
2. **CRITICAL**: Comment check failures return True → bypass validation
3. **HIGH**: Fork PRs fail due to branch fetch logic
4. **MODERATE**: Emergency bypass has no audit trail

---

## Blocking Issues Detail

### Issue 1: Fail-Open on Git Failures (CRITICAL)

**Location:** `scripts/validate_review.py:48`

```python
# CURRENT (UNSAFE):
def get_changed_files() -> list[dict[str, Any]]:
    try:
        # ... git diff logic
    except subprocess.CalledProcessError:
        return []  # ❌ FAIL-OPEN: Empty list bypasses all checks
```

**Impact:**
- Any git error causes script to exit success
- PR merges without review validation
- Governance control completely bypassed

**Required Fix:**
```python
def get_changed_files() -> list[dict[str, Any]]:
    try:
        # ... git diff logic
    except subprocess.CalledProcessError as e:
        if "CI" in os.environ:
            print(f"❌ CRITICAL: Git diff failed: {e}")
            sys.exit(1)  # ✅ FAIL-CLOSED in CI
        else:
            print(f"⚠️  Warning: Git diff failed: {e}")
            return []  # Local: warn but don't block
```

---

### Issue 2: Fail-Open on Comment Check (CRITICAL)

**Location:** `scripts/validate_review.py:147-149`

```python
# CURRENT (UNSAFE):
except (subprocess.CalledProcessError, json.JSONDecodeError):
    # If we can't check, be permissive
    return True, "Unable to check PR comments"  # ❌ FAIL-OPEN
```

**Impact:**
- GitHub API failures bypass approval checks
- Network errors allow unreviewed merges
- Governance validation theater

**Required Fix:**
```python
except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
    if "CI" in os.environ:
        print(f"❌ CRITICAL: Cannot validate PR comments: {e}")
        return False, f"❌ Comment validation failed: {e}"  # ✅ FAIL-CLOSED
    else:
        return True, f"⚠️  Local: Cannot check comments: {e}"
```

---

### Issue 3: Fork PR Incompatibility (HIGH)

**Location:** `.github/workflows/review-gate.yml:63-68`

**Problem:** Already fixed in HestAI-MCP PR #193 but not deployed to other repos

**Status:** ✅ Solution exists, needs propagation

---

### Issue 4: Emergency Bypass Audit Gap (MODERATE)

**Location:** `scripts/validate_review.py:154-171`

**Current:** Commit message check only, no audit trail

**Required:**
- Audit log: `.hestai/audit/bypass-log.jsonl`
- Maintainer approval artifact required
- Post-merge review tracking

---

## Remediation Protocol

### Phase 1: IMMEDIATE (Today) 🚨

**Action:** Deployment freeze + issue creation

1. **Create GitHub Issue** in HestAI-MCP repo
   - Title: `[CRITICAL] Review Gate Fail-Open Vulnerabilities`
   - Labels: `security`, `blocking`, `review-gate`
   - Assignee: Implementation Lead
   - Link to this document

2. **Freeze New Deployments**
   - ⚠️ Do NOT deploy to 3 pending repos
   - Document freeze in all repo READMEs
   - Notify stakeholders

3. **Risk Assessment**
   - Existing deployments: Low immediate risk (internal repos, trusted contributors)
   - Future deployments: High risk (blocks must be fixed first)

---

### Phase 2: TDD DEVELOPMENT (Next 2-3 days) 🧪

**Responsible:** Implementation Lead
**Review:** CRS + CE
**Protocol:** RED → GREEN → REFACTOR

#### Step 1: Create Test Suite

**File:** `tests/test_validate_review.py`

```python
"""
Test suite for review validation script.
Implements TDD protocol for fail-closed behavior.
"""
import pytest
import subprocess
from unittest.mock import patch, MagicMock

class TestGetChangedFiles:
    """Test file change detection with fail-closed behavior."""

    def test_git_failure_in_ci_exits_nonzero(self):
        """CRITICAL: Git failures must fail-closed in CI."""
        with patch.dict('os.environ', {'CI': 'true'}):
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git')):
                with pytest.raises(SystemExit) as exc:
                    get_changed_files()
                assert exc.value.code == 1

    def test_git_failure_locally_returns_empty(self):
        """Local git failures warn but don't block."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git')):
                result = get_changed_files()
                assert result == []

class TestCheckPRComments:
    """Test PR comment validation with fail-closed behavior."""

    def test_api_failure_in_ci_returns_false(self):
        """CRITICAL: Comment check failures must fail-closed in CI."""
        with patch.dict('os.environ', {'CI': 'true', 'PR_NUMBER': '123'}):
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'gh')):
                approved, message = check_pr_comments('TIER_2_CRS')
                assert approved is False
                assert "validation failed" in message.lower()

    def test_api_failure_locally_returns_true(self):
        """Local comment checks are permissive."""
        with patch.dict('os.environ', {'PR_NUMBER': '123'}):
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'gh')):
                approved, message = check_pr_comments('TIER_2_CRS')
                assert approved is True

class TestEmergencyBypass:
    """Test emergency bypass audit trail."""

    def test_bypass_creates_audit_log(self):
        """Emergency bypass must create audit trail."""
        # Test implementation
        pass
```

**Test Markers:**
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "security: Security-critical tests (must pass)",
    "fail_closed: Fail-closed behavior tests",
]
```

#### Step 2: Implement Fixes (TDD RED → GREEN)

1. **Run tests** → RED (all fail)
2. **Implement fail-closed logic** → GREEN (tests pass)
3. **Refactor** → Clean up, ensure clarity
4. **Git evidence** → Commit with test proof

#### Step 3: CRS Review

- Logic correctness ✅
- Test coverage ≥90% ✅
- No new security issues ✅

#### Step 4: CE Review

- Fail-closed verified ✅
- Production readiness ✅
- Deployment plan approved ✅

---

### Phase 3: COORDINATED ROLLOUT (After tests pass)

**Responsible:** Implementation Lead + System Steward

#### Step 1: Version Bump

```python
# scripts/validate_review.py
"""
Version: 2.0.0 (SECURITY: Fail-closed error handling)
Breaking Change: Now exits non-zero on CI failures
Source: https://github.com/elevanaltd/HestAI-MCP
"""
```

#### Step 2: Update All Repos Simultaneously

**Deployment Order:**
1. HestAI-MCP (origin repo) - PR with tests
2. odyssean-anchor-mcp - Copy v2.0.0
3. eav-monorepo - Copy v2.0.0
4. Wait for validation (1 week)
5. Deploy to 3 pending repos

**PR Template:**
```
Title: [SECURITY] Update review-gate to v2.0.0 (fail-closed)

## Security Fix

Addresses critical fail-open vulnerabilities identified in CE/CRS review.

## Breaking Changes

- Git failures now exit non-zero in CI (was: return empty list)
- Comment check failures now block in CI (was: permissive)

## Test Evidence

- ✅ `pytest tests/test_validate_review.py -m security`
- ✅ Coverage: 95%
- ✅ CRS Approved: [link to review]
- ✅ CE Approved: [link to review]

## Rollout Coordination

This is part of coordinated security rollout across 6 repos.
See: docs/guides/review-gate-critical-remediation-plan.md
```

#### Step 3: Validation (Post-Deployment)

**Per Repo:**
1. Test fork PR (verify fork support works)
2. Test git failure (verify fail-closed behavior)
3. Test comment validation failure (verify blocking)
4. Monitor for false positives (1 week)

---

### Phase 4: POST-REMEDIATION (After rollout complete)

1. **Update Distribution Strategy**
   - Document security incident
   - Confirm evolution trigger hit (6 repos)
   - Plan migration to reusable action (Phase 2)

2. **Create Reusable Action** (Next evolution)
   - Package as `elevanaltd/HestAI-MCP/.github/actions/review-gate@v2`
   - Single source of truth
   - Version-pinned consumption

3. **Add to CI/CD Standards**
   - Mandatory for all new HestAI repos
   - Include in project templates
   - Add to governance rules

---

## Governance Controls

### Deployment Freeze Authority

**Who Can Lift Freeze:**
- ✅ Critical Engineer (after CE APPROVED)
- ✅ Code Review Specialist (after CRS APPROVED)
- ✅ Implementation Lead (with CE+CRS sign-off)

**Freeze Conditions:**
- ❌ All blocking issues resolved
- ❌ Test suite passing (≥90% coverage)
- ❌ CRS + CE approval obtained
- ❌ Rollout plan documented

### Review Requirements

**This Remediation:**
- Implementation: Implementation Lead (TDD required)
- CRS Review: MANDATORY (logic + security)
- CE Review: MANDATORY (production readiness)

**Evidence Required:**
```
CRS APPROVED: [detailed assessment]
CE APPROVED: Production deployment APPROVED - all blocking issues resolved

Test Evidence:
pytest tests/test_validate_review.py -m security --cov
Coverage: 95%
All security tests: PASSED
```

---

## Communication Plan

### Stakeholders

1. **Repos Currently Using (3)**
   - HestAI-MCP
   - odyssean-anchor-mcp
   - eav-monorepo

2. **Repos Pending (3)**
   - [List repos blocked by freeze]

### Messages

**To Current Users:**
```
⚠️ SECURITY NOTICE: Review Gate Deployment Freeze

Critical fail-open vulnerabilities discovered in review-gate validation.
All deployments frozen until remediation complete.

Impact: Low (internal repos, trusted contributors)
Timeline: Remediation in progress, ~3 days to resolution
Action Required: None (coordinated rollout planned)

Details: docs/guides/review-gate-critical-remediation-plan.md
```

**To Pending Users:**
```
⚠️ Review Gate Deployment Blocked

Planned review-gate deployment blocked due to security remediation.
Will resume after fail-closed fixes validated.

Timeline: ~3 days for remediation + testing
Notification: Will notify when deployment approved

Alternative: Continue with existing review process temporarily
```

---

## Success Criteria

### Remediation Complete When:

- ✅ All blocking issues resolved
- ✅ Test suite ≥90% coverage with security markers
- ✅ CRS approval obtained
- ✅ CE approval obtained
- ✅ All 3 current repos updated to v2.0.0
- ✅ Fork PR tested and working
- ✅ 1 week validation period passed
- ✅ Zero false positives reported

### Deployment Freeze Lifted When:

- ✅ All success criteria met
- ✅ CE issues NO-GO lifted to GO
- ✅ CRS confirms reliability score ≥95/100
- ✅ Rollout plan approved

---

## Ownership

**Overall:** Implementation Lead
**Security:** Critical Engineer
**Quality:** Code Review Specialist
**Coordination:** System Steward

**Accountability:** This is a CODE_REVIEW_STANDARDS domain issue - CE has blocking authority until remediation proves production-ready.

---

## Appendix: Why This Matters

### Fail-Open vs Fail-Closed

**Fail-Open (UNSAFE for security controls):**
```python
try:
    validate_security()
except:
    return True  # ❌ "When in doubt, allow" - security theater
```

**Fail-Closed (REQUIRED for security controls):**
```python
try:
    validate_security()
except:
    return False  # ✅ "When in doubt, block" - real enforcement
```

### Review Gates are Security Controls

Review gates enforce governance policy. Fail-open patterns mean:
- Git errors → PRs merge without review
- API failures → approvals not validated
- Network issues → security bypassed

This isn't a "nice-to-have" - it's a **security control that must work correctly or not at all**.

---

## Next Steps

1. ✅ Create GitHub issue (Implementation Lead)
2. ✅ Notify stakeholders (System Steward)
3. ✅ Begin TDD development (Implementation Lead)
4. ⏳ CRS/CE reviews (after tests green)
5. ⏳ Coordinated rollout (after approvals)

**Timeline:** 3-5 days to resolution, 1 week validation

**Status Updates:** Daily in HestAI-MCP issue tracker
