===RLS_OPTIMIZATION===
META:
  TYPE::SUPPORTING_DOCUMENTATION
  VERSION::"1.0"
  PURPOSE::"RLS Optimization Patterns"
  STATUS::ACTIVE
  CANONICAL::".hestai-sys/library/skills/supabase-operations/rls-optimization.oct.md"
  SOURCE::"src/hestai_mcp/_bundled_hub/library/skills/supabase-operations/rls-optimization.oct.md"
§1::PERFORMANCE_TARGETS
QUERY_TARGETS::[
  "Simple SELECT: <50ms with RLS enforcement",
  "Complex JOINs: <200ms with multi-table RLS",
  "Write operations: <500ms including triggers and RLS validation"
]
§2::INITPLAN_OPTIMIZATION
IMPROVEMENT::"~70% faster (150ms -> 45ms)"
PROBLEM::"RLS policies using auth.uid() in subqueries cause sequential scans"
SOLUTION::"Structure policies to enable InitPlan optimization"
BAD_PATTERN:
  ```sql
CREATE POLICY "client_select" ON records
FOR SELECT USING (
  user_id IN (
    SELECT user_id FROM client_assignments WHERE client_id = auth.uid()
  )
);
  ```
GOOD_PATTERN:
  ```sql
CREATE POLICY "client_select" ON records
FOR SELECT USING (
  user_id = auth.uid()
);
  ```
PERFORMANCE_IMPACT::[
  "Before: 150ms (sequential scan over client_assignments)",
  "After: 45ms (index lookup on user_id)",
  "Improvement: ~70% faster"
]
USE_WHEN::[
  "Admin/client access pattern separation",
  "Direct user ownership relationships",
  "Simple authorization rules"
]
§3::POLICY_CONSOLIDATION
IMPROVEMENT::"50% reduction in RLS overhead"
PROBLEM::"Multiple overlapping policies create redundant authorization checks"
BAD_PATTERN:
  ```sql
CREATE POLICY "admin_select" ON records FOR SELECT USING (is_admin());
CREATE POLICY "owner_select" ON records FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "public_select" ON records FOR SELECT USING (is_public = true);
  ```
GOOD_PATTERN:
  ```sql
CREATE POLICY "unified_select" ON records
FOR SELECT USING (
  is_admin() OR user_id = auth.uid() OR is_public = true
);
  ```
PERFORMANCE_IMPACT::[
  "Before: 3 policy evaluations per row",
  "After: 1 policy evaluation per row",
  "Improvement: 50% reduction in RLS overhead"
]
USE_WHEN::[
  "Multiple authorization rules for same operation",
  "Performance-critical queries",
  "High-frequency access patterns"
]
§4::SECURITY_DEFINER_PROTECTION
PROBLEM::"SECURITY DEFINER functions vulnerable to search_path injection"
BAD_PATTERN:
  ```sql
CREATE FUNCTION get_user_records()
RETURNS SETOF records
SECURITY DEFINER
AS $$
  SELECT * FROM records WHERE user_id = current_user_id();
$$;
  ```
GOOD_PATTERN:
  ```sql
CREATE FUNCTION get_user_records()
RETURNS SETOF records
SECURITY DEFINER
SET search_path = public, pg_temp
LANGUAGE plpgsql
AS $$
  SELECT * FROM records WHERE user_id = current_user_id();
$$;
  ```
SECURITY_IMPACT::["Prevents function injection attacks via malicious search_path manipulation","Ensures function operates in controlled schema namespace"]
USE_WHEN::[
  "Always when using SECURITY DEFINER",
  "Functions that bypass RLS",
  "Functions with elevated privileges"
]
§5::ROLE_BASED_PATTERN_SEPARATION
ADMIN_PATTERN:
  ```sql
CREATE POLICY "admin_all" ON records
FOR ALL USING (
  is_admin() -- Custom function checking auth.jwt() claims
);
  ```
CLIENT_PATTERN:
  ```sql
CREATE POLICY "client_select" ON records
FOR SELECT USING (
  user_id = auth.uid()
);
  ```
BENEFITS::[
  "Clear authorization boundaries",
  "Easy to audit access patterns",
  "Performance-optimized for each role",
  "Simple mental model"
]
§6::RLS_DESIGN_PRINCIPLES
PERFORMANCE_FIRST::[
  "Prefer direct equality checks: user_id = auth.uid()",
  "Use indexes on RLS columns",
  "Avoid subqueries when possible (InitPlan pattern)",
  "Test with EXPLAIN ANALYZE"
]
CONSOLIDATION::[
  "Combine similar policies with OR conditions",
  "Use role-based functions for complex logic",
  "Avoid redundant authorization checks"
]
EXPLICIT_SECURITY::[
  "Always SET search_path on SECURITY DEFINER functions",
  "Document privilege elevation",
  "Audit bypass scenarios"
]
TESTABILITY::[
  "Test with anon key (enforces RLS)",
  "Test with service key (bypasses RLS)",
  "Verify both access grant AND denial"
]
§7::ANTI_PATTERNS
COMPLEX_SUBQUERIES:
  ```sql
-- DON'T: Nested subqueries kill performance
CREATE POLICY "complex" ON records
FOR SELECT USING (
  id IN (
    SELECT record_id FROM permissions
    WHERE user_id IN (
      SELECT id FROM users WHERE team_id = get_team()
    )
  )
);
  ```
COMPLEX_SUBQUERIES_FIX::"Flatten with JOINs or use materialized views"
MISSING_INDEXES:
  ```sql
-- DON'T: RLS columns without indexes
CREATE POLICY "select" ON records
FOR SELECT USING (user_id = auth.uid());
-- Missing: CREATE INDEX idx_records_user_id ON records(user_id);
  ```
MISSING_INDEXES_FIX::"Create indexes on ALL RLS filter columns"
OVERLY_PERMISSIVE:
  ```sql
-- DON'T: Security theater
CREATE POLICY "everyone" ON records
FOR SELECT USING (true);
  ```
OVERLY_PERMISSIVE_FIX::"Implement actual authorization logic or disable RLS if truly public"
§8::PERFORMANCE_BENCHMARKING
BASELINE_MEASUREMENT:
  ```sql
-- Disable RLS to get baseline
ALTER TABLE records DISABLE ROW LEVEL SECURITY;
EXPLAIN ANALYZE SELECT * FROM records WHERE user_id = 'uuid';
-- Note baseline time

-- Enable RLS to measure overhead
ALTER TABLE records ENABLE ROW LEVEL SECURITY;
EXPLAIN ANALYZE SELECT * FROM records WHERE user_id = 'uuid';
-- Compare to baseline
  ```
BASELINE_TARGET::"RLS overhead should be <20% of baseline query time"
INITPLAN_DETECTION:
  ```sql
EXPLAIN ANALYZE SELECT * FROM records;
  ```
INITPLAN_SIGNALS::["InitPlan in query plan = Good (constant-time auth check)","Seq Scan on auth tables = Bad (linear-time auth check)"]
POLICY_COUNT_CHECK:
  ```sql
SELECT schemaname, tablename, policyname
FROM pg_policies
WHERE tablename = 'records';
  ```
POLICY_COUNT_TARGET::"1-2 policies per operation (more = overhead)"
§9::RLS_APPLICATION_PATTERNS
ADMIN_DASHBOARD::[
  "Use service role key to bypass RLS",
  "Implement application-level authorization",
  "Log all admin operations"
]
MULTI_TENANT_SAAS::[
  "RLS enforces tenant isolation",
  "Use tenant_id in all policies",
  "Index tenant_id columns"
]
PUBLIC_PRIVATE_DATA::[
  "Separate policies for public vs authenticated",
  "Use is_public column for public data",
  "Cache public data aggressively (no RLS overhead)"
]
§10::TROUBLESHOOTING
SYMPTOM::"Slow queries with RLS enabled"
DIAGNOSIS_STEPS::[
  "Compare baseline (RLS disabled) vs actual (RLS enabled)",
  "Check EXPLAIN ANALYZE for Sequential Scans",
  "Verify indexes exist on RLS filter columns",
  "Count number of policies evaluated",
  "Look for InitPlan optimization opportunities"
]
COMMON_FIXES::[
  "Add indexes to RLS columns",
  "Consolidate multiple policies",
  "Restructure for InitPlan pattern",
  "Cache auth.uid() calls in policy functions"
]
===END===
