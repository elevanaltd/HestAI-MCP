"""Tests for OCTAVE validation via the canonical octave-mcp package.

Replaces the prior tests that loaded a vendored ``octave-validator.py`` script
via ``spec_from_file_location``. After Phase 3 of #406 the vendored validator
has been retired; CI, pre-commit, and consumers now invoke the canonical
``octave validate`` CLI shipped by the ``octave-mcp`` package directly.

This module asserts upstream-package behaviour that consumers depend on:
- ``octave_mcp.parse`` and ``parse_with_warnings`` accept SKILL and
  AGENT_DEFINITION documents that HestAI authors produce.
- ``octave validate`` CLI returns expected exit codes for VALIDATED,
  UNVALIDATED, and INVALID outcomes.
- ``Validator`` + ``load_schema_by_name`` resolve the built-in HestAI
  document schemas (META, SKILL, AGENT_DEFINITION).

These mirror the contract test pattern in ``test_octave_mcp_compat.py``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

pytest.importorskip("octave_mcp", reason="octave-mcp not installed")


# --- Helpers ---


def _make_skill_doc(extra_meta: str = "") -> str:
    """Build a minimal SKILL-type OCTAVE document."""
    extra = f"\n{extra_meta}" if extra_meta else ""
    return (
        "===TEST_SKILL===\n"
        "META:\n"
        "  TYPE::SKILL\n"
        '  VERSION::"1.0.0"\n'
        '  PURPOSE::"Test skill"'
        f"{extra}\n"
        "CONTENT::value\n"
        "===END==="
    )


def _make_agent_doc(extra_meta: str = "") -> str:
    """Build a minimal AGENT_DEFINITION-type OCTAVE document."""
    extra = f"\n{extra_meta}" if extra_meta else ""
    return (
        "===TEST_AGENT===\n"
        "META:\n"
        "  TYPE::AGENT_DEFINITION\n"
        '  VERSION::"1.0.0"\n'
        '  PURPOSE::"Test agent"'
        f"{extra}\n"
        "CONTENT::value\n"
        "===END==="
    )


@pytest.fixture
def octave_cli() -> list[str]:
    """Return the command prefix used by CI/pre-commit to invoke the canonical CLI.

    Returns ``[sys.executable, "-m", "octave_mcp.cli.main"]`` which mirrors the
    exact form used in ``.github/workflows/ci.yml`` and ``.pre-commit-config.yaml``
    after Phase 3 of #406. This dodges PATH collisions with unrelated ``octave``
    binaries (e.g. Homebrew GNU Octave math package).

    Skips the test if the ``octave_mcp`` package is not importable from the
    active interpreter.
    """
    import sys

    # Probe importability up-front so the skip happens at fixture resolution time.
    probe = subprocess.run(
        [sys.executable, "-c", "import octave_mcp"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if probe.returncode != 0:
        pytest.skip("octave_mcp not importable from active interpreter")
    return [sys.executable, "-m", "octave_mcp.cli.main"]


# --- Python API: parse + parse_with_warnings ---


@pytest.mark.unit
class TestOctaveMcpParseApi:
    """The canonical parse APIs accept HestAI's SKILL/AGENT document shapes."""

    def test_parse_accepts_skill_document(self) -> None:
        from octave_mcp import parse

        doc = parse(_make_skill_doc())
        assert doc is not None

    def test_parse_accepts_agent_document(self) -> None:
        from octave_mcp import parse

        doc = parse(_make_agent_doc())
        assert doc is not None

    def test_parse_with_warnings_returns_doc_and_warnings(self) -> None:
        from octave_mcp import parse_with_warnings

        doc, warnings = parse_with_warnings(_make_skill_doc())
        assert doc is not None
        assert isinstance(warnings, list)

    def test_parse_with_warnings_accepts_v6_meta_fields(self) -> None:
        """Documents bearing v6 META fields parse without structural error."""
        from octave_mcp import parse_with_warnings

        meta_extras = (
            '  OCTAVE::"Olympian Common Text And Vocabulary Engine"\n'
            "  CONTRACT::HOLOGRAPHIC<JIT_GRAMMAR_COMPILATION>\n"
            "  TAGS::[dependency,octave,alignment]"
        )
        doc, _warnings = parse_with_warnings(_make_skill_doc(meta_extras))
        assert doc is not None


# --- Python API: Validator + schema loader ---


@pytest.mark.unit
class TestOctaveMcpValidatorApi:
    """Built-in HestAI schemas are resolvable and produce a Validator."""

    @pytest.mark.parametrize("schema_name", ["META", "SKILL", "AGENT_DEFINITION"])
    def test_load_schema_by_name_resolves_builtin(self, schema_name: str) -> None:
        from octave_mcp.schemas.loader import load_schema_by_name

        schema = load_schema_by_name(schema_name)
        assert schema is not None, f"Built-in schema {schema_name!r} should resolve"

    def test_validator_constructs_with_no_schema(self) -> None:
        from octave_mcp.core.validator import Validator

        v = Validator()
        assert v is not None


# --- CLI: octave validate exit codes ---


@pytest.mark.unit
class TestOctaveCliValidate:
    """The canonical CLI used by CI/pre-commit returns expected exit codes."""

    def _run(
        self, octave_cli: list[str], *args: str, stdin: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*octave_cli, "validate", *args],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def test_valid_skill_via_stdin_unvalidated_exit_zero(self, octave_cli: list[str]) -> None:
        """Well-formed SKILL doc without --schema returns UNVALIDATED, exit 0."""
        result = self._run(octave_cli, "--stdin", stdin=_make_skill_doc())
        assert result.returncode == 0, result.stderr
        assert "validation_status: UNVALIDATED" in result.stdout

    def test_valid_doc_with_builtin_meta_schema_validated_exit_zero(
        self, octave_cli: list[str]
    ) -> None:
        """A doc passed --schema META resolves the built-in dict schema and validates."""
        result = self._run(octave_cli, "--stdin", "--schema", "META", stdin=_make_skill_doc())
        assert result.returncode == 0, result.stderr
        # META is the canonical builtin dict schema; resolution yields VALIDATED.
        assert "validation_status: VALIDATED" in result.stdout

    def test_non_builtin_schema_remains_unvalidated_exit_zero(self, octave_cli: list[str]) -> None:
        """--schema SKILL is not a builtin dict; CLI degrades to UNVALIDATED, exit 0.

        Documents the current CLI contract: only ``get_builtin_schema`` keys
        (notably META) produce VALIDATED via the CLI; other names like SKILL
        and AGENT_DEFINITION fall through. The Python API
        (``load_schema_by_name``) DOES resolve them — see
        ``TestOctaveMcpValidatorApi`` above.
        """
        result = self._run(octave_cli, "--stdin", "--schema", "SKILL", stdin=_make_skill_doc())
        assert result.returncode == 0, result.stderr
        assert "validation_status: UNVALIDATED" in result.stdout

    def test_malformed_document_exit_nonzero(self, octave_cli: list[str]) -> None:
        """A document that fails the strict parser exits with non-zero."""
        garbage = "===BAD===\nMETA:\n  TYPE::SKILL\nUNCLOSED::(oops\n===END==="
        result = self._run(octave_cli, "--stdin", stdin=garbage)
        assert result.returncode != 0

    def test_validate_file_path_argument(self, octave_cli: list[str], tmp_path: Path) -> None:
        """The CLI accepts a positional file path (matches CI's loop form)."""
        doc_path = tmp_path / "sample.oct.md"
        doc_path.write_text(_make_agent_doc(), encoding="utf-8")
        result = self._run(octave_cli, str(doc_path))
        assert result.returncode == 0, result.stderr
        assert "validation_status:" in result.stdout
