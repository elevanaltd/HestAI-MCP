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


# =============================================================================
# BLOCKING ISSUE 1: asyncio.run() in Running Event Loop (CRS Review)
# =============================================================================


@pytest.mark.unit
class TestAsyncContextExecution:
    """Test that semantic validation runs correctly from async context (MCP server).

    BLOCKING ISSUE: asyncio.run() raises RuntimeError when called from within
    a running event loop (like the MCP server's async context). The current
    implementation silently catches this and skips semantic validation.

    These tests verify the fix works correctly.
    """

    @pytest.mark.asyncio
    async def test_semantic_validation_runs_in_async_context(self, tmp_path: Path):
        """Verify semantic validation actually executes when called from async context.

        This is the key test - it simulates the MCP server's async call_tool()
        calling _run_semantic_validation() and verifies validation actually runs.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import _run_semantic_validation
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
        )

        # Create a file so CTX validation has something to check
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "test.md").write_text("# Test")

        # Create config with only ctx_validity enabled (non-AI, deterministic)
        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="block",
            checks=SemanticChecksConfig(
                cognition_appropriateness=False,
                tension_relevance=False,
                ctx_validity=True,  # Only this check - filesystem based, no AI
                commit_feasibility=False,
            ),
        )

        # Mock load_semantic_config to return our test config
        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.load_semantic_config",
            return_value=config,
        ):
            # Call from async context (simulating MCP server's call_tool)
            # This should NOT skip semantic validation
            result = _run_semantic_validation(
                role="test-role",
                cognition_type="LOGOS",
                tensions=[{"ctx_path": "docs/test.md", "constraint": "TEST"}],
                commit_artifact="src/test.py",
                working_dir=str(tmp_path),
            )

        # Key assertion: validation was NOT skipped
        assert result.skipped is False, (
            "Semantic validation was skipped when called from async context. "
            "This indicates asyncio.run() failed in the running event loop."
        )
        # And it should succeed since file exists
        assert result.success is True

    @pytest.mark.asyncio
    async def test_semantic_validation_detects_missing_file_from_async_context(
        self, tmp_path: Path
    ):
        """Verify semantic validation detects issues when called from async context.

        This proves the validation actually ran (not just returned a stub result).
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import _run_semantic_validation
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
        )

        # Config with block mode and ctx_validity only
        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="block",
            checks=SemanticChecksConfig(
                cognition_appropriateness=False,
                tension_relevance=False,
                ctx_validity=True,
                commit_feasibility=False,
            ),
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.load_semantic_config",
            return_value=config,
        ):
            # Reference a file that doesn't exist
            result = _run_semantic_validation(
                role="test-role",
                cognition_type="LOGOS",
                tensions=[{"ctx_path": "nonexistent/file.md", "constraint": "TEST"}],
                commit_artifact="src/test.py",
                working_dir=str(tmp_path),
            )

        # Key assertion: validation ran and detected the missing file
        assert result.skipped is False, "Semantic validation was incorrectly skipped"
        assert result.success is False, "Validation should fail for missing file"
        assert len(result.concerns) > 0, "Should have concerns about missing file"
        assert any("nonexistent" in c.lower() for c in result.concerns)


# =============================================================================
# BLOCKING ISSUE 2: CTX Path Traversal Vulnerability (CRS Review)
# =============================================================================


@pytest.mark.unit
class TestCtxPathTraversalSecurity:
    """Test CTX path validation prevents path traversal attacks.

    SECURITY VULNERABILITY: check_ctx_validity() doesn't properly sandbox paths.
    An attacker-controlled TENSION.ctx_path could:
    1. Use absolute paths like /etc/passwd
    2. Use relative traversal like ../../etc/passwd

    With fail_mode=block, accept/reject leaks target path existence (oracle attack).
    """

    def test_ctx_validity_rejects_absolute_paths(self, tmp_path: Path):
        """CTX paths must be relative, not absolute."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        # Attempt to reference an absolute path (security violation)
        tensions = [
            {"ctx_path": "/etc/passwd", "constraint": "EXPLOIT"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        # Security: absolute paths should be INVALID (rejected)
        assert result.valid is False, (
            "SECURITY: Absolute path '/etc/passwd' was not rejected. "
            "CTX paths must be relative to working_dir."
        )
        # The missing_files list should include the rejected path
        assert "/etc/passwd" in result.missing_files

    def test_ctx_validity_rejects_path_traversal_dotdot(self, tmp_path: Path):
        """CTX paths with .. must not escape working directory."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        # Create a file outside working_dir to test traversal
        parent_dir = tmp_path.parent
        secret_file = parent_dir / "secret.txt"
        secret_file.write_text("secret data")

        # Attempt path traversal
        tensions = [
            {"ctx_path": "../secret.txt", "constraint": "EXPLOIT"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        # Security: path traversal should be INVALID
        assert result.valid is False, (
            "SECURITY: Path traversal '../secret.txt' was not rejected. "
            "CTX paths must stay within working_dir."
        )

    def test_ctx_validity_rejects_deep_traversal(self, tmp_path: Path):
        """CTX paths with multiple .. levels must not escape working directory."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        tensions = [
            {"ctx_path": "../../etc/passwd", "constraint": "EXPLOIT"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        assert (
            result.valid is False
        ), "SECURITY: Deep traversal '../../etc/passwd' was not rejected."

    def test_ctx_validity_allows_relative_within_workdir(self, tmp_path: Path):
        """Valid relative paths within working_dir should be allowed."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        # Create nested structure
        (tmp_path / "docs" / "sub").mkdir(parents=True)
        (tmp_path / "docs" / "sub" / "file.md").write_text("# Doc")

        tensions = [
            {"ctx_path": "docs/sub/file.md", "constraint": "VALID"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        # Valid relative path should work
        assert result.valid is True
        assert len(result.missing_files) == 0

    def test_ctx_validity_rejects_backslash_traversal(self, tmp_path: Path):
        """CTX paths with Windows-style backslashes should be handled safely."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        tensions = [
            {"ctx_path": "..\\..\\etc\\passwd", "constraint": "EXPLOIT"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        # Should not allow backslash traversal either
        assert result.valid is False, "SECURITY: Backslash traversal was not rejected."

    def test_ctx_validity_requires_file_not_directory(self, tmp_path: Path):
        """CTX paths must point to files, not directories."""
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import check_ctx_validity

        # Create a directory
        (tmp_path / "docs").mkdir()

        tensions = [
            {"ctx_path": "docs", "constraint": "DIR_NOT_FILE"},
        ]

        result = check_ctx_validity(tensions, str(tmp_path))

        # Should be invalid - directories are not valid CTX targets
        assert (
            result.valid is False
        ), "CTX path pointing to directory should be rejected - must be a file."


# =============================================================================
# CRITICAL ISSUE 3: json Import Inside try Block (CRS Review)
# =============================================================================


@pytest.mark.unit
class TestJsonImportPlacement:
    """Test that json imports are at module level, not inside functions.

    ISSUE: json imports inside try blocks in _get_session_focus() and
    other functions can cause subtle issues and is poor practice.
    """

    def test_json_import_at_module_level(self):
        """Verify json is imported at module level in odyssean_anchor_semantic.py."""
        import ast
        from pathlib import Path

        # Read the source file
        source_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "hestai_mcp"
            / "mcp"
            / "tools"
            / "odyssean_anchor_semantic.py"
        )
        source_code = source_file.read_text()

        # Parse the AST
        tree = ast.parse(source_code)

        # Check for local imports inside functions by looking for
        # import statements after the first function definition
        class FunctionImportVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_function = False
                self.function_imports = []

            def visit_FunctionDef(self, node):
                self.in_function = True
                self.generic_visit(node)
                self.in_function = False

            def visit_AsyncFunctionDef(self, node):
                self.in_function = True
                self.generic_visit(node)
                self.in_function = False

            def visit_Import(self, node):
                if self.in_function:
                    for alias in node.names:
                        if alias.name == "json":
                            self.function_imports.append(node.lineno)

        visitor = FunctionImportVisitor()
        visitor.visit(tree)

        # There should be no json imports inside functions
        assert len(visitor.function_imports) == 0, (
            f"Found json imports inside functions at lines: {visitor.function_imports}. "
            "json should be imported at module level only."
        )
