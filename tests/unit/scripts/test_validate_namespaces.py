"""
Tests for scripts/validate_namespaces.py — pre-commit hook for namespace validation.

TDD RED phase: These tests are written before the script exists.

Behaviour contract:
- Exit 0 when all files are valid (no errors, no warnings)
- Exit 0 (not blocked) when files have only warnings (missing namespace declaration)
- Exit 1 when a file has errors (e.g., file not found)
- Exit 0 when no files are passed
- Print WARNING: prefix for warnings
- Print summary line at the end
"""

import subprocess
import sys
from pathlib import Path

import pytest


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the validate_namespaces script with the given arguments."""
    script = Path(__file__).parent.parent.parent.parent / "scripts" / "validate_namespaces.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
    )


@pytest.mark.unit
class TestValidateNamespacesScript:
    """Tests for the validate_namespaces.py pre-commit hook script."""

    def test_exit_0_when_no_files_passed(self) -> None:
        """Script exits 0 silently when called with no arguments."""
        result = run_script()
        assert result.returncode == 0

    def test_exit_0_for_valid_file_with_namespace(self, tmp_path: Path) -> None:
        """Script exits 0 when all files have valid namespace declarations."""
        f = tmp_path / "valid.md"
        f.write_text("META:\n  NAMESPACE::SYS\n\nClean content with no issues.")
        result = run_script(str(f))
        assert result.returncode == 0

    def test_exit_0_for_warning_only_file(self, tmp_path: Path) -> None:
        """Script exits 0 (not blocked) when file has only warnings (missing namespace)."""
        f = tmp_path / "no_namespace.md"
        f.write_text("# A document\n\nNo namespace declared here.")
        result = run_script(str(f))
        assert result.returncode == 0

    def test_warnings_are_printed_with_prefix(self, tmp_path: Path) -> None:
        """Warnings are printed with WARNING: prefix to stdout or stderr."""
        f = tmp_path / "no_namespace.md"
        f.write_text("# A document\n\nNo namespace declared here.")
        result = run_script(str(f))
        combined = result.stdout + result.stderr
        assert "WARNING:" in combined

    def test_exit_1_for_file_not_found(self, tmp_path: Path) -> None:
        """Script exits 1 when a file does not exist (hard error)."""
        missing = tmp_path / "nonexistent.md"
        result = run_script(str(missing))
        assert result.returncode == 1

    def test_summary_line_printed(self, tmp_path: Path) -> None:
        """A summary line is printed at the end of the run."""
        f = tmp_path / "doc.md"
        f.write_text("META:\n  NAMESPACE::PROD\n\nSome content.")
        result = run_script(str(f))
        combined = result.stdout + result.stderr
        # Summary should mention files checked
        assert "1 file" in combined or "files checked" in combined.lower()

    def test_multiple_files_all_valid(self, tmp_path: Path) -> None:
        """Script exits 0 when multiple valid files are passed."""
        f1 = tmp_path / "doc1.md"
        f1.write_text("META:\n  NAMESPACE::SYS\n\nContent.")
        f2 = tmp_path / "doc2.md"
        f2.write_text("META:\n  NAMESPACE::PROD\n\nContent.")
        result = run_script(str(f1), str(f2))
        assert result.returncode == 0

    def test_multiple_files_one_error_exits_1(self, tmp_path: Path) -> None:
        """Script exits 1 when any file has an error, even if others are valid."""
        f1 = tmp_path / "valid.md"
        f1.write_text("META:\n  NAMESPACE::SYS\n\nContent.")
        missing = tmp_path / "nonexistent.md"
        result = run_script(str(f1), str(missing))
        assert result.returncode == 1

    def test_warning_does_not_cause_exit_1_even_with_valid_files(self, tmp_path: Path) -> None:
        """Mixed warning-only and valid files both exit 0 (warnings do not block)."""
        f1 = tmp_path / "valid.md"
        f1.write_text("META:\n  NAMESPACE::SYS\n\nContent.")
        f2 = tmp_path / "warn_only.md"
        f2.write_text("# No namespace\n\nJust content.")
        result = run_script(str(f1), str(f2))
        assert result.returncode == 0

    def test_summary_shows_correct_file_count(self, tmp_path: Path) -> None:
        """Summary line reports the number of files checked."""
        f1 = tmp_path / "doc1.md"
        f1.write_text("META:\n  NAMESPACE::SYS\n\nContent.")
        f2 = tmp_path / "doc2.md"
        f2.write_text("META:\n  NAMESPACE::PROD\n\nContent.")
        f3 = tmp_path / "doc3.md"
        f3.write_text("# No namespace\n\nContent.")
        result = run_script(str(f1), str(f2), str(f3))
        combined = result.stdout + result.stderr
        assert "3" in combined
