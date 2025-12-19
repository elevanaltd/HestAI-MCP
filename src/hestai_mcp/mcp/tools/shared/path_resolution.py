"""
Layered transcript path resolution with security validation.

Provides TranscriptPathResolver class for discovering Claude session JSONL files
through multiple fallback layers with path traversal prevention.

Resolution order:
0. Hook-provided path (with allowlist validation)
1. Temporal beacon (scan recent files for session_id)
2. Metadata inversion (match project_root via project_config.json)
3. Explicit config (CLAUDE_TRANSCRIPT_DIR env var)
4. Legacy fallback
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Security and performance constants
TEMPORAL_BEACON_MAX_AGE_HOURS = 24
MAX_PROJECTS_SCAN = 1000
MAX_SCAN_TIME = 10  # seconds


class TranscriptPathResolver:
    """
    Layered transcript discovery with security validation.

    Discovers Claude session JSONL files through multiple fallback strategies
    while enforcing path containment to prevent directory traversal attacks.
    """

    def _validate_path_containment(
        self, input_path: Path, allowed_root: Optional[Path] = None
    ) -> Path:
        """
        Validate path is within allowed root directory.

        Args:
            input_path: Path to validate
            allowed_root: Optional custom allowed root (defaults to ~/.claude/projects)

        Returns:
            Resolved absolute path

        Raises:
            ValueError: If path traversal attempt detected
        """
        if allowed_root is None:
            allowed_root = Path("~/.claude/projects").expanduser().resolve()
        else:
            allowed_root = allowed_root.expanduser().resolve()

        target_path = input_path.expanduser().resolve()

        if not target_path.is_relative_to(allowed_root):
            raise ValueError(f"Path traversal attempt: {target_path} not within {allowed_root}")

        return target_path

    def _find_by_temporal_beacon(
        self, session_id: str, claude_projects: Optional[Path] = None
    ) -> Path:
        """
        Layer 1: Find JSONL by scanning recently modified files for session_id content.

        The clockout command writes to the JSONL log, so the session_id is guaranteed
        to be present in the file. Temporal filter (24h) provides I/O efficiency.

        Args:
            session_id: Unique session identifier to search for
            claude_projects: Optional path to Claude projects directory

        Returns:
            Path to JSONL file containing session_id

        Raises:
            FileNotFoundError: If no matching file found in last 24h
            ValueError: If path traversal detected
        """
        default_root = Path("~/.claude/projects").expanduser()
        if claude_projects is None:
            claude_projects = default_root
            allowed_root = default_root
        else:
            # Custom root provided - validate it's absolute and resolve it
            claude_projects = claude_projects.expanduser().resolve()
            # When custom root provided, use CLAUDE_TRANSCRIPT_DIR or default
            custom_env = os.environ.get("CLAUDE_TRANSCRIPT_DIR")
            if custom_env and claude_projects.is_relative_to(Path(custom_env).resolve()):
                allowed_root = Path(custom_env).resolve()
            else:
                allowed_root = default_root

        # Validate path containment
        claude_projects = self._validate_path_containment(claude_projects, allowed_root)

        if not claude_projects.exists():
            raise FileNotFoundError(f"Claude projects directory not found: {claude_projects}")

        # Calculate cutoff time (24h ago)
        cutoff_time = time.time() - (TEMPORAL_BEACON_MAX_AGE_HOURS * 60 * 60)

        # Scan all JSONL files modified in last 24h
        for project_dir in claude_projects.iterdir():
            if not project_dir.is_dir():
                continue

            for jsonl_file in project_dir.glob("*.jsonl"):
                try:
                    # Check modification time first (I/O efficiency)
                    if jsonl_file.stat().st_mtime < cutoff_time:
                        continue

                    # Scan file content for session_id
                    with open(jsonl_file) as f:
                        for line in f:
                            if session_id in line:
                                logger.debug(f"Found session_id via temporal beacon: {jsonl_file}")
                                return jsonl_file

                except OSError as e:
                    logger.warning(f"Error reading {jsonl_file}: {e}")
                    continue

        raise FileNotFoundError(
            f"No JSONL file found containing session_id {session_id} "
            f"in last {TEMPORAL_BEACON_MAX_AGE_HOURS}h"
        )

    def _find_by_metadata_inversion(
        self, project_root: Path, claude_projects: Optional[Path] = None
    ) -> Path:
        """
        Layer 2: Find JSONL by scanning project_config.json files to match project root.

        Args:
            project_root: Project root directory to match
            claude_projects: Optional path to Claude projects directory

        Returns:
            Path to most recent JSONL file in matched project directory

        Raises:
            FileNotFoundError: If no matching project or JSONL found, or MAX_PROJECTS_SCAN exceeded
            ValueError: If path traversal detected
        """
        default_root = Path("~/.claude/projects").expanduser()
        if claude_projects is None:
            claude_projects = default_root
            allowed_root = default_root
        else:
            # Custom root provided - validate it's absolute and resolve it
            claude_projects = claude_projects.expanduser().resolve()
            # When custom root provided, use CLAUDE_TRANSCRIPT_DIR or default
            custom_env = os.environ.get("CLAUDE_TRANSCRIPT_DIR")
            if custom_env and claude_projects.is_relative_to(Path(custom_env).resolve()):
                allowed_root = Path(custom_env).resolve()
            else:
                allowed_root = default_root

        # Validate path containment
        claude_projects = self._validate_path_containment(claude_projects, allowed_root)

        if not claude_projects.exists():
            raise FileNotFoundError(f"Claude projects directory not found: {claude_projects}")

        project_root = project_root.resolve()
        scanned_count = 0
        start_time = time.time()

        # Scan project directories
        for project_dir in claude_projects.iterdir():
            if not project_dir.is_dir():
                continue

            scanned_count += 1

            # DoS prevention: enforce MAX_PROJECTS_SCAN limit
            if scanned_count > MAX_PROJECTS_SCAN:
                raise FileNotFoundError(
                    f"MAX_PROJECTS_SCAN ({MAX_PROJECTS_SCAN}) exceeded - "
                    f"use explicit config or temporal beacon instead"
                )

            # Timeout protection
            if time.time() - start_time > MAX_SCAN_TIME:
                raise FileNotFoundError(f"Metadata inversion timeout ({MAX_SCAN_TIME}s) exceeded")

            # Check for project_config.json
            config_file = project_dir / "project_config.json"
            if not config_file.exists():
                continue

            try:
                config = json.loads(config_file.read_text())
                config_root = Path(config.get("rootPath", "")).resolve()

                if config_root == project_root:
                    # Found matching project - find most recent JSONL
                    jsonl_files = list(project_dir.glob("*.jsonl"))
                    if not jsonl_files:
                        raise FileNotFoundError(f"No JSONL files in matched project: {project_dir}")

                    most_recent = max(jsonl_files, key=lambda p: p.stat().st_mtime)
                    logger.debug(f"Found JSONL via metadata inversion: {most_recent}")
                    return most_recent

            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Error reading {config_file}: {e}")
                continue

        raise FileNotFoundError(
            f"No project_config.json found matching project root: {project_root}"
        )

    def _find_by_explicit_config(self, session_id: str) -> Path:
        """
        Layer 3: Find JSONL via explicit configuration (CLAUDE_TRANSCRIPT_DIR env var).

        Args:
            session_id: Session identifier to locate file

        Returns:
            Path to JSONL file in configured directory

        Raises:
            FileNotFoundError: If env var not set or no matching file found
        """
        transcript_dir = os.environ.get("CLAUDE_TRANSCRIPT_DIR")

        if not transcript_dir:
            raise FileNotFoundError("CLAUDE_TRANSCRIPT_DIR environment variable not set")

        # The env var IS the allowed root (escape hatch for custom locations)
        custom_root = Path(transcript_dir).expanduser().resolve()

        if not custom_root.exists():
            raise FileNotFoundError(f"CLAUDE_TRANSCRIPT_DIR does not exist: {custom_root}")

        # Find JSONL file containing session_id
        for jsonl_file in custom_root.rglob("*.jsonl"):
            try:
                # Validate that found file is within the custom root (not outside via symlink)
                if not jsonl_file.resolve().is_relative_to(custom_root):
                    logger.warning(f"Skipping {jsonl_file} - outside custom root")
                    continue

                with open(jsonl_file) as f:
                    for line in f:
                        if session_id in line:
                            logger.debug(f"Found session_id via explicit config: {jsonl_file}")
                            return jsonl_file
            except OSError as e:
                logger.warning(f"Error reading {jsonl_file}: {e}")
                continue

        raise FileNotFoundError(
            f"No JSONL file containing session_id {session_id} in {custom_root}"
        )

    def resolve(self, session_data: dict[str, str], project_root: Path) -> Path:
        """
        Layered transcript resolution with security validation.

        Resolution order:
        0. Hook-provided path (deterministic, from clockin)
        1. Temporal beacon (scan recent files for session_id)
        2. Metadata inversion (match project_root via project_config.json)
        3. Explicit config (CLAUDE_TRANSCRIPT_DIR env var)
        4. Legacy fallback (not implemented - raises)

        Args:
            session_data: Session metadata dict
            project_root: Project root directory

        Returns:
            Path to session JSONL file

        Raises:
            FileNotFoundError: If no transcript found via any method
        """
        session_id = session_data.get("session_id", "")

        # Determine custom root from env var (used for all layers)
        custom_root_str = os.environ.get("CLAUDE_TRANSCRIPT_DIR")
        custom_root = Path(custom_root_str) if custom_root_str else None

        # Layer 0: Hook-provided path (existing behavior - highest priority)
        if session_data.get("transcript_path"):
            provided = Path(session_data["transcript_path"])

            # Security: validate hook-provided path BEFORE checking existence
            # This prevents path traversal attacks via malicious session.json
            try:
                validated = self._validate_path_containment(provided, custom_root)
            except ValueError as e:
                # SECURITY: Do NOT fall back when path traversal detected
                # This is a security violation, not a configuration issue
                logger.error(f"Path traversal attempt blocked: {e}")
                raise ValueError(f"Security violation: {e}") from e

            # If path passes containment check, verify it exists
            if validated.exists():
                logger.debug("Using hook-provided transcript path")
                return validated
            else:
                # Path is safe but missing - allow fallback to discovery
                logger.warning("Hook path missing, falling back to discovery")

        # Layer 1: Temporal beacon (efficient for recent sessions)
        if session_id:
            try:
                return self._find_by_temporal_beacon(session_id, custom_root)
            except (FileNotFoundError, ValueError) as e:
                logger.debug(f"Temporal beacon failed: {e}")

        # Layer 2: Metadata inversion (robust cross-project discovery)
        try:
            return self._find_by_metadata_inversion(project_root, custom_root)
        except (FileNotFoundError, ValueError) as e:
            logger.debug(f"Metadata inversion failed: {e}")

        # Layer 3: Explicit config (escape hatch for custom setups)
        if session_id:
            try:
                return self._find_by_explicit_config(session_id)
            except FileNotFoundError as e:
                logger.debug(f"Explicit config failed: {e}")

        # Layer 4: Legacy fallback not implemented in this version
        raise FileNotFoundError(
            f"Could not locate transcript for session {session_id} via any resolution layer"
        )
