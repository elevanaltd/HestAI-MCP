---
name: documentation-placement
description: Document placement using timeline test and HestAI visibility rules. Maps artifacts to .hestai/, docs/, .hestai/state/ with phase artifact rules and documentation-first protocols.
allowed-tools: ["Read", "Write", "Bash"]
triggers: ["documentation placement", "ADR placement", "phase artifact", "documentation first", "B1 migration gate"]
---

===DOCUMENTATION_PLACEMENT===
META:
  TYPE::SKILL
  VERSION::2.0
  STATUS::ACTIVE
  COMPRESSION_TIER::AGGRESSIVE
  DOMAIN::HERMES[communication]⊕HESTIA[structure]

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
  context/apps/{app}/→"APP-CONTEXT.md, APP-CHECKLIST.md, APP-HISTORY.md",
  sessions/active/→"Active session working state",
  sessions/archive/→"Archived session transcripts",
  reports/→"Audit reports, scan outputs, quality gate evidence"
]

DEBATE_ARTIFACTS[debates/]::[
  *.json→GITIGNORED[full_debate_machine_format],
  *.oct.md→COMMITTED[compressed_debate_synthesis]
]

§3::PHASE_ARTIFACT_MAPPING

PLACEMENT::[
  D1_NORTH_STAR::.hestai/north-star/,
  D2_DESIGN::.hestai/rules/specs/,
  D3_BLUEPRINT::docs/[architecture_documentation],
  B0_VALIDATION::.hestai/rules/specs/,
  B1_B4_REPORTS::.hestai/state/reports/
]

CRITICAL::"D3 blueprint migrates to docs/ at B1 gate"

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
  B1_01_B1_02::.hestai/rules/specs/[design_phase_artifacts],
  MIGRATION_GATE::manual_checkpoint[verify_D3→docs/],
  B1_03_B1_05::docs/[implementation_documentation]
]

CRITICAL::"B1_02 in .hestai/rules/specs/, B1_03 in docs/ after manual migration"


§6::PROJECT_CONTEXT_STATUS

PURPOSE::"Mitigate worktree isolation with visible project status"

LOCATION::.hestai/state/context/PROJECT-CONTEXT.md

SECTIONS::[
  feature_name_and_branch,
  blueprint_link::docs/,
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
LOCATION::docs/adr/
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
  "PROJECT-CONTEXT.md_prevents_worktree_blindness"
]

===END===
