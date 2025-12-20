"""
Security module for session archive redaction.

Provides RedactionEngine class for detecting and redacting sensitive data
from session transcripts before archival to prevent credential leakage.

Fail-closed design: If redaction fails, archival is blocked.
"""

import re
from pathlib import Path
from re import Pattern


class RedactionEngine:
    """
    Engine for redacting sensitive data from text content.

    Phase 1 patterns (high-confidence, low false-positive):
    - AI API keys (sk-...)
    - AWS access keys (AKIA..., ASIA...)
    - Private keys (PEM format)
    - Bearer tokens
    - Database passwords in connection strings
    """

    # Pre-compiled regex patterns for performance
    PATTERNS: dict[str, tuple[Pattern[str], str]] = {
        # AI API keys: sk- followed by 20+ alphanumeric chars
        "ai_api_key": (
            re.compile(r"sk-[a-zA-Z0-9]{20,}"),
            "[REDACTED_API_KEY]",
        ),
        # AWS access keys: AKIA or ASIA followed by 16 uppercase alphanumeric
        "aws_key": (
            re.compile(r"(AKIA|ASIA)[0-9A-Z]{16}"),
            "[REDACTED_AWS_KEY]",
        ),
        # PEM private keys: entire BEGIN/END block
        "private_key": (
            re.compile(
                r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----",
                re.DOTALL,
            ),
            "[REDACTED_PRIVATE_KEY]",
        ),
        # Bearer tokens: Bearer followed by base64-like characters
        "bearer_token": (
            re.compile(r"Bearer [a-zA-Z0-9\-\._~\+\/]+=*"),
            "Bearer [REDACTED_BEARER]",
        ),
        # Database passwords in connection strings
        # Matches: scheme://user:password@host:port/db
        # Uses negative lookahead to find the LAST @ before host/port/path
        # Pattern breakdown:
        #   (\w+://[^:]+:) - Capture scheme://user:
        #   (.+)           - Capture password (greedy, everything)
        #   (@)            - Capture the @ separator
        #   (?=[^@]*$)     - Lookahead: ensure no more @ after this one (= last @)
        #   This ensures password can contain @ symbols but we match to the final @
        "db_password": (
            re.compile(r"(\w+://[^:]+:)(.+)(@)(?=[^@]*$)"),
            r"\1[REDACTED_PASSWORD]\3",
        ),
    }

    @classmethod
    def redact_content(cls, text: str) -> str:
        """
        Redact sensitive data from text content.

        Args:
            text: Input text that may contain secrets

        Returns:
            Text with secrets replaced by redaction markers
        """
        result = text

        for _pattern_name, (pattern, replacement) in cls.PATTERNS.items():
            result = pattern.sub(replacement, result)

        return result

    @classmethod
    def copy_and_redact(cls, src: Path, dst: Path) -> None:
        """
        Copy file from src to dst with redaction applied.

        Stream-based processing for memory efficiency with large files.
        Processes line-by-line to avoid loading entire file into memory.
        Fail-closed: raises exception if source doesn't exist or redaction fails.
        If redaction fails, destination file is not created (or deleted if partially written).

        Args:
            src: Source file path
            dst: Destination file path

        Raises:
            FileNotFoundError: If source file doesn't exist
            Exception: If redaction fails (destination not created)
        """
        # Fail closed: verify source exists
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")

        # Stream line-by-line for memory efficiency (HIGH-1)
        # This prevents loading multi-MB session files entirely into memory
        # Fail-closed: if redaction fails, clean up partial output
        try:
            with (
                open(src, encoding="utf-8") as src_file,
                open(dst, "w", encoding="utf-8") as dst_file,
            ):
                for line in src_file:
                    redacted_line = cls.redact_content(line)
                    dst_file.write(redacted_line)
        except Exception:
            # Fail-closed: remove partial output if redaction failed
            if dst.exists():
                dst.unlink()
            raise
