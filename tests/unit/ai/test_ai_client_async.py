"""
Tests for async-first AIClient implementation.

SS-I2 Compliance: All provider calls, MCP tool invocations, and I/O operations
must be async. No blocking calls in the MCP server event loop.

Validation: AIClient uses httpx.AsyncClient. All tool handlers are async def.
"""

import inspect
from typing import ClassVar

import httpx
import pytest

from hestai_mcp.ai.client import AIClient
from hestai_mcp.ai.config import AIConfig, ProviderConfig
from hestai_mcp.ai.providers.base import CompletionRequest


@pytest.mark.unit
class TestAIClientAsyncCompliance:
    """Test SS-I2: AIClient must be async-first."""

    def test_complete_text_is_async(self):
        """AIClient.complete_text must be an async method (SS-I2)."""
        client = AIClient()

        # SS-I2 requires: "All provider calls... must be async"
        assert inspect.iscoroutinefunction(
            client.complete_text
        ), "complete_text must be async def to comply with SS-I2"

    def test_aiclient_has_async_context_manager(self):
        """AIClient must support async context manager for connection pooling."""
        # SS-I2: Connection pooling requires proper async lifecycle
        assert hasattr(
            AIClient, "__aenter__"
        ), "AIClient must implement __aenter__ for async context manager"
        assert hasattr(
            AIClient, "__aexit__"
        ), "AIClient must implement __aexit__ for async context manager"


@pytest.mark.unit
class TestAIClientAsyncBehavior:
    """Test async behavior of AIClient."""

    @pytest.mark.asyncio
    async def test_context_manager_creates_async_client(self):
        """Async context manager must create httpx.AsyncClient internally."""
        client = AIClient()

        async with client as c:
            # Should have an internal async client
            assert hasattr(c, "_async_client")
            # Check it has the expected async methods
            assert hasattr(c._async_client, "post")
            assert hasattr(c._async_client, "aclose")

    @pytest.mark.asyncio
    async def test_complete_text_without_api_key_raises(self):
        """complete_text raises ValueError when no API key is configured."""
        client = AIClient()
        request = CompletionRequest(
            system_prompt="Test system prompt",
            user_prompt="Test user prompt",
        )

        # Without API keys, should raise ValueError
        async with client:
            with pytest.raises(ValueError, match="No API key available"):
                await client.complete_text(request)

    @pytest.mark.asyncio
    async def test_fallback_chain_async(self, mock_httpx_async_timeout, monkeypatch):
        """Fallback chain must work asynchronously (SS-I2)."""
        # Set a fake API key so the provider is tried
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key-for-testing")

        client = AIClient()
        request = CompletionRequest(
            system_prompt="Test",
            user_prompt="Test",
        )

        # When all providers timeout, should raise TimeoutException or ValueError
        async with client:
            with pytest.raises((httpx.TimeoutException, ValueError)):
                await client.complete_text(request)


@pytest.mark.unit
class TestProviderAsyncCompliance:
    """Test that providers are async-first."""

    def test_openai_compat_provider_complete_text_is_async(self):
        """OpenAICompatProvider.complete_text must be async."""
        from hestai_mcp.ai.providers.openai_compat import OpenAICompatProvider

        provider = OpenAICompatProvider(
            provider_name="openai", base_url="https://api.openai.com/v1"
        )

        assert inspect.iscoroutinefunction(
            provider.complete_text
        ), "Provider.complete_text must be async def to comply with SS-I2"


class MockTransportWithTracking(httpx.AsyncBaseTransport):
    """Mock transport that tracks requests and returns configurable responses.

    This class implements httpx.AsyncBaseTransport to intercept all HTTP requests
    made through httpx.AsyncClient. By using the transport layer, we:
    1. Keep the real httpx.AsyncClient instance (isinstance checks pass)
    2. Intercept actual HTTP calls at the network layer
    3. Track what requests were made for verification
    """

    # Class-level tracking for verification across instances
    requests_made: ClassVar[list[httpx.Request]] = []
    response_content: ClassVar[str] = "Mocked AI response"
    response_status: ClassVar[int] = 200
    should_timeout: ClassVar[bool] = False

    @classmethod
    def reset(cls) -> None:
        """Reset tracking state between tests."""
        cls.requests_made = []
        cls.response_content = "Mocked AI response"
        cls.response_status = 200
        cls.should_timeout = False

    @classmethod
    def configure_response(cls, content: str, status: int = 200) -> None:
        """Configure the response that will be returned."""
        cls.response_content = content
        cls.response_status = status
        cls.should_timeout = False

    @classmethod
    def configure_timeout(cls) -> None:
        """Configure to simulate a timeout."""
        cls.should_timeout = True

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Handle async request - core interception point."""
        # Track the request for verification
        MockTransportWithTracking.requests_made.append(request)

        if MockTransportWithTracking.should_timeout:
            raise httpx.TimeoutException("Mocked timeout", request=request)

        return httpx.Response(
            MockTransportWithTracking.response_status,
            json={
                "choices": [{"message": {"content": MockTransportWithTracking.response_content}}]
            },
            request=request,
        )


# Store reference to real AsyncClient before any patching
_RealAsyncClient = httpx.AsyncClient


@pytest.fixture
def mock_httpx_async_response(monkeypatch):
    """Mock httpx.AsyncClient with tracked mock transport for success responses.

    This fixture:
    1. Returns REAL httpx.AsyncClient instances (isinstance checks pass)
    2. Uses MockTransportWithTracking to intercept HTTP calls
    3. Patches at both httpx module AND the import location in client.py
    4. Resets tracking state between tests
    """
    MockTransportWithTracking.reset()
    MockTransportWithTracking.configure_response("Mocked AI response", 200)

    def create_mock_client(**kwargs):
        # Filter out transport if provided, use our mock transport
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "transport"}
        return _RealAsyncClient(transport=MockTransportWithTracking(), **filtered_kwargs)

    # Patch in both locations to ensure interception
    monkeypatch.setattr("httpx.AsyncClient", create_mock_client)
    monkeypatch.setattr("hestai_mcp.ai.client.httpx.AsyncClient", create_mock_client)

    return MockTransportWithTracking


@pytest.fixture
def mock_httpx_async_timeout(monkeypatch):
    """Mock httpx.AsyncClient to simulate timeout with tracking."""
    MockTransportWithTracking.reset()
    MockTransportWithTracking.configure_timeout()

    def create_timeout_client(**kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "transport"}
        return _RealAsyncClient(transport=MockTransportWithTracking(), **filtered_kwargs)

    monkeypatch.setattr("httpx.AsyncClient", create_timeout_client)
    monkeypatch.setattr("hestai_mcp.ai.client.httpx.AsyncClient", create_timeout_client)

    return MockTransportWithTracking


@pytest.fixture
def openai_config():
    """Create AIConfig with OpenAI as primary provider.

    The default config uses openrouter, but our tests mock OpenAI responses.
    This ensures AIClient uses the openai provider so OPENAI_API_KEY is resolved.
    """
    return AIConfig(
        primary=ProviderConfig(provider="openai", model="gpt-4o"),
        fallback=[],
    )


@pytest.mark.unit
class TestMockIntegrity:
    """Test that our mock correctly intercepts httpx calls and preserves types."""

    @pytest.mark.asyncio
    async def test_mock_returns_real_async_client_instance(self, mock_httpx_async_response):
        """Verify mock returns real httpx.AsyncClient for isinstance checks."""
        # Create client through the mock
        client = httpx.AsyncClient()

        # CRITICAL: isinstance checks must pass
        # This verifies we're returning real httpx.AsyncClient, not a mock object
        assert isinstance(
            client, _RealAsyncClient
        ), "Mock must return real httpx.AsyncClient instance for type compatibility"

        # Also verify it has the expected httpx.AsyncClient interface
        assert hasattr(client, "post")
        assert hasattr(client, "get")
        assert hasattr(client, "aclose")

        await client.aclose()

    @pytest.mark.asyncio
    async def test_mock_transport_intercepts_http_calls(self, mock_httpx_async_response):
        """Verify mock transport actually intercepts HTTP requests."""
        mock_httpx_async_response.reset()

        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.example.com/test", json={"test": "data"})

        # CRITICAL: Verify the request was intercepted
        assert (
            len(mock_httpx_async_response.requests_made) == 1
        ), "Mock transport must intercept HTTP requests"

        # Verify the request details
        intercepted_request = mock_httpx_async_response.requests_made[0]
        assert str(intercepted_request.url) == "https://api.example.com/test"
        assert intercepted_request.method == "POST"

        # Verify we got our mock response, not a real HTTP response
        assert response.status_code == 200
        data = response.json()
        assert data["choices"][0]["message"]["content"] == "Mocked AI response"

    @pytest.mark.asyncio
    async def test_mock_configurable_response_content(self, mock_httpx_async_response):
        """Verify mock can return different response content."""
        custom_content = "Custom test response from mock"
        mock_httpx_async_response.configure_response(custom_content, 200)

        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.example.com/test", json={})

        data = response.json()
        assert data["choices"][0]["message"]["content"] == custom_content


@pytest.mark.unit
class TestAIClientFullCallChain:
    """Test full call chain: AIClient -> Provider -> httpx (intercepted by mock)."""

    @pytest.mark.asyncio
    async def test_complete_text_full_chain_success(
        self, mock_httpx_async_response, monkeypatch, openai_config
    ):
        """Verify AIClient.complete_text calls through to provider and returns response.

        This tests the FULL call chain:
        AIClient.complete_text()
          -> _complete_text_with_client()
            -> provider.complete_text()
              -> client.post() [intercepted by mock transport]
                -> returns mocked response
                  -> parsed and returned as string
        """
        # Configure expected response content
        expected_content = "This is the AI-generated response"
        mock_httpx_async_response.configure_response(expected_content, 200)

        # Set API key so provider is enabled
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-for-testing")

        # Use openai_config to ensure OpenAI provider is primary
        client = AIClient(config=openai_config)
        request = CompletionRequest(
            system_prompt="You are a helpful assistant",
            user_prompt="Hello, how are you?",
        )

        # Execute the full call chain
        async with client as c:
            result = await c.complete_text(request)

        # CRITICAL: Verify we got the mocked response content
        assert result == expected_content, (
            f"Expected '{expected_content}' but got '{result}'. "
            "Full call chain must return parsed response from mock."
        )

        # Verify the HTTP call was intercepted
        assert (
            len(mock_httpx_async_response.requests_made) >= 1
        ), "At least one HTTP request must have been intercepted"

        # Verify request details match expected API call
        intercepted_request = mock_httpx_async_response.requests_made[0]
        assert "api.openai.com" in str(intercepted_request.url), "Request should be to OpenAI API"
        assert "/chat/completions" in str(
            intercepted_request.url
        ), "Request should be to chat completions endpoint"

    @pytest.mark.asyncio
    async def test_complete_text_without_context_manager(
        self, mock_httpx_async_response, monkeypatch, openai_config
    ):
        """Verify complete_text works without async context manager (temporary client)."""
        expected_content = "Response via temporary client"
        mock_httpx_async_response.configure_response(expected_content, 200)
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

        # Create client but don't use async context manager
        client = AIClient(config=openai_config)
        request = CompletionRequest(
            system_prompt="Test",
            user_prompt="Test prompt",
        )

        # complete_text should create temporary client internally
        result = await client.complete_text(request)

        assert result == expected_content
        assert len(mock_httpx_async_response.requests_made) >= 1

    @pytest.mark.asyncio
    async def test_internal_async_client_isinstance_check(
        self, mock_httpx_async_response, monkeypatch, openai_config
    ):
        """Verify _async_client passes isinstance checks inside AIClient."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        client = AIClient(config=openai_config)

        async with client as c:
            # CRITICAL: The internal client must be a real httpx.AsyncClient
            # This is what the user concern was about
            assert c._async_client is not None
            assert isinstance(c._async_client, _RealAsyncClient), (
                "AIClient._async_client must be real httpx.AsyncClient instance. "
                "isinstance checks failing would indicate the mock is broken."
            )

    @pytest.mark.asyncio
    async def test_request_headers_contain_authorization(
        self, mock_httpx_async_response, monkeypatch, openai_config
    ):
        """Verify provider sends correct Authorization header."""
        mock_httpx_async_response.configure_response("test", 200)
        test_api_key = "sk-test-key-12345"
        monkeypatch.setenv("OPENAI_API_KEY", test_api_key)

        client = AIClient(config=openai_config)
        request = CompletionRequest(
            system_prompt="System",
            user_prompt="User",
        )

        async with client:
            await client.complete_text(request)

        # Verify authorization header
        intercepted_request = mock_httpx_async_response.requests_made[0]
        auth_header = intercepted_request.headers.get("Authorization")
        assert (
            auth_header == f"Bearer {test_api_key}"
        ), f"Authorization header should be 'Bearer {test_api_key}', got '{auth_header}'"

    @pytest.mark.asyncio
    async def test_request_body_contains_prompts(
        self, mock_httpx_async_response, monkeypatch, openai_config
    ):
        """Verify provider sends correct request body with prompts."""
        mock_httpx_async_response.configure_response("test", 200)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        system_prompt = "You are a code reviewer"
        user_prompt = "Review this function: def foo(): pass"

        client = AIClient(config=openai_config)
        request = CompletionRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        async with client:
            await client.complete_text(request)

        # Verify request body
        intercepted_request = mock_httpx_async_response.requests_made[0]
        # Read the request body content
        body_content = intercepted_request.content.decode("utf-8")

        assert system_prompt in body_content, "Request body should contain system prompt"
        assert user_prompt in body_content, "Request body should contain user prompt"


# =============================================================================
# TMG Test Plan: Priority 0 - Critical Reliability Paths
# =============================================================================


class ConfigurableMockTransport(httpx.AsyncBaseTransport):
    """Mock transport with per-request configurable responses.

    Unlike MockTransportWithTracking which uses class-level state,
    this transport allows configuring responses per-URL for testing
    fallback chains where different providers return different responses.
    """

    def __init__(self, responses: dict[str, tuple[int, str | Exception]] | None = None):
        """Initialize with response mapping.

        Args:
            responses: Dict mapping URL patterns to (status_code, content) or Exception.
                       If content is an Exception, it will be raised.
        """
        self.responses = responses or {}
        self.requests_made: list[httpx.Request] = []
        self.default_response: tuple[int, str] = (200, "Default response")

    def set_response(self, url_pattern: str, status: int, content: str) -> None:
        """Set response for URLs matching pattern."""
        self.responses[url_pattern] = (status, content)

    def set_exception(self, url_pattern: str, exception: Exception) -> None:
        """Set exception to raise for URLs matching pattern."""
        self.responses[url_pattern] = (0, exception)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Handle async request with URL-based response selection."""
        self.requests_made.append(request)
        url_str = str(request.url)

        # Check for matching URL pattern
        for pattern, response_config in self.responses.items():
            if pattern in url_str:
                status_or_exc, content = response_config
                if isinstance(content, Exception):
                    raise content
                return httpx.Response(
                    status_or_exc,
                    json={"choices": [{"message": {"content": content}}]},
                    request=request,
                )

        # Default response
        status, content = self.default_response
        return httpx.Response(
            status,
            json={"choices": [{"message": {"content": content}}]},
            request=request,
        )


@pytest.fixture
def configurable_transport():
    """Create a configurable mock transport."""
    return ConfigurableMockTransport()


@pytest.fixture
def mock_httpx_with_transport(monkeypatch, configurable_transport):
    """Mock httpx.AsyncClient with configurable transport."""

    def create_client(**kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "transport"}
        return _RealAsyncClient(transport=configurable_transport, **filtered_kwargs)

    monkeypatch.setattr("httpx.AsyncClient", create_client)
    monkeypatch.setattr("hestai_mcp.ai.client.httpx.AsyncClient", create_client)

    return configurable_transport


@pytest.mark.unit
class TestNonRetryableErrorHaltsChain:
    """Test client.py:163-164 - Non-retryable errors halt fallback chain immediately."""

    @pytest.mark.asyncio
    async def test_http_401_halts_chain_no_fallback(self, mock_httpx_with_transport, monkeypatch):
        """HTTP 401 (Unauthorized) should raise immediately, NO fallback attempt.

        Target: client.py:162-164 (_is_retryable_error returns False for 4xx)
        """
        monkeypatch.setenv("OPENAI_API_KEY", "invalid-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "backup-key")

        # Configure OpenAI to return 401
        mock_httpx_with_transport.set_response("api.openai.com", 401, "Unauthorized")
        # Configure OpenRouter to succeed (should NOT be called)
        mock_httpx_with_transport.set_response("openrouter.ai", 200, "Fallback success")

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[ProviderConfig(provider="openrouter", model="claude-3.5-sonnet")],
        )
        client = AIClient(config=config)
        request = CompletionRequest(
            system_prompt="Test",
            user_prompt="Test",
        )

        # Act & Assert - should raise HTTPStatusError, not fall back
        async with client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.complete_text(request)

        # Verify 401 error
        assert exc_info.value.response.status_code == 401

        # CRITICAL: Verify only ONE request was made (no fallback attempted)
        assert len(mock_httpx_with_transport.requests_made) == 1
        assert "api.openai.com" in str(mock_httpx_with_transport.requests_made[0].url)

    @pytest.mark.asyncio
    async def test_http_403_halts_chain(self, mock_httpx_with_transport, monkeypatch):
        """HTTP 403 (Forbidden) should also halt chain immediately."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "backup-key")

        mock_httpx_with_transport.set_response("api.openai.com", 403, "Forbidden")
        mock_httpx_with_transport.set_response("openrouter.ai", 200, "Success")

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[ProviderConfig(provider="openrouter", model="model")],
        )
        client = AIClient(config=config)
        request = CompletionRequest(system_prompt="Test", user_prompt="Test")

        async with client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.complete_text(request)

        assert exc_info.value.response.status_code == 403
        assert len(mock_httpx_with_transport.requests_made) == 1

    @pytest.mark.asyncio
    async def test_http_400_halts_chain(self, mock_httpx_with_transport, monkeypatch):
        """HTTP 400 (Bad Request) should halt chain immediately."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_httpx_with_transport.set_response("api.openai.com", 400, "Bad Request")

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[],
        )
        client = AIClient(config=config)
        request = CompletionRequest(system_prompt="Test", user_prompt="Test")

        async with client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.complete_text(request)

        assert exc_info.value.response.status_code == 400


@pytest.mark.unit
class TestRetryableErrorTriggersFallback:
    """Test client.py:94-102 - Retryable errors trigger fallback chain."""

    @pytest.mark.asyncio
    async def test_http_503_triggers_fallback_to_secondary(
        self, mock_httpx_with_transport, monkeypatch
    ):
        """HTTP 503 (Service Unavailable) should trigger fallback to secondary provider.

        Target: client.py:94-102 (_is_retryable_error returns True for 5xx)
        """
        monkeypatch.setenv("OPENAI_API_KEY", "primary-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "secondary-key")

        # Primary returns 503, Secondary succeeds
        mock_httpx_with_transport.set_response("api.openai.com", 503, "Service Unavailable")
        mock_httpx_with_transport.set_response("openrouter.ai", 200, "Fallback succeeded!")

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[ProviderConfig(provider="openrouter", model="claude-3.5-sonnet")],
        )
        client = AIClient(config=config)
        request = CompletionRequest(system_prompt="Test", user_prompt="Test")

        # Act
        async with client:
            result = await client.complete_text(request)

        # Assert - should succeed via fallback
        assert result == "Fallback succeeded!"

        # Verify both providers were attempted
        assert len(mock_httpx_with_transport.requests_made) == 2
        assert "api.openai.com" in str(mock_httpx_with_transport.requests_made[0].url)
        assert "openrouter.ai" in str(mock_httpx_with_transport.requests_made[1].url)

    @pytest.mark.asyncio
    async def test_http_500_triggers_fallback(self, mock_httpx_with_transport, monkeypatch):
        """HTTP 500 (Internal Server Error) should trigger fallback."""
        monkeypatch.setenv("OPENAI_API_KEY", "primary-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "secondary-key")

        mock_httpx_with_transport.set_response("api.openai.com", 500, "Internal Error")
        mock_httpx_with_transport.set_response("openrouter.ai", 200, "Recovery success")

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[ProviderConfig(provider="openrouter", model="model")],
        )
        client = AIClient(config=config)
        request = CompletionRequest(system_prompt="Test", user_prompt="Test")

        async with client:
            result = await client.complete_text(request)

        assert result == "Recovery success"
        assert len(mock_httpx_with_transport.requests_made) == 2

    @pytest.mark.asyncio
    async def test_timeout_triggers_fallback(self, monkeypatch):
        """Timeout exceptions should trigger fallback.

        Target: client.py:94-95 (TimeoutException is retryable)
        """
        monkeypatch.setenv("OPENAI_API_KEY", "primary-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "secondary-key")

        # Create transport that times out for OpenAI but works for OpenRouter
        transport = ConfigurableMockTransport()
        timeout_exc = httpx.TimeoutException("Connection timed out")
        transport.set_exception("api.openai.com", timeout_exc)
        transport.set_response("openrouter.ai", 200, "Fallback after timeout")

        def create_client(**kwargs):
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != "transport"}
            return _RealAsyncClient(transport=transport, **filtered_kwargs)

        monkeypatch.setattr("httpx.AsyncClient", create_client)
        monkeypatch.setattr("hestai_mcp.ai.client.httpx.AsyncClient", create_client)

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[ProviderConfig(provider="openrouter", model="model")],
        )
        client = AIClient(config=config)
        request = CompletionRequest(system_prompt="Test", user_prompt="Test")

        async with client:
            result = await client.complete_text(request)

        assert result == "Fallback after timeout"

    @pytest.mark.asyncio
    async def test_connect_error_triggers_fallback(self, monkeypatch):
        """Connection errors should trigger fallback.

        Target: client.py:94 (ConnectError is retryable)
        """
        monkeypatch.setenv("OPENAI_API_KEY", "primary-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "secondary-key")

        transport = ConfigurableMockTransport()
        connect_exc = httpx.ConnectError("Connection refused")
        transport.set_exception("api.openai.com", connect_exc)
        transport.set_response("openrouter.ai", 200, "Fallback after connect error")

        def create_client(**kwargs):
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != "transport"}
            return _RealAsyncClient(transport=transport, **filtered_kwargs)

        monkeypatch.setattr("httpx.AsyncClient", create_client)
        monkeypatch.setattr("hestai_mcp.ai.client.httpx.AsyncClient", create_client)

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[ProviderConfig(provider="openrouter", model="model")],
        )
        client = AIClient(config=config)
        request = CompletionRequest(system_prompt="Test", user_prompt="Test")

        async with client:
            result = await client.complete_text(request)

        assert result == "Fallback after connect error"


@pytest.mark.unit
class TestAllProvidersFail:
    """Test client.py:170-171 - When all providers fail, raise LAST exception."""

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises_last_exception(
        self, mock_httpx_with_transport, monkeypatch
    ):
        """When all providers return 5xx, raise the LAST exception (from final provider).

        Target: client.py:170-171
        """
        monkeypatch.setenv("OPENAI_API_KEY", "primary-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "secondary-key")

        # Both providers return 5xx errors
        mock_httpx_with_transport.set_response("api.openai.com", 500, "Primary failed")
        mock_httpx_with_transport.set_response("openrouter.ai", 502, "Secondary failed")

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[ProviderConfig(provider="openrouter", model="model")],
        )
        client = AIClient(config=config)
        request = CompletionRequest(system_prompt="Test", user_prompt="Test")

        async with client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.complete_text(request)

        # CRITICAL: Should be the LAST error (502 from secondary), not the first (500)
        assert exc_info.value.response.status_code == 502

        # Verify both providers were tried
        assert len(mock_httpx_with_transport.requests_made) == 2

    @pytest.mark.asyncio
    async def test_multiple_fallbacks_all_fail(self, mock_httpx_with_transport, monkeypatch):
        """With multiple fallbacks, all failing, raise last exception."""
        monkeypatch.setenv("OPENAI_API_KEY", "key1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "key2")

        mock_httpx_with_transport.set_response("api.openai.com", 503, "First failed")
        mock_httpx_with_transport.set_response("openrouter.ai", 504, "Last failed")

        config = AIConfig(
            primary=ProviderConfig(provider="openai", model="gpt-4o"),
            fallback=[ProviderConfig(provider="openrouter", model="model")],
        )
        client = AIClient(config=config)
        request = CompletionRequest(system_prompt="Test", user_prompt="Test")

        async with client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.complete_text(request)

        # Should be 504 (last error)
        assert exc_info.value.response.status_code == 504


@pytest.mark.unit
class TestUnsupportedProvider:
    """Test client.py:78-79 - Unsupported provider raises ValueError."""

    def test_get_provider_unknown_raises_valueerror(self):
        """_get_provider with unknown provider name should raise ValueError.

        Target: client.py:78-79
        """
        client = AIClient()

        with pytest.raises(ValueError) as exc_info:
            client._get_provider("unknown-provider")

        assert "Unsupported provider" in str(exc_info.value)
        assert "unknown-provider" in str(exc_info.value)

    def test_get_provider_empty_string_raises_valueerror(self):
        """_get_provider with empty string should raise ValueError."""
        client = AIClient()

        with pytest.raises(ValueError) as exc_info:
            client._get_provider("")

        assert "Unsupported provider" in str(exc_info.value)

    def test_get_provider_typo_raises_valueerror(self):
        """_get_provider with typo (openaii vs openai) should raise ValueError."""
        client = AIClient()

        with pytest.raises(ValueError) as exc_info:
            client._get_provider("openaii")  # Typo

        assert "Unsupported provider" in str(exc_info.value)

    def test_get_provider_valid_providers_succeed(self):
        """_get_provider should succeed for valid providers."""
        from hestai_mcp.ai.providers.base import BaseProvider

        client = AIClient()

        # These should not raise
        openai_provider = client._get_provider("openai")
        openrouter_provider = client._get_provider("openrouter")

        assert isinstance(openai_provider, BaseProvider)
        assert isinstance(openrouter_provider, BaseProvider)


@pytest.mark.unit
class TestIsRetryableError:
    """Test client.py:84-102 - _is_retryable_error logic."""

    def test_timeout_exception_is_retryable(self):
        """TimeoutException should be retryable."""
        client = AIClient()
        error = httpx.TimeoutException("Timed out")

        assert client._is_retryable_error(error) is True

    def test_connect_error_is_retryable(self):
        """ConnectError should be retryable."""
        client = AIClient()
        error = httpx.ConnectError("Connection refused")

        assert client._is_retryable_error(error) is True

    def test_http_500_is_retryable(self):
        """HTTP 500 should be retryable."""
        client = AIClient()
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(500, request=request)
        error = httpx.HTTPStatusError("Server Error", request=request, response=response)

        assert client._is_retryable_error(error) is True

    def test_http_502_is_retryable(self):
        """HTTP 502 should be retryable."""
        client = AIClient()
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(502, request=request)
        error = httpx.HTTPStatusError("Bad Gateway", request=request, response=response)

        assert client._is_retryable_error(error) is True

    def test_http_503_is_retryable(self):
        """HTTP 503 should be retryable."""
        client = AIClient()
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(503, request=request)
        error = httpx.HTTPStatusError("Service Unavailable", request=request, response=response)

        assert client._is_retryable_error(error) is True

    def test_http_401_not_retryable(self):
        """HTTP 401 should NOT be retryable."""
        client = AIClient()
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(401, request=request)
        error = httpx.HTTPStatusError("Unauthorized", request=request, response=response)

        assert client._is_retryable_error(error) is False

    def test_http_403_not_retryable(self):
        """HTTP 403 should NOT be retryable."""
        client = AIClient()
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(403, request=request)
        error = httpx.HTTPStatusError("Forbidden", request=request, response=response)

        assert client._is_retryable_error(error) is False

    def test_http_400_not_retryable(self):
        """HTTP 400 should NOT be retryable."""
        client = AIClient()
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(400, request=request)
        error = httpx.HTTPStatusError("Bad Request", request=request, response=response)

        assert client._is_retryable_error(error) is False

    def test_http_429_not_retryable(self):
        """HTTP 429 (Rate Limited) should NOT be retryable (4xx)."""
        client = AIClient()
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(429, request=request)
        error = httpx.HTTPStatusError("Rate Limited", request=request, response=response)

        assert client._is_retryable_error(error) is False

    def test_generic_exception_not_retryable(self):
        """Generic exceptions should NOT be retryable."""
        client = AIClient()
        error = ValueError("Some other error")

        assert client._is_retryable_error(error) is False

    def test_http_499_not_retryable(self):
        """HTTP 499 (edge of 4xx) should NOT be retryable."""
        client = AIClient()
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(499, request=request)
        error = httpx.HTTPStatusError("Client Error", request=request, response=response)

        assert client._is_retryable_error(error) is False
