"""
Test format guidance appears in error messages.

This test verifies that agents receive concrete format examples
when validation fails, not just abstract error messages.
"""

import json


class TestFormatGuidance:
    """Test that format guidance with examples appears in validation errors."""

    def test_bind_errors_include_format_template(self, tmp_path):
        """BIND validation errors include concrete format examples."""
        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-format-guide"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Invalid vector with BIND errors
        invalid_vector = """## BIND
ROLE::
COGNITION::INVALID
"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=invalid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
            retry_count=0,
        )

        # Verify format template appears in guidance
        assert "REQUIRED FORMAT (copy and modify this template):" in result.guidance
        assert "## BIND" in result.guidance
        assert "ROLE::your-agent-role" in result.guidance
        assert "COGNITION::LOGOS::ATLAS" in result.guidance
        assert "AUTHORITY::RESPONSIBLE[" in result.guidance
        assert "Valid types: ETHOS, LOGOS, PATHOS" in result.guidance

    def test_tension_errors_include_tier_specific_format(self, tmp_path):
        """TENSION validation errors include tier-specific format examples."""
        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-tension-format"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Valid BIND but no TENSION
        vector_with_tension_errors = """## BIND
ROLE::implementation-lead
COGNITION::LOGOS::ATLAS
AUTHORITY::RESPONSIBLE[test]

## TENSION

## COMMIT
ARTIFACT::file.py
GATE::pytest
"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector_with_tension_errors,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="deep",
            retry_count=0,
        )

        # Verify deep tier format appears
        assert "## TENSION (minimum 3 required for tier 'deep')" in result.guidance
        assert "CTX:path/to/file.md:10-20[state_description]" in result.guidance
        assert "line range BEFORE brackets" in result.guidance

    def test_format_guide_references_bind_ceremony(self, tmp_path):
        """Format guidance references full bind ceremony documentation."""
        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-reference"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        invalid_vector = "## BIND\nROLE::\n"

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=invalid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
            retry_count=0,
        )

        # Verify reference to full documentation
        assert ".hestai-sys/library/commands/bind.md" in result.guidance
        assert "full ceremony documentation" in result.guidance
