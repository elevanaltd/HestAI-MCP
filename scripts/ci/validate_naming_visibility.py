from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RE_STANDARD = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(\.oct)?\.md$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+(\.oct)?\.md$")
RE_ADR = re.compile(r"^adr-\d{4}-[a-z0-9-]+(\.oct)?\.md$")
RE_REPORT = re.compile(r"^report-\d{3}-[a-z0-9-]+(\.oct)?\.md$")
RE_NORTH_STAR = re.compile(r"^000-[A-Z0-9-]+-NORTH-STAR(-SUMMARY)?(\.oct)?\.md$")
RE_WHITELIST = re.compile(
    r"^(README|LICENSE|CONTRIBUTING|CHANGELOG|SECURITY|CODE_OF_CONDUCT|CLAUDE|CODEOWNERS|ARCHITECTURE|PROJECT-CONTEXT|PROJECT-CHECKLIST|PROJECT-HISTORY|PROJECT-ROADMAP|APP-CONTEXT|APP-CHECKLIST|DECISIONS|VISIBILITY-RULES|NAMING-STANDARD|TEST-STRUCTURE-STANDARD|current_state)(\.(oct\.)?md)?$"
)


ALLOWED_ROOTS = ("docs/", "hub/", ".hestai/", ".claude/")
FORBIDDEN_FOLDERS = {".archive", ".sources", "_legacy", "legacy"}


def _run_git(args: list[str]) -> str:
    res = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise SystemExit(res.stderr.strip() or f"git {' '.join(args)} failed")
    return res.stdout


def _staged_files() -> list[str]:
    out = _run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    return [line.strip() for line in out.splitlines() if line.strip()]


def _is_doc(path: str) -> bool:
    return path.endswith(".md") or path.endswith(".oct.md")


def _is_allowed_root(path: str) -> bool:
    return path.startswith(ALLOWED_ROOTS)


def _validate_one(path: str) -> None:
    p = Path(path)
    name = p.name

    if name == "current_state.oct.md":
        return

    if "_" in name:
        raise SystemExit(f"ERROR naming-standard: underscores forbidden in filenames: {path}")

    if RE_WHITELIST.match(name) or RE_NORTH_STAR.match(name):
        return

    if not (
        RE_STANDARD.match(name)
        or RE_DATE.match(name)
        or RE_ADR.match(name)
        or RE_REPORT.match(name)
    ):
        raise SystemExit(f"ERROR naming-standard: filename violates patterns: {path}")

    parts = [part.lower() for part in p.parts]
    if any(part in FORBIDDEN_FOLDERS for part in parts):
        raise SystemExit(
            f"ERROR visibility-rules: canonical docs forbidden in archive/source folders: {path}"
        )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Validate staged docs only (git index).",
    )
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)

    paths = args.paths
    if args.staged:
        paths = _staged_files()

    docs = [p for p in paths if _is_doc(p) and _is_allowed_root(p)]
    if not docs:
        print("SKIP naming/visibility (no relevant docs)")
        return 0

    for p in docs:
        _validate_one(p)

    print("OK naming/visibility")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
