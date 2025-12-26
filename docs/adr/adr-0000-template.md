# ADR-0000: [Decision Title]

- **Status**: [Draft|Proposed|Accepted|Implemented|Superseded]
- **Type**: ADR
- **Author**: [Your Name or Agent Role]
- **Created**: [YYYY-MM-DD]
- **Updated**: [YYYY-MM-DD]
- **GitHub Issue**: [#N](https://github.com/elevanaltd/HestAI-MCP/issues/N)
- **Phase**: [D0|D1|D2|D3|B0|B1|B2|B3|B4|B5]
- **Supersedes**: (none or ADR-XXXX)
- **Superseded-By**: (none or ADR-XXXX)
- **From-RFC**: (none or RFC-XXXX if this ADR ratifies an RFC)

## Context

What is the issue that we're seeing that is motivating this decision or change?

Describe the forces at play (technical, business, social, etc.). What constraints exist? What options were considered?

## Decision

What is the change that we're proposing and/or doing?

State the decision clearly and unambiguously. Use active voice: "We will..." or "The system shall..."

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive

- List benefits and improvements

### Negative

- List costs, risks, or new constraints introduced

### Neutral

- List changes that are neither clearly positive nor negative

## Related Documents

- **RFC**: [RFC-XXXX](../../rfcs/active/XXXX-title.md) (if this ADR ratifies an RFC)
- **ADRs**: Links to related architectural decisions
- **Issues**: Links to relevant GitHub Issues

---

## How to Use This Template

1. **Create a GitHub Issue** with title "ADR: [Your Topic]" and label `adr`
2. **Note the issue number** (e.g., #42)
3. **Copy this template** to `docs/adr/adr-{ISSUE_NUMBER:04d}-your-topic.md` (e.g., `adr-0042-your-topic.md`)
4. **Update the header** to use the issue number: `# ADR-0042: Your Topic`
5. **Link the issue** in the frontmatter above
6. **Set Status to Draft** while writing
7. **Submit PR** referencing the issue
8. **Update Status to Accepted** when merged

### Status Lifecycle

```
Draft → Proposed → Accepted → Implemented → (optionally) Superseded
```

- **Draft**: Initial writing, not ready for review
- **Proposed**: Ready for discussion and review
- **Accepted**: Decision made, ready for implementation
- **Implemented**: Decision has been built and shipped
- **Superseded**: Replaced by a newer ADR (link in Superseded-By)
