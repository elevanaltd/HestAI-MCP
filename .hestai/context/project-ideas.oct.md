===PROJECT_IDEAS===

META:
  TYPE::IDEAS_DOCUMENT
  VERSION::1.0
  STATUS::DRAFT
  VISIBILITY::PROJECT_INTERNAL

## Overview
This document captures high-level ideas, potential features, and future directions for the HestAI MCP product.

## Product Vision
[Add your high-level product vision here]

## Potential Features
- **Context Consistency Checker (Tool)**
  - **Problem**: Agents implementing against missing, outdated, or hallucinated specs (e.g., missing payload spec in ADR-0004).
  - **Solution**: A System Steward capability (`check_consistency`) that scans a set of documents (ADRs, Plans, Specs) to verify:
    1.  **Referential Integrity**: Do all cited files exist?
    2.  **Semantic Alignment**: Do the implementation plans match the architectural decisions?
    3.  **Version Consistency**: Are we building against the latest accepted spec?
  - **Integration**:
    - **Pre-Flight**: Run before major `anchor_lock` or implementation start.
    - **Orchestra Map**: Leverage ADR-0034 dependency graph to find related docs.
  - **Value**: Prevents "building the wrong thing perfectly" by catching context gaps early.

- **Decision Gravity and Routing Framework**
  - **Problem**: Unauthorized agents making unilateral decisions ("Option 3 it is!") without authority or impact analysis.
  - **Solution**: A structured "Decision Gravity" calculator to enforce the RASI model.
    - **Mechanism**:
      1.  **Calculate Gravity**: `Score = (Scope * Irreversibility * Strategic_Risk)`
      2.  **Route by Score**:
          - **Low (0-20)**: Local Decision (Just do it).
          - **Medium (21-60)**: Consultative (Check with `I`/`C`).
          - **High (61-80)**: **Debate Hall** (Trigger `debate-hall-mcp` to resolve competitive options).
          - **Critical (81-100)**: **Authority Mandate** (Stop. Require explicit `A` sign-off).
    - **Integration**:
      - Embed in `operational-workflow.oct.md`.
      - System Steward enforces: "High Gravity decision detected? Show me the Debate ID or Decision Record."
- **Debate Hall: RACI Dialogue Mode**
  - **Problem**: "Workflow Theatre" vs. "Rogue Decisions". We need a middle ground between "Just doing it" and "Full Heavy Debate."
  - **Solution**: A lightweight `RACI_ALIGNMENT` recipe for `debate-hall-mcp`.
    - **Concept**: Treat a decision record like an email thread where R, A, C, and I are "CC'd".
    - **Mapping**:
      - **Responsible (R)** = **Wind** (Proposes the action/decision).
      - **Consulted (C)** = **Wall** (Checks constraints/risks).
      - **Accountable (A)** = **Door** (Ratifies and closes).
      - **Informed (I)** = **Observer** (Receive the immutable transcript).
    - **Mechanism**:
      - A "Single Round" Debate (Speed Mode): R proposes, then C critiques/validates, then A decides.
      - **Zero-Friction**: If C has no objections, they yield immediately.
      - **Audit Trail**: The "Debate" ID becomes the "Decision Record" (e.g., `DECISION-2026-001`).
  - **Value**: **Front-loaded Alignment**. While invoking agents feels like friction, it is actually "Parallel Processing" of concerns. It is infinitely cheaper to spend 30 seconds loading the "Consulted" agent now than to revert a decision 3 days later because a constraint was missed.

- **The Integrity Engine Pivot**
  - **Concept**: Move HestAI from "Governance Framework" (Rules) to "Integrity Engine" (Coherence).
  - **Core Mechanism**: **The Coherence Loop**.
    1.  **Intent**: Defined in `ADR` + `Spec` (Docs).
    2.  **Reality**: Defined in `Code` + `Tests` (Runtime).
    3.  **Check**: `verify_consistency` runs the diff between Intent and Reality.
  - **Shift**:
    - **Old**: "Did you follow the rule?" (Bureaucracy)
    - **New**: "Does your code match your spec?" (Integrity)
  - **Odyssean Anchor Update**: Becomes "Proof of Comprehension". You cannot bind if you are incoherent (e.g., your mental model contradicts the spec).
  - **Edge Handling ("Break Glass")**:
    - **Problem**: Deadlocks (Circular Trap) where you can't fix code because it contradicts docs, and can't fix docs because CI blocks code.
    - **Solution**: A `break_glass` flag for `check_consistency`.
      - Allows bypass for emergency fixes.
      - **Cost**: Creates a **Blocking Debt Item**. No new features can be merged until the consistency is restored.
    - **Atomic Rule**: Consistency is validated against the *Staged Commit*, allowing simultaneous Doc+Code updates.

## Implementation Order and Parallelization

### Phase 1: Foundation (Sequential)
**The Integrity Engine Pivot**
- Fundamental shift from "rules" to "coherence"
- Establishes Intent vs Reality framework
- All other features build on this concept

### Phase 2: Core Systems (Fully Parallel)
These can be developed independently:

**2A. Odyssean Anchor (Standalone)**
- Pure security/identity layer
- No dependencies on other systems
- Delivers immediate value: role-based access

**2B. HestAI Secretary (Standalone)**
- Pure coordination layer
- No dependencies on other systems
- Delivers immediate value: document consistency

**2C. Context Consistency Checker**
- Builds on Integrity Engine concept
- No dependencies on OA or Secretary
- Delivers immediate value: spec validation

### Phase 3: Decision Framework (Parallel with Phase 2)
Can be developed alongside Phase 2:

**3A. Decision Gravity Framework**
- Quantifies decision importance
- Independent of other systems

**3B. Debate Hall RACI Mode**
- Implements decision routing
- Natural extension of 3A

### Phase 4: Integration (After Phase 2)
**Optional Integration Layer**
- Connect OA + Secretary if both used
- Add consistency checks to workflows
- Integrate decision framework

## Future Roadmap
-

## Constraints and Considerations
[Add any known constraints or important considerations]

## Validation Requirements
- Ensure ideas align with North Star principles
- Validate against existing architectural constraints

## Future Roadmap
### Odyssean Anchor: Identity and Access Control (Standalone)
- **Purpose**: Role-based access control for agent operations
- **Core Concept**: Agents must bind to roles before performing role-specific work
- **Permit-Based Tool Restrictions**
  - **Implementation**: `verify_permit` validates agent has required role for operations
  - **Scope**: Tool access, operation types, file paths based on agent role
  - **Example**: "Only implementation-lead can write code files"
  - **Value**: Prevents unauthorized actions while enabling flexible permissions
- **Progressive Interrogation Integration**
  - **SEA→SHANK→ARM→FLUKES**: Full ceremony for comprehensive agent binding
  - **Capability Declaration**: Agents declare required tools/paths in §3::CAPABILITIES
  - **Dynamic Permit Generation**: Session-based permits with agent-specific scopes
- **Standalone Value**: Works independently - users get role-based access control

### HestAI-MCP: Secretary Coordination (Standalone)
- **Purpose**: Intelligent document routing and consistency management
- **Core Concept**: All documents flow through secretary for smart placement
- **Document Submission Secretary Pattern**
  - **Problem**: Agents writing in silos with inconsistent naming/location
  - **Solution**: System Steward as intelligent document coordinator (internal LLM service)
  - **Mechanism**: `document_submit` routes content based on type, context, relationships
  - **Benefits**: Consistent naming, visibility rules, knowledge graph maintenance
  - **Intelligence**: Orchestra Map provides holistic view of document relationships
- **The Two-Tool Architecture**
  - **document_submit**: Secretary interface for intelligent routing/enforcement
  - **write_docs**: Direct file access for special cases (fallback option)
  - **Delegation Model**: Agents delegate placement decisions to System Steward
  - **Coordination vs. Restriction**: Focus on intelligent routing, not access denial
- **Standalone Value**: Works independently - users get consistent document management

### Architectural Separation (When Both Used)
- **Independent Layers**: OA and Secretary operate at different architectural layers
- **No Direct Dependency**: Secretary doesn't validate OA permits internally
  - Secretary is a service, not an agent needing binding
  - Calling agents either have permissions (if OA used) or don't (if not used)
- **Optional Integration Points**:
  - OA could restrict which agents can call `document_submit` tool
  - But Secretary itself doesn't check permits - that's OA's job
- **Complementary Benefits**:
  - OA provides: "Who can do what" (role-based access)
  - Secretary provides: "Where things belong" (intelligent routing)
  - Together: Comprehensive governance without tight coupling

## Constraints and Considerations
- **Modular Architecture**: Each system must provide standalone value
- **Single Writer Pattern**: Secretary coordination prevents silo formation
- **Performance vs. Coordination**: Balance intelligent routing with operation latency
- **Backwards Compatibility**: Consider existing direct-write patterns in production apps
- **Clear Boundaries**: OA handles "who can", Secretary handles "where should"

## Validation Requirements
- **Independent Testing**: Each system must be testable in isolation
- **Security Boundary Verification**: Ensure OA maintains pure access control
- **Secretary Performance**: Test document coordination under load
- **Optional Integration**: Verify systems work alone and together
- **Knowledge Graph Consistency**: Verify orchestra map maintains coherent relationships

## Change Log
- Document created: 2026-01-10
- Added Odyssean Anchor access control ideas: 2026-01-11
- Added HestAI-MCP secretary coordination concepts: 2026-01-11
- Documented architectural integration approach: 2026-01-11
- Clarified separation of concerns between OA and Secretary: 2026-01-11

===END===
