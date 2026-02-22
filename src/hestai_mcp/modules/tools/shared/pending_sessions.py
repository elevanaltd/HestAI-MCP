"""Pending session helpers for staged binding protocols.

This module supports handshake-style protocols (e.g., OA5) where a session is created
as *pending* and only promoted to *active* after successful proof/commit.

Directory model:
- .hestai/state/sessions/pending/{token}/handshake.json
- .hestai/state/sessions/active/{token}/  (created via promotion)

Design goals:
- Keep pending handshakes isolated from active session lifecycle tools (e.g., clock_out)
- Provide deterministic cleanup to avoid garbage buildup
- Enforce basic path traversal protections on tokens
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def validate_handshake_token(token: str) -> str:
    """Validate handshake token to prevent path traversal and odd filenames.

    Accepts common safe tokens (UUIDs, short ids) comprised of [A-Za-z0-9._-].

    Args:
        token: Proposed token

    Returns:
        Normalized token

    Raises:
        ValueError: if token is unsafe/invalid
    """
    if not token or not token.strip():
        raise ValueError("handshake token cannot be empty")

    token = token.strip()

    # Hard path traversal protection
    if token.startswith("/") or ".." in token or "/" in token or "\\" in token:
        raise ValueError("handshake token contains invalid path characters")

    if not _TOKEN_RE.match(token):
        raise ValueError("handshake token must match ^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

    return token


def pending_dir(working_dir: Path) -> Path:
    return working_dir / ".hestai" / "state" / "sessions" / "pending"


def active_dir(working_dir: Path) -> Path:
    return working_dir / ".hestai" / "state" / "sessions" / "active"


def pending_session_dir(working_dir: Path, token: str) -> Path:
    token = validate_handshake_token(token)
    return pending_dir(working_dir) / token


def active_session_dir(working_dir: Path, token: str) -> Path:
    token = validate_handshake_token(token)
    return active_dir(working_dir) / token


def create_pending_handshake(
    *,
    working_dir: Path,
    token: str,
    handshake: dict[str, Any],
    overwrite: bool = False,
) -> Path:
    """Create a pending handshake directory and write handshake.json.

    Returns the created directory path.
    """
    token = validate_handshake_token(token)

    pdir = pending_dir(working_dir)
    pdir.mkdir(parents=True, exist_ok=True)

    session_dir = pdir / token

    if session_dir.exists():
        if not overwrite:
            raise FileExistsError(f"pending session already exists: {token}")
        # Overwrite semantics: remove prior directory to avoid stale file buildup.
        shutil.rmtree(session_dir)

    session_dir.mkdir(parents=True, exist_ok=True)

    handshake_path = session_dir / "handshake.json"

    # Record a server-side timestamp if caller didn't provide one.
    if "created_at" not in handshake:
        handshake = {**handshake, "created_at": datetime.now(UTC).isoformat()}

    handshake_path.write_text(json.dumps(handshake, indent=2))
    return session_dir


def promote_pending_to_active(*, working_dir: Path, token: str) -> Path:
    """Promote a pending handshake session to an active session.

    Promotion is implemented as a directory rename:
    .hestai/state/sessions/pending/{token} -> .hestai/state/sessions/active/{token}

    This should be called only after the handshake is fully validated and
    anchor state has been persisted.

    Returns the new active session directory path.
    """
    token = validate_handshake_token(token)

    src = pending_session_dir(working_dir, token)
    dst_parent = active_dir(working_dir)
    dst_parent.mkdir(parents=True, exist_ok=True)
    dst = dst_parent / token

    if not src.exists():
        raise FileNotFoundError(f"pending session not found: {token}")

    if not (src / "handshake.json").exists():
        raise FileNotFoundError(f"pending session missing handshake.json: {token}")

    if dst.exists():
        raise FileExistsError(f"active session already exists: {token}")

    # Rename within the same filesystem is atomic.
    src.rename(dst)
    return dst


@dataclass
class PendingCleanupResult:
    removed: int
    kept: int
    errors: list[str]


def cleanup_stale_pending_sessions(
    *,
    working_dir: Path,
    max_age_hours: int = 24,
) -> PendingCleanupResult:
    """Remove stale pending handshake sessions.

    A session is considered stale if its handshake timestamp (preferred) or
    filesystem mtime is older than max_age_hours.

    This is intended to be called during Stage 1 INIT for mode in [full, lite].
    """
    if max_age_hours <= 0:
        raise ValueError("max_age_hours must be positive")

    base = pending_dir(working_dir)
    if not base.exists():
        return PendingCleanupResult(removed=0, kept=0, errors=[])

    now = datetime.now(UTC)
    removed = 0
    kept = 0
    errors: list[str] = []

    for entry in base.iterdir():
        if not entry.is_dir():
            continue

        token = entry.name

        # Determine age.
        created_at: datetime | None = None
        handshake_path = entry / "handshake.json"
        try:
            if handshake_path.exists():
                data = json.loads(handshake_path.read_text())
                raw = data.get("created_at")
                if isinstance(raw, str) and raw.strip():
                    # datetime.fromisoformat supports offsets; enforce UTC when missing.
                    dt = datetime.fromisoformat(raw)
                    created_at = dt if dt.tzinfo else dt.replace(tzinfo=UTC)
        except Exception as e:  # noqa: BLE001 - cleanup must be resilient
            errors.append(f"{token}: failed to parse handshake.json: {e}")

        try:
            if created_at is None:
                stat = (handshake_path if handshake_path.exists() else entry).stat()
                created_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)

            age_hours = (now - created_at).total_seconds() / 3600
            if age_hours > max_age_hours:
                shutil.rmtree(entry)
                removed += 1
            else:
                kept += 1
        except Exception as e:  # noqa: BLE001 - cleanup must be resilient
            errors.append(f"{token}: failed to evaluate/remove pending session: {e}")

    if removed:
        logger.info(f"Removed {removed} stale pending sessions from {base}")

    return PendingCleanupResult(removed=removed, kept=kept, errors=errors)
