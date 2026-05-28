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
- The retained ``_bundled_hub/tools/octave-validator.py`` deprecation stub
  warns on stderr and forwards faithfully to the canonical CLI.

These mirror the contract test pattern in ``test_octave_mcp_compat.py``.

Coverage boundary (per #406 Phase 3)
------------------------------------
Schema-enforcement *semantics* — the ``unknown_policy`` strict/warn/ignore
behaviour and exhaustive acceptance of the ~21 META fields — were owned by the
now-retired vendored validator and are now the responsibility of octave-mcp's
own test suite. This file does NOT re-implement or re-test those upstream rules.
It tests the INTEGRATION CONTRACT only: that HestAI invokes the canonical
CLI/Python API and gets correct pass/fail outcomes, correct schema resolution,
and a graceful deprecation path for the legacy ``.hestai-sys/tools/`` script
path that downstream consumers may still call. Any change to *how* a schema
accepts or rejects fields is verified upstream, not here.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("octave_mcp", reason="octave-mcp not installed")


# Path to the retained deprecation stub. The _bundled_hub tree is injected into
# .hestai-sys/ at MCP server startup, so this path mirrors the downstream
# .hestai-sys/tools/octave-validator.py that legacy callers may still invoke.
_STUB_PATH = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "hestai_mcp"
    / "_bundled_hub"
    / "tools"
    / "octave-validator.py"
)


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
        # Assert the parsed structure, not mere non-None: the document name and
        # the resolved META TYPE prove the SKILL doc parsed into a usable CST.
        assert doc.name == "TEST_SKILL"
        assert doc.meta["TYPE"] == "SKILL"
        assert len(doc.sections) >= 1

    def test_parse_accepts_agent_document(self) -> None:
        from octave_mcp import parse

        doc = parse(_make_agent_doc())
        assert doc.name == "TEST_AGENT"
        assert doc.meta["TYPE"] == "AGENT_DEFINITION"
        assert len(doc.sections) >= 1

    def test_parse_with_warnings_clean_doc_has_no_warnings(self) -> None:
        from octave_mcp import parse_with_warnings

        doc, warnings = parse_with_warnings(_make_skill_doc())
        assert doc.meta["TYPE"] == "SKILL"
        # A well-formed SKILL doc parses cleanly: zero lenient-parse warnings.
        assert warnings == []

    def test_parse_with_warnings_surfaces_lenient_parse_warning(self) -> None:
        """A bare identifier without an operator yields a concrete lenient-parse warning.

        ``A::a::b`` drops the trailing bare ``b`` and reports a
        ``bare_line_dropped`` lenient-parse warning. This asserts the SPECIFIC
        warning, not merely that ``warnings`` is a list.
        """
        from octave_mcp import parse_with_warnings

        bare_line_doc = (
            "===TEST_SKILL===\n"
            "META:\n"
            "  TYPE::SKILL\n"
            '  VERSION::"1.0.0"\n'
            "CONTENT::a::b\n"
            "===END==="
        )
        doc, warnings = parse_with_warnings(bare_line_doc)
        assert doc.meta["TYPE"] == "SKILL"
        assert len(warnings) == 1
        warning = warnings[0]
        assert warning["type"] == "lenient_parse"
        assert warning["subtype"] == "bare_line_dropped"

    def test_parse_with_warnings_accepts_v6_meta_fields(self) -> None:
        """Documents bearing v6 META fields parse without structural error."""
        from octave_mcp import parse_with_warnings

        meta_extras = (
            '  OCTAVE::"Olympian Common Text And Vocabulary Engine"\n'
            "  CONTRACT::HOLOGRAPHIC<JIT_GRAMMAR_COMPILATION>\n"
            "  TAGS::[dependency,octave,alignment]"
        )
        doc, warnings = parse_with_warnings(_make_skill_doc(meta_extras))
        # v6 META fields resolve into the meta dict without dropping the doc.
        assert doc.meta["TYPE"] == "SKILL"
        assert doc.meta["OCTAVE"] == "Olympian Common Text And Vocabulary Engine"
        assert all(w.get("type") != "error" for w in warnings)


# --- Python API: Validator + schema loader ---


@pytest.mark.unit
class TestOctaveMcpValidatorApi:
    """Built-in HestAI schemas are resolvable and enforce required fields."""

    @pytest.mark.parametrize("schema_name", ["META", "SKILL", "AGENT_DEFINITION"])
    def test_load_schema_by_name_resolves_builtin(self, schema_name: str) -> None:
        from octave_mcp.schemas.loader import load_schema_by_name

        schema = load_schema_by_name(schema_name)
        assert schema is not None, f"Built-in schema {schema_name!r} should resolve"

    def test_validator_accepts_valid_meta_document(self) -> None:
        """A Validator built on the META schema passes a conformant document.

        Replaces the prior vacuous ``Validator() is not None`` smoke test with a
        real ``validate()`` call asserting the conformant outcome (no errors).
        """
        from octave_mcp import parse
        from octave_mcp.core.validator import Validator
        from octave_mcp.schemas.loader import get_builtin_schema

        schema_def = get_builtin_schema("META")
        validator = Validator(schema=schema_def)
        doc = parse(_make_skill_doc())
        errors = validator.validate(doc, strict=False)
        assert errors == []

    def test_validator_rejects_meta_document_with_bad_enum(self) -> None:
        """The META schema rejects an out-of-range STATUS enum value.

        The builtin META schema constrains STATUS to one of
        DRAFT/ACTIVE/DEPRECATED; a value outside that set yields an E005 error.
        This proves the Validator enforces schema constraints (the failure side
        of the integration contract), complementing the passing case above.
        """
        from octave_mcp import parse
        from octave_mcp.core.validator import Validator
        from octave_mcp.schemas.loader import get_builtin_schema

        schema_def = get_builtin_schema("META")
        validator = Validator(schema=schema_def)
        bad_doc = parse(
            "===TEST_SKILL===\n"
            "META:\n"
            "  TYPE::SKILL\n"
            '  VERSION::"1.0.0"\n'
            "  STATUS::BOGUS\n"
            "CONTENT::value\n"
            "===END==="
        )
        errors = validator.validate(bad_doc, strict=False)
        assert errors, "STATUS::BOGUS must fail the META enum constraint"
        assert any(e.code == "E005" for e in errors)


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

    def test_schema_invalid_doc_reports_invalid_exit_nonzero(self, octave_cli: list[str]) -> None:
        """A doc that PARSES but VIOLATES its schema yields INVALID + non-zero exit.

        This is the semantic-validation-failure path distinct from a parse
        failure: the document is structurally well-formed (the strict parser
        accepts it) but its STATUS value is outside the META schema's enum, so
        ``validate`` flags it INVALID and the CLI exits 1.
        """
        bad_doc = (
            "===TEST_SKILL===\n"
            "META:\n"
            "  TYPE::SKILL\n"
            '  VERSION::"1.0.0"\n'
            "  STATUS::BOGUS\n"
            "CONTENT::value\n"
            "===END==="
        )
        result = self._run(octave_cli, "--stdin", "--schema", "META", stdin=bad_doc)
        assert result.returncode != 0
        assert "validation_status: INVALID" in result.stdout

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


# --- Deprecation stub: _bundled_hub/tools/octave-validator.py ---


@pytest.mark.unit
class TestOctaveValidatorDeprecationStub:
    """The retained legacy-path stub warns and forwards to the canonical CLI.

    The stub exists solely so downstream consumers still invoking
    ``.hestai-sys/tools/octave-validator.py`` get an actionable migration
    message instead of a bare ``No such file or directory``. It holds no
    validation logic of its own — it forwards to ``octave_mcp.cli.main``.
    """

    def _run_stub(self, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(_STUB_PATH), *args],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def test_stub_file_exists(self) -> None:
        assert _STUB_PATH.is_file(), f"deprecation stub missing at {_STUB_PATH}"

    def test_stub_warns_and_forwards_valid_doc(self, tmp_path: Path) -> None:
        """Valid doc: stub emits a stderr deprecation warning and exits 0."""
        doc_path = tmp_path / "valid.oct.md"
        doc_path.write_text(_make_skill_doc(), encoding="utf-8")
        result = self._run_stub(str(doc_path))
        assert result.returncode == 0, result.stderr
        # Warning lands on stderr (stdout stays clean for downstream parsing).
        assert "DEPRECATED" in result.stderr
        assert "octave_mcp.cli.main" in result.stderr
        assert "DEPRECATED" not in result.stdout

    def test_stub_strips_legacy_profile_flag(self, tmp_path: Path) -> None:
        """The old ``--profile protocol <file>`` form does not crash the stub.

        The legacy vendored CLI took ``--profile protocol``; the canonical CLI
        has no equivalent. The stub strips a leading ``--profile <value>`` pair
        and forwards the remaining file args, so old callers keep working.
        """
        doc_path = tmp_path / "valid.oct.md"
        doc_path.write_text(_make_skill_doc(), encoding="utf-8")
        result = self._run_stub("--profile", "protocol", str(doc_path))
        assert result.returncode == 0, result.stderr
        assert "DEPRECATED" in result.stderr

    def test_stub_propagates_nonzero_exit_on_malformed_doc(self, tmp_path: Path) -> None:
        """A malformed doc forwarded through the stub propagates a non-zero exit."""
        doc_path = tmp_path / "bad.oct.md"
        doc_path.write_text(
            "===BAD===\nMETA:\n  TYPE::SKILL\nUNCLOSED::(oops\n===END===",
            encoding="utf-8",
        )
        result = self._run_stub(str(doc_path))
        assert result.returncode != 0
        assert "DEPRECATED" in result.stderr
