===HUB_AUTHORING_RULES===

META:
  TYPE::RULE
  ID::hub-authoring-rules
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"Rules for authoring system governance payload (injected as .hestai-sys/)"
  DOMAIN::governance
  OWNERS::[system-steward]
  CREATED::2025-12-23
  CANONICAL::.hestai-sys/governance/rules/hub-authoring-rules.oct.md
  SOURCE::src/hestai_mcp/_bundled_hub/governance/rules/hub-authoring-rules.oct.md
  TAGS::[hestai-sys, system, authoring, bundled-hub]

---

§1::CONTEXT

// This document is META-VISIBILITY: rules for building the SYSTEM itself.
// visibility-rules.oct.md covers PRODUCT placement (what consumers see).
// This document covers HUB authoring (what we build that becomes .hestai-sys/).

SITUATION::[
  HestAI-MCP_is_BOTH_system_AND_project,
  source_payload::src/hestai_mcp/_bundled_hub/→injected_as::.hestai-sys/,
  consumers_never_see_source_payload→only_.hestai-sys/[read_only]
]

---

§2::DIRECTORY_PURPOSE

// NOTE: Governance is authored in the bundled hub source tree and injected into consumer projects.
// Source (maintainers): src/hestai_mcp/_bundled_hub/
// Injected (agents/consumers): .hestai-sys/

.hestai-sys/::[
  PURPOSE::"System governance content delivered to all HestAI consumers",
  SOURCE::src/hestai_mcp/_bundled_hub/,
  AUDIENCE::all_products_using_HestAI,
  LIFECYCLE::injected_read_only_for_consumers
]

.hestai-sys/governance/::[
  PURPOSE::"Constitutional rules and North Stars",
  CONTENT::[
    workflow/→system_north_star[000-SYSTEM-HESTAI-NORTH-STAR.md],
    rules/→governance_standards[naming+visibility+test_structure+this_file]
  ]
]

.hestai-sys/agents/::[
  PURPOSE::"Agent constitution templates",
  CONTENT::agent_definitions[.oct.md_format],
  NOTE::"Templates that consumers can use/extend"
]

.hestai-sys/templates/::[
  PURPOSE::"Project scaffolding templates",
  CONTENT::[
    north_star_templates,
    project_structure_templates
  ]
]

.hestai-sys/library/::[
  PURPOSE::"Reference materials and guides",
  CONTENT::[
    octave/→OCTAVE_usage_guide_for_consumers,
    patterns/→common_patterns_and_examples
  ]
]

.hestai-sys/tools/::[
  PURPOSE::"System utility scripts",
  CONTENT::[validators, checkers, helpers]
]

---

§3::PLACEMENT_RULES

RULE_1::CONSUMER_FACING_ONLY::[
  WHAT::only_content_useful_to_consumers_goes_in_.hestai-sys/,
  WHY::.hestai-sys/_is_read_only_for_consumers_and_agents,
  SOURCE::authored_in_src/hestai_mcp/_bundled_hub/_and_injected_as_.hestai-sys/,
  TEST::"Would a project using HestAI need this?"→YES→.hestai-sys/|NO→.hestai/_or_docs/
]

RULE_2::INTERNAL_PROJECT_DOCS::[
  WHAT::HestAI-MCP_specific_development_docs,
  WHERE::.hestai/workflow/_or_docs/,
  EXAMPLES::[
    internal_integration_notes,
    project_specific_assumptions,
    development_roadmaps
  ]
]

RULE_3::NO_DUPLICATION::[
  WHAT::never_duplicate_between_.hestai-sys/_and_.hestai/,
  WHY::single_source_of_truth,
  PATTERN::reference_canonical_source_instead
]

---

§4::FORMAT_RULES

OCTAVE_FORMAT[.oct.md]::[
  USE_FOR::[
    agent_constitutions,
    governance_rules,
    north_stars,
    methodology_docs,
    structured_context[PROJECT-CONTEXT_etc]
  ],
  WHY::[
    machine_parseable,
    semantic_density,
    agent_consumption_optimized
  ]
]

MARKDOWN_FORMAT[.md]::[
  USE_FOR::[
    developer_guides[setup_deployment],
    ADRs[architecture_decisions],
    READMEs[navigation_pointers],
    human_first_documentation
  ],
  WHY::[
    github_rendering,
    IDE_preview,
    developer_familiarity
  ]
]

DECISION_TREE::[
  "Is primary audience AI agents?"→YES→.oct.md,
  "Is it governance/methodology/constitution?"→YES→.oct.md,
  "Is primary audience human developers?"→YES→.md,
  "Is it an ADR or setup guide?"→YES→.md,
  "Is it a README/navigation pointer?"→YES→.md
]

---

§5::EXAMPLES

CORRECT_PLACEMENT::[
  "System North Star"→.hestai-sys/governance/workflow/[consumer_needs_it],
  "Visibility Rules"→.hestai-sys/governance/rules/[consumer_needs_it],
  "Agent Templates"→.hestai-sys/agents/[consumer_needs_it],
  "OCTAVE Usage Guide"→.hestai-sys/library/octave/[consumer_needs_it],
  "HestAI-MCP Product North Star"→.hestai/workflow/[internal_only],
  "HestAI-MCP Build Phase Tracking"→.hestai/context/[internal_only],
  "HestAI-MCP ADRs"→docs/adr/[internal_architecture_decisions],
  "Proposals"→GitHub_Issues[per_ADR-0060]
]

INCORRECT_PLACEMENT::[
  "HestAI-MCP specific roadmap"→.hestai-sys/[WRONG→.hestai/workflow/],
  "Internal assumption tracking"→.hestai-sys/[WRONG→.hestai/workflow/],
  "System North Star"→.hestai/[WRONG→.hestai-sys/governance/]
]

---

§6::CONSUMER_VIEW

// What a consumer project sees after HestAI setup:

CONSUMER_DIRECTORY_STRUCTURE::[
  ".hestai-sys/[read_only_injected_from_src/hestai_mcp/_bundled_hub/]"::[
    governance/workflow/→system_north_star,
    governance/rules/→naming+visibility+test_standards,
    agents/→agent_templates,
    templates/→project_scaffolds,
    library/→reference_materials,
    tools/→utility_scripts
  ],
  ".hestai/[their_mutable_context]"::[
    context/→PROJECT-CONTEXT+CHECKLIST+ROADMAP,
    sessions/→session_artifacts,
    workflow/→product_north_star+methodology,
    reports/→evidence_archives
  ],
  "docs/[their_developer_docs]"::[
    adr/→architecture_decisions,
    development/→setup_guides
  ]
]

---

§7::COMPANION_DOCS

RELATED::[
  .hestai-sys/governance/rules/visibility-rules.oct.md→product_placement_rules[what_consumers_follow],
  .hestai-sys/governance/rules/naming-standard.oct.md→file_naming_conventions,
  .hestai-sys/governance/rules/test-structure-standard.oct.md→test_organization
]

---

§8::ADR_PROCESS

// Issue-based document numbering per ADR-0031
// RFC files deprecated per ADR-0060 - proposals use GitHub Issues

ADR_CREATION::[
  1::create_GitHub_issue["ADR: Topic"]→label["adr"],
  2::note_issue_number[#N],
  3::create_document[docs/adr/adr-{N:04d}-topic.md],
  4::link_issue_in_frontmatter["GitHub Issue: [#N](url)"],
  5::submit_PR["Implements #N"]
]

PROPOSAL_PROCESS::[
  1::create_GitHub_issue_with_label["rfc"|"discussion"],
  2::discussion_happens_in_issue_comments,
  3::when_ratified→create_ADR_per_above,
  POLICY::"The Discussion IS the Draft. The Synthesis IS the Law."
]

REFERENCE::docs/adr/adr-0031-github-issue-based-numbering.md
SEE_ALSO::docs/adr/adr-0060-rfc-adr-alignment.md

===END===
