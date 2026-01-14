"""
HestAI MCP Server - Dual-Layer Context Architecture (ADR-0007).

This MCP server provides context management tools for AI agents:
- clock_in: Register session start and return context paths
- clock_out: Archive session transcript with OCTAVE compression
- odyssean_anchor: Validate and complete agent identity vector (RAPH Vector v4.0)
- document_submit: Submit documents to .hestai/ (TODO - Phase 4)

Architecture:
- System Governance: .hestai-sys/ delivered by MCP (not committed)
- Project Documentation: .hestai/ committed (single writer via MCP tools)
- Hub: Bundled with MCP server package (no external HESTAI_HUB_ROOT dependency)
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from hestai_mcp.modules.tools.bind import bind
from hestai_mcp.modules.tools.clock_in import clock_in_async, validate_working_dir
from hestai_mcp.modules.tools.clock_out import clock_out
from hestai_mcp.modules.tools.odyssean_anchor import odyssean_anchor

# Load .env file for HESTAI_PROJECT_ROOT and other configuration
# This must happen BEFORE bootstrap_system_governance() is called
load_dotenv()

logger = logging.getLogger(__name__)

# Critical-Engineer: consulted for Governance injection target validation + clock_out target hardening


def _validate_project_root(project_root: Path) -> None:
    """Validate project root before writing any governance artifacts.

    Fail-closed: project_root must exist and be a directory.
    """
    if not project_root.exists():
        raise FileNotFoundError(f"Project root not found: {project_root}")
    if not project_root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {project_root}")


def _validate_project_identity(project_root: Path) -> None:
    """Validate the target directory is a real project root.

    Fail-closed: prevent governance injection into arbitrary directories.

    Accepted markers (any-of):
    - .git (directory or file, to support worktrees)
    - .hestai (directory)
    """
    git_marker = project_root / ".git"
    hestai_marker = project_root / ".hestai"

    if git_marker.exists():
        return

    if hestai_marker.exists() and hestai_marker.is_dir():
        return

    raise RuntimeError(
        f"Refusing governance injection: target is not a project root (missing .git/.hestai): {project_root}"
    )


def _check_governance_opt_in(project_root: Path) -> bool:
    """Check if project has opted in to governance injection.

    Projects opt in by having HESTAI_GOVERNANCE_ENABLED in .env or
    by having a .hestai directory already present.

    Returns:
        True if project has opted in, False otherwise
    """
    # Check if .hestai directory exists (already using HestAI)
    if (project_root / ".hestai").exists():
        return True

    # Check for .env file with HESTAI_GOVERNANCE_ENABLED
    env_file = project_root / ".env"
    if env_file.exists():
        try:
            content = env_file.read_text()
            # Look for HESTAI_GOVERNANCE_ENABLED=true or =1
            import re

            pattern = r"^\s*HESTAI_GOVERNANCE_ENABLED\s*=\s*(true|1|yes)\s*$"
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                return True
        except Exception:
            pass

    return False


def _ensure_gitignore_entry(project_root: Path) -> None:
    """Ensure .hestai-sys/ is in .gitignore.

    Creates .gitignore if it doesn't exist, or appends the entry if missing.
    """
    gitignore_path = project_root / ".gitignore"
    entry = ".hestai-sys/"

    # Check if entry already exists
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        # Check for exact entry or with leading slash
        if entry in content or f"/{entry}" in content:
            return
        # Append to existing file
        with gitignore_path.open("a") as f:
            # Add newline if file doesn't end with one
            if not content.endswith("\n"):
                f.write("\n")
            f.write("\n# HestAI system governance (auto-added, not committed)\n")
            f.write(f"{entry}\n")
    else:
        # Create new .gitignore
        with gitignore_path.open("w") as f:
            f.write("# HestAI system governance (auto-added, not committed)\n")
            f.write(f"{entry}\n")

    logger.info(f"Added {entry} to .gitignore")


# Create server instance
app = Server("hestai-mcp")


def get_hub_path() -> Path:
    """Get the bundled hub path.

    The hub is shipped inside the Python package as `_bundled_hub/` so that
    discovery works in both editable (repo) installs and installed wheels.

    Returns:
        Path to bundled hub directory

    Raises:
        FileNotFoundError: If bundled hub directory doesn't exist
    """
    # server.py lives at: hestai_mcp/mcp/server.py
    # Bundled hub lives at: hestai_mcp/_bundled_hub/
    hub_path = Path(__file__).resolve().parent.parent / "_bundled_hub"

    if not hub_path.exists():
        raise FileNotFoundError(
            f"Bundled hub not found at {hub_path}. "
            "The hub must be packaged inside hestai_mcp/_bundled_hub/."
        )

    return hub_path


def get_hub_version() -> str:
    """Read hub version from bundled VERSION file.

    Fail-closed: VERSION must exist. If it doesn't, packaging is broken and
    governance cannot be trusted.

    Returns:
        Version string (e.g., "1.0.0")

    Raises:
        FileNotFoundError: If VERSION file is missing
    """
    version_file = get_hub_path() / "VERSION"
    if not version_file.exists():
        raise FileNotFoundError(f"Bundled hub VERSION file missing: {version_file}")
    return version_file.read_text().strip()


def inject_system_governance(project_root: Path) -> None:
    """Inject system governance files into .hestai-sys/.

    This operation is performed as an atomic swap:
    1) build a complete new tree in a temp dir
    2) rename temp -> .hestai-sys

    This avoids partially-injected states if the process is interrupted.

    Args:
        project_root: Project root directory

    Raises:
        FileNotFoundError: If required hub content is missing
    """
    _validate_project_root(project_root)
    _validate_project_identity(project_root)

    # Ensure .hestai-sys is in .gitignore before creating it
    _ensure_gitignore_entry(project_root)

    hub_path = get_hub_path()

    # Agents are now part of library directory
    required_dirs = ["governance", "library", "templates"]
    for d in required_dirs:
        if not (hub_path / d).exists():
            raise FileNotFoundError(f"Bundled hub missing required directory: {hub_path / d}")

    hestai_sys_dir = project_root / ".hestai-sys"
    tmp_dir = project_root / ".hestai-sys.__tmp__"
    old_dir = project_root / ".hestai-sys.__old__"

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files from bundled hub into tmp tree
    # This includes CONSTITUTION.md, README.md, and all subdirectories
    # Exclude __pycache__ and other temporary artifacts
    shutil.copytree(
        hub_path,
        tmp_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )

    # Write version marker into tmp tree
    (tmp_dir / ".version").write_text(get_hub_version())

    # Swap in the new tree
    if hestai_sys_dir.exists():
        if old_dir.exists():
            shutil.rmtree(old_dir)
        hestai_sys_dir.rename(old_dir)

    tmp_dir.rename(hestai_sys_dir)

    if old_dir.exists():
        shutil.rmtree(old_dir)

    logger.info(f"Injected system governance v{get_hub_version()} to {hestai_sys_dir}")


def ensure_system_governance(project_root: Path) -> dict[str, Any]:
    """Ensure .hestai-sys exists and matches the bundled Hub version.

    Idempotent behavior:
    - If opt-in is not present, skip governance injection
    - If .hestai-sys/.version matches the hub VERSION *and* required subdirs are
      present, do nothing.
    - Otherwise, (re)inject from the bundled hub.

    Returns a structured status dict for diagnostics.

    Raises:
        FileNotFoundError: if the bundled hub cannot be located/validated
    """
    _validate_project_root(project_root)
    _validate_project_identity(project_root)

    # Check if project has opted in to governance
    if not _check_governance_opt_in(project_root):
        logger.debug(f"Skipping governance for {project_root}: opt-in not present")
        return {"status": "skipped", "reason": "opt_in_required"}

    # Agents are now part of library directory
    required_dirs = ["governance", "library", "templates"]
    required_files = ["CONSTITUTION.md", "README.md"]

    hestai_sys_dir = project_root / ".hestai-sys"
    version_path = hestai_sys_dir / ".version"

    desired = get_hub_version()
    current = version_path.read_text().strip() if version_path.exists() else None

    # Check if required directories and files exist
    has_required_tree = (
        hestai_sys_dir.exists()
        and all((hestai_sys_dir / d).exists() for d in required_dirs)
        and all((hestai_sys_dir / f).exists() for f in required_files)
    )

    if current == desired and has_required_tree:
        return {"status": "up_to_date", "current": current, "desired": desired}

    inject_system_governance(project_root)
    return {
        "status": "injected" if current is None else "updated",
        "previous": current,
        "desired": desired,
    }


def bootstrap_system_governance(project_root: Path | None) -> dict[str, Any]:
    """Bootstrap governance before any agent/tool interactions.

    Creates .hestai-sys in the specified project root, or uses a smart default.
    Only injects governance if the project has opted in via:
    - HESTAI_GOVERNANCE_ENABLED=true in .env
    - Existing .hestai directory

    Args:
        project_root: explicit project root. If None, uses:
            1. HESTAI_PROJECT_ROOT env var if set
            2. Current working directory (CWD) as fallback

    Returns:
        Status dict with injection results
    """
    used_cwd_fallback = False

    if project_root is None:
        # Try env var first (for explicit control)
        raw = os.environ.get("HESTAI_PROJECT_ROOT")
        # User explicitly set a path: use it. Otherwise: CWD (debate-hall pattern)
        if raw:
            project_root = validate_working_dir(raw)
        else:
            used_cwd_fallback = True
            project_root = Path.cwd()
    else:
        _validate_project_root(project_root)

    try:
        _validate_project_identity(project_root)
    except RuntimeError:
        # Provide actionable guidance when implicit CWD fallback isn't a project root.
        if used_cwd_fallback:
            # Not a project root, skip governance injection silently
            logger.debug(f"Skipping governance: {project_root} is not a project root")
            return {"status": "skipped", "reason": "not_a_project_root"}
        raise

    # Delegate to ensure_system_governance which handles opt-in checking
    return ensure_system_governance(project_root)


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
        Tool(
            name="odyssean_anchor",
            description=(
                "Validate and complete agent identity vector (RAPH Vector v4.0). "
                "Validates BIND, TENSION, COMMIT sections and injects ARM. "
                "Returns validated anchor or retry guidance. "
                "Implements OA-I5: Odyssean Identity Binding."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Expected role name (must match BIND.ROLE)",
                    },
                    "vector_candidate": {
                        "type": "string",
                        "description": "Agent's BIND+TENSION+COMMIT sections",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session ID from clock_in for ARM injection",
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Project working directory path",
                    },
                    "tier": {
                        "type": "string",
                        "description": "Validation tier: quick, default, or deep",
                        "default": "default",
                    },
                    "retry_count": {
                        "type": "integer",
                        "description": "Current retry attempt (0, 1, 2)",
                        "default": 0,
                    },
                },
                "required": ["role", "vector_candidate", "session_id", "working_dir"],
            },
        ),
        Tool(
            name="bind",
            description=(
                "Bootstrap agent binding with low token usage. "
                "Enables two-tier agent discovery (.hestai-sys/library/agents → .claude/agents). "
                "Relies on server's ensure_system_governance() for .hestai-sys management. "
                "Security hardening: path validation, resource limits, and error handling."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Agent role name (e.g., 'implementation-lead')",
                    },
                    "topic": {
                        "type": "string",
                        "description": "Work focus area",
                        "default": "general",
                    },
                    "tier": {
                        "type": "string",
                        "description": "Binding tier: quick, standard, or deep",
                        "default": "standard",
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Project working directory path",
                    },
                },
                "required": ["role"],
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
        # Validate working_dir before any governance writes (fail-closed).
        working_dir_path = validate_working_dir(arguments["working_dir"])
        _validate_project_identity(working_dir_path)

        # Ensure governance is present in the target working directory.
        ensure_system_governance(working_dir_path)

        # Use async path with AI synthesis capability (Issue #56 fix)
        result = await clock_in_async(
            role=arguments["role"],
            working_dir=arguments["working_dir"],
            focus=arguments.get("focus", "general"),
            model=arguments.get("model"),
            enable_ai_synthesis=True,
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
            potential_session = (
                root / ".hestai" / "sessions" / "active" / session_id / "session.json"
            )
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
        actual_project_root = validate_working_dir(session_data["working_dir"])
        _validate_project_identity(actual_project_root)

        result = await clock_out(
            session_id=session_id,
            description=arguments.get("description", ""),
            project_root=actual_project_root,
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "odyssean_anchor":
        import json

        # Validate working_dir before any governance writes (fail-closed).
        working_dir_path = validate_working_dir(arguments["working_dir"])
        _validate_project_identity(working_dir_path)

        # Ensure governance is present in the target working directory.
        ensure_system_governance(working_dir_path)

        anchor_result = odyssean_anchor(
            role=arguments["role"],
            vector_candidate=arguments["vector_candidate"],
            session_id=arguments["session_id"],
            working_dir=arguments["working_dir"],
            tier=arguments.get("tier", "default"),
            retry_count=arguments.get("retry_count", 0),
        )

        # Convert result dataclass to dict for JSON serialization
        result_dict = {
            "success": anchor_result.success,
            "anchor": anchor_result.anchor,
            "errors": anchor_result.errors,
            "guidance": anchor_result.guidance,
            "retry_count": anchor_result.retry_count,
            "terminal": anchor_result.terminal,
        }

        return [TextContent(type="text", text=json.dumps(result_dict, indent=2))]

    elif name == "bind":
        import json

        # Ensure governance is present in the target directory if working_dir provided
        if "working_dir" in arguments and arguments["working_dir"]:
            working_dir_path = validate_working_dir(arguments["working_dir"])
            _validate_project_identity(working_dir_path)
            ensure_system_governance(working_dir_path)

        bind_result = bind(
            role=arguments["role"],
            topic=arguments.get("topic", "general"),
            tier=arguments.get("tier", "standard"),
            working_dir=arguments.get("working_dir"),
        )

        return [TextContent(type="text", text=json.dumps(bind_result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Start HestAI MCP server.

    Entry point for MCP server using stdio transport.

    Governance MUST be available before agents can do work.
    """
    # Fail-closed bootstrap: materialize .hestai-sys from bundled hub if needed.
    bootstrap_system_governance(None)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
