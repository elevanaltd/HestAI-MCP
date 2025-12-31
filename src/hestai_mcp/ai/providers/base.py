"""Base provider interface for AI completions.

SS-I2 Compliance: All provider calls must be async.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    import httpx


class CompletionRequest(BaseModel):
    """Request parameters for text completion."""

    system_prompt: str
    user_prompt: str
    model: str = "gpt-4o"  # Default model, should be overridden by tier config
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout_seconds: int = 30


class ModelInfo(BaseModel):
    """Information about an available model."""

    id: str
    name: str
    description: str | None = None


class BaseProvider(ABC):
    """Abstract base class for AI provider implementations.

    SS-I2 Compliance: All methods that make network calls are async.

    Concrete providers (OpenAI, Anthropic, OpenRouter) must implement:
    - list_models: Return available models for this provider (async)
    - test_connection: Verify API key and connectivity (async)
    - complete_text: Execute a text completion request (async)
    """

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """List available models for this provider.

        Returns:
            List of ModelInfo objects describing available models
        """
        pass

    @abstractmethod
    async def test_connection(self, model: str, api_key: str) -> dict[str, object]:
        """Test connectivity and authentication with this provider.

        Args:
            model: Model ID to test with
            api_key: API key for authentication

        Returns:
            Dict with 'success' (bool) and optional 'error' (str) keys
        """
        pass

    @abstractmethod
    async def complete_text(
        self, request: CompletionRequest, api_key: str, client: "httpx.AsyncClient"
    ) -> str:
        """Execute a text completion request.

        SS-I2: Async-first - accepts shared AsyncClient for connection pooling.

        Args:
            request: CompletionRequest with prompt and parameters
            api_key: API key for authentication
            client: Shared httpx.AsyncClient for connection pooling

        Returns:
            Completion text from the model

        Raises:
            Various exceptions for connection errors, auth failures, etc.
        """
        pass
