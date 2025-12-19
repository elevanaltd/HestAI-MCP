"""
ClaudeJsonlLens: Schema-on-read adapter for Claude session JSONL files.

This module provides a read-only adapter that parses Claude session logs (.jsonl)
into typed events. Designed for fail-fast validation to detect format changes.

Architecture Context:
- Part of hestai-core's multi-model future support
- Abstracts provider-specific formats (Claude, Gemini, Codex)
- Enables normalized event processing for session analysis
- Supports OCTAVE compression pipeline (clock_out tool)

Design Decisions:
1. Schema-on-Read: No file writing, strict schema validation
2. Fail-Fast: Raises on unknown formats (detects Claude API changes)
3. Streaming: Generator-based for large session files
4. Normalization: Raw JSONL → HestAIEvent objects

Reference Implementation:
- Extracted from hestai-mcp-server/tools/clockout.py::_parse_session_transcript
- Improved with strict typing and fail-fast validation
"""

import json
import re
from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

# ============================================================================
# EXCEPTIONS
# ============================================================================


class JsonlLensError(Exception):
    """Base exception for JsonlLens errors."""

    pass


class JsonlParseError(JsonlLensError):
    """Raised when JSON parsing fails."""

    def __init__(self, line_number: int, message: str):
        self.line_number = line_number
        super().__init__(f"Line {line_number}: {message}")


class UnknownSchemaError(JsonlLensError):
    """Raised when record type is not recognized (fail-fast)."""

    def __init__(self, line_number: int, record_type: str):
        self.line_number = line_number
        self.record_type = record_type
        super().__init__(f"Line {line_number}: Unknown record type '{record_type}'")


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class HestAIEvent(BaseModel):
    """Base class for normalized session events."""

    event_type: str
    timestamp: datetime | None = None
    line_number: int


class UserMessage(HestAIEvent):
    """User message event."""

    event_type: Literal["user_message"] = "user_message"
    content: str


class AssistantMessage(HestAIEvent):
    """Assistant message event."""

    event_type: Literal["assistant_message"] = "assistant_message"
    content: str
    model: str | None = None


class ToolUse(HestAIEvent):
    """Tool invocation event."""

    event_type: Literal["tool_use"] = "tool_use"
    tool_name: str
    tool_id: str
    parameters: dict[str, Any]


class ToolResult(HestAIEvent):
    """Tool result event."""

    event_type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    output: str
    is_error: bool = False


class ModelSwap(HestAIEvent):
    """Model change event."""

    event_type: Literal["model_swap"] = "model_swap"
    model: str
    source: Literal["assistant_message", "swap_command"] = "assistant_message"


# ============================================================================
# MAIN LENS CLASS
# ============================================================================


class ClaudeJsonlLens:
    """
    Read-only adapter for Claude session JSONL files.

    Parses raw Claude logs and yields normalized HestAIEvent objects.
    Designed for schema-on-read with fail-fast validation.

    Example:
        >>> lens = ClaudeJsonlLens()
        >>> for event in lens.parse_file(Path("session.jsonl")):
        ...     if isinstance(event, UserMessage):
        ...         print(f"User: {event.content}")
    """

    def __init__(self, strict: bool = True):
        """
        Initialize the lens.

        Args:
            strict: If True, raise on unknown record types.
                   If False, skip unknown records (not recommended).
        """
        self.strict = strict
        self._current_model: str | None = None

    def parse_file(self, jsonl_path: Path) -> Iterator[HestAIEvent]:
        """
        Parse a Claude session JSONL file.

        Args:
            jsonl_path: Path to .jsonl file

        Yields:
            HestAIEvent subclass instances

        Raises:
            JsonlParseError: On malformed JSON
            UnknownSchemaError: On unknown record type (if strict=True)
        """
        with open(jsonl_path) as f:
            yield from self.parse_stream(f)

    def parse_stream(self, lines: Iterable[str]) -> Iterator[HestAIEvent]:
        """
        Parse a stream of JSONL lines (for testing or stdin).

        Args:
            lines: Iterable of JSONL strings

        Yields:
            HestAIEvent subclass instances

        Raises:
            JsonlParseError: On malformed JSON
            UnknownSchemaError: On unknown record type (if strict=True)
        """
        for line_number, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                continue

            # Parse JSON
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                raise JsonlParseError(line_number, f"Invalid JSON: {e}") from e

            # Extract record type
            record_type = record.get("type")
            if not record_type:
                if self.strict:
                    raise UnknownSchemaError(line_number, "<missing>")
                continue

            # Dispatch to parser
            if record_type == "user":
                yield from self._parse_user(record, line_number)
            elif record_type == "assistant":
                yield from self._parse_assistant(record, line_number)
            elif record_type == "tool_use":
                yield from self._parse_tool_use(record, line_number)
            elif record_type == "tool_result":
                yield from self._parse_tool_result(record, line_number)
            else:
                if self.strict:
                    raise UnknownSchemaError(line_number, record_type)

    # ========================================================================
    # PARSER METHODS
    # ========================================================================

    def _parse_user(self, record: dict[str, Any], line_number: int) -> Iterator[HestAIEvent]:
        """Parse user message record."""
        message = record.get("message", {})
        content = self._extract_text_content(message.get("content"))

        # Detect model swap commands
        if content and "Set model to" in content:
            match = re.search(r"\((claude-[^)]+)\)", content)
            if match:
                swap_model = match.group(1)
                if swap_model != self._current_model:
                    self._current_model = swap_model
                    yield ModelSwap(
                        model=swap_model,
                        timestamp=record.get("timestamp"),
                        line_number=line_number,
                        source="swap_command",
                    )

        # Yield user message
        if content:
            yield UserMessage(
                content=content,
                timestamp=record.get("timestamp"),
                line_number=line_number,
            )

    def _parse_assistant(self, record: dict[str, Any], line_number: int) -> Iterator[HestAIEvent]:
        """Parse assistant message record."""
        message = record.get("message", {})
        content = self._extract_text_content(message.get("content"))
        model = message.get("model")

        # Track model changes (exclude synthetic models)
        if model and model != self._current_model and model != "<synthetic>":
            self._current_model = model
            yield ModelSwap(
                model=model,
                timestamp=record.get("timestamp"),
                line_number=line_number,
                source="assistant_message",
            )

        # Yield assistant message
        if content:
            yield AssistantMessage(
                content=content,
                model=model,
                timestamp=record.get("timestamp"),
                line_number=line_number,
            )

    def _parse_tool_use(self, record: dict[str, Any], line_number: int) -> Iterator[HestAIEvent]:
        """Parse tool_use record."""
        yield ToolUse(
            tool_name=record.get("name", "unknown"),
            tool_id=record.get("id", "unknown"),
            parameters=record.get("input", {}),
            timestamp=record.get("timestamp"),
            line_number=line_number,
        )

    def _parse_tool_result(self, record: dict[str, Any], line_number: int) -> Iterator[HestAIEvent]:
        """Parse tool_result record."""
        content_parts = record.get("content", [])
        output = self._extract_text_content(content_parts)

        yield ToolResult(
            tool_use_id=record.get("tool_use_id", "unknown"),
            output=output,
            is_error=record.get("is_error", False),
            timestamp=record.get("timestamp"),
            line_number=line_number,
        )

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _extract_text_content(self, content: Any) -> str:
        """
        Extract text from content field.

        Handles both string and list[dict] formats from Claude API.

        Args:
            content: String or list of content blocks

        Returns:
            Extracted text content
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text = part.get("text")
                    if text:
                        text_parts.append(text)
            return "\n".join(text_parts)
        else:
            return ""
