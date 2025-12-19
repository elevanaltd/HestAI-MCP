#!/bin/bash
# SessionStart Hook - North Star Summary Auto-Loading
# Based on Issue #7: https://github.com/elevanaltd/hestai/issues/7
#
# Loads compressed North Star Summary (~100-130 lines) instead of full document (~300+ lines)
# Saves ~2.5k tokens at startup while maintaining 100% decision-logic fidelity
#
# Multi-Location Support:
# 1. Primary: .hestai/governance/workflow/ (hestai-core structure)
# 2. Fallback: .hestai/workflow/ (alternative structure)
# 3. Fallback: docs/workflow/ (for projects without .hestai)

set -e

# Get project directory from environment or current working directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# ANSI colors
BLUE='\033[34m'
GREEN='\033[32m'
YELLOW='\033[33m'
BOLD='\033[1m'
RESET='\033[0m'

SUMMARY_FILE=""
LOCATION_SOURCE=""

# Check for .hestai/governance/workflow/ structure (primary location for hestai-core)
HESTAI_GOV_WORKFLOW="$PROJECT_DIR/.hestai/governance/workflow"

if [ -d "$HESTAI_GOV_WORKFLOW" ]; then
  # Find North Star Summary file (pattern: *NORTH-STAR-SUMMARY*.md)
  SUMMARY_FILE=$(find "$HESTAI_GOV_WORKFLOW" -maxdepth 1 -name "*NORTH-STAR-SUMMARY*.md" -type f 2>/dev/null | head -1)
  if [ -n "$SUMMARY_FILE" ]; then
    LOCATION_SOURCE="hestai governance"
  fi
fi

# Fallback: Check .hestai/workflow/ if no summary found yet
if [ -z "$SUMMARY_FILE" ]; then
  HESTAI_WORKFLOW="$PROJECT_DIR/.hestai/workflow"

  if [ -d "$HESTAI_WORKFLOW" ]; then
    SUMMARY_FILE=$(find "$HESTAI_WORKFLOW" -maxdepth 1 -name "*NORTH-STAR-SUMMARY*.md" -type f 2>/dev/null | head -1)
    if [ -n "$SUMMARY_FILE" ]; then
      LOCATION_SOURCE="hestai workflow"
    fi
  fi
fi

# Fallback: Check docs/workflow/ if no summary found yet
if [ -z "$SUMMARY_FILE" ]; then
  DOCS_WORKFLOW="$PROJECT_DIR/docs/workflow"

  if [ -d "$DOCS_WORKFLOW" ]; then
    SUMMARY_FILE=$(find "$DOCS_WORKFLOW" -maxdepth 1 -name "*NORTH-STAR-SUMMARY*.md" -type f 2>/dev/null | head -1)
    if [ -n "$SUMMARY_FILE" ]; then
      LOCATION_SOURCE="docs"
    fi
  fi
fi

# Exit silently if no summary found in any location
if [ -z "$SUMMARY_FILE" ]; then
  exit 0
fi

# Verify file is readable and non-empty
if [ ! -r "$SUMMARY_FILE" ] || [ ! -s "$SUMMARY_FILE" ]; then
  echo -e "${YELLOW}⚠️  North Star Summary found but could not be loaded${RESET}"
  exit 0
fi

# Calculate relative path for display
RELATIVE_PATH="${SUMMARY_FILE#$PROJECT_DIR/}"

# Output formatted banner
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}📋 NORTH STAR SUMMARY${RESET}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# Output file contents
cat "$SUMMARY_FILE"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "${GREEN}✓ North Star Summary loaded from $LOCATION_SOURCE${RESET}"
echo -e "${BLUE}  Location: $RELATIVE_PATH${RESET}"
echo ""
