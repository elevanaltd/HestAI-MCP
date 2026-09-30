"""Pattern kernel guard: bundled-hub patterns must carry an extractable ANCHOR_KERNEL.

WHY THIS EXISTS
----------------
At bind time the Odyssean Anchor ceremony compiles each declared pattern into a
kernel via ``extract_pattern_kernel``. When a pattern has no extractable kernel the
ceremony injects ``WARN::UNSTRUCTURED[<name>]::No extractable kernel found`` in
place of the pattern - the bound agent proceeds believing it received the pattern's
rules when it received nothing. This is the same "the ceremony silently loads
nothing" class of defect guarded by ``test_bundled_hub_selector_resolution.py``.

Measured at odyssean-anchor 2c065610 before PR #451: ``tdd-discipline``,
``verification-protocols`` and ``phase-transition-cleanup`` all returned that WARN,
so binds of implementation-lead, test-methodology-guardian, task-decomposer,
visual-architect and system-steward received no kernel for them. This guard pins the
fix: each pattern now carries an extractable ANCHOR_KERNEL.

MIRRORED EXTRACTOR RULE (hestai-mcp does NOT depend on ``odyssean_anchor``)
---------------------------------------------------------------------------
Mirrors priority 1 of ``extract_pattern_kernel`` and the helpers it calls, from
odyssean-anchor-mcp @ 2c065610 (``src/odyssean_anchor/core/extraction.py``):

- ``_strip_yaml_frontmatter`` (l.897): a leading ``---`` ... ``---`` block is removed.
- ``_extract_anchor_kernel`` (l.951):
  * the start marker is the regex ``§(?:\\d+::)?ANCHOR_KERNEL`` (first match anywhere);
  * extraction begins on the line AFTER the marker line;
  * it stops at a line starting ``===END_KERNEL===``, a line matching
    ``^§\\d+::``, or a line starting ``===END===`` (all after ``strip()``);
  * no collected lines -> ``None`` (falls through to priority 2/3).
  * a non-empty result is returned as ``"\\n".join(lines).strip()``.
- ``extract_pattern_kernel`` (l.1274) only reaches priorities 2/3
  (``§1::CORE_PRINCIPLE`` / a ``§1::`` section containing ``PRINCIPLE``) when
  priority 1 yields nothing. This guard asserts priority 1 so the kernel is the
  explicit, exported one rather than an accidental principle fallback.

The extra assertion (TARGET/NEVER/MUST/GATE keys) is a hestai-mcp house convention
taken from the in-hub precedents (pr-scope-containment, review-handoff,
progressive-simplification), not an extractor requirement.

If the extractor rule drifts, update this mirror and the SHA above together.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PATTERNS_DIR = _REPO_ROOT / "src" / "hestai_mcp" / "_bundled_hub" / "library" / "patterns"

_KERNEL_MARKER = re.compile(r"§(?:\d+::)?ANCHOR_KERNEL")
_SECTION_START = re.compile(r"^§\d+::")
_REQUIRED_KEYS: tuple[str, ...] = ("TARGET", "NEVER", "MUST", "GATE")

# Patterns that must gain a kernel (RED until the octave author adds them).
_TARGET_PATTERNS: tuple[str, ...] = (
    "tdd-discipline",
    "verification-protocols",
    "phase-transition-cleanup",
)
# In-hub precedents that already carry a kernel: positive control proving this
# test can pass, so a failure on the targets is attributable to the files.
_PRECEDENT_PATTERNS: tuple[str, ...] = (
    "pr-scope-containment",
    "review-handoff",
    "progressive-simplification",
)


def _strip_yaml_frontmatter(content: str) -> str:
    """Mirror of extraction.py::_strip_yaml_frontmatter (l.897)."""
    if not content or not content.startswith("---"):
        return content
    lines = content.split("\n")
    if lines[0].strip() != "---":
        return content
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1 :]).lstrip("\n")
    return content


def _extract_anchor_kernel(content: str) -> str | None:
    """Mirror of extraction.py::_extract_anchor_kernel (l.951)."""
    kernel_match = _KERNEL_MARKER.search(content)
    if kernel_match is None:
        return None

    kernel_lines: list[str] = []
    in_kernel = False
    for line in content[kernel_match.start() :].split("\n"):
        if _KERNEL_MARKER.search(line) and not in_kernel:
            in_kernel = True
            continue
        if in_kernel:
            stripped = line.strip()
            if stripped.startswith("===END_KERNEL==="):
                break
            if _SECTION_START.match(stripped) or stripped.startswith("===END==="):
                break
            kernel_lines.append(line)

    if not kernel_lines:
        return None
    return "\n".join(kernel_lines).strip()


def _kernel_for(pattern: str) -> str | None:
    path = _PATTERNS_DIR / f"{pattern}.oct.md"
    assert path.is_file(), f"pattern file missing: {path}"
    return _extract_anchor_kernel(_strip_yaml_frontmatter(path.read_text(encoding="utf-8")))


_ALL_PATTERNS = _TARGET_PATTERNS + _PRECEDENT_PATTERNS


@pytest.mark.parametrize("pattern", _ALL_PATTERNS)
def test_pattern_has_extractable_anchor_kernel(pattern: str) -> None:
    kernel = _kernel_for(pattern)
    assert kernel, (
        f"{pattern}.oct.md has no extractable §N::ANCHOR_KERNEL section; the ceremony "
        f"would inject 'WARN::UNSTRUCTURED[{pattern}]::No extractable kernel found'"
    )


@pytest.mark.parametrize("pattern", _ALL_PATTERNS)
def test_pattern_anchor_kernel_carries_required_keys(pattern: str) -> None:
    kernel = _kernel_for(pattern)
    assert kernel, f"{pattern}.oct.md has no extractable ANCHOR_KERNEL body to inspect"
    missing = [
        key for key in _REQUIRED_KEYS if not re.search(rf"^\s*{key}::", kernel, re.MULTILINE)
    ]
    assert not missing, f"{pattern}.oct.md ANCHOR_KERNEL is missing keys: {missing}"
