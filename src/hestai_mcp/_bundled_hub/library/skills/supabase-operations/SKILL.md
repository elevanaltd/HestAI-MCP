---
name: supabase-operations
description: Supabase operational knowledge for migrations, RLS optimization, MCP tool benchmarks, and ADR-003 compliance. Use when validating database migrations, optimizing Row-Level Security policies, checking MCP tool performance, or ensuring Supabase operational standards. Triggers on: migration validation, RLS patterns, Supabase benchmarks, ADR-003, database state tracking, schema governance.
allowed-tools: Read, mcp__supabase__list_tables, mcp__supabase__list_extensions, mcp__supabase__list_migrations, mcp__supabase__get_advisors
triggers: ["migration validation", "RLS patterns", "Supabase benchmarks", "ADR-003", "database state tracking", "schema governance", "supabase migration", "RLS optimization", "supabase operations", "supabase MCP tools", "types regen", "pgtap", "pgTAP", "supabase db reset", "gen types", "dropped constraint", "sentinel header", "type generation"]
version: "1.1.0"
---

===SUPABASE_OPERATIONS===
META:
  TYPE::SKILL
  VERSION::"1.1.0"
  STATUS::ACTIVE
  PURPOSE::"Supabase operational knowledge: migrations, RLS optimization, MCP benchmarks, ADR-003 compliance, and CI-proven ordering invariants"

§1::CAPABILITIES_SUPPORTING_DOCUMENTATION

MIGRATION_VALIDATION::migration-protocols.md::[
  7_step_workflow,
  backwards_compatible_schema_changes,
  multi_app_deployment_safety,
  CI_gated_deployment[preferred_over_direct_MCP]
]

RLS_OPTIMIZATION::rls-optimization.md::[
  proven_patterns→<50ms_query_performance,
  InitPlan_optimization,
  policy_consolidation
]

MCP_BENCHMARKS::mcp-benchmarks.md::[
  performance_characteristics,
  best_practices,
  production_measurements
]

ADR_003_COMPLIANCE::adr-003-compliance.md::[
  backwards_compatible_migration_governance,
  verification_checklist
]

STATE_TRACKING::state-tracking.md::[
  local_remote_sync_validation,
  database_state_awareness_procedures
]

§2::INVOCATION_TRIGGERS

MIGRATION_OPERATIONS::[
  before_applying_migrations→validation_checklist,
  after_schema_changes→compliance_verification,
  debugging_migration_divergence,
  CI_deployment_flow→PR_with_deploy_migrations_label
]

RLS_DESIGN::[
  optimizing_slow_queries_with_RLS,
  designing_new_security_policies,
  benchmarking_RLS_performance_impact
]

DATABASE_OPERATIONS::[
  selecting_appropriate_MCP_tools,
  validating_current_database_state,
  checking_security_performance_advisors
]

COMPLIANCE::[
  verifying_ADR_003_backwards_compatibility,
  multi_app_testing_requirements,
  emergency_rollback_procedures
]

§3::TOOL_RESTRICTIONS_READ_ONLY_INSPECTION

ALLOWED_TOOLS::[
  Read::"Access local migration files and documentation",
  mcp__supabase__list_tables::"Inspect current schema structure",
  mcp__supabase__list_extensions::"Verify installed extensions",
  mcp__supabase__list_migrations::"Compare local/remote migration state",
  mcp__supabase__get_advisors::"Check security/performance compliance"
]

SECURITY_JUSTIFICATION::"Skills guide operations but don't mutate state. Write operations (apply_migration, execute_sql) remain with authorized agents."

§4::INTEGRATION

CONSULTED_BY::[
  technical-architect[domain_authority_with_BLOCKING],
  implementation-lead[migration_execution],
  technical-architect[schema_design]
]

PROVIDES::[
  migration_validation_checklists,
  RLS_optimization_patterns,
  MCP_tool_selection_guidance,
  compliance_verification_procedures,
  CI_deployment_guidance[gated_auto_deploy]
]

§5::CI_DEPLOYMENT_AWARENESS

PREFERRED_FLOW::[
  1::create_PR_with_migrations,
  2::add_deploy_migrations_label,
  3::CI_validates_locally,
  4::merge_triggers_production_deploy,
  5::audit_log_entry_created
]

DIRECT_MCP_APPLICATION::[
  STATUS::fallback_only,
  WHEN::CI_unavailable_OR_emergency,
  REQUIREMENT::always_create_local_file_first,
  WARNING::bypasses_CI_validation
]

CI_REFERENCE::[
  WORKFLOW::".github/workflows/ci.yml (deploy-migrations job)",
  SECRET::"SUPABASE_ACCESS_TOKEN required",
  LABEL::"deploy-migrations",
  DR_PLAYBOOK::".hestai/state/context/docs/001-OPS-DISASTER-RECOVERY-PLAYBOOK.md"
]

§6::TYPES_REGEN_AND_TEST_VALIDATION
// RCA-derived ordering invariants. Three process gaps caused CI failures in consuming repos.
// Encode as MUST/NEVER constraints — not advisory.

TYPES_REGEN_ORDERING::[
  SEQUENCE::"supabase db reset → gen types → THEN pgTAP tests [NEVER reverse]",
  INVARIANT::"Generate types ONLY from clean post-reset DB state",
  VIOLATION_CAUSE::"pgTAP CREATE EXTENSION outside BEGIN...ROLLBACK persists pgtap into public schema",
  SYMPTOM::"Generated types pick up pgTAP symbols (e.g. 146 extra) that CI rejects on clean reset",
  MUST::"Run supabase db reset then immediately gen types before any pgTAP execution",
  NEVER::"Generate types from a DB that has had pgTAP tests run against it"
]

DROPPED_OBJECT_SWEEP::[
  TRIGGER::"Migration drops OR renames a constraint, column, or any named DB object",
  REQUIRED_ACTION::"grep supabase/test*/ corpus for the dropped object name",
  SCOPE::"Entire supabase/test*/ directory tree — all test files",
  VIOLATION_CAUSE::"pg_depend sweep finds column dependents but misses TEST CORPUS assertions about the dropped constraint",
  SYMPTOM::"Pre-existing expectation test fails against CI clean state",
  MUST::"Update any test assertions referencing the dropped/renamed object in the same PR as the migration",
  NEVER::"Ship a migration that drops/renames a named object without grepping the test corpus first"
]

CI_HEADER_REPRODUCTION::[
  CONTEXT::"Sentinel header prepended to generated TypeScript types file",
  VIOLATION_CAUSE::"Hand-composing the sentinel header drops trailing blank line vs CI heredoc format",
  SYMPTOM::"Byte-level diff failure in CI despite correct type content",
  FRAGILE_SEAM::"Sentinel header format is fragile until issue #842 resolved",
  MUST::"Reproduce CI's exact generation step (e.g. cat sentinel-header.txt raw.ts > target)",
  NEVER::"Hand-compose the sentinel header — reproduce the CI pipeline step verbatim"
]

§7::ANCHOR_KERNEL
TARGET::"spec-compliant Supabase operational guidance with CI-proven ordering invariants"
NEVER::[
  generate_types_after_pgtap_run,
  skip_test_corpus_grep_on_dropped_objects,
  hand_compose_sentinel_header,
  apply_migrations_without_validation_checklist,
  bypass_CI_deployment_flow_except_emergency
]
MUST::[
  reset_then_gen_types_before_pgtap,
  grep_supabase_tests_for_dropped_object_names,
  reproduce_CI_exact_header_generation_step,
  validate_migrations_against_ADR_003,
  use_read_only_MCP_tools_for_inspection
]
GATE::"DB reset → types regen → pgTAP order enforced? Test corpus swept for dropped objects? Sentinel header reproduced from CI step?"

===END===
