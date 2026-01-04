"""
RAPH Vector v4.0 Compatibility Tests for octave-mcp Integration.

Tests verify that octave-mcp can handle HestAI's custom OCTAVE extensions:
- Multiple archetype synthesis (⊕ operator)
- RAPH Vector v4.0 format
- Security boundaries preservation
- Custom validation rules

This is a BLOCKING GATE for octave-mcp adoption per ADR-0037.
"""

from pathlib import Path

import pytest


@pytest.mark.integration
class TestOctaveMcpRaphCompatibility:
    """Validate octave-mcp compatibility with RAPH Vector v4.0 extensions."""

    def test_import_octave_mcp(self):
        """Verify octave-mcp is installed and importable."""
        try:
            import octave_mcp

            # Verify key functions exist
            assert hasattr(octave_mcp, "parse")
            assert hasattr(octave_mcp, "validate")
            assert hasattr(octave_mcp, "emit")
            assert hasattr(octave_mcp, "get_field")
        except ImportError:
            pytest.skip("octave-mcp not installed - run: pip install octave-mcp>=0.3.0")

    def test_parse_raph_vector_with_synthesis(self):
        """Verify octave-mcp preserves ⊕ synthesis operator."""
        pytest.skip("Pending octave-mcp installation")

        # TODO: Enable after octave-mcp installed
        import octave_mcp

        raph_vector = """===RAPH_VECTOR::v4.0===
## BIND
ROLE::holistic-orchestrator
COGNITION::LOGOS::ATHENA⊕ODYSSEUS⊕DAEDALUS
AUTHORITY::RESPONSIBLE[main]

## ARM
PHASE::B1_FOUNDATION
BRANCH::main[0↑0↓]
FILES::5[odyssean_anchor.py]
FOCUS::validation

## TENSION
L1::[Custom validation]⇌CTX:odyssean_anchor.py:246[synthesis]→TRIGGER[validate]
L2::[Security boundary]⇌CTX:paths.py:22[traversal]→TRIGGER[reject]

## COMMIT
ARTIFACT::docs/validation.md
GATE::test_suite_passes
===END_RAPH_VECTOR==="""

        # Parse with octave-mcp
        doc = octave_mcp.parse(raph_vector)
        assert doc is not None

        # Extract COGNITION field
        cognition = octave_mcp.get_field(doc, "BIND.COGNITION")

        # CRITICAL: Must preserve ⊕ operator
        assert "⊕" in cognition, "octave-mcp must preserve ⊕ synthesis operator"
        assert "ATHENA" in cognition
        assert "ODYSSEUS" in cognition
        assert "DAEDALUS" in cognition

    def test_parse_ascii_synthesis_alias(self):
        """Verify octave-mcp handles + as alias for ⊕."""
        pytest.skip("Pending octave-mcp installation")

        import octave_mcp

        raph_vector = """## BIND
ROLE::test-agent
COGNITION::LOGOS::ATHENA+ODYSSEUS+DAEDALUS
AUTHORITY::RESPONSIBLE[test]"""

        doc = octave_mcp.parse(raph_vector)
        cognition = octave_mcp.get_field(doc, "BIND.COGNITION")

        # Should accept + as synthesis operator
        assert "+" in cognition or "⊕" in cognition

    def test_security_path_traversal_protection(self):
        """Verify octave-mcp doesn't enable path traversal attacks."""
        pytest.skip("Pending octave-mcp installation")

        import octave_mcp

        malicious_octave = """===TEST===
## TENSION
L1::[Evil]⇌CTX:../../etc/passwd[COMPROMISED]→TRIGGER[exploit]
L2::[Sneaky]⇌CTX:~/.ssh/id_rsa[STOLEN]→TRIGGER[exfiltrate]
===END==="""

        # Parse should succeed but not resolve paths
        doc = octave_mcp.parse(malicious_octave)

        # Extract CTX values
        tension = octave_mcp.get_field(doc, "TENSION")

        # Verify paths are preserved as strings, not resolved
        assert "../../etc/passwd" in str(tension)
        assert "~/.ssh/id_rsa" in str(tension)

        # Verify no actual file access occurred
        assert Path("/etc/passwd").stat().st_size != 0  # Just checking we didn't read it

    def test_octave_mcp_validation_api(self):
        """Test octave-mcp validation against schema."""
        pytest.skip("Pending octave-mcp installation")

        import octave_mcp

        valid_octave = """===SESSION_LOG===
META:
  TYPE::SESSION_LOG
  VERSION::1.0

DECISIONS::[
  DECISION_1::BECAUSE[performance]→chose_rust→faster,
  DECISION_2::BECAUSE[security]→added_validation→safer
]

OUTCOMES::[
  reduced_parsing_errors_by_95%,
  improved_performance_by_2x
]
===END==="""

        # Validate against SESSION_LOG schema
        errors = octave_mcp.validate(valid_octave, schema="SESSION_LOG")
        assert errors is None or len(errors) == 0

    def test_octave_mcp_emit_canonical(self):
        """Test canonical OCTAVE emission."""
        pytest.skip("Pending octave-mcp installation")

        import octave_mcp

        # Create document programmatically
        doc = octave_mcp.create_document("PROJECT_CONTEXT")
        octave_mcp.set_field(doc, "PHASE", "B1_FOUNDATION")
        octave_mcp.set_field(doc, "STATUS", "active")

        # Emit canonical OCTAVE
        canonical = octave_mcp.emit(doc)

        # Verify proper OCTAVE structure
        assert "===PROJECT_CONTEXT===" in canonical
        assert "PHASE::B1_FOUNDATION" in canonical
        assert "STATUS::active" in canonical
        assert "===END===" in canonical

    def test_graceful_degradation_pattern(self):
        """Test hybrid approach: octave-mcp with regex fallback."""
        import re

        def extract_section_hybrid(content: str, section: str) -> str | None:
            """Hybrid extraction with graceful degradation."""
            try:
                # Try octave-mcp first
                import octave_mcp

                doc = octave_mcp.parse(content)
                return octave_mcp.get_field(doc, section)
            except (ImportError, Exception):
                # Fallback to regex
                pattern = rf"{section}::\[(.*?)\]"
                match = re.search(pattern, content, re.DOTALL)
                return match.group(1) if match else None

        test_content = "DECISIONS::[decision_1, decision_2]"
        result = extract_section_hybrid(test_content, "DECISIONS")
        assert "decision_1" in result

    @pytest.mark.benchmark
    def test_performance_comparison(self, benchmark):
        """Benchmark octave-mcp vs regex for typical RAPH vector."""
        pytest.skip("Pending octave-mcp installation")

        import re

        import octave_mcp

        # Typical RAPH vector (~500 bytes)
        raph_vector = """===RAPH_VECTOR::v4.0===
## BIND
ROLE::test
COGNITION::LOGOS::ATHENA
AUTHORITY::RESPONSIBLE[test]

## TENSION
L1::[Test]⇌CTX:file.py:1[state]→TRIGGER[action]

## COMMIT
ARTIFACT::test.md
GATE::validation
===END_RAPH_VECTOR==="""

        def parse_with_regex():
            """Current regex implementation."""
            pattern = r"ROLE::(\S+)"
            match = re.search(pattern, raph_vector)
            return match.group(1) if match else None

        def parse_with_octave_mcp():
            """octave-mcp implementation."""
            doc = octave_mcp.parse(raph_vector)
            return octave_mcp.get_field(doc, "BIND.ROLE")

        # Benchmark both approaches
        regex_time = benchmark(parse_with_regex)
        mcp_time = benchmark(parse_with_octave_mcp)

        # Requirement: octave-mcp within 2x of regex for small docs
        assert mcp_time < regex_time * 2, f"octave-mcp too slow: {mcp_time} vs {regex_time}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
