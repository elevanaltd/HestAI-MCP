"""OpenAI-compatible provider implementation (OpenAI + OpenRouter)."""

from typing import Dict, List

import httpx

from hestai_mcp.ai.providers.base import BaseProvider, CompletionRequest, ModelInfo


# Curated model lists for providers that require authentication to list
OPENAI_CURATED_MODELS = [
    ModelInfo(id="gpt-4o", name="GPT-4 Optimized", description="Latest GPT-4 model"),
    ModelInfo(id="gpt-4", name="GPT-4", description="GPT-4 base model"),
    ModelInfo(id="gpt-4-turbo", name="GPT-4 Turbo", description="Faster GPT-4 variant"),
    ModelInfo(id="gpt-3.5-turbo", name="GPT-3.5 Turbo", description="Fast and affordable"),
]


class OpenAICompatProvider(BaseProvider):
    """Provider for OpenAI-compatible APIs (OpenAI, OpenRouter).

    Uses OpenAI's chat completions format:
    POST /chat/completions
    {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ],
        "max_tokens": 4096,
        "temperature": 0.7
    }
    """

    def __init__(self, provider_name: str, base_url: str) -> None:
        """Initialize provider.

        Args:
            provider_name: Name of provider ('openai', 'openrouter')
            base_url: Base URL for API (e.g., 'https://api.openai.com/v1')
        """
        self.provider_name = provider_name
        self.base_url = base_url.rstrip("/")

    def list_models(self) -> List[ModelInfo]:
        """List available models.

        OpenRouter: Fetch live from /models endpoint
        OpenAI: Return curated list (API requires auth)

        Returns:
            List of ModelInfo objects
        """
        if self.provider_name == "openrouter":
            return self._fetch_openrouter_models()
        elif self.provider_name == "openai":
            return OPENAI_CURATED_MODELS
        else:
            return []

    def _fetch_openrouter_models(self) -> List[ModelInfo]:
        """Fetch models from OpenRouter API.

        Returns:
            List of ModelInfo from OpenRouter's /models endpoint
        """
        try:
            response = httpx.get(f"{self.base_url}/models", timeout=10.0)
            response.raise_for_status()
            data = response.json()

            models = []
            for model_data in data.get("data", []):
                models.append(
                    ModelInfo(
                        id=model_data["id"],
                        name=model_data.get("name", model_data["id"]),
                        description=model_data.get("description"),
                    )
                )
            return models
        except Exception:
            # Return empty list on failure (don't crash listing)
            return []

    def test_connection(self, model: str, api_key: str) -> Dict[str, object]:
        """Test connection to provider.

        Args:
            model: Model ID to test with
            api_key: API key for authentication

        Returns:
            Dict with 'success' (bool) and optional 'error' (str)
        """
        try:
            # Make minimal completion request to verify connectivity
            test_request = CompletionRequest(
                system_prompt="Test",
                user_prompt="Hi",
                max_tokens=10,
            )

            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": test_request.system_prompt},
                        {"role": "user", "content": test_request.user_prompt},
                    ],
                    "max_tokens": test_request.max_tokens,
                },
                timeout=test_request.timeout_seconds,
            )

            if response.status_code == 200:
                return {"success": True}
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get(
                    "message", f"HTTP {response.status_code}"
                )
                return {"success": False, "error": error_msg}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def complete_text(self, request: CompletionRequest, api_key: str) -> str:
        """Execute text completion.

        Args:
            request: CompletionRequest with prompts and parameters
            api_key: API key for authentication

        Returns:
            Completion text from model

        Raises:
            httpx.HTTPError: On network or HTTP errors
            KeyError: If response format is unexpected
        """
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o",  # Model should come from config, hardcoded for now
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
            },
            timeout=request.timeout_seconds,
        )

        response.raise_for_status()
        data = response.json()
        content: str = data["choices"][0]["message"]["content"]
        return content
