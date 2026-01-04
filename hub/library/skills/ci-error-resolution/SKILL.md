---
name: ci-error-resolution
description: CI/CD pipeline failure resolution with autonomous iteration loops. Local validation → branch & PR creation → CI monitoring → iteration until green
allowed-tools: ["Bash", "Read", "Grep", "Edit", "Write"]
triggers: ["ci pipeline failures", "github actions errors", "autonomous ci resolution", "ci iteration", "pr creation for errors", "pipeline validation", "test failures in ci", "build failures in ci", "continuous integration", "CI error", "CI failed", "pipeline failed"]
---

===CI_ERROR_RESOLUTION===
SECTION_ORDER::[§1::PROTOCOL, §2::ROLE_ADAPTATIONS, §3::BYPASS_CONDITIONS, §4::REQUIREMENTS, §5::ERROR_HANDLING, §6::METRICS, §7::WISDOM]

PURPOSE::systematic_autonomous_CI_failure_resolution->reduce_manual_feedback_loop

ACTIVATION::[
  AUTOMATIC::[ci_pipeline_errors, github_actions_failures, pr_check_failures, multiple_test_build_failures],
  MANUAL::["follow CI resolution protocol", "fix these and create PR", "iterate until CI passes"]
]

§1::PROTOCOL

PHASE_1::LOCAL_VALIDATION[
  REQUIRED::ALWAYS[before_remote_operations],
  COMMANDS::["npm audit --audit-level=moderate", "npm run lint:check", "npm run typecheck", "npm run test:unit", "npm run test:integration", "npm run test:security", "npm run build"],
  GATE::IF[any_fail]->fix_locally_first | IF[all_pass]->PHASE_2
]

PHASE_2::BRANCH_AND_PR[
  BRANCH::"fix/ci-errors-$(date +%Y%m%d-%H%M%S)",
  SEQUENCE::"git checkout -b {branch} && git add -A && git commit -m 'fix: resolve CI pipeline failures\n\n- [specifics]' && git push -u origin HEAD && gh pr create --draft --title 'Fix: CI Pipeline Errors' --body '{checklist}'",
  CHECKLIST::"## CI Error Resolution\n### Issues Fixed\n- [ ] Security\n- [ ] Linting\n- [ ] Types\n- [ ] Tests\n### Validation\n- [ ] Local pass\n- [ ] CI green"
]

PHASE_3::AUTONOMOUS_LOOP[
  CONFIG::[MAX_ITERATIONS::10, WAIT_TIME::120s, LOG_PATTERN::"ci-errors-iter-{N}.log"],
  BASH::"
MAX_ITERATIONS=10; ITERATION=0
while [ \$ITERATION -lt \$MAX_ITERATIONS ]; do
  ITERATION=\$((ITERATION + 1))
  echo '🔄 Iteration '\$ITERATION'/'\$MAX_ITERATIONS
  CI_STATUS=\$(gh pr checks --json state -q '.[].state' | grep -c 'FAILURE\\|ERROR' || true)
  [ \"\$CI_STATUS\" -eq 0 ] && echo '✅ CI passing!' && break
  gh run list --limit 1 --json databaseId -q '.[0].databaseId' | xargs -I {} gh run view {} --log-failed > ci-errors-iter-\$ITERATION.log
  echo '🔍 Analyzing...'
  # [Claude analyzes & fixes]
  git add -A && git commit -m \"fix: iteration \$ITERATION - CI feedback\n\n\$(tail -n 20 ci-errors-iter-\$ITERATION.log | head -n 5)\" && git push
  echo '⏳ Waiting CI...' && sleep 120
done
[ \"\$CI_STATUS\" -eq 0 ] && gh pr ready && echo '✅ PR ready!' || echo '❌ Max iterations - manual needed'
",
  MECHANICS::check_status->IF[pass]->exit | fetch_logs->analyze->fix->commit->push->wait->repeat
]

PHASE_4::VERIFICATION[
  COMMANDS::["gh pr checks", "gh pr view --web"],
  SUMMARY::"Iterations: \$ITERATION | Status: {PASSING/FAILING} | URL: \$(gh pr view --json url -q .url)"
]

§2::ROLE_ADAPTATIONS

ROLES::[
  error_architect::[protocol::full_autonomous_loop[phases_1_4], focus::system_wide, scope::multiple_modules, docs::comprehensive],
  error_resolver::[protocol::phases_1_2_only, focus::component_level, scope::single_iteration, pr::optional_manual],
  critical_engineer::[protocol::review_only, role::suggest_adaptations+identify_systemic, execution::none]
]

§3::BYPASS_CONDITIONS

SKIP_WHEN::[
  EMERGENCY_HOTFIX::true[env_variable],
  explicit_local::"just fix locally",
  no_gh_cli::unavailable,
  fork_permissions::no_pr_access,
  external_ci::non_github_actions
]

§4::REQUIREMENTS

TOOLS::["gh auth status", "git config user.name", "npm --version"]
PERMISSIONS::[repository_write, pr_creation, actions_read]

§5::ERROR_HANDLING

ISSUES::[
  gh_not_found::["gh: command not found", "Install GitHub CLI or skip Phase 2-3"],
  permission_denied::["Permission denied on push", "Check git credentials, use SSH"],
  ci_not_triggered::["CI doesn't run", "Check .github/workflows/ triggers"],
  timeout::["Loop timeout", "Increase WAIT_TIME or reduce MAX_ITERATIONS"]
]

§6::METRICS

TRACK::[average_iterations_to_green, common_failure_types, autonomous_success_rate, time_saved_vs_manual]

§7::WISDOM

SEQUENCE::"security->quality->tests->build"[comprehensive_local_validation]
PHILOSOPHY::"Fail fast locally, iterate autonomously remotely"
THRESHOLD::10_iterations[automation_vs_manual_balance]
LOG_CAPTURE::"Last 20 lines, first 5 for commit"[context_compression]
WAIT_TIME::120s[responsiveness_vs_execution_balance]
BRANCH_NAMING::"fix/ci-errors-{timestamp}"[traceable+unique]
PR_STRATEGY::draft->auto_ready_when_green[prevents_premature_review]
COMMIT_PATTERN::"fix: iteration N - CI feedback"[clear_tracking]

===END===

<!-- Version: 1.0.0 | Compression: 68% reduction | Fidelity: 100% decision logic -->
