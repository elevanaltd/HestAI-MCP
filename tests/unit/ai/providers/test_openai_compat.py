"""
Tests for OpenAI-compatible provider implementation.

TDD Discipline:
1. RED: Write failing tests first
2. GREEN: Minimal implementation to pass
3. REFACTOR: Improve while tests pass

Coverage Targets:
- list_models: 90% (openai and openrouter paths)
- test_connection: 90%
- complete_text: 80%
- _fetch_openrouter_models: 90%
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from hestai_mcp.ai.providers.base import CompletionRequest, ModelInfo
from hestai_mcp.ai.providers.openai_compat import (
    OPENAI_CURATED_MODELS,
    OpenAICompatProvider,
)

# =============================================================================
# PHASE 3: list_models tests
# =============================================================================


@pytest.mark.unit
class TestListModelsOpenRouter:
    """Test model listing for OpenRouter provider."""

    @pytest.mark.asyncio
    async def test_fetches_models_from_openrouter_api(self):
        """Fetches live model list from OpenRouter /models endpoint."""
        provider = OpenAICompatProvider("openrouter", "https://openrouter.ai/api/v1")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": "openai/gpt-4", "name": "GPT-4", "description": "OpenAI GPT-4"},
                {"id": "anthropic/claude-3", "name": "Claude 3", "description": "Anthropic Claude"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            models = await provider.list_models()

        assert len(models) == 2
        assert models[0].id == "openai/gpt-4"
        assert models[0].name == "GPT-4"
        assert models[1].id == "anthropic/claude-3"

    @pytest.mark.asyncio
    async def test_returns_empty_list_on_api_failure(self):
        """Returns empty list when OpenRouter API fails (don't crash listing)."""
        provider = OpenAICompatProvider("openrouter", "https://openrouter.ai/api/v1")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            models = await provider.list_models()

        assert models == []

    @pytest.mark.asyncio
    async def test_handles_missing_model_fields_gracefully(self):
        """Handles models with missing optional fields."""
        provider = OpenAICompatProvider("openrouter", "https://openrouter.ai/api/v1")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": "model-1"},  # Missing name and description
                {"id": "model-2", "name": "Model Two"},  # Missing description
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            models = await provider.list_models()

        assert len(models) == 2
        assert models[0].id == "model-1"
        assert models[0].name == "model-1"  # Falls back to id
        assert models[1].name == "Model Two"


@pytest.mark.unit
class TestListModelsOpenAI:
    """Test model listing for OpenAI provider."""

    @pytest.mark.asyncio
    async def test_returns_curated_model_list(self):
        """Returns static curated model list (API requires auth)."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        models = await provider.list_models()

        assert models == OPENAI_CURATED_MODELS
        assert len(models) == 4  # gpt-4o, gpt-4, gpt-4-turbo, gpt-3.5-turbo

    @pytest.mark.asyncio
    async def test_curated_models_have_required_fields(self):
        """Verifies curated models have all required fields."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        models = await provider.list_models()

        for model in models:
            assert model.id is not None
            assert model.name is not None
            assert isinstance(model, ModelInfo)


@pytest.mark.unit
class TestListModelsUnknownProvider:
    """Test model listing for unknown providers."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_unknown_provider(self):
        """Returns empty list for unknown provider type."""
        provider = OpenAICompatProvider("unknown_provider", "https://example.com/api")

        models = await provider.list_models()

        assert models == []


# =============================================================================
# PHASE 3: test_connection tests
# =============================================================================


@pytest.mark.unit
class TestConnectionHandling:
    """Test connection verification and error handling."""

    @pytest.mark.asyncio
    async def test_returns_success_on_200_response(self):
        """Returns success=True when API responds with 200."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Hello"}}]}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await provider.test_connection("gpt-4o", "sk-test-key")

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_returns_failure_on_401_unauthorized(self):
        """Returns success=False with error message on 401."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await provider.test_connection("gpt-4o", "invalid-key")

        assert result["success"] is False
        assert "Invalid API key" in result["error"]

    @pytest.mark.asyncio
    async def test_returns_failure_on_500_server_error(self):
        """Returns success=False with HTTP status on 500."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": {}}  # No message field

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await provider.test_connection("gpt-4o", "sk-test-key")

        assert result["success"] is False
        assert "HTTP 500" in result["error"]

    @pytest.mark.asyncio
    async def test_returns_failure_on_connection_error(self):
        """Returns success=False with error message on connection failure."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await provider.test_connection("gpt-4o", "sk-test-key")

        assert result["success"] is False
        assert "Connection refused" in result["error"]

    @pytest.mark.asyncio
    async def test_sends_correct_auth_header(self):
        """Sends Bearer token in Authorization header."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Hi"}}]}

        captured_kwargs = {}

        async def capture_post(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return mock_response

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=capture_post)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            await provider.test_connection("gpt-4o", "sk-secret-key")

        assert "headers" in captured_kwargs
        assert captured_kwargs["headers"]["Authorization"] == "Bearer sk-secret-key"


# =============================================================================
# PHASE 3: complete_text tests
# =============================================================================


@pytest.mark.unit
class TestCompleteText:
    """Test text completion execution."""

    @pytest.mark.asyncio
    async def test_returns_completion_content(self):
        """Returns content from successful completion."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Completed text response"}}]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        request = CompletionRequest(
            system_prompt="You are helpful",
            user_prompt="Hello",
            max_tokens=100,
            temperature=0.7,
        )

        result = await provider.complete_text(request, "sk-test-key", mock_client)

        assert result == "Completed text response"

    @pytest.mark.asyncio
    async def test_sends_correct_payload(self):
        """Sends correct chat completion payload."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Response"}}]}
        mock_response.raise_for_status = MagicMock()

        captured_json = {}

        async def capture_post(*args, **kwargs):
            captured_json.update(kwargs.get("json", {}))
            return mock_response

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=capture_post)

        request = CompletionRequest(
            system_prompt="System prompt",
            user_prompt="User prompt",
            max_tokens=500,
            temperature=0.5,
        )

        await provider.complete_text(request, "sk-test-key", mock_client)

        assert "messages" in captured_json
        assert len(captured_json["messages"]) == 2
        assert captured_json["messages"][0]["role"] == "system"
        assert captured_json["messages"][0]["content"] == "System prompt"
        assert captured_json["messages"][1]["role"] == "user"
        assert captured_json["messages"][1]["content"] == "User prompt"
        assert captured_json["max_tokens"] == 500
        assert captured_json["temperature"] == 0.5

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self):
        """Raises httpx.HTTPStatusError on non-200 response."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Server error", request=MagicMock(), response=MagicMock()
            )
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        request = CompletionRequest(
            system_prompt="Test",
            user_prompt="Test",
        )

        with pytest.raises(httpx.HTTPStatusError):
            await provider.complete_text(request, "sk-test-key", mock_client)


# =============================================================================
# PHASE 3: Provider initialization tests
# =============================================================================


@pytest.mark.unit
class TestProviderInitialization:
    """Test provider initialization and configuration."""

    def test_stores_provider_name(self):
        """Stores provider name correctly."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")
        assert provider.provider_name == "openai"

    def test_stores_base_url_and_strips_trailing_slash(self):
        """Stores base URL and removes trailing slash."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1/")
        assert provider.base_url == "https://api.openai.com/v1"

    def test_handles_base_url_without_trailing_slash(self):
        """Handles base URL that doesn't have trailing slash."""
        provider = OpenAICompatProvider("openai", "https://api.openai.com/v1")
        assert provider.base_url == "https://api.openai.com/v1"
