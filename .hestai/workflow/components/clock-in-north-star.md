# COMPONENT NORTH STAR: CLOCK_IN TOOL

**Component**: clock_in MCP Tool (Session Registration & Context Synthesis)
**Parent**: .hestai/workflow/components/000-SYSTEM-STEWARD-NORTH-STAR.md
**Status**: DRAFT
**Version**: 1.0
**Date**: 2025-12-28

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **clock_in** MCP tool.
It inherits all requirements from the **System Steward North Star** (SS-I1 through SS-I6)
and the **HestAI-MCP Product North Star** (I1 through I6).

The clock_in tool is the **front door** to the HestAI-MCP system. Every agent must call it
before doing any work. It registers the session, gathers relevant context, and provides
the agent with the information needed to begin working effectively.

---

## SECTION 1: THE UNCHANGEABLES (5 Immutables)

### CI-I1: SESSION REGISTRATION IS MANDATORY
**Requirement**: Every agent session must begin with clock_in. No work occurs before session registration.
**Rationale**: Session tracking enables audit trails, conflict detection, and cognitive continuity (Product I1).
**Validation**: clock_in returns session_id. All subsequent tool calls reference this session_id.

### CI-I2: CONTEXT MUST BE FRESH
**Requirement**: clock_in generates fresh state data on every invocation. No stale cached context.
**Rationale**: Prevents hallucinations from outdated data (Product I4: Freshness Verification).
**Validation**: State vector includes generation timestamp. Pre-commit warns if context >24h old.

| Context Type | Generation Method | Staleness Threshold |
|--------------|-------------------|---------------------|
| Git state | `git log`, `git status` | Real-time on clock_in |
| Quality gates | Run typecheck/lint/test commands | Real-time on clock_in |
| FAST layer | AI synthesis from codebase | Generated fresh each session |
| Human-authored | Read from .hestai/context/ | Preserved, not regenerated |

### CI-I3: AI-ASSISTED CONTEXT SELECTION
**Requirement**: clock_in uses AI to select and synthesize relevant context based on role and focus.
**Rationale**: Agents need role-appropriate context, not everything (Issue #87: System Architecture Blindness).
**Validation**: AIClient.complete_text() called with role+focus+codebase summary. Deterministic fallback if AI fails (SS-I6).

**Context Selection Sources** (flexible, not fixed to specific tools):
- Codebase structure analysis (currently Repomix, may change)
- GitHub issues matching focus query
- Existing .hestai/context/ files
- Recent git activity
- ADR constraints and decisions

### CI-I4: FAST LAYER LIFECYCLE
**Requirement**: clock_in updates the FAST layer files in `.hestai/context/state/` with session-specific context.
**Rationale**: Agents need to see current focus, active blockers, and task checklist (ADR-0056).
**Validation**: After clock_in, FAST layer files reflect session state.

| FAST Layer File | Updated On clock_in |
|-----------------|---------------------|
| `current-focus.oct.md` | Session ID, role, focus, branch, timestamp |
| `checklist.oct.md` | Session task, carry forward incomplete from previous |
| `blockers.oct.md` | Preserve unresolved, add session context |

### CI-I5: FOCUS CONFLICT DETECTION
**Requirement**: clock_in detects if another session is already active in the same worktree with conflicting focus.
**Rationale**: Prevents concurrent agents from overwriting each other's context.
**Validation**: Returns conflict info with existing session details. Agent decides to continue, abort, or take over.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **Context Sources** | Must gather comprehensive context (CI-I3) | Which tools used (Repomix, Dependency Cruiser, etc.) |
| **Focus Resolution** | Must resolve from somewhere | Priority order: explicit arg > GitHub issue > branch name > "general" |
| **AI Model** | Must use async (SS-I2) | Configurable via ~/.hestai/config/ai.json |
| **Session Storage** | Must create session record | Format (JSON in active/, OCTAVE in archive/) |
| **FAST Layer Format** | Must be OCTAVE (ADR-0046) | Schema evolution within OCTAVE constraints |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Confidence | Validation Plan |
|----|------------|------------|-----------------|
| CI-A1 | AI can synthesize useful FAST context from codebase + focus | 80% | POC with real sessions |
| CI-A2 | GitHub issue search provides relevant context for focus | 85% | Test with Issue #56 as focus |
| CI-A3 | 30-day archive + 72-hour stale session cleanup is sufficient | 90% | Monitor disk usage over time |
| CI-A4 | Workspace config (.hestai_workspace.yaml) covers customization needs | 75% | Gather user feedback |
| CI-A5 | Focus conflict detection prevents session collisions | 95% | Unit test with concurrent sessions |

---

## SECTION 4: INPUT/OUTPUT CONTRACT

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `role` | string | Yes | Agent role (e.g., "holistic-orchestrator", "implementation-lead") |
| `focus` | string | No | Work focus/topic (e.g., "implement odyssean_anchor"). Defaults to "general" |
| `working_dir` | string | Yes | Absolute path to project root |
| `model` | string | No | AI model override. Default from config |

### Output Structure

```json
{
  "session_id": "uuid-v4",
  "context_paths": {
    "project_context": ".hestai/context/PROJECT-CONTEXT.oct.md",
    "current_state": ".hestai/context/state/current-state.oct.md",
    "checklist": ".hestai/context/state/checklist.oct.md",
    "blockers": ".hestai/context/state/blockers.oct.md",
    "current_focus": ".hestai/context/state/current-focus.oct.md",
    "negatives": ".hestai/context/CONTEXT-NEGATIVES.oct.md"
  },
  "conflict": null | {
    "existing_session_id": "...",
    "existing_role": "...",
    "existing_focus": "...",
    "started_at": "ISO8601"
  },
  "focus_resolved": {
    "value": "implement odyssean_anchor",
    "source": "explicit" | "github_issue" | "branch" | "default"
  },
  "github_context": {
    "related_issues": [...],
    "active_pr": {...} | null
  },
  "instruction": "Read context_paths. Produce Full RAPH. Submit anchor."
}
```

---

## SECTION 5: EXECUTION SEQUENCE

```
CLOCK_IN_SEQUENCE:

  STEP_1: VALIDATE_INPUT
    - Validate role format (alphanumeric + hyphens)
    - Validate working_dir exists and is absolute
    - Prevent path traversal attacks
    - OUTPUT: validated_params

  STEP_2: DETECT_FOCUS_CONFLICT
    - Check .hestai/sessions/active/ for existing sessions
    - If conflict: return conflict info in response
    - OUTPUT: conflict_status

  STEP_3: CREATE_SESSION
    - Generate session_id (UUID v4)
    - Create .hestai/sessions/active/{session_id}/
    - Write session.json with metadata
    - OUTPUT: session_id, session_dir

  STEP_4: RESOLVE_FOCUS
    - IF explicit focus provided: use it
    - ELSE IF GitHub issue in branch name: extract issue context
    - ELSE IF branch name is descriptive: infer from branch
    - ELSE: default to "general"
    - OUTPUT: resolved_focus

  STEP_5: GATHER_CONTEXT [AI-ASSISTED]
    - Query codebase structure (via configured tool)
    - Search GitHub issues matching focus
    - Read recent git activity (log, status, diff)
    - Check quality gate status (if quick to run)
    - Extract relevant ADR constraints
    - FALLBACK: If AI fails, use deterministic file list
    - OUTPUT: gathered_context

  STEP_6: SYNTHESIZE_FAST_LAYER [AI-ASSISTED]
    - Call AIClient.complete_text() with:
      - Role
      - Focus
      - Gathered context summary
      - FAST layer template
    - Generate current-focus.oct.md content
    - Generate checklist.oct.md content
    - Update blockers.oct.md content
    - FALLBACK: Use template with minimal data if AI fails
    - OUTPUT: fast_layer_content

  STEP_7: WRITE_FAST_LAYER
    - Validate via octave_ingest (SS-I1)
    - Write via octave_create to .hestai/context/state/
    - OUTPUT: written_files

  STEP_8: RESOLVE_CONTEXT_PATHS
    - Build map of all context files agent should read
    - Include human-authored (PROJECT-CONTEXT.oct.md)
    - Include generated (current-state.oct.md)
    - Include FAST layer (checklist, blockers, current-focus)
    - OUTPUT: context_paths

  STEP_9: RETURN_RESPONSE
    - Assemble response object
    - Include session_id, context_paths, conflict, focus_resolved
    - Include github_context if available
    - OUTPUT: ClockInResponse
```

---

## SECTION 6: INTEGRATION POINTS

### Inherits From
- **System Steward North Star** (SS-I1 through SS-I6)
- **Product North Star** (I1 through I6)

### Dependencies
| Dependency | Purpose | Fallback |
|------------|---------|----------|
| AIClient (async) | Context synthesis, FAST layer generation | Deterministic template |
| OCTAVE MCP | Validate and write FAST layer files | Local validation |
| GitHub CLI (gh) | Issue search for focus context | Skip GitHub enrichment |
| Repomix or equivalent | Codebase structure analysis | Basic file listing |
| Git | State queries (log, status, diff) | None (required) |

### Downstream Consumers
- **Odyssean Anchor**: Uses session_id from clock_in response
- **clock_out**: Closes the session registered by clock_in
- **All agents**: Read context_paths returned by clock_in

### Position in Binding Ceremony
clock_in is **Step 2 of 5** in the Odyssean Anchor binding:

```
1. READ_PROMPT     - Agent loads constitution file
2. CLOCK_IN        - [THIS TOOL] Session registered, context paths returned
3. READ_CONTEXT    - Agent reads git state + project context
4. ODYSSEAN_ANCHOR - Agent submits identity proof for validation
5. DASHBOARD       - Agent shows validated binding
```

---

## SECTION 7: SESSION LIFECYCLE

### Session States
```
CREATED     - clock_in called, session.json written
ACTIVE      - Agent working, may update FAST layer
COMPLETED   - clock_out called, archived to OCTAVE
STALE       - No activity for 72 hours, eligible for cleanup
ARCHIVED    - In .hestai/sessions/archive/, retained 30 days
```

### Cleanup Policy
| Condition | Action |
|-----------|--------|
| Session inactive >72 hours | Mark as STALE, warn on next clock_in |
| Stale session on clock_in | Offer to clean up or continue |
| Archive older than 30 days | Delete from archive |

### Workspace Configuration
Support optional `.hestai_workspace.yaml` for customization:

```yaml
# .hestai_workspace.yaml
context_paths:
  additional:
    - docs/architecture/
    - .github/workflows/
  exclude:
    - node_modules/
    - .git/

github:
  issue_search: true
  pr_context: true

ai:
  model_override: "anthropic/claude-3.5-sonnet"

cleanup:
  stale_session_hours: 72
  archive_retention_days: 30
```

---

## SECTION 8: ERROR HANDLING

| Error Condition | Response | Recovery |
|-----------------|----------|----------|
| Invalid role format | Reject with validation error | Agent fixes input |
| Invalid working_dir | Reject with path error | Agent provides valid path |
| Path traversal attempt | Block and log security event | None (security violation) |
| AI provider timeout | Use deterministic fallback (SS-I6) | Degraded but functional |
| OCTAVE validation fails | Retry with simpler content | Log for debugging |
| GitHub API rate limit | Skip GitHub enrichment | Proceed without issues |
| Disk full | Reject with storage error | User clears space |

---

## SECTION 9: RELATED ISSUES AND ADRs

### GitHub Issues
| Issue | Relationship |
|-------|--------------|
| #56 | FAST layer lifecycle integration (direct implementation) |
| #87 | System Architecture Blindness (context gathering strategy) |
| #96 | State Vector return enhancement (COMPLETED) |
| #102 | Odyssean anchor (uses clock_in session_id) |
| #35 | Living Artifacts Auto-Refresh (freshness guarantee) |
| #36 | Odyssean Anchor Binding ADR (binding ceremony context) |

### ADRs
| ADR | Relationship |
|-----|--------------|
| ADR-0033 | Dual-Layer Context Architecture (directory structure) |
| ADR-0035 | Living Artifacts Auto-Refresh (freshness mechanism) |
| ADR-0036 | Odyssean Anchor Binding (Step 2 of ceremony) |
| ADR-0046 | Velocity-Layered Fragments (FAST layer structure) |
| ADR-0056 | FAST Layer Lifecycle (clock_in updates) |

---

## SECTION 10: IMPLEMENTATION PHASES

### Phase 1 (MVP)
- [ ] Session creation with UUID
- [ ] Focus conflict detection
- [ ] Context path resolution
- [ ] Basic FAST layer update (template-based)
- [ ] GitHub issue search for focus
- [ ] Deterministic fallback for all AI operations

### Phase 2 (AI Enhancement)
- [ ] AI-powered context selection
- [ ] AI-powered FAST layer synthesis
- [ ] Repomix integration for codebase analysis
- [ ] Workspace configuration support

### Phase 3 (Advanced)
- [ ] Session cleanup automation
- [ ] Quality gate status inclusion
- [ ] ADR constraint extraction
- [ ] Dependency graph awareness (Orchestra Map)

---

## DECISION LOG

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-28 | AI required for context selection | Issue #87 shows agents need curated context |
| 2025-12-28 | Focus resolution priority order | Explicit > GitHub > branch > default |
| 2025-12-28 | 30-day archive + 72-hour stale | Balance between history and disk usage |
| 2025-12-28 | Workspace config support | Enables project-specific customization |
| 2025-12-28 | GitHub issue search for focus | Direct user request for issue context |

---

**Protection Clause**: Any work contradicting these immutables must STOP, CITE the specific requirement, and ESCALATE to requirements-steward.
