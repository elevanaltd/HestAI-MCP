===SKILL:CODEBASE_SYNTHESIS===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Methodology for extracting patterns from large-scale file sets"

§1::SYNTHESIS_PROTOCOL
STEPS::[
  SCOPE_DEFINITION::"Clarify exact pattern/cause/decision being investigated",
  STRATEGIC_SAMPLING::"Identify representative files using Glob patterns",
  PATTERN_EXTRACTION::"Read targeted files, extract relevant code sections",
  EVIDENCE_AGGREGATION::"Collect citations: file:line_range, snippet",
  SYNTHESIS::"Compress findings into OCTAVE format showing pattern distribution"
]

§2::PATTERN_CATEGORIES
TYPES::[
  ARCHITECTURAL_TENSION::"Forces pulling in opposite directions",
  ASSUMPTION_CASCADE::"Chain of dependencies on unvalidated assumptions",
  CROSS_BOUNDARY_INCONSISTENCY::"Different components assume different invariants",
  VALIDATION_GAP::"Data flows without validation at critical points",
  AUTHORITY_CONFUSION::"Unclear decision ownership"
]

===END===
