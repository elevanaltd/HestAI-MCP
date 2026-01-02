"""
Odyssean Anchor Semantic Validation - AI-driven semantic checks.

This module provides optional AI-driven semantic validation for the odyssean_anchor
tool. When enabled, it validates that TENSION and COMMIT sections reflect genuine
understanding rather than surface-level compliance.

Key Features:
- Config loading from ai.yaml (odyssean_anchor.semantic_validation section)
- Environment variable overrides (HESTAI_OA_SEMANTIC_VALIDATION, HESTAI_OA_SEMANTIC_FAIL_MODE)
- Four semantic checks:
  1. cognition_appropriateness: Is COGNITION type correct for role?
  2. tension_relevance: Do TENSIONs cite constraints that exist?
  3. ctx_validity: Do CTX paths reference actual files? (non-AI)
  4. commit_feasibility: Is COMMIT artifact achievable?
- Graceful degradation on timeout/error

GitHub Issue: #131
ADR: docs/adr/adr-0036-odyssean-anchor-binding.md (Semantic Validation Extension)
"""

import asyncio
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from hestai_mcp.ai.client import AIClient
from hestai_mcp.ai.config import AITier, get_yaml_config_path
from hestai_mcp.ai.providers.base import CompletionRequest

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration Models
# =============================================================================


class SemanticChecksConfig(BaseModel):
    """Configuration for individual semantic checks."""

    cognition_appropriateness: bool = True
    tension_relevance: bool = True
    ctx_validity: bool = True
    commit_feasibility: bool = True


class SemanticConfig(BaseModel):
    """Configuration for semantic validation."""

    enabled: bool = False  # Default off for backward compatibility
    tier: AITier = "analysis"
    timeout_seconds: int = 15
    fail_mode: Literal["warn", "block"] = "warn"
    checks: SemanticChecksConfig = Field(default_factory=SemanticChecksConfig)


# =============================================================================
# Result Dataclasses
# =============================================================================


@dataclass
class SemanticValidationResult:
    """Result from semantic validation."""

    success: bool
    skipped: bool = False
    timed_out: bool = False
    concerns: list[str] = field(default_factory=list)


@dataclass
class CognitionAppropriatenessResult:
    """Result from cognition appropriateness check."""

    appropriate: bool
    concern: str | None = None


@dataclass
class CtxValidityResult:
    """Result from CTX validity check."""

    valid: bool
    missing_files: list[str] = field(default_factory=list)


@dataclass
class TensionRelevanceResult:
    """Result from tension relevance check."""

    valid: bool
    invalid_constraints: list[str] = field(default_factory=list)


@dataclass
class CommitFeasibilityResult:
    """Result from commit feasibility check."""

    feasible: bool
    concern: str | None = None


# =============================================================================
# Configuration Loading
# =============================================================================


def load_semantic_config() -> SemanticConfig:
    """
    Load semantic validation config from ai.yaml.

    Resolution order:
    1. Environment variable overrides (HESTAI_OA_SEMANTIC_VALIDATION, HESTAI_OA_SEMANTIC_FAIL_MODE)
    2. ai.yaml odyssean_anchor.semantic_validation section
    3. Defaults (disabled, warn mode)

    Returns:
        SemanticConfig instance
    """
    config = _load_config_from_yaml()

    # Apply environment variable overrides
    config = _apply_env_overrides(config)

    return config


def _load_config_from_yaml() -> SemanticConfig:
    """Load config from ai.yaml file."""
    yaml_path = get_yaml_config_path()

    if not yaml_path.exists():
        logger.debug(f"No ai.yaml found at {yaml_path}, using defaults")
        return SemanticConfig()

    try:
        config_data = yaml.safe_load(yaml_path.read_text())
        if not config_data:
            return SemanticConfig()

        # Extract odyssean_anchor.semantic_validation section
        oa_config = config_data.get("odyssean_anchor", {})
        semantic_config = oa_config.get("semantic_validation", {})

        if not semantic_config:
            return SemanticConfig()

        # Parse checks subsection
        checks_data = semantic_config.get("checks", {})
        checks = SemanticChecksConfig(**checks_data) if checks_data else SemanticChecksConfig()

        return SemanticConfig(
            enabled=semantic_config.get("enabled", False),
            tier=semantic_config.get("tier", "analysis"),
            timeout_seconds=semantic_config.get("timeout_seconds", 15),
            fail_mode=semantic_config.get("fail_mode", "warn"),
            checks=checks,
        )

    except (yaml.YAMLError, TypeError, ValueError) as e:
        logger.warning(f"Error parsing ai.yaml: {e}, using defaults")
        return SemanticConfig()


def _apply_env_overrides(config: SemanticConfig) -> SemanticConfig:
    """Apply environment variable overrides to config."""
    # HESTAI_OA_SEMANTIC_VALIDATION override
    env_enabled = os.environ.get("HESTAI_OA_SEMANTIC_VALIDATION")
    if env_enabled is not None:
        enabled = env_enabled.lower() in ("true", "1", "yes")
        config = SemanticConfig(
            enabled=enabled,
            tier=config.tier,
            timeout_seconds=config.timeout_seconds,
            fail_mode=config.fail_mode,
            checks=config.checks,
        )

    # HESTAI_OA_SEMANTIC_FAIL_MODE override
    env_fail_mode = os.environ.get("HESTAI_OA_SEMANTIC_FAIL_MODE")
    if env_fail_mode is not None and env_fail_mode in ("warn", "block"):
        config = SemanticConfig(
            enabled=config.enabled,
            tier=config.tier,
            timeout_seconds=config.timeout_seconds,
            fail_mode=env_fail_mode,  # type: ignore[arg-type]
            checks=config.checks,
        )

    return config


# =============================================================================
# Main Validation Function
# =============================================================================


async def validate_semantic(
    role: str,
    cognition_type: str,
    tensions: list[dict],
    commit_artifact: str,
    working_dir: str,
    config: SemanticConfig | None = None,
) -> SemanticValidationResult:
    """
    Perform semantic validation on anchor components.

    This function runs after structural validation passes. It validates
    semantic correctness using AI-driven checks.

    Args:
        role: The agent role from BIND section
        cognition_type: The cognition type (ETHOS, LOGOS, PATHOS)
        tensions: List of parsed tensions from TENSION section
        commit_artifact: The artifact from COMMIT section
        working_dir: Project working directory
        config: Semantic config (loaded from yaml if None)

    Returns:
        SemanticValidationResult with success status and any concerns
    """
    if config is None:
        config = load_semantic_config()

    # Short-circuit if disabled
    if not config.enabled:
        return SemanticValidationResult(success=True, skipped=True)

    concerns: list[str] = []
    timed_out = False

    try:
        # Run checks with timeout
        async with asyncio.timeout(config.timeout_seconds):
            # Run CTX validity check (non-AI, always fast)
            if config.checks.ctx_validity:
                ctx_result = check_ctx_validity(tensions, working_dir)
                if not ctx_result.valid:
                    for missing in ctx_result.missing_files:
                        concerns.append(f"CTX file not found: {missing}")

            # Run AI-powered checks
            if config.checks.cognition_appropriateness:
                try:
                    cog_result = await check_cognition_appropriateness(
                        role=role,
                        cognition_type=cognition_type,
                        tier=config.tier,
                    )
                    if not cog_result.appropriate and cog_result.concern:
                        concerns.append(f"Cognition concern: {cog_result.concern}")
                except Exception as e:
                    logger.warning(f"Cognition appropriateness check failed: {e}")
                    # Graceful degradation - don't fail on AI errors

            if config.checks.tension_relevance:
                try:
                    # Load constitution for reference
                    constitution_text = _load_constitution(working_dir)
                    rel_result = await check_tension_relevance(
                        tensions=tensions,
                        constitution_text=constitution_text,
                        tier=config.tier,
                    )
                    if not rel_result.valid:
                        for invalid in rel_result.invalid_constraints:
                            concerns.append(f"Invalid constraint: {invalid}")
                except Exception as e:
                    logger.warning(f"Tension relevance check failed: {e}")

            if config.checks.commit_feasibility:
                try:
                    # Get focus from session if available
                    focus = _get_session_focus(working_dir)
                    feas_result = await check_commit_feasibility(
                        artifact=commit_artifact,
                        focus=focus,
                        tier=config.tier,
                    )
                    if not feas_result.feasible and feas_result.concern:
                        concerns.append(f"Commit concern: {feas_result.concern}")
                except Exception as e:
                    logger.warning(f"Commit feasibility check failed: {e}")

    except TimeoutError:
        logger.warning(f"Semantic validation timed out after {config.timeout_seconds}s")
        timed_out = True
        concerns.append(f"Semantic validation timed out ({config.timeout_seconds}s)")

    except Exception as e:
        logger.warning(f"Semantic validation error: {e}")
        # Graceful degradation on unexpected errors

    # Determine success based on fail_mode
    if config.fail_mode == "warn":
        # In warn mode, always succeed but log concerns
        if concerns:
            for concern in concerns:
                logger.warning(f"Semantic concern: {concern}")
        return SemanticValidationResult(
            success=True,
            skipped=False,
            timed_out=timed_out,
            concerns=concerns,
        )
    else:
        # In block mode, fail if there are concerns
        return SemanticValidationResult(
            success=len(concerns) == 0,
            skipped=False,
            timed_out=timed_out,
            concerns=concerns,
        )


# =============================================================================
# Individual Check Functions
# =============================================================================


def check_ctx_validity(tensions: list[dict], working_dir: str) -> CtxValidityResult:
    """
    Check if CTX paths reference actual files (non-AI check).

    Args:
        tensions: List of parsed tensions with ctx_path field
        working_dir: Project working directory

    Returns:
        CtxValidityResult with validity and list of missing files
    """
    missing_files: list[str] = []
    working_path = Path(working_dir)

    for tension in tensions:
        ctx_path = tension.get("ctx_path", "")
        if not ctx_path:
            continue

        # Strip line range suffixes (e.g., ":10-20" or ":45")
        clean_path = re.sub(r":\d+(-\d+)?$", "", ctx_path)

        # Check if file exists
        full_path = working_path / clean_path
        if not full_path.exists():
            missing_files.append(ctx_path)

    return CtxValidityResult(
        valid=len(missing_files) == 0,
        missing_files=missing_files,
    )


async def check_cognition_appropriateness(
    role: str,
    cognition_type: str,
    tier: AITier,
) -> CognitionAppropriatenessResult:
    """
    Check if cognition type is appropriate for the role using AI.

    Expected mappings (guidance, not strict):
    - LOGOS: architects, coordinators, technical leads
    - ETHOS: validators, guardians, reviewers
    - PATHOS: ideators, explorers, researchers

    Args:
        role: The agent role
        cognition_type: The cognition type (ETHOS, LOGOS, PATHOS)
        tier: AI tier to use

    Returns:
        CognitionAppropriatenessResult with appropriateness and concern
    """
    system_prompt = """You are a semantic validator for agent identity binding.
Your task is to assess if a cognition type is appropriate for an agent role.

Cognition types and their typical associations:
- LOGOS (The Door/Structure): architects, coordinators, technical leads, implementation leads
- ETHOS (The Wall/Boundary): validators, guardians, reviewers, stewards, security specialists
- PATHOS (The Wind/Possibility): ideators, explorers, researchers, creative roles

Respond with JSON: {"appropriate": true/false, "reason": "explanation"}
Be lenient - many roles can reasonably use different cognition types.
Only flag clear mismatches (e.g., validator using PATHOS for exploration-focused work)."""

    user_prompt = f"""Assess if this cognition type is appropriate for this role:
Role: {role}
Cognition Type: {cognition_type}

Respond with JSON only."""

    async with AIClient() as client:
        response = await client.complete_text(
            CompletionRequest(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
            ),
            tier=tier,
        )

    # Parse response
    try:
        import json

        result = json.loads(response)
        if result.get("appropriate", True):
            return CognitionAppropriatenessResult(appropriate=True)
        else:
            return CognitionAppropriatenessResult(
                appropriate=False,
                concern=result.get("reason", f"{cognition_type} may not be appropriate for {role}"),
            )
    except (json.JSONDecodeError, KeyError):
        # If we can't parse, assume appropriate (graceful degradation)
        logger.warning(f"Could not parse AI response for cognition check: {response}")
        return CognitionAppropriatenessResult(appropriate=True)


async def check_tension_relevance(
    tensions: list[dict],
    constitution_text: str,
    tier: AITier,
) -> TensionRelevanceResult:
    """
    Check if tension constraints reference real constraints using AI.

    Validates that constraint names aren't hallucinated.

    Args:
        tensions: List of parsed tensions with constraint field
        constitution_text: Text of loaded constitution for reference
        tier: AI tier to use

    Returns:
        TensionRelevanceResult with validity and invalid constraints
    """
    if not tensions:
        return TensionRelevanceResult(valid=True)

    constraint_names = [t.get("constraint", "") for t in tensions if t.get("constraint")]
    if not constraint_names:
        return TensionRelevanceResult(valid=True)

    system_prompt = """You are a semantic validator checking if constraint names are real.
Given a list of constraint names and a constitution text, determine which constraints
appear to be real (mentioned or implied in the constitution) vs hallucinated.

Common real constraint patterns: TDD_MANDATE, MINIMAL_INTERVENTION, MIP, LANE_ENFORCEMENT,
QUALITY_GATES, HUMAN_PRIMACY, I1-I6 immutables, PHASE_GATED, etc.

Respond with JSON: {"all_valid": true/false, "invalid_constraints": ["list", "of", "hallucinated"]}
Be lenient - if a constraint could reasonably derive from the constitution, accept it."""

    user_prompt = f"""Check these constraints against the constitution:
Constraints: {constraint_names}

Constitution excerpt:
{constitution_text[:2000]}

Respond with JSON only."""

    async with AIClient() as client:
        response = await client.complete_text(
            CompletionRequest(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
            ),
            tier=tier,
        )

    try:
        import json

        result = json.loads(response)
        if result.get("all_valid", True):
            return TensionRelevanceResult(valid=True)
        else:
            return TensionRelevanceResult(
                valid=False,
                invalid_constraints=result.get("invalid_constraints", []),
            )
    except (json.JSONDecodeError, KeyError):
        logger.warning(f"Could not parse AI response for tension check: {response}")
        return TensionRelevanceResult(valid=True)


async def check_commit_feasibility(
    artifact: str,
    focus: str,
    tier: AITier,
) -> CommitFeasibilityResult:
    """
    Check if commit artifact is achievable using AI.

    Args:
        artifact: The artifact path/description from COMMIT
        focus: The session focus area
        tier: AI tier to use

    Returns:
        CommitFeasibilityResult with feasibility and concern
    """
    system_prompt = """You are a semantic validator checking if a commit artifact is achievable.
An artifact is achievable if it's a concrete, specific output that could be produced in a session.

Examples of achievable artifacts:
- src/validators/semantic.py (specific file)
- Updated test suite for anchor validation
- PR #123 with implementation

Examples of unrealistic artifacts:
- Complete system rewrite
- All bugs fixed
- Perfect documentation

Respond with JSON: {"feasible": true/false, "reason": "explanation"}
Be lenient - most specific artifacts are achievable."""

    user_prompt = f"""Assess if this artifact is achievable:
Artifact: {artifact}
Focus: {focus}

Respond with JSON only."""

    async with AIClient() as client:
        response = await client.complete_text(
            CompletionRequest(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
            ),
            tier=tier,
        )

    try:
        import json

        result = json.loads(response)
        if result.get("feasible", True):
            return CommitFeasibilityResult(feasible=True)
        else:
            return CommitFeasibilityResult(
                feasible=False,
                concern=result.get("reason", f"Artifact may not be achievable: {artifact}"),
            )
    except (json.JSONDecodeError, KeyError):
        logger.warning(f"Could not parse AI response for feasibility check: {response}")
        return CommitFeasibilityResult(feasible=True)


# =============================================================================
# Helper Functions
# =============================================================================


def _load_constitution(working_dir: str) -> str:
    """Load constitution text for reference."""
    working_path = Path(working_dir)

    # Try common constitution locations
    candidates = [
        working_path / ".hestai" / "workflow" / "000-MCP-PRODUCT-NORTH-STAR.md",
        working_path / "hub" / "governance" / "workflow" / "000-SYSTEM-HESTAI-NORTH-STAR.md",
        Path.home() / ".claude" / "CLAUDE.md",
    ]

    for candidate in candidates:
        if candidate.exists():
            try:
                return candidate.read_text()
            except OSError:
                continue

    return ""


def _get_session_focus(working_dir: str) -> str:
    """Get current session focus if available."""
    working_path = Path(working_dir)
    sessions_dir = working_path / ".hestai" / "sessions" / "active"

    if not sessions_dir.exists():
        return "general"

    # Find most recent session
    try:
        session_dirs = list(sessions_dir.iterdir())
        if not session_dirs:
            return "general"

        for session_dir in sorted(session_dirs, reverse=True):
            session_file = session_dir / "session.json"
            if session_file.exists():
                import json

                data = json.loads(session_file.read_text())
                focus = data.get("focus", "general")
                return str(focus) if focus else "general"
    except (OSError, json.JSONDecodeError):
        pass

    return "general"
