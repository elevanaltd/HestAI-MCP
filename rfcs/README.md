# RFC (Request for Comments) Directory

This directory contains proposals and experimental designs for the HestAI MCP system.

## Active RFCs

### [RFC-0001: Context Registry](active/0001-context-registry.md)
**Status**: EXPERIMENTAL
Proposes a centralized context registry for managing session and agent contexts across the HestAI ecosystem.

### [RFC-0002: Hub as Application](active/0002-hub-as-application.md)
**Status**: PROPOSED
Transform the HestAI Hub from static governance files into an active application with project registry, push capability, and version management.

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
│   ├── 0001-context-registry.md
│   └── 0002-hub-as-application.md
├── implemented/              # Accepted and implemented RFCs
│   └── (empty - none yet)
└── experimental/             # Prototypes and proof-of-concepts
    └── 0001-context-registry/    # Experimental registry code
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

1. Copy `0000-template.md` to `active/NNNN-title.md`
2. Fill out all sections completely
3. Submit PR for discussion
4. Optional: Add experimental code to `experimental/NNNN-title/`
5. Update this README to list your RFC
