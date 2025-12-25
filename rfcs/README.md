# RFC (Request for Comments) Directory

This directory contains proposals and experimental designs for the HestAI MCP system.

## Active RFCs

### [RFC-0031: GitHub Issue-Based Document Numbering](active/0031-github-issue-based-numbering.md)
**Status**: PROPOSED
**GitHub Issue**: [#31](https://github.com/elevanaltd/HestAI-MCP/issues/31)
Adopt GitHub Issue numbers as canonical identifiers for ADRs and RFCs to eliminate sequence clash conflicts in multi-worktree environments. This RFC itself demonstrates the pattern.

### [RFC-0037: Context Registry](active/0037-context-registry.md)
**Status**: EXPERIMENTAL
**GitHub Issue**: [#37](https://github.com/elevanaltd/HestAI-MCP/issues/37)
Proposes a centralized context registry for managing session and agent contexts across the HestAI ecosystem.

### [RFC-0038: Hub as Application](active/0038-hub-as-application.md)
**Status**: PROPOSED
**GitHub Issue**: [#38](https://github.com/elevanaltd/HestAI-MCP/issues/38)
Transform the HestAI Hub from static governance files into an active application with project registry, push capability, and version management.

### [RFC-0039: Agent Master Forge](active/0039-agent-master-forge.oct.md)
**Status**: PROPOSED
**GitHub Issue**: [#39](https://github.com/elevanaltd/HestAI-MCP/issues/39)
Agent forging methodology and patterns library.

### [RFC-0040: Agent Patterns Library](active/0040-agent-patterns-library.oct.md)
**Status**: PROPOSED
**GitHub Issue**: [#40](https://github.com/elevanaltd/HestAI-MCP/issues/40)
Reusable agent pattern templates and archetypes.

### [RFC-0054: Universal Coordination Hub](active/0054-universal-coordination-hub.md)
**Status**: DRAFT
**GitHub Issue**: [#54](https://github.com/elevanaltd/HestAI-MCP/issues/54)
A persistent, holistic coordination layer outside repository snapshots for cross-repository orchestration context.

## Purpose

- **Experimental Designs**: Ideas and prototypes that aren't ready for production
- **Architecture Proposals**: Significant system changes requiring review
- **Feature Specifications**: Detailed plans for new features before implementation

## Structure

```
rfcs/
├── README.md                 # This file
├── 0000-template.md          # Template for new RFCs
├── active/                   # RFCs under active consideration
│   ├── 0031-github-issue-based-numbering.md  # Issue-based numbering RFC
│   ├── 0037-context-registry.md              # Context registry
│   ├── 0038-hub-as-application.md            # Hub as application
│   ├── 0039-agent-master-forge.oct.md        # Agent forging
│   ├── 0040-agent-patterns-library.oct.md    # Pattern library
│   └── 0054-universal-coordination-hub.md    # Universal hub
├── implemented/              # Accepted and implemented RFCs
│   └── (empty - none yet)
└── experimental/             # Prototypes and proof-of-concepts
    └── 0001-context-registry/    # Experimental registry code (legacy)
```

## Process

1. **Draft**: Create RFC in `active/` using the template
2. **Review**: Discuss and refine the proposal
3. **Decision**: Accept, reject, or defer
4. **Implementation**: Move to `implemented/` once built
5. **Experimental**: Use `experimental/` for code prototypes

## RFC States

- **DRAFT**: Initial proposal being written
- **PROPOSED**: Ready for discussion
- **EXPERIMENTAL**: Has proof-of-concept code
- **ACCEPTED**: Approved for implementation
- **REJECTED**: Not moving forward
- **DEFERRED**: Postponed for future consideration
- **IMPLEMENTED**: Completed and merged

## Benefits

- Keeps main codebase clean
- Enables collaborative design review
- Maintains history of architectural decisions
- Separates "what if" from "what is"

## Experimental Code Policy

- Experimental implementations go in `rfcs/experimental/`
- Not included in production builds
- Can be gitignored if desired
- Prototypes should be self-contained
- Deleted after RFC decision (accept or reject)

## When to Use RFCs

- Breaking changes to existing functionality
- New major features or subsystems
- Significant architectural changes
- External API modifications
- Experimental ideas needing discussion

## Creating a New RFC

### New Process (Issue-Based Numbering)

As of RFC-0031, new RFCs use GitHub Issue numbers to prevent sequence clashes:

1. **Create GitHub Issue** with title "RFC: [Topic]" and label `rfc`
2. **Note the issue number** (e.g., #31)
3. **Create document** as `active/{ISSUE_NUMBER:04d}-title.md` (e.g., `0031-title.md`)
4. **Add GitHub Issue link** in frontmatter
5. **Fill out all sections** using `0000-template.md` as guide
6. **Update this README** to list your RFC
7. **Submit PR** referencing the issue

### Legacy Process (Pre-RFC-0031)

For reference, the original process was:
1. Copy `0000-template.md` to `active/NNNN-title.md` (manually pick next number)
2. Fill out all sections completely
3. Submit PR for discussion

Legacy RFCs have been migrated to issue-based numbering (0037-0040).
