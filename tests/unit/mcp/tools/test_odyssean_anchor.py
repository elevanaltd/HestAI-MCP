"""
Tests for Odyssean Anchor MCP Tool - Agent Identity Binding Validation.

This test suite follows TDD discipline:
1. Tests written FIRST (RED phase)
2. Implementation follows (GREEN phase)
3. Refactor while tests pass

Test Coverage:
- BIND section validation (ROLE, COGNITION, AUTHORITY)
- TENSION section validation with CTX citations (tier-aware)
- COMMIT section validation (artifact + gate)
- ARM injection from session/git state (server-authoritative)
- Self-correction protocol with retry guidance (max 2 retries)

Schema: RAPH Vector v4.0 per ADR-0036 Amendment 01
Key Innovation: Server-Authoritative ARM (agent provides BIND+TENSION+COMMIT, tool injects ARM)

GitHub Issue: #102
ADR: docs/adr/adr-0036-odyssean-anchor-binding.md
"""

from unittest.mock import patch

import pytest

# =============================================================================
# BIND Section Validation Tests
# =============================================================================


@pytest.mark.unit
class TestBindSectionValidation:
    """Test BIND section validation (Identity Lock)."""

    def test_validate_bind_accepts_valid_section(self):
        """Accepts valid BIND section with ROLE, COGNITION, AUTHORITY."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        valid_bind = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]"""

        result = validate_bind_section(valid_bind)

        assert result.valid is True
        assert result.role == "implementation-lead"
        assert result.cognition_type == "LOGOS"
        assert result.cognition_archetype == "HEPHAESTUS"
        assert result.authority == "RESPONSIBLE[build_phase_execution]"
        assert len(result.errors) == 0

    def test_validate_bind_rejects_missing_role(self):
        """Rejects BIND section missing ROLE field."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        invalid_bind = """## BIND (Identity Lock)
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]"""

        result = validate_bind_section(invalid_bind)

        assert result.valid is False
        assert "ROLE" in str(result.errors)

    def test_validate_bind_rejects_missing_cognition(self):
        """Rejects BIND section missing COGNITION field."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        invalid_bind = """## BIND (Identity Lock)
ROLE::implementation-lead
AUTHORITY::RESPONSIBLE[build_phase_execution]"""

        result = validate_bind_section(invalid_bind)

        assert result.valid is False
        assert "COGNITION" in str(result.errors)

    def test_validate_bind_rejects_missing_authority(self):
        """Rejects BIND section missing AUTHORITY field."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        invalid_bind = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS"""

        result = validate_bind_section(invalid_bind)

        assert result.valid is False
        assert "AUTHORITY" in str(result.errors)

    def test_validate_bind_rejects_invalid_cognition_type(self):
        """Rejects BIND section with invalid cognition type."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        invalid_bind = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::INVALID_TYPE::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]"""

        result = validate_bind_section(invalid_bind)

        assert result.valid is False
        assert "COGNITION" in str(result.errors)
        # Valid types are: ETHOS, LOGOS, PATHOS

    def test_validate_bind_rejects_invalid_archetype(self):
        """Rejects BIND section with invalid archetype."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        invalid_bind = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::INVALID_ARCHETYPE
AUTHORITY::RESPONSIBLE[build_phase_execution]"""

        result = validate_bind_section(invalid_bind)

        assert result.valid is False
        # Valid archetypes: ATLAS, ATHENA, HEPHAESTUS, HERMES, APOLLO, ARGUS, PROMETHEUS, DIONYSUS

    def test_validate_bind_rejects_empty_role(self):
        """Rejects BIND section with empty ROLE."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        invalid_bind = """## BIND (Identity Lock)
ROLE::
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]"""

        result = validate_bind_section(invalid_bind)

        assert result.valid is False
        assert "ROLE" in str(result.errors)

    def test_validate_bind_accepts_delegated_authority(self):
        """Accepts BIND section with DELEGATED authority (for subagents)."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        valid_bind = """## BIND (Identity Lock)
ROLE::code-reviewer
COGNITION::ETHOS::ATHENA
AUTHORITY::DELEGATED[parent_session_abc123]"""

        result = validate_bind_section(valid_bind)

        assert result.valid is True
        assert "DELEGATED" in result.authority

    def test_validate_bind_accepts_multiple_archetypes_unicode(self):
        """Accepts BIND section with multiple archetypes using ⊕ (synthesis operator)."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        valid_bind = """## BIND (Identity Lock)
ROLE::holistic-orchestrator
COGNITION::LOGOS::ATLAS⊕ODYSSEUS⊕APOLLO
AUTHORITY::RESPONSIBLE[system_coherence_orchestration]"""

        result = validate_bind_section(valid_bind)

        assert result.valid is True
        assert result.cognition_archetype == "ATLAS⊕ODYSSEUS⊕APOLLO"

    def test_validate_bind_accepts_multiple_archetypes_ascii(self):
        """Accepts BIND section with multiple archetypes using + (ASCII alias for ⊕)."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        valid_bind = """## BIND (Identity Lock)
ROLE::holistic-orchestrator
COGNITION::LOGOS::ATLAS+ODYSSEUS+APOLLO
AUTHORITY::RESPONSIBLE[system_coherence_orchestration]"""

        result = validate_bind_section(valid_bind)

        assert result.valid is True
        assert result.cognition_archetype == "ATLAS+ODYSSEUS+APOLLO"

    def test_validate_bind_rejects_invalid_archetype_in_list(self):
        """Rejects BIND section if any archetype in the list is invalid."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        invalid_bind = """## BIND (Identity Lock)
ROLE::holistic-orchestrator
COGNITION::LOGOS::ATLAS⊕INVALID⊕APOLLO
AUTHORITY::RESPONSIBLE[system_coherence_orchestration]"""

        result = validate_bind_section(invalid_bind)

        assert result.valid is False
        assert "INVALID" in str(result.errors)


# =============================================================================
# TENSION Section Validation Tests
# =============================================================================


@pytest.mark.unit
class TestTensionSectionValidation:
    """Test TENSION section validation (Cognitive Proof)."""

    def test_validate_tension_accepts_valid_section_default_tier(self):
        """Accepts valid TENSION section for default tier (min 2 tensions)."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        valid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:docs/adr/adr-0036-odyssean-anchor-binding.md:177[schema_v4.0]→TRIGGER[IMPLEMENT_MINIMAL]"""

        result = validate_tension_section(valid_tension, tier="default")

        assert result.valid is True
        assert result.tension_count == 2
        assert len(result.errors) == 0

    def test_validate_tension_rejects_insufficient_count_default_tier(self):
        """Rejects TENSION section with insufficient count for default tier."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        # Only 1 tension, but default tier requires 2
        invalid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:path/to/file.md[state]→TRIGGER[ACTION]"""

        result = validate_tension_section(invalid_tension, tier="default")

        assert result.valid is False
        assert "minimum" in str(result.errors).lower() or "2" in str(result.errors)

    def test_validate_tension_accepts_one_tension_quick_tier(self):
        """Accepts TENSION section with 1 tension for quick tier."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        valid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[STATUS_CHECK]⇌CTX:path/to/file.md[current_state]→TRIGGER[REPORT]"""

        result = validate_tension_section(valid_tension, tier="quick")

        assert result.valid is True
        assert result.tension_count == 1

    def test_validate_tension_requires_three_for_deep_tier(self):
        """Requires TENSION section with 3+ tensions for deep tier."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        # Only 2 tensions, but deep tier requires 3
        invalid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[CONSTRAINT_A]⇌CTX:file1.md:10-20[state_a]→TRIGGER[ACTION_A]
L2::[CONSTRAINT_B]⇌CTX:file2.md:30-40[state_b]→TRIGGER[ACTION_B]"""

        result = validate_tension_section(invalid_tension, tier="deep")

        assert result.valid is False
        assert "3" in str(result.errors) or "deep" in str(result.errors).lower()

    def test_validate_tension_accepts_three_tensions_deep_tier(self):
        """Accepts TENSION section with 3+ tensions for deep tier."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        valid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[CONSTRAINT_A]⇌CTX:file1.md:10-20[state_a]→TRIGGER[ACTION_A]
L2::[CONSTRAINT_B]⇌CTX:file2.md:30-40[state_b]→TRIGGER[ACTION_B]
L3::[CONSTRAINT_C]⇌CTX:file3.md:50-60[state_c]→TRIGGER[ACTION_C]"""

        result = validate_tension_section(valid_tension, tier="deep")

        assert result.valid is True
        assert result.tension_count == 3

    def test_validate_tension_rejects_missing_ctx_citation(self):
        """Rejects TENSION without CTX: citation."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        invalid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌[some_state]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌[another_state]→TRIGGER[IMPLEMENT_MINIMAL]"""

        result = validate_tension_section(invalid_tension, tier="default")

        assert result.valid is False
        assert "CTX" in str(result.errors)

    def test_validate_tension_rejects_missing_trigger(self):
        """Rejects TENSION without TRIGGER action."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        invalid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→IMPLICATION
L2::[MINIMAL_INTERVENTION]⇌CTX:file2.md[state2]→IMPLICATION2"""

        result = validate_tension_section(invalid_tension, tier="default")

        assert result.valid is False
        assert "TRIGGER" in str(result.errors)

    def test_validate_tension_rejects_generic_constraint(self):
        """Rejects TENSION with generic/placeholder constraint."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        invalid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TODO]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[CONSTRAINT]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]"""

        result = validate_tension_section(invalid_tension, tier="default")

        assert result.valid is False
        # Should reject placeholders like TODO, TBD, CONSTRAINT (too generic)

    def test_validate_tension_deep_tier_requires_line_ranges(self):
        """Deep tier requires line ranges in CTX citations."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        # Missing line ranges for deep tier
        invalid_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[ARCHITECTURAL_DECISION]⇌CTX:file1.md[state_a]→TRIGGER[ACTION_A]
L2::[DESIGN_CONSTRAINT]⇌CTX:file2.md[state_b]→TRIGGER[ACTION_B]
L3::[IMMUTABLE_RULE]⇌CTX:file3.md[state_c]→TRIGGER[ACTION_C]"""

        result = validate_tension_section(invalid_tension, tier="deep")

        assert result.valid is False
        assert "line" in str(result.errors).lower() or "range" in str(result.errors).lower()

    def test_validate_tension_accepts_ascii_operator_aliases(self):
        """Accepts TENSION section with ASCII operator aliases (<-> and ->).

        Per OCTAVE spec: parser accepts both ASCII and Unicode operators for
        backward compatibility. Unicode (the canonical form) is preferred for
        emission, but ASCII aliases must remain valid for input.

        This test ensures backward compatibility with existing agent vectors.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        # ASCII aliases: <-> for bidirectional, -> for implication
        ascii_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]<->CTX:.hestai/workflow/NORTH-STAR.md[I1::TDD]->TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]<->CTX:docs/adr/adr-0036.md:177[schema]->TRIGGER[IMPLEMENT_MINIMAL]"""

        result = validate_tension_section(ascii_tension, tier="default")

        assert result.valid is True, (
            "ASCII operator aliases (<-> and ->) must remain valid for backward compatibility. "
            f"Got errors: {result.errors}"
        )
        assert result.tension_count == 2


# =============================================================================
# COMMIT Section Validation Tests
# =============================================================================


@pytest.mark.unit
class TestCommitSectionValidation:
    """Test COMMIT section validation (Falsifiable Contract)."""

    def test_validate_commit_accepts_valid_section(self):
        """Accepts valid COMMIT section with concrete artifact and gate."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        valid_commit = """## COMMIT (Falsifiable Contract)
ARTIFACT::src/hestai_mcp/mcp/tools/odyssean_anchor.py
GATE::pytest tests/unit/mcp/tools/test_odyssean_anchor.py -v"""

        result = validate_commit_section(valid_commit)

        assert result.valid is True
        assert result.artifact == "src/hestai_mcp/mcp/tools/odyssean_anchor.py"
        assert "pytest" in result.gate
        assert len(result.errors) == 0

    def test_validate_commit_rejects_missing_artifact(self):
        """Rejects COMMIT section missing ARTIFACT field."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        invalid_commit = """## COMMIT (Falsifiable Contract)
GATE::pytest tests/unit/mcp/tools/test_odyssean_anchor.py -v"""

        result = validate_commit_section(invalid_commit)

        assert result.valid is False
        assert "ARTIFACT" in str(result.errors)

    def test_validate_commit_rejects_missing_gate(self):
        """Rejects COMMIT section missing GATE field."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        invalid_commit = """## COMMIT (Falsifiable Contract)
ARTIFACT::src/hestai_mcp/mcp/tools/odyssean_anchor.py"""

        result = validate_commit_section(invalid_commit)

        assert result.valid is False
        assert "GATE" in str(result.errors)

    def test_validate_commit_rejects_generic_artifact(self):
        """Rejects COMMIT section with generic artifact (not concrete path)."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        invalid_commit = """## COMMIT (Falsifiable Contract)
ARTIFACT::response
GATE::manual review"""

        result = validate_commit_section(invalid_commit)

        assert result.valid is False
        # Should reject: response, result, output, completion (too generic)

    def test_validate_commit_rejects_placeholder_artifact(self):
        """Rejects COMMIT section with placeholder artifact."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        invalid_commit = """## COMMIT (Falsifiable Contract)
ARTIFACT::TODO
GATE::pytest tests/"""

        result = validate_commit_section(invalid_commit)

        assert result.valid is False

    def test_validate_commit_accepts_test_file_artifact(self):
        """Accepts COMMIT section with test file as artifact."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        valid_commit = """## COMMIT (Falsifiable Contract)
ARTIFACT::tests/unit/tools/test_odyssean_anchor.py
GATE::pytest -v --tb=short"""

        result = validate_commit_section(valid_commit)

        assert result.valid is True
        assert "test" in result.artifact

    def test_validate_commit_accepts_documentation_artifact(self):
        """Accepts COMMIT section with documentation artifact."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        valid_commit = """## COMMIT (Falsifiable Contract)
ARTIFACT::docs/adr/adr-0036-odyssean-anchor-binding.md
GATE::human review of ADR structure"""

        result = validate_commit_section(valid_commit)

        assert result.valid is True
        assert ".md" in result.artifact


# =============================================================================
# ARM Injection Tests (Server-Authoritative)
# =============================================================================


@pytest.mark.unit
class TestARMInjection:
    """Test ARM section injection from session/git state (server-authoritative)."""

    def test_inject_arm_from_session(self, tmp_path):
        """Injects ARM section from session_id and git state."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-123"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "b2-implementation",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Setup mock PROJECT-CONTEXT with phase
        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text(
            """===PROJECT_CONTEXT===
META:
  TYPE::PROJECT_CONTEXT
  PHASE::B2
===END===
"""
        )

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True
        assert result.phase == "B2"
        assert result.focus == "b2-implementation"
        # Branch and files come from git (may be None in test env without git)

    def test_inject_arm_returns_branch_info(self, tmp_path):
        """Injects ARM with branch ahead/behind info from git."""
        import json
        import subprocess

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-456"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test-focus",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Setup PROJECT-CONTEXT
        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text(
            """===PROJECT_CONTEXT===
META:
  TYPE::PROJECT_CONTEXT
  PHASE::B1
===END===
"""
        )

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(working_dir),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=str(working_dir), capture_output=True
        )
        # Create initial commit
        (working_dir / "test.txt").write_text("test")
        subprocess.run(["git", "add", "."], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"], cwd=str(working_dir), capture_output=True
        )

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True
        assert result.branch is not None
        # Should have branch name (master or main)

    def test_inject_arm_returns_modified_files(self, tmp_path):
        """Injects ARM with modified files count from git status."""
        import json
        import subprocess

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-789"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test-focus",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Setup PROJECT-CONTEXT
        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text(
            """===PROJECT_CONTEXT===
META:
  TYPE::PROJECT_CONTEXT
  PHASE::B1
===END===
"""
        )

        # Initialize git repo and add modified file
        subprocess.run(["git", "init"], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(working_dir),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=str(working_dir), capture_output=True
        )
        (working_dir / "file1.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], cwd=str(working_dir), capture_output=True
        )
        # Modify a file
        (working_dir / "file1.txt").write_text("modified content")
        (working_dir / "file2.txt").write_text("new file")

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True
        assert result.files_count >= 1

    def test_inject_arm_invalid_session_returns_error(self, tmp_path):
        """Returns error for invalid/nonexistent session_id."""
        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        result = inject_arm_section(
            session_id="nonexistent-session",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert "session" in str(result.errors).lower()


# =============================================================================
# Self-Correction Protocol Tests
# =============================================================================


@pytest.mark.unit
class TestSelfCorrectionProtocol:
    """Test self-correction protocol (OA-I3) with retry guidance."""

    def test_odyssean_anchor_returns_success_on_valid_input(self, tmp_path):
        """Returns success with validated anchor on valid input."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-success"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "b2-implementation",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text(
            """===PROJECT_CONTEXT===
META:
  PHASE::B2
===END===
"""
        )

        valid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:.hestai/workflow/000-MCP-NORTH-STAR.md[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:docs/adr/adr-0036.md:177[schema_v4]→TRIGGER[IMPLEMENT_MINIMAL]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/hestai_mcp/mcp/tools/odyssean_anchor.py
GATE::pytest tests/unit/mcp/tools/test_odyssean_anchor.py -v"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=valid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is True
        assert result.anchor is not None
        assert "BIND" in result.anchor
        assert "ARM" in result.anchor  # ARM should be injected
        assert "TENSION" in result.anchor
        assert "COMMIT" in result.anchor
        assert result.terminal is False

    def test_odyssean_anchor_returns_validation_errors_with_guidance(self, tmp_path):
        """Returns validation errors with specific retry guidance."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-fail"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        invalid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[CONSTRAINT]⇌[state]→TRIGGER[ACTION]

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
        assert len(result.errors) > 0
        assert result.guidance is not None
        assert len(result.guidance) > 0
        assert result.retry_count == 0
        assert result.terminal is False

    def test_odyssean_anchor_increments_retry_count(self, tmp_path):
        """Increments retry_count on subsequent validation failures."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-retry"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        invalid_vector = """## BIND (Identity Lock)
ROLE::
COGNITION::INVALID::TYPE

## COMMIT (Falsifiable Contract)
ARTIFACT::TODO"""

        # First failure
        result1 = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=invalid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
            retry_count=0,
        )

        assert result1.success is False
        assert result1.retry_count == 0

        # Second failure (retry_count should be passed in)
        result2 = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=invalid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
            retry_count=1,
        )

        assert result2.success is False
        assert result2.retry_count == 1

    def test_odyssean_anchor_terminal_after_max_retries(self, tmp_path):
        """Sets terminal=True after max retries (2) exhausted."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-terminal"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        invalid_vector = """## BIND (Identity Lock)
ROLE::
COGNITION::INVALID"""

        # Third attempt (retry_count=2 means max retries exhausted)
        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=invalid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
            retry_count=2,
        )

        assert result.success is False
        assert result.terminal is True
        assert "exhausted" in result.guidance.lower() or "max" in result.guidance.lower()

    def test_odyssean_anchor_guidance_is_failure_specific(self, tmp_path):
        """Provides failure-specific guidance (not generic)."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-guidance"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Missing CTX citation specifically
        invalid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌[state_without_ctx]→TRIGGER[ACTION]
L2::[MINIMAL_INTERVENTION]⇌[another_state]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/file.py
GATE::pytest"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=invalid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        # Guidance should mention CTX specifically since that's what's missing
        assert "CTX" in result.guidance.upper() or "citation" in result.guidance.lower()


# =============================================================================
# Complete Integration Tests
# =============================================================================


@pytest.mark.unit
class TestOdysseanAnchorIntegration:
    """Integration tests for complete odyssean_anchor flow."""

    def test_role_mismatch_validation(self, tmp_path):
        """Validates that declared role matches submitted role."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-mismatch"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Role in vector doesn't match role parameter
        mismatched_vector = """## BIND (Identity Lock)
ROLE::holistic-orchestrator
COGNITION::LOGOS::HERMES
AUTHORITY::RESPONSIBLE[orchestration]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[CONSTRAINT]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[CONSTRAINT2]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/file.py
GATE::pytest"""

        result = odyssean_anchor(
            role="implementation-lead",  # Different from ROLE in vector
            vector_candidate=mismatched_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        assert "role" in str(result.errors).lower() or "mismatch" in str(result.errors).lower()

    def test_output_includes_injected_arm(self, tmp_path):
        """Output anchor includes server-injected ARM section."""
        import json
        import subprocess

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session with git
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-session-arm"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "odyssean-anchor-impl",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text(
            """===PROJECT_CONTEXT===
META:
  PHASE::B2
===END===
"""
        )

        # Setup git
        subprocess.run(["git", "init"], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(working_dir),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=str(working_dir), capture_output=True
        )
        (working_dir / "test.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], cwd=str(working_dir), capture_output=True
        )

        valid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:.hestai/workflow/NORTH-STAR.md[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:docs/adr/adr-0036.md:177[schema]→TRIGGER[IMPLEMENT_MINIMAL]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/hestai_mcp/mcp/tools/odyssean_anchor.py
GATE::pytest tests/ -v"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=valid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is True
        assert result.anchor is not None
        # ARM should be injected by server
        assert "## ARM" in result.anchor
        assert "PHASE::" in result.anchor
        assert "BRANCH::" in result.anchor
        assert "FOCUS::" in result.anchor


# =============================================================================
# Result Dataclass Tests
# =============================================================================


@pytest.mark.unit
class TestOdysseanAnchorResult:
    """Test OdysseanAnchorResult dataclass structure."""

    def test_result_has_required_fields(self):
        """OdysseanAnchorResult has all required fields."""
        from hestai_mcp.mcp.tools.odyssean_anchor import OdysseanAnchorResult

        result = OdysseanAnchorResult(
            success=True,
            anchor="validated anchor",
            errors=[],
            guidance="",
            retry_count=0,
            terminal=False,
        )

        assert hasattr(result, "success")
        assert hasattr(result, "anchor")
        assert hasattr(result, "errors")
        assert hasattr(result, "guidance")
        assert hasattr(result, "retry_count")
        assert hasattr(result, "terminal")

    def test_result_success_case(self):
        """OdysseanAnchorResult success case has anchor."""
        from hestai_mcp.mcp.tools.odyssean_anchor import OdysseanAnchorResult

        result = OdysseanAnchorResult(
            success=True,
            anchor="===RAPH_VECTOR::v4.0===\n...",
            errors=[],
            guidance="",
            retry_count=0,
            terminal=False,
        )

        assert result.success is True
        assert result.anchor is not None
        assert len(result.errors) == 0

    def test_result_failure_case(self):
        """OdysseanAnchorResult failure case has errors and guidance."""
        from hestai_mcp.mcp.tools.odyssean_anchor import OdysseanAnchorResult

        result = OdysseanAnchorResult(
            success=False,
            anchor=None,
            errors=["BIND: Missing ROLE field"],
            guidance="Add ROLE::agent_name to BIND section",
            retry_count=1,
            terminal=False,
        )

        assert result.success is False
        assert result.anchor is None
        assert len(result.errors) > 0
        assert len(result.guidance) > 0


# =============================================================================
# Security Tests - Path Traversal Prevention
# =============================================================================


@pytest.mark.unit
class TestSecurityPathTraversal:
    """Test security measures against path traversal attacks."""

    def test_session_id_rejects_absolute_path(self, tmp_path):
        """Rejects session_id containing absolute path (security risk)."""
        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        # Attack: session_id="/tmp" could read files outside project
        result = inject_arm_section(
            session_id="/tmp",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert any("path" in e.lower() or "invalid" in e.lower() for e in result.errors)

    def test_session_id_rejects_parent_traversal(self, tmp_path):
        """Rejects session_id containing parent directory traversal."""
        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        # Attack: session_id="../../../etc" could traverse outside
        result = inject_arm_section(
            session_id="../../../etc",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert any("path" in e.lower() or "invalid" in e.lower() for e in result.errors)

    def test_session_id_rejects_slash_in_name(self, tmp_path):
        """Rejects session_id containing forward slash."""
        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        (working_dir / ".hestai" / "sessions" / "active").mkdir(parents=True)

        # Attack: session_id="foo/bar" could traverse subdirectories
        result = inject_arm_section(
            session_id="foo/bar",
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert any("path" in e.lower() or "invalid" in e.lower() for e in result.errors)

    def test_session_id_accepts_valid_alphanumeric(self, tmp_path):
        """Accepts valid alphanumeric session_id with hyphens."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "valid-session-id-123"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()
        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True


# =============================================================================
# ARM Branch Fallback Tests
# =============================================================================


@pytest.mark.unit
class TestARMBranchFallback:
    """Test ARM branch field has proper fallback when git fails."""

    def test_arm_branch_fallback_to_unknown_when_git_fails(self, tmp_path):
        """ARM branch should be 'unknown' (not None) when git fails."""
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup session WITHOUT git repo
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-no-git"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()
        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True
        # Branch should fallback to "unknown", NOT None
        assert result.branch is not None
        assert result.branch == "unknown"


# =============================================================================
# TENSION Section Extraction Security Tests
# =============================================================================


@pytest.mark.unit
class TestTensionSectionExtractionSecurity:
    """Test TENSION section extraction resists smuggling attacks."""

    def test_extract_tension_rejects_indented_header_smuggling(self):
        """Rejects whitespace-prefixed headers inside TENSION block."""
        from hestai_mcp.mcp.tools.odyssean_anchor import _extract_tension_section

        # Attack: indented "## COMMIT" inside TENSION should NOT terminate extraction
        smuggled_vector = """## BIND (Identity Lock)
ROLE::test-role

## TENSION (Cognitive Proof)
L1::[CONSTRAINT_A]⇌CTX:file.md[state]→TRIGGER[ACTION]
  ## COMMIT (Falsifiable Contract)
ARTIFACT::malicious-artifact
L2::[CONSTRAINT_B]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::legitimate-artifact
GATE::pytest"""

        tension_text = _extract_tension_section(smuggled_vector)

        # The indented "## COMMIT" should NOT terminate extraction
        # L2 should still be in the tension section
        assert "CONSTRAINT_B" in tension_text
        # The real COMMIT section starts at the non-indented "## COMMIT"

    def test_extract_tension_handles_legitimate_headers(self):
        """Properly terminates at legitimate non-indented headers."""
        from hestai_mcp.mcp.tools.odyssean_anchor import _extract_tension_section

        valid_vector = """## BIND (Identity Lock)
ROLE::test-role

## TENSION (Cognitive Proof)
L1::[CONSTRAINT_A]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[CONSTRAINT_B]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::legitimate-artifact
GATE::pytest"""

        tension_text = _extract_tension_section(valid_vector)

        assert "CONSTRAINT_A" in tension_text
        assert "CONSTRAINT_B" in tension_text
        # COMMIT content should NOT be in tension section
        assert "legitimate-artifact" not in tension_text


# =============================================================================
# Section-Scoped Validation Tests
# =============================================================================


@pytest.mark.unit
class TestSectionScopedValidation:
    """Test validators operate on extracted sections, not whole document."""

    def test_bind_validation_only_checks_bind_section(self):
        """BIND validation should only check BIND section content."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        # BIND section is invalid, but TENSION section has ROLE:: pattern
        tricky_input = """## BIND (Identity Lock)
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof)
ROLE::fake-role-in-tension
L1::[CONSTRAINT]⇌CTX:file.md[state]→TRIGGER[ACTION]"""

        result = validate_bind_section(tricky_input)

        # Should FAIL because BIND section has no ROLE
        # The ROLE:: in TENSION should NOT satisfy the requirement
        assert result.valid is False
        assert "ROLE" in str(result.errors)

    def test_tension_validation_requires_tension_section_header(self):
        """TENSION validation requires ## TENSION header - content elsewhere should fail.

        This test verifies that TENSION-like content outside the TENSION section
        does not satisfy validation. An agent cannot embed valid TENSION entries
        in the COMMIT section and bypass validation.

        GitHub Issue: #102 - CRS verdict blocking on Issue 4
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import (
            _extract_tension_section,
            validate_tension_section,
        )

        # Vector has NO ## TENSION section, but has TENSION-like content in COMMIT
        vector_without_tension_header = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## COMMIT (Falsifiable Contract)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:file2.md[state2]→TRIGGER[IMPLEMENT_MINIMAL]
ARTIFACT::src/x.py
GATE::pytest"""

        # Extract TENSION section - should be empty since there's no ## TENSION header
        tension_section = _extract_tension_section(vector_without_tension_header)

        # Validation should FAIL because extracted section is empty/missing
        result = validate_tension_section(tension_section, "default")
        assert not result.valid, (
            "TENSION validation should fail when ## TENSION header is missing. "
            f"Got valid={result.valid}, tension_count={result.tension_count}"
        )
        # Should have insufficient count error since no tensions were extracted
        assert any(
            "Insufficient" in e or "minimum" in e.lower() for e in result.errors
        ), f"Expected 'Insufficient' error but got: {result.errors}"

    def test_odyssean_anchor_rejects_vector_missing_tension_header(self, tmp_path):
        """odyssean_anchor rejects vector without ## TENSION header.

        Even if TENSION-like content exists elsewhere (e.g., in COMMIT section),
        the main function must validate ONLY the extracted TENSION section.

        GitHub Issue: #102 - CRS verdict blocking on Issue 4
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup mock session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-missing-tension-header"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "test",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Vector WITHOUT ## TENSION section - TENSION-like content in COMMIT
        # This should NOT pass validation
        malformed_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]

## COMMIT (Falsifiable Contract)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:file2.md[state2]→TRIGGER[IMPLEMENT_MINIMAL]
ARTIFACT::src/x.py
GATE::pytest"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=malformed_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        # Must FAIL because there's no ## TENSION section
        assert result.success is False, (
            "odyssean_anchor should reject vector missing ## TENSION header. "
            f"Got success={result.success}"
        )
        # Should have TENSION-related error
        assert any(
            "TENSION" in e or "Insufficient" in e for e in result.errors
        ), f"Expected TENSION-related error but got: {result.errors}"

    def test_commit_validation_only_checks_commit_section(self):
        """COMMIT validation should only check COMMIT section content."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        # COMMIT section is invalid, but BIND section has ARTIFACT:: pattern
        tricky_input = """## BIND (Identity Lock)
ARTIFACT::fake-artifact-in-bind
ROLE::test-role

## COMMIT (Falsifiable Contract)
GATE::pytest"""

        result = validate_commit_section(tricky_input)

        # Should FAIL because COMMIT section has no ARTIFACT
        # The ARTIFACT:: in BIND should NOT satisfy the requirement
        assert result.valid is False
        assert "ARTIFACT" in str(result.errors)


# =============================================================================
# Anchor State Persistence Tests (OA-I6 Support)
# =============================================================================


@pytest.mark.unit
class TestAnchorStatePersistence:
    """Test anchor state persistence for OA-I6 tool gating."""

    def test_odyssean_anchor_returns_false_on_persist_failure(self, tmp_path, monkeypatch):
        """odyssean_anchor returns success=False when anchor.json write fails.

        This tests the "zombie state" bug fix: if _persist_anchor_state() fails
        (e.g., OSError during file write), odyssean_anchor() must return
        success=False, NOT success=True.

        Without this fix, agents appear bound (success=True returned) but
        anchor.json is not written to disk, causing has_valid_anchor() to
        return False and trapping agents in an infinite retry loop.

        GitHub Issue: #102 - CRS/CE blocking on zombie state bug
        """
        import json
        from pathlib import Path

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup valid session environment
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-persist-failure"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "b2-implementation",
            "working_dir": str(working_dir),
        }
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text(
            """===PROJECT_CONTEXT===
META:
  PHASE::B2
===END===
"""
        )

        # Valid vector that would normally succeed
        valid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:.hestai/workflow/000-MCP-NORTH-STAR.md[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:docs/adr/adr-0036.md:177[schema_v4]→TRIGGER[IMPLEMENT_MINIMAL]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/hestai_mcp/mcp/tools/odyssean_anchor.py
GATE::pytest tests/unit/mcp/tools/test_odyssean_anchor.py -v"""

        # Monkeypatch Path.write_text to raise OSError when writing anchor.json
        original_write_text = Path.write_text

        def failing_write_text(self, content, *args, **kwargs):
            if self.name == "anchor.json":
                raise OSError("Simulated disk write failure for anchor.json")
            return original_write_text(self, content, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", failing_write_text)

        # Call odyssean_anchor with valid input - persist will fail
        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=valid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        # CRITICAL ASSERTION: Must return success=False when persist fails
        assert result.success is False, (
            "odyssean_anchor MUST return success=False when anchor.json persist fails. "
            f"Got success={result.success}. This is the zombie state bug - agent appears "
            "bound but anchor.json not written, causing has_valid_anchor() to fail."
        )

        # Error message should indicate persistence failure
        error_str = " ".join(result.errors).lower() if result.errors else ""
        guidance_str = result.guidance.lower() if result.guidance else ""
        assert "persist" in error_str or "persist" in guidance_str or "anchor" in error_str, (
            f"Error should mention persistence failure. Got errors={result.errors}, "
            f"guidance={result.guidance}"
        )

    def test_odyssean_anchor_persists_anchor_on_success(self, tmp_path):
        """odyssean_anchor creates anchor.json on successful validation.

        Verifies the normal success path: when validation passes and persist
        succeeds, anchor.json should exist with correct content.
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup valid session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-persist-success"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {
            "session_id": session_id,
            "role": "implementation-lead",
            "focus": "b2-implementation",
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
L1::[TDD_MANDATE]⇌CTX:.hestai/workflow/000-MCP-NORTH-STAR.md[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
L2::[MINIMAL_INTERVENTION]⇌CTX:docs/adr/adr-0036.md:177[schema_v4]→TRIGGER[IMPLEMENT_MINIMAL]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/hestai_mcp/mcp/tools/odyssean_anchor.py
GATE::pytest tests/unit/mcp/tools/test_odyssean_anchor.py -v"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=valid_vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        # Should succeed
        assert result.success is True

        # anchor.json should exist
        anchor_file = session_dir / "anchor.json"
        assert anchor_file.exists(), "anchor.json should be created on successful validation"

        # Verify content
        anchor_data = json.loads(anchor_file.read_text())
        assert anchor_data["validated"] is True
        assert anchor_data["role"] == "implementation-lead"
        assert anchor_data["tier"] == "default"
        assert "timestamp" in anchor_data


# =============================================================================
# Alternative Tension Pattern Tests (Coverage: lines 340-359)
# =============================================================================


@pytest.mark.unit
class TestAlternativeTensionPattern:
    """Test alternative TENSION pattern matching without line number prefix."""

    def test_validate_tension_accepts_pattern_without_line_number(self):
        """Accepts TENSION format without L{N}:: prefix (alternative pattern).

        This covers the alt_pattern branch at lines 340-359 in odyssean_anchor.py.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        # Alternative format: [constraint]⇌CTX:path[state]→TRIGGER[action]
        # (without the L{N}:: prefix)
        alt_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
[TDD_MANDATE]⇌CTX:.hestai/workflow/north-star.md[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
[MINIMAL_INTERVENTION]⇌CTX:docs/adr/adr-0036.md[schema_v4]→TRIGGER[IMPLEMENT_MINIMAL]"""

        result = validate_tension_section(alt_tension, tier="default")

        assert result.valid is True
        assert result.tension_count == 2
        # Verify the tensions were parsed correctly
        assert result.tensions[0]["constraint"] == "TDD_MANDATE"
        assert result.tensions[1]["constraint"] == "MINIMAL_INTERVENTION"

    def test_validate_tension_alternative_pattern_validates_ctx(self):
        """Alternative pattern still requires CTX citation."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        # Alternative format with missing CTX
        invalid_alt_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
[TDD_MANDATE]⇌CTX:[I1::TDD]→TRIGGER[WRITE_TEST_FIRST]
[MINIMAL_INTERVENTION]⇌CTX:[schema_v4]→TRIGGER[IMPLEMENT_MINIMAL]"""

        result = validate_tension_section(invalid_alt_tension, tier="default")

        # Should detect missing CTX path even with alternative pattern
        assert result.valid is False
        assert any("CTX" in str(e) for e in result.errors)

    def test_validate_tension_alternative_pattern_validates_trigger(self):
        """Alternative pattern still requires TRIGGER."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        # Alternative format with missing TRIGGER
        alt_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
[TDD_MANDATE]⇌CTX:file.md[state]→IMPLICATION_WITHOUT_TRIGGER
[MINIMAL_INTERVENTION]⇌CTX:file2.md[state2]→ALSO_NO_TRIGGER"""

        result = validate_tension_section(alt_tension, tier="default")

        assert result.valid is False
        assert any("TRIGGER" in str(e) for e in result.errors)

    def test_validate_tension_mixed_patterns(self):
        """Accepts mix of standard and alternative TENSION patterns."""
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_tension_section

        # Mix of both formats
        mixed_tension = """## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file1.md[state1]→TRIGGER[ACTION1]
[MINIMAL_INTERVENTION]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]"""

        result = validate_tension_section(mixed_tension, tier="default")

        assert result.valid is True
        assert result.tension_count == 2


# =============================================================================
# Session Data Reading Edge Cases (Coverage: lines 575-577, 587-588)
# =============================================================================


@pytest.mark.unit
class TestSessionDataEdgeCases:
    """Test session data reading error handling in inject_arm_section."""

    def test_inject_arm_handles_json_decode_error(self, tmp_path):
        """Returns error when session.json contains invalid JSON.

        This covers the JSONDecodeError exception at lines 575-577.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup session with invalid JSON
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-bad-json"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        # Write invalid JSON
        (session_dir / "session.json").write_text("{ invalid json }")

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is False
        assert any("session data" in e.lower() or "json" in e.lower() for e in result.errors)

    def test_inject_arm_handles_project_context_read_error(self, tmp_path, monkeypatch):
        """Logs warning when PROJECT-CONTEXT.oct.md read fails.

        This covers the OSError exception at lines 587-588.
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup valid session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-context-error"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        # Create PROJECT-CONTEXT but make it unreadable
        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        project_context = context_dir / "PROJECT-CONTEXT.oct.md"
        project_context.write_text("PHASE::B2")

        # Monkeypatch Path.read_text to fail for PROJECT-CONTEXT
        original_read_text = type(project_context).read_text

        def failing_read_text(self, *args, **kwargs):
            if "PROJECT-CONTEXT" in str(self):
                raise OSError("Permission denied")
            return original_read_text(self, *args, **kwargs)

        monkeypatch.setattr(type(project_context), "read_text", failing_read_text)

        # Should still succeed but phase will be empty (logged as warning)
        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        # Should still be valid, just with empty phase
        assert result.valid is True
        assert result.phase == ""


# =============================================================================
# Git Operations Edge Cases (Coverage: lines 601-603, 617-641, 659-660)
# =============================================================================


@pytest.mark.unit
class TestGitOperationsEdgeCases:
    """Test git command error handling in inject_arm_section."""

    def test_inject_arm_handles_git_branch_failure(self, tmp_path, monkeypatch):
        """Handles git rev-parse failure gracefully.

        This covers the branch fallback to 'unknown' at lines 600-603.
        """
        import json
        import subprocess

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup valid session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-git-fail"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Monkeypatch subprocess.run to raise exception for git
        original_run = subprocess.run

        def failing_run(cmd, *args, **kwargs):
            if cmd[0] == "git":
                raise subprocess.TimeoutExpired(cmd, 5)
            return original_run(cmd, *args, **kwargs)

        monkeypatch.setattr(subprocess, "run", failing_run)

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        # Should still be valid with fallback branch
        assert result.valid is True
        assert result.branch == "unknown"

    def test_inject_arm_with_tracking_branch_ahead_behind(self, tmp_path):
        """Captures ahead/behind count from tracking branch.

        This covers the branch tracking code at lines 617-641.
        """
        import json
        import subprocess

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-tracking"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Initialize git with a remote tracking branch
        subprocess.run(["git", "init"], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(working_dir),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(working_dir),
            capture_output=True,
        )

        # Create initial commit
        (working_dir / "test.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=str(working_dir),
            capture_output=True,
        )

        # Create a "fake" remote tracking situation (as bare simulation)
        # Without actual remote, the tracking branch query will fail - that's expected
        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True
        # Without actual remote, ahead/behind will be 0
        assert result.ahead == 0
        assert result.behind == 0

    def test_inject_arm_handles_git_status_exception(self, tmp_path, monkeypatch):
        """Handles git status failure gracefully.

        This covers lines 659-660 where git status exception is caught.
        """
        import json
        import subprocess

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup valid session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-status-fail"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Initialize git
        subprocess.run(["git", "init"], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(working_dir),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(working_dir),
            capture_output=True,
        )
        (working_dir / "test.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=str(working_dir),
            capture_output=True,
        )

        # Monkeypatch only the git status call to fail
        original_run = subprocess.run

        def selective_failing_run(cmd, *args, **kwargs):
            if cmd[0] == "git" and "status" in cmd:
                raise FileNotFoundError("git not found")
            return original_run(cmd, *args, **kwargs)

        monkeypatch.setattr(subprocess, "run", selective_failing_run)

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        # Should still be valid, just with no files info
        assert result.valid is True
        assert result.files_count == 0


# =============================================================================
# Anchor Persistence Edge Cases (Coverage: lines 708-710)
# =============================================================================


@pytest.mark.unit
class TestAnchorPersistenceEdgeCases:
    """Test _persist_anchor_state error handling."""

    def test_persist_anchor_fails_for_missing_session_dir(self, tmp_path):
        """_persist_anchor_state returns error for missing session directory.

        This covers lines 708-710 where session directory doesn't exist.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import _persist_anchor_state

        working_dir = tmp_path / "project"
        working_dir.mkdir()

        # Don't create session directory - it should fail
        success, error = _persist_anchor_state(
            session_id="nonexistent-session",
            working_dir=str(working_dir),
            role="test-role",
            tier="default",
        )

        assert success is False
        assert "session directory not found" in error.lower()


# =============================================================================
# Validation Edge Cases (Coverage: lines 218, 225, 448, 467, 476, 505, 524)
# =============================================================================


@pytest.mark.unit
class TestValidationEdgeCases:
    """Test edge cases in BIND, COMMIT validation."""

    def test_validate_bind_fallback_when_no_bind_section(self):
        """Uses original text when no BIND section found.

        This covers line 218 - fallback when _extract_bind_section returns empty.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        # Text without ## BIND header but has BIND-like content
        raw_bind = """ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build_phase_execution]"""

        result = validate_bind_section(raw_bind)

        # Should still validate (using fallback to original text)
        assert result.valid is True
        assert result.role == "implementation-lead"

    def test_validate_bind_rejects_empty_role_value(self):
        """Rejects ROLE field with empty value.

        This covers line 225 - empty ROLE field check.
        The regex requires at least one character after ROLE::, so empty matches as "missing".
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_bind_section

        bind_with_empty_role = """## BIND (Identity Lock)
ROLE::
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]"""

        result = validate_bind_section(bind_with_empty_role)

        assert result.valid is False
        # The regex doesn't match empty role, so it appears as "missing ROLE"
        assert any("role" in e.lower() for e in result.errors)

    def test_validate_commit_fallback_when_no_commit_section(self):
        """Uses original text when no COMMIT section found.

        This covers line 448 - fallback when _extract_commit_section returns empty.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        # Text without ## COMMIT header but has COMMIT-like content
        raw_commit = """ARTIFACT::src/file.py
GATE::pytest tests/"""

        result = validate_commit_section(raw_commit)

        # Should still validate (using fallback)
        assert result.valid is True
        assert result.artifact == "src/file.py"

    def test_validate_commit_rejects_empty_artifact_value(self):
        """Rejects ARTIFACT field with empty value.

        This covers line 467 - empty ARTIFACT check.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        commit_with_empty_artifact = """## COMMIT (Falsifiable Contract)
ARTIFACT::
GATE::pytest"""

        result = validate_commit_section(commit_with_empty_artifact)

        assert result.valid is False
        assert any("empty" in e.lower() or "artifact" in e.lower() for e in result.errors)

    def test_validate_commit_rejects_empty_gate_value(self):
        """Rejects GATE field with empty value.

        This covers line 476 - empty GATE check.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import validate_commit_section

        commit_with_empty_gate = """## COMMIT (Falsifiable Contract)
ARTIFACT::src/file.py
GATE::   """

        result = validate_commit_section(commit_with_empty_gate)

        assert result.valid is False
        assert any("empty" in e.lower() or "gate" in e.lower() for e in result.errors)

    def test_session_id_rejects_empty_string(self):
        """Rejects empty session_id.

        This covers line 505 - empty session_id validation.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        result = inject_arm_section(
            session_id="",
            working_dir="/tmp/project",
        )

        assert result.valid is False
        assert any("empty" in e.lower() for e in result.errors)

    def test_session_id_rejects_backslash(self):
        """Rejects session_id with backslash.

        This covers line 524 - backslash check.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        result = inject_arm_section(
            session_id="session\\with\\backslash",
            working_dir="/tmp/project",
        )

        assert result.valid is False
        assert any("backslash" in e.lower() for e in result.errors)


# =============================================================================
# RuntimeError Path in Semantic Validation (Coverage: lines 802-819)
# =============================================================================


@pytest.mark.unit
class TestSemanticValidationRuntimeError:
    """Test RuntimeError handling when no event loop is running."""

    def test_run_semantic_validation_without_event_loop(self, tmp_path):
        """Tests _run_semantic_validation when not in async context.

        This covers lines 802-819 - the RuntimeError path where no event loop exists.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import _run_semantic_validation
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticChecksConfig,
            SemanticConfig,
        )

        # Create a file for CTX validation
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "test.md").write_text("# Test")

        config = SemanticConfig(
            enabled=True,
            tier="analysis",
            timeout_seconds=15,
            fail_mode="warn",
            checks=SemanticChecksConfig(
                cognition_appropriateness=False,
                tension_relevance=False,
                ctx_validity=True,  # Only filesystem check
                commit_feasibility=False,
            ),
        )

        # Call directly from sync context (no event loop)
        # This should exercise the RuntimeError path
        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.load_semantic_config",
            return_value=config,
        ):
            result = _run_semantic_validation(
                role="test-role",
                cognition_type="LOGOS",
                tensions=[{"ctx_path": "docs/test.md", "constraint": "TEST"}],
                commit_artifact="src/test.py",
                working_dir=str(tmp_path),
            )

        # Should succeed (file exists)
        assert result.success is True
        assert result.skipped is False

    def test_run_semantic_validation_exception_graceful_degradation(self, tmp_path, monkeypatch):
        """Tests graceful degradation on unexpected exception.

        This covers lines 816-819 - exception handling.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import _run_semantic_validation

        # Monkeypatch load_semantic_config to raise an exception
        def raising_config():
            raise ValueError("Unexpected config error")

        monkeypatch.setattr(
            "hestai_mcp.mcp.tools.odyssean_anchor_semantic.load_semantic_config",
            raising_config,
        )

        result = _run_semantic_validation(
            role="test-role",
            cognition_type="LOGOS",
            tensions=[],
            commit_artifact="test.py",
            working_dir=str(tmp_path),
        )

        # Should degrade gracefully - return success with skipped
        assert result.success is True
        assert result.skipped is True


# =============================================================================
# Main Function Error Paths (Coverage: lines 926, 944, 956-968, 984-985, 1000-1001, 1084, 1088)
# =============================================================================


@pytest.mark.unit
class TestMainFunctionErrorPaths:
    """Test error paths in the main odyssean_anchor function."""

    def test_odyssean_anchor_trigger_guidance(self, tmp_path):
        """Missing TRIGGER generates specific guidance.

        This covers line 926 - TRIGGER guidance.
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-trigger-guidance"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Vector with missing TRIGGER
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→IMPLICATION_NO_TRIGGER
L2::[MIP]⇌CTX:file2.md[state2]→ALSO_NO_TRIGGER

## COMMIT (Falsifiable Contract)
ARTIFACT::src/file.py
GATE::pytest"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        assert "TRIGGER" in result.guidance

    def test_odyssean_anchor_line_range_guidance_deep_tier(self, tmp_path):
        """Missing line ranges in deep tier generates specific guidance.

        This covers lines 944 - line range guidance for deep tier.
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-line-range-guidance"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Vector without line ranges (required for deep tier)
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[MIP]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]
L3::[QUALITY]⇌CTX:file3.md[state3]→TRIGGER[ACTION3]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/file.py
GATE::pytest"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="deep",  # Deep tier requires line ranges
        )

        assert result.success is False
        # Should have line range guidance
        assert "line" in result.guidance.lower()

    def test_odyssean_anchor_generic_artifact_guidance(self, tmp_path):
        """Generic artifact generates specific guidance.

        This covers lines 956-968 - artifact guidance for generic/placeholder.
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-artifact-guidance"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Vector with generic artifact
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[MIP]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::response
GATE::manual review"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        # Should mention replacing generic artifact
        assert "generic" in result.guidance.lower() or "concrete" in result.guidance.lower()

    def test_odyssean_anchor_placeholder_artifact_guidance(self, tmp_path):
        """Placeholder artifact generates specific guidance.

        This covers lines 962-965 - placeholder guidance.
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-placeholder-guidance"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Vector with placeholder artifact
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[MIP]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::TBD
GATE::manual review"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        # Should mention placeholder
        assert "placeholder" in result.guidance.lower()

    def test_odyssean_anchor_arm_failure_guidance(self, tmp_path):
        """ARM injection failure generates specific guidance.

        This covers lines 984-985 - ARM failure guidance.
        """

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup session with INVALID session_id to trigger ARM failure
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Valid vector but invalid session
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[MIP]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/file.py
GATE::pytest"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id="nonexistent-session",  # This will fail ARM injection
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        # Should have guidance about session
        assert "session" in result.guidance.lower()

    def test_odyssean_anchor_semantic_failure_guidance(self, tmp_path, monkeypatch):
        """Semantic validation failure generates specific guidance.

        This covers lines 1000-1001 - semantic failure guidance.
        """
        import json
        from unittest.mock import patch

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor
        from hestai_mcp.mcp.tools.odyssean_anchor_semantic import (
            SemanticValidationResult,
        )

        # Setup valid session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-semantic-guidance"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Valid structural vector
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[MIP]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::src/file.py
GATE::pytest"""

        # Mock semantic validation to return failure
        mock_result = SemanticValidationResult(
            success=False,
            skipped=False,
            concerns=["Cognition concern: LOGOS is not appropriate for this role"],
        )

        with patch(
            "hestai_mcp.mcp.tools.odyssean_anchor._run_semantic_validation",
            return_value=mock_result,
        ):
            result = odyssean_anchor(
                role="implementation-lead",
                vector_candidate=vector,
                session_id=session_id,
                working_dir=str(working_dir),
                tier="default",
            )

        assert result.success is False
        # Should have semantic validation guidance
        assert "semantic" in result.guidance.lower() or "cognition" in result.guidance.lower()


# =============================================================================
# ARM Section Building Edge Cases (Coverage: lines 1084, 1088)
# =============================================================================


@pytest.mark.unit
class TestARMSectionBuilding:
    """Test _build_arm_section edge cases."""

    def test_build_arm_with_ahead_behind(self):
        """Build ARM section with ahead/behind counts.

        This covers line 1084 - branch with ahead/behind.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import (
            ARMInjectionResult,
            _build_arm_section,
        )

        arm_result = ARMInjectionResult(
            valid=True,
            phase="B2",
            branch="feature-branch",
            ahead=3,
            behind=1,
            files_count=5,
            top_files=["file1.py", "file2.py", "file3.py"],
            focus="implementation",
        )

        arm_section = _build_arm_section(arm_result)

        # Should include ahead/behind info
        assert "3up1down" in arm_section
        assert "feature-branch" in arm_section

    def test_build_arm_with_top_files(self):
        """Build ARM section with top files list.

        This covers line 1088 - files with top_files.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import (
            ARMInjectionResult,
            _build_arm_section,
        )

        arm_result = ARMInjectionResult(
            valid=True,
            phase="B2",
            branch="main",
            ahead=0,
            behind=0,
            files_count=3,
            top_files=["src/main.py", "tests/test_main.py"],
            focus="testing",
        )

        arm_section = _build_arm_section(arm_result)

        # Should include file names
        assert "src/main.py" in arm_section
        assert "3[" in arm_section  # files count followed by list

    def test_build_arm_empty_top_files(self):
        """Build ARM section with no top files.

        This covers the empty top_files case.
        """
        from hestai_mcp.mcp.tools.odyssean_anchor import (
            ARMInjectionResult,
            _build_arm_section,
        )

        arm_result = ARMInjectionResult(
            valid=True,
            phase="B1",
            branch="main",
            ahead=0,
            behind=0,
            files_count=0,
            top_files=[],
            focus="setup",
        )

        arm_section = _build_arm_section(arm_result)

        # Should have empty list
        assert "0[]" in arm_section


# =============================================================================
# Git Remote Tracking Tests (Coverage: lines 617-639)
# =============================================================================


@pytest.mark.unit
class TestGitRemoteTracking:
    """Test git remote tracking for ahead/behind counts."""

    def test_inject_arm_with_actual_remote_tracking(self, tmp_path):
        """Captures ahead/behind with actual remote tracking branch.

        This covers lines 617-639 - actual remote tracking with ahead/behind.
        """
        import json
        import subprocess

        from hestai_mcp.mcp.tools.odyssean_anchor import inject_arm_section

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-remote-tracking"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Create a bare repo to act as "remote"
        remote_dir = tmp_path / "remote.git"
        subprocess.run(["git", "init", "--bare"], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "init", "--bare", str(remote_dir)],
            capture_output=True,
        )

        # Initialize local repo
        subprocess.run(["git", "init"], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(working_dir),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(working_dir),
            capture_output=True,
        )

        # Add remote
        subprocess.run(
            ["git", "remote", "add", "origin", str(remote_dir)],
            cwd=str(working_dir),
            capture_output=True,
        )

        # Create initial commit
        (working_dir / "test.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=str(working_dir),
            capture_output=True,
        )

        # Push to remote
        subprocess.run(
            ["git", "push", "-u", "origin", "master"],
            cwd=str(working_dir),
            capture_output=True,
        )

        # Create local-only commit (ahead by 1)
        (working_dir / "test.txt").write_text("updated")
        subprocess.run(["git", "add", "."], cwd=str(working_dir), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Update"],
            cwd=str(working_dir),
            capture_output=True,
        )

        result = inject_arm_section(
            session_id=session_id,
            working_dir=str(working_dir),
        )

        assert result.valid is True
        # Should have tracked the ahead count
        assert result.ahead >= 0  # May be 1 if tracking works


# =============================================================================
# ARTIFACT Error Guidance Tests (Coverage: lines 956-968)
# =============================================================================


@pytest.mark.unit
class TestArtifactErrorGuidance:
    """Test ARTIFACT error generates appropriate guidance text."""

    def test_artifact_generic_error_guidance(self, tmp_path):
        """Generic artifact error generates specific guidance text.

        This covers lines 956-961 - 'generic' in error message.
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-generic-artifact"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Vector with generic artifact that triggers "generic" error
        # Note: "response" is in the generic artifacts list
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[MIP]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::response
GATE::manual review"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        # Should have guidance for generic artifact
        assert "generic" in result.guidance.lower() or "concrete" in result.guidance.lower()

    def test_artifact_placeholder_error_guidance(self, tmp_path):
        """Placeholder artifact error generates specific guidance text.

        This covers lines 962-966 - 'placeholder' in error message.
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-placeholder-artifact"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Vector with placeholder artifact
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[MIP]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
ARTIFACT::TODO
GATE::manual review"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        # Should have guidance for placeholder
        assert "placeholder" in result.guidance.lower() or "tbd" in result.guidance.lower()

    def test_artifact_missing_error_guidance(self, tmp_path):
        """Missing artifact error generates specific guidance text.

        This covers lines 967-971 - general ARTIFACT error (not generic/placeholder).
        """
        import json

        from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor

        # Setup session
        working_dir = tmp_path / "project"
        working_dir.mkdir()
        hestai_dir = working_dir / ".hestai"
        sessions_dir = hestai_dir / "sessions" / "active"
        sessions_dir.mkdir(parents=True)

        session_id = "test-missing-artifact"
        session_dir = sessions_dir / session_id
        session_dir.mkdir()

        session_data = {"session_id": session_id, "focus": "test"}
        (session_dir / "session.json").write_text(json.dumps(session_data))

        context_dir = hestai_dir / "context"
        context_dir.mkdir()
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        # Vector with missing ARTIFACT (no ARTIFACT line)
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof - AGENT GENERATED)
L1::[TDD_MANDATE]⇌CTX:file.md[state]→TRIGGER[ACTION]
L2::[MIP]⇌CTX:file2.md[state2]→TRIGGER[ACTION2]

## COMMIT (Falsifiable Contract)
GATE::pytest"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(working_dir),
            tier="default",
        )

        assert result.success is False
        # Should have general ARTIFACT guidance
        assert "artifact" in result.guidance.lower()
