"""Tests for pending session helpers (staged handshake lifecycle)."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest


@pytest.mark.unit
class TestPendingSessionHelpers:
    def test_create_pending_handshake_writes_handshake_json(self, tmp_path: Path) -> None:
        from hestai_mcp.mcp.tools.shared.pending_sessions import create_pending_handshake

        working_dir = tmp_path / "project"
        working_dir.mkdir()

        token = "abc-123"
        session_dir = create_pending_handshake(
            working_dir=working_dir,
            token=token,
            handshake={"role": "implementation-lead", "mode": "full"},
        )

        assert session_dir == working_dir / ".hestai" / "sessions" / "pending" / token
        handshake_path = session_dir / "handshake.json"
        assert handshake_path.exists()

        data = json.loads(handshake_path.read_text())
        assert data["role"] == "implementation-lead"
        assert data["mode"] == "full"
        assert "created_at" in data

    def test_promote_pending_to_active_moves_directory(self, tmp_path: Path) -> None:
        from hestai_mcp.mcp.tools.shared.pending_sessions import (
            create_pending_handshake,
            promote_pending_to_active,
        )

        working_dir = tmp_path / "project"
        working_dir.mkdir()

        token = "tok_1"
        pending = create_pending_handshake(
            working_dir=working_dir,
            token=token,
            handshake={"role": "critical-engineer", "mode": "lite"},
        )

        active = promote_pending_to_active(working_dir=working_dir, token=token)

        assert not pending.exists()
        assert active.exists()
        assert (active / "handshake.json").exists()

    def test_cleanup_stale_pending_sessions_removes_old_entries(self, tmp_path: Path) -> None:
        from hestai_mcp.mcp.tools.shared.pending_sessions import (
            cleanup_stale_pending_sessions,
            create_pending_handshake,
        )

        working_dir = tmp_path / "project"
        working_dir.mkdir()

        # Fresh session
        create_pending_handshake(
            working_dir=working_dir,
            token="fresh",
            handshake={"role": "implementation-lead", "mode": "full"},
        )

        # Stale session: provide an old created_at timestamp (preferred aging source)
        stale_created_at = (datetime.now(UTC) - timedelta(hours=48)).isoformat()
        create_pending_handshake(
            working_dir=working_dir,
            token="stale",
            handshake={
                "role": "implementation-lead",
                "mode": "full",
                "created_at": stale_created_at,
            },
        )

        result = cleanup_stale_pending_sessions(working_dir=working_dir, max_age_hours=1)

        assert result.removed == 1
        assert result.kept == 1

        assert (working_dir / ".hestai" / "sessions" / "pending" / "fresh").exists()
        assert not (working_dir / ".hestai" / "sessions" / "pending" / "stale").exists()

    def test_token_validation_rejects_path_traversal(self, tmp_path: Path) -> None:
        from hestai_mcp.mcp.tools.shared.pending_sessions import create_pending_handshake

        working_dir = tmp_path / "project"
        working_dir.mkdir()

        with pytest.raises(ValueError):
            create_pending_handshake(
                working_dir=working_dir,
                token="../evil",
                handshake={"role": "implementation-lead"},
            )
