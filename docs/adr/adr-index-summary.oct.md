===ADR_INDEX_SUMMARY===

META:
  TYPE::REPORT
  VERSION::"1.1"
  GENERATED::"2025-12-27T19:30:00Z"
  PURPOSE::"Scannable index of all ADRs with status, themes, and patterns"
  SOURCE::docs/adr/
  CHANGELOG::"Added ADR-0082 (Claude Code Gitignore + Worktree Symlinks)"

ARCHITECTURE_OVERVIEW:
  DOCUMENT::docs/ARCHITECTURE.md
  STATUS::IMPLEMENTATION_PHASE
  CORE_PATTERN::Dual-Layer_Context[System_Governance+Project_Context]
  KEY_COMPONENTS::[Orchestra_Map,Living_Artifacts,Odyssean_Anchor,Session_Lifecycle]

ADR_REGISTRY:
  ADR-0000:
    TITLE::"ADR Template"
    STATUS::TEMPLATE
    PURPOSE::"Standard structure for architectural decisions"
    LIFECYCLE::[Draft->Proposed->Accepted->Implemented->Superseded]

  ADR-0031:
    TITLE::"GitHub Issue-Based Document Numbering"
    STATUS::IMPLEMENTED
    PHASE::B1
    PURPOSE::"Document Number = GitHub Issue Number to prevent multi-worktree sequence clashes"
    FROM_RFC::RFC-0031
    KEY_INSIGHT::"GitHub Issues solve numbering uniqueness problem natively"

  ADR-0033:
    TITLE::"Dual-Layer Context Architecture"
    STATUS::ACCEPTED
    PURPOSE::"Separate System Governance (runtime injected) from Project Context (git committed)"
    PATTERN::Single_Writer[System_Steward_validates_all_writes]
    LAYERS::[
      Layer_1::System_Governance[.hestai-sys/,gitignored,MCP_injected],
      Layer_2::Project_Documentation[.hestai/,committed,MCP_tools_only]
    ]
    FOUNDATIONAL::TRUE

  ADR-0034:
    TITLE::"Orchestra Map Architecture"
    STATUS::VALIDATED[MVP_Complete]
    PURPOSE::"Dependency awareness across ALL artifact types via Anchor Pattern Inversion"
    KEY_INSIGHT::"Concepts claim Code via imports, not Code citing Concepts via annotations"
    LAYERS::[
      Layer_1::Code_Dependencies[AST_analysis],
      Layer_2::Concept_Anchors[specs_import_code],
      Layer_3::Semantic_Knowledge[Basic_Memory_MCP]
    ]
    CONFIDENCE::85%[validated_from_65%]
    STALENESS_RULE::"LastCommit(Spec) < LastCommit(Impl) == STALE"

  ADR-0035:
    TITLE::"Living Artifacts Auto-Refresh"
    STATUS::APPROVED
    PURPOSE::"Split-artifact hybrid to prevent context staleness"
    PATTERN::Query_Driven_State[generated_fresh_on_clock_in]
    ARTIFACTS::[
      CHANGELOG.md::docs/[CI_updated_on_merge,audit_trail],
      current_state.oct::.hestai/context/[clock_in_generated,query_driven],
      PROJECT-CONTEXT.oct.md::.hestai/context/[System_Steward_tools,committed]
    ]
    TRIGGER::"6+ PRs merged with no documentation update"

  ADR-0036:
    TITLE::"Odyssean Anchor Binding Architecture"
    STATUS::ACCEPTED
    PURPOSE::"Unified agent identity binding with structural validation"
    SUPERSEDES::anchor_submit+load2.md_patterns
    PATTERN::RAPH_Vector[BIND+ARM+FLUKE+TENSION+HAZARD+COMMIT]
    KEY_FEATURES::[
      Unified_Path::main_and_subagents_same_ceremony,
      Structural_Validation::strict_schema_enforcement,
      Self_Correction::retry_on_failure[max_2_attempts]
    ]
    IMPLEMENTS::[I1::Verifiable_Behavioral_Specification,I3::Structural_Enforcement]

  ADR-0039:
    TITLE::"Agent Master Forge"
    STATUS::IMPLEMENTED
    PHASE::B2
    PURPOSE::"Standardized methodology for producing high-performance OCTAVE agents"
    FROM_RFC::RFC-0039
    CORE_PRINCIPLE::"TRUE MODULARITY = Components that modify the whole, not add to the whole"
    ARCHITECTURE::[
      Immutable_Shanks::cognitive_foundations[LOGOS,ETHOS,PATHOS],
      Archetype_Accumulation::capabilities_bring_archetypes,
      Semantic_Weaving::patterns_integrate_at_insertion_points,
      Emergent_Properties::combinations_create_new_capabilities
    ]
    TARGET::90-120_lines[max_150]

  ADR-0040:
    TITLE::"Agent Patterns Library"
    STATUS::IMPLEMENTED
    PHASE::B2
    PURPOSE::"Comprehensive pattern library for agent creation with anti-pattern detection"
    FROM_RFC::RFC-0040
    RELATED::ADR-0039
    TAXONOMY::[Immutable,Accumulative,Weavable,Universal]
    TRANSFORMATION_PATTERNS::[P0::PANDORA,P0::RAPH,P1-P5::Various]
    ANTI_PATTERNS::[PANDORA,ICARIAN,SISYPHEAN,TROJAN]
    FATAL_ERRORS::[E01-E13::compilation_failures]

  ADR-0046:
    TITLE::"Velocity-Layered Fragments Architecture"
    STATUS::ACCEPTED
    PURPOSE::"Organize .hestai/ by change velocity to balance git visibility and conflict prevention"
    PATTERN::Shearing_Layers[Stewart_Brand]
    DEBATE_SOURCE::Wind/Wall/Door[debate-hall_MCP]
    LAYERS::[
      SLOW::workflow/[monthly,human_only],
      MEDIUM::context/[daily-weekly,System_Steward],
      FAST::context/state/[hourly-daily,agents_via_MCP],
      APPEND::reports/[per-session,unique_names],
      EPHEMERAL::sessions/active/[continuous,gitignored]
    ]
    REJECTED::[Orthogonal_Worktrees,Ledger_Event_Sourcing,Git_Submodules,Symlink_External]

  ADR-0056:
    TITLE::"FAST Layer Lifecycle Integration"
    STATUS::PROPOSED
    PURPOSE::"Dynamic FAST layer updates via clock_in/clock_out lifecycle"
    DEPENDS_ON::ADR-0046
    PROBLEM::"FAST layer files are static, not session-aware"
    SOLUTION::[
      clock_in::updates_current_focus+checklist+blockers,
      clock_out::clears_focus+marks_complete+persists_unresolved,
      load_command::passes_topic_to_clock_in
    ]
    CONFLICT_STRATEGY::last_writer_wins[audit_in_archive]

  ADR-0060:
    TITLE::"RFC/ADR Alignment - Issues as Drafts, ADRs as Law"
    STATUS::ACCEPTED
    PHASE::D1
    PURPOSE::"Unify RFC/ADR lifecycle - GitHub Issues are drafts, ADRs are ratified decisions"
    CORE_PRINCIPLE::"The Discussion IS the Draft. The Synthesis IS the Law."
    POLICY::[
      GitHub_Issues::drafts_and_debates[label_rfc],
      ADRs::ratified_decisions_only[immutable_once_merged],
      rfcs_folder::DELETED[migrated_to_Issues_or_ADRs],
      ADR_number::matches_Issue_number
    ]

  ADR-0082:
    TITLE::"Claude Code .claude Gitignore + Worktree Hook Symlinks"
    STATUS::IMPLEMENTED
    PHASE::B0
    PURPOSE::"Clean git history while maintaining worktree SessionStart hook functionality"
    PROBLEM::".claude/ user state pollutes git, but worktrees need .claude/hooks for SessionStart"
    SOLUTION::[
      gitignore_claude::completely_ignore[.claude/,.gemini-clipboard/],
      symlink_hooks::worktree_symlinks_to_main[.claude/hooks],
      global_hook::setup-dependencies.sh_creates_symlinks,
      shared_readonly::all_worktrees_share_main_hooks
    ]
    VALIDATION::"Tested with multiple worktrees successfully sharing symlinked hooks"

STATUS_SUMMARY:
  IMPLEMENTED::[ADR-0031,ADR-0039,ADR-0040,ADR-0082]
  ACCEPTED::[ADR-0033,ADR-0036,ADR-0046,ADR-0060]
  APPROVED::[ADR-0035]
  VALIDATED::[ADR-0034]
  PROPOSED::[ADR-0056]
  TEMPLATE::[ADR-0000]

ARCHITECTURAL_THEMES:
  CONTEXT_ARCHITECTURE::[ADR-0033,ADR-0046,ADR-0056]
    PATTERN::"Velocity-based separation + Single-writer enforcement"

  AGENT_IDENTITY::[ADR-0036,ADR-0039,ADR-0040]
    PATTERN::"Structural validation + Cognitive foundations + Pattern library"

  LIVING_DOCUMENTATION::[ADR-0035,ADR-0031,ADR-0060]
    PATTERN::"Query-driven freshness + Issue-based numbering + Issue-as-draft"

  DEPENDENCY_AWARENESS::[ADR-0034]
    PATTERN::"Anchor Pattern Inversion - Specs claim Code"

  WORKTREE_OPERATIONS::[ADR-0082]
    PATTERN::"Symlink shared assets, gitignore ephemeral state"

CROSS_CUTTING_PATTERNS:
  SINGLE_WRITER::"All .hestai/ writes via MCP tools through System Steward"
  OCTAVE_FORMAT::"Semantic compression for all context artifacts"
  VALIDATION_GATES::"Structural enforcement over trust"
  GIT_VISIBILITY::"All agent-relevant context committed and taggable"
  ISSUE_BASED_NUMBERING::"Document number = GitHub Issue number"

IMPLEMENTATION_STATUS:
  COMPLETE::[
    Dual_Layer_Structure::ADR-0033,
    Issue_Numbering::ADR-0031,
    Agent_Forge::ADR-0039,
    Pattern_Library::ADR-0040,
    RFC_Folder_Deleted::ADR-0060,
    Worktree_Hooks_Gitignored::ADR-0082
  ]
  PARTIAL::[
    Orchestra_Map_MVP::ADR-0034[Layer_3_pending],
    Living_Artifacts::ADR-0035[CI_workflow_pending],
    Odyssean_Anchor::ADR-0036[tool_implemented,migration_pending]
  ]
  PENDING::[
    FAST_Layer_Lifecycle::ADR-0056
  ]

DEPENDENCIES::[
  ADR-0056_depends_on_ADR-0046::"FAST layer lifecycle depends on velocity-layered structure",
  ADR-0046_depends_on_ADR-0033::"Velocity layering refines dual-layer architecture",
  ADR-0040_complements_ADR-0039::"Pattern library complements Agent Master Forge",
  ADR-0035_extends_ADR-0033::"Living artifacts within dual-layer context",
  ADR-0060_builds_on_ADR-0031::"RFC/ADR alignment builds on issue-based numbering"
]

===END===
