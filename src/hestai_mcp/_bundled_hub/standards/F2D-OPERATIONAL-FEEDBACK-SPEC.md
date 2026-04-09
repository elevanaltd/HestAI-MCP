---
type: SPECIFICATION
id: f2d-operational-feedback
version: "1.0"
status: PROPOSED
purpose: Post-session operational feedback architecture for governance machinery quality
created: 2026-04-07
origin: HO orchestration — Wind/Wall/Door debate + technical-architect + requirements-steward + ho-liaison consultations
builds-on:
  - "RCCAFP-ERROR-RECOVERY-SPEC.md (tool pattern, JSONL append, server envelope)"
  - "HESTAI-ECOSYSTEM-LIGHTHOUSE.md v4.0 (four-system architecture, separation of concerns)"
delivery: "Bundled hub -> .hestai-sys/standards/ (cross-repo, all agents)"
---

# F2D Operational Feedback Architecture

**Version:** 1.0
**Status:** PROPOSED

---

## WHAT THIS DOCUMENT IS

Cross-repo specification for post-session operational feedback in the HestAI agent ecosystem. Defines the `submit_friction_record` tool schema, the universal storage model, and the Friction-to-Debate (F2D) lifecycle.

This is the **single source of truth** for operational feedback architecture. Implementing agents in any repo should reference this spec.

**What this is NOT:**
- NOT feedback on what the agent built or implemented
- NOT a retrospective on task outcomes or code quality
- NOT a replacement for RCCAFP (error recovery during build failures)

**What this IS:**
- Feedback on how well the **system's governance machinery** served the agent
- Observations about anchor ceremony friction, instruction clarity, review command effectiveness, file placement rules, governance gaps, and assumptions the agent had to make
- A structured signal for continuous improvement of the governance system itself

**Relationship to other documents:**
- **RCCAFP Error Recovery Spec:** RCCAFP captures build failures mid-session (hot-path). F2D captures governance friction post-session (cold-path). These are **complementary, not competing.** Shared JSONL infrastructure, divergent workflows. When an RCCAFP resolution required a governance workaround, the agent should also submit a friction record noting the governance gap.
- **Ecosystem Lighthouse v4.0:** F2D respects the four-system separation of concerns (ADR-0353). Capture lives in hestai-context-mcp (context stewardship), triage routes through Debate Hall (deliberation), resolution produces PRs to the governance source (Vault or hestai-context-mcp as appropriate).
- **Product North Star:** Directly satisfies I1 (Persistent Cognitive Continuity) by persisting operational learnings across sessions. Respects I3 (Dual-Layer Authority) by keeping friction records as mutable context until ratified through governance process.

---

## 1. THE PROBLEM

Agents operate within a governance system (anchor ceremonies, skills, patterns, instructions, review commands, file placement rules) that is designed by humans and other agents. When this governance machinery works well, the agent operates smoothly. When it doesn't — unclear instructions, missing guidance, confusing file placement, friction in the anchor process — the agent either:

1. **Silently works around the issue** — governance improvement signal is lost
2. **Guesses** — may introduce subtle misalignment that compounds across sessions
3. **Fails** — escalates to RCCAFP, but the governance root cause is not captured separately

There is currently no mechanism for agents to report back on governance quality. The system has no way to learn whether its own machinery is serving agents well.

---

## 2. THE ARCHITECTURE

### 2.1 Design Principles

1. **Governance introspection, not task retrospective.** F2D captures how well the system served the agent, not what the agent accomplished.
2. **Universal storage.** Governance friction is system-wide, not project-specific. An unclear anchor instruction is unclear regardless of which repo the agent is working in.
3. **Capture is cheap.** The agent is at session end. Friction capture must be fast, lightweight, and independent of other session-end operations.
4. **Evidence is mandatory.** Without evidence (file paths, log references, quoted instructions), friction records are noise. The schema enforces this.
5. **Mutable until ratified.** Friction records are mutable context (I3). They become governance changes only through explicit triage and ratified PRs.

### 2.2 submit_friction_record Tool — Governance Feedback Boundary

`submit_friction_record` is an MCP tool in the **Governance Engine (hestai-context-mcp)**. It captures structured operational feedback about governance machinery quality.

**Locked Tool Schema:**

| Field | Type | Required | Purpose |
|---|---|---|---|
| `working_dir` | String | Yes | Project root path for session context. Canonicalized and validated. Used for session detection, NOT for storage (storage is universal). |
| `target_machinery` | String | Yes | Which governance subsystem generated friction. Suggested vocabulary: `anchor`, `instruction`, `review`, `skill`, `pattern`, `file_placement`, `governance_gap`, `guessed_assumption`. Free text at B1; hardened to enum at B2 when friction corpus exists. |
| `severity` | Integer (0-3) | Yes | `0` = minor (noticed but irrelevant), `1` = recovered (found workaround quickly), `2` = workaround (significant effort to work around), `3` = deadlock (could not proceed without human intervention or guessing) |
| `evidence` | String | Yes | **MANDATORY.** Filepath, log reference, quoted instruction, or specific step that generated friction. Without evidence, the record is noise. |
| `friction_narrative` | String | Yes | Expected behavior vs actual behavior. What should the governance have told me? What did it actually tell me (or fail to tell me)? |
| `resolution` | String | No | How the agent resolved the friction. Required if severity <= 1. This is the most valuable field — it shows what the agent inferred that the governance should have stated explicitly. |

**Logging:** All submissions are appended to `~/.hestai/friction/{YYYY-MM-DD}-{session-id-short}.friction.jsonl`. One file per session enables per-session correlation and cleanup.

**Record envelope:** Each JSON line is a self-contained record with server-generated metadata:

```json
{
  "record_id": "friction-{uuid4}",
  "timestamp": "ISO-8601",
  "session_id": "from active session",
  "agent_role": "from active permit",
  "working_dir": "/path/to/project",
  "target_machinery": "anchor",
  "severity": 2,
  "evidence": ".hestai-sys/library/agents/implementation-lead.oct.md:§3 — CAPABILITIES section does not specify which skills load for build_failure_recovery profile",
  "friction_narrative": "Expected: CAPABILITIES section lists skills for each profile including build_failure_recovery. Actual: Only STANDARD and REVIEW profiles are defined. Had to guess that error-triage skill should load.",
  "resolution": "Loaded error-triage skill based on RCCAFP spec reference. Worked but was not governed."
}
```

**Path validation:** The implementation must canonicalize `working_dir` for session detection but writes to `~/.hestai/friction/` regardless of working_dir value.

**Append safety:** Same as RCCAFP — use `O_APPEND` mode for writes. If friction narratives exceed PIPE_BUF (4096 bytes), use file locking (`fcntl.flock`) as fallback. Implementation should enforce a reasonable size bound (~8KB per record).

**Universal storage rationale:** Unlike RCCAFP's `{working_dir}/.hestai/state/error-metrics.jsonl` (project-specific build errors), friction records are system-wide. An anchor ceremony issue in repo A is the same issue in repo B. Per-project storage fragments the signal and prevents pattern detection across repos (I6 Universal Scope).

### 2.3 F2D Lifecycle (Friction-to-Debate)

The full lifecycle spans three phases and three services:

```text
B1 CAPTURE (Governance Engine — this spec)
  Agent calls submit_friction_record at session end
  JSONL record appended to ~/.hestai/friction/
  Tool returns record_id for reference

B2 TRIAGE (Debate Hall — future spec)
  Periodic review of friction records with severity >= 2
  Human or designated specialist reviews queue
  Actionable items promoted to Debate Hall as structured topics
  Non-actionable items annotated and archived

B3 RESOLVE (governance source — future spec)
  Debate produces synthesis with governance improvement recommendation
  Ratified improvement becomes PR to governance source (Vault for identity artifacts, hestai-context-mcp for context artifacts)
  Governance amendment follows standard review chain
  Friction record linked to resolution for audit trail
```

**Phase boundaries are strict:**
- B1 builds ONLY the capture tool and storage. No automation, no triage logic.
- B2 builds the triage workflow with explicit ownership and promotion criteria.
- B3 builds the resolution pipeline connecting debate outputs to governance PRs.

### 2.4 Relationship to clock_out

Friction capture is a **separate tool called before clock_out**, not embedded within it.

**Rationale:**
1. **Independence.** clock_out is currently broken (PROJECT-CONTEXT §2). Friction capture must work regardless. A separate tool ensures friction records survive clock_out failures.
2. **Single responsibility.** clock_out archives transcripts. submit_friction_record captures governance observations. Different concerns, different tools.
3. **Optional.** Not every session has friction to report. The agent skips the call if nothing was observed.

**Operational sequence at session end:**

```text
1. Agent calls submit_friction_record (if friction was observed)
2. Agent calls clock_out (session archival)
```

### 2.5 Relationship to RCCAFP

| | RCCAFP (submit_rccafp_record) | F2D (submit_friction_record) |
|---|---|---|
| **When** | Mid-session, after build failure | End of session, reflective |
| **What** | Build error diagnosis and recovery | Governance machinery quality |
| **Storage** | Per-project: `{working_dir}/.hestai/state/error-metrics.jsonl` | Universal: `~/.hestai/friction/` |
| **Why per-project vs universal** | Build errors are project-specific | Governance friction is system-wide |
| **Urgency** | Immediate — agent is stuck | Deferred — queue for review |
| **Consumer** | Dispatch layer (escalation) | Triage queue (governance improvement) |
| **Format** | JSONL | JSONL |
| **Shared** | Server envelope pattern, O_APPEND writes, evidence requirement | Same |

**Cross-reference:** When an RCCAFP resolution required a governance workaround (e.g., the agent had to guess at a missing instruction to fix the build), the agent should also submit a friction record. The RCCAFP record captures the build fix. The friction record captures the governance gap that made the fix harder than necessary.

---

## 3. BUILD SEQUENCE

### 3A. Governance Engine (hestai-context-mcp) — B1

Implement `submit_friction_record` as an MCP tool alongside existing `submit_rccafp_record`:
- Accept `working_dir` for session detection (same pattern as existing tools)
- Validate schema (all required fields present, types correct, evidence non-empty)
- Resolve `~/.hestai/friction/` storage path (create if needed)
- Generate filename: `{YYYY-MM-DD}-{session-id-short}.friction.jsonl` (fallback to `{YYYY-MM-DD}-{uuid4-short}.friction.jsonl` if no active session)
- Append JSONL record with server-generated envelope (§2.2)
- Atomic writes via O_APPEND, with size bound enforcement
- Return confirmation with `record_id`
- The tool records and returns. It does NOT triage — triage is a B2 concern.

### 3B. Triage Workflow (Debate Hall integration) — B2

**NOT IN SCOPE FOR B1.** Documented here for architectural completeness.

A triage mechanism will:
- Periodically scan `~/.hestai/friction/` for records with `severity >= 2`
- Present to designated reviewer (human or specialist agent)
- Actionable items promoted to Debate Hall as structured debate topics
- The severity threshold (>= 2) is itself a governance policy requiring explicit declaration in standards, not hardcoded in tool logic

### 3C. Resolution Pipeline — B3

**NOT IN SCOPE FOR B1.** Documented here for architectural completeness.

Resolution connects debate outputs to governance amendments:
- Debate synthesis produces governance improvement recommendation
- Recommendation becomes PR to governance source (Vault for identity artifacts like skills/agents/standards, hestai-context-mcp for context artifacts)
- Standard review chain applies (TMG, CRS, CE per tier)
- Friction record linked to resolution for audit trail

---

## 4. DESIGN DECISIONS

### Why universal storage, not per-project?

RCCAFP uses per-project storage because build errors are project-specific — a type error in repo A is irrelevant to repo B. Governance friction is different: "the anchor ceremony required 6 round-trips and the agent guessed at step 4" is the same problem regardless of which repo the agent is working in. Per-project storage fragments the signal and prevents cross-repo pattern detection.

The Ecosystem Lighthouse (Section 2) places context stewardship (clock_in/clock_out) in hestai-context-mcp per ADR-0353. Friction is governance context. The universal storage namespace (`~/.hestai/`) is the correct home.

### Why JSONL, not OCTAVE?

JSONL is essential for capture (fast, atomic, machine-parseable). OCTAVE is essential for deliberation (semantic structure, section headers). The format transition happens at triage (B2), not capture (B1). This follows MIP — don't add format complexity at a stage that doesn't benefit from it.

### Why not embed in clock_out?

clock_out is currently broken (ClaudeJsonlLens failure). Coupling friction capture to clock_out means governance feedback is lost when transcription fails. Independence ensures the most valuable signal (governance improvement) survives infrastructure failures.

### Why free text for target_machinery at B1?

We don't yet know all governance subsystems that will generate friction. Reanchoring Upload, dispatch_colleague, capability profiles — these are all upcoming machinery. Hardcoding an enum now means every new subsystem requires a schema change. Collect the corpus first (B1), then derive the enum from actual data (B2).

### Why evidence is mandatory?

Without evidence, a friction record is an opinion, not a signal. "The anchor was confusing" is noise. "The anchor's SEA stage at .hestai-sys/SYSTEM-STANDARD.md required citing I1-I9 but the file only contains §0-§4 with no I-numbered invariants" is actionable. Mandatory evidence forces diagnostic precision.

---

## 5. GOVERNANCE TRAIL

### Decision Provenance

This spec was produced through structured multi-perspective analysis:

1. **Wind/Wall/Door Debate** (thread: `2026-04-07-post-session-operational-feedb-01knmmkj`): Proposed F2D Protocol with three-layer lifecycle. Identified key tensions: contextual locality vs ecosystem universality, dead-letter queues vs hallucinated automation, shared immune system vs distinct workflows.

2. **Requirements Steward** (Codex): Verdict IN_SCOPE. I1 aligned (persists operational learnings), I2 aligned (if lightweight), I3 aligned (if strict mutable→ratified separation). Phase: Capture=B1, Triage=B2+. Flagged severity auto-promotion threshold as governance policy requiring explicit ownership.

3. **Ho-Liaison** (Gemini): GO with corrected placement. Tool in Core, universal storage. Per-project storage = fragmented feedback loss. Workbench owning tool = separation of concerns violation.

4. **Technical Architect**: Comprehensive assessment. Confirmed universal storage, JSONL format, Core ownership, separate from clock_out. Added: resolution field for self-corrected friction, server-generated envelope following RCCAFP precedent, free text target_machinery at B1.

### Immutable Alignment

| Immutable | Alignment | Notes |
|-----------|-----------|-------|
| I1 (Persistent Cognitive Continuity) | ALIGNED | Friction records persist operational learnings across sessions |
| I2 (Structural Integrity Priority) | ALIGNED | If kept lightweight and bounded; capture only at B1 |
| I3 (Dual-Layer Authority) | ALIGNED | Friction = mutable context; becomes governance only via ratified PR |
| I4 (Freshness Verification) | N/A | Friction records are historical observations, not context to verify |
| I5 (Odyssean Identity Binding) | ALIGNED | Agent role captured in envelope enables pattern detection per-role |
| I6 (Universal Scope) | ALIGNED | Universal storage prevents cross-repo fragmentation |

---

## 6. IMPLEMENTATION NOTES FOR AGENTS

**If you are building the Governance Engine (hestai-context-mcp):**
- Implement `submit_friction_record` as specified in §3A
- Storage path: `~/.hestai/friction/`
- Follow `submit_rccafp_record` implementation pattern (server envelope, O_APPEND, path validation)
- Schema is locked (§2.2) — do not add or remove fields without updating this spec

**If you are an agent completing a session:**
- Before calling `clock_out`, consider: did any governance machinery cause friction?
- If yes, call `submit_friction_record` with specific evidence
- Severity guide: 0 = noticed, 1 = resolved quickly, 2 = significant workaround, 3 = could not proceed
- The `resolution` field is the most valuable — capture how you worked around the issue

**If you are building the Triage workflow (B2):**
- Read from `~/.hestai/friction/` (JSONL files, one per session)
- The severity >= 2 promotion threshold is a governance policy — declare it in standards, don't hardcode
- Promote actionable items to Debate Hall as structured topics with cited evidence
