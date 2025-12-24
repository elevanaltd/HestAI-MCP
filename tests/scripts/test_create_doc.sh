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
    local output
    if output=$("$CREATE_DOC_SCRIPT" 2>&1); then
        echo "FAIL: Script should require type argument"
        return 1
    fi
    # Check for correct error/usage message
    if ! echo "$output" | grep -q "Missing required arguments"; then
         echo "FAIL: Unexpected error message (expected 'Missing required arguments')"
         echo "Output: $output"
         return 1
    fi
    echo "PASS: Script correctly requires type argument"
    return 0
}

# Test 3: Script requires title argument
test_requires_title_argument() {
    local output
    if output=$("$CREATE_DOC_SCRIPT" adr 2>&1); then
        echo "FAIL: Script should require title argument"
        return 1
    fi
    if ! echo "$output" | grep -q "Missing required arguments"; then
         echo "FAIL: Unexpected error message"
         echo "Output: $output"
         return 1
    fi
    echo "PASS: Script correctly requires title argument"
    return 0
}

# Test 4: Script validates type (adr or rfc only)
test_validates_type() {
    local output
    if output=$("$CREATE_DOC_SCRIPT" invalid "Test Title" 2>&1); then
        echo "FAIL: Script should reject invalid type"
        return 1
    fi
    if ! echo "$output" | grep -q "Invalid type 'invalid'"; then
         echo "FAIL: Unexpected error message"
         echo "Output: $output"
         return 1
    fi
    echo "PASS: Script rejects invalid type"
    return 0
}

# Test 5: Happy path - ADR creation with mocked gh CLI
test_adr_creation_happy_path() {
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Create mock gh script
    local mock_gh="$temp_dir/gh"
    cat > "$mock_gh" << 'EOF'
#!/usr/bin/env bash
# Mock gh CLI for testing
if [ "$1" = "auth" ] && [ "$2" = "status" ]; then
    exit 0  # Authenticated
elif [ "$1" = "issue" ] && [ "$2" = "create" ]; then
    # Simulate issue creation, return URL with issue number
    echo "https://github.com/elevanaltd/HestAI-MCP/issues/42"
    exit 0
fi
exit 1
EOF
    chmod +x "$mock_gh"

    # Create test environment
    local test_project="$temp_dir/test-project"
    mkdir -p "$test_project/docs/adr"

    # Run test in subshell to isolate state
    (
        cd "$test_project"

        # Initialize minimal git config for test
        git init -q
        git config user.name "Test User"
        git config user.email "test@example.com"

        # Override PATH to use mock gh
        export PATH="$temp_dir:$PATH"

        # Run script
        local output
        output=$("$CREATE_DOC_SCRIPT" adr "Test ADR Title" 2>&1)

        # Verify file was created
        local expected_file="docs/adr/adr-0042-test-adr-title.md"
        if [ ! -f "$expected_file" ]; then
            echo "FAIL: Expected file not created: $expected_file"
            echo "Output: $output"
            exit 1
        fi

        # Verify frontmatter contains GitHub Issue
        if ! grep -q "GitHub Issue.*#42" "$expected_file"; then
            echo "FAIL: Frontmatter missing GitHub Issue #42"
            cat "$expected_file"
            exit 1
        fi

        # Verify frontmatter contains ADR number
        if ! grep -q "ADR-0042: Test ADR Title" "$expected_file"; then
            echo "FAIL: Missing ADR number in title"
            cat "$expected_file"
            exit 1
        fi

        # Verify author field exists
        if ! grep -q "Author.*Test User" "$expected_file"; then
            echo "FAIL: Author field not populated"
            cat "$expected_file"
            exit 1
        fi
    )

    # Check subshell exit status
    if [ $? -ne 0 ]; then
        return 1
    fi

    echo "PASS: ADR created successfully with correct frontmatter"
    return 0
}

# Test 6: Happy path - RFC creation with mocked gh CLI
test_rfc_creation_happy_path() {
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Create mock gh script
    local mock_gh="$temp_dir/gh"
    cat > "$mock_gh" << 'EOF'
#!/usr/bin/env bash
# Mock gh CLI for testing
if [ "$1" = "auth" ] && [ "$2" = "status" ]; then
    exit 0  # Authenticated
elif [ "$1" = "issue" ] && [ "$2" = "create" ]; then
    # Simulate issue creation, return URL with issue number
    echo "https://github.com/elevanaltd/HestAI-MCP/issues/99"
    exit 0
fi
exit 1
EOF
    chmod +x "$mock_gh"

    # Create test environment
    local test_project="$temp_dir/test-project"
    mkdir -p "$test_project/rfcs/active"

    (
        cd "$test_project"

        # Initialize minimal git config for test
        git init -q
        git config user.name "RFC Author"
        git config user.email "rfc@example.com"

        # Override PATH to use mock gh
        export PATH="$temp_dir:$PATH"

        # Run script
        local output
        output=$("$CREATE_DOC_SCRIPT" rfc "Add New Feature" 2>&1)

        # Verify file was created
        local expected_file="rfcs/active/0099-add-new-feature.md"
        if [ ! -f "$expected_file" ]; then
            echo "FAIL: Expected RFC file not created: $expected_file"
            echo "Output: $output"
            exit 1
        fi

        # Verify frontmatter contains GitHub Issue
        if ! grep -q "GitHub Issue.*#99" "$expected_file"; then
            echo "FAIL: Frontmatter missing GitHub Issue #99"
            cat "$expected_file"
            exit 1
        fi

        # Verify frontmatter contains RFC number
        if ! grep -q "RFC-0099: Add New Feature" "$expected_file"; then
            echo "FAIL: Missing RFC number in title"
            cat "$expected_file"
            exit 1
        fi

        # Verify RFC-specific Implementation Plan section
        if ! grep -q "## Implementation Plan" "$expected_file"; then
            echo "FAIL: RFC missing Implementation Plan section"
            cat "$expected_file"
            exit 1
        fi
    )

    if [ $? -ne 0 ]; then
        return 1
    fi

    echo "PASS: RFC created successfully with correct frontmatter and sections"
    return 0
}

# Test 7: Failure path - gh auth check fails
test_gh_auth_failure() {
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Create mock gh script that fails auth
    local mock_gh="$temp_dir/gh"
    cat > "$mock_gh" << 'EOF'
#!/usr/bin/env bash
exit 1
EOF
    chmod +x "$mock_gh"

    export PATH="$temp_dir:$PATH"

    local output
    if output=$("$CREATE_DOC_SCRIPT" adr "Fail Title" 2>&1); then
        echo "FAIL: Script should have failed when gh auth fails"
        return 1
    fi

    if ! echo "$output" | grep -q "Not authenticated with GitHub CLI"; then
        echo "FAIL: Unexpected error message"
        echo "Output: $output"
        return 1
    fi

    echo "PASS: Script fails with correct error when gh auth fails"
    return 0
}

# Test 8: Failure path - gh issue create fails
test_gh_create_failure() {
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Create mock gh script that fails issue create
    local mock_gh="$temp_dir/gh"
    cat > "$mock_gh" << 'EOF'
#!/usr/bin/env bash
if [ "$1" = "auth" ]; then exit 0; fi
if [ "$1" = "issue" ] && [ "$2" = "create" ]; then exit 1; fi
exit 0
EOF
    chmod +x "$mock_gh"

    export PATH="$temp_dir:$PATH"

    local output
    if output=$("$CREATE_DOC_SCRIPT" adr "Fail Title" 2>&1); then
        echo "FAIL: Script should have failed when gh issue create fails"
        return 1
    fi

    if ! echo "$output" | grep -q "Failed to create GitHub issue"; then
        echo "FAIL: Unexpected error message"
        echo "Output: $output"
        return 1
    fi

    echo "PASS: Script fails with correct error when gh issue create fails"
    return 0
}

# Test 9: Input sanitization - special chars in title
test_input_sanitization() {
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Mock gh
    local mock_gh="$temp_dir/gh"
    cat > "$mock_gh" << 'EOF'
#!/usr/bin/env bash
echo "https://github.com/org/repo/issues/123"
exit 0
EOF
    chmod +x "$mock_gh"
    export PATH="$temp_dir:$PATH"

    # Setup environment
    local test_project="$temp_dir/test-project"
    mkdir -p "$test_project/docs/adr"

    (
        cd "$test_project"
        git init -q
        git config user.name "Test"

        # 1. Complex chars
        "$CREATE_DOC_SCRIPT" adr "Fix 'quotes' and /slashes/" >/dev/null
        local expected1="docs/adr/adr-0123-fix-quotes-and-slashes.md"
        if [ ! -f "$expected1" ]; then
            echo "FAIL: Expected sanitized filename: $expected1"
            exit 1
        fi

        # 2. Shell metachars
        "$CREATE_DOC_SCRIPT" adr "Title with \`backticks\` and \$vars" >/dev/null
        local expected2="docs/adr/adr-0123-title-with-backticks-and-vars.md"
        if [ ! -f "$expected2" ]; then
            echo "FAIL: Expected sanitized filename: $expected2"
            exit 1
        fi

        # 3. Path traversal
        "$CREATE_DOC_SCRIPT" adr "../../../etc/passwd" >/dev/null
        # make_slug removes slashes/dots, so path traversal is neutralized
        local expected_traversal="docs/adr/adr-0123-etcpasswd.md"
        if [ ! -f "$expected_traversal" ]; then
             echo "FAIL: Expected sanitized filename for traversal"
             exit 1
        fi
    )

    if [ $? -ne 0 ]; then
        return 1
    fi

    echo "PASS: Filename correctly sanitized"
    return 0
}

# Run all tests
echo "Testing create-doc.sh script..."
echo "Project root: $PROJECT_ROOT"

run_test "Script exists and is executable" test_script_exists
run_test "Requires type argument" test_requires_type_argument
run_test "Requires title argument" test_requires_title_argument
run_test "Validates type" test_validates_type
run_test "ADR creation happy path (mocked gh)" test_adr_creation_happy_path
run_test "RFC creation happy path (mocked gh)" test_rfc_creation_happy_path
run_test "Failure path - gh auth failure" test_gh_auth_failure
run_test "Failure path - gh create failure" test_gh_create_failure
run_test "Input sanitization - special chars" test_input_sanitization

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
