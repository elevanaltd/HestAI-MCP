===DEBATE_RECORD===
META:
  TYPE::DEBATE_RECORD
  THREAD_ID::"adr-rfc-alignment-v2-2025-12-26"
  DATE::"2025-12-26"
  STATUS::RESOLVED
  MODE::mediated
  TOPIC::"Agoral Forge - RFC as GitHub Discussions with debate-hall-mcp"

QUESTION:
  CORE::"Should RFCs become GitHub Discussions with debate-hall-mcp integration?"
  PROPOSAL::[debate_turns_to_GH_comments, eliminate_rfcs_folder, ADRs_remain_immutable]
  PARTICIPANTS::[
    Wind_edge-optimizer_gemini-3-pro-preview_PATHOS,
    Wall_critical-engineer_codex_ETHOS,
    Door_synthesizer_claude-opus-4-5-20251101_LOGOS
  ]

DEBATE_FLOW:
  WIND::AGORAL_FORGE_VISION[
    PREMISE::["Files are for Code", "Discussions are for Ideas"],
    STATE_MACHINE::[
      S1::human_starts_discussion_Category_RFC,
      S2::trigger_debate_hall_Label_debate-requested,
      S3::agents_descend_Wind_Wall_Door_comments,
      S4::community_intervention_humans_reply,
      S5::ratification_ratify_Auto_PR_ADR
    ],
    KILLER_FEATURE::"Auto-Legislator - Discussion_IS_Draft Synthesis_IS_Law",
    BENEFITS::[async_cognition, dynamic_adjustment, voting_signal, hyperlinked_context]
  ]

  WALL::CONDITIONAL_GO[
    CHALLENGES::[
      API::[GraphQL_primary, category_limit_25, webhooks_in_preview],
      DISCOVERABILITY::[no_git_grep, no_PR_diffs, deletion_possible],
      MIGRATION::[freeze_policy, bulk_import, redirect_stubs, ratify_backfill, delete_folder]
    ],
    ACCEPTANCE_CRITERIA::[
      A1::trigger_spec_category_plus_label_OR_slash_command_idempotent,
      A2::canonicality_spec_ADR_source_of_truth_discussion_locked_after_ratify,
      A3::repo_index_present_docs_adr_rfc-index.md,
      A4::prototype_policy_experiments_in_git_linked_from_discussion
    ],
    RISKS_AND_SOLVES::[
      R1::webhook_instability_fallback_polling,
      R2::canonicality_drift_ADR_supersedes_plus_lock,
      R3::bot_permission_GitHub_App_minimal_scopes,
      R4::category_limit_use_labels_for_taxonomy,
      R5::offline_discoverability_index_plus_mirror
    ]
  ]

SYNTHESIS:
  DOOR::APPROVED[
    NAME::"Agoral Forge Architecture",
    KEY_INSIGHT::"debate-hall-mcp IS the bridge - structured turns to threaded comments"
  ]

  COGNITION_TO_COMMENT_MAPPING::[
    Wind_PATHOS::"## WIND PATHOS - Possibility Exploration",
    Wall_ETHOS::"## WALL ETHOS - Constraint Analysis",
    Door_LOGOS::"## DOOR LOGOS - Synthesis"
  ]

  NEW_MCP_TOOLS::[
    github_sync_debate_thread_id_discussion_number::[
      ACTION::post_each_turn_as_comment_with_cognition_header,
      IDEMPOTENCY::skip_if_comment_id_exists,
      BINDING::store_turn_index_to_comment_node_id
    ],
    ratify_rfc_thread_id_adr_number_title::[
      1::extract_Door_synthesis,
      2::format_as_ADR_template,
      3::create_PR_docs_adr_issue_slug.md,
      4::lock_discussion_mark_answered,
      5::update_rfc_index.md
    ],
    human_interject_discussion_id_comment_id::[
      TRIGGER::webhook_on_human_reply,
      ACTION::inject_as_evidence_or_expansion,
      EFFECT::next_turn_incorporates
    ]
  ]

IMPLEMENTATION_PHASES:
  P0_FOUNDATION_Week_1::[
    create_GitHub_App_discussions_write_contents_write,
    create_Discussion_category_RFC_plus_template,
    define_labels_debate-requested_debate-active_ratified
  ]
  P1_CORE_TOOLS_Weeks_2-3::[
    implement_github_sync_debate_GraphQL_mutations,
    implement_ratify_rfc_ADR_generation_PR_creation,
    add_index_maintenance
  ]
  P2_AUTOMATION_Week_4::[
    GitHub_Actions_workflow_on_discussion_and_discussion_comment,
    human_intervention_detection,
    webhook_reliability_fallback_polling_5min
  ]
  P3_MIGRATION_Weeks_5-6::[
    freeze_rfcs_active_writes,
    bulk_import_active_RFCs,
    redirect_stubs_rfcs_md_to_Discussion_URL,
    delete_rfcs_folder_after_100_pct_coverage
  ]

EMERGENT_CAPABILITIES:
  FILE_BASED_RFC_NEVER_COULD::[
    1::ASYNC_MULTI_MODEL_COGNITION::"Gemini Codex Claude debate in parallel via clink",
    2::HUMAN_IN_LOOP_WITHOUT_GIT::"Reply to agent comment feedback injected",
    3::QUANTITATIVE_SENTIMENT::"Upvotes on Wind vs Wall inform synthesis",
    4::LIVING_DECISION_ARCHAEOLOGY::"Threaded narrative vs opaque git diffs",
    5::CROSS_REPO_FEDERATION::"Org-level Discussions for federated governance"
  ]

KEY_DECISIONS:
  D1::ADOPT_GitHub_Discussions::"Platform is forum, repo is law"
  D2::ADOPT_debate-hall-mcp_integration::"Structured cognition to comments"
  D3::ADOPT_ratify_auto_legislator::"Zero manual ADR transcription"
  D4::DELETE_rfcs_folder::"After 100pct migration coverage"
  D5::PRESERVE_ADRs_in_repo::"Immutable governance artifacts"
  D6::REQUIRE_A1-A4_acceptance::"GO if implemented BLOCK otherwise"

COST_BENEFIT:
  COST::[
    ENGINEERING::40h_adapter_workflow_testing,
    OPERATIONAL::minimal_GitHub_App_maintenance,
    MIGRATION::8h_bulk_import_stubs
  ]
  BENEFIT::[
    COGNITIVE_LOAD::REDUCED_no_git_for_RFC_discussion,
    DISCOVERABILITY::IMPROVED_search_notifications_mentions,
    AUDITABILITY::ENHANCED_immutable_comment_history,
    COLLABORATION::MULTIPLIED_async_multi_agent_human_interleaving,
    AUTOMATION::ENABLED_ratify_eliminates_manual_transcription
  ]
  VERDICT::"BENEFIT exceeds COST"

PRESERVED_INSIGHTS:
  WIND::[
    ACCEPTED::files_for_code_discussions_for_ideas,
    ACCEPTED::auto_legislator_concept,
    ACCEPTED::delete_rfcs_folder_vision
  ]
  WALL::[
    ACCEPTED::API_integration_challenges_identified,
    ACCEPTED::A1-A4_acceptance_criteria_mandatory,
    ACCEPTED::migration_path_defined,
    ACCEPTED::risk_solve_matrix_complete
  ]

NEXT_ACTIONS:
  IMMEDIATE::[
    convert_synthesis_to_RFC,
    create_GitHub_Issue_for_tracking,
    design_GitHub_App_permissions
  ]
  AFTER_APPROVAL::[
    begin_Phase_0,
    schedule_Phase_1_sprint
  ]
===END===
