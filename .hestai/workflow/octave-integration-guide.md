# OCTAVE Integration in HestAI-MCP

## Overview

OCTAVE (Olympian Common Text And Vocabulary Engine) v5.1 is the canonical structured format for all HestAI-MCP artifacts. This guide covers **how HestAI-MCP uses OCTAVE**, not the OCTAVE spec itself.

**Canonical Specification:** `/Volumes/OCTAVE/octave/specs/`

**Key Files:**
- `octave-5-llm-core.oct.md` - Core syntax, operators, types
- `octave-mcp-architecture.oct.md` - MCP tool architecture

---

## MCP Tools

### octave_ingest

Parse, normalize, and validate OCTAVE content.

**Pipeline:** `PREPARSE → PARSE → NORMALIZE → VALIDATE → REPAIR → EMIT`

**Parameters:**
- `content` - OCTAVE text to process
- `schema` - Schema for validation (e.g., `META`, `SESSION_LOG`)
- `tier` - Compression level (`LOSSLESS`, `CONSERVATIVE`, `AGGRESSIVE`, `ULTRA`)
- `fix` - Enable auto-repair for minor issues
- `verbose` - Show pipeline stages

**Normalization:**
- ASCII aliases (`->`, `+`, `vs`) normalized to Unicode (`→`, `⊕`, `⇌`)
- Whitespace around `::` removed
- Missing envelope inferred for single documents

### octave_eject

Project OCTAVE content to various formats.

**Modes:**
- `canonical` - Full validated output (lossless)
- `authoring` - Lenient format for editing
- `executive` - STATUS, RISKS, DECISIONS only (lossy)
- `developer` - TESTS, CI, DEPS only (lossy)

**Formats:** `octave`, `json`, `yaml`, `markdown`

**Template Generation:** Pass `null` content with a schema to generate blank template.

---

## Skills Integration

Load skills for OCTAVE competence during authoring:

1. **octave-literacy** (load first) - Essential syntax and operators
2. **octave-mastery** (requires literacy) - Semantic Pantheon and advanced patterns
3. **octave-compression** - Workflow for transforming verbose content

Skills are located in `~/.claude/skills/` and auto-loaded by Claude Code.

---

## HestAI-MCP Architecture Alignment

From `octave-mcp-architecture.oct.md` §15:

```
ALIGNMENT::[
  DUAL_LAYER_CONTEXT::compatible[documents_in_.hestai/context, sessions_in_.hestai/sessions],
  SINGLE_WRITER_RULE::supported_via_MCP_tools[use_document_submit|context_update],
  ODYSSEAN_ANCHOR::recommended_precondition[bind_agent_identity_before_ingest]
]
```

### Living Context Documents

All operational context in `.hestai/` uses OCTAVE format:

| Location | Purpose | Update Pattern |
|----------|---------|----------------|
| `.hestai/context/PROJECT-CONTEXT.oct.md` | Project state, blockers, achievements | Regenerated on clock_in |
| `.hestai/context/PROJECT-CHECKLIST.oct.md` | Phase tracking, quality gates | Single-writer MCP |
| `.hestai/context/PROJECT-ROADMAP.oct.md` | Vision, phases, milestones | Single-writer MCP |
| `.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR*.md` | Product immutables | Governance change |
| `.hestai/reports/*.oct.md` | Compressed session archives | clock_out |

### Session Lifecycle

```
clock_in() → reads .hestai/context/ (OCTAVE)
    ↓
Agent executes work
    ↓
clock_out() → compresses session to OCTAVE
    ↓
Archive: .hestai/reports/{date}-{role}-{session}.oct.md
    ↓
Learnings indexed: .hestai/learnings-index.jsonl
```

---

## Knowledge Artifact Patterns

OCTAVE extraction captures structured knowledge:

**DECISION Pattern:**
```octave
DECISION_1::BECAUSE[constraint]→choice→outcome
```

**BLOCKER Pattern:**
```octave
blocker_name⊗resolved[resolution_details]
blocker_name⊗blocked[what_blocks_it]
```

**LEARNING Pattern:**
```octave
LEARNING::problem→solution→wisdom→transfer_guidance
```

---

## Semantic Compression

OCTAVE uses Greek mythology for semantic density:

| Archetype | Semantic | Use In HestAI |
|-----------|----------|---------------|
| ATHENA | Strategy, Wisdom | Architecture decisions |
| HEPHAESTUS | Implementation, Build | Code changes |
| HERMES | Communication, APIs | Interface contracts |
| APOLLO | Clarity, Truth | Validation, analysis |
| ODYSSEUS | Navigation, Journey | Phase progression |
| ARGUS | Vigilance, Boundaries | Enforcement, gates |

| Pattern | Semantic | Use In HestAI |
|---------|----------|---------------|
| ODYSSEAN | Long journey with goal | Multi-phase projects |
| SISYPHEAN | Repetitive cycles | Tech debt, maintenance |
| GORDIAN | Cut through complexity | Simplification decisions |

---

## File Locations

### Canonical Specification (DO NOT DUPLICATE)
- `/Volumes/OCTAVE/octave/specs/octave-5-llm-core.oct.md`
- `/Volumes/OCTAVE/octave/specs/octave-mcp-architecture.oct.md`

### HestAI-MCP Integration
- `.hestai/workflow/octave-integration-guide.md` (this file)
- `hub/library/octave/README.md` (reference pointer)

### Living Context
- `.hestai/context/*.oct.md` - Mutable project state
- `.hestai/workflow/*.md` - North Star and methodology
- `.hestai/reports/*.oct.md` - Session archives

### Processing Code
- `src/hestai_mcp/mcp/tools/shared/compression.py`
- `src/hestai_mcp/mcp/tools/shared/verification.py`
- `src/hestai_mcp/mcp/tools/clock_out.py`

---

## Critical Assumptions

| ID | Assumption | Confidence | Status |
|----|-----------|-----------|--------|
| A4 | OCTAVE Readability | 85% | PENDING[B1] |
| A6 | RAPH Efficacy | 70% | PENDING[B1] |

Validated through B1 phase execution.

---

## References

- **OCTAVE v5.1 Spec:** `/Volumes/OCTAVE/octave/specs/`
- **MCP Architecture:** `/Volumes/OCTAVE/octave/specs/octave-mcp-architecture.oct.md`
- **Product North Star:** `.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md`
- **ADR-0001:** Dual-Layer Context Architecture
