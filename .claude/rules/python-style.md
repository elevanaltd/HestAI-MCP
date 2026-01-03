---
description: Python code style for HestAI MCP
globs:
  - "src/**/*.py"
  - "scripts/**/*.py"
---

# Python Style Rules

## Type Hints

- All functions require type hints (enforced by mypy)
- Use `from __future__ import annotations` for forward refs
- Prefer `list`, `dict`, `set` over `List`, `Dict`, `Set`

## Imports

- Use absolute imports from `hestai_mcp`
- ruff handles isort-style ordering
- Group: stdlib, third-party, local

## Error Handling

- Raise specific exceptions, not generic `Exception`
- Document exceptions in docstrings
- Use `from __future__ import annotations` for forward refs

## Docstrings

- Google-style docstrings
- Required for public functions/classes
- Include Args, Returns, Raises sections

## Line Length

- 100 characters max
- Enforced by black and ruff
