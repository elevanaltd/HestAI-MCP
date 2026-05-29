"""Self-application guard — bundled-hub + project governance artifacts must satisfy octave-mcp validators.

Walks every ``*.md`` and ``*.oct.md`` under ``src/hestai_mcp/_bundled_hub/`` and the
project-local ``.hestai/north-star/`` and ``.hestai/rules/`` trees and runs octave-mcp's
``W_SNAKE_CASE_BLOB`` detector on each. Asserts zero hits.

WHY THIS EXISTS (#406 Phase 1/2)
--------------------------------
``W_SNAKE_CASE_BLOB`` flags snake-fragmented prose in reasoning-field positions
(DECISION, BECAUSE, RATIONALE, PRINCIPLE, WHY, ...). The bundled hub injects into
``.hestai-sys/`` at MCP server startup, so a blob shipped here teaches every
downstream agent that blobs are canonical — an autocatalytic corruption loop
(see octave-mcp#452). PRs #408/#409/#410 cleared the existing hits and migrated
the North Star summaries to TELEGRAPHIC_PHRASE / UPOG form; this test is the
mechanical guard that keeps the surface clean going forward.

If this test fails after an upstream octave-mcp release, the validator likely got
stricter — investigate whether the new triggers are correct, then either fix the
surfaced artifacts (telegraphic-phrase per octave-compression §4 R3a) or escalate
to the octave-mcp maintainers. Do not silence the guard.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("octave_mcp", reason="octave-mcp not installed")

# Private API tracked deliberately — octave-mcp does not yet export a public entry
# point for the W_SNAKE_CASE_BLOB detector. Revisit if upstream renames or promotes
# the function (grep "W_SNAKE_CASE_BLOB" in the installed octave_mcp package).
from octave_mcp.mcp.write_detection import _detect_snake_case_blob  # noqa: PLC2701

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCAN_ROOTS = [
    _REPO_ROOT / "src" / "hestai_mcp" / "_bundled_hub",
    _REPO_ROOT / ".hestai" / "north-star",
    _REPO_ROOT / ".hestai" / "rules",
]


def _scan_targets() -> list[Path]:
    files: set[Path] = set()
    for root in _SCAN_ROOTS:
        if not root.exists():
            continue
        for pattern in ("*.md", "*.oct.md"):
            files.update(root.rglob(pattern))
    return sorted(files)


@pytest.mark.smoke
@pytest.mark.unit
class TestBundledHubSelfApplication:
    """Governance artifacts we ship must pass octave-mcp's W_SNAKE_CASE_BLOB detector."""

    def test_scan_targets_are_discovered(self) -> None:
        """Guard against a silently-empty scan (moved dirs, bad glob) giving false safety."""
        targets = _scan_targets()
        assert targets, (
            "Self-application scan found no .md/.oct.md files under "
            f"{[str(r) for r in _SCAN_ROOTS]} — the guard would pass vacuously. "
            "Verify the scan roots still exist."
        )

    def test_no_w_snake_case_blob_in_shipped_artifacts(self) -> None:
        """Every scanned artifact emits zero W_SNAKE_CASE_BLOB warnings."""
        offenders: dict[str, list[dict[str, object]]] = {}
        for path in _scan_targets():
            content = path.read_text(encoding="utf-8")
            warnings = _detect_snake_case_blob(content)
            if warnings:
                offenders[str(path.relative_to(_REPO_ROOT))] = warnings

        assert not offenders, (
            "Snake-case prose blob detected in reasoning-field positions. Convert each "
            "offender to a TELEGRAPHIC_PHRASE (quoted value, stopwords dropped, operators "
            "⊕ ⇌ ∧ ∨ → carry English connectives — see octave-compression §4 R3a). "
            f"Offenders: {offenders}"
        )
