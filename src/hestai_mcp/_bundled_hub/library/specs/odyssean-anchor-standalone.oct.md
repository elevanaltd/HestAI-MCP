===SPECIFICATION===
META:
  TITLE::"Odyssean Anchor Standalone MCP Specification"
  TYPE::SPECIFICATION
  STATUS::DRAFT
  AUTHOR::Warp
  DATE::2026-01-05
  PURPOSE::"Define standalone MCP server for agent identity, conduct, and capability binding where the agent must demonstrate cognitive proof"

## Overview
**Architecture**: Standalone MCP server for agent identity, conduct, and capability binding
**Core Principle**: The agent must do the cognitive work—the ceremony IS the proof

The Odyssean Anchor binds agents to roles through a multi-stage handshake where the agent demonstrates genuine situational grounding. The agent cannot pass by reciting static constraints—it must map conduct constraints onto retrieved project state and declare operational triggers.

**The Keystone**: The TENSION MAP is the cognitive proof. Format:
```
CONDUCT:{constraint_id} ↔ CTX:{path}[state] → TRIGGER:{action}
```
This proves the agent has *perceived* the actual project state, not just loaded a static prompt.

## Terminology

| Term | Alias | Description | Nature |
|------|-------|-------------|--------|
| **SHANK** | Identity | Who the agent is. Constitutional foundation, cognitive foundation, operational identity, principles. The immutable core. | Immutable |
| **ARMS** | Approach | How the agent engages the world. Split into two layers: | |
| → **CONDUCT** | Behavior | Stable work-type behavioral constraints, relational integration patterns | Semi-stable |
| → **CONTEXT** | Focus | Variable runtime focus: phase, target, repo state, task objective | Retrieved live |
| **FLUKES** | Skills | Hotswappable capabilities. Loaded after permit is granted. | Dynamic |
| **Anchor Steward** | Gatekeeper | Server-side validation system (Retriever + Validator) | Internal |

## Architecture Components

### Anchor Steward (Two-Component System)

**CTX Retriever** (Tool-Assisted + Model-Curated)
- Pattern from `clock_in.py`: Reads PROJECT-CONTEXT, git state, North Star, blockers
- Uses configurable model (default: `gemini-flash`) to curate relevant context
- Returns structured context for agent consumption

**Validator** (Structural Checks)
- Pattern from `odyssean_anchor_semantic.py`
- Validates: CTX paths exist, constraint IDs are real, mapping format correct
- Can use nano model for semantic consistency checks
- Configurable via `config.yaml` (mirroring `ai.yaml` pattern)

### Constraint ID System

IDs are **artifact-scoped** and generated/managed at compile-time:
```
(artifact_id, clause_id)
```

Example in OCTAVE block:
```octave
CONDUCT::[artifact_id::"architect-conduct"]
  @C-01::no_write_without_read
  @C-02::tdd_required_for_mutations
  @POL-03::must_validate_before_commit
```

Agent references as: `CONDUCT:architect-conduct@C-02`

## Binding Tiers

### FULL (Complete Ceremony)
For high-stakes work, architectural changes, or first-time role binding.

**Flow**:
```
┌─────────────────────────────────────────────────────────────────┐
│ (a) ROLE REQUEST                                                │
│     Agent submits: role + tier (+ optional topic/focus)         │
│     → Tool: anchor_request(role, tier, focus?)                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ (b) SHANK DELIVERY + VALIDATION REQUEST                         │
│     Server returns:                                             │
│       - SHANK content (identity prompt)                         │
│       - session_id                                              │
│       - validation_template: "EXTRACT & SUBMIT [fields...]"     │
│     Fields configurable in profile YAML                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        [Agent reads SHANK, processes, reasons]
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ (c) INITIAL LOCK + ARMS REQUEST                                 │
│     Agent submits:                                              │
│       - session_id                                              │
│       - shank_validation: { extracted fields per template }     │
│       - focus (if not provided in step a)                       │
│     → Tool: anchor_lock(session_id, validation, focus?)         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ (d) ARMS DELIVERY (CONDUCT + CONTEXT)                           │
│     Steward:                                                    │
│       - Validates shank lock (structural + optional semantic)   │
│       - Retrieves CONTEXT via CTX Retriever                     │
│     Returns:                                                    │
│       - CONDUCT content (behavioral constraints with @IDs)      │
│       - CONTEXT summary (project state, git, blockers)          │
│       - tension_template: format guide for TENSION MAP          │
│       - commit_template: format guide for COMMIT                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        [Agent maps CONDUCT to CONTEXT - THE COGNITIVE WORK]
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ (e) TENSION MAP + COMMIT                                        │
│     Agent submits:                                              │
│       - session_id                                              │
│       - tensions: [                                             │
│           {                                                     │
│             conduct: "architect-conduct@C-02",                  │
│             ctx: "src/auth/handler.py[no_tests]",               │
│             trigger: "write_tests_before_refactor"              │
│           },                                                    │
│           ...                                                   │
│         ]                                                       │
│       - commit: {                                               │
│           artifact: "src/auth/handler_test.py",                 │
│           gate: "pytest"                                        │
│         }                                                       │
│     → Tool: anchor_commit(session_id, tensions, commit)         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ (f) VALIDATION + PERMIT                                         │
│     Steward validates:                                          │
│       ✓ CTX paths/states exist                                  │
│       ✓ Constraint IDs are real (exist in CONDUCT)              │
│       ✓ Mapping is consistent with SHANK + CONDUCT              │
│       ✓ Commit artifact + gate method are allowed               │
│                                                                 │
│     If APPROVED:                                                │
│       - Issue permit_id                                         │
│       - Load FLUKES (skills)                                    │
│       - Return bound agent response                             │
│                                                                 │
│     If DENIED:                                                  │
│       - Return structured feedback                              │
│       - Agent may retry (max 2 retries)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ (g) ODYSSEAN ANCHOR (Optional Dashboard)                        │
│     Verified agent produces immutable anchor record:            │
│       - SHANK summary                                           │
│       - TENSION MAP                                             │
│       - COMMIT contract                                         │
│       - permit_id + timestamp                                   │
│     Visible to subsequent agents in session/project             │
└─────────────────────────────────────────────────────────────────┘
```

### STANDARD (Reduced Ceremony)
For normal work and minor/medium changes where cognitive proof is still required.

- Same staged flow as FULL
- SHANK validation is shorter (configurable extract fields)
- Steward returns ARMS (CONDUCT + CTX) as normal
- Agent submits smaller TENSION MAP (1-2 bindings) + simplified COMMIT
- Steward verifies and, if approved, issues permit + loads FLUKES

### MICRO (Single-Call Bundle)
For explorer/nano agents and bounded read-only tasks.

- **Single-call**: `anchor_micro(role, task_description)`
- Returns ready-to-run bundle:
  - micro-SHANK (compressed identity)
  - minimal CONDUCT
  - FLUKES (read-only only)
  - output_contract (required response format)
- **No Steward involvement** by default
- **No staged proof step**—cognitive grounding enforced by output format (paths + evidence)
- **No privileged permits**—FLUKES must be safe/read-only per metadata

### MICRO+ (Refined Single-Call)
Same as MICRO, but for ambiguous requests needing scope refinement.

- Steward refines prompt + scope
- Optionally provides scoped CTX starter set
- Still single-call, no handshake, no permits, read-only FLUKES
- Intended for "help me look in the right places" rather than deep anchoring

## Tool Surface (MCP)

### Tools

#### `anchor_request` (Step a)
```typescript
anchor_request(
  role: string,           // e.g., "architect", "implementation-lead"
  tier: "full" | "standard" | "micro" | "micro+",
  focus?: string,         // Optional work focus
  working_dir?: string    // Project root (for CTX retrieval)
): {
  session_id: string,
  shank: string,          // Full SHANK content
  validation_template: {
    required_fields: string[],  // e.g., ["COGNITION", "ARCHETYPES", "CORE_FORCES"]
    format: string              // OCTAVE format guide
  }
}
```

#### `anchor_lock` (Step c)
```typescript
anchor_lock(
  session_id: string,
  shank_validation: Record<string, string>,  // Extracted fields
  focus?: string                             // If not provided in request
): {
  lock_status: "accepted" | "rejected",
  rejection_reason?: string,  // If rejected
  // ONLY if lock_status == "accepted":
  conduct?: string,           // CONDUCT content with @IDs
  context?: {                 // Retrieved project state
    summary: string,
    files: string[],
    git_state: string,
    blockers: string[]
  },
  tension_template?: string,  // Format guide
  commit_template?: string    // Format guide
}
```

#### `anchor_commit` (Step e)
```typescript
anchor_commit(
  session_id: string,
  tensions: Array<{
    conduct: string,   // "artifact@clause_id"
    ctx: string,       // "path[state]"
    trigger: string    // action
  }>,
  commit: {
    artifact: string,  // path
    gate: string       // method
  }
): {
  status: "approved" | "denied",
  permit_id?: string,
  flukes?: Array<{
    id: string,
    content: string
  }>,
  feedback?: string,        // If denied
  retries_remaining?: number // If denied
}
```

#### `anchor_micro` (MICRO/MICRO+ tiers)
```typescript
anchor_micro(
  role: string,
  task_description: string,
  use_steward?: boolean     // true = MICRO+, false = MICRO
): {
  bundle: {
    shank: string,          // Micro-SHANK
    conduct: string,        // Minimal conduct
    flukes: Array<{         // Read-only only
      id: string,
      content: string,
      safe: true
    }>,
    output_contract: string // Required response format
  },
  ctx_hints?: string[]      // If MICRO+ with steward
}
```

#### `anchor_verify`
```typescript
anchor_verify(
  permit_id: string
): {
  valid: boolean,
  role: string,
  tier: string,
  expires_at: string,
  tensions_summary: string[]
}
```

### Resources

| URI | Description |
|-----|-------------|
| `oa://shanks/{role}` | SHANK content for role |
| `oa://conduct/{role}` | CONDUCT content with @IDs |
| `oa://flukes/{skill_id}` | FLUKE content |
| `oa://permits/{permit_id}` | Permit record + anchor dashboard |

## Storage Layout

```
~/.odyssean-anchor/
├── config.yaml                    # Global config
├── shanks/                        # Identity prompts
│   ├── architect.oct.md
│   └── implementation-lead.oct.md
├── conduct/                       # Behavioral constraints (with @IDs)
│   ├── architect.oct.md
│   └── implementation-lead.oct.md
├── flukes/                        # Skills
│   ├── tdd-workflow.oct.md
│   ├── code-review.oct.md
│   └── _metadata.yaml             # Safety flags per fluke
├── profiles/                      # Role profiles linking shank+conduct+flukes
│   ├── architect.yaml
│   └── implementation-lead.yaml
├── permits/                       # Session artifacts
│   ├── active/
│   │   └── {permit_id}.json
│   └── archive/
└── governance/                    # Pluggable provider mounts
    └── hestai/
```

## Profile Format

```yaml
# ~/.odyssean-anchor/profiles/architect.yaml
id: "architect"
version: "1.0"
description: "System architect role"

shank:
  source: "file://shanks/architect.oct.md"

conduct:
  source: "file://conduct/architect.oct.md"

flukes:
  - id: "architecture-review"
    source: "file://flukes/arch-review.oct.md"
  - id: "tdd-workflow"
    source: "file://flukes/tdd-workflow.oct.md"

# Permission configuration for commit validation
gates:
  allowed: ["pytest", "npm test", "cargo test", "jest", "mocha", "make check", "make test"]
  # Optional defaults per project type
  defaults:
    backend: ["pytest", "cargo test"]
    frontend: ["npm test", "jest", "mocha"]
    generic: ["pytest", "npm test"]

# Tier-specific configuration
tiers:
  full:
    validation_fields: ["COGNITION", "ARCHETYPES", "CORE_FORCES", "PRINCIPLES"]
    min_tensions: 3
  standard:
    validation_fields: ["COGNITION", "CORE_FORCES"]
    min_tensions: 1
  micro:
    allowed: true
    flukes_override: ["read-only-analysis"]  # Safe subset

steward:
  retriever_model: "gemini-flash"
  validator_model: "gemini-flash-lite"
  timeout_seconds: 30
  max_retries: 2
```

## Flukes Metadata (Safety Enforcement)

```yaml
# ~/.odyssean-anchor/flukes/_metadata.yaml
flukes:
  tdd-workflow:
    safe: false
    requires_permit: true
    gates: ["pytest", "npm test"]

  code-review:
    safe: false
    requires_permit: true

  read-only-analysis:
    safe: true
    requires_permit: false  # Can be used in MICRO

  search-codebase:
    safe: true
    requires_permit: false
```

## Validation Logic

### Steward Validator Checks (Step f)

```python
# Pattern from odyssean_anchor_semantic.py

def validate_tension_map(tensions, conduct_content, working_dir):
    """Validate cognitive proof."""
    errors = []

    for tension in tensions:
        # 1. CTX path exists
        ctx_path = extract_path(tension["ctx"])
        if not path_exists(working_dir, ctx_path):
            errors.append(f"CTX path not found: {ctx_path}")

        # 2. Constraint ID exists in CONDUCT
        constraint_id = tension["conduct"]
        if not constraint_exists(conduct_content, constraint_id):
            errors.append(f"Constraint ID not found: {constraint_id}")

        # 3. Format valid
        if not valid_trigger_format(tension["trigger"]):
            errors.append(f"Invalid trigger format: {tension['trigger']}")

    return errors

def validate_commit(commit, profile):
    """Validate commit contract."""
    errors = []

    # Artifact path is valid target
    if not is_valid_artifact_path(commit["artifact"]):
        errors.append(f"Invalid artifact path: {commit['artifact']}")

    # Gate method is allowed for this profile
    # Falls back to global defaults if not specified
    if profile.get("gates", {}).get("allowed"):
        allowed_gates = profile["gates"]["allowed"]
    elif profile.get("allowed_gates"):
        allowed_gates = profile["allowed_gates"]
    else:
        # Default to common gates
        allowed_gates = ["pytest", "npm test", "cargo test", "jest", "mocha", "make check", "make test"]

    if commit["gate"] not in allowed_gates:
        errors.append(f"Gate not allowed: {commit['gate']}. Allowed: {allowed_gates}")

    return errors
```

## Configuration

```yaml
# ~/.odyssean-anchor/config.yaml
version: "1.0"

steward:
  retriever:
    model: "gemini-flash"
    timeout_seconds: 30
  validator:
    model: "gemini-flash-lite"
    timeout_seconds: 15
    fail_mode: "block"  # or "warn"

security:
  require_0700: true
  max_retries: 2
  permit_ttl_seconds: 3600

governance:
  active_provider: "local"  # or "hestai"
  providers:
    hestai:
      sync_source: ".hestai/governance"
      auto_sync: true
```

## MVP Scope

### Phase 1: Core (FULL tier only)
1. Storage structure + config loading
2. `anchor_request` → returns SHANK + validation template
3. `anchor_lock` → validates shank, returns CONDUCT + CTX
4. `anchor_commit` → validates tensions, issues permit, returns FLUKES
5. Basic CTX retriever (files + git state, pattern from clock_in.py)
6. Structural validator (paths exist, IDs exist)

### Phase 2: Steward Integration
7. Model-curated CTX retrieval
8. Semantic consistency checks (optional, pattern from odyssean_anchor_semantic.py)
9. Retry logic with structured feedback

### Phase 3: Tiers
10. STANDARD tier (reduced ceremony)
11. MICRO tier (single-call bundle)
12. MICRO+ tier (steward-refined)

### Phase 4: Ecosystem
13. `anchor_verify` tool
14. Odyssean Anchor dashboard generation
15. HestAI governance provider sync
16. OCTAVE package integration for shank/conduct authoring

## Example: Full Binding Flow

```
Agent: anchor_request(role="architect", tier="full", working_dir="/project")

Server: {
  session_id: "abc-123",
  shank: "[Full architect SHANK content...]",
  validation_template: {
    required_fields: ["COGNITION", "ARCHETYPES", "CORE_FORCES"],
    format: "OCTAVE"
  }
}

Agent: [Reads SHANK, extracts understanding]

Agent: anchor_lock(
  session_id: "abc-123",
  shank_validation: {
    COGNITION: "LOGOS - I operate through systematic analysis...",
    ARCHETYPES: "The Architect, The Guardian...",
    CORE_FORCES: "Structural integrity over velocity..."
  },
  focus: "auth-system-refactor"
)

Server: {
  lock_status: "accepted",
  conduct: "[CONDUCT with @C-01, @C-02, @POL-03...]",
  context: {
    summary: "Branch: feat/auth-refactor, 3 modified files...",
    files: ["src/auth/handler.py", "src/auth/middleware.py"],
    git_state: "4 commits ahead of main",
    blockers: []
  },
  tension_template: "CONDUCT:{id} ↔ CTX:{path}[state] → TRIGGER:{action}"
}

// IF lock_status == "rejected":
Server: {
  lock_status: "rejected",
  rejection_reason: "Shank validation failed: Missing required COGNITION field"
}

Agent: [Maps CONDUCT constraints to actual CTX - THE COGNITIVE WORK]

Agent: anchor_commit(
  session_id: "abc-123",
  tensions: [
    {
      conduct: "architect-conduct@C-02",  // tdd_required
      ctx: "src/auth/handler.py[no_test_file]",
      trigger: "create_handler_test.py_before_refactor"
    },
    {
      conduct: "architect-conduct@POL-03",  // must_validate_before_commit
      ctx: "src/auth/middleware.py[auth_logic_change]",
      trigger: "run_auth_integration_tests"
    }
  ],
  commit: {
    artifact: "src/auth/handler_test.py",
    gate: "pytest"
  }
)

Server: [Validates: paths exist, IDs exist, mapping consistent]

Server: {
  status: "approved",
  permit_id: "permit-xyz-789",
  flukes: [
    { id: "tdd-workflow", content: "[TDD skill content...]" },
    { id: "architecture-review", content: "[Review skill content...]" }
  ]
}

Agent: [Now bound with identity + conduct + skills, ready to work]
```

===END===
