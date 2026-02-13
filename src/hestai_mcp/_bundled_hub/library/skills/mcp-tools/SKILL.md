---
name: mcp-tools
description: MCP tool implementation patterns for HestAI including tool structure, session tools, and shared utilities
allowed-tools: "*"
triggers: ["MCP tool", "clock_in", "clock_out", "bind", "mcp server", "tool implementation", "hestai context", "session management", "path_resolution", "fast_layer"]
---

===MCP_TOOLS===
META:
  TYPE::SKILL
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"MCP tool implementation patterns for HestAI"
  DOMAIN::HEPHAESTUS[tool_crafting]⊕HERMES[communication]

§1::TOOL_STRUCTURE
  LOCATION::src/hestai_mcp/mcp/tools/
  RETURN_TYPE::dict[str,Any]
  PATTERN::[
    "async def my_tool_async(",
    "    required_param: str,",
    "    optional_param: str | None = None,",
    ") -> dict[str, Any]:",
    "    \"\"\"Tool description.\"\"\"",
    "    # Validate inputs first",
    "    validated = validate_param(required_param)",
    "    # Implementation",
    "    return {\"status\": \"success\", \"data\": result}"
  ]

§2::SESSION_TOOLS
  CLOCK_IN::[
    PURPOSE::"Start session, returns context paths + AI synthesis",
    PARAMS::[role,working_dir,focus?,model?],
    RETURNS::[session_id,context_paths,ai_synthesis]
  ]
  CLOCK_OUT::[
    PURPOSE::"Archive session transcript to OCTAVE",
    PARAMS::[session_id,description?],
    RETURNS::[archive_path,learnings]
  ]
  BIND::[
    PURPOSE::"Bootstrap agent binding with low token usage",
    PARAMS::[role,topic?,tier?,working_dir?],
    RETURNS::[agent_file,skills,context_paths]
  ]

§3::KEY_DIRECTORIES
  CONTEXT::.hestai/context/["Living context files (PROJECT-CONTEXT, etc.)"]
  ACTIVE::.hestai/sessions/active/["Current session data (gitignored)"]
  ARCHIVE::.hestai/sessions/archive/["Compressed session archives (committed)"]
  WORKFLOW::.hestai/workflow/["North Star and specs"]

§4::SHARED_UTILITIES
  LOCATION::src/hestai_mcp/mcp/tools/shared/
  MODULES::[
    path_resolution.py::"Path validation and traversal prevention",
    security.py::"Input sanitization",
    fast_layer.py::"Git state and branch detection",
    compression.py::"OCTAVE compression helpers"
  ]

§5::SECURITY
  PATH_VALIDATION::prevent_traversal[../,symlinks]
  INPUT_SANITIZATION::validate_before_use
  ROLE_VALIDATION::allowlist_pattern["^[a-z][a-z0-9-]*$"]

§6::ASYNC_PATTERNS
  REQUIREMENT::all_MCP_tools_must_be_async
  AI_INTEGRATION::AIClient.complete_text()[optional_synthesis]
  ERROR_HANDLING::graceful_fallback_on_failure

===END===
