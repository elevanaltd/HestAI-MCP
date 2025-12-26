# ADR-0056: FAST Layer Lifecycle Integration

**Status**: PROPOSED
**Date**: 2025-12-25
**Author**: holistic-orchestrator (HO)
**GitHub Issue**: [#56](https://github.com/elevanaltd/HestAI-MCP/issues/56)
**Depends On**: ADR-0046 (Velocity-Layered Fragments)

---

## Context

ADR-0046 established the Velocity-Layered Fragments architecture with a FAST layer at `.hestai/context/state/` containing:
- `checklist.oct.md` - Current tasks (hourly-daily updates)
- `blockers.oct.md` - Active blockers
- `current-focus.oct.md` - Session focus

**Problem**: These files are currently **static**. They were created with initial content but have no mechanism to:
1. Populate with session-specific context during `clock_in`
2. Update with session results during `clock_out`
3. Receive topic/focus from load commands (`/load3`, `/oa-prototype-load`)

### Multi-Worktree Reality

```
/Volumes/HestAI-MCP/                    → main branch
/Volumes/HestAI-MCP/worktrees/
  ├── adr-0046/                         → .hestai/context/state/ for ADR-0046 work
  ├── feature-auth/                     → .hestai/context/state/ for auth feature
  └── bugfix-123/                       → .hestai/context/state/ for bug fix
```

Each worktree's FAST layer should reflect **that worktree's current session**, not static boilerplate.

## Decision

Integrate FAST layer lifecycle management into the `clock_in` and `clock_out` MCP tools.

### 1. Clock_in FAST Layer Updates

When `clock_in(role, focus, working_dir)` is called:

```python
def clock_in(role: str, focus: str, working_dir: str) -> ClockInResponse:
    # ... existing session creation ...

    # NEW: Update FAST layer
    state_dir = Path(working_dir) / ".hestai/context/state"

    if state_dir.exists():
        update_current_focus(state_dir, {
            "session_id": session_id,
            "role": role,
            "focus": focus,
            "branch": get_current_branch(),
            "started_at": datetime.utcnow().isoformat()
        })

        update_checklist(state_dir, {
            "session_task": focus,
            "carry_forward": get_incomplete_tasks(state_dir)
        })

        # Blockers: preserve existing, add session context
        update_blockers(state_dir, {
            "session_id": session_id,
            "carry_forward": True  # Don't clear unresolved blockers
        })
```

### 2. Clock_out FAST Layer Updates

When `clock_out(session_id)` is called:

```python
def clock_out(session_id: str) -> ClockOutResponse:
    # ... existing session archival ...

    # NEW: Update FAST layer
    state_dir = get_state_dir_for_session(session_id)

    if state_dir.exists():
        clear_current_focus(state_dir, {
            "completed_at": datetime.utcnow().isoformat(),
            "session_id": session_id
        })

        update_checklist(state_dir, {
            "mark_session_complete": True,
            "preserve_incomplete": True
        })

        # Blockers: persist unresolved, clear resolved
        persist_blockers(state_dir, {
            "clear_resolved": True,
            "keep_unresolved": True
        })
```

### 3. Load Command Integration

Update `/load3` protocol to pass topic to clock_in:

```octave
// Current
/load3 {role}
  → clock_in(role:"ho", focus:"general", working_dir:"{cwd}")

// Proposed
/load3 {role} [topic]
  → clock_in(role:"ho", focus:"{topic|branch_inferred}", working_dir:"{cwd}")
```

**Topic Resolution Priority**:
1. Explicit argument: `/load3 ho "implement ADR-0047"`
2. GitHub issue: `/load3 ho --issue 56`
3. Branch inference: `adr-0047` → "ADR-0047 work"
4. Default: "general"

### 4. FAST Layer File Formats

#### current-focus.oct.md (Session Active)
```octave
===CURRENT_FOCUS===
META:
  TYPE::SESSION_FOCUS
  VELOCITY::HOURLY_DAILY

SESSION:
  ID::"abc123"
  ROLE::holistic-orchestrator
  FOCUS::"Implement FAST layer lifecycle"
  BRANCH::adr-0047
  STARTED::"2025-12-25T10:30:00Z"

CONTEXT:
  GITHUB_ISSUE::#56
  RELATED_ADR::ADR-0047

===END===
```

#### current-focus.oct.md (Session Ended)
```octave
===CURRENT_FOCUS===
META:
  TYPE::SESSION_FOCUS
  VELOCITY::HOURLY_DAILY

SESSION::NONE
LAST_SESSION:
  ID::"abc123"
  COMPLETED::"2025-12-25T12:45:00Z"
  OUTCOME::merged_pr_52

===END===
```

#### checklist.oct.md (Session Managed)
```octave
===SESSION_CHECKLIST===
META:
  TYPE::FAST_CHECKLIST
  VELOCITY::HOURLY_DAILY
  SESSION::"abc123"

CURRENT_TASK::"Implement FAST layer lifecycle"

ITEMS:
  implement_clock_in_updates::IN_PROGRESS
  implement_clock_out_updates::PENDING
  update_load3_protocol::PENDING
  write_tests::PENDING

CARRIED_FORWARD:
  fix_ruff_errors::PENDING[from_previous_session]

===END===
```

### 5. Multi-Agent Conflict Resolution

**Strategy**: Last-writer-wins with audit trail

```octave
CONFLICT_HANDLING::[
  DETECTION::file_mtime_check_before_write,
  RESOLUTION::last_writer_wins,
  AUDIT::previous_content_preserved_in_session_archive,
  WARNING::log_concurrent_session_detected
]
```

**Rationale**: FAST layer is ephemeral by design. True conflicts are rare (same worktree, same time). The session archive preserves history for forensics.

## Consequences

### Positive

1. **Dynamic Context**: FAST layer reflects actual session state
2. **Topic Continuity**: Focus carries from load command → clock_in → FAST files
3. **Blocker Persistence**: Unresolved blockers survive sessions
4. **Multi-Worktree Isolation**: Each worktree has independent FAST state

### Negative

1. **MCP Tool Complexity**: clock_in/clock_out gain file I/O responsibility
2. **State Coupling**: FAST layer tied to session lifecycle
3. **Migration**: Existing static FAST files need transition handling

### Neutral

1. **OCTAVE Format**: Maintained for consistency
2. **Git Tracking**: FAST files remain committed (not gitignored)

## Implementation Plan

| Phase | Task | Owner |
|-------|------|-------|
| 1 | Update clock_in to write FAST layer | implementation-lead |
| 2 | Update clock_out to update FAST layer | implementation-lead |
| 3 | Update /load3 to accept topic parameter | system-steward |
| 4 | Add tests for FAST layer lifecycle | universal-test-engineer |
| 5 | Update PROJECT-CONTEXT with ADR-0047 | system-steward |

## Rejected Alternatives

### Agent-Namespaced State Directories
```
.hestai/context/state/{session-id}/
```
- **Rejected**: Creates directory sprawl, complicates @tag references, violates ADR-0046 structure

### Gitignored FAST Layer
```
.gitignore: .hestai/context/state/
```
- **Rejected**: Loses git visibility benefit from ADR-0046, breaks agent @tag capability

### Event-Sourced State
```
.hestai/context/state/events.jsonl → projection
```
- **Rejected**: Over-engineering for FAST layer purpose (already rejected in ADR-0046)

## References

- ADR-0046: Velocity-Layered Fragments Architecture
- ADR-0033: Dual-Layer Context Architecture
- GitHub Issue #56: FAST layer lifecycle integration
