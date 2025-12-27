# ADR-0082: Claude Code .claude Gitignore + Worktree Hook Symlinks

- **Status**: Implemented
- **Type**: ADR
- **Author**: Claude Code Agent
- **Created**: 2025-12-27
- **Updated**: 2025-12-27
- **GitHub Issue**: [#82](https://github.com/elevanaltd/HestAI-MCP/issues/82)
- **Phase**: B0
- **Supersedes**: (none)
- **Superseded-By**: (none)

## Context

Claude Code stores user-local configuration and runtime state in the `.claude/` directory:

- `.claude/settings.json`: Project-specific hook configurations
- `.claude/hooks/`: Session start hooks, skill activation hooks, state management
- `.claude/commands/`: Project-specific command definitions
- `.claude/skills/`: Project-specific skill library
- `.claude/hooks/state/`: Runtime state (test suggestions, intent analysis, etc.)

This directory is **user-specific and ephemeral**—each developer and each worktree may have different configurations. When using git worktrees:

1. The main repo has a `.claude/` directory with hooks and skills
2. Each worktree initially creates its own `.claude/` directory
3. Worktrees are temporary branches (often feature branches), so `.claude/` gets recreated per-worktree
4. The `.claude/hooks/session_start/` scripts are **critical for setup**—they're referenced in settings.json and run on SessionStart

**The Problem**: If `.claude/` is committed to git, every worktree change pollutes the repository. If it's ignored, worktrees don't have access to the shared `.claude/hooks/` that SessionStart needs.

## Decision

We will:

1. **Gitignore `.claude/` completely** (added to `.gitignore`)
2. **Gitignore `.gemini-clipboard/` completely** (Gemini clipboard cache)
3. **Create `.claude/hooks` symlinks in worktrees** via the global SessionStart hook (`setup-dependencies.sh`)
4. **Symlink to the main repo's `.claude/hooks`** so all worktrees share the same hook implementation

This design treats `.claude/hooks` as a **shared, read-only asset** (like `.hestai` symlinks) while allowing `.claude/settings.json` and `.claude/commands/` to be worktree-specific.

### Implementation Details

The global `~/.claude/hooks/session_start/setup-dependencies.sh` now includes:

```bash
# Restore .claude/hooks for worktrees (Claude Code project-local hooks)
# .claude is gitignored, so worktrees need .claude/hooks from main repo

if [ "$IS_WORKTREE" = true ] && [ -d "$MAIN_REPO/.claude/hooks" ]; then
  # Ensure .claude directory exists in worktree
  mkdir -p "$WORKTREE_DIR/.claude"

  # Remove broken symlink if exists
  if [ -L "$WORKTREE_DIR/.claude/hooks" ]; then
    rm -f "$WORKTREE_DIR/.claude/hooks"
  fi

  # Symlink hooks from main repo (shared across worktrees)
  if [ ! -e "$WORKTREE_DIR/.claude/hooks" ]; then
    ln -sfn "$MAIN_REPO/.claude/hooks" "$WORKTREE_DIR/.claude/hooks"
    echo "[SessionStart] ✓ Restored .claude/hooks symlink from main repo"
  fi
fi
```

This runs **after** the `.hestai` symlink restoration and **before** dependency installation.

## Consequences

### Positive

- **Clean git history**: No ephemeral user state committed to version control
- **Worktree support works seamlessly**: SessionStart hooks work in all worktrees without manual intervention
- **Shared hook definitions**: All developers and worktrees use the same hook code from main repo
- **Disk space efficient**: Hooks are symlinked, not duplicated
- **Consistent with existing patterns**: Uses the same symlink approach as `.hestai` restoration

### Negative

- **Worktree initialization dependency**: If main repo's `.claude/hooks` doesn't exist, worktrees won't have hooks (but this is acceptable—projects without project-local hooks simply won't have them)
- **Manual hook setup required**: Developers using worktrees must have the global `setup-dependencies.sh` hook configured in their `~/.claude/settings.json`

### Neutral

- **Project-specific state is ephemeral**: `.claude/settings.json`, `.claude/commands/`, and `.claude/skills/` are gitignored and worktree-specific (by design, since each project and worktree may have different preferences)

## Migration Path

**For existing worktrees**: The next SessionStart after this change will automatically create the `.claude/hooks` symlink.

**For new worktrees**: Symlinks are created automatically during SessionStart.

**For developers without worktrees**: No change—their single `.claude/` directory works as before.

## Related Documents

- **ADRs**: [ADR-0033: Dual Layer Context Architecture](adr-0033-dual-layer-context-architecture.md)
- **Issues**: [PR #81: Add Claude Code and clipboard cache to gitignore](https://github.com/elevanaltd/HestAI-MCP/pull/81)
- **Global Hook Script**: `~/.claude/hooks/session_start/setup-dependencies.sh` (universal worktree dependency setup)
