# Agent Instructions: How to Use the submit_review Tool

## What is the Review Gate Tool?

The `submit_review` tool is an MCP (Model Context Protocol) tool that allows agents to post formal review comments on GitHub Pull Requests. These comments are specially formatted to be recognized by the review-gate CI system, which automatically validates and processes them to clear review requirements.

## When to Use This Tool

Use the `submit_review` tool when:
- You've been asked to review a Pull Request
- You're completing implementation and need to self-review (IL role)
- You're a Code Review Specialist (CRS) reviewing code quality
- You're a Critical Engineer (CE) reviewing production readiness
- You need to block or conditionally approve changes

## How to Use the Tool

### Basic Usage

The tool requires these parameters:
- `repo`: Repository in "owner/name" format (e.g., "elevanaltd/HestAI-MCP")
- `pr_number`: The PR number to comment on (must be an existing PR)
- `role`: Your reviewing role - one of "CRS", "CE", or "IL"
- `verdict`: Your decision - one of "APPROVED", "BLOCKED", or "CONDITIONAL"
- `assessment`: Your detailed review assessment (required, cannot be empty)
- `dry_run`: (optional) Set to `true` to test without posting (default: `false`)
- `model_annotation`: (optional) Add your model name for transparency (e.g., "Claude", "Gemini")

### Example Agent Usage

```python
# For an Implementation Lead self-review
await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="IL",
    verdict="APPROVED",
    assessment="Self-review complete: All tests passing, TDD process followed, no logic changes",
    model_annotation="Claude"
)

# For a Code Review Specialist review
await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="CRS",
    verdict="APPROVED",
    assessment="Code follows standards, good test coverage, clean architecture",
    model_annotation="Claude"
)

# For a Critical Engineer blocking a PR
await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="CE",
    verdict="BLOCKED",
    assessment="Security vulnerability detected: SQL injection risk in user input handling at line 45",
    model_annotation="Claude"
)

# For testing your format without posting
await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="CRS",
    verdict="APPROVED",
    assessment="Test review",
    dry_run=True  # This won't post to GitHub
)
```

## Review Tiers and Requirements

The system has three review tiers based on change complexity:

### Tier 1: Self-Review (IL Role)
- **When**: Changes under 50 lines, documentation/config only
- **Required**: IL APPROVED comment
- **Example changes**: README updates, config tweaks, small fixes

### Tier 2: Code Review (CRS Role)
- **When**: 50-500 lines of code changes
- **Required**: CRS APPROVED comment
- **Example changes**: Feature additions, bug fixes, refactoring

### Tier 3: Full Review (CRS + CE Roles)
- **When**: 500+ lines, architecture changes, database changes, cross-module changes
- **Required**: Both CRS APPROVED and CE APPROVED comments
- **Example changes**: Major features, system redesigns, security-critical code

## Understanding the Response

The tool returns a structured response:

```json
{
  "success": true,
  "comment_url": "https://github.com/owner/repo/pull/123#issuecomment-456",
  "validation": {
    "would_clear_il": false,
    "would_clear_crs": true,
    "would_clear_ce": false
  },
  "tier_requirement": "TIER_2_CRS: CRS APPROVED comment required"
}
```

### Error Handling

If the tool fails, check the `error_type`:

- `"validation"`: Your input is invalid (wrong role/verdict format)
- `"auth"`: GitHub token is missing or invalid
- `"network"`: Temporary network issue - retry immediately
- `"rate_limit"`: GitHub API rate limit - wait and retry with backoff
- `"github_api"`: GitHub returned an error (PR doesn't exist, etc.)

## Important Notes for Agents

1. **PR Must Exist**: You cannot use this tool to review commits that aren't in a PR yet. The PR must be created first.

2. **Format is Strict**: The tool validates your comment format before posting. Invalid formats are rejected to prevent posting comments that won't clear the CI gate.

3. **Only APPROVED Clears Gates**: BLOCKED and CONDITIONAL verdicts are valid reviews but won't clear the review gate. They're used to provide feedback that needs addressing.

4. **Be Specific in Assessments**: Especially for BLOCKED/CONDITIONAL verdicts, provide specific line numbers, file names, or detailed explanations of issues.

5. **Use Dry Run for Testing**: When unsure about format, use `dry_run=true` to validate without posting.

## Workflow Examples

### Simple Change Workflow (Agent as IL)
1. Implement the requested change
2. Run tests to ensure everything passes
3. Create PR using `gh pr create`
4. Use `submit_review` with role="IL" to self-review
5. CI validates and allows merge

### Multi-Agent Review Workflow
1. IL agent implements feature
2. IL creates PR
3. CRS agent reviews with `submit_review(role="CRS", ...)`
4. CE agent reviews with `submit_review(role="CE", ...)`
5. If both approve, PR can be merged
6. If either blocks, IL addresses feedback and reviewers re-review

### Draft PR Strategy (For Complex Changes)
1. IL creates draft PR: `gh pr create --draft`
2. Reviewers can comment incrementally as work progresses
3. When ready, IL marks ready: `gh pr ready {pr_number}`
4. Final approvals posted with `submit_review`
5. Merge when all requirements met

## Checking Review Status

To see if reviews have been posted correctly:
1. Check the PR comments on GitHub
2. Look for the CI check status (review-gate)
3. The validation response tells you which gates would be cleared

## Common Mistakes to Avoid

1. **Don't forget the assessment**: Empty or whitespace-only assessments are rejected
2. **Don't use wrong role**: Ensure you're using the correct role for your agent type
3. **Don't assume verdicts clear gates**: Only APPROVED verdicts clear gates
4. **Don't post without a PR**: The PR must exist before you can review it
5. **Don't ignore validation errors**: If dry_run shows issues, fix them before posting

## Getting Help

- Check the tool's validation response for specific error messages
- Use `dry_run=true` to test formats
- Refer to `docs/guides/submit_review_tool_workflow.md` for detailed workflows
- The CI workflow logs will show why a review wasn't recognized
