#!/usr/bin/env bash
# Skill Activation Hook - Entry Point for user_prompt_submit hook
#
# This hook is executed by Claude Code on every user prompt submission.
# It analyzes the prompt and injects relevant skills into the conversation context.
#
# Security validations implemented:
# - Skill name allowlist: ^[a-z0-9][a-z0-9_-]*$
# - Path containment: resolved paths must start with skillsBase
# - Directory existence verification before path export
#
# Environment variables:
# - CLAUDE_PROJECT_DIR: Project root (provided by Claude Code)
# - HESTAI_SKILLS_PATH: Exported path to skills library (if valid)

set -e

# Determine project directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
HOOKS_DIR="${PROJECT_DIR}/.claude/hooks"

# Security: Validate skill name format (allowlist pattern)
validate_skill_name() {
    local skill_name="$1"
    if [[ ! "$skill_name" =~ ^[a-z0-9][a-z0-9_-]*$ ]]; then
        echo "ERROR: Invalid skill name format: $skill_name" >&2
        return 1
    fi
    return 0
}

# Security: Validate path containment
# Cross-platform realpath wrapper (macOS realpath doesn't support -e flag)
resolve_canonical_path() {
    local path="$1"
    local must_exist="$2"  # "true" or "false"

    # Check existence first if required
    if [[ "$must_exist" == "true" ]] && [[ ! -e "$path" ]]; then
        return 1
    fi

    # Use realpath without -e flag for macOS compatibility
    # realpath follows symlinks by default
    realpath "$path" 2>/dev/null
}

validate_path_containment() {
    local resolved_path="$1"
    local base_path="$2"

    # Resolve both paths to absolute canonical form
    # Uses realpath to follow symlinks (critical for symlink traversal prevention)
    local canonical_resolved
    local canonical_base

    # Resolve base path - must exist
    if [[ ! -d "$base_path" ]]; then
        echo "ERROR: Base path does not exist or is not a directory: $base_path" >&2
        return 1
    fi
    if ! canonical_base="$(resolve_canonical_path "$base_path" "true")"; then
        echo "ERROR: Base path is inaccessible: $base_path" >&2
        return 1
    fi

    # Resolve target path - follow symlinks to reveal true destination
    if [[ -e "$resolved_path" ]]; then
        # File/symlink exists - resolve to canonical path (symlinks resolved)
        # This is the CRITICAL security check: symlinks are followed to their target
        if ! canonical_resolved="$(resolve_canonical_path "$resolved_path" "true")"; then
            echo "ERROR: Cannot resolve path: $resolved_path" >&2
            return 1
        fi
    else
        # File doesn't exist yet - resolve parent dir and append filename
        local parent_dir
        parent_dir="$(dirname "$resolved_path")"
        if [[ ! -d "$parent_dir" ]]; then
            echo "ERROR: Parent directory does not exist: $parent_dir" >&2
            return 1
        fi
        if ! parent_dir="$(resolve_canonical_path "$parent_dir" "true")"; then
            echo "ERROR: Cannot resolve parent directory: $(dirname "$resolved_path")" >&2
            return 1
        fi
        canonical_resolved="${parent_dir}/$(basename "$resolved_path")"
    fi

    # SECURITY: Check containment with path separator boundary
    # This prevents /base/skills from matching /base/skillsevil
    # Must match exactly OR start with base + separator
    if [[ "$canonical_resolved" == "$canonical_base" ]] || \
       [[ "$canonical_resolved" == "$canonical_base/"* ]]; then
        return 0
    fi

    echo "ERROR: Path traversal detected: $resolved_path resolves outside $base_path" >&2
    return 1
}

# Security: Validate directory exists
validate_directory_exists() {
    local dir_path="$1"
    if [[ ! -d "$dir_path" ]]; then
        echo "ERROR: Directory does not exist: $dir_path" >&2
        return 1
    fi
    return 0
}

# Set up skills path with security validation and fallback chain
# Precedence:
# 1. HESTAI_HUB_SKILLS_PATH (hub-level, set by setup-mcp.sh)
# 2. HESTAI_SKILLS_PATH (explicit override, already set)
# 3. Local project hub/library/skills/ fallback
setup_skills_path() {
    # If HESTAI_HUB_SKILLS_PATH is already set and valid, use it
    if [[ -n "${HESTAI_HUB_SKILLS_PATH:-}" ]]; then
        if validate_directory_exists "$HESTAI_HUB_SKILLS_PATH"; then
            # HESTAI_HUB_SKILLS_PATH is valid, export as HESTAI_SKILLS_PATH for TypeScript
            export HESTAI_SKILLS_PATH="${HESTAI_HUB_SKILLS_PATH}"
            return 0
        fi
    fi

    # If HESTAI_SKILLS_PATH is already set and valid, keep it
    if [[ -n "${HESTAI_SKILLS_PATH:-}" ]]; then
        if validate_directory_exists "$HESTAI_SKILLS_PATH"; then
            return 0
        fi
    fi

    # Fallback to local project skills directory
    local skills_base="${PROJECT_DIR}/hub/library/skills"
    if validate_directory_exists "$skills_base"; then
        export HESTAI_SKILLS_PATH="$skills_base"
    fi
}

# Load API key from .env if available
if [ -f "${HOOKS_DIR}/.env" ]; then
    set -a  # automatically export variables
    # shellcheck disable=SC1091
    source "${HOOKS_DIR}/.env"
    set +a
fi

# Set up skills path
setup_skills_path

# Change to hooks directory for TypeScript execution
cd "${HOOKS_DIR}"

# Execute the TypeScript skill activation prompt
# stdin is piped through to the TypeScript module
cat | npx tsx skill-activation-prompt.ts
