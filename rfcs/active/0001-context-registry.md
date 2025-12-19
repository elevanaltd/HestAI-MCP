# RFC-0001: Context Registry for Intelligent Document Filtering

- **Status**: Draft
- **Author**: Context Steward Team
- **Created**: 2025-12-19
- **Updated**: 2025-12-19

## Summary

Implement a registry-based document categorization system that reduces token usage by 60-70% through intelligent filtering during agent clock-in. Agents would only receive documents relevant to their role, phase, and focus area.

## Motivation

Currently, the `clock_in` tool returns all context files from `.hestai/context/`, leading to:
- **Token waste**: Agents receive 5000-10000 tokens of context when they may only need 1000-3000
- **Cognitive overhead**: Irrelevant documents confuse agents
- **No prioritization**: All documents treated equally regardless of importance

## Detailed Design

### Registry Schema

Documents would be categorized as:
- **Core**: Always visible (North Star, Project Context)
- **Operational**: Active work state (Checklist, History)
- **Governance**: Standards and methodology
- **Auxiliary**: Reference material available on demand

### Visibility Rules

Each document entry contains:
```json
{
  "path": ".hestai/context/PROJECT-CHECKLIST.oct.md",
  "category": "operational",
  "visibility": "role_specific",
  "priority": 8,
  "roles": ["implementation-lead", "workspace-architect"],
  "phases": ["B2", "B3", "B4"],
  "tags": ["checklist", "tasks"]
}
```

### Integration

The enhanced `clock_in` would:
1. Load the registry from `.hestai/registry/context-registry.json`
2. Filter documents based on agent role and detected phase
3. Return categorized paths (core/required/optional)
4. Provide visibility metadata for transparency

## Examples

When `implementation-lead` clocks in during B2:
```python
result = clock_in_with_registry(
    role="implementation-lead",
    working_dir="/project",
    focus="b2-implementation"
)

# Returns:
{
    "context_paths": {
        "core": ["PROJECT-NORTH-STAR.oct.md", "PROJECT-CONTEXT.oct.md"],
        "required": ["PROJECT-CHECKLIST.oct.md", "BUILD-STANDARDS.md"],
        "optional": ["context-negatives.oct.md"]
    },
    "visibility_metadata": {
        "total_available": 15,
        "loaded": 4,
        "filtered_out": 10,
        "reason": "Filtered for implementation-lead in phase B2"
    }
}
```

## Drawbacks

- **Maintenance burden**: Registry needs updating when documents added
- **Complexity**: Additional system to understand and maintain
- **Migration**: Existing projects would need registry creation

## Alternatives

1. **Hardcoded filtering**: Less flexible, harder to maintain
2. **Agent self-selection**: Agents choose what to load (unreliable)
3. **No filtering**: Continue with current approach (wasteful)

## Unresolved Questions

- Should the registry be auto-generated or manually maintained?
- How to handle app-specific contexts in monorepos?
- Should we support regex patterns for document matching?

## Implementation Plan

- [ ] Phase 1: Create registry schema and specification
- [ ] Phase 2: Build registry management tools
- [ ] Phase 3: Integrate with existing `clock_in`
- [ ] Phase 4: Migration tools for existing projects

## Experimental Code

See `rfcs/experimental/context-registry/` for prototype implementation including:
- `context-registry-spec.oct.md`: Full specification
- `context_registry.py`: Registry implementation
- `clock_in_enhanced.py`: Integration prototype
