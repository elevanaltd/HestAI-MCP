"""Integration tests for odyssean_anchor MCP server exposure.

These tests verify that the odyssean_anchor tool is properly exposed via
the MCP server and can be invoked through the MCP protocol.

Tests:
1. Tool appears in list_tools() response
2. call_tool("odyssean_anchor", {...}) works correctly
3. Result is proper JSON with expected fields

GitHub Issue: #11 (Phase 3 - MCP Server Integration)
ADR: docs/adr/adr-0036-odyssean-anchor-binding.md

Run with: uv run --python 3.11 -m pytest tests/integration/odyssean_anchor/test_mcp_integration.py -v -m integration
"""

import json
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
class TestOdysseanAnchorMCPIntegration:
    """Integration tests for odyssean_anchor MCP server exposure."""

    @pytest.mark.asyncio
    async def test_odyssean_anchor_in_list_tools(self) -> None:
        """Verify odyssean_anchor appears in MCP list_tools() response.

        The MCP server must expose odyssean_anchor as an available tool
        for agents to discover and invoke during the binding ceremony.
        """
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        # Extract tool names
        tool_names = [tool.name for tool in tools]

        assert "odyssean_anchor" in tool_names, (
            f"odyssean_anchor not found in available tools. " f"Found: {tool_names}"
        )

    @pytest.mark.asyncio
    async def test_odyssean_anchor_tool_schema(self) -> None:
        """Verify odyssean_anchor tool has correct schema.

        The tool schema must match the expected parameters per ADR-0036:
        - role (required): Expected role name
        - vector_candidate (required): Agent's BIND+TENSION+COMMIT sections
        - session_id (required): Session ID from clock_in
        - working_dir (required): Project working directory path
        - tier (optional): Validation tier
        - retry_count (optional): Retry attempt number
        """
        from hestai_mcp.mcp.server import list_tools

        tools = await list_tools()

        # Find odyssean_anchor tool
        oa_tool = None
        for tool in tools:
            if tool.name == "odyssean_anchor":
                oa_tool = tool
                break

        assert oa_tool is not None, "odyssean_anchor tool not found"

        # Verify schema structure
        schema = oa_tool.inputSchema
        assert schema["type"] == "object"

        # Required parameters
        required = schema.get("required", [])
        assert "role" in required
        assert "vector_candidate" in required
        assert "session_id" in required
        assert "working_dir" in required

        # Properties exist
        props = schema.get("properties", {})
        assert "role" in props
        assert "vector_candidate" in props
        assert "session_id" in props
        assert "working_dir" in props
        assert "tier" in props
        assert "retry_count" in props

    @pytest.mark.asyncio
    async def test_odyssean_anchor_call_tool_success(self, tmp_path: Path) -> None:
        """Verify call_tool("odyssean_anchor", {...}) works correctly.

        This test sets up a complete environment and invokes odyssean_anchor
        through the MCP call_tool handler, verifying end-to-end functionality.
        """
        from hestai_mcp.mcp.server import call_tool

        # Setup: Create project structure
        project_dir = tmp_path / "mcp_test_project"
        project_dir.mkdir()

        # Initialize git repository
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Create initial commit
        readme = project_dir / "README.md"
        readme.write_text("# MCP Test Project")
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Setup session directory and file
        session_id = "mcp-test-session"
        session_dir = project_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        session_file = session_dir / "session.json"
        session_file.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "role": "implementation-lead",
                    "focus": "mcp-integration-testing",
                    "working_dir": str(project_dir),
                }
            )
        )

        # Setup context directory
        context_dir = project_dir / ".hestai" / "context"
        context_dir.mkdir(parents=True)
        project_context = context_dir / "PROJECT-CONTEXT.oct.md"
        project_context.write_text(
            """===PROJECT_CONTEXT===
META:
  TYPE::PROJECT_CONTEXT
  PHASE::B1
===END===
"""
        )

        # Valid vector candidate
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[mcp_integration_test]

## TENSION (Cognitive Proof)
L1::[TDD_MANDATE]⇌CTX:README.md[exists]→TRIGGER[VERIFY]
L2::[STRUCTURAL_INTEGRITY]⇌CTX:PROJECT-CONTEXT.oct.md[B1]→TRIGGER[VALIDATE]

## COMMIT (Falsifiable Contract)
ARTIFACT::tests/integration/odyssean_anchor/test_mcp_integration.py
GATE::pytest -m integration
"""

        # Invoke through MCP call_tool
        result = await call_tool(
            name="odyssean_anchor",
            arguments={
                "role": "implementation-lead",
                "vector_candidate": vector,
                "session_id": session_id,
                "working_dir": str(project_dir),
                "tier": "default",
            },
        )

        # Verify result structure
        assert len(result) == 1
        assert result[0].type == "text"

        # Parse JSON response
        response_data = json.loads(result[0].text)

        # Verify expected fields per OdysseanAnchorResult dataclass
        assert "success" in response_data
        assert "anchor" in response_data
        assert "errors" in response_data
        assert "guidance" in response_data
        assert "retry_count" in response_data
        assert "terminal" in response_data

        # Verify success
        assert (
            response_data["success"] is True
        ), f"Expected success but got errors: {response_data['errors']}"
        assert response_data["anchor"] is not None
        assert "## ARM" in response_data["anchor"]

    @pytest.mark.asyncio
    async def test_odyssean_anchor_call_tool_failure_with_guidance(self, tmp_path: Path) -> None:
        """Verify call_tool returns proper error response with guidance.

        When validation fails, the MCP response should include errors
        and guidance for the agent to correct their vector.
        """
        from hestai_mcp.mcp.server import call_tool

        # Setup minimal project structure
        project_dir = tmp_path / "mcp_failure_test"
        project_dir.mkdir()

        subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        (project_dir / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Setup session
        session_id = "failure-test"
        session_dir = project_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "session.json").write_text(
            json.dumps({"session_id": session_id, "focus": "failure-testing"})
        )

        context_dir = project_dir / ".hestai" / "context"
        context_dir.mkdir(parents=True)
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Invalid vector - missing fields and generic values
        invalid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[test]

## TENSION (Cognitive Proof)
L1::[CONSTRAINT]⇌[state]→TRIGGER[ACTION]

## COMMIT (Falsifiable Contract)
ARTIFACT::response
GATE::review
"""

        result = await call_tool(
            name="odyssean_anchor",
            arguments={
                "role": "implementation-lead",
                "vector_candidate": invalid_vector,
                "session_id": session_id,
                "working_dir": str(project_dir),
                "tier": "default",
            },
        )

        # Parse response
        response_data = json.loads(result[0].text)

        # Verify failure with guidance
        assert response_data["success"] is False
        assert len(response_data["errors"]) > 0
        assert response_data["guidance"]
        assert len(response_data["guidance"]) > 0
        assert response_data["terminal"] is False

    @pytest.mark.asyncio
    async def test_odyssean_anchor_call_tool_unknown_raises(self) -> None:
        """Verify call_tool raises ValueError for unknown tools.

        This confirms the existing behavior is preserved after adding
        the odyssean_anchor handler.
        """
        from hestai_mcp.mcp.server import call_tool

        with pytest.raises(ValueError, match="Unknown tool"):
            await call_tool(name="nonexistent_tool", arguments={})
