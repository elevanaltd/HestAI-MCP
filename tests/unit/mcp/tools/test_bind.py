import pytest


@pytest.mark.unit
def test_bind_emits_command_steps_and_todos(tmp_path, monkeypatch):
    """bind() should emit a command-style 7-step sequence for the agent to follow."""
    # Ensure discovery finds a local .hestai-sys agent file
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / ".hestai-sys" / "library" / "agents"
    agents_dir.mkdir(parents=True)

    (agents_dir / "technical-architect.oct.md").write_text(
        """COGNITION::LOGOS
ARCHETYPES::ATLAS
MUST::[a,b]
NEVER::[c,d]
"""
    )

    from hestai_mcp.mcp.tools.bind import bind

    result = bind(
        role="technical-architect",
        topic="general",
        tier="standard",
        working_dir=str(tmp_path),
    )

    assert result["success"] is True
    assert result["anchor_tier"] == "default"

    assert "todos" in result
    assert isinstance(result["todos"], list)
    assert len(result["todos"]) == 7

    assert "command_steps" in result
    steps = result["command_steps"]
    assert isinstance(steps, str)

    # Step skeleton should be present
    assert "T0::TodoWrite" in steps
    assert "T1::CONSTITUTION" in steps
    assert "mcp__hestai__clock_in" in steps
    assert "mcp__hestai__odyssean_anchor" in steps


@pytest.mark.unit
def test_bind_rejects_invalid_role_format():
    from hestai_mcp.mcp.tools.bind import bind

    result = bind(role="../bad")
    assert result["success"] is False
    assert "error" in result
