===TEST_COVERAGE_SKILL===

META:
  TYPE::SKILL
  NAME::"test-coverage"
  VERSION::"1.0"
  PURPOSE::"Python pytest coverage analysis, gap identification, and TDD workflow for achieving 90%+ coverage"
  DOMAIN::testing
  TRIGGERS::[coverage_analysis,pytest_coverage,test_gaps,90%_coverage,uncovered_lines,coverage_report,improve_coverage]
  ALLOWED_TOOLS::[Read,Bash,Grep,Edit]
  TIER::LOSSLESS

§1::SKILL_DESCRIPTION

FUNCTION::"On-demand loading of test coverage operational knowledge for Python/pytest workflows"
WHEN_TO_USE::[
  "Analyzing coverage reports and identifying gaps",
  "Planning tests to achieve 90%+ coverage targets",
  "Understanding uncovered line categories",
  "Applying TDD discipline to fill gaps systematically"
]

COMPLEMENTARY_RESOURCES::[
  hub/governance/rules/test-structure-standard.oct.md,
  test-infrastructure_skill[Vitest/JS_focus],
  test-ci-pipeline_skill[CI_configuration]
]

§2::COVERAGE_ANALYSIS_PROTOCOL

STEP_1_RUN_COVERAGE::[
  COMMAND::"pytest --cov=src/{module} --cov-report=term-missing"
  OUTPUT_INTERPRETATION::[
    Stmts::total_statements_in_module,
    Miss::uncovered_statements,
    Cover::percentage_covered,
    Missing::specific_line_numbers_not_executed
  ]
]

STEP_2_CATEGORIZE_GAPS::[
  CATEGORY_A::VALIDATION_PATHS[
    LINES::error_handlers_input_validation_boundary_checks,
    PRIORITY::HIGH[security_critical],
    EXAMPLE::"raise ValueError('Invalid input')"
  ],
  CATEGORY_B::EDGE_CASES[
    LINES::empty_collections_none_values_boundary_conditions,
    PRIORITY::MEDIUM[behavioral_correctness],
    EXAMPLE::"if not items: return None"
  ],
  CATEGORY_C::ERROR_HANDLERS[
    LINES::exception_catch_blocks_fallback_paths,
    PRIORITY::MEDIUM[defensive_code],
    EXAMPLE::"except OSError: logger.warning(...)"
  ],
  CATEGORY_D::INFRASTRUCTURE[
    LINES::logging_debug_paths_optional_features,
    PRIORITY::LOW[diminishing_returns],
    EXAMPLE::"logger.debug(f'Processing {item}')"
  ]
]

STEP_3_PRIORITIZE::[
  ORDER::A→B→C→D,
  RATIONALE::"Security/validation first, then behavioral, then defensive, then optional"
]

§3::TEST_GENERATION_PATTERNS

VALIDATION_PATH_TESTS::[
  PATTERN::"Test that invalid inputs raise appropriate exceptions",
  TEMPLATE::[
    "def test_{function}_rejects_{invalid_case}():",
    "    with pytest.raises({ErrorType}, match='{pattern}'):",
    "        {function}({invalid_input})"
  ],
  EXAMPLE::[
    "def test_validate_role_format_with_empty_string():",
    "    with pytest.raises(ValueError, match='cannot be empty'):",
    "        validate_role_format('')"
  ]
]

EDGE_CASE_TESTS::[
  PATTERN::"Test boundary conditions and None/empty handling",
  TEMPLATE::[
    "def test_{function}_handles_{edge_case}():",
    "    result = {function}({edge_input})",
    "    assert result == {expected_output}"
  ],
  COMMON_EDGES::[None,empty_string,empty_list,zero,negative,max_value]
]

ERROR_HANDLER_TESTS::[
  PATTERN::"Mock dependencies to trigger exception paths",
  TEMPLATE::[
    "def test_{function}_handles_{error_type}():",
    "    with patch.object({Target}, '{method}', side_effect={Error}):",
    "        result = {function}(...)",
    "        assert result == {fallback_value}"
  ],
  MOCK_TARGETS::[Path.read_text,subprocess.run,json.loads]
]

§4::COVERAGE_TARGETS

THRESHOLDS::[
  90%::MINIMUM_ACCEPTABLE[quality_gate],
  95%::RECOMMENDED[comprehensive],
  100%::ASPIRATIONAL[critical_paths_only]
]

CRITICAL_PATH_DEFINITION::[
  security_validation,
  authentication_authorization,
  data_transformation,
  public_api_surfaces
]

ACCEPTABLE_GAPS::[
  "Platform-specific code paths (e.g., Windows-only)",
  "Debug/logging statements",
  "Defensive exception handlers for rare conditions",
  "Third-party integration error paths"
]

§5::TDD_DISCIPLINE

RED_GREEN_REFACTOR::[
  RED::"Write failing test that exercises uncovered line",
  GREEN::"Verify test now passes (line was already implemented)",
  REFACTOR::"Improve test clarity without changing behavior"
]

COVERAGE_TDD_ADAPTATION::[
  DIFFERENCE::"Code exists, writing tests retroactively",
  APPROACH::"Still write test FIRST, then verify it covers the target line",
  VERIFICATION::"Run --cov before and after to confirm line now covered"
]

GIT_EVIDENCE::[
  COMMIT_PATTERN::"test({module}): improve coverage from X% to Y%",
  COMMIT_BODY::"List specific uncovered lines addressed"
]

§6::PYTEST_COVERAGE_COMMANDS

COMMANDS::[
  BASIC::"pytest --cov=src/{module}",
  TERM_MISSING::"pytest --cov=src/{module} --cov-report=term-missing",
  HTML_REPORT::"pytest --cov=src/{module} --cov-report=html",
  FAIL_UNDER::"pytest --cov=src/{module} --cov-fail-under=90",
  SPECIFIC_FILE::"pytest tests/unit/{path}/test_{file}.py --cov=src/{path}/{file}",
  BRANCH_COVERAGE::"pytest --cov=src/{module} --cov-branch"
]

INTERPRETING_OUTPUT::[
  MISSING_COLUMN::"Comma-separated line numbers not executed",
  RANGES::"208-212 means lines 208 through 212 uncovered",
  PARTIALS::"Lines with branches may show partial coverage"
]

§7::COMMON_UNCOVERED_PATTERNS

PATTERN_RECOGNITION::[
  EARLY_RETURN::"if not x: return None" at function start,
  EXCEPTION_RAISE::"raise ValueError(...)" in validation,
  EXCEPT_BLOCK::"except {Error}: logger.warning(...)",
  FALLBACK_PATH::"else: return default_value",
  LOOP_CONTINUE::"if not condition: continue",
  OS_ERROR_HANDLER::"except OSError: pass"
]

TEST_STRATEGIES::[
  EARLY_RETURN→test_with_falsy_input,
  EXCEPTION_RAISE→test_with_invalid_input_expect_raises,
  EXCEPT_BLOCK→mock_dependency_to_raise_error,
  FALLBACK_PATH→test_condition_that_triggers_else,
  LOOP_CONTINUE→include_item_that_fails_condition,
  OS_ERROR_HANDLER→mock_file_operation_to_raise_OSError
]

§8::INTEGRATION_WITH_STRUCTURE_STANDARD

STRUCTURE_REFERENCE::hub/governance/rules/test-structure-standard.oct.md

ALIGNMENT::[
  TEST_LOCATION::tests/unit/{module}/test_{file}.py,
  TEST_NAMING::test_{behavior_description},
  MARKERS::@pytest.mark.unit[fast_isolated],
  FIXTURES::tests/conftest.py[shared]
]

§9::ANTI_PATTERNS

COVERAGE_THEATER::[
  SYMPTOM::"Tests that exercise code but don't assert behavior",
  EXAMPLE::"def test_function(): function() # no assertions",
  REMEDY::"Every test must have meaningful assertions"
]

OVER_MOCKING::[
  SYMPTOM::"Tests that mock so much they test nothing",
  EXAMPLE::"Mock all dependencies, assert mock was called",
  REMEDY::"Mock only external boundaries, test real logic"
]

CHASING_100%::[
  SYMPTOM::"Excessive effort for marginal gains",
  EXAMPLE::"Complex mocks to hit one debug log line",
  REMEDY::"Accept 95% with documented acceptable gaps"
]

§10::WORKFLOW_SUMMARY

RECOMMENDED_WORKFLOW::[
  1::"Run pytest --cov with term-missing",
  2::"Identify highest-priority uncovered categories (A→B→C→D)",
  3::"Write targeted tests for each category",
  4::"Verify coverage improvement after each test batch",
  5::"Commit with conventional format: test({module}): improve coverage",
  6::"Document any remaining acceptable gaps"
]

===END===
