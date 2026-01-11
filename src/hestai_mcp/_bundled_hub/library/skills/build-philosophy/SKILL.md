---
name: build-philosophy
description: Comprehensive build philosophy including system awareness, MIP for code, decision frameworks, and wisdom paths. Prevents accumulative complexity through systematic thinking.
allowed-tools: "*"
triggers: ["build philosophy", "system awareness", "code complexity", "minimal intervention", "ripple mapping", "UNDERSTAND SHAPE ACT", "essential complexity", "accumulative complexity"]
---

===SKILL:BUILD_PHILOSOPHY===
META:
  TYPE::SKILL
  VERSION::"2.0"
  PURPOSE::"Comprehensive build philosophy framework preventing accumulative complexity"
  SOURCE::"Consolidated from ~/.claude/skills/build-execution/*.oct.md"

§1::SYSTEM_AWARENESS_MANDATE
CORE_PRINCIPLE::"Code change → System ripple → Understand ripples BEFORE modification"

SYSTEM_THINKING::[
  MAP_IMPACT::[
    "Trace all imports/uses of changed code",
    "Follow data flow dependencies",
    "Identify shared state impacts",
    "Document ripple paths explicitly"
  ],
  LOCAL_CHANGE_SYSTEM_CONTEXT::"Simple edit can break distant components - think globally",
  LOCAL_OPTIMIZATION_DEGRADES::"Faster function ≠ better system if breaks caching",
  MINIMAL_CODE_SERVES::"Essential complexity serves users, accumulative serves maintenance burden"
]

MAINTAIN_LIVING_SYSTEM::"Not editing text files - every change affects production"

§2::MINIMAL_INTERVENTION_PRINCIPLE
DEFINITION::[
  ESSENTIAL::"Code serving measurable user value",
  ACCUMULATIVE::"Code adding maintenance burden without proportional user value"
]

DECISION::"Could we achieve same outcome with simpler means?"

PROCESS::"Remove components until UX degrades → identify break point → restore last essential → minimal achieved"

ENFORCEMENT::[
  JUSTIFICATION::"User problem? Why not extend existing? Simplification test?",
  EVIDENCE::"What removed? Break point found? Minimal restoration done?",
  SIGNOFF::"Reviewer verifies minimality credible, no obvious bloat"
]

§3::PHILOSOPHY_FRAMEWORK
UNDERSTAND_SHAPE_ACT::[
  UNDERSTAND::[
    "What is the user problem?",
    "System connections and dependencies?",
    "Core assumptions and invariants?",
    "WARNING: 'just try this', 'probably works', 'not sure how'"
  ],
  SHAPE::[
    "Simplest solution satisfying requirements",
    "Obvious to future readers (6mo test)",
    "Easy test isolation",
    "Minimal coupling",
    "PATTERNS: proven>novel, simple>clever, explicit>implicit"
  ],
  ACT::[
    "TDD: failing test first",
    "Implement minimal solution",
    "Refactor for essential simplification only",
    "Commit atomically",
    "SCOPE: requested ≠ while_here, one concern per commit"
  ]
]

WISDOM_PATH::[
  BETWEEN::"Complexity labyrinth ← minimal effective → Oversimplification sea",
  AVOID_LABYRINTH::"Over-abstracted, premature generalization, unjustified patterns",
  AVOID_OVERSIMPLIFICATION::"Unjustified duplication, skipping necessary abstractions",
  MINIMAL_EFFECTIVE::[
    "Just enough abstraction to prevent duplication",
    "Just enough flexibility to handle known variations",
    "Just enough structure to maintain coherence"
  ]
]

§4::DECISION_GATES
BEFORE_CODE::[
  "Is this solving a user problem?",
  "Can we extend existing components?",
  "Is this feature explicitly requested?",
  "Are we solving a problem that doesn't exist yet?",
  "IF accumulative → DON'T ADD"
]

BEFORE_ABSTRACTION::[
  "Rule of Three: 1st concrete → 2nd copy → 3rd abstract",
  "Does it reduce cognitive load?",
  "Is it understandable without docs?",
  "Cost if requirements change?",
  "IF mysterious → KEEP CONCRETE"
]

BEFORE_OPTIMIZATION::[
  "Is this a measured bottleneck?",
  "Have we profiled first?",
  "Is the gain measured?",
  "PROFILE FIRST → IF not measured → DON'T OPTIMIZE"
]

BEFORE_TESTS::[
  "Does this test user-facing behavior?",
  "Does it validate component contract?",
  "Will it catch real bugs?",
  "Testing behavior not implementation?",
  "IF not user-facing → RECONSIDER"
]

BEFORE_REFACTOR::[
  "Does this improve clarity?",
  "Does it reduce complexity?",
  "Are tests still green?",
  "Will it make future changes easier?",
  "SAFETY: small steps, test after each, revert if fail",
  "IF behavior changes → NOT REFACTORING, IT'S A FEATURE"
]

§5::PRACTICAL_EXAMPLES
RIPPLE_MAP_EXAMPLE::[
  CHANGE::"processUser(id) → processUser(user)",
  DIRECT::"10 files need to pass user object",
  INDIRECT::"Tests need fixtures not IDs, API needs hydration, caching changes",
  FLOW::"DB queries move to callers, N+1 risk emerges",
  OUTCOME::"Simple signature change → 20 files + performance testing + staged migration"
]

WITH_WITHOUT_PHILOSOPHY::[
  REQUEST::"Add PDF export",
  WITHOUT::"Add library → create service → endpoint → ship = 500 lines untested",
  WITH::[
    "UNDERSTAND: Who? Why? How often? → 1 user, monthly report, using screenshots now",
    "SHAPE: Screenshot API suffices → 10 lines",
    "ACT: TEST → IMPLEMENT → TEST → DOCUMENT = 50 lines tested, solves actual need"
  ]
]

§6::WISDOM
CORE_TRUTH::"Code change = system change. Think systemically + Code minimally + Verify rigorously"

QUALITY_HIERARCHY::[
  BEST::"Code you don't write",
  SECOND::"Code that is obvious, testable, and minimal"
]

RIPPLE_AWARENESS::"Between isolated edit (wrong) and system paralysis (wrong) lies systematic local change with global awareness"

===END===
