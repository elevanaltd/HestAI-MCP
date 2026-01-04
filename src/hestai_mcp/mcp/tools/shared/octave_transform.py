"""
OCTAVE Format Transformation Module.

Converts legacy RAPH Vector v4.0 format to OCTAVE-compliant format.
Supports bidirectional transformation during migration period.

Key transformations:
- Envelope format: ::v4.0 suffix → META section
- Section headers: ## BIND → BIND field
- Maintains micro-syntax for TENSION lines (valid OCTAVE)
"""

import re
from typing import Any


def raph_v4_to_octave(content: str) -> str:
    """
    Convert RAPH Vector v4.0 format to OCTAVE-compliant format.

    Transformations:
    1. Envelope: ===RAPH_VECTOR::v4.0=== → ===RAPH_VECTOR=== with META
    2. Headers: ## BIND → BIND: (field notation)
    3. Sections become nested fields
    4. Preserve TENSION micro-syntax as valid OCTAVE strings

    Args:
        content: RAPH Vector v4.0 formatted content

    Returns:
        OCTAVE-compliant formatted content
    """
    lines = content.split("\n")
    output: list[str] = []
    in_section: str | None = None
    section_content: list[str] = []

    for line in lines:
        # Handle envelope opening
        if line == "===RAPH_VECTOR::v4.0===":
            output.append("===RAPH_VECTOR===")
            output.append("META:")
            output.append("  TYPE::RAPH_VECTOR")
            output.append("  VERSION::5.0")
            output.append("  SCHEMA::ODYSSEAN_ANCHOR")
            output.append("")
            continue

        # Handle envelope closing
        if line == "===END_RAPH_VECTOR===":
            # Flush any pending section
            if in_section and section_content:
                _flush_section(output, in_section, section_content)
                section_content = []
            output.append("===END===")
            continue

        # Handle section headers
        if line.startswith("## "):
            # Flush previous section if any (even if empty)
            if in_section:
                _flush_section(output, in_section, section_content)
                section_content = []

            # Start new section
            section_name = line[3:].strip()
            in_section = section_name
            continue

        # Accumulate section content
        if in_section:
            # Skip empty lines at section start
            if not section_content and not line.strip():
                continue
            section_content.append(line)
        else:
            output.append(line)

    # Flush final section if any (even if empty)
    if in_section:
        _flush_section(output, in_section, section_content)

    return "\n".join(output)


def _flush_section(output: list, section_name: str, content: list) -> None:
    """
    Flush accumulated section content to output in OCTAVE format.

    Args:
        output: Output lines list
        section_name: Name of section (BIND, TENSION, etc)
        content: Section content lines
    """
    if section_name == "BIND":
        output.append("BIND:")
        for line in content:
            if line.strip():
                output.append(f"  {line}")

    elif section_name == "ARM":
        output.append("ARM:")
        for line in content:
            if line.strip():
                output.append(f"  {line}")

    elif section_name == "TENSION":
        # Keep TENSION lines as micro-syntax (valid OCTAVE)
        tension_lines = [line for line in content if line.strip() and line.startswith("L")]
        if tension_lines:
            output.append("TENSIONS::[")
            for i, line in enumerate(tension_lines):
                # Add comma after each tension except last
                if i < len(tension_lines) - 1:
                    output.append(f"  {line},")
                else:
                    output.append(f"  {line}")
            output.append("]")
        else:
            # Empty tensions
            output.append("TENSIONS::[")
            output.append("]")

    elif section_name == "COMMIT":
        output.append("COMMIT:")
        for line in content:
            if line.strip():
                output.append(f"  {line}")

    else:
        # Unknown section, preserve as-is
        output.append(f"{section_name}:")
        for line in content:
            output.append(f"  {line}")

    output.append("")  # Empty line after section


def octave_to_raph_v4(content: str) -> str:
    """
    Convert OCTAVE-compliant format back to RAPH Vector v4.0 format.

    For backward compatibility during migration period.

    Args:
        content: OCTAVE-compliant formatted content

    Returns:
        RAPH Vector v4.0 formatted content
    """
    lines = content.split("\n")
    output = []
    skip_meta = False

    for _i, line in enumerate(lines):
        # Handle envelope opening
        if line == "===RAPH_VECTOR===":
            output.append("===RAPH_VECTOR::v4.0===")
            skip_meta = True
            continue

        # Skip META section
        if skip_meta:
            if line.startswith("META:") or line.startswith("  "):
                continue
            else:
                skip_meta = False

        # Handle envelope closing
        if line == "===END===":
            output.append("===END_RAPH_VECTOR===")
            continue

        # Convert field notation back to headers
        if line.startswith("BIND:"):
            output.append("## BIND")
            continue

        if line.startswith("ARM:"):
            output.append("## ARM")
            continue

        if line.startswith("TENSIONS::"):
            output.append("## TENSION")
            # Parse the list format
            if line.endswith("["):
                # Multi-line tensions
                continue
            continue

        if line.startswith("COMMIT:"):
            output.append("## COMMIT")
            continue

        # Handle indented content (remove indent)
        if line.startswith("  "):
            output.append(line[2:])
        elif line == "]":
            # End of tensions list
            continue
        else:
            output.append(line)

    return "\n".join(output)


def is_raph_v4_format(content: str) -> bool:
    """
    Check if content is in RAPH Vector v4.0 format.

    Args:
        content: Content to check

    Returns:
        True if RAPH v4.0 format, False if OCTAVE-compliant
    """
    return "===RAPH_VECTOR::v4.0===" in content


def is_octave_format(content: str) -> bool:
    """
    Check if content is in OCTAVE-compliant format.

    Args:
        content: Content to check

    Returns:
        True if OCTAVE-compliant, False otherwise
    """
    return "===RAPH_VECTOR===" in content and "META:" in content and "TYPE::RAPH_VECTOR" in content


def parse_with_fallback(content: str) -> dict[str, Any]:
    """
    Parse RAPH/OCTAVE content with automatic format detection.

    Tries octave-mcp first, falls back to custom parser if needed.

    Args:
        content: Content to parse (either format)

    Returns:
        Parsed content as dictionary
    """
    try:
        import octave_mcp  # type: ignore[import-not-found]

        # Convert to OCTAVE format if needed
        if is_raph_v4_format(content):
            content = raph_v4_to_octave(content)

        # Parse with octave-mcp
        return octave_mcp.parse(content)  # type: ignore[no-any-return]

    except (ImportError, Exception):
        # Fall back to custom parsing
        return _custom_parse_raph(content)


def _custom_parse_raph(content: str) -> dict[str, Any]:
    """
    Custom parser for RAPH Vector format (fallback).

    Args:
        content: RAPH Vector content

    Returns:
        Parsed content as dictionary
    """
    result: dict[str, Any] = {
        "type": "RAPH_VECTOR",
        "version": "4.0" if "::v4.0" in content else "5.0",
        "bind": {},
        "arm": {},
        "tensions": [],
        "commit": {},
    }

    # Extract BIND section
    bind_match = re.search(r"## BIND\n(.*?)(?=\n##|\n===|$)", content, re.DOTALL)
    if bind_match:
        bind_text = bind_match.group(1)

        role_match = re.search(r"ROLE::(.+)", bind_text)
        if role_match:
            result["bind"]["role"] = role_match.group(1).strip()

        cognition_match = re.search(r"COGNITION::(.+)", bind_text)
        if cognition_match:
            result["bind"]["cognition"] = cognition_match.group(1).strip()

        authority_match = re.search(r"AUTHORITY::(.+)", bind_text)
        if authority_match:
            result["bind"]["authority"] = authority_match.group(1).strip()

    # Extract TENSION section
    tension_match = re.search(r"## TENSION\n(.*?)(?=\n##|\n===|$)", content, re.DOTALL)
    if tension_match:
        tension_text = tension_match.group(1)
        for line in tension_text.split("\n"):
            if line.strip().startswith("L"):
                result["tensions"].append(line.strip())

    # Extract COMMIT section
    commit_match = re.search(r"## COMMIT\n(.*?)(?=\n##|\n===|$)", content, re.DOTALL)
    if commit_match:
        commit_text = commit_match.group(1)

        artifact_match = re.search(r"ARTIFACT::(.+)", commit_text)
        if artifact_match:
            result["commit"]["artifact"] = artifact_match.group(1).strip()

        gate_match = re.search(r"GATE::(.+)", commit_text)
        if gate_match:
            result["commit"]["gate"] = gate_match.group(1).strip()

    return result


# Example usage
if __name__ == "__main__":
    # Test transformation
    raph_v4 = """===RAPH_VECTOR::v4.0===
## BIND
ROLE::holistic-orchestrator
COGNITION::LOGOS::ATHENA⊕ODYSSEUS
AUTHORITY::RESPONSIBLE[main]

## TENSION
L1::[Manual parsing]⇌CTX:parser.py:86[regex]→TRIGGER[migrate]
L2::[Custom format]⇌CTX:anchor.py:246[synthesis]→TRIGGER[standardize]

## COMMIT
ARTIFACT::test.md
GATE::validation
===END_RAPH_VECTOR==="""

    octave_format = raph_v4_to_octave(raph_v4)
    print("OCTAVE-compliant format:")
    print(octave_format)
    print("\n" + "=" * 60 + "\n")

    # Test reverse transformation
    back_to_raph = octave_to_raph_v4(octave_format)
    print("Back to RAPH v4.0:")
    print(back_to_raph)
