===SKILL:BUILD_EXECUTION===
META:
  TYPE::SKILL
  VERSION::"2.0"
  PURPOSE::"Comprehensive guide for systematic build execution, integrating philosophy, anti-patterns, and MCP tools."

§1::CORE_PHILOSOPHY
SYSTEM_THINKING::[
  MAP_IMPACT::"Code change -> System ripple -> Understand ripples BEFORE modification",
  MINIMAL_CODE::"Essential complexity serves users, accumulative complexity serves maintenance",
  MAINTAIN_LIVING::"Maintain a living system, don't just edit text files"
]

§2::DECISION_GATES
BEFORE_CODE::[
  "Is this a user problem?",
  "Can we extend existing components?",
  "Is this feature explicitly requested?",
  "Are we solving a problem that doesn't exist yet?"
]
BEFORE_ABSTRACTION::[
  "Rule of Three: 1st concrete -> 2nd copy -> 3rd abstract",
  "Does it reduce cognitive load?",
  "Is it understandable without docs?"
]

§3::MCP_TOOL_INTEGRATION
CONTEXT7::[
  PURPOSE::"Real-time library documentation retrieval",
  USE_FOR::"React hooks, Framework APIs, Third-party libs",
  MANDATE::"Resolve library ID -> Get docs -> Implement based on current truth"
]
REPOMIX::[
  PURPOSE::"Codebase analysis and pattern extraction",
  USE_FOR::"Refactoring, Signatures, Architectural analysis",
  MANDATE::"Pack -> Grep -> Map usage sites -> Plan migration"
]

§4::ANTI_PATTERNS
COMMON_TRAPS::[
  ISOLATED_EDITS::"Changing one function without checking all call sites",
  FEATURE_BLOAT::"Adding 'nice to have' features while in the code",
  CONTEXT_DESTRUCTION::"Removing 'WHY' comments or commit history",
  PREMATURE_OPTIMIZATION::"Optimizing without profiling data",
  SNOWBALL_COMMITS::"PRs with 100+ files and mixed concerns"
]

§5::REQUIRED_PATTERNS
CORE_DISCIPLINES::[
  tdd-discipline,        // Red-Green-Refactor loop
  verification-protocols, // Evidence requirements
  minimal-intervention   // Stop when essential value delivered
]

===END===
