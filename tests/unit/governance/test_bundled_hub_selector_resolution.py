"""Selector resolution guard — every declared capability name must resolve to a file.

WHY THIS EXISTS
----------------
``src/hestai_mcp/_bundled_hub/library/agents/*.oct.md`` agent definitions declare
capabilities in ``§3::CAPABILITIES`` under three distinct declaration shapes (see
SCHEMES below). The legacy Odyssean Anchor ceremony resolves each declared name
against the deployed ``.hestai-sys/library`` tree at bind time. If a declared name
has no corresponding directory or file, the ceremony loads NOTHING for that selector
and says nothing about the gap — the agent proceeds believing it has a capability it
never received.

This was observed live: a critical-engineer reviewer on elevanaltd/hestai-context-mcp
PR #165 (2026-09-09) reported four of its own declared capability files absent from
the injected governance tree. This test proves the defect is systemic, not a one-off
typo in a single agent file.

SCHEMES (all covered by this guard — one invariant, three declaration shapes)
------------------------------------------------------------------------------
1. TOP-LEVEL: ``SKILLS::[...]`` / ``PATTERNS::[...]`` directly under
   ``§3::CAPABILITIES`` (23 of 34 agent files, e.g. implementation-lead.oct.md).
2. PROFILE-NESTED (v8 Chassis-Profile): lowercase ``skills::[...]`` /
   ``patterns::[...]`` / ``kernel_only::[...]`` nested under named ``PROFILES``
   entries (11 of 34 agent files, e.g. holistic-orchestrator.oct.md:79-81). Disjoint
   from scheme 1 — no agent file uses both (measured: `comm -12` over
   `grep -lE '^\\s*(SKILLS|PATTERNS)::'` and `grep -lE '^\\s*(skills|patterns|kernel_only)::'`
   returns zero shared files at HEAD 6ed6547). 23 + 11 = 34, the full agent count.
   A per-profile declaration is the same promise to the same reader as a top-level
   one, so both schemes feed the same unresolved-selector check.
3. CHASSIS: ``CHASSIS::[...]`` — a top-level array declared alongside (and only
   ever alongside) the PROFILE-NESTED scheme's ``PROFILES:`` block (11 of the 11
   profile-nested agent files also declare ``CHASSIS``, e.g.
   agent-expert.oct.md:90). A CHASSIS entry is the same kind of promise as a
   skill/pattern/kernel_only selector — a bare name expected to resolve against
   the library at bind time — so it feeds the same unresolved-selector check.

RESOLUTION RULE (measured, not assumed)
----------------------------------------
- A skill name (top-level ``SKILLS`` or profile-nested ``skills``) resolves iff
  ``library/skills/<name>/`` exists as a directory.
- A pattern name (top-level ``PATTERNS`` or profile-nested ``patterns``) resolves
  iff ``library/patterns/<name>.oct.md`` exists as a file. Note the compound
  suffix: the file on disk is ``<name>.oct.md``, NOT ``<name>.md`` under a stem of
  ``<name>.oct``. ``Path.stem`` only strips the final ``.md``, leaving
  ``<name>.oct`` — comparing against that stripped form produces 7 false-positive
  "missing" patterns (mip-architecture, mip-build, octave-tool-reference,
  review-handoff, ripple-analysis-execution, tdd-discipline,
  verification-protocols) that are, in fact, present. This test builds its
  resolved-pattern-name set directly from the ``.oct.md`` compound suffix to
  avoid that trap.
- ``kernel_only`` resolves against ``library/skills/`` (same rule as ``skills``),
  NOT ``library/patterns/``. This was undecided from a single example (one
  observed binding payload carried ``KERNEL_ONLY::[review-gate]``, and
  ``review-gate`` is a skill directory — but one instance is not a rule, and
  ``review-gate`` does not appear as a ``kernel_only`` value anywhere in this
  hub's source files, so that example cannot be re-derived from the artifacts
  scanned here). The rule below is instead settled by exhaustive measurement:
  every ``kernel_only`` value declared anywhere in
  ``src/hestai_mcp/_bundled_hub/library/agents/*.oct.md`` at HEAD 6ed6547 — 14
  distinct names across 28 occurrences (abstraction-layer-mapping,
  agent-interview, cognitive-load-assessment, dependency-graph-analysis,
  drift-detection, e2e-test-strategy, integrity-defense, operating-discipline,
  python-style, rollback-orchestration, security-threat-modeling, skill-creator,
  stub-detection, test-validation-standards) — resolves as a
  ``library/skills/<name>/`` directory, and ZERO resolve as a
  ``library/patterns/<name>.oct.md`` file. No counterexample exists in the
  current hub, so this test encodes "kernel_only resolves against skills" as the
  rule rather than checking both namespaces. If a future kernel_only value is
  added that is a pattern, not a skill, this rule will need revisiting — that
  would be new evidence, not a bug in this test.
- ``CHASSIS`` resolves against ``library/skills/`` (same rule as ``skills`` and
  ``kernel_only``), NOT ``library/patterns/``. Settled the same way as
  ``kernel_only``: exhaustive measurement, not a single example. Every
  ``CHASSIS`` value declared anywhere in
  ``src/hestai_mcp/_bundled_hub/library/agents/*.oct.md`` at HEAD 6ed6547 — 12
  distinct names across 19 occurrences (agent-creation, code-quality-standards,
  complexity-assessment, integration-orchestration, octave-literacy,
  operating-discipline, review-context, review-discipline, review-preflight,
  standards-review, subagent-rules, synthesis-foundation) — resolves as a
  ``library/skills/<name>/`` directory, and ZERO resolve as a
  ``library/patterns/<name>.oct.md`` file. No counterexample exists in the
  current hub, so this test encodes "CHASSIS resolves against skills" as the
  rule rather than checking both namespaces. If a future CHASSIS value is added
  that is a pattern, not a skill, this rule will need revisiting — that would be
  new evidence, not a bug in this test.

SCOPE — SHRINK-ONLY RATCHET (was a RED-phase guard, now converted)
--------------------------------------------------------------------
At HEAD 6ed6547 the TOP-LEVEL scheme alone accounted for every unresolved
selector found (47 — 29 skills + 18 patterns — across 13 of the 34 bundled-hub
agent definitions; see issue #431 for the same figure independently measured on
2026-06-06). The PROFILE-NESTED scheme (skills/patterns/kernel_only nested under
PROFILES, 11 agent files) and the CHASSIS scheme (11 of those same 11 files) were
both measured and found to have ZERO unresolved selectors — every profile-nested
skill, pattern, kernel_only, and CHASSIS name in the hub resolves. That is a real
finding, not a gap in coverage: this test scans all three schemes.

Two of the 47 original offenders were resolved directly (critical-engineer.oct.md
§3::CAPABILITIES: `critical-domain-invariants` was ported from the hestai-workbench
starter library, making the pre-existing declaration resolve). Three more were
pruned from critical-engineer.oct.md's own declarations by operator ruling
(`observability-validation-standards`, `disaster-recovery-validation`,
`incident-response` — removed, not replaced; see PR discussion for
ce-silent-absent-capabilities). That leaves exactly 43 unresolved top-level
selectors, captured below as ``KNOWN_UNRESOLVED`` — a ratchet, not a silencer:

- Every selector class is still scanned every run (nothing is skipped/xfailed).
- Any unresolved selector NOT in ``KNOWN_UNRESOLVED`` is NEW ROT and fails the
  build immediately, naming the offending selector.
- Any ``KNOWN_UNRESOLVED`` entry that no longer appears as unresolved (because
  it now resolves, or because the declaration was removed/renamed) is a STALE
  baseline entry and fails the build, telling you exactly which line to delete
  from ``KNOWN_UNRESOLVED``.
- The baseline can therefore only ever shrink, one entry at a time, as issue
  #431 (the open reconcile-vs-migrate question for these agents: author the
  missing files, port them from elsewhere, or prune the declarations) is
  worked through — never grow, and never silently pass.

Do NOT add new names directly to ``KNOWN_UNRESOLVED`` to make a newly-introduced
unresolved selector pass — that defeats the ratchet's purpose. Only remove
entries, and only when the underlying selector has actually been resolved or
its declaration removed. If this test starts failing with a materially
different set of offenders than ``KNOWN_UNRESOLVED``, that is a signal the
bundled hub changed shape — investigate whether new agent files/selectors were
added (expected — is the new selector really unresolved on purpose? if so, that
requires an explicit, reviewed addition to the baseline with its own
justification) or whether a resolution rule above stopped matching reality
(escalate).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_AGENTS_DIR = _REPO_ROOT / "src" / "hestai_mcp" / "_bundled_hub" / "library" / "agents"
_SKILLS_DIR = _REPO_ROOT / "src" / "hestai_mcp" / "_bundled_hub" / "library" / "skills"
_PATTERNS_DIR = _REPO_ROOT / "src" / "hestai_mcp" / "_bundled_hub" / "library" / "patterns"

# selector_type -> (declaration key exact-case, resolver namespace)
# TOP-LEVEL (uppercase SKILLS/PATTERNS), PROFILE-NESTED (lowercase
# skills/patterns/kernel_only), and CHASSIS (uppercase, declared alongside the
# profile-nested scheme) declaration keys are all scanned. kernel_only and
# CHASSIS only exist in/alongside the profile-nested scheme. "namespace" picks
# which resolver (_skill_resolves / _pattern_resolves) applies.
_SELECTOR_KEYS: tuple[tuple[str, str, str], ...] = (
    ("SKILLS", "top_level_skill", "skill"),
    ("PATTERNS", "top_level_pattern", "pattern"),
    ("skills", "profile_skill", "skill"),
    ("patterns", "profile_pattern", "pattern"),
    ("kernel_only", "kernel_only", "skill"),
    ("CHASSIS", "chassis", "skill"),
)


def _extract_bracket_lists(text: str, key: str) -> list[str]:
    """Return every bare name inside `key::[...]` blocks (exact-case key).

    Handles multi-line arrays by depth-tracking brackets rather than a single-line
    regex, since several agent files wrap long selector arrays across lines
    (including multi-line ``kernel_only::[`` blocks in profile-nested agents).
    """
    items: list[str] = []
    for match in re.finditer(re.escape(key) + r"::\s*\[", text):
        start = match.end()
        depth = 1
        i = start
        while depth > 0 and i < len(text):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
            i += 1
        block = text[start : i - 1]
        items.extend(part.strip() for part in block.split(",") if part.strip())
    return items


def _declared_selectors() -> list[tuple[Path, str, str, str]]:
    """Return (agent_file, selector_type, selector_name, namespace) for every declared selector.

    selector_type distinguishes the four declaration shapes for reporting
    (top_level_skill, top_level_pattern, profile_skill, profile_pattern,
    kernel_only); namespace ("skill" or "pattern") picks the resolver.
    """
    declared: list[tuple[Path, str, str, str]] = []
    for agent_file in sorted(_AGENTS_DIR.glob("*.oct.md")):
        text = agent_file.read_text(encoding="utf-8")
        for key, selector_type, namespace in _SELECTOR_KEYS:
            for name in _extract_bracket_lists(text, key):
                declared.append((agent_file, selector_type, name, namespace))
    return declared


def _skill_resolves(name: str) -> bool:
    return (_SKILLS_DIR / name).is_dir()


def _pattern_resolves(name: str) -> bool:
    return (_PATTERNS_DIR / f"{name}.oct.md").is_file()


_RESOLVERS = {"skill": _skill_resolves, "pattern": _pattern_resolves}

# KNOWN_UNRESOLVED — shrink-only ratchet baseline (see module docstring SCOPE
# section). Each entry is (selector_type, name, declaring_agent_relpath) for a
# selector that does NOT currently resolve to a file in the bundled hub. This
# is the exact 43-entry remainder after the critical-engineer.oct.md fix
# (ce-silent-absent-capabilities): 2 of the original 47 offenders now resolve
# (critical-domain-invariants was ported) and critical-engineer.oct.md itself
# dropped 3 more declarations by operator ruling (observability-validation-
# standards, disaster-recovery-validation, incident-response — removed, not
# replaced). Whether each remaining entry should be authored, ported, or
# pruned is tracked by issue #431 (the open reconcile-vs-migrate question).
#
# https://github.com/elevanaltd/HestAI-MCP/issues/431
#
# DO NOT add entries here to paper over newly-introduced rot — only remove
# entries once the underlying selector resolves or its declaration is deleted
# (test_no_stale_baseline_entries will tell you exactly which line to delete).
KNOWN_UNRESOLVED: frozenset[tuple[str, str, str]] = frozenset(
    {
        (
            "top_level_pattern",
            "ambiguity-trap",
            "src/hestai_mcp/_bundled_hub/library/agents/requirements-steward.oct.md",
        ),
        (
            "top_level_pattern",
            "architectural-drift",
            "src/hestai_mcp/_bundled_hub/library/agents/quality-observer.oct.md",
        ),
        (
            "top_level_pattern",
            "attack-surface-reduction",
            "src/hestai_mcp/_bundled_hub/library/agents/security-specialist.oct.md",
        ),
        (
            "top_level_pattern",
            "cascade-prevention",
            "src/hestai_mcp/_bundled_hub/library/agents/error-architect.oct.md",
        ),
        (
            "top_level_pattern",
            "error-priority-triage",
            "src/hestai_mcp/_bundled_hub/library/agents/error-architect.oct.md",
        ),
        (
            "top_level_pattern",
            "metrics-degradation",
            "src/hestai_mcp/_bundled_hub/library/agents/quality-observer.oct.md",
        ),
        (
            "top_level_pattern",
            "nfr-specification",
            "src/hestai_mcp/_bundled_hub/library/agents/design-architect.oct.md",
        ),
        (
            "top_level_pattern",
            "scope-creep-intervention",
            "src/hestai_mcp/_bundled_hub/library/agents/requirements-steward.oct.md",
        ),
        (
            "top_level_pattern",
            "sensitive-data-flow",
            "src/hestai_mcp/_bundled_hub/library/agents/security-specialist.oct.md",
        ),
        (
            "top_level_pattern",
            "subtractive-ideation",
            "src/hestai_mcp/_bundled_hub/library/agents/ideator.oct.md",
        ),
        (
            "top_level_pattern",
            "systemic-health-assessment",
            "src/hestai_mcp/_bundled_hub/library/agents/principal-engineer.oct.md",
        ),
        (
            "top_level_pattern",
            "test-debt-accumulation",
            "src/hestai_mcp/_bundled_hub/library/agents/quality-observer.oct.md",
        ),
        (
            "top_level_pattern",
            "traceability-chain",
            "src/hestai_mcp/_bundled_hub/library/agents/requirements-steward.oct.md",
        ),
        (
            "top_level_pattern",
            "tradeoff-synthesis",
            "src/hestai_mcp/_bundled_hub/library/agents/edge-optimizer.oct.md",
        ),
        (
            "top_level_pattern",
            "transition-architecture",
            "src/hestai_mcp/_bundled_hub/library/agents/principal-engineer.oct.md",
        ),
        (
            "top_level_pattern",
            "triad-generation",
            "src/hestai_mcp/_bundled_hub/library/agents/ideator.oct.md",
        ),
        (
            "top_level_pattern",
            "zero-trust-validation",
            "src/hestai_mcp/_bundled_hub/library/agents/security-specialist.oct.md",
        ),
        (
            "top_level_skill",
            "algorithmic-complexity-analysis",
            "src/hestai_mcp/_bundled_hub/library/agents/edge-optimizer.oct.md",
        ),
        (
            "top_level_skill",
            "ambiguity-resolution",
            "src/hestai_mcp/_bundled_hub/library/agents/requirements-steward.oct.md",
        ),
        (
            "top_level_skill",
            "api-contract-definition",
            "src/hestai_mcp/_bundled_hub/library/agents/design-architect.oct.md",
        ),
        (
            "top_level_skill",
            "architectural-threat-modeling",
            "src/hestai_mcp/_bundled_hub/library/agents/design-architect.oct.md",
        ),
        (
            "top_level_skill",
            "async-flow-debugging",
            "src/hestai_mcp/_bundled_hub/library/agents/error-architect.oct.md",
        ),
        (
            "top_level_skill",
            "compliance-validation",
            "src/hestai_mcp/_bundled_hub/library/agents/security-specialist.oct.md",
        ),
        (
            "top_level_skill",
            "constraint-inversion",
            "src/hestai_mcp/_bundled_hub/library/agents/ideator.oct.md",
        ),
        (
            "top_level_skill",
            "data-flow-mapping",
            "src/hestai_mcp/_bundled_hub/library/agents/design-architect.oct.md",
        ),
        (
            "top_level_skill",
            "delivery-excellence",
            "src/hestai_mcp/_bundled_hub/library/agents/solution-steward.oct.md",
        ),
        (
            "top_level_skill",
            "dependency-audit",
            "src/hestai_mcp/_bundled_hub/library/agents/security-specialist.oct.md",
        ),
        (
            "top_level_skill",
            "metrics-extraction",
            "src/hestai_mcp/_bundled_hub/library/agents/quality-observer.oct.md",
        ),
        (
            "top_level_skill",
            "nfr-validation",
            "src/hestai_mcp/_bundled_hub/library/agents/principal-engineer.oct.md",
        ),
        (
            "top_level_skill",
            "performance-profiling",
            "src/hestai_mcp/_bundled_hub/library/agents/edge-optimizer.oct.md",
        ),
        (
            "top_level_skill",
            "regression-test-design",
            "src/hestai_mcp/_bundled_hub/library/agents/error-architect.oct.md",
        ),
        (
            "top_level_skill",
            "requirement-process-validation",
            "src/hestai_mcp/_bundled_hub/library/agents/requirements-steward.oct.md",
        ),
        (
            "top_level_skill",
            "requirement-traceability-mapping",
            "src/hestai_mcp/_bundled_hub/library/agents/requirements-steward.oct.md",
        ),
        (
            "top_level_skill",
            "scope-boundary-enforcement",
            "src/hestai_mcp/_bundled_hub/library/agents/requirements-steward.oct.md",
        ),
        (
            "top_level_skill",
            "security-analysis",
            "src/hestai_mcp/_bundled_hub/library/agents/security-specialist.oct.md",
        ),
        (
            "top_level_skill",
            "semantic-drift-analysis",
            "src/hestai_mcp/_bundled_hub/library/agents/requirements-steward.oct.md",
        ),
        (
            "top_level_skill",
            "smartsuite-patterns",
            "src/hestai_mcp/_bundled_hub/library/agents/smartsuite-expert.oct.md",
        ),
        (
            "top_level_skill",
            "stack-trace-synthesis",
            "src/hestai_mcp/_bundled_hub/library/agents/error-architect.oct.md",
        ),
        (
            "top_level_skill",
            "static-analysis-execution",
            "src/hestai_mcp/_bundled_hub/library/agents/quality-observer.oct.md",
        ),
        (
            "top_level_skill",
            "task-decomposition",
            "src/hestai_mcp/_bundled_hub/library/agents/task-decomposer.oct.md",
        ),
        (
            "top_level_skill",
            "technical-debt-quantification",
            "src/hestai_mcp/_bundled_hub/library/agents/principal-engineer.oct.md",
        ),
        (
            "top_level_skill",
            "test-generation",
            "src/hestai_mcp/_bundled_hub/library/agents/universal-test-engineer.oct.md",
        ),
        (
            "top_level_skill",
            "threat-modeling",
            "src/hestai_mcp/_bundled_hub/library/agents/security-specialist.oct.md",
        ),
    }
)


def _unresolved_now() -> set[tuple[str, str, str]]:
    """Return the set of (selector_type, name, agent_relpath) currently unresolved."""
    unresolved: set[tuple[str, str, str]] = set()
    for agent_file, selector_type, name, namespace in _declared_selectors():
        if not _RESOLVERS[namespace](name):
            rel_path = str(agent_file.relative_to(_REPO_ROOT))
            unresolved.add((selector_type, name, rel_path))
    return unresolved


def _fmt(entry: tuple[str, str, str]) -> str:
    selector_type, name, rel_path = entry
    return f"{selector_type}:{name} <- declared by {rel_path}"


@pytest.mark.smoke
@pytest.mark.unit
class TestBundledHubSelectorResolution:
    """Every capability selector declared by a bundled-hub agent must resolve."""

    def test_scan_targets_are_discovered(self) -> None:
        """Guard against a silently-empty scan (moved dirs, renamed suffix) giving false safety."""
        agent_files = sorted(_AGENTS_DIR.glob("*.oct.md"))
        assert agent_files, (
            f"No *.oct.md agent files found under {_AGENTS_DIR} — "
            "the selector-resolution guard would pass vacuously. Verify the path."
        )
        declared = _declared_selectors()
        assert declared, (
            f"No selectors were extracted from {len(agent_files)} agent files across "
            f"the known declaration keys {[k for k, _, _ in _SELECTOR_KEYS]} — the "
            "extraction regex likely broke. The guard would pass vacuously."
        )

    def test_no_new_unresolved_selectors_beyond_baseline(self) -> None:
        """Every currently-unresolved selector must already be in KNOWN_UNRESOLVED — no new rot."""
        unresolved_now = _unresolved_now()
        new_rot = unresolved_now - KNOWN_UNRESOLVED

        assert not new_rot, (
            f"{len(new_rot)} declared capability selector(s) are unresolved but NOT present in "
            "KNOWN_UNRESOLVED. Each of these loads NOTHING at ceremony bind time, silently — the "
            "agent believes it has a capability it never received (see issue #431 and the live "
            "CE-reviewer incident on elevanaltd/hestai-context-mcp PR #165, 2026-09-09). This is "
            "NEW rot introduced since the baseline was captured — resolve it (author the missing "
            "file, port it, or prune the declaration) rather than adding it to KNOWN_UNRESOLVED to "
            "make the test pass.\n"
            "New unresolved selectors (selector_type:name <- declaring agent file):\n"
            + "\n".join(sorted(_fmt(e) for e in new_rot))
        )

    def test_no_stale_baseline_entries(self) -> None:
        """Every KNOWN_UNRESOLVED entry must still be unresolved — baseline may only shrink."""
        unresolved_now = _unresolved_now()
        stale = KNOWN_UNRESOLVED - unresolved_now

        assert not stale, (
            f"{len(stale)} KNOWN_UNRESOLVED entr{'y is' if len(stale) == 1 else 'ies are'} stale: "
            "the selector now resolves to a file, or its declaration was removed/renamed. The "
            "baseline is a shrink-only ratchet (see module docstring SCOPE) — delete these exact "
            "entries from KNOWN_UNRESOLVED in tests/unit/governance/test_bundled_hub_selector_resolution.py:\n"
            + "\n".join(sorted(_fmt(e) for e in stale))
        )
