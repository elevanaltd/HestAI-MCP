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
  CANONICAL::.hestai/rules/hub-authoring-rules.oct.md
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
  PURPOSE::"Reference materials, skills, agent definitions, and guides",
  CONTENT::[
    skills/→ecosystem_wide_operational_skills,
    agents/→agent_definitions[.oct.md],
    patterns/→common_patterns_and_examples,
    schemas/→schema_definitions,
    octave/→OCTAVE_usage_guide_for_consumers
  ]
]

.hestai-sys/tools/::[
  PURPOSE::"System utility scripts",
  CONTENT::[validators, checkers, helpers]
]

---

§3::PLACEMENT_RULES

RULE_1::ECOSYSTEM_AND_CONSUMER_FACING::[
  WHAT::content_useful_to_agents_across_any_HestAI_repo_goes_in_src/hestai_mcp/_bundled_hub/,
  WHY::_bundled_hub_is_injected_as_.hestai-sys/_into_every_repo_at_startup,
  SOURCE::authored_in_src/hestai_mcp/_bundled_hub/→injected_as::.hestai-sys/,
  TEST::"Would an agent operating in any HestAI repo need this?"→YES→src/hestai_mcp/_bundled_hub/|NO→.hestai/_or_docs/,
  NOTE::"This includes ecosystem-level coordination (dependency graphs, repo directories, ecosystem overviews) — not just consumer-facing docs. Agents developing the ecosystem ARE consumers of this context."
]

RULE_2::INTERNAL_PROJECT_DOCS::[
  WHAT::HestAI-MCP_specific_development_docs[not_relevant_to_other_repos],
  WHERE::.hestai/north-star/_or_docs/,
  EXAMPLES::[
    internal_integration_notes,
    project_specific_assumptions,
    single_repo_development_roadmaps
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
  "System North Star"→src/hestai_mcp/_bundled_hub/governance/workflow/[agents_across_all_repos_need_it],
  "Ecosystem Overview"→src/hestai_mcp/_bundled_hub/governance/[agents_across_all_repos_need_it],
  "Ecosystem Dependency Graph"→src/hestai_mcp/_bundled_hub/governance/[agents_across_all_repos_need_it],
  "Repo Directory"→src/hestai_mcp/_bundled_hub/governance/[agents_across_all_repos_need_it],
  "Visibility Rules"→src/hestai_mcp/_bundled_hub/governance/rules/[agents_across_all_repos_need_it],
  "Agent Templates"→src/hestai_mcp/_bundled_hub/agents/[agents_across_all_repos_need_it],
  "OCTAVE Usage Guide"→src/hestai_mcp/_bundled_hub/library/octave/[agents_across_all_repos_need_it],
  "HestAI-MCP Product North Star"→.hestai/north-star/[internal_only],
  "HestAI-MCP Build Phase Tracking"→.hestai/state/context/[internal_only],
  "HestAI-MCP ADRs"→docs/adr/[internal_architecture_decisions],
  "Proposals"→GitHub_Issues[per_ADR-0060]
]

INCORRECT_PLACEMENT::[
  "HestAI-MCP specific roadmap"→src/hestai_mcp/_bundled_hub/[WRONG→.hestai/north-star/],
  "Internal assumption tracking"→src/hestai_mcp/_bundled_hub/[WRONG→.hestai/north-star/],
  "System North Star"→.hestai/[WRONG→src/hestai_mcp/_bundled_hub/governance/],
  "Ecosystem Dependency Graph"→.hestai/context/[WRONG→src/hestai_mcp/_bundled_hub/governance/]
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
  ".hestai/[their_mutable_governance+state]"::[
    north-star/→product_north_star[000-*-NORTH-STAR.md+components/],
    decisions/→compiled_governance_decisions[debate_outcomes],
    rules/→project_standards+methodology+workflow_guidance,
    schemas/→schema_definitions,
    state/context/→PROJECT-CONTEXT+CHECKLIST+HISTORY[shared_via_symlink],
    state/sessions/→session_artifacts[active+archive|shared_via_symlink],
    state/reports/→evidence_archives[shared_via_symlink]
  ],
  "docs/[their_developer_docs]"::[
    adr/→architecture_decisions,
    development/→setup_guides
  ],
  "debates/[cognitive_evidence]"::[
    *.json→GITIGNORED[full_debate_machine_format],
    *.oct.md→COMMITTED[compressed_debate_synthesis]
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
