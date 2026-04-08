"""
Tests for submit_rccafp_record MCP tool.

Covers: valid submission, missing required fields, path validation,
JSONL format, server envelope fields, optional fields, append behavior,
project identity validation, symlink escape prevention, filesystem error
handling, and short write detection.
"""

import json
import os
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def project_root(tmp_path: Path) -> Path:
    """Create a minimal project root with .git marker and .hestai/state/."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".hestai" / "state").mkdir(parents=True)
    return tmp_path


@pytest.fixture()
def valid_args(project_root: Path) -> dict:
    """Return a minimal valid argument dict for submit_rccafp_record."""
    return {
        "working_dir": str(project_root),
        "context_summary": "Implementing pagination for the users endpoint",
        "root_cause_analysis": "Off-by-one in cursor-based pagination query",
        "fix_attempt_1": "Adjusted LIMIT clause — still fails on empty result set",
        "escalation_required": False,
        "future_proofing_rule": "Add boundary tests for empty, single, and full-page result sets",
    }


# ---------------------------------------------------------------------------
# Tests — Valid Submission
# ---------------------------------------------------------------------------
class TestValidSubmission:
    """Tests for successful RCCAFP record submission."""

    @pytest.mark.smoke
    @pytest.mark.unit
    @pytest.mark.behavior
    async def test_returns_success_with_record_id(self, valid_args: dict) -> None:
        """A valid submission returns success=True and a record_id."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        result = await submit_rccafp_record(**valid_args)

        assert result["success"] is True
        assert result["record_id"].startswith("rccafp-")
        # record_id should contain a valid UUID after the prefix
        uuid_part = result["record_id"].removeprefix("rccafp-")
        uuid.UUID(uuid_part)  # raises if invalid

    @pytest.mark.unit
    async def test_writes_jsonl_to_error_metrics(
        self, valid_args: dict, project_root: Path
    ) -> None:
        """Submission appends a valid JSON line to error-metrics.jsonl."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        result = await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        assert metrics_file.exists()

        lines = metrics_file.read_text().strip().split("\n")
        assert len(lines) == 1

        record = json.loads(lines[0])
        assert record["record_id"] == result["record_id"]

    @pytest.mark.unit
    async def test_envelope_fields_present(self, valid_args: dict, project_root: Path) -> None:
        """Server envelope has record_id, timestamp, session_id, agent_role."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        assert "record_id" in record
        assert "timestamp" in record
        assert "session_id" in record
        assert "agent_role" in record

    @pytest.mark.unit
    async def test_input_fields_preserved_in_record(
        self, valid_args: dict, project_root: Path
    ) -> None:
        """All input fields are preserved in the JSONL record."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        assert record["working_dir"] == str(project_root)
        assert record["context_summary"] == valid_args["context_summary"]
        assert record["root_cause_analysis"] == valid_args["root_cause_analysis"]
        assert record["fix_attempt_1"] == valid_args["fix_attempt_1"]
        assert record["fix_attempt_2"] is None
        assert record["escalation_required"] is False
        assert record["future_proofing_rule"] == valid_args["future_proofing_rule"]

    @pytest.mark.unit
    async def test_optional_fix_attempt_2_included(
        self, valid_args: dict, project_root: Path
    ) -> None:
        """fix_attempt_2 is stored when provided."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        valid_args["fix_attempt_2"] = "Added null-check before cursor parse — fixes empty set"
        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        assert record["fix_attempt_2"] == valid_args["fix_attempt_2"]

    @pytest.mark.unit
    async def test_timestamp_is_iso8601(self, valid_args: dict, project_root: Path) -> None:
        """Timestamp in the record is ISO-8601 format."""
        from datetime import datetime

        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        # Should parse without error
        datetime.fromisoformat(record["timestamp"])

    @pytest.mark.unit
    async def test_multiple_submissions_append(self, valid_args: dict, project_root: Path) -> None:
        """Multiple submissions append to the same JSONL file (not overwrite)."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        r1 = await submit_rccafp_record(**valid_args)
        r2 = await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        lines = metrics_file.read_text().strip().split("\n")
        assert len(lines) == 2

        record1 = json.loads(lines[0])
        record2 = json.loads(lines[1])
        assert record1["record_id"] == r1["record_id"]
        assert record2["record_id"] == r2["record_id"]
        assert record1["record_id"] != record2["record_id"]


# ---------------------------------------------------------------------------
# Tests — Missing Required Fields
# ---------------------------------------------------------------------------
class TestMissingRequiredFields:
    """Tests for missing required field validation."""

    @pytest.mark.unit
    async def test_missing_context_summary(self, valid_args: dict) -> None:
        """Missing context_summary returns validation error."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        valid_args["context_summary"] = ""
        result = await submit_rccafp_record(**valid_args)
        assert result["success"] is False
        assert "context_summary" in result["error"]

    @pytest.mark.unit
    async def test_missing_root_cause_analysis(self, valid_args: dict) -> None:
        """Missing root_cause_analysis returns validation error."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        valid_args["root_cause_analysis"] = ""
        result = await submit_rccafp_record(**valid_args)
        assert result["success"] is False
        assert "root_cause_analysis" in result["error"]

    @pytest.mark.unit
    async def test_missing_fix_attempt_1(self, valid_args: dict) -> None:
        """Missing fix_attempt_1 returns validation error."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        valid_args["fix_attempt_1"] = ""
        result = await submit_rccafp_record(**valid_args)
        assert result["success"] is False
        assert "fix_attempt_1" in result["error"]

    @pytest.mark.unit
    async def test_missing_future_proofing_rule(self, valid_args: dict) -> None:
        """Missing future_proofing_rule returns validation error."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        valid_args["future_proofing_rule"] = ""
        result = await submit_rccafp_record(**valid_args)
        assert result["success"] is False
        assert "future_proofing_rule" in result["error"]

    @pytest.mark.unit
    async def test_whitespace_only_context_summary(self, valid_args: dict) -> None:
        """Whitespace-only context_summary returns validation error."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        valid_args["context_summary"] = "   \t\n  "
        result = await submit_rccafp_record(**valid_args)
        assert result["success"] is False


# ---------------------------------------------------------------------------
# Tests — Path Validation
# ---------------------------------------------------------------------------
class TestPathValidation:
    """Tests for working_dir path validation and security."""

    @pytest.mark.unit
    async def test_nonexistent_working_dir(self, tmp_path: Path) -> None:
        """Non-existent working_dir returns error."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        result = await submit_rccafp_record(
            working_dir=str(tmp_path / "nonexistent"),
            context_summary="test",
            root_cause_analysis="test",
            fix_attempt_1="test",
            escalation_required=False,
            future_proofing_rule="test",
        )
        assert result["success"] is False

    @pytest.mark.unit
    async def test_path_traversal_rejected(self, project_root: Path) -> None:
        """Path with .. traversal is rejected."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        result = await submit_rccafp_record(
            working_dir=str(project_root) + "/../../../etc",
            context_summary="test",
            root_cause_analysis="test",
            fix_attempt_1="test",
            escalation_required=False,
            future_proofing_rule="test",
        )
        assert result["success"] is False

    @pytest.mark.unit
    async def test_creates_state_directory_if_missing(self, tmp_path: Path) -> None:
        """If .hestai/state/ does not exist, it is created."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        (tmp_path / ".git").mkdir()
        # .hestai/state/ does NOT exist yet

        result = await submit_rccafp_record(
            working_dir=str(tmp_path),
            context_summary="test",
            root_cause_analysis="test",
            fix_attempt_1="test",
            escalation_required=False,
            future_proofing_rule="test",
        )
        assert result["success"] is True
        assert (tmp_path / ".hestai" / "state" / "error-metrics.jsonl").exists()

    @pytest.mark.unit
    async def test_working_dir_not_a_directory(self, tmp_path: Path) -> None:
        """working_dir pointing to a file returns error."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        file_path = tmp_path / "somefile.txt"
        file_path.write_text("not a dir")

        result = await submit_rccafp_record(
            working_dir=str(file_path),
            context_summary="test",
            root_cause_analysis="test",
            fix_attempt_1="test",
            escalation_required=False,
            future_proofing_rule="test",
        )
        assert result["success"] is False


# ---------------------------------------------------------------------------
# Tests — JSONL Record Format
# ---------------------------------------------------------------------------
class TestJsonlFormat:
    """Tests for JSONL record format compliance."""

    @pytest.mark.unit
    async def test_each_line_is_valid_json(self, valid_args: dict, project_root: Path) -> None:
        """Each line in the JSONL file is valid JSON."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        await submit_rccafp_record(**valid_args)
        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        for line in metrics_file.read_text().strip().split("\n"):
            json.loads(line)  # raises if not valid JSON

    @pytest.mark.unit
    async def test_record_id_format(self, valid_args: dict, project_root: Path) -> None:
        """record_id follows rccafp-{uuid4} format."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        assert record["record_id"].startswith("rccafp-")
        uuid_str = record["record_id"].removeprefix("rccafp-")
        parsed = uuid.UUID(uuid_str)
        assert parsed.version == 4

    @pytest.mark.unit
    async def test_escalation_required_is_boolean(
        self, valid_args: dict, project_root: Path
    ) -> None:
        """escalation_required is a boolean in the record."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        valid_args["escalation_required"] = True
        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        assert record["escalation_required"] is True
        assert isinstance(record["escalation_required"], bool)


# ---------------------------------------------------------------------------
# Tests — Session and Role Detection
# ---------------------------------------------------------------------------
class TestSessionAndRoleDetection:
    """Tests for optional session_id and agent_role detection."""

    @pytest.mark.unit
    async def test_session_id_null_when_no_active_session(
        self, valid_args: dict, project_root: Path
    ) -> None:
        """session_id is null when no active session directory exists."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        assert record["session_id"] is None

    @pytest.mark.unit
    async def test_agent_role_null_when_no_active_session(
        self, valid_args: dict, project_root: Path
    ) -> None:
        """agent_role is null when no active session directory exists."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        assert record["agent_role"] is None

    @pytest.mark.unit
    async def test_detects_active_session(self, valid_args: dict, project_root: Path) -> None:
        """session_id and agent_role are populated from active session."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        # Create an active session
        session_id = "test-session-123"
        session_dir = project_root / ".hestai" / "state" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        session_data = {"session_id": session_id, "role": "implementation-lead"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        await submit_rccafp_record(**valid_args)

        metrics_file = project_root / ".hestai" / "state" / "error-metrics.jsonl"
        record = json.loads(metrics_file.read_text().strip())

        assert record["session_id"] == session_id
        assert record["agent_role"] == "implementation-lead"


# ---------------------------------------------------------------------------
# Tests — Project Identity Validation (regression: trusted-root)
# ---------------------------------------------------------------------------
class TestProjectIdentityValidation:
    """Tests that non-project directories are rejected."""

    @pytest.mark.unit
    async def test_plain_directory_without_git_or_hestai_rejected(self, tmp_path: Path) -> None:
        """A plain directory without .git or .hestai is rejected."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        # tmp_path has no .git or .hestai markers
        result = await submit_rccafp_record(
            working_dir=str(tmp_path),
            context_summary="test",
            root_cause_analysis="test",
            fix_attempt_1="test",
            escalation_required=False,
            future_proofing_rule="test",
        )
        assert result["success"] is False
        assert "not a project root" in result["error"]

    @pytest.mark.unit
    async def test_directory_with_only_hestai_accepted(self, tmp_path: Path) -> None:
        """A directory with .hestai (but no .git) is accepted."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        (tmp_path / ".hestai").mkdir()

        result = await submit_rccafp_record(
            working_dir=str(tmp_path),
            context_summary="test",
            root_cause_analysis="test",
            fix_attempt_1="test",
            escalation_required=False,
            future_proofing_rule="test",
        )
        assert result["success"] is True


# ---------------------------------------------------------------------------
# Tests — Symlink Escape Prevention (regression: symlink vectors)
# ---------------------------------------------------------------------------
class TestSymlinkEscapePrevention:
    """Tests that symlink escape vectors in write targets are rejected."""

    @pytest.mark.unit
    async def test_symlinked_state_dir_rejected(self, tmp_path: Path) -> None:
        """Symlinked .hestai/state/ pointing outside project root is rejected."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()

        # Create an external target
        external = tmp_path / "external_state"
        external.mkdir()

        # Create .hestai/ as real dir but state/ as symlink to external
        hestai = project / ".hestai"
        hestai.mkdir()
        (hestai / "state").symlink_to(external)

        result = await submit_rccafp_record(
            working_dir=str(project),
            context_summary="test",
            root_cause_analysis="test",
            fix_attempt_1="test",
            escalation_required=False,
            future_proofing_rule="test",
        )
        assert result["success"] is False
        assert "symlink" in result["error"].lower() or "outside project root" in result["error"]

    @pytest.mark.unit
    async def test_symlinked_metrics_file_rejected(self, tmp_path: Path) -> None:
        """Symlinked error-metrics.jsonl is rejected."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        state_dir = project / ".hestai" / "state"
        state_dir.mkdir(parents=True)

        # Create a symlink for the metrics file
        external_file = tmp_path / "external_metrics.jsonl"
        external_file.write_text("")
        (state_dir / "error-metrics.jsonl").symlink_to(external_file)

        result = await submit_rccafp_record(
            working_dir=str(project),
            context_summary="test",
            root_cause_analysis="test",
            fix_attempt_1="test",
            escalation_required=False,
            future_proofing_rule="test",
        )
        assert result["success"] is False
        assert "symlink" in result["error"]


# ---------------------------------------------------------------------------
# Tests — Filesystem Error Handling (regression: OSError)
# ---------------------------------------------------------------------------
class TestFilesystemErrorHandling:
    """Tests that OSError during writes returns structured error, not exception."""

    @pytest.mark.unit
    async def test_oserror_on_mkdir_returns_structured_error(self, project_root: Path) -> None:
        """OSError during mkdir returns structured error response."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        with patch("pathlib.Path.mkdir", side_effect=OSError("Read-only file system")):
            result = await submit_rccafp_record(
                working_dir=str(project_root),
                context_summary="test",
                root_cause_analysis="test",
                fix_attempt_1="test",
                escalation_required=False,
                future_proofing_rule="test",
            )
        assert result["success"] is False
        assert "Failed to write RCCAFP record" in result["error"]

    @pytest.mark.unit
    async def test_oserror_on_os_open_returns_structured_error(self, project_root: Path) -> None:
        """OSError during os.open returns structured error response."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        with patch("os.open", side_effect=OSError("Permission denied")):
            result = await submit_rccafp_record(
                working_dir=str(project_root),
                context_summary="test",
                root_cause_analysis="test",
                fix_attempt_1="test",
                escalation_required=False,
                future_proofing_rule="test",
            )
        assert result["success"] is False
        assert "Failed to write RCCAFP record" in result["error"]

    @pytest.mark.unit
    async def test_oserror_on_os_write_returns_structured_error(self, project_root: Path) -> None:
        """OSError during os.write returns structured error response."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        real_open = os.open

        def mock_open_then_fail_write(*args, **kwargs):
            return real_open(*args, **kwargs)

        with patch("os.write", side_effect=OSError("Disk full")):
            result = await submit_rccafp_record(
                working_dir=str(project_root),
                context_summary="test",
                root_cause_analysis="test",
                fix_attempt_1="test",
                escalation_required=False,
                future_proofing_rule="test",
            )
        assert result["success"] is False
        assert "Failed to write RCCAFP record" in result["error"]


# ---------------------------------------------------------------------------
# Tests — Short Write Detection (regression: partial writes)
# ---------------------------------------------------------------------------
class TestShortWriteDetection:
    """Tests that short writes are detected and reported."""

    @pytest.mark.unit
    async def test_short_write_returns_error(self, project_root: Path) -> None:
        """Short write (fewer bytes than expected) returns structured error."""
        from hestai_mcp.modules.tools.submit_rccafp import submit_rccafp_record

        # Mock os.write to return fewer bytes than requested
        with patch("os.write", return_value=5):
            result = await submit_rccafp_record(
                working_dir=str(project_root),
                context_summary="test",
                root_cause_analysis="test",
                fix_attempt_1="test",
                escalation_required=False,
                future_proofing_rule="test",
            )
        assert result["success"] is False
        assert "short write" in result["error"]
