"""Smoke tests to verify basic imports work."""


def test_import_main_package() -> None:
    """Test that main package imports successfully."""
    import hestai_mcp

    assert hestai_mcp.__version__ == "0.1.0"


def test_import_ai_client() -> None:
    """Test that AI client imports successfully."""
    from hestai_mcp.modules.services.ai import AIClient, AIConfig

    assert AIClient is not None
    assert AIConfig is not None


def test_import_schemas() -> None:
    """Test that schemas import successfully."""
    from hestai_mcp.schemas.schemas import EventType, HestAIConfig, HestAIEvent

    assert EventType is not None
    assert HestAIEvent is not None
    assert HestAIConfig is not None


def test_import_mcp_tools() -> None:
    """Test that MCP tools import successfully."""
    from hestai_mcp.modules.tools import clock_in, clock_out

    assert clock_in is not None
    assert clock_out is not None


def test_import_jsonl_lens() -> None:
    """Test that jsonl_lens imports successfully."""
    from hestai_mcp.events.jsonl_lens import ClaudeJsonlLens

    assert ClaudeJsonlLens is not None
