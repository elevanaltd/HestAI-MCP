from datetime import UTC, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import UUID4, BaseModel, Field, field_validator


class EventType(str, Enum):
    SESSION_START = "session_start"
    CONTEXT_UPDATE = "context_update"
    ARTIFACT_SUBMIT = "artifact_submit"
    SESSION_END = "session_end"


class HestAIEvent(BaseModel):
    """Immutable event record for the HestAI context ledger."""

    id: UUID4
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: str
    role: str
    type: EventType
    payload: dict[str, Any]


class SessionStartPayload(BaseModel):
    focus: str
    working_dir: str
    branch: str


class SessionEndPayload(BaseModel):
    """Payload for session end events."""

    session_id: str
    outcomes: list[str]  # What was accomplished
    golden_nuggets: list[str] = Field(..., max_length=2)  # Key learnings (max 2, <50 chars each)
    next_actions: list[str]  # Suggested continuations

    @field_validator("golden_nuggets")
    @classmethod
    def validate_golden_nuggets(cls, v: list[str]) -> list[str]:
        """Validate golden nuggets constraints."""
        if len(v) > 2:
            raise ValueError("Maximum 2 golden nuggets allowed")
        for nugget in v:
            if len(nugget) > 50:
                raise ValueError(f"Golden nugget exceeds 50 characters: {len(nugget)}")
        return v


class ContextUpdatePayload(BaseModel):
    target_file: str  # e.g. "PROJECT-CONTEXT.md"
    section: str | None = None
    operation: str = "append"  # append, replace, delete
    content: str


class ArtifactSubmitPayload(BaseModel):
    """Payload for artifact submission events."""

    artifact_type: Literal["adr", "session_note", "workflow", "config"]
    path: str  # Relative path where artifact should go
    content: str  # Artifact content
    intent: str  # What this artifact documents


class HestAIConfig(BaseModel):
    """Configuration for HestAI MCP server (ADR-0007)."""

    project_root: str
    # Direct .hestai/ directory (no symlinks/worktrees)
    hestai_dir: str = ".hestai"
