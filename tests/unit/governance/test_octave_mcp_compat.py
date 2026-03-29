"""Smoke tests for octave-mcp 1.9.5 compatibility.

Verifies the octave-mcp package is importable and its core APIs
work with HestAI's usage patterns.
"""

import pytest

pytest.importorskip("octave_mcp", reason="octave-mcp not installed")


@pytest.mark.smoke
class TestOctaveMcpCompat:
    """Verify octave-mcp 1.9.5 compatibility with HestAI imports."""

    @pytest.mark.unit
    def test_core_imports(self):
        """Core imports used by context_steward.py work."""
        from octave_mcp import Document, parse
        from octave_mcp.core.ast_nodes import Assignment, Block, Section

        assert Document is not None
        assert parse is not None
        assert Assignment is not None
        assert Block is not None
        assert Section is not None

    @pytest.mark.unit
    def test_version_minimum(self):
        """Installed octave-mcp meets minimum version requirement."""
        import octave_mcp

        version = octave_mcp.__version__
        # Strip pre-release suffixes (e.g., "1.9.5.dev1", "1.9.5rc1")
        import re

        numeric_parts = re.findall(r"\d+", version.split("+")[0].split("-")[0])
        parts = [int(x) for x in numeric_parts[:3]]
        parts.extend([0] * (3 - len(parts)))  # Pad missing minor/patch
        # Must be >= 1.9.5
        assert tuple(parts) >= (1, 9, 5)

    @pytest.mark.unit
    def test_parse_simple_document(self):
        """octave-mcp can parse a simple OCTAVE document."""
        from octave_mcp import parse

        doc_text = (
            "===TEST===\n"
            "META:\n"
            "  TYPE::SKILL\n"
            '  VERSION::"1.0.0"\n'
            '  OCTAVE::"Olympian Common Text And Vocabulary Engine"\n'
            "CONTENT::value\n"
            "===END==="
        )
        doc = parse(doc_text)
        assert doc is not None

    @pytest.mark.unit
    def test_parse_with_warnings_available(self):
        """parse_with_warnings API exists (used for detailed diagnostics)."""
        from octave_mcp import parse_with_warnings

        assert callable(parse_with_warnings)
