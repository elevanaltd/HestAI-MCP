from enum import Enum
from typing import Dict, Any, Optional, Literal, List
from pydantic import BaseModel, Field, UUID4, field_validator
from datetime import datetime


class EventType(str, Enum):
    SESSION_START = "session_start"
    CONTEXT_UPDATE = "context_update"
    ARTIFACT_SUBMIT = "artifact_submit"
    SESSION_END = "session_end"


class HestAIEvent(BaseModel):
    """Immutable event record for the HestAI context ledger."""

    id: UUID4
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str
    role: str
    type: EventType
    payload: Dict[str, Any]


class SessionStartPayload(BaseModel):
    focus: str
    working_dir: str
    branch: str


class SessionEndPayload(BaseModel):
    """Payload for session end events."""

    session_id: str
    outcomes: List[str]  # What was accomplished
    golden_nuggets: List[str] = Field(..., max_length=2)  # Key learnings (max 2, <50 chars each)
    next_actions: List[str]  # Suggested continuations

    @field_validator("golden_nuggets")
    @classmethod
    def validate_golden_nuggets(cls, v: List[str]) -> List[str]:
        """Validate golden nuggets constraints."""
        if len(v) > 2:
            raise ValueError("Maximum 2 golden nuggets allowed")
        for nugget in v:
            if len(nugget) > 50:
                raise ValueError(f"Golden nugget exceeds 50 characters: {len(nugget)}")
        return v


class ContextUpdatePayload(BaseModel):
    target_file: str  # e.g. "PROJECT-CONTEXT.md"
    section: Optional[str] = None
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
