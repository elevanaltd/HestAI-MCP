---
name: mcp-tools
description: MCP tool implementation patterns for HestAI including tool structure, session tools, and shared utilities
allowed-tools: "*"
triggers:
  - MCP tool
  - clock_in
  - clock_out
  - odyssean_anchor
  - mcp server
  - tool implementation
  - hestai context
  - session management
  - path_resolution
  - fast_layer
---

# MCP Tool Implementation

## Tool Structure

Tools live in `src/hestai_mcp/mcp/tools/` and return dicts:

```python
async def my_tool_async(
    required_param: str,
    optional_param: str | None = None,
) -> dict[str, Any]:
    """Tool description."""
    # Validate inputs first
    validated = validate_param(required_param)
    # Implementation
    return {"status": "success", "data": result}
```

## Session Tools

- `clock_in` - Start session, returns context paths + AI synthesis
- `clock_out` - Archive session transcript to OCTAVE
- `odyssean_anchor` - Validate agent identity binding (RAPH vector)

## Key Directories

- `.hestai/context/` - Living context files (PROJECT-CONTEXT, etc.)
- `.hestai/sessions/active/` - Current session data (gitignored)
- `.hestai/sessions/archive/` - Compressed session archives (committed)
- `.hestai/workflow/` - North Star and specs

## Shared Utilities

Tools use shared modules in `src/hestai_mcp/mcp/tools/shared/`:
- `path_resolution.py` - Path validation and traversal prevention
- `security.py` - Input sanitization
- `fast_layer.py` - Git state and branch detection
- `compression.py` - OCTAVE compression helpers
