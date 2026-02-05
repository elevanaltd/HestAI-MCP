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
    1. Check .hestai-sys/library/agents/{role}.oct.md
    2. Fall back to .claude/agents/{role}.oct.md

    Validates role to prevent path traversal before discovery.
    """
    # Security: Validate role first
    if not _validate_role(role):
        return None

    try:
        # First try .hestai-sys/library/agents
        hestai_agent = Path.cwd() / ".hestai-sys" / "library" / "agents" / f"{role}.oct.md"
        if hestai_agent.exists() and ".hestai-sys/library/agents" in str(hestai_agent.resolve()):
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


def _normalize_tier_for_anchor(tier: str) -> str:
    """Normalize bind tier to Odyssean Anchor tier names.

    bind tool historically used: quick | standard | deep
    odyssean_anchor expects:      quick | default  | deep
    """
    if tier == "standard":
        return "default"
    if tier in {"quick", "deep", "default"}:
        return tier
    # Fail-closed to default semantics if unknown
    return "default"


def _bind_todos() -> list[dict[str, str]]:
    """Return the canonical 7-step bind TODO list.

    This mirrors the /bind command ceremony steps.
    """
    return [
        {"content": "T0: TodoWrite", "status": "in_progress", "activeForm": "Sequencing"},
        {"content": "T1: Constitution", "status": "pending", "activeForm": "Identity"},
        {"content": "T2: clock_in + ARM", "status": "pending", "activeForm": "Context"},
        {"content": "T3: TENSION", "status": "pending", "activeForm": "Cognitive proof"},
        {"content": "T4: COMMIT", "status": "pending", "activeForm": "Contract"},
        {"content": "T5: Odyssean Anchor", "status": "pending", "activeForm": "MCP validation"},
        {"content": "T6: Dashboard", "status": "pending", "activeForm": "Summary"},
    ]


def _build_command_steps(
    *,
    role: str,
    focus: str,
    working_dir: str,
    tier: str,
) -> str:
    """Build a command-style step sequence for agents to follow.

    Intentionally minimal: no prose between steps.
    """
    anchor_tier = _normalize_tier_for_anchor(tier)

    todos_lines = ["TODOS::["]
    for i, t in enumerate(_bind_todos()):
        comma = "," if i < 6 else ""
        todos_lines.append(
            f"  {{content:\"{t['content']}\",status:\"{t['status']}\",activeForm:\"{t['activeForm']}\"}}{comma}"
        )
    todos_lines.append("]")

    # Keep placeholders in-step (agent-authored steps: T3/T4)
    return "\n".join(
        [
            "⚠️ AGENT INSTRUCTION: You must strictly follow this binding sequence.",
            "1. Create these TODOs using 'create_todo_list'.",
            "2. Execute T0-T6 sequentially.",
            "",
        ]
        + todos_lines
        + [
            "",
            "T0::TodoWrite(TODOS)→mark_complete",
            f'T1::CONSTITUTION→Read(".hestai-sys/library/agents/{role}.oct.md")→EXTRACT[COGNITION,ARCHETYPES,MUST[2],NEVER[2]]→SET_AUTHORITY[main→RESPONSIBLE[scope]|sub→DELEGATED[parent_session]]→EMIT',
            f'T2::CLOCK_IN→mcp__hestai__clock_in(role:"{role}",working_dir:"{working_dir}",focus:"{focus}")→CAPTURE[SESSION_ID,CONTEXT_PATHS]→IF[FAIL]→STOP',
            "T2b::ARM_CONTEXT→Read(project_context)→Bash(git_log+status+branch+ahead_behind)→EXTRACT[PHASE,BRANCH,FILES]→EMIT",
            "T3::TENSION→GENERATE[L{N}::[constraint]⇌CTX:{path}[state]→TRIGGER[action]]→MIN_COUNT_PER_TIER→mark_complete",
            "T4::COMMIT→DECLARE[ARTIFACT::concrete_path,GATE::validation_method]→mark_complete",
            "T5::ANCHOR→BUILD_VECTOR[BIND+TENSION+COMMIT]→mcp__hestai__odyssean_anchor(role,vector,session_id,working_dir,tier)→HANDLE_RESULT",
            f'T5_ARGS::role="{role}" tier="{anchor_tier}" working_dir="{working_dir}"',
            "T6::DASHBOARD→EMIT[VECTOR_BLOCK+DASHBOARD_BLOCK]→mark_complete",
        ]
    )


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

    working_dir_str = str(working_dir_path)

    # Command-style sequence output (mirrors bind.md intent; agent follows steps)
    todos = _bind_todos()
    command_steps = _build_command_steps(
        role=role,
        focus=topic,
        working_dir=working_dir_str,
        tier=tier,
    )

    # Minimal dashboard response + command steps
    response = {
        "success": True,
        "role": role,
        "topic": topic,
        "tier": tier,
        "anchor_tier": _normalize_tier_for_anchor(tier),
        "cognition": cognition,
        "archetypes": archetypes,
        # Note: this is a lightweight stub; real session_id comes from clock_in.
        "session_id": f"session-{role}-{working_dir_path.name}",
        "agent_file": agent_file,
        "working_dir": working_dir_str,
        "todos": todos,
        "command_steps": command_steps,
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
