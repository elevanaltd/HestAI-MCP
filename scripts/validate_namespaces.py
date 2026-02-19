"""
Pre-commit hook script for namespace validation of governance documents.

Usage:
    python scripts/validate_namespaces.py [file1 file2 ...]

Behaviour:
- Accepts file paths as command-line arguments (sys.argv[1:])
- Calls validate_file(Path(f)) on each file argument
- Prints warnings (prefixed with WARNING:) but does NOT exit non-zero for warnings
- Exits non-zero (exit code 1) only if there are errors (hard failures)
- If no files passed, exits 0 silently
- Prints a summary line at the end

Exit codes:
    0 — all files checked, no errors (warnings may have been emitted)
    1 — one or more files had errors
"""

import sys
from pathlib import Path

from hestai_mcp.core.namespace_resolver import validate_file


def main() -> None:
    """Run namespace validation on files passed as command-line arguments."""
    files = sys.argv[1:]

    if not files:
        sys.exit(0)

    total_warnings = 0
    total_errors = 0

    for filepath in files:
        result = validate_file(Path(filepath))

        for warning in result["warnings"]:
            print(f"WARNING: {filepath}: {warning}")
            total_warnings += 1

        for error in result["errors"]:
            print(f"ERROR: {filepath}: {error}")
            total_errors += 1

    n = len(files)
    file_word = "file" if n == 1 else "files"
    print(
        f"Namespace validation: {n} {file_word} checked,"
        f" {total_warnings} warnings, {total_errors} errors"
    )

    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
