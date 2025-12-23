===OCTAVE_INTEGRATION===

META:
  TYPE::METHODOLOGY
  ID::octave-integration-guide
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"How HestAI-MCP uses OCTAVE (not the spec itself)"
  DOMAIN::workflow
  OWNERS::[system-steward]
  CREATED::2025-12-21
  UPDATED::2025-12-23
  CANONICAL::.hestai/workflow/octave-integration-guide.oct.md
  TAGS::[octave, mcp-tools, skills, methodology]

---

§1::CANONICAL_SOURCE

SPEC_LOCATION::/Volumes/OCTAVE/octave/specs/
KEY_FILES::[
  octave-5-llm-core.oct.md[syntax+operators+types],
  octave-mcp-architecture.oct.md[MCP_tool_architecture]
]
RULE::"Never duplicate spec—reference canonical source"

---

§2::MCP_TOOLS

OCTAVE_INGEST:
  PURPOSE::parse+normalize+validate_OCTAVE_content
  PIPELINE::[PREPARSE→PARSE→NORMALIZE→VALIDATE→REPAIR→EMIT]
  PARAMETERS::[
    content[OCTAVE_text_to_process],
    schema[validation_schema_e.g._META+SESSION_LOG],
    tier[LOSSLESS∨CONSERVATIVE∨AGGRESSIVE∨ULTRA],
    fix[enable_auto_repair],
    verbose[show_pipeline_stages]
  ]
  NORMALIZATIONS::[
    "->→→",
    "+→⊕",
    "vs→⇌",
    "whitespace_around_::_removed",
    "missing_envelope_inferred"
  ]

OCTAVE_EJECT:
  PURPOSE::project_OCTAVE_to_various_formats
  MODES::[
    canonical[full_validated_lossless],
    authoring[lenient_for_editing],
    executive[STATUS+RISKS+DECISIONS_only_lossy],
    developer[TESTS+CI+DEPS_only_lossy]
  ]
  FORMATS::[octave, json, yaml, markdown]
  TEMPLATE_GENERATION::"Pass null content with schema to generate blank template"

---

§3::SKILLS_INTEGRATION

LOAD_ORDER::[
  1::octave-literacy[essential_syntax+operators],
  2::octave-mastery[semantic_pantheon+advanced_patterns],
  3::octave-compression[transformation_workflow]
]
LOCATION::~/.claude/skills/
ACTIVATION::auto_loaded_by_Claude_Code

---

§4::HESTAI_ARCHITECTURE_ALIGNMENT

// From octave-mcp-architecture.oct.md §15

ALIGNMENT::[
  DUAL_LAYER_CONTEXT::compatible[.hestai/context+.hestai/sessions],
  SINGLE_WRITER_RULE::supported_via_MCP_tools[document_submit∨context_update],
  ODYSSEAN_ANCHOR::recommended_precondition[bind_identity_before_ingest]
]

LIVING_CONTEXT_DOCUMENTS::[
  .hestai/context/PROJECT-CONTEXT.oct.md[project_state]→regenerated_on_clock_in,
  .hestai/context/PROJECT-CHECKLIST.oct.md[phase_tracking]→single_writer_MCP,
  .hestai/context/PROJECT-ROADMAP.oct.md[vision+milestones]→single_writer_MCP,
  .hestai/workflow/000-MCP-PRODUCT-NORTH-STAR*.md[immutables]→governance_change,
  .hestai/reports/*.oct.md[session_archives]→clock_out
]

SESSION_LIFECYCLE::[
  clock_in→reads_.hestai/context/[OCTAVE],
  agent_executes_work,
  clock_out→compresses_session_to_OCTAVE,
  archive→.hestai/reports/{date}-{role}-{session}.oct.md,
  index→.hestai/learnings-index.jsonl
]

---

§5::KNOWLEDGE_ARTIFACT_PATTERNS

DECISION_PATTERN::DECISION_N::BECAUSE[constraint]→choice→outcome
BLOCKER_PATTERN::blocker_name⊗resolved[details]∨blocker_name⊗blocked[reason]
LEARNING_PATTERN::LEARNING::problem→solution→wisdom→transfer_guidance

---

§6::SEMANTIC_COMPRESSION

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

§7::FILE_LOCATIONS

CANONICAL_SPEC[DO_NOT_DUPLICATE]::[
  /Volumes/OCTAVE/octave/specs/octave-5-llm-core.oct.md,
  /Volumes/OCTAVE/octave/specs/octave-mcp-architecture.oct.md
]

HESTAI_INTEGRATION::[
  .hestai/workflow/octave-integration-guide.oct.md[this_file],
  hub/library/octave/README.md[reference_pointer]
]

LIVING_CONTEXT::[
  .hestai/context/*.oct.md[mutable_project_state],
  .hestai/workflow/*.md[north_star+methodology],
  .hestai/reports/*.oct.md[session_archives]
]

PROCESSING_CODE::[
  src/hestai_mcp/mcp/tools/shared/compression.py,
  src/hestai_mcp/mcp/tools/shared/verification.py,
  src/hestai_mcp/mcp/tools/clock_out.py
]

---

§8::CRITICAL_ASSUMPTIONS

ASSUMPTIONS::[
  A4::OCTAVE_READABILITY[85%]→PENDING[B1],
  A6::RAPH_EFFICACY[70%]→PENDING[B1]
]
VALIDATION::through_B1_phase_execution

---

§9::REFERENCES

OCTAVE_SPEC::/Volumes/OCTAVE/octave/specs/
MCP_ARCHITECTURE::/Volumes/OCTAVE/octave/specs/octave-mcp-architecture.oct.md
PRODUCT_NORTH_STAR::.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
ADR_0001::Dual-Layer_Context_Architecture

===END===
