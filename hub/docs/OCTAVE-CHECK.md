===OCTAVE_CHECK_GUIDE===

META:
  NAME::"OCTAVE v4 Compliance Check"
  VERSION::"1.0"
  PURPOSE::"How to run/enable the local check script and optional user pre-commit hook"

USAGE:
  SCRIPT::`python3 tools/check_octave_v4.py`
  RESULT::"exit 0 when all .oct.md files are v4 compliant"

HOOK_INTEGRATION:
  LOCATION::`$HOME/.githooks/pre-commit`
  STEPS::[
    "mkdir -p $HOME/.githooks",
    "printf '#!/bin/sh\npython3 hub/tools/check_octave_v4.py || exit $?\n' > $HOME/.githooks/pre-commit",
    "chmod +x $HOME/.githooks/pre-commit",
    "git config core.hooksPath $HOME/.githooks"
  ]
  NOTE::"This uses user-level hooks; no repo workflow required yet."

TIPS:
  1::"Run the script locally before committing large doc changes",
  2::"Keep META near the top; header ===NAME=== and footer ===END===",
  3::"Extend the checker if new OCTAVE rules are added"

===END===
