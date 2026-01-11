===PATTERN:MINIMAL_INTERVENTION===
META:
  TYPE::PATTERN_COMPATIBILITY_STUB
  VERSION::"1.0"
  STATUS::DEPRECATED
  PURPOSE::"Compatibility stub for legacy references - use mip-architecture or mip-orchestration instead"

COMPATIBILITY::[
  ARCHITECTURAL_USAGE::mip-architecture,
  ORCHESTRATION_USAGE::mip-orchestration
]

§1::MIGRATION_GUIDANCE
RECOMMENDED_ACTIONS::[
  "Update agent references to mip-architecture or mip-orchestration",
  "Remove minimal-intervention references in your agent configuration"
]

§2::REDIRECTION
REDIRECT::[
  ARCHITECTURE_PATTERN::"Use mip-architecture for preventing over-engineering",
  ORCHESTRATION_PATTERN::"Use mip-orchestration for reducing coordination overhead"
]

===END===
