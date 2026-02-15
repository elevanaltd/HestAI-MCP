# submit_review Tool Workflow Guide

## Overview
The `submit_review` MCP tool enables agents to programmatically post PR review comments that clear the review-gate CI check.

## Current Capabilities

### What It Can Do
- Post review comments to existing PRs
- Format comments to match CI validation patterns
- Self-validate that APPROVED comments will clear gates
- Return structured errors with retry guidance
- Support dry-run mode for testing

### Current Limitation
**Requires an existing PR** - The tool posts to GitHub's issue comments API which needs a valid PR number.

## Recommended Workflows

### 1. Simple Changes (Single Agent, Tier 1)
```mermaid
graph LR
    A[IL Implements] --> B[Create PR]
    B --> C[IL Self-Review]
    C --> D[Use submit_review]
    D --> E[CI Validates]
    E --> F[Merge]
```

**Agent Instructions:**
```python
# After creating PR
result = await submit_review(
    repo="owner/repo",
    pr_number=123,
    role="IL",
    verdict="APPROVED",
    assessment="Tier 1 change: formatting only, no logic changes",
    dry_run=False
)
```

### 2. Standard Changes (Multi-Agent Review)
```mermaid
graph LR
    A[IL Implements] --> B[Create PR]
    B --> C[CRS Review]
    C --> D[CE Review]
    D --> E{Both Approved?}
    E -->|Yes| F[Merge]
    E -->|No| G[IL Rework]
    G --> C
```

**HO Orchestration:**
```python
# Step 1: Delegate to IL
Task("implementation-lead", "Implement feature X with TDD")

# Step 2: After PR creation
Task("code-review-specialist", f"""
Review PR #{pr_number} using submit_review tool:
- Code quality and standards
- Test coverage
- Architecture alignment
""")

Task("critical-engineer", f"""
Review PR #{pr_number} using submit_review tool:
- Production readiness
- Performance implications
- Security concerns
""")
```

### 3. Complex Changes (Draft PR Strategy)
```mermaid
graph LR
    A[IL Initial Implementation] --> B[Create Draft PR]
    B --> C[Early CRS Review]
    C --> D[IL Addresses Feedback]
    D --> E[CE Review]
    E --> F[IL Final Changes]
    F --> G[Mark Ready for Review]
    G --> H[Final Approvals]
    H --> I[Merge]
```

**Benefits of Draft PR:**
- Reviews can happen incrementally
- Feedback incorporated early
- Review comments accumulate in one place
- CI runs but doesn't block

**Commands:**
```bash
# Create draft PR
gh pr create --draft --title "WIP: Feature implementation"

# When ready
gh pr ready {pr_number}
```

## Tool Usage Examples

### Dry Run (Testing Format)
```python
# Test without posting
result = await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="CRS",
    verdict="APPROVED",
    assessment="Testing format",
    dry_run=True
)

# Check if format would clear gate
if result["validation"]["would_clear_crs"]:
    print("Format is correct")
```

### With Model Annotation
```python
# Adds model name to review
result = await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="CE",
    verdict="APPROVED",
    assessment="No production risks identified",
    model_annotation="Gemini"  # Produces: "CE (Gemini) APPROVED: ..."
)
```

### Error Handling
```python
result = await submit_review(...)

if not result["success"]:
    error_type = result["error_type"]

    if error_type == "rate_limit":
        # Wait and retry with exponential backoff
        await asyncio.sleep(60)

    elif error_type == "auth":
        # Token issue - needs human intervention
        raise Exception("GitHub token missing or invalid")

    elif error_type == "network":
        # Transient failure - retry immediately
        result = await submit_review(...)

    elif error_type == "validation":
        # Bad input - do not retry
        print(f"Input error: {result['error']}")
```

## Future Enhancements

### 1. Commit Comments (Pre-PR)
Could extend to support commit-level reviews:
```python
# Hypothetical future feature
await submit_commit_review(
    repo="owner/repo",
    commit_sha="abc123",
    role="CRS",
    verdict="APPROVED",
    assessment="Commit looks good"
)
```

### 2. Batch Reviews
Could support reviewing multiple aspects at once:
```python
# Hypothetical future feature
await submit_review_batch(
    repo="owner/repo",
    pr_number=123,
    reviews=[
        {"role": "CRS", "verdict": "APPROVED", "assessment": "..."},
        {"role": "CE", "verdict": "CONDITIONAL", "assessment": "..."}
    ]
)
```

### 3. Review Templates
Could provide standard templates:
```python
# Hypothetical future feature
from hestai_mcp.modules.tools.review_templates import security_review

await submit_review(
    repo="owner/repo",
    pr_number=123,
    role="CE",
    template=security_review,
    findings={"sql_injection": False, "xss": False}
)
```

## Integration with CI

The review comments trigger the review-gate CI check which:

1. Scans PR comments for review patterns
2. Determines required approvals based on change tier
3. Validates format using shared `review_formats.py`
4. Updates PR status check

## Best Practices

1. **Use dry_run first** when testing format
2. **Be specific** in assessments, especially for BLOCKED/CONDITIONAL
3. **Include model annotation** for transparency
4. **Check error_type** to implement appropriate retry logic
5. **Create draft PRs** for complex changes needing iterative review

## Common Issues

### Review Not Recognized by CI
- Check exact format with dry_run
- Ensure no extra characters/formatting
- Verify role and verdict are valid

### Rate Limiting
- Implement exponential backoff
- Consider batching reviews
- Monitor x-ratelimit headers

### Authentication Errors
- Verify GITHUB_TOKEN is set
- Check token has repo scope
- Ensure token hasn't expired