# HestAI-MCP

**Model Context Protocol server implementing dual-layer context architecture for AI agent coordination**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Overview

HestAI-MCP is a Model Context Protocol (MCP) server that solves the **cognitive continuity crisis** in AI-assisted development. It provides persistent memory and context management for AI agents working on long-running projects.

### The Solution: "Installed Governance"

HestAI-MCP treats system governance as **installed software**:
- **No copy-pasting** rules between projects
- **No drifting** standards
- **Instant updates** when you upgrade the MCP server

## Architecture

```
YOUR PROJECT (using HestAI)
├── .hestai-sys/              # SYSTEM (read-only, injected by MCP)
│   ├── governance/           # Rules, North Stars
│   ├── agents/               # Agent templates
│   └── library/              # Reference materials (OCTAVE guide, etc)
│
├── .hestai/                  # PRODUCT (your project's context)
│   ├── context/              # Living state (PROJECT-CONTEXT, etc)
│   ├── sessions/             # Session artifacts
│   ├── workflow/             # Product North Star, methodology
│   └── reports/              # Evidence archives
│
├── docs/                     # Developer documentation (ADRs, guides)
└── src/                      # Your code
```

### Key Principle: Single Writer

**All documentation writes go through MCP tools.** No direct file creation.

```
Agent → MCP Tool (document_submit/context_update) → System Steward → Files
```

This prevents:
- Multi-agent conflicts
- Governance drift
- Inconsistent documentation

### The Two Layers

| Layer | Location | Delivery | Mutability |
|-------|----------|----------|------------|
| **System** | `hub/` → `.hestai-sys/` | MCP injection | Read-only |
| **Product** | `.hestai/` | Direct files | Via MCP tools only |

For detailed architecture, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## MCP Tools

| Tool | Purpose |
|------|---------|
| `clock_in` | Start session, load context |
| `clock_out` | End session, compress to OCTAVE |
| `odyssean_anchor` | Validate agent identity |
| `document_submit` | Route docs to correct location |
| `context_update` | Update context with conflict resolution |

## Documentation Format

### When to use OCTAVE (`.oct.md`)
- Agent constitutions
- Governance rules
- North Stars
- Context files (PROJECT-CONTEXT, etc)
- Session archives

### When to use Markdown (`.md`)
- Developer guides
- ADRs
- READMEs
- Setup instructions

**Decision:** Primary audience AI agents? → `.oct.md`. Human developers? → `.md`

## Quick Start

```bash
# Clone and install
git clone https://github.com/your-org/hestai-mcp.git
cd hestai-mcp
pip install -e ".[dev]"

# Run tests
pytest

# Check quality
ruff check . && mypy src/ && black --check .
```

### MCP Configuration

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

## Governance Rules

Documentation placement is governed by rules in `hub/governance/rules/`:

| Rule | Document | Purpose |
|------|----------|---------|
| **Visibility** | `visibility-rules.oct.md` | Where docs belong (product placement) |
| **Hub Authoring** | `hub-authoring-rules.oct.md` | What goes in system (hub/) |
| **Naming** | `naming-standard.oct.md` | How to name files |
| **Format** | In visibility-rules | When to use OCTAVE vs Markdown |

## Development Status

- ✅ Phase 0-2: Foundation, porting, MCP server
- ✅ Phase 2.5: Hub architecture, bundled governance
- 🚧 Phase 3: Single writer tools (document_submit, context_update)
- 🚧 Phase 4: Governance injection at runtime

## Related

- [OCTAVE](https://github.com/your-org/octave) - Compression format specification
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detailed architecture

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

"Odyssean Anchor" is a registered trademark of Shaun Buswell - see [docs/trademarks.md](docs/trademarks.md) for usage guidelines.
