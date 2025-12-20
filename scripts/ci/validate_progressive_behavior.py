from __future__ import annotations

import argparse
import glob
import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from hestai_mcp.integrations.progressive import INTEGRATION_POINTS, IntegrationPointSpec


@dataclass(frozen=True)
class IntegrationPointState:
    point_id: str
    stage: str
    referenced_in_code: bool
    implemented: bool
    contract_tests: list[str]
    integration_tests: list[str]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_module_present(module: str | None) -> bool:
    if not module:
        return False
    return importlib.util.find_spec(module) is not None


def _glob(rel_pattern: str) -> list[str]:
    root = _repo_root()
    matches = glob.glob(str(root / rel_pattern), recursive=True)
    return sorted(os.path.relpath(m, root) for m in matches if Path(m).is_file())


def _code_references_token(token: str) -> bool:
    if not token:
        return False
    root = _repo_root()
    for path in root.joinpath("src").rglob("*.py"):
        if "src/hestai_mcp/integrations/" in str(path).replace("\\", "/"):
            continue
        try:
            if token in path.read_text(encoding="utf-8"):
                return True
        except OSError:
            continue
    return False


def _compute_states() -> list[IntegrationPointState]:
    states: list[IntegrationPointState] = []
    for spec in INTEGRATION_POINTS:
        if not isinstance(spec, IntegrationPointSpec):
            raise TypeError("integration_specs_must_be_IntegrationPointSpec")

        point_id = spec.point_id
        stage = spec.stage
        token = spec.reference_token
        impl = spec.implementation_import
        contract_glob = spec.contract_test_glob
        integration_glob = spec.integration_test_glob

        referenced = _code_references_token(token)
        implemented = _is_module_present(impl)
        contract_tests = _glob(contract_glob)
        integration_tests = _glob(integration_glob)
        states.append(
            IntegrationPointState(
                point_id=point_id,
                stage=stage,
                referenced_in_code=referenced,
                implemented=implemented,
                contract_tests=contract_tests,
                integration_tests=integration_tests,
            )
        )
    return states


def _validate(states: list[IntegrationPointState]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    run_integration = False

    for state in states:
        stage = state.stage.upper()
        implemented = state.implemented
        referenced = state.referenced_in_code

        if stage not in {"NOW", "SOON", "LATER"}:
            errors.append(f"invalid_stage:{state.point_id}:{state.stage}")
            continue

        if stage == "NOW":
            if not implemented:
                errors.append(f"now_requires_implementation:{state.point_id}")
            if len(state.integration_tests) == 0:
                errors.append(f"now_requires_integration_tests:{state.point_id}")
            run_integration = True

        if stage == "SOON":
            if implemented:
                errors.append(f"soon_but_implemented:update_stage_to_NOW:{state.point_id}")
            if len(state.integration_tests) > 0:
                errors.append(f"soon_forbids_integration_tests:{state.point_id}")
            if referenced and len(state.contract_tests) == 0:
                errors.append(f"soon_referenced_requires_contract_tests:{state.point_id}")

        if stage == "LATER":
            if implemented:
                errors.append(f"later_but_implemented:update_stage_to_NOW:{state.point_id}")
            if referenced:
                errors.append(f"later_forbids_code_reference:{state.point_id}")
            if len(state.contract_tests) > 0:
                errors.append(f"later_forbids_contract_tests:{state.point_id}")
            if len(state.integration_tests) > 0:
                errors.append(f"later_forbids_integration_tests:{state.point_id}")

    return run_integration, errors


def _write_github_output(path: str, run_integration: bool) -> None:
    Path(path).write_text(
        f"run_integration={'true' if run_integration else 'false'}\n", encoding="utf-8"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-output", default=None)
    args = parser.parse_args(argv)

    states = _compute_states()
    run_integration, errors = _validate(states)

    if args.github_output:
        _write_github_output(args.github_output, run_integration)

    if errors:
        for err in errors:
            print(f"PROGRESSIVE_BEHAVIOR_ERROR::{err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
