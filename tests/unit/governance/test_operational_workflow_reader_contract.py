"""Reader-contract regression test for OPERATIONAL-WORKFLOW.oct.md.

PR #447 review (Copilot + cubic): the bundled workflow document is consumed by
line-regex readers, not by an OCTAVE parser, so its *line shape* is a contract:

1. Exactly one phase-marker key per phase (D0..D3, B0..B5), in order, each a
   one-line ``KEY::scalar``.
2. No other key anywhere in the file starts with a phase prefix (``D0_``..``D3_``,
   ``B0_``..``B5_``). The readers treat every such key as a phase boundary, so a
   stray ``B2_00_REQUIREMENTS`` or ``B5_CRITERIA`` truncates or contaminates a phase.
3. Inside a phase block the fields the readers extract (PURPOSE, RACI, DELIVERABLE,
   DELIVERABLES, ENTRY, EXIT, QUALITY_GATE_MANDATORY, QUALITY_GATES, SUBPHASES)
   are complete single-line values. A value that is just ``[`` or ends with an
   unclosed ``[`` (what a multi-line list rewrite produces) is read as ``['[']``.
4. No list item (DELIVERABLE(S)/ENTRY/EXIT) contains a comma inside quotes: the context-mcp
   reader splits ``[...]`` naively on commas, so such an item would be served as two.
5. B1, the served phase, is pinned to an explicit expected snapshot (purpose, the four
   deliverables, quality gates); see ``B1_EXPECTED_*``.

The hestai-context-mcp reader lives in another repository and cannot be imported
in CI. The line-shape assertions below ARE its contract; see
hestai-context-mcp ``src/hestai_context_mcp/core/context_steward.py``
(``ContextSteward._extract_phase_section``). The legacy in-repo reader
(``hestai_mcp.core.governance.state.context_steward``) is exercised directly.

Every check takes the file path through ``_target()`` so a scratch script can point
``WORKFLOW_PATH`` at a broken input and prove the guard fires. The committed test
targets only the bundled file.
"""

import re
from pathlib import Path

import pytest

from hestai_mcp.core.governance.state.context_steward import ContextSteward

WORKFLOW_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "src"
    / "hestai_mcp"
    / "_bundled_hub"
    / "standards"
    / "workflow"
    / "OPERATIONAL-WORKFLOW.oct.md"
)

PHASES = ["D0", "D1", "D2", "D3", "B0", "B1", "B2", "B3", "B4", "B5"]
PHASE_KEY_RE = re.compile(r"^(?:D[0-3]|B[0-5])_")
SCALAR_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
SINGLE_LINE_FIELDS = {
    "PURPOSE",
    "RACI",
    "DELIVERABLE",
    "DELIVERABLES",
    "ENTRY",
    "EXIT",
    "QUALITY_GATE_MANDATORY",
    "QUALITY_GATES",
    "SUBPHASES",
}


def _target() -> Path:
    return WORKFLOW_PATH


def _keyed_lines(path: Path) -> list[tuple[int, str, str]]:
    """Return (line_no, key, value) for every line with '::', as the readers see it."""
    rows = []
    for number, line in enumerate(path.read_text().split("\n"), start=1):
        stripped = line.strip()
        if "::" in stripped:
            key, value = stripped.split("::", 1)
            rows.append((number, key.strip(), value.strip()))
    return rows


def _phase_markers(path: Path) -> list[tuple[int, str, str]]:
    return [row for row in _keyed_lines(path) if PHASE_KEY_RE.match(row[1])]


def marker_violations(path: Path) -> list[str]:
    """One scalar phase marker per phase, in D0..B5 order, and no other phase-prefixed key."""
    markers = _phase_markers(path)
    violations = []
    seen = [key[:2] for _, key, _ in markers]
    if seen != PHASES:
        violations.append(
            f"phase-prefixed keys {[key for _, key, _ in markers]} "
            f"do not form exactly one marker per phase in order {PHASES}"
        )
    for number, key, value in markers:
        if not SCALAR_RE.match(value):
            violations.append(
                f"line {number}: marker {key} value {value!r} is not a one-line scalar"
            )
    return violations


def field_violations(path: Path) -> list[str]:
    """Reader-extracted fields are complete single-line values, at most once per block."""
    rows = _keyed_lines(path)
    marker_lines = {number for number, _, _ in _phase_markers(path)}
    violations = []
    current: str | None = None
    counts: dict[str, int] = {}
    for number, key, value in rows:
        if number in marker_lines:
            current = key
            counts = {}
            continue
        if current is None or key not in SINGLE_LINE_FIELDS:
            continue
        if key in {"DELIVERABLE", "DELIVERABLES"}:
            other = "DELIVERABLES" if key == "DELIVERABLE" else "DELIVERABLE"
            if other in counts:
                violations.append(
                    f"line {number}: {current} block has both DELIVERABLE and DELIVERABLES "
                    "(ambiguous: reader prefers DELIVERABLE)"
                )
        counts[key] = counts.get(key, 0) + 1
        if counts[key] > 1:
            violations.append(
                f"line {number}: {current} block repeats {key} (last value wins in readers)"
            )
        if not value or value in {"[]", '""'}:
            violations.append(f"line {number}: {current} {key} has an empty value")
        elif value.endswith("[") or value.count("[") != value.count("]") or value.count('"') % 2:
            violations.append(
                f"line {number}: {current} {key} is not a complete one-line value: {value[:60]!r}"
            )
    return violations


def _phase_blocks(path: Path) -> dict[str, list[tuple[int, str, str]]]:
    """Map phase id to the keyed lines of its own block (marker excluded).

    A block runs from its marker to the next phase marker, or to EOF for the last
    phase, exactly as the line-regex readers collect it.
    """
    marker_lines = {number: key[:2] for number, key, _ in _phase_markers(path)}
    blocks: dict[str, list[tuple[int, str, str]]] = {}
    current: str | None = None
    for row in _keyed_lines(path):
        if row[0] in marker_lines:
            current = marker_lines[row[0]]
            blocks[current] = []
        elif current is not None:
            blocks[current].append(row)
    return blocks


def _own_purpose(block: list[tuple[int, str, str]]) -> str | None:
    """The block's own PURPOSE value (last wins, as in the readers), unquoted."""
    values = [value for _, key, value in block if key == "PURPOSE"]
    return values[-1].strip('"') if values else None


def b1_purpose_violations(path: Path) -> list[str]:
    """B1 PURPOSE, taken from the B1 block only, describes the architecture-to-implementation plan."""
    block = _phase_blocks(path).get("B1")
    if block is None:
        return ["B1 marker missing"]
    purposes = [(number, value) for number, key, value in block if key == "PURPOSE"]
    if not purposes:
        return ["B1 block has no PURPOSE of its own"]
    number, value = purposes[-1]
    lowered = value.lower()
    if "architecture" in lowered or "implementation" in lowered:
        return []
    return [f"line {number}: B1 PURPOSE {value!r} mentions neither architecture nor implementation"]


def _parse_items(raw: str) -> list[str]:
    """Items the reader should serve for a one-line value: split a top-level [..] list on
    commas outside brackets/quotes and strip quotes; a bare or quoted scalar is one item."""
    raw = raw.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        return [raw.strip('"')] if raw else []
    items, depth, quoted, current = [], 0, False, ""
    for char in raw[1:-1]:
        if char == '"':
            quoted = not quoted
        elif not quoted and char == "[":
            depth += 1
        elif not quoted and char == "]":
            depth -= 1
        if char == "," and depth == 0 and not quoted:
            items.append(current.strip().strip('"'))
            current = ""
        else:
            current += char
    if current.strip():
        items.append(current.strip().strip('"'))
    return items


LIST_FIELDS = {"DELIVERABLE", "DELIVERABLES", "ENTRY", "EXIT"}

# B1 is the phase served to agents. This is a deliberate snapshot of what the contract says
# B1 must serve. Changing B1 content in OPERATIONAL-WORKFLOW.oct.md requires updating this
# snapshot deliberately, in the same PR.
B1_EXPECTED_PURPOSE = "Validated architecture→actionable implementation plan"
B1_EXPECTED_DELIVERABLES = [
    "B1-BUILD-PLAN.md⊕task_breakdown",
    "B1-WORKSPACE.md⊕environment⊕CI/CD_setup⊕QUALITY_GATE_EVIDENCE",
    "B1-DEPENDENCIES.md⊕critical_path",
    "TRACED_artifacts",
]
B1_EXPECTED_QUALITY_GATES = "⚠️ Load workspace-setup skill for stack-specific gates. NO src/ FILES WITHOUT PASSING quality gates per project stack: python[ruff_check,black_check,mypy,pytest] | node[lint,typecheck,test_via_repo_declared_runner:package.json_packageManager+declared_scripts+lockfile,NEVER_assume_npm] | generic[lint,typecheck,test]"


def _context_mcp_items(raw: str) -> list[str]:
    r"""Reproduce hestai-context-mcp's list splitting, which is NOT quote-aware.

    Mirrors ``ContextSteward._extract_list_field`` in hestai-context-mcp
    ``src/hestai_context_mcp/core/context_steward.py`` lines 167-181 at commit 06aac8c:
    ``re.match(r"^\[(.+)\]$", value)`` then ``group(1).split(",")``, strip, drop empties;
    any other non-empty value is a single item. That reader keeps quotes; callers strip
    them where they compare content.
    """
    if not raw:
        return []
    match = re.match(r"^\[(.+)\]$", raw)
    if match:
        return [item for item in (part.strip() for part in match.group(1).split(",")) if item]
    return [raw]


def list_split_violations(path: Path) -> list[str]:
    """No comma inside a quoted list item: the naive and quote-aware splits must agree."""
    violations = []
    current: str | None = None
    marker_lines = {number: key for number, key, _ in _phase_markers(path)}
    for number, key, value in _keyed_lines(path):
        if number in marker_lines:
            current = key
            continue
        if current is None or key not in LIST_FIELDS:
            continue
        naive, aware = _context_mcp_items(value), _parse_items(value)
        if len(naive) != len(aware):
            violations.append(
                f"line {number}: {current} {key} splits into {len(naive)} items in the "
                f"context-mcp reader but {len(aware)} quote-aware (comma inside a quoted item?)"
            )
    return violations


def b1_snapshot_violations(path: Path) -> list[str]:
    """B1 serves exactly the pinned purpose, deliverables and quality gates."""
    block = _phase_blocks(path).get("B1")
    if block is None:
        return ["B1 marker missing"]
    violations = []
    fields = {key: value for _, key, value in block}
    purpose = fields.get("PURPOSE", "").strip('"')
    if purpose != B1_EXPECTED_PURPOSE:
        violations.append(f"B1 PURPOSE {purpose!r} != snapshot {B1_EXPECTED_PURPOSE!r}")
    raw = fields.get("DELIVERABLE", fields.get("DELIVERABLES", ""))
    split = [item.strip('"') for item in _context_mcp_items(raw)]
    if split != B1_EXPECTED_DELIVERABLES:
        violations.append(f"B1 deliverables (context-mcp split) {split} != snapshot")
    gates = fields.get("QUALITY_GATE_MANDATORY", fields.get("QUALITY_GATES", "")).strip('"')
    if gates != B1_EXPECTED_QUALITY_GATES:
        violations.append(f"B1 quality gates {gates!r} != snapshot")
    try:
        served = ContextSteward(workflow_path=path).synthesize_active_state("B1")
    except Exception as error:  # noqa: BLE001 - any reader failure is a contract failure
        return [*violations, f"B1: legacy reader failed: {error!r}"]
    if served.purpose != B1_EXPECTED_PURPOSE:
        violations.append(f"B1 legacy-served purpose {served.purpose!r} != snapshot")
    if served.deliverables != B1_EXPECTED_DELIVERABLES:
        violations.append(f"B1 legacy-served deliverables {served.deliverables} != snapshot")
    if served.quality_gates != B1_EXPECTED_QUALITY_GATES:
        violations.append(f"B1 legacy-served quality_gates {served.quality_gates!r} != snapshot")
    return violations


def legacy_reader_violations(path: Path) -> list[str]:
    """The in-repo legacy reader resolves all ten phases from their own blocks."""
    violations = []
    steward = ContextSteward(workflow_path=path)
    blocks = _phase_blocks(path)
    markers = {key[:2]: value for _, key, value in _phase_markers(path)}
    for phase in PHASES:
        try:
            constraints = steward.synthesize_active_state(phase)
        except Exception as error:  # noqa: BLE001 - any reader failure is a contract failure
            violations.append(f"{phase}: legacy reader failed: {error!r}")
            continue
        block = blocks.get(phase, [])
        own_purpose = _own_purpose(block)
        if own_purpose is None and phase.startswith("B"):
            violations.append(f"{phase}: block has no PURPOSE of its own (reader would fall back)")
        elif own_purpose is None:
            # D0-D3 legitimately have no PURPOSE line: the reader uses the marker value.
            if constraints.purpose != markers[phase]:
                violations.append(
                    f"{phase}: purpose {constraints.purpose!r} != marker value {markers[phase]!r}"
                )
        elif constraints.purpose != own_purpose:
            violations.append(
                f"{phase}: purpose {constraints.purpose!r} != own PURPOSE {own_purpose!r}"
            )
        if constraints.purpose == f"Phase {phase}":
            violations.append(f"{phase}: purpose resolved to the generic fallback")
        # Reader precedence (_extract_list_field): DELIVERABLE wins over DELIVERABLES.
        raw_by_key = {
            key: value for _, key, value in block if key in {"DELIVERABLE", "DELIVERABLES"}
        }
        own_raw = raw_by_key.get("DELIVERABLE", raw_by_key.get("DELIVERABLES"))
        if own_raw is None:
            violations.append(f"{phase}: block has no DELIVERABLE(S) line of its own")
        else:
            deliverables = constraints.deliverables
            expected = _parse_items(own_raw)
            if not deliverables:
                violations.append(f"{phase}: reader served empty deliverables for {own_raw[:60]!r}")
            elif phase.startswith("B") and not deliverables[0].startswith(f"{phase}-"):
                violations.append(f"{phase}: deliverables not from own block: {deliverables}")
            elif deliverables != expected:
                violations.append(
                    f"{phase}: served deliverables {deliverables} != items parsed from own block "
                    f"{expected}"
                )
        if phase == "B1" and not (constraints.quality_gates or "").strip():
            violations.append("B1: reader served empty quality_gates")
        if phase == "B5":
            text = str(constraints.to_dict()).lower()
            if "post-mortem" in text or "post_mortem" in text:
                violations.append(
                    f"B5: post-mortem text leaked into B5 constraints: {constraints.to_dict()}"
                )
    return violations


def taxonomy_violations(path: Path) -> list[str]:
    keys = {key for _, key, _ in _keyed_lines(path)}
    keys |= {line.strip().rstrip(":") for line in path.read_text().split("\n")}
    return [] if "ERROR_HANDLING_TAXONOMY" in keys else ["ERROR_HANDLING_TAXONOMY missing"]


@pytest.mark.unit
def test_bundled_workflow_exists():
    assert _target().exists(), f"Bundled workflow not found: {_target()}"


@pytest.mark.unit
def test_exactly_one_scalar_marker_per_phase_and_no_other_phase_prefixed_key():
    assert not marker_violations(_target())


@pytest.mark.unit
def test_reader_fields_are_complete_single_line_values():
    assert not field_violations(_target())


@pytest.mark.unit
def test_b1_purpose_mentions_architecture_or_implementation():
    assert not b1_purpose_violations(_target())


@pytest.mark.unit
def test_legacy_reader_resolves_all_ten_phases_from_their_own_blocks():
    assert not legacy_reader_violations(_target())


@pytest.mark.unit
def test_no_comma_inside_quoted_list_items():
    assert not list_split_violations(_target())


@pytest.mark.unit
def test_b1_serves_pinned_purpose_deliverables_and_quality_gates():
    assert not b1_snapshot_violations(_target())


@pytest.mark.unit
def test_error_handling_taxonomy_present():
    assert not taxonomy_violations(_target())
