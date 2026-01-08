---
name: documentation-placement
description: Document placement using timeline test (before-code vs after-code). Defines repository structure for dev/docs/ vs coordination/ with phase artifact rules and documentation-first protocols.
allowed-tools: ["Read", "Write", "Bash"]
triggers: ["documentation placement", "ADR placement", "phase artifact", "documentation first", "B1 migration gate"]
---

===DOCUMENTATION_PLACEMENT===

META:
  TYPE::SKILL
  VERSION::1.0
  COMPRESSION_TIER::AGGRESSIVE
  DOMAIN::HERMES[communication]⊕HESTIA[structure]

§1::CORE_PRINCIPLE

TIMELINE_TEST::[
  IF[document_before_code]->coordination/workflow-docs/,
  IF[document_describes_implementation]->dev/docs/,
  IF[document_guides_implementation]->dev/docs/
]

RATIONALE::"Timeline→placement: planning=coordination/, implementation=dev/"

§2::REPOSITORY_STRUCTURE

COORDINATION::[
  workflow-docs/::"Phase artifacts (D1, D2, B0)",
  phase-reports/::"Phase gates (B1-B4)",
  planning-docs/::"CHARTER, ASSIGNMENTS, PROJECT-CONTEXT",
  ACTIVE-WORK.md::"Status board for worktree visibility"
]

DEV::[
  architecture/::"D3-BLUEPRINT-ORIGINAL, ARCHITECTURE-AS-BUILT, DEVIATIONS",
  adr/::"ADR-XXXX-{slug} (GitHub issue-based numbering)",
  api/::"API endpoint documentation",
  guides/::"Technical guides"
]

§3::PHASE_ARTIFACT_MAPPING

PLACEMENT::[
  D1_NORTH_STAR::coordination/workflow-docs/,
  D2_DESIGN::coordination/workflow-docs/,
  D3_BLUEPRINT::dev/docs/architecture/D3-BLUEPRINT-ORIGINAL.md,
  B0_VALIDATION::coordination/workflow-docs/,
  B1_B4_REPORTS::coordination/phase-reports/
]

CRITICAL::"D3 migrates FROM coordination TO dev/ at B1 gate"

§4::DOCUMENTATION_FIRST_PROTOCOL

SEQUENCE::[
  1::write_docs_first[ADR, specification, blueprint],
  2::merge_docs_PR[before implementation],
  3::implementation_PR_references_merged_docs[via PR number],
  4::implementation_blocked_until_docs_merged
]

HANDOFF::"Docs PR merged (#N) → Implementation: 'Implements ADR-XXX (merged in PR #N)'"

MERGE_STRATEGY::[
  D3_BLUEPRINT::immediate[before B0],
  ADRs::immediate[before implementation],
  API_DOCS::with_or_before_implementation,
  ARCHITECTURE_AS_BUILT::with_implementation,
  DEVIATIONS::as_discovered
]


§5::B1_MIGRATION_GATE

CONTEXT_REQUIREMENTS::[
  B1_01_B1_02::ideation_directory,
  MIGRATION_GATE::manual_checkpoint[verify D3→dev/],
  B1_03_B1_05::dev_directory
]

CRITICAL::"B1_02 in ideation/, B1_03 in dev/ after manual migration"


§6::ACTIVE_WORK_MD_STATUS_BOARD

PURPOSE::"Mitigate worktree isolation with visible project status"

SECTIONS::[
  feature_name_and_branch,
  blueprint_link::dev/docs/architecture/,
  ADR_status::[MERGED,IN_REVIEW],
  current_phase::[B1,B2,B3,B4],
  PR_link[with_WIP_marker],
  agent_assigned
]

UPDATE_PROTOCOL::[
  on_worktree_creation::update,
  on_PR_merge::complete,
  on_phase_gate::refresh
]


§7::ADR_FRONT_MATTER

ARCHITECTURE_DOCS::[
  applies_to_tag,
  supersedes,
  superseded_by,
  schema_version,
  phase::D3,
  status::[ORIGINAL,AS_BUILT,DEVIATION]
]

ADR_DOCS::[
  adr_number::"MUST match GitHub Issue number (zero-padded 4 digits)",
  title,
  status::[ACCEPTED,SUPERSEDED,DEPRECATED],
  decision_date::ISO_8601,
  implements::blueprint_section,
  deviates_from
]

NUMBERING_RULE::"ADR-{GITHUB_ISSUE_NUMBER}-{slug}.md with zero-padded 4 digits"
VALIDATION::scripts/ci/validate-doc-numbering.sh[enforced_on_push]


§8::CLEANUP_AT_PHASE_GATES

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

§9::INTEGRATION

TRIGGERS_WHEN::[documentation_created, artifact_placed, B1_migration]
CONSULT::[holistic-orchestrator, workspace-architect, system-steward]
WISDOMS::[
  "Documentation_is_prerequisite_not_side_effect",
  "Timeline_determines_placement",
  "B1_migration_is_critical_checkpoint",
  "ACTIVE-WORK.md_prevents_worktree_blindness"
]

===END===
