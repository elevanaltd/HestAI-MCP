# MCP Server Management

Manage MCP servers for the current project/worktree.

## Usage

```
/mcp-servers [list|disable|enable] [server-name]
```

**Commands:**
- `list` (default) - Show all MCP servers and their status
- `disable <name>` - Disable a server for this path
- `enable <name>` - Re-enable a server for this path

---

## EXECUTION PROTOCOL

When this command is invoked, execute the Node.js script:

### Parse Arguments
```bash
ACTION="${1:-list}"
SERVER="${2:-}"
SCRIPT="$HOME/.claude/bin/mcp-server-manager.mjs"
```

### Execute Command
```bash
node "$SCRIPT" "$ACTION" "$SERVER"
```

### Post-Execution
If disable or enable was executed:
1. Inform user: "Restart Claude session for changes to take effect"
2. Optionally run `/mcp-servers list` to show new state

---

## EXAMPLES

```bash
# List all servers
/mcp-servers
/mcp-servers list

# Disable supabase for current project
/mcp-servers disable supabase

# Re-enable supabase
/mcp-servers enable supabase
```

---

## Default Behavior

**Note:** Claude Code defaults to enabling all servers for new projects/worktrees. To restrict servers:
1. Run `/mcp-servers disable <server-name>` for servers you don't need
2. Changes take effect after restarting the session

This is intentional - all servers are available by default, you selectively disable what you don't need.

## CONTEXT STEWARD INTEGRATION (Future)

The Context Steward could invoke this script during `/load`:
1. Read project's `.hestai/config.yaml` for MCP preferences
2. Auto-enable/disable servers based on project needs
3. Example config:
   ```yaml
   mcp:
     required: [hestai]
     optional: [supabase, smartsuite]
     disabled: [chrome-devtools, repomix]
   ```

This allows project-specific MCP configuration without manual intervention.
