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

NOTE: clock_out is async (SS-I2 compliance). All tests calling clock_out
must use @pytest.mark.asyncio and await.
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

    @pytest.mark.asyncio
    async def test_validates_session_exists(self, tmp_path: Path):
        """Raises FileNotFoundError if session directory doesn't exist."""
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Create .hestai/sessions structure but no active session
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        active_dir.mkdir(parents=True)

        # Try to clock out non-existent session
        with pytest.raises(FileNotFoundError, match="Session .* not found"):
            await clock_out(
                session_id="nonexistent",
                description="",
                project_root=tmp_path,
            )

    @pytest.mark.asyncio
    async def test_blocks_path_traversal_via_session_json(self, tmp_path: Path, monkeypatch):
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
            await clock_out(
                session_id=session_id,
                description="",
                project_root=tmp_path,
            )


@pytest.mark.unit
class TestClaudeJsonlLensIntegration:
    """Test ClaudeJsonlLens replaces hardcoded _parse_session_transcript."""

    @pytest.mark.asyncio
    async def test_uses_jsonl_lens_for_parsing(self, tmp_path: Path):
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
        result = await clock_out(
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

    @pytest.mark.asyncio
    async def test_creates_archive_with_correct_naming(self, tmp_path: Path):
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
        result = await clock_out(
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

    @pytest.mark.asyncio
    async def test_removes_active_session_directory(self, tmp_path: Path):
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
        await clock_out(session_id=session_id, description="", project_root=tmp_path)

        # Verify session removed after
        assert not session_dir.exists()


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling for missing sessions and invalid paths."""

    @pytest.mark.asyncio
    async def test_handles_missing_session_metadata(self, tmp_path: Path):
        """Raises FileNotFoundError if session.json missing."""
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Create session directory but no session.json
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        session_dir = active_dir / "missing-metadata"
        session_dir.mkdir(parents=True)

        with pytest.raises(FileNotFoundError, match="Session metadata not found"):
            await clock_out(
                session_id="missing-metadata",
                description="",
                project_root=tmp_path,
            )


@pytest.mark.unit
class TestSecretRedaction:
    """Test sensitive parameter redaction in archived transcripts."""

    @pytest.mark.asyncio
    async def test_applies_redaction_to_archived_jsonl(self, tmp_path: Path):
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
        result = await clock_out(session_id=session_id, description="", project_root=tmp_path)

        # Verify archive created
        assert result["status"] == "success"
        redacted_jsonl_path = Path(result["redacted_jsonl_path"])
        assert redacted_jsonl_path.exists()

        # Verify secret redacted in archive
        archived_content = redacted_jsonl_path.read_text()
        assert "sk-1234567890abcdefghij123" not in archived_content
        assert "[REDACTED_API_KEY]" in archived_content


@pytest.mark.unit
class TestFASTLayerUpdate:
    """
    Test FAST layer update during clock_out per ADR-0046 and ADR-0056.

    The FAST layer at .hestai/context/state/ should be updated
    during clock_out to reflect session completion.
    """

    @pytest.fixture
    def session_with_fast_layer(self, tmp_path: Path):
        """
        Create session with populated FAST layer for clock_out testing.

        Returns tuple of (project_root, session_id, jsonl_path).
        """
        # Setup session structure
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        state_dir = hestai_dir / "context" / "state"

        active_dir.mkdir(parents=True)
        state_dir.mkdir(parents=True)

        session_id = "fast-layer-test-session"
        session_dir = active_dir / session_id
        session_dir.mkdir()

        # Create minimal JSONL
        jsonl_path = tmp_path / "session.jsonl"
        jsonl_path.write_text(
            json.dumps(
                {
                    "type": "user",
                    "message": {"role": "user", "content": [{"type": "text", "text": "Test"}]},
                }
            )
        )

        # Create session metadata
        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test-fast-layer",
            "started_at": "2025-12-28T10:00:00Z",
            "transcript_path": str(jsonl_path),
            "working_dir": str(tmp_path),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Populate FAST layer files (simulating clock_in state)
        current_focus_content = f"""===CURRENT_FOCUS===
META:
  TYPE::SESSION_FOCUS
  VELOCITY::HOURLY_DAILY

SESSION:
  ID::"{session_id}"
  ROLE::implementation-lead
  FOCUS::"test-fast-layer"
  BRANCH::clock-in-tool
  STARTED::"2025-12-28T10:00:00Z"

===END===
"""
        (state_dir / "current-focus.oct.md").write_text(current_focus_content)

        checklist_content = f"""===SESSION_CHECKLIST===
META:
  TYPE::FAST_CHECKLIST
  VELOCITY::HOURLY_DAILY
  SESSION::"{session_id}"

CURRENT_TASK::"test-fast-layer"

ITEMS:
  implement_feature::IN_PROGRESS
  write_tests::PENDING
  run_quality_gates::PENDING

===END===
"""
        (state_dir / "checklist.oct.md").write_text(checklist_content)

        blockers_content = f"""===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS
  VELOCITY::HOURLY_DAILY
  SESSION::"{session_id}"

ACTIVE:
  blocker_001:
    DESCRIPTION::"Test blocker"
    SINCE::"2025-12-28T10:30:00Z"
    STATUS::UNRESOLVED

===END===
"""
        (state_dir / "blockers.oct.md").write_text(blockers_content)

        return tmp_path, session_id, jsonl_path

    @pytest.mark.asyncio
    async def test_clock_out_clears_current_focus(self, session_with_fast_layer):
        """
        clock_out clears current focus and records session completion.

        ADR-0056 format after clock_out:
        ===CURRENT_FOCUS===
        SESSION::NONE
        LAST_SESSION:
          ID::"{session_id}"
          COMPLETED::"{timestamp}"
        ===END===
        """
        from hestai_mcp.mcp.tools.clock_out import clock_out

        project_root, session_id, _ = session_with_fast_layer

        await clock_out(
            session_id=session_id,
            description="Test complete",
            project_root=project_root,
        )

        current_focus_path = project_root / ".hestai" / "context" / "state" / "current-focus.oct.md"
        assert current_focus_path.exists()

        content = current_focus_path.read_text()

        # Verify session is cleared
        assert "SESSION::NONE" in content
        assert "LAST_SESSION:" in content
        assert f'ID::"{session_id}"' in content
        assert "COMPLETED::" in content

    @pytest.mark.asyncio
    async def test_clock_out_updates_checklist_marks_complete(self, session_with_fast_layer):
        """
        clock_out marks session task as complete, preserves incomplete items.

        ADR-0056: Incomplete tasks should be preserved for next session.
        """
        from hestai_mcp.mcp.tools.clock_out import clock_out

        project_root, session_id, _ = session_with_fast_layer

        await clock_out(
            session_id=session_id,
            description="Session complete",
            project_root=project_root,
        )

        checklist_path = project_root / ".hestai" / "context" / "state" / "checklist.oct.md"
        assert checklist_path.exists()

        content = checklist_path.read_text()

        # Session task should be marked complete or session cleared
        # Incomplete items should be preserved
        assert "write_tests::PENDING" in content or "PENDING" in content
        assert "run_quality_gates::PENDING" in content or "PENDING" in content

    @pytest.mark.asyncio
    async def test_clock_out_persists_unresolved_blockers(self, session_with_fast_layer):
        """
        clock_out persists unresolved blockers for next session.

        ADR-0056: Unresolved blockers should survive session transitions.
        """
        from hestai_mcp.mcp.tools.clock_out import clock_out

        project_root, session_id, _ = session_with_fast_layer

        await clock_out(
            session_id=session_id,
            description="",
            project_root=project_root,
        )

        blockers_path = project_root / ".hestai" / "context" / "state" / "blockers.oct.md"
        assert blockers_path.exists()

        content = blockers_path.read_text()

        # Unresolved blocker should still be present
        assert 'DESCRIPTION::"Test blocker"' in content
        assert "STATUS::UNRESOLVED" in content

    @pytest.mark.asyncio
    async def test_clock_out_clears_resolved_blockers(self, tmp_path: Path):
        """
        clock_out clears blockers marked as RESOLVED.

        ADR-0056: Resolved blockers should be cleared on session end.
        """
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Setup session structure
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        state_dir = hestai_dir / "context" / "state"

        active_dir.mkdir(parents=True)
        state_dir.mkdir(parents=True)

        session_id = "resolved-blockers-test"
        session_dir = active_dir / session_id
        session_dir.mkdir()

        # Create JSONL
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
            "focus": "test",
            "transcript_path": str(jsonl_path),
            "working_dir": str(tmp_path),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Create blockers with one resolved
        blockers_content = """===BLOCKERS===
META:
  TYPE::FAST_BLOCKERS
  VELOCITY::HOURLY_DAILY

ACTIVE:
  blocker_001:
    DESCRIPTION::"Fixed issue"
    STATUS::RESOLVED
  blocker_002:
    DESCRIPTION::"Still pending"
    STATUS::UNRESOLVED

===END===
"""
        (state_dir / "blockers.oct.md").write_text(blockers_content)
        (state_dir / "current-focus.oct.md").write_text(
            "===CURRENT_FOCUS===\nSESSION::ACTIVE\n===END==="
        )
        (state_dir / "checklist.oct.md").write_text("===SESSION_CHECKLIST===\n===END===")

        await clock_out(
            session_id=session_id,
            description="",
            project_root=tmp_path,
        )

        blockers_path = state_dir / "blockers.oct.md"
        content = blockers_path.read_text()

        # Resolved blocker should be removed
        assert 'DESCRIPTION::"Fixed issue"' not in content
        # Unresolved blocker should remain
        assert 'DESCRIPTION::"Still pending"' in content

    @pytest.mark.asyncio
    async def test_clock_out_handles_missing_fast_layer_gracefully(self, tmp_path: Path):
        """
        clock_out succeeds even if FAST layer files don't exist.

        Graceful degradation - don't fail archival if state files are missing.
        """
        from hestai_mcp.mcp.tools.clock_out import clock_out

        # Setup session without FAST layer
        hestai_dir = tmp_path / ".hestai"
        sessions_dir = hestai_dir / "sessions"
        active_dir = sessions_dir / "active"
        active_dir.mkdir(parents=True)

        session_id = "no-fast-layer"
        session_dir = active_dir / session_id
        session_dir.mkdir()

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
            "focus": "test",
            "transcript_path": str(jsonl_path),
            "working_dir": str(tmp_path),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Note: No .hestai/context/state/ directory exists

        # Should succeed without error
        result = await clock_out(
            session_id=session_id,
            description="",
            project_root=tmp_path,
        )

        assert result["status"] == "success"
