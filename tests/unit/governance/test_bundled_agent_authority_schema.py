"""Regression guard: bundled-hub agent AUTHORITY schema and config path correctness.

Fixes #425 — two-layer anchor ceremony failure:
  1. odyssean.yaml was missing `paths.agents`; config first-found-wins loading
     silently discarded the user-global agents path override.
  2. ideator.oct.md and synthesizer.oct.md lacked AUTHORITY fields required by
     the SHANK validator regex: \\bAUTHORITY(?:_[A-Z_]+)?::

This test module is the regression guard that prevents both regressions from
silently re-entering the codebase.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
BUNDLED_AGENTS_DIR = REPO_ROOT / "src" / "hestai_mcp" / "_bundled_hub" / "library" / "agents"
ODYSSEAN_CONFIG = REPO_ROOT / "odyssean.yaml"

# SHANK validator regex from odyssean-anchor-mcp/src/odyssean_anchor/core/proof_validation.py
AUTHORITY_PATTERN = re.compile(r"\bAUTHORITY(?:_[A-Z_]+)?::")
ROLE_PATTERN = re.compile(r"\bROLE::(\S+)")
COGNITION_PATTERN = re.compile(r"\bCOGNITION::(\S+)")


def all_agent_files() -> list[Path]:
    return sorted(BUNDLED_AGENTS_DIR.glob("*.oct.md"))


# ---------------------------------------------------------------------------
# Section 1: SHANK validator gate — all bundled agents must pass
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent_file", all_agent_files(), ids=lambda p: p.stem)
def test_bundled_agent_passes_shank_authority_gate(agent_file: Path) -> None:
    """Every bundled agent must satisfy the SHANK validator ROLE/COGNITION/AUTHORITY gate.

    Regression guard for #425: ideator and synthesizer lacked AUTHORITY fields,
    causing the anchor ceremony to reject them with 'Agent file must contain
    ROLE::, COGNITION::, and AUTHORITY:: fields.'
    """
    content = agent_file.read_text(encoding="utf-8")

    has_role = bool(ROLE_PATTERN.search(content))
    has_cognition = bool(COGNITION_PATTERN.search(content))
    has_authority = bool(AUTHORITY_PATTERN.search(content))

    assert has_role, f"{agent_file.name}: missing ROLE:: field (SHANK gate failure)"
    assert has_cognition, f"{agent_file.name}: missing COGNITION:: field (SHANK gate failure)"
    assert has_authority, (
        f"{agent_file.name}: missing AUTHORITY field — add AUTHORITY_MANDATE, "
        "AUTHORITY_BLOCKING, or similar compound field. "
        "SHANK validator requires: \\bAUTHORITY(?:_[A-Z_]+)?::"
    )


# ---------------------------------------------------------------------------
# Section 2: odyssean.yaml agents path — config must not silently fall back
# ---------------------------------------------------------------------------


def test_odyssean_yaml_declares_agents_path() -> None:
    """odyssean.yaml must explicitly set paths.agents.

    Regression guard for #425: the project config was missing this key, causing
    first-found-wins config loading in odyssean-anchor-mcp to discard the
    user-global override (~/.odyssean-anchor/odyssean.yaml) that correctly pointed
    at .hestai-sys/library/agents. Without it, the server falls back to
    ~/.claude/agents which contains no HestAI roles.
    """
    assert ODYSSEAN_CONFIG.exists(), f"odyssean.yaml not found at {ODYSSEAN_CONFIG}"

    config = yaml.safe_load(ODYSSEAN_CONFIG.read_text(encoding="utf-8"))
    assert isinstance(config, dict), "odyssean.yaml must parse as a YAML mapping"

    paths = config.get("paths", {})
    assert "agents" in paths, (
        "odyssean.yaml is missing paths.agents — anchor server will fall back to "
        "~/.claude/agents (which does not contain HestAI roles). "
        "Add: agents: .hestai-sys/library/agents"
    )


def test_odyssean_yaml_agents_path_points_at_bundled_hub_runtime() -> None:
    """paths.agents must resolve to the runtime agents directory under .hestai-sys.

    The expected value is `.hestai-sys/library/agents` (relative). This is the
    runtime-delivered copy of `_bundled_hub/library/agents/` injected by the MCP
    server on startup.
    """
    config = yaml.safe_load(ODYSSEAN_CONFIG.read_text(encoding="utf-8"))
    agents_path = config.get("paths", {}).get("agents", "")

    assert agents_path == ".hestai-sys/library/agents", (
        f"paths.agents is '{agents_path}', expected '.hestai-sys/library/agents'. "
        "Correct value is the runtime-delivered agent directory. "
        "Source: _bundled_hub/library/agents/ → (MCP startup injection) → .hestai-sys/library/agents/"
    )
