---
name: documentation-placement
description: Document placement using timeline test and HestAI visibility rules. Maps artifacts to .hestai-sys/, .hestai/, docs/, .hestai/state/ with phase artifact rules, format selection, anti-patterns, and documentation-first protocols.
allowed-tools: ["Read", "Write", "Bash"]
triggers: ["documentation placement", "ADR placement", "phase artifact", "documentation first", "B1 migration gate", "visibility rules"]
---

===DOCUMENTATION_PLACEMENT===
META:
  TYPE::SKILL
  VERSION::"2.1"
  STATUS::ACTIVE
  COMPRESSION_TIER::AGGRESSIVE
  DOMAIN::HERMES[communication]+HESTIA[structure]

§1::CORE_PRINCIPLE

TIMELINE_TEST::[
  IF[document_before_code]→.hestai/north-star/|.hestai/rules/,
  IF[document_describes_implementation]→docs/,
  IF[document_guides_implementation]→docs/,
  IF[operational_state_or_tracking]→.hestai/state/context/,
  IF[session_or_handoff]→.hestai/state/sessions/
]

RATIONALE::"Timeline→placement: planning=.hestai/, implementation=docs/, operational=.hestai/state/"

CANONICAL_REFERENCE::.hestai-sys/governance/rules/visibility-rules.oct.md

§2::REPOSITORY_STRUCTURE

// Per visibility-rules.oct.md v1.6

SYSTEM_GOVERNANCE[.hestai-sys/]::[
  READ_ONLY[injected_from_src/hestai_mcp/_bundled_hub/],
  governance/workflow/→"System North Star (000-SYSTEM-HESTAI-NORTH-STAR.md)",
  governance/rules/→"Naming standard, visibility rules, test standards",
  agents/→"Agent constitution templates (.oct.md)",
  templates/→"Project scaffolding templates",
  library/skills/→"Ecosystem-wide operational skills",
  library/agents/→"Agent definitions",
  library/patterns/→"Reusable patterns and examples",
  library/schemas/→"Schema definitions",
  library/octave/→"OCTAVE usage guides",
  tools/→"System utility scripts (validators, checkers)"
]

NOTE::"Agents CANNOT place artifacts in .hestai-sys/ — it is injected read-only at runtime"

PROJECT_GOVERNANCE[.hestai/]::[
  north-star/→"North Star documents (000-*-NORTH-STAR.md + components/)",
  decisions/→"Compiled governance decisions (debate outcomes, NOT ADRs)",
  rules/→"Project standards, methodology, workflow guidance, specs",
  schemas/→"Schema definitions"
]

DEVELOPER_DOCS[docs/]::[
  adr/→"ADR-NNNN-topic.md (GitHub issue-based numbering per ADR-0031)",
  api/→"API endpoint documentation",
  development/→"Setup guides",
  deployment/→"Deployment guides"
]

OPERATIONAL_STATE[.hestai/state/]::[
  context/→"PROJECT-CONTEXT.md, PROJECT-CHECKLIST.md, PROJECT-HISTORY.md",
  context/apps/<app>/→"APP-CONTEXT.md, APP-CHECKLIST.md, APP-HISTORY.md",
  sessions/active/→"Active session working state",
  sessions/archive/→"YYYY-MM-DD-<focus>-<id>-octave.oct.md (committed) + raw.jsonl (gitignored)",
  reports/→"YYYY-MM-DD-* audit reports, scan outputs, quality gate evidence"
]

DEBATE_ARTIFACTS[debates/]::[
  json→GITIGNORED[full_debate_machine_format],
  oct.md→COMMITTED[compressed_debate_synthesis]
]

CLAUDE_CODE[.claude/]::[
  agents/→"Agent constitutions (.oct.md)",
  commands/→"Slash commands",
  skills/→"Project-specific skills (per-repo, NOT ecosystem-wide)",
  hooks/→"Git workflow automation"
]

NOTE::.claude/skills/→project_specific|.hestai-sys/library/skills/→ecosystem_wide

§3::PHASE_ARTIFACT_MAPPING

PLACEMENT::[
  D1_NORTH_STAR::.hestai/north-star/,
  D2_DESIGN::.hestai/rules/specs/,
  D3_BLUEPRINT::docs/[architecture_documentation],
  B0_VALIDATION::.hestai/rules/specs/,
  B1_B4_REPORTS::.hestai/state/reports/
]

CRITICAL::"D3 blueprint migrates to docs/ at B1 gate"

§4::FORMAT_SELECTION

// Per visibility-rules.oct.md FORMAT_RULES + FILE_RETENTION_POLICY

OCTAVE_FORMAT[.oct.md]::[
  agent_constitutions,
  governance_rules,
  north_stars,
  methodology_docs,
  context_files[PROJECT-CONTEXT_etc],
  session_archives[compressed_semantic]
]

MARKDOWN_FORMAT[.md]::[
  developer_guides[setup_deployment],
  ADRs[architecture_decisions],
  READMEs[navigation_pointers],
  human_first_documentation
]

FORMAT_DECISION_TREE::[
  "Primary audience AI agents?"→YES→.oct.md,
  "Governance/methodology/constitution?"→YES→.oct.md,
  "Primary audience human developers?"→YES→.md,
  "ADR or setup guide?"→YES→.md
]

RETENTION_RULE::[
  json_jsonl[raw]→GITIGNORED[machine_format+large+reconstructible],
  oct.md[compressed]→COMMITTED[semantic_density+audit_trail],
  "Raw machine formats are ephemeral; semantic compressions are permanent"
]

§5::DOCUMENTATION_FIRST_PROTOCOL

SEQUENCE::[
  1::write_docs_first[ADR+specification+blueprint],
  2::merge_docs_PR[before_implementation],
  3::implementation_PR_references_merged_docs[via_PR_number],
  4::implementation_blocked_until_docs_merged
]

HANDOFF::"Docs PR merged (#N) → Implementation: 'Implements ADR-XXX (merged in PR #N)'"

MERGE_STRATEGY::[
  D3_BLUEPRINT::immediate[before_B0],
  ADRs::immediate[before_implementation],
  API_DOCS::with_or_before_implementation,
  ARCHITECTURE_AS_BUILT::with_implementation,
  DEVIATIONS::as_discovered
]

§6::B1_MIGRATION_GATE

CONTEXT_REQUIREMENTS::[
  B1_01_B1_02::.hestai/rules/specs/[design_phase_artifacts],
  MIGRATION_GATE::manual_checkpoint[verify_D3→docs/],
  B1_03_B1_05::docs/[implementation_documentation]
]

CRITICAL::"B1_02 in .hestai/rules/specs/, B1_03 in docs/ after manual migration"

§7::ANTI_PATTERNS

// From visibility-rules.oct.md ANTI_PATTERNS

AVOID::[
  DUPLICATE_CONTENT::"ADRs ONLY in docs/adr/ — never in .hestai/",
  DEVELOPER_DOCS_IN_HESTAI::"Developers will not find setup guides in .hestai/ — use docs/",
  COMMIT_EPHEMERAL::"Session handoffs go to .hestai/state/sessions/ (shared state, not git)",
  MIX_ABSTRACTION_LEVELS::"Dashboard (PROJECT) guides to detail (APP) — no implementation in PROJECT-CONTEXT",
  NON_NORTH_STAR_IN_NORTH_STAR_FOLDER::"Only 000-*-NORTH-STAR* files and components/ belong in north-star/",
  CONFUSE_DECISIONS_WITH_ADRS::".hestai/decisions/ = compiled governance decisions | docs/adr/ = formal ADRs",
  PLACE_IN_HESTAI_SYS::".hestai-sys/ is read-only injected — agents cannot write there"
]

§8::PROJECT_CONTEXT_STATUS

PURPOSE::"Mitigate worktree isolation with visible project status"

LOCATION::.hestai/state/context/PROJECT-CONTEXT.md

SECTIONS::[
  feature_name_and_branch,
  blueprint_link::docs/,
  ADR_status::[MERGED+IN_REVIEW],
  current_phase::[B1+B2+B3+B4],
  PR_link[with_WIP_marker],
  agent_assigned
]

UPDATE_PROTOCOL::[
  on_worktree_creation::update,
  on_PR_merge::complete,
  on_phase_gate::refresh
]

§9::ADR_FRONT_MATTER

ARCHITECTURE_DOCS::[
  applies_to_tag,
  supersedes,
  superseded_by,
  schema_version,
  phase::D3,
  status::[ORIGINAL+AS_BUILT+DEVIATION]
]

ADR_DOCS::[
  adr_number::"MUST match GitHub Issue number (zero-padded 4 digits)",
  title,
  status::[ACCEPTED+SUPERSEDED+DEPRECATED],
  decision_date::ISO_8601,
  implements::blueprint_section,
  deviates_from
]

NUMBERING_RULE::"ADR-<GITHUB_ISSUE_NUMBER>-<slug>.md with zero-padded 4 digits"
LOCATION::docs/adr/
VALIDATION::scripts/ci/validate-doc-numbering.sh[enforced_on_push]

§10::CLEANUP_AT_PHASE_GATES

MANDATORY_POINTS::[
  after_B1_02::before_migration,
  after_B2_04::before_B3,
  after_B3_04::before_B4,
  after_B4_05::before_delivery
]

AGENT_BOUNDARIES::[
  directory-curator::"Reports only",
  workspace-architect::"Fixes violations, owns migrations",
  holistic-orchestrator::"Enforces at gates"
]

§11::INTEGRATION

TRIGGERS_WHEN::[documentation_created, artifact_placed, B1_migration]
CONSULT::[holistic-orchestrator, workspace-architect, system-steward]

COMPANION_DOCS::[
  .hestai-sys/governance/rules/visibility-rules.oct.md→"WHERE does artifact belong?",
  .hestai-sys/governance/rules/naming-standard.oct.md→"HOW to name once placed?",
  .hestai/rules/hub-authoring-rules.oct.md→"WHERE in system governance payload?"
]

WISDOMS::[
  "Documentation_is_prerequisite_not_side_effect",
  "Timeline_determines_placement",
  "B1_migration_is_critical_checkpoint",
  "PROJECT-CONTEXT.md_prevents_worktree_blindness",
  ".hestai-sys/_is_read_only_system_governance"
]

===END===
