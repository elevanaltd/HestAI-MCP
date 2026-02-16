#!/usr/bin/env python3
"""
Pre-commit hook for validating SYS::/PROD:: namespace compliance.

Uses the core NamespaceResolver for consistency with tested validation logic.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Add src to path to import core module
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "src"))

try:
    from hestai_mcp.core.namespace_resolver import NamespaceResolver
except ImportError:
    print(
        "ERROR: Cannot import NamespaceResolver. Ensure project is installed with: pip install -e .",
        file=sys.stderr,
    )
    sys.exit(2)


def get_staged_files() -> list[Path]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = []
        for line in result.stdout.strip().split("\n"):
            if line:
                files.append(Path(line))
        return files
    except subprocess.CalledProcessError:
        return []


def should_validate(file_path: Path) -> bool:
    """
    Check if file should be validated for namespace compliance.

    Only validates documentation files in specific directories.
    """
    # Must be a documentation file
    if file_path.suffix not in {".md", ".oct.md"}:
        return False

    # Check if in relevant directory
    relevant_dirs = {
        "docs/",
        "src/hestai_mcp/_bundled_hub/",
        ".hestai/",
        ".hestai-sys/",
        ".claude/",
    }

    path_str = str(file_path)
    return any(path_str.startswith(d) for d in relevant_dirs)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate SYS::/PROD:: namespace compliance")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Validate only staged files",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Files to validate",
    )

    args = parser.parse_args()

    # Get files to validate
    if args.staged:
        files = get_staged_files()
    elif args.files:
        files = args.files
    else:
        print("Error: Must specify --staged or provide files", file=sys.stderr)
        return 2

    # Filter to relevant files
    files_to_check = [f for f in files if should_validate(f)]

    if not files_to_check:
        print("✓ No documentation files to validate")
        return 0

    # Use the core NamespaceResolver
    resolver = NamespaceResolver()
    total_warnings = 0
    total_errors = 0

    for file_path in files_to_check:
        if not file_path.exists():
            continue

        result = resolver.validate_file(file_path)

        if result.warnings or result.errors:
            print(f"\n{file_path}:")

            for warning in result.warnings:
                print(f"  ⚠️  WARNING [{warning.line}]: {warning.message}")
                total_warnings += 1

            for error in result.errors:
                print(f"  ❌ ERROR [{error.line}]: {error.message}")
                total_errors += 1

    # Summary
    if total_errors == 0 and total_warnings == 0:
        print(f"✓ All {len(files_to_check)} files pass namespace validation")
        return 0
    elif total_errors == 0:
        print(f"\n✓ Validation passed with {total_warnings} warning(s)")
        return 0
    else:
        print(f"\n❌ Validation failed: {total_errors} error(s), {total_warnings} warning(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
