# Context Registry Experimental Implementation

This directory contains the experimental prototype for the Context Registry system proposed in RFC-0001.

## Contents

- `context-registry-spec.oct.md`: Full OCTAVE specification
- `context_registry.py`: Python implementation of the registry
- `clock_in_enhanced.py`: Enhanced clock-in with registry integration

## Status

**EXPERIMENTAL** - This code is not production-ready and should not be deployed.

## Testing

To test the registry locally:

```python
from context_registry import ContextRegistry

registry = ContextRegistry(working_dir)
paths = registry.filter_for_agent(
    role="implementation-lead",
    phase="B2"
)
```

## Next Steps

If this RFC is approved:
1. Move implementation to main codebase
2. Add comprehensive tests
3. Create migration tools
4. Update documentation
