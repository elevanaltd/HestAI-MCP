# HestAI MCP Server

Python MCP server providing context management tools for Claude Code.

## Quick Commands

```bash
# Quality gates (run before committing)
python -m ruff check src tests scripts
python -m black --check src tests scripts
python -m mypy src
python -m pytest

# Fix formatting
python -m black src tests scripts
python -m ruff check --fix src tests scripts

# Run specific test markers
python -m pytest -m smoke       # Fast sanity checks
python -m pytest -m behavior    # Behavioral tests (NOW)
python -m pytest -m contract    # Contract tests (SOON)
```

## Core Files

- `src/hestai_mcp/mcp/server.py` - MCP server entry point
- `src/hestai_mcp/mcp/tools/` - MCP tool implementations (clock_in, clock_out, bind)
- `src/hestai_mcp/ai/` - AI client and provider abstractions
- `src/hestai_mcp/schemas/` - Pydantic schemas
- `tests/` - Test suite mirroring src/ structure
- `.hestai/workflow/` - North Star and workflow docs
- `docs/ARCHITECTURE.md` - System architecture reference

## Testing

- **pytest markers**: smoke, unit, behavior, contract, integration
- **Coverage**: 89% threshold enforced in CI
- Tests live in `tests/` mirroring `src/` structure

## Code Style

- Line length: 100 chars
- Python 3.11+ with full type hints
- Use `ruff` for linting, `black` for formatting
- All public functions need docstrings

## Git Conventions

- Branch from `main`
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- PRs require CI green
