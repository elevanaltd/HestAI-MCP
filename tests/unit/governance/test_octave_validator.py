"""Tests for the vendored OctaveValidator's META field handling.

Covers:
- Newly-allowed META fields (OCTAVE, CONTRACT, TAGS, etc.)
- unknown_policy enforcement (strict, warn, ignore)
- SKILL and AGENT_DEFINITION document types
"""

import sys
from importlib import import_module
from pathlib import Path

import pytest

# The vendored validator lives in the bundled hub tools directory.
# Add it to sys.path so we can import it directly.
_VALIDATOR_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "hestai_mcp" / "_bundled_hub" / "tools"
)
sys.path.insert(0, str(_VALIDATOR_DIR))

octave_validator = import_module("octave-validator")  # noqa: E402
OctaveValidator = octave_validator.OctaveValidator


# --- Fixtures ---


def _make_doc(meta_fields: str, body: str = "CONTENT::value") -> str:
    """Build a minimal OCTAVE document with given META fields."""
    return f'===TEST===\nMETA:\n  TYPE::PROTOCOL_DEFINITION\n  VERSION::"1.0"\n  STATUS::ACTIVE\n{meta_fields}\n{body}\n===END==='


def _make_skill_doc(meta_fields: str = "") -> str:
    """Build a minimal SKILL-type OCTAVE document."""
    return (
        '---\nname: test-skill\nversion: "1.0.0"\n---\n\n'
        f'===TEST_SKILL===\nMETA:\n  TYPE::SKILL\n  VERSION::"1.0.0"\n'
        f'  PURPOSE::"Test skill"\n{meta_fields}\n'
        "CONTENT::value\n===END==="
    )


def _make_agent_doc(meta_fields: str = "") -> str:
    """Build a minimal AGENT_DEFINITION-type OCTAVE document."""
    return (
        f'===TEST_AGENT===\nMETA:\n  TYPE::AGENT_DEFINITION\n  VERSION::"1.0.0"\n'
        f'  PURPOSE::"Test agent"\n{meta_fields}\n'
        "CONTENT::value\n===END==="
    )


# --- Tests: Newly-allowed META fields ---


class TestAllowedMetaFields:
    """Verify that v6 META fields added in the validator update are accepted."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "field_name,field_value",
        [
            ("OCTAVE", '"Olympian Common Text And Vocabulary Engine"'),
            ("CONTRACT", "HOLOGRAPHIC<JIT_GRAMMAR_COMPILATION>"),
            ("TAGS", "[dependency,octave,alignment]"),
            ("ID", "test-doc-001"),
            ("INHERITS", "parent-doc.oct.md"),
            ("DOMAIN", "octave-validation"),
            ("SOURCE", "octave-mcp"),
            ("CREATED", "2026-03-29"),
            ("UPDATED", "2026-03-29"),
            ("REVISED", "2026-03-29"),
            ("RELATED", "[doc-a,doc-b]"),
            ("REPLACES", "old-doc.oct.md"),
            ("RESOLVES", "issue-123"),
            ("SUPPLEMENTS", "other-doc.oct.md"),
            ("CANONICAL", "true"),
            ("COMPRESSION_TIER", "LOSSLESS"),
            ("ENFORCEMENT", "BLOCKING"),
            ("FORMAT", "OCTAVE"),
            ("IMMUTABLES", "[I1,I2,I3]"),
            ("OWNERS", "[team-a]"),
            ("PHASES", "[PLAN,BUILD]"),
        ],
    )
    def test_v6_meta_field_accepted_with_warn_policy(self, field_name, field_value):
        """Each newly-allowed META field should not produce warnings under warn policy."""
        doc = _make_doc(f"  {field_name}::{field_value}")
        v = OctaveValidator(unknown_policy="warn")
        valid, messages = v.validate_octave_document(doc)
        unknown_warnings = [m for m in messages if "Unknown META field" in m]
        assert (
            not unknown_warnings
        ), f"META::{field_name} should be allowed but got: {unknown_warnings}"

    @pytest.mark.unit
    def test_octave_field_in_skill_document(self):
        """OCTAVE field in a SKILL-type doc should not produce unknown-field warnings."""
        doc = _make_skill_doc(
            '  OCTAVE::"Olympian Common Text And Vocabulary Engine — Semantic DSL for LLMs"'
        )
        v = OctaveValidator(profile="hestai-skill", unknown_policy="warn")
        valid, messages = v.validate_octave_document(doc)
        unknown_warnings = [m for m in messages if "Unknown META field" in m]
        assert not unknown_warnings, f"OCTAVE field should be allowed: {unknown_warnings}"

    @pytest.mark.unit
    def test_contract_field_in_agent_document(self):
        """CONTRACT field in an AGENT_DEFINITION doc should not produce unknown-field warnings."""
        doc = _make_agent_doc("  CONTRACT::HOLOGRAPHIC<JIT_GRAMMAR_COMPILATION>")
        v = OctaveValidator(profile="hestai-agent", unknown_policy="warn")
        valid, messages = v.validate_octave_document(doc)
        unknown_warnings = [m for m in messages if "Unknown META field" in m]
        assert not unknown_warnings, f"CONTRACT field should be allowed: {unknown_warnings}"


# --- Tests: unknown_policy enforcement ---


class TestUnknownPolicy:
    """Verify the three unknown_policy modes: ignore, warn, strict."""

    UNKNOWN_FIELD_DOC = _make_doc("  TOTALLY_FAKE_FIELD::nonsense")

    @pytest.mark.unit
    def test_ignore_policy_no_warnings(self):
        """ignore policy should silently accept unknown META fields."""
        v = OctaveValidator(unknown_policy="ignore")
        valid, messages = v.validate_octave_document(self.UNKNOWN_FIELD_DOC)
        assert valid
        assert not any("Unknown META field" in m for m in messages)

    @pytest.mark.unit
    def test_warn_policy_produces_warning(self):
        """warn policy should produce a warning for unknown META fields."""
        v = OctaveValidator(unknown_policy="warn")
        valid, messages = v.validate_octave_document(self.UNKNOWN_FIELD_DOC)
        # Warnings don't cause validation failure
        assert valid
        assert any("TOTALLY_FAKE_FIELD" in m for m in messages)

    @pytest.mark.unit
    def test_strict_policy_protocol_profile_rejects(self):
        """strict policy with protocol profile should reject unknown META fields."""
        v = OctaveValidator(unknown_policy="strict", profile="protocol")
        valid, messages = v.validate_octave_document(self.UNKNOWN_FIELD_DOC)
        assert not valid
        assert any("E007" in m for m in messages)
        assert any("TOTALLY_FAKE_FIELD" in m for m in messages)

    @pytest.mark.unit
    def test_strict_policy_non_protocol_profile_no_error(self):
        """strict policy with non-protocol profile should not error (strict only applies to protocol)."""
        v = OctaveValidator(unknown_policy="strict", profile="hestai-agent")
        # Agent docs don't have YAML frontmatter requirement for this test
        doc = '===TEST===\nMETA:\n  TYPE::AGENT_DEFINITION\n  VERSION::"1.0"\n  TOTALLY_FAKE::value\nCONTENT::x\n===END==='
        valid, messages = v.validate_octave_document(doc)
        # Should not have E007 error since strict only applies to protocol profile
        assert not any("E007" in m for m in messages)

    @pytest.mark.unit
    def test_strict_policy_hestai_skill_profile_no_error(self):
        """strict policy with hestai-skill profile should not produce E007 errors."""
        doc = _make_skill_doc("  TOTALLY_FAKE::value")
        v = OctaveValidator(unknown_policy="strict", profile="hestai-skill")
        valid, messages = v.validate_octave_document(doc)
        # strict only applies to protocol profile — skill profile should not get E007
        assert not any("E007" in m for m in messages)


# --- Tests: Document types ---


class TestDocumentTypes:
    """Verify the validator handles SKILL and AGENT_DEFINITION META.TYPE."""

    @pytest.mark.unit
    def test_skill_type_produces_warning_not_error(self):
        """TYPE::SKILL produces an 'unknown type' warning but not an error."""
        doc = _make_skill_doc()
        v = OctaveValidator(profile="hestai-skill", unknown_policy="ignore")
        valid, messages = v.validate_octave_document(doc)
        # The validator doesn't have specific schema rules for SKILL type,
        # so it produces a warning about unknown type — this is expected behavior.
        type_warnings = [m for m in v.warnings if "Unknown META.TYPE" in m]
        assert len(type_warnings) > 0, "Expected 'Unknown META.TYPE' warning for SKILL"
        # But it should not be in errors — document should still be structurally valid
        type_errors = [e for e in v.errors if "Unknown META.TYPE" in e]
        assert len(type_errors) == 0

    @pytest.mark.unit
    def test_agent_definition_type_produces_warning_not_error(self):
        """TYPE::AGENT_DEFINITION produces an 'unknown type' warning but not an error."""
        doc = _make_agent_doc()
        v = OctaveValidator(profile="hestai-agent", unknown_policy="ignore")
        valid, messages = v.validate_octave_document(doc)
        type_warnings = [m for m in v.warnings if "Unknown META.TYPE" in m]
        # Warning is expected (no specific schema validation for this type)
        assert len(type_warnings) > 0
        # But it should not be in errors
        type_errors = [e for e in v.errors if "Unknown META.TYPE" in e]
        assert len(type_errors) == 0
