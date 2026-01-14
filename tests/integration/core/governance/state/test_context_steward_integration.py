"""Integration tests for ContextSteward governance engine.

This module tests the integration between ContextSteward and real workflow policy documents
stored in the repository hub.
"""

from pathlib import Path

import pytest

from hestai_mcp.core.governance.state.context_steward import ContextSteward


class TestContextStewardIntegration:
    """Integration test suite for ContextSteward."""

    def test_real_workflow_document_integration(self):
        """Integration test with actual OPERATIONAL-WORKFLOW.oct.md file."""
        # Use the actual bundled workflow file
        real_workflow = (
            Path(__file__).resolve().parents[5]
            / "src"
            / "hestai_mcp"
            / "_bundled_hub"
            / "governance"
            / "workflow"
            / "OPERATIONAL-WORKFLOW.oct.md"
        )

        if not real_workflow.exists():
            pytest.skip(f"Real workflow file not found at: {real_workflow}")

        steward = ContextSteward(workflow_path=real_workflow)

        # Test synthesis with real file
        constraints = steward.synthesize_active_state(phase="B1")
        assert constraints.phase == "B1"
        # Purpose in real workflow is "Validated architecture→actionable implementation plan"
        assert "architecture" in constraints.purpose or "implementation" in constraints.purpose

        # Test multiple phases
        d0_constraints = steward.synthesize_active_state(phase="D0")
        assert d0_constraints.phase == "D0"
