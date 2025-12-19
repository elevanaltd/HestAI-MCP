"""AI configuration loading, saving, and secret resolution."""

import json
import os
from pathlib import Path

import keyring
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Provider and model configuration."""

    provider: str
    model: str


class TimeoutConfig(BaseModel):
    """Network timeout configuration."""

    connect_seconds: int = 5
    request_seconds: int = 30


class AIConfig(BaseModel):
    """AI client configuration with primary and fallback providers."""

    primary: ProviderConfig
    fallback: list[ProviderConfig] = Field(default_factory=list)
    timeouts: TimeoutConfig = Field(default_factory=TimeoutConfig)


def get_config_path() -> Path:
    """Get the path to the AI config file.

    Returns:
        Path to ~/.hestai/config/ai.json
    """
    return Path.home() / ".hestai" / "config" / "ai.json"


def load_config() -> AIConfig:
    """Load AI configuration from disk.

    Returns:
        AIConfig instance, either from file or with default values

    Raises:
        ValueError: If config file exists but contains invalid JSON
    """
    config_path = get_config_path()

    if not config_path.exists():
        # Return default config
        return AIConfig(
            primary=ProviderConfig(
                provider="openrouter", model="anthropic/claude-3.5-sonnet"
            ),  # ggignore
            fallback=[],
            timeouts=TimeoutConfig(),
        )

    try:
        config_data = json.loads(config_path.read_text())
        return AIConfig(**config_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {config_path}: {e}") from e


def save_config(config: AIConfig) -> None:
    """Save AI configuration to disk.

    Args:
        config: AIConfig instance to save

    Creates parent directories if they don't exist.
    """
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config_dict = config.model_dump()
    config_path.write_text(json.dumps(config_dict, indent=2))


def resolve_api_key(provider: str) -> str | None:
    """Resolve API key for a provider from keyring or environment.

    Resolution order:
    1. Keyring entry (service='hestai-core', account='{provider}-key')
    2. Environment variable ({PROVIDER}_API_KEY)

    Args:
        provider: Provider name ('openrouter', 'openai', 'anthropic')

    Returns:
        API key string if found, None otherwise
    """
    # Try keyring first
    keyring_key = keyring.get_password("hestai-core", f"{provider}-key")
    if keyring_key:
        return str(keyring_key)

    # Fall back to environment variable
    env_var_name = f"{provider.upper()}_API_KEY"
    return os.environ.get(env_var_name)
