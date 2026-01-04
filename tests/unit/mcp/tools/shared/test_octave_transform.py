"""
Tests for OCTAVE format transformation module.

Verifies bidirectional conversion between RAPH v4.0 and OCTAVE-compliant formats.
"""

import pytest

from hestai_mcp.mcp.tools.shared.octave_transform import (
    is_octave_format,
    is_raph_v4_format,
    octave_to_raph_v4,
    raph_v4_to_octave,
)


class TestOctaveTransform:
    """Test suite for OCTAVE format transformations."""

    @pytest.fixture
    def raph_v4_sample(self):
        """Sample RAPH Vector v4.0 format."""
        return """===RAPH_VECTOR::v4.0===
## BIND
ROLE::holistic-orchestrator
COGNITION::LOGOS::ATHENA⊕ODYSSEUS⊕DAEDALUS
AUTHORITY::RESPONSIBLE[main]

## ARM
PHASE::B1_FOUNDATION
BRANCH::main[0↑0↓]
FILES::5[test.py,main.py]
FOCUS::validation

## TENSION
L1::[Manual parsing]⇌CTX:parser.py:86[regex]→TRIGGER[migrate]
L2::[Custom format]⇌CTX:anchor.py:246[synthesis]→TRIGGER[standardize]

## COMMIT
ARTIFACT::docs/test.md
GATE::validation
===END_RAPH_VECTOR==="""

    @pytest.fixture
    def octave_sample(self):
        """Sample OCTAVE-compliant format."""
        return """===RAPH_VECTOR===
META:
  TYPE::RAPH_VECTOR
  VERSION::5.0
  SCHEMA::ODYSSEAN_ANCHOR

BIND:
  ROLE::holistic-orchestrator
  COGNITION::LOGOS::ATHENA⊕ODYSSEUS⊕DAEDALUS
  AUTHORITY::RESPONSIBLE[main]

ARM:
  PHASE::B1_FOUNDATION
  BRANCH::main[0↑0↓]
  FILES::5[test.py,main.py]
  FOCUS::validation

TENSIONS::[
  L1::[Manual parsing]⇌CTX:parser.py:86[regex]→TRIGGER[migrate],
  L2::[Custom format]⇌CTX:anchor.py:246[synthesis]→TRIGGER[standardize]
]

COMMIT:
  ARTIFACT::docs/test.md
  GATE::validation

===END==="""

    def test_format_detection_raph_v4(self, raph_v4_sample):
        """Test detection of RAPH v4.0 format."""
        assert is_raph_v4_format(raph_v4_sample) is True
        assert is_octave_format(raph_v4_sample) is False

    def test_format_detection_octave(self, octave_sample):
        """Test detection of OCTAVE-compliant format."""
        assert is_octave_format(octave_sample) is True
        assert is_raph_v4_format(octave_sample) is False

    def test_raph_to_octave_envelope(self, raph_v4_sample):
        """Test envelope transformation from RAPH to OCTAVE."""
        result = raph_v4_to_octave(raph_v4_sample)

        # Check opening envelope
        assert "===RAPH_VECTOR===" in result
        assert "===RAPH_VECTOR::v4.0===" not in result

        # Check META section added
        assert "META:" in result
        assert "TYPE::RAPH_VECTOR" in result
        assert "VERSION::5.0" in result
        assert "SCHEMA::ODYSSEAN_ANCHOR" in result

        # Check closing envelope
        assert "===END===" in result
        assert "===END_RAPH_VECTOR===" not in result

    def test_raph_to_octave_sections(self, raph_v4_sample):
        """Test section transformation from headers to fields."""
        result = raph_v4_to_octave(raph_v4_sample)

        # Check headers converted to fields
        assert "## BIND" not in result
        assert "BIND:" in result

        assert "## ARM" not in result
        assert "ARM:" in result

        assert "## TENSION" not in result
        assert "TENSIONS::[" in result

        assert "## COMMIT" not in result
        assert "COMMIT:" in result

    def test_raph_to_octave_preserves_content(self, raph_v4_sample):
        """Test that content is preserved during transformation."""
        result = raph_v4_to_octave(raph_v4_sample)

        # Check BIND content preserved
        assert "ROLE::holistic-orchestrator" in result
        assert "COGNITION::LOGOS::ATHENA⊕ODYSSEUS⊕DAEDALUS" in result
        assert "AUTHORITY::RESPONSIBLE[main]" in result

        # Check TENSION micro-syntax preserved
        assert "L1::[Manual parsing]⇌CTX:parser.py:86[regex]→TRIGGER[migrate]" in result
        assert "L2::[Custom format]⇌CTX:anchor.py:246[synthesis]→TRIGGER[standardize]" in result

        # Check COMMIT content preserved
        assert "ARTIFACT::docs/test.md" in result
        assert "GATE::validation" in result

    def test_octave_to_raph_envelope(self, octave_sample):
        """Test envelope transformation from OCTAVE to RAPH."""
        result = octave_to_raph_v4(octave_sample)

        # Check opening envelope
        assert "===RAPH_VECTOR::v4.0===" in result
        assert "===RAPH_VECTOR===" not in result or "===RAPH_VECTOR::v4.0===" in result

        # Check META section removed
        assert "META:" not in result
        assert "TYPE::RAPH_VECTOR" not in result
        assert "SCHEMA::ODYSSEAN_ANCHOR" not in result

        # Check closing envelope
        assert "===END_RAPH_VECTOR===" in result
        assert "===END===" not in result or "===END_RAPH_VECTOR===" in result

    def test_octave_to_raph_sections(self, octave_sample):
        """Test section transformation from fields to headers."""
        result = octave_to_raph_v4(octave_sample)

        # Check fields converted to headers
        assert "## BIND" in result
        assert "## ARM" in result
        assert "## TENSION" in result
        assert "## COMMIT" in result

    def test_roundtrip_raph_to_octave_to_raph(self, raph_v4_sample):
        """Test roundtrip conversion preserves essential content."""
        # Transform to OCTAVE
        octave = raph_v4_to_octave(raph_v4_sample)
        # Transform back to RAPH
        back_to_raph = octave_to_raph_v4(octave)

        # Check key content preserved
        assert "ROLE::holistic-orchestrator" in back_to_raph
        assert "COGNITION::LOGOS::ATHENA⊕ODYSSEUS⊕DAEDALUS" in back_to_raph
        assert "L1::[Manual parsing]" in back_to_raph
        assert "ARTIFACT::docs/test.md" in back_to_raph

    def test_handles_empty_sections(self):
        """Test handling of empty sections."""
        minimal_raph = """===RAPH_VECTOR::v4.0===
## BIND
ROLE::test

## TENSION

## COMMIT
ARTIFACT::test.md
===END_RAPH_VECTOR==="""

        result = raph_v4_to_octave(minimal_raph)
        assert "BIND:" in result
        assert "TENSIONS::[\n]" in result
        assert "COMMIT:" in result

    def test_preserves_unicode_operators(self, raph_v4_sample):
        """Test that Unicode operators are preserved."""
        result = raph_v4_to_octave(raph_v4_sample)

        # Check synthesis operator
        assert "⊕" in result

        # Check tension operators
        assert "⇌" in result
        assert "→" in result
        assert "↑" in result
        assert "↓" in result

    def test_handles_multiline_tensions(self):
        """Test handling of multiple TENSION lines."""
        raph_with_tensions = """===RAPH_VECTOR::v4.0===
## TENSION
L1::[First]⇌CTX:file1.py:10[state1]→TRIGGER[action1]
L2::[Second]⇌CTX:file2.py:20[state2]→TRIGGER[action2]
L3::[Third]⇌CTX:file3.py:30[state3]→TRIGGER[action3]
===END_RAPH_VECTOR==="""

        result = raph_v4_to_octave(raph_with_tensions)

        assert "TENSIONS::[" in result
        assert "L1::" in result
        assert "L2::" in result
        assert "L3::" in result
        # Check commas between tensions
        lines = result.split("\n")
        tension_lines = [line for line in lines if line.strip().startswith("L")]
        assert len(tension_lines) == 3
        # First two should have commas
        assert tension_lines[0].rstrip().endswith(",")
        assert tension_lines[1].rstrip().endswith(",")
        # Last should not have comma
        assert not tension_lines[2].rstrip().endswith(",")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
