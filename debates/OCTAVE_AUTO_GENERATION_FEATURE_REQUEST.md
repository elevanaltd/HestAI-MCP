# Feature Request: OCTAVE Auto-Generation on close_debate

## Issue Context

**Related to**: issue 63, phase 4 - Debate Artifacts Systematization
**Repository**: debate-hall-mcp
**Requested Feature**: Enhance `close_debate` tool to auto-generate OCTAVE format transcript

## Problem Statement

Currently, debate-hall-mcp outputs debate transcripts in JSON format. This requires post-processing to convert to OCTAVE (semantic documentation format) for:
- Architectural decision archival
- Knowledge preservation
- Cross-repository governance documentation
- Improved searchability and semantic density

## Current Workflow (Manual)

1. Run debate through debate-hall-mcp (outputs JSON)
2. Manually parse JSON structure
3. Transform debate turns to OCTAVE format
4. Validate OCTAVE syntax
5. Commit to repository

**Pain points**:
- 15-20 minutes of manual work per debate
- Error-prone transformation
- No consistency enforcement
- Bloats tool invocation pipeline

## Proposed Enhancement

### New Parameter for `close_debate`

```python
close_debate(
    thread_id: str,
    synthesis: str,
    output_format: Literal["json", "octave", "both"] = "json"
) -> dict
```

### OCTAVE Output Structure

When `output_format` is "octave" or "both", generate:

```octave
===DEBATE_TRANSCRIPT===
META:
  TYPE::"DEBATE_RECORD"
  THREAD_ID::"{thread_id}"
  DATE::"{transcript_date}"
  TOPIC::"{debate_topic}"
  STATUS::"SYNTHESIS"
  MODE::"{mode}"
  ROUNDS::{round_count}
  TURNS::{turn_count}

DEBATE_CONTEXT:
  QUESTION::"{debate_topic}"
  PARTICIPANTS::[Wind,Wall,Door]
  COGNITIONS::[PATHOS,ETHOS,LOGOS]

TURN_1_WIND:
  AGENT::"..."
  COGNITION::PATHOS
  [structured turn content...]

TURN_2_WALL:
  [structured turn content...]

TURN_3_DOOR:
  [structured turn content...]

FINAL_SYNTHESIS:
  NAME::"..."
  DECISION::"..."
  STATUS::"..."

===END===
```

### Transformation Rules

**Per Turn Mapping**:
- `role` → `TURN_N_{ROLE}` (Wind/Wall/Door)
- `cognition` → `COGNITION::{type}` (PATHOS/ETHOS/LOGOS)
- `agent_role` → `AGENT::"..."`
- `content` → Parsed to semantic structure (not raw markdown)
- `timestamp` → Metadata context
- `hash` → Integrity tracking (optional)

**Synthesis Consolidation**:
- Extract Door's final synthesis turn
- Create FINAL_SYNTHESIS block with consolidated insights
- Map Wind accepted insights
- Map Wall accepted constraints
- Map Door verdict and next actions

**String Sanitization**:
- Replace hyphens with underscores in values (OCTAVE parser requirement)
- Escape quotes appropriately
- Validate no special characters in keys
- Compress whitespace

### Return Value

```python
{
    "status": "success",
    "thread_id": "...",
    "format": "both|octave|json",
    "outputs": {
        "json_path": "/path/to/file.json",
        "octave_path": "/path/to/file.oct.md"  # if format includes octave
    },
    "validation": {
        "octave_valid": true,
        "compression_ratio": 0.75,  # new size / original size
        "metadata": {...}
    }
}
```

## Implementation Benefits

1. **Automation**: Zero-touch conversion from JSON to OCTAVE
2. **Consistency**: Standardized transformation logic
3. **Archival**: Direct .oct.md files ready for git commit
4. **Compression**: OCTAVE format achieves 20-25% size reduction
5. **Governance**: Architectural decisions immediately documentable
6. **Velocity**: Debate → Decision artifact in single step

## Integration Points

- System Steward MCP tools can reference auto-generated OCTAVE files
- CI/CD pipelines can validate OCTAVE compliance
- Documentation systems can index semantic transcripts
- Agents can `@tag` OCTAVE debate files for cross-reference

## Existing Proof

HestAI-MCP has successfully converted 4 debate transcripts:
- `2025-12-26-adr-rfc-alignment.oct.md` (RFC/ADR unification)
- `2025-12-26-adr-rfc-alignment-v2-agoral-forge.oct.md` (Discussions integration)
- `2024-12-24-hestai-context-architecture.oct.md` (Directory structure)
- `2024-12-25-hestai-context-distribution.oct.md` (Context distribution)

All validate successfully against OCTAVE v5.1.0 schema.

## Alternative: Issue 26 Linkage

If debate-hall-mcp issue 26 already addresses this, this feature request should be linked as enhancement/expansion rather than duplication.

## Acceptance Criteria

- [ ] `close_debate` accepts `output_format` parameter
- [ ] OCTAVE output validates against OCTAVE schema
- [ ] Compression ratio documented (target: 20-30%)
- [ ] All cognitive roles and turns preserved in OCTAVE
- [ ] Example debate transcript conversion included in tests
- [ ] Documentation updated with OCTAVE format spec
