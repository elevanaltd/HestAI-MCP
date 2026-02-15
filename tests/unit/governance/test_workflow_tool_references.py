"""Test workflow documentation doesn't reference deprecated MCP tools.

Issue #226: Remove deprecated MCP tool references from OPERATIONAL-WORKFLOW.oct.md
"""

from pathlib import Path

import pytest

# Current HestAI MCP server only provides these 4 tools
VALID_HESTAI_MCP_TOOLS = {
    "mcp__hestai__clock_in",
    "mcp__hestai__clock_out",
    "mcp__hestai__bind",
    "mcp__hestai__submit_review",
}

# Deprecated tools that should NOT appear in workflow documentation
DEPRECATED_HESTAI_MCP_TOOLS = {
    # THINKING_TOOLS (all deprecated)
    "mcp__hestai__planner",
    "mcp__hestai__thinkdeep",
    "mcp__hestai__consensus",
    "mcp__hestai__debug",
    "mcp__hestai__analyze",
    # VALIDATION_TOOLS (all deprecated)
    "mcp__hestai__critical-engineer",
    "mcp__hestai__testguard",
    "mcp__hestai__secaudit",
    # CLI_SPECIALISTS (deprecated)
    "mcp__hestai__clink",
}

# Semantic terms that should NOT appear (case-insensitive)
# These catch references to deprecated concepts without the mcp__ prefix
DEPRECATED_SEMANTIC_TERMS = {
    "TESTGUARD",  # Deprecated tool concept, use TEST_STRATEGY_FIRST instead
}


def _get_workflow_file_paths() -> list[Path]:
    """Get both copies of the workflow document."""
    project_root = Path(__file__).parent.parent.parent.parent
    return [
        project_root
        / "src/hestai_mcp/_bundled_hub/governance/workflow/OPERATIONAL-WORKFLOW.oct.md",
        project_root / ".hestai-sys/governance/workflow/OPERATIONAL-WORKFLOW.oct.md",
    ]


def _check_workflow_for_deprecated_tools(file_path: Path) -> list[str]:
    """Check workflow file for deprecated tool references.

    Args:
        file_path: Path to workflow document

    Returns:
        List of deprecated tools found in the file
    """
    if not file_path.exists():
        pytest.fail(f"Workflow file not found: {file_path}")

    content = file_path.read_text()
    found_deprecated = []

    for deprecated_tool in DEPRECATED_HESTAI_MCP_TOOLS:
        if deprecated_tool in content:
            found_deprecated.append(deprecated_tool)

    return found_deprecated


def _check_workflow_for_deprecated_semantic_terms(file_path: Path) -> list[str]:
    """Check workflow file for deprecated semantic terms.

    Args:
        file_path: Path to workflow document

    Returns:
        List of deprecated semantic terms found in the file
    """
    if not file_path.exists():
        pytest.fail(f"Workflow file not found: {file_path}")

    content = file_path.read_text().upper()  # Case-insensitive search
    found_deprecated = []

    for deprecated_term in DEPRECATED_SEMANTIC_TERMS:
        if deprecated_term.upper() in content:
            found_deprecated.append(deprecated_term)

    return found_deprecated


@pytest.mark.unit
def test_workflow_documents_do_not_reference_deprecated_hestai_tools():
    """Test that workflow documents don't reference deprecated HestAI MCP tools."""
    for file_path in _get_workflow_file_paths():
        deprecated_found = _check_workflow_for_deprecated_tools(file_path)

        assert (
            not deprecated_found
        ), f"Found deprecated tool references in {file_path.name}: {deprecated_found}"


@pytest.mark.unit
def test_both_workflow_copies_are_identical():
    """Test that both copies of the workflow document are identical."""
    workflow_paths = _get_workflow_file_paths()

    # Read both files
    contents = []
    for file_path in workflow_paths:
        if not file_path.exists():
            pytest.fail(f"Workflow file not found: {file_path}")
        contents.append(file_path.read_text())

    # Compare
    assert (
        contents[0] == contents[1]
    ), "Workflow document copies are not identical - they must be kept in sync"


@pytest.mark.unit
def test_workflow_documents_exist():
    """Test that both workflow document copies exist."""
    for file_path in _get_workflow_file_paths():
        assert file_path.exists(), f"Workflow file not found: {file_path}"
        assert file_path.is_file(), f"Path is not a file: {file_path}"


@pytest.mark.unit
def test_workflow_documents_do_not_reference_deprecated_semantic_terms():
    """Test that workflow documents don't reference deprecated semantic terms.

    This catches references to deprecated concepts like TESTGUARD_FIRST
    that don't use the mcp__ prefix.
    """
    for file_path in _get_workflow_file_paths():
        deprecated_found = _check_workflow_for_deprecated_semantic_terms(file_path)

        assert (
            not deprecated_found
        ), f"Found deprecated semantic terms in {file_path.name}: {deprecated_found}"
