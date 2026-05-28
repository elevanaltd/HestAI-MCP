"""UPOG compliance regression guard for North Star governance documents.

Locks the gain from the UPOG (Universal Parse-Only Governance) migration
(PR #409, octave-literacy §8). The legacy immutable form
``I1::NAME::[PRINCIPLE::v, WHY::v, STATUS::v]`` silently lost data under the
octave-mcp 1.13 strict lexer: the chained ``::NAME::[...]`` read as an
assignment, hoisting inner keys to file-top-level so PRINCIPLE/WHY/STATUS
collided across I1..IN (W_DUPLICATE_KEY x3N, last-write-wins). PRODUCT-tier
files additionally failed E_TOKENIZE on ``## markdown headings``.

The bundled regex validator (octave-validator.py v5.1.0) does NOT detect
W_DUPLICATE_KEY — that false-confidence is what let the bug live. This test
uses ``octave_mcp.parse_with_warnings`` (the 1.13 strict lexer) which is the
only mechanism that surfaces the collision.

Guard: every governance North Star .oct.md MUST parse without LexerError
(catches markdown-heading regression) and emit zero structural-loss warnings
(catches inline-map regression). New NS files are covered automatically via
glob — the guard is the schema.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("octave_mcp", reason="octave-mcp not installed")

# tests/unit/governance/<this> -> repo root is parents[3]
_REPO_ROOT = Path(__file__).resolve().parents[3]

# Warning subtypes that signal a regression back to the broken legacy form.
# duplicate_key  -> inline-map immutable form collided keys (the data-loss bug)
# bare_line_dropped -> unkeyed content silently dropped
# bare_flow      -> flow operator outside brackets (legacy GATES/ESCALATE form)
_REGRESSION_SUBTYPES = {"duplicate_key", "bare_line_dropped", "bare_flow"}


def _north_star_docs() -> list[Path]:
    """All governance North Star .oct.md docs that must hold UPOG form.

    Covers project NS (.hestai/north-star) and bundled-hub source NS
    (system summary + project template). Excludes .hestai-sys/ — that is the
    gitignored runtime copy regenerated from _bundled_hub/ on server start.
    """
    docs: list[Path] = []
    docs.extend((_REPO_ROOT / ".hestai" / "north-star").rglob("*.oct.md"))
    bundled = _REPO_ROOT / "src" / "hestai_mcp" / "_bundled_hub"
    docs.extend(bundled.rglob("*NORTH-STAR-SUMMARY.oct.md"))
    # Deduplicate and stabilise ordering for readable parametrize ids.
    return sorted(set(docs))


_DOCS = _north_star_docs()


@pytest.mark.smoke
@pytest.mark.unit
def test_north_star_docs_discovered() -> None:
    """Sanity: the glob actually finds the governance NS corpus.

    A zero-length corpus would make every per-file test vacuously pass —
    this anchors the suite against a silently-empty glob.
    """
    assert _DOCS, "No North Star .oct.md documents found — glob is broken"


@pytest.mark.unit
@pytest.mark.parametrize("doc", _DOCS, ids=lambda p: p.relative_to(_REPO_ROOT).as_posix())
def test_north_star_doc_is_upog_clean(doc: Path) -> None:
    """Each NS doc parses under the strict lexer with no structural-loss warnings."""
    from octave_mcp import LexerError, parse_with_warnings

    content = doc.read_text(encoding="utf-8")

    # E_TOKENIZE regression (e.g. reintroduced "## markdown headings") raises here.
    try:
        _, warnings = parse_with_warnings(content)
    except LexerError as exc:  # pragma: no cover - failure path
        pytest.fail(
            f"{doc.relative_to(_REPO_ROOT)} failed strict tokenization "
            f"(UPOG §8c markdown-eradication regression?): {exc}"
        )

    offenders = [w for w in warnings if (w.get("subtype") or w.get("type")) in _REGRESSION_SUBTYPES]
    assert not offenders, (
        f"{doc.relative_to(_REPO_ROOT)} regressed to lossy legacy form. "
        f"Structural-loss warnings: "
        + ", ".join(
            f"{w.get('subtype') or w.get('type')}" f"({w.get('key') or w.get('message', '')[:40]})"
            for w in offenders
        )
    )
