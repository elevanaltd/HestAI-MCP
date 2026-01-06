#!/usr/bin/env python3
"""
Simple MCP bind tool that replaces bind command and enables agent discovery.

Critical-Engineer: Consulted for path validation, resource limits, and security hardening.
.hestai-sys creation is delegated to the MCP server's ensure_system_governance() function
to maintain governance integrity per docs/hestai-sys-security-model.md.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any


def _validate_role(role: str | None) -> bool:
    """
    Validate role to prevent path traversal attacks.
    Rejects: path separators, leading /, drive letters, .., relative paths.
    """
    if not role:
        return False

    # Whitelist: alphanumeric, hyphens, underscores only
    # Max 128 chars (reasonable limit for role names)
    if not re.match(r"^[a-zA-Z0-9_-]{1,128}$", role):
        return False

    # Double-check: reject any path-like patterns
    return not ("/" in role or "\\" in role or role.startswith("-") or ".." in role)


def discover_agent_file(role: str) -> str | None:
    """
    Two-tier discovery:
    1. Check .hestai-sys/agents/{role}.oct.md
    2. Fall back to .claude/agents/{role}.oct.md

    Validates role to prevent path traversal before discovery.
    """
    # Security: Validate role first
    if not _validate_role(role):
        return None

    try:
        # First try .hestai-sys
        hestai_agent = Path.cwd() / ".hestai-sys" / "agents" / f"{role}.oct.md"
        if hestai_agent.exists() and ".hestai-sys/agents" in str(hestai_agent.resolve()):
            return str(hestai_agent)

        # Fall back to .claude
        claude_agent = Path.home() / ".claude" / "agents" / f"{role}.oct.md"
        if claude_agent.exists() and ".claude/agents" in str(claude_agent.resolve()):
            return str(claude_agent)
    except (OSError, RuntimeError):
        # Path resolution errors - return None
        return None

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


def execute_bind(
    role: str, topic: str = "general", tier: str = "standard", working_dir: str | None = None
) -> dict[str, Any]:
    """Execute bind process with security hardening.

    Note: .hestai-sys creation/management is delegated to ensure_system_governance()
    in the MCP server for proper governance integrity.
    """
    # Validate role first (before any file operations)
    if not _validate_role(role):
        return {
            "success": False,
            "error": "Invalid role format (must be alphanumeric, hyphens, underscores only)",
        }

    # Resolve working directory path if provided
    working_dir_path = Path(working_dir).resolve() if working_dir else Path.cwd()

    # Discover agent file
    agent_file = discover_agent_file(role)
    if not agent_file:
        return {
            "success": False,
            "error": f"Agent file not found for role: {role}",
        }

    # Read agent constitution with resource limits
    # Cap file size to 1MB to prevent resource exhaustion
    max_file_size = 1024 * 1024
    try:
        agent_path = Path(agent_file)
        file_size = agent_path.stat().st_size
        if file_size > max_file_size:
            return {
                "success": False,
                "error": f"Agent file too large ({file_size} > {max_file_size} bytes)",
            }
        agent_content = agent_path.read_text()
    except Exception as e:
        return {"success": False, "error": f"Failed to read agent file: {str(e)}"}

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
        "role": role,
        "topic": topic,
        "tier": tier,
        "cognition": cognition,
        "archetypes": archetypes,
        "session_id": f"session-{role}-{working_dir_path.name}",
        "agent_file": agent_file,
        "working_dir": str(working_dir_path),
    }

    return response


def main() -> int:
    """Main entry point for MCP tool."""
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
def bind(
    role: str, topic: str = "general", tier: str = "standard", working_dir: str | None = None
) -> dict[str, Any]:
    """Bind function for MCP server."""
    return execute_bind(role, topic, tier, working_dir)
