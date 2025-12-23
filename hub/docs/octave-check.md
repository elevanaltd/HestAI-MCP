===OCTAVE_CHECK_GUIDE===

META:
  NAME::"OCTAVE v4.1 Compliance Check"
  VERSION::"2.0"
  PURPOSE::"How to validate OCTAVE documents using MCP tools and skills"

PRIMARY_METHOD:
  MCP_TOOLS:
    INGEST::"octave_ingest - validates and normalizes OCTAVE content"
    EJECT::"octave_eject - projects to various formats, generates templates"
  USAGE::"Call octave_ingest with content and schema for validation"

SKILLS_INTEGRATION:
  LOAD_ORDER::[octave-literacy, octave-mastery, octave-compression]
  LITERACY::"Essential syntax and operators (load first)"
  MASTERY::"Semantic vocabulary and patterns (requires literacy)"
  COMPRESSION::"Workflow for transforming verbose content"

OPERATOR_NORMALIZATION:
  CANONICAL::[→, ⊕, ⇌]
  ASCII_ALIASES::[->, +, _VERSUS_]
  NOTE::"MCP ingest tool auto-normalizes ASCII to Unicode"

LEGACY_SCRIPT:
  SCRIPT::`python3 hub/tools/check_octave_v4.py`
  STATUS::DEPRECATED
  NOTE::"Prefer MCP tools for validation"

HOOK_INTEGRATION:
  LOCATION::`$HOME/.githooks/pre-commit`
  STEPS::[
    "mkdir -p $HOME/.githooks",
    "printf '#!/bin/sh\npython3 hub/tools/octave-validator.py --path . || exit $?\n' > $HOME/.githooks/pre-commit",
    "chmod +x $HOME/.githooks/pre-commit",
    "git config core.hooksPath $HOME/.githooks"
  ]
  NOTE::"Optional - MCP tools provide interactive validation during authoring"

TIPS:
  1::"Use octave_ingest for immediate feedback during authoring"
  2::"Load octave-literacy skill for syntax reference"
  3::"Keep META near the top; header ===NAME=== and footer ===END==="
  4::"ASCII aliases accepted but Unicode canonical preferred"

===END===
