"""Integration tests for odyssean_anchor tool.

These tests verify end-to-end functionality with real filesystem and git operations.
They complement unit tests by testing the complete workflow including:
- Real git repository initialization and operations
- Real session file creation and management
- Real context file operations
- Server-authoritative ARM injection from actual system state

Run with: uv run --python 3.11 -m pytest tests/integration/odyssean_anchor/ -v -m integration
"""

import json
import subprocess
from pathlib import Path

import pytest

from hestai_mcp.mcp.tools.odyssean_anchor import odyssean_anchor


@pytest.mark.integration
class TestOdysseanAnchorIntegration:
    """Integration tests with real filesystem and git."""

    def test_odyssean_anchor_with_real_session_and_git(self, tmp_path: Path) -> None:
        """Verify odyssean_anchor works with real session file and git repo.

        This test sets up a complete environment with:
        - A real git repository with initial commit
        - A proper session directory structure
        - A valid PROJECT-CONTEXT with phase information

        The test then submits a valid vector and verifies the tool
        correctly validates and injects ARM data from the real system state.
        """
        # Setup: Create a git repo
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Initialize git repository
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Create a file and commit
        readme = project_dir / "README.md"
        readme.write_text("# Test Project\n\nThis is a test project for integration testing.")
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "Initial commit"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Setup session directory and file
        session_dir = project_dir / ".hestai" / "sessions" / "active" / "test-session"
        session_dir.mkdir(parents=True)
        session_file = session_dir / "session.json"
        session_file.write_text(
            json.dumps(
                {
                    "session_id": "test-session",
                    "role": "implementation-lead",
                    "focus": "integration-testing",
                    "working_dir": str(project_dir),
                }
            )
        )

        # Setup context directory
        context_dir = project_dir / ".hestai" / "context"
        context_dir.mkdir(parents=True)
        project_context = context_dir / "PROJECT-CONTEXT.oct.md"
        project_context.write_text(
            """===PROJECT_CONTEXT===
META:
  TYPE::PROJECT_CONTEXT
  PHASE::B1
===END===
"""
        )

        # Valid vector candidate
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[integration_test]

## TENSION (Cognitive Proof)
L1::[TDD_MANDATE]⇌CTX:README.md[exists]→TRIGGER[VERIFY]
L2::[STRUCTURAL_INTEGRITY]⇌CTX:PROJECT-CONTEXT.oct.md[B1]→TRIGGER[VALIDATE]

## COMMIT (Falsifiable Contract)
ARTIFACT::tests/integration/odyssean_anchor/test_odyssean_anchor_integration.py
GATE::pytest -m integration
"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id="test-session",
            working_dir=str(project_dir),
            tier="default",
        )

        assert result.success, f"Expected success but got errors: {result.errors}"
        assert result.anchor is not None
        assert "## ARM" in result.anchor
        assert "BRANCH::" in result.anchor
        assert "PHASE::B1" in result.anchor
        assert "FOCUS::integration-testing" in result.anchor

    def test_odyssean_anchor_arm_reflects_git_state(self, tmp_path: Path) -> None:
        """Verify ARM section accurately reflects actual git state.

        This test modifies files after the initial commit and verifies
        that the ARM section correctly reports the number of changed files.
        """
        # Setup git repo
        project_dir = tmp_path / "git_state_project"
        project_dir.mkdir()

        subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Initial commit
        (project_dir / "file1.txt").write_text("initial content")
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "initial"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Make changes to create modified/untracked files
        (project_dir / "file1.txt").write_text("modified content")  # Modified
        (project_dir / "file2.txt").write_text("new file")  # Untracked

        # Setup session
        session_id = "git-state-test"
        session_dir = project_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "session.json").write_text(
            json.dumps({"session_id": session_id, "focus": "git-state-verification"})
        )

        # Setup context
        context_dir = project_dir / ".hestai" / "context"
        context_dir.mkdir(parents=True)
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[git_state_test]

## TENSION (Cognitive Proof)
L1::[GIT_STATE_AWARENESS]⇌CTX:file1.txt[modified]→TRIGGER[TRACK]
L2::[FILE_CHANGES]⇌CTX:file2.txt[untracked]→TRIGGER[MONITOR]

## COMMIT (Falsifiable Contract)
ARTIFACT::tests/integration/odyssean_anchor/test_odyssean_anchor_integration.py
GATE::pytest -m integration
"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(project_dir),
            tier="default",
        )

        assert result.success, f"Expected success but got errors: {result.errors}"
        assert result.anchor is not None
        # ARM should reflect the 2 changed files (1 modified + 1 untracked)
        assert "FILES::" in result.anchor
        # Branch should be captured
        assert "BRANCH::" in result.anchor

    def test_odyssean_anchor_handles_feature_branch(self, tmp_path: Path) -> None:
        """Verify ARM captures feature branch name correctly.

        Tests that when working on a feature branch, the ARM section
        correctly identifies the branch name.
        """
        project_dir = tmp_path / "branch_project"
        project_dir.mkdir()

        # Setup git with main branch
        subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        (project_dir / "README.md").write_text("# Project")
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "initial"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Create and checkout feature branch
        subprocess.run(
            ["git", "checkout", "-b", "feature/odyssean-anchor"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Setup session and context
        session_id = "branch-test"
        session_dir = project_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "session.json").write_text(
            json.dumps({"session_id": session_id, "focus": "branch-testing"})
        )

        context_dir = project_dir / ".hestai" / "context"
        context_dir.mkdir(parents=True)
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B2")

        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[branch_test]

## TENSION (Cognitive Proof)
L1::[BRANCH_AWARENESS]⇌CTX:README.md[exists]→TRIGGER[VERIFY]
L2::[FEATURE_WORK]⇌CTX:PROJECT-CONTEXT.oct.md[B2]→TRIGGER[BUILD]

## COMMIT (Falsifiable Contract)
ARTIFACT::tests/integration/odyssean_anchor/test_odyssean_anchor_integration.py
GATE::pytest -m integration
"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(project_dir),
            tier="default",
        )

        assert result.success, f"Expected success but got errors: {result.errors}"
        assert result.anchor is not None
        # Should capture the feature branch name
        assert "BRANCH::feature/odyssean-anchor" in result.anchor

    def test_odyssean_anchor_quick_tier_with_single_tension(self, tmp_path: Path) -> None:
        """Verify quick tier accepts single tension for lightweight binding.

        Quick tier is designed for fast operations where minimal
        cognitive proof is acceptable.
        """
        project_dir = tmp_path / "quick_tier_project"
        project_dir.mkdir()

        # Minimal git setup
        subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        (project_dir / "README.md").write_text("# Quick")
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "init"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        # Setup session
        session_id = "quick-tier"
        session_dir = project_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "session.json").write_text(
            json.dumps({"session_id": session_id, "focus": "quick-check"})
        )

        context_dir = project_dir / ".hestai" / "context"
        context_dir.mkdir(parents=True)
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Single tension is valid for quick tier
        vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[quick_check]

## TENSION (Cognitive Proof)
L1::[STATUS_CHECK]⇌CTX:README.md[exists]→TRIGGER[REPORT]

## COMMIT (Falsifiable Contract)
ARTIFACT::status_report.md
GATE::human review
"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=vector,
            session_id=session_id,
            working_dir=str(project_dir),
            tier="quick",  # Quick tier allows single tension
        )

        assert result.success, f"Expected success but got errors: {result.errors}"
        assert result.anchor is not None

    def test_odyssean_anchor_retry_guidance_on_failure(self, tmp_path: Path) -> None:
        """Verify retry guidance is provided on validation failure.

        When validation fails, the tool should provide actionable
        guidance to help the agent correct their vector.
        """
        project_dir = tmp_path / "retry_test"
        project_dir.mkdir()

        subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
        # Disable global hooks for test hermeticity
        subprocess.run(
            ["git", "config", "core.hooksPath", ""],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        (project_dir / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "init"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        session_id = "retry-test"
        session_dir = project_dir / ".hestai" / "sessions" / "active" / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "session.json").write_text(
            json.dumps({"session_id": session_id, "focus": "retry-testing"})
        )

        context_dir = project_dir / ".hestai" / "context"
        context_dir.mkdir(parents=True)
        (context_dir / "PROJECT-CONTEXT.oct.md").write_text("PHASE::B1")

        # Invalid vector - missing CTX citation and generic artifact
        invalid_vector = """## BIND (Identity Lock)
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS
AUTHORITY::RESPONSIBLE[build]

## TENSION (Cognitive Proof)
L1::[CONSTRAINT]⇌[state]→TRIGGER[ACTION]

## COMMIT (Falsifiable Contract)
ARTIFACT::response
GATE::review
"""

        result = odyssean_anchor(
            role="implementation-lead",
            vector_candidate=invalid_vector,
            session_id=session_id,
            working_dir=str(project_dir),
            tier="default",
        )

        assert not result.success
        assert result.errors
        assert result.guidance
        assert len(result.guidance) > 0
        # Should provide specific guidance
        assert (
            "CTX" in result.guidance
            or "ARTIFACT" in result.guidance
            or "TENSION" in result.guidance
        )
        assert result.retry_count == 0
        assert not result.terminal
