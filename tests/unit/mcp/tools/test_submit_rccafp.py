"""
Tests for submit_rccafp_record MCP tool.

Covers: valid submission, missing required fields, path validation,
JSONL format, server envelope fields, optional fields, and append behavior.
"""

import json
import uuid
from pathlib import Path

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
