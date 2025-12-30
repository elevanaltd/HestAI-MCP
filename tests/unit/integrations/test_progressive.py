"""Tests for progressive integration registry.

Validates the data contract and structural integrity of INTEGRATION_POINTS
without testing runtime import behavior (handled by CI preflight scripts).
"""

import pytest

from hestai_mcp.integrations.progressive import (
    INTEGRATION_POINTS,
    IntegrationPointSpec,
)


class TestIntegrationPointSpec:
    """Tests for IntegrationPointSpec dataclass structure."""

    def test_integration_point_spec_is_frozen_dataclass(self) -> None:
        """IntegrationPointSpec must be immutable (frozen=True)."""
        spec = IntegrationPointSpec(
            point_id="test",
            stage="NOW",
            reference_token="INTEGRATION_POINT::test",
            implementation_import="hestai_mcp.test",
            contract_test_glob="tests/contracts/test/test_*.py",
            integration_test_glob="tests/integration/test/test_*.py",
        )
        with pytest.raises(AttributeError):
            spec.point_id = "modified"  # type: ignore[misc]

    def test_integration_point_spec_has_required_fields(self) -> None:
        """IntegrationPointSpec must have all required fields."""
        spec = IntegrationPointSpec(
            point_id="test",
            stage="NOW",
            reference_token="INTEGRATION_POINT::test",
            implementation_import="hestai_mcp.test",
            contract_test_glob="tests/contracts/test/test_*.py",
            integration_test_glob="tests/integration/test/test_*.py",
        )
        assert hasattr(spec, "point_id")
        assert hasattr(spec, "stage")
        assert hasattr(spec, "reference_token")
        assert hasattr(spec, "implementation_import")
        assert hasattr(spec, "contract_test_glob")
        assert hasattr(spec, "integration_test_glob")


class TestIntegrationPointsRegistry:
    """Tests for INTEGRATION_POINTS registry data integrity."""

    def test_registry_is_tuple(self) -> None:
        """INTEGRATION_POINTS must be a tuple for immutability."""
        assert isinstance(INTEGRATION_POINTS, tuple)

    def test_registry_is_not_empty(self) -> None:
        """INTEGRATION_POINTS must contain at least one entry."""
        assert len(INTEGRATION_POINTS) > 0

    def test_all_entries_are_integration_point_spec(self) -> None:
        """Each entry must be an IntegrationPointSpec instance."""
        for entry in INTEGRATION_POINTS:
            assert isinstance(
                entry, IntegrationPointSpec
            ), f"Entry {entry} is not IntegrationPointSpec"

    def test_stages_are_valid(self) -> None:
        """Stages must be NOW, SOON, or LATER per ADR-0056."""
        valid_stages = {"NOW", "SOON", "LATER"}
        for entry in INTEGRATION_POINTS:
            assert (
                entry.stage in valid_stages
            ), f"{entry.point_id} has invalid stage '{entry.stage}'"

    def test_point_ids_are_unique(self) -> None:
        """All point_id values must be unique."""
        point_ids = [entry.point_id for entry in INTEGRATION_POINTS]
        assert len(point_ids) == len(set(point_ids)), "Duplicate point_id found"

    def test_reference_tokens_follow_convention(self) -> None:
        """Reference tokens must follow INTEGRATION_POINT::{id} pattern."""
        for entry in INTEGRATION_POINTS:
            expected_token = f"INTEGRATION_POINT::{entry.point_id}"
            assert (
                entry.reference_token == expected_token
            ), f"{entry.point_id} has non-standard reference_token"

    def test_contract_test_globs_follow_convention(self) -> None:
        """Contract test globs must follow tests/contracts/{id}/ pattern."""
        for entry in INTEGRATION_POINTS:
            assert entry.contract_test_glob.startswith(
                "tests/contracts/"
            ), f"{entry.point_id} contract_test_glob does not follow convention"
            assert entry.contract_test_glob.endswith(
                "/test_*.py"
            ), f"{entry.point_id} contract_test_glob does not end with /test_*.py"

    def test_integration_test_globs_follow_convention(self) -> None:
        """Integration test globs must follow tests/integration/{id}/ pattern."""
        for entry in INTEGRATION_POINTS:
            assert entry.integration_test_glob.startswith(
                "tests/integration/"
            ), f"{entry.point_id} integration_test_glob does not follow convention"
            assert entry.integration_test_glob.endswith(
                "/test_*.py"
            ), f"{entry.point_id} integration_test_glob does not end with /test_*.py"

    def test_implementation_imports_are_valid_module_paths(self) -> None:
        """Implementation imports must be valid Python module paths."""
        for entry in INTEGRATION_POINTS:
            if entry.implementation_import is not None:
                # Check it looks like a valid module path
                assert entry.implementation_import.startswith(
                    "hestai_mcp"
                ), f"{entry.point_id} implementation_import does not start with hestai_mcp"
                # Check no invalid characters
                assert (
                    "/" not in entry.implementation_import
                ), f"{entry.point_id} implementation_import contains /"
                assert (
                    "\\" not in entry.implementation_import
                ), f"{entry.point_id} implementation_import contains \\"
