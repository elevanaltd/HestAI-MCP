# hestai-context-mcp Interface Contract

**Created**: 2026-04-06
**Purpose**: Define the TARGET-STATE MCP tool endpoints for `hestai-context-mcp` after Phase 1 harvest. This is Wall's Mitigation M2.
**Satisfies**: ADR-0353 §Implementation Phase 1
**Transport**: stdio (JSON-RPC over stdin/stdout)
**Important**: This document describes the POST-Phase-1 target state of `hestai-context-mcp` (a new repo). It does NOT describe the current `hestai-mcp` server, which retains `bind`, `ensure_system_governance()`, and different return shapes. Current state is defined in `src/hestai_mcp/mcp/server.py`.

---

## 1. SCOPE: What Stays, What Goes

### RETAINED (System Steward core)

| Tool | Lines | Rationale |
|------|-------|-----------|
| `clock_in` | 955 | Session lifecycle, context synthesis, focus resolution |
| `clock_out` | 260 | Knowledge extraction, redaction, archival |
| `submit_review` | ~100 | Review infrastructure, CI gate clearing |

### DELETED (moved to Vault + Workbench)

| Tool | Rationale |
|------|-----------|
| `bind` | Identity injection — replaced by Vault + Payload Compiler |
| `ensure_system_governance()` | `.hestai-sys/` delivery — replaced by Vault |
| `bootstrap_system_governance()` | Bundled hub injection — replaced by Vault |
| All `_bundled_hub/` references | Identity content — moved to Vault |

### ADDED (new in subtracted engine)

| Tool | Rationale |
|------|-----------|
| `get_context` | Read-only context synthesis without creating a session. Enables Payload Compiler preview, CI pipelines, and lightweight reads. |

---

## 2. TOOL SIGNATURES

### 2.1 `clock_in`

**Purpose**: Register agent session start. Create session tracking. Synthesize dynamic project context. Return structured data for KVAEPH Position 3 injection.

**Callers**: Workbench Payload Compiler (at dispatch time) OR CLI agent (direct terminal use).

```json
{
  "name": "clock_in",
  "inputSchema": {
    "type": "object",
    "properties": {
      "role": {
        "type": "string",
        "description": "Agent role name (e.g., 'implementation-lead')"
      },
      "working_dir": {
        "type": "string",
        "description": "Absolute path to project working directory"
      },
      "focus": {
        "type": "string",
        "description": "Work focus area. Auto-inferred from branch if omitted.",
        "default": "general"
      },
      "model": {
        "type": "string",
        "description": "Optional AI model identifier for session metadata"
      }
    },
    "required": ["role", "working_dir"]
  }
}
```

**Returns**:

```json
{
  "session_id": "string — UUID for this session",
  "role": "string — resolved role name",
  "focus": "string — resolved focus (explicit, branch-inferred, or 'general')",
  "focus_source": "string — 'explicit' | 'github_issue' | 'branch' | 'default'",
  "branch": "string — current git branch name",
  "working_dir": "string — absolute path",
  "context_paths": ["string[] — absolute paths to OCTAVE context files for agent to read"],
  "context": {
    "product_north_star": "string | null — contents of Product North Star if found",
    "project_context": "string | null — contents of PROJECT-CONTEXT.oct.md if found",
    "phase_constraints": "object | null — ContextSteward-synthesized phase constraints",
    "git_state": {
      "branch": "string",
      "ahead": "integer",
      "behind": "integer",
      "modified_files": ["string[]"]
    },
    "active_sessions": ["string[] — other active session focuses (conflict detection)"]
  }
}
```

**Key design choice**: Context is returned as **structured fields**, not a pre-compiled blob. The Payload Compiler can select which fields to include at Position 3 based on dispatch tier (baseline gets `project_context` only; reliability gets everything). The Compiler owns assembly; the engine owns data.

**Side effects**: Creates `.hestai/state/sessions/active/{session_id}/session.json`.

---

### 2.2 `get_context` (NEW)

**Purpose**: Read-only context synthesis. Returns identical context data as `clock_in` but WITHOUT creating a session or any side effects. Enables:
- Payload Compiler preview ("what would an agent see?")
- CI pipeline context injection
- Lightweight reads without session overhead

```json
{
  "name": "get_context",
  "inputSchema": {
    "type": "object",
    "properties": {
      "working_dir": {
        "type": "string",
        "description": "Absolute path to project working directory"
      }
    },
    "required": ["working_dir"]
  }
}
```

**Returns**: Same `context` object as `clock_in`, minus `session_id` and session-specific fields.

```json
{
  "working_dir": "string",
  "context": {
    "product_north_star": "string | null",
    "project_context": "string | null",
    "phase_constraints": "object | null",
    "git_state": { "branch": "...", "ahead": 0, "behind": 0, "modified_files": [] },
    "active_sessions": ["string[]"]
  }
}
```

**Side effects**: NONE. Pure read.

---

### 2.3 `clock_out`

**Purpose**: Archive session transcript. Extract learnings. Redact credentials. Update learnings index. Clean up active session.

**Callers**: Workbench lifecycle manager (on session end) OR CLI agent (direct terminal use).

```json
{
  "name": "clock_out",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "Session ID from clock_in"
      },
      "working_dir": {
        "type": "string",
        "description": "Project working directory (recommended). Falls back to cwd search."
      },
      "description": {
        "type": "string",
        "description": "Optional session summary/description",
        "default": ""
      }
    },
    "required": ["session_id"]
  }
}
```

**Returns**:

```json
{
  "status": "string — 'success' | 'error'",
  "session_id": "string",
  "archive_path": "string | null — path to archived redacted transcript",
  "octave_path": "string | null — path to OCTAVE-compressed session",
  "message_count": "integer — number of messages parsed from transcript",
  "compression_status": "string — 'success' | 'failed' | 'skipped'",
  "extracted_learnings": {
    "decisions": ["string[] — DECISION_N keys extracted"],
    "blockers": ["string[] — BLOCKER_N keys extracted"],
    "learnings": ["string[] — LEARNING_N keys extracted"]
  }
}
```

**Side effects**:
- Reads Claude session JSONL transcript (via ClaudeJsonlLens)
- Redacts credentials (via RedactionEngine)
- Archives redacted JSONL to `.hestai/state/sessions/archive/`
- Compresses to OCTAVE format
- Appends to `learnings-index.jsonl`
- Removes active session directory

**Provider note**: Currently parses Claude JSONL format only. Future: abstract transcript parsing to support Codex/Gemini/Goose transcript formats via adapter pattern.

---

### 2.4 `submit_review`

**Purpose**: Post structured review verdict on a GitHub PR. Clear CI review-gate checks. Support dry-run validation.

**Callers**: Review agents (CRS, CE, TMG, etc.) during review workflows.

```json
{
  "name": "submit_review",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo": {
        "type": "string",
        "description": "Repository in owner/name format (e.g., 'elevanaltd/HestAI-MCP')"
      },
      "pr_number": {
        "type": "integer",
        "description": "PR number to comment on"
      },
      "role": {
        "type": "string",
        "enum": ["CE", "CIV", "CRS", "HO", "IL", "PE", "SR", "TMG"],
        "description": "Reviewer role"
      },
      "verdict": {
        "type": "string",
        "enum": ["APPROVED", "BLOCKED", "CONDITIONAL"],
        "description": "Review verdict"
      },
      "assessment": {
        "type": "string",
        "description": "Review assessment content"
      },
      "model_annotation": {
        "type": "string",
        "description": "Optional model name (e.g., 'Gemini') for annotation"
      },
      "commit_sha": {
        "type": "string",
        "description": "PR head SHA the reviewer verified. Pinned in metadata for audit trail."
      },
      "dry_run": {
        "type": "boolean",
        "description": "If true, validate format without posting",
        "default": false
      }
    },
    "required": ["repo", "pr_number", "role", "verdict", "assessment"]
  }
}
```

**Returns**:

```json
{
  "status": "string — 'success' | 'error'",
  "comment_url": "string | null — GitHub comment URL if posted",
  "validation": "string — format validation result",
  "dry_run": "boolean — whether this was a dry run"
}
```

**Side effects**: Posts formatted comment to GitHub PR (unless dry_run=true). Handles rate limiting, 403 responses, and mixed-case headers.

---

## 3. WHAT IS NOT IN THIS CONTRACT

These are explicitly excluded from `hestai-context-mcp`:

| Capability | Why Excluded | New Home |
|-----------|-------------|----------|
| Agent definition serving | Identity concern | Vault (git-backed library) |
| `.hestai-sys/` injection | Identity delivery | Workbench writes from Vault at spawn |
| Anchor ceremony (`bind`) | Identity verification | Alley-Oop pattern in Payload Compiler |
| Bundled hub management | Identity content | Vault |
| Governance integrity enforcement for `.hestai-sys/` | Identity protection | Vault git-backed immutability |
| `ensure_system_governance()` | Bootstrap identity | Vault bootstrap service |

---

## 4. TRANSPORT SPECIFICATION

**Protocol**: MCP JSON-RPC 2.0 over stdio (stdin/stdout)

**Spawn command (Workbench)**:
```
python -m hestai_context_mcp --working-dir /path/to/project
```

**Spawn command (CLI config, e.g. claude_desktop_config.json)**:
```json
{
  "mcpServers": {
    "hestai-context": {
      "command": "python",
      "args": ["-m", "hestai_context_mcp"],
      "env": {}
    }
  }
}
```

**Lifecycle**: Process starts when session begins, dies when session ends. Stateless between invocations — all state is on disk in `.hestai/state/`.

---

## 5. WORKBENCH INTEGRATION PATTERN

The Payload Compiler's Position 3 assembly:

```
Payload Compiler (Position 3 assembly):
  1. Call hestai-context-mcp.get_context(working_dir)
  2. Receive structured context object
  3. Select fields based on dispatch tier:
     - baseline: project_context only
     - reliability: product_north_star + project_context + phase_constraints + git_state
  4. Format selected fields into KVAEPH Position 3 OCTAVE block
  5. Continue to Position 4 (TASK)

Session lifecycle:
  1. Before dispatch: clock_in(role, working_dir, focus)
  2. Agent works...
  3. After session: clock_out(session_id, working_dir)
```

---

## 6. HARVEST PATH

Phase 1 creates `hestai-context-mcp` as a **new repo** by harvesting from `hestai-mcp`:

1. **Create**: New repo `elevanaltd/hestai-context-mcp` with clean Python project structure
2. **Harvest**: Copy System Steward code from hestai-mcp — `clock_in` (session/context logic only, not governance injection), `clock_out`, `ContextSteward`, `RedactionEngine`, `submit_review`, `pending_sessions`
3. **Build**: `get_context` tool as new code (extract read-only path from harvested `clock_in` logic)
4. **Refactor**: `clock_in` to return structured context object (see §2.1 return shape)
5. **TDD**: Write new tests for harvested code (red→green→refactor). Do NOT copy legacy tests — write tests that match the new interface contract.
6. **Package**: `hestai_context_mcp` with entry point `python -m hestai_context_mcp`

Legacy `hestai-mcp` stays **100% intact** — enabling A/B comparison of old system vs new until the new system is proven. Deprecation happens only after daily-use validation.

---

## 7. FEATURE-PARITY MATRIX (M3 Preview)

| Capability | Current hestai-mcp | hestai-context-mcp | Parity |
|-----------|-------------------|-------------------|--------|
| Session creation with focus resolution | clock_in | clock_in | 1:1 |
| Git branch focus inference | clock_in internals | clock_in internals | 1:1 |
| Focus conflict detection | pending_sessions | clock_in internals | 1:1 |
| Context file discovery | clock_in internals | clock_in + get_context | Enhanced |
| AI context synthesis | clock_in (optional) | clock_in (optional) | 1:1 |
| Product North Star serving | N/A (hook does this) | clock_in + get_context | NEW |
| ContextSteward phase constraints | clock_in internals | clock_in + get_context | 1:1 |
| Transcript parsing | clock_out | clock_out | 1:1 |
| Credential redaction | RedactionEngine | RedactionEngine | 1:1 |
| OCTAVE compression | clock_out | clock_out | 1:1 |
| Learnings indexing | clock_out | clock_out | 1:1 |
| Review submission | submit_review | submit_review | 1:1 |
| Dry-run review validation | submit_review | submit_review | 1:1 |
| Agent identity serving | bind | DELETED | Moved to Vault |
| `.hestai-sys/` injection | bootstrap | DELETED | Moved to Vault |
| Governance integrity | SHA-256/chmod | DELETED | Vault handles |
| Read-only context query | N/A | get_context | NEW |
