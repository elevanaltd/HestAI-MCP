"""Backward compatibility shim for hestai_mcp.mcp.tools -> hestai_mcp.modules.tools.

DEPRECATED: This module exists only for backward compatibility with tests.
New code should import from hestai_mcp.modules.tools instead.
"""

# Re-export all tools from new location
# Expose module-level access for tests doing runtime imports
import sys

from hestai_mcp.modules import tools as _new_tools_module
from hestai_mcp.modules.tools import (  # noqa: F401
    bind,
    clock_in,
    clock_out,
    shared,
)

# Create module alias for backward compatibility
sys.modules["hestai_mcp.mcp.tools"] = _new_tools_module
sys.modules["hestai_mcp.mcp.tools.shared"] = _new_tools_module.shared

__all__ = [
    "bind",
    "clock_in",
    "clock_out",
    "shared",
]
