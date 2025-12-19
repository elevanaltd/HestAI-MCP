"""
Tests for clock_out OCTAVE compression features (Features 2-5).

Test Coverage:
- Feature 2: OCTAVE compression (compress_to_octave)
- Feature 3: Context extraction (extract_context_from_octave)
- Feature 4: Verification claims (verify_context_claims)
- Feature 5: Learnings index (extract_learnings_keys, append_to_learnings_index)
"""

import json
from pathlib import Path
import pytest


@pytest.mark.unit
class TestOctaveCompression:
    """Test Feature 2: OCTAVE compression with graceful degradation."""

    def test_compress_to_octave_function_exists(self):
        """Verify compress_to_octave function exists and is callable."""
        from hestai_mcp.mcp.tools.shared.compression import compress_to_octave
        import inspect

        # Verify function exists
        assert callable(compress_to_octave)

        # Verify it's async
        assert inspect.iscoroutinefunction(compress_to_octave)

    def test_load_compression_prompt(self):
        """Compression prompt template loads successfully."""
        from hestai_mcp.mcp.tools.shared.compression import load_compression_prompt

        prompt = load_compression_prompt()

        assert prompt is not None
        assert "SESSION_COMPRESSION_PROTOCOL" in prompt
        assert "OCTAVE" in prompt
        assert "DECISIONS" in prompt
        assert "BLOCKERS" in prompt
        assert "LEARNINGS" in prompt


@pytest.mark.unit
class TestContextExtraction:
    """Test Feature 3: Context extraction from OCTAVE content."""

    def test_extract_context_parses_sections(self):
        """Extracts DECISIONS, OUTCOMES, BLOCKERS from OCTAVE content."""
        from hestai_mcp.mcp.tools.shared.context_extraction import extract_context_from_octave

        octave_content = """
===SESSION_COMPRESSION===

DECISIONS::[
  DECISION_1::BECAUSE[TDD_discipline]→write_test_first→verified_behavior,
  DECISION_2::BECAUSE[security]→apply_redaction→prevent_credential_leakage
]

OUTCOMES::[
  completed_clock_out_integration[4_features_added],
  achieved_60%_compression[baseline_1000_lines→400_lines]
]

BLOCKERS::[
  path_resolution⊗resolved[used_TranscriptPathResolver],
  async_testing⊗blocked[need_pytest_asyncio]
]

===END_SESSION_COMPRESSION===
"""

        result = extract_context_from_octave(octave_content)

        assert result is not None
        assert "DECISIONS:" in result
        assert "DECISION_1" in result
        assert "OUTCOMES:" in result
        assert "BLOCKERS:" in result
        assert "path_resolution⊗resolved" in result

    def test_extract_context_returns_none_for_empty(self):
        """Returns None if no extractable content."""
        from hestai_mcp.mcp.tools.shared.context_extraction import extract_context_from_octave

        result = extract_context_from_octave("")
        assert result is None

        result = extract_context_from_octave("Some content without OCTAVE sections")
        assert result is None


@pytest.mark.unit
class TestVerificationClaims:
    """Test Feature 4: Verification of OCTAVE content claims."""

    def test_verify_claims_detects_missing_files(self, tmp_path: Path):
        """Detects FILES_MODIFIED references to non-existent files."""
        from hestai_mcp.mcp.tools.shared.verification import verify_context_claims

        octave_content = """
FILES_MODIFIED::["src/existing.py", "src/nonexistent.py"]
"""

        # Create only one of the files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "existing.py").write_text("# exists")

        result = verify_context_claims(octave_content, tmp_path)

        assert result["passed"] is False
        assert len(result["issues"]) > 0
        assert any("nonexistent" in issue for issue in result["issues"])

    def test_verify_claims_passes_for_valid_files(self, tmp_path: Path):
        """Passes when all FILES_MODIFIED exist."""
        from hestai_mcp.mcp.tools.shared.verification import verify_context_claims

        octave_content = """
FILES_MODIFIED::["src/file1.py", "src/file2.py"]
"""

        # Create both files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "file1.py").write_text("# exists")
        (src_dir / "file2.py").write_text("# exists")

        result = verify_context_claims(octave_content, tmp_path)

        assert result["passed"] is True
        assert len(result["issues"]) == 0

    def test_verify_claims_detects_path_traversal(self, tmp_path: Path):
        """Detects path traversal attempts in file references."""
        from hestai_mcp.mcp.tools.shared.verification import verify_context_claims

        octave_content = """
FILES_MODIFIED::["../etc/passwd"]
"""

        result = verify_context_claims(octave_content, tmp_path)

        assert result["passed"] is False
        assert any("traversal" in issue.lower() for issue in result["issues"])

    def test_verify_claims_rejects_absolute_paths_in_files_modified(self, tmp_path: Path):
        """Rejects absolute paths in FILES_MODIFIED to prevent system file access."""
        from hestai_mcp.mcp.tools.shared.verification import verify_context_claims

        octave_content = """
===SESSION_COMPRESSION===
FILES_MODIFIED::[/etc/passwd]
LEARNINGS::[x]
===END===
"""

        result = verify_context_claims(octave_content, tmp_path)

        # Should fail due to absolute path
        assert result["passed"] is False
        assert len(result["issues"]) > 0
        assert any(
            "absolute" in issue.lower() or "/etc/passwd" in issue for issue in result["issues"]
        )

    def test_verify_claims_rejects_absolute_paths_in_markdown_links(self, tmp_path: Path):
        """Rejects absolute paths in markdown links to prevent system file references."""
        from hestai_mcp.mcp.tools.shared.verification import verify_context_claims

        octave_content = """
===SESSION_COMPRESSION===
LEARNINGS::[
  See configuration in [system file](/etc/hosts)
]
===END===
"""

        result = verify_context_claims(octave_content, tmp_path)

        # Should fail due to absolute path in markdown link
        assert result["passed"] is False
        assert len(result["issues"]) > 0
        assert any(
            "absolute" in issue.lower() or "/etc/hosts" in issue for issue in result["issues"]
        )

    def test_verify_claims_rejects_file_uri_absolute_paths(self, tmp_path: Path):
        """file:// URIs with absolute paths should fail."""
        from hestai_mcp.mcp.tools.shared.verification import verify_context_claims

        octave_content = """
===SESSION_COMPRESSION===
LEARNINGS::[
  see [x](file://localhost/etc/passwd)
]
===END===
"""

        result = verify_context_claims(octave_content, tmp_path)

        assert result["passed"] is False
        assert any(
            "absolute" in issue.lower() or "not allowed" in issue.lower()
            for issue in result["issues"]
        )

    def test_verify_claims_rejects_angle_bracket_absolute_paths(self, tmp_path: Path):
        """Angle-bracket wrapped absolute paths should fail."""
        from hestai_mcp.mcp.tools.shared.verification import verify_context_claims

        octave_content = """
===SESSION_COMPRESSION===
LEARNINGS::[
  see [x](</etc/passwd>)
]
===END===
"""

        result = verify_context_claims(octave_content, tmp_path)

        assert result["passed"] is False
        assert any(
            "absolute" in issue.lower() or "not allowed" in issue.lower()
            for issue in result["issues"]
        )


@pytest.mark.unit
class TestLearningsIndex:
    """Test Feature 5: Learnings index extraction and appending."""

    def test_extract_learnings_keys(self):
        """Extracts DECISION_*, BLOCKER_*, LEARNING_* keys."""
        from hestai_mcp.mcp.tools.shared.learnings_index import extract_learnings_keys

        octave_content = """
DECISIONS::[
  DECISION_1::BECAUSE[constraint]→choice→outcome,
  DECISION_2::BECAUSE[evidence]→choice→outcome
]

BLOCKERS::[
  path_issue⊗resolved[fixed_with_Path],
  async_bug⊗blocked[need_investigation]
]

LEARNINGS::[
  TDD_prevents_regressions→test_first→verified_behavior,
  graceful_degradation→better_than_hard_fail→user_experience
]
"""

        keys = extract_learnings_keys(octave_content)

        assert "decisions" in keys
        assert "blockers" in keys
        assert "learnings" in keys

        assert len(keys["decisions"]) == 2
        assert len(keys["blockers"]) == 2
        assert len(keys["learnings"]) == 2

        # Verify content
        assert "BECAUSE[constraint]→choice→outcome" in keys["decisions"][0]
        assert "path_issue⊗resolved" in keys["blockers"][0]
        assert "TDD_prevents_regressions" in keys["learnings"][0]

    def test_append_to_learnings_index(self, tmp_path: Path):
        """Appends learnings to JSONL index."""
        from hestai_mcp.mcp.tools.shared.learnings_index import append_to_learnings_index

        session_data = {
            "session_id": "test-123",
            "role": "implementation-lead",
            "duration": "2h",
            "focus": "clock_out",
        }

        keys = {
            "decisions": ["DECISION_1::test"],
            "blockers": ["blocker_1⊗resolved"],
            "learnings": ["learning_1"],
        }

        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()

        append_to_learnings_index(session_data, keys, archive_dir)

        # Verify JSONL was created
        index_path = archive_dir / "learnings-index.jsonl"
        assert index_path.exists()

        # Verify content
        content = index_path.read_text()
        entry = json.loads(content.strip())

        assert entry["session_id"] == "test-123"
        assert entry["role"] == "implementation-lead"
        assert len(entry["decisions"]) == 1
        assert len(entry["learnings"]) == 1
