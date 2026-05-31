===ADR_003_COMPLIANCE===
META:
  TYPE::SUPPORTING_DOCUMENTATION
  VERSION::"1.0"
  PURPOSE::"ADR-003 Compliance Checklist"
  STATUS::ACTIVE
  CANONICAL::".hestai-sys/library/skills/supabase-operations/adr-003-compliance.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/skills/supabase-operations/adr-003-compliance.oct.md"
OVERVIEW::"ADR-003 governs schema migration standards for the 7-app ecosystem, ensuring backwards-compatible additive patterns that prevent breaking changes across applications."
§1::CORE_PRINCIPLES
BACKWARDS_COMPATIBLE_ADDITIVE:
  RULE::"Schema changes must be additive only — new apps use new features, old apps continue functioning"
  ALLOWED::[
    "ADD COLUMN with DEFAULT value",
    "CREATE TABLE (new tables don't break old apps)",
    "CREATE INDEX (performance improvement, no schema impact)",
    "ADD CONSTRAINT (if doesn't conflict with existing data)"
  ]
  PROHIBITED_WITHOUT_DEPRECATION::[
    "ALTER COLUMN (changing type, removing DEFAULT)",
    "DROP COLUMN (removes data old apps expect)",
    "DROP TABLE (catastrophic for old apps)",
    "RENAME COLUMN (breaks old apps expecting old name)",
    "RENAME TABLE (breaks all references)"
  ]
COMPONENT_FK_INTEGRITY:
  RULE::"All component tables must reference component_id foreign key pattern for ecosystem consistency"
  VALIDATION:
    ```sql
-- Check: Do all component tables have component_id FK?
SELECT table_name
FROM information_schema.tables
WHERE table_name LIKE '%_component%'
  AND table_name NOT IN (
    SELECT table_name
    FROM information_schema.columns
    WHERE column_name = 'component_id'
  );
    ```
  EXPECTED::"Empty result (all component tables have component_id)"
MULTI_APP_TESTING:
  RULE::"Schema changes validated across all 7 apps before production deployment"
  REQUIRED_APPS::[
    "scripts-web (main application)",
    admin-dashboard,
    client-portal,
    reporting-engine,
    integration-service,
    analytics-pipeline,
    mobile-api
  ]
  CHECKLIST::[
    "[ ] New columns have DEFAULT or are nullable (old apps won't provide values)",
    "[ ] New tables don't conflict with existing table names",
    "[ ] FK constraints reference existing tables",
    "[ ] No breaking changes to existing columns",
    "[ ] Triggers/functions don't break old query patterns"
  ]
DEPRECATION_CYCLE:
  RULE::"Breaking changes require 14-day deprecation period with fallback compatibility"
  PROCESS::[
    "Day 0: Add new column/table (additive change)",
    "Day 0-14: Dual-write pattern (write to both old and new)",
    "Day 14: Notify all teams of upcoming deprecation",
    "Day 14-28: Monitor old column usage (should decrease to 0)",
    "Day 28: Remove old column (if usage = 0)"
  ]
  RENAME_EXAMPLE:
    ```sql
-- Day 0: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);
UPDATE users SET email_address = email; -- Backfill

-- Day 0-14: Dual-write pattern in application code

-- Day 28: Drop old column
ALTER TABLE users DROP COLUMN email; -- After verification
    ```
EMERGENCY_ROLLBACK:
  RULE::"Migration reversal procedure documented for production incidents"
  TEMPLATE:
    ```sql
-- Rollback for: [Migration Description]
-- Created: [Timestamp]
-- Author: [Developer]

-- Step 1: Verify current state
SELECT column_name FROM information_schema.columns
WHERE table_name = 'table_name';

-- Step 2: Reverse migration
[REVERSE DDL STATEMENTS]

-- Step 3: Verify rollback success
SELECT column_name FROM information_schema.columns
WHERE table_name = 'table_name';

-- Step 4: Document incident
    ```
§2::COMPLIANCE_CHECKLIST
SCHEMA_CHANGE_TYPE::[
  "[ ] Identify change type (ADD COLUMN, CREATE TABLE, ALTER COLUMN, etc.)",
  "[ ] Verify it's additive OR has 14-day deprecation plan",
  "[ ] Document rationale for breaking changes (if any)"
]
BACKWARDS_COMPAT::[
  "[ ] New columns have DEFAULT values OR are nullable",
  "[ ] New tables don't use names conflicting with existing tables",
  "[ ] Renamed columns use deprecation cycle (dual-write pattern)",
  "[ ] Dropped columns verified as unused (0 queries in logs)"
]
FK_INTEGRITY::[
  "[ ] If creating component table -> includes component_id FK",
  "[ ] If adding FK -> references existing table",
  "[ ] If modifying FK -> doesn't break existing references"
]
MULTI_APP_IMPACT::[
  "[ ] List all 7 apps potentially affected",
  "[ ] For each app: Will old version break? (Should be NO)",
  "[ ] If YES -> implement compatibility layer or dual-write",
  "[ ] Test each app with new schema in staging"
]
ROLLBACK_PREP::[
  "[ ] Write reverse migration SQL",
  "[ ] Test rollback in staging",
  "[ ] Document rollback procedure",
  "[ ] Identify rollback trigger conditions (errors, performance degradation)"
]
DOCUMENTATION::[
  "[ ] Migration file has descriptive name",
  "[ ] Comments explain WHY (not just WHAT)",
  "[ ] Breaking changes documented in ADR-003 exceptions log",
  "[ ] Team notified via communication channel"
]
§3::COMMON_VIOLATIONS
ALTER_WITHOUT_DEPRECATION:
  VIOLATION:
    ```sql
-- VIOLATION: Changes column type without deprecation
ALTER TABLE users ALTER COLUMN age TYPE VARCHAR(10);
    ```
  FIX:
    ```sql
-- COMPLIANT: Add new column, dual-write, deprecate old
ALTER TABLE users ADD COLUMN age_text VARCHAR(10);
UPDATE users SET age_text = age::VARCHAR;
-- [14-day deprecation cycle]
-- ALTER TABLE users DROP COLUMN age; -- After verification
    ```
MISSING_DEFAULT:
  VIOLATION:
    ```sql
-- VIOLATION: New column without DEFAULT
ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) NOT NULL;
    ```
  FIX:
    ```sql
-- COMPLIANT: New column with DEFAULT
ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free';
    ```
DROP_WITHOUT_VERIFICATION:
  VIOLATION:
    ```sql
-- VIOLATION: Dropping column without usage check
ALTER TABLE users DROP COLUMN legacy_id;
    ```
  FIX:
    ```sql
-- COMPLIANT: Verify usage before drop
-- Step 1: Check application logs for queries using legacy_id
-- Step 2: If usage = 0 for 14 days, proceed
ALTER TABLE users DROP COLUMN legacy_id; -- Verified 0 usage in logs
    ```
MISSING_COMPONENT_FK:
  VIOLATION:
    ```sql
-- VIOLATION: Component table without component_id
CREATE TABLE video_component (
  id UUID PRIMARY KEY,
  video_url TEXT
);
    ```
  FIX:
    ```sql
-- COMPLIANT: Includes component_id FK
CREATE TABLE video_component (
  id UUID PRIMARY KEY,
  component_id UUID NOT NULL REFERENCES components(id),
  video_url TEXT
);
    ```
§4::EXCEPTIONS_LOG
PURPOSE::"Document unavoidable breaking changes"
TEMPLATE::[
  "Exception: [Description]",
  "Date: [Timestamp]",
  "Migration: [Migration file name]",
  "Violation: [Which ADR-003 rule violated]",
  "Justification: [Why exception is necessary]",
  "Mitigation: [How breaking change was handled]",
  "Impact: [Which apps affected, how tested]",
  "Approval: [Who approved exception]"
]
§5::ENFORCEMENT
PRE_MIGRATION::[
  "ADR-003 checklist must be completed",
  "Breaking changes require exception approval",
  "Multi-app testing required for all schema changes"
]
POST_MIGRATION::[
  "get_advisors validation (0 errors/warnings)",
  "Monitor application logs for errors",
  "Track old column usage during deprecation cycle"
]
VIOLATIONS::[
  "Rollback non-compliant migrations immediately",
  "Document violation in lessons learned",
  "Update checklist to prevent recurrence"
]
===END===
