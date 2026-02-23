---
name: rccafp
description: Root Cause, Corrective Action, and Future Proofing - incident management protocol for multi-agent AI systems. Triggers on incidents, system failures, constraint violations, LLM overreach, or post-mortem analysis.
allowed-tools: [Read, Write, Edit, Grep, Glob, Bash, Task, TodoWrite, AskUserQuestion]
---

# RCCAFP - Root Cause, Corrective Action, and Future Proofing

Structured 5-phase incident management protocol for multi-agent AI systems with human orchestration oversight.

## When to Use

Trigger RCCAFP when:
- A system constraint violation is detected
- An agent operates outside its role boundaries (overreach)
- A production failure or regression occurs
- A constitutional principle (I1-I6) is violated
- An assumption cascade causes unexpected behavior
- Post-mortem analysis is requested

## Five-Phase Process

### Phase 1: Detection and Triage
1. Create incident directory: `.hestai/state/incidents/YYYYMMDD-[incident-name]/`
2. Create subdirectories: `01-root-cause/`, `02-corrective-action/`, `03-future-proof/`
3. Document initial symptoms and severity assessment
4. Determine if full RCCAFP is warranted vs minor fix

### Phase 2: Root Cause Investigation
1. Collect evidence: exact causality chains, artifacts, logs
2. Cross-validate through multi-agent assessment
3. Document in `01-root-cause/causality-chain.md`
4. Identify which system boundaries were violated

### Phase 3: Corrective Action
1. Immediate containment and mitigation
2. Constraint validation - identify gaps in existing boundaries
3. Execute triage and damage control
4. Document in `02-corrective-action/constraint-validations.md` and `triage-execution.md`

### Phase 4: Future Proofing
1. Extract architectural learnings from the incident
2. Design prevention mechanisms with evidence
3. Define monitoring requirements
4. Document in `03-future-proof/prevention-mechanisms.md`

### Phase 5: Closure and Integration
1. Verify all phases are complete and documented
2. Pass findings through synthesis gate before integration
3. Update system documentation only after review
4. Refine protocol based on learnings

## Agent Roles in RCCAFP

| Agent | RCCAFP Role |
|-------|-------------|
| Holistic Orchestrator | Orchestrates process, owns gap accountability |
| Critical Engineer | Leads root cause investigation (tactical) |
| Principal Engineer | Leads future proofing (strategic prevention) |
| Implementation Lead | Executes corrective action implementations |
| Requirements Steward | Validates learnings against North Star |

## Synthesis Gate

All incident learnings must pass through the synthesis gate before being promoted to governance documentation:
- Findings go to `.hestai/state/incidents/pending/`
- Review validates evidence quality and relevance
- Only validated learnings are integrated into system docs

## Anti-Patterns

- **Silent Fix**: Fixing without documenting root cause
- **Skip Synthesis**: Promoting learnings without gate review
- **Blame Cascade**: Attributing to agents rather than system gaps
- **Speculative Prevention**: Creating mechanisms without evidence
- **Scope Creep**: Expanding response beyond the specific failure

## Success Metrics

- Mean Time to Detection (MTTD)
- Mean Time to Containment (MTTC)
- Documentation completeness
- Constraint validation effectiveness
- Incident recurrence rate
- Architecture improvement rate
