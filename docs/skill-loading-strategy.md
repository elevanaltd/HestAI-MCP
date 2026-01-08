# Skill Loading Strategy

## Overview
Skills in the HestAI system follow a two-tier loading pattern based on their criticality and purpose.

## Loading Tiers

### 1. Constitutional Skills (Anchor-Loaded)
Skills that define the core constitutional capabilities of an agent. These are:
- Listed in the agent's §3::CAPABILITIES section
- Automatically provided during anchor ceremony at Stage 3 (COMMIT)
- Essential for role integrity and constraint enforcement

**Example:** For holistic-orchestrator:
- `prophetic-intelligence` - Core failure prediction capability
- `gap-ownership` - Essential cross-boundary responsibility
- `system-orchestration` - Fundamental coordination methodology
- `constitutional-enforcement` - Required for system integrity
- `ho-mode` - Critical lane discipline preventing implementation drift

### 2. Operational Skills (Manually Loaded)
Skills that define specific operational workflows. These are:
- NOT listed in agent §3::CAPABILITIES
- Loaded on-demand via `Skill()` tool or slash commands
- Extend or enhance constitutional capabilities

**Example:** For holistic-orchestrator:
- `ho-orchestrate` - Extends ho-mode with quality gates and debate-hall
- Loaded via `/ho-orchestrate` or `Skill(ho-orchestrate)`

## Decision Criteria

Add to §3::CAPABILITIES (Constitutional) when:
- Skill prevents role drift or confusion
- Skill enforces critical constraints
- Skill defines core identity/capabilities
- Absence would compromise agent integrity

Keep as operational (Manual) when:
- Skill is workflow-specific
- Skill extends existing capabilities
- Skill is situational or context-dependent
- Skill adds optional enhancements

## Implementation Notes

1. **Anchor provides skills from `.hestai-sys/library/skills/`** based on agent §3::CAPABILITIES
2. **Subagents receive their skills through their own anchor ceremony**
3. **Skills reference patterns dynamically loaded from `.hestai-sys/library/patterns/`**
4. **No hard-coded paths** - all loading through anchor or Skill() tool

## Benefits

- **Single Source of Truth:** Agent definitions control constitutional skills
- **Flexible Enhancement:** Operational skills loaded as needed
- **Clean Separation:** Constitutional vs operational concerns
- **Dynamic Loading:** Skills and patterns provided at runtime
- **Path Independence:** No brittle file path dependencies
