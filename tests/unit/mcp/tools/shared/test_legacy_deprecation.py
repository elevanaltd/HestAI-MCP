"""Tests for legacy_deprecation shared helper (ADR-0353 / issue #400).

TDD discipline:
1. RED: tests written first, must fail before implementation
2. GREEN: minimal helper to pass
3. REFACTOR: only if tests still green

The helper provides three responsibilities under issue #400:
  (a) is_legacy_enabled() — read HESTAI_MCP_LEGACY_TOOLS_ENABLED
  (b) deprecation_payload(tool_name) — Q2 structured payload (default state)
  (c) record_legacy_invocation(tool_name, audit_path) — Q3 telemetry on rollback
  (d) deprecation_field() — additive `_deprecation` field for rollback responses
  (e) emit_stderr_warning(tool_name) — stderr line for rollback path
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest


@pytest.mark.unit
class TestIsLegacyEnabled:
    """HESTAI_MCP_LEGACY_TOOLS_ENABLED env-var parsing."""

    def test_unset_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import is_legacy_enabled

        monkeypatch.delenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", raising=False)
        assert is_legacy_enabled() is False

    def test_zero_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import is_legacy_enabled

        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "0")
        assert is_legacy_enabled() is False

    def test_empty_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import is_legacy_enabled

        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "")
        assert is_legacy_enabled() is False

    def test_one_returns_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import is_legacy_enabled

        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        assert is_legacy_enabled() is True

    def test_true_returns_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import is_legacy_enabled

        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "true")
        assert is_legacy_enabled() is True

    def test_uppercase_true_returns_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import is_legacy_enabled

        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "TRUE")
        assert is_legacy_enabled() is True


@pytest.mark.unit
class TestDeprecationPayload:
    """Q2 structured payload returned in DEFAULT (deactivated) state."""

    def test_payload_shape_for_clock_in(self) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import deprecation_payload

        payload = deprecation_payload("clock_in")

        assert payload == {
            "error": "DEPRECATED",
            "tool": "mcp__hestai__clock_in",
            "replacement": "mcp__hestai-context__clock_in",
            "reason": "Legacy hestai-mcp tool deactivated per ADR-0353. Use hestai-context-mcp.",
            "rollback": "Set HESTAI_MCP_LEGACY_TOOLS_ENABLED=1 to temporarily restore.",
        }

    def test_payload_shape_for_clock_out(self) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import deprecation_payload

        payload = deprecation_payload("clock_out")
        assert payload["tool"] == "mcp__hestai__clock_out"
        assert payload["replacement"] == "mcp__hestai-context__clock_out"
        assert payload["error"] == "DEPRECATED"

    def test_payload_shape_for_submit_review(self) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import deprecation_payload

        payload = deprecation_payload("submit_review")
        assert payload["tool"] == "mcp__hestai__submit_review"
        assert payload["replacement"] == "mcp__hestai-context__submit_review"


@pytest.mark.unit
class TestRecordLegacyInvocation:
    """Q3.iii: append-only JSONL telemetry on rollback path."""

    def test_appends_record_with_required_schema(self, tmp_path: Path) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import record_legacy_invocation

        audit_path = tmp_path / "legacy-tool-invocations.jsonl"
        record_legacy_invocation(
            tool_name="clock_in",
            audit_path=audit_path,
            working_dir=str(tmp_path),
            caller_session_id="sess-abc",
        )

        assert audit_path.exists()
        lines = audit_path.read_text().strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["tool"] == "mcp__hestai__clock_in"
        assert record["env"] == "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1"
        assert record["working_dir"] == str(tmp_path)
        assert record["caller_session_id"] == "sess-abc"
        # ISO-8601 UTC timestamp parses
        ts = record["timestamp"]
        parsed = datetime.fromisoformat(ts)
        assert parsed.tzinfo is not None

    def test_caller_session_id_defaults_to_null(self, tmp_path: Path) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import record_legacy_invocation

        audit_path = tmp_path / "legacy-tool-invocations.jsonl"
        record_legacy_invocation(
            tool_name="submit_review",
            audit_path=audit_path,
            working_dir=str(tmp_path),
        )

        record = json.loads(audit_path.read_text().strip())
        assert record["caller_session_id"] is None

    def test_appends_not_overwrites(self, tmp_path: Path) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import record_legacy_invocation

        audit_path = tmp_path / "legacy-tool-invocations.jsonl"
        record_legacy_invocation("clock_in", audit_path, str(tmp_path))
        record_legacy_invocation("clock_out", audit_path, str(tmp_path))
        record_legacy_invocation("submit_review", audit_path, str(tmp_path))

        lines = audit_path.read_text().strip().splitlines()
        assert len(lines) == 3
        tools = [json.loads(line)["tool"] for line in lines]
        assert tools == [
            "mcp__hestai__clock_in",
            "mcp__hestai__clock_out",
            "mcp__hestai__submit_review",
        ]

    def test_creates_parent_directory_if_missing(self, tmp_path: Path) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import record_legacy_invocation

        audit_path = tmp_path / "deep" / "nested" / "audit.jsonl"
        record_legacy_invocation("clock_in", audit_path, str(tmp_path))
        assert audit_path.exists()


@pytest.mark.unit
class TestDeprecationField:
    """Q3.ii: additive `_deprecation` field on rollback path."""

    def test_returns_dict_with_expected_keys(self) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import deprecation_field

        field = deprecation_field("clock_in")
        assert field["tool"] == "mcp__hestai__clock_in"
        assert field["replacement"] == "mcp__hestai-context__clock_in"
        assert "ADR-0353" in field["reason"]
        assert field["rollback_env"] == "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1"


@pytest.mark.unit
class TestEmitStderrWarning:
    """Q3.i: stderr line on rollback path with exact format."""

    def test_emits_exact_format_to_stderr(self, capsys: pytest.CaptureFixture[str]) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import emit_stderr_warning

        emit_stderr_warning("clock_in")
        captured = capsys.readouterr()
        assert (
            captured.err.strip()
            == "[DEPRECATED] mcp__hestai__clock_in invoked under HESTAI_MCP_LEGACY_TOOLS_ENABLED=1"
        )

    def test_emit_for_each_tool(self, capsys: pytest.CaptureFixture[str]) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import emit_stderr_warning

        emit_stderr_warning("clock_out")
        emit_stderr_warning("submit_review")
        captured = capsys.readouterr()
        lines = [line for line in captured.err.strip().splitlines() if line]
        assert lines == [
            "[DEPRECATED] mcp__hestai__clock_out invoked under HESTAI_MCP_LEGACY_TOOLS_ENABLED=1",
            "[DEPRECATED] mcp__hestai__submit_review invoked under HESTAI_MCP_LEGACY_TOOLS_ENABLED=1",
        ]


@pytest.mark.unit
class TestAuditPathResolution:
    """Helper for resolving the canonical audit-log path under a project root."""

    def test_resolves_under_project_root(self, tmp_path: Path) -> None:
        from hestai_mcp.modules.tools.shared.legacy_deprecation import resolve_audit_path

        path = resolve_audit_path(tmp_path)
        assert path == tmp_path / ".hestai" / "state" / "audit" / "legacy-tool-invocations.jsonl"
