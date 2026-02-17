# HestAI MCP Server

Python MCP server providing context management tools for Claude Code.

## Quick Commands

**Always use `.venv/bin/python` — the system `python` does not have project packages.**
The `.venv` is created by the session startup hook (`uv sync --all-extras`).

```bash
# Quality gates (run before committing)
.venv/bin/python -m ruff check src tests scripts
.venv/bin/python -m black --check src tests scripts
.venv/bin/python -m mypy src
.venv/bin/python -m pytest

# Fix formatting
.venv/bin/python -m black src tests scripts
.venv/bin/python -m ruff check --fix src tests scripts

# Run specific test markers
.venv/bin/python -m pytest -m smoke       # Fast sanity checks
.venv/bin/python -m pytest -m behavior    # Behavioral tests (NOW)
.venv/bin/python -m pytest -m contract    # Contract tests (SOON)
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
