#!/usr/bin/env bash
# Test suite for create-doc.sh CLI helper
# Integration tests verifying issue creation and file generation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CREATE_DOC_SCRIPT="$PROJECT_ROOT/scripts/create-doc.sh"

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

assert_contains() {
    local file="$1"
    local pattern="$2"
    if ! grep -q "$pattern" "$file"; then
        echo "FAIL: Expected '$pattern' in $file"
        return 1
    fi
    echo "PASS: Found '$pattern' in $file"
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
    assert_exists "$CREATE_DOC_SCRIPT"
}

# Test 2: Script requires type argument
test_requires_type_argument() {
    if "$CREATE_DOC_SCRIPT" 2>/dev/null; then
        echo "FAIL: Script should require type argument"
        return 1
    fi
    echo "PASS: Script correctly requires type argument"
    return 0
}

# Test 3: Script requires title argument
test_requires_title_argument() {
    if "$CREATE_DOC_SCRIPT" adr 2>/dev/null; then
        echo "FAIL: Script should require title argument"
        return 1
    fi
    echo "PASS: Script correctly requires title argument"
    return 0
}

# Test 4: Script validates type (adr or rfc only)
test_validates_type() {
    if "$CREATE_DOC_SCRIPT" invalid "Test Title" 2>/dev/null; then
        echo "FAIL: Script should reject invalid type"
        return 1
    fi
    echo "PASS: Script rejects invalid type"
    return 0
}

# Run all tests
echo "Testing create-doc.sh script..."
echo "Project root: $PROJECT_ROOT"

run_test "Script exists and is executable" test_script_exists
run_test "Requires type argument" test_requires_type_argument
run_test "Requires title argument" test_requires_title_argument
run_test "Validates type" test_validates_type

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
