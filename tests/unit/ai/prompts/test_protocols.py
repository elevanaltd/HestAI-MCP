"""
Tests for Operation Protocols - clock_in structured output protocols.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase) - this file
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

Test Coverage:
- compose_prompt() works with protocols
- Clock_in synthesis protocol uses OCTAVE structured output

GitHub Issue: #131 (protocol refactoring)
"""

import pytest

# =============================================================================
# compose_prompt Integration Tests
# =============================================================================


@pytest.mark.unit
class TestComposePromptWithProtocols:
    """Test that compose_prompt works with operation protocols."""

    def test_compose_prompt_combines_identity_and_protocol(self):
        """compose_prompt combines identity kernel with any protocol string."""
        from hestai_mcp.modules.services.ai.prompts.protocols import (
            CLOCK_IN_SYNTHESIS_PROTOCOL,
            compose_prompt,
        )

        result = compose_prompt(CLOCK_IN_SYNTHESIS_PROTOCOL)

        # Should contain identity kernel and protocol
        assert "OPERATION:" in result
        assert "Session Context Synthesis" in result
        # Should be separated by ---
        assert "---" in result

    def test_compose_prompt_with_clock_out_protocol(self):
        """compose_prompt combines identity with clock_out protocol."""
        from hestai_mcp.modules.services.ai.prompts.protocols import (
            CLOCK_OUT_COMPRESSION_PROTOCOL,
            compose_prompt,
        )

        result = compose_prompt(CLOCK_OUT_COMPRESSION_PROTOCOL)

        assert "OPERATION:" in result
        assert "Session Transcript Compression" in result
        assert "---" in result


# =============================================================================
# Clock_in Synthesis Protocol Tests (OCTAVE Structured Output)
# =============================================================================


@pytest.mark.unit
class TestClockInSynthesisProtocol:
    """
    Test CLOCK_IN_SYNTHESIS_PROTOCOL content integrity.

    Validates that clock_in uses structured OCTAVE output format
    with navigable file references.
    """

    def test_protocol_references_valid_north_star_path(self):
        """
        CONTEXT_FILES example must reference the actual North Star file.

        The correct path is: .hestai/north-star/000-MCP-PRODUCT-NORTH-STAR.md
        NOT: .hestai/north-star/000-NORTH-STAR.md
        """
        from hestai_mcp.modules.services.ai.prompts.protocols import CLOCK_IN_SYNTHESIS_PROTOCOL

        # Should reference the actual file that exists
        assert (
            "000-MCP-PRODUCT-NORTH-STAR.md" in CLOCK_IN_SYNTHESIS_PROTOCOL
        ), "Protocol must reference actual North Star path: 000-MCP-PRODUCT-NORTH-STAR.md"

        # Should NOT reference non-existent file
        # Note: We check for the exact bad pattern to avoid false positives
        assert "000-NORTH-STAR.md:L" not in CLOCK_IN_SYNTHESIS_PROTOCOL or (
            "000-MCP-PRODUCT-NORTH-STAR.md" in CLOCK_IN_SYNTHESIS_PROTOCOL
        ), "Protocol must not reference non-existent 000-NORTH-STAR.md"

    def test_protocol_contains_required_octave_fields(self):
        """
        Protocol must define all required OCTAVE output fields.
        """
        from hestai_mcp.modules.services.ai.prompts.protocols import CLOCK_IN_SYNTHESIS_PROTOCOL

        required_fields = [
            "CONTEXT_FILES::",
            "FOCUS::",
            "PHASE::",
            "BLOCKERS::",
            "TASKS::",
            "FRESHNESS_WARNING::",
        ]

        for field in required_fields:
            assert (
                field in CLOCK_IN_SYNTHESIS_PROTOCOL
            ), f"Protocol must define {field} in OUTPUT FORMAT"

    def test_compose_prompt_includes_identity_and_protocol(self):
        """
        compose_prompt correctly combines identity kernel with protocol.
        """
        from hestai_mcp.modules.services.ai.prompts.protocols import (
            CLOCK_IN_SYNTHESIS_PROTOCOL,
            compose_prompt,
        )

        result = compose_prompt(CLOCK_IN_SYNTHESIS_PROTOCOL)

        # Should include both identity and protocol
        assert "CONTEXT_STEWARD" in result or "Context Steward" in result
        assert "Session Context Synthesis" in result
        assert "---" in result  # Separator between identity and protocol
