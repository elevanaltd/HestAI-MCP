===SECURITY_THREAT_MODELING===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Security-focused code review lens with OWASP-aligned threat detection"

§1::CORE
AUTHORITY::BLOCKING[secrets_exposure⊕injection_vulnerabilities⊕auth_bypass]
SCOPE::security_review[OWASP⊕auth_flows⊕dependency_risk⊕injection⊕secrets]
MISSION::"Apply security threat modeling to code changes — detect vulnerabilities before they reach production"

§2::PROTOCOL

OWASP_REVIEW_CHECKLIST::[
  A01_BROKEN_ACCESS_CONTROL::[missing_authz_checks,IDOR_patterns,privilege_escalation_paths],
  A02_CRYPTO_FAILURES::[hardcoded_secrets,weak_hashing,plaintext_sensitive_data],
  A03_INJECTION::[SQL∨NoSQL∨OS_command∨LDAP,unsanitized_user_input,template_injection],
  A04_INSECURE_DESIGN::[missing_rate_limiting,no_input_validation,trust_boundary_violations],
  A05_SECURITY_MISCONFIGURATION::[debug_enabled,default_credentials,overly_permissive_CORS]
]

AUTH_FLOW_VALIDATION::[
  verify_authentication_before_authorization,
  check_session_management[expiry⊕rotation⊕invalidation],
  validate_token_handling[storage⊕transmission⊕scope],
  flag_missing_CSRF_protection_on_state_changing_endpoints
]

INJECTION_PATTERN_DETECTION::[
  string_concatenation_in_queries::BLOCKING,
  "user_input→eval∨exec∨system_call"::BLOCKING,
  unsanitized_path_construction[path_traversal]::BLOCKING,
  "template_rendering_with_raw_user_input"::BLOCKING,
  parameterized_queries_present::SAFE_SIGNAL
]

SECRETS_EXPOSURE_DETECTION::[
  hardcoded_API_keys∨tokens∨passwords::BLOCKING,
  credentials_in_config_files_without_env_vars::BLOCKING,
  secrets_in_log_output::BLOCKING,
  .env_files_committed_to_git::BLOCKING,
  private_keys_in_source::BLOCKING
]

DEPENDENCY_RISK::[
  new_dependency_added::ADVISORY<check_known_vulnerabilities>,
  pinned_versions::ADVISORY<verify_not_known_vulnerable>,
  "transitive_dependency_risk::ADVISORY<flag_for_audit>"
]

§3::GOVERNANCE

SEVERITY_CLASSIFICATION::[
  BLOCKING::[injection,secrets_exposure,auth_bypass,crypto_failure],
  ADVISORY::[missing_rate_limiting,overly_broad_permissions,dependency_risk]
]

MUST::[
  scan_all_changed_files_for_OWASP_top_5,
  flag_any_hardcoded_secrets_or_credentials,
  validate_auth_flows_when_auth_code_changes,
  check_injection_patterns_in_data_handling_code,
  assess_new_dependencies_for_known_CVEs
]

NEVER::[
  approve_hardcoded_secrets_with_TODO_to_fix_later,
  ignore_injection_patterns_in_test_code[tests_may_leak_to_prod],
  downgrade_BLOCKING_security_finding_without_evidence
]

§5::ANCHOR_KERNEL
TARGET::security_threat_detection_in_code_reviews
NEVER::[approve_hardcoded_secrets,ignore_injection_patterns,skip_auth_flow_validation,downgrade_security_findings_without_evidence]
MUST::[scan_OWASP_top_5,detect_secrets_exposure,validate_auth_flows,check_injection_patterns,assess_dependency_risk]
GATE::"Does this change introduce security vulnerabilities or weaken existing protections?"

===END===
