---
name: python-style
description: Python code style guidelines for HestAI MCP including type hints, imports, error handling, and docstrings
allowed-tools: ["Edit", "Write", "Read", "Grep"]
triggers: ["python style", "type hints", "docstrings", "python imports", "ruff", "black", "mypy", "PEP 8", "python formatting"]
---

===PYTHON_STYLE===

META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Python code style guidelines for HestAI MCP development"
  DOMAIN::HEPHAESTUS[craftsmanship]⊕ATHENA[precision]

§1::TYPE_HINTS
  REQUIREMENT::all_functions_require_type_hints[enforced_by_mypy]
  FORWARD_REFS::"from __future__ import annotations"
  PREFER::[list,dict,set]
  AVOID::[List,Dict,Set][typing_module_deprecated]
  EXAMPLE::"def process(items: list[str]) -> dict[str, int]:"

§2::IMPORTS
  STYLE::absolute_imports_from_hestai_mcp
  ORDERING::ruff_handles_isort_style
  GROUPS::[
    stdlib::first,
    third_party::second,
    local::third
  ]
  EXAMPLE::[
    "from pathlib import Path",
    "from pydantic import BaseModel",
    "from hestai_mcp.schemas import SessionConfig"
  ]

§3::ERROR_HANDLING
  EXCEPTIONS::raise_specific[not_generic_Exception]
  DOCUMENTATION::document_exceptions_in_docstrings
  PATTERN::[
    "try:",
    "    result = risky_operation()",
    "except SpecificError as e:",
    "    logger.error(f'Operation failed: {e}')",
    "    raise"
  ]

§4::DOCSTRINGS
  STYLE::Google_style
  REQUIRED::public_functions_and_classes
  SECTIONS::[Args,Returns,Raises]
  EXAMPLE::[
    "\"\"\"Process items and return counts.",
    "",
    "Args:",
    "    items: List of items to process.",
    "    strict: If True, raise on invalid items.",
    "",
    "Returns:",
    "    Dictionary mapping item names to counts.",
    "",
    "Raises:",
    "    ValueError: If items is empty and strict is True.",
    "\"\"\""
  ]

§5::LINE_LENGTH
  MAX::100_characters
  ENFORCEMENT::[black,ruff]

§6::QUALITY_GATES
  COMMANDS::[
    "python -m ruff check src tests scripts",
    "python -m black --check src tests scripts",
    "python -m mypy src"
  ]
  FIX_COMMANDS::[
    "python -m black src tests scripts",
    "python -m ruff check --fix src tests scripts"
  ]

===END===
