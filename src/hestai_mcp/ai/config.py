"""AI configuration loading, saving, and secret resolution.

Supports tiered AI configuration for different use cases:
- synthesis: Fast, cheap models for context synthesis (clock_in)
- analysis: Balanced models for deeper analysis
- critical: High-capability models for important decisions

Configuration is loaded from:
1. ~/.hestai/config/ai.yaml (preferred, supports tiers)
2. .env file (for API keys and defaults)
3. Environment variables (fallback defaults)

API keys are resolved from:
1. Keyring (secure, production)
2. Environment variables / .env file (development, CI)
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Literal

import keyring
import keyring.errors
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, model_validator

# Load .env file if present (won't override existing env vars)
# Searches current directory and parent directories
load_dotenv()

logger = logging.getLogger(__name__)

# Keyring service name for storing API keys
KEYRING_SERVICE = "hestai-mcp"

# Available AI tiers
AITier = Literal["synthesis", "analysis", "critical"]

# Default tier for operations that don't specify
DEFAULT_TIER: AITier = "synthesis"


class TierConfig(BaseModel):
    """Configuration for a specific AI tier."""

    provider: str
    model: str
    description: str = ""


class TimeoutConfig(BaseModel):
    """Network timeout configuration."""

    connect_seconds: int = 5
    request_seconds: int = 30


class TieredAIConfig(BaseModel):
    """AI configuration with tiered model support.

    Tiers allow different models for different use cases:
    - synthesis: Fast/cheap for routine context generation
    - analysis: Balanced for deeper analysis tasks
    - critical: Best available for high-stakes decisions

    Operations can be mapped to specific tiers via the operations field,
    allowing YAML-based configuration of which tier each operation uses.
    """

    tiers: dict[str, TierConfig] = Field(default_factory=dict)
    operations: dict[str, AITier] = Field(default_factory=dict)
    default_tier: AITier = DEFAULT_TIER
    timeouts: TimeoutConfig = Field(default_factory=TimeoutConfig)

    @model_validator(mode="after")
    def validate_tier_references(self) -> "TieredAIConfig":
        """Validate that all referenced tiers exist.

        Ensures:
        - default_tier exists in tiers (if tiers is non-empty)
        - All operation mappings reference existing tiers

        This catches configuration errors at load time rather than runtime.
        """
        tier_names = set(self.tiers.keys())

        # Skip validation if no tiers configured (empty config)
        if not tier_names:
            return self

        # Validate default_tier exists
        if self.default_tier not in tier_names:
            raise ValueError(f"default_tier '{self.default_tier}' not found in tiers: {tier_names}")

        # Validate all operation mappings reference existing tiers
        for operation, tier in self.operations.items():
            if tier not in tier_names:
                raise ValueError(
                    f"Operation '{operation}' maps to unknown tier '{tier}'. "
                    f"Available tiers: {tier_names}"
                )

        return self

    def get_operation_tier(self, operation: str) -> AITier:
        """Get the tier for a named operation.

        Returns configured tier if operation is mapped, otherwise default_tier.

        Args:
            operation: The operation name (e.g., "clock_in_synthesis", "document_analysis")

        Returns:
            The AITier to use for this operation.
        """
        return self.operations.get(operation, self.default_tier)

    def get_tier_config(self, tier: AITier | None = None) -> TierConfig:
        """Get configuration for a specific tier.

        Args:
            tier: The tier to get config for. Uses default_tier if None.

        Returns:
            TierConfig for the requested tier.

        Raises:
            KeyError: If the tier is not configured.
        """
        tier = tier or self.default_tier
        if tier not in self.tiers:
            raise KeyError(f"AI tier '{tier}' not configured. Available: {list(self.tiers.keys())}")
        return self.tiers[tier]


def get_config_dir() -> Path:
    """Get the HestAI config directory.

    Returns:
        Path to ~/.hestai/config/
    """
    return Path.home() / ".hestai" / "config"


def get_yaml_config_path() -> Path:
    """Get the path to the YAML AI config file.

    Returns:
        Path to ~/.hestai/config/ai.yaml
    """
    return get_config_dir() / "ai.yaml"


def _get_default_tiered_config() -> TieredAIConfig:
    """Get default tiered configuration.

    Uses environment variables if set, otherwise sensible defaults.
    """
    # Check for environment variable overrides
    default_provider = os.environ.get("HESTAI_AI_PROVIDER", "openrouter")
    default_model = os.environ.get("HESTAI_AI_MODEL", "google/gemini-2.0-flash-lite")

    return TieredAIConfig(
        tiers={
            "synthesis": TierConfig(
                provider=default_provider,
                model=default_model,
                description="Fast, cost-effective model for context synthesis",
            ),
            "analysis": TierConfig(
                provider=default_provider,
                model=os.environ.get("HESTAI_AI_MODEL_ANALYSIS", "anthropic/claude-3.5-sonnet"),
                description="Balanced model for deeper analysis",
            ),
            "critical": TierConfig(
                provider=default_provider,
                model=os.environ.get("HESTAI_AI_MODEL_CRITICAL", "anthropic/claude-3.5-sonnet"),
                description="High-capability model for critical decisions",
            ),
        },
        operations={
            "clock_in_synthesis": "synthesis",
            "context_update": "synthesis",
            "document_analysis": "analysis",
        },
        default_tier="synthesis",
        timeouts=TimeoutConfig(),
    )


def load_config() -> TieredAIConfig:
    """Load tiered AI configuration from disk.

    Tries YAML config first, then returns defaults from environment/.env.

    Returns:
        TieredAIConfig instance
    """
    yaml_path = get_yaml_config_path()

    # Try YAML config (preferred)
    if yaml_path.exists():
        try:
            config_data = yaml.safe_load(yaml_path.read_text())
            if config_data:
                logger.info(f"Loaded AI config from {yaml_path}")
                return TieredAIConfig(**config_data)
        except (yaml.YAMLError, TypeError, ValidationError) as e:
            logger.warning(f"Invalid YAML in {yaml_path}: {e}, using defaults")

    # Return defaults (from .env or built-in)
    logger.info("No AI config found, using defaults (configure at ~/.hestai/config/ai.yaml)")
    return _get_default_tiered_config()


def save_config(config: TieredAIConfig) -> None:
    """Save tiered AI configuration to YAML.

    Args:
        config: TieredAIConfig instance to save
    """
    yaml_path = get_yaml_config_path()
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    config_dict = config.model_dump()
    yaml_content = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
    yaml_path.write_text(yaml_content)
    logger.info(f"Saved AI config to {yaml_path}")


def resolve_api_key(provider: str) -> str | None:
    """Resolve API key for a provider from keyring or environment.

    Resolution order:
    1. Keyring entry (service='hestai-mcp', account='{provider}-key')
    2. Environment variable ({PROVIDER}_API_KEY)

    Args:
        provider: Provider name ('openrouter', 'openai').
            Note: Anthropic models are available via OpenRouter
            (e.g., model='anthropic/claude-3.5-sonnet' with provider='openrouter').

    Returns:
        API key string if found, None otherwise
    """
    # Try keyring first (gracefully handle missing keyring backend in CI)
    try:
        keyring_key = keyring.get_password(KEYRING_SERVICE, f"{provider}-key")
        if keyring_key:
            return str(keyring_key)
    except keyring.errors.NoKeyringError:
        # No keyring backend available (common in CI environments)
        pass

    # Fall back to environment variable
    env_var_name = f"{provider.upper()}_API_KEY"
    return os.environ.get(env_var_name)


async def async_resolve_api_key(provider: str) -> str | None:
    """Resolve API key asynchronously to avoid blocking event loop.

    Wraps keyring access in a separate thread.

    Args:
        provider: Provider name.

    Returns:
        API key string if found, None otherwise
    """
    # Try keyring in a separate thread (blocking I/O)
    try:
        keyring_key = await asyncio.to_thread(
            keyring.get_password, KEYRING_SERVICE, f"{provider}-key"
        )
        if keyring_key:
            return str(keyring_key)
    except keyring.errors.NoKeyringError:
        pass

    # Fall back to environment variable (non-blocking)
    env_var_name = f"{provider.upper()}_API_KEY"
    return os.environ.get(env_var_name)
