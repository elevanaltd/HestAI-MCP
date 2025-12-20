===TEST_STRUCTURE_STANDARD===

META:
  NAME::"Test Structure Standard"
  VERSION::"1.1"
  PURPOSE::"Standardizes test layout, naming, and safety guardrails to prevent validation theater"

METADATA::[
  type::standard
  domain::testing
  status::active
  owners::[system-steward|test-infrastructure-steward|test-methodology-guardian|implementation-lead]
  created::2025-12-19
  updated::2025-12-20
  id::test-structure-standard
  canonical::hub/governance/rules/test-structure-standard.oct.md
  format::octave
  tags::[testing|structure|tdd|packaging|validation_theater]
]

===CORE_PRINCIPLE===

PATH_BASED_TEST_ORGANIZATION+ARTIFACT_VALIDATION

STRUCTURE_LOGIC::[
  src/{module}/→tests/{tier}/{module}/
  one_test_file_per_source_file
  test_filename::test_{source_filename}
  tiered_tests::unit_vs_contracts_vs_integration_vs_e2e
  packaging_exclusion::tests_not_shipped
  validation::CI_verifies_installed_artifact
]

===STANDARD_1_STRUCTURE===

EXAMPLE::[
  src/hestai_mcp/mcp/server.py→tests/unit/mcp/test_server.py
  src/hestai_mcp/mcp/tools/clock_in.py→tests/unit/mcp/tools/test_clock_in.py
  src/hestai_mcp/events/jsonl_lens.py→tests/unit/events/test_jsonl_lens.py
]

TEST_ORGANIZATION::[
  tests/→root_test_directory
  tests/conftest.py→shared_fixtures
  tests/unit/{module}/→mirrors_src/{module}/
  tests/contracts/→integration_boundary_contracts
  tests/integration/→cross_module_behaviors
  tests/e2e/→end_to_end_system_behaviors
]

===STANDARD_2_NAMING===

TEST_FILES::test_{source_filename}.py[test_*.py_only]
TEST_CLASSES::Test{ClassName}
TEST_FUNCTIONS::test_{behavior_description}

EXAMPLES::[
  test_server.py::tests_server_module
  test_clock_in.py::tests_clock_in_tool
  TestServer::tests_Server_class
  test_inject_system_governance::tests_inject_system_governance_function
]

DISALLOWED::[
  "*.test.py"→python_import_conflict_risk
  "*_test.py"→nonstandard_for_project
  "tests.py"→ambiguous_filename
]

===STANDARD_3_DISCOVERY===

PYTEST_DISCOVERY::[
  pattern::test_*.py
  recommended::test_*.py[HestAI_standard]
  collection::automatic_via_pytest
]

===STANDARD_4_PACKAGING_GUARDRAILS===

PACKAGE_DISCOVERY_EXPLICIT::MANDATORY[
  PURPOSE::prevent_tests_inclusion_in_distribution
  SETUPTOOLS::[
    tool.setuptools.packages.find.where::["src"]
    tool.setuptools.packages.find.include::["{package_name}*"]
    tool.setuptools.packages.find.exclude::["tests*"]
    tool.setuptools.include-package-data::false
  ]
]

TESTS_INIT_PROHIBITED::HIGH_PRIORITY[
  RULE::"tests/ MUST NOT contain __init__.py at any level"
  BECAUSE::tests_package_import_collisions+accidental_production_coupling
  ENFORCEMENT::precommit_hook_required
]

PRECOMMIT_ENFORCEMENT::[
  hook_id::no-tests-init
  entry::"bash -c 'find tests -name \"__init__.py\" -type f | grep -q . && echo \"ERROR: tests/__init__.py files must not exist\" && exit 1 || exit 0'"
  always_run::true
  pass_filenames::false
]

===STANDARD_5_IMPORT_GUARDS===

NO_SYS_PATH_INJECTION::CRITICAL[
  RULE::"tests MUST NOT use sys.path insertion to import src/"
  BECAUSE::tests_pass_locally_fail_when_installed
  REQUIRED_DEV_WORKFLOW::"pip install -e ."[editable_install]
]

IMPORT_SOURCE_VALIDATION::[
  LOCATION::tests/conftest.py
  GOAL::detect_importing_from_source_tree_instead_of_installed_artifact
  DEV_EXCEPTION::editable_install_allowed
  CI_REQUIREMENT::wheel_install_validation_must_enforce_site_packages
]

===STANDARD_6_CI_ARTIFACT_VALIDATION===

WHEEL_VALIDATION::CRITICAL[
  RULE::"CI MUST build+install the wheel in a clean directory and verify import surface"
  CHECKS::[
    build_wheel
    install_wheel_in_temp_dir
    import_package_from_site_packages
    assert_no_test_files_in_installed_package
    assert_no_tests_paths_in_wheel
  ]
]

===STANDARD_7_MARKERS===

MARKERS_REQUIRED::IMPORTANT[
  PURPOSE::separate_fast_unit_gate_from_slow_or_external_tests
  CONFIG::pytest_strict_markers_enabled
  REQUIRED_MARKERS::[unit|integration|e2e]
  OPTIONAL_MARKERS::[behavior|contract]
]

MARKER_USAGE::[
  unit::fast_isolated_no_external_dependencies
  behavior::executable_behavior_spec_for_current_reality
  contract::integration_boundary_contracts_not_full_integration
  integration::external_or_cross_module_dependencies_allowed
  e2e::full_system_behaviors
]

===STANDARD_8_EXCEPTIONS===

CONTRACT_TESTS::[
  LOCATION::tests/contracts/
  NAMING::test_{contract_name}.py
  PURPOSE::validate_integration_points_without_testing_nonexistent_components
]

INTEGRATION_TESTS::[
  LOCATION::tests/integration/
  NAMING::test_{behavior}_integration.py
  REQUIREMENT::must_reference_involved_source_modules
  PURPOSE::cross_module_behaviors
]

DUAL_TARGET_EXCEPTION::[
  WHEN::module_exposes_dual_public_api_surfaces
  REQUIREMENT::explicitly_documented_reason_in_test_module_docstring
  EXAMPLE::legacy_api_vs_tool_api
]

===FIXTURES===

FIXTURE_PLACEMENT::[
  global_fixtures→tests/conftest.py
  module_fixtures→tests/{module}/conftest.py
  test_specific→inline_in_test_file
]

===ENFORCEMENT_PRIORITY===

PRIORITY::[
  P1::WHEEL_VALIDATION[CRITICAL]
  P2::NO_SYS_PATH_INJECTION[CRITICAL]
  P3::TESTS_INIT_PROHIBITED[HIGH]
  P4::PACKAGE_DISCOVERY_EXPLICIT[MEDIUM]
  P5::MARKERS_REQUIRED[MEDIUM]
]

===VALIDATION_THEATER===

WARNING::[
  SYMPTOM::tests_green_but_artifact_broken
  CAUSE::tests_run_against_source_tree_not_shipped_wheel
  VIOLATION::truth_over_convenience
  REMEDY::WHEEL_VALIDATION+IMPORT_GUARDS+STRUCTURAL_EXCLUSION
]

===VERIFICATION_COMMANDS===

COMMANDS::[
  pytest_all::"pytest"
  pytest_unit::"pytest -m unit"
  build_wheel::"python -m build --wheel"
  check_wheel_for_tests::"unzip -l dist/*.whl | grep -E \"(test_|tests/)\""
  check_no_tests_init::"find tests -name \"__init__.py\" -type f"
]

===AUTHORITY===

SOURCE::HestAI_testing_standards
VERSION::1.1
COMPANION::[naming-standard.oct.md|visibility-rules.oct.md]

===END===
