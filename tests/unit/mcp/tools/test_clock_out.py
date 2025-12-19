"""
Tests for ClockOut MCP Tool - Session archival and transcript extraction.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase)
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

Test Coverage:
- Session validation (path traversal prevention)
- ClaudeJsonlLens integration (replaces hardcoded parser)
- Archive creation (JSONL preservation)
- Session cleanup (remove active session)
- Error handling (missing session, invalid paths)
- Secret redaction (security validation)
"""

import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def set_claude_transcript_dir_for_tests(tmp_path, monkeypatch):
    """
    Auto-fixture: Set CLAUDE_TRANSCRIPT_DIR to tmp_path for all tests.

    This allows TranscriptPathResolver to accept test paths in tmp_path
    without triggering path traversal blocking (which is correct security behavior).
    """
    monkeypatch.setenv("CLAUDE_TRANSCRIPT_DIR", str(tmp_path.parent))
    yield


@pytest.mark.unit
class TestSessionValidation:
    """Test session ID validation and path traversal prevention."""

    def test_validates_session_id_format(self):
        """Rejects session IDs with path traversal characters."""
        from hestai_mcp.mcp.tools.clock_out import validate_session_id

        # Valid session IDs
        assert validate_session_id("abc123") == "abc123"
        assert validate_session_id("test-session-1") == "test-session-1"

        # Invalid session IDs (path traversal)
        with pytest.raises(ValueError, match="path separators not allowed"):
            validate_session_id("../etc/passwd")

        with pytest.raises(ValueError, match="path separators not allowed"):
            validate_session_id("test/session")

        with pytest.raises(ValueError, match="path separators not allowed"):
            validate_session_id("test\\session")

        # Empty session ID
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_session_id("")

    def test_validates_session_exists(self, tmp_path: Path):
        """Raises FileNotFoundError if session directory doesn't exist."""
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Create .hestai/sessions structure but no active session
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        active_dir.mkdir(parents=True)

        # Try to clock out non-existent session
        with pytest.raises(FileNotFoundError, match="Session .* not found"):
            clock_out(
                session_id="nonexistent",
                description="",
                project_root=tmp_path,
            )

    def test_blocks_path_traversal_via_session_json(self, tmp_path: Path, monkeypatch):
        """
        SECURITY TEST: Blocks path traversal attempts via transcript_path in session.json.

        TranscriptPathResolver must be enforced to prevent malicious transcript_path
        values from accessing files outside allowed sandbox.
        """
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Remove CLAUDE_TRANSCRIPT_DIR to test default sandbox behavior
        monkeypatch.delenv("CLAUDE_TRANSCRIPT_DIR", raising=False)

        # Setup session structure
        session_id = "malicious-test"
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        session_dir = active_dir / session_id
        session_dir.mkdir(parents=True)

        # Create malicious session.json attempting path traversal
        session_data = {
            "session_id": session_id,
            "transcript_path": "/etc/passwd",  # ATTACK: Outside sandbox
            "role": "test",
            "model": "test",
            "focus": "test",
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Execute clock_out - should BLOCK via TranscriptPathResolver
        with pytest.raises(ValueError, match="Path traversal"):
            clock_out(
                session_id=session_id,
                description="",
                project_root=tmp_path,
            )


@pytest.mark.unit
class TestClaudeJsonlLensIntegration:
    """Test ClaudeJsonlLens replaces hardcoded _parse_session_transcript."""

    def test_uses_jsonl_lens_for_parsing(self, tmp_path: Path):
        """Verifies ClaudeJsonlLens is used instead of custom parser."""
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Setup session structure
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        archive_dir = sessions_dir / "archive"
        active_dir.mkdir(parents=True)

        session_id = "test-session"
        session_dir = active_dir / session_id

        # Create session metadata
        session_dir.mkdir()
        session_file = session_dir / "session.json"

        # Create mock JSONL transcript
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_content = [
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "Hello"}],
                    },
                }
            ),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "Hi there"}],
                        "model": "claude-opus-4-5-20251101",
                    },
                }
            ),
        ]
        jsonl_path.write_text("\n".join(jsonl_content))

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "testing",
            "started_at": "2025-12-16T10:00:00",
            "model": "claude-opus-4-5-20251101",
            "transcript_path": str(jsonl_path),
            "working_dir": str(tmp_path),
        }
        session_file.write_text(json.dumps(session_data))

        # Execute clock_out
        result = clock_out(
            session_id=session_id,
            description="Test session",
            project_root=tmp_path,
        )

        # Verify archive was created
        assert archive_dir.exists()
        archive_files = list(archive_dir.glob("*-redacted.jsonl"))
        assert len(archive_files) == 1

        # Verify ClaudeJsonlLens could parse it (implicit through successful completion)
        assert result["status"] == "success"
        assert result["message_count"] == 2  # UserMessage + AssistantMessage


@pytest.mark.unit
class TestArchiveCreation:
    """Test archive file creation and naming."""

    def test_creates_archive_with_correct_naming(self, tmp_path: Path):
        """Archive filename follows {timestamp}-{focus}-{session_id}-raw.jsonl pattern."""
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Setup minimal session structure
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        active_dir.mkdir(parents=True)

        session_id = "abc123"
        session_dir = active_dir / session_id
        session_dir.mkdir()

        # Create minimal JSONL
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "Test"}],
                    },
                }
            )
        )

        session_data = {
            "session_id": session_id,
            "role": "test-role",
            "focus": "unit-testing",
            "started_at": "2025-12-16T10:00:00",
            "transcript_path": str(jsonl_path),
            "working_dir": str(tmp_path),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Execute
        result = clock_out(
            session_id=session_id,
            description="",
            project_root=tmp_path,
        )

        # Verify naming pattern
        archive_dir = sessions_dir / "archive"
        redacted_files = list(archive_dir.glob("*-unit-testing-abc123-redacted.jsonl"))
        assert len(redacted_files) == 1

        # Verify archive path in response
        assert "redacted_jsonl_path" in result
        assert Path(result["redacted_jsonl_path"]).name.endswith("-redacted.jsonl")


@pytest.mark.unit
class TestSessionCleanup:
    """Test active session removal after archival."""

    def test_removes_active_session_directory(self, tmp_path: Path):
        """Active session directory deleted after successful archive."""
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Setup session
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        active_dir.mkdir(parents=True)

        session_id = "cleanup-test"
        session_dir = active_dir / session_id
        session_dir.mkdir()

        # Minimal JSONL
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "user",
                    "message": {"role": "user", "content": [{"type": "text", "text": "X"}]},
                }
            )
        )

        session_data = {
            "session_id": session_id,
            "role": "test",
            "focus": "cleanup",
            "transcript_path": str(jsonl_path),
            "working_dir": str(tmp_path),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Verify session exists before
        assert session_dir.exists()

        # Execute
        clock_out(session_id=session_id, description="", project_root=tmp_path)

        # Verify session removed after
        assert not session_dir.exists()


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling for missing sessions and invalid paths."""

    def test_handles_missing_session_metadata(self, tmp_path: Path):
        """Raises FileNotFoundError if session.json missing."""
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Create session directory but no session.json
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        session_dir = active_dir / "missing-metadata"
        session_dir.mkdir(parents=True)

        with pytest.raises(FileNotFoundError, match="Session metadata not found"):
            clock_out(
                session_id="missing-metadata",
                description="",
                project_root=tmp_path,
            )


@pytest.mark.unit
class TestSecretRedaction:
    """Test sensitive parameter redaction in archived transcripts."""

    def test_applies_redaction_to_archived_jsonl(self, tmp_path: Path):
        """Verifies RedactionEngine applied to archived JSONL files."""
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Setup session with secret in transcript
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        active_dir.mkdir(parents=True)

        session_id = "redaction-test"
        session_dir = active_dir / session_id

        # Create JSONL with API key (realistic 20+ char key)
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_content = json.dumps(
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "Using key sk-1234567890abcdefghij123"}],
                },
            }
        )
        jsonl_path.write_text(jsonl_content)

        session_dir.mkdir()
        session_data = {
            "session_id": session_id,
            "role": "test",
            "focus": "security",
            "transcript_path": str(jsonl_path),
            "working_dir": str(tmp_path),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Execute clock_out
        result = clock_out(session_id=session_id, description="", project_root=tmp_path)

        # Verify archive created
        assert result["status"] == "success"
        redacted_jsonl_path = Path(result["redacted_jsonl_path"])
        assert redacted_jsonl_path.exists()

        # Verify secret redacted in archive
        archived_content = redacted_jsonl_path.read_text()
        assert "sk-1234567890abcdefghij123" not in archived_content
        assert "[REDACTED_API_KEY]" in archived_content
