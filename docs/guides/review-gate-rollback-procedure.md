# Review Gate Rollback Procedure

## Quick Rollback (< 5 minutes)

If issues arise with v2.0.0 review-gate implementation:

### 1. Immediate Reversion
```bash
# Revert to previous version
git revert <commit-hash-of-v2.0.0>
git push origin fix-review-gate
```

### 2. Bypass Temporarily
Add `EMERGENCY:` prefix to commit messages to bypass while fixing:
```bash
git commit -m "EMERGENCY: Reverting review-gate to v1.0.0 due to false positives"
```

### 3. Notification
- Comment on Issue #194 with rollback reason
- Tag @critical-engineer and @code-review-specialist

## Monitoring Verification

### Audit Trail Location
`.hestai/audit/bypass-log.jsonl`

### Monitoring Points
1. **CI Pipeline**: Review-gate exit codes logged
2. **Audit Log**: Emergency bypasses tracked with metadata
3. **False Positives**: Track via Issue #194 comments

### Success Metrics (1 week validation)
- Zero false positives blocking legitimate PRs
- All emergency bypasses have audit entries
- No unintended fail-open behaviors observed

## Recovery Checklist
- [ ] Tests still passing locally
- [ ] CI pipeline functional
- [ ] Audit logs being created
- [ ] No false positives reported
- [ ] All repos using same version
