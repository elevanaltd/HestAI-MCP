"""AIClient orchestrator with fallback chain.

SS-I2 Compliance: All provider calls, MCP tool invocations, and I/O operations
must be async. No blocking calls in the MCP server event loop.
"""

from types import TracebackType

import httpx
from typing_extensions import Self

from hestai_mcp.ai.config import (
    AITier,
    TieredAIConfig,
    async_resolve_api_key,
    load_config,
)
from hestai_mcp.ai.providers.base import BaseProvider, CompletionRequest
from hestai_mcp.ai.providers.openai_compat import OpenAICompatProvider

# // Critical-Engineer: consulted for async/sync boundary integrity and resource management


# Provider base URLs
PROVIDER_URLS = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}


class AIClient:
    """AI client with tiered model support.

    SS-I2 Compliance: Uses httpx.AsyncClient for all provider calls.
    Supports async context manager for proper connection pooling.

    Orchestrates completion requests using tiered configuration:
    - synthesis: Fast/cheap for routine context generation
    - analysis: Balanced for deeper analysis
    - critical: Best available for important decisions

    Usage:
        async with AIClient() as client:
            result = await client.complete_text(request, tier="synthesis")
    """

    def __init__(self, config: TieredAIConfig | None = None) -> None:
        """Initialize AIClient.

        Args:
            config: TieredAIConfig instance. If None, loads from disk.
        """
        self.config = config if config is not None else load_config()
        self._async_client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        """Enter async context manager, creating shared AsyncClient.

        SS-I2: Connection pooling requires proper async lifecycle.
        """
        self._async_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=self.config.timeouts.connect_seconds,
                read=self.config.timeouts.request_seconds,
                write=self.config.timeouts.request_seconds,
                pool=self.config.timeouts.connect_seconds,
            )
        )
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

    async def complete_text(self, request: CompletionRequest, tier: AITier | None = None) -> str:
        """Execute text completion using specified tier.

        SS-I2 Compliance: Async method using httpx.AsyncClient.

        Args:
            request: CompletionRequest with prompts and parameters
            tier: AI tier to use ('synthesis', 'analysis', 'critical').
                  Uses config default_tier if None.

        Returns:
            Completion text from provider

        Raises:
            ValueError: If no API key available for provider
            RuntimeError: If called outside async context manager
            httpx.HTTPError: If provider request fails
            KeyError: If tier is not configured
        """
        # Ensure we have an async client (must be used within context manager)
        if self._async_client is None:
            raise RuntimeError(
                "AIClient.complete_text must be called within an 'async with' block "
                "to ensure proper connection pooling."
            )

        return await self._complete_text_with_client(request, self._async_client, tier)

    async def _complete_text_with_client(
        self,
        request: CompletionRequest,
        client: httpx.AsyncClient,
        tier: AITier | None = None,
    ) -> str:
        """Internal implementation of complete_text with explicit client.

        Args:
            request: CompletionRequest with prompts and parameters
            client: httpx.AsyncClient to use for requests
            tier: AI tier to use (uses config default if None)

        Returns:
            Completion text from provider
        """
        # Get tier configuration
        tier_config = self.config.get_tier_config(tier)

        # Resolve API key for this provider
        api_key = await async_resolve_api_key(tier_config.provider)
        if not api_key:
            raise ValueError(
                f"No API key available for provider '{tier_config.provider}'. "
                f"Set {tier_config.provider.upper()}_API_KEY environment variable "
                "or configure in keyring."
            )

        try:
            provider = self._get_provider(tier_config.provider)
            # Override model in request with tier-specific model
            tier_request = CompletionRequest(
                system_prompt=request.system_prompt,
                user_prompt=request.user_prompt,
                model=tier_config.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            return await provider.complete_text(tier_request, api_key, client)

        except Exception:
            # For now, no fallback chain - just raise the error
            # Future: could add fallback to other tiers on retryable errors
            raise
