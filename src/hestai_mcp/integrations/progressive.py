from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationPointSpec:
    point_id: str
    stage: str  # NOW|SOON|LATER
    reference_token: str
    implementation_import: str | None
    contract_test_glob: str
    integration_test_glob: str


INTEGRATION_POINTS: tuple[IntegrationPointSpec, ...] = (
    IntegrationPointSpec(
        point_id="orchestra_map",
        stage="SOON",
        reference_token="INTEGRATION_POINT::orchestra_map",
        implementation_import="hestai_mcp.orchestra_map",
        contract_test_glob="tests/contracts/orchestra_map/test_*.py",
        integration_test_glob="tests/integration/orchestra_map/test_*.py",
    ),
    IntegrationPointSpec(
        point_id="living_artifacts",
        stage="SOON",
        reference_token="INTEGRATION_POINT::living_artifacts",
        implementation_import="hestai_mcp.living_artifacts",
        contract_test_glob="tests/contracts/living_artifacts/test_*.py",
        integration_test_glob="tests/integration/living_artifacts/test_*.py",
    ),
)
