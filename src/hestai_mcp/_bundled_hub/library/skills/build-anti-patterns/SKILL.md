---
name: build-anti-patterns
description: Comprehensive catalog of build anti-patterns that degrade quality, increase maintenance, and introduce bugs. Includes detection frameworks and prevention strategies.
allowed-tools: "*"
triggers: ["anti-pattern", "isolated edits", "feature bloat", "context destruction", "premature optimization", "test procrastination", "snowball commits", "code smell"]
---

===SKILL:BUILD_ANTI_PATTERNS===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Comprehensive anti-pattern catalog for build phase"
  SOURCE::"Extracted from anti-patterns.oct.md"

§1::ISOLATED_EDITS
SYMPTOMS::"'I just changed one function' → unexpected failures in distant components"
EXAMPLE::"processUser(id)→processUser(userId): 15 call sites + db query builder + GraphQL resolver = 4hrs debugging"
DETECT::[
  "Changes without grepping usage",
  "Skip dependency analysis",
  "Quick fix mentality",
  "No test failures but prod breaks"
]
PREVENT::[
  "Ripple map before coding (git grep usage)",
  "Run full test suite (not just changed file)",
  "Check types (mypy/tsc)",
  "System impact analysis"
]

§2::FEATURE_BLOAT
SYMPTOMS::"'Since I'm here I'll also...' → features nobody asked for"
EXAMPLE::"Task: email validation. Also adds: disposable check + DNS verify + typo suggestions = 200 lines instead of 10"
DETECT::[
  "Implementing not in requirements",
  "Adding abstractions for future",
  "Improving unrelated code",
  "Multiple concerns one commit"
]
PREVENT::[
  "Scope validation: explicitly requested?",
  "Defer until needed (Rule of Three)",
  "Separate PRs for improvements",
  "One concern per commit"
]

§3::CONTEXT_DESTRUCTION
SYMPTOMS::"'Comment is obvious, removing it' → deleting architectural rationale"
EXAMPLE::"setTimeout comment explaining why not setInterval → deleted → future dev reintroduces bug"
DETECT::[
  "Deleting non-obvious comments",
  "Removing TODOs without resolution",
  "Stripping git history",
  "Cleanup PRs removing context"
]
PREVENT::[
  "Git handles versions, comments explain WHY not WHAT",
  "Preserve TODOs with explanations",
  "Architectural decisions in docs",
  "Commit messages explain WHY"
]

§4::PREMATURE_OPTIMIZATION
SYMPTOMS::"'This could be faster' → optimization without profiling"
EXAMPLE::"Optimize array iteration while real bottleneck is N+1 database queries"
DETECT::[
  "Optimizing without measuring",
  "Assuming bottlenecks",
  "Complexity added for theoretical speed",
  "Ignoring profiler results"
]
PREVENT::[
  "Profile first ALWAYS",
  "Optimize algorithms before code (O(n²)→O(n))",
  "Benchmark before/after",
  "Complexity cost must be justified"
]

§5::TEST_PROCRASTINATION
SYMPTOMS::"'I'll add tests later' → tests fit code not requirements"
EXAMPLE::"Implement feature → write tests after → tests pass but feature breaks edge cases"
DETECT::[
  "Tests added after code",
  "Commit message 'Add tests'",
  "Single commit with both test and implementation",
  "Test timestamp newer than implementation"
]
PREVENT::[
  "TDD discipline: RED→GREEN→REFACTOR",
  "Git history enforcement: test commit→feat commit",
  "Failing test proof required",
  "No merge without TDD evidence"
]

§6::ABSTRACTION_ADDICTION
SYMPTOMS::"'Future flexibility' → abstractions for 2 use cases"
EXAMPLE::"2 similar functions → DataProcessor class with generics → only 2 call sites + complex config"
DETECT::[
  "Abstraction before 3rd use",
  "Generic solutions for specific problems",
  "Indirection without clarity benefit",
  "Flexibility nobody needs"
]
PREVENT::[
  "Rule of Three: 1st concrete → 2nd note → 3rd abstract",
  "YAGNI: You Aren't Gonna Need It",
  "Abstractions must reduce cognitive load",
  "Must be understandable without docs"
]

§7::SNOWBALL_COMMITS
SYMPTOMS::"100+ files in one PR → impossible to review"
EXAMPLE::"Refactor user service + add feature + fix bugs + update deps = 247 files changed"
DETECT::[
  "PRs with 50+ files",
  "Multiple unrelated changes",
  "Commits with mixed concerns",
  "Reviewer comment: 'too large to review'"
]
PREVENT::[
  "Atomic commits: one logical change",
  "Feature flags for gradual rollout",
  "Separate refactor from features",
  "Stacked PRs: small incremental"
]

§8::DEPENDENCY_DRIFT
SYMPTOMS::"Outdated dependencies → security vulnerabilities + compatibility issues"
EXAMPLE::"react@16.8→18.0 without testing → breaking changes in hooks"
DETECT::[
  "Dependencies not updated 6mo+",
  "Security warnings ignored",
  "Version pinning without reason",
  "No dependency audit"
]
PREVENT::[
  "Regular updates: monthly review",
  "Security scanning: npm audit, Dependabot",
  "Test before update: integration suite",
  "Document version decisions"
]

§9::ENVIRONMENT_PARITY_GAPS
SYMPTOMS::"'Works locally' → production failures"
EXAMPLE::"Local: node@18 + sqlite | Prod: node@16 + postgres → crashes on deploy"
DETECT::[
  "No version specification",
  "Different DBs dev/prod",
  "Missing .env.example",
  "Manual environment setup"
]
PREVENT::[
  "Version specification: .nvmrc, engines",
  "Docker for consistency",
  "CI matches prod",
  "Env var validation on startup"
]

§10::DETECTION_FRAMEWORK
QUICK_CHECK::[
  "Changing without system analysis? → ISOLATED_EDITS",
  "Adding unrequested features? → FEATURE_BLOAT",
  "Deleting WHY comments? → CONTEXT_DESTRUCTION",
  "Optimizing without profiling? → PREMATURE_OPTIMIZATION",
  "Writing tests after? → TEST_PROCRASTINATION",
  "Abstracting for 2 cases? → ABSTRACTION_ADDICTION",
  "PR with 100+ files? → SNOWBALL_COMMITS",
  "Dependencies 6mo+ old? → DEPENDENCY_DRIFT",
  "Works locally not prod? → ENVIRONMENT_PARITY_GAPS"
]

§11::WISDOM
PREVENTION_OVER_CURE::"Recognize pattern early → apply prevention → avoid hours debugging"
CORE_TRUTH::"Anti-patterns are shortcuts creating technical debt. Pay now or pay later with interest"

===END===
