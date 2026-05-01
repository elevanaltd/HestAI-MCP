"""Tests for soft-deprecation reconciliation in governance/validators.py (issue #400).

Per ADR-0353 and the deactivation gate, mcp__hestai__{clock_in, clock_out,
submit_review} are soft-deprecated:
  - registered (still visible to MCP clients)
  - default-OFF (return deprecation payload)
  - rollback restorable (env-var=1)
  - replacement: mcp__hestai-context__*

Governance reconciliation:
  - VALID_HESTAI_MCP_TOOLS now contains only mcp__hestai__bind
  - SOFT_DEPRECATED_HESTAI_MCP_TOOLS is a NEW set with the three legacy names
  - DEPRECATED_HESTAI_MCP_TOOLS (hard-deprecated, must not appear) unchanged
  - validate_no_deprecated_tools(...) does NOT flag soft-deprecated names
    (they remain referenceable in workflow docs during the transition)
"""

from __future__ import annotations

import pytest

from hestai_mcp.governance.validators import (
    DEPRECATED_HESTAI_MCP_TOOLS,
    SOFT_DEPRECATED_HESTAI_MCP_TOOLS,
    VALID_HESTAI_MCP_TOOLS,
    validate_no_deprecated_tools,
)


@pytest.mark.unit
def test_valid_set_only_contains_bind() -> None:
    assert {"mcp__hestai__bind"} == VALID_HESTAI_MCP_TOOLS


@pytest.mark.unit
def test_soft_deprecated_contains_three_legacy_tools() -> None:
    assert {
        "mcp__hestai__clock_in",
        "mcp__hestai__clock_out",
        "mcp__hestai__submit_review",
    } == SOFT_DEPRECATED_HESTAI_MCP_TOOLS


@pytest.mark.unit
def test_soft_and_hard_deprecated_are_disjoint() -> None:
    assert SOFT_DEPRECATED_HESTAI_MCP_TOOLS.isdisjoint(DEPRECATED_HESTAI_MCP_TOOLS)


@pytest.mark.unit
def test_soft_and_valid_are_disjoint() -> None:
    assert SOFT_DEPRECATED_HESTAI_MCP_TOOLS.isdisjoint(VALID_HESTAI_MCP_TOOLS)


@pytest.mark.unit
def test_validate_no_deprecated_tools_does_not_flag_soft_deprecated() -> None:
    """Soft-deprecated names remain referenceable; only hard-deprecated trip the validator."""
    for name in SOFT_DEPRECATED_HESTAI_MCP_TOOLS:
        content = f"Some workflow text mentioning {name}"
        assert validate_no_deprecated_tools(content) == []


@pytest.mark.unit
def test_validate_no_deprecated_tools_still_flags_hard_deprecated() -> None:
    content = "Use mcp__hestai__planner for planning"
    result = validate_no_deprecated_tools(content)
    assert "mcp__hestai__planner" in result
