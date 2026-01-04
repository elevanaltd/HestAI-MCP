"""
Tests for Operation Protocols - Odyssean Anchor semantic validation protocols.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase) - this file
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

Test Coverage:
- Protocol constants exist for odyssean anchor semantic checks
- Protocol constants follow existing pattern (operation-scoped, ~50 lines)
- compose_prompt() works with new protocols
- odyssean_anchor_semantic.py uses compose_prompt() with protocols

GitHub Issue: #131 (protocol refactoring)
ADR: docs/adr/adr-0036-odyssean-anchor-binding.md
"""

import pytest

# =============================================================================
# Protocol Constants Existence Tests
# =============================================================================


@pytest.mark.unit
class TestOdysseanAnchorProtocolConstants:
    """Test that Odyssean Anchor protocol constants exist in protocols.py."""

    def test_cognition_check_protocol_exists(self):
        """ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL constant exists."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL,
        )

        assert ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL is not None
        assert isinstance(ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL, str)
        assert len(ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL) > 0

    def test_tension_check_protocol_exists(self):
        """ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL constant exists."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL,
        )

        assert ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL is not None
        assert isinstance(ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL, str)
        assert len(ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL) > 0

    def test_commit_check_protocol_exists(self):
        """ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL constant exists."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL,
        )

        assert ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL is not None
        assert isinstance(ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL, str)
        assert len(ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL) > 0


# =============================================================================
# Protocol Content Tests
# =============================================================================


@pytest.mark.unit
class TestOdysseanAnchorProtocolContent:
    """Test that protocol constants have expected content structure."""

    def test_cognition_protocol_has_operation_header(self):
        """Cognition protocol follows OPERATION: header pattern."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL,
        )

        assert "OPERATION:" in ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL

    def test_cognition_protocol_describes_cognition_types(self):
        """Cognition protocol describes LOGOS, ETHOS, PATHOS types."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL,
        )

        # Should describe the three cognition types
        assert "LOGOS" in ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL
        assert "ETHOS" in ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL
        assert "PATHOS" in ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL

    def test_cognition_protocol_specifies_json_output(self):
        """Cognition protocol specifies JSON output format."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL,
        )

        assert "JSON" in ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL
        assert "appropriate" in ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL

    def test_tension_protocol_has_operation_header(self):
        """Tension protocol follows OPERATION: header pattern."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL,
        )

        assert "OPERATION:" in ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL

    def test_tension_protocol_references_constraints(self):
        """Tension protocol references constraint validation."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL,
        )

        # Should reference constraint validation
        assert "constraint" in ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL.lower()

    def test_tension_protocol_specifies_json_output(self):
        """Tension protocol specifies JSON output format."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL,
        )

        assert "JSON" in ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL
        assert "all_valid" in ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL

    def test_commit_protocol_has_operation_header(self):
        """Commit protocol follows OPERATION: header pattern."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL,
        )

        assert "OPERATION:" in ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL

    def test_commit_protocol_references_artifact_feasibility(self):
        """Commit protocol references artifact feasibility."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL,
        )

        # Should reference artifact/feasibility validation
        assert "artifact" in ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL.lower()
        assert "feasible" in ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL.lower()

    def test_commit_protocol_specifies_json_output(self):
        """Commit protocol specifies JSON output format."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL,
        )

        assert "JSON" in ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL
        assert "feasible" in ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL


# =============================================================================
# compose_prompt Integration Tests
# =============================================================================


@pytest.mark.unit
class TestComposePromptWithOdysseanAnchorProtocols:
    """Test that compose_prompt works with new Odyssean Anchor protocols."""

    def test_compose_prompt_with_cognition_protocol(self):
        """compose_prompt combines identity with cognition protocol."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL,
            compose_prompt,
        )

        result = compose_prompt(ODYSSEAN_ANCHOR_COGNITION_CHECK_PROTOCOL)

        # Should contain identity kernel and protocol
        assert "OPERATION:" in result
        assert "LOGOS" in result
        # Should be separated by ---
        assert "---" in result

    def test_compose_prompt_with_tension_protocol(self):
        """compose_prompt combines identity with tension protocol."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL,
            compose_prompt,
        )

        result = compose_prompt(ODYSSEAN_ANCHOR_TENSION_CHECK_PROTOCOL)

        assert "OPERATION:" in result
        assert "constraint" in result.lower()
        assert "---" in result

    def test_compose_prompt_with_commit_protocol(self):
        """compose_prompt combines identity with commit protocol."""
        from hestai_mcp.ai.prompts.protocols import (
            ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL,
            compose_prompt,
        )

        result = compose_prompt(ODYSSEAN_ANCHOR_COMMIT_CHECK_PROTOCOL)

        assert "OPERATION:" in result
        assert "feasible" in result.lower()
        assert "---" in result


# =============================================================================
# odyssean_anchor_semantic.py Integration Tests
# =============================================================================


@pytest.mark.unit
class TestOdysseanAnchorSemanticUsesProtocols:
    """Test that odyssean_anchor_semantic.py uses compose_prompt() with protocols."""

    def test_semantic_module_imports_compose_prompt(self):
        """odyssean_anchor_semantic imports compose_prompt from protocols."""
        from pathlib import Path

        # Read the source file
        source_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "hestai_mcp"
            / "mcp"
            / "tools"
            / "odyssean_anchor_semantic.py"
        )
        source_code = source_file.read_text()

        # Check for compose_prompt import
        assert (
            "from hestai_mcp.ai.prompts.protocols import" in source_code
            or "from hestai_mcp.ai.prompts.protocols import compose_prompt" in source_code
        ), "odyssean_anchor_semantic.py should import compose_prompt from protocols"

    def test_check_cognition_uses_compose_prompt(self):
        """check_cognition_appropriateness uses compose_prompt()."""
        import ast
        from pathlib import Path

        source_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "hestai_mcp"
            / "mcp"
            / "tools"
            / "odyssean_anchor_semantic.py"
        )
        source_code = source_file.read_text()

        # Parse AST and find check_cognition_appropriateness function
        tree = ast.parse(source_code)

        class ComposeFinder(ast.NodeVisitor):
            def __init__(self):
                self.in_cognition_func = False
                self.found_compose = False

            def visit_AsyncFunctionDef(self, node):
                if node.name == "check_cognition_appropriateness":
                    self.in_cognition_func = True
                    self.generic_visit(node)
                    self.in_cognition_func = False
                else:
                    self.generic_visit(node)

            def visit_Call(self, node):
                if (
                    self.in_cognition_func
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "compose_prompt"
                ):
                    self.found_compose = True
                self.generic_visit(node)

        finder = ComposeFinder()
        finder.visit(tree)

        assert finder.found_compose, (
            "check_cognition_appropriateness should call compose_prompt(). "
            "Found inline prompt instead of protocol reference."
        )

    def test_check_tension_uses_compose_prompt(self):
        """check_tension_relevance uses compose_prompt()."""
        import ast
        from pathlib import Path

        source_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "hestai_mcp"
            / "mcp"
            / "tools"
            / "odyssean_anchor_semantic.py"
        )
        source_code = source_file.read_text()

        tree = ast.parse(source_code)

        class ComposeFinder(ast.NodeVisitor):
            def __init__(self):
                self.in_tension_func = False
                self.found_compose = False

            def visit_AsyncFunctionDef(self, node):
                if node.name == "check_tension_relevance":
                    self.in_tension_func = True
                    self.generic_visit(node)
                    self.in_tension_func = False
                else:
                    self.generic_visit(node)

            def visit_Call(self, node):
                if (
                    self.in_tension_func
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "compose_prompt"
                ):
                    self.found_compose = True
                self.generic_visit(node)

        finder = ComposeFinder()
        finder.visit(tree)

        assert finder.found_compose, (
            "check_tension_relevance should call compose_prompt(). "
            "Found inline prompt instead of protocol reference."
        )

    def test_check_commit_uses_compose_prompt(self):
        """check_commit_feasibility uses compose_prompt()."""
        import ast
        from pathlib import Path

        source_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "hestai_mcp"
            / "mcp"
            / "tools"
            / "odyssean_anchor_semantic.py"
        )
        source_code = source_file.read_text()

        tree = ast.parse(source_code)

        class ComposeFinder(ast.NodeVisitor):
            def __init__(self):
                self.in_commit_func = False
                self.found_compose = False

            def visit_AsyncFunctionDef(self, node):
                if node.name == "check_commit_feasibility":
                    self.in_commit_func = True
                    self.generic_visit(node)
                    self.in_commit_func = False
                else:
                    self.generic_visit(node)

            def visit_Call(self, node):
                if (
                    self.in_commit_func
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "compose_prompt"
                ):
                    self.found_compose = True
                self.generic_visit(node)

        finder = ComposeFinder()
        finder.visit(tree)

        assert finder.found_compose, (
            "check_commit_feasibility should call compose_prompt(). "
            "Found inline prompt instead of protocol reference."
        )

    def test_no_inline_system_prompts_in_semantic_checks(self):
        """No inline system prompts should exist in semantic check functions."""
        import ast
        from pathlib import Path

        source_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "hestai_mcp"
            / "mcp"
            / "tools"
            / "odyssean_anchor_semantic.py"
        )
        source_code = source_file.read_text()

        tree = ast.parse(source_code)

        check_functions = {
            "check_cognition_appropriateness",
            "check_tension_relevance",
            "check_commit_feasibility",
        }

        class InlinePromptFinder(ast.NodeVisitor):
            def __init__(self):
                self.current_func = None
                self.inline_prompts = []

            def visit_AsyncFunctionDef(self, node):
                if node.name in check_functions:
                    self.current_func = node.name
                    self.generic_visit(node)
                    self.current_func = None
                else:
                    self.generic_visit(node)

            def visit_Assign(self, node):
                if self.current_func:
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "system_prompt":
                            # Found inline system_prompt assignment
                            self.inline_prompts.append(f"{self.current_func}:line {node.lineno}")
                self.generic_visit(node)

        finder = InlinePromptFinder()
        finder.visit(tree)

        assert len(finder.inline_prompts) == 0, (
            f"Found inline system_prompt assignments in: {finder.inline_prompts}. "
            "These should be replaced with compose_prompt(PROTOCOL_CONSTANT)."
        )
