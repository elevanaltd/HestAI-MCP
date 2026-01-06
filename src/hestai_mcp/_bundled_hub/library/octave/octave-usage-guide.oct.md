===OCTAVE_USAGE_GUIDE===

META:
  TYPE::GUIDE
  ID::octave-usage-guide
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"How to use OCTAVE in HestAI projects (consumer-facing)"
  DOMAIN::library
  OWNERS::[system-steward]
  CREATED::2025-12-23
  CANONICAL::.hestai-sys/library/octave/octave-usage-guide.oct.md
  SOURCE::src/hestai_mcp/_bundled_hub/library/octave/octave-usage-guide.oct.md
  TAGS::[octave, mcp-tools, skills, guide]

---

§1::CANONICAL_SPEC

// DO NOT duplicate the OCTAVE specification here.
// Reference the canonical source.

SPEC_LOCATION::/Volumes/OCTAVE/octave/specs/
KEY_FILES::[
  octave-5-llm-core.oct.md[syntax+operators+types],
  octave-5-llm-data.oct.md[data_mode_patterns],
  octave-5-llm-schema.oct.md[schema_mode_holographic],
  octave-mcp-architecture.oct.md[MCP_tool_architecture]
]

---

§2::MCP_TOOLS

OCTAVE_INGEST:
  PURPOSE::parse+normalize+validate_OCTAVE_content
  PIPELINE::[PREPARSE→PARSE→NORMALIZE→VALIDATE→REPAIR→EMIT]
  PARAMETERS::[
    content[OCTAVE_text_to_process∧REQ],
    schema[validation_schema∧REQ],
    tier[LOSSLESS∨CONSERVATIVE∨AGGRESSIVE∨ULTRA∧OPT],
    fix[enable_auto_repair∧OPT],
    verbose[show_pipeline_stages∧OPT]
  ]
  NORMALIZATIONS::[
    "->→→[flow]",
    "+→⊕[synthesis]",
    "vs→⇌[tension]",
    "whitespace_around_::→removed",
    "missing_envelope→inferred"
  ]

OCTAVE_EJECT:
  PURPOSE::project_OCTAVE_to_various_formats
  MODES::[
    canonical[full_validated∧lossless],
    authoring[lenient_for_editing∧lossless],
    executive[STATUS+RISKS+DECISIONS∧lossy],
    developer[TESTS+CI+DEPS∧lossy]
  ]
  FORMATS::[octave, json, yaml, markdown]
  TEMPLATE::"Pass null content with schema to generate blank template"

---

§3::SKILLS

// Skills provide OCTAVE competence during authoring.
// Load in order (each builds on previous).

LOAD_ORDER::[
  1::octave-literacy[essential_syntax+operators],
  2::octave-mastery[semantic_pantheon+advanced_patterns],
  3::octave-compression[transformation_workflow]
]

LOCATION::~/.claude/skills/
ACTIVATION::auto_loaded_by_Claude_Code_on_trigger

---

§4::HESTAI_ALIGNMENT

// OCTAVE integrates with HestAI dual-layer architecture.

DUAL_LAYER_CONTEXT::[
  .hestai/context/→OCTAVE_format[PROJECT-CONTEXT.oct.md_etc],
  .hestai/sessions/→session_artifacts,
  .hestai/workflow/→methodology[north_stars+decisions]
]

SINGLE_WRITER_RULE::[
  agents_read_OCTAVE_files_directly,
  agents_write_via_MCP_tools[document_submit∨context_update],
  system_steward_validates+commits
]

SESSION_LIFECYCLE::[
  clock_in→reads_.hestai/context/[OCTAVE_format],
  agent_executes_work,
  clock_out→compresses_session_to_OCTAVE,
  archive→.hestai/reports/{date}-{role}-{session}.oct.md
]

---

§5::KNOWLEDGE_PATTERNS

// Standard patterns for extractable knowledge artifacts.

DECISION::"DECISION_N::BECAUSE[constraint]→choice→outcome"
BLOCKER::"blocker_name⊗resolved[details]"∨"blocker_name⊗blocked[reason]"
LEARNING::"LEARNING::problem→solution→wisdom→transfer"

---

§6::SEMANTIC_COMPRESSION

// Greek mythology provides semantic density.

ARCHETYPES::[
  ATHENA[strategy+wisdom]→architecture_decisions,
  HEPHAESTUS[implementation+build]→code_changes,
  HERMES[communication+APIs]→interface_contracts,
  APOLLO[clarity+truth]→validation+analysis,
  ODYSSEUS[navigation+journey]→phase_progression,
  ARGUS[vigilance+boundaries]→enforcement+gates
]

PATTERNS::[
  ODYSSEAN[long_journey_with_goal]→multi_phase_projects,
  SISYPHEAN[repetitive_cycles]→tech_debt+maintenance,
  GORDIAN[cut_through_complexity]→simplification_decisions
]

---

§7::FORMAT_DECISION

// When to use OCTAVE vs Markdown.

USE_OCTAVE[.oct.md]::[
  agent_constitutions,
  governance_rules,
  north_stars,
  methodology_docs,
  context_files[PROJECT-CONTEXT_etc],
  session_archives
]

USE_MARKDOWN[.md]::[
  developer_guides,
  ADRs,
  READMEs,
  setup_instructions
]

DECISION_TREE::[
  "Primary audience AI agents?"→YES→.oct.md,
  "Governance/methodology/constitution?"→YES→.oct.md,
  "Primary audience human developers?"→YES→.md,
  "ADR or setup guide?"→YES→.md
]

===END===
