"""Soft-deprecation gate primitives for legacy hestai-mcp tools (issue #400).

Per ADR-0353, ``mcp__hestai__{clock_in, clock_out, submit_review}`` are
soft-deprecated in favour of ``mcp__hestai-context__*``. This module supplies
the shared infrastructure used by ``hestai_mcp.mcp.server.call_tool`` to gate
those three tools behind the ``HESTAI_MCP_LEGACY_TOOLS_ENABLED`` env-var.

Steady-state semantics (env-var unset/0):
    Tools remain registered (visible to MCP clients) but return the structured
    deprecation payload from :func:`deprecation_payload` instead of executing
    legacy logic. No telemetry, no stderr.

Rollback semantics (env-var=1):
    Legacy logic executes. Three concurrent surfaces signal the rollback:
      1. stderr deprecation line (:func:`emit_stderr_warning`)
      2. additive ``_deprecation`` field on the response (:func:`deprecation_field`)
      3. append-only JSONL telemetry (:func:`record_legacy_invocation`) under
         ``.hestai/state/audit/legacy-tool-invocations.jsonl``
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

#: Env-var that re-enables legacy tool execution as a rollback safety net.
LEGACY_ENV_VAR: str = "HESTAI_MCP_LEGACY_TOOLS_ENABLED"

#: Tool short-names whose ``mcp__hestai__`` registration is soft-deprecated.
SOFT_DEPRECATED_TOOLS: frozenset[str] = frozenset({"clock_in", "clock_out", "submit_review"})

_TRUE_VALUES: frozenset[str] = frozenset({"1", "true", "yes", "on"})


def is_legacy_enabled() -> bool:
    """Return True iff the rollback env-var is set to a truthy value.

    The default (unset, empty, ``0``, ``false``) is False — soft-deprecation
    is the steady state per ADR-0353.
    """
    raw = os.environ.get(LEGACY_ENV_VAR, "").strip().lower()
    return raw in _TRUE_VALUES


def deprecation_payload(tool_short_name: str) -> dict[str, str]:
    """Build the Q2 structured payload returned in the default (deactivated) state.

    Parameters
    ----------
    tool_short_name:
        The tool's short name (e.g. ``"clock_in"``), without the
        ``mcp__hestai__`` prefix.
    """
    return {
        "error": "DEPRECATED",
        "tool": f"mcp__hestai__{tool_short_name}",
        "replacement": f"mcp__hestai-context__{tool_short_name}",
        "reason": ("Legacy hestai-mcp tool deactivated per ADR-0353. " "Use hestai-context-mcp."),
        "rollback": "Set HESTAI_MCP_LEGACY_TOOLS_ENABLED=1 to temporarily restore.",
    }


def deprecation_field(tool_short_name: str) -> dict[str, str]:
    """Build the additive ``_deprecation`` field for rollback responses.

    This is appended to the otherwise-unchanged successful response payload,
    so callers receive a breadcrumb without breaking existing response shape.
    """
    return {
        "tool": f"mcp__hestai__{tool_short_name}",
        "replacement": f"mcp__hestai-context__{tool_short_name}",
        "reason": (
            "Legacy hestai-mcp tool invoked under rollback flag per ADR-0353. "
            "Migrate to hestai-context-mcp."
        ),
        "rollback_env": f"{LEGACY_ENV_VAR}=1",
    }


def emit_stderr_warning(tool_short_name: str) -> None:
    """Emit the exact-format stderr deprecation line for a rollback invocation."""
    print(
        f"[DEPRECATED] mcp__hestai__{tool_short_name} invoked under " f"{LEGACY_ENV_VAR}=1",
        file=sys.stderr,
    )


def resolve_audit_path(project_root: Path) -> Path:
    """Resolve the canonical audit-log path under a project root.

    Mirrors the precedent set by ``.hestai/state/audit/bypass-log.jsonl``.
    """
    return project_root / ".hestai" / "state" / "audit" / "legacy-tool-invocations.jsonl"


def record_legacy_invocation(
    tool_name: str,
    audit_path: Path,
    working_dir: str,
    caller_session_id: str | None = None,
) -> None:
    """Append a single telemetry record for a rollback-path invocation.

    Schema::

        {
          "timestamp": "<ISO-8601 UTC>",
          "tool": "mcp__hestai__<name>",
          "env": "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1",
          "working_dir": "<cwd>",
          "caller_session_id": "<if available, else null>"
        }

    Failures are intentionally swallowed at the call-site in ``server.call_tool``
    (telemetry must never break the user-visible tool); this function itself
    raises so unit tests can assert behaviour.
    """
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "tool": f"mcp__hestai__{tool_name}",
        "env": f"{LEGACY_ENV_VAR}=1",
        "working_dir": working_dir,
        "caller_session_id": caller_session_id,
    }
    with audit_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
