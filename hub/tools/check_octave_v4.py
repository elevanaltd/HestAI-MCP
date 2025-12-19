#!/usr/bin/env python3
"""
OCTAVE v4 compliance checker

Checks all .oct.md files under the repo (this hub subtree) for:
- Header: first non-blank line matches ^===([A-Z0-9_]+)===$
- META block appears within the first 10 lines after header
- Footer: last non-blank line is ===END===

Exit codes:
 0 = all compliant
 >0 = number of files with issues (capped at 255)
"""
from __future__ import annotations
import os
import re
import sys
from typing import List, Tuple

HEADER_RE = re.compile(r"^===([A-Z0-9_]+)===$")


def is_octave_v4_compliant(path: str) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except Exception as e:
        return False, [f"read_error: {e}"]

    # first/last non-empty
    first = next((i for i, l in enumerate(lines) if l.strip() != ""), None)
    last = next((len(lines) - 1 - i for i, l in enumerate(reversed(lines)) if l.strip() != ""), None)

    if first is None or not HEADER_RE.match(lines[first]):
        issues.append("header:missing_or_invalid")

    if last is None or lines[last].strip() != "===END===":
        issues.append("footer:missing_or_invalid")

    meta_idx = next((i for i, l in enumerate(lines) if l.strip().startswith("META:")), -1)
    if first is not None:
        if meta_idx == -1 or meta_idx > first + 10:
            issues.append("meta:missing_or_too_late")
    else:
        issues.append("meta:cannot_verify_no_header")

    return len(issues) == 0, issues


def find_octave_files(root: str) -> List[str]:
    results: List[str] = []
    for dirpath, _, filenames in os.walk(root):
        if ".git" in dirpath.split(os.sep):
            continue
        for f in filenames:
            if f.endswith(".oct.md"):
                results.append(os.path.join(dirpath, f))
    return sorted(results)


def main() -> int:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    hub_root = repo_root  # script sits under hub/tools

    files = find_octave_files(hub_root)
    noncompliant = 0
    for p in files:
        ok, issues = is_octave_v4_compliant(p)
        if not ok:
            rel = os.path.relpath(p, hub_root)
            print(f"OCTAVE v4 NON-COMPLIANT: {rel} -> {', '.join(issues)}")
            noncompliant += 1

    if noncompliant == 0:
        print(f"OCTAVE v4: {len(files)} files compliant")
        return 0
    return min(noncompliant, 255)


if __name__ == "__main__":
    sys.exit(main())
