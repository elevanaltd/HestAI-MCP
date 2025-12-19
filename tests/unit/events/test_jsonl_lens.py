"""
Tests for ClaudeJsonlLens - Claude session JSONL parser.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase)
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

Test Coverage:
- Basic message parsing (user, assistant)
- Tool operations (tool_use, tool_result)
- Model swap detection
- Streaming behavior
- Error handling (strict mode, malformed JSON)
- Edge cases (empty lines, mixed content)
"""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from hestai_mcp.events import (
    AssistantMessage,
    ClaudeJsonlLens,
    JsonlParseError,
    ModelSwap,
    ToolResult,
    ToolUse,
    UnknownSchemaError,
    UserMessage,
)


@pytest.mark.unit
class TestUserMessage:
    """Test parsing of user messages from Claude JSONL."""

    def test_parses_user_message(self, tmp_path: Path):
        """Basic user message extraction."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "Hello, Claude!"}],
                    },
                }
            )
            + "\n"
        )

        lens = ClaudeJsonlLens()
        events = list(lens.parse_file(jsonl_path))

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, UserMessage)
        assert event.event_type == "user_message"
        assert event.content == "Hello, Claude!"
        assert event.line_number == 0


@pytest.mark.unit
class TestAssistantMessage:
    """Test parsing of assistant messages from Claude JSONL."""

    def test_parses_assistant_message(self, tmp_path: Path):
        """Assistant message with model info."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "I understand."}],
                        "model": "claude-opus-4-5-20251101",
                    },
                }
            )
            + "\n"
        )

        lens = ClaudeJsonlLens()
        events = list(lens.parse_file(jsonl_path))

        assert len(events) == 2  # AssistantMessage + ModelSwap

        # Check assistant message
        msg = [e for e in events if isinstance(e, AssistantMessage)][0]
        assert msg.event_type == "assistant_message"
        assert msg.content == "I understand."
        assert msg.model == "claude-opus-4-5-20251101"

        # Check model swap event
        swap = [e for e in events if isinstance(e, ModelSwap)][0]
        assert swap.event_type == "model_swap"
        assert swap.model == "claude-opus-4-5-20251101"


@pytest.mark.unit
class TestToolOperations:
    """Test parsing of tool_use and tool_result entries."""

    def test_parses_tool_use(self, tmp_path: Path):
        """Tool invocation with parameters."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "tool_use",
                    "name": "Read",
                    "id": "toolu_01ABC123",
                    "input": {"file_path": "/path/to/file.py"},
                }
            )
            + "\n"
        )

        lens = ClaudeJsonlLens()
        events = list(lens.parse_file(jsonl_path))

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, ToolUse)
        assert event.event_type == "tool_use"
        assert event.tool_name == "Read"
        assert event.tool_id == "toolu_01ABC123"
        assert event.parameters == {"file_path": "/path/to/file.py"}

    def test_parses_tool_result(self, tmp_path: Path):
        """Tool result extraction."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_01ABC123",
                    "content": [{"type": "text", "text": "File contents here"}],
                }
            )
            + "\n"
        )

        lens = ClaudeJsonlLens()
        events = list(lens.parse_file(jsonl_path))

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, ToolResult)
        assert event.event_type == "tool_result"
        assert event.tool_use_id == "toolu_01ABC123"
        assert event.output == "File contents here"
        assert event.is_error is False


@pytest.mark.unit
class TestModelSwapDetection:
    """Test model change detection from swap commands."""

    def test_detects_model_swap(self, tmp_path: Path):
        """Model change detection from swap command."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Set model to claude-sonnet-4-5-20250929 (claude-sonnet-4-5-20250929)",
                            }
                        ],
                    },
                }
            )
            + "\n"
        )

        lens = ClaudeJsonlLens()
        events = list(lens.parse_file(jsonl_path))

        # Should yield both UserMessage and ModelSwap
        assert len(events) == 2

        swap_events = [e for e in events if isinstance(e, ModelSwap)]
        assert len(swap_events) == 1
        swap = swap_events[0]
        assert swap.model == "claude-sonnet-4-5-20250929"
        assert swap.source == "swap_command"


@pytest.mark.unit
class TestStreamingBehavior:
    """Test that parsing yields events one at a time."""

    def test_streaming_generator(self, tmp_path: Path):
        """Yields events one at a time (not list)."""
        jsonl_path = tmp_path / "session.jsonl"
        lines = [
            json.dumps(
                {
                    "type": "user",
                    "message": {"role": "user", "content": [{"type": "text", "text": "First"}]},
                }
            )
            + "\n",
            json.dumps(
                {
                    "type": "user",
                    "message": {"role": "user", "content": [{"type": "text", "text": "Second"}]},
                }
            )
            + "\n",
        ]
        jsonl_path.write_text("".join(lines))

        lens = ClaudeJsonlLens()
        result = lens.parse_file(jsonl_path)

        # Verify it's a generator/iterator
        assert isinstance(result, Iterator)

        # Consume one at a time
        events = []
        for event in result:
            events.append(event)

        assert len(events) == 2
        assert events[0].content == "First"
        assert events[1].content == "Second"


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_strict_mode_raises_on_unknown(self, tmp_path: Path):
        """UnknownSchemaError on bad type in strict mode."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(json.dumps({"type": "unknown_type", "data": "something"}) + "\n")

        lens = ClaudeJsonlLens(strict=True)

        with pytest.raises(UnknownSchemaError) as exc_info:
            list(lens.parse_file(jsonl_path))

        assert exc_info.value.line_number == 0
        assert exc_info.value.record_type == "unknown_type"

    def test_handles_malformed_json(self, tmp_path: Path):
        """JsonlParseError on bad JSON."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text("not valid json\n")

        lens = ClaudeJsonlLens()

        with pytest.raises(JsonlParseError) as exc_info:
            list(lens.parse_file(jsonl_path))

        assert exc_info.value.line_number == 0


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and mixed content."""

    def test_handles_mixed_content_blocks(self, tmp_path: Path):
        """Text + tool_use in same message."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "Let me check that file."},
                            {
                                "type": "tool_use",
                                "name": "Read",
                                "id": "toolu_123",
                                "input": {"file_path": "/test.py"},
                            },
                        ],
                        "model": "claude-opus-4-5-20251101",
                    },
                }
            )
            + "\n"
        )

        lens = ClaudeJsonlLens()
        events = list(lens.parse_file(jsonl_path))

        # Should extract text from assistant message, tool_use separately
        # plus model swap event
        assert len(events) >= 2

        msg_events = [e for e in events if isinstance(e, AssistantMessage)]
        assert len(msg_events) == 1
        assert msg_events[0].content == "Let me check that file."

    def test_handles_empty_lines(self, tmp_path: Path):
        """Skips blank lines gracefully."""
        jsonl_path = tmp_path / "session.jsonl"
        content = (
            json.dumps(
                {
                    "type": "user",
                    "message": {"role": "user", "content": [{"type": "text", "text": "First"}]},
                }
            )
            + "\n"
            + "\n"  # Empty line
            + json.dumps(
                {
                    "type": "user",
                    "message": {"role": "user", "content": [{"type": "text", "text": "Second"}]},
                }
            )
            + "\n"
        )
        jsonl_path.write_text(content)

        lens = ClaudeJsonlLens()
        events = list(lens.parse_file(jsonl_path))

        assert len(events) == 2
        assert events[0].content == "First"
        assert events[1].content == "Second"

    def test_handles_string_content(self, tmp_path: Path):
        """Handle both string and list content formats."""
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {"type": "user", "message": {"role": "user", "content": "Plain string content"}}
            )
            + "\n"
        )

        lens = ClaudeJsonlLens()
        events = list(lens.parse_file(jsonl_path))

        assert len(events) == 1
        assert events[0].content == "Plain string content"


@pytest.mark.unit
class TestParseStream:
    """Test parse_stream for in-memory lines."""

    def test_parse_stream(self):
        """Parse stream of JSONL lines (for testing or stdin)."""
        lines = [
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "Stream test"}],
                    },
                }
            )
            + "\n"
        ]

        lens = ClaudeJsonlLens()
        events = list(lens.parse_stream(lines))

        assert len(events) == 1
        assert events[0].content == "Stream test"
