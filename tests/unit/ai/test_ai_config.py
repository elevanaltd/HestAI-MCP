"""
Tests for AI configuration loading, saving, and secret resolution.

Target coverage: 90%+ for ai/config.py

Test Plan Coverage:
- TieredAIConfig model behavior and tier resolution
- load_config: YAML loading (preferred), defaults from .env/environment
- save_config: YAML saving with directory creation
- resolve_api_key: keyring priority, env fallback, NoKeyringError handling
"""

from pathlib import Path
from unittest.mock import MagicMock

import keyring.errors
import pytest
import yaml
from pydantic import ValidationError

from hestai_mcp.modules.services.ai.config import (
    KEYRING_SERVICE,
    TierConfig,
    TieredAIConfig,
    TimeoutConfig,
    get_yaml_config_path,
    load_config,
    resolve_api_key,
    save_config,
)


@pytest.mark.unit
class TestTieredAIConfigModel:
    """Test TieredAIConfig Pydantic model behavior."""

    def test_tiered_config_default_values(self):
        """TieredAIConfig should have sensible defaults."""
        config = TieredAIConfig()

        assert config.tiers == {}
        assert config.default_tier == "synthesis"
        assert config.timeouts.connect_seconds == 5
        assert config.timeouts.request_seconds == 30

    def test_tiered_config_with_tiers(self):
        """TieredAIConfig should accept tier configuration."""
        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(
                    provider="openrouter",
                    model="google/gemini-flash",
                    description="Fast model",
                ),
                "critical": TierConfig(
                    provider="openai",
                    model="gpt-4o",
                    description="Best model",
                ),
            },
            default_tier="synthesis",
        )

        assert len(config.tiers) == 2
        assert config.tiers["synthesis"].provider == "openrouter"
        assert config.tiers["critical"].model == "gpt-4o"

    def test_get_tier_config_returns_correct_tier(self):
        """get_tier_config should return the requested tier."""
        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(provider="openrouter", model="fast-model"),
                "critical": TierConfig(provider="openai", model="smart-model"),
            },
            default_tier="synthesis",
        )

        synthesis_tier = config.get_tier_config("synthesis")
        critical_tier = config.get_tier_config("critical")

        assert synthesis_tier.model == "fast-model"
        assert critical_tier.model == "smart-model"

    def test_get_tier_config_uses_default_when_none(self):
        """get_tier_config should use default_tier when tier is None."""
        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(provider="openrouter", model="default-model"),
                "critical": TierConfig(provider="openai", model="other-model"),
            },
            default_tier="synthesis",
        )

        result = config.get_tier_config(None)

        assert result.model == "default-model"

    def test_get_tier_config_raises_keyerror_for_missing_tier(self):
        """get_tier_config should raise KeyError for unconfigured tier."""
        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(provider="openrouter", model="model"),
            },
        )

        with pytest.raises(KeyError) as exc_info:
            config.get_tier_config("critical")

        assert "critical" in str(exc_info.value)
        assert "synthesis" in str(exc_info.value)  # Shows available tiers


@pytest.mark.unit
class TestTierConfigModel:
    """Test TierConfig Pydantic model behavior."""

    def test_tier_config_requires_provider_and_model(self):
        """TierConfig should require provider and model fields."""
        with pytest.raises(ValidationError):
            TierConfig()  # type: ignore

    def test_tier_config_description_optional(self):
        """TierConfig description should be optional with empty default."""
        config = TierConfig(provider="openai", model="gpt-4o")

        assert config.description == ""


@pytest.mark.unit
class TestLoadConfigYaml:
    """Test load_config with YAML configuration (preferred path)."""

    def test_load_config_yaml_returns_tiered_config(self, monkeypatch, tmp_path):
        """When YAML config exists, load and parse it as TieredAIConfig."""
        yaml_file = tmp_path / "ai.yaml"
        config_data = {
            "tiers": {
                "synthesis": {
                    "provider": "openrouter",
                    "model": "google/gemini-flash",
                    "description": "Fast model for synthesis",
                },
                "analysis": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "description": "Balanced analysis model",
                },
                "critical": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "description": "Best model for critical decisions",
                },
            },
            "default_tier": "synthesis",
            "timeouts": {"connect_seconds": 10, "request_seconds": 120},
        }
        yaml_file.write_text(yaml.dump(config_data))

        monkeypatch.setattr("hestai_mcp.ai.config.get_yaml_config_path", lambda: yaml_file)

        config = load_config()

        assert isinstance(config, TieredAIConfig)
        assert len(config.tiers) == 3
        assert config.tiers["synthesis"].provider == "openrouter"
        assert config.tiers["critical"].model == "gpt-4o"
        assert config.timeouts.connect_seconds == 10


@pytest.mark.unit
class TestLoadConfigDefaults:
    """Test load_config default behavior when no config files exist."""

    def test_load_config_missing_file_returns_defaults(self, monkeypatch, tmp_path):
        """When no config file exists, return default TieredAIConfig."""
        monkeypatch.setattr(
            "hestai_mcp.ai.config.get_yaml_config_path",
            lambda: tmp_path / "nonexistent.yaml",
        )

        config = load_config()

        assert isinstance(config, TieredAIConfig)
        assert "synthesis" in config.tiers
        assert "analysis" in config.tiers
        assert "critical" in config.tiers
        assert config.tiers["synthesis"].provider == "openrouter"
        assert config.default_tier == "synthesis"

    def test_load_config_env_overrides_defaults(self, monkeypatch, tmp_path):
        """Environment variables should override default values."""
        monkeypatch.setattr(
            "hestai_mcp.ai.config.get_yaml_config_path",
            lambda: tmp_path / "nonexistent.yaml",
        )
        monkeypatch.setenv("HESTAI_AI_PROVIDER", "openai")
        monkeypatch.setenv("HESTAI_AI_MODEL", "gpt-4o-mini")

        config = load_config()

        assert config.tiers["synthesis"].provider == "openai"
        assert config.tiers["synthesis"].model == "gpt-4o-mini"

    def test_load_config_invalid_yaml_uses_defaults(self, monkeypatch, tmp_path):
        """Invalid YAML should fall back to defaults."""
        yaml_file = tmp_path / "ai.yaml"
        yaml_file.write_text("{ invalid: yaml: here }")

        monkeypatch.setattr("hestai_mcp.ai.config.get_yaml_config_path", lambda: yaml_file)

        config = load_config()

        # Should fall back to defaults
        assert isinstance(config, TieredAIConfig)
        assert "synthesis" in config.tiers


@pytest.mark.unit
class TestSaveConfig:
    """Test save_config function."""

    def test_save_config_creates_yaml_file(self, monkeypatch, tmp_path):
        """save_config should create YAML file with config."""
        yaml_file = tmp_path / "nested" / "dirs" / "ai.yaml"
        monkeypatch.setattr("hestai_mcp.ai.config.get_yaml_config_path", lambda: yaml_file)

        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(
                    provider="openrouter",
                    model="test-model",
                    description="Test tier",
                ),
            },
            default_tier="synthesis",
        )

        save_config(config)

        assert yaml_file.exists()
        saved_data = yaml.safe_load(yaml_file.read_text())
        assert saved_data["tiers"]["synthesis"]["provider"] == "openrouter"
        assert saved_data["tiers"]["synthesis"]["model"] == "test-model"
        assert saved_data["default_tier"] == "synthesis"

    def test_save_config_overwrites_existing(self, monkeypatch, tmp_path):
        """save_config should overwrite existing file."""
        yaml_file = tmp_path / "ai.yaml"
        yaml_file.write_text("old: data")
        monkeypatch.setattr("hestai_mcp.ai.config.get_yaml_config_path", lambda: yaml_file)

        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(provider="new-provider", model="new-model"),
            },
        )

        save_config(config)

        saved_data = yaml.safe_load(yaml_file.read_text())
        assert saved_data["tiers"]["synthesis"]["provider"] == "new-provider"
        assert "old" not in saved_data


@pytest.mark.unit
class TestResolveApiKey:
    """Test resolve_api_key function."""

    def test_resolve_key_keyring_success(self, monkeypatch):
        """When keyring returns a key, use it (not env)."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key-should-not-be-used")
        mock_get_password = MagicMock(return_value="keyring-secret-key")
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        result = resolve_api_key("openai")

        assert result == "keyring-secret-key"
        mock_get_password.assert_called_once_with(KEYRING_SERVICE, "openai-key")

    def test_resolve_key_keyring_empty_falls_back_to_env(self, monkeypatch):
        """When keyring returns None/empty, fall back to environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-fallback-key")
        mock_get_password = MagicMock(return_value=None)
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        result = resolve_api_key("openai")

        assert result == "env-fallback-key"

    def test_resolve_key_no_keyring_falls_back_to_env(self, monkeypatch):
        """When keyring.get_password raises NoKeyringError, fall back to env."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "env-api-key-12345")
        mock_get_password = MagicMock(side_effect=keyring.errors.NoKeyringError())
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        result = resolve_api_key("openrouter")

        assert result == "env-api-key-12345"
        mock_get_password.assert_called_once_with(KEYRING_SERVICE, "openrouter-key")

    def test_resolve_key_no_keyring_no_env_returns_none(self, monkeypatch):
        """When keyring fails and no env var, return None."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        mock_get_password = MagicMock(side_effect=keyring.errors.NoKeyringError())
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        result = resolve_api_key("openrouter")

        assert result is None


@pytest.mark.asyncio
class TestAsyncResolveApiKey:
    """Test async_resolve_api_key function."""

    async def test_async_resolve_key_keyring_success(self, monkeypatch):
        """When keyring returns a key, use it (not env) asynchronously."""
        from hestai_mcp.modules.services.ai.config import async_resolve_api_key

        monkeypatch.setenv("OPENAI_API_KEY", "env-key-should-not-be-used")
        mock_get_password = MagicMock(return_value="keyring-secret-key")
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        result = await async_resolve_api_key("openai")

        assert result == "keyring-secret-key"
        # Verify it was called
        mock_get_password.assert_called_once_with(KEYRING_SERVICE, "openai-key")

    async def test_async_resolve_key_fallback_to_env(self, monkeypatch):
        """When keyring fails, fallback to env asynchronously."""
        from hestai_mcp.modules.services.ai.config import async_resolve_api_key

        monkeypatch.setenv("OPENAI_API_KEY", "env-fallback-key")
        mock_get_password = MagicMock(side_effect=keyring.errors.NoKeyringError())
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        result = await async_resolve_api_key("openai")

        assert result == "env-fallback-key"


@pytest.mark.unit
class TestConfigPathHelpers:
    """Test config path helper functions."""

    def test_get_yaml_config_path_returns_home_based_path(self):
        """YAML config path should be under ~/.hestai/config/."""
        path = get_yaml_config_path()

        assert isinstance(path, Path)
        assert path.name == "ai.yaml"
        assert ".hestai" in str(path)
        assert "config" in str(path)


@pytest.mark.unit
class TestTimeoutConfig:
    """Test TimeoutConfig model behavior."""

    def test_timeout_config_default_values(self):
        """TimeoutConfig should have sensible defaults."""
        config = TimeoutConfig()

        assert config.connect_seconds == 5
        assert config.request_seconds == 30

    def test_timeout_config_custom_values(self):
        """TimeoutConfig should accept custom values."""
        config = TimeoutConfig(connect_seconds=10, request_seconds=120)

        assert config.connect_seconds == 10
        assert config.request_seconds == 120


@pytest.mark.unit
class TestOperationTierMapping:
    """Test operation-to-tier mapping in TieredAIConfig."""

    def test_get_operation_tier_returns_configured_tier(self):
        """When operation is configured, return its tier."""
        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(provider="x", model="y"),
                "analysis": TierConfig(provider="x", model="z"),
            },
            operations={"clock_in_synthesis": "analysis"},  # Configured to use analysis
        )

        result = config.get_operation_tier("clock_in_synthesis")

        assert result == "analysis"

    def test_get_operation_tier_falls_back_to_default(self):
        """When operation not configured, return default_tier."""
        config = TieredAIConfig(
            tiers={"synthesis": TierConfig(provider="x", model="y")},
            operations={},  # No operations configured
            default_tier="synthesis",
        )

        result = config.get_operation_tier("unknown_operation")

        assert result == "synthesis"

    def test_operations_field_defaults_to_empty(self):
        """Operations field should default to empty dict."""
        config = TieredAIConfig()

        assert config.operations == {}

    def test_get_operation_tier_with_all_standard_operations(self):
        """Test all standard operations return expected tiers."""
        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(provider="x", model="fast"),
                "analysis": TierConfig(provider="x", model="balanced"),
                "critical": TierConfig(provider="x", model="best"),
            },
            operations={
                "clock_in_synthesis": "synthesis",
                "context_update": "synthesis",
                "document_analysis": "analysis",
            },
            default_tier="synthesis",
        )

        assert config.get_operation_tier("clock_in_synthesis") == "synthesis"
        assert config.get_operation_tier("context_update") == "synthesis"
        assert config.get_operation_tier("document_analysis") == "analysis"
        # Unmapped operations fall back to default
        assert config.get_operation_tier("unknown") == "synthesis"


@pytest.mark.unit
class TestTierReferenceValidation:
    """Test model_validator for tier reference validation."""

    def test_invalid_default_tier_raises_validation_error(self):
        """When default_tier references a non-existent tier, raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            TieredAIConfig(
                tiers={
                    "synthesis": TierConfig(provider="x", model="y"),
                },
                default_tier="analysis",  # Does not exist in tiers
            )

        error_message = str(exc_info.value)
        assert "default_tier" in error_message
        assert "analysis" in error_message
        assert "synthesis" in error_message

    def test_operation_mapping_to_nonexistent_tier_raises_validation_error(self):
        """When operation maps to non-existent tier, raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            TieredAIConfig(
                tiers={
                    "synthesis": TierConfig(provider="x", model="y"),
                },
                operations={
                    "clock_in": "analysis",  # Maps to non-existent tier
                },
                default_tier="synthesis",
            )

        error_message = str(exc_info.value)
        assert "clock_in" in error_message
        assert "analysis" in error_message

    def test_empty_tiers_skips_validation(self):
        """Empty tiers dict should not trigger validation errors."""
        # Should not raise - empty config is valid
        config = TieredAIConfig(
            tiers={},
            default_tier="synthesis",  # Would be invalid if tiers were non-empty
        )

        assert config.default_tier == "synthesis"

    def test_valid_tier_references_passes_validation(self):
        """Valid tier references should pass validation."""
        # Should not raise
        config = TieredAIConfig(
            tiers={
                "synthesis": TierConfig(provider="x", model="fast"),
                "analysis": TierConfig(provider="x", model="balanced"),
                "critical": TierConfig(provider="x", model="best"),
            },
            operations={
                "clock_in": "synthesis",
                "deep_analysis": "analysis",
                "important_decision": "critical",
            },
            default_tier="synthesis",
        )

        assert len(config.tiers) == 3
        assert len(config.operations) == 3


@pytest.mark.unit
class TestValidationErrorFallback:
    """Test that ValidationError in YAML falls back to defaults."""

    def test_yaml_with_invalid_tier_reference_uses_defaults(self, monkeypatch, tmp_path):
        """YAML with invalid tier reference should fall back to defaults."""
        yaml_file = tmp_path / "ai.yaml"
        # This YAML has valid syntax but invalid tier reference
        invalid_yaml_config = {
            "tiers": {
                "synthesis": {"provider": "openrouter", "model": "fast"},
            },
            "default_tier": "nonexistent",  # Invalid - doesn't exist in tiers
        }
        yaml_file.write_text(yaml.dump(invalid_yaml_config))

        monkeypatch.setattr("hestai_mcp.ai.config.get_yaml_config_path", lambda: yaml_file)

        config = load_config()

        # Should have loaded defaults
        assert isinstance(config, TieredAIConfig)
        assert "synthesis" in config.tiers
        assert "analysis" in config.tiers
        assert "critical" in config.tiers

    def test_yaml_with_invalid_operation_mapping_uses_defaults(self, monkeypatch, tmp_path):
        """YAML with invalid operation tier mapping should fall back to defaults."""
        yaml_file = tmp_path / "ai.yaml"
        invalid_yaml_config = {
            "tiers": {
                "synthesis": {"provider": "openrouter", "model": "fast"},
            },
            "operations": {
                "clock_in": "analysis",  # Invalid - analysis not in tiers
            },
            "default_tier": "synthesis",
        }
        yaml_file.write_text(yaml.dump(invalid_yaml_config))

        monkeypatch.setattr("hestai_mcp.ai.config.get_yaml_config_path", lambda: yaml_file)

        config = load_config()

        # Should have loaded defaults
        assert isinstance(config, TieredAIConfig)
        assert "synthesis" in config.tiers
        assert "analysis" in config.tiers
        assert "critical" in config.tiers
