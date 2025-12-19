"""Base provider interface for AI completions."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel


class CompletionRequest(BaseModel):
    """Request parameters for text completion."""

    system_prompt: str
    user_prompt: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout_seconds: int = 30


class ModelInfo(BaseModel):
    """Information about an available model."""

    id: str
    name: str
    description: Optional[str] = None


class BaseProvider(ABC):
    """Abstract base class for AI provider implementations.

    Concrete providers (OpenAI, Anthropic, OpenRouter) must implement:
    - list_models: Return available models for this provider
    - test_connection: Verify API key and connectivity
    - complete_text: Execute a text completion request
    """

    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        """List available models for this provider.

        Returns:
            List of ModelInfo objects describing available models
        """
        pass

    @abstractmethod
    def test_connection(self, model: str, api_key: str) -> Dict[str, object]:
        """Test connectivity and authentication with this provider.

        Args:
            model: Model ID to test with
            api_key: API key for authentication

        Returns:
            Dict with 'success' (bool) and optional 'error' (str) keys
        """
        pass

    @abstractmethod
    def complete_text(self, request: CompletionRequest, api_key: str) -> str:
        """Execute a text completion request.

        Args:
            request: CompletionRequest with prompt and parameters
            api_key: API key for authentication

        Returns:
            Completion text from the model

        Raises:
            Various exceptions for connection errors, auth failures, etc.
        """
        pass
