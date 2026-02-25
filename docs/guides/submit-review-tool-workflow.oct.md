===SUBMIT_REVIEW_GUIDE===
META:
  TYPE::AGENT_GUIDE
  VERSION::"2.1.0"
  PURPOSE::"Agent instructions for submit_review MCP tool usage"
  COMPRESSION_TIER::CONSERVATIVE
  LOSS_PROFILE::"~15% verbose phrasing, repetition"
  NARRATIVE_DEPTH::PRESERVED
  TARGET_AUDIENCE::AGENTS
§1::TOOL_IDENTITY
  NAME::submit_review
  PROTOCOL::"MCP[Model_Context_Protocol]"
  PURPOSE::"Post formatted PR comments to clear review-gate CI"
  CAPABILITIES::[
    post_review_comments,
    format_for_CI_validation,
    self_validate_APPROVED,
    structured_error_handling,
    dry_run_testing
  ]
  LIMITATION::"requires_existing_PR[GitHub_issue_API_constraint]"
§2::ACTIVATION_TRIGGERS
  USE_WHEN::[
    "Review PR requested",
    "IL self-review needed",
    "HO supervisory review after delegation",
    "CRS code quality review",
    "CE production readiness check",
    "Block or Conditional approval required"
  ]
  ROLE_MAPPING::[
    IL::"Implementation Lead[self_review]",
    HO::"Holistic Orchestrator[supervisory_review,T1_alternative]",
    CRS::"Code Review Specialist[code_quality]",
    CE::"Critical Engineer[production_readiness]"
  ]
§3::PARAMETERS
  REQUIRED::[
    repo::"STRING[owner/name format]",
    pr_number::"INTEGER[existing_PR_only]",
    role::"ENUM[IL,HO,CRS,CE]",
    verdict::"ENUM[APPROVED,BLOCKED,CONDITIONAL]",
    assessment::"STRING[non_empty,detailed_reasoning]"
  ]
  OPTIONAL::[
    dry_run::"BOOLEAN[default:false,test_without_posting]",
    model_annotation::"STRING[transparency:Claude,Gemini,Codex]"
  ]
  ADVISORY::"CRS without model_annotation gets warning re TIER_3_STRICT compatibility"
§4::REVIEW_TIERS
  TIER_0_EXEMPT::[
    TRIGGER::"only exempt files changed[md,tests,json,lock]",
    REQUIRED::NONE
  ]
  TIER_1_SELF::[
    TRIGGER::"non_exempt_lines_lt_50 AND single_non_exempt_file",
    REQUIRED::"IL_SELF_REVIEWED OR HO_REVIEWED",
    EXAMPLES::[
      README,
      config,
      small_fixes
    ]
  ]
  TIER_2_STANDARD::[
    TRIGGER::"non_exempt_lines[50-500] OR default_when_ambiguous",
    REQUIRED::"CRS_APPROVED AND CE_APPROVED",
    EXAMPLES::[
      features,
      bug_fixes,
      refactoring
    ]
  ]
  TIER_3_STRICT::[
    TRIGGER::"non_exempt_lines_gt_500 OR sql_changes",
    REQUIRED::"CRS_GEMINI_APPROVED AND CRS_CODEX_APPROVED AND CE_APPROVED",
    EXAMPLES::[
      major_features,
      redesigns,
      security_critical
    ]
  ]
§5::WORKFLOWS
  SIMPLE_TIER_1::"IL_implements→create_PR→submit_review[role:IL]→CI_validates→merge"
  HO_TIER_1::"HO_delegates_to_IL→IL_implements→create_PR→HO_submit_review[role:HO,verdict:APPROVED→REVIEWED]→CI_validates→merge"
  MULTI_AGENT::"IL_implements→create_PR→CRS_reviews→CE_reviews→IF[both_APPROVED]→merge ELSE→rework→re_review"
  DRAFT_STRATEGY::"create_draft→incremental_reviews→mark_ready→final_approvals→merge"
§6::USAGE_EXAMPLES
compatibility:
  ```python
await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="CRS",
    verdict="APPROVED",
    assessment="Logic correct, tests pass, no security issues",
    model_annotation="Gemini"
)
  ```
review:
  ```python
await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="CE",
    verdict="BLOCKED",
    assessment="Security vulnerability: SQL injection risk at line 45"
)
  ```
GitHub:
  ```python
await submit_review(
    repo="elevanaltd/HestAI-MCP",
    pr_number=123,
    role="CRS",
    verdict="APPROVED",
    assessment="Test review",
    dry_run=True
)
  ```
§7::RESPONSE_STRUCTURE
  SUCCESS::[
    success::true,
    comment_url::"STRING[GitHub_comment_URL]",
    formatted_comment::"STRING[posted_comment_text]",
    validation::[
      would_clear_gate::BOOLEAN,
      tier_requirements::STRING
    ],
    advisory::"STRING[present_when_CRS_missing_model_annotation]"
  ]
§8::ERROR_HANDLING
  ERROR_TYPES::[
    validation::"no_retry[input_invalid]",
    auth::"configure_env[add_GITHUB_TOKEN]",
    network::"retry_immediate[transient_failure]",
    rate_limit::"retry_backoff[wait_60s,exponential]",
    github_api::"check_PR_exists[404_or_other]"
  ]
errors:
  ```python
result = await submit_review(repo=repo, pr_number=pr, role="CRS",
                             verdict="APPROVED", assessment="...")
if not result["success"]:
    error = result["error_type"]
    if error == "rate_limit":
        await asyncio.sleep(60)
        result = await submit_review(...)
    elif error == "network":
        result = await submit_review(...)
    else:
        raise ReviewError(result["error"])
  ```
§9::CRITICAL_CONSTRAINTS
  RULES::[
    "PR_MUST_EXIST[cannot review commits outside PR]",
    "FORMAT_STRICT[invalid format rejected pre-post]",
    "ONLY_APPROVED_CLEARS[BLOCKED/CONDITIONAL provide feedback only]",
    "ASSESSMENT_SPECIFICITY[line numbers and files for BLOCKED/CONDITIONAL]",
    "DRY_RUN_FIRST[test format before production posting]",
    "MODEL_ANNOTATION_FOR_T3[CRS must annotate for dual-CRS compatibility]"
  ]
§10::COMMON_MISTAKES
  AVOID::[
    empty_assessment,
    wrong_role_for_agent_type,
    assuming_all_verdicts_clear_gates,
    posting_without_PR,
    ignoring_validation_errors,
    CRS_without_model_annotation_at_T3
  ]
§11::INTEGRATION_POINTS
  CI_WORKFLOW::"scan_PR_comments→pattern_match→determine_tier→required_approvals→validate_format[shared:review_formats.py]→update_PR_status"
  FUTURE::[
    commit_level_reviews,
    batch_review_submission,
    review_templates,
    structured_metadata_blocks
  ]
§12::TROUBLESHOOTING
  REVIEW_NOT_RECOGNIZED::"check_format[dry_run:true]→verify_no_extra_chars→validate_role_and_verdict"
  RATE_LIMITING::"implement_exponential_backoff→monitor_x_ratelimit_headers→consider_batching"
  AUTH_ERRORS::"verify_GITHUB_TOKEN_set→check_repo_scope→ensure_not_expired"
===END===
