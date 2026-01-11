===SKILL:BUILD_EXECUTION===
META:
  TYPE::SKILL
  VERSION::"3.0"
  PURPOSE::"Orchestration skill for build execution, delegating to specialized skills and patterns"

§1::PHILOSOPHY_DELEGATION
BUILD_PHILOSOPHY::"See build-philosophy skill for comprehensive framework"
CORE_REFERENCES::[
  "build-philosophy: System awareness, MIP, UNDERSTAND→SHAPE→ACT framework",
  "build-anti-patterns: 9-pattern catalog with detection and prevention",
  "mip-build: Minimal Intervention for code complexity"
]

§2::MCP_TOOL_INTEGRATION
CONTEXT7::[
  PURPOSE::"Real-time library documentation retrieval",
  WORKFLOW::[
    "resolve-library-id: Get Context7-compatible ID",
    "get-library-docs: Retrieve current documentation",
    "Implement based on latest API truth"
  ],
  USE_FOR::"React hooks, Next.js routing, Supabase, any third-party library",
  ANTI_PATTERN::"Never assume API from memory - always verify"
]

REPOMIX::[
  PURPOSE::"Codebase analysis and pattern extraction",
  WORKFLOW::[
    "pack_codebase: Package for analysis",
    "grep_repomix_output: Find usage patterns",
    "Map all call sites before changes"
  ],
  USE_FOR::"Signature changes, refactoring, impact analysis",
  EXAMPLE::"processUser(id)→processUser(user): Pack→Grep(15 sites)→Analyze→Plan migration"
]

INTEGRATION::"Context7 for external contracts + Repomix for internal structure = System awareness"

§3::TDD_ENFORCEMENT
DISCIPLINE::"See tdd-discipline pattern"
WORKFLOW::[
  "RED: Write failing test first",
  "GREEN: Minimal code to pass",
  "REFACTOR: Improve while green",
  "COMMIT: test: → feat: → refactor: pattern"
]
PRAGMATIC_EXCEPTIONS::"When spec provides exact code+tests, trivial operations, exploratory spikes"

§4::VERIFICATION_REQUIREMENTS
EVIDENCE::"See verification-protocols pattern"
MANDATORY::[
  "Test output showing pass/fail",
  "Lint + Typecheck with 0 errors",
  "Coverage reports with actual numbers",
  "CI pipeline links"
]
ANTI_VALIDATION_THEATER::"'Tests pass' without output = rejection"

§5::DELEGATION_NOTES
IMPORTANT::"This skill delegates to other skills/patterns that must be loaded separately by agents"
TYPICALLY_LOADED_WITH::[
  "Skills: build-philosophy, build-anti-patterns, clarification-gate",
  "Patterns: mip-build, tdd-discipline, verification-protocols"
]
AGENT_RESPONSIBILITY::"Agents using build-execution should explicitly load needed companions"

===END===
