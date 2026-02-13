import json
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# _validate_role
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validate_role_returns_false_for_none():
    """Line 23: _validate_role returns False when role is None."""
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role(None) is False


@pytest.mark.unit
def test_validate_role_returns_false_for_empty_string():
    """Line 23: _validate_role returns False when role is empty string."""
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role("") is False


@pytest.mark.unit
def test_validate_role_returns_true_for_valid_role():
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role("implementation-lead") is True


@pytest.mark.unit
def test_validate_role_rejects_path_traversal():
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role("../etc/passwd") is False


@pytest.mark.unit
def test_validate_role_rejects_forward_slash():
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role("some/role") is False


@pytest.mark.unit
def test_validate_role_rejects_backslash():
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role("some\\role") is False


@pytest.mark.unit
def test_validate_role_rejects_leading_dash():
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role("-dangerous") is False


@pytest.mark.unit
def test_validate_role_rejects_too_long():
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role("a" * 129) is False


@pytest.mark.unit
def test_validate_role_accepts_underscores():
    from hestai_mcp.modules.tools.bind import _validate_role

    assert _validate_role("my_role_name") is True


# ---------------------------------------------------------------------------
# discover_agent_file
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_discover_agent_file_returns_none_for_invalid_role():
    """Line 44: discover_agent_file returns None when role fails validation."""
    from hestai_mcp.modules.tools.bind import discover_agent_file

    result = discover_agent_file("../bad-role")
    assert result is None


@pytest.mark.unit
def test_discover_agent_file_finds_hestai_sys_agent(tmp_path, monkeypatch):
    """Primary path: discovers agent in .hestai-sys/library/agents/."""
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / ".hestai-sys" / "library" / "agents"
    agents_dir.mkdir(parents=True)
    agent_file = agents_dir / "test-role.oct.md"
    agent_file.write_text("COGNITION::ETHOS\n")

    from hestai_mcp.modules.tools.bind import discover_agent_file

    result = discover_agent_file("test-role")
    assert result is not None
    assert "test-role.oct.md" in result


@pytest.mark.unit
def test_discover_agent_file_falls_back_to_claude_agents(tmp_path, monkeypatch):
    """Lines 54-55: Falls back to .claude/agents/ when .hestai-sys not found."""
    monkeypatch.chdir(tmp_path)
    # No .hestai-sys directory exists

    # Create .claude/agents/ fallback in home directory
    fake_home = tmp_path / "fakehome"
    fake_home.mkdir()
    claude_agents = fake_home / ".claude" / "agents"
    claude_agents.mkdir(parents=True)
    agent_file = claude_agents / "fallback-role.oct.md"
    agent_file.write_text("COGNITION::LOGOS\n")

    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))

    from hestai_mcp.modules.tools.bind import discover_agent_file

    result = discover_agent_file("fallback-role")
    assert result is not None
    assert "fallback-role.oct.md" in result
    assert ".claude/agents" in result


@pytest.mark.unit
def test_discover_agent_file_returns_none_when_no_file_exists(tmp_path, monkeypatch):
    """Line 60: Returns None when no agent file exists in either location."""
    monkeypatch.chdir(tmp_path)
    fake_home = tmp_path / "fakehome"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))

    from hestai_mcp.modules.tools.bind import discover_agent_file

    result = discover_agent_file("nonexistent-role")
    assert result is None


@pytest.mark.unit
def test_discover_agent_file_handles_os_error(tmp_path, monkeypatch):
    """Lines 56-58: Returns None when OSError occurs during path resolution."""
    monkeypatch.chdir(tmp_path)

    from hestai_mcp.modules.tools.bind import discover_agent_file

    # Make Path.cwd() raise OSError after validation
    def broken_cwd():
        raise OSError("filesystem error")

    monkeypatch.setattr(Path, "cwd", staticmethod(broken_cwd))

    result = discover_agent_file("valid-role")
    assert result is None


@pytest.mark.unit
def test_discover_agent_file_handles_runtime_error(tmp_path, monkeypatch):
    """Lines 56-58: Returns None when RuntimeError occurs during resolution."""
    monkeypatch.chdir(tmp_path)

    from hestai_mcp.modules.tools.bind import discover_agent_file

    def broken_cwd():
        raise RuntimeError("symlink loop")

    monkeypatch.setattr(Path, "cwd", staticmethod(broken_cwd))

    result = discover_agent_file("valid-role")
    assert result is None


# ---------------------------------------------------------------------------
# parse_arguments
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_arguments_empty_args():
    """Line 67-68: Returns defaults for empty args."""
    from hestai_mcp.modules.tools.bind import parse_arguments

    result = parse_arguments([])
    assert result["role"] is None
    assert result["topic"] == "general"
    assert result["tier"] == "standard"


@pytest.mark.unit
def test_parse_arguments_role_extraction():
    """Line 94-95: Extracts first arg as role (passthrough when not alias)."""
    from hestai_mcp.modules.tools.bind import parse_arguments

    result = parse_arguments(["my-custom-role"])
    assert result["role"] == "my-custom-role"


@pytest.mark.unit
def test_parse_arguments_alias_mapping():
    """Lines 71-92: Maps known aliases to full role names."""
    from hestai_mcp.modules.tools.bind import parse_arguments

    result = parse_arguments(["ho"])
    assert result["role"] == "holistic-orchestrator"

    result = parse_arguments(["ce"])
    assert result["role"] == "critical-engineer"

    result = parse_arguments(["il"])
    assert result["role"] == "implementation-lead"

    result = parse_arguments(["ute"])
    assert result["role"] == "universal-test-engineer"


@pytest.mark.unit
def test_parse_arguments_quick_flag():
    """Lines 101-103: --quick flag sets tier to quick."""
    from hestai_mcp.modules.tools.bind import parse_arguments

    result = parse_arguments(["my-role", "--quick"])
    assert result["tier"] == "quick"


@pytest.mark.unit
def test_parse_arguments_deep_flag():
    """Lines 104-106: --deep flag sets tier to deep."""
    from hestai_mcp.modules.tools.bind import parse_arguments

    result = parse_arguments(["my-role", "--deep"])
    assert result["tier"] == "deep"


@pytest.mark.unit
def test_parse_arguments_quoted_topic():
    """Lines 107-109: Quoted string is extracted as topic."""
    from hestai_mcp.modules.tools.bind import parse_arguments

    result = parse_arguments(["my-role", '"Fix the login bug"'])
    assert result["topic"] == "Fix the login bug"


@pytest.mark.unit
def test_parse_arguments_unknown_args_skipped():
    """Lines 110-111: Unknown args are silently skipped."""
    from hestai_mcp.modules.tools.bind import parse_arguments

    result = parse_arguments(["my-role", "--unknown", "random-arg", "--deep"])
    assert result["role"] == "my-role"
    assert result["tier"] == "deep"
    assert result["topic"] == "general"


@pytest.mark.unit
def test_parse_arguments_combined_flags():
    """Multiple flags and topic together."""
    from hestai_mcp.modules.tools.bind import parse_arguments

    result = parse_arguments(["ta", "--quick", '"Design the API"'])
    assert result["role"] == "technical-architect"
    assert result["tier"] == "quick"
    assert result["topic"] == "Design the API"


# ---------------------------------------------------------------------------
# _normalize_tier
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_normalize_tier_standard_to_default():
    """Line 122-123: 'standard' maps to 'default'."""
    from hestai_mcp.modules.tools.bind import _normalize_tier

    assert _normalize_tier("standard") == "default"


@pytest.mark.unit
def test_normalize_tier_quick_passthrough():
    """Line 124-125: 'quick' passes through unchanged."""
    from hestai_mcp.modules.tools.bind import _normalize_tier

    assert _normalize_tier("quick") == "quick"


@pytest.mark.unit
def test_normalize_tier_deep_passthrough():
    """Line 124-125: 'deep' passes through unchanged."""
    from hestai_mcp.modules.tools.bind import _normalize_tier

    assert _normalize_tier("deep") == "deep"


@pytest.mark.unit
def test_normalize_tier_default_passthrough():
    """Line 124-125: 'default' passes through unchanged."""
    from hestai_mcp.modules.tools.bind import _normalize_tier

    assert _normalize_tier("default") == "default"


@pytest.mark.unit
def test_normalize_tier_unknown_falls_to_default():
    """Line 127: Unknown tier falls closed to 'default'."""
    from hestai_mcp.modules.tools.bind import _normalize_tier

    assert _normalize_tier("banana") == "default"
    assert _normalize_tier("") == "default"
    assert _normalize_tier("QUICK") == "default"


# ---------------------------------------------------------------------------
# execute_bind (existing tests + new error paths)
# ---------------------------------------------------------------------------


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

    from hestai_mcp.modules.tools.bind import bind

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
    assert "mcp__odyssean-anchor__anchor_request" in steps


@pytest.mark.unit
def test_bind_rejects_invalid_role_format():
    from hestai_mcp.modules.tools.bind import bind

    result = bind(role="../bad")
    assert result["success"] is False
    assert "error" in result


@pytest.mark.unit
def test_execute_bind_file_too_large(tmp_path, monkeypatch):
    """Lines 222-223: Returns error when agent file exceeds 1MB."""
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / ".hestai-sys" / "library" / "agents"
    agents_dir.mkdir(parents=True)

    # Create a file larger than 1MB
    large_content = "x" * (1024 * 1024 + 1)
    (agents_dir / "large-role.oct.md").write_text(large_content)

    from hestai_mcp.modules.tools.bind import execute_bind

    result = execute_bind("large-role", working_dir=str(tmp_path))
    assert result["success"] is False
    assert "too large" in result["error"]


@pytest.mark.unit
def test_execute_bind_read_exception(tmp_path, monkeypatch):
    """Lines 228-229: Returns error when agent file read raises exception."""
    monkeypatch.chdir(tmp_path)

    from hestai_mcp.modules.tools.bind import execute_bind

    # Mock discover_agent_file to return a path to a non-existent file
    # This bypasses discovery but causes Path.stat() to fail in execute_bind
    fake_agent_path = str(tmp_path / "nonexistent-agent.oct.md")
    monkeypatch.setattr(
        "hestai_mcp.modules.tools.bind.discover_agent_file",
        lambda role: fake_agent_path,
    )

    result = execute_bind("broken-role", working_dir=str(tmp_path))
    assert result["success"] is False
    assert "Failed to read agent file" in result["error"]


@pytest.mark.unit
def test_execute_bind_agent_not_found(tmp_path, monkeypatch):
    """Lines 210-214: Returns error when agent file is not found."""
    monkeypatch.chdir(tmp_path)
    fake_home = tmp_path / "fakehome"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))

    from hestai_mcp.modules.tools.bind import execute_bind

    result = execute_bind("nonexistent-role", working_dir=str(tmp_path))
    assert result["success"] is False
    assert "not found" in result["error"]


@pytest.mark.unit
def test_execute_bind_with_working_dir(tmp_path, monkeypatch):
    """Verifies working_dir parameter is passed through to response."""
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / ".hestai-sys" / "library" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "test-role.oct.md").write_text("COGNITION::ETHOS\n")

    from hestai_mcp.modules.tools.bind import execute_bind

    result = execute_bind("test-role", working_dir=str(tmp_path))
    assert result["success"] is True
    assert result["working_dir"] == str(tmp_path.resolve())


@pytest.mark.unit
def test_execute_bind_extracts_cognition_and_archetypes(tmp_path, monkeypatch):
    """Verifies cognition and archetypes are extracted from agent file."""
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / ".hestai-sys" / "library" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "test-role.oct.md").write_text("COGNITION::PATHOS\nARCHETYPES::HERMES{speed}\n")

    from hestai_mcp.modules.tools.bind import execute_bind

    result = execute_bind("test-role", working_dir=str(tmp_path))
    assert result["success"] is True
    assert result["cognition"] == "PATHOS"
    assert result["archetypes"] == "HERMES{speed}"


# ---------------------------------------------------------------------------
# main() CLI entry point
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_main_success(tmp_path, monkeypatch):
    """Lines 282-293: main() parses sys.argv and outputs JSON."""
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / ".hestai-sys" / "library" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "test-role.oct.md").write_text("COGNITION::ETHOS\n")

    monkeypatch.setattr("sys.argv", ["bind", "test-role", "--quick"])

    from hestai_mcp.modules.tools.bind import main

    captured_output = []
    monkeypatch.setattr("builtins.print", lambda x: captured_output.append(x))

    exit_code = main()
    assert exit_code == 0
    assert len(captured_output) == 1
    output = json.loads(captured_output[0])
    assert output["success"] is True
    assert output["role"] == "test-role"
    assert output["tier"] == "quick"


@pytest.mark.unit
def test_main_failure_no_agent(tmp_path, monkeypatch):
    """Lines 282-293: main() returns 1 when bind fails."""
    monkeypatch.chdir(tmp_path)
    fake_home = tmp_path / "fakehome"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    monkeypatch.setattr("sys.argv", ["bind", "nonexistent-role"])

    from hestai_mcp.modules.tools.bind import main

    captured_output = []
    monkeypatch.setattr("builtins.print", lambda x: captured_output.append(x))

    exit_code = main()
    assert exit_code == 1
    output = json.loads(captured_output[0])
    assert output["success"] is False


@pytest.mark.unit
def test_main_no_args(tmp_path, monkeypatch):
    """Lines 285-289: main() with no args passes None role -> validation fails."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["bind"])

    from hestai_mcp.modules.tools.bind import main

    captured_output = []
    monkeypatch.setattr("builtins.print", lambda x: captured_output.append(x))

    exit_code = main()
    assert exit_code == 1
    output = json.loads(captured_output[0])
    assert output["success"] is False


# ---------------------------------------------------------------------------
# _bind_todos
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_bind_todos_returns_seven_steps():
    """Verify _bind_todos returns exactly 7 canonical steps."""
    from hestai_mcp.modules.tools.bind import _bind_todos

    todos = _bind_todos()
    assert len(todos) == 7
    assert todos[0]["content"] == "T0: TodoWrite"
    assert todos[0]["status"] == "in_progress"
    assert todos[6]["content"] == "T6: Dashboard"


# ---------------------------------------------------------------------------
# _build_command_steps
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_build_command_steps_contains_all_markers():
    """Verify command steps contain all required markers."""
    from hestai_mcp.modules.tools.bind import _build_command_steps

    steps = _build_command_steps(
        role="test-role",
        focus="testing",
        working_dir="/tmp/test",
        tier="standard",
    )

    assert "T0::TodoWrite" in steps
    assert "T1::CONSTITUTION" in steps
    assert "T2::CLOCK_IN" in steps
    assert "T3::TENSION" in steps
    assert "T4::COMMIT" in steps
    assert "T5::ANCHOR" in steps
    assert "T6::DASHBOARD" in steps
    assert "test-role" in steps
    assert "/tmp/test" in steps


@pytest.mark.unit
def test_build_command_steps_normalizes_tier():
    """Verify _build_command_steps normalizes the tier in anchor request."""
    from hestai_mcp.modules.tools.bind import _build_command_steps

    steps = _build_command_steps(
        role="test-role",
        focus="testing",
        working_dir="/tmp/test",
        tier="standard",
    )
    # Standard should be normalized to "default" in the anchor_request call
    assert 'tier:"default"' in steps
