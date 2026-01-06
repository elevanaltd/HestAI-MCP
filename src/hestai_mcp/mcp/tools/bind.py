#!/usr/bin/env python3
"""
Simple MCP bind tool that replaces bind command and creates .hestai-sys directory.
Low token implementation for bootstrapping.
"""

import json
import sys
from pathlib import Path
from typing import Any


def ensure_hestai_sys_exists() -> bool:
    """Create minimal .hestai-sys structure if it doesn't exist."""
    hestai_sys = Path.cwd() / ".hestai-sys"

    if not hestai_sys.exists():
        # Create basic structure
        directories = ["library/commands", "library/specs", "agents", "skills"]

        for dir_path in directories:
            (hestai_sys / dir_path).mkdir(parents=True, exist_ok=True)

        # Create minimal README
        readme_content = "# HESTAI System Structure\n\ndirectory is read-only after initialization"
        (hestai_sys / "README.md").write_text(readme_content)

        return True
    return False


def discover_agent_file(role: str) -> str | None:
    """
    Two-tier discovery:
    1. Check .hestai-sys/agents/{role}.oct.md
    2. Fall back to .claude/agents/{role}.oct.md
    """
    # First try .hestai-sys
    hestai_agent = Path.cwd() / ".hestai-sys" / "agents" / f"{role}.oct.md"
    if hestai_agent.exists():
        return str(hestai_agent)

    # Fall back to .claude
    claude_agent = Path.home() / ".claude" / "agents" / f"{role}.oct.md"
    if claude_agent.exists():
        return str(claude_agent)

    return None


def parse_arguments(args: list[str]) -> dict[str, Any]:
    """Parse bind command arguments."""
    result = {"role": None, "topic": "general", "tier": "standard"}

    if not args:
        return result

    # Extract role (first argument)
    role_aliases = {
        "ho": "holistic-orchestrator",
        "ce": "critical-engineer",
        "il": "implementation-lead",
        "ta": "technical-architect",
        "ea": "error-architect",
        "ca": "completion-architect",
        "wa": "workspace-architect",
        "ss": "system-steward",
        "rs": "requirements-steward",
        "td": "task-decomposer",
        "crs": "code-review-specialist",
        "tmg": "test-methodology-guardian",
        "tis": "test-infrastructure-steward",
        "ute": "universal-test-engineer",
    }

    role = args[0]
    result["role"] = role_aliases.get(role, role)

    # Parse remaining args
    i = 1
    while i < len(args):
        arg = args[i]
        if arg == "--quick":
            result["tier"] = "quick"
            i += 1
        elif arg == "--deep":
            result["tier"] = "deep"
            i += 1
        elif arg.startswith('"') and arg.endswith('"'):
            result["topic"] = arg.strip('"')
            i += 1
        else:
            i += 1

    return result


def execute_bind(role: str, topic: str = "general", tier: str = "standard") -> dict[str, Any]:
    """Execute bind process minimally."""
    # Ensure .hestai-sys exists
    created = ensure_hestai_sys_exists()

    # Discover agent file
    agent_file = discover_agent_file(role)
    if not agent_file:
        return {
            "success": False,
            "error": f"Agent file not found for role: {role}",
            "attempted_paths": [
                str(Path.cwd() / ".hestai-sys" / "agents" / f"{role}.oct.md"),
                str(Path.home() / ".claude" / "agents" / f"{role}.oct.md"),
            ],
        }

    # Read agent constitution minimally
    try:
        agent_content = Path(agent_file).read_text()
    except Exception as e:
        return {"success": False, "error": f"Failed to read agent file: {e}"}

    # Extract key sections (minimal token extraction)
    lines = agent_content.split("\n")
    cognition = "Unknown"
    archetypes = "ATLAS"

    for line in lines:
        if "COGNITION::" in line:
            cognition = (
                line.split("COGNITION::")[1].strip()
                if "::" in line
                else line.split("COGNITION::")[1].strip()
            )
        elif "ARCHETYPES::" in line:
            archetypes = (
                line.split("ARCHETYPES::")[1].strip()
                if "::" in line
                else line.split("ARCHETYPES::")[1].strip()
            )
            break  # Stop after finding both for efficiency

    # Minimal dashboard response
    response = {
        "success": True,
        "hestai_sys_created": created,
        "role": role,
        "topic": topic,
        "tier": tier,
        "cognition": cognition,
        "archetypes": archetypes,
        "session_id": f"session-{role}-{Path.cwd().name}",
        "agent_file": agent_file,
        "hestai_sys_path": str(Path.cwd() / ".hestai-sys"),
    }

    return response


def main() -> int:
    """Main entry point for MCP tool."""
    import sys

    # Parse arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    parsed = parse_arguments(args)

    # Execute bind
    result = execute_bind(parsed["role"], parsed["topic"], parsed["tier"])

    # Output JSON for MCP
    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())


# Export bind function for MCP server
def bind(role: str, topic: str = "general", tier: str = "standard") -> dict[str, Any]:
    """Bind function for MCP server."""
    return execute_bind(role, topic, tier)
