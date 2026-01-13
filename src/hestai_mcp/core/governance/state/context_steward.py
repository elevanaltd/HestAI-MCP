"""ContextSteward - Dynamic Governance State Synthesis Engine.

This module implements the "Brain" of ADR-0184's Fractal Modularization:
- Reads OCTAVE workflow policy documents (OPERATIONAL-WORKFLOW.oct.md)
- Parses using octave-mcp library
- Extracts phase-specific constraints
- Synthesizes transient context blocks for agent injection

Implements Dynamic Governance: Mechanism (Python) reads Policy (OCTAVE).
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from octave_mcp import Document, parse
from octave_mcp.core.ast_nodes import Assignment, Block, Section


@dataclass
class PhaseConstraints:
    """Phase-specific governance constraints synthesized for agent context.

    This structure represents the "Active State" injected into agent context
    via the ARM proof during clock_in, containing only relevant constraints.
    """

    phase: str
    purpose: str
    raci: str
    deliverables: list[str]
    entry_criteria: list[str]
    exit_criteria: list[str]
    quality_gates: str | None = None
    subphases: str | None = None

    def to_dict(self) -> dict:
        """Serialize to dictionary for context injection."""
        return asdict(self)


class ContextSteward:
    """Dynamic Governance Engine - Synthesizes phase-specific constraints.

    The ContextSteward reads OCTAVE workflow documents and extracts only
    the constraints relevant to a specific phase, enabling lightweight
    context injection without dumping full documents.

    Example:
        >>> steward = ContextSteward(workflow_path=Path("OPERATIONAL-WORKFLOW.oct.md"))
        >>> constraints = steward.synthesize_active_state(phase="B1")
        >>> print(constraints.purpose)
        "Validated architecture→actionable implementation plan"
    """

    def __init__(self, workflow_path: Path):
        """Initialize ContextSteward with path to workflow document.

        Args:
            workflow_path: Path to OPERATIONAL-WORKFLOW.oct.md file
        """
        self.workflow_path = workflow_path

    def synthesize_active_state(self, phase: str) -> PhaseConstraints:
        """Synthesize phase-specific constraints from workflow document.

        This is the core "Active State Synthesis" protocol:
        1. Read the OPERATIONAL-WORKFLOW.oct.md
        2. Parse using octave-mcp
        3. Extract section for the specified phase
        4. Return structured constraints

        Args:
            phase: Phase identifier (e.g., "D0", "B1", "B2")

        Returns:
            PhaseConstraints object ready for context injection

        Raises:
            FileNotFoundError: If workflow_path doesn't exist
            ValueError: If phase not found in workflow document
        """
        # Step 1: Parse the workflow document
        document = self._parse_workflow()

        # Step 2: Extract phase-specific section
        phase_data = self._extract_phase_section(document, phase)

        if not phase_data:
            raise ValueError(f"Phase {phase} not found in workflow document")

        # Step 3: Build structured constraints
        return self._build_constraints(phase, phase_data)

    def _parse_workflow(self) -> Document:
        """Parse OCTAVE workflow document using octave-mcp library.

        Returns:
            Parsed Document AST

        Raises:
            FileNotFoundError: If workflow file doesn't exist
        """
        if not self.workflow_path.exists():
            raise FileNotFoundError(f"Workflow document not found: {self.workflow_path}")

        content = self.workflow_path.read_text()
        return parse(content)

    def _extract_phase_section(self, document: Document, phase: str) -> dict[str, Any] | None:
        """Extract phase-specific data from parsed OCTAVE document.

        Handles two different OCTAVE structures:
        1. Flat structure: Phases as children of WORKFLOW_PHASES section
        2. Nested structure: Phases as top-level sections (real workflow file)

        Args:
            document: Parsed OCTAVE Document
            phase: Phase identifier (e.g., "D0", "B1")

        Returns:
            Dictionary containing phase data, or None if not found
        """
        phase_prefix = f"{phase}_"

        # STRATEGY 1: Try finding phase as a top-level section (real workflow structure)
        for section in document.sections:
            # Type check: section should be Assignment/Section/Block which all have 'key'
            if not isinstance(section, (Assignment, Section, Block)):
                continue
            if section.key.startswith(phase_prefix):
                # Found phase as top-level section
                phase_data: dict[str, Any] = {section.key: self._get_phase_marker_value(section)}
                # Collect subsequent sections until next phase marker
                start_collecting = False
                for s in document.sections:
                    # Type check for mypy
                    if not isinstance(s, (Assignment, Section, Block)):
                        continue
                    if s.key == section.key:
                        start_collecting = True
                        continue
                    if start_collecting:
                        # Stop if we hit another phase marker
                        if any(
                            s.key.startswith(f"{p}_")
                            for p in ["D0", "D1", "D2", "D3", "B0", "B1", "B2", "B3", "B4", "B5"]
                        ):
                            break
                        # Collect this section's data
                        value = self._section_to_simple_value(s)
                        phase_data[s.key] = value
                return phase_data

        # STRATEGY 2: Try finding phase within WORKFLOW_PHASES section (test mock structure)
        workflow_section: Assignment | Section | Block | None = None
        for section in document.sections:
            # Type check for mypy
            if not isinstance(section, (Assignment, Section, Block)):
                continue
            if section.key == "WORKFLOW_PHASES":
                workflow_section = section
                break

        if not workflow_section or not hasattr(workflow_section, "children"):
            return None

        phase_result: dict[str, Any] = {}
        collecting = False

        # Walk through children sequentially
        for child in workflow_section.children:
            if not hasattr(child, "key"):
                continue

            # Type narrowing for assignments that have 'key' and 'value'
            if not isinstance(child, (Assignment, Section, Block)):
                continue

            # Check if this is a phase marker
            if any(
                child.key.startswith(f"{p}_")
                for p in ["D0", "D1", "D2", "D3", "B0", "B1", "B2", "B3", "B4", "B5"]
            ):
                # This is a phase marker
                if child.key.startswith(phase_prefix):
                    # Found our target phase - Assignment has 'value' attribute
                    if isinstance(child, Assignment):
                        phase_result[child.key] = child.value
                    collecting = True
                else:
                    # Different phase - stop collecting if we were
                    if collecting:
                        break
                    collecting = False
            elif collecting and isinstance(child, Assignment):
                # Regular assignment belonging to current phase
                phase_result[child.key] = child.value

        return phase_result if phase_result else None

    def _get_phase_marker_value(self, section: Assignment | Section | Block) -> str:
        """Extract the value associated with a phase marker section.

        For real workflow, phase sections have a value like "IDEATION_SETUP".
        For test mocks, we use the first child value if available.
        """
        if hasattr(section, "value") and section.value:
            return str(section.value)
        if hasattr(section, "children") and section.children:
            first_child = section.children[0]
            if hasattr(first_child, "value"):
                return str(first_child.value)
        return ""

    def _section_to_simple_value(self, section: Assignment | Section | Block) -> str | list[str]:
        """Convert a section to a simple value (str or list).

        Used for extracting values from top-level phase sections.
        """
        if hasattr(section, "children") and section.children:
            # If section has multiple children, return as list
            if len(section.children) > 1:
                result = []
                for c in section.children:
                    if hasattr(c, "value"):
                        converted = self._convert_value(c.value)
                        if isinstance(converted, str):
                            result.append(converted)
                    else:
                        result.append(str(c))
                return result
            # Single child - return its value
            child = section.children[0]
            if hasattr(child, "value"):
                converted = self._convert_value(child.value)
                # Ensure we return str, not list
                if isinstance(converted, str):
                    return converted
                return str(converted)
        return ""

    def _section_to_dict(self, section: Assignment | Section | Block) -> dict[str, Any]:
        """Convert OCTAVE Block to dictionary.

        Args:
            section: OCTAVE Block object

        Returns:
            Dictionary representation of section
        """
        result = {}
        # octave-mcp Block objects have 'children' attribute
        if hasattr(section, "children"):
            for child in section.children:
                if hasattr(child, "key") and hasattr(child, "value"):
                    # Convert assignment value to appropriate Python type
                    value = self._convert_value(child.value)
                    result[child.key] = value
        return result

    def _convert_value(self, value: Any) -> str | list[Any]:
        """Convert OCTAVE value to Python type.

        Args:
            value: OCTAVE value object

        Returns:
            Converted Python value (str, list, dict, etc.)
        """
        # Handle different OCTAVE value types
        type_name = type(value).__name__

        if type_name == "ListValue":  # List type from octave-mcp
            # Extract items from ListValue
            return [self._convert_value(item) for item in value.items]
        elif hasattr(value, "value"):  # Scalar/String
            return str(value.value)
        elif isinstance(value, str):
            return value
        else:
            return str(value)

    def _build_constraints(self, phase: str, phase_data: dict) -> PhaseConstraints:
        """Build PhaseConstraints from extracted phase data.

        Args:
            phase: Phase identifier
            phase_data: Dictionary of phase-specific data

        Returns:
            Structured PhaseConstraints object
        """
        # Extract phase marker value (e.g., D0_MNEMOSYNE_GENESIS has value IDEATION_SETUP)
        phase_marker_value = None
        for key, value in phase_data.items():
            if key.startswith(f"{phase}_"):
                phase_marker_value = str(value)
                break

        # Extract common fields across all phases
        purpose = self._extract_field(phase_data, ["PURPOSE"])
        # If no explicit PURPOSE, use the phase marker value
        if not purpose and phase_marker_value:
            purpose = phase_marker_value

        raci = self._extract_field(phase_data, ["RACI"])
        deliverables = self._extract_list_field(phase_data, ["DELIVERABLE", "DELIVERABLES"])
        entry_criteria = self._extract_list_field(phase_data, ["ENTRY"])
        exit_criteria = self._extract_list_field(phase_data, ["EXIT"])
        quality_gates = self._extract_field(phase_data, ["QUALITY_GATE_MANDATORY", "QUALITY_GATES"])
        subphases = self._extract_field(phase_data, ["SUBPHASES"])

        return PhaseConstraints(
            phase=phase,
            purpose=purpose or f"Phase {phase}",
            raci=raci or "Not specified",
            deliverables=deliverables,
            entry_criteria=entry_criteria,
            exit_criteria=exit_criteria,
            quality_gates=quality_gates,
            subphases=subphases,
        )

    def _extract_field(self, data: dict, keys: list[str]) -> str | None:
        """Extract a single field value from phase data.

        Args:
            data: Phase data dictionary
            keys: List of possible key names to check

        Returns:
            Field value as string, or None if not found
        """
        for key in keys:
            if key in data:
                value = data[key]
                return str(value) if value else None
        return None

    def _extract_list_field(self, data: dict, keys: list[str]) -> list[str]:
        """Extract a list field value from phase data.

        Args:
            data: Phase data dictionary
            keys: List of possible key names to check

        Returns:
            List of values, or empty list if not found
        """
        for key in keys:
            if key in data:
                value = data[key]
                # Convert using our converter to handle ListValue objects
                converted = self._convert_value(value)
                if isinstance(converted, list):
                    return [str(v) for v in converted]
                elif converted:
                    # Single value - wrap in list
                    return [str(converted)]
        return []
