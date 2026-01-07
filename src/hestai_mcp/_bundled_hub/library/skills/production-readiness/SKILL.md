===SKILL:PRODUCTION_READINESS===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Production readiness validation and domain accountability for critical systems"

§1::VALIDATION_FRAMEWORK
CRITICAL_LENSES::WILL_IT_BREAK×WILL_IT_SCALE×WHO_MAINTAINS×WHAT_ATTACKS×WHY_COMPLEX
  WILL_IT_BREAK::[single_points_of_failure, edge_cases, race_conditions]
  WILL_IT_SCALE::[10x_load_capacity, bottleneck_identification, resource_limits]
  WHO_MAINTAINS::[3am_debuggability, documentation, operational_runbooks]
  WHAT_ATTACKS::[attack_surface, vulnerability_assessment, defense_depth]
  WHY_COMPLEX::[justify_abstractions, simplification_opportunities]

§2::DOMAIN_ACCOUNTABILITY
DOMAINS::[
  AUTH_DOMAIN::[jwt_strategy, session_management, oauth_flows],
  SECRETS_MANAGEMENT::[vault_integration, rotation_policies],
  DEPLOYMENT_PIPELINE::[ci_cd_configuration, rollout_strategies],
  PERFORMANCE_MONITORING::[metrics_collection, alerting_thresholds],
  SECURITY_SCANNING::[vulnerability_assessment, dependency_audit],
  COMPLIANCE_VALIDATION::[regulatory_requirements, audit_trails],
  ARCHITECTURE_DECISIONS::[pattern_selection, scaling_strategies],
  TEST_INFRASTRUCTURE::[framework_selection, coverage_requirements]
]

§3::ARTIFACT_REQUIREMENTS
MANDATORY_EVIDENCE::[
  "System scales to 10x load"→"Load test report showing 10x capacity",
  "Zero-downtime deployment"→"Canary deployment logs + rollback test",
  "Security hardened"→"Penetration test report + OWASP compliance",
  "Production ready"→"Monitoring setup + runbook + incident response"
]

===END===
