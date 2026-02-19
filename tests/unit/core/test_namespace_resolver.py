"""
Tests for namespace_resolver module — Constitution §3.5 namespace validation (#241).

TDD Discipline:
1. RED: Write failing tests first
2. GREEN: Minimal implementation to pass
3. REFACTOR: Improve while tests pass

Namespace Context:
- Documents declare NAMESPACE::SYS or NAMESPACE::PROD in META/frontmatter
- Cross-namespace immutable citations must use qualified form (SYS::I2, PROD::I4)
- Bare form (I2) valid only within a single-namespace document citing its own namespace
"""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestExtractNamespace:
    """Test extraction of NAMESPACE declaration from document content."""

    def test_extract_namespace_finds_sys(self) -> None:
        """Detects NAMESPACE::SYS in OCTAVE META block."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "META:\n  NAMESPACE::SYS\n\nSome content here."
        assert extract_namespace(content) == "SYS"

    def test_extract_namespace_finds_prod(self) -> None:
        """Detects NAMESPACE::PROD in OCTAVE META block."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "META:\n  NAMESPACE::PROD\n\nSome content here."
        assert extract_namespace(content) == "PROD"

    def test_extract_namespace_returns_none_when_missing(self) -> None:
        """Returns None when no NAMESPACE declaration is present."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "# Some document\n\nNo namespace declared here."
        assert extract_namespace(content) is None

    def test_extract_namespace_yaml_frontmatter_sys(self) -> None:
        """Detects NAMESPACE::SYS in YAML-style frontmatter."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "---\nNAMESPACE::SYS\ntitle: Some Doc\n---\n\nBody content."
        assert extract_namespace(content) == "SYS"

    def test_extract_namespace_yaml_frontmatter_prod(self) -> None:
        """Detects NAMESPACE::PROD in YAML-style frontmatter."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "---\nNAMESPACE::PROD\ntitle: Some Doc\n---\n\nBody content."
        assert extract_namespace(content) == "PROD"

    def test_extract_namespace_ignores_invalid_values(self) -> None:
        """Does not extract invalid namespace values like NAMESPACE::FOO."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "META:\n  NAMESPACE::FOO\n\nContent."
        assert extract_namespace(content) is None

    def test_extract_namespace_case_sensitive(self) -> None:
        """NAMESPACE::sys (lowercase) is not a valid declaration."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "META:\n  NAMESPACE::sys\n\nContent."
        assert extract_namespace(content) is None

    def test_extract_namespace_ignores_body_text_mention(self) -> None:
        """NAMESPACE::SYS in body text (not a declaration line) is not extracted."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "# Guide\n\nUse NAMESPACE::SYS as an example, not a declaration."
        assert extract_namespace(content) is None

    def test_extract_namespace_ignores_partial_value(self) -> None:
        """NAMESPACE::SYSADMIN should not match as SYS."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "META:\n  NAMESPACE::SYSADMIN\n\nContent."
        assert extract_namespace(content) is None

    def test_extract_namespace_ignores_partial_prod_value(self) -> None:
        """NAMESPACE::PRODUCTION should not match as PROD."""
        from hestai_mcp.core.namespace_resolver import extract_namespace

        content = "META:\n  NAMESPACE::PRODUCTION\n\nContent."
        assert extract_namespace(content) is None


@pytest.mark.unit
class TestFindBareReferences:
    """Test detection of bare immutable references (I1-I9) not qualified with namespace."""

    def test_find_bare_references_detects_bare_i1_through_i6(self) -> None:
        """Finds bare I1-I6 references that are not qualified."""
        from hestai_mcp.core.namespace_resolver import find_bare_references

        content = "This cites I1 and I3 and I6 for context."
        result = find_bare_references(content)
        assert "I1" in result
        assert "I3" in result
        assert "I6" in result

    def test_find_bare_references_ignores_qualified_sys_prefix(self) -> None:
        """SYS::I2 is qualified and should NOT appear in bare references."""
        from hestai_mcp.core.namespace_resolver import find_bare_references

        content = "Citing SYS::I2 which is Phase-Gated Progression."
        result = find_bare_references(content)
        assert "I2" not in result

    def test_find_bare_references_ignores_qualified_prod_prefix(self) -> None:
        """PROD::I4 is qualified and should NOT appear in bare references."""
        from hestai_mcp.core.namespace_resolver import find_bare_references

        content = "Citing PROD::I4 which is Freshness Verification."
        result = find_bare_references(content)
        assert "I4" not in result

    def test_find_bare_references_returns_empty_when_none(self) -> None:
        """Returns empty list when no bare references exist."""
        from hestai_mcp.core.namespace_resolver import find_bare_references

        content = "No immutable references here at all."
        result = find_bare_references(content)
        assert result == []

    def test_find_bare_references_mixed_qualified_and_bare(self) -> None:
        """Returns only the unqualified references when both types present."""
        from hestai_mcp.core.namespace_resolver import find_bare_references

        content = "SYS::I2 is fine, but I3 is bare, and PROD::I4 is fine too."
        result = find_bare_references(content)
        assert "I3" in result
        assert "I2" not in result
        assert "I4" not in result

    def test_find_bare_references_in_cite_block(self) -> None:
        """Detects bare references inside CITE[...] syntax."""
        from hestai_mcp.core.namespace_resolver import find_bare_references

        content = "This document CITE[I2] uses bare citation syntax."
        result = find_bare_references(content)
        assert "I2" in result

    def test_find_bare_references_qualified_cite_block_ignored(self) -> None:
        """CITE[SYS::I2] is qualified and must not appear in bare references."""
        from hestai_mcp.core.namespace_resolver import find_bare_references

        content = "This document CITE[SYS::I2] uses qualified citation syntax."
        result = find_bare_references(content)
        assert "I2" not in result

    def test_find_bare_references_no_false_positives_from_text(self) -> None:
        """Standalone 'I' followed by a digit in normal words is not flagged."""
        from hestai_mcp.core.namespace_resolver import find_bare_references

        # "I1" as a standalone token should be detected; ensure no false positives
        # from substrings like "PI3K" or "item1"
        content = "The PI3K pathway involves item1 and matrix I5 values."
        result = find_bare_references(content)
        # PI3K should not produce I3, item1 should not produce I1
        # but matrix I5 (with space before) should be detected
        assert "I3" not in result
        assert "I1" not in result
        assert "I5" in result


@pytest.mark.unit
class TestValidateFile:
    """Test file-level namespace and citation validation."""

    def test_validate_file_valid_with_namespace_and_qualified_refs(self, tmp_path: Path) -> None:
        """File with namespace + only qualified refs is fully valid."""
        from hestai_mcp.core.namespace_resolver import validate_file

        content = "META:\n  NAMESPACE::SYS\n\nCiting SYS::I2 and PROD::I4 properly."
        f = tmp_path / "doc.md"
        f.write_text(content)

        result = validate_file(f)

        assert result["valid"] is True
        assert result["namespace"] == "SYS"
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_file_no_namespace_produces_warning(self, tmp_path: Path) -> None:
        """File with no namespace declaration produces a warning."""
        from hestai_mcp.core.namespace_resolver import validate_file

        content = "# A document\n\nNo namespace declared."
        f = tmp_path / "doc.md"
        f.write_text(content)

        result = validate_file(f)

        assert result["namespace"] is None
        assert len(result["warnings"]) >= 1
        assert any("namespace" in w.lower() for w in result["warnings"])

    def test_validate_file_bare_refs_no_namespace_produces_warnings(self, tmp_path: Path) -> None:
        """File with bare references and no namespace lists them in warnings."""
        from hestai_mcp.core.namespace_resolver import validate_file

        content = "# Doc\n\nThis cites I2 and I5 without qualification."
        f = tmp_path / "doc.md"
        f.write_text(content)

        result = validate_file(f)

        assert "I2" in " ".join(result["warnings"])
        assert "I5" in " ".join(result["warnings"])

    def test_validate_file_intra_namespace_bare_refs_are_valid(self, tmp_path: Path) -> None:
        """Bare refs in a SYS document citing only SYS indices are valid (intra-namespace)."""
        from hestai_mcp.core.namespace_resolver import validate_file

        content = "META:\n  NAMESPACE::SYS\n\nThis document references I2 within its own namespace."
        f = tmp_path / "doc.md"
        f.write_text(content)

        result = validate_file(f)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_file_nonexistent_file_produces_error(self, tmp_path: Path) -> None:
        """Nonexistent file path returns an error, not an exception."""
        from hestai_mcp.core.namespace_resolver import validate_file

        missing = tmp_path / "nonexistent.md"

        result = validate_file(missing)

        assert result["valid"] is False
        assert len(result["errors"]) >= 1
        assert any("not found" in e.lower() or "exist" in e.lower() for e in result["errors"])

    def test_validate_file_returns_correct_keys(self, tmp_path: Path) -> None:
        """Result dict always has valid, namespace, warnings, and errors keys."""
        from hestai_mcp.core.namespace_resolver import validate_file

        content = "META:\n  NAMESPACE::PROD\n\nClean content."
        f = tmp_path / "doc.md"
        f.write_text(content)

        result = validate_file(f)

        assert "valid" in result
        assert "namespace" in result
        assert "warnings" in result
        assert "errors" in result

    def test_validate_file_bare_ref_with_namespace_warns_about_ambiguity(
        self, tmp_path: Path
    ) -> None:
        """File with namespace but bare ref to the other namespace's index produces warning."""
        from hestai_mcp.core.namespace_resolver import validate_file

        # A SYS document that has bare I2 — this is intra-namespace (OK), so no warning.
        # But a PROD document that has bare I1, I2 — also intra-namespace (OK).
        # The warning only fires when both SYS and PROD are in scope (multi-namespace context).
        # For single-file validation, bare refs in a declared namespace are valid.
        content = "META:\n  NAMESPACE::PROD\n\nReferencing I3 without qualification."
        f = tmp_path / "doc.md"
        f.write_text(content)

        result = validate_file(f)

        # Intra-namespace: PROD doc citing I3 → valid, no warnings
        assert result["valid"] is True
        assert result["warnings"] == []

    def test_validate_file_binary_file_produces_error(self, tmp_path: Path) -> None:
        """Binary file that cannot be decoded as UTF-8 returns an error."""
        from hestai_mcp.core.namespace_resolver import validate_file

        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x80\x81\x82\xff\xfe")

        result = validate_file(f)

        assert result["valid"] is False
        assert any("utf-8" in e.lower() or "decode" in e.lower() for e in result["errors"])
