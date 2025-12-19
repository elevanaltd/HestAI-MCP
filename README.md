# HestAI-MCP

**MCP Server implementing Dual-Layer Context Architecture for AI agent coordination**

## Architecture

This project implements [ADR-0007 Dual-Layer Context Architecture](docs/adr/adr-0007-dual-layer-context-architecture.md):

- **System Governance** (`.hestai/.sys-runtime/`) - Delivered by MCP server, NOT git committed
- **Project Documentation** (`.hestai/`) - Git committed, single writer (System Steward)

## Why Fresh Start?

This replaces the legacy `hestai-core` worktree+symlink architecture which caused:
- Symlink commit failures ("symbolic link restrictions")
- Agent visibility problems (files invisible to `git ls-files`, can't `@tag`)
- Multi-agent conflicts (no single writer enforcement)
- Conway's Law accumulation (complex architecture impossible to untangle)

## Key Principles

- **NO symlinks** for `.hestai` (direct directory only)
- **OCTAVE format** for all context files
- **Single writer**: System Steward MCP tools only write to `.hestai/`
- **Delivered governance**: `.sys-runtime/` injected by MCP server at startup

## Project Status

**Phase**: Foundation (Phase 0)

See `.hestai/context/PROJECT-CONTEXT.oct` for current status.

## Development Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run quality gates
pytest
mypy .
ruff check .
black --check .
```

## Directory Structure

```
/Volumes/HestAI-MCP/
├── .hestai/                          # Direct directory, NOT symlink
│   ├── context/                      # COMMITTED - OCTAVE context files
│   ├── workflow/                     # COMMITTED - Project governance
│   ├── sessions/
│   │   ├── active/                   # GITIGNORED - Ephemeral
│   │   └── archive/                  # COMMITTED - Durable
│   └── reports/                      # COMMITTED - Audit artifacts
├── src/hestai_mcp/                   # Python source
├── tests/                            # Test suite
├── docs/adr/                         # Architecture decisions
└── pyproject.toml                    # Project configuration
```

## License

MIT
