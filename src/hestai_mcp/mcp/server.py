"""
HestAI MCP Server - Dual-Layer Context Architecture (ADR-0007).

This MCP server provides context management tools for AI agents:
- clock_in: Register session start and return context paths
- clock_out: Archive session transcript with OCTAVE compression
- document_submit: Submit documents to .hestai/ (TODO - Phase 3)

Architecture:
- System Governance: .sys-runtime/ delivered by MCP (not committed)
- Project Documentation: .hestai/ committed (single writer via MCP tools)
"""

import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from hestai_mcp.mcp.tools.clock_in import clock_in
from hestai_mcp.mcp.tools.clock_out import clock_out

logger = logging.getLogger(__name__)

# Create server instance
app = Server("hestai-mcp")


def inject_system_governance(project_root: Path) -> None:
    """
    Inject system governance files into .hestai/.sys-runtime/.

    ADR-0007: System governance is delivered by MCP server at startup,
    not committed to git. This provides agents, rules, and templates.

    Args:
        project_root: Project root directory

    TODO: Implement in Phase 4
    - Read HESTAI_HUB_ROOT environment variable
    - Copy governance files to .sys-runtime/
    - Write version marker
    """
    sys_runtime = project_root / ".hestai" / ".sys-runtime"

    # TODO Phase 4: Implement governance injection
    # hub_root = os.environ.get("HESTAI_HUB_ROOT")
    # if hub_root:
    #     shutil.copytree(Path(hub_root) / "governance", sys_runtime)
    #     (sys_runtime / ".version").write_text(get_hub_version())

    logger.info(f"System governance injection (TODO): {sys_runtime}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available MCP tools.

    Returns:
        List of tool definitions for MCP protocol
    """
    return [
        Tool(
            name="clock_in",
            description=(
                "Register agent session start and return context paths. "
                "Creates session directory in .hestai/sessions/active/ and "
                "returns OCTAVE context file paths from .hestai/context/. "
                "ADR-0007: Uses direct .hestai/ directory (no symlinks/worktrees)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Agent role name (e.g., 'implementation-lead')",
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Project working directory path",
                    },
                    "focus": {
                        "type": "string",
                        "description": "Work focus area (e.g., 'b2-implementation')",
                        "default": "general",
                    },
                    "model": {
                        "type": "string",
                        "description": "Optional AI model identifier",
                    },
                },
                "required": ["role", "working_dir"],
            },
        ),
        Tool(
            name="clock_out",
            description=(
                "Archive agent session transcript and extract learnings. "
                "Compresses session transcript to OCTAVE format and "
                "archives to .hestai/sessions/archive/. "
                "Cleans up active session directory."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID from clock_in",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional session summary/description",
                        "default": "",
                    },
                },
                "required": ["session_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Execute MCP tool.

    Args:
        name: Tool name to execute
        arguments: Tool-specific arguments

    Returns:
        Tool execution results as TextContent

    Raises:
        ValueError: If tool name is unknown
    """
    if name == "clock_in":
        result = clock_in(
            role=arguments["role"],
            working_dir=arguments["working_dir"],
            focus=arguments.get("focus", "general"),
            model=arguments.get("model"),
        )
        import json

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "clock_out":
        import json

        # Read session metadata to get project_root
        session_id = arguments["session_id"]

        # Find session file - check all possible locations
        # Sessions are stored in {project}/.hestai/sessions/active/{session_id}/
        # We need to search for the session to find the project root
        possible_roots = [
            Path.cwd(),  # Current directory
            Path.cwd().parent,  # Parent directory
        ]

        session_file = None
        project_root = None

        for root in possible_roots:
            potential_session = root / ".hestai" / "sessions" / "active" / session_id / "session.json"
            if potential_session.exists():
                session_file = potential_session
                project_root = root
                break

        if not session_file or not project_root:
            raise FileNotFoundError(
                f"Session {session_id} not found. Searched in: {possible_roots}"
            )

        # Load session data to get the actual working_dir
        session_data = json.loads(session_file.read_text())
        actual_project_root = Path(session_data["working_dir"])

        result = clock_out(
            session_id=session_id,
            description=arguments.get("description", ""),
            project_root=actual_project_root,
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """
    Start HestAI MCP server.

    Entry point for MCP server using stdio transport.
    """
    # TODO Phase 4: Inject system governance on startup
    # project_root = Path.cwd()  # Or from environment variable
    # inject_system_governance(project_root)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
