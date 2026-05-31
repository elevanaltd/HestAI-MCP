===STATE_TRACKING===
META:
  TYPE::SUPPORTING_DOCUMENTATION
  VERSION::"1.0"
  PURPOSE::"State Tracking Procedures"
  STATUS::ACTIVE
  CANONICAL::".hestai-sys/library/skills/supabase-operations/state-tracking.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/skills/supabase-operations/state-tracking.oct.md"
OVERVIEW::"Database state awareness requires continuous validation of local development state vs remote production state to prevent migration divergence and maintain schema synchronization."
§1::CURRENT_STATE_AWARENESS
PRODUCTION_DB::[
  "Project ID: zbxvjyrbkycbfhwmmnmy",
  "Application: scripts-web",
  "Environment: Production"
]
STATE_COMPONENTS::[
  "Schema Version: Latest applied migration timestamp",
  "Migration Sync: Local files vs remote applied migrations",
  "RLS Policies: Active policies and performance baselines",
  "Extensions: Installed Postgres extensions",
  "Performance Metrics: Query times against RLS targets"
]
§2::LOCAL_REMOTE_SYNC_VALIDATION
STEP_1_READ_LOCAL:
  ```bash
ls -la supabase/migrations/*.sql
  ```
EXPECTED_FORMAT::[
  "20231201120000_initial_schema.sql",
  "20231205143000_add_users_table.sql",
  "20231210092000_add_rls_policies.sql"
]
LOCAL_VALIDATION::[
  "Timestamps in chronological order",
  "No duplicate timestamps",
  "Descriptive file names"
]
STEP_2_QUERY_REMOTE:
  ```javascript
const remoteMigrations = await mcp__supabase__list_migrations({
  project_id: 'zbxvjyrbkycbfhwmmnmy'
});
  ```
STEP_3_DETECT_DIVERGENCE:
  PATTERN_PENDING::"Local: [A,B,C,D] Remote: [A,B,C] — D is pending, apply via workflow"
  PATTERN_DRIFT::"Local: [A,B,D] Remote: [A,B,C,D] — C missing from local, INVESTIGATE"
  PATTERN_CONFLICT::"Local: [A,B,C_local] Remote: [A,B,C_remote] — HALT, resolve conflict"
  PATTERN_SYNC::"Local: [A,B,C] Remote: [A,B,C] — synchronized, proceed"
§3::SYNC_GUIDANCE
PENDING_MIGRATIONS:
  SCENARIO::"Local has migrations not yet applied to remote"
  VALIDATION::[
    "Verify local migrations are in git (committed)",
    "Check ADR-003 compliance for pending migrations",
    "Run migration workflow from Step 4 onwards",
    "Apply pending migrations via apply_migration"
  ]
  COMMANDS:
    ```bash
# Verify git tracking
git log --oneline -- supabase/migrations/

# Apply pending migration
mcp__supabase__apply_migration({
  project_id: 'zbxvjyrbkycbfhwmmnmy',
  name: '20231210092000_add_rls_policies',
  query: '[SQL CONTENT]'
})
    ```
MISSING_LOCAL:
  SCENARIO::"Remote has migrations not in local repository"
  INVESTIGATION::[
    "Check git history: Was migration intentionally excluded?",
    "Check team communication: Did someone apply directly to production?",
    "Retrieve migration content from Supabase dashboard",
    "Commit missing migration to git",
    "Synchronize local state"
  ]
  RECOVERY:
    ```bash
git add supabase/migrations/20231207100000_missing_migration.sql
git commit -m "Recover missing migration from production"
    ```
CONFLICTING_MIGRATIONS:
  SCENARIO::"Same timestamp, different content (developer conflict)"
  RESOLUTION::[
    "HALT: Do not apply either migration",
    "Compare content: Developer A vs Developer B",
    "If independent: Rename one with new timestamp",
    "If conflicting: Merge into single migration",
    "Test merged migration in staging",
    "Apply to production"
  ]
  PREVENTION::[
    "Coordinate migration creation with team",
    "Use timestamp + developer initials in filename",
    "Pull latest migrations before creating new ones"
  ]
§4::STATE_REPORTING
STANDARD_REPORT_FORMAT::"PROJECT / TIMESTAMP / LOCAL_STATE / REMOTE_STATE / DIVERGENCE / SYNC_GUIDANCE"
REPORT_EXAMPLE:
  ```text
═══════════════════════════════════════
SUPABASE STATE REPORT
═══════════════════════════════════════

PROJECT: scripts-web (zbxvjyrbkycbfhwmmnmy)
TIMESTAMP: 2023-12-15 14:30:00 UTC

LOCAL STATE:
  Migrations: 15 files
  Latest: 20231210092000_add_rls_policies.sql

REMOTE STATE:
  Migrations: 14 applied
  Latest: 20231205143000_add_users_table.sql

DIVERGENCE:
  Status: PENDING MIGRATIONS
  Details: 1 local migration not yet applied
  Pending: 20231210092000_add_rls_policies.sql

SYNC GUIDANCE:
  1. Validate ADR-003 compliance for pending migration
  2. Run get_advisors after applying migration
  3. Expected application time: ~500ms
  4. No rollback concerns (additive change)

═══════════════════════════════════════
  ```
§5::LIVING_PROTOCOL_UPDATES
PROTOCOL_LOCATION::"/Users/shaunbuswell/.claude/protocols/SUPABASE-OPERATIONS.md"
UPDATE_TRIGGERS::[
  "After migration application",
  "After RLS optimization discovery",
  "After performance validation",
  "After troubleshooting resolution"
]
§6::PERFORMANCE_MONITORING
QUERY_BASELINES:
  ```sql
-- Measure RLS-enabled query performance
SELECT * FROM records WHERE user_id = auth.uid();
-- Expected: <50ms

-- Measure complex JOIN performance
SELECT r.*, u.name FROM records r
JOIN users u ON r.user_id = u.id
WHERE r.user_id = auth.uid();
-- Expected: <200ms
  ```
DEGRADATION_THRESHOLD::"If current > baseline + 20%, investigate"
RLS_OVERHEAD:
  ```sql
-- Disable RLS (admin/testing only)
ALTER TABLE records DISABLE ROW LEVEL SECURITY;
EXPLAIN ANALYZE SELECT * FROM records WHERE user_id = 'uuid';
-- Note baseline time: X ms

-- Enable RLS
ALTER TABLE records ENABLE ROW LEVEL SECURITY;
EXPLAIN ANALYZE SELECT * FROM records WHERE user_id = 'uuid';
-- Note RLS time: Y ms

-- Calculate overhead: (Y - X) / X * 100%
-- Target: <20% overhead
  ```
§7::STATE_VERIFICATION_COMMANDS
QUICK_CHECK:
  ```bash
# Local migration count
ls supabase/migrations/*.sql | wc -l

# Remote migration count (via MCP tool)
mcp__supabase__list_migrations({ project_id })
  ```
DETAILED_ANALYSIS:
  ```javascript
const local = await readLocalMigrations();
const remote = await mcp__supabase__list_migrations({ project_id });
const tables = await mcp__supabase__list_tables({ project_id });
const advisors = await mcp__supabase__get_advisors({
  project_id,
  type: 'security'
});
generateStateReport({ local, remote, tables, advisors });
  ```
§8::ANTI_PATTERNS
NEVER::[
  "Assume local/remote sync without validation",
  "Apply migrations without checking remote state first",
  "Ignore missing migrations in local repository",
  "Skip state documentation after operations",
  "Apply migrations from multiple developers simultaneously",
  "Modify production schema without migration files"
]
===END===
