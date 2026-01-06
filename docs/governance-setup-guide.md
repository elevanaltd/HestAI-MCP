# HestAI Governance Setup Guide

## Overview

HestAI MCP Server provides an optional system governance layer (`.hestai-sys/`) that contains read-only configuration and rules for AI agents. This governance layer is **opt-in** to respect project autonomy while providing powerful context management for projects that need it.

## Opt-In Methods

### Method 1: Environment Variable (Recommended for New Projects)

Add to your project's `.env` file:

```bash
# Enable HestAI system governance
HESTAI_GOVERNANCE_ENABLED=true
```

This tells the MCP server that your project wants the governance layer. The server will:
1. Create `.hestai-sys/` directory with governance files
2. Automatically add `.hestai-sys/` to your `.gitignore`
3. Keep governance updated to the latest bundled version

### Method 2: Existing .hestai Directory (Automatic for Existing Projects)

If your project already has a `.hestai/` directory, governance is automatically enabled. This ensures backward compatibility - existing HestAI projects continue to work without changes.

## What Gets Added

When governance is enabled, the following structure is created:

```
your-project/
├── .hestai-sys/           # System governance (read-only, not committed)
│   ├── governance/        # Rules and standards
│   ├── agents/           # Agent definitions
│   ├── library/          # Shared resources
│   ├── templates/        # Project templates
│   └── .version          # Version marker
├── .hestai/              # Your project context (committed)
│   ├── workflow/         # Project workflows
│   ├── context/          # Project-specific context
│   └── sessions/         # Session data
└── .gitignore           # Updated automatically
```

## Gitignore Management

The MCP server automatically manages `.gitignore` entries:

1. **Automatic Addition**: When governance is enabled, `.hestai-sys/` is added to `.gitignore`
2. **Safe Appending**: Existing `.gitignore` content is preserved
3. **Idempotent**: Won't duplicate entries if already present

Example `.gitignore` entry added:

```gitignore
# HestAI system governance (auto-added, not committed)
.hestai-sys/
```

## When Governance is NOT Injected

The server will skip governance injection when:

1. **No opt-in**: Neither `.env` variable nor `.hestai/` directory exists
2. **Not a project root**: Directory lacks `.git` or `.hestai` markers
3. **Explicit environment control**: `HESTAI_PROJECT_ROOT` points to a non-project directory

## Security Considerations

- `.hestai-sys/` is **read-only** - agents cannot modify governance files
- Governance is **never committed** to version control
- Each developer gets fresh governance from the MCP server package
- Version checking ensures governance stays up-to-date

## Migration Guide

### For New Projects

1. Add `HESTAI_GOVERNANCE_ENABLED=true` to `.env`
2. Start your MCP server or use HestAI tools
3. Governance will be automatically set up

### For Existing Projects

No action needed! If you have `.hestai/` already, governance continues to work.

### For Projects Without Git

If your project doesn't use Git:
1. Create a `.hestai/` directory: `mkdir .hestai`
2. This signals that your project uses HestAI
3. Governance will be enabled automatically

## Troubleshooting

### Governance Not Appearing

Check:
- Is `HESTAI_GOVERNANCE_ENABLED=true` in `.env`?
- Does `.hestai/` directory exist?
- Is this a valid project root (has `.git` or `.hestai`)?

### Wrong Directory Getting Governance

Set explicit project root:
```bash
export HESTAI_PROJECT_ROOT=/path/to/your/project
```

### Governance Version Outdated

The MCP server automatically updates governance when:
- Server starts and versions don't match
- Required directories are missing

## Best Practices

1. **Commit `.env.example`** with `HESTAI_GOVERNANCE_ENABLED=true` as documentation
2. **Never commit `.hestai-sys/`** - it's auto-generated
3. **Do commit `.hestai/`** - it's your project's context
4. **Use worktrees** - governance works seamlessly across Git worktrees

## Related Documentation

- [ADR-0007: Direct .hestai Directory Access](../docs/adr/adr-0007-direct-hestai-directory.md)
- [Security Model: .hestai-sys Governance Protection](../docs/hestai-sys-security-model.md)
- [ADR-0082: Claude Code Gitignore + Worktree Symlinks](../docs/adr/adr-0082-claude-code-gitignore-worktree-symlinks.md)
