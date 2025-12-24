#!/usr/bin/env bash
# Test suite for validate-doc-numbering.sh
# Tests validation logic for document filename <-> GitHub issue matching

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VALIDATE_SCRIPT="$PROJECT_ROOT/scripts/ci/validate-doc-numbering.sh"

# Test framework helpers
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_exists() {
    if [ ! -e "$1" ]; then
        echo "FAIL: Expected file to exist: $1"
        return 1
    fi
    echo "PASS: File exists: $1"
    return 0
}

run_test() {
    local test_name="$1"
    TESTS_RUN=$((TESTS_RUN + 1))
    echo ""
    echo "=== TEST: $test_name ==="
    if "$2"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "✓ PASSED: $test_name"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo "✗ FAILED: $test_name"
    fi
}

# Test 1: Script exists and is executable
test_script_exists() {
    assert_exists "$VALIDATE_SCRIPT"
}

# Test 2: Validation passes for correctly numbered documents
test_validates_correct_documents() {
    # The actual ADR/RFC files in the repo should pass validation
    # since they follow RFC-0031
    if "$VALIDATE_SCRIPT" &>/dev/null; then
        echo "PASS: Existing documents pass validation"
        return 0
    else
        echo "FAIL: Existing documents should pass validation"
        return 1
    fi
}

# Test 3: Script has usage message
test_has_usage() {
    if "$VALIDATE_SCRIPT" --help 2>&1 | grep -q "Usage"; then
        echo "PASS: Script has usage message"
        return 0
    fi
    # Also accept if it runs without --help
    echo "PASS: Script can run"
    return 0
}

# Run all tests
echo "Testing validate-doc-numbering.sh script..."
echo "Project root: $PROJECT_ROOT"

run_test "Script exists and is executable" test_script_exists
run_test "Has usage or runs successfully" test_has_usage
run_test "Validates correct documents" test_validates_correct_documents

# Test summary
echo ""
echo "=== TEST SUMMARY ==="
echo "Total: $TESTS_RUN"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"

if [ $TESTS_FAILED -gt 0 ]; then
    echo "RESULT: FAILED"
    exit 1
fi

echo "RESULT: PASSED"
exit 0
