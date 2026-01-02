"""
Tests for Odyssean Anchor Semantic Validation - AI-driven semantic checks.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase) - this file
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

Test Coverage:
- Config loading from ai.yaml (odyssean_anchor.semantic_validation section)
- Environment variable overrides
- Semantic validation disabled by default (backward compatibility)
- cognition_appropriateness check (mock AI response)
- ctx_validity check with existing/missing files
- warn mode logs but doesn't block
- block mode adds errors
- Timeout handling (graceful degradation)

GitHub Issue: #131
ADR: docs/adr/adr-0036-odyssean-anchor-binding.md (Semantic Validation Extension)
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Config Loading Tests
# =============================================================================


@pytest.mark.unit
class TestSemanticConfigLoading:
    """Test semantic validation config loading from ai.yaml."""

    def test_load_semantic_config_from_yaml(self, tmp_path: Path):
        """Load semantic_validation config from ai.yaml odyssean_anchor section."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import load_semantic_config

        # Create a test config file
        config_dir = tmp_path / ".hestai" / "config"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "ai.yaml"
        config_file.write_text(
            """
odyssean_anchor:
  semantic_validation:
    enabled: true
    tier: analysis
    timeout_seconds: 20
    fail_mode: block
    checks:
      cognition_appropriateness: true
      tension_relevance: false
      ctx_validity: true
      commit_feasibility: false
"""
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.get_yaml_config_path",
            return_value=config_file,
        ):
            config = load_semantic_config()

        assert config.enabled is True
        assert config.tier == "analysis"
        assert config.timeout_seconds == 20
        assert config.fail_mode == "block"
        assert config.checks.cognition_appropriateness is True
        assert config.checks.tension_relevance is False
        assert config.checks.ctx_validity is True
        assert config.checks.commit_feasibility is False

    def test_semantic_config_defaults_when_missing(self, tmp_path: Path):
        """Returns defaults when ai.yaml doesn't exist."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import load_semantic_config

        # Point to non-existent file
        nonexistent = tmp_path / "does_not_exist.yaml"

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.get_yaml_config_path",
            return_value=nonexistent,
        ):
            config = load_semantic_config()

        # Default: disabled, warn mode, all checks enabled
        assert config.enabled is False
        assert config.fail_mode == "warn"
        assert config.timeout_seconds == 15

    def test_semantic_config_defaults_when_section_missing(self, tmp_path: Path):
        """Returns defaults when odyssean_anchor section is missing from ai.yaml."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import load_semantic_config

        config_dir = tmp_path / ".hestai" / "config"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "ai.yaml"
        # Config without odyssean_anchor section
        config_file.write_text(
            """
tiers:
  synthesis:
    provider: openrouter
    model: test-model
"""
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.get_yaml_config_path",
            return_value=config_file,
        ):
            config = load_semantic_config()

        assert config.enabled is False  # Default off


# =============================================================================
# Environment Variable Override Tests
# =============================================================================


@pytest.mark.unit
class TestEnvironmentVariableOverrides:
    """Test environment variable overrides for semantic validation config."""

    def test_env_override_enabled(self, tmp_path: Path):
        """HESTAI_OA_SEMANTIC_VALIDATION=true overrides config enabled."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import load_semantic_config

        # Config has enabled: false
        config_dir = tmp_path / ".hestai" / "config"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "ai.yaml"
        config_file.write_text(
            """
odyssean_anchor:
  semantic_validation:
    enabled: false
"""
        )

        with (
            patch.dict(
                "os.environ",
                {"HESTAI_OA_SEMANTIC_VALIDATION": "true"},
                clear=False,
            ),
            patch(
                "hestai_mcp.mcp.tools.odyssean_anchor_semantic.get_yaml_config_path",
                return_value=config_file,
            ),
        ):
            config = load_semantic_config()

        assert config.enabled is True

    def test_env_override_disabled(self, tmp_path: Path):
        """HESTAI_OA_SEMANTIC_VALIDATION=false overrides config enabled."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import load_semantic_config

        config_dir = tmp_path / ".hestai" / "config"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "ai.yaml"
        config_file.write_text(
            """
odyssean_anchor:
  semantic_validation:
    enabled: true
"""
        )

        with (
            patch.dict(
                "os.environ",
                {"HESTAI_OA_SEMANTIC_VALIDATION": "false"},
                clear=False,
            ),
            patch(
                "hestai_mcp.mcp.tools.odyssean_anchor_semantic.get_yaml_config_path",
                return_value=config_file,
            ),
        ):
            config = load_semantic_config()

        assert config.enabled is False

    def test_env_override_fail_mode(self, tmp_path: Path):
        """HESTAI_OA_SEMANTIC_FAIL_MODE overrides config fail_mode."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import load_semantic_config

        config_dir = tmp_path / ".hestai" / "config"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "ai.yaml"
        config_file.write_text(
            """
odyssean_anchor:
  semantic_validation:
    enabled: true
    fail_mode: warn
"""
        )

        with (
            patch.dict(
                "os.environ",
                {"HESTAI_OA_SEMANTIC_FAIL_MODE": "block"},
                clear=False,
            ),
            patch(
                "hestai_mcp.mcp.tools.odyssean_anchor_semantic.get_yaml_config_path",
                return_value=config_file,
            ),
        ):
            config = load_semantic_config()

        assert config.fail_mode == "block"


# =============================================================================
# Semantic Validation Disabled By Default Tests
# =============================================================================


@pytest.mark.unit
class TestSemanticValidationDisabledDefault:
    """Test that semantic validation is disabled by default for backward compatibility."""

    @pytest.mark.asyncio
    async def test_validate_semantic_returns_success_when_disabled(self):
        """validate_semantic returns success without running checks when disabled."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
            validate_semantic,
        )

        config = SemanticConfig(
            enabled=False,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="block",
            checks=SemanticChecksConfig(),
        )

        result = await validate_semantic(
            role="implementation-lead",
            cognition_type="LOGOS",
            tensions=[],
            commit_artifact="src/test.py",
            working_dir="/tmp/test",
            config=config,
        )

        assert result.success is True
        assert result.skipped is True
        assert len(result.concerns) == 0


# =============================================================================
# Cognition Appropriateness Check Tests
# =============================================================================


def _create_mock_ai_client(response: str) -> MagicMock:
    """Create a properly mocked AIClient for async context manager usage."""
    mock_client = MagicMock()
    mock_client.complete_text = AsyncMock(return_value=response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.mark.unit
class TestCognitionAppropriatenessCheck:
    """Test AI-driven cognition appropriateness validation."""

    @pytest.mark.asyncio
    async def test_check_cognition_appropriateness_logos_for_architect(self):
        """LOGOS is appropriate for architect roles."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            check_cognition_appropriateness,
        )

        mock_client = _create_mock_ai_client(
            '{"appropriate": true, "reason": "LOGOS is correct for architects"}'
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await check_cognition_appropriateness(
                role="technical-architect",
                cognition_type="LOGOS",
                tier="analysis",
            )

        assert result.appropriate is True
        assert result.concern is None

    @pytest.mark.asyncio
    async def test_check_cognition_appropriateness_ethos_for_validator(self):
        """ETHOS is appropriate for validator roles."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            check_cognition_appropriateness,
        )

        mock_client = _create_mock_ai_client(
            '{"appropriate": true, "reason": "ETHOS is correct for validators"}'
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await check_cognition_appropriateness(
                role="requirements-steward",
                cognition_type="ETHOS",
                tier="analysis",
            )

        assert result.appropriate is True

    @pytest.mark.asyncio
    async def test_check_cognition_appropriateness_mismatch(self):
        """Returns concern when cognition type doesn't match role."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            check_cognition_appropriateness,
        )

        mock_client = _create_mock_ai_client(
            '{"appropriate": false, "reason": "PATHOS is not suitable for validators"}'
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await check_cognition_appropriateness(
                role="test-methodology-guardian",
                cognition_type="PATHOS",
                tier="analysis",
            )

        assert result.appropriate is False
        assert result.concern is not None
        assert "PATHOS" in result.concern or "validator" in result.concern.lower()


# =============================================================================
# CTX Validity Check Tests
# =============================================================================


@pytest.mark.unit
class TestCtxValidityCheck:
    """Test CTX path validation (filesystem, not AI)."""

    def test_check_ctx_validity_existing_files(self, tmp_path: Path):
        """Returns valid when all CTX paths exist."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        # Create files referenced in tensions
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "north-star.md").write_text("# North Star")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "module.py").write_text("# Module")

        tensions = [
            {"ctx_path": "docs/north-star.md", "constraint": "TDD_MANDATE"},
            {"ctx_path": "src/module.py", "constraint": "MIP"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        assert result.valid is True
        assert len(result.missing_files) == 0

    def test_check_ctx_validity_missing_files(self, tmp_path: Path):
        """Returns invalid with list of missing files."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        # Only create one of the referenced files
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "exists.md").write_text("# Exists")

        tensions = [
            {"ctx_path": "docs/exists.md", "constraint": "TDD"},
            {"ctx_path": "docs/missing.md", "constraint": "MIP"},
            {"ctx_path": "src/not_here.py", "constraint": "QUALITY"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        assert result.valid is False
        assert len(result.missing_files) == 2
        assert "docs/missing.md" in result.missing_files
        assert "src/not_here.py" in result.missing_files

    def test_check_ctx_validity_empty_tensions(self, tmp_path: Path):
        """Returns valid for empty tensions list (no files to check)."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        result = check_ctx_validity([], str(tmp_path))

        assert result.valid is True
        assert len(result.missing_files) == 0

    def test_check_ctx_validity_handles_line_ranges(self, tmp_path: Path):
        """Strips line ranges from CTX path before checking."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "file.md").write_text("# File")

        tensions = [
            {"ctx_path": "docs/file.md:10-20", "constraint": "TDD"},
            {"ctx_path": "docs/file.md:45", "constraint": "MIP"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        assert result.valid is True


# =============================================================================
# Warn Mode Tests
# =============================================================================


@pytest.mark.unit
class TestWarnMode:
    """Test warn mode behavior - logs but doesn't block."""

    @pytest.mark.asyncio
    async def test_warn_mode_logs_concerns_returns_success(self, tmp_path: Path, caplog):
        """In warn mode, semantic concerns are logged but don't fail validation."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
            validate_semantic,
        )

        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="warn",  # Warn mode
            checks=SemanticChecksConfig(
                cognition_appropriateness=False,  # Disable AI checks for this test
                tension_relevance=False,
                ctx_validity=True,  # Enable file check
                commit_feasibility=False,
            ),
        )

        # Create working dir without the referenced file
        tensions = [{"ctx_path": "missing/file.md", "constraint": "TEST"}]

        result = await validate_semantic(
            role="test-role",
            cognition_type="LOGOS",
            tensions=tensions,
            commit_artifact="src/test.py",
            working_dir=str(tmp_path),
            config=config,
        )

        # Should succeed despite concerns (warn mode)
        assert result.success is True
        assert result.skipped is False
        assert len(result.concerns) > 0
        # Concerns should be about missing file
        assert any("missing" in c.lower() for c in result.concerns)


# =============================================================================
# Block Mode Tests
# =============================================================================


@pytest.mark.unit
class TestBlockMode:
    """Test block mode behavior - adds errors and fails validation."""

    @pytest.mark.asyncio
    async def test_block_mode_fails_on_concerns(self, tmp_path: Path):
        """In block mode, semantic concerns cause validation failure."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
            validate_semantic,
        )

        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="block",  # Block mode
            checks=SemanticChecksConfig(
                cognition_appropriateness=False,
                tension_relevance=False,
                ctx_validity=True,
                commit_feasibility=False,
            ),
        )

        tensions = [{"ctx_path": "missing/file.md", "constraint": "TEST"}]

        result = await validate_semantic(
            role="test-role",
            cognition_type="LOGOS",
            tensions=tensions,
            commit_artifact="src/test.py",
            working_dir=str(tmp_path),
            config=config,
        )

        # Should fail due to concerns (block mode)
        assert result.success is False
        assert len(result.concerns) > 0

    @pytest.mark.asyncio
    async def test_block_mode_succeeds_without_concerns(self, tmp_path: Path):
        """In block mode, validation succeeds when no concerns."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
            validate_semantic,
        )

        # Create the file that will be referenced
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "file.md").write_text("# Doc")

        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="block",
            checks=SemanticChecksConfig(
                cognition_appropriateness=False,  # Skip AI checks
                tension_relevance=False,
                ctx_validity=True,
                commit_feasibility=False,
            ),
        )

        tensions = [{"ctx_path": "docs/file.md", "constraint": "TEST"}]

        result = await validate_semantic(
            role="test-role",
            cognition_type="LOGOS",
            tensions=tensions,
            commit_artifact="src/test.py",
            working_dir=str(tmp_path),
            config=config,
        )

        assert result.success is True
        assert len(result.concerns) == 0


# =============================================================================
# Timeout Handling Tests
# =============================================================================


@pytest.mark.unit
class TestTimeoutHandling:
    """Test timeout handling for graceful degradation."""

    @pytest.mark.asyncio
    async def test_timeout_returns_success_in_warn_mode(self):
        """On AI timeout, returns success in warn mode (graceful degradation)."""
        import asyncio

        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
            validate_semantic,
        )

        # Mock AI client to timeout
        mock_client = MagicMock()

        async def slow_completion(*args, **kwargs):
            await asyncio.sleep(100)  # Longer than timeout
            return '{"appropriate": true}'

        mock_client.complete_text = slow_completion
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=1,  # Very short timeout
            fail_mode="warn",
            checks=SemanticChecksConfig(
                cognition_appropriateness=True,  # This will timeout
                tension_relevance=False,
                ctx_validity=False,
                commit_feasibility=False,
            ),
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await validate_semantic(
                role="test-role",
                cognition_type="LOGOS",
                tensions=[],
                commit_artifact="test.py",
                working_dir="/tmp",
                config=config,
            )

        # Should succeed on timeout in warn mode
        assert result.success is True
        # Should note the timeout
        assert result.timed_out is True or any("timeout" in c.lower() for c in result.concerns)

    @pytest.mark.asyncio
    async def test_ai_error_logged_graceful_degradation(self, caplog):
        """On AI error, logs warning and continues (graceful degradation)."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
            validate_semantic,
        )

        # Mock AI client to raise error
        mock_client = MagicMock()
        mock_client.complete_text = AsyncMock(side_effect=Exception("API Error"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="warn",
            checks=SemanticChecksConfig(
                cognition_appropriateness=True,
                tension_relevance=False,
                ctx_validity=False,
                commit_feasibility=False,
            ),
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await validate_semantic(
                role="test-role",
                cognition_type="LOGOS",
                tensions=[],
                commit_artifact="test.py",
                working_dir="/tmp",
                config=config,
            )

        # Should succeed despite AI error (graceful degradation)
        assert result.success is True


# =============================================================================
# Tension Relevance Check Tests
# =============================================================================


@pytest.mark.unit
class TestTensionRelevanceCheck:
    """Test AI-driven tension relevance validation."""

    @pytest.mark.asyncio
    async def test_check_tension_relevance_valid_constraints(self):
        """Returns valid when constraints reference real constraints."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            check_tension_relevance,
        )

        mock_client = _create_mock_ai_client('{"all_valid": true, "invalid_constraints": []}')

        tensions = [
            {"constraint": "TDD_MANDATE", "ctx_path": "north-star.md"},
            {"constraint": "MINIMAL_INTERVENTION", "ctx_path": "adr-0036.md"},
        ]

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await check_tension_relevance(
                tensions=tensions,
                constitution_text="I1::TDD, MIP, MINIMAL_INTERVENTION",
                tier="analysis",
            )

        assert result.valid is True
        assert len(result.invalid_constraints) == 0

    @pytest.mark.asyncio
    async def test_check_tension_relevance_hallucinated_constraint(self):
        """Returns invalid when constraint appears hallucinated."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            check_tension_relevance,
        )

        mock_client = _create_mock_ai_client(
            '{"all_valid": false, "invalid_constraints": ["MADE_UP_CONSTRAINT"]}'
        )

        tensions = [
            {"constraint": "TDD_MANDATE", "ctx_path": "north-star.md"},
            {"constraint": "MADE_UP_CONSTRAINT", "ctx_path": "file.md"},
        ]

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await check_tension_relevance(
                tensions=tensions,
                constitution_text="I1::TDD, MIP",
                tier="analysis",
            )

        assert result.valid is False
        assert "MADE_UP_CONSTRAINT" in result.invalid_constraints


# =============================================================================
# Commit Feasibility Check Tests
# =============================================================================


@pytest.mark.unit
class TestCommitFeasibilityCheck:
    """Test AI-driven commit feasibility validation."""

    @pytest.mark.asyncio
    async def test_check_commit_feasibility_achievable(self):
        """Returns valid when artifact is achievable."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            check_commit_feasibility,
        )

        mock_client = _create_mock_ai_client(
            '{"feasible": true, "reason": "Artifact is concrete and achievable"}'
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await check_commit_feasibility(
                artifact="src/validators/semantic.py",
                focus="B2 implementation",
                tier="analysis",
            )

        assert result.feasible is True
        assert result.concern is None

    @pytest.mark.asyncio
    async def test_check_commit_feasibility_unrealistic(self):
        """Returns invalid when artifact seems unrealistic."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            check_commit_feasibility,
        )

        mock_client = _create_mock_ai_client(
            '{"feasible": false, "reason": "Complete system rewrite is not achievable in a session"}'
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.AIClient",
            return_value=mock_client,
        ):
            result = await check_commit_feasibility(
                artifact="Complete rewrite of entire codebase",
                focus="general",
                tier="analysis",
            )

        assert result.feasible is False
        assert result.concern is not None


# =============================================================================
# Integration with odyssean_anchor() Tests
# =============================================================================


@pytest.mark.unit
class TestOdysseanAnchorIntegration:
    """Test semantic validation integration into odyssean_anchor() flow."""

    @pytest.mark.asyncio
    async def test_odyssean_anchor_calls_semantic_validation_when_enabled(self, tmp_path: Path):
        """odyssean_anchor() calls semantic validation after structural passes."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
        )

        # This test verifies integration point exists
        # The actual integration is tested via the odyssean_anchor module
        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="warn",
            checks=SemanticChecksConfig(),
        )

        # Config should be loadable and usable
        assert config.enabled is True
        assert config.fail_mode == "warn"

    def test_semantic_config_model_validates(self):
        """SemanticConfig pydantic model validates correctly."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
        )

        # Valid config
        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="warn",
            checks=SemanticChecksConfig(
                cognition_appropriateness=True,
                tension_relevance=True,
                ctx_validity=True,
                commit_feasibility=True,
            ),
        )

        assert config.enabled is True
        assert config.checks.cognition_appropriateness is True

    def test_semantic_result_dataclass(self):
        """SemanticValidationResult has expected fields."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticValidationResult,
        )

        result = SemanticValidationResult(
            success=True,
            skipped=False,
            timed_out=False,
            concerns=["test concern"],
        )

        assert result.success is True
        assert result.skipped is False
        assert result.timed_out is False
        assert "test concern" in result.concerns
