# OCTAVE Integration in HestAI-MCP

## Overview

OCTAVE (Olympian Common Text And Vocabulary Engine) v4.1 is the canonical structured format specification for all artifacts, context, and knowledge within HestAI-MCP. It serves as the persistent memory layer, enabling cognitive continuity and knowledge preservation across agent sessions.

**Key Philosophy:** "Strict Protocol for Machines, Flexible Dialect for Minds"

**v4.1 Updates:**
- MCP tools (`octave_ingest`, `octave_eject`) for validation and transformation
- Skills integration (`octave-literacy`, `octave-mastery`, `octave-compression`)
- Unicode operator canonicalization with ASCII alias support

---

## OCTAVE v4.1 Specification

### The Protocol Contract (Strict Enforcement)

OCTAVE v4.1 is defined as a rigid protocol for system tools (validators, indexers, routers) with flexible semantic guidance for human communication.

#### Document Structure

Every OCTAVE v4 document follows this envelope:

```
===DOCUMENT_NAME===
[preface comments (optional)]
META:
  KEY1::VALUE1
  KEY2::VALUE2
[document content]
===END===
```

**Required Components:**
1. **Header:** `===NAME===` as first non-whitespace line
2. **Footer:** `===END===` as last non-whitespace line
3. **META Block:** Immediately after preface, required for all documents
   - Must include `TYPE` key
   - For SESSION_CONTEXT: requires TYPE, SESSION_ID, ROLE, DATE
   - For PROTOCOL_DEFINITION: requires TYPE, VERSION, STATUS

#### Type System

- **STRING:** `bare_word` or `"with spaces"`
- **NUMBER:** `42`, `3.14`, `-1e10`
- **BOOLEAN:** `true`, `false` (lowercase only)
- **NULL:** `null` (lowercase only)

#### Syntax Rules

| Feature | Format | Example |
|---------|--------|---------|
| **Assignment** | `KEY::VALUE` | `ROLE::implementation-lead` |
| **Hierarchy** | 2-space indentation | ` KEY:\n  SUBKEY::VALUE` |
| **Lists** | `[item1, item2, item3]` | `FLOW::[INIT->BUILD->DEPLOY]` |
| **Progression** | `[A->B->C]` | List-only operator |
| **Synthesis** | `A+B` | Binary only (no chaining) |
| **Tension** | `A _VERSUS_ B` | Trade-off expression |

#### Operators

**Canonical Unicode (output by MCP tools):**
- **Flow (`→`):** Sequence progression (inside lists)
- **Synthesis (`⊕`):** Binary combination of elements
- **Tension (`⇌`):** Opposition/trade-off expression
- **Definition (`::`):** Key-value separator

**ASCII Aliases (accepted on input, normalized by `octave_ingest`):**
- `->` → `→`
- `+` → `⊕`
- `_VERSUS_` → `⇌`

**Anti-Patterns (Blocked by Validator):**
- Operator chaining: ❌ `A+B+C` (use nested structures)
- Progression outside lists: ❌ `KEY->VALUE` (use `[A->B]`)
- Tab indentation: ❌ (spaces only)

#### Knowledge Artifacts

OCTAVE extraction layer captures structured knowledge:

**DECISION_N Pattern:**
```
DECISION_1::BECAUSE[reason]→choice→outcome
```

**BLOCKER Pattern:**
```
blocker_name⊗resolved[resolution_details]
blocker_name⊗blocked[what_blocks_it]
```
(Note: ⊗ is UTF-8 U+2297)

**LEARNING Pattern:**
```
LEARNING::problem→solution→wisdom→transfer_guidance
```

---

## OCTAVE Validation

### MCP Tools (Primary Method)

**`octave_ingest`** - Parse, normalize, and validate OCTAVE content:
```
Pipeline: PREPARSE → PARSE → NORMALIZE → VALIDATE → REPAIR → EMIT
```

**Parameters:**
- `content`: OCTAVE text to process
- `schema`: Schema for validation (e.g., `META`, `SESSION_LOG`)
- `tier`: Compression level (`LOSSLESS`, `CONSERVATIVE`, `AGGRESSIVE`, `ULTRA`)
- `fix`: Enable auto-repair for minor issues
- `verbose`: Show pipeline stages

**`octave_eject`** - Project OCTAVE to various formats:

**Modes:**
- `canonical`: Full validated output
- `authoring`: Lenient format for writing
- `executive`: STATUS, RISKS, DECISIONS only
- `developer`: TESTS, CI, DEPS only

**Formats:** `octave`, `json`, `yaml`, `markdown`

**Template Generation:** Pass `null` content with a schema to generate blank template.

---

### Skills Integration

Load skills for OCTAVE competence during authoring:

1. **octave-literacy** (load first): Essential syntax and operators
2. **octave-mastery** (requires literacy): Semantic Pantheon and advanced patterns
3. **octave-compression**: Workflow for transforming verbose content

---

### Legacy Validator Tool

**Location:** `hub/tools/octave-validator.py` (deprecated, prefer MCP tools)

**Profiles:**
- `protocol` (default): Strict enforcement for system tools
- `hestai-agent`: Allows YAML frontmatter, relaxed operator rules
- `hestai-skill`: Includes SECTION_ORDER validation

**Usage:**
```bash
# Validate single file
python hub/tools/octave-validator.py path/to/file.oct.md --profile hestai-agent

# Scan directory
python hub/tools/octave-validator.py --path . --profile protocol
```

---

## OCTAVE in HestAI-MCP Architecture

### Living Context Documents (.oct.md)

All operational context is stored in OCTAVE format for compression, structure, and searchability.

#### .hestai/context/ (Mutable Context Layer)

Generated fresh on each `clock_in`, single-writer pattern via System Steward MCP tools.

**PROJECT-CONTEXT.oct.md**
```octave
===PROJECT_CONTEXT===
META:
  NAME::"HestAI-MCP Operational Context"
  VERSION::"0.1.0"
  PHASE::PHASE_0_FOUNDATION
  STATUS::fresh_start_initialized

PURPOSE::"Project state, active work, blockers, achievements"

ACTIVE_WORK::[
  Phase_0::completed,
  Phase_1::completed,
  Phase_2::in_progress
]

BLOCKERS::none

NEXT_ACTIONS::[
  1::Port_additional_tests,
  2::Implement_document_submit_tool
]
===END===
```

**PROJECT-CHECKLIST.oct.md**
- Tracks all phase completions
- Documents quality gates (pytest, ruff, black, mypy)
- Records test passing counts
- Captures commit history

**PROJECT-ROADMAP.oct.md**
- Vision and horizon
- Phase deliverables
- Progress metrics
- Timeline tracking

#### .hestai/workflow/ (North Star Documents)

System-governance and product-specific decision-logic.

**000-MCP-PRODUCT-NORTH-STAR-SUMMARY.oct.md**
- 6 Immutables (I1-I6)
- Critical assumptions (A4: OCTAVE_READABILITY, A6: RAPH_EFFICACY)
- Constrained variables
- Scope boundaries
- Agent escalation routes

#### .hestai/reports/ (Session Archives)

Timestamped OCTAVE compression artifacts from `clock_out`:

**Format:** `{YYYY-MM-DD}-{role}-{phase}.oct.md`

**Content:**
```octave
===SESSION_COMPRESSION===
META:
  SESSION_ID::"83fe7568"
  ROLE::octave-specialist
  DATE::2025-12-21
  DURATION::session_duration

DECISIONS::[
  DECISION_1::BECAUSE[constraint]→choice→outcome
]

BLOCKERS::[
  blocker_1⊗resolved[details]
]

LEARNINGS::[
  problem→solution→wisdom
]

OUTCOMES::[
  outcome_1[metric_with_context]
]

NEXT_ACTIONS::[
  ACTION_1::owner→description
]
===END===
```

---

## OCTAVE Processing Pipeline

### Session Lifecycle: OCTAVE Compression

When agents `clock_out`, HestAI-MCP executes the compression pipeline:

#### 1. **Transcript Extraction** (clock_out.py)
- Reads Claude JSONL session transcript
- Parses with `ClaudeJsonlLens` schema-on-read parser
- Validates session_id, prevents path traversal

#### 2. **Sensitive Redaction** (clock_out.py)
- Strips API keys, tokens, passwords from tool invocations
- Redacts credentials from transcript before archival
- Security-first: explicit sensitive-pattern list

#### 3. **OCTAVE Compression** (compression.py)
- Calls AIClient with session-compression-protocol prompt
- Extracts DECISIONS, BLOCKERS, LEARNINGS from transcript
- Achieves 60-80% compression with causal fidelity
- Returns `None` on failure (graceful degradation)

**Compression Algorithm:**
```
1. IDENTIFY_MARKERS: decisions, blockers, learnings, outcomes, actions
2. RECONSTRUCT_CAUSALITY: BECAUSE[reason]→choice→outcome
3. GROUND_WITH_SCENARIOS: concrete_examples_for_abstractions
4. PRESERVE_METRICS: include[context+baseline+validation]
```

#### 4. **Context Extraction** (context_extraction.py)
- Parses DECISIONS, OUTCOMES, BLOCKERS from compressed OCTAVE
- Extracts high-signal content for PROJECT-CONTEXT update
- Formats for `context_update` tool consumption

#### 5. **Verification** (verification.py)
- Validates OCTAVE content claims before context sync
- **Check 1:** FILES_MODIFIED references exist
- **Check 2:** Markdown links resolve
- **Check 3:** No path traversal attempts
- **Check 4:** No references to sensitive paths (warnings only)
- **Design:** Fail-closed—blocks bad context rather than corruption

#### 6. **Learnings Indexing** (learnings_index.py)
- Parses DECISION_N, BLOCKER_N, LEARNING_N keys
- Creates searchable knowledge base entries (JSONL)
- Atomic append to `.hestai/learnings-index.jsonl`
- Enables future wisdom retrieval and search

#### 7. **Artifact Archival**
- Saves compressed OCTAVE to `.hestai/reports/{timestamp}.oct.md`
- Keeps raw JSONL for complete session history
- Both artifacts committed to git (via System Steward)

---

## OCTAVE Semantic Compression

### Mythological Primitives

OCTAVE uses Greek mythology for semantic compression:

| Archetype | Semantic | Operational |
|-----------|----------|-------------|
| **ATHENA** | Strategy, Architecture, Wisdom | MANDATE_DECISION[24h] |
| **HEPHAESTUS** | Implementation, Code, Build | BUILD_CHECK |
| **HERMES** | Communication, Interfaces, APIs | CONTRACT_VERIFY |
| **APOLLO** | Illumination, Clarity, Truth | VISION_ALIGNMENT |
| **ODYSSEUS** | Navigation, Journey, Persistence | MILESTONE_TRACKING |
| **ARGUS** | Vigilance, Observation, Boundaries | ENFORCEMENT_WATCH |

### Pattern Primitives

| Pattern | Semantic | Operational |
|---------|----------|-------------|
| **ODYSSEAN** | Long navigational journey | MILESTONE_TRACKING |
| **SISYPHEAN** | Repetitive, futile cycles | ESCALATE_AFTER[3] |
| **GORDIAN** | Cutting through complexity | SIMPLIFY_NOW |

### Application in HestAI-MCP

**North Star Structure:**
```octave
I1::PERSISTENT_COGNITIVE_CONTINUITY::[
  PRINCIPLE::system_must_persist_context_decisions_learnings_across_sessions,
  WHY::prevents_costly_re-learning+amnesia_is_system_failure,
  STATUS::PENDING[implementation-lead@B1]
]
```

**Session Compression:**
```octave
DECISIONS::[
  DECISION_1::BECAUSE[ATHENA_constraint]→choice→outcome
]
```

**Context Updates:**
```octave
ACTIVE_WORK::[
  ODYSSEAN_journey::phase_0->phase_1->phase_2,
  GORDIAN_simplification::removed_symlinks->direct_.hestai
]
```

---

## OCTAVE Micro Primer

For quick reference, the 6-rule quick-start:

```octave
===OCTAVE_MICRO_PRIMER===
META:
  NAME::"OCTAVE Essentials"
  VERSION::"4.0"

RULES:
  1_STRUCTURE::"===NAME=== ... ===END==="
  2_META::"Always include META: section"
  3_ASSIGNMENT::"KEY::VALUE (double colon)"
  4_HIERARCHY::"Exactly 2 spaces per indent level"
  5_LISTS::"[item1, item2, item3] no trailing comma"
  6_OPERATORS::[
    PROGRESSION::"[A->B->C] in lists only",
    SYNTHESIS::"A+B binary only",
    TENSION::"A _VERSUS_ B"
  ]

TYPES:
  STRING::bare_word or "with spaces"
  NUMBER::42, 3.14, -1e10
  BOOLEAN::true, false
  NULL::null

===END===
```

---

## OCTAVE Quality Assurance

### Pre-Commit Hook (Optional)

Enable local OCTAVE validation before commits:

```bash
mkdir -p $HOME/.githooks
printf '#!/bin/sh\npython3 hub/tools/octave-validator.py --path . || exit $?\n' > $HOME/.githooks/pre-commit
chmod +x $HOME/.githooks/pre-commit
git config core.hooksPath $HOME/.githooks
```

### Continuous Quality

**CI Pipeline Integration:**
- All `.oct.md` files validated on PR
- `ruff`, `black`, `mypy` also enforce syntax
- Schemas extracted and verified before merge

**Local Validation:**
```bash
python3 hub/tools/octave-validator.py hub/library/octave/octave-spec.oct.md
python3 hub/tools/octave-validator.py --path .hestai/context/ --profile protocol
```

---

## OCTAVE in Production: HestAI-MCP Workflow

### Context Continuity (I1 Immutable)

```
Agent Session Start
  ↓
clock_in() → reads .hestai/context/ (OCTAVE files)
  ↓
Agent sees PROJECT-CONTEXT, PROJECT-ROADMAP, PROJECT-CHECKLIST
  ↓
Agent executes work
  ↓
clock_out() → compresses session to OCTAVE
  ↓
OCTAVE compressed to .hestai/reports/{timestamp}.oct.md
  ↓
Learnings indexed → .hestai/learnings-index.jsonl
  ↓
Next agent reads updated context
```

### Governance Enforcement (I3 Immutable)

```
.hestai-sys/ (read-only governance, injected by MCP)
  ├── agents/ (role definitions)
  ├── rules/ (compliance gates)
  └── workflow/ (system constitution)

.hestai/ (mutable context, single-writer)
  ├── context/ (PROJECT-*, living state)
  ├── workflow/ (product North Star)
  └── reports/ (compressed sessions)
```

### Freshness Verification (I4 Immutable)

```octave
CONTEXT_METADATA:
  CREATED::2025-12-21T01:13:00Z
  LAST_UPDATED::2025-12-21T06:15:00Z
  STALE_AFTER::24h

PRE_COMMIT_CHECK:
  IF::now - LAST_UPDATED > STALE_AFTER
  THEN::[WARN, suggest_refresh, allow_override]
```

---

## File Locations Summary

### Core Specification
- **Canonical Spec:** `/Volumes/OCTAVE/octave/specs/octave-4.oct.md`
- **Local Mirror:** `hub/library/octave/octave-spec.oct.md`
- **Micro Primer:** `hub/library/octave/octave-micro-primer.oct.md`
- **Validator Tool:** `hub/tools/octave-validator.py`

### Living Context (Mutable)
- **Project Context:** `.hestai/context/PROJECT-CONTEXT.oct.md`
- **Checklist:** `.hestai/context/PROJECT-CHECKLIST.oct.md`
- **Roadmap:** `.hestai/context/PROJECT-ROADMAP.oct.md`
- **Assessment:** `.hestai/context/test-infrastructure-assessment.oct.md`

### North Stars
- **System NS:** `hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR-SUMMARY.oct.md`
- **Product NS:** `.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR-SUMMARY.oct.md`

### Session Archives
- **Reports:** `.hestai/reports/{YYYY-MM-DD}-{role}-{session_id}.oct.md`
- **Learnings Index:** `.hestai/learnings-index.jsonl`
- **Raw Transcripts:** `.hestai/sessions/archive/{session_id}.jsonl`

### Processing Code
- **Compression:** `src/hestai_mcp/mcp/tools/shared/compression.py`
- **Verification:** `src/hestai_mcp/mcp/tools/shared/verification.py`
- **Context Extraction:** `src/hestai_mcp/mcp/tools/shared/context_extraction.py`
- **Learnings Index:** `src/hestai_mcp/mcp/tools/shared/learnings_index.py`
- **Clock Out:** `src/hestai_mcp/mcp/tools/clock_out.py`

---

## Critical Assumptions (From North Star)

| Assumption | Confidence | Status | Owner |
|-----------|-----------|--------|-------|
| **A4: OCTAVE Readability** | 85% | PENDING | AI-Lead@B1 |
| **A6: RAPH Efficacy** | 70% | PENDING | AI-Lead@B1 |

These assumptions are validated through B1 phase execution. Readability measured by agent comprehension; efficacy measured by RAPH vector accuracy and consistency.

---

## Design Decisions

### Why OCTAVE for HestAI-MCP?

1. **Compression:** 60-80% token reduction vs. prose (critical for context windows)
2. **Structure:** Protocol contract enables reliable extraction for system tools
3. **Semantic:** Mythological primitives compress domain knowledge
4. **Persistence:** OCTAVE files are version-controllable and searchable
5. **Interop:** Canonical spec enables multi-project synchronization

### Single-Writer Pattern

Context updates flow through System Steward MCP tools only:
- Prevents concurrent writes
- Ensures atomic transactions
- Maintains audit trails (git history)
- Supports rollback to previous state

### Fail-Closed Verification

Verification gates **block** corrupted context rather than allowing broken references:
- Path traversal attempts → immediate rejection
- Broken file references → blocks context sync
- Sensitive path leakage → warnings only (recorded)
- Better to skip update than corrupt context

---

## Future Enhancements

### Planned Features

1. **Context Registry (RFC-0001):** Searchable index of all context documents
2. **Learnings Retrieval API:** Query semantic knowledge base
3. **OCTAVE-to-JSON Transformation:** Enable API consumption of context
4. **Multi-Repo OCTAVE Sync:** Federated context across HestAI projects
5. **RAPH Integration:** Bind agent identity through OCTAVE verification

### B2+ Phase Work

- Implement full `context_update` tool (Phase 3)
- Add OCTAVE schema validation beyond v4 protocol
- Build learnings search interface
- Create OCTAVE view of system state
- Establish cross-project context federation

---

## References

- **OCTAVE v4 Canonical:** `/Volumes/OCTAVE/octave/specs/octave-4.oct.md`
- **HestAI-MCP Repo:** `/Volumes/HestAI-MCP/worktrees/octave-as-its-own-tool/`
- **System North Star:** `hub/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md`
- **ADR-0001 (Dual-Layer):** Architecture Decision Record on context architecture
- **ADR-0007 (Direct .hestai):** Architecture Decision Record on removing symlinks
