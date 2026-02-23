# .hestai/

AI coordination and context management. Does not affect application code.

## Three-Tier Architecture

### Tier 1: `.hestai-sys/` (System Governance)
Read-only. Delivered by the MCP server at runtime. Gitignored.
Contains: constitution, system north star, skills, agent definitions.

### Tier 2: `.hestai/` (Project Governance) -- this directory
Committed to git. Changes via PR only. Read-only at runtime.

- **north-star/** - Project North Star and component North Stars only
- **decisions/** - Architectural Decision Records
- **rules/** - Project-wide standards, methodology guides, and workflow standards
- **schemas/** - Schema definitions

### Tier 3: `.hestai/state/` (Project Working State)
Symlinked to `{main_repo}/.hestai-state/`. Shared across worktrees. Gitignored.
Writable by agents and MCP tools without PR overhead.

- **context/** - PROJECT-CONTEXT, checklist, roadmap, exemplars
- **reports/** - Audit trails and evidence artifacts
- **research/** - Investigation findings
- **sessions/** - Session archives
- **audit/** - Bypass logs and audit trail

## Should I commit this?

The governance files (north-star, decisions, rules, schemas) are committed.
The `state/` symlink and its contents are gitignored and shared across worktrees.

## Can I delete it?

If you're not using HestAI, you can safely remove this folder. Check with your team first.
