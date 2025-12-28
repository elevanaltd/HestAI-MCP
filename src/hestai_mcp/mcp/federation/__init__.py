"""MCP Federation - upstream tool federation for SS-I3 compliance.

SS-I3: HestAI-MCP must act as both MCP Server (outward) and MCP Client
(inward to OCTAVE and other MCP servers). Upstream tools are namespaced.
"""

from hestai_mcp.mcp.federation.client_manager import MCPClientManager

__all__ = ["MCPClientManager"]
