# RFC (Request for Comments) Directory

This directory contains proposals and experimental designs for the HestAI MCP system.

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
│   └── NNNN-feature-name.md
├── implemented/              # Accepted and implemented RFCs
│   └── NNNN-feature-name.md
└── experimental/             # Prototypes and proof-of-concepts
    └── context-registry/     # Example experimental feature
```

## Process

1. **Draft**: Create RFC in `active/` using the template
2. **Review**: Discuss and refine the proposal
3. **Decision**: Accept, reject, or defer
4. **Implementation**: Move to `implemented/` once built
5. **Experimental**: Use `experimental/` for code prototypes

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

## When to Use RFCs

- Breaking changes to existing functionality
- New major features or subsystems
- Significant architectural changes
- External API modifications
- Experimental ideas needing discussion
