# MCP Server Setup for document-submit

## Overview

This repository contains a LOCAL MCP server implementation with clockin/clockout tools. The server is implemented in Python at `src/hestai_mcp/mcp/server.py`.

## Installation

### 1. Run the Setup Script

```bash
./setup_mcp_server.sh
```

This script will:
- Create a Python virtual environment (`.venv`)
- Install the hestai-mcp package in development mode
- Install all required dependencies

### 2. Configure Claude Desktop

Add the following to your Claude Desktop configuration:

1. Open Claude Desktop
2. Go to Settings → Developer → Edit Config
3. Add to the `mcpServers` section:

```json
{
  "mcpServers": {
    "document-submit": {
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

### clock_in
Register agent session start and return context paths.
- Creates session directory in `.hestai/sessions/active/`
- Returns OCTAVE context file paths from `.hestai/context/`

**Parameters:**
- `role` (required): Agent role name (e.g., 'implementation-lead')
- `working_dir` (required): Project working directory path
- `focus` (optional): Work focus area (default: 'general')
- `model` (optional): AI model identifier

### clock_out
Archive agent session transcript and extract learnings.
- Compresses session transcript to OCTAVE format
- Archives to `.hestai/sessions/archive/`
- Cleans up active session directory

**Parameters:**
- `session_id` (required): Session ID from clock_in
- `description` (optional): Session summary/description

## File Structure

```
document-submit/
├── src/
│   └── hestai_mcp/
│       ├── mcp/
│       │   ├── server.py          # Main MCP server
│       │   └── tools/
│       │       ├── clock_in.py    # Clock in implementation
│       │       └── clock_out.py   # Clock out implementation
│       └── ...
├── .venv/                          # Python virtual environment
├── .hestai/
│   ├── context/                   # Project context files
│   ├── sessions/
│   │   ├── active/                # Active sessions
│   │   └── archive/               # Archived sessions
│   └── reports/
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
- `mcp__document_submit__clock_in`
- `mcp__document_submit__clock_out`

## Notes

- The server uses stdio transport (standard input/output)
- Sessions are stored locally in `.hestai/sessions/`
- Archive includes both raw JSONL and OCTAVE compressed formats
- Hub injection is planned for Phase 4 (currently commented out)

---
*Last updated: 2025-12-19*
