"""
Tests for governance integrity module - Holographic Constitution (#235).

TDD Discipline:
1. RED: Write failing tests first
2. GREEN: Minimal implementation to pass
3. REFACTOR: Improve while tests pass

Governance Context:
- .hestai-sys/ files must be protected with read-only permissions (chmod 444/555)
- SHA256 content hashing provides tamper detection
- Integrity verification enables self-healing governance
"""

import os
import stat
from pathlib import Path

import pytest


@pytest.mark.unit
class TestApplyReadonlyPermissions:
    """Test applying read-only permissions to governance directory."""

    def test_apply_readonly_permissions_sets_444_on_files(self, tmp_path: Path) -> None:
        """After apply_readonly_permissions, all files have mode 0o444."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            apply_readonly_permissions,
        )

        # Create test files
        (tmp_path / "file1.md").write_text("content1")
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "file2.md").write_text("content2")

        apply_readonly_permissions(tmp_path)

        for root, _dirs, files in os.walk(tmp_path):
            for f in files:
                fpath = os.path.join(root, f)
                mode = stat.S_IMODE(os.stat(fpath).st_mode)
                assert mode == 0o444, f"{fpath} has mode {oct(mode)}, expected 0o444"

    def test_apply_readonly_permissions_sets_555_on_directories(self, tmp_path: Path) -> None:
        """Directories get 0o555 (read+execute, no write)."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            apply_readonly_permissions,
        )

        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "file.md").write_text("content")

        apply_readonly_permissions(tmp_path)

        for root, dirs, _files in os.walk(tmp_path):
            for d in dirs:
                dpath = os.path.join(root, d)
                mode = stat.S_IMODE(os.stat(dpath).st_mode)
                assert mode == 0o555, f"{dpath} has mode {oct(mode)}, expected 0o555"

        # Also check the root directory itself
        root_mode = stat.S_IMODE(os.stat(tmp_path).st_mode)
        assert root_mode == 0o555, f"Root dir has mode {oct(root_mode)}, expected 0o555"

    def test_apply_readonly_permissions_handles_empty_directory(self, tmp_path: Path) -> None:
        """Graceful handling of empty directory."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            apply_readonly_permissions,
        )

        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Should not raise
        apply_readonly_permissions(empty_dir)

        mode = stat.S_IMODE(os.stat(empty_dir).st_mode)
        assert mode == 0o555

    def test_apply_readonly_permissions_skips_nonexistent_path(self, tmp_path: Path) -> None:
        """Returns without error if path doesn't exist."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            apply_readonly_permissions,
        )

        nonexistent = tmp_path / "nonexistent"

        # Should not raise
        apply_readonly_permissions(nonexistent)


@pytest.mark.unit
class TestRestoreWritablePermissions:
    """Test restoring writable permissions before re-injection."""

    def test_restore_writable_permissions_before_reinject(self, tmp_path: Path) -> None:
        """Utility to make files writable again before re-injection."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            apply_readonly_permissions,
            restore_writable_permissions,
        )

        # Create and lock down files
        (tmp_path / "file.md").write_text("content")
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.md").write_text("nested")

        apply_readonly_permissions(tmp_path)

        # Verify locked
        file_mode = stat.S_IMODE(os.stat(tmp_path / "file.md").st_mode)
        assert file_mode == 0o444

        # Restore writable
        restore_writable_permissions(tmp_path)

        # Verify writable: files 0o644, dirs 0o755
        file_mode = stat.S_IMODE(os.stat(tmp_path / "file.md").st_mode)
        assert file_mode == 0o644, f"File has mode {oct(file_mode)}, expected 0o644"

        dir_mode = stat.S_IMODE(os.stat(sub).st_mode)
        assert dir_mode == 0o755, f"Dir has mode {oct(dir_mode)}, expected 0o755"

    def test_restore_writable_permissions_skips_nonexistent_path(self, tmp_path: Path) -> None:
        """Returns without error if path doesn't exist."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            restore_writable_permissions,
        )

        nonexistent = tmp_path / "nonexistent"

        # Should not raise
        restore_writable_permissions(nonexistent)


@pytest.mark.unit
class TestComputeGovernanceHash:
    """Test SHA256 content hashing of governance directory."""

    def test_compute_governance_hash_returns_sha256_hex(self, tmp_path: Path) -> None:
        """Returns a 64-char hex string."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        (tmp_path / "file.md").write_text("content")

        result = compute_governance_hash(tmp_path)

        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_compute_governance_hash_deterministic(self, tmp_path: Path) -> None:
        """Same content produces same hash."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        (tmp_path / "file.md").write_text("content")
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.md").write_text("nested")

        hash1 = compute_governance_hash(tmp_path)
        hash2 = compute_governance_hash(tmp_path)

        assert hash1 == hash2

    def test_compute_governance_hash_detects_content_change(self, tmp_path: Path) -> None:
        """Modifying file content changes the hash."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        f = tmp_path / "file.md"
        f.write_text("original")

        hash1 = compute_governance_hash(tmp_path)

        f.write_text("modified")

        hash2 = compute_governance_hash(tmp_path)

        assert hash1 != hash2

    def test_compute_governance_hash_detects_file_addition(self, tmp_path: Path) -> None:
        """Adding a file changes the hash."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        (tmp_path / "file1.md").write_text("content1")

        hash1 = compute_governance_hash(tmp_path)

        (tmp_path / "file2.md").write_text("content2")

        hash2 = compute_governance_hash(tmp_path)

        assert hash1 != hash2

    def test_compute_governance_hash_detects_file_deletion(self, tmp_path: Path) -> None:
        """Removing a file changes the hash."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        f1 = tmp_path / "file1.md"
        f1.write_text("content1")
        (tmp_path / "file2.md").write_text("content2")

        hash1 = compute_governance_hash(tmp_path)

        f1.unlink()

        hash2 = compute_governance_hash(tmp_path)

        assert hash1 != hash2

    def test_compute_governance_hash_ignores_permissions(self, tmp_path: Path) -> None:
        """Hash is content-only, not affected by permission changes."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        f = tmp_path / "file.md"
        f.write_text("content")

        hash1 = compute_governance_hash(tmp_path)

        os.chmod(str(f), 0o444)

        hash2 = compute_governance_hash(tmp_path)

        assert hash1 == hash2

        # Restore for cleanup
        os.chmod(str(f), 0o644)

    def test_compute_governance_hash_ignores_symlinks(self, tmp_path: Path) -> None:
        """Symlinks are not followed during hash computation."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        gov_dir = tmp_path / "gov"
        gov_dir.mkdir()
        (gov_dir / "real.md").write_text("content")

        hash_without_symlink = compute_governance_hash(gov_dir)

        # Create a symlink pointing outside governance dir
        outside_file = tmp_path / "outside.md"
        outside_file.write_text("external content")
        (gov_dir / "sneaky_link").symlink_to(outside_file)

        hash_with_symlink = compute_governance_hash(gov_dir)

        # Hash should be the same — symlink is not followed
        assert hash_without_symlink == hash_with_symlink

    def test_compute_governance_hash_handles_empty_directory(self, tmp_path: Path) -> None:
        """Returns valid hash for empty directory."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = compute_governance_hash(empty_dir)

        assert isinstance(result, str)
        assert len(result) == 64


@pytest.mark.unit
class TestVerifyGovernanceIntegrity:
    """Test integrity verification against stored hash."""

    def test_verify_governance_integrity_passes_when_hash_matches(self, tmp_path: Path) -> None:
        """Returns intact=True when stored hash matches computed."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            store_governance_hash,
            verify_governance_integrity,
        )

        (tmp_path / "file.md").write_text("content")
        store_governance_hash(tmp_path)

        result = verify_governance_integrity(tmp_path)

        assert result["intact"] is True

    def test_verify_governance_integrity_fails_when_hash_mismatches(self, tmp_path: Path) -> None:
        """Returns intact=False with reason when tampered."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            store_governance_hash,
            verify_governance_integrity,
        )

        (tmp_path / "file.md").write_text("original")
        store_governance_hash(tmp_path)

        # Tamper with file
        (tmp_path / "file.md").write_text("tampered")

        result = verify_governance_integrity(tmp_path)

        assert result["intact"] is False
        assert "reason" in result

    def test_verify_governance_integrity_passes_when_no_stored_hash(self, tmp_path: Path) -> None:
        """First run (no stored hash) returns intact=True, first_run=True."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            verify_governance_integrity,
        )

        (tmp_path / "file.md").write_text("content")

        result = verify_governance_integrity(tmp_path)

        assert result["intact"] is True
        assert result["first_run"] is True

    def test_verify_governance_integrity_rejects_symlinked_governance_dir(
        self, tmp_path: Path
    ) -> None:
        """Returns intact=False when governance_dir is itself a symlink (root-level substitution)."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            verify_governance_integrity,
        )

        # Create a real directory with content
        real_dir = tmp_path / "real_governance"
        real_dir.mkdir()
        (real_dir / "CONSTITUTION.md").write_text("real content")

        # Create a symlink that points to the real directory
        symlink_dir = tmp_path / "symlink_governance"
        symlink_dir.symlink_to(real_dir)

        assert symlink_dir.is_symlink()

        result = verify_governance_integrity(symlink_dir)

        assert result["intact"] is False
        assert "reason" in result
        assert "symlink" in result["reason"].lower()


@pytest.mark.unit
class TestComputeGovernanceHashSymlinkRejection:
    """Test that compute_governance_hash rejects symlinked governance dir."""

    def test_compute_governance_hash_rejects_symlinked_governance_dir(self, tmp_path: Path) -> None:
        """Raises ValueError when governance_dir is itself a symlink."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            compute_governance_hash,
        )

        real_dir = tmp_path / "real_governance"
        real_dir.mkdir()
        (real_dir / "CONSTITUTION.md").write_text("real content")

        symlink_dir = tmp_path / "symlink_governance"
        symlink_dir.symlink_to(real_dir)

        assert symlink_dir.is_symlink()

        with pytest.raises(ValueError, match="symlink"):
            compute_governance_hash(symlink_dir)


@pytest.mark.unit
class TestApplyReadonlyPermissionsSymlinkRejection:
    """Test that apply_readonly_permissions rejects symlinked governance dir."""

    def test_apply_readonly_permissions_rejects_symlinked_governance_dir(
        self, tmp_path: Path
    ) -> None:
        """Raises ValueError when governance_dir is itself a symlink."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            apply_readonly_permissions,
        )

        real_dir = tmp_path / "real_governance"
        real_dir.mkdir()
        (real_dir / "CONSTITUTION.md").write_text("real content")

        symlink_dir = tmp_path / "symlink_governance"
        symlink_dir.symlink_to(real_dir)

        assert symlink_dir.is_symlink()

        with pytest.raises(ValueError, match="symlink"):
            apply_readonly_permissions(symlink_dir)


@pytest.mark.unit
class TestRestoreWritablePermissionsSymlinkRejection:
    """Test that restore_writable_permissions rejects symlinked governance dir."""

    def test_restore_writable_permissions_rejects_symlinked_governance_dir(
        self, tmp_path: Path
    ) -> None:
        """Raises ValueError when governance_dir is itself a symlink."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            restore_writable_permissions,
        )

        real_dir = tmp_path / "real_governance"
        real_dir.mkdir()
        (real_dir / "CONSTITUTION.md").write_text("real content")

        symlink_dir = tmp_path / "symlink_governance"
        symlink_dir.symlink_to(real_dir)

        assert symlink_dir.is_symlink()

        with pytest.raises(ValueError, match="symlink"):
            restore_writable_permissions(symlink_dir)


@pytest.mark.unit
class TestStoreGovernanceHashSymlinkRejection:
    """Test that store_governance_hash rejects symlinked governance dir."""

    def test_store_governance_hash_rejects_symlinked_governance_dir(self, tmp_path: Path) -> None:
        """Raises ValueError when governance_dir is itself a symlink."""
        from hestai_mcp.modules.tools.shared.governance_integrity import (
            store_governance_hash,
        )

        real_dir = tmp_path / "real_governance"
        real_dir.mkdir()
        (real_dir / "CONSTITUTION.md").write_text("real content")

        symlink_dir = tmp_path / "symlink_governance"
        symlink_dir.symlink_to(real_dir)

        assert symlink_dir.is_symlink()

        with pytest.raises(ValueError, match="symlink"):
            store_governance_hash(symlink_dir)
