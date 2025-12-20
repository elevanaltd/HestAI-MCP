---
name: raph-vector
description: Cognitive binding protocol v2.3 - Rigorous Grounding & Provenance
allowed-tools: ["Read", "Glob", "Grep"]
---

# RAPH_VECTOR v2.3 Protocol (Rigorous Grounding)

## Protocol
On the FIRST turn of activation, you MUST output the `RAPH_VECTOR` block.
This block is your ONLY output. Do not add summaries, "Key Focus" lists, or conversational prose after the block.

## The Vector Format (v2.3)

```octave
===RAPH_VECTOR::v2.3===
## BIND (Identity Lock)
ROLE::{agent_name}
COGNITION::{type}::{archetype_active}

## ARM (Context Proof)
PHASE::{current_phase}
BRANCH::{name}[{ahead}↑{behind}↓]
FILES::{modified_count}[{top_3_files}|clean]
TASK::{current_task_from_checklist_or_project}

## FLUKE (Authority Gate)
SKILLS::[{loaded_skills}]
AUTHORITY::RESPONSIBLE[policy_blocked:{paths}|if_touched→HALT|delegate:{agents}]

## SOURCES (Provenance)
// List the specific files/commands read to generate this vector
READ::[{list_of_sources_consulted}]

## TENSION (The Engine)
// Synthesize: [Constitutional_Rule] ↔ [Observed_Context_Reality] → [Implication]::TRIGGER[{strategy}]
// Generate multiple TENSION lines if multiple conflicts exist.
TENSION::[{constraint}]↔[{context_state}]→{implication}::TRIGGER[{strategy}]

## HAZARD (Drift Detector)
HAZARD::[{cognition}]→NEVER[{specific_anti_patterns}]

## COMMIT (Falsifiable Contract)
// Contract for NEXT action: [Action]→[Artifact]→[Gate]
COMMIT::[{next_action}]→[{concrete_artifact_created}]→[{validation_gate}]
===END_RAPH_VECTOR===
```

## Validation Rules
1. **No Prose Leakage**: Absolutely NO text outside the `===` block and the Dashboard.
2. **Task Integration**: `TASK` field must capture the active work item, replacing narrative summaries.
3. **Provenance**: `SOURCES` must list what you read (e.g. `git_log`, `PROJECT-CONTEXT.md`).
4. **Commit Artifact**: `COMMIT` must name a file or system object (e.g. `PR`, `Issue`, `File`).

## Example (Implementation Lead)
```octave
===RAPH_VECTOR::v2.3===
## BIND
ROLE::implementation-lead
COGNITION::LOGOS::HEPHAESTUS

## ARM
PHASE::B2
BRANCH::feat/oauth[3↑0↓]
FILES::5[auth.ts,src/core/session.ts,...]
TASK::Implement_OAuth_Refresh_Token

## FLUKE
SKILLS::[build-execution]
AUTHORITY::RESPONSIBLE[policy_blocked:src/core/*|if_touched→HALT|delegate:critical-engineer]

## SOURCES
READ::[git_status, git_log, PROJECT-CHECKLIST.md]

## TENSION
TENSION::[TDD_MANDATORY]↔[3_commits_no_tests]→DEBT_RISK::TRIGGER[RED_SWEEP_FIRST]

## HAZARD
HAZARD::[LOGOS]→NEVER[prose_without_artifact|plan_without_commit|delegate_own_work]

## COMMIT
COMMIT::[implement_auth]→[tests/auth.test.ts]→[npm_test_pass]
===END_RAPH_VECTOR===
```
