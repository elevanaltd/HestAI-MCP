===SUBMIT_REVIEW_GUIDE===
META:
  TYPE::AGENT_GUIDE
  VERSION::"1.0.0"
  PURPOSE::"Agent instructions for submit_review MCP tool usage"
  COMPRESSION_TIER::CONSERVATIVE
  LOSS_PROFILE::"~15% verbose phrasing, repetition"
  NARRATIVE_DEPTH::PRESERVED
  TARGET_AUDIENCE::AGENTS

§1::TOOL_IDENTITY
  NAME::submit_review
  PROTOCOL::MCP[Model_Context_Protocol]
  PURPOSE::"Post formatted PR comments → clear review-gate CI"

  CAPABILITIES:[
    post_review_comments,
    format_for_CI_validation,
    self_validate_APPROVED,
    structured_error_handling,
    dry_run_testing
  ]

  LIMITATION::requires_existing_PR[GitHub_issue_API_constraint]

§2::ACTIVATION_TRIGGERS
  USE_WHEN:[
    "Review PR requested",
    "IL self-review needed",
    "CRS code quality review",
    "CE production readiness check",
    "Block∨Conditional approval required"
  ]

  ROLE_MAPPING:
    IL::"Implementation Lead" → self_review
    CRS::"Code Review Specialist" → code_quality
    CE::"Critical Engineer" → production_readiness

§3::PARAMETERS
  REQUIRED:
    repo::STRING["owner/name format"]
    pr_number::INTEGER[existing_PR_only]
    role::ENUM[IL,CRS,CE]
    verdict::ENUM[APPROVED,BLOCKED,CONDITIONAL]
    assessment::STRING[non_empty,detailed_reasoning]

  OPTIONAL:
    dry_run::BOOLEAN[default:false,test_without_posting]
    model_annotation::STRING[transparency:"Claude"∨"Gemini"]

§4::REVIEW_TIERS
  TIER_1_SELF:
    TRIGGER::[non_exempt_lines_lt_50_and_single_non_exempt_file]
    REQUIRED::[IL_SELF_REVIEWED∨HO_REVIEWED]
    EXAMPLES::[README,config,small_fixes]

  TIER_2_STANDARD:
    TRIGGER::[lines_50_to_500]
    REQUIRED::[CRS_APPROVED∧CE_APPROVED]
    EXAMPLES::[features,bug_fixes,refactoring]

  TIER_3_STRICT:
    TRIGGER::[lines_gt_500_or_sql_changes]
    REQUIRED::[CRS_GEMINI_APPROVED∧CRS_CODEX_APPROVED∧CE_APPROVED]
    EXAMPLES::[major_features,redesigns,security_critical]

§5::WORKFLOWS
  SIMPLE_TIER_1:[
    IL_implements → create_PR → submit_review[role:IL] → CI_validates → merge
  ]

  MULTI_AGENT:[
    IL_implements → create_PR,
    CRS_reviews::submit_review[role:CRS,verdict],
    CE_reviews::submit_review[role:CE,verdict],
    IF[both_APPROVED]→merge ELSE→rework→re_review
  ]

  DRAFT_STRATEGY:[
    create_draft::"gh pr create --draft",
    incremental_reviews→accumulate_feedback,
    mark_ready::"gh pr ready {pr_number}",
    final_approvals→submit_review→merge
  ]

§6::USAGE_EXAMPLES
  IL_SELF_REVIEW:
    await submit_review(
      repo="elevanaltd/HestAI-MCP",
      pr_number=123,
      role="IL",
      verdict="APPROVED",
      assessment="Self-review complete: All tests passing, TDD process followed",
      model_annotation="Claude"
    )

  CE_BLOCKING:
    await submit_review(
      repo="elevanaltd/HestAI-MCP",
      pr_number=123,
      role="CE",
      verdict="BLOCKED",
      assessment="Security vulnerability: SQL injection risk at line 45"
    )

  DRY_RUN_TEST:
    await submit_review(
      repo="elevanaltd/HestAI-MCP",
      pr_number=123,
      role="CRS",
      verdict="APPROVED",
      assessment="Test review",
      dry_run=true  // No GitHub post
    )

§7::RESPONSE_STRUCTURE
  SUCCESS_RESPONSE:
    success::true
    comment_url::STRING[GitHub_comment_URL]
    formatted_comment::STRING[posted_comment_text]
    validation:
      would_clear_gate::BOOLEAN
      tier_requirements::STRING[human_readable]

§8::ERROR_HANDLING
  ERROR_TYPES→ACTION_MAPPING:
    validation→no_retry[input_invalid]
    auth→configure_env[add_GITHUB_TOKEN_to_.env_file]
    network→retry_immediate[transient_failure]
    rate_limit→retry_backoff[wait_60s,exponential]
    github_api→check_PR_exists[404∨other_API_error]

  RETRY_PATTERN:
    result = await submit_review(...)
    IF[!result.success]:
      SWITCH[result.error_type]:
        rate_limit→sleep(60)→retry
        network→retry_immediate
        auth∨validation→fail_fast

§9::CRITICAL_CONSTRAINTS
  PR_MUST_EXIST::"Cannot review commits outside PR"
  FORMAT_STRICT::"Invalid format rejected pre-post"
  ONLY_APPROVED_CLEARS::"BLOCKED/CONDITIONAL provide feedback only"
  ASSESSMENT_SPECIFICITY::"Line numbers, files for BLOCKED/CONDITIONAL"
  DRY_RUN_FIRST::"Test format before production posting"

§10::COMMON_MISTAKES
  AVOID:[
    empty_assessment,
    wrong_role_for_agent_type,
    assuming_all_verdicts_clear_gates,
    posting_without_PR,
    ignoring_validation_errors
  ]

§11::INTEGRATION_POINTS
  CI_WORKFLOW:
    scan_PR_comments→pattern_match
    determine_tier→required_approvals
    validate_format[shared:review_formats.py]
    update_PR_status_check

  FUTURE_ENHANCEMENTS:[
    commit_level_reviews,
    batch_review_submission,
    review_templates,
    debate_hall_orchestration[#163]
  ]

§12::TROUBLESHOOTING
  REVIEW_NOT_RECOGNIZED:
    check_format[dry_run:true]
    verify_no_extra_chars
    validate_role∧verdict

  RATE_LIMITING:
    implement_exponential_backoff
    monitor_x_ratelimit_headers
    consider_batching

  AUTH_ERRORS:
    verify_GITHUB_TOKEN_set
    check_repo_scope
    ensure_not_expired

===END===
