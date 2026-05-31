===MCP_BENCHMARKS===
META:
  TYPE::SUPPORTING_DOCUMENTATION
  VERSION::"1.0"
  PURPOSE::"MCP Tool Performance Benchmarks"
  STATUS::ACTIVE
  CANONICAL::".hestai-sys/library/skills/supabase-operations/mcp-benchmarks.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/skills/supabase-operations/mcp-benchmarks.oct.md"
NOTE::"Performance data from production usage. Replace YOUR_PROJECT_ID with your actual Supabase project ID."
§1::TOOL_PERFORMANCE
LIST_MIGRATIONS:
  PURPOSE::"Retrieve remote migration state for sync validation"
  PERF::[
    "Typical: 200-400ms",
    "Operation: Remote API call to Supabase Management API",
    "Network-dependent: Add ~100ms for slow connections"
  ]
  USE_WHEN::[
    "Step 2 of migration workflow (state validation)",
    "Debugging migration divergence",
    "Verifying migration application"
  ]
  BEST_PRACTICES::["Cache results when checking multiple migrations","Use at beginning of migration workflow (not per-migration)"]
APPLY_MIGRATION:
  PURPOSE::"Execute DDL operations with tracking"
  PERF::[
    "Simple DDL: 500-800ms (CREATE INDEX, ADD COLUMN)",
    "Complex DDL: 1000-2000ms (multi-table ALTER, FK constraints)",
    "Depends on: Table size, existing constraints, lock contention"
  ]
  USE_WHEN::[
    "DDL operations (CREATE, ALTER, DROP)",
    "Schema changes requiring audit trail",
    "Operations needing rollback procedures"
  ]
  BEST_PRACTICES::[
    "Test complex migrations in staging first",
    "Monitor for lock timeouts (>5s indicates contention)",
    "Use during low-traffic periods for large tables"
  ]
  ANTI_PATTERN::"Don't use for DML (data migrations) - use execute_sql instead"
EXECUTE_SQL:
  PURPOSE::"Run DML queries and complex operations"
  PERF::[
    "Simple queries: 50-150ms",
    "Complex JOINs: 150-500ms",
    "Target: <200ms for production queries"
  ]
  USE_WHEN::[
    "DML operations (INSERT, UPDATE, DELETE)",
    "Data migrations",
    "Complex analytical queries",
    "Temporary operations not requiring migration history"
  ]
  BEST_PRACTICES::[
    "Parameterize queries to prevent SQL injection",
    "Use EXPLAIN ANALYZE for performance testing",
    "Batch large operations (1000 rows at a time)"
  ]
  ANTI_PATTERN::"Don't use for DDL that should be tracked (use apply_migration)"
GET_ADVISORS:
  PURPOSE::"Security and performance validation"
  PERF::[
    "Security scan: 300-600ms",
    "Performance scan: 300-600ms",
    "Full analysis: ~1000ms (both scans)"
  ]
  USE_WHEN::[
    "After schema changes (migration validation)",
    "Before production deployment",
    "Debugging security/performance issues",
    "Regular audits (weekly/monthly)"
  ]
  BEST_PRACTICES::[
    "Run after every migration (Step 6 validation)",
    "Treat warnings as errors (zero-tolerance gate)",
    "Document remediation for each issue"
  ]
  COMMON_ISSUES::[
    "Missing RLS policies (security)",
    "Missing indexes on foreign keys (performance)",
    "Inefficient query patterns (performance)",
    "Permission gaps (security)"
  ]
GENERATE_TYPESCRIPT_TYPES:
  PURPOSE::"Generate TypeScript interfaces from schema"
  PERF::[
    "Small schema (<20 tables): 1000-1500ms",
    "Medium schema (20-50 tables): 1500-2500ms",
    "Large schema (>50 tables): 2500-3500ms"
  ]
  USE_WHEN::[
    "After schema changes",
    "Before committing migrations",
    "When TypeScript errors indicate schema drift"
  ]
  BEST_PRACTICES::[
    "Run as final step after migration validation",
    "Commit generated types with migration files",
    "Use in shared library for consistency across apps"
  ]
  ANTI_PATTERN::"Don't generate manually - automate with migration workflow"
LIST_TABLES:
  PURPOSE::"Inspect current schema structure"
  PERF::["Standard: 150-300ms","Includes: Table names, schemas, columns"]
  USE_WHEN::[
    "Schema exploration",
    "Validation of table existence",
    "Debugging missing tables"
  ]
  BEST_PRACTICES::["Filter by schema when possible (faster)","Cache results for multi-query workflows"]
LIST_EXTENSIONS:
  PURPOSE::"Verify installed Postgres extensions"
  PERF::["Standard: 100-200ms"]
  USE_WHEN::[
    "Verifying extension installation (uuid-ossp, pg_stat_statements)",
    "Debugging missing extension functions",
    "Pre-migration dependency checks"
  ]
  BEST_PRACTICES::["Check extensions before creating functions that depend on them","Document required extensions in migration comments"]
§2::TOOL_SELECTION_MATRIX
SCHEMA_CHANGE_DDL::"apply_migration — Trackable, reversible, auditable"
DATA_MIGRATION_DML::"execute_sql — Flexible, can batch operations"
STATE_VALIDATION::"list_migrations — Shows local/remote sync status"
SECURITY_CHECK::"get_advisors(security) — Detects RLS gaps, permission issues"
PERFORMANCE_CHECK::"get_advisors(performance) — Identifies missing indexes, slow queries"
SCHEMA_INSPECTION::"list_tables — Quick schema overview"
TYPE_GENERATION::"generate_typescript_types — Ensures type safety"
EXTENSION_CHECK::"list_extensions — Validates dependencies"
§3::PERFORMANCE_OPTIMIZATION
BATCH_OPERATIONS:
  ```javascript
// Don't: Execute 1000 queries sequentially
for (let i = 0; i < 1000; i++) {
  await execute_sql(`INSERT INTO records VALUES (${i})`);
}

// Do: Batch into single query
await execute_sql(`
  INSERT INTO records
  SELECT generate_series(1, 1000)
`);
  ```
BATCH_IMPACT::"1000x faster (50s -> 50ms)"
CACHE_MIGRATION_STATE:
  ```javascript
// Don't: Query migrations repeatedly
for (let migration of localMigrations) {
  const remote = await list_migrations(); // Repeated API calls
  checkSync(migration, remote);
}

// Do: Query once, cache results
const remoteMigrations = await list_migrations(); // Single API call
for (let migration of localMigrations) {
  checkSync(migration, remoteMigrations);
}
  ```
CACHE_IMPACT::"Nx faster (N = number of migrations)"
PARALLEL_OPS:
  ```javascript
// Don't: Sequential when operations are independent
await list_tables();
await list_extensions();
await get_advisors('security');

// Do: Parallel execution
await Promise.all([
  list_tables(),
  list_extensions(),
  get_advisors('security')
]);
  ```
PARALLEL_IMPACT::"3x faster (900ms -> 300ms)"
SMART_ADVISORS:
  ```javascript
// Don't: Run advisors on every query
await execute_sql(query);
await get_advisors('performance');

// Do: Run advisors after schema changes only
await apply_migration(migration);
await get_advisors('security');
await get_advisors('performance');
  ```
SMART_ADVISORS_IMPACT::"Reduces unnecessary API calls"
§4::TIMEOUT_RECOMMENDATIONS
TIMEOUTS::[
  "list_migrations: 2s — Network-bound, rarely >1s",
  "apply_migration: 10s — DDL can be slow on large tables",
  "execute_sql: 5s — DML should be fast, timeout if slow",
  "get_advisors: 3s — Analysis rarely >1s",
  "generate_typescript_types: 5s — Schema traversal takes time",
  "list_tables: 2s — Quick metadata query",
  "list_extensions: 2s — Quick metadata query"
]
§5::ERROR_PATTERNS
CONNECTION_TIMEOUTS:
  SYMPTOM::"Tool hangs, eventually times out"
  CAUSES::[
    "Network issues",
    "Supabase service degradation",
    "Large result sets"
  ]
  MITIGATION::[
    "Implement retry with exponential backoff",
    "Use shorter timeouts for quick-fail",
    "Check Supabase status page"
  ]
RATE_LIMITING:
  SYMPTOM::"429 Too Many Requests"
  CAUSES::["Rapid sequential API calls","Multiple agents calling tools simultaneously"]
  MITIGATION::[
    "Batch operations when possible",
    "Add delays between calls (100ms)",
    "Use cached results instead of re-querying"
  ]
LOCK_CONTENTION:
  SYMPTOM::"Migration takes >10s, times out"
  CAUSES::[
    "Altering table with active queries",
    "Adding constraints to large tables",
    "Concurrent migrations"
  ]
  MITIGATION::[
    "Run during low-traffic periods",
    "Use CREATE INDEX CONCURRENTLY",
    "Test in staging first"
  ]
===END===
