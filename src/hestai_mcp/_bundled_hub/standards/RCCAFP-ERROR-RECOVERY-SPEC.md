---
type: SPECIFICATION
id: rccafp-error-recovery
version: "1.0"
status: APPROVED
purpose: Canonical error recovery architecture for the HestAI agent ecosystem
created: 2026-04-06
origin: Implementation Lead session — LLM attention physics analysis and design debate
builds-on:
  - "dream-team-architecture.md §1.3 (B2 BUILD), §2.4 (Archetype Matrix), §4.2 (Config-Driven Orchestration)"
  - "dream-team-proposal.md (error-architect consolidation)"
delivery: "Bundled hub → .hestai-sys/standards/ (cross-repo, all agents)"
---

# RCCAFP Error Recovery Architecture

**Version:** 1.0
**Status:** APPROVED

---

## WHAT THIS DOCUMENT IS

Cross-repo specification for error recovery in the HestAI agent ecosystem. Defines the RCCAFP tool schema, the Reanchoring Upload mechanism, and the canonical 7-step error recovery workflow.

This is the **single source of truth** for error recovery architecture. Implementing agents in any repo should reference this spec. It supersedes any earlier discussions of error-architect consolidation or session-teardown approaches.

**Relationship to other documents:**
- **Dream Team Architecture:** This spec implements B2 BUILD error recovery (§1.3 rework loop) using the Archetype Matrix profile system (§2.4).
- **Ecosystem Lighthouse:** Future Lighthouse update should reference this spec for Governance Engine capabilities.
- **PROJECT-CONTEXT:** Per-repo contexts may note this spec exists; this spec is authoritative.
- **RCCAFP Skill (`library/skills/rccafp/SKILL.md`):** The existing RCCAFP skill defines a 5-phase HO-orchestrated incident management protocol for system-level incidents (directory-based artifacts under `.hestai/state/incidents/`). This spec defines a lightweight single-agent build-failure tool that captures the same RCCAFP principles (root cause, corrective action, future proofing) in a compact JSON record. **These are complementary, not conflicting:** the `submit_rccafp_record` tool handles local build failures within a single IL session; the full RCCAFP skill handles system-level incidents requiring multi-agent coordination. When `escalation_required=true` triggers dispatch to a specialist AND the issue is determined to be systemic, the specialist may invoke the full RCCAFP incident protocol.

---

## 1. THE PROBLEM

When an LLM agent hits a build failure during implementation, it has approximately **2 attempts** before attention contamination degrades diagnostic quality. Failed hypotheses accumulate in the context window and drag on the softmax distribution, causing the model to generate variations of already-failed approaches.

Two naive solutions both fail:

| Approach | Why It Fails |
|----------|-------------|
| Prompt instructions ("produce a root cause report") | Cannot break diagnosis momentum — LLMs facing stack traces succumb to brute-force loops and ignore text-level instructions to stop |
| Session teardown ("start fresh") | Context-arson — destroys implementation intent, codebase understanding, dependency mappings, and nuanced decisions accumulated during the session |

---

## 2. THE ARCHITECTURE

### 2.1 Reanchoring Upload — Mid-Session Profile Swap

Identity (Role) and Axioms (System Standards) are **Primacy** — they stay static in the system prompt. Archetypes and Skills are **Praxis** — they operate through **Recency Bias** and can be swapped mid-session.

When an agent needs to switch profiles (e.g., `feature_implementation` → `build_failure_recovery`), the Payload Compiler generates a Reanchoring Upload injected into the latest chat turn:

```
===REANCHORING_UPLOAD===
MODE::{profile_name}
ARCHETYPE_LENS::{archetype_from_matrix}
KERNELS_INJECTED::[raw §5::ANCHOR_KERNEL text for requested skills...]

MANDATE::"Calibrate your lens. Do not drift. Output [LENS_CALIBRATION: {Skill} → {Target}] identifying which diagnostic skill you are applying to the error, then resume execution."
```

The forced structural output creates an **autoregressive state-lock** — subsequent tokens are conditioned on the new lens. This redirects output mode without destroying accumulated context.

**Critical limitation:** Reanchoring Uploads redirect output **format** but not attention **distribution**. After 2+ failed diagnostic iterations, contaminated hypothesis tokens still influence reasoning through softmax drag. This is why the RCCAFP tool is required as a hard physical boundary.

### 2.2 RCCAFP Tool — Physical Diagnostic Boundary

`submit_rccafp_record` is an MCP tool in the **Governance Engine (hestai-context-mcp)**. It forces the model from continuation mode into summarization mode via structured JSON schema — a fundamentally different cognitive operation that breaks diagnosis momentum.

**Locked Tool Schema:**

| Field | Type | Required | Purpose |
|---|---|---|---|
| `working_dir` | String | Yes | Project root path for resolving `.hestai/state/` target directory. Required for multi-repo path resolution — mirrors `clock_in`, `clock_out`, `bind` patterns. |
| `context_summary` | String | Yes | What was the implementation intent before the failure? Enables lossless dispatch if escalated. |
| `root_cause_analysis` | String | Yes | What actually broke? |
| `fix_attempt_1` | String | Yes | First hypothesis: what was tried, why it failed |
| `fix_attempt_2` | String | No | Second hypothesis: what was tried, why it failed |
| `escalation_required` | Boolean | Yes | The binary structural gate — determines whether the agent continues or a specialist is dispatched |
| `future_proofing_rule` | String | Yes | If fixed: prevention rule for the codebase. If escalated: context constraints the specialist needs. |

**Logging:** All submissions are appended to `{working_dir}/.hestai/state/error-metrics.jsonl`. This satisfies **I1 (Persistent Cognitive Continuity)** for cross-session learning and enables **B3 REINTEGRATE** to extract error patterns.

**Record envelope:** Each JSON line is a self-contained record with server-generated metadata:

```json
{
  "record_id": "rccafp-{uuid4}",
  "timestamp": "ISO-8601",
  "session_id": "from active session",
  "agent_role": "from active permit",
  "working_dir": "/path/to/project",
  "context_summary": "...",
  "root_cause_analysis": "...",
  "fix_attempt_1": "...",
  "fix_attempt_2": null,
  "escalation_required": false,
  "future_proofing_rule": "..."
}
```

Writes must be atomic (write to temp file, then rename) to prevent partial records from concurrent sessions.

### 2.3 Canonical 7-Step Error Recovery Workflow

```
1. IL hits build failure during feature_implementation
2. Engine triggers Reanchoring Upload → build_failure_recovery profile
3. IL diagnoses (attempt 1)
4. If unresolved → attempt 2
5. After attempt 2 → submit_rccafp_record is MANDATORY
6. escalation_required=false →
     Reanchoring Upload back to feature_implementation
     IL implements fix with full context preserved
7. escalation_required=true →
     dispatch_colleague(specialist) with RCCAFP JSON
     Specialist (typically Critical Engineer) gets fresh context
     RCCAFP JSON acts as attention firewall — no contaminated bytes transfer
```

**Step 5 is the structural gate.** The RCCAFP tool forces summarization (switching from "generate next code diff" to "compress semantic state"). The `escalation_required` boolean is a commitment the model must make — it cannot sleepwalk through it.

**Step 7 is the attention firewall.** When escalated, the dispatched specialist receives ONLY `context_summary` + `root_cause_analysis` + `future_proofing_rule`. None of the IL's failed hypothesis tokens, stack trace explorations, or contaminated reasoning transfers. The specialist binds fresh via anchor ceremony with clean context.

---

## 3. BUILD SEQUENCE

### 3A. Payload Compiler (hestai-workbench)

The Payload Compiler must support a `ReanchoringUploadGenerator` that:
- Reads the target profile from the archetype matrix
- Extracts archetype + qualifier + skill kernels (§5::ANCHOR_KERNEL from each skill)
- Generates the Reanchoring Upload block with MANDATE output requirement
- Injects into the current chat turn without destroying KV cache

**Trigger:** Agent calls `swap_profile("build_failure_recovery")` or equivalent dispatch signal.

### 3B. Governance Engine (hestai-context-mcp)

Implement `submit_rccafp_record` as an MCP tool alongside existing `clock_in`, `clock_out`, `bind`:
- Accept `working_dir` for path resolution (same pattern as existing tools)
- Validate schema (all required fields present, types correct)
- Append to `{working_dir}/.hestai/state/error-metrics.jsonl` with server-generated envelope (§2.2)
- Atomic writes (temp file + rename) to prevent partial records
- Return confirmation with `record_id` for dispatch reference
- The tool itself does NOT dispatch — it records and returns. Dispatch is the Workbench's responsibility.

### 3C. Dispatch Layer (hestai-workbench)

The Workbench monitors RCCAFP submissions for `escalation_required=true`:
- Reads `context_summary` + `root_cause_analysis` + `future_proofing_rule` from the record
- Triggers `dispatch_colleague(critical-engineer)` with structured payload
- The specialist binds fresh via anchor ceremony with RCCAFP context only
- Uses continuation model (`dispatch_id`) if the specialist needs follow-up

---

## 4. DESIGN DECISIONS

### Why not a separate error-architect agent?

The Implementation Lead owns "Full lifecycle ownership: construction through failure recovery back to green." Local build failures are IL's domain. The RCCAFP escalation gate replaces error-architect for local errors. System-wide errors (if they occur) route through the dispatch layer's existing `dispatch_colleague` mechanism — no dedicated error agent needed.

### Why not session teardown?

Session teardown destroys tacit context that is not fully reconstructable from a root cause report. The Reanchoring Upload preserves this context while redirecting the agent's operational mode. The RCCAFP tool provides the hard boundary that prompt instructions cannot.

### Why not a post_error_build profile?

After diagnosis (step 6, `escalation_required=false`), the agent Reanchoring Uploads back to `feature_implementation`. Implementing a fix is structurally identical to implementing any feature — the only difference is input context, which the RCCAFP record provides. A separate profile adds complexity without adding different capabilities. MIP wins.

### Why 2 attempts, not 3?

LLM attention contamination is measurable after 2 failed diagnostic iterations. Each failed hypothesis adds ~2-4k tokens of contaminated reasoning to the context. After 2 attempts, the contamination mass (~4-8k tokens) begins to dominate over the Reanchoring Upload's recency signal. The 2-attempt limit is a physics constraint, not an arbitrary threshold.

---

## 5. RELATIONSHIP TO EXISTING ARCHITECTURE

| System | Relationship |
|--------|-------------|
| **Archetype Matrix** (dream-team-architecture §2.4) | `build_failure_recovery` is a profile defined per-agent in the matrix |
| **dispatch_colleague** (Lighthouse §4) | Escalation uses existing dispatch mechanism — no new pattern |
| **B2 BUILD** (dream-team-architecture §1.3) | Error recovery is part of the B2 rework loop |
| **I1 Cognitive Continuity** (North Star) | Error metrics persist in `.hestai/state/error-metrics.jsonl` |
| **B3 REINTEGRATE** (dream-team-architecture §1.4) | EXTRACT step can mine error-metrics.jsonl for recurring patterns |

---

## 6. IMPLEMENTATION NOTES FOR AGENTS

**If you are building the Governance Engine (hestai-context-mcp):**
- Implement `submit_rccafp_record` as specified in §3B
- The tool logs to `.hestai/state/error-metrics.jsonl`
- Schema is locked (§2.2) — do not add or remove fields without updating this spec

**If you are building the Workbench Payload Compiler:**
- Implement `ReanchoringUploadGenerator` as specified in §3A
- The Reanchoring Upload format (§2.1) is the canonical template
- The MANDATE line must force structural output to achieve autoregressive state-lock

**If you are building the Workbench Dispatch Layer:**
- Monitor RCCAFP submissions as specified in §3C
- Use existing `dispatch_colleague` contract — no new dispatch mechanism needed
- The RCCAFP JSON IS the attention firewall — pass only the structured fields, never raw session context

**If you are defining agent profiles in the Archetype Matrix:**
- Every implementing agent (IL, etc.) should have a `build_failure_recovery` profile
- This profile loads error-triage + diagnostic-protocols skills
- The profile is activated via Reanchoring Upload, not initial binding
