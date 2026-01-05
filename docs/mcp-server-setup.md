# HestAI MCP Server Setup

## Overview

This repository contains the **HestAI MCP server** - a Model Context Protocol server that provides persistent memory, system governance, and context management for AI agents. The server is implemented in Python at `src/hestai_mcp/mcp/server.py`.

## Installation

### Quick Setup (Automatic Configuration)

```bash
./setup-mcp.sh           # Interactive setup
./setup-mcp.sh --all     # Configure all clients automatically
```

This script supports multiple AI clients:
- **Claude Desktop** - Desktop application
- **Claude Code CLI** - Command-line interface
- **OpenAI Codex CLI** - OpenAI's CLI tool
- **Google Gemini CLI** - Google's CLI tool

Features:
- ✅ **Multi-client support** - Configure any or all AI clients
- ✅ **Automatic platform detection** (macOS, Linux, WSL, Windows)
- ✅ **Smart configuration updates** - merges with existing config
- ✅ **Backup creation** - saves your config before modifications
- ✅ **Interactive menu** - guided setup experience
- ✅ **Worktree-aware** - works correctly in git worktrees
- ✅ **Uninstall option** - clean removal with `--uninstall`

See `./setup-mcp.sh --help` for all options.

### Manual Configuration

#### Step 1: Configure Environment (Required)

**Recommended:** Set `HESTAI_PROJECT_ROOT` in your `.env` file:

```bash
# .env file in your project root
HESTAI_PROJECT_ROOT=/path/to/your/project
```

Copy `.env.example` to `.env` and update the path. The MCP server automatically loads `.env` files.

**Alternative:** Set via MCP client configuration (see Step 2 example with `"env"` section).

> **Why .env?** Simpler setup, version-controlled (when appropriate), and familiar to developers.

#### Step 2: Configure MCP Client

Run `./setup-mcp.sh --show-config` to get copy/paste configuration for your setup.

**With .env file** (recommended - simpler):

```json
{
  "mcpServers": {
    "hestai": {
      "command": "/path/to/HestAI-MCP/.venv/bin/python",
      "args": ["/path/to/HestAI-MCP/src/hestai_mcp/mcp/server.py"]
    }
  }
}
```

**Without .env file** (requires env in client config):

```json
{
  "mcpServers": {
    "hestai": {
      "command": "/path/to/HestAI-MCP/.venv/bin/python",
      "args": ["/path/to/HestAI-MCP/src/hestai_mcp/mcp/server.py"],
      "env": {
        "HESTAI_PROJECT_ROOT": "/path/to/your/project"
      }
    }
  }
}
```

After configuring, restart your AI client to apply changes.

## Available Tools

### Currently Implemented

#### clock_in
Register agent session start and return context paths.
- Creates session directory in `.hestai/sessions/active/`
- Returns OCTAVE context file paths from `.hestai/context/`

**Parameters:**
- `role` (required): Agent role name (e.g., 'implementation-lead')
- `working_dir` (required): Project working directory path
- `focus` (optional): Work focus area (default: 'general')
- `model` (optional): AI model identifier

#### clock_out
Archive agent session transcript and extract learnings.
- Compresses session transcript to OCTAVE format
- Archives to `.hestai/sessions/archive/`
- Cleans up active session directory

**Parameters:**
- `session_id` (required): Session ID from clock_in
- `description` (optional): Session summary/description

### Planned Tools (Phase 3)

#### document_submit
Submit documents to `.hestai/` directory (TODO - not yet implemented).
This tool will provide single-writer access to project documentation.

## File Structure

```
HestAI-MCP/
├── src/
│   └── hestai_mcp/
│       ├── mcp/
│       │   ├── server.py          # Main MCP server
│       │   └── tools/
│       │       ├── clock_in.py    # Clock in implementation
│       │       ├── clock_out.py   # Clock out implementation
│       │       └── (document_submit.py - TODO Phase 3)
│       └── ...
├── .venv/                          # Python virtual environment
├── .hestai/                        # Project documentation (committed)
│   ├── context/                   # Living operational state
│   ├── sessions/                  # Session management
│   │   ├── active/                # Active sessions (gitignored)
│   │   └── archive/               # Archived sessions
│   ├── workflow/                  # Project-specific rules
│   └── reports/                   # Analysis and assessments
├── docs/
│   ├── adr/                       # Architecture Decision Records
│   └── ARCHITECTURE.md            # System architecture overview
└── setup-mcp.sh                   # Setup script (multi-client)
```

## Development

### Running the Server Manually

```bash
source .venv/bin/activate
python -m hestai_mcp.mcp.server
```

### Testing Tools

After configuring Claude Desktop and restarting, the tools will be available as:
- `mcp__hestai_mcp__clock_in`
- `mcp__hestai_mcp__clock_out`
- `mcp__hestai_mcp__document_submit` (when implemented)

## Notes

- The server uses stdio transport (standard input/output)
- Sessions are stored locally in `.hestai/sessions/`
- Archive includes both raw JSONL and OCTAVE compressed formats
- Hub injection is planned for Phase 4 (currently commented out)

---
*Last updated: 2026-01-05*
