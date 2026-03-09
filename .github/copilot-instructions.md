# Copilot Code Review Instructions

## Project Context

HestAI-MCP is a Python MCP server providing context management tools for Claude Code.
Stack: Python 3.11+, Pydantic, MCP protocol. Full type hints required.

## Review Focus

When reviewing pull requests, prioritise these areas in order:

1. **Security**: Input validation, injection risks, secrets exposure, OWASP Top 10
2. **Correctness**: Logic errors, edge cases, off-by-one, null/None handling
3. **Type Safety**: Missing or incorrect type hints, Pydantic schema mismatches
4. **Error Handling**: Bare excepts, swallowed errors, missing error paths
5. **Architecture**: Coupling, abstraction leaks, violation of existing patterns

## Code Standards

- Line length: 100 chars
- Linting: ruff + black
- Type checking: mypy (strict)
- All public functions require docstrings
- Tests in `tests/` mirroring `src/` structure

## What NOT to Flag

- Do not flag OCTAVE format files (*.oct.md) for markdown issues — these use a
  domain-specific notation that is intentionally non-standard markdown.
- Do not suggest adding comments to self-explanatory code.
- Do not flag conventional commit message format in PR titles.
- Do not suggest restructuring test files — they mirror src/ by convention.

## Governance Files

Files under `.hestai-sys/` and `.hestai/` are governance/configuration files.
Review these for structural correctness only, not code style.

## Severity Guide

- **Critical**: Security vulnerabilities, data loss risks, broken functionality
- **Major**: Logic errors, missing error handling, type safety violations
- **Minor**: Style inconsistencies, naming suggestions, minor improvements
- **Nit**: Formatting, optional improvements — keep these minimal
