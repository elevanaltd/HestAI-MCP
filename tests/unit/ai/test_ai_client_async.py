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
