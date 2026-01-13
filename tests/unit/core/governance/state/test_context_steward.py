"""Tests for ContextSteward - Dynamic Governance State Synthesis Engine.

This module tests the governance engine that reads OCTAVE workflow documents
and synthesizes phase-specific constraints for agent context injection.
"""

from pathlib import Path

import pytest

from hestai_mcp.core.governance.state.context_steward import (
    ContextSteward,
    PhaseConstraints,
)


@pytest.fixture
def mock_workflow_content():
    """Mock OCTAVE workflow document for testing."""
    return """===OPERATIONAL_WORKFLOW===
META:
  TYPE::STANDARD
  VERSION::"1.0"
  STATUS::ACTIVE

WORKFLOW_PHASES:
  D0_MNEMOSYNE_GENESIS::IDEATION_SETUP
  SUBPHASES::"D0_01[sessions-manager]→session_structure"
  RACI::"R[sessions-manager]→A[sessions-manager]"
  DELIVERABLE::"Complete ideation session"
  ENTRY::[new_project_concept]
  EXIT::[ready_for_D1]
  B1_HERMES_COORDINATION::BUILD_EXECUTION_ROADMAP
  PURPOSE::"Validated architecture→actionable implementation plan"
  SUBPHASES::"B1_01[task-decomposer]→B1_02[workspace-architect]"
  RACI::"R[planning_specialists]→A[critical-engineer]"
  DELIVERABLES::["B1-BUILD-PLAN.md","B1-WORKSPACE.md"]
  QUALITY_GATE_MANDATORY::"NO src/ FILES WITHOUT PASSING: lint && typecheck && test"
  CRITERIA::[all_components_have_tasks,dependencies_mapped]

===END===
"""


@pytest.fixture
def mock_workflow_file(tmp_path, mock_workflow_content):
    """Create a temporary workflow file for testing."""
    workflow_file = tmp_path / "OPERATIONAL-WORKFLOW.oct.md"
    workflow_file.write_text(mock_workflow_content)
    return workflow_file


class TestContextSteward:
    """Test suite for ContextSteward governance engine."""

    def test_initialization(self, mock_workflow_file):
        """Test ContextSteward initializes with workflow document path."""
        steward = ContextSteward(workflow_path=mock_workflow_file)
        assert steward.workflow_path == mock_workflow_file

    def test_synthesize_active_state_d0_phase(self, mock_workflow_file):
        """Test synthesis of D0 phase constraints."""
        steward = ContextSteward(workflow_path=mock_workflow_file)
        constraints = steward.synthesize_active_state(phase="D0")

        # Verify basic structure
        assert isinstance(constraints, PhaseConstraints)
        assert constraints.phase == "D0"

        # Verify phase-specific data
        assert "IDEATION_SETUP" in constraints.purpose
        assert "sessions-manager" in str(constraints.raci)
        assert "Complete ideation session" in constraints.deliverables
        assert "new_project_concept" in constraints.entry_criteria
        assert "ready_for_D1" in constraints.exit_criteria

    def test_synthesize_active_state_b1_phase(self, mock_workflow_file):
        """Test synthesis of B1 phase constraints."""
        steward = ContextSteward(workflow_path=mock_workflow_file)
        constraints = steward.synthesize_active_state(phase="B1")

        # Verify basic structure
        assert isinstance(constraints, PhaseConstraints)
        assert constraints.phase == "B1"

        # Verify phase-specific data
        # Purpose comes from explicit PURPOSE field in mock
        assert (
            "Validated architecture" in constraints.purpose
            or "BUILD_EXECUTION_ROADMAP" in constraints.purpose
        )
        assert "planning_specialists" in str(constraints.raci)
        assert "B1-BUILD-PLAN.md" in constraints.deliverables
        assert constraints.quality_gates and (
            "lint" in constraints.quality_gates or "NO src/" in constraints.quality_gates
        )

    def test_synthesize_active_state_invalid_phase(self, mock_workflow_file):
        """Test error handling for invalid phase."""
        steward = ContextSteward(workflow_path=mock_workflow_file)

        with pytest.raises(ValueError, match="Phase X99 not found"):
            steward.synthesize_active_state(phase="X99")

    def test_synthesize_active_state_missing_workflow_file(self):
        """Test error handling for missing workflow file."""
        fake_path = Path("/nonexistent/workflow.oct.md")
        steward = ContextSteward(workflow_path=fake_path)

        with pytest.raises(FileNotFoundError):
            steward.synthesize_active_state(phase="B1")

    def test_parse_octave_document(self, mock_workflow_file, mock_workflow_content):
        """Test OCTAVE document parsing using octave-mcp library."""
        steward = ContextSteward(workflow_path=mock_workflow_file)
        document = steward._parse_workflow()

        # Verify document structure
        assert document is not None
        # META is stored in document.meta, not as a section
        assert document.meta is not None
        assert "WORKFLOW_PHASES" in [s.key for s in document.sections]

    def test_extract_phase_section(self, mock_workflow_file):
        """Test extraction of phase-specific section from parsed document."""
        steward = ContextSteward(workflow_path=mock_workflow_file)
        document = steward._parse_workflow()

        # Extract B1 phase
        b1_section = steward._extract_phase_section(document, phase="B1")
        assert b1_section is not None

        # Verify section contains expected keys
        section_text = str(b1_section)
        assert "B1_HERMES_COORDINATION" in section_text
        assert "BUILD_EXECUTION_ROADMAP" in section_text

    def test_constraints_serialization(self, mock_workflow_file):
        """Test that PhaseConstraints can be serialized for context injection."""
        steward = ContextSteward(workflow_path=mock_workflow_file)
        constraints = steward.synthesize_active_state(phase="B1")

        # Should be serializable to dict/JSON for context injection
        constraints_dict = constraints.to_dict()
        assert isinstance(constraints_dict, dict)
        assert constraints_dict["phase"] == "B1"
        assert "purpose" in constraints_dict
        assert "deliverables" in constraints_dict

    def test_real_workflow_document_integration(self):
        """Integration test with actual OPERATIONAL-WORKFLOW.oct.md file."""
        # Use the actual bundled workflow file
        real_workflow = Path(
            "/Volumes/HestAI-MCP/worktrees/rccafp-review"
            "/src/hestai_mcp/_bundled_hub/governance/workflow"
            "/OPERATIONAL-WORKFLOW.oct.md"
        )

        if not real_workflow.exists():
            pytest.skip("Real workflow file not available")

        steward = ContextSteward(workflow_path=real_workflow)

        # Test synthesis with real file
        constraints = steward.synthesize_active_state(phase="B1")
        assert constraints.phase == "B1"
        # Purpose in real workflow is "Validated architecture→actionable implementation plan"
        assert "architecture" in constraints.purpose or "implementation" in constraints.purpose

        # Test multiple phases
        d0_constraints = steward.synthesize_active_state(phase="D0")
        assert d0_constraints.phase == "D0"

    def test_top_level_assignment_values(self, tmp_path):
        """Regression test: Ensure top-level assignments (Strategy 1) are captured."""
        # Note: Strategy 1 is when phases are top-level headers, not inside WORKFLOW_PHASES
        content = """===WORKFLOW===
META:
  TYPE::STANDARD
B1_HERMES_COORDINATION::BUILD_EXECUTION_ROADMAP
PURPOSE::"Top Level Purpose"
RACI::"R[Nobody]"
DELIVERABLES::["Item1"]
B2_HEPHAESTUS_FORGE::CODE_CONSTRUCTION
===END==="""
        f = tmp_path / "test_strat1.oct.md"
        f.write_text(content)

        steward = ContextSteward(workflow_path=f)
        constraints = steward.synthesize_active_state(phase="B1")

        assert constraints.phase == "B1"
        # Before fix: this returns empty string "" because _section_to_simple_value ignores non-block assignments
        assert "Top Level Purpose" in constraints.purpose
