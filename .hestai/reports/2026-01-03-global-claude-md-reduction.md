# Global CLAUDE.md Reduction Report

**Date:** 2026-01-03
**Context:** Boris Cherny best practices alignment

## Summary

Reduced global `~/.claude/CLAUDE.md` from 275 lines to 51 lines, aligning with Boris's "keep CLAUDE.md concise" guidance while maintaining HestAI governance through MCP tool injection.

## Rationale

### The Conflict
- **Boris's guidance:** Keep CLAUDE.md concise, every token counts
- **HestAI's approach:** Full governance context for cognitive continuity

### The Resolution
HestAI's MCP tools (`clock_in`, `odyssean_anchor`) already inject governance context dynamically. The global CLAUDE.md was duplicating context that gets loaded anyway:

| Content | Was In CLAUDE.md | Now Loaded Via |
|---------|------------------|----------------|
| North Star immutables | Yes (36 lines) | `clock_in` → context_paths |
| Workflow phases | Yes (20 lines) | North Star Summary (hook) |
| Binding protocol | Yes (36 lines) | `odyssean_anchor` tool |
| Directory placement | Yes (16 lines) | `clock_in` context |
| Tool ecosystem | Yes (23 lines) | MCP tool descriptions |

### What Stays in Global CLAUDE.md

1. **First Contact Guide** (~10 lines) - Tells unbound agents to run `/bind`
2. **Quality Gates** (~15 lines) - Practical commands (Boris-style)
3. **Protection Clause** (~5 lines) - Minimal safety net

### Token Savings

- **Before:** 275 lines loaded on every prompt
- **After:** 51 lines loaded on every prompt
- **Savings:** ~82% reduction in baseline context

## Verification

The governance context is still fully available:
1. `clock_in` returns `context_paths` including North Star
2. SessionStart hook loads North Star Summary
3. `odyssean_anchor` validates full RAPH vector

## Clarification: .claude/rules/ Loading Behavior

**Tested 2026-01-03:** Rules are loaded at **startup**, not lazily.

| Behavior | Expected | Actual |
|----------|----------|--------|
| Rules discovery | Startup | ✓ Startup |
| Token consumption | On file match | ✗ Always loaded |
| `paths:` frontmatter | Lazy loading | Conditional **application** only |

The `paths:` field tells Claude when to **apply** rules, not when to **load** them.
All `.claude/rules/*.md` files consume tokens from session start.

**Implication:** Keep rules concise. Current total: ~1.7k tokens (acceptable).

## Boris's Key Insight: Verification

From Boris's X post (2025): "Probably the most important thing to get great results
out of Claude Code -- give Claude a way to verify its work. If Claude has that
feedback loop, it will 2-3x the quality of the final result."

HestAI alignment:
- Quality gates (lint, typecheck, test) provide verification
- TDD protocol enforces test-first verification
- `odyssean_anchor` validates agent identity

## Additional Boris Practices (from X post)

| Practice | HestAI Status |
|----------|---------------|
| Plan mode first (shift+tab×2) | Supported via /design command |
| Subagents for workflows | ✓ Task() with specialized agents |
| PostToolUse hooks | ✓ SessionStart hooks implemented |
| Shared `.claude/settings.json` | Not yet (local-first approach) |
| Parallel sessions (5+ local) | ✓ Supported via worktrees |

## Related

- Boris's X post: https://x.com/bcherny/status/2007179832300581177
- Anthropic best practices: https://www.anthropic.com/engineering/claude-code-best-practices
- I5 (Odyssean Identity Binding): Agents still undergo full binding ceremony
- ADR-0007: Context delivered via .hestai/ structure
