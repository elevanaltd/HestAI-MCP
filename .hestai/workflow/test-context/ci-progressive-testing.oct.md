===CI_PROGRESSIVE_TESTING===
// Progressive testing workflow for HestAI-MCP CI
// OCTAVE v4 compliant

META:
  NAME::"CI Progressive Testing"
  VERSION::"1.0"
  TYPE::WORKFLOW
  STATUS::ACTIVE
  PURPOSE::"Define NOW/SOON/LATER test routing and required CI gates"
  CANONICAL::.hestai/workflow/test-context/ci-progressive-testing.oct.md

FOUNDATION::[
  NORTH_STAR::docs/workflow/000-MCP-PRODUCT-NORTH-STAR.md
  ARCHITECTURE::docs/ARCHITECTURE.md
  STANDARD_TEST_STRUCTURE::.hestai-sys/governance/rules/test-structure-standard.oct.md
  STANDARD_NAMING::.hestai-sys/governance/rules/naming-standard.oct.md
  STANDARD_VISIBILITY::.hestai-sys/governance/rules/visibility-rules.oct.md
  OCTAVE_GUIDE::.hestai-sys/library/octave/octave-usage-guide.oct.md
  OCTAVE_VALIDATOR::src/hestai_mcp/_bundled_hub/tools/octave-validator.py[vendored_from:/Volumes/OCTAVE/octave/tools/]
  OCTAVE_CANONICAL::/Volumes/OCTAVE/octave/[specs,tools,mcp]
]

===MODEL_NOW_SOON_LATER===

DEFINITIONS::[
  NOW::"Executable behavior for code that exists and must not regress"
  SOON::"Executable contracts for integration boundaries that are referenced but not yet fully integrated"
  LATER::"Forbidden surface until promoted (no references, no tests) to avoid future-test debt"
]

MIGRATION_PATH::[
  SOON->NOW::"When integration point implementation exists and integration tests are present"
  LATER->SOON::"When an explicit integration marker is introduced in code"
]

===SOURCES_OF_TRUTH===

REGISTRY::src/hestai_mcp/integrations/progressive.py
TOKENS::[
  FORMAT::"INTEGRATION_POINT::{id}"
  LOCATION::src/**/*.py
]
VALIDATOR::scripts/ci/validate_progressive_behavior.py

===CI_JOBS===

WORKFLOW_FILE::.github/workflows/ci.yml

JOBS::[
  preflight::[
    PURPOSE::"Route and enforce NOW/SOON/LATER invariants"
    OUTPUTS::[run_contracts|run_integration]
    EXECUTES::python scripts/ci/validate_progressive_behavior.py --github-output "$GITHUB_OUTPUT"
  ]
  docs_validate::[
    PURPOSE::"Validate doc naming/visibility + OCTAVE protocol for changed .oct.md"
    EXECUTES::[
      python src/hestai_mcp/_bundled_hub/tools/octave-validator.py --profile protocol {changed}.oct.md
      python scripts/ci/validate_naming_visibility.py {changed_docs}
    ]
  ]
  typecheck::[
    PURPOSE::"Type safety gate"
    EXECUTES::python -m mypy src
  ]
  lint::[
    PURPOSE::"Static style and formatting gate"
    EXECUTES::[
      python -m ruff check src tests scripts
      python -m black --check src tests scripts
    ]
  ]
  test_now::[
    PURPOSE::"Core behavioral tests for current reality (NOW)"
    EXECUTES::python -m pytest -m "not integration and not contract and not e2e"
  ]
  test_contracts::[
    PURPOSE::"Executable integration boundary contracts (SOON) when referenced"
    CONDITION::run_contracts==true
    EXECUTES::python -m pytest -m "contract"
  ]
  build_artifact::[
    PURPOSE::"Build shippable artifact (wheel)"
    OUTPUTS::dist/*.whl[uploaded_artifact]
    EXECUTES::python -m build --wheel
  ]
  artifact_validate::[
    PURPOSE::"Validate shipped artifact in clean environment"
    INPUTS::dist/*.whl[downloaded_artifact]
    CHECKS::[
      install_wheel_in_temp_dir
      import_package_from_site_packages
      assert_no_test_files_in_installed_package
      assert_no_tests_paths_in_wheel
    ]
  ]
  test_integration::[
    PURPOSE::"Full integration tests against installed artifact (LATER->NOW)"
    CONDITION::run_integration==true
    INPUTS::dist/*.whl[downloaded_artifact]
    EXECUTES::python -m pytest -m "integration"
  ]
  final_gate::[
    PURPOSE::"Branch protection check aggregator"
    REQUIRES::[
      preflight
      typecheck
      lint
      test_now
      artifact_validate
    ]
    CONDITIONAL_REQUIRES::[
      IF[run_contracts==true]::test_contracts
      IF[run_integration==true]::test_integration
    ]
  ]
]

===STAGE_RULES===

RULES::[
  SOON_REFERENCED_REQUIRES_CONTRACTS::[
    IF::token_present_in_src
    THEN::tests/contracts/{id}/test_*.py MUST_EXIST AND pytest -m contract MUST_PASS
  ]
  SOON_FORBIDS_INTEGRATION_TESTS::[
    IF::registry.stage==SOON
    THEN::tests/integration/{id}/ MUST_BE_EMPTY
  ]
  IMPLEMENTED_REQUIRES_NOW::[
    IF::implementation_module_present_in_repo
    THEN::registry.stage MUST_BE NOW
  ]
  NOW_REQUIRES_INTEGRATION_TESTS::[
    IF::registry.stage==NOW
    THEN::tests/integration/{id}/test_*.py MUST_EXIST
  ]
  LATER_FORBIDS_SURFACE::[
    IF::registry.stage==LATER
    THEN::no_token_in_src AND no_tests_in_contracts_or_integration
  ]
]

===AUTHORING_GUIDE===

ADD_NEW_INTEGRATION_POINT::[
  1::Add_registry_entry[src/hestai_mcp/integrations/progressive.py]
  2::Add_token_to_code["INTEGRATION_POINT::{id}"]
  3::Create_contract_tests_if_SOON[tests/contracts/{id}/test_*.py,@pytest.mark.contract]
  4::Promote_to_NOW_when_ready[stage:NOW,integration_tests,@pytest.mark.integration]
]

MARKERS::[
  REQUIRED::[unit|integration|e2e]
  OPTIONAL::[behavior|contract]
]

===END===
