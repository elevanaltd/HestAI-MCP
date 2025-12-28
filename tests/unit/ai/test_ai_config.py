"""
Tests for AI configuration loading, saving, and secret resolution.

Target coverage: 90%+ for ai/config.py

TMG Test Plan Coverage:
- test_load_config_missing_file: config.py:67-71 (default config on missing file)
- test_load_config_invalid_json: config.py:82-86 (ValueError on bad JSON)
- test_resolve_key_no_keyring: config.py:106-109 (NoKeyringError fallback to env)
"""

import json
from pathlib import Path
from unittest.mock import MagicMock

import keyring.errors
import pytest
from pydantic import ValidationError

from hestai_mcp.ai.config import (
    KEYRING_SERVICE,
    AIConfig,
    ProviderConfig,
    TimeoutConfig,
    get_config_path,
    load_config,
    resolve_api_key,
    save_config,
)


@pytest.mark.unit
class TestLoadConfigMissingFile:
    """Test config.py:67-71 - default config when file doesn't exist."""

    def test_load_config_missing_file_returns_default(self, monkeypatch, tmp_path):
        """When config file doesn't exist, return default AIConfig with openrouter primary.

        Target: config.py:57-65
        """
        # Point config path to a non-existent file
        non_existent = tmp_path / "does_not_exist" / "ai.json"
        monkeypatch.setattr("hestai_mcp.ai.config.get_config_path", lambda: non_existent)

        # Act
        config = load_config()

        # Assert - should return default config
        assert isinstance(config, AIConfig)
        assert config.primary.provider == "openrouter"
        assert config.primary.model == "anthropic/claude-3.5-sonnet"
        assert config.fallback == []
        assert isinstance(config.timeouts, TimeoutConfig)
        assert config.timeouts.connect_seconds == 5
        assert config.timeouts.request_seconds == 30

    def test_load_config_existing_file_loads_content(self, monkeypatch, tmp_path):
        """When config file exists with valid JSON, load and parse it.

        Target: config.py:67-69
        """
        # Create a valid config file
        config_file = tmp_path / "ai.json"
        config_data = {
            "primary": {"provider": "openai", "model": "gpt-4o"},
            "fallback": [{"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"}],
            "timeouts": {"connect_seconds": 10, "request_seconds": 60},
        }
        config_file.write_text(json.dumps(config_data))

        monkeypatch.setattr("hestai_mcp.ai.config.get_config_path", lambda: config_file)

        # Act
        config = load_config()

        # Assert - should load from file
        assert config.primary.provider == "openai"
        assert config.primary.model == "gpt-4o"
        assert len(config.fallback) == 1
        assert config.fallback[0].provider == "openrouter"
        assert config.timeouts.connect_seconds == 10
        assert config.timeouts.request_seconds == 60


@pytest.mark.unit
class TestLoadConfigInvalidJson:
    """Test config.py:70-71 - ValueError on invalid JSON."""

    def test_load_config_invalid_json_raises_valueerror(self, monkeypatch, tmp_path):
        """When config file contains invalid JSON, raise ValueError with clear message.

        Target: config.py:70-71
        """
        # Create a config file with invalid JSON
        config_file = tmp_path / "ai.json"
        config_file.write_text("{ invalid json here }")

        monkeypatch.setattr("hestai_mcp.ai.config.get_config_path", lambda: config_file)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            load_config()

        # Verify error message contains useful info
        assert "Invalid JSON" in str(exc_info.value)
        assert str(config_file) in str(exc_info.value)

    def test_load_config_truncated_json_raises_valueerror(self, monkeypatch, tmp_path):
        """Truncated JSON should also raise ValueError."""
        config_file = tmp_path / "ai.json"
        config_file.write_text('{"primary": {"provider": "openai"')  # Missing closing braces

        monkeypatch.setattr("hestai_mcp.ai.config.get_config_path", lambda: config_file)

        with pytest.raises(ValueError) as exc_info:
            load_config()

        assert "Invalid JSON" in str(exc_info.value)

    def test_load_config_empty_file_raises_valueerror(self, monkeypatch, tmp_path):
        """Empty file should raise ValueError (not valid JSON)."""
        config_file = tmp_path / "ai.json"
        config_file.write_text("")

        monkeypatch.setattr("hestai_mcp.ai.config.get_config_path", lambda: config_file)

        with pytest.raises(ValueError) as exc_info:
            load_config()

        assert "Invalid JSON" in str(exc_info.value)


@pytest.mark.unit
class TestResolveApiKeyNoKeyring:
    """Test config.py:106-109 - NoKeyringError fallback to environment."""

    def test_resolve_key_no_keyring_falls_back_to_env(self, monkeypatch):
        """When keyring.get_password raises NoKeyringError, fall back to os.environ.

        Target: config.py:107-109
        """
        # Set environment variable
        monkeypatch.setenv("OPENAI_API_KEY", "env-api-key-12345")

        # Mock keyring to raise NoKeyringError
        mock_get_password = MagicMock(side_effect=keyring.errors.NoKeyringError())
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        # Act
        result = resolve_api_key("openai")

        # Assert - should get key from environment
        assert result == "env-api-key-12345"

        # Verify keyring was attempted first
        mock_get_password.assert_called_once_with(KEYRING_SERVICE, "openai-key")

    def test_resolve_key_no_keyring_no_env_returns_none(self, monkeypatch):
        """When keyring fails and no env var, return None."""
        # Ensure env var is not set
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        # Mock keyring to raise NoKeyringError
        mock_get_password = MagicMock(side_effect=keyring.errors.NoKeyringError())
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        # Act
        result = resolve_api_key("openrouter")

        # Assert
        assert result is None

    def test_resolve_key_keyring_success_returns_key(self, monkeypatch):
        """When keyring succeeds, return keyring value (not env)."""
        # Set both keyring and env
        monkeypatch.setenv("OPENAI_API_KEY", "env-key-should-not-be-used")

        mock_get_password = MagicMock(return_value="keyring-secret-key")
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        # Act
        result = resolve_api_key("openai")

        # Assert - should prefer keyring
        assert result == "keyring-secret-key"

    def test_resolve_key_keyring_empty_falls_back_to_env(self, monkeypatch):
        """When keyring returns empty/None, fall back to environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-fallback-key")

        mock_get_password = MagicMock(return_value=None)
        monkeypatch.setattr("keyring.get_password", mock_get_password)

        # Act
        result = resolve_api_key("openai")

        # Assert - should fall back to env
        assert result == "env-fallback-key"


@pytest.mark.unit
class TestSaveConfig:
    """Test save_config function."""

    def test_save_config_creates_parent_directories(self, monkeypatch, tmp_path):
        """save_config should create parent directories if needed."""
        config_file = tmp_path / "nested" / "dirs" / "ai.json"
        monkeypatch.setattr("hestai_mcp.ai.config.get_config_path", lambda: config_file)

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[],
        )

        # Act
        save_config(config)

        # Assert - file should exist with correct content
        assert config_file.exists()
        saved_data = json.loads(config_file.read_text())
        assert saved_data["primary"]["provider"] == "openai"
        assert saved_data["primary"]["model"] == "gpt-4o"

    def test_save_config_overwrites_existing(self, monkeypatch, tmp_path):
        """save_config should overwrite existing file."""
        config_file = tmp_path / "ai.json"
        config_file.write_text('{"old": "data"}')
        monkeypatch.setattr("hestai_mcp.ai.config.get_config_path", lambda: config_file)

        config = AIConfig(
            primary=ProviderConfig(provider="openrouter", model="new-model"),
            fallback=[],
        )

        # Act
        save_config(config)

        # Assert
        saved_data = json.loads(config_file.read_text())
        assert saved_data["primary"]["model"] == "new-model"
        assert "old" not in saved_data


@pytest.mark.unit
class TestGetConfigPath:
    """Test get_config_path function."""

    def test_get_config_path_returns_home_based_path(self):
        """Config path should be under ~/.hestai/config/."""
        path = get_config_path()

        assert isinstance(path, Path)
        assert path.name == "ai.json"
        assert "hestai" in str(path).lower()
        assert "config" in str(path).lower()


@pytest.mark.unit
class TestPydanticModels:
    """Test Pydantic model behavior."""

    def test_aiconfig_default_timeouts(self):
        """AIConfig should have default timeouts."""
        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
        )

        assert config.timeouts.connect_seconds == 5
        assert config.timeouts.request_seconds == 30

    def test_aiconfig_default_fallback(self):
        """AIConfig should default to empty fallback list."""
        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
        )

        assert config.fallback == []

    def test_provider_config_requires_fields(self):
        """ProviderConfig should require provider and model."""
        with pytest.raises(ValidationError):
            ProviderConfig()  # type: ignore
