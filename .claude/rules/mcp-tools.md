---
description: MCP tool implementation patterns
globs:
  - "src/hestai_mcp/tools/**/*.py"
  - "src/hestai_mcp/server.py"
---

# MCP Tool Implementation

## Tool Structure

Tools live in `src/hestai_mcp/tools/` and follow this pattern:

```python
from mcp.types import Tool, TextContent

async def my_tool(arguments: dict) -> list[TextContent]:
    """Tool description for Claude."""
    # Implementation
    return [TextContent(type="text", text=result)]
```

## Session Tools

- `clock_in` - Start session, returns context paths
- `clock_out` - Archive session transcript
- `odyssean_anchor` - Validate agent identity binding

## Key Directories

- `.hestai/context/` - Living context files
- `.hestai/sessions/active/` - Current session data
- `.hestai/workflow/` - North Star and specs

## Error Responses

Return structured errors with actionable guidance:
```python
return [TextContent(type="text", text=f"ERROR: {reason}\nSuggestion: {fix}")]
```
