"""
Governance integrity module for Holographic Constitution (#235).

Provides three-layer governance protection:
1. SHA256 content hashing for tamper detection
2. chmod 444/555 read-only permissions on .hestai-sys/
3. Integrity verification and self-healing support

Used by inject_system_governance() to protect governance files
after every injection cycle.
"""

import hashlib
import logging
import os
import stat
from pathlib import Path

logger = logging.getLogger(__name__)

# Metadata files excluded from hash computation
_HASH_EXCLUDED_FILES = {".version", ".integrity"}


def apply_readonly_permissions(governance_dir: Path) -> None:
    """Apply read-only permissions to all governance files.

    Sets files to 0o444 (read-only for all) and directories to 0o555
    (read+execute for all, no write). Agents using Edit/Write tools
    will receive OS-level PermissionError.

    Args:
        governance_dir: Path to .hestai-sys/ directory
    """
    if not governance_dir.exists():
        return

    file_count = 0

    # Walk bottom-up so we can set directory permissions after
    # processing their contents
    for root, dirs, files in os.walk(str(governance_dir), topdown=False):
        for f in files:
            fpath = os.path.join(root, f)
            os.chmod(fpath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            file_count += 1

        for d in dirs:
            dpath = os.path.join(root, d)
            os.chmod(
                dpath,
                stat.S_IRUSR
                | stat.S_IXUSR
                | stat.S_IRGRP
                | stat.S_IXGRP
                | stat.S_IROTH
                | stat.S_IXOTH,
            )

    # Set root directory permissions
    os.chmod(
        str(governance_dir),
        stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH,
    )

    logger.info(
        "Applied read-only permissions to %d files in %s",
        file_count,
        governance_dir,
    )


def restore_writable_permissions(governance_dir: Path) -> None:
    """Temporarily restore writable permissions for re-injection.

    Called before inject_system_governance() needs to replace files.
    Sets files to 0o644 and directories to 0o755.

    Args:
        governance_dir: Path to .hestai-sys/ directory
    """
    if not governance_dir.exists():
        return

    # Walk top-down so we can set directory permissions first,
    # enabling write access to modify contents
    for root, dirs, files in os.walk(str(governance_dir), topdown=True):
        # Restore directory write permission first
        os.chmod(
            root,
            stat.S_IRUSR
            | stat.S_IWUSR
            | stat.S_IXUSR
            | stat.S_IRGRP
            | stat.S_IXGRP
            | stat.S_IROTH
            | stat.S_IXOTH,
        )

        for f in files:
            fpath = os.path.join(root, f)
            os.chmod(
                fpath,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH,
            )

        for d in dirs:
            dpath = os.path.join(root, d)
            os.chmod(
                dpath,
                stat.S_IRUSR
                | stat.S_IWUSR
                | stat.S_IXUSR
                | stat.S_IRGRP
                | stat.S_IXGRP
                | stat.S_IROTH
                | stat.S_IXOTH,
            )

    logger.info("Restored writable permissions on %s", governance_dir)


def compute_governance_hash(governance_dir: Path) -> str:
    """Compute SHA256 hash of entire governance directory tree.

    Hash is computed over sorted (relative_path, file_content) pairs
    to ensure determinism regardless of filesystem ordering.
    Ignores .version and .integrity files (metadata, not content).

    Args:
        governance_dir: Path to .hestai-sys/ directory

    Returns:
        64-character hex SHA256 hash string
    """
    hasher = hashlib.sha256()

    # Collect all file paths relative to governance_dir, sorted
    file_entries: list[tuple[str, Path]] = []
    for root, _dirs, files in os.walk(str(governance_dir)):
        for f in files:
            if f in _HASH_EXCLUDED_FILES:
                continue
            full_path = Path(root) / f
            rel_path = str(full_path.relative_to(governance_dir))
            file_entries.append((rel_path, full_path))

    # Sort by relative path for determinism
    file_entries.sort(key=lambda x: x[0])

    for rel_path, full_path in file_entries:
        # Hash the relative path
        hasher.update(rel_path.encode("utf-8"))
        # Hash the file content
        hasher.update(full_path.read_bytes())

    return hasher.hexdigest()


def verify_governance_integrity(governance_dir: Path) -> dict:
    """Verify governance files haven't been tampered with.

    Compares computed hash against stored reference hash
    in .integrity file.

    Args:
        governance_dir: Path to .hestai-sys/ directory

    Returns:
        dict with 'intact' (bool), optionally 'reason' (str),
        'first_run' (bool)
    """
    integrity_file = governance_dir / ".integrity"

    if not integrity_file.exists():
        return {"intact": True, "first_run": True}

    stored_hash = integrity_file.read_text().strip()
    current_hash = compute_governance_hash(governance_dir)

    if stored_hash == current_hash:
        return {"intact": True}

    return {
        "intact": False,
        "reason": (
            f"Governance hash mismatch: "
            f"stored={stored_hash[:16]}... "
            f"computed={current_hash[:16]}..."
        ),
    }


def store_governance_hash(governance_dir: Path) -> str:
    """Compute and store governance hash as reference.

    Called after successful injection to establish baseline.

    Args:
        governance_dir: Path to .hestai-sys/ directory

    Returns:
        The computed hash string
    """
    gov_hash = compute_governance_hash(governance_dir)
    integrity_file = governance_dir / ".integrity"
    integrity_file.write_text(gov_hash)
    logger.info(
        "Stored governance hash %s... in %s",
        gov_hash[:16],
        integrity_file,
    )
    return gov_hash
