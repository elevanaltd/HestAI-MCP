#!/usr/bin/env bash
# CI validation for RFC-0031 GitHub issue-based document numbering
#
# This script validates that document filenames match their GitHub issue numbers
# as specified in the frontmatter.
#
# Usage: ./scripts/ci/validate-doc-numbering.sh
#
# Exit codes:
#   0 - All documents valid
#   1 - Validation failures detected
#
# See RFC-0031 for design rationale
# https://github.com/elevanaltd/HestAI-MCP/blob/main/rfcs/active/0031-github-issue-based-numbering.md

set -euo pipefail

# Configuration
REPO_OWNER="elevanaltd"
REPO_NAME="HestAI-MCP"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_DOCS=0
VALID_DOCS=0
INVALID_DOCS=0
SKIPPED_DOCS=0

# Helper functions
error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}WARNING: $1${NC}" >&2
}

info() {
    echo -e "${BLUE}INFO: $1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

failure() {
    echo -e "${RED}✗ $1${NC}"
}

# Extract issue number from filename
# ADR: adr-0031-topic.md -> 31
# RFC: 0031-topic.md -> 31
extract_filename_number() {
    local filename="$1"
    local basename
    basename=$(basename "$filename")

    # Match adr-NNNN or NNNN at start of filename
    if [[ "$basename" =~ ^adr-0*([0-9]+)- ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$basename" =~ ^0*([0-9]+)- ]]; then
        echo "${BASH_REMATCH[1]}"
    else
        echo ""
    fi
}

# Extract GitHub issue number from frontmatter
# Looks for: - **GitHub Issue**: [#31](https://github.com/org/repo/issues/31)
# or: - **GitHub Issue**: #31
extract_frontmatter_issue() {
    local file="$1"

    # Look for GitHub Issue field in frontmatter
    local issue_line
    issue_line=$(grep -E "^\- \*\*GitHub Issue\*\*:" "$file" | head -1 || true)

    if [ -z "$issue_line" ]; then
        echo ""
        return
    fi

    # Extract number from [#123](...) or #123 format
    if [[ "$issue_line" =~ \#([0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    else
        echo ""
    fi
}

# Validate a single document
validate_document() {
    local file="$1"
    local doc_type="$2"

    TOTAL_DOCS=$((TOTAL_DOCS + 1))

    local filename
    filename=$(basename "$file")

    # Skip template files
    if [[ "$filename" =~ template ]]; then
        info "Skipping template: $filename"
        SKIPPED_DOCS=$((SKIPPED_DOCS + 1))
        return 0
    fi

    # Skip files without issue-based numbering (grandfathered)
    # RFC-0031 allows existing docs to keep old numbers
    local filename_number
    filename_number=$(extract_filename_number "$file")

    if [ -z "$filename_number" ]; then
        warn "Skipping non-numbered document: $filename"
        SKIPPED_DOCS=$((SKIPPED_DOCS + 1))
        return 0
    fi

    # Extract issue number from frontmatter
    local issue_number
    issue_number=$(extract_frontmatter_issue "$file")

    if [ -z "$issue_number" ]; then
        warn "Skipping grandfathered document (no GitHub Issue): $filename"
        SKIPPED_DOCS=$((SKIPPED_DOCS + 1))
        return 0
    fi

    # Compare numbers
    if [ "$filename_number" != "$issue_number" ]; then
        failure "$doc_type: $filename - Filename number ($filename_number) doesn't match issue (#$issue_number)"
        INVALID_DOCS=$((INVALID_DOCS + 1))
        return 1
    fi

    # Validation passed
    success "$doc_type: $filename (#$issue_number)"
    VALID_DOCS=$((VALID_DOCS + 1))
    return 0
}

# Main validation
main() {
    info "Validating RFC-0031 document numbering..."
    info "Repository: $REPO_OWNER/$REPO_NAME"
    echo ""

    # Find and validate ADR files
    if [ -d "docs/adr" ]; then
        info "Checking ADR files..."
        while IFS= read -r -d '' file; do
            validate_document "$file" "ADR"
        done < <(find docs/adr -name "adr-*.md" -print0 2>/dev/null || true)
    fi

    echo ""

    # Find and validate RFC files
    if [ -d "rfcs/active" ]; then
        info "Checking RFC files..."
        while IFS= read -r -d '' file; do
            validate_document "$file" "RFC"
        done < <(find rfcs/active -name "*.md" -print0 2>/dev/null || true)
    fi

    echo ""
    echo "=== VALIDATION SUMMARY ==="
    echo "Total documents: $TOTAL_DOCS"
    echo "Valid: $VALID_DOCS"
    echo "Invalid: $INVALID_DOCS"
    echo "Skipped: $SKIPPED_DOCS"

    if [ $INVALID_DOCS -gt 0 ]; then
        echo ""
        error "Validation failed: $INVALID_DOCS document(s) have numbering mismatches"
        error "Ensure document filename numbers match their GitHub Issue numbers"
        error "See RFC-0031: https://github.com/$REPO_OWNER/$REPO_NAME/blob/main/rfcs/active/0031-github-issue-based-numbering.md"
        exit 1
    fi

    echo ""
    success "All documents validated successfully!"
    exit 0
}

# Show usage if requested
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    cat << EOF
Usage: $0

Validates that ADR and RFC filenames match their GitHub Issue numbers.

Checks:
  - docs/adr/adr-NNNN-*.md files
  - rfcs/active/NNNN-*.md files

Each file must have:
  - Filename with issue number (e.g., adr-0031-topic.md)
  - Frontmatter with matching GitHub Issue (e.g., [#31](...))

Exit codes:
  0 - All documents valid
  1 - Validation failures detected

See RFC-0031 for specification.
EOF
    exit 0
fi

main "$@"
