# HestAI MCP Server Setup

## Overview

This repository contains the **HestAI MCP server** - a Model Context Protocol server that provides persistent memory, system governance, and context management for AI agents. The server is implemented in Python at `src/hestai_mcp/mcp/server.py`.

## Installation

### Quick Setup (Automatic Configuration)

```bash
./setup_mcp_server.sh
```

This enhanced script will:
- Create a Python virtual environment (`.venv`)
- Install the hestai-mcp package in development mode
- Install all required dependencies
- **Automatically update your Claude Desktop configuration** (with your permission)
- Create a backup of your existing config before making changes

The script features:
- ✅ **Automatic platform detection** (macOS, Linux, WSL, Windows)
- ✅ **Smart configuration updates** - merges with existing config
- ✅ **Backup creation** - saves your config before modifications
- ✅ **Colored output** - clear success/warning/error messages
- ✅ **Cross-platform support** - works on all major platforms

### Manual Configuration (if automatic setup is skipped)

If you choose to skip automatic configuration:

```json
{
  "mcpServers": {
    "hestai-mcp": {
      "command": "/Volumes/HestAI-MCP/worktrees/document-submit/.venv/bin/python",
      "args": [
        "-m",
        "hestai_mcp.mcp.server"
      ]
    }
  }
}
```

4. Restart Claude Desktop

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
└── setup_mcp_server.sh            # Setup script
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
*Last updated: 2025-12-19*
