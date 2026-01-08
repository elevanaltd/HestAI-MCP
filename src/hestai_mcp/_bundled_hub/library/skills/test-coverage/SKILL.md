---
name: test-coverage
description: Python pytest coverage analysis, gap identification, and TDD workflow for achieving 90%+ coverage
allowed-tools: ["Read", "Bash", "Grep", "Edit"]
triggers: ["coverage analysis", "pytest coverage", "test gaps", "90% coverage", "uncovered lines", "coverage report", "improve coverage", "test coverage gaps", "missing coverage"]
---

===TEST_COVERAGE===

META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Python pytest coverage analysis, gap identification, and TDD workflow for achieving 90%+ coverage"
  DOMAIN::ATHENA[quality]⊕ARTEMIS[precision_targeting]

§1::WHEN_TO_USE
  TRIGGERS::[
    "Analyzing coverage reports and identifying gaps",
    "Planning tests to achieve 90%+ coverage targets",
    "Understanding uncovered line categories",
    "Applying TDD discipline to fill gaps systematically"
  ]
  COMPLEMENTARY::[test-infrastructure,test-ci-pipeline,testing]

§2::ANALYSIS_PROTOCOL
  STEP_1::RUN_COVERAGE[
    COMMAND::"pytest --cov=src/{module} --cov-report=term-missing",
    OUTPUT::[Stmts::total,Miss::uncovered,Cover::percentage,Missing::line_numbers]
  ]
  STEP_2::CATEGORIZE_GAPS[
    A::VALIDATION_PATHS[HIGH::security_critical,"raise ValueError('...')"],
    B::EDGE_CASES[MEDIUM::behavioral,"if not items: return None"],
    C::ERROR_HANDLERS[MEDIUM::defensive,"except OSError: logger.warning(...)"],
    D::INFRASTRUCTURE[LOW::diminishing_returns,"logger.debug(...)"]
  ]
  STEP_3::PRIORITIZE[ORDER::A→B→C→D,"Security first, then behavioral, then defensive, then optional"]

§3::TEST_PATTERNS
  VALIDATION_PATH::[
    PATTERN::"Test invalid inputs raise appropriate exceptions",
    TEMPLATE::"def test_{fn}_rejects_{case}(): with pytest.raises({Error}): {fn}({invalid})"
  ]
  EDGE_CASE::[
    PATTERN::"Test boundary conditions and None/empty handling",
    TEMPLATE::"def test_{fn}_handles_{edge}(): assert {fn}({input}) == {expected}",
    COMMON::[None,empty_string,empty_list,zero,negative,max_value]
  ]
  ERROR_HANDLER::[
    PATTERN::"Mock dependencies to trigger exception paths",
    TEMPLATE::"with patch.object({T}, '{m}', side_effect={E}): assert {fn}(...) == {fallback}"
  ]

§4::TARGETS
  THRESHOLDS::[
    90%::MINIMUM[quality_gate],
    95%::RECOMMENDED[comprehensive],
    100%::ASPIRATIONAL[critical_paths_only]
  ]
  CRITICAL_PATHS::[security_validation,auth,data_transformation,public_api]
  ACCEPTABLE_GAPS::[platform_specific,debug_logging,rare_defensive_handlers,third_party_errors]

§5::TDD_DISCIPLINE
  RED_GREEN_REFACTOR::[
    RED::"Write failing test that exercises uncovered line",
    GREEN::"Verify test passes (line already implemented)",
    REFACTOR::"Improve test clarity"
  ]
  COVERAGE_ADAPTATION::[
    DIFFERENCE::"Code exists, tests retroactive",
    APPROACH::"Write test FIRST, verify covers target line",
    VERIFICATION::"Run --cov before/after"
  ]
  GIT_EVIDENCE::"test({module}): improve coverage from X% to Y%"

§6::COMMANDS
  BASIC::"pytest --cov=src/{module}"
  TERM_MISSING::"pytest --cov=src/{module} --cov-report=term-missing"
  HTML::"pytest --cov=src/{module} --cov-report=html"
  FAIL_UNDER::"pytest --cov=src/{module} --cov-fail-under=90"
  SPECIFIC::"pytest tests/unit/{path}/test_{file}.py --cov=src/{path}/{file}"
  BRANCH::"pytest --cov=src/{module} --cov-branch"

§7::COMMON_PATTERNS
  RECOGNITION::[
    EARLY_RETURN::"if not x: return None"→test_with_falsy,
    EXCEPTION_RAISE::"raise ValueError(...)"→test_invalid_expect_raises,
    EXCEPT_BLOCK::"except {E}: logger.warning(...)"→mock_to_raise,
    FALLBACK_PATH::"else: return default"→test_else_condition,
    LOOP_CONTINUE::"if not cond: continue"→include_failing_item,
    OS_ERROR::"except OSError: pass"→mock_file_op_to_raise
  ]

§8::ANTI_PATTERNS
  COVERAGE_THEATER::[
    SYMPTOM::"Tests exercise code but don't assert behavior",
    EXAMPLE::"def test_fn(): fn()  # no assertions",
    REMEDY::"Every test must have meaningful assertions"
  ]
  OVER_MOCKING::[
    SYMPTOM::"Mock so much tests prove nothing",
    EXAMPLE::"Mock all deps, assert mock called",
    REMEDY::"Mock only external boundaries"
  ]
  CHASING_100::[
    SYMPTOM::"Excessive effort for marginal gains",
    EXAMPLE::"Complex mocks to hit debug log",
    REMEDY::"Accept 95% with documented gaps"
  ]

§9::WORKFLOW
  STEPS::[
    1::"Run pytest --cov with term-missing",
    2::"Identify highest-priority gaps (A→B→C→D)",
    3::"Write targeted tests per category",
    4::"Verify improvement after each batch",
    5::"Commit: test({module}): improve coverage",
    6::"Document remaining acceptable gaps"
  ]

===END===
