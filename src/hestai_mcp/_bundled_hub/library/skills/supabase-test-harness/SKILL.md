---
name: supabase-test-harness
description: Supabase test harness patterns including local Supabase setup, test user creation via Auth Admin API, RLS testing, migration testing (db_reset), seed sequences, rate limiting, and environment detection. Use when setting up Supabase testing infrastructure, creating test users, troubleshooting Supabase test failures, or implementing RLS validation. Triggers on: supabase test setup, test user creation, supabase local testing, RLS testing, migration testing, supabase test harness, auth test helpers.
allowed-tools: ["Read"]
triggers: ["supabase test setup", "test user creation", "supabase local testing", "RLS testing", "migration testing", "supabase test harness", "auth test helpers", "supabase db reset test", "supabase seed sequence", "auth admin api test", "supabase rate limiting"]
version: "1.0.0"
---

===SUPABASE_TEST_HARNESS===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Supabase test harness patterns: local setup, Auth Admin API test users, RLS validation, migration testing, seed sequences, rate limiting, environment detection"

SUPABASE_TEST_MASTERY::[LOCAL_SETUP+AUTH_ADMIN_API+RLS_VALIDATION+MIGRATION_TESTING+SEED_SEQUENCES]→PRODUCTION_READY

§1::PRIMARY_SOURCE_MANDATORY_FIRST

SOURCE::.hestai/state/context/test-context/RULES.md
PRINCIPLE::"POC-proven pattern post-it note — ALWAYS consult BEFORE infrastructure decisions"

CONTAINS::[
  supabase_setup[local_env],
  test_users[standardized_credentials],
  migration_testing[supabase_db_reset],
  fail_fast_guards
]

§2::DETAILED_DOCUMENTATION

SUPABASE_HARNESS::.hestai/state/context/test-context/SUPABASE-TEST-HARNESS.md→[
  local_setup[docker∨cli],
  test_user_creation[auth_admin_api],
  RLS_testing,
  seed_procedures,
  preview_branch_integration,
  env_config
]

§3::POC_REFERENCE_WHEN_NEEDED

PROVEN_INFRASTRUCTURE::/Volumes/HestAI-Projects/eav-ops/eav-apps/scripts-web/src/test/
FILES::[
  supabase-test-client.ts::"Test client with environment detection, fail-fast guards",
  auth-helpers.ts::"Auth utilities with rate limiting (750ms delay)"
]

OPERATIONAL_SCRIPTS::/Volumes/HestAI-Projects/eav-ops/eav-apps/scripts-web/scripts/
FILES::[
  create-test-users-via-api.mjs::"Test user creation via Auth Admin API (used by CI)"
]

§4::CRITICAL_PATTERNS_POC_PROVEN

PATTERN_1::MIGRATION_TESTING::[
  USE::supabase_db_reset_local[NOT_db_push],
  BECAUSE::"EMERGENCY FIX 2025-10-26 — db push fails with complex trigger functions",
  EVIDENCE::POC_ci.yml:105
]

PATTERN_2::TEST_USER_CREATION::[
  METHOD::auth_admin_api_via_scripts/create-test-users-via-api.mjs[NOT_SQL],
  BECAUSE::"Ensures proper GoTrue internal state (auth.users + auth.identities)",
  EVIDENCE::[POC_ci.yml:144-161, POC_scripts/create-test-users-via-api.mjs]
]

PATTERN_3::RATE_LIMITING::[
  DELAY::750ms_between_auth_operations,
  IMPLEMENTATION::authDelay()_helper,
  BECAUSE::"Prevents Supabase rate limit failures",
  EVIDENCE::POC_src/test/supabase-test-client.ts:121-131
]

PATTERN_4::FAIL_FAST_GUARDS::[
  DETECTION::CI_misconfiguration[hardcoded_urls_blocking_preview],
  CODE::"if(SUPABASE_PREVIEW_URL && SUPABASE_URL.includes('127.0.0.1'))→throw('CI_MISCONFIGURATION')",
  BECAUSE::"Prevents 50+ minute CI hangs",
  EVIDENCE::POC_src/test/supabase-test-client.ts:75-81
]

PATTERN_5::ENVIRONMENT_PRIORITY::[
  ORDER::SUPABASE_PREVIEW_URL > 127.0.0.1:54321 > VITE_SUPABASE_URL,
  BECAUSE::"Automatic environment detection (CI preview > local > remote fallback)",
  EVIDENCE::POC_src/test/supabase-test-client.ts:37-41
]

PATTERN_6::SEED_SEQUENCE::[
  ORDER::migrations→test_users_via_auth_api→seed_data_via_sql,
  BECAUSE::"Order matters for FK constraints (users must exist before data references them)",
  EVIDENCE::POC_ci.yml:100-168
]

§5::TEST_USERS_STANDARDIZED

CREDENTIALS::[
  admin::{email:admin.test@example.com, password:test-password-admin-123},
  client::{email:client.test@example.com, password:test-password-client-123},
  unauthorized::{email:unauthorized.test@example.com, password:test-password-unauth-123}
]
SOURCE::POC_src/test/supabase-test-client.ts:102-115

§6::ENVIRONMENT_CONFIGURATION

ROOT_ENV::[
  SUPABASE::[VITE_SUPABASE_URL:https://project.supabase.co, VITE_SUPABASE_PUBLISHABLE_KEY:sb_publishable_*, SUPABASE_SECRET_KEY:sb_secret_*]
]

CI_OVERRIDES::[
  SUPABASE_PREVIEW_URL:https://preview-branch.supabase.co,
  SUPABASE_PREVIEW_ANON_KEY:sb_publishable_preview_*,
  VITEST_INTEGRATION:true
]

§7::GITGUARDIAN_EXCLUSIONS

PATH_EXCLUSIONS::[packages/*/src/test/**, apps/*/src/test/**, **/*.test.ts(x)]
PATTERN_EXCLUSIONS::[test-mock-.*, test-project\.supabase\.co, 127\.0\.0\.1:54321, test-password-(admin|client|unauth)-123]
RATIONALE::"Real credentials in .env (gitignored), test fixtures non-functional"

§8::AGENT_CONSULTATION

CONSULT::[
  security-specialist::"Credential management, GitGuardian patterns, test data isolation",
  critical-engineer::"Production risk from test infrastructure failures",
  universal-test-engineer::"Actual test writing (delegate, don't implement)"
]

§9::KNOWLEDGE_BASE_REFERENCES

PRIMARY::.hestai/state/context/test-context/RULES.md[POC_proven_patterns]→CONSULT_FIRST

DOCUMENTATION::[
  .hestai/state/context/test-context/SUPABASE-TEST-HARNESS.md
]

POC_REFERENCE::[
  /Volumes/HestAI-Projects/eav-ops/eav-apps/scripts-web/src/test/,
  /Volumes/HestAI-Projects/eav-ops/eav-apps/scripts-web/scripts/create-test-users-via-api.mjs
]

NORTH_STAR::.hestai/north-star/000-UNIVERSAL-EAV_SYSTEM-D1-NORTH-STAR.md[I7:TDD_RED_discipline, I8:production_grade_quality]

§10::ANCHOR_KERNEL
TARGET::"spec-compliant Supabase test harness guidance with POC-proven patterns"
NEVER::[
  use_db_push_for_migration_testing[use_db_reset_local],
  create_test_users_via_SQL[use_auth_admin_api],
  skip_rate_limiting_between_auth_ops,
  omit_fail_fast_guards_for_preview_detection,
  seed_data_before_test_users_exist
]
MUST::[
  consult_RULES_md_before_infrastructure_decisions,
  use_supabase_db_reset_local_for_migration_testing,
  create_test_users_via_auth_admin_api,
  apply_750ms_delay_between_auth_operations,
  follow_seed_sequence[migrations→test_users→seed_data]
]
GATE::"RULES.md consulted first? db reset used (not db push)? Auth Admin API for test users? Rate limiting applied? Seed sequence correct?"

===END===
