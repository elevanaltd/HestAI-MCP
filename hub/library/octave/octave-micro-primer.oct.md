===OCTAVE_MICRO_PRIMER===
// Essential OCTAVE v4.1 in 6 rules (110-140 tokens)

META:
  NAME::"OCTAVE Micro Primer"
  VERSION::"4.1"
  PURPOSE::"Minimal viable OCTAVE for direct model emission"

SEMANTIC_MODE::"Use Greek mythology for compression (domains/patterns/forces)"

RULES:
  1_STRUCTURE::"Start with ===NAME=== and end with ===END==="
  2_META::"Include META: immediately after header (required)"
  3_ASSIGNMENT::"KEY::VALUE uses double colon"
  4_HIERARCHY::"Indent exactly 2 spaces per level"
  5_LISTS::"[item1, item2, item3] no trailing comma"
  6_OPERATORS:
    // Canonical Unicode (MCP tools normalize to these)
    FLOW::"→ (ASCII alias: ->)"
    SYNTHESIS::"⊕ (ASCII alias: +)"
    TENSION::"⇌ (ASCII alias: _VERSUS_)"

TYPES:
  STRING::bare_word or "with spaces"
  NUMBER::42, 3.14, -1e10
  BOOLEAN::true, false (lowercase only)
  NULL::null (lowercase only)

EXAMPLE:
  STATUS::DEGRADED
  PATTERN::ICARIAN_TRAJECTORY
  FLOW::[INIT→BUILD→DEPLOY]
  TENSION::SPEED⇌RELIABILITY
  METRICS:
    CPU::94
    MEMORY::82

MCP_VALIDATION::"Use octave_ingest tool to validate and normalize"

===END===
