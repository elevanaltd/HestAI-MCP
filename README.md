# HestAI-MCP

**Model Context Protocol server implementing dual-layer context architecture for AI agent coordination**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Overview

HestAI-MCP is a Model Context Protocol (MCP) server that solves the **cognitive continuity crisis** in AI-assisted development. It provides persistent memory and context management for AI agents working on long-running projects that require months of accumulated knowledge.

### The Solution: "Installed Governance"

HestAI-MCP treats system governance (rules, agent definitions, workflows) as **installed software**.
*   **No more copy-pasting** rules between projects.
*   **No more drifting** standards.
*   **Instant updates** when you upgrade the MCP server.

It implements a **Dual-Layer Context Architecture** (see [Architecture](docs/ARCHITECTURE.md)):
1.  **System Governance** (`.hestai-sys/`): Injected at runtime, read-only.
2.  **Project Documentation** (`.hestai/`): Living project context, committed to git.

## Architecture

For a deep dive into the system design, including diagrams and decision records, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

### Core Concepts

*   **Dual-Layer Context**: Separating immutable system rules from living project state.
*   **Orchestra Map**: Tracking dependencies between Concepts (specs) and Code.
*   **Odyssean Anchor**: Verified identity binding for agents.
*   **Single Writer**: All context writes go through the System Steward to prevent conflicts.

## Features

- ✅ **Clock In/Out**: Session management with context preservation
- ✅ **OCTAVE Format**: Compressed, structured documentation (5-10x reduction)
- ✅ **Single Writer Pattern**: Prevents multi-agent conflicts
- ✅ **Bundled Hub**: System governance included in package
- ✅ **No Symlinks**: Direct files for full agent visibility
- 🚧 **Document Submit**: Route documents to correct locations (Phase 3)
- 🚧 **Context Update**: AI-driven conflict resolution (Phase 3)
- 🚧 **Governance Injection**: Runtime delivery of system rules (Phase 4)

## Installation

### Prerequisites

- Python 3.11+
- Git
- MCP-compatible AI environment (Claude Desktop, Continue, etc.)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/hestai-mcp.git
cd hestai-mcp

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Check code quality
ruff check .
mypy src/
black --check .
```

### MCP Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "hestai": {
      "command": "python",
      "args": ["-m", "hestai_mcp.mcp.server"],
      "env": {
        "HESTAI_PROJECT_ROOT": "/path/to/your/project"
      }
    }
  }
}
```

## Development Roadmap

### Current Status: MVP Achieved (Phase 2.5 Complete)

- ✅ **Phase 0**: Foundation - Directory structure, git setup
- ✅ **Phase 1**: Code Porting - 2541 lines from hestai-core
- ✅ **Phase 2**: MCP Server - Basic server with clock tools
- ✅ **Phase 2.5**: Hub Architecture - Bundled governance files
- 🚧 **Phase 3**: Single Writer - document_submit, context_update tools
- 🚧 **Phase 4**: Governance Delivery - Runtime injection of system rules

### Quality Metrics

- **Tests**: 58 passing (62% coverage)
- **Lines**: 3,823 total (2,541 ported + 1,282 new)
- **Linting**: Ruff 0 errors, Black formatted
- **Type Checking**: MyPy 0 errors

## OCTAVE Format

All project documentation uses OCTAVE format for compression and structure:

```octave
===PROJECT_CONTEXT===
META:
  NAME::"Project Dashboard"
  VERSION::"1.0.0"

PHASE::BUILD[B2_implementation]
STATUS::tests_passing[58/58]

ACTIVE_WORK::[
  single_writer::implementing,
  governance_delivery::pending
]
===END===
```

Benefits:
- 5-10x compression vs markdown
- Machine-parseable structure
- Semantic density through patterns
- Human-readable despite compression

## Why This Replaces hestai-core

The legacy `hestai-core` worktree+symlink architecture caused:
- **Symlink commit failures**: "symbolic link restrictions" errors
- **Agent visibility problems**: Files invisible to `git ls-files`, can't `@tag`
- **Multi-agent conflicts**: No single writer enforcement
- **Conway's Law accumulation**: Complex architecture impossible to untangle

This fresh start implements the lessons learned without the architectural debt.

## Contributing

This project uses HestAI methodology:
1. Test-first development (TDD)
2. OCTAVE documentation format
3. Single writer pattern for `.hestai/`
4. Phase-gated progression

See `.hestai/context/project-checklist.oct.md` for current tasks.

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

## Related Projects

- [hestai-core](https://github.com/your-org/hestai-core) - Original implementation (being migrated from)
- [HestAI Hub](https://github.com/your-org/hestai-hub) - System governance and methodology
- [OCTAVE](https://github.com/your-org/octave) - Compression format specification

## License

MIT - See LICENSE file for details

## Acknowledgments

Built with the HestAI methodology for AI-assisted development with integrated governance.
