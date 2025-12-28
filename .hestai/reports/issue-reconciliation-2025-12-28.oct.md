===ISSUE_RECONCILIATION_REPORT===

META:
  TYPE::MIGRATION_PLAN
  VERSION::"1.0"
  GENERATED::"2025-12-28"
  PURPOSE::"Cross-repo issue analysis with deprecation-aware transfer recommendations"
  CONTEXT::hestai-core+hestai-mcp-server_being_deprecated

EXECUTIVE_SUMMARY:
  TOTAL_ISSUES_ANALYZED::140[across_4_repos]
  REPOS::[
    HestAI-MCP::24_open[current_product],
    hestai::16_open[governance→hub_migration],
    hestai-mcp-server::30_open[DEPRECATED_python_server],
    hestai-core::36_open[DEPRECATED_original_build]
  ]
  VERDICT::11_issues_to_transfer+3_to_hub+harvest_patterns

DEPRECATION_CONTEXT:
  hestai-core::DEPRECATED[original_build→superseded_by_HestAI-MCP]
  hestai-mcp-server::BEING_DEPRECATED[python_tools→replaced_by_TypeScript+PAL]
  hestai::TRANSITIONING[governance→hub/,research_discussions_continue]

===TRANSFER_TO_HESTAI-MCP===

FROM_HESTAI-CORE:
  PRIORITY::B1_IMMEDIATE
    Issue_18_Context_Architecture:
      TITLE::"Context Architecture Overhaul - State Vector + Negatives + Configurable Paths"
      SOURCE::hestai-core#18
      REASON::"Directly implements ADR-0046 (FAST layer) + ADR-0056"
      ACTION::create_new_issue[reference_hestai-core#18_learnings]
      PHASE::B1
      LABELS::[enhancement,area:context,priority:p1-high,phase:b1]

    Issue_96_Visibility_Rules:
      TITLE::"Load VISIBILITY-RULES for document placement decisions"
      SOURCE::hestai-core#96
      REASON::"Supports ADR-0046 fragment routing logic"
      ACTION::create_new_issue[extract_pattern]
      PHASE::B1
      LABELS::[enhancement,area:context,priority:p1-high,phase:b1]

    Session_OCTAVE_Patterns:
      TITLE::"Session OCTAVE Compression - Harvest ClaudeJsonlLens Design"
      SOURCE::hestai-core#45,#62,#63
      REASON::"Informs ADR-0035 (Living Artifacts) implementation"
      ACTION::create_design_reference[harvest_algorithm,close_source_issues]
      PHASE::B1
      LABELS::[enhancement,area:sessions,priority:p1-high,phase:b1]

  PRIORITY::B2_NEXT_PHASE
    Issue_53_Context_DOM:
      TITLE::"Context DOM Engine - Structured Guardrails for Project Context"
      SOURCE::hestai-core#53
      REASON::"Orchestra Map (ADR-0034) implementation concept"
      ACTION::create_new_issue[architectural_enhancement]
      PHASE::B2
      LABELS::[enhancement,area:context,priority:p2-medium,phase:b2]

    Issue_39_Blockage_Resolution:
      TITLE::"Blockage Resolution Orchestrator - Debate Sequencing"
      SOURCE::hestai-core#39
      REASON::"Relates to debate-hall integration (RFC#60)"
      ACTION::create_new_issue[future_integration]
      PHASE::Future
      LABELS::[enhancement,area:agents,priority:p3-low,phase:future]

FROM_HESTAI-MCP-SERVER:
  PRIORITY::ARCHITECTURAL_PATTERNS
    ADR_004_OCTAVE_Native:
      TITLE::"ADR: OCTAVE-Native Context Management Approach"
      SOURCE::hestai-mcp-server#78
      REASON::"Architectural pattern applicable to TypeScript implementation"
      ACTION::create_adr_reference_issue[extract_design_not_code]
      PHASE::B2
      LABELS::[adr,area:context,priority:p2-medium,phase:b2]

    ADR_005_Document_Routing:
      TITLE::"Enhancement: Document Routing Logic (from ADR-005)"
      SOURCE::hestai-mcp-server#79
      REASON::"Enhance document_submit tool with routing patterns"
      ACTION::create_enhancement_issue[routing_logic]
      PHASE::B2
      LABELS::[enhancement,area:mcp-tools,priority:p2-medium,phase:b2]

  PRIORITY::QUALITY_GATES
    Issue_104_Clockout_Verification:
      TITLE::"Clockout Coherence Verification Gate"
      SOURCE::hestai-mcp-server#104
      REASON::"Quality gate pattern for session closure"
      ACTION::create_new_issue[quality_enhancement]
      PHASE::B2
      LABELS::[enhancement,area:sessions,priority:p2-medium,phase:b2]

    Issue_164_Archive_Redaction:
      TITLE::"Security: Session Archive Redaction System"
      SOURCE::hestai-mcp-server#164
      REASON::"Production security requirement"
      ACTION::create_security_issue
      PHASE::B2/B3
      LABELS::[security,area:sessions,priority:p2-medium,phase:b2]

FROM_HESTAI:
  PRIORITY::SESSION_ENHANCEMENTS
    Issue_3_WHY_Synthesis:
      TITLE::"Session Context: Add WHY synthesis to session initialization"
      SOURCE::hestai#3
      REASON::"Session context enhancement for clock_in"
      ACTION::create_new_issue[session_tooling]
      PHASE::B2
      LABELS::[enhancement,area:sessions,priority:p2-medium,phase:b2]

    Issue_5_MUST_NEVER_Monitoring:
      TITLE::"Quality: MUST_NEVER Constraint Monitoring"
      SOURCE::hestai#5
      REASON::"Quality gate enforcement mechanism"
      ACTION::create_new_issue[quality_gates]
      PHASE::B2
      LABELS::[enhancement,area:governance,priority:p2-medium,phase:b2]

===MIGRATE_TO_HUB===

FROM_HESTAI:
  Issue_13_RCCAFP:
    TITLE::"RCCAFP Implementation: Organizational Learning Framework"
    SOURCE::hestai#13
    DESTINATION::hub/governance/quality/rccafp-framework.oct.md
    REASON::"System-wide quality framework, not product-specific"
    ACTION::migrate_to_hub[create_governance_doc]

  Issue_4_Blockage_Protocol:
    TITLE::"Blockage Resolution: Structured Debate Protocol"
    SOURCE::hestai#4
    DESTINATION::hub/governance/workflow/blockage-resolution-protocol.oct.md
    REASON::"Universal workflow pattern for all HestAI products"
    ACTION::migrate_to_hub[create_governance_doc]

  Audit_Results:
    SOURCES::[hestai#6,#7,#8]
    DESTINATIONS::[
      hub/governance/tools/mcp-tool-audit.md,
      hub/governance/workflow/north-star-audit.md,
      hub/governance/tools/repomix-audit.md
    ]
    REASON::"Governance findings applicable system-wide"
    ACTION::extract_findings_to_hub[close_source_issues]

===KEEP_OPEN_METHODOLOGY===

HESTAI_RESEARCH_ISSUES:
  PATTERN::"Vibe-Coding Mitigation Research Series"
  ISSUES::[hestai#14-31]
  TITLES::[
    #14::Functional_Correctness,
    #15::Security_Vulnerabilities,
    #17::Testing_Gaps,
    #19::Hallucinated_APIs,
    #21::Licensing_Provenance,
    #22::Toolchain_Security,
    #23::Skill_Atrophy,
    #24::Domain_Invariants,
    #25::Observability_Telemetry,
    #27::Infra_Deployment_Governance,
    #28::Concurrency_Testing,
    #30::Human_in_Loop_PR_Policy,
    #31::Security_Compliance_Audits
  ]
  DECISION::KEEP_OPEN[methodology_research]
  RATIONALE::"Valuable ongoing research informing hub/ governance"
  ALTERNATIVE::migrate_to_hub/governance/research/[living_documents]

===CLOSE_AS_OBSOLETE===

HESTAI-CORE:
  SUPERSEDED_BY_CURRENT_ARCH::[
    #10::EventLog_implementation[different_session_model],
    #11::clock_in_Python[TypeScript_implementation],
    #12::clock_out_Python[TypeScript_implementation],
    #13::SnapshotGenerator[harvest_algorithm_then_close],
    #21-27::MCP_tool_ports[using_PAL+new_tools],
    #28-30::Server_config[TypeScript_architecture]
  ]
  COMPLETED_WORK::[
    #6::Checklist_vs_Projects[DONE_using_issues],
    #8::Worktree_Init[DONE_ADR-0082],
    #40::Living_Orchestra_North_Star[DONE_have_000-MCP-PRODUCT],
    #41::Unified_hestai[DONE_ADR-0033]
  ]
  META_ISSUES::[
    #4::Coordination_Readiness[extract_checklist_then_close],
    #7::Issue_Transfer_Investigation[DONE_this_report],
    #9::Ecosystem_Consolidation[DONE_superseded],
    #15::Master_Checklist[DONE_superseded_by_roadmap]
  ]

HESTAI-MCP-SERVER:
  PYTHON_SPECIFIC_IMPLEMENTATION::[
    #30-53::Infrastructure_tests_CLI_bugs,
    #71-93::Context_Steward_v2_phases[Python],
    #85-87::Phase_1_foundation[Python],
    #103::clockout_bugs[Python],
    #107::Archival_enforcement[Python],
    #116::OCTAVE_compression_bugs[Python],
    #151::Auto-pick_CLI[PAL_handles_this]
  ]
  DESIGN_HARVESTED::[
    #89::context_update_patterns[extract_conflict_resolution],
    #88::document_submit_patterns[validate_approach],
    #97::Configurable_paths[already_solved_ADR-0046],
    #98::Rollback_mechanism[note_pattern]
  ]

HESTAI:
  COMPLETED::[
    #2::Role_Compliance[CLOSED],
    #9::System_Tool_Audit[CLOSED],
    #10::RAPH_Audit[CLOSED]
  ]
  SOLVED_BY_ADR-0082::[
    #11::Worktree_boundary_enforcement
  ]

===IMPLEMENTATION_PLAN===

PHASE_1_IMMEDIATE:
  TIMELINE::This_sprint
  ACTIONS::[
    1::Create_11_new_issues_in_HestAI-MCP[use_templates_below],
    2::Migrate_3_documents_to_hub/governance/,
    3::Label_hestai_research_issues[methodology-research],
    4::Close_obsolete_issues_with_harvest_comments
  ]

PHASE_2_HUB_MIGRATION:
  TIMELINE::Next_sprint
  ACTIONS::[
    1::Review_hestai_research_findings,
    2::Consider_migration_to_hub/governance/research/,
    3::Update_hub/governance/README_with_research_index
  ]

PHASE_3_REPO_CLOSURE:
  TIMELINE::After_harvest_complete
  ACTIONS::[
    1::Archive_hestai-core_repo,
    2::Archive_hestai-mcp-server_repo,
    3::Keep_hestai_open_or_archive[based_on_research_decision]
  ]

===ISSUE_TEMPLATES===

TEMPLATE_TRANSFER_WITH_HARVEST:
  TITLE::"[Transferred] {Original Title}"
  BODY::"""
  **Transferred from**: {source_repo}#{issue_number}
  **Original Context**: {brief_summary}

  **Why Transferred**:
  {reason_for_transfer}

  **Harvested Learnings**:
  {key_patterns_or_decisions_from_original}

  **Proposed Approach**:
  {how_to_implement_in_HestAI-MCP_context}

  **Related**:
  - ADR: {relevant_adrs}
  - Issues: {related_issues}

  **Original Issue**: {link_to_source}
  """

TEMPLATE_ADR_REFERENCE:
  TITLE::"ADR: {Decision Title} (from {source})"
  BODY::"""
  **Source**: {source_repo} ADR-{number}
  **Original Context**: {architectural_decision}

  **Applicability to HestAI-MCP**:
  {how_pattern_applies_to_TypeScript_implementation}

  **Proposed Decision**:
  {adapted_decision_for_this_product}

  **Alternatives Considered**:
  {if_different_from_source}

  **Original ADR**: {link}
  """

===VALIDATION_CHECKLIST===

BEFORE_TRANSFER:
  ☐::Review_source_issue_comments[capture_all_learnings]
  ☐::Check_for_related_PRs[note_implementation_patterns]
  ☐::Validate_still_relevant[not_superseded_by_current_arch]
  ☐::Identify_dependencies[transfer_together_if_needed]

AFTER_TRANSFER:
  ☐::Link_bidirectionally[source↔new_issue]
  ☐::Apply_correct_labels[phase,area,priority]
  ☐::Add_to_project_board[if_using]
  ☐::Update_source_with_transfer_notice

===RISK_MITIGATION===

RISK_LOSING_CONTEXT:
  MITIGATION::"Harvest comments + link to original + attach to new issue"
  EVIDENCE::Transfer_template_includes_Original_Issue_link

RISK_DUPLICATE_WORK:
  MITIGATION::"Cross-reference existing HestAI-MCP issues before creating"
  EVIDENCE::Check_current_24_issues_for_overlap

RISK_OVERWHELMING_BACKLOG:
  MITIGATION::"Phase transfers: B1 immediate, B2 next, Future later"
  EVIDENCE::Only_3_issues_marked_B1_immediate

===STATUS_SUMMARY===

TO_CREATE_IN_HESTAI-MCP::11_issues
TO_MIGRATE_TO_HUB::3_governance_docs
TO_KEEP_OPEN_METHODOLOGY::11_research_issues
TO_CLOSE_WITH_HARVEST::60+_obsolete_issues

NEXT_ACTIONS:
  1::Review_this_report_with_human
  2::Get_approval_for_transfer_plan
  3::Execute_Phase_1_transfers
  4::Update_repo_READMEs_with_deprecation_notices

===END===
