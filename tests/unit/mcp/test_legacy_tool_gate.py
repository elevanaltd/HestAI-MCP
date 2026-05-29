"""Tests for legacy-tool deactivation gate at server.call_tool() (issue #400 / ADR-0353).

The gate intercepts mcp__hestai__{clock_in,clock_out,submit_review} calls and:

DEFAULT (HESTAI_MCP_LEGACY_TOOLS_ENABLED unset/0):
  - Returns the Q2 structured deprecation payload
  - Does NOT execute legacy tool logic
  - Does NOT write telemetry
  - Does NOT emit stderr warning

ROLLBACK (HESTAI_MCP_LEGACY_TOOLS_ENABLED=1):
  - Executes legacy logic
  - Appends `_deprecation` field to response payload (additive)
  - Emits stderr deprecation line (exact format)
  - Appends a JSONL telemetry record under .hestai/state/audit/

Tools NOT gated: bind, submit_rccafp_record (these are not in the deprecation set).
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    (project / ".hestai" / "state" / "sessions" / "active").mkdir(parents=True)
    (project / ".hestai" / "state" / "sessions" / "archive").mkdir(parents=True)
    (project / ".hestai" / "state" / "context" / "state").mkdir(parents=True)
    (project / ".hestai" / "state" / "audit").mkdir(parents=True)
    return project


def _patch_audit_path_under(project: Path):
    """Redirect resolve_audit_path so tests don't pollute the real audit log.

    The gate computes the audit path from the working_dir of the call. By
    routing all three tools to a project under tmp_path, the canonical
    .hestai/state/audit/legacy-tool-invocations.jsonl resolves under tmp_path
    automatically — no patching needed when tools accept working_dir.
    """
    return project / ".hestai" / "state" / "audit" / "legacy-tool-invocations.jsonl"


# =============================================================================
# DEFAULT STATE (env-var unset/0)
# =============================================================================


@pytest.mark.unit
class TestDefaultStateClockIn:
    """clock_in returns deprecation payload, does not execute legacy logic."""

    @pytest.mark.asyncio
    async def test_returns_deprecation_payload_without_executing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.delenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", raising=False)
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        with patch.object(server, "clock_in_async", new_callable=AsyncMock) as mock_clock_in:
            result = await call_tool(
                "clock_in",
                {"role": "test-role", "working_dir": str(project), "focus": "f"},
            )

        mock_clock_in.assert_not_called()
        payload = json.loads(result[0].text)
        assert payload == {
            "error": "DEPRECATED",
            "tool": "mcp__hestai__clock_in",
            "replacement": "mcp__hestai-context__clock_in",
            "reason": "Legacy hestai-mcp tool deactivated per ADR-0353. " "Use hestai-context-mcp.",
            "rollback": "Set HESTAI_MCP_LEGACY_TOOLS_ENABLED=1 to temporarily restore.",
        }
        assert capsys.readouterr().err == ""
        audit = _patch_audit_path_under(project)
        assert not audit.exists()


@pytest.mark.unit
class TestDefaultStateClockOut:
    @pytest.mark.asyncio
    async def test_returns_deprecation_payload_without_executing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.delenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", raising=False)
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        with patch.object(server, "clock_out", new_callable=AsyncMock) as mock_clock_out:
            result = await call_tool(
                "clock_out",
                {"session_id": "anything", "working_dir": str(project)},
            )

        mock_clock_out.assert_not_called()
        payload = json.loads(result[0].text)
        assert payload["error"] == "DEPRECATED"
        assert payload["tool"] == "mcp__hestai__clock_out"
        assert capsys.readouterr().err == ""
        assert not _patch_audit_path_under(project).exists()


@pytest.mark.unit
class TestDefaultStateSubmitReview:
    @pytest.mark.asyncio
    async def test_returns_deprecation_payload_without_executing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.delenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", raising=False)
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        with patch.object(server, "submit_review", new_callable=AsyncMock) as mock_sr:
            result = await call_tool(
                "submit_review",
                {
                    "repo": "elevanaltd/test",
                    "pr_number": 1,
                    "role": "implementation-lead",
                    "verdict": "APPROVED",
                    "assessment": "ok",
                    "working_dir": str(project),
                },
            )

        mock_sr.assert_not_called()
        payload = json.loads(result[0].text)
        assert payload["error"] == "DEPRECATED"
        assert payload["tool"] == "mcp__hestai__submit_review"
        assert capsys.readouterr().err == ""
        assert not _patch_audit_path_under(project).exists()


# =============================================================================
# ROLLBACK STATE (env-var=1)
# =============================================================================


@pytest.mark.unit
class TestRollbackStateClockIn:
    @pytest.mark.asyncio
    async def test_executes_legacy_emits_telemetry_stderr_and_field(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        legacy_response = {"session_id": "s-1", "context_paths": []}
        with (
            patch.object(server, "ensure_system_governance", return_value={"status": "ok"}),
            patch.object(server, "clock_in_async", new_callable=AsyncMock) as mock_clock_in,
        ):
            mock_clock_in.return_value = legacy_response
            result = await call_tool(
                "clock_in",
                {"role": "test-role", "working_dir": str(project), "focus": "f"},
            )

        mock_clock_in.assert_called_once()
        payload = json.loads(result[0].text)
        # Original keys preserved
        assert payload["session_id"] == "s-1"
        assert payload["context_paths"] == []
        # Additive `_deprecation` field present
        assert "_deprecation" in payload
        assert payload["_deprecation"]["tool"] == "mcp__hestai__clock_in"
        assert payload["_deprecation"]["replacement"] == "mcp__hestai-context__clock_in"
        # stderr line emitted with exact format
        captured_err = capsys.readouterr().err
        assert (
            "[DEPRECATED] mcp__hestai__clock_in invoked under "
            "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1" in captured_err
        )
        # Telemetry record appended
        audit = _patch_audit_path_under(project)
        assert audit.exists()
        record = json.loads(audit.read_text().strip())
        assert record["tool"] == "mcp__hestai__clock_in"
        assert record["env"] == "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1"
        assert record["working_dir"] == str(project)


@pytest.mark.unit
class TestRollbackStateClockOut:
    @pytest.mark.asyncio
    async def test_executes_legacy_emits_telemetry_stderr_and_field(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        project = _make_project(tmp_path)
        # Seed a minimal session.json so clock_out routing finds it.
        session_id = "s-2"
        session_dir = project / ".hestai" / "state" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "session.json").write_text(
            json.dumps({"session_id": session_id, "role": "r", "working_dir": str(project)})
        )

        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        with patch.object(server, "clock_out", new_callable=AsyncMock) as mock_clock_out:
            mock_clock_out.return_value = {"status": "completed", "session_id": session_id}
            result = await call_tool(
                "clock_out",
                {"session_id": session_id, "working_dir": str(project)},
            )

        mock_clock_out.assert_called_once()
        payload = json.loads(result[0].text)
        assert payload["status"] == "completed"
        assert payload["session_id"] == session_id
        assert "_deprecation" in payload
        assert payload["_deprecation"]["tool"] == "mcp__hestai__clock_out"
        assert (
            "[DEPRECATED] mcp__hestai__clock_out invoked under "
            "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1" in capsys.readouterr().err
        )
        # clock_out telemetry derives from the validated session working_dir.
        expected_working_dir = str(server.validate_working_dir(str(project)))
        audit = _patch_audit_path_under(server.validate_working_dir(str(project)))
        assert audit.exists()
        record = json.loads(audit.read_text().strip())
        assert record["tool"] == "mcp__hestai__clock_out"
        assert record["env"] == "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1"
        assert record["working_dir"] == expected_working_dir
        assert "timestamp" in record
        assert "caller_session_id" in record  # may be None
        assert record["caller_session_id"] is None


@pytest.mark.unit
class TestRollbackStateSubmitReview:
    @pytest.mark.asyncio
    async def test_executes_legacy_emits_telemetry_stderr_and_field(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        with patch.object(server, "submit_review", new_callable=AsyncMock) as mock_sr:
            mock_sr.return_value = {"posted": True, "comment_id": 42}
            result = await call_tool(
                "submit_review",
                {
                    "repo": "elevanaltd/test",
                    "pr_number": 1,
                    "role": "implementation-lead",
                    "verdict": "APPROVED",
                    "assessment": "ok",
                    "working_dir": str(project),
                },
            )

        mock_sr.assert_called_once()
        payload = json.loads(result[0].text)
        assert payload["posted"] is True
        assert payload["comment_id"] == 42
        assert "_deprecation" in payload
        assert payload["_deprecation"]["tool"] == "mcp__hestai__submit_review"
        assert (
            "[DEPRECATED] mcp__hestai__submit_review invoked under "
            "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1" in capsys.readouterr().err
        )
        # submit_review telemetry derives from the validated working_dir.
        expected_working_dir = str(server.validate_working_dir(str(project)))
        audit = _patch_audit_path_under(server.validate_working_dir(str(project)))
        assert audit.exists()
        record = json.loads(audit.read_text().strip())
        assert record["tool"] == "mcp__hestai__submit_review"
        assert record["env"] == "HESTAI_MCP_LEGACY_TOOLS_ENABLED=1"
        assert record["working_dir"] == expected_working_dir
        assert "timestamp" in record
        assert "caller_session_id" in record  # may be None
        assert record["caller_session_id"] is None


# =============================================================================
# NON-DEACTIVATED TOOLS PASS THROUGH UNCHANGED
# =============================================================================


@pytest.mark.unit
class TestBindNotGated:
    @pytest.mark.asyncio
    async def test_bind_passes_through_default_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", raising=False)
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        with (
            patch.object(server, "ensure_system_governance", return_value={"status": "ok"}),
            patch.object(server, "bind") as mock_bind,
        ):
            mock_bind.return_value = {"status": "bound"}
            result = await call_tool(
                "bind",
                {"role": "implementation-lead", "working_dir": str(project)},
            )

        mock_bind.assert_called_once()
        payload = json.loads(result[0].text)
        assert payload["status"] == "bound"
        assert "_deprecation" not in payload
        assert payload.get("error") != "DEPRECATED"


@pytest.mark.unit
class TestSubmitRccafpNotGated:
    @pytest.mark.asyncio
    async def test_submit_rccafp_record_passes_through_default_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", raising=False)
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        with patch.object(server, "submit_rccafp_record", new_callable=AsyncMock) as mock_rr:
            mock_rr.return_value = {"record_id": "rec-1"}
            result = await call_tool(
                "submit_rccafp_record",
                {
                    "working_dir": str(project),
                    "context_summary": "x",
                    "root_cause_analysis": "y",
                    "fix_attempt_1": "z",
                    "escalation_required": False,
                    "future_proofing_rule": "rule",
                },
            )

        mock_rr.assert_called_once()
        payload = json.loads(result[0].text)
        assert payload["record_id"] == "rec-1"
        assert "_deprecation" not in payload
        assert payload.get("error") != "DEPRECATED"


# =============================================================================
# SECURITY: telemetry write path MUST derive from the VALIDATED working_dir
# (cubic-dev-ai finding, PR #401) — never from the raw, attacker-controlled
# argument. validate_working_dir is fail-closed (rejects "..", non-existent,
# non-dir). The rollback telemetry path must not bypass it.
# =============================================================================


@pytest.mark.unit
class TestTelemetryUsesValidatedWorkingDirClockIn:
    @pytest.mark.asyncio
    async def test_path_traversal_working_dir_is_rejected_before_telemetry(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A working_dir containing '..' must be rejected (fail-closed) and write no telemetry."""
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        malicious = f"{project}/../evil"
        with (
            patch.object(server, "ensure_system_governance", return_value={"status": "ok"}),
            patch.object(server, "clock_in_async", new_callable=AsyncMock) as mock_clock_in,
        ):
            mock_clock_in.return_value = {"session_id": "s-1", "context_paths": []}
            with pytest.raises(ValueError, match="[Pp]ath traversal"):
                await call_tool(
                    "clock_in",
                    {"role": "r", "working_dir": malicious, "focus": "f"},
                )

        # Fail-closed: legacy logic never ran, and nothing was written anywhere.
        mock_clock_in.assert_not_called()
        assert not _patch_audit_path_under(project).exists()

    @pytest.mark.asyncio
    async def test_telemetry_path_derives_from_validated_path_not_raw_argument(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Behavioural: the WRITTEN telemetry record derives from the validated
        (normalized) working_dir, not the raw unnormalized argument.

        Passing a working_dir with a trailing slash must still resolve the real
        jsonl write under the canonical validated path. No mocking of the
        recorder — we assert the actual written record and its location.
        """
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        validated = server.validate_working_dir(str(project))
        raw_arg = f"{project}/"  # unnormalized (trailing slash)

        with (
            patch.object(server, "ensure_system_governance", return_value={"status": "ok"}),
            patch.object(server, "clock_in_async", new_callable=AsyncMock) as mock_clock_in,
        ):
            mock_clock_in.return_value = {"session_id": "s-1", "context_paths": []}
            await call_tool(
                "clock_in",
                {"role": "r", "working_dir": raw_arg, "focus": "f"},
            )

        # Real write landed under the validated (normalized) path, not the raw arg.
        audit = _patch_audit_path_under(validated)
        assert audit.exists()
        record = json.loads(audit.read_text().strip())
        assert record["tool"] == "mcp__hestai__clock_in"
        assert record["working_dir"] == str(validated)
        # The unnormalized raw argument is explicitly NOT what was written.
        assert record["working_dir"] != raw_arg


@pytest.mark.unit
class TestTelemetryUsesValidatedWorkingDirSubmitReview:
    @pytest.mark.asyncio
    async def test_invalid_working_dir_skips_telemetry_without_breaking_review(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """CE finding (PR #401): an invalid telemetry-only working_dir must NOT crash a
        completed submit_review. Validation still runs (security preserved: nothing is
        written to the attacker-controlled path), but failure is isolated — the review
        returns normally and a warning is logged.
        """
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        malicious = f"{project}/../evil"
        with (
            patch.object(server, "submit_review", new_callable=AsyncMock) as mock_sr,
            caplog.at_level("WARNING", logger="hestai_mcp.mcp.server"),
        ):
            mock_sr.return_value = {"posted": True, "comment_id": 7}
            result = await call_tool(
                "submit_review",
                {
                    "repo": "elevanaltd/test",
                    "pr_number": 1,
                    "role": "implementation-lead",
                    "verdict": "APPROVED",
                    "assessment": "ok",
                    "working_dir": malicious,
                },
            )

        # The completed review returns normally — no exception raised.
        payload = json.loads(result[0].text)
        assert payload["posted"] is True
        assert payload["comment_id"] == 7
        assert payload["_deprecation"]["tool"] == "mcp__hestai__submit_review"
        # Security preserved: telemetry never written to the attacker-controlled path.
        assert not _patch_audit_path_under(project).exists()
        evil_audit = (
            project.parent
            / "evil"
            / ".hestai"
            / "state"
            / "audit"
            / "legacy-tool-invocations.jsonl"
        )
        assert not evil_audit.exists()
        # Telemetry was skipped, with a warning — not crashed.
        assert any(
            "Failed to record legacy-tool telemetry for submit_review" in rec.message
            for rec in caplog.records
        )

    @pytest.mark.asyncio
    async def test_valid_working_dir_writes_telemetry_under_validated_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A valid (even unnormalized) working_dir resolves telemetry under the validated path."""
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        project = _make_project(tmp_path)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        validated = server.validate_working_dir(str(project))
        raw_arg = f"{project}/"  # unnormalized (trailing slash)

        with patch.object(server, "submit_review", new_callable=AsyncMock) as mock_sr:
            mock_sr.return_value = {"posted": True}
            await call_tool(
                "submit_review",
                {
                    "repo": "elevanaltd/test",
                    "pr_number": 1,
                    "role": "implementation-lead",
                    "verdict": "APPROVED",
                    "assessment": "ok",
                    "working_dir": raw_arg,
                },
            )

        audit = _patch_audit_path_under(validated)
        assert audit.exists()
        record = json.loads(audit.read_text().strip())
        assert record["tool"] == "mcp__hestai__submit_review"
        assert record["working_dir"] == str(validated)

    @pytest.mark.asyncio
    async def test_submit_review_without_working_dir_uses_trusted_cwd(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When no working_dir is supplied, submit_review falls back to the server's own cwd.

        submit_review has no project-root semantics; the server cwd is trusted
        (not attacker-controlled), so telemetry resolves there.
        """
        monkeypatch.setenv("HESTAI_MCP_LEGACY_TOOLS_ENABLED", "1")
        project = _make_project(tmp_path)
        monkeypatch.chdir(project)
        from hestai_mcp.mcp import server
        from hestai_mcp.mcp.server import call_tool

        with patch.object(server, "submit_review", new_callable=AsyncMock) as mock_sr:
            mock_sr.return_value = {"posted": True}
            await call_tool(
                "submit_review",
                {
                    "repo": "elevanaltd/test",
                    "pr_number": 1,
                    "role": "implementation-lead",
                    "verdict": "APPROVED",
                    "assessment": "ok",
                },
            )

        audit = _patch_audit_path_under(project.resolve())
        assert audit.exists()
        record = json.loads(audit.read_text().strip())
        assert record["tool"] == "mcp__hestai__submit_review"
