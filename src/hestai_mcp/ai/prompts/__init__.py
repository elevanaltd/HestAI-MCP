"""AI prompt components for HestAI-MCP internal AI operations.

This module implements the LAYERED CONSTITUTIONAL INJECTION architecture
decided in debate 2026-01-02-context-steward-prompt-architecture:

- Identity Kernel (~30 lines): WHO the agent IS - always loaded
- Operation Protocols (~50 lines): WHAT each specific call does - per-tool

The organizing principle: IDENTITY ≠ OPERATION.
Don't mix WHO (persistent) with WHAT (transient). Layer them, don't blend them.
"""

from hestai_mcp.ai.prompts.identity_kernel import CONTEXT_STEWARD_IDENTITY
from hestai_mcp.ai.prompts.protocols import (
    CLOCK_IN_SYNTHESIS_PROTOCOL,
    CLOCK_OUT_COMPRESSION_PROTOCOL,
    compose_prompt,
)

__all__ = [
    "CONTEXT_STEWARD_IDENTITY",
    "CLOCK_IN_SYNTHESIS_PROTOCOL",
    "CLOCK_OUT_COMPRESSION_PROTOCOL",
    "compose_prompt",
]
