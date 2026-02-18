"""
Tests for namespace validation (SYS::/PROD:: Relativity Governance Protocol).

Tests validation rules V1-V4 from NAMESPACE-MIGRATION-GUIDE.md §10.
"""

from __future__ import annotations

from datetime import date

import pytest

from hestai_mcp.core.namespace_resolver import (
    Namespace,
    NamespaceResolver,
    format_result,
    validate_file,
)


class TestNamespaceExtraction:
    """Test extraction of namespace declarations."""

    def test_extract_octave_meta_namespace_sys(self):
        """Extract SYS namespace from OCTAVE META block."""
        content = """===AGENT===
META:
  TYPE::AGENT
  NAMESPACE::SYS
  VERSION::"1.0"
===END==="""
        resolver = NamespaceResolver()
        assert resolver.extract_namespace(content) == Namespace.SYS

    def test_extract_octave_meta_namespace_prod(self):
        """Extract PROD namespace from OCTAVE META block."""
        content = """===WORKFLOW===
META:
  TYPE::WORKFLOW
  NAMESPACE::PROD
  VERSION::"1.0"
===END==="""
        resolver = NamespaceResolver()
        assert resolver.extract_namespace(content) == Namespace.PROD

    def test_extract_yaml_frontmatter_namespace_sys(self):
        """Extract SYS namespace from YAML frontmatter."""
        content = """---
type: WORKFLOW
version: 1.0
namespace: SYS
---

# Workflow Document
"""
        resolver = NamespaceResolver()
        assert resolver.extract_namespace(content) == Namespace.SYS

    def test_extract_yaml_frontmatter_namespace_prod(self):
        """Extract PROD namespace from YAML frontmatter."""
        content = """---
type: AGENT
version: 1.0
namespace: PROD
---

# Agent Document
"""
        resolver = NamespaceResolver()
        assert resolver.extract_namespace(content) == Namespace.PROD

    def test_extract_no_namespace(self):
        """Return None when no namespace declaration exists."""
        content = """# Mixed Context Document

This document has no namespace.
"""
        resolver = NamespaceResolver()
        assert resolver.extract_namespace(content) is None

    def test_yaml_takes_precedence(self):
        """YAML frontmatter takes precedence over META block."""
        content = """---
namespace: SYS
---
===AGENT===
META:
  NAMESPACE::PROD
===END==="""
        resolver = NamespaceResolver()
        assert resolver.extract_namespace(content) == Namespace.SYS


class TestReferenceDetection:
    """Test detection of I1-I6 references."""

    def test_find_bare_references(self):
        """Detect bare I# references."""
        content = """# Document
This satisfies I1 and I2.
Additional reference to I5.
"""
        resolver = NamespaceResolver()
        refs = resolver.find_references(content)

        assert len(refs) == 3
        assert refs[0].ref == "I1"
        assert not refs[0].is_qualified
        assert refs[1].ref == "I2"
        assert not refs[1].is_qualified
        assert refs[2].ref == "I5"
        assert not refs[2].is_qualified

    def test_find_qualified_sys_references(self):
        """Detect SYS:: qualified references."""
        content = """# Document
This follows SYS::I1 (TDD) and SYS::I2 (Phase Gates).
"""
        resolver = NamespaceResolver()
        refs = resolver.find_references(content)

        assert len(refs) == 2
        assert refs[0].ref == "SYS::I1"
        assert refs[0].is_qualified
        assert refs[0].namespace == Namespace.SYS
        assert refs[1].ref == "SYS::I2"
        assert refs[1].is_qualified

    def test_find_qualified_prod_references(self):
        """Detect PROD:: qualified references."""
        content = """# Document
This supports PROD::I1 (Cognitive Continuity) and PROD::I5 (Odyssean Identity).
"""
        resolver = NamespaceResolver()
        refs = resolver.find_references(content)

        assert len(refs) == 2
        assert refs[0].ref == "PROD::I1"
        assert refs[0].namespace == Namespace.PROD
        assert refs[1].ref == "PROD::I5"
        assert refs[1].namespace == Namespace.PROD

    def test_find_mixed_references(self):
        """Detect both bare and qualified references."""
        content = """# Document
Bare reference to I1.
Qualified reference to SYS::I2.
Cross-namespace PROD::I5.
Another bare I6.
"""
        resolver = NamespaceResolver()
        refs = resolver.find_references(content)

        assert len(refs) == 4
        assert refs[0].ref == "I1"
        assert not refs[0].is_qualified
        assert refs[1].ref == "SYS::I2"
        assert refs[1].is_qualified
        assert refs[2].ref == "PROD::I5"
        assert refs[2].is_qualified
        assert refs[3].ref == "I6"
        assert not refs[3].is_qualified

    def test_skip_comment_lines(self):
        """Skip references in comment lines."""
        content = """# Document
// This is a comment with I1
# Also a comment with I2
Real reference: I3
"""
        resolver = NamespaceResolver()
        refs = resolver.find_references(content)

        assert len(refs) == 1
        assert refs[0].ref == "I3"

    def test_line_numbers_correct(self):
        """Verify correct line numbers for references."""
        content = """Line 1
Line 2 has I1
Line 3
Line 4 has I2 and I3
"""
        resolver = NamespaceResolver()
        refs = resolver.find_references(content)

        assert refs[0].line_num == 2
        assert refs[1].line_num == 4
        assert refs[2].line_num == 4


class TestValidationRules:
    """Test validation rules V1-V4."""

    def test_v1_declared_namespace_with_bare_refs_passes(self):
        """V1: File with namespace declaration and bare refs should pass."""
        content = """===AGENT===
META:
  TYPE::AGENT
  NAMESPACE::SYS

This agent follows I1 (TDD) and I2 (Phase Gates).
===END==="""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)

        assert result.is_valid
        assert result.file_namespace == Namespace.SYS
        assert len(result.references) == 2

    def test_v1_no_namespace_with_bare_refs_fails_after_grace(self):
        """V1: File without namespace and bare refs should fail after grace period."""
        content = """# Document
This references I1 and I2 without namespace.
"""
        # After grace period
        resolver = NamespaceResolver(current_date=date(2026, 8, 17))
        result = resolver.validate_namespace_compliance(content)

        assert not result.is_valid
        assert len(result.errors) > 0
        assert "Bare reference" in result.errors[0]

    def test_v1_no_namespace_with_bare_refs_warns_during_grace(self):
        """V1: File without namespace and bare refs should warn during grace period."""
        content = """# Document
This references I1 and I2 without namespace.
"""
        # During grace period
        resolver = NamespaceResolver(current_date=date(2026, 6, 1))
        result = resolver.validate_namespace_compliance(content)

        assert result.is_valid  # Warnings don't fail validation
        assert len(result.warnings) > 0
        assert "GRACE_PERIOD" in result.warnings[0]

    def test_v1_no_namespace_with_qualified_refs_passes(self):
        """V1: File without namespace but all refs qualified should pass."""
        content = """# Document
This follows SYS::I1 and supports PROD::I5.
"""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_v2_same_namespace_redundant_qualifier_warns(self):
        """V2: Redundant qualifier for same namespace should warn."""
        content = """===AGENT===
META:
  TYPE::AGENT
  NAMESPACE::SYS

This agent follows SYS::I1 (redundant).
===END==="""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)

        assert result.is_valid  # Warnings don't fail
        assert len(result.warnings) > 0
        assert "Redundant namespace qualifier" in result.warnings[0]

    def test_v2_cross_namespace_refs_must_be_qualified(self):
        """V2: Cross-namespace references must be qualified."""
        content = """===AGENT===
META:
  TYPE::AGENT
  NAMESPACE::SYS

This agent supports PROD::I5 (correct).
Also references I1 (resolves to SYS::I1, correct).
===END==="""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)

        assert result.is_valid

    def test_v4_invalid_namespace_value_fails(self):
        """V4: Invalid namespace value should fail."""
        content = """===AGENT===
META:
  TYPE::AGENT
  NAMESPACE::SYSTEM

This is invalid.
===END==="""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)

        assert not result.is_valid
        assert any("Invalid NAMESPACE value" in e for e in result.errors)


class TestReferenceResolution:
    """Test reference resolution logic."""

    def test_resolve_bare_ref_with_sys_namespace(self):
        """Resolve bare reference with SYS namespace."""
        resolver = NamespaceResolver()
        resolved = resolver.resolve_reference("I1", Namespace.SYS)
        assert resolved == "SYS::I1"

    def test_resolve_bare_ref_with_prod_namespace(self):
        """Resolve bare reference with PROD namespace."""
        resolver = NamespaceResolver()
        resolved = resolver.resolve_reference("I5", Namespace.PROD)
        assert resolved == "PROD::I5"

    def test_resolve_already_qualified_ref(self):
        """Already qualified reference remains unchanged."""
        resolver = NamespaceResolver()
        resolved = resolver.resolve_reference("SYS::I1", Namespace.PROD)
        assert resolved == "SYS::I1"

    def test_resolve_bare_ref_without_namespace_fails(self):
        """Resolving bare reference without namespace should fail."""
        resolver = NamespaceResolver()
        with pytest.raises(ValueError, match="Cannot resolve bare reference"):
            resolver.resolve_reference("I1", None)


class TestGracePeriod:
    """Test grace period behavior."""

    def test_during_grace_period_warnings_only(self):
        """During grace period, violations should be warnings."""
        content = """# Document
Bare reference I1 without namespace.
"""
        resolver = NamespaceResolver(current_date=date(2026, 6, 1))
        result = resolver.validate_namespace_compliance(content)

        assert result.is_valid
        assert len(result.warnings) > 0
        assert len(result.errors) == 0

    def test_after_grace_period_errors(self):
        """After grace period, violations should be errors."""
        content = """# Document
Bare reference I1 without namespace.
"""
        resolver = NamespaceResolver(current_date=date(2026, 8, 17))
        result = resolver.validate_namespace_compliance(content)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_strict_mode_ignores_grace_period(self):
        """Strict mode should treat violations as errors even during grace period."""
        content = """# Document
Bare reference I1 without namespace.
"""
        resolver = NamespaceResolver(current_date=date(2026, 6, 1))
        result = resolver.validate_namespace_compliance(content, strict=True)

        assert not result.is_valid
        assert len(result.errors) > 0


class TestCompleteScenarios:
    """Test complete validation scenarios from migration guide."""

    def test_correct_sys_usage(self):
        """Test correct SYS namespace usage from migration guide §9."""
        content = """===CHECKLIST===
META:
  NAMESPACE::SYS

VERIFY_TDD::I1_compliance
VERIFY_GATES::I2_evidence
SUPPORT_PRODUCT::PROD::I1_ctx
===END==="""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)

        assert result.is_valid
        assert result.file_namespace == Namespace.SYS
        # Should have 2 bare refs (I1, I2) and 1 qualified (PROD::I1)
        bare_refs = [r for r in result.references if not r.is_qualified]
        qualified_refs = [r for r in result.references if r.is_qualified]
        assert len(bare_refs) == 2
        assert len(qualified_refs) == 1

    def test_incorrect_mixed_refs(self):
        """Test incorrect mixed reference scenario from migration guide §9."""
        content = """===CHECKLIST===
META:
  NAMESPACE::SYS

VERIFY_TDD::I1_compliance
VERIFY_IDENTITY::I5_binding
===END==="""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)

        # Should pass validation (bare I5 resolves to SYS::I5)
        # but may have warnings if context implies PROD::I5 was intended
        assert result.is_valid
        assert result.file_namespace == Namespace.SYS

    def test_missing_declaration_scenario(self):
        """Test missing declaration scenario from migration guide §9."""
        content = """# Workflow
Agents must satisfy I5 before work.
"""
        # After grace period
        resolver = NamespaceResolver(current_date=date(2026, 8, 17))
        result = resolver.validate_namespace_compliance(content)

        assert not result.is_valid
        assert len(result.errors) > 0


class TestFormatting:
    """Test result formatting."""

    def test_format_result_with_namespace(self):
        """Format result with declared namespace."""
        content = """===AGENT===
META:
  NAMESPACE::SYS

References I1.
===END==="""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)
        formatted = format_result(result)

        assert "Declared namespace: SYS" in formatted
        assert "References found: 1" in formatted

    def test_format_result_without_namespace(self):
        """Format result without declared namespace."""
        content = """# Document
References SYS::I1.
"""
        resolver = NamespaceResolver()
        result = resolver.validate_namespace_compliance(content)
        formatted = format_result(result)

        assert "Declared namespace: (none)" in formatted

    def test_format_result_with_errors(self):
        """Format result with errors."""
        content = """# Document
Bare reference I1.
"""
        resolver = NamespaceResolver(current_date=date(2026, 8, 17))
        result = resolver.validate_namespace_compliance(content)
        formatted = format_result(result)

        assert "ERROR(S):" in formatted
        assert "FAILED" in formatted


@pytest.mark.behavior
class TestBehaviorContracts:
    """Behavioral tests for namespace validation."""

    def test_roundtrip_resolution(self):
        """Test roundtrip: extract namespace, resolve refs, validate."""
        content = """===WORKFLOW===
META:
  NAMESPACE::SYS

Follows I1, I2, and PROD::I5.
===END==="""
        resolver = NamespaceResolver()

        # Extract namespace
        namespace = resolver.extract_namespace(content)
        assert namespace == Namespace.SYS

        # Find references
        refs = resolver.find_references(content)
        assert len(refs) == 3

        # Resolve bare references
        for ref in refs:
            if not ref.is_qualified:
                resolved = resolver.resolve_reference(ref.ref, namespace)
                assert resolved.startswith("SYS::")

        # Validate
        result = resolver.validate_namespace_compliance(content)
        assert result.is_valid

    def test_multiple_files_validation(self, tmp_path):
        """Test validation across multiple files."""
        # Create test files
        file1 = tmp_path / "docs" / "agent.md"
        file1.parent.mkdir(parents=True)
        file1.write_text("""===AGENT===
META:
  NAMESPACE::PROD

Agent uses I5 (Odyssean Identity).
===END===""")

        file2 = tmp_path / "docs" / "workflow.md"
        file2.write_text("""---
namespace: SYS
---

# Workflow

Follows I1 (TDD) and supports PROD::I5.
""")

        # Validate both
        result1 = validate_file(file1)
        result2 = validate_file(file2)

        assert result1.is_valid
        assert result1.file_namespace == Namespace.PROD

        assert result2.is_valid
        assert result2.file_namespace == Namespace.SYS
