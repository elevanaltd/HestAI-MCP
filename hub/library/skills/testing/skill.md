---
name: testing
description: Testing patterns and conventions for HestAI MCP including pytest markers, TDD protocol, and coverage requirements
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
triggers:
  - pytest
  - test markers
  - TDD
  - test driven
  - unit tests
  - behavior tests
  - integration tests
  - test coverage
  - conftest
  - async testing
  - pytest-asyncio
---

# Testing Rules

## Test Markers (Progressive Testing Model)

- `@pytest.mark.smoke` - Fast import/sanity tests (< 1s)
- `@pytest.mark.behavior` - NOW: Real behavioral tests
- `@pytest.mark.contract` - SOON: Integration contract tests
- `@pytest.mark.integration` - LATER: Full integration tests

## Test Structure

```
tests/
  unit/           # Component-level tests
  behavior/       # Behavioral specification tests
  contracts/      # External integration contracts
  conftest.py     # Shared fixtures
```

## TDD Protocol

1. RED: Write failing test first
2. GREEN: Minimal implementation to pass
3. REFACTOR: Improve while green
4. Commit sequence: `test:` -> `feat:` -> `refactor:`

## Coverage

- 89% threshold in CI
- Focus on behavioral coverage, not line coverage
- Mock external dependencies, not internal modules

## Async Testing

- `asyncio_mode = "auto"` in pytest config
- Use `pytest-asyncio` for async tests
