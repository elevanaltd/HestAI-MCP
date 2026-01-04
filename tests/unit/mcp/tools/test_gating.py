"""
Tests for Gating Module - OA-I6 Tool Gating Enforcement.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase)
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

OA-I6: TOOL GATING ENFORCEMENT
"Work tools MUST check for a valid anchor before executing.
Validation alone is insufficient; enforcement is mandatory."

Test Coverage:
- has_valid_anchor returns False for missing session
- has_valid_anchor returns False for unvalidated session
- has_valid_anchor returns True for validated session
- has_valid_anchor validates session_id format (security)
- has_valid_anchor prevents path traversal attacks

GitHub Issue: #11
ADR: docs/adr/adr-0036-odyssean-anchor-binding.md Amendment 01
"""

import json

import pytest

# =============================================================================
# GatingResult Dataclass Tests
# =============================================================================


@pytest.mark.unit
class TestGatingResultDataclass:
    """Test GatingResult dataclass structure."""

    def test_gating_result_has_required_fields(self):
        """GatingResult has all required fields."""
        from hestai_mcp.mcp.tools.gating import GatingResult

        result = GatingResult(
            valid=True,
            role="implementation-lead",
            tier="default",
            validated_at="2026-01-02T10:00:00+00:00",
            error=None,
        )

        assert hasattr(result, "valid")
        assert hasattr(result, "role")
        assert hasattr(result, "tier")
        assert hasattr(result, "validated_at")
        assert hasattr(result, "error")

    def test_gating_result_valid_case(self):
        """GatingResult valid case has role and tier."""
        from hestai_mcp.mcp.tools.gating import GatingResult

        result = GatingResult(
            valid=True,
            role="implementation-lead",
            tier="default",
            validated_at="2026-01-02T10:00:00+00:00",
            error=None,
        )

        assert result.valid is True
        assert result.role == "implementation-lead"
        assert result.tier == "default"
        assert result.validated_at is not None
        assert result.error is None

    def test_gating_result_invalid_case(self):
        """GatingResult invalid case has error."""
        from hestai_mcp.mcp.tools.gating import GatingResult

        result = GatingResult(
            valid=False,
            role=None,
            tier=None,
            validated_at=None,
            error="Session not found",
        )

        assert result.valid is False
        assert result.role is None
        assert result.error is not None


# =============================================================================
# has_valid_anchor Tests - Missing Session
# =============================================================================


@pytest.mark.unit
class TestHasValidAnchorMissingSession:
    """Test has_valid_anchor returns False for missing session."""

    def test_has_valid_anchor_returns_false_for_missing_session(self, tmp_path):
        """Returns False when session directory does not exist."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        result = has_valid_anchor(
            session_id="nonexistent-session-123",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None
        assert "session" in result.error.lower() or "not found" in result.error.lower()

    def test_has_valid_anchor_returns_false_for_empty_session_dir(self, tmp_path):
        """Returns False when session directory exists but is empty."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "empty-session-456"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        # Session directory exists but no anchor.json

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None


# =============================================================================
# has_valid_anchor Tests - Unvalidated Session
# =============================================================================


@pytest.mark.unit
class TestHasValidAnchorUnvalidatedSession:
    """Test has_valid_anchor returns False for unvalidated session."""

    def test_has_valid_anchor_returns_false_for_unvalidated_session(self, tmp_path):
        """Returns False when session exists but anchor not validated."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "unvalidated-session-789"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)

        # Create session.json but NO anchor.json
        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test-focus",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None
        assert "anchor" in result.error.lower() or "not validated" in result.error.lower()

    def test_has_valid_anchor_returns_false_for_validated_false(self, tmp_path):
        """Returns False when anchor.json exists but validated=false."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "invalid-anchor-session"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)

        # Create anchor.json with validated=false
        anchor_data = {
            "validated": False,
            "timestamp": "2026-01-02T10:00:00+00:00",
            "role": "implementation-lead",
            "tier": "default",
        }
        (session_dir / "anchor.json").write_text(json.dumps(anchor_data))

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None


# =============================================================================
# Anchor State Persistence Tests (odyssean_anchor writes anchor.json)
# =============================================================================


@pytest.mark.unit
class TestAnchorStatePersistence:
    """Test odyssean_anchor persists anchor state on success."""

    def test_odyssean_anchor_writes_anchor_json_on_success(self, tmp_path):
        """odyssean_anchor writes anchor.json when validation succeeds."""
        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-persist-session"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test-focus",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        valid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:.hestai/workflow/NORTH-STAR.md[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:docs/adr/adr-0036.md:177[schema]→TRIGGER[IMPLEMENT_MINIMAL]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/hestai_mcp/mcp/tools/gating.py
GATE::pytest tests/ -v"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=valid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is True

        # anchor.json should now exist
        anchor_file = session_dir / "anchor.json"
        assert anchor_file.exists(), "anchor.json was not created on successful validation"

        # Verify content
        anchor_data = json.loads(anchor_file.read_text())
        assert anchor_data["validated"] is True
        assert anchor_data["role"] == "implementation-lead"
        assert anchor_data["tier"] == "default"
        assert "timestamp" in anchor_data

    def test_odyssean_anchor_does_not_write_anchor_json_on_failure(self, tmp_path):
        """odyssean_anchor does NOT write anchor.json when validation fails."""
        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-no-persist-session"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test-focus",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Invalid vector - missing tensions
        invalid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[GENERIC_CONSTRAINT]⇌[state]→TRIGGER[ACTION]

## COMMIT (Falsifiable Contract)
ARTIFACT::response
GATE::review"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=invalid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False

        # anchor.json should NOT exist on failure
        anchor_file = session_dir / "anchor.json"
        assert not anchor_file.exists(), "anchor.json was created on failed validation"

    def test_has_valid_anchor_works_after_odyssean_anchor_success(self, tmp_path):
        """Integration: has_valid_anchor returns True after odyssean_anchor succeeds."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor
        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-integration-session"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "integration-test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # First verify no valid anchor exists
        result_before = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )
        assert result_before.valid is False

        # Now validate with odyssean_anchor
        valid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:.hestai/workflow/NORTH-STAR.md[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:docs/adr/adr-0036.md:177[schema]→TRIGGER[IMPLEMENT_MINIMAL]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/hestai_mcp/mcp/tools/gating.py
GATE::pytest tests/ -v"""

        oa_result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=valid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )
        assert oa_result.success is True

        # Now has_valid_anchor should return True
        result_after = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )
        assert result_after.valid is True
        assert result_after.role == "implementation-lead"
        assert result_after.tier == "default"


# =============================================================================
# has_valid_anchor Tests - Validated Session
# =============================================================================


@pytest.mark.unit
class TestHasValidAnchorValidatedSession:
    """Test has_valid_anchor returns True for validated session."""

    def test_has_valid_anchor_returns_true_for_validated_session(self, tmp_path):
        """Returns True when session has valid anchor.json."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "validated-session-abc"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)

        # Create valid anchor.json
        anchor_data = {
            "validated": True,
            "timestamp": "2026-01-02T10:00:00+00:00",
            "role": "implementation-lead",
            "tier": "default",
        }
        (session_dir / "anchor.json").write_text(json.dumps(anchor_data))

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True
        assert result.role == "implementation-lead"
        assert result.tier == "default"
        assert result.validated_at == "2026-01-02T10:00:00+00:00"
        assert result.error is None

    def test_has_valid_anchor_extracts_all_fields(self, tmp_path):
        """Extracts all fields from valid anchor.json."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "full-anchor-session"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)

        anchor_data = {
            "validated": True,
            "timestamp": "2026-01-02T12:30:45+00:00",
            "role": "holistic-orchestrator",
            "tier": "deep",
        }
        (session_dir / "anchor.json").write_text(json.dumps(anchor_data))

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True
        assert result.role == "holistic-orchestrator"
        assert result.tier == "deep"
        assert result.validated_at == "2026-01-02T12:30:45+00:00"


# =============================================================================
# has_valid_anchor Tests - Session ID Format Validation
# =============================================================================


@pytest.mark.unit
class TestHasValidAnchorSessionIdFormat:
    """Test has_valid_anchor validates session_id format."""

    def test_has_valid_anchor_validates_session_id_format(self, tmp_path):
        """Rejects empty session_id."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        result = has_valid_anchor(
            session_id="",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None
        assert "session_id" in result.error.lower() or "empty" in result.error.lower()

    def test_has_valid_anchor_accepts_uuid_format(self, tmp_path):
        """Accepts UUID-format session_id."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)

        anchor_data = {
            "validated": True,
            "timestamp": "2026-01-02T10:00:00+00:00",
            "role": "test-role",
            "tier": "quick",
        }
        (session_dir / "anchor.json").write_text(json.dumps(anchor_data))

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True

    def test_has_valid_anchor_accepts_alphanumeric_with_hyphens(self, tmp_path):
        """Accepts alphanumeric session_id with hyphens."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "valid-session-id-123"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)

        anchor_data = {
            "validated": True,
            "timestamp": "2026-01-02T10:00:00+00:00",
            "role": "test-role",
            "tier": "default",
        }
        (session_dir / "anchor.json").write_text(json.dumps(anchor_data))

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True


# =============================================================================
# has_valid_anchor Tests - Path Traversal Prevention (Security)
# =============================================================================


@pytest.mark.unit
class TestHasValidAnchorPathTraversalPrevention:
    """Test has_valid_anchor prevents path traversal attacks."""

    def test_has_valid_anchor_prevents_path_traversal_parent(self, tmp_path):
        """Rejects session_id with parent directory traversal (..)."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        result = has_valid_anchor(
            session_id="../../../etc/passwd",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None
        assert "path" in result.error.lower() or "invalid" in result.error.lower()

    def test_has_valid_anchor_prevents_path_traversal_absolute(self, tmp_path):
        """Rejects session_id with absolute path."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        result = has_valid_anchor(
            session_id="/tmp/malicious",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None

    def test_has_valid_anchor_prevents_path_traversal_slash(self, tmp_path):
        """Rejects session_id with forward slash."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        result = has_valid_anchor(
            session_id="foo/bar",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None

    def test_has_valid_anchor_prevents_path_traversal_backslash(self, tmp_path):
        """Rejects session_id with backslash (Windows path separator)."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        result = has_valid_anchor(
            session_id="foo\\bar",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None


# =============================================================================
# has_valid_anchor Tests - Error Handling
# =============================================================================


@pytest.mark.unit
class TestHasValidAnchorErrorHandling:
    """Test has_valid_anchor error handling."""

    def test_has_valid_anchor_handles_invalid_json(self, tmp_path):
        """Handles malformed anchor.json gracefully."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "bad-json-session"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)

        # Write invalid JSON
        (session_dir / "anchor.json").write_text("{ invalid json }")

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None

    def test_has_valid_anchor_handles_missing_validated_field(self, tmp_path):
        """Handles anchor.json missing validated field."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        session_id = "missing-field-session"
        session_dir = working_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)

        # Create anchor.json without validated field
        anchor_data = {
            "timestamp": "2026-01-02T10:00:00+00:00",
            "role": "test-role",
        }
        (session_dir / "anchor.json").write_text(json.dumps(anchor_data))

        result = has_valid_anchor(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert result.error is not None

    def test_has_valid_anchor_handles_nonexistent_working_dir(self, tmp_path):
        """Handles nonexistent working directory."""
        from hestai_mcp.mcp.tools.gating import has_valid_anchor

        result = has_valid_anchor(
            session_id="some-session",
            working_dir="/nonexistent/path/to/project",
        )

        assert result.valid is False
        assert result.error is not None
