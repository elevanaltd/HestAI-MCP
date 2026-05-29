"""
Contract tests for content-aware review-depth escalation via bitemporal set-union.

Feature (GitHub issue #412): a change can declare "this needs deeper review than
the diff-shape suggests" in a way the org-shared gate honours. Declarations are
extracted from FOUR sources and unioned (escalation-only):

    Required_Roles = Diff_Roles ∪ Base_Roles ∪ Head_Roles ∪ PR_Body_Roles

then intersected with ALLOWED_ESCALATION_ROLES before enforcement.

Schema (LOCKED — do not invent syntax):
- Canonical field: REQUIRED_REVIEWERS (OCTAVE block field + HTML-comment markers).
- HTML-comment markers (plain .md + PR body):
    <!-- review-requirements: [TMG, CRS, CE, CIV, SR] -->
    <!-- review-tier: TIER_3_CRITICAL: reason -->
- Whitelist: ALLOWED_ESCALATION_ROLES = VALID_ROLES - {IL, HO}
            = {TMG, CRS, CE, CIV, PE, SR}

Source of truth: issue #412 test corpus + comments 4569263110 / 4569387061.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import validate_review  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _f(path: str, added: int = 1, deleted: int = 0, status: str = "M") -> dict:
    """Build a changed-file dict matching get_changed_files() output."""
    return {
        "path": path,
        "added": added,
        "deleted": deleted,
        "total_changed": added + deleted,
        "status": status,
    }


# ---------------------------------------------------------------------------
# 0. ALLOWED_ESCALATION_ROLES is derived, not hardcoded
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.behavior
class TestAllowedEscalationRoles:
    """The whitelist must be derived from review_formats.VALID_ROLES - {IL, HO}."""

    def test_whitelist_value(self) -> None:
        assert {
            "TMG",
            "CRS",
            "CE",
            "CIV",
            "PE",
            "SR",
        } == validate_review.ALLOWED_ESCALATION_ROLES

    def test_whitelist_excludes_self_review_roles(self) -> None:
        assert "IL" not in validate_review.ALLOWED_ESCALATION_ROLES
        assert "HO" not in validate_review.ALLOWED_ESCALATION_ROLES

    def test_whitelist_derived_from_valid_roles(self) -> None:
        """Must equal VALID_ROLES - {IL, HO}, not a hardcoded literal."""
        derived = set(validate_review._VALID_ROLES) - {"IL", "HO"}
        assert derived == validate_review.ALLOWED_ESCALATION_ROLES


# ---------------------------------------------------------------------------
# 1. The single extractor: _parse_review_declaration
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.behavior
class TestParseReviewDeclaration:
    """_parse_review_declaration(text) -> {tier?, roles?, reason?, source}."""

    def test_html_comment_review_requirements(self) -> None:
        decl = validate_review._parse_review_declaration(
            "<!-- review-requirements: [TMG, CRS, CE, CIV, SR] -->"
        )
        assert decl["roles"] == {"TMG", "CRS", "CE", "CIV", "SR"}

    def test_html_comment_review_tier(self) -> None:
        decl = validate_review._parse_review_declaration(
            "<!-- review-tier: TIER_3_CRITICAL: governance ADR -->"
        )
        assert decl["tier"] == "TIER_3_CRITICAL"
        # TIER_3_CRITICAL maps through tier->role table to a set including CIV
        assert "CIV" in decl["roles"]
        assert decl["reason"] == "governance ADR"

    def test_octave_required_reviewers_block_field(self) -> None:
        """OCTAVE REQUIRED_REVIEWERS::"{CE, CRS, SR}" override field."""
        text = "===ADR===\n" "META:\n" "  TYPE::RULE\n" 'REQUIRED_REVIEWERS::"{CE, CRS, SR}"\n'
        decl = validate_review._parse_review_declaration(text)
        assert decl["roles"] == {"CE", "CRS", "SR"}

    def test_frontmatter_review_requirements(self) -> None:
        """YAML-frontmatter declaration per the issue's _parse_review_declaration spec."""
        text = "---\n" "review-requirements: [CE, CRS]\n" "---\n" "# Some doc\n"
        decl = validate_review._parse_review_declaration(text)
        assert decl["roles"] == {"CE", "CRS"}

    def test_no_declaration_returns_empty_roles(self) -> None:
        decl = validate_review._parse_review_declaration("Just some prose, no markers.")
        assert not decl.get("roles")

    def test_malformed_declaration_does_not_crash(self) -> None:
        """Malformed markers must not raise — return empty/partial, never crash."""
        decl = validate_review._parse_review_declaration("<!-- review-requirements: [TMG, , -->")
        # No exception; whatever parsed is a set (possibly empty)
        assert isinstance(decl.get("roles", set()), set)


# ---------------------------------------------------------------------------
# 2. Bitemporal collection: _collect_bitemporal_declarations
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.behavior
class TestCollectBitemporalDeclarations:
    """Union declarations from PR body + base blob + head blob per changed file."""

    def test_pr_body_declaration(self, monkeypatch) -> None:
        monkeypatch.setattr(validate_review, "_git_show_file", lambda sha, path: None)
        roles, prov = validate_review._collect_bitemporal_declarations(
            files=[_f("docs/ADR.md")],
            pr_body="<!-- review-requirements: [SR] -->",
            base_sha="base",
            head_sha="head",
        )
        assert "SR" in roles
        assert "PR_BODY" in prov["SR"]

    def test_head_blob_declaration(self, monkeypatch) -> None:
        def fake_show(sha, path):
            if sha == "head":
                return "<!-- review-requirements: [TMG] -->"
            return None

        monkeypatch.setattr(validate_review, "_git_show_file", fake_show)
        roles, prov = validate_review._collect_bitemporal_declarations(
            files=[_f("docs/ADR.md")],
            pr_body="",
            base_sha="base",
            head_sha="head",
        )
        assert "TMG" in roles
        assert "HEAD" in prov["TMG"]
        assert "BASE" not in prov.get("TMG", set())

    def test_base_only_declaration_retained(self, monkeypatch) -> None:
        """RATCHET core: role declared in BASE but absent from HEAD is retained."""

        def fake_show(sha, path):
            if sha == "base":
                return "<!-- review-requirements: [CRS] -->"
            return ""  # HEAD blob exists but has no declaration

        monkeypatch.setattr(validate_review, "_git_show_file", fake_show)
        roles, prov = validate_review._collect_bitemporal_declarations(
            files=[_f("docs/ADR.md")],
            pr_body="",
            base_sha="base",
            head_sha="head",
        )
        assert "CRS" in roles, "BASE-declared role must survive (set-union cannot subtract)"
        assert prov["CRS"] == {"BASE"}, "BASE-only role must show BASE provenance only"

    def test_missing_base_blob_no_crash(self, monkeypatch) -> None:
        """New file (no BASE blob): _git_show_file returns None — union uses HEAD only."""

        def fake_show(sha, path):
            if sha == "head":
                return "<!-- review-requirements: [CE] -->"
            return None  # base blob missing (new file)

        monkeypatch.setattr(validate_review, "_git_show_file", fake_show)
        roles, prov = validate_review._collect_bitemporal_declarations(
            files=[_f("docs/NEW.md", status="A")],
            pr_body="",
            base_sha="base",
            head_sha="head",
        )
        assert roles == {"CE"}
        assert prov["CE"] == {"HEAD"}

    def test_out_of_whitelist_role_dropped(self, monkeypatch) -> None:
        """[GOD_MODE] is outside ALLOWED_ESCALATION_ROLES -> dropped, non-fatal."""
        monkeypatch.setattr(validate_review, "_git_show_file", lambda sha, path: None)
        roles, prov = validate_review._collect_bitemporal_declarations(
            files=[_f("docs/ADR.md")],
            pr_body="<!-- review-requirements: [GOD_MODE, CRS] -->",
            base_sha="base",
            head_sha="head",
        )
        assert "GOD_MODE" not in roles
        assert "CRS" in roles

    def test_il_ho_dropped_as_self_review_roles(self, monkeypatch) -> None:
        """IL and HO are self-review roles, not escalation-declarable -> dropped."""
        monkeypatch.setattr(validate_review, "_git_show_file", lambda sha, path: None)
        roles, _prov = validate_review._collect_bitemporal_declarations(
            files=[_f("docs/ADR.md")],
            pr_body="<!-- review-requirements: [IL, HO, SR] -->",
            base_sha="base",
            head_sha="head",
        )
        assert roles == {"SR"}


# ---------------------------------------------------------------------------
# 3. classify_pr_facets integration — the 10-test frozen corpus
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.behavior
class TestClassifyPrFacetsEscalation:
    """classify_pr_facets must union declared roles BEFORE both early returns."""

    # --- Corpus #1: regression guard ---
    def test_diff_only_no_declaration_unchanged(self) -> None:
        """Diff-only PR, no declaration -> unchanged behaviour."""
        files = [_f("src/core.py", added=50, deleted=20)]
        facets, roles, tier, _ = validate_review.classify_pr_facets(files)
        assert roles == {"CE", "CRS", "TMG"}
        assert tier == "TIER_2_STANDARD"

    def test_diff_only_exempt_still_tier_0(self) -> None:
        """Pure .md with no declaration still TIER_0_EXEMPT (regression guard)."""
        files = [_f("docs/README.md", added=10, deleted=5)]
        facets, roles, tier, _ = validate_review.classify_pr_facets(files)
        assert tier == "TIER_0_EXEMPT"
        assert roles == set()

    # --- Corpus #3: .oct.md REQUIRED_REVIEWERS override escalates ---
    def test_octave_required_reviewers_escalates(self) -> None:
        """.oct.md declaring REQUIRED_REVIEWERS escalates to declared roles."""
        files = [_f("docs/governance/POLICY.oct.md", added=5, deleted=2)]
        facets, roles, tier, _ = validate_review.classify_pr_facets(
            files, declared_roles={"CIV", "CE", "CRS", "SR", "TMG"}
        )
        assert {"CIV", "CE", "CRS", "SR", "TMG"}.issubset(roles)
        assert tier == "TIER_3_CRITICAL"  # CIV present

    # --- Corpus #4: PR body declares roles ---
    def test_declared_roles_union_with_diff(self) -> None:
        """Declared roles union with diff-computed roles (escalation-only ADD)."""
        files = [_f("src/core.py", added=50, deleted=20)]  # diff -> {CE, CRS, TMG}
        facets, roles, tier, _ = validate_review.classify_pr_facets(
            files, declared_roles={"CIV", "SR"}
        )
        # union: diff {CE, CRS, TMG} ∪ declared {CIV, SR}
        assert roles == {"CE", "CRS", "TMG", "CIV", "SR"}
        assert tier == "TIER_3_CRITICAL"

    # --- Corpus #9 KEYSTONE: all-exempt-escalation ---
    def test_all_exempt_with_declaration_does_not_return_tier_0(self) -> None:
        """KEYSTONE (elevana-studio #868): docs-only PR carrying a declaration
        escalates to the declared role set and does NOT return TIER_0_EXEMPT.

        This proves the union runs BEFORE the `:301 if not facets` early return.
        """
        files = [_f("decisions/ADR-HO-AUTH.md", added=40, deleted=0, status="A")]
        facets, roles, tier, _ = validate_review.classify_pr_facets(
            files, declared_roles={"TMG", "CRS", "CE", "CIV", "SR"}
        )
        assert tier != "TIER_0_EXEMPT", "all-exempt PR with declaration must NOT be exempt"
        assert roles == {"TMG", "CRS", "CE", "CIV", "SR"}
        assert tier == "TIER_3_CRITICAL"

    # --- Corpus #10 KEYSTONE: declaration suppresses self-review ---
    def test_declaration_suppresses_tier_1_self(self) -> None:
        """KEYSTONE: a declaration on an otherwise TIER_1_SELF-eligible change
        suppresses self-review (does not short-circuit to TIER_1_SELF).

        Proves the union runs BEFORE the `:319 TIER_1_SELF` early return.
        """
        files = [_f("src/config.py", added=3, deleted=1)]  # would be TIER_1_SELF
        facets, roles, tier, _ = validate_review.classify_pr_facets(files, declared_roles={"CRS"})
        assert tier != "TIER_1_SELF", "declaration must suppress self-review short-circuit"
        assert "CRS" in roles

    def test_no_declaration_still_tier_1_self(self) -> None:
        """Without a declaration, the TIER_1_SELF short-circuit is preserved."""
        files = [_f("src/config.py", added=3, deleted=1)]
        facets, roles, tier, _ = validate_review.classify_pr_facets(files)
        assert tier == "TIER_1_SELF"

    # --- Escalation-only structural property ---
    def test_declaration_cannot_subtract_diff_roles(self) -> None:
        """Declaring a SMALLER set never removes diff-computed roles (escalation-only)."""
        files = [_f("src/core.py", added=50, deleted=20)]  # diff -> {CE, CRS, TMG}
        facets, roles, tier, _ = validate_review.classify_pr_facets(
            files, declared_roles={"SR"}  # declares only SR
        )
        # diff roles are retained; SR is added
        assert {"CE", "CRS", "TMG"}.issubset(roles)
        assert "SR" in roles


# ---------------------------------------------------------------------------
# 4. End-to-end through the bitemporal collector (corpus #2, #5, #6, #7, #8)
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.behavior
class TestEndToEndEscalation:
    """Full path: collector -> classify, exercising the locked HTML-comment markers."""

    # --- Corpus #2: markdown-only PR with review-tier marker escalates ---
    def test_markdown_only_review_tier_escalates(self, monkeypatch) -> None:
        def fake_show(sha, path):
            if sha == "head":
                return "<!-- review-tier: TIER_3_CRITICAL: governance ADR -->"
            return None

        monkeypatch.setattr(validate_review, "_git_show_file", fake_show)
        files = [_f("docs/ADR.md", added=40, deleted=0, status="A")]
        declared, _prov = validate_review._collect_bitemporal_declarations(
            files=files, pr_body="", base_sha="base", head_sha="head"
        )
        facets, roles, tier, _ = validate_review.classify_pr_facets(files, declared_roles=declared)
        assert tier != "TIER_0_EXEMPT"
        assert "CIV" in roles  # TIER_3 maps to a CIV-bearing set
        assert tier == "TIER_3_CRITICAL"

    # --- Corpus #5 KEYSTONE: ratchet ---
    def test_ratchet_base_declaration_removed_in_head_retained(self, monkeypatch) -> None:
        """KEYSTONE: declaration in BASE, removed in HEAD -> role RETAINED.

        Proves escalation-only is a structural property of set-union, not a rule.
        """

        def fake_show(sha, path):
            if sha == "base":
                return "<!-- review-requirements: [CE, CRS, TMG, CIV, SR] -->"
            return ""  # HEAD: declaration deleted

        monkeypatch.setattr(validate_review, "_git_show_file", fake_show)
        files = [_f("decisions/ADR.md", added=2, deleted=8)]
        declared, prov = validate_review._collect_bitemporal_declarations(
            files=files, pr_body="", base_sha="base", head_sha="head"
        )
        assert declared == {"CE", "CRS", "TMG", "CIV", "SR"}
        for role in declared:
            assert prov[role] == {"BASE"}, f"{role} attempted-reduction must show BASE only"
        facets, roles, tier, _ = validate_review.classify_pr_facets(files, declared_roles=declared)
        assert tier == "TIER_3_CRITICAL"

    # --- Corpus #6: malformed declaration falls back, no crash ---
    def test_malformed_declaration_falls_back_to_diff_floor(self, monkeypatch) -> None:
        def fake_show(sha, path):
            if sha == "head":
                return "<!-- review-requirements: [ -->"  # malformed
            return None

        monkeypatch.setattr(validate_review, "_git_show_file", fake_show)
        files = [_f("src/core.py", added=50, deleted=20)]
        declared, _prov = validate_review._collect_bitemporal_declarations(
            files=files, pr_body="", base_sha="base", head_sha="head"
        )
        # malformed -> no extra roles; declared is empty (no crash)
        facets, roles, tier, _ = validate_review.classify_pr_facets(files, declared_roles=declared)
        # falls back to diff-computed floor for a .py file
        assert roles == {"CE", "CRS", "TMG"}

    # --- Corpus #7: out-of-whitelist role dropped, gate computes without it ---
    def test_god_mode_dropped_gate_computes_without_it(self, monkeypatch) -> None:
        def fake_show(sha, path):
            if sha == "head":
                return "<!-- review-requirements: [GOD_MODE] -->"
            return None

        monkeypatch.setattr(validate_review, "_git_show_file", fake_show)
        files = [_f("docs/ADR.md", added=10, deleted=0)]
        declared, _prov = validate_review._collect_bitemporal_declarations(
            files=files, pr_body="", base_sha="base", head_sha="head"
        )
        assert declared == set()
        facets, roles, tier, _ = validate_review.classify_pr_facets(files, declared_roles=declared)
        # docs-only + no valid declared roles -> still exempt (GOD_MODE dropped non-fatally)
        assert tier == "TIER_0_EXEMPT"

    # --- Corpus #8: new file, no BASE blob, union on HEAD only ---
    def test_new_file_no_base_blob_union_head_only(self, monkeypatch) -> None:
        def fake_show(sha, path):
            if sha == "head":
                return "<!-- review-requirements: [SR] -->"
            return None  # no base blob

        monkeypatch.setattr(validate_review, "_git_show_file", fake_show)
        files = [_f("docs/NEW-ADR.md", added=30, deleted=0, status="A")]
        declared, prov = validate_review._collect_bitemporal_declarations(
            files=files, pr_body="", base_sha="base", head_sha="head"
        )
        assert declared == {"SR"}
        assert prov["SR"] == {"HEAD"}


# ---------------------------------------------------------------------------
# 5. Provenance emitted in JSON output
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.behavior
class TestProvenanceInJsonOutput:
    """_emit_json_summary must include a per-role provenance source map."""

    def test_emit_json_includes_provenance(self, capsys) -> None:
        import json

        validate_review._emit_json_summary(
            tier="TIER_3_CRITICAL",
            reason="escalated",
            reviewers=["CRS", "TMG"],
            status="fail",
            required_count=2,
            found_count=0,
            sha="abc1234",
            provenance={"CRS": ["HEAD", "BASE"], "TMG": ["DIFF"]},
        )
        out = capsys.readouterr().out
        marker = "<!-- REVIEW_GATE_JSON:"
        assert marker in out
        payload = out.split(marker, 1)[1].split(" -->", 1)[0]
        data = json.loads(payload)
        assert data["provenance"]["CRS"] == ["HEAD", "BASE"]
        assert data["provenance"]["TMG"] == ["DIFF"]

    def test_emit_json_provenance_optional(self, capsys) -> None:
        """Backward compat: omitting provenance must not crash; defaults to empty."""
        validate_review._emit_json_summary(
            tier="TIER_2_STANDARD",
            reason="r",
            reviewers=["CE"],
            status="pass",
            required_count=1,
            found_count=1,
            sha="abc1234",
        )
        out = capsys.readouterr().out
        assert "<!-- REVIEW_GATE_JSON:" in out
