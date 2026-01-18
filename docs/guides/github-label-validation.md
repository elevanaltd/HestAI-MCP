# GitHub Label Validation System

## Problem

Agents frequently waste time when creating GitHub issues with invalid labels. The `gh issue create` command fails with "label not found" errors, forcing agents to:
1. Re-analyze the error
2. Identify which labels are invalid
3. Re-write the entire issue creation command
4. Retry the operation

This is a significant processing waste, especially for complex issues with multiple labels.

## Solution

A **two-layer defense system** that combines proactive validation with educational resources:

### Layer 1: Pre-Submit Hook (Automatic Validation)

**File:** `.claude/hooks/user_prompt_submit/validate-gh-labels.ts`

**How it works:**
1. Intercepts all user prompts before execution
2. Detects `gh issue create` commands with `--label` flags
3. Fetches valid labels from the repository (cached for 5 minutes)
4. Compares requested labels against valid labels
5. Automatically removes invalid labels
6. Warns the agent about changes made

**Example:**

```bash
# Agent attempts:
gh issue create --title "Fix bug" --label "invalid-label,enhancement,p1" --body "..."

# Hook automatically modifies to:
gh issue create --title "Fix bug" --label "enhancement" --body "..."

# Agent sees warning:
⚠️  GitHub Label Validation:
   Invalid labels removed: invalid-label, p1
   Valid labels kept: enhancement

💡 Tip: Use the "github-labels" skill to see all valid labels.
```

**Key Features:**
- **Non-blocking:** Falls through on any errors to avoid blocking legitimate work
- **Caching:** Reduces API calls by caching valid labels for 5 minutes
- **Educational:** Provides helpful warnings and tips
- **Safe:** Preserves all other command arguments

### Layer 2: GitHub Labels Skill (Reference Documentation)

**File:** `.hestai-sys/library/skills/github-labels/SKILL.md`

**How it works:**
1. Auto-activates when agents mention GitHub issues or labels
2. Provides comprehensive reference of all valid labels
3. Documents label taxonomy and naming conventions
4. Includes usage examples and common mistakes

**Categories Covered:**
- Standard labels (bug, enhancement, documentation)
- Document types (adr, rfc)
- Priority levels (priority:p0-critical, priority:p1-high, etc.)
- Development phases (phase:b1, phase:b2, etc.)
- Area tags (area:mcp-tools, area:governance, etc.)
- Status tags (status:blocked, status:needs-discussion, etc.)
- Milestones (milestone:b1-foundation, etc.)

**Trigger Patterns:**
- "gh issue create"
- "create.*issue"
- "github.*label"
- "what labels"
- "valid labels"

## Benefits

1. **Eliminates Label Errors:** Hook prevents invalid labels from reaching GitHub
2. **Saves Processing Time:** No need to retry failed issue creation
3. **Educational:** Agents learn correct label taxonomy over time
4. **Low Maintenance:** Labels are fetched dynamically, no manual updates needed
5. **Non-Intrusive:** Works silently in the background, only warns when needed

## Usage for Agents

### Recommended Workflow

1. **When creating issues, trust the hook:**
   ```bash
   # Just use labels as you normally would
   gh issue create \
     --title "Add new feature" \
     --label "enhancement,priority:p1-high,area:mcp-tools" \
     --body "Description"
   ```

2. **If you see a warning, reference the skill:**
   - The hook will tell you which labels were removed
   - Use the `github-labels` skill to find the correct label names

3. **For new label types, verify first:**
   ```bash
   # Check if a label exists before using it
   gh label list --json name --jq '.[].name' | grep "my-label"
   ```

### Common Corrections

| ❌ Invalid | ✅ Valid |
|-----------|---------|
| `p0`, `p1`, `p2` | `priority:p0-critical`, `priority:p1-high`, `priority:p2-medium` |
| `b1`, `b2` | `phase:b1`, `phase:b2` |
| `mcp-tools` | `area:mcp-tools` |
| `blocked` | `status:blocked` |

## Testing

Test the hook manually:

```bash
cd .claude/hooks

# Test with invalid labels
echo '{"text":"gh issue create --title \"Test\" --label \"invalid-label,enhancement\"","conversationId":"test"}' \
  | npx tsx user_prompt_submit/validate-gh-labels.ts

# Expected output: JSON with modified text and warning
```

## Maintenance

### Adding New Labels

When new labels are added to the repository:

1. Create the label in GitHub:
   ```bash
   gh label create "new-label" --description "Description" --color "hex-color"
   ```

2. The hook automatically picks it up (within 5 minutes due to cache)

3. Update the skill documentation:
   - Edit `.hestai-sys/library/skills/github-labels/SKILL.md`
   - Add the new label to the appropriate category

### Monitoring

Check hook execution logs (if available) to see:
- How often invalid labels are caught
- Which labels are most commonly misused
- Whether the skill is effectively educating agents

## Future Enhancements

Potential improvements:

1. **Fuzzy Matching:** Suggest closest valid label for invalid ones (e.g., `p1` → `priority:p1-high`)
2. **Label Categories:** Auto-suggest missing required categories
3. **Historical Analysis:** Track which labels are most error-prone
4. **Smart Defaults:** Auto-apply common label combinations for certain issue types

## Implementation Details

### Hook Architecture

```typescript
// High-level flow:
1. Parse stdin for HookContext
2. Check if text contains "gh issue create" with labels
3. Extract labels using regex
4. Fetch valid labels (with caching)
5. Filter invalid labels
6. Rebuild command with only valid labels
7. Output modified text + warning
```

### Error Handling

The hook is designed to **never block** legitimate work:
- If label fetching fails → skip validation
- If parsing fails → pass through original text
- If any unexpected error → pass through original text

This ensures the hook enhances workflow without becoming a bottleneck.

## Related Documentation

- [Claude Code Hooks Documentation](https://docs.claude.com/claude-code/hooks)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [HestAI Skills System](.hestai-sys/library/skills/README.md)
