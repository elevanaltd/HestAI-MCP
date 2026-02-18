"""
Namespace resolver for Constitution §3.5 namespace validation (#241).

Three validation rules:
- V1: Documents should declare NAMESPACE::SYS or NAMESPACE::PROD in META/frontmatter
- V2: Cross-namespace immutable citations must use qualified form (SYS::I2, PROD::I4)
- V3: Bare form (I2) is valid within single-namespace context (intra-namespace citation)

Immutable index collision table (I1-I6 have different meanings in SYS vs PROD):
  SYS: I1=Verifiable Behavioral Specification First, I2=Phase-Gated Progression,
       I3=Human Primacy, I4=Discoverable Artifact Persistence,
       I5=Quality Verification Before Progression, I6=Explicit Accountability
  PROD: I1=Persistent Cognitive Continuity, I2=Structural Integrity Priority,
        I3=Dual Layer Authority, I4=Freshness Verification,
        I5=Odyssean Identity Binding, I6=Universal Scope
"""

import re
from pathlib import Path

# Matches NAMESPACE::SYS or NAMESPACE::PROD (valid values only)
_NAMESPACE_PATTERN = re.compile(r"NAMESPACE::(SYS|PROD)")

# Matches all immutable references I1-I9 (bare or qualified)
# Used in find_bare_references to filter out qualified forms
_ALL_REF_PATTERN = re.compile(r"(?:(?:SYS|PROD)::)?(I[1-9])")

# Matches qualified immutable references (SYS::I2 or PROD::I4)
_QUALIFIED_REF_PATTERN = re.compile(r"(?:SYS|PROD)::I[1-9]")


def extract_namespace(content: str) -> str | None:
    """Extract NAMESPACE::SYS or NAMESPACE::PROD from document content.

    Handles both OCTAVE META block format and YAML frontmatter format.
    Returns None when no valid namespace declaration is found.

    Args:
        content: Full text content of the document

    Returns:
        "SYS", "PROD", or None
    """
    match = _NAMESPACE_PATTERN.search(content)
    if match:
        return match.group(1)
    return None


def find_bare_references(content: str) -> list[str]:
    """Find bare immutable references (I1-I9) not qualified with SYS:: or PROD::.

    A bare reference is one like 'I2' or 'CITE[I3]' not preceded by a namespace
    qualifier. Qualified forms 'SYS::I2' and 'PROD::I4' are excluded.

    Strategy: replace all qualified refs with a placeholder, then find remaining
    standalone I1-I9 tokens that are not embedded in longer words.

    Args:
        content: Full text content of the document

    Returns:
        List of bare reference strings (e.g. ["I2", "I5"]), deduplicated and sorted
    """
    # Remove all qualified references so they cannot match as bare
    stripped = _QUALIFIED_REF_PATTERN.sub("QUALIFIED", content)
    # Now find bare I1-I9 tokens (word-boundary match, not part of longer word)
    bare_pattern = re.compile(r"\bI([1-9])\b")
    matches = bare_pattern.findall(stripped)
    return sorted({f"I{digit}" for digit in matches})


def validate_file(path: Path) -> dict:
    """Validate namespace declaration and reference qualification for a document.

    Checks:
    - V1: Document declares NAMESPACE::SYS or NAMESPACE::PROD
    - V2/V3: Bare references are only present in intra-namespace context
      (document has declared its own namespace — bare refs are then valid)
      or flagged as warnings when no namespace is declared.

    Args:
        path: Path to the document file to validate

    Returns:
        dict with:
          - valid (bool): True if no errors and no ambiguous warnings
          - namespace (str | None): Detected namespace or None
          - warnings (list[str]): Non-fatal issues (bare refs without namespace, missing decl)
          - errors (list[str]): Hard failures (file not found)
    """
    if not path.exists():
        return {
            "valid": False,
            "namespace": None,
            "warnings": [],
            "errors": [f"File not found: {path}"],
        }

    content = path.read_text(encoding="utf-8")
    namespace = extract_namespace(content)
    bare_refs = find_bare_references(content)
    warnings: list[str] = []
    errors: list[str] = []

    if namespace is None:
        warnings.append("V1: No NAMESPACE::SYS or NAMESPACE::PROD declaration found")
        # Bare refs without namespace are ambiguous — warn about each
        for ref in bare_refs:
            warnings.append(
                f"V2: Bare reference {ref} is ambiguous without a namespace declaration"
            )
    else:
        # Intra-namespace: document has declared its namespace, bare refs are valid (V3)
        pass

    valid = len(errors) == 0 and len(warnings) == 0
    return {
        "valid": valid,
        "namespace": namespace,
        "warnings": warnings,
        "errors": errors,
    }
