===DEBATE_RECORD===
META:
  TYPE::DEBATE_RECORD
  THREAD_ID::"adr-rfc-alignment-2025-12-26"
  DATE::"2025-12-26"
  STATUS::RESOLVED
  MODE::mediated
  TOPIC::"ADR and RFC Unification and Lifecycle Tracking"

QUESTION:
  CORE::"How should ADRs and RFCs be unified, organized, and tracked?"
  CONSIDERATIONS::[lifecycle_RFC_to_ADR, location_consistency, template_parity, GitHub_Issue_integration]
  PARTICIPANTS::[
    Wind_edge-optimizer_gemini-3-pro-preview_PATHOS,
    Wall_critical-engineer_codex_ETHOS,
    Door_synthesizer_claude-opus-4-5-20251101_LOGOS
  ]

DEBATE_FLOW:
  WIND::UNIFIED_CONTINUUM[
    OBSERVATION::"RFC vs ADR is bureaucratic artifact - same intellectual thread",
    PROBLEMS::[state_duplication, repo_pollution, context_gap],
    PROPOSAL::[
      delete_rfcs_folder,
      rename_docs_adr_to_governance,
      unified_template_GOV,
      lifecycle_field_Draft_Proposed_Accepted_Implemented_Superseded
    ],
    PRINCIPLE::"Stop moving files, start changing states"
  ]

  WALL::BLOCKED[
    EVIDENCE_COUNT::10,
    CRITICAL_CONSTRAINTS::[
      E1::authoring_rules_encode_ADR_RFC_split,
      E2::GitHub_Issues_required_for_both,
      E4::CI_enforcement_hardcoded_docs_adr_rfcs_active,
      E5::semantic_distinction_real_RFC_what_if_ADR_what_is,
      E9::RFC-0031_marks_structure_FIXED
    ],
    FAILURE_MODES::[
      F1::CI_precommit_hard_breaks,
      F2::mass_link_rot,
      F3::governance_blur,
      F4::decision_orphans,
      F5::lifecycle_conflation
    ],
    REFINEMENTS::[R1_shared_metadata_schema, R2_GitHub_Issue_canonical, R3_continuum_as_overlay]
  ]

SYNTHESIS:
  DOOR::APPROVED[
    NAME::"Lifecycle-as-Metadata",
    KEY_INNOVATION::"Both and via Frontmatter - state not location"
  ]

  TENSION_RESOLUTION::[
    WIND_INSIGHT::"RFC to ADR is lifecycle not category",
    WALL_CONSTRAINT::"CI hardcoded, namespace collision",
    SYNTHESIS::"Lifecycle as STATE not LOCATION"
  ]

  UNIFIED_FRONTMATTER::[
    Status::[Draft, Proposed, Accepted, Implemented, Superseded],
    Type::[RFC, ADR],
    GitHub_Issue::num_with_URL,
    Phase::[D0, D1, D2, D3, B0, B1, B2, B3, B4, B5],
    Supersedes::if_applicable,
    Superseded_By::if_applicable
  ]

  RFC_TO_ADR_PROMOTION::[
    1::keep_RFC_in_place_Status_Accepted,
    2::create_ADR_with_linked_issue,
    3::update_RFC_Implements_ADR-NNNN,
    4::update_ADR_From-RFC_RFC-NNNN
  ]

  INDEX_LEDGER::"Add table to both README.md with Number Title Type Status Phase GitHub_Issue"

KEY_DECISIONS:
  D1::PRESERVE_Directory_Structure::"docs_adr and rfcs_active unchanged"
  D2::PRESERVE_CI_Compatibility::"Additive validation only"
  D3::PRESERVE_RFC-0031_Compliance::"GitHub Issue remains canonical"
  D4::ADD_Unified_Frontmatter::"Same schema across both"
  D5::ADD_ADR_Template::"Fill existing gap"
  D6::ADD_Index_Ledgers::"Cross-linked README tables"
  D7::REJECT_Rename_Governance::"Collides with hub_governance"

IMPLEMENTATION:
  PHASE_1::[create_adr_template, align_rfc_template]::system-steward
  PHASE_2::[add_index_ledgers_to_READMEs]
  PHASE_3::[extend_CI_with_status_validation]::implementation-lead
  PHASE_4::[update_hub_authoring_rules]

COST_BENEFIT:
  COST::LOW_4_files_modified_0_files_moved_0_CI_paths_changed
  BENEFIT::HIGH_unified_mental_model_queryable_status_template_gap_filled_zero_link_rot

PRESERVED_INSIGHTS:
  WIND::[
    ACCEPTED::lifecycle_transition_not_category,
    ACCEPTED::stop_moving_files_change_states,
    REJECTED::unified_continuum_breaks_CI
  ]
  WALL::[
    ACCEPTED::CI_hardcoded_constraint,
    ACCEPTED::semantic_distinction_real,
    ACCEPTED::RFC-0031_compliance_required,
    ACCEPTED::namespace_collision_risk
  ]
===END===
