"""
Tests for RedactionEngine - Security-critical secret detection and redaction.

TDD Discipline:
1. RED: Write failing tests first
2. GREEN: Minimal implementation to pass
3. REFACTOR: Improve while tests pass

Security Context:
- Session transcripts may contain API keys, tokens, credentials
- Archives must redact secrets BEFORE writing to disk
- Fail-closed: If redaction fails, archival must be BLOCKED
"""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestRedactionPatterns:
    """Test detection and redaction of sensitive patterns."""

    def test_redacts_ai_api_keys(self):
        """Detects and redacts AI API keys (sk-... pattern)."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        text = "Using API key sk-1234567890abcdefghij for requests"
        redacted = RedactionEngine.redact_content(text)

        assert "sk-1234567890abcdefghij" not in redacted
        assert "[REDACTED_API_KEY]" in redacted

    def test_redacts_aws_access_keys(self):
        """Detects and redacts AWS access keys (AKIA/ASIA pattern)."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        redacted = RedactionEngine.redact_content(text)

        assert "AKIAIOSFODNN7EXAMPLE" not in redacted
        assert "[REDACTED_AWS_KEY]" in redacted

    def test_redacts_private_keys(self):
        """Detects and redacts PEM private keys."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        text = """
        -----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEA1234567890
        -----END RSA PRIVATE KEY-----
        """
        redacted = RedactionEngine.redact_content(text)

        assert "MIIEpAIBAAKCAQEA1234567890" not in redacted
        assert "[REDACTED_PRIVATE_KEY]" in redacted

    def test_redacts_bearer_tokens(self):
        """Detects and redacts Bearer tokens."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        redacted = RedactionEngine.redact_content(text)

        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in redacted
        assert "Bearer [REDACTED_BEARER]" in redacted

    def test_redacts_database_passwords(self):
        """Detects and redacts passwords in connection strings."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        text = "postgresql://user:secret_password@localhost:5432/db"
        redacted = RedactionEngine.redact_content(text)

        assert "secret_password" not in redacted
        assert "[REDACTED_PASSWORD]" in redacted
        assert "postgresql://user:" in redacted  # Preserve structure
        assert "@localhost:5432/db" in redacted

    def test_preserves_non_sensitive_content(self):
        """Normal content passes through unchanged."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        text = "This is normal log output with no secrets"
        redacted = RedactionEngine.redact_content(text)

        assert redacted == text


@pytest.mark.unit
class TestCopyAndRedact:
    """Test file copying with redaction applied."""

    def test_copies_file_with_redaction(self, tmp_path: Path):
        """Copies file line-by-line with secrets redacted."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        # Create source file with secrets (realistic API key length: 20+ chars)
        src = tmp_path / "source.jsonl"
        src.write_text(
            "Line 1: Normal\nLine 2: API key sk-1234567890abcdefghij123\nLine 3: Normal\n"
        )

        dst = tmp_path / "archive.jsonl"

        # Copy with redaction
        RedactionEngine.copy_and_redact(src, dst)

        # Verify redaction applied
        result = dst.read_text()
        assert "sk-1234567890abcdefghij123" not in result
        assert "[REDACTED_API_KEY]" in result
        assert "Line 1: Normal" in result
        assert "Line 3: Normal" in result

    def test_fails_closed_on_missing_source(self, tmp_path: Path):
        """Raises FileNotFoundError if source doesn't exist (fail-closed)."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        src = tmp_path / "nonexistent.jsonl"
        dst = tmp_path / "archive.jsonl"

        with pytest.raises(FileNotFoundError, match="Source file not found"):
            RedactionEngine.copy_and_redact(src, dst)

        # Verify destination not created
        assert not dst.exists()

    def test_cleans_up_on_redaction_failure(self, tmp_path: Path):
        """Removes partial output if redaction fails (fail-closed)."""
        from unittest.mock import patch

        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        src = tmp_path / "source.jsonl"
        src.write_text("test content\n")
        dst = tmp_path / "archive.jsonl"

        # Simulate redaction failure mid-copy
        with (
            patch.object(
                RedactionEngine, "redact_content", side_effect=Exception("Redaction failed")
            ),
            pytest.raises(Exception, match="Redaction failed"),
        ):
            RedactionEngine.copy_and_redact(src, dst)

        # Verify destination cleaned up
        assert not dst.exists()

    def test_handles_large_files_efficiently(self, tmp_path: Path):
        """Processes large files line-by-line (memory efficiency)."""
        from hestai_mcp.mcp.tools.shared.security import RedactionEngine

        # Create large source file (1000 lines)
        src = tmp_path / "large.jsonl"
        lines = [f"Line {i}: Normal content\n" for i in range(1000)]
        lines[500] = "Line 500: API key sk-1234567890abcdefghij456\n"  # Secret in middle
        src.write_text("".join(lines))

        dst = tmp_path / "archive.jsonl"

        # Copy with redaction
        RedactionEngine.copy_and_redact(src, dst)

        # Verify redaction
        result = dst.read_text()
        assert "sk-1234567890abcdefghij456" not in result
        assert "[REDACTED_API_KEY]" in result
        assert "Line 999: Normal content" in result
