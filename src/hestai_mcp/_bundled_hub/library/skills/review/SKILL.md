---
name: review
description: Orchestrate the full PR review workflow - tier classification, bot triage, evidence collection, gate status check, and reviewer dispatch. Use on any PR that needs the CRS/CE review chain.
allowed-tools: [Read, Grep, Glob, Bash, mcp__pal__clink, mcp__pal__chat, mcp__hestai__submit_review]
---

# /review - PR Review Workflow Orchestrator

Structured review workflow for PRs. Classifies tier, triages bot findings, collects
evidence, checks gate status, and dispatches reviewers in the correct chain order.

## When to Use

Trigger `/review` when:
- A PR is ready for review (all CI checks green)
- You need to orchestrate the CRS/CE review chain
- You want to check current review gate status on a PR

## Required Context

The user must provide:
- `{repo}`: Repository in `owner/name` format (e.g., `elevanaltd/HestAI-MCP`)
- `{pr_number}`: The PR number to review

## Workflow Sections

### S1 TIER_CLASSIFICATION

Determine the review tier for the PR.

1. Fetch PR metadata: `gh pr view {pr_number} --repo {repo} --json files,additions,deletions`
2. Run tier classification: `.venv/bin/python scripts/validate_review.py` (or parse files locally using the tier rules from review-requirements)
3. Record tier (T0-T4) and required reviewer roles

Tier rules:
- T0: Only exempt files (markdown, tests-only, generated JSON, lock files)
- T1: <10 non-exempt lines, single file, no security paths
- T2: 10-500 lines or multiple files -> TMG + CRS + CE
- T3: >500 lines, architecture, security, SQL, new tools -> TMG + CRS + CE + CIV
- T4: Manual only (`/review --strategic`) -> TMG + CRS + CE + CIV + PE

### S2 EVIDENCE_PACK

Collect the evidence pack for reviewers.

1. Fetch the full diff: `gh pr diff {pr_number} --repo {repo}`
2. Fetch CI status: `gh pr checks {pr_number} --repo {repo}`
3. Fetch PR description: `gh pr view {pr_number} --repo {repo} --json body,title,headRefName`
4. Identify changed file paths and categorize by facet (ROUTINE_CODE, SECURITY, GOVERNANCE, EXECUTABLE_SPEC, META_CONTROL_PLANE)

### S2.5 BOT_TRIAGE

Collect and summarize bot review findings as ADVISORY context for human/agent reviewers.
Bot findings are strictly ADVISORY -- they NEVER block or satisfy review gates.

1. Fetch inline bot comments on the PR:
   ```
   gh api repos/{repo}/pulls/{pr_number}/comments \
     --jq '.[] | select(.user.login | test("cubic-dev-ai|qodo-code-review|coderabbitai"))'
   ```

2. Fetch PR-level bot comments (not just inline):
   ```
   gh pr view {pr_number} --repo {repo} --json comments \
     --jq '.comments[] | select(.author.login | test("cubic-dev-ai|qodo-code-review|coderabbitai"))'
   ```

3. Summarize bot findings by priority:
   - Cubic findings first (P0/P1 priority items surface first)
   - CodeRabbit findings second (general review)
   - Qodo findings third (monitoring/suggestions)
   - For each bot: extract key concerns, file references, severity indicators

4. Format the summary as a BOT_TRIAGE_BRIEF:
   ```
   === BOT PRE-REVIEW FINDINGS (ADVISORY ONLY) ===
   Status: {N} bot comments found from {bot_names}
   Classification: ADVISORY -- these findings do NOT satisfy or block review gates

   [Cubic] ({N} findings):
   - {P0/P1 items first, then lower priority}

   [CodeRabbit] ({N} findings):
   - {key concerns with file references}

   [Qodo] ({N} findings):
   - {monitoring observations}
   === END BOT TRIAGE ===
   ```

5. If no bot comments found, note: "No bot review comments found on this PR."

### S3 READ_REVIEW_GATE_STATUS

Check current state of the review gate.

1. Check for existing reviewer approvals: `gh pr view {pr_number} --repo {repo} --json comments --jq '.comments[].body'`
2. Look for approval patterns: `TMG APPROVED:`, `CRS APPROVED:`, `CE APPROVED:`, `CIV APPROVED:`, `PE APPROVED:`
3. Look for structured metadata: `<!-- review: {...} -->`
4. Report which roles have approved and which are still needed
5. If all required approvals present, report gate as SATISFIED

### S4 DISPATCH_REVIEWERS

Dispatch reviewers in chain order based on tier. Each reviewer receives
the bot triage summary as additional context.

For T2+ PRs, dispatch in this order:
1. **TMG** (Test Methodology Guardian) - reviews test quality
   - Dispatch via: `mcp__pal__clink` with `cli:goose, role:test-methodology-guardian`
   - Fallback: `cli:codex, role:test-methodology-guardian`
   - Prompt includes: PR diff (test files only), test coverage, bot pre-review findings: {BOT_TRIAGE_BRIEF}

2. **CRS** (Code Review Specialist) - reviews code quality
   - Dispatch via: `mcp__pal__clink` with `cli:gemini, role:code-review-specialist`
   - Fallback: `cli:codex, role:code-review-specialist`
   - Prompt includes: Full PR diff, CI status, facet classification, bot pre-review findings: {BOT_TRIAGE_BRIEF}

3. **CE** (Critical Engineer) - deep review for structural risk
   - Dispatch via: `mcp__pal__clink` with `cli:codex, role:critical-engineer`
   - Fallback: `cli:gemini, role:critical-engineer`
   - Prompt includes: Full PR diff, CRS findings as context, bot pre-review findings: {BOT_TRIAGE_BRIEF}

For T3+ PRs, additionally dispatch:
4. **CIV** (Critical Implementation Validator)
   - Dispatch via: `mcp__pal__clink` with `cli:goose, role:critical-implementation-validator`
   - Prompt includes: Full PR diff, CRS+CE findings, bot pre-review findings: {BOT_TRIAGE_BRIEF}

For T4 PRs, additionally dispatch:
5. **PE** (Principal Engineer)
   - Dispatch via: `mcp__pal__clink` with `cli:goose, role:principal-engineer`
   - Prompt includes: Full PR diff, all prior findings, bot pre-review findings: {BOT_TRIAGE_BRIEF}

### S5 SUBMIT_VERDICTS

Post review verdicts to the PR using `mcp__hestai__submit_review`.

Each reviewer posts their verdict with structured metadata:
```
<!-- review: {"role":"CRS","provider":"gemini","verdict":"APPROVED","sha":"abc1234"} -->
CRS APPROVED: [assessment summary]
```

### S6 GATE_CHECK

Final gate check after all reviewers have posted.

1. Re-run S3 to verify all required approvals are present
2. If gate is satisfied, report success
3. If gate is not satisfied, report which approvals are still missing

## Bot Comment Policy

Bot comments from the following accounts are ADVISORY ONLY:
- `cubic-dev-ai[bot]` - Cubic AI (advisory auto-review, P0/P1 priority)
- `coderabbitai[bot]` - CodeRabbit (advisory auto-review)
- `qodo-code-review[bot]` - Qodo (monitoring)
- `github-copilot[bot]` - Copilot (BLOCKED/non-functional)

These bot comments:
- Are collected and summarized in S2.5 BOT_TRIAGE
- Are passed as context to reviewer dispatch prompts
- NEVER count as approvals for review gate validation
- NEVER block the review gate
- Are explicitly excluded by `scripts/validate_review.py`
