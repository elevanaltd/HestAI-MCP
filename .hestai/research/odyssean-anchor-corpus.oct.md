===ODYSSEAN_ANCHOR_CORPUS===

META:
  TYPE::RESEARCH_CORPUS
  SOURCE::[/Volumes/HestAI-Projects/odyssean-anchor/docs/architecture-decisions/, /Volumes/HestAI-deprecated/research/odyssean-anchor/]
  EXTRACTED::"2026-01-02"
  PURPOSE::"Implementation patterns for odyssean_anchor MCP tool"
  EVIDENCE_BASE::"4 validated agent vectors + multi-model assessment + specification documents"
  TERMINOLOGY::"See docs/odyssean-anchor-terminology.md for two-layer abstraction (Identity Composition vs Runtime Binding)"
  LAYER::IDENTITY_COMPOSITION[design-time_patterns_for_agent_prompts]

## ERROR_TEMPLATES

### Validation Failure Message Template

```
VALIDATION_FAILED: Odyssean Anchor rejected
---

FAILURES:
1. {SECTION}[{index}]: {failure_description}
   Expected: {expected_format}
   Found: {actual_value}

2. {SECTION}: {failure_description}
   Found: "{problematic_value}"
   Expected: {correct_format_example}

3. {SECTION}: {failure_description}
   Expected: {format_requirement}
   Found: {current_state}

---

RETRY GUIDANCE:
- {specific_fix_instruction_1}
- {specific_fix_instruction_2}
- {specific_fix_instruction_3}
- {verification_instruction}

RETRY_ATTEMPT: {N} of 2 (regenerate and resubmit)
```

### Example Error Messages (From Spec)

```
FAILURES:
1. TENSION[1]: Missing CTX: citation
   Expected: CTX:{filename}:{line}→evidence
   Found: [constraint]<->[state]->implication

2. COMMIT: Artifact too generic
   Found: "response"
   Expected: concrete artifact (e.g., "src/auth/service.ts" or "test result")

3. ARM: FILES section empty
   Expected: FILES::{count}[file1,file2,file3]
   Found: FILES::0[]
```

### Status Response Values

```python
STATUS_VALUES = {
    "success": "Vector validated, binding complete",
    "validation_failed": "Specific failures identified, retry possible",
    "retry_exhausted": "Max 2 retries reached, escalate to human"
}
```

### Terminal Failure Message

```
VECTOR VALIDATION FAILED (max retries exhausted)
Agent cannot proceed without valid anchor.
Escalate to manual review.
```

## RETRY_GUIDANCE_PATTERNS

### Self-Correction Protocol (OA-I3)

RETRY_LOGIC::[
  ON_FAILURE::[
    IF[retry_attempt < 2]->{
      COMPOSE::detailed_failure_message[
        failed_checks::[specifics],
        guidance::[what_to_fix],
        example::[corrected_section]
      ],
      RETURN::failure_response_with_guidance,
      AGENT_READS->REGENERATES->RESUBMITS
    },
    IF[retry_attempt >= 2]->{
      STOP::"Max retries exhausted",
      DO::log_failure_for_human_audit
    }
  ]
]

### Guidance Message Components

GUIDANCE_STRUCTURE::[
  1. SPECIFIC_FAILURE::"Identify exact section and field that failed",
  2. EXPECTED_FORMAT::"Show correct syntax with example",
  3. FOUND_VALUE::"Quote exactly what was submitted",
  4. FIX_INSTRUCTION::"Imperative verb + specific action",
  5. VERIFICATION_HINT::"How agent can verify fix before resubmit"
]

### Guidance Examples by Failure Type

#### Missing CTX Citation
```
RETRY GUIDANCE:
- Add CTX:{filename}:{line_range}→evidence to TENSION[N]
- Cite actual file from your loaded context
- Verify file exists in your working directory
```

#### Generic Artifact in COMMIT
```
RETRY GUIDANCE:
- Replace "response" with actual output path
- Use concrete filename (e.g., "src/validators/anchor.ts")
- Include file extension or method name
```

#### Missing TRIGGER
```
RETRY GUIDANCE:
- Add TRIGGER[{action}] to end of TENSION line
- Action should be concrete (DELEGATE, HALT, VALIDATE, SCAN)
- Reference what happens when tension activates
```

#### Empty FILES Section
```
RETRY GUIDANCE:
- Populate FILES with actual modified files from git status
- Include 1-3 most relevant files
- Verify count matches actual modifications
```

#### Placeholder Values
```
RETRY GUIDANCE:
- Replace {TODO} with actual value from context
- ARM values must reflect real branch/phase state
- No placeholder syntax allowed in final vector
```

### Key Insight: Coaching Not Rejection

From ChatGPT Assessment:
> "The tool should provide detailed failure messages with specific guidance, not just pass/fail."
> "Agents understand failure reason 90% of time = success metric"

Implementation Pattern:
- Error messages MUST include "what to fix"
- Error messages SHOULD include corrected example
- Error messages MUST NOT be generic rejections

## VALIDATION_LOGIC

### Three-Phase Validation Pipeline

PHASE_1::STRUCTURE_VALIDATION::[
  opening_marker::"===ODYSSEAN_ANCHOR===" in line 1-3,
  closing_marker::"===END_ODYSSEAN_ANCHOR===" in final line,
  section_headers::[
    "## BIND",
    "## ARM",
    "## FLUKE",
    "## SOURCES",
    "## TENSION",
    "## HAZARD",
    "## COMMIT"
  ]->all_present_in_order
]

PHASE_2::CONTENT_VALIDATION::[
  BIND::[
    has_ROLE::"ROLE::{agent_name}"[not_empty],
    has_COGNITION::"COGNITION::{type}::{archetype}"[valid_values],
    COGNITION_type::[ETHOS, LOGOS, PATHOS],
    COGNITION_archetype::[ATLAS, ATHENA, HEPHAESTUS, HERMES, APOLLO, ARGUS, PROMETHEUS, DIONYSUS],
    role_matches_invocation::actual_role == declared_role
  ],
  ARM::[
    has_PHASE::"PHASE::{value}"[not_placeholder],
    PHASE_valid_values::[D0,D1,D2,D3,B0,B1,B2,B3,B4,B5],
    has_BRANCH::if_main_agent["BRANCH::{name}[{ahead}up{behind}down]"],
    has_BRANCH::if_subagent["BRANCH::{request_summary}"],
    FILES_present::if_main_agent["FILES::{count}[file1,file2,file3]"],
    FILES_actual_data::not_all_brackets_empty,
    FAIL_IF::"ARM contains placeholders or TODO values"
  ],
  FLUKE::[
    has_SKILLS::"SKILLS::[skill1,skill2,...]"[not_empty],
    has_AUTHORITY::"AUTHORITY::RESPONSIBLE[...]",
    AUTHORITY_format::[policy_blocked::{path_list}, if_touched->HALT, delegate::{agent_list}],
    delegate_agents_valid::known_agent_names,
    FAIL_IF::"AUTHORITY missing policies or delegate targets"
  ],
  SOURCES::[
    BY_TIER::{quick::optional, default::required, deep::required_and_exhaustive},
    format::"CTX:{filename}:{line_range}->{evidence}",
    evidence_present::not_empty_or_generic,
    citations_count::>=tension_count,
    FAIL_IF::"SOURCES missing or generic citations"
  ],
  TENSION::[
    count_by_tier::{quick::min_1, default::min_2, deep::min_3},
    each_tension_format::"TENSION::[constraint]<->[state]->implication::TRIGGER[strategy]",
    each_tension_has_CTX::"CTX:{filename}:{line}->evidence",
    each_tension_has_L::L{N}_line_reference,
    each_tension_has_TRIGGER::"TRIGGER[{action}]",
    constraint_and_state_not_generic::actual_code_reference_or_policy,
    FAIL_IF::[tension_count_below_tier_minimum, missing_CTX_citation, missing_TRIGGER, generic_constraint_or_state, duplicate_tensions]
  ],
  HAZARD::[
    has_cognition::"HAZARD::[{cognition}]->NEVER[...]",
    NEVER_list_present::not_empty,
    NEVER_items_specific::actual_anti_patterns_not_generic,
    count::"at_least_2_hazards_for_default",
    FAIL_IF::"HAZARD generic or vague"
  ],
  COMMIT::[
    format::"COMMIT::[action]->[artifact]->[gate]",
    artifact_concrete::not_generic[
      valid_hints::[".","test","ts","tsx","md","json","/",".spec"],
      invalid_hints::[response, result, output, completion]
    ],
    artifact_addressable::path_like_or_method_name,
    validation_gate_testable::not_vague,
    FAIL_IF::[artifact_generic, gate_untestable, action_vague, artifact_already_exists_without_change_context]
  ]
]

PHASE_3::SEMANTIC_VALIDATION::[
  no_circular_tensions::"A->B and B->A same vector = fail",
  no_contradictory_hazards::"NEVER[X] but TENSION_suggests_X = fail",
  AUTHORITY_align_with_FILES::"if_FILES_show_src_changes_but_AUTHORITY_blocks_src = fail",
  COMMIT_feasible::"artifact_path_exists_or_can_be_created = ok, artifact_path_violates_AUTHORITY = fail"
]

### Tier Requirements Summary

| Tier    | Tensions | Sources   | Hazards | Use Case                    |
|---------|----------|-----------|---------|----------------------------|
| quick   | min 1    | optional  | min 1   | Status checks, <5min tasks |
| default | min 2    | required  | min 2   | Normal feature work        |
| deep    | min 3    | exhaustive| min 3   | Architecture decisions     |

### Validation Response Schema

```python
{
  "status": "success" | "validation_failed" | "retry_exhausted",
  "validated_anchor": str,          # Canonical anchor block (on success)
  "validation_failures": [str],     # Specific failures (on failure)
  "retry_guidance": str,            # What to fix (on failure)
  "retry_count": int,               # Track attempts
  "canonical_binding": dict         # Parsed anchor data (on success)
}
```

## EDGE_CASES

### Empty Repository State
- Trigger: git status returns no files, branch info incomplete
- Handling: ARM section must still contain valid PHASE and BRANCH
- Guidance: "Provide at least branch name even if no modified files"

### Detached HEAD State
- Trigger: Not on a named branch
- Handling: BRANCH should show "BRANCH::detached[commit_sha_short]"
- Guidance: "Include commit SHA prefix if no branch name available"

### Subagent Context Injection
- Trigger: Subagent has no direct git access, receives context bundle
- Handling: ARM section uses "BRANCH::{request_summary}" format instead of git state
- Difference: Subagents don't populate FILES, use parent context summary

### Stale Session State
- Trigger: Session started >24h ago
- Handling: Tool should warn but not fail
- Guidance: "Consider re-running clock_in for fresh context"

### Missing Constitution File
- Trigger: Agent role has no discoverable constitution
- Handling: Validation cannot verify COGNITION archetype
- Guidance: "Verify agent constitution exists at expected path"

### Line Number Fragility (Critical Finding)

From ChatGPT Assessment:
> "If you keep L{N}, you recreate your own critique: line numbers are fragile and can be faked."

MITIGATION_OPTIONS::[
  OPTION_A::"Use stable IDs: RULE:NO_DIRECT_IMPLEMENTATION, RULE:ARTIFACT_PERSISTENCE",
  OPTION_B::"Attach CONSTITUTION_SHA::{hash} and validate L{N} against exact version",
  RECOMMENDED::"RULE:{ID}@L{N} as hybrid (stable ID primary, line number secondary)"
]

Example hybrid format:
```
TENSION::[RULE:NO_DIRECT_IMPLEMENTATION@L315]<->[CTX:role=orchestrator]->LANE_ENFORCEMENT::TRIGGER[DELEGATE_CODE]
```

### File Output vs Cognitive Context (Critical Discovery)

From Prototype Findings:
> "Agents generated vectors and wrote them to files, but vectors remained external to agent's active cognitive context."

SYMPTOM::[
  Vector written to disk::YES,
  Vector in agent's working memory::NO,
  Agent can reference it during subsequent work::NO
]

SOLUTION::[
  MCP_OUTPUT_MUST_INCLUDE::"canonical_vector_reintroduced_to_context",
  AGENT_SEES::"Validated vector in active conversation",
  AGENT_CARRIES::"Vector through rest of session"
]

### Multi-Model Variations

From Prototype (4 vectors, 2 models):
- Opus: 57-61 lines, 2-3 tensions, functional format
- Haiku: 54-80 lines, 3 tensions, more detailed structure
- Both: Valid on first generation, no placeholder issues

IMPLICATION::"Model size affects detail level; both valid. Validation must not penalize brevity if requirements met."

## ASSUMPTION_RATIONALE

### Why Unified Binding Path?

DECISION::"Main agents + subagents use identical odyssean_anchor MCP call"
RATIONALE::[
  "Both receive prompt + context (no structural difference)",
  "Both need validation gates (symmetric quality)",
  "Different paths = cognitive overhead on delegating agents",
  "Identical paths = one mechanism to maintain, fewer bugs"
]

### Why MCP Tool Over Skill Injection?

DECISION::"Validation as MCP tool call, not skill triggering"
RATIONALE::[
  "Skills trigger on keywords (agents don't say 'validate me')",
  "Constitutional protocols are mandatory (skill system is optional)",
  "MCP allows stateful validation (retry loop, session context)",
  "Skill system doesn't support self-correction loops"
]

### Why Max 2 Retries?

DECISION::"Max 2 retries. Then fail with clear message."
RATIONALE::[
  "Unlimited = potential infinite loop (agent keeps generating same invalid vector)",
  "2 retries = agent has chance to fix + recover from transient error",
  "Fail hard = forces human escalation if agent can't self-correct",
  "Better to fail fast than loop silently"
]

### Why Tier System?

DECISION::"Three tiers (quick/default/deep) with tier-specific requirements"
RATIONALE::[
  "Status checks don't need 3 tensions (quick tier = 1)",
  "Feature work needs caution (default = 2 tensions)",
  "Architecture decisions need rigor (deep = 3 tensions)",
  "Single level -> under-validates simple tasks OR over-validates fast queries",
  "Tiers allow proportional rigor without penalty"
]

### Why Tool Gating Pattern?

From ChatGPT Assessment - Enforcement Pattern A (Strongest):
> "Every 'real work' tool call checks: has_valid_anchor(session_id, agent_id). If not, it fails hard with 'Bind first.'"

RATIONALE::"This is how you make binding non-optional for both main and subagents"

Alternative patterns:
- Pattern B (Orchestrator gating): Weaker, rogue tool could run without orchestrator noticing
- Pattern C (Prompt-only policy): Fails under pressure and drift, not sufficient for structural integrity

## KEY_INSIGHTS

### Insight 1: Split-Brain Binding Problem

From ChatGPT Assessment:
> "You have two partially overlapping 'binding products': Anchor (T4) is binding metadata + enforcement return. Vector (T6) is the actual cognitive binding artifact. They are generated by different mechanisms, validated differently, stored differently, and can diverge without you noticing. The real problem is not redundancy, it's split-brain binding."

SOLUTION::"Converge on one canonical binding record (Odyssean Anchor == vector == stored anchor)"

### Insight 2: Tool Cannot Force, Must Gate

From ChatGPT Assessment:
> "An MCP tool can't 'make' an LLM do anything by itself. It can make the system enforce: 'No work unless a valid anchor exists.'"

IMPLEMENTATION::"Tool gating pattern - every work tool checks for valid anchor"

### Insight 3: Compute, Don't Just Store

From ChatGPT Assessment:
> "To make auditability real (not theater), the tool should not just store what the LLM claims. It should compute and validate parts of the anchor from the real world."

TOOL_SHOULD_COMPUTE::[
  "branch, ahead/behind",
  "git status summary (modified count, top files)",
  "context file existence + hashes",
  "enforcement policy for role (blocked paths, delegate lanes)"
]

### Insight 4: Agents Understand the Spec

From Prototype Validation:
> "All 4 agents generated valid vectors on first attempt. No placeholder syntax issues. All required sections present and properly formatted."

IMPLICATION::"Specification is clear enough for agents to follow. Implementation should trust agent generation capability while validating output."

### Insight 5: Context Reintroduction Required

From Key Finding:
> "Vector should be both: 1) Output in conversation -> Active cognitive binding, 2) Written to file -> Persistent audit trail + human review"

MCP_DESIGN_REQUIREMENT::[
  "OUTPUT canonical_vector_to_conversation (NEW)",
  "PERSIST_to_file",
  "agent_continues_with_vector_in_context (NEW)"
]

### Insight 6: Validation Clarity Drives Success

From Decision Summary:
> "Error clarity: Agents understand failure reason 90% of time = success metric"

DESIGN_PRINCIPLE::"Validation failures must be specific, actionable, and include fix guidance"

## PERFORMANCE_REQUIREMENTS

| Metric               | Requirement   | Rationale                    |
|---------------------|---------------|------------------------------|
| Validation latency  | <1 second     | User experience (agent waits)|
| Retry overhead      | <5 seconds    | Acceptable slowdown for 2 retries |
| Session state lookup| <100ms        | Common case optimization     |
| Failure message gen | <200ms        | UX clarity                   |

## SUCCESS_METRICS

PRIMARY::[
  "Binding success: >95% first attempt, >99% with retries",
  "Load time: <5s (main), <2s (subagent)",
  "Zero silent failures: All invalid vectors caught",
  "Symmetric paths: Main = Subagent (same steps)"
]

SECONDARY::[
  "Retry rate: <5% (quality indicator)",
  "Error clarity: Agents understand 90% of failures",
  "Audit completeness: 100% of bindings logged",
  "Adoption: All new agents use odyssean_anchor"
]

===END===
