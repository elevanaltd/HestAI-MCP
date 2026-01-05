"""Pytest configuration.

Ensures `src/` is on sys.path so tests can import `hestai_mcp` without
requiring an editable install.

This keeps local TDD loops lightweight while preserving packaging behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    # Allow tests to import both the Python package (src/) and repository utilities
    # (e.g., scripts/ used by CI validation tests) without requiring an editable install.
    sys.path.insert(0, str(repo_root))

    src = repo_root / "src"
    sys.path.insert(0, str(src))
