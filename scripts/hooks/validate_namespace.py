#!/usr/bin/env python3
"""
Pre-commit hook for validating SYS::/PROD:: namespace compliance.

Implements Constitution §3.5 Relativity Governance Protocol validation.
Validates namespace declarations and immutable references across documentation.

Usage:
    python scripts/hooks/validate_namespace.py --staged  # Check staged files
    python scripts/hooks/validate_namespace.py FILE...  # Check specific files

Grace period until 2026-08-16: warnings only
After grace period: violations become errors

Exit codes:
    0 - All files pass validation (or only warnings during grace period)
    1 - Validation errors found
    2 - Script errors
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# Define inline to avoid import issues
GRACE_PERIOD_END = date(2026, 8, 16)


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


def validate_namespace_inline(file_path: Path) -> tuple[list[str], list[str]]:
    """
    Simple inline namespace validation.

    Returns:
        Tuple of (warnings, errors)
    """
    warnings = []
    errors = []

    try:
        content = file_path.read_text()
    except Exception as e:
        errors.append(f"Could not read file: {e}")
        return warnings, errors

    # Extract namespace declaration
    namespace = None

    # Check OCTAVE META block
    meta_match = re.search(r"META::[^]]*NAMESPACE::(\w+)", content)
    if meta_match:
        namespace = meta_match.group(1)

    # Check YAML frontmatter
    if content.startswith("---\n"):
        yaml_end = content.find("\n---\n", 4)
        if yaml_end > 0:
            yaml_section = content[4:yaml_end]
            ns_match = re.search(r"^namespace:\s*(\w+)", yaml_section, re.MULTILINE)
            if ns_match:
                namespace = ns_match.group(1).upper()

    # Find all I# references
    bare_refs = re.findall(r"\bI[1-6]\b(?!::)", content)
    sys_refs = re.findall(r"\bSYS::I[1-6]\b", content)
    prod_refs = re.findall(r"\bPROD::I[1-6]\b", content)

    # Apply validation rules
    in_grace_period = date.today() < GRACE_PERIOD_END

    # V1: No namespace + bare refs = error
    if not namespace and bare_refs:
        msg = f"No namespace declared but found {len(bare_refs)} bare I# reference(s)"
        if in_grace_period:
            warnings.append(msg)
        else:
            errors.append(msg)

    # V2: Cross-namespace refs must be qualified
    if namespace == "SYS" and prod_refs and not all("PROD::" in r for r in prod_refs):
        msg = "Cross-namespace references to PROD must be qualified"
        errors.append(msg)
    elif namespace == "PROD" and sys_refs and not all("SYS::" in r for r in sys_refs):
        msg = "Cross-namespace references to SYS must be qualified"
        errors.append(msg)

    # V3: Redundant qualification warning
    if namespace == "SYS" and sys_refs:
        warnings.append(
            f"Redundant SYS:: qualification in SYS namespace file ({len(sys_refs)} instances)"
        )
    elif namespace == "PROD" and prod_refs:
        warnings.append(
            f"Redundant PROD:: qualification in PROD namespace file ({len(prod_refs)} instances)"
        )

    return warnings, errors


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

    # Validate each file
    total_warnings = 0
    total_errors = 0

    for file_path in files_to_check:
        if not file_path.exists():
            continue

        warnings, errors = validate_namespace_inline(file_path)

        if warnings or errors:
            print(f"\n{file_path}:")
            for warning in warnings:
                print(f"  ⚠️  WARNING: {warning}")
                total_warnings += 1
            for error in errors:
                print(f"  ❌ ERROR: {error}")
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
