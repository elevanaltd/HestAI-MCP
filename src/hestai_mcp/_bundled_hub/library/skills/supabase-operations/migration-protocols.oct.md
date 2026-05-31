===MIGRATION_PROTOCOLS===
META:
  TYPE::SUPPORTING_DOCUMENTATION
  VERSION::"1.0"
  PURPOSE::"Migration Validation Protocols"
  STATUS::ACTIVE
  CANONICAL::".hestai-sys/library/skills/supabase-operations/migration-protocols.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/skills/supabase-operations/migration-protocols.oct.md"
§1::MIGRATION_WORKFLOW
STEPS::[
  "1: Validate local migration files exist",
  "2: Query remote migration state via list_migrations",
  "3: Compare local vs remote state — detect divergence",
  "4: Validate ADR-003 compliance",
  "5: Execute migration (CI preferred, MCP fallback)",
  "6: Verify with get_advisors (zero-tolerance gate)",
  "7: Update living protocol"
]
§2::STEP_1_VALIDATE_LOCAL
VALIDATE:
  FORMAT::YYYYMMDDHHMMSS_description.sql
  CHECK::[
    "Migration files present with timestamp naming",
    "File names are descriptive and indicate purpose",
    "No conflicting timestamps with remote migrations"
  ]
BASH_EXAMPLE:
  ```bash
ls supabase/migrations/*.sql
  ```
§3::STEP_2_QUERY_REMOTE_STATE
TOOL::mcp__supabase__list_migrations
EXPECTED_RESPONSE::[
  "List of applied migrations with timestamps",
  "Migration names and descriptions",
  "Application timestamps"
]
BASH_EXAMPLE:
  ```bash
mcp__supabase__list_migrations(project_id)
  ```
§4::STEP_3_COMPARE_LOCAL_VS_REMOTE
DIVERGENCE_DETECTION::[
  "Local migrations NOT in remote = pending migrations",
  "Remote migrations NOT in local = state drift (requires investigation)",
  "Matching migrations = synchronized state"
]
COMMON_PATTERNS::[
  "Developer applied migrations directly without committing to git",
  "Multiple developers created migrations simultaneously",
  "Migration rollback without removing file"
]
§5::STEP_4_ADR_003_COMPLIANCE
SEE::"adr-003-compliance.oct.md for complete checklist"
VERIFY::[
  "Backwards-compatible additive pattern (ADD COLUMN, not ALTER/DROP)",
  "Component FK integrity preserved",
  "Multi-app compatibility maintained",
  "Deprecation cycle followed for breaking changes (14 days)"
]
§6::STEP_5_EXECUTE_MIGRATION
PREFERRED::"CI Pipeline Deployment (Gated Auto-Deploy)"
CI_STEPS::[
  "Create PR with migration files in supabase/migrations/",
  "Add deploy-migrations label to PR",
  "CI validates locally (lint, reset, tests, schema lint)",
  "Merge to main triggers production deployment",
  "Audit log entry created automatically"
]
CI_BENEFITS::[
  "No drift between code and schema",
  "All migrations tied to git commits",
  "Automatic audit trail",
  "Requires CI checks to pass first"
]
FALLBACK::"Direct MCP Application — use only when CI unavailable or emergency"
TOOL_SELECTION::["apply_migration: DDL operations (CREATE, ALTER, DROP with deprecation)","execute_sql: DML operations, data migrations, temporary operations"]
WARNING::"Direct MCP bypasses CI validation. Always: create local file first, commit to git after, document why CI was bypassed"
§7::STEP_6_VERIFY_WITH_ADVISORS
COMMANDS:
  ```bash
mcp__supabase__get_advisors(project_id, type: "security")
mcp__supabase__get_advisors(project_id, type: "performance")
  ```
ZERO_TOLERANCE::[
  "0 errors required",
  "0 warnings required",
  "Any violations = investigate and remediate"
]
COMMON_ISSUES::[
  "Missing RLS policies on new tables",
  "Index opportunities for foreign keys",
  "Permission issues",
  "Column type mismatches"
]
§8::STEP_7_UPDATE_LIVING_PROTOCOL
DOCUMENT::[
  "Current schema version (latest migration timestamp)",
  "Last sync timestamp",
  "Active RLS policies",
  "Any novel patterns discovered during migration"
]
LOCATION::"/Users/shaunbuswell/.claude/protocols/SUPABASE-OPERATIONS.md"
§9::MIGRATION_TYPES
DDL_USE_APPLY_MIGRATION::[
  "CREATE TABLE",
  "ALTER TABLE ADD COLUMN (with DEFAULT for backwards compatibility)",
  "CREATE INDEX",
  "ALTER TABLE ADD CONSTRAINT (FK, CHECK)",
  "CREATE FUNCTION",
  "CREATE TRIGGER"
]
DDL_BENEFITS::[
  "Tracked in migration history",
  "Reversible through rollback procedures",
  Auditable
]
DML_USE_EXECUTE_SQL::[
  "INSERT data migrations",
  "UPDATE existing records",
  "DELETE cleanup operations",
  "Complex transformations"
]
DML_CAUTION::[
  "Not automatically reversible",
  "Document rollback SQL separately",
  "Test with small batches first"
]
§10::EMERGENCY_ROLLBACK
SCENARIO::"Migration causes production issues"
STEPS::[
  "Assess impact (tables affected, data integrity)",
  "Create reverse migration SQL",
  "Test reverse migration in staging",
  "Apply reverse migration via apply_migration",
  "Document incident in living protocol",
  "Add preventive validation to Step 4"
]
ROLLBACK_PATTERNS::[
  "DROP COLUMN: requires data backup first (destructive)",
  "ADD COLUMN: DROP COLUMN (safe if no data written)",
  "CREATE INDEX: DROP INDEX (always safe)",
  "ALTER COLUMN: Complex (may require data migration)"
]
§11::BEST_PRACTICES
BEFORE::[
  "Read ADR-003 compliance requirements",
  "Verify local/remote sync",
  "Test in staging environment",
  "Document rollback procedure",
  "Notify team of pending schema change"
]
DURING::[
  "Use apply_migration for DDL (trackable)",
  "Monitor execution time (timeout risk)",
  "Watch for lock conflicts"
]
AFTER::[
  "Run get_advisors for validation",
  "Verify 0 errors/warnings",
  "Update living protocol",
  "Generate TypeScript types if applicable",
  "Test affected applications"
]
§12::ANTI_PATTERNS
NEVER::[
  "Skip local/remote sync validation",
  "Apply migrations without ADR-003 compliance check",
  "Ignore advisor warnings/errors",
  "Apply breaking changes without 14-day deprecation cycle",
  "Bypass migration protocol for urgent changes",
  "Modify production schema directly without migration files",
  "Use MCP apply_migration without creating local file first (causes drift)",
  "Skip CI deployment flow for convenience"
]
§13::CI_DEPLOYMENT_REFERENCE
LOCATION::".github/workflows/ci.yml (deploy-migrations job)"
REQUIRED_SECRET::"SUPABASE_ACCESS_TOKEN in GitHub repo settings"
LABEL::"deploy-migrations (must be on PR before merge)"
AUDIT::"Deployments recorded in audit_log table"
AUDIT_FIELDS::["action: ci_migration_deploy","details: commit_sha, actor, pr_number, pr_title"]
DR_PLAYBOOK::".hestai/state/context/docs/001-OPS-DISASTER-RECOVERY-PLAYBOOK.md"
===END===
