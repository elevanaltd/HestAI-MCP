"""Validate META.CANONICAL / META.SOURCE paths in staged .oct.md files.

Every committed .oct.md must declare at least one of:
  CANONICAL::"<repo-relative-path>"  — the file's own path (or deployed path)
  SOURCE::"<repo-relative-path>"     — the authored source path

At least one declared value must match the file's actual repo-relative posix
path (normalised, leading ./ stripped).

Bypass: SOURCE::legacy or CANONICAL::legacy exempts a file pending cleanup.

Exit 0 — all files pass.
Exit 1 — one or more files fail; all errors printed to stderr before exit.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

# Matches CANONICAL or SOURCE in the META block.
# Handles quoted ("value") and unquoted (value) forms, trailing commas,
# and optional inline comments.
_RE_FIELD = re.compile(
    r"""^\s*(?P<field>CANONICAL|SOURCE)::[ \t]*(?:"(?P<qval>[^"\n]*)"|\s*(?P<uval>[^\s,#\n][^,#\n]*?))[ \t]*,?[ \t]*(?:#[^\n]*)?\s*$""",
    re.MULTILINE,
)

# Captures the META block: everything after "META:\n" up to (but not
# including) the first section marker (§) or document end (===).
# Allows blank lines within the block (authors sometimes add them for readability).
_RE_META_BLOCK = re.compile(
    r"^META:\s*\n((?:(?!§|===)(?:[ \t][^\n]*|\s*)\n)*)",
    re.MULTILINE,
)


def _extract_meta_fields(content: str) -> dict[str, str]:
    """Return CANONICAL and SOURCE values from the META block, if present."""
    meta_match = _RE_META_BLOCK.search(content)
    if not meta_match:
        return {}

    meta_block = meta_match.group(1)
    fields: dict[str, str] = {}
    for m in _RE_FIELD.finditer(meta_block):
        field = m.group("field")
        value = m.group("qval") if m.group("qval") is not None else m.group("uval")
        if value is not None:
            fields[field] = value.strip()
    return fields


def _normalize_path(raw: str) -> str:
    """Normalise a path for comparison: strip leading ./ prefix only."""
    s = raw.strip()
    if s.startswith("./"):
        s = s[2:]
    return str(PurePosixPath(s))


def _git_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("ERROR canonical-paths: not in a git repository")
    return Path(result.stdout.strip())


def _staged_oct_md_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "-z", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("ERROR canonical-paths: git diff --cached failed")
    # -z outputs NUL-separated paths; handles filenames with spaces correctly
    return [f for f in result.stdout.split("\0") if f.endswith(".oct.md")]


def _validate_file(file_path: str, repo_root: Path) -> str | None:
    """Validate one .oct.md file.

    Returns None on success, or an error string describing the failure.
    """
    abs_path = (repo_root / file_path).resolve()
    try:
        content = abs_path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"FAIL {file_path}: cannot read file — {exc}"

    fields = _extract_meta_fields(content)
    canonical = fields.get("CANONICAL", "").strip()
    source = fields.get("SOURCE", "").strip()

    # Legacy bypass — file is pending proper annotation
    if canonical.lower() == "legacy" or source.lower() == "legacy":
        return None

    if not canonical and not source:
        return (
            f"FAIL {file_path}: missing META.CANONICAL and META.SOURCE.\n"
            f'  Add  SOURCE::"{file_path}"  or  SOURCE::legacy  (pending cleanup).'
        )

    file_norm = _normalize_path(file_path)

    for value in (canonical, source):
        if not value:
            continue
        if _normalize_path(value) == file_norm:
            return None

    declared: list[str] = []
    if canonical:
        declared.append(f"CANONICAL::{canonical!r}")
    if source:
        declared.append(f"SOURCE::{source!r}")

    return (
        f"FAIL {file_path}: declared path(s) do not match file location.\n"
        f"  File is at: {file_norm}\n"
        f"  Declared:   {', '.join(declared)}\n"
        f"  Fix: update the declared path or add SOURCE::legacy to bypass."
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate META.CANONICAL/SOURCE paths in .oct.md files.",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Validate staged .oct.md files (from git index).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        metavar="DIR",
        help="Repository root (defaults to git rev-parse --show-toplevel).",
    )
    parser.add_argument("paths", nargs="*", help=".oct.md file paths to check.")
    args = parser.parse_args(argv)

    files: list[str] = list(args.paths)
    if args.staged:
        files = _staged_oct_md_files()

    # Filter to .oct.md only (positional args may include other files)
    files = [f for f in files if f.endswith(".oct.md")]

    if not files:
        print("SKIP canonical-paths (no .oct.md files to check)")
        return 0

    repo_root: Path = args.repo_root or _git_repo_root()

    errors: list[str] = []
    for file_path in files:
        error = _validate_file(file_path, repo_root)
        if error:
            errors.append(error)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(
            f"FAIL canonical-paths: {len(errors)}/{len(files)} file(s) failed",
            file=sys.stderr,
        )
        return 1

    print(f"OK canonical-paths: {len(files)} file(s) validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
