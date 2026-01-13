"""
Tests for TranscriptPathResolver - Layered transcript path resolution with security validation.

TDD Discipline:
1. RED: Write failing tests first
2. GREEN: Minimal implementation to pass
3. REFACTOR: Improve while tests pass

Security Context:
- Path traversal prevention is CRITICAL (CVE-level vulnerability)
- Symlink attacks must be detected and blocked
- All path resolution layers must validate containment

Coverage Targets:
- _validate_path_containment: 100% (security-critical)
- _find_by_temporal_beacon: 95%
- _find_by_metadata_inversion: 95%
- _find_by_explicit_config: 90%
- resolve: 90%
"""

import json
import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from hestai_mcp.modules.tools.shared.path_resolution import (
    MAX_PROJECTS_SCAN,
    TEMPORAL_BEACON_MAX_AGE_HOURS,
    TranscriptPathResolver,
)


@pytest.fixture
def resolver() -> TranscriptPathResolver:
    """Create a TranscriptPathResolver instance."""
    return TranscriptPathResolver()


@pytest.fixture
def mock_claude_projects(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Create mock ~/.claude/projects structure for testing.

    Sets CLAUDE_TRANSCRIPT_DIR to allow tests to use tmp_path for path containment.

    Returns:
        Path to mock claude projects directory
    """
    projects_dir = tmp_path / ".claude" / "projects"
    projects_dir.mkdir(parents=True)

    # Set env var to allow tests to use tmp_path based projects dir
    monkeypatch.setenv("CLAUDE_TRANSCRIPT_DIR", str(projects_dir))

    return projects_dir


# =============================================================================
# PHASE 1: Security Core - _validate_path_containment
# Target: 100% coverage (security-critical)
# =============================================================================


@pytest.mark.unit
class TestValidatePathContainmentSecurity:
    """
    Test path traversal prevention - security-critical functionality.

    These tests ensure all escape attempts are blocked with ValueError.
    NEVER allow paths that escape the allowed root directory.
    """

    def test_accepts_path_within_allowed_root(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Accepts paths that are within the allowed root directory."""
        allowed_root = tmp_path / "allowed"
        allowed_root.mkdir()
        target = allowed_root / "subdir" / "file.jsonl"
        target.parent.mkdir(parents=True)
        target.touch()

        result = resolver._validate_path_containment(target, allowed_root)

        assert result == target.resolve()

    @pytest.mark.parametrize(
        "escape_path,description",
        [
            ("../escape", "Parent directory escape"),
            ("../../escape", "Multi-level parent escape"),
            ("subdir/../../../escape", "Mixed path escape"),
            ("./subdir/../../escape", "Dot-prefixed escape"),
        ],
    )
    def test_rejects_parent_directory_traversal(
        self,
        resolver: TranscriptPathResolver,
        tmp_path: Path,
        escape_path: str,
        description: str,
    ):
        """Rejects paths using ../ to escape allowed root."""
        allowed_root = tmp_path / "allowed"
        allowed_root.mkdir()

        malicious_path = allowed_root / escape_path

        with pytest.raises(ValueError, match="[Pp]ath traversal"):
            resolver._validate_path_containment(malicious_path, allowed_root)

    def test_rejects_tilde_expansion_escape(self, resolver: TranscriptPathResolver, tmp_path: Path):
        """Rejects paths using ~/ that escape to user home directory."""
        allowed_root = tmp_path / "allowed"
        allowed_root.mkdir()

        # Create path that uses ~ to escape to home directory
        malicious_path = Path("~/etc/passwd")

        with pytest.raises(ValueError, match="[Pp]ath traversal"):
            resolver._validate_path_containment(malicious_path, allowed_root)

    def test_rejects_absolute_path_outside_root(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Rejects absolute paths that are outside the allowed root."""
        allowed_root = tmp_path / "allowed"
        allowed_root.mkdir()

        # Create absolute path outside allowed root
        outside_path = tmp_path / "outside" / "file.jsonl"
        outside_path.parent.mkdir()
        outside_path.touch()

        with pytest.raises(ValueError, match="[Pp]ath traversal"):
            resolver._validate_path_containment(outside_path, allowed_root)

    def test_rejects_symlink_escape_outside_root(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Rejects symlinks that point outside the allowed root."""
        allowed_root = tmp_path / "allowed"
        allowed_root.mkdir()

        # Create file outside allowed root
        outside_file = tmp_path / "outside" / "secret.jsonl"
        outside_file.parent.mkdir()
        outside_file.touch()

        # Create symlink inside allowed root pointing outside
        symlink_path = allowed_root / "escape_link"
        symlink_path.symlink_to(outside_file)

        with pytest.raises(ValueError, match="[Pp]ath traversal"):
            resolver._validate_path_containment(symlink_path, allowed_root)

    def test_uses_default_allowed_root_when_none(self, resolver: TranscriptPathResolver):
        """Uses ~/.claude/projects as default allowed root when none provided."""
        # Path outside default root (~/.claude/projects) should fail
        outside_path = Path("/tmp/outside/file.jsonl")

        with pytest.raises(ValueError, match="[Pp]ath traversal"):
            resolver._validate_path_containment(outside_path, None)

    def test_normalizes_path_before_validation(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Normalizes paths with redundant components before validation."""
        allowed_root = tmp_path / "allowed"
        allowed_root.mkdir()
        target = allowed_root / "subdir" / "file.jsonl"
        target.parent.mkdir()
        target.touch()

        # Use path with redundant components
        redundant_path = allowed_root / "subdir" / "." / ".." / "subdir" / "file.jsonl"

        result = resolver._validate_path_containment(redundant_path, allowed_root)

        assert result == target.resolve()


# =============================================================================
# PHASE 1: _find_by_temporal_beacon
# Target: 95% coverage
# =============================================================================


@pytest.mark.unit
class TestFindByTemporalBeacon:
    """
    Test temporal beacon layer - finds JSONL by scanning recent files.

    Uses file modification time filtering for I/O efficiency.
    """

    def test_finds_file_within_24h_containing_session_id(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path
    ):
        """Finds JSONL file modified <24h ago containing session_id."""
        project_dir = mock_claude_projects / "test-project"
        project_dir.mkdir()

        session_id = "test-session-uuid-12345"
        jsonl_file = project_dir / "session.jsonl"
        jsonl_file.write_text(f'{{"session_id": "{session_id}", "data": "test"}}\n')

        # Set modification time to recent (within 24h)
        recent_mtime = time.time() - 3600  # 1 hour ago
        os.utime(jsonl_file, (recent_mtime, recent_mtime))

        result = resolver._find_by_temporal_beacon(session_id, mock_claude_projects)

        assert result == jsonl_file

    def test_ignores_file_older_than_24h(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path
    ):
        """Ignores JSONL file modified >24h ago even if it contains session_id."""
        project_dir = mock_claude_projects / "test-project"
        project_dir.mkdir()

        session_id = "old-session-uuid-67890"
        jsonl_file = project_dir / "old-session.jsonl"
        jsonl_file.write_text(f'{{"session_id": "{session_id}", "data": "test"}}\n')

        # Set modification time to 25 hours ago (beyond 24h window)
        old_mtime = time.time() - (TEMPORAL_BEACON_MAX_AGE_HOURS + 1) * 3600
        os.utime(jsonl_file, (old_mtime, old_mtime))

        with pytest.raises(FileNotFoundError, match="No JSONL file found"):
            resolver._find_by_temporal_beacon(session_id, mock_claude_projects)

    def test_raises_file_not_found_when_no_matching_file(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path
    ):
        """Raises FileNotFoundError when no file contains session_id."""
        project_dir = mock_claude_projects / "test-project"
        project_dir.mkdir()

        # Create file with different session_id
        jsonl_file = project_dir / "other-session.jsonl"
        jsonl_file.write_text('{"session_id": "different-uuid", "data": "test"}\n')

        with pytest.raises(FileNotFoundError, match="No JSONL file found"):
            resolver._find_by_temporal_beacon("nonexistent-session-id", mock_claude_projects)

    def test_raises_file_not_found_when_directory_not_exists(
        self, resolver: TranscriptPathResolver, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Raises FileNotFoundError when claude projects directory doesn't exist."""
        nonexistent = tmp_path / "nonexistent" / ".claude" / "projects"

        # Set env var to allow this path (but directory doesn't exist)
        monkeypatch.setenv("CLAUDE_TRANSCRIPT_DIR", str(nonexistent))

        with pytest.raises(FileNotFoundError, match="[Cc]laude projects directory not found"):
            resolver._find_by_temporal_beacon("session-id", nonexistent)

    def test_skips_non_directory_items(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path
    ):
        """Skips non-directory items in claude projects root."""
        # Create a file at projects root (not a directory)
        (mock_claude_projects / "some-file.txt").write_text("not a directory")

        project_dir = mock_claude_projects / "valid-project"
        project_dir.mkdir()

        session_id = "test-session-uuid"
        jsonl_file = project_dir / "session.jsonl"
        jsonl_file.write_text(f'{{"session_id": "{session_id}"}}\n')

        result = resolver._find_by_temporal_beacon(session_id, mock_claude_projects)

        assert result == jsonl_file

    def test_handles_unreadable_files_gracefully(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path
    ):
        """Handles files that can't be read without crashing."""
        project_dir = mock_claude_projects / "test-project"
        project_dir.mkdir()

        # Create a valid file we can find
        project_dir2 = mock_claude_projects / "valid-project"
        project_dir2.mkdir()

        session_id = "test-session-uuid"
        jsonl_file = project_dir2 / "session.jsonl"
        jsonl_file.write_text(f'{{"session_id": "{session_id}"}}\n')

        result = resolver._find_by_temporal_beacon(session_id, mock_claude_projects)

        assert result == jsonl_file

    def test_validates_path_containment_on_custom_root(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Validates path containment when custom root is provided."""
        # Create a valid projects directory
        valid_projects = tmp_path / "valid" / "projects"
        valid_projects.mkdir(parents=True)

        project_dir = valid_projects / "test-project"
        project_dir.mkdir()

        session_id = "test-session"
        jsonl_file = project_dir / "session.jsonl"
        jsonl_file.write_text(f'{{"session_id": "{session_id}"}}\n')

        # Set CLAUDE_TRANSCRIPT_DIR to allow custom root
        with patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(valid_projects)}):
            result = resolver._find_by_temporal_beacon(session_id, valid_projects)

        assert result == jsonl_file


# =============================================================================
# PHASE 1: _find_by_metadata_inversion
# Target: 95% coverage
# =============================================================================


@pytest.mark.unit
class TestFindByMetadataInversion:
    """
    Test metadata inversion layer - matches project_root via project_config.json.
    """

    def test_finds_jsonl_with_matching_project_root(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path, tmp_path: Path
    ):
        """Finds JSONL in project with matching rootPath in project_config.json."""
        project_root = tmp_path / "my-project"
        project_root.mkdir()

        # Create claude project with matching config
        claude_project = mock_claude_projects / "my-project-abc123"
        claude_project.mkdir()

        config = {"rootPath": str(project_root)}
        (claude_project / "project_config.json").write_text(json.dumps(config))

        jsonl_file = claude_project / "session.jsonl"
        jsonl_file.write_text('{"data": "test"}\n')

        result = resolver._find_by_metadata_inversion(project_root, mock_claude_projects)

        assert result == jsonl_file

    def test_raises_file_not_found_when_no_matching_project(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path, tmp_path: Path
    ):
        """Raises FileNotFoundError when no project_config.json matches project_root."""
        project_root = tmp_path / "my-project"
        project_root.mkdir()

        # Create claude project with different root
        claude_project = mock_claude_projects / "other-project"
        claude_project.mkdir()

        config = {"rootPath": "/different/path"}
        (claude_project / "project_config.json").write_text(json.dumps(config))

        with pytest.raises(FileNotFoundError, match="No project_config.json found"):
            resolver._find_by_metadata_inversion(project_root, mock_claude_projects)

    def test_handles_malformed_json_gracefully(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path, tmp_path: Path
    ):
        """Handles malformed project_config.json without crashing."""
        project_root = tmp_path / "my-project"
        project_root.mkdir()

        # Create project with malformed JSON
        bad_project = mock_claude_projects / "bad-project"
        bad_project.mkdir()
        (bad_project / "project_config.json").write_text("not valid json {{{")

        # Create valid project
        good_project = mock_claude_projects / "good-project"
        good_project.mkdir()
        config = {"rootPath": str(project_root)}
        (good_project / "project_config.json").write_text(json.dumps(config))
        jsonl_file = good_project / "session.jsonl"
        jsonl_file.write_text('{"data": "test"}\n')

        result = resolver._find_by_metadata_inversion(project_root, mock_claude_projects)

        assert result == jsonl_file

    def test_handles_missing_root_path_key(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path, tmp_path: Path
    ):
        """Handles project_config.json missing rootPath key."""
        project_root = tmp_path / "my-project"
        project_root.mkdir()

        # Create project with config missing rootPath
        incomplete_project = mock_claude_projects / "incomplete-project"
        incomplete_project.mkdir()
        config = {"someOtherKey": "value"}
        (incomplete_project / "project_config.json").write_text(json.dumps(config))

        with pytest.raises(FileNotFoundError, match="No project_config.json found"):
            resolver._find_by_metadata_inversion(project_root, mock_claude_projects)

    def test_selects_most_recent_jsonl_when_multiple_exist(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path, tmp_path: Path
    ):
        """Selects most recently modified JSONL when multiple exist in project."""
        project_root = tmp_path / "my-project"
        project_root.mkdir()

        claude_project = mock_claude_projects / "my-project"
        claude_project.mkdir()

        config = {"rootPath": str(project_root)}
        (claude_project / "project_config.json").write_text(json.dumps(config))

        # Create multiple JSONL files with different modification times
        older_file = claude_project / "old-session.jsonl"
        older_file.write_text('{"data": "old"}\n')
        old_time = time.time() - 3600
        os.utime(older_file, (old_time, old_time))

        newer_file = claude_project / "new-session.jsonl"
        newer_file.write_text('{"data": "new"}\n')
        # Current time is default

        result = resolver._find_by_metadata_inversion(project_root, mock_claude_projects)

        assert result == newer_file

    def test_raises_file_not_found_when_no_jsonl_in_matched_project(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path, tmp_path: Path, caplog
    ):
        """Logs warning when matched project has no JSONL files, then raises generic error.

        Note: The specific "No JSONL files in matched project" FileNotFoundError is caught
        and logged as a warning, then the function falls through to raise the generic
        "No project_config.json found" error after checking all projects.
        """
        import logging

        project_root = tmp_path / "my-project"
        project_root.mkdir()

        claude_project = mock_claude_projects / "my-project"
        claude_project.mkdir()

        config = {"rootPath": str(project_root)}
        (claude_project / "project_config.json").write_text(json.dumps(config))
        # No JSONL file created

        with (
            caplog.at_level(logging.WARNING),
            pytest.raises(FileNotFoundError, match="No project_config.json found"),
        ):
            resolver._find_by_metadata_inversion(project_root, mock_claude_projects)

        # The actual error is logged as a warning
        assert "No JSONL files in matched project" in caplog.text

    def test_raises_file_not_found_when_directory_not_exists(
        self, resolver: TranscriptPathResolver, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Raises FileNotFoundError when claude projects directory doesn't exist."""
        project_root = tmp_path / "my-project"
        project_root.mkdir()

        nonexistent = tmp_path / "nonexistent"

        # Set env var to allow this path (but directory doesn't exist)
        monkeypatch.setenv("CLAUDE_TRANSCRIPT_DIR", str(nonexistent))

        with pytest.raises(FileNotFoundError, match="[Cc]laude projects directory not found"):
            resolver._find_by_metadata_inversion(project_root, nonexistent)

    def test_enforces_max_projects_scan_limit(
        self, resolver: TranscriptPathResolver, mock_claude_projects: Path, tmp_path: Path
    ):
        """Raises FileNotFoundError when MAX_PROJECTS_SCAN limit exceeded."""
        project_root = tmp_path / "my-project"
        project_root.mkdir()

        # Create more than MAX_PROJECTS_SCAN directories
        for i in range(MAX_PROJECTS_SCAN + 5):
            project = mock_claude_projects / f"project-{i:04d}"
            project.mkdir()
            # Don't create project_config.json to ensure scanning continues

        with pytest.raises(FileNotFoundError, match="MAX_PROJECTS_SCAN.*exceeded"):
            resolver._find_by_metadata_inversion(project_root, mock_claude_projects)


# =============================================================================
# PHASE 1: _find_by_explicit_config
# Target: 90% coverage
# =============================================================================


@pytest.mark.unit
class TestFindByExplicitConfig:
    """
    Test explicit config layer - uses CLAUDE_TRANSCRIPT_DIR env var.
    """

    def test_finds_file_when_env_var_set(self, resolver: TranscriptPathResolver, tmp_path: Path):
        """Finds JSONL file in CLAUDE_TRANSCRIPT_DIR containing session_id."""
        transcript_dir = tmp_path / "transcripts"
        transcript_dir.mkdir()

        session_id = "test-session-uuid"
        jsonl_file = transcript_dir / "session.jsonl"
        jsonl_file.write_text(f'{{"session_id": "{session_id}"}}\n')

        with patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(transcript_dir)}):
            result = resolver._find_by_explicit_config(session_id)

        assert result == jsonl_file

    def test_raises_file_not_found_when_env_var_not_set(self, resolver: TranscriptPathResolver):
        """Raises FileNotFoundError when CLAUDE_TRANSCRIPT_DIR not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Ensure the env var is not set
            os.environ.pop("CLAUDE_TRANSCRIPT_DIR", None)

            with pytest.raises(FileNotFoundError, match="CLAUDE_TRANSCRIPT_DIR.*not set"):
                resolver._find_by_explicit_config("session-id")

    def test_raises_file_not_found_when_dir_not_exists(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Raises FileNotFoundError when CLAUDE_TRANSCRIPT_DIR doesn't exist."""
        nonexistent_dir = tmp_path / "nonexistent"

        with (
            patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(nonexistent_dir)}),
            pytest.raises(FileNotFoundError, match="CLAUDE_TRANSCRIPT_DIR does not exist"),
        ):
            resolver._find_by_explicit_config("session-id")

    def test_raises_file_not_found_when_no_matching_file(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Raises FileNotFoundError when no file contains session_id."""
        transcript_dir = tmp_path / "transcripts"
        transcript_dir.mkdir()

        # Create file with different session_id
        jsonl_file = transcript_dir / "other.jsonl"
        jsonl_file.write_text('{"session_id": "different-id"}\n')

        with (
            patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(transcript_dir)}),
            pytest.raises(FileNotFoundError, match="No JSONL file containing"),
        ):
            resolver._find_by_explicit_config("target-session-id")

    def test_searches_recursively_in_subdirectories(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Searches recursively for JSONL files in subdirectories."""
        transcript_dir = tmp_path / "transcripts"
        subdir = transcript_dir / "project1" / "sessions"
        subdir.mkdir(parents=True)

        session_id = "nested-session-uuid"
        jsonl_file = subdir / "session.jsonl"
        jsonl_file.write_text(f'{{"session_id": "{session_id}"}}\n')

        with patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(transcript_dir)}):
            result = resolver._find_by_explicit_config(session_id)

        assert result == jsonl_file

    def test_skips_symlinks_pointing_outside_custom_root(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Skips symlinks that resolve outside the custom root directory."""
        transcript_dir = tmp_path / "transcripts"
        transcript_dir.mkdir()

        # Create target file outside transcript_dir
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        outside_file = outside_dir / "secret.jsonl"
        outside_file.write_text('{"session_id": "target-session"}\n')

        # Create symlink inside transcript_dir pointing outside
        symlink_file = transcript_dir / "escape.jsonl"
        symlink_file.symlink_to(outside_file)

        with (
            patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(transcript_dir)}),
            pytest.raises(FileNotFoundError, match="No JSONL file containing"),
        ):
            resolver._find_by_explicit_config("target-session")


# =============================================================================
# PHASE 1: resolve (Integration Tests)
# Target: 90% coverage
# =============================================================================


@pytest.mark.unit
class TestResolveLayerPriority:
    """
    Test resolve() method - integration test of resolution order.

    Resolution order:
    0. Hook path (highest priority)
    1. Temporal beacon
    2. Metadata inversion
    3. Explicit config
    """

    def test_hook_path_wins_over_beacon(self, resolver: TranscriptPathResolver, tmp_path: Path):
        """Hook-provided path takes priority over temporal beacon."""
        # Set up environment for hook path to work
        allowed_root = tmp_path / "claude" / "projects"
        allowed_root.mkdir(parents=True)

        hook_file = allowed_root / "hook.jsonl"
        hook_file.write_text('{"from": "hook"}\n')

        beacon_dir = allowed_root / "beacon-project"
        beacon_dir.mkdir()
        beacon_file = beacon_dir / "beacon.jsonl"
        beacon_file.write_text('{"session_id": "test-session", "from": "beacon"}\n')

        session_data = {
            "session_id": "test-session",
            "transcript_path": str(hook_file),
        }

        with patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(allowed_root)}):
            result = resolver.resolve(session_data, tmp_path)

        assert result == hook_file.resolve()

    def test_beacon_wins_over_metadata(self, resolver: TranscriptPathResolver, tmp_path: Path):
        """Temporal beacon takes priority over metadata inversion."""
        # Set up claude projects with both beacon and metadata files
        projects_root = tmp_path / "claude" / "projects"
        projects_root.mkdir(parents=True)

        # Create beacon-findable file (recent)
        beacon_project = projects_root / "beacon-project"
        beacon_project.mkdir()
        beacon_file = beacon_project / "beacon.jsonl"
        beacon_file.write_text('{"session_id": "test-session"}\n')

        # Create metadata-findable project (would be found by metadata inversion)
        metadata_project = projects_root / "metadata-project"
        metadata_project.mkdir()
        config = {"rootPath": str(tmp_path)}
        (metadata_project / "project_config.json").write_text(json.dumps(config))
        metadata_file = metadata_project / "metadata.jsonl"
        metadata_file.write_text('{"from": "metadata"}\n')

        session_data = {"session_id": "test-session"}

        with patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(projects_root)}):
            result = resolver.resolve(session_data, tmp_path)

        assert result == beacon_file

    def test_fallback_to_explicit_config_when_others_fail(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Falls back to explicit config when beacon and metadata fail."""
        # Create transcript in env var location
        transcript_dir = tmp_path / "transcripts"
        transcript_dir.mkdir()

        session_id = "fallback-session"
        explicit_file = transcript_dir / "explicit.jsonl"
        explicit_file.write_text(f'{{"session_id": "{session_id}"}}\n')

        session_data = {"session_id": session_id}

        # No hook path, no beacon matches, no metadata matches
        project_root = tmp_path / "empty-project"
        project_root.mkdir()

        with patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(transcript_dir)}):
            result = resolver.resolve(session_data, project_root)

        assert result == explicit_file

    def test_raises_file_not_found_when_all_layers_fail(
        self, resolver: TranscriptPathResolver, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Raises FileNotFoundError when all resolution layers fail."""
        # Use a very unique session_id that won't exist anywhere
        import uuid

        session_data = {"session_id": f"nonexistent-test-{uuid.uuid4().hex}"}

        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create an empty home directory structure to prevent searching real ~/.claude/projects
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()
        empty_projects = fake_home / ".claude" / "projects"
        empty_projects.mkdir(parents=True)

        # Mock the home directory to use our fake one
        monkeypatch.setenv("HOME", str(fake_home))

        # Clear CLAUDE_TRANSCRIPT_DIR to make explicit config fail
        monkeypatch.delenv("CLAUDE_TRANSCRIPT_DIR", raising=False)

        with pytest.raises(FileNotFoundError, match="Could not locate transcript"):
            resolver.resolve(session_data, project_root)

    def test_raises_security_error_on_hook_path_traversal(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Raises ValueError (not FileNotFoundError) on path traversal attempt."""
        session_data = {
            "session_id": "test-session",
            "transcript_path": "../../../etc/passwd",
        }
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Path traversal should raise ValueError, not fall back
        with pytest.raises(ValueError, match="[Ss]ecurity violation"):
            resolver.resolve(session_data, project_root)

    def test_falls_back_when_hook_path_missing(
        self, resolver: TranscriptPathResolver, tmp_path: Path
    ):
        """Falls back to discovery when hook path is safe but file missing."""
        projects_root = tmp_path / "claude" / "projects"
        projects_root.mkdir(parents=True)

        # Create a project with session file
        project = projects_root / "project"
        project.mkdir()
        session_file = project / "session.jsonl"
        session_file.write_text('{"session_id": "test-session"}\n')

        # Hook path points to non-existent file within allowed root
        missing_file = projects_root / "nonexistent.jsonl"

        session_data = {
            "session_id": "test-session",
            "transcript_path": str(missing_file),
        }

        with patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(projects_root)}):
            result = resolver.resolve(session_data, tmp_path)

        # Should fall back to temporal beacon
        assert result == session_file

    def test_handles_empty_session_id(self, resolver: TranscriptPathResolver, tmp_path: Path):
        """Handles empty session_id by skipping beacon and explicit config layers."""
        projects_root = tmp_path / "claude" / "projects"
        projects_root.mkdir(parents=True)

        # Set up metadata inversion
        project = projects_root / "my-project"
        project.mkdir()

        project_root = tmp_path / "my-actual-project"
        project_root.mkdir()

        config = {"rootPath": str(project_root)}
        (project / "project_config.json").write_text(json.dumps(config))
        metadata_file = project / "session.jsonl"
        metadata_file.write_text('{"from": "metadata"}\n')

        session_data = {"session_id": ""}  # Empty session_id

        with patch.dict(os.environ, {"CLAUDE_TRANSCRIPT_DIR": str(projects_root)}):
            result = resolver.resolve(session_data, project_root)

        # Should use metadata inversion since beacon requires session_id
        assert result == metadata_file
