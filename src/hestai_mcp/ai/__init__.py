"""Backward compatibility shim for hestai_mcp.ai -> hestai_mcp.modules.services.ai.

DEPRECATED: This module exists only for backward compatibility with tests.
New code should import from hestai_mcp.modules.services.ai instead.
"""

# Re-export all AI modules from new location
from hestai_mcp.modules.services.ai import (  # noqa: F401
    client,
    config,
    prompts,
    providers,
)

# Re-export specific items for direct imports
from hestai_mcp.modules.services.ai.client import AIClient  # noqa: F401
from hestai_mcp.modules.services.ai.config import (  # noqa: F401
    TierConfig,
    TieredAIConfig,
    TimeoutConfig,
)

# Alias for backward compatibility
AIConfig = TieredAIConfig

# Expose module-level access for tests doing runtime imports
import sys  # noqa: E402

from hestai_mcp.modules.services import ai as _new_ai_module  # noqa: E402

sys.modules["hestai_mcp.ai"] = _new_ai_module
sys.modules["hestai_mcp.ai.client"] = _new_ai_module.client
sys.modules["hestai_mcp.ai.config"] = _new_ai_module.config
sys.modules["hestai_mcp.ai.prompts"] = _new_ai_module.prompts
sys.modules["hestai_mcp.ai.providers"] = _new_ai_module.providers

__all__ = [
    "client",
    "config",
    "prompts",
    "providers",
    "AIClient",
    "AIConfig",
    "TieredAIConfig",
    "TierConfig",
    "TimeoutConfig",
]
