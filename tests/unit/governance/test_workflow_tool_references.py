"""Test workflow documentation doesn't reference deprecated MCP tools.

Issue #226: Remove deprecated MCP tool references from OPERATIONAL-WORKFLOW.oct.md

This test validates workflow documentation using the governance validators module.
The validators are reusable production code that contributes to test coverage.
"""

from pathlib import Path

import pytest

from hestai_mcp.governance.validators import (
    DEPRECATED_HESTAI_MCP_TOOLS,
    DEPRECATED_SEMANTIC_TERMS,
    VALID_HESTAI_MCP_TOOLS,
    check_workflow_synchronization,
    get_workflow_file_paths,
    validate_no_deprecated_semantic_terms,
    validate_no_deprecated_tools,
    validate_workflow_documents,
)


@pytest.mark.unit
def test_workflow_documents_do_not_reference_deprecated_hestai_tools():
    """Test that workflow documents don't reference deprecated HestAI MCP tools."""
    project_root = Path(__file__).parent.parent.parent.parent
    results = validate_workflow_documents(project_root)

    for file_path, result in results.items():
        assert result["exists"], f"Workflow file not found: {file_path}"
        assert not result[
            "deprecated_tools"
        ], f"Found deprecated tool references in {Path(file_path).name}: {result['deprecated_tools']}"


@pytest.mark.unit
def test_both_workflow_copies_are_identical():
    """Test that both copies of the workflow document are identical."""
    project_root = Path(__file__).parent.parent.parent.parent

    try:
        are_identical = check_workflow_synchronization(project_root)
        assert (
            are_identical
        ), "Workflow document copies are not identical - they must be kept in sync"
    except FileNotFoundError as e:
        pytest.fail(str(e))


@pytest.mark.unit
def test_workflow_documents_exist():
    """Test that both workflow document copies exist."""
    project_root = Path(__file__).parent.parent.parent.parent
    for file_path in get_workflow_file_paths(project_root):
        assert file_path.exists(), f"Workflow file not found: {file_path}"
        assert file_path.is_file(), f"Path is not a file: {file_path}"


@pytest.mark.unit
def test_workflow_documents_do_not_reference_deprecated_semantic_terms():
    """Test that workflow documents don't reference deprecated semantic terms.

    This catches references to deprecated concepts like TESTGUARD_FIRST
    that don't use the mcp__ prefix.
    """
    project_root = Path(__file__).parent.parent.parent.parent
    results = validate_workflow_documents(project_root)

    for file_path, result in results.items():
        assert result["exists"], f"Workflow file not found: {file_path}"
        assert not result[
            "deprecated_terms"
        ], f"Found deprecated semantic terms in {Path(file_path).name}: {result['deprecated_terms']}"


# Additional tests for validator functions themselves


@pytest.mark.unit
def test_validate_no_deprecated_tools_with_clean_content():
    """Test validator returns empty list for clean content."""
    content = "Use mcp__hestai__clock_in and mcp__hestai__bind"
    result = validate_no_deprecated_tools(content)
    assert result == []


@pytest.mark.unit
def test_validate_no_deprecated_tools_finds_violations():
    """Test validator finds deprecated tool references."""
    content = "Use mcp__hestai__planner for planning"
    result = validate_no_deprecated_tools(content)
    assert "mcp__hestai__planner" in result


@pytest.mark.unit
def test_validate_no_deprecated_tools_finds_multiple_violations():
    """Test validator finds multiple deprecated tools."""
    content = "Use mcp__hestai__planner and mcp__hestai__testguard"
    result = validate_no_deprecated_tools(content)
    assert "mcp__hestai__planner" in result
    assert "mcp__hestai__testguard" in result


@pytest.mark.unit
def test_validate_no_deprecated_semantic_terms_with_clean_content():
    """Test semantic validator returns empty list for clean content."""
    content = "Use TEST_STRATEGY_FIRST pattern"
    result = validate_no_deprecated_semantic_terms(content)
    assert result == []


@pytest.mark.unit
def test_validate_no_deprecated_semantic_terms_case_insensitive():
    """Test semantic validator is case-insensitive."""
    for content in ["TESTGUARD_FIRST", "testguard_first", "TestGuard_First"]:
        result = validate_no_deprecated_semantic_terms(content)
        assert "TESTGUARD" in result


@pytest.mark.unit
def test_check_workflow_synchronization_raises_on_missing_file(tmp_path):
    """Test synchronization check raises FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError, match="Workflow file not found"):
        check_workflow_synchronization(tmp_path)


@pytest.mark.unit
def test_get_workflow_file_paths_with_custom_root(tmp_path):
    """Test workflow path getter with custom project root."""
    paths = get_workflow_file_paths(tmp_path)
    assert len(paths) == 2
    assert all(tmp_path in path.parents for path in paths)


@pytest.mark.unit
def test_validate_workflow_documents_returns_structure():
    """Test validate_workflow_documents returns expected structure."""
    project_root = Path(__file__).parent.parent.parent.parent
    results = validate_workflow_documents(project_root)

    assert isinstance(results, dict)
    assert len(results) == 2  # Two workflow copies

    for _file_path, result in results.items():
        assert "exists" in result
        assert "deprecated_tools" in result
        assert "deprecated_terms" in result
        assert isinstance(result["deprecated_tools"], list)
        assert isinstance(result["deprecated_terms"], list)


@pytest.mark.unit
def test_constants_are_exported():
    """Test that constant sets are properly exported."""
    assert isinstance(VALID_HESTAI_MCP_TOOLS, set)
    assert isinstance(DEPRECATED_HESTAI_MCP_TOOLS, set)
    assert isinstance(DEPRECATED_SEMANTIC_TERMS, set)
    assert len(VALID_HESTAI_MCP_TOOLS) > 0
    assert len(DEPRECATED_HESTAI_MCP_TOOLS) > 0
    assert len(DEPRECATED_SEMANTIC_TERMS) > 0
