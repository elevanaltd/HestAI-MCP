---
component: clock_in
scope: tool
phase: D1
created: 2025-12-28
status: approved
approved_by: requirements-steward
approved_date: 2025-12-28
parent_north_star: .hestai/workflow/components/000-SYSTEM-STEWARD-NORTH-STAR.md
version: 1.2
---

# COMPONENT NORTH STAR: CLOCK_IN TOOL

**Component**: clock_in MCP Tool (Session Registration & Context Synthesis)
**Parent**: .hestai/workflow/components/000-SYSTEM-STEWARD-NORTH-STAR.md
**Status**: ACTIVE
**Version**: 1.2
**Date**: 2025-12-28
**Reviewed By**: requirements-steward

---

## COMMITMENT STATEMENT

This document establishes the immutable requirements for the **clock_in** MCP tool.
It inherits all requirements from:
- **System North Star** (I1 through I6) - Constitutional principles
- **HestAI-MCP Product North Star** (I1 through I6) - Product requirements
- **System Steward North Star** (SS-I1 through SS-I6) - Component requirements

The clock_in tool is the **front door** to the HestAI-MCP system. Every agent must call it
before doing any work. It registers the session, gathers relevant context, and provides
the agent with the information needed to begin working effectively.

---

## SECTION 1: THE UNCHANGEABLES (6 Immutables)

### CI-I1: SESSION REGISTRATION IS MANDATORY
**Requirement**: Every agent session must begin with clock_in. No MCP tool invocations or file modifications occur before clock_in returns session_id.
**Rationale**: Session tracking enables audit trails, conflict detection, and cognitive continuity (Product I1).
**Validation**: clock_in returns session_id. All subsequent tool calls reference this session_id.

### CI-I2: CONTEXT MUST BE FRESH
**Requirement**: clock_in generates fresh state data on every invocation. No stale cached context.
**Rationale**: Prevents hallucinations from outdated data (Product I4: Freshness Verification).
**Validation**: State vector includes generation timestamp. Pre-commit **blocks** if context >24h old without explicit acknowledgment. Agents cannot proceed with stale context.

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

**Context Selection Criteria**:
- Role affinity (what context does this role typically need?)
- Focus relevance (what relates to the stated focus/topic?)
- Recency (what changed recently that might affect this work?)
- ADR constraints (what decisions constrain this work?)

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

**Conflict Resolution Options**:
- **Continue**: Proceed despite conflict (agent accepts risk)
- **Abort**: Reject clock_in, do not create session
- **Take Over**: Mark existing session as STALE, create new session with ownership transfer logged in both session records

### CI-I6: TDD DISCIPLINE ENFORCEMENT
**Requirement**: All clock_in implementation must follow RED→GREEN→REFACTOR discipline. Test commits must precede feature commits.
**Rationale**: Inherited from System North Star I1 (Verifiable Behavioral Specification First).
**Validation**: Git history shows test-first evidence for all implementation phases. Pattern: `test: X` commit precedes `feat: X` commit.

---

## SECTION 2: CONSTRAINED VARIABLES

| Variable | Immutable Aspect | Flexible Aspect |
|----------|------------------|-----------------|
| **Context Sources** | Must gather comprehensive context (CI-I3) | Which tools used (Repomix, Dependency Cruiser, etc.) |
| **Focus Resolution** | Must resolve from somewhere | Priority order: explicit arg > GitHub issue > branch name > "general" |
| **AI Model** | Must use async (SS-I2) | Configurable via ~/.hestai/config/ai.yaml or .env |
| **AI Prompts** | Must be versioned and auditable (SS-I5) | Prompt text content |
| **Session Storage** | Must create session record | Format (JSON in active/, OCTAVE in archive/) |
| **FAST Layer Format** | Must be OCTAVE (ADR-0046) | Schema evolution within OCTAVE constraints |

**Focus Resolution - "Descriptive Branch" Definition**:
A branch is considered "descriptive" if it contains:
- Issue number pattern: `#XX` or `issue-XX`
- Feature keyword prefix: `feat/`, `fix/`, `chore/`, `refactor/`, `docs/`

---

## SECTION 2B: SCOPE BOUNDARIES

### What This Tool IS

| Scope | Description |
|-------|-------------|
| ✅ Session Registration | Create and track agent sessions with unique IDs |
| ✅ FAST Layer Lifecycle | Update current-focus, checklist, blockers on session start |
| ✅ AI-Assisted Context Selection | Use AI to curate relevant context for role+focus |
| ✅ Focus Conflict Detection | Detect and report when multiple sessions in same worktree |
| ✅ GitHub Issue Enrichment | Search and include relevant issues based on focus |

### What This Tool IS NOT

| Out of Scope | Responsible Component |
|--------------|----------------------|
| ❌ Session Archival | clock_out tool |
| ❌ Identity Validation | odyssean_anchor tool |
| ❌ Context File Writing | octave_create via OCTAVE MCP |
| ❌ Governance Enforcement | System Steward persona |
| ❌ Context Updates Mid-Session | context_update tool |
| ❌ Document Routing | document_submit tool |

---

## SECTION 3: ASSUMPTION REGISTER

| ID | Assumption | Confidence | Impact | Validation Plan | Owner | Timing |
|----|------------|------------|--------|-----------------|-------|--------|
| CI-A1 | AI can synthesize useful FAST context from codebase + focus | 80% | High | POC with real sessions | implementation-lead | Before B1 |
| CI-A2 | GitHub issue search provides relevant context for focus | 85% | Medium | Test with Issue #56 as focus | implementation-lead | During B1 |
| CI-A3 | 30-day archive + 72-hour stale session cleanup is sufficient | 90% | Low | Monitor disk usage over time | implementation-lead | During B2 |
| CI-A4 | Workspace config (.hestai_workspace.yaml) covers customization needs | 75% | Medium | Gather user feedback | implementation-lead | During B2 |
| CI-A5 | Focus conflict detection prevents session collisions | 95% | High | Unit test with concurrent sessions | implementation-lead | Before B1 |
| CI-A6 | System Steward async infrastructure (SS-I2, SS-I3) will be ready | 70% | Critical | Track parallel session progress | technical-architect | Before B1 |

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
    - ELSE IF GitHub issue in branch name (#XX or issue-XX): extract issue context
    - ELSE IF branch has feature prefix (feat/, fix/, etc.): infer from branch
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
    - Load versioned synthesis prompt from ~/.hestai/prompts/clock_in_synthesis.txt
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
- **System North Star** (I1 through I6)
- **Product North Star** (I1 through I6)
- **System Steward North Star** (SS-I1 through SS-I6)

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
| Session inactive >72 hours | Mark as STALE, block on next clock_in until resolved |
| Stale session on clock_in | Offer to clean up or continue (agent decides) |
| Archive older than 30 days | Delete from archive |

**Human Authority**: Cleanup thresholds (72h stale, 30-day archive) are configurable by the human user via `.hestai_workspace.yaml`. Agents may recommend but not autonomously change these thresholds.

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
| Stale context (>24h) | Block with staleness error | Run clock_in to refresh |

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
| 2025-12-28 | Add CI-I6 TDD Discipline | requirements-steward review: align with System I1 |
| 2025-12-28 | Staleness blocks not warns | requirements-steward review: align with System I5 |
| 2025-12-28 | Complete inheritance chain | requirements-steward review: explicit System NS reference |

---

## COMMITMENT CEREMONY

**Status**: ACTIVE
**Reviewer**: requirements-steward
**Review Date**: 2025-12-28

**The Oath**:
> "These 6 Immutables (CI-I1 through CI-I6) are the binding requirements for clock_in implementation. Any contradiction requires STOP, CITE, ESCALATE."

**Amendments Applied**:
1. Added CI-I6 (TDD Discipline Enforcement)
2. Changed CI-I2 validation from "warns" to "blocks"
3. Completed inheritance chain (System + Product + System Steward)
4. Added versioned prompt reference (STEP_6)
5. Clarified "take over" semantics (CI-I5)
6. Added Human Authority clause (Section 7)
7. Defined "descriptive branch" criteria (Section 2)
8. Added context selection criteria (CI-I3)

---

## EVIDENCE SUMMARY

### Constitutional Compliance
- **Total Immutables**: 6 (✓ within 5-9 range)
- **System-Agnostic**: 6/6 passed Technology Change Test (no technology-specific language)
- **Assumptions Tracked**: 6 (✓ 6+ required per PROPHETIC_VIGILANCE)
- **Critical Assumptions**: 3 requiring pre-B1 validation (CI-A1, CI-A5, CI-A6)
- **Commitment Ceremony**: ✓ Completed 2025-12-28

### Quality Gates
- **YAML Front-Matter**: ✓ Present
- **Inheritance Chain**: ✓ Documented (System NS + Product NS + System Steward NS)
- **Miller's Law**: ✓ 6 immutables (within 5-9 range)
- **PROPHETIC_VIGILANCE**: ✓ 6 assumptions with validation plans
- **Scope Boundaries**: ✓ IS/IS NOT documented
- **Evidence Trail**: ✓ requirements-steward review documented

### Readiness Status
- **D1 Gate**: ✓ Ready for implementation
- **Blocking Dependencies**: SS-I2 (async AIClient), SS-I3 (MCP client manager)

---

**Protection Clause**: Any work contradicting these immutables must STOP, CITE the specific requirement, and ESCALATE to requirements-steward.
