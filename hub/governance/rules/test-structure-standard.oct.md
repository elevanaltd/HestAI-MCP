===TEST_STRUCTURE_STANDARD===

METADATA::[
  type::standard,
  domain::governance,
  status::active,
  owners::[system-steward],
  created::2025-12-19,
  updated::2025-12-19,
  id::test-structure-standard,
  canonical::hub/governance/rules/test-structure-standard.oct.md,
  format::octave,
  tags::[testing|structure|placement]
]

===CORE_PRINCIPLE===

TESTS_MIRROR_SOURCE_STRUCTURE

STRUCTURE_LOGIC::[
  src/{module}/→tests/{module}/,
  one_test_file_per_source_file,
  test_filename::test_{source_filename},
  test_organization::mirrors_source_tree
]

===STANDARD_STRUCTURE===

EXAMPLE::[
  src/hestai_mcp/mcp/server.py→tests/mcp/test_server.py,
  src/hestai_mcp/tools/context.py→tests/tools/test_context.py,
  src/hestai_mcp/services/auth.py→tests/services/test_auth.py
]

TEST_ORGANIZATION::[
  tests/→root_test_directory,
  tests/conftest.py→shared_fixtures,
  tests/{module}/→mirrors_src/{module}/,
  tests/{module}/test_{file}.py→tests_for_src/{module}/{file}.py
]

===NAMING_CONVENTION===

TEST_FILES::test_{source_filename}.py
TEST_CLASSES::Test{ClassName}
TEST_FUNCTIONS::test_{behavior_description}

EXAMPLES::[
  test_server.py::tests_for_server.py,
  TestServer::tests_Server_class,
  test_get_hub_path::tests_get_hub_path_function,
  test_inject_system_governance::tests_inject_system_governance_function
]

===DISCOVERY_PATTERN===

PYTEST_DISCOVERY::[
  pattern::test_*.py|*_test.py,
  recommended::test_*.py[HestAI_standard],
  collection::automatic_via_pytest
]

===FIXTURES===

FIXTURE_PLACEMENT::[
  global_fixtures→tests/conftest.py,
  module_fixtures→tests/{module}/conftest.py,
  test_specific→inline_in_test_file
]

===AUTHORITY===

SOURCE::HestAI_testing_standards
VERSION::1.0
COMPANION::[naming-standard.oct.md|visibility-rules.oct.md]

===END===
