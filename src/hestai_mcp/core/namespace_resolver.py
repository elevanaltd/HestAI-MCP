"""
Namespace resolution for SYS::/PROD:: Relativity Governance Protocol.

Implements Constitution §3.5 namespace resolution to prevent I1-I6 collisions
between System (HOW to build) and Product (WHAT to build) North Stars.

Key rules:
1. Files declare namespace via META::NAMESPACE::[SYS|PROD] or YAML frontmatter
2. Bare I# refs resolve to declared namespace
3. Cross-namespace refs MUST use prefix (SYS::I5, PROD::I1)
4. No declaration = all refs must be qualified

Grace period: 2026-02-16 to 2026-08-16 (warnings only)
After grace period: violations become errors

Authority: src/hestai_mcp/_bundled_hub/governance/migration/NAMESPACE-MIGRATION-GUIDE.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path


class Namespace(StrEnum):
    """Valid namespace identifiers."""

    SYS = "SYS"
    PROD = "PROD"


@dataclass(frozen=True)
class NamespaceReference:
    """A reference to an immutable (I1-I6) in a document."""

    ref: str  # e.g., "I1", "SYS::I1", "PROD::I5"
    line_num: int
    line_text: str
    is_qualified: bool  # Has namespace prefix
    namespace: Namespace | None  # SYS or PROD if qualified, None if bare


@dataclass(frozen=True)
class ValidationResult:
    """Result of namespace validation."""

    is_valid: bool
    warnings: list[str]
    errors: list[str]
    file_namespace: Namespace | None
    references: list[NamespaceReference]


class NamespaceResolver:
    """Resolves namespace references according to Relativity Governance Protocol."""

    # Grace period end date
    GRACE_PERIOD_END = date(2026, 8, 16)

    # Regex patterns
    META_NAMESPACE_RE = re.compile(r'^\s*NAMESPACE::(?:"|)?(SYS|PROD)(?:"|)?', re.MULTILINE)
    YAML_NAMESPACE_RE = re.compile(r"^namespace:\s*(SYS|PROD)\s*$", re.MULTILINE)
    # Allow I# followed by non-digit (including _ for cases like I1_compliance)
    BARE_I_REF_RE = re.compile(r"\bI([1-6])(?!\d)")
    QUALIFIED_I_REF_RE = re.compile(r"\b(SYS|PROD)::I([1-6])(?!\d)")

    def __init__(self, current_date: date | None = None):
        """
        Initialize resolver.

        Args:
            current_date: Current date for grace period checks (defaults to today)
        """
        self.current_date = current_date or date.today()
        self.in_grace_period = self.current_date < self.GRACE_PERIOD_END

    def extract_namespace(self, content: str) -> Namespace | None:
        """
        Extract declared namespace from document.

        Checks both OCTAVE META blocks and YAML frontmatter.

        Args:
            content: Document content

        Returns:
            Namespace enum value or None if not declared
        """
        # Check YAML frontmatter first (appears before OCTAVE markers)
        if content.strip().startswith("---"):
            yaml_match = self.YAML_NAMESPACE_RE.search(content)
            if yaml_match:
                return Namespace(yaml_match.group(1))

        # Check OCTAVE META block
        meta_match = self.META_NAMESPACE_RE.search(content)
        if meta_match:
            return Namespace(meta_match.group(1))

        return None

    def find_references(self, content: str) -> list[NamespaceReference]:
        """
        Find all I1-I6 references in document.

        Args:
            content: Document content

        Returns:
            List of NamespaceReference objects
        """
        references: list[NamespaceReference] = []
        lines = content.splitlines()

        for line_num, line in enumerate(lines, start=1):
            # Skip comment lines
            if line.strip().startswith("//") or line.strip().startswith("#"):
                continue

            # Find qualified references (SYS::I# or PROD::I#) and track their positions
            qualified_positions: set[tuple[int, int]] = set()
            for match in self.QUALIFIED_I_REF_RE.finditer(line):
                namespace_str = match.group(1)
                immutable_num = match.group(2)
                references.append(
                    NamespaceReference(
                        ref=f"{namespace_str}::I{immutable_num}",
                        line_num=line_num,
                        line_text=line.strip(),
                        is_qualified=True,
                        namespace=Namespace(namespace_str),
                    )
                )
                # Track the position of the I# part (not the full qualified ref)
                # Match gives us the full "PROD::I5", we need to track where "I5" is
                # The I# part starts after the "::" which is 5 chars before the end
                i_start = match.start() + len(namespace_str) + 2  # +2 for "::"
                i_end = match.end()
                qualified_positions.add((i_start, i_end))

            # Find bare references (I# without prefix)
            # Skip if this position was already captured as part of a qualified ref
            for match in self.BARE_I_REF_RE.finditer(line):
                # Check if this match position overlaps with a qualified reference
                if (match.start(), match.end()) in qualified_positions:
                    continue  # Skip, already captured as qualified

                immutable_num = match.group(1)
                references.append(
                    NamespaceReference(
                        ref=f"I{immutable_num}",
                        line_num=line_num,
                        line_text=line.strip(),
                        is_qualified=False,
                        namespace=None,
                    )
                )

        return references

    def validate_namespace_compliance(self, content: str, strict: bool = False) -> ValidationResult:
        """
        Validate namespace compliance for a document.

        Applies validation rules V1-V4 from migration guide §10.

        Args:
            content: Document content
            strict: If True, treat warnings as errors (ignores grace period)

        Returns:
            ValidationResult with validation status and messages
        """
        warnings: list[str] = []
        errors: list[str] = []

        # Extract namespace declaration
        file_namespace = self.extract_namespace(content)

        # Find all references
        references = self.find_references(content)

        # V1: DECLARATION_CONSISTENCY
        # If namespace declared, bare refs resolve to that namespace
        # If no namespace, all refs must be qualified
        bare_refs = [r for r in references if not r.is_qualified]

        if file_namespace is None and bare_refs:
            # V1: No declaration requires all refs be qualified
            for ref in bare_refs:
                msg = (
                    f"Line {ref.line_num}: Bare reference '{ref.ref}' requires "
                    f"namespace qualification (no NAMESPACE declaration found). "
                    f"Either add 'NAMESPACE::{ref.ref[0:2]}' to META or qualify as "
                    f"'SYS::{ref.ref}' or 'PROD::{ref.ref}'."
                )
                if strict or not self.in_grace_period:
                    errors.append(msg)
                else:
                    warnings.append(msg + " [GRACE_PERIOD]")

        # V2: CROSS_NAMESPACE_QUALIFICATION
        # If document namespace is X and reference is to Y, must be qualified
        # This is implicitly satisfied by our model (qualified refs are explicit)
        # We validate that qualified refs to the SAME namespace are unnecessary
        for ref in references:
            if ref.is_qualified and file_namespace is not None and ref.namespace == file_namespace:
                msg = (
                    f"Line {ref.line_num}: Redundant namespace qualifier '{ref.ref}'. "
                    f"Within NAMESPACE::{file_namespace.value} document, use bare "
                    f"'{ref.ref.split('::')[1]}' instead."
                )
                warnings.append(msg)

        # V4: NAMESPACE_VALUES
        # Already enforced by Namespace enum, but check META/YAML for invalid values
        invalid_namespace_pattern = re.compile(
            r'\bNAMESPACE::(?:"|)?(SYSTEM|PRODUCT|SYS\|PROD|[^"SYS|PROD][^"]*?)(?:"|)?',
            re.MULTILINE,
        )
        invalid_match = invalid_namespace_pattern.search(content)
        if invalid_match:
            errors.append(
                f"Invalid NAMESPACE value '{invalid_match.group(1)}'. " f"Must be 'SYS' or 'PROD'."
            )

        # Check for ambiguous references in grace period
        if self.in_grace_period and bare_refs and file_namespace:
            # Info message: bare refs will resolve to file namespace
            ref_list = ", ".join(sorted({r.ref for r in bare_refs[:5]}))
            if len(bare_refs) > 5:
                ref_list += f", ... (+{len(bare_refs) - 5} more)"
            warnings.append(
                f"Found {len(bare_refs)} bare reference(s) ({ref_list}) that resolve to "
                f"NAMESPACE::{file_namespace.value}. After grace period (2026-08-16), "
                f"cross-namespace refs without prefix will be errors."
            )

        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors,
            file_namespace=file_namespace,
            references=references,
        )

    def resolve_reference(self, ref: str, file_namespace: Namespace | None) -> str:
        """
        Resolve a reference to its fully-qualified form.

        Args:
            ref: Reference string (e.g., "I1", "SYS::I5")
            file_namespace: Declared namespace of containing file

        Returns:
            Fully-qualified reference (e.g., "SYS::I1")

        Raises:
            ValueError: If reference cannot be resolved (no namespace context)
        """
        # Already qualified
        if "::" in ref:
            return ref

        # Bare reference needs namespace context
        if file_namespace is None:
            raise ValueError(
                f"Cannot resolve bare reference '{ref}' without namespace context. "
                f"File must declare NAMESPACE::SYS or NAMESPACE::PROD."
            )

        return f"{file_namespace.value}::{ref}"


def validate_file(
    file_path: Path, strict: bool = False, current_date: date | None = None
) -> ValidationResult:
    """
    Validate namespace compliance for a file.

    Args:
        file_path: Path to file to validate
        strict: If True, treat warnings as errors
        current_date: Current date for grace period checks

    Returns:
        ValidationResult

    Raises:
        FileNotFoundError: If file does not exist
        UnicodeDecodeError: If file cannot be decoded as UTF-8
    """
    content = file_path.read_text(encoding="utf-8")
    resolver = NamespaceResolver(current_date=current_date)
    return resolver.validate_namespace_compliance(content, strict=strict)


def format_result(result: ValidationResult, file_path: Path | None = None) -> str:
    """
    Format validation result as human-readable string.

    Args:
        result: ValidationResult to format
        file_path: Optional file path to include in output

    Returns:
        Formatted string
    """
    lines: list[str] = []

    if file_path:
        lines.append(f"File: {file_path}")

    if result.file_namespace:
        lines.append(f"Declared namespace: {result.file_namespace.value}")
    else:
        lines.append("Declared namespace: (none)")

    lines.append(f"References found: {len(result.references)}")

    if result.errors:
        lines.append(f"\n❌ {len(result.errors)} ERROR(S):")
        for error in result.errors:
            lines.append(f"  - {error}")

    if result.warnings:
        lines.append(f"\n⚠️  {len(result.warnings)} WARNING(S):")
        for warning in result.warnings:
            lines.append(f"  - {warning}")

    if result.is_valid and not result.warnings:
        lines.append("\n✅ Namespace validation passed")
    elif result.is_valid:
        lines.append("\n✅ Namespace validation passed (with warnings)")
    else:
        lines.append("\n❌ Namespace validation FAILED")

    return "\n".join(lines)
