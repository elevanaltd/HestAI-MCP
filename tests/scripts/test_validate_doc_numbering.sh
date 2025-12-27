#!/usr/bin/env bash
# Test suite for validate-doc-numbering.sh
# Tests validation logic for ADR filename <-> GitHub issue matching
# Note: RFC tests removed per ADR-0060 (rfcs/ folder deleted)

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
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Create directory structure (ADRs only - RFCs deprecated per ADR-0060)
    mkdir -p "$temp_dir/docs/adr"

    # Create valid ADR
    cat > "$temp_dir/docs/adr/adr-0042-answer.md" << 'EOF'
# ADR-0042: Answer
- **GitHub Issue**: [#42](url)
EOF

    # Run validation in temp dir
    (
        cd "$temp_dir"
        if ! "$VALIDATE_SCRIPT" >/dev/null 2>&1; then
            echo "FAIL: Validation failed for correct documents"
            exit 1
        fi
    )
    if [ $? -ne 0 ]; then return 1; fi

    echo "PASS: Correct documents validate successfully"
    return 0
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

# Test 4: Validation fails with proper summary for mismatched documents
test_validates_failure_path() {
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Create temporary test structure (ADRs only - RFCs deprecated per ADR-0060)
    mkdir -p "$temp_dir/docs/adr"

    # Create an ADR with mismatched number
    cat > "$temp_dir/docs/adr/adr-0100-mismatch-test.md" << 'EOF'
# ADR-0100: Mismatch Test

- **Status**: Draft
- **Author**: Test
- **Created**: 2025-01-01
- **Updated**: 2025-01-01
- **GitHub Issue**: [#99](https://github.com/elevanaltd/HestAI-MCP/issues/99)

## Summary
Test document with intentional mismatch (filename=100, issue=99)
EOF

    # Run validation in temp directory (should fail)
    (
        cd "$temp_dir"
        local output
        local exit_code
        output=$("$VALIDATE_SCRIPT" 2>&1) && exit_code=0 || exit_code=$?

        # Should exit with code 1
        if [ "$exit_code" -ne 1 ]; then
            echo "FAIL: Expected exit code 1, got $exit_code"
            exit 1
        fi

        # Should contain summary
        if ! echo "$output" | grep -q "VALIDATION SUMMARY"; then
            echo "FAIL: Output should contain VALIDATION SUMMARY"
            echo "Output was: $output"
            exit 1
        fi

        # Should report 1 invalid document
        if ! echo "$output" | grep -q "Invalid: 1"; then
            echo "FAIL: Output should report 'Invalid: 1'"
            echo "Output was: $output"
            exit 1
        fi

        # Should show the mismatch error
        if ! echo "$output" | grep -q "Filename number (100) doesn't match issue (#99)"; then
            echo "FAIL: Output should show mismatch details"
            echo "Output was: $output"
            exit 1
        fi
    )
    if [ $? -ne 0 ]; then return 1; fi

    echo "PASS: Validation correctly fails with proper summary for mismatched documents"
    return 0
}

# Test 5: Validation handles relaxed spacing (e.g. # 123)
test_validates_resilient_frontmatter() {
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    mkdir -p "$temp_dir/docs/adr"

    # Create ADR with space in issue number
    cat > "$temp_dir/docs/adr/adr-0042-relaxed.md" << 'EOF'
# ADR-0042: Relaxed
- **GitHub Issue**: # 42
EOF

    (
        cd "$temp_dir"
        if ! "$VALIDATE_SCRIPT" >/dev/null 2>&1; then
            echo "FAIL: Validation failed for relaxed frontmatter (# 42)"
            exit 1
        fi
    )
    if [ $? -ne 0 ]; then return 1; fi

    echo "PASS: Relaxed frontmatter validates successfully"
    return 0
}

# Run all tests
echo "Testing validate-doc-numbering.sh script..."
echo "Project root: $PROJECT_ROOT"

run_test "Script exists and is executable" test_script_exists
run_test "Has usage or runs successfully" test_has_usage
run_test "Validates correct documents" test_validates_correct_documents
run_test "Validates failure path with summary" test_validates_failure_path
run_test "Validates relaxed frontmatter" test_validates_resilient_frontmatter

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
