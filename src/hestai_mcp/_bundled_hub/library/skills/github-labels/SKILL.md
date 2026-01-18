---
name: github-labels
description: Reference for valid GitHub labels in HestAI-MCP repository to prevent label errors
allowed-tools: [Bash]
trigger-patterns:
  - "gh issue create"
  - "create.*issue"
  - "github.*label"
  - "what labels"
  - "valid labels"
auto-activation: true
---

# GitHub Labels Skill

## Purpose

Prevents "label not found" errors when creating GitHub issues by providing agents with the current valid label taxonomy.

## Valid Labels (Current Repository)

### Standard Labels
- `bug` - Something isn't working
- `documentation` - Improvements or additions to documentation
- `duplicate` - This issue or pull request already exists
- `enhancement` - New feature or request
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `invalid` - This doesn't seem right
- `question` - Further information is requested
- `wontfix` - This will not be worked on

### Document Types
- `adr` - Architecture Decision Record
- `rfc` - Request for Comments (deprecated per ADR-0060)

### Priority Levels
- `priority:p0-critical` - Blocking production or critical path
- `priority:p1-high` - Important, should be addressed soon
- `priority:p2-medium` - Normal priority
- `priority:p3-low` - Nice to have

### Development Phases
- `phase:b1` - B1: Foundation phase
- `phase:b2` - B2: Features phase
- `phase:future` - Future consideration

### Area Tags
- `area:mcp-tools` - MCP tool implementation
- `area:governance` - Governance system
- `area:ci-cd` - CI/CD pipeline
- `area:agents` - Agent system

### Status Tags
- `status:blocked` - Blocked by dependencies
- `status:needs-discussion` - Needs team discussion
- `status:implementation-pending` - Approved, waiting for implementation
- `status:draft` - Draft/work in progress
- `obsolete` - No longer relevant

### Milestone Tags
- `milestone:b1-foundation` - B1 milestone
- `milestone:b2-features` - B2 milestone
- `milestone:b3-integration` - B3 milestone

### Special Tags
- `epic` - Epic tracking issue
- `octave-integration` - OCTAVE integration work

## Usage Pattern

**Before creating a GitHub issue:**

```bash
# 1. Verify current labels (labels can change over time)
gh label list --json name --jq '.[].name'

# 2. Create issue with ONLY valid labels
gh issue create \
  --title "Issue Title" \
  --label "enhancement,priority:p2-medium,phase:b1" \
  --body "Issue description"
```

## Common Mistakes to Avoid

❌ **Don't use:**
- `p0`, `p1`, `p2`, `p3` (missing `priority:` prefix)
- `b1`, `b2` (missing `phase:` prefix)
- `mcp-tools`, `governance` (missing `area:` prefix)
- Custom labels that don't exist

✅ **Do use:**
- `priority:p0-critical`, `priority:p1-high`
- `phase:b1`, `phase:b2`
- `area:mcp-tools`, `area:governance`
- Exact label names from the valid list above (including spaces when present, e.g., `good first issue`)

## Auto-Validation

The `~/.claude/hooks/pre_tool_use/validate-gh-labels.sh` hook automatically:
1. Intercepts Bash tool before `gh issue create` executes
2. Validates labels against current repository labels (cached 5min)
3. Removes invalid labels
4. Warns you about changes

If you see a warning, check this skill for the correct label names.

## Dynamic Label Lookup

To get the current label list programmatically:

```bash
gh label list --json name,description --jq '.[] | "\(.name): \(.description)"'
```

## Integration with Hooks

This skill works in tandem with the label validation hook to:
- **Prevent errors** before they happen
- **Save time** by avoiding re-writes
- **Educate agents** about valid taxonomy

## Escalation

If you need a new label that doesn't exist:
1. Discuss with the team first
2. Create label via: `gh label create <name> --description "..." --color <hex>`
3. Update this skill documentation
