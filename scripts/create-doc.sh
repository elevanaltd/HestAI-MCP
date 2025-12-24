#!/usr/bin/env bash
# CLI helper for creating ADRs/RFCs with GitHub issue-based numbering
# Usage: ./scripts/create-doc.sh <adr|rfc> "Document Title"
#
# This script:
# 1. Creates a GitHub issue with appropriate label
# 2. Captures the issue number
# 3. Generates filename with issue number
# 4. Creates document file with pre-populated frontmatter
#
# See RFC-0031 for design rationale
# https://github.com/elevanaltd/HestAI-MCP/blob/main/rfcs/active/0031-github-issue-based-numbering.md

set -euo pipefail

# Configuration
REPO_OWNER="elevanaltd"
REPO_NAME="HestAI-MCP"
GITHUB_REPO="$REPO_OWNER/$REPO_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

info() {
    echo -e "${GREEN}$1${NC}"
}

warn() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

usage() {
    cat << EOF
Usage: $0 <type> "Title"

Arguments:
  type    Document type: 'adr' or 'rfc'
  title   Document title (quoted if it contains spaces)

Examples:
  $0 adr "Use PostgreSQL for persistence"
  $0 rfc "Add caching layer"

This script creates a GitHub issue and generates the corresponding document file
following RFC-0031 issue-based numbering convention.
EOF
    exit 1
}

# Create slug from title (lowercase, hyphenated)
make_slug() {
    local title="$1"
    echo "$title" | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/[^a-z0-9 -]//g' | \
        tr -s ' ' '-' | \
        sed 's/^-//; s/-$//'
}

# Get current date in YYYY-MM-DD format
get_date() {
    date +%Y-%m-%d
}

# Show usage if requested
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    usage
fi

# Main script
main() {
    # Validate arguments
    if [ $# -lt 2 ]; then
        error "Missing required arguments"
        usage
    fi

    local doc_type="$1"
    local doc_title="$2"

    # Validate document type
    if [ "$doc_type" != "adr" ] && [ "$doc_type" != "rfc" ]; then
        error "Invalid type '$doc_type'. Must be 'adr' or 'rfc'"
    fi

    # Check gh CLI is available
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI (gh) is not installed. Install from https://cli.github.com/"
    fi

    # Check gh authentication
    if ! gh auth status &> /dev/null; then
        error "Not authenticated with GitHub CLI. Run: gh auth login"
    fi

    info "Creating GitHub issue for $doc_type: $doc_title"

    # Create GitHub issue with label
    local issue_title
    if [ "$doc_type" = "adr" ]; then
        issue_title="ADR: $doc_title"
    else
        issue_title="RFC: $doc_title"
    fi

    # Create issue and capture URL
    local issue_url
    if ! issue_url=$(gh issue create \
        --repo "$GITHUB_REPO" \
        --title "$issue_title" \
        --label "$doc_type" \
        --body "Document placeholder - content will be added via PR" \
        2>&1); then
        error "Failed to create GitHub issue: $issue_url"
    fi

    # Extract issue number from URL
    local issue_number
    issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')

    if [ -z "$issue_number" ]; then
        error "Failed to extract issue number from: $issue_url"
    fi

    info "Created issue #$issue_number: $issue_url"

    # Generate slug
    local slug
    slug=$(make_slug "$doc_title")

    # Determine file path based on type
    local file_path
    if [ "$doc_type" = "adr" ]; then
        file_path="docs/adr/adr-$(printf "%04d" "$issue_number")-$slug.md"
    else
        file_path="rfcs/active/$(printf "%04d" "$issue_number")-$slug.md"
    fi

    # Check if file already exists
    if [ -e "$file_path" ]; then
        warn "File already exists: $file_path"
        warn "Issue created but file not written. You may need to manually create the file."
        exit 0
    fi

    # Get current date
    local current_date
    current_date=$(get_date)

    # Get git user name for author
    local author
    author=$(git config user.name 2>/dev/null || echo "Unknown")

    # Create document with frontmatter
    local doc_number
    if [ "$doc_type" = "adr" ]; then
        doc_number="ADR-$(printf "%04d" "$issue_number")"
    else
        doc_number="RFC-$(printf "%04d" "$issue_number")"
    fi

    cat > "$file_path" << EOF
# $doc_number: $doc_title

- **Status**: Draft
- **Author**: $author
- **Created**: $current_date
- **Updated**: $current_date
- **GitHub Issue**: [#$issue_number]($issue_url)

## Summary

[Brief one-paragraph explanation]

## Motivation

[Why are we doing this? What problem does it solve?]

## Detailed Design

[Explain the design in detail]

## Examples

[Show concrete examples]

## Drawbacks

[Why should we *not* do this?]

## Alternatives

[What other designs were considered?]

## Unresolved Questions

[What parts are still TBD?]
EOF

    if [ "$doc_type" = "rfc" ]; then
        cat >> "$file_path" << EOF

## Implementation Plan

- [ ] Phase 1: ...
- [ ] Phase 2: ...
- [ ] Phase 3: ...
EOF
    fi

    info "Created document: $file_path"
    info ""
    info "Next steps:"
    info "  1. Edit the document: $file_path"
    info "  2. Commit and push your changes"
    info "  3. Create PR with: Implements #$issue_number"
    info "  4. Discussion can happen in issue: $issue_url"
}

main "$@"
