"""
Verification Claims - Validate OCTAVE content before context sync.

Implements Feature 4: Verify compression artifacts before PROJECT-CONTEXT update.
Prevents broken references, path traversal, and invalid claims.

Security boundaries:
- Files mentioned in FILES_MODIFIED must exist
- Markdown links must resolve
- No path traversal in file references
- No absolute paths to sensitive directories
"""

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def verify_context_claims(octave_content: str, working_dir: Path) -> dict[str, Any]:
    """
    Verify OCTAVE content claims before syncing to PROJECT-CONTEXT.

    Validation checks:
    1. FILES_MODIFIED references exist
    2. Markdown links resolve to real files
    3. No path traversal attempts
    4. No references to sensitive system paths

    Args:
        octave_content: OCTAVE compressed content
        working_dir: Project root directory for path resolution

    Returns:
        dict with:
            - passed: bool (True if all checks pass)
            - issues: List[str] (validation errors found)
            - warnings: List[str] (non-blocking concerns)

    Design Decision:
        Fail-closed: If verification fails, block context update.
        Better to skip update than corrupt PROJECT-CONTEXT with broken refs.
    """
    issues: list[str] = []
    warnings: list[str] = []

    # Check 1: Verify FILES_MODIFIED references
    file_issues = _verify_files_modified(octave_content, working_dir)
    issues.extend(file_issues)

    # Check 2: Verify markdown links
    link_issues = _verify_markdown_links(octave_content, working_dir)
    issues.extend(link_issues)

    # Check 3: Path traversal detection
    traversal_issues = _detect_path_traversal(octave_content)
    issues.extend(traversal_issues)

    # Check 4: Sensitive path detection (warning only)
    sensitive_warnings = _detect_sensitive_paths(octave_content)
    warnings.extend(sensitive_warnings)

    return {"passed": len(issues) == 0, "issues": issues, "warnings": warnings}


def _verify_files_modified(octave_content: str, working_dir: Path) -> list[str]:
    """
    Verify that files mentioned in FILES_MODIFIED exist and are within working_dir.

    Pattern: FILES_MODIFIED::[file1, file2, ...]

    Security: Rejects absolute paths and enforces repo-relative containment.
    """
    issues: list[str] = []
    working_dir_resolved = working_dir.resolve()

    # Extract FILES_MODIFIED section
    pattern = r"FILES_MODIFIED::\[(.*?)\]"
    match = re.search(pattern, octave_content, re.DOTALL)

    if not match:
        # No FILES_MODIFIED section is fine
        return issues

    files_section = match.group(1).strip()

    # Parse file paths (comma-separated, may have quotes)
    file_paths = re.findall(r'["\']([^"\']+)["\']|([^,\s]+)', files_section)
    file_paths = [f[0] or f[1] for f in file_paths if f[0] or f[1]]

    for file_path_str in file_paths:
        file_path_str = file_path_str.strip()
        if not file_path_str:
            continue

        file_path = Path(file_path_str)

        # SECURITY: Reject absolute paths
        if file_path.is_absolute():
            issues.append(f"Absolute path not allowed: {file_path_str}")
            continue

        # Resolve relative to working_dir
        resolved = (working_dir / file_path).resolve()

        # SECURITY: Enforce repo-relative containment
        if not resolved.is_relative_to(working_dir_resolved):
            issues.append(f"Path traversal attempt: {file_path_str}")
            continue

        if not resolved.exists():
            issues.append(f"FILES_MODIFIED references non-existent file: {file_path_str}")

    return issues


def _normalize_link_destination(dest: str) -> str:
    """Normalize markdown link destination for security checks."""
    # Strip angle brackets: </etc/passwd> -> /etc/passwd
    if dest.startswith("<") and dest.endswith(">"):
        dest = dest[1:-1]

    # Handle file:// URIs
    if dest.startswith("file://"):
        # file://localhost/path or file:///path -> /path
        dest = dest[7:]  # Remove "file://"
        if dest.startswith("localhost"):
            dest = dest[9:]  # Remove "localhost"
        elif dest.startswith("//"):
            dest = dest[2:]  # Remove leading //

    return dest


def _verify_markdown_links(octave_content: str, working_dir: Path) -> list[str]:
    """
    Verify markdown links [text](path) resolve to real files within working_dir.

    Only checks file:// links or relative paths, not http(s)://

    Security: Rejects absolute paths and enforces repo-relative containment.
    """
    issues = []
    working_dir_resolved = working_dir.resolve()

    # Pattern: [text](path) where path is not http(s)://
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    matches = re.findall(pattern, octave_content)

    for link_text, link_path in matches:
        # Skip external links
        if link_path.startswith(("http://", "https://", "#")):
            continue

        # Normalize the link destination (handles file:// URIs and angle brackets)
        link_path = _normalize_link_destination(link_path)

        file_path = Path(link_path)

        # SECURITY: Reject absolute paths
        if file_path.is_absolute():
            issues.append(f"Absolute path not allowed in markdown link: [{link_text}]({link_path})")
            continue

        # Resolve relative to working_dir
        resolved = (working_dir / file_path).resolve()

        # SECURITY: Enforce repo-relative containment
        if not resolved.is_relative_to(working_dir_resolved):
            issues.append(f"Path traversal in markdown link: [{link_text}]({link_path})")
            continue

        if not resolved.exists():
            issues.append(f"Markdown link [{link_text}]({link_path}) references non-existent file")

    return issues


def _detect_path_traversal(octave_content: str) -> list[str]:
    """
    Detect path traversal attempts (../ or absolute paths outside project).

    Blocks:
    - ../ sequences
    - Absolute paths (except within working_dir)
    """
    issues = []

    # Check for ../ traversal
    if ".." in octave_content:
        # Count occurrences in file paths (not in prose)
        file_pattern = r'["\']([^"\']*\.\.[^"\']*)["\']'
        traversal_matches = re.findall(file_pattern, octave_content)

        if traversal_matches:
            issues.append(f"Path traversal detected: {traversal_matches[0]}")

    return issues


def _detect_sensitive_paths(octave_content: str) -> list[str]:
    """
    Detect references to sensitive system paths (warning, not error).

    Patterns:
    - /etc/
    - /var/
    - /System/
    - ~/.ssh/
    - ~/.aws/
    """
    warnings = []

    sensitive_patterns = [
        r"/etc/",
        r"/var/",
        r"/System/",
        r"~/\.ssh/",
        r"~/\.aws/",
        r"/root/",
    ]

    for pattern in sensitive_patterns:
        if re.search(pattern, octave_content):
            warnings.append(f"References sensitive path matching: {pattern}")

    return warnings
