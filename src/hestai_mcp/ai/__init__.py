"""AI connectivity layer for hestai-core MCP tools."""

from hestai_mcp.ai.client import AIClient
from hestai_mcp.ai.config import (
    TierConfig,
    TieredAIConfig,
    TimeoutConfig,
    load_config,
    resolve_api_key,
    save_config,
)

# Backward compatibility alias
AIConfig = TieredAIConfig

__all__ = [
    "AIClient",
    "AIConfig",  # Backward compatibility alias
    "TierConfig",
    "TieredAIConfig",
    "TimeoutConfig",
    "load_config",
    "resolve_api_key",
    "save_config",
]
