"""Workflow documentation validators for HestAI MCP governance.

This module provides validation functions to ensure workflow documentation
maintains quality standards and doesn't reference deprecated tools or concepts.

Issue #226: Remove deprecated MCP tool references from OPERATIONAL-WORKFLOW.oct.md
"""

from pathlib import Path
from typing import TypedDict


class ValidationResult(TypedDict):
    """Result of validating a workflow document."""

    deprecated_tools: list[str]
    deprecated_terms: list[str]
    exists: bool


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


def get_workflow_file_paths(project_root: Path | None = None) -> list[Path]:
    """Get the bundled workflow document path.

    Note: Only returns the bundled version since .hestai-sys/ is gitignored
    and only exists at runtime. CI environments don't have the runtime copy.

    Args:
        project_root: Root directory of the project. If None, inferred from this file's location.

    Returns:
        List containing path to the bundled workflow document (source of truth).
    """
    if project_root is None:
        # Infer project root from this file's location
        # This file is in src/hestai_mcp/governance/validators.py
        project_root = Path(__file__).parent.parent.parent.parent

    return [
        project_root
        / "src/hestai_mcp/_bundled_hub/governance/workflow/OPERATIONAL-WORKFLOW.oct.md",
    ]


def validate_no_deprecated_tools(content: str) -> list[str]:
    """Validate content doesn't contain deprecated tool references.

    Args:
        content: Text content to validate.

    Returns:
        List of deprecated tool references found. Empty list if validation passes.

    Example:
        >>> content = "Use mcp__hestai__planner for planning"
        >>> validate_no_deprecated_tools(content)
        ['mcp__hestai__planner']
    """
    found_deprecated = []

    for deprecated_tool in DEPRECATED_HESTAI_MCP_TOOLS:
        if deprecated_tool in content:
            found_deprecated.append(deprecated_tool)

    return found_deprecated


def validate_no_deprecated_semantic_terms(content: str) -> list[str]:
    """Validate content doesn't contain deprecated semantic terms.

    Performs case-insensitive search for deprecated concept references.

    Args:
        content: Text content to validate.

    Returns:
        List of deprecated semantic terms found. Empty list if validation passes.

    Example:
        >>> content = "Use TESTGUARD_FIRST pattern"
        >>> validate_no_deprecated_semantic_terms(content)
        ['TESTGUARD']
    """
    content_upper = content.upper()
    found_deprecated = []

    for deprecated_term in DEPRECATED_SEMANTIC_TERMS:
        if deprecated_term.upper() in content_upper:
            found_deprecated.append(deprecated_term)

    return found_deprecated


def validate_workflow_documents(
    project_root: Path | None = None,
) -> dict[str, ValidationResult]:
    """Validate the bundled workflow document for deprecated references.

    Note: Only validates the bundled version since .hestai-sys/ is gitignored
    and only exists at runtime. CI environments don't have the runtime copy.

    Args:
        project_root: Root directory of the project. If None, inferred from this file's location.

    Returns:
        Dictionary mapping file paths to validation results:
        {
            "/path/to/bundled_workflow": {
                "deprecated_tools": [...],
                "deprecated_terms": [...],
                "exists": True
            }
        }

    Example:
        >>> results = validate_workflow_documents()
        >>> any(r["deprecated_tools"] for r in results.values())
        False
    """
    workflow_paths = get_workflow_file_paths(project_root)
    results: dict[str, ValidationResult] = {}

    for file_path in workflow_paths:
        file_results: ValidationResult = {
            "deprecated_tools": [],
            "deprecated_terms": [],
            "exists": file_path.exists(),
        }

        if file_path.exists():
            content = file_path.read_text()
            file_results["deprecated_tools"] = validate_no_deprecated_tools(content)
            file_results["deprecated_terms"] = validate_no_deprecated_semantic_terms(content)

        results[str(file_path)] = file_results

    return results
