"""Tests for scripts/ci/validate_canonical_paths.py.

TDD RED phase: written before the implementation exists.

Behaviour contract:
- Exit 0 when all staged .oct.md files have a META.CANONICAL or META.SOURCE
  whose value matches the file's repo-relative path (normalised posix).
- Exit 0 when SOURCE::legacy or CANONICAL::legacy is declared (bypass for
  files pending cleanup).
- Exit 1 when any file declares neither field, or the declared value does
  not match the file's actual location.
- Non-.oct.md files passed as positional args are silently ignored.
- Exit 0 with SKIP message when no .oct.md files are found.
- All failures are reported together (not fail-fast on first error).
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_oct_md(root: Path, rel_path: str, meta_lines: str) -> Path:
    """Create a minimal .oct.md file with the given META body under root."""
    file = root / rel_path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(
        f"===DOC===\nMETA:\n{meta_lines}\n§1::CONTENT\n  VALUE::test\n===END===\n",
        encoding="utf-8",
    )
    return file


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestValidateCanonicalPaths:
    """Unit tests for validate_canonical_paths.main() and helpers."""

    # ------------------------------------------------------------------
    # PASS cases
    # ------------------------------------------------------------------

    def test_pass_matching_source_quoted(self, tmp_path: Path) -> None:
        """SOURCE with quoted value matching repo-relative path → pass."""
        rel = "src/hestai_mcp/_bundled_hub/standards/rules/some-rule.oct.md"
        _write_oct_md(tmp_path, rel, f'  SOURCE::"{rel}"\n')
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_pass_matching_canonical_unquoted(self, tmp_path: Path) -> None:
        """CANONICAL without quotes matching repo-relative path → pass."""
        rel = ".hestai/rules/hub-authoring-rules.oct.md"
        _write_oct_md(tmp_path, rel, f"  CANONICAL::{rel}\n")
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_pass_source_legacy_unquoted(self, tmp_path: Path) -> None:
        """SOURCE::legacy (unquoted) bypasses validation."""
        rel = "debates/2025-12-24-old-debate.oct.md"
        _write_oct_md(tmp_path, rel, "  SOURCE::legacy\n")
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_pass_source_legacy_quoted(self, tmp_path: Path) -> None:
        """SOURCE::"legacy" (quoted) also bypasses validation."""
        rel = "debates/2025-12-24-old-debate.oct.md"
        _write_oct_md(tmp_path, rel, '  SOURCE::"legacy"\n')
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_pass_canonical_legacy(self, tmp_path: Path) -> None:
        """CANONICAL::legacy bypasses validation."""
        rel = "src/hestai_mcp/_bundled_hub/library/agents/old.oct.md"
        _write_oct_md(tmp_path, rel, "  CANONICAL::legacy\n")
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_pass_canonical_deployed_source_matches(self, tmp_path: Path) -> None:
        """bundled_hub file: CANONICAL points to .hestai-sys/ (deployed),
        SOURCE matches actual file path → pass (at least one field matches)."""
        rel = "src/hestai_mcp/_bundled_hub/standards/rules/visibility-rules.oct.md"
        meta = (
            '  CANONICAL::".hestai-sys/standards/rules/visibility-rules.oct.md"\n'
            f'  SOURCE::"{rel}"\n'
        )
        _write_oct_md(tmp_path, rel, meta)
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_pass_dot_slash_prefix_in_value(self, tmp_path: Path) -> None:
        """SOURCE::"./src/foo/bar.oct.md" normalises to src/foo/bar.oct.md → pass."""
        rel = "src/foo/bar.oct.md"
        _write_oct_md(tmp_path, rel, '  SOURCE::"./src/foo/bar.oct.md"\n')
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_skip_non_oct_md_files(self, tmp_path: Path) -> None:
        """Non-.oct.md files passed as positional args are ignored."""
        md = tmp_path / "docs" / "guide.md"
        md.parent.mkdir(parents=True)
        md.write_text("# Guide\n")
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), "docs/guide.md"]) == 0

    def test_empty_file_list_passes(self, tmp_path: Path) -> None:
        """No files → exit 0 with SKIP message."""
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path)]) == 0

    # ------------------------------------------------------------------
    # FAIL cases
    # ------------------------------------------------------------------

    def test_fail_no_canonical_no_source(self, tmp_path: Path) -> None:
        """File with no CANONICAL or SOURCE → fail."""
        rel = "src/hestai_mcp/_bundled_hub/library/agents/agent.oct.md"
        _write_oct_md(tmp_path, rel, '  TYPE::AGENT_DEFINITION\n  VERSION::"1.0"\n')
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 1

    def test_fail_source_wrong_path(self, tmp_path: Path) -> None:
        """SOURCE declared but doesn't match file's actual path → fail."""
        rel = "src/foo/actual.oct.md"
        _write_oct_md(tmp_path, rel, '  SOURCE::"src/foo/wrong-name.oct.md"\n')
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 1

    def test_fail_canonical_wrong_path(self, tmp_path: Path) -> None:
        """CANONICAL declared but doesn't match file's actual path (and no SOURCE) → fail."""
        rel = ".hestai/rules/rule.oct.md"
        _write_oct_md(tmp_path, rel, '  CANONICAL::".hestai/rules/other-rule.oct.md"\n')
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 1

    def test_fail_semantic_source_no_canonical(self, tmp_path: Path) -> None:
        """Debate file with SOURCE as content provenance (not a path) → fail."""
        rel = "debates/2025-12-24-some-debate.oct.md"
        _write_oct_md(tmp_path, rel, "  SOURCE::system_steward_analysis+LLM_research[2025-12-18]\n")
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 1

    def test_fail_multiple_files_all_reported(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Multiple failing files: all reported, exit 1."""
        paths = ["src/a.oct.md", "src/b.oct.md"]
        for p in paths:
            _write_oct_md(tmp_path, p, "  TYPE::AGENT_DEFINITION\n")
        from scripts.ci.validate_canonical_paths import main

        result = main(["--repo-root", str(tmp_path)] + paths)
        assert result == 1
        captured = capsys.readouterr()
        assert "src/a.oct.md" in captured.err
        assert "src/b.oct.md" in captured.err

    def test_fail_partial_batch_exit_1(self, tmp_path: Path) -> None:
        """One passing + one failing file → exit 1."""
        good = "src/good.oct.md"
        bad = "src/bad.oct.md"
        _write_oct_md(tmp_path, good, f'  SOURCE::"{good}"\n')
        _write_oct_md(tmp_path, bad, "  TYPE::STANDARD\n")
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), good, bad]) == 1

    # ------------------------------------------------------------------
    # Internal helper tests
    # ------------------------------------------------------------------

    def test_extract_meta_fields_quoted(self, tmp_path: Path) -> None:
        """_extract_meta_fields parses quoted CANONICAL and SOURCE values."""
        from scripts.ci.validate_canonical_paths import _extract_meta_fields

        content = (
            "===DOC===\n"
            "META:\n"
            '  CANONICAL::".hestai-sys/foo/bar.oct.md"\n'
            '  SOURCE::"src/foo/bar.oct.md"\n'
            "§1::SECTION\n===END===\n"
        )
        fields = _extract_meta_fields(content)
        assert fields.get("CANONICAL") == ".hestai-sys/foo/bar.oct.md"
        assert fields.get("SOURCE") == "src/foo/bar.oct.md"

    def test_extract_meta_fields_unquoted(self, tmp_path: Path) -> None:
        """_extract_meta_fields parses unquoted CANONICAL values."""
        from scripts.ci.validate_canonical_paths import _extract_meta_fields

        content = (
            "===DOC===\n"
            "META:\n"
            "  CANONICAL::.hestai/rules/hub-authoring-rules.oct.md\n"
            "§1::SECTION\n===END===\n"
        )
        fields = _extract_meta_fields(content)
        assert fields.get("CANONICAL") == ".hestai/rules/hub-authoring-rules.oct.md"

    def test_extract_meta_fields_legacy(self, tmp_path: Path) -> None:
        """_extract_meta_fields parses SOURCE::legacy."""
        from scripts.ci.validate_canonical_paths import _extract_meta_fields

        content = "===DOC===\nMETA:\n  SOURCE::legacy\n§1::SECTION\n===END===\n"
        fields = _extract_meta_fields(content)
        assert fields.get("SOURCE") == "legacy"

    def test_extract_meta_fields_stops_at_section(self, tmp_path: Path) -> None:
        """_extract_meta_fields does not parse SOURCE in body sections."""
        from scripts.ci.validate_canonical_paths import _extract_meta_fields

        content = (
            "===DOC===\n"
            "META:\n"
            "  TYPE::STANDARD\n"
            "§1::SECTION\n"
            '  SOURCE::"should-not-be-parsed.oct.md"\n'
            "===END===\n"
        )
        fields = _extract_meta_fields(content)
        assert "SOURCE" not in fields

    def test_normalize_path_strips_dot_slash(self) -> None:
        """_normalize_path strips leading ./ for comparison."""
        from scripts.ci.validate_canonical_paths import _normalize_path

        assert _normalize_path("./src/foo/bar.oct.md") == "src/foo/bar.oct.md"
        assert _normalize_path("src/foo/bar.oct.md") == "src/foo/bar.oct.md"
        assert _normalize_path(".hestai/rules/foo.oct.md") == ".hestai/rules/foo.oct.md"

    # ------------------------------------------------------------------
    # CRS rework: edge cases identified in review
    # ------------------------------------------------------------------

    def test_pass_root_level_file_no_slash(self, tmp_path: Path) -> None:
        """Root-level .oct.md with SOURCE::"root.oct.md" (no /) must pass.

        The '/' guard in the original implementation incorrectly blocked root
        files whose SOURCE value contains no path separator.
        """
        rel = "root.oct.md"
        _write_oct_md(tmp_path, rel, f'  SOURCE::"{rel}"\n')
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_pass_meta_with_blank_line_between_fields(self, tmp_path: Path) -> None:
        """Blank line inside META block must not truncate field extraction.

        The original _RE_META_BLOCK regex required every line to be indented,
        stopping capture at the first blank line and silently missing subsequent
        CANONICAL/SOURCE declarations.
        """
        rel = "src/foo/spaced.oct.md"
        (tmp_path / "src" / "foo").mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(
            "===DOC===\n"
            "META:\n"
            "  TYPE::STANDARD\n"
            "\n"
            f'  SOURCE::"{rel}"\n'
            "§1::CONTENT\n"
            "  VALUE::test\n"
            "===END===\n",
            encoding="utf-8",
        )
        from scripts.ci.validate_canonical_paths import main

        assert main(["--repo-root", str(tmp_path), rel]) == 0

    def test_extract_meta_fields_blank_line_in_meta(self) -> None:
        """_extract_meta_fields must parse SOURCE even after a blank META line."""
        from scripts.ci.validate_canonical_paths import _extract_meta_fields

        content = (
            "===DOC===\n"
            "META:\n"
            "  TYPE::STANDARD\n"
            "\n"
            '  SOURCE::"src/foo/bar.oct.md"\n'
            "§1::SECTION\n"
            "===END===\n"
        )
        fields = _extract_meta_fields(content)
        assert fields.get("SOURCE") == "src/foo/bar.oct.md"
