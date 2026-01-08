===SKILL:CI_ERROR_RESOLUTION===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Protocol for systematic CI pipeline failure resolution"

§1::RESOLUTION_PROTOCOL
PHASES::[
  LOCAL_VALIDATION::"Ensure 'npm run {audit,lint,typecheck,test,build}' all pass locally first",
  BRANCH_STRATEGY::"Create 'fix/ci-errors-{timestamp}' branch for isolation",
  ITERATION_LOOP::"Check CI status -> Fetch logs -> Analyze -> Fix -> Commit -> Push -> Wait",
  VERIFICATION::"Confirm all checks pass via 'gh pr checks'"
]

§2::ERROR_HANDLING
ISSUES::[
  GH_NOT_FOUND::"Install GitHub CLI or skip autonomous loop",
  PERMISSION_DENIED::"Check git credentials, use SSH",
  CI_NOT_TRIGGERED::"Check .github/workflows/ triggers",
  TIMEOUT::"Increase wait time or reduce max iterations"
]

§3::METRICS
TRACK::[
  AVERAGE_ITERATIONS::"Count commits to green",
  FAILURE_TYPES::"Categorize (Lint vs Test vs Build)",
  AUTONOMOUS_SUCCESS::"Rate of resolution without human intervention"
]

===END===
