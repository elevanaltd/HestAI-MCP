===HESTAI_MCP_OCTAVE_INTERNAL===

META:
  TYPE::METHODOLOGY
  ID::hestai-mcp-octave-internal
  VERSION::"1.0"
  STATUS::ACTIVE
  PURPOSE::"HestAI-MCP internal OCTAVE integration notes (not for consumers)"
  DOMAIN::workflow
  OWNERS::[system-steward]
  CREATED::2025-12-21
  UPDATED::2025-12-23
  CANONICAL::.hestai/workflow/octave-integration-guide.oct.md
  TAGS::[octave, internal, hestai-mcp]

---

// This file is HestAI-MCP INTERNAL documentation.
// Consumer-facing OCTAVE guide: .hestai-sys/library/octave/octave-usage-guide.oct.md

§1::INTERNAL_FILE_LOCATIONS

PROCESSING_CODE::[
  src/hestai_mcp/mcp/tools/shared/compression.py[session_compression],
  src/hestai_mcp/mcp/tools/shared/verification.py[content_validation],
  src/hestai_mcp/mcp/tools/clock_out.py[session_archival],
  src/hestai_mcp/mcp/tools/clock_in.py[context_loading]
]

CONTEXT_FILES::[
  .hestai/context/PROJECT-CONTEXT.oct.md[project_dashboard],
  .hestai/context/PROJECT-CHECKLIST.oct.md[phase_tracking],
  .hestai/context/PROJECT-ROADMAP.oct.md[vision+milestones]
]

---

§2::CRITICAL_ASSUMPTIONS

// These assumptions are HestAI-MCP specific validation targets.

ASSUMPTIONS::[
  A4::OCTAVE_READABILITY[85%]→PENDING[B1],
  A6::RAPH_EFFICACY[70%]→PENDING[B1]
]
VALIDATION::through_B1_phase_execution

---

§3::INTERNAL_REFERENCES

OCTAVE_SPEC::/Volumes/OCTAVE/octave/specs/
CONSUMER_GUIDE::.hestai-sys/library/octave/octave-usage-guide.oct.md
PRODUCT_NORTH_STAR::.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md
ADR_0033::docs/adr/adr-0033-dual-layer-context-architecture.md

===END===
