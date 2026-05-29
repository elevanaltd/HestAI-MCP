===CI_PROGRESSIVE_TESTING===
META:
  NAME::"CI Progressive Testing"
  VERSION::"1.0"
  TYPE::WORKFLOW
  STATUS::ACTIVE
  PURPOSE::"Define NOW/SOON/LATER test routing and required CI gates"
  CONTRACT::HOLOGRAPHIC<parse_only_governance>
  CANONICAL::".hestai/rules/ci-progressive-testing.oct.md"
  SOURCE::".hestai/rules/ci-progressive-testing.oct.md"
§0::FOUNDATION
  NORTH_STAR::"docs/workflow/000-MCP-PRODUCT-NORTH-STAR.md"
  ARCHITECTURE::"docs/ARCHITECTURE.md"
  STANDARD_TEST_STRUCTURE::".hestai-sys/governance/rules/test-structure-standard.oct.md"
  STANDARD_NAMING::".hestai-sys/governance/rules/naming-standard.oct.md"
  STANDARD_VISIBILITY::".hestai-sys/governance/rules/visibility-rules.oct.md"
  OCTAVE_GUIDE::".hestai-sys/library/octave/octave-usage-guide.oct.md"
  OCTAVE_VALIDATOR::"canonical_octave_mcp_cli<invocation:python_-m_octave_mcp.cli.main_validate>"
  OCTAVE_CANONICAL::octave-mcp<pip_transitive_dep>
§1::MODEL_NOW_SOON_LATER
  DEFINITIONS:
    NOW::"Executable behavior for code that exists and must not regress"
    SOON::"Executable contracts for integration boundaries that are referenced but not yet fully integrated"
    LATER::"Forbidden surface until promoted (no references, no tests) to avoid future-test debt"
  MIGRATION_PATH:
    SOON_TO_NOW::"When integration point implementation exists and integration tests are present"
    LATER_TO_SOON::"When an explicit integration marker is introduced in code"
§2::SOURCES_OF_TRUTH
  REGISTRY::"src/hestai_mcp/integrations/progressive.py"
  TOKENS:
    FORMAT::"INTEGRATION_POINT::{id}"
    LOCATION::"src/**/*.py"
  VALIDATOR::"scripts/ci/validate_progressive_behavior.py"
§3::CI_JOBS
  WORKFLOW_FILE::".github/workflows/ci.yml"
  JOBS:
    PREFLIGHT<preflight>:
      PURPOSE::"Route and enforce NOW/SOON/LATER invariants"
      OUTPUTS::[run_contracts∨run_integration]
      EXECUTES::"python scripts/ci/validate_progressive_behavior.py --github-output \"$GITHUB_OUTPUT\""
    DOCS_VALIDATE<docs_validate>:
      PURPOSE::"Validate doc naming/visibility + OCTAVE protocol for changed .oct.md"
      EXECUTES::["python -m octave_mcp.cli.main validate {changed}.oct.md","python scripts/ci/validate_naming_visibility.py {changed_docs}"]
    TYPECHECK<typecheck>:
      PURPOSE::"Type safety gate"
      EXECUTES::"python -m mypy src"
    LINT<lint>:
      PURPOSE::"Static style and formatting gate"
      EXECUTES::["python -m ruff check src tests scripts","python -m black --check src tests scripts"]
    TEST_NOW<test_now>:
      PURPOSE::"Core behavioral tests for current reality (NOW)"
      EXECUTES::"python -m pytest -m \"not integration and not contract and not e2e\""
    TEST_CONTRACTS<test_contracts>:
      PURPOSE::"Executable integration boundary contracts (SOON) when referenced"
      CONDITION::"run_contracts==true"
      EXECUTES::"python -m pytest -m \"contract\""
    BUILD_ARTIFACT<build_artifact>:
      PURPOSE::"Build shippable artifact (wheel)"
      OUTPUTS::"dist/*.whl [uploaded_artifact]"
      EXECUTES::"python -m build --wheel"
    ARTIFACT_VALIDATE<artifact_validate>:
      PURPOSE::"Validate shipped artifact in clean environment"
      INPUTS::"dist/*.whl [downloaded_artifact]"
      CHECKS::[
        install_wheel_in_temp_dir,
        import_package_from_site_packages,
        assert_no_test_files_in_installed_package,
        assert_no_tests_paths_in_wheel
      ]
    TEST_INTEGRATION<test_integration>:
      PURPOSE::"Full integration tests against installed artifact (LATER->NOW)"
      CONDITION::"run_integration==true"
      INPUTS::"dist/*.whl [downloaded_artifact]"
      EXECUTES::"python -m pytest -m \"integration\""
    FINAL_GATE<final_gate>:
      PURPOSE::"Branch protection check aggregator"
      REQUIRES::[
        preflight,
        typecheck,
        lint,
        test_now,
        artifact_validate
      ]
      CONDITIONAL_REQUIRES:
        IF_RUN_CONTRACTS::"run_contracts==true → test_contracts"
        IF_RUN_INTEGRATION::"run_integration==true → test_integration"
§4::STAGE_RULES
  RULES:
    SOON_REFERENCED_REQUIRES_CONTRACTS:
      IF::token_present_in_src
      THEN::"tests/contracts/{id}/test_*.py MUST_EXIST AND pytest -m contract MUST_PASS"
    SOON_FORBIDS_INTEGRATION_TESTS:
      IF::"registry.stage==SOON"
      THEN::"tests/integration/{id}/ MUST_BE_EMPTY"
    IMPLEMENTED_REQUIRES_NOW:
      IF::implementation_module_present_in_repo
      THEN::"registry.stage MUST_BE NOW"
    NOW_REQUIRES_INTEGRATION_TESTS:
      IF::"registry.stage==NOW"
      THEN::"tests/integration/{id}/test_*.py MUST_EXIST"
    LATER_FORBIDS_SURFACE:
      IF::"registry.stage==LATER"
      THEN::"no_token_in_src AND no_tests_in_contracts_or_integration"
§5::AUTHORING_GUIDE
  ADD_NEW_INTEGRATION_POINT:
    STEP_1::"Add registry entry [src/hestai_mcp/integrations/progressive.py]"
    STEP_2::"Add token to code [\"INTEGRATION_POINT::{id}\"]"
    STEP_3::"Create contract tests if SOON [tests/contracts/{id}/test_*.py, @pytest.mark.contract]"
    STEP_4::"Promote to NOW when ready [stage:NOW, integration_tests, @pytest.mark.integration]"
  MARKERS:
    REQUIRED::[unit∨integration∨e2e]
    OPTIONAL::[behavior∨contract]
===END===
