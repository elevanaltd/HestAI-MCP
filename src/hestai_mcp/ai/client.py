"""AIClient orchestrator with fallback chain.

SS-I2 Compliance: All provider calls, MCP tool invocations, and I/O operations
must be async. No blocking calls in the MCP server event loop.
"""

from types import TracebackType

import httpx
from typing_extensions import Self

from hestai_mcp.ai.config import AIConfig, load_config, resolve_api_key
from hestai_mcp.ai.providers.base import BaseProvider, CompletionRequest
from hestai_mcp.ai.providers.openai_compat import OpenAICompatProvider

# Provider base URLs
PROVIDER_URLS = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}


class AIClient:
    """AI client with provider fallback chain.

    SS-I2 Compliance: Uses httpx.AsyncClient for all provider calls.
    Supports async context manager for proper connection pooling.

    Orchestrates completion requests across configured providers,
    with automatic fallback on retryable errors (timeouts, 5xx).
    Does NOT fallback on auth/validation errors (4xx).

    Usage:
        async with AIClient() as client:
            result = await client.complete_text(request)
    """

    def __init__(self, config: AIConfig | None = None) -> None:
        """Initialize AIClient.

        Args:
            config: AIConfig instance. If None, loads from disk.
        """
        self.config = config if config is not None else load_config()
        self._async_client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        """Enter async context manager, creating shared AsyncClient.

        SS-I2: Connection pooling requires proper async lifecycle.
        """
        self._async_client = httpx.AsyncClient()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager, closing AsyncClient."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def _get_provider(self, provider_name: str) -> BaseProvider:
        """Get provider instance for a given provider name.

        Args:
            provider_name: Name of provider ('openai', 'openrouter')

        Returns:
            BaseProvider instance

        Raises:
            ValueError: If provider is not supported
        """
        if provider_name not in PROVIDER_URLS:
            raise ValueError(f"Unsupported provider: {provider_name}")

        base_url = PROVIDER_URLS[provider_name]
        return OpenAICompatProvider(provider_name=provider_name, base_url=base_url)

    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error should trigger fallback.

        Args:
            error: Exception raised during completion

        Returns:
            True if error is retryable (timeout, 5xx), False otherwise
        """
        # Timeout errors are retryable
        if isinstance(error, (httpx.TimeoutException, httpx.ConnectError)):
            return True

        # HTTP 5xx errors are retryable
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code >= 500

        # All other errors (4xx auth, validation, etc.) are NOT retryable
        return False

    async def complete_text(self, request: CompletionRequest) -> str:
        """Execute text completion with fallback chain.

        SS-I2 Compliance: Async method using httpx.AsyncClient.

        Tries primary provider first. On retryable errors (timeout, 5xx),
        falls back to configured fallback providers in order.

        Args:
            request: CompletionRequest with prompts and parameters

        Returns:
            Completion text from successful provider

        Raises:
            ValueError: If no API key available for any provider
            RuntimeError: If called outside async context manager
            httpx.HTTPError: If all providers fail or non-retryable error
        """
        # Ensure we have an async client (either from context manager or create one)
        if self._async_client is None:
            # Create a temporary client for this request
            async with httpx.AsyncClient() as temp_client:
                return await self._complete_text_with_client(request, temp_client)
        else:
            return await self._complete_text_with_client(request, self._async_client)

    async def _complete_text_with_client(
        self, request: CompletionRequest, client: httpx.AsyncClient
    ) -> str:
        """Internal implementation of complete_text with explicit client.

        Args:
            request: CompletionRequest with prompts and parameters
            client: httpx.AsyncClient to use for requests

        Returns:
            Completion text from successful provider
        """
        # Build provider chain: primary + fallbacks
        provider_configs = [self.config.primary] + self.config.fallback

        last_error: Exception | None = None

        for provider_config in provider_configs:
            # Resolve API key for this provider
            api_key = resolve_api_key(provider_config.provider)
            if not api_key:
                # Skip providers without keys (but continue trying others)
                continue

            try:
                provider = self._get_provider(provider_config.provider)
                return await provider.complete_text(request, api_key, client)

            except Exception as e:
                last_error = e

                # If error is not retryable, fail immediately (don't try fallbacks)
                if not self._is_retryable_error(e):
                    raise

                # Otherwise, continue to next provider in chain
                continue

        # If we get here, all providers failed or no API keys available
        if last_error:
            raise last_error
        else:
            raise ValueError("No API key available for any configured provider")
