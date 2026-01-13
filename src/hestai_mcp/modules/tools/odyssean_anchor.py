"""
Odyssean Anchor MCP Tool - Agent Identity Binding Validation.

This tool implements the Odyssean Anchor binding mechanism for HestAI agents,
providing structural validation and self-correction for agent identity vectors.

Key Features:
- BIND section validation (ROLE, COGNITION, AUTHORITY)
- TENSION section validation with CTX citations (tier-aware)
- COMMIT section validation (artifact + gate)
- ARM injection from session/git state (server-authoritative)
- Self-correction protocol with retry guidance (max 2 retries)
- Optional semantic validation (AI-driven, Issue #131)

Schema: RAPH Vector v4.0 per ADR-0036 Amendment 01
Key Innovation: Server-Authoritative ARM (agent provides BIND+TENSION+COMMIT, tool injects ARM)

GitHub Issue: #102
ADR: docs/adr/adr-0036-odyssean-anchor-binding.md
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hestai_mcp.modules.tools.odyssean_anchor_semantic import SemanticValidationResult

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

# Valid cognition types per OCTAVE architecture
VALID_COGNITION_TYPES = {"ETHOS", "LOGOS", "PATHOS"}

# Valid archetypes per OCTAVE Semantic Pantheon (octave-mastery skill §1)
# Plus narrative dynamics (§2) and system forces (§3) for extended usage
VALID_ARCHETYPES = {
    # Semantic Pantheon - 10 core domains
    "ZEUS",  # Executive function, authority, strategic direction
    "ATHENA",  # Strategic wisdom, planning, elegant solutions
    "APOLLO",  # Analytics, data, insight, clarity, prediction
    "HERMES",  # Communication, translation, APIs, messaging
    "HEPHAESTUS",  # Infrastructure, tooling, engineering, automation
    "ARES",  # Security, defense, stress testing, adversarial
    "ARTEMIS",  # Monitoring, observation, logging, alerting
    "POSEIDON",  # Data lakes, storage, databases
    "DEMETER",  # Resource allocation, budgeting, scaling
    "DIONYSUS",  # User experience, engagement, creativity
    # Narrative dynamics archetypes (octave-mythology §3)
    "ODYSSEUS",  # Long transformative journey, navigation
    "SISYPHUS",  # Repetitive maintenance, cyclical patterns
    "PROMETHEUS",  # Breakthrough innovation, boundary-breaking
    "ICARUS",  # Overreach from early success
    "PANDORA",  # Unforeseen cascading problems
    "ATLAS",  # Ultimate accountability, system-wide burden
    "ARGUS",  # Vigilant observation, multi-perspective
    "THEMIS",  # Justice, rule enforcement, fairness
    "DAEDALUS",  # Architectural mastery, complex construction
}

# Tier requirements for tension count
TIER_TENSION_REQUIREMENTS = {
    "quick": 1,
    "default": 2,
    "deep": 3,
}

# Generic/placeholder values to reject
GENERIC_ARTIFACTS = {"response", "result", "output", "completion", "answer", "reply"}
PLACEHOLDER_VALUES = {"TODO", "TBD", "FIXME", "XXX", "PLACEHOLDER", "EXAMPLE"}
GENERIC_CONSTRAINTS = {"CONSTRAINT", "RULE", "POLICY", "REQUIREMENT"}

# Maximum retry attempts per OA-I3
MAX_RETRIES = 2


# =============================================================================
# Result Dataclasses
# =============================================================================


@dataclass
class BindValidationResult:
    """Result from BIND section validation."""

    valid: bool
    role: str = ""
    cognition_type: str = ""
    cognition_archetype: str = ""
    authority: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class TensionValidationResult:
    """Result from TENSION section validation."""

    valid: bool
    tension_count: int = 0
    tensions: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class CommitValidationResult:
    """Result from COMMIT section validation."""

    valid: bool
    artifact: str = ""
    gate: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class ARMInjectionResult:
    """Result from ARM section injection."""

    valid: bool
    phase: str = ""
    branch: str | None = None
    ahead: int = 0
    behind: int = 0
    files_count: int = 0
    top_files: list[str] = field(default_factory=list)
    focus: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class OdysseanAnchorResult:
    """Result from odyssean_anchor tool call."""

    success: bool
    anchor: str | None = None
    errors: list[str] = field(default_factory=list)
    guidance: str = ""
    retry_count: int = 0
    terminal: bool = False


# =============================================================================
# Section Extraction Helpers (for scoped validation)
# =============================================================================


def _extract_section(document: str, section_header: str) -> str:
    """
    Extract a specific section from the document.

    Extracts content from after the section header until the next "## " header.
    Only considers non-indented headers as section boundaries.

    Args:
        document: Full document text
        section_header: Header pattern to match (e.g., "## BIND", "## COMMIT")

    Returns:
        Extracted section content (includes header line)
    """
    lines = []
    in_section = False

    for line in document.split("\n"):
        # Check for section header (must contain the pattern)
        if section_header in line and "##" in line:
            in_section = True
            lines.append(line)
            continue

        if in_section:
            # Only stop at non-indented section headers (security: prevent header smuggling)
            stripped = line.lstrip()
            if stripped.startswith("## ") and line == stripped:
                # This is a new section at column 0, stop extraction
                break
            lines.append(line)

    return "\n".join(lines)


def _extract_bind_section(document: str) -> str:
    """Extract BIND section from document."""
    return _extract_section(document, "## BIND")


def _extract_commit_section(document: str) -> str:
    """Extract COMMIT section from document."""
    return _extract_section(document, "## COMMIT")


# =============================================================================
# BIND Section Validation
# =============================================================================


def validate_bind_section(bind_text: str) -> BindValidationResult:
    """
    Validate BIND section (Identity Lock).

    Required fields:
    - ROLE::{agent_name} (non-empty)
    - COGNITION::{type}::{archetype} (valid type and archetype)
    - AUTHORITY::{RESPONSIBLE|DELEGATED}[...]

    Args:
        bind_text: The BIND section text to validate (may be full document or just section)

    Returns:
        BindValidationResult with validation status and extracted values
    """
    errors = []
    role = ""
    cognition_type = ""
    cognition_archetype = ""
    authority = ""

    # Extract only the BIND section to prevent cross-section pollution (RAPH compliance)
    scoped_text = _extract_bind_section(bind_text)
    # If no BIND section found, use original text (backward compatibility)
    if not scoped_text:
        scoped_text = bind_text

    # Extract ROLE from scoped section only
    role_match = re.search(r"ROLE::(.+?)(?:\n|$)", scoped_text)
    if role_match:
        role = role_match.group(1).strip()
        if not role:
            errors.append("BIND: ROLE field is empty")
    else:
        errors.append("BIND: Missing ROLE field")

    # Extract COGNITION from scoped section only
    # Supports multiple archetypes: COGNITION::LOGOS::ATLAS⊕ODYSSEUS⊕APOLLO
    # Also accepts + as ASCII alias for ⊕ (synthesis operator)
    cognition_match = re.search(r"COGNITION::([A-Z]+)::([A-Z⊕+]+)", scoped_text)
    if cognition_match:
        cognition_type = cognition_match.group(1)
        archetype_str = cognition_match.group(2)

        # Split on ⊕ or + (synthesis operator and its ASCII alias)
        archetypes = re.split(r"[⊕+]", archetype_str)
        cognition_archetype = archetype_str  # Store full string for output

        if cognition_type not in VALID_COGNITION_TYPES:
            errors.append(
                f"BIND: Invalid COGNITION type '{cognition_type}'. "
                f"Valid types: {', '.join(sorted(VALID_COGNITION_TYPES))}"
            )

        # Validate each archetype in the list
        invalid_archetypes = [a for a in archetypes if a not in VALID_ARCHETYPES]
        if invalid_archetypes:
            errors.append(
                f"BIND: Invalid COGNITION archetype(s) '{', '.join(invalid_archetypes)}'. "
                f"Valid archetypes: {', '.join(sorted(VALID_ARCHETYPES))}"
            )
    else:
        errors.append(
            "BIND: Missing or malformed COGNITION field "
            "(expected COGNITION::{type}::{archetype} or COGNITION::{type}::{arch1}⊕{arch2}⊕{arch3})"
        )

    # Extract AUTHORITY
    # Extract AUTHORITY from scoped section only
    authority_match = re.search(r"AUTHORITY::((?:RESPONSIBLE|DELEGATED)\[.+?\])", scoped_text)
    if authority_match:
        authority = authority_match.group(1)
    else:
        errors.append(
            "BIND: Missing AUTHORITY field (expected AUTHORITY::{RESPONSIBLE|DELEGATED}[...])"
        )

    return BindValidationResult(
        valid=len(errors) == 0,
        role=role,
        cognition_type=cognition_type,
        cognition_archetype=cognition_archetype,
        authority=authority,
        errors=errors,
    )


# =============================================================================
# TENSION Section Validation
# =============================================================================


def validate_tension_section(tension_text: str, tier: str = "default") -> TensionValidationResult:
    """
    Validate TENSION section (Cognitive Proof).

    Required:
    - Minimum tension count based on tier (quick=1, default=2, deep=3)
    - Each tension must have CTX:{path}[{state}] citation
    - Each tension must have TRIGGER[{action}]
    - No placeholder/generic constraints

    For deep tier:
    - CTX citations must include line ranges

    Args:
        tension_text: The TENSION section text to validate
        tier: Validation tier (quick, default, deep)

    Returns:
        TensionValidationResult with validation status
    """
    errors = []
    tensions = []

    # Parse tension lines using OCTAVE operators per octave-5-llm-core.oct.md
    # Format: L{N}::[constraint]⇌CTX:{path}[state]→TRIGGER[action]
    # Accepts both Unicode (⇌, →) and ASCII aliases (<->, ->) per OCTAVE spec §2b
    # Note: <-> is legacy alias for ⇌ (tension), -> is alias for → (flow)

    # Tension operator: ⇌ (Unicode) or <-> (ASCII alias)
    tension_op = r"(?:⇌|<->)"
    # Flow operator: → (Unicode) or -> (ASCII alias)
    flow_op = r"(?:→|->)"

    # First pattern: with line number prefix
    tension_pattern = re.compile(
        rf"L(\d+)::\[([^\]]+)\]{tension_op}(?:CTX:)?([^\[]*)\[([^\]]*)\]{flow_op}(.*)"
    )

    # Alternative pattern without line number prefix
    alt_pattern = re.compile(rf"\[([^\]]+)\]{tension_op}CTX:([^\[]*)\[([^\]]*)\]{flow_op}(.*)")

    # Pattern to extract TRIGGER[action] from the end portion
    trigger_pattern = re.compile(r"TRIGGER\[([^\]]+)\]")

    for line in tension_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Try main pattern first
        match = tension_pattern.search(line)
        if match:
            line_num = match.group(1)
            constraint = match.group(2)
            ctx_path = match.group(3)
            state = match.group(4)
            trigger_part = match.group(5)

            # Check if TRIGGER[] format is present
            trigger_match = trigger_pattern.search(trigger_part) if trigger_part else None
            trigger = trigger_match.group(1) if trigger_match else None
            has_trigger_format = trigger_match is not None

            tension_data = {
                "line_num": line_num,
                "constraint": constraint,
                "ctx_path": ctx_path.strip(),
                "state": state,
                "trigger": trigger,
                "has_trigger_format": has_trigger_format,
            }
            tensions.append(tension_data)
            continue

        # Try alternative pattern
        alt_match = alt_pattern.search(line)
        if alt_match:
            constraint = alt_match.group(1)
            ctx_path = alt_match.group(2)
            state = alt_match.group(3)
            trigger_part = alt_match.group(4)

            trigger_match = trigger_pattern.search(trigger_part) if trigger_part else None
            trigger = trigger_match.group(1) if trigger_match else None
            has_trigger_format = trigger_match is not None

            tension_data = {
                "line_num": str(len(tensions) + 1),
                "constraint": constraint,
                "ctx_path": ctx_path.strip(),
                "state": state,
                "trigger": trigger,
                "has_trigger_format": has_trigger_format,
            }
            tensions.append(tension_data)

    # Validate tension count
    min_required = TIER_TENSION_REQUIREMENTS.get(tier, 2)
    if len(tensions) < min_required:
        errors.append(
            f"TENSION: Insufficient count. Tier '{tier}' requires minimum {min_required} tensions, found {len(tensions)}"
        )

    # Validate each tension
    for i, tension in enumerate(tensions, 1):
        # Check for CTX citation
        t_ctx_path_val = tension.get("ctx_path", "")
        t_ctx_path: str = str(t_ctx_path_val) if t_ctx_path_val else ""
        if not t_ctx_path or t_ctx_path.upper() in PLACEHOLDER_VALUES:
            errors.append(f"TENSION[{i}]: Missing CTX: citation. Add CTX:{{filename}}[{{state}}]")

        # Check for TRIGGER - must be in TRIGGER[action] format
        t_has_trigger: bool = bool(tension.get("has_trigger_format", False))
        t_trigger = tension.get("trigger")
        if not t_has_trigger or not t_trigger:
            errors.append(f"TENSION[{i}]: Missing TRIGGER[{{action}}]")

        # Check for generic/placeholder constraint
        t_constraint_val = tension.get("constraint", "")
        t_constraint: str = str(t_constraint_val).upper() if t_constraint_val else ""
        if t_constraint in GENERIC_CONSTRAINTS or t_constraint in PLACEHOLDER_VALUES:
            errors.append(
                f"TENSION[{i}]: Constraint '{tension.get('constraint')}' is too generic. "
                "Use specific constraint names (e.g., TDD_MANDATE, MINIMAL_INTERVENTION)"
            )

        # For deep tier, require line ranges in CTX
        # Line ranges must be in format :10 or :10-20
        if (
            tier == "deep"
            and t_ctx_path
            and ":" not in t_ctx_path.split("/")[-1]
            and not re.search(r":\d+(-\d+)?", t_ctx_path)
        ):
            errors.append(
                f"TENSION[{i}]: Deep tier requires line ranges in CTX citations. "
                f"Found: CTX:{t_ctx_path}. Expected: CTX:path/file.md:10-20[state]"
            )

    # Additional check: tensions without CTX in the line
    if tensions:
        for i, tension in enumerate(tensions, 1):
            state = tension.get("state", "")
            ctx_path = tension.get("ctx_path", "")
            # If state exists but no proper CTX path
            if state and not ctx_path:
                errors.append(f"TENSION[{i}]: Found state but missing CTX: path citation")

    return TensionValidationResult(
        valid=len(errors) == 0,
        tension_count=len(tensions),
        tensions=tensions,
        errors=errors,
    )


# =============================================================================
# COMMIT Section Validation
# =============================================================================


def validate_commit_section(commit_text: str) -> CommitValidationResult:
    """
    Validate COMMIT section (Falsifiable Contract).

    Required fields:
    - ARTIFACT::{concrete_path} (not generic like "response")
    - GATE::{validation_method}

    Args:
        commit_text: The COMMIT section text to validate (may be full document or just section)

    Returns:
        CommitValidationResult with validation status
    """
    errors = []
    artifact = ""
    gate = ""

    # Extract only the COMMIT section to prevent cross-section pollution (RAPH compliance)
    scoped_text = _extract_commit_section(commit_text)
    # If no COMMIT section found, use original text (backward compatibility)
    if not scoped_text:
        scoped_text = commit_text

    # Extract ARTIFACT from scoped section only
    artifact_match = re.search(r"ARTIFACT::(.+?)(?:\n|$)", scoped_text)
    if artifact_match:
        artifact = artifact_match.group(1).strip()

        # Check for generic/placeholder artifacts
        artifact_lower = artifact.lower()
        if artifact_lower in GENERIC_ARTIFACTS:
            errors.append(
                f"COMMIT: Artifact '{artifact}' is too generic. "
                "Use concrete file path (e.g., 'src/module/file.py')"
            )
        elif artifact.upper() in PLACEHOLDER_VALUES:
            errors.append(
                f"COMMIT: Artifact '{artifact}' is a placeholder. " "Use actual artifact path"
            )
        elif not artifact:
            errors.append("COMMIT: ARTIFACT field is empty")
    else:
        errors.append("COMMIT: Missing ARTIFACT field")

    # Extract GATE from scoped section only
    gate_match = re.search(r"GATE::(.+?)(?:\n|$)", scoped_text)
    if gate_match:
        gate = gate_match.group(1).strip()
        if not gate:
            errors.append("COMMIT: GATE field is empty")
    else:
        errors.append("COMMIT: Missing GATE field")

    return CommitValidationResult(
        valid=len(errors) == 0,
        artifact=artifact,
        gate=gate,
        errors=errors,
    )


# =============================================================================
# ARM Section Injection (Server-Authoritative)
# =============================================================================


def _validate_session_id(session_id: str) -> tuple[bool, str]:
    """
    Validate session_id to prevent path traversal attacks.

    Args:
        session_id: Session ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Reject empty session_id
    if not session_id:
        return False, "ARM: session_id cannot be empty"

    # Reject absolute paths (start with /)
    if session_id.startswith("/"):
        return False, "ARM: session_id contains invalid path characters (absolute path not allowed)"

    # Reject parent directory traversal (..)
    if ".." in session_id:
        return (
            False,
            "ARM: session_id contains invalid path characters (parent traversal not allowed)",
        )

    # Reject forward slashes (subdirectory traversal)
    if "/" in session_id:
        return False, "ARM: session_id contains invalid path characters (slash not allowed)"

    # Reject backslashes (Windows path separators)
    if "\\" in session_id:
        return False, "ARM: session_id contains invalid path characters (backslash not allowed)"

    return True, ""


def inject_arm_section(
    session_id: str,
    working_dir: str,
) -> ARMInjectionResult:
    """
    Inject ARM section from session/git state (server-authoritative).

    The ARM section is computed by the tool from authoritative sources:
    - PHASE: From PROJECT-CONTEXT.oct.md
    - BRANCH: From git rev-parse
    - AHEAD/BEHIND: From git rev-list
    - FILES: From git status
    - FOCUS: From session.json

    Args:
        session_id: Session ID from clock_in
        working_dir: Project working directory path

    Returns:
        ARMInjectionResult with computed ARM values
    """
    errors = []
    phase = ""
    branch = None
    ahead = 0
    behind = 0
    files_count = 0
    top_files: list[str] = []
    focus = ""

    # Validate session_id to prevent path traversal attacks (Security: Issue #2)
    is_valid, error_msg = _validate_session_id(session_id)
    if not is_valid:
        return ARMInjectionResult(valid=False, errors=[error_msg])

    working_path = Path(working_dir)

    # Load session data
    session_file = working_path / ".hestai" / "sessions" / "active" / session_id / "session.json"
    if not session_file.exists():
        errors.append(f"ARM: Session '{session_id}' not found. Run clock_in first.")
        return ARMInjectionResult(valid=False, errors=errors)

    try:
        session_data = json.loads(session_file.read_text())
        focus = session_data.get("focus", "general")
    except (json.JSONDecodeError, OSError) as e:
        errors.append(f"ARM: Failed to read session data: {e}")
        return ARMInjectionResult(valid=False, errors=errors)

    # Extract PHASE from PROJECT-CONTEXT.oct.md
    project_context = working_path / ".hestai" / "context" / "PROJECT-CONTEXT.oct.md"
    if project_context.exists():
        try:
            content = project_context.read_text()
            phase_match = re.search(r"PHASE::(\w+)", content)
            if phase_match:
                phase = phase_match.group(1)
        except OSError as e:
            logger.warning(f"Failed to read PROJECT-CONTEXT: {e}")

    # Get git branch info
    try:
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(working_path),
        )
        # Git command success -> use branch name; failure -> fallback to "unknown"
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # Git not available or other error - use fallback
        branch = "unknown"

    # Get ahead/behind if tracking remote
    if branch and branch != "HEAD":
        try:
            # Get tracking branch
            tracking_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(working_path),
            )
            if tracking_result.returncode == 0:
                upstream = tracking_result.stdout.strip()

                # Count ahead
                ahead_result = subprocess.run(
                    ["git", "rev-list", "--count", f"{upstream}..HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=str(working_path),
                )
                if ahead_result.returncode == 0:
                    ahead = int(ahead_result.stdout.strip())

                # Count behind
                behind_result = subprocess.run(
                    ["git", "rev-list", "--count", f"HEAD..{upstream}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=str(working_path),
                )
                if behind_result.returncode == 0:
                    behind = int(behind_result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError, ValueError):
            pass

    # Get modified files from git status
    try:
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(working_path),
        )
        if status_result.returncode == 0:
            lines = [line for line in status_result.stdout.strip().split("\n") if line]
            files_count = len(lines)
            # Extract top 3 file names
            for line in lines[:3]:
                if len(line) > 3:
                    top_files.append(line[3:].strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return ARMInjectionResult(
        valid=True,
        phase=phase,
        branch=branch,
        ahead=ahead,
        behind=behind,
        files_count=files_count,
        top_files=top_files,
        focus=focus,
        errors=errors,
    )


# =============================================================================
# Anchor State Persistence (OA-I6 Support)
# =============================================================================


def _persist_anchor_state(
    session_id: str,
    working_dir: str,
    role: str,
    tier: str,
) -> tuple[bool, str]:
    """
    Persist anchor validation state to session directory.

    This enables OA-I6 tool gating - work tools can check has_valid_anchor()
    to verify an agent has completed the binding ceremony before executing.

    Creates anchor.json in: .hestai/sessions/active/{session_id}/anchor.json

    Args:
        session_id: Session ID from clock_in
        working_dir: Project working directory path
        role: The validated agent role
        tier: The validation tier used

    Returns:
        Tuple of (success, error_message). On success, error_message is empty.
        On failure, error_message describes what went wrong.
    """
    working_path = Path(working_dir)
    session_dir = working_path / ".hestai" / "sessions" / "active" / session_id

    if not session_dir.exists():
        error_msg = f"Failed to persist anchor state: session directory not found ({session_id})"
        logger.warning(error_msg)
        return False, error_msg

    anchor_data = {
        "validated": True,
        "timestamp": datetime.now(UTC).isoformat(),
        "role": role,
        "tier": tier,
    }

    anchor_file = session_dir / "anchor.json"
    try:
        anchor_file.write_text(json.dumps(anchor_data, indent=2))
        logger.info(f"Anchor state persisted for session: {session_id}")
        return True, ""
    except OSError as e:
        error_msg = f"Failed to persist anchor state: {e}"
        logger.error(f"{error_msg} (session: {session_id})")
        return False, error_msg


# =============================================================================
# Semantic Validation Integration (Issue #131)
# =============================================================================


def _run_semantic_validation(
    role: str,
    cognition_type: str,
    tensions: list[dict],
    commit_artifact: str,
    working_dir: str,
) -> SemanticValidationResult:
    """
    Run semantic validation if enabled (sync wrapper for async validation).

    This function loads semantic config and runs AI-driven validation checks
    if enabled. Handles async context properly:
    - If called from running event loop (MCP server): uses thread pool executor
    - If called from sync context: uses asyncio.run()

    On error or timeout: returns success=True (graceful degradation).

    Args:
        role: The agent role from BIND section
        cognition_type: The cognition type (ETHOS, LOGOS, PATHOS)
        tensions: List of parsed tensions from TENSION section
        commit_artifact: The artifact from COMMIT section
        working_dir: Project working directory

    Returns:
        SemanticValidationResult with success status and concerns
    """
    # Import here to avoid circular imports
    from hestai_mcp.modules.tools.odyssean_anchor_semantic import (
        SemanticValidationResult,
        load_semantic_config,
        validate_semantic,
    )

    try:
        config = load_semantic_config()

        # Short-circuit if disabled
        if not config.enabled:
            return SemanticValidationResult(success=True, skipped=True)

        # Check if we're already in a running event loop
        try:
            asyncio.get_running_loop()
            # We're in an async context (e.g., MCP server's call_tool)
            # Run the async validation in a thread pool to avoid blocking
            import concurrent.futures

            def run_in_new_loop() -> SemanticValidationResult:
                """Run the async validation in a new event loop in a thread."""
                return asyncio.run(
                    validate_semantic(
                        role=role,
                        cognition_type=cognition_type,
                        tensions=tensions,
                        commit_artifact=commit_artifact,
                        working_dir=working_dir,
                        config=config,
                    )
                )

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                result = future.result(timeout=config.timeout_seconds + 5)

            return result

        except RuntimeError:
            # No running event loop - we can use asyncio.run() directly
            result = asyncio.run(
                validate_semantic(
                    role=role,
                    cognition_type=cognition_type,
                    tensions=tensions,
                    commit_artifact=commit_artifact,
                    working_dir=working_dir,
                    config=config,
                )
            )
            return result

    except Exception as e:
        # Graceful degradation on any error
        logger.warning(f"Semantic validation error: {e}")
        return SemanticValidationResult(success=True, skipped=True, concerns=[])


# =============================================================================
# Format Guidance Builder
# =============================================================================


def _build_format_guide(
    bind_errors: list[str],
    tension_errors: list[str],
    commit_errors: list[str],
    tier: str = "default",
) -> str:
    """
    Build comprehensive format guidance with concrete examples.

    This addresses the usability issue where agents receive validation errors
    but no clear examples of the correct format. Provides section-by-section
    guidance with actual working examples.

    Args:
        bind_errors: List of BIND section validation errors
        tension_errors: List of TENSION section validation errors
        commit_errors: List of COMMIT section validation errors
        tier: Validation tier for tension-specific guidance

    Returns:
        Formatted guidance string with concrete examples
    """
    guide_parts = ["REQUIRED FORMAT (copy and modify this template):"]

    # BIND section guidance
    if bind_errors:
        guide_parts.append(
            "\n## BIND\n"
            "ROLE::your-agent-role\n"
            "COGNITION::LOGOS::ATLAS\n"
            "  # Or multi-archetype: COGNITION::LOGOS::ATLAS⊕PROMETHEUS⊕HEPHAESTUS\n"
            "  # Valid types: ETHOS, LOGOS, PATHOS\n"
            f"  # Valid archetypes: {', '.join(sorted(list(VALID_ARCHETYPES)[:5]))}...\n"
            "AUTHORITY::RESPONSIBLE[your_domain+specific_scope]\n"
            "  # Or: AUTHORITY::DELEGATED[parent_session]"
        )

    # TENSION section guidance
    if tension_errors:
        min_tensions = TIER_TENSION_REQUIREMENTS.get(tier, 2)
        if tier == "deep":
            guide_parts.append(
                f"\n## TENSION (minimum {min_tensions} required for tier '{tier}')\n"
                "L1::[SPECIFIC_CONSTRAINT]⇌CTX:path/to/file.md:10-20[state_description]→TRIGGER[action]\n"
                "L2::[ANOTHER_CONSTRAINT]⇌CTX:src/module.py:45-67[relevant_state]→TRIGGER[handle_violation]\n"
                "L3::[THIRD_CONSTRAINT]⇌CTX:docs/architecture.md:100-150[arch_state]→TRIGGER[escalate]\n"
                "  # Deep tier REQUIRES line ranges (e.g., :10-20) in CTX citations\n"
                "  # Format: CTX:filename:start-end[state] (line range BEFORE brackets)"
            )
        elif tier == "default":
            guide_parts.append(
                f"\n## TENSION (minimum {min_tensions} required for tier '{tier}')\n"
                "L1::[SPECIFIC_CONSTRAINT]⇌CTX:path/to/file.md[state_description]→TRIGGER[action]\n"
                "L2::[ANOTHER_CONSTRAINT]⇌CTX:src/module.py[relevant_state]→TRIGGER[handle_violation]\n"
                "  # Use ⇌ (or <-> as ASCII alias) for tension operator\n"
                "  # Use → (or -> as ASCII alias) for flow operator\n"
                "  # Constraint names must be SPECIFIC (not 'CONSTRAINT', 'RULE', 'TODO')"
            )
        else:  # quick
            guide_parts.append(
                f"\n## TENSION (minimum {min_tensions} required for tier '{tier}')\n"
                "L1::[SPECIFIC_CONSTRAINT]⇌CTX:path/to/file.md[state]→TRIGGER[action]\n"
                "  # Even 'quick' tier requires proper CTX citation and TRIGGER"
            )

    # COMMIT section guidance
    if commit_errors:
        guide_parts.append(
            "\n## COMMIT\n"
            "ARTIFACT::path/to/output.py[function_name+module_changes]\n"
            "  # Use concrete paths, not 'response', 'output', 'result'\n"
            "GATE::pytest[test_file.py]\n"
            "  # Or: GATE::manual_review[specific_criteria]\n"
            "  # Or: GATE::build[npm_run_typecheck]"
        )

    # Add reference to full documentation
    guide_parts.append(
        "\n\nREFERENCE: See .hestai-sys/library/commands/bind.md for full ceremony documentation"
    )

    return "\n".join(guide_parts)


# =============================================================================
# Main Odyssean Anchor Tool
# =============================================================================


def odyssean_anchor(
    role: str,
    vector_candidate: str,
    session_id: str,
    working_dir: str,
    tier: str = "default",
    retry_count: int = 0,
) -> OdysseanAnchorResult:
    """
    Validate and complete agent identity vector (RAPH Vector v4.0).

    This tool:
    1. Validates BIND section (agent provides)
    2. Validates TENSION section (agent provides, CTX citations required)
    3. Validates COMMIT section (agent provides)
    4. Injects ARM section (server-authoritative from session/git)
    5. Runs semantic validation if enabled (Issue #131)
    6. Returns validated anchor or retry guidance

    Semantic Validation (optional, Issue #131):
    - Configurable via ai.yaml odyssean_anchor.semantic_validation section
    - Environment overrides: HESTAI_OA_SEMANTIC_VALIDATION, HESTAI_OA_SEMANTIC_FAIL_MODE
    - Checks: cognition_appropriateness, tension_relevance, ctx_validity, commit_feasibility
    - Default: disabled for backward compatibility

    Self-Correction Protocol (OA-I3):
    - Max 2 retries with specific guidance per failure
    - Terminal failure after max retries

    Args:
        role: Expected role name (must match BIND.ROLE)
        vector_candidate: Agent's BIND+TENSION+COMMIT sections
        session_id: Session ID from clock_in for ARM injection
        working_dir: Project working directory
        tier: Validation tier (quick, default, deep)
        retry_count: Current retry attempt (0, 1, 2)

    Returns:
        OdysseanAnchorResult with validated anchor or failure guidance
    """
    all_errors: list[str] = []
    guidance_parts: list[str] = []

    # 1. Validate BIND section
    bind_result = validate_bind_section(vector_candidate)
    if not bind_result.valid:
        all_errors.extend(bind_result.errors)
        for error in bind_result.errors:
            if "ROLE" in error:
                guidance_parts.append(
                    "- Add ROLE::{agent_name} to BIND section\n"
                    "- Role must match the role parameter passed to odyssean_anchor"
                )
            if "COGNITION" in error:
                guidance_parts.append(
                    "- Add COGNITION::{type}::{archetype} to BIND section\n"
                    "- Multiple archetypes supported: {type}::{arch1}⊕{arch2}⊕{arch3}\n"
                    f"- Valid types: {', '.join(sorted(VALID_COGNITION_TYPES))}\n"
                    f"- Valid archetypes: {', '.join(sorted(VALID_ARCHETYPES))}"
                )
            if "AUTHORITY" in error:
                guidance_parts.append(
                    "- Add AUTHORITY::RESPONSIBLE[...] or AUTHORITY::DELEGATED[parent_session]\n"
                    "- Include scope description in brackets"
                )

    # Check role mismatch
    if bind_result.role and bind_result.role != role:
        all_errors.append(f"BIND: Role mismatch. Expected '{role}', found '{bind_result.role}'")
        guidance_parts.append(
            f"- Change ROLE::{bind_result.role} to ROLE::{role}\n"
            "- Role in BIND must match the role parameter"
        )

    # 2. Validate TENSION section (must extract section first to prevent cross-section pollution)
    tension_section = _extract_tension_section(vector_candidate)
    tension_result = validate_tension_section(tension_section, tier=tier)
    if not tension_result.valid:
        all_errors.extend(tension_result.errors)
        for error in tension_result.errors:
            if "CTX" in error:
                guidance_parts.append(
                    "- Add CTX:{filename}:{line_range}->evidence to TENSION lines\n"
                    "- Cite actual file from your loaded context\n"
                    "- Verify file exists in your working directory"
                )
            if "TRIGGER" in error:
                guidance_parts.append(
                    "- Add TRIGGER[{action}] to end of TENSION line\n"
                    "- Action should be concrete (DELEGATE, HALT, VALIDATE, SCAN)\n"
                    "- Reference what happens when tension activates"
                )
            if "Insufficient" in error:
                min_req = TIER_TENSION_REQUIREMENTS.get(tier, 2)
                guidance_parts.append(
                    f"- Add more TENSION lines. Tier '{tier}' requires minimum {min_req}\n"
                    "- Format: L{{N}}::[constraint]⇌CTX:path[state]→TRIGGER[action]"
                )
            if "generic" in error.lower():
                guidance_parts.append(
                    "- Replace generic constraint name with specific one\n"
                    "- Good: TDD_MANDATE, MINIMAL_INTERVENTION, LANE_ENFORCEMENT\n"
                    "- Bad: CONSTRAINT, RULE, TODO"
                )
            if "line range" in error.lower():
                guidance_parts.append(
                    "- Deep tier requires line ranges in CTX citations\n"
                    "- Format: CTX:path/file.md:10-20[state]\n"
                    "- Include specific line numbers for precision"
                )

    # 3. Validate COMMIT section
    commit_result = validate_commit_section(vector_candidate)
    if not commit_result.valid:
        all_errors.extend(commit_result.errors)
        for error in commit_result.errors:
            if "ARTIFACT" in error:
                if "generic" in error.lower():
                    guidance_parts.append(
                        "- Replace generic artifact with actual output path\n"
                        "- Use concrete filename (e.g., 'src/validators/anchor.ts')\n"
                        "- Include file extension or method name"
                    )
                elif "placeholder" in error.lower():
                    guidance_parts.append(
                        "- Replace placeholder with actual artifact path\n"
                        "- No TODO, TBD, or PLACEHOLDER values allowed"
                    )
                else:
                    guidance_parts.append(
                        "- Add ARTIFACT::{file_path} to COMMIT section\n"
                        "- Use concrete file path, not generic terms"
                    )
            if "GATE" in error:
                guidance_parts.append(
                    "- Add GATE::{validation_method} to COMMIT section\n"
                    "- Specify how artifact will be validated (e.g., pytest, manual review)"
                )

    # 4. Inject ARM section (server-authoritative)
    arm_result = inject_arm_section(
        session_id=session_id,
        working_dir=working_dir,
    )
    if not arm_result.valid:
        all_errors.extend(arm_result.errors)
        guidance_parts.append(
            "- Ensure valid session_id from clock_in\n" "- Verify working_dir path is correct"
        )

    # 5. Semantic validation (optional, AI-driven, Issue #131)
    # Only runs if structural validation passes and semantic validation is enabled
    if not all_errors:
        semantic_result = _run_semantic_validation(
            role=role,
            cognition_type=bind_result.cognition_type,
            tensions=tension_result.tensions,
            commit_artifact=commit_result.artifact,
            working_dir=working_dir,
        )
        if not semantic_result.success:
            all_errors.extend(semantic_result.concerns)
            guidance_parts.append(
                "- Review semantic validation concerns above\n"
                "- Ensure COGNITION type matches role responsibilities\n"
                "- Verify CTX files exist and are accessible"
            )

    # If any errors, return failure with guidance
    if all_errors:
        # Build comprehensive format guidance with concrete examples
        format_guide = _build_format_guide(
            bind_errors=[e for e in all_errors if "BIND" in e],
            tension_errors=[e for e in all_errors if "TENSION" in e],
            commit_errors=[e for e in all_errors if "COMMIT" in e],
            tier=tier,
        )

        # Check if max retries exhausted AFTER validation
        # This ensures agents see validation errors even on final attempt
        if retry_count >= MAX_RETRIES:
            return OdysseanAnchorResult(
                success=False,
                anchor=None,
                errors=all_errors,
                guidance="VECTOR VALIDATION FAILED (max retries exhausted)\n"
                "---\n\n"
                "FINAL ATTEMPT FAILURES:\n"
                + "\n".join(f"{i}. {error}" for i, error in enumerate(all_errors, 1))
                + "\n\n---\n\n"
                + format_guide
                + "\n\n---\n\n"
                "Agent cannot proceed without valid anchor.\n"
                "Escalate to manual review or fix the errors above.",
                retry_count=retry_count,
                terminal=True,
            )

        # Remove duplicate guidance entries
        unique_guidance = list(dict.fromkeys(guidance_parts))
        guidance = (
            "VALIDATION_FAILED: Odyssean Anchor rejected\n"
            "---\n\n"
            "FAILURES:\n"
            + "\n".join(f"{i}. {error}" for i, error in enumerate(all_errors, 1))
            + "\n\n---\n\n"
            + format_guide
            + "\n\n---\n\n"
            "RETRY GUIDANCE:\n"
            + "\n".join(unique_guidance)
            + f"\n\nRETRY_ATTEMPT: {retry_count} of 2 (regenerate and resubmit)"
        )

        return OdysseanAnchorResult(
            success=False,
            anchor=None,
            errors=all_errors,
            guidance=guidance,
            retry_count=retry_count,
            terminal=False,
        )

    # 5. Build validated anchor with injected ARM
    arm_section = _build_arm_section(arm_result)

    # Extract agent-provided sections and combine with ARM
    validated_anchor = _build_validated_anchor(
        bind_result=bind_result,
        arm_section=arm_section,
        tension_text=_extract_tension_section(vector_candidate),
        commit_result=commit_result,
    )

    # 6. Persist anchor state for OA-I6 tool gating
    # CRITICAL: Must check for persistence failure to prevent "zombie state"
    # where agent appears bound but anchor.json not written to disk
    persist_success, persist_error = _persist_anchor_state(
        session_id=session_id,
        working_dir=working_dir,
        role=role,
        tier=tier,
    )

    if not persist_success:
        return OdysseanAnchorResult(
            success=False,
            anchor=None,
            errors=[persist_error],
            guidance=(
                "VALIDATION_FAILED: Anchor state could not be persisted\n"
                "---\n\n"
                f"ERROR: {persist_error}\n\n"
                "RETRY GUIDANCE:\n"
                "- Verify session directory exists and is writable\n"
                "- Check disk space and permissions\n"
                "- Retry the odyssean_anchor call"
            ),
            retry_count=retry_count,
            terminal=False,
        )

    return OdysseanAnchorResult(
        success=True,
        anchor=validated_anchor,
        errors=[],
        guidance="",
        retry_count=retry_count,
        terminal=False,
    )


def _build_arm_section(arm_result: ARMInjectionResult) -> str:
    """Build ARM section from injection result."""
    branch_str = arm_result.branch or "unknown"
    if arm_result.ahead or arm_result.behind:
        branch_str = f"{branch_str}[{arm_result.ahead}up{arm_result.behind}down]"

    files_str = f"{arm_result.files_count}"
    if arm_result.top_files:
        files_str += f"[{','.join(arm_result.top_files[:3])}]"
    else:
        files_str += "[]"

    return f"""## ARM (Context Proof - SERVER INJECTED)
PHASE::{arm_result.phase}
BRANCH::{branch_str}
FILES::{files_str}
FOCUS::{arm_result.focus}"""


def _extract_tension_section(vector_candidate: str) -> str:
    """Extract TENSION section from vector candidate."""
    lines = []
    in_tension = False

    for line in vector_candidate.split("\n"):
        if "## TENSION" in line:
            in_tension = True
            lines.append(line)
            continue

        if in_tension:
            if line.startswith("## "):
                break
            lines.append(line)

    return "\n".join(lines)


def _build_validated_anchor(
    bind_result: BindValidationResult,
    arm_section: str,
    tension_text: str,
    commit_result: CommitValidationResult,
) -> str:
    """Build complete validated anchor from components."""
    return f"""===RAPH_VECTOR::v4.0===
## BIND (Identity Lock)
ROLE::{bind_result.role}
COGNITION::{bind_result.cognition_type}::{bind_result.cognition_archetype}
AUTHORITY::{bind_result.authority}

{arm_section}

{tension_text}

## COMMIT (Falsifiable Contract)
ARTIFACT::{commit_result.artifact}
GATE::{commit_result.gate}
===END_RAPH_VECTOR==="""
