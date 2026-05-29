#!/usr/bin/env python3
"""Deprecation stub retained for downstream-path compatibility (#406 Phase 3).

The vendored OCTAVE validator was retired; this thin stub holds NO validation
logic. It exists only because ``_bundled_hub/`` is injected into ``.hestai-sys/``
at MCP server startup, so downstream callers may still invoke
``.hestai-sys/tools/octave-validator.py``. It warns and forwards to the
canonical ``octave-mcp`` CLI, propagating that CLI's exit code faithfully.
"""

from __future__ import annotations

import subprocess
import sys

_WARNING = (
    "DEPRECATED: _bundled_hub/tools/octave-validator.py is retired. This stub "
    "forwards to the canonical octave-mcp CLI. Migrate callers to: "
    "python -m octave_mcp.cli.main validate <file>. The stub will be removed in "
    "a future release (see #406)."
)


def main() -> int:
    print(_WARNING, file=sys.stderr)  # stderr only; keep stdout clean for parsing
    args = sys.argv[1:]
    # The legacy CLI took `--profile <value>`; the canonical CLI has no equivalent
    # and bare `validate <file>` is the chosen equivalence per the PR audit. Strip a
    # leading `--profile <value>` PAIR only when both flag and value are present, so a
    # degenerate lone `--profile` is NOT silently turned into a file-less validate call.
    if args[:1] == ["--profile"]:
        if len(args) < 2:
            print(
                "ERROR: legacy --profile flag requires a value; nothing to forward. "
                "Migrate to: python -m octave_mcp.cli.main validate <file>",
                file=sys.stderr,
            )
            return 2
        args = args[2:]
    result = subprocess.run([sys.executable, "-m", "octave_mcp.cli.main", "validate", *args])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
