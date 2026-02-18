# ADR-0240: SYS::/PROD:: Namespace Resolution for Immutable References

- **Status**: Accepted
- **Type**: ADR
- **Author**: holistic-orchestrator
- **Created**: 2026-02-18
- **Updated**: 2026-02-18
- **GitHub Issue**: [#240](https://github.com/elevanaltd/hestai-mcp/issues/240)
- **Phase**: B1
- **Supersedes**: (none)
- **Superseded-By**: (none)
- **From-RFC**: (none)

## Context

The HestAI governance system defines two independent North Stars, each with six immutables (I1-I6):

| Index | System North Star (SYS) | Product North Star (PROD) |
|-------|------------------------|---------------------------|
| I1 | Verifiable Behavioral Specification First | Persistent Cognitive Continuity |
| I2 | Phase-Gated Progression | Structural Integrity Priority |
| I3 | Human Primacy | Dual Layer Authority |
| I4 | Discoverable Artifact Persistence | Freshness Verification |
| I5 | Quality Verification Before Progression | Odyssean Identity Binding |
| I6 | Explicit Accountability | Universal Scope |

Bare citations like `CITE[I2]` or `violates I4` are ambiguous when both North Stars are in scope. An agent reading `CITE[I2]` cannot determine whether Phase-Gated Progression (SYS) or Structural Integrity Priority (PROD) is intended. This creates enforcement drift: agents may escalate or block based on the wrong constraint.

This collision was identified during multi-model debate (`2026-02-14-namespace-resolution`) and motivated PR #238, subsequently split into focused issues (#240 governance, #241 tooling).

## Decision

We will adopt a two-namespace prefix convention to disambiguate immutable references:

- **`SYS::`** — system-level governance documents (Constitution, System North Star, system ADRs)
- **`PROD::`** — product-level context documents (Product North Stars, product ADRs, workflow docs)

**Rules:**

1. When citing an immutable where cross-namespace ambiguity exists, use the fully-qualified form: `SYS::I2`, `PROD::I4`.
2. Within a single-namespace context (inside a SYS document citing only SYS immutables), the short form (`I2`) remains valid when unambiguous.
3. Governance documents declare their namespace in the META section: `NAMESPACE::SYS` or `NAMESPACE::PROD`.
4. Existing documents without a declaration are assumed SYS:: (system governance) or PROD:: (product context) by document type. The declaration should be added on next edit.

**Constitutional amendment:** §3.5::NAMESPACE_RESOLUTION has been added to `src/hestai_mcp/_bundled_hub/CONSTITUTION.md` encoding these rules.

**Migration:** See `src/hestai_mcp/_bundled_hub/governance/migration/NAMESPACE-MIGRATION-GUIDE.md` for step-by-step adoption instructions.

## Consequences

### Positive

- Enforcement protocols are unambiguous: `CITE[SYS::I2]` cannot be confused with `CITE[PROD::I2]`
- Agents anchoring against either North Star can cite constraints without ambiguity
- The collision is resolved at the constitutional level — lower documents inherit the rule
- Migration is additive: existing short-form citations remain valid within their namespace context

### Negative

- Cross-namespace citations become verbose (`SYS::I2` vs `I2`)
- Documents without namespace declarations require a one-time editorial pass to add `NAMESPACE::` declarations

### Neutral

- The two-namespace model is intentionally minimal. Future namespaces (e.g., `COMPONENT::`) are not precluded but require a separate amendment
- Tooling to validate namespace citations (e.g., lint for bare `I#` references in cross-namespace contexts) is deferred to issue #241

## Related Documents

- **ADRs**: [ADR-0033](adr-0033-dual-layer-context-architecture.md) (Dual-Layer Context Architecture — establishes SYS/PROD separation)
- **Constitutional Amendment**: `src/hestai_mcp/_bundled_hub/CONSTITUTION.md §3.5`
- **Migration Guide**: `src/hestai_mcp/_bundled_hub/governance/migration/NAMESPACE-MIGRATION-GUIDE.md`
- **Issues**: [#240](https://github.com/elevanaltd/hestai-mcp/issues/240) (this issue), [#241](https://github.com/elevanaltd/hestai-mcp/issues/241) (namespace tooling)
