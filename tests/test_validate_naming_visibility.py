"""Tests for validate_naming_visibility.py - Issue #68 fix.

Tests the root-level file blind spot fix where non-whitelisted root-level
.md files should be rejected with clear guidance.
"""

from __future__ import annotations

import pytest


class TestRootLevelDocValidation:
    """Test cases for root-level document validation behavior."""

    def test_root_readme_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """README.md at root should pass validation (whitelisted)."""
        from scripts.ci.validate_naming_visibility import main

        # README.md is in RE_WHITELIST, should pass
        result = main(["README.md"])
        assert result == 0

    def test_root_claude_md_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """CLAUDE.md at root should pass validation (whitelisted)."""
        from scripts.ci.validate_naming_visibility import main

        # CLAUDE.md is in RE_WHITELIST, should pass
        result = main(["CLAUDE.md"])
        assert result == 0

    def test_root_arbitrary_md_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PHASE_4_COMPLETION.md at root should fail with visibility error."""
        from scripts.ci.validate_naming_visibility import main

        # Arbitrary root-level .md file not in whitelist should fail
        with pytest.raises(SystemExit) as exc_info:
            main(["PHASE_4_COMPLETION.md"])

        error_message = str(exc_info.value)
        assert "visibility-rules" in error_message.lower() or "root-level" in error_message.lower()

    def test_docs_valid_md_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """docs/valid-name.md should pass validation."""
        from scripts.ci.validate_naming_visibility import main

        # Files in docs/ with valid naming should pass
        result = main(["docs/valid-name.md"])
        assert result == 0

    def test_root_changelog_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """CHANGELOG.md at root should pass validation (whitelisted)."""
        from scripts.ci.validate_naming_visibility import main

        # CHANGELOG.md is in RE_WHITELIST, should pass
        result = main(["CHANGELOG.md"])
        assert result == 0

    def test_root_contributing_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """CONTRIBUTING.md at root should pass validation (whitelisted)."""
        from scripts.ci.validate_naming_visibility import main

        # CONTRIBUTING.md is in RE_WHITELIST, should pass
        result = main(["CONTRIBUTING.md"])
        assert result == 0

    def test_root_random_uppercase_md_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """RANDOM-UPPERCASE-FILE.md at root should fail."""
        from scripts.ci.validate_naming_visibility import main

        # Random uppercase file not in whitelist should fail
        with pytest.raises(SystemExit) as exc_info:
            main(["RANDOM-UPPERCASE-FILE.md"])

        error_message = str(exc_info.value)
        assert "visibility-rules" in error_message.lower() or "root-level" in error_message.lower()

    def test_hestai_context_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """.hestai/ files should pass through to standard validation."""
        from scripts.ci.validate_naming_visibility import main

        # Files in .hestai/ should pass if they follow naming rules
        result = main([".hestai/context/PROJECT-CONTEXT.md"])
        assert result == 0

    def test_bundled_hub_governance_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Bundled hub payload docs should pass validation."""
        from scripts.ci.validate_naming_visibility import main

        result = main(["src/hestai_mcp/_bundled_hub/governance/rules/naming-standard.oct.md"])
        assert result == 0
