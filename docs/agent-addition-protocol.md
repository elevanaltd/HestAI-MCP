# Agent Addition Protocol

## Overview
This document defines the standardized process for adding new agents to the HestAI MCP bundled hub.

## Agent Format Specification

All agents MUST conform to OCTAVE Agents v6.0.0 "Dual-Lock" schema as defined in:
`.venv/lib/python3.12/site-packages/octave_mcp/resources/specs/octave-agents-spec.oct.md`

## Required Structure

```octave
---
name: agent-name
description: Brief description of agent purpose and capabilities.
---

===AGENT_NAME===
META:
  TYPE::AGENT_DEFINITION
  VERSION::"6.0.0"
  PURPOSE::"Expanded description of agent purpose."
  CONTRACT::HOLOGRAPHIC[JIT_GRAMMAR_COMPILATION]

§1::IDENTITY
  // STAGE 1 LOCK: IMMUTABLE • CONSTITUTIONAL
  CORE::[...]

§2::BEHAVIOR
  // STAGE 2 LOCK: CONTEXTUAL • OPERATIONAL
  CONDUCT::[...]

§3::CAPABILITIES
  // DYNAMIC LOADING
  SKILLS::[...]
  PATTERNS::[...]

§4::INTERACTION_RULES
  // HOLOGRAPHIC CONTRACT
  GRAMMAR::[...]

===END===
```

## Key Constraints

1. **Size**: Target 90-120 lines total
2. **Version**: Must use VERSION::"6.0.0"
3. **Sections**: All four sections (§1-§4) are required
4. **Frontmatter**: YAML frontmatter with name and description required

## Process for Adding New Agents

### Step 1: Define Core Identity
- Determine ROLE, COGNITION (LOGOS/ETHOS/PATHOS), and ARCHETYPE
- Define MISSION and PRINCIPLES
- Establish AUTHORITY levels

### Step 2: Specify Behavior
- Set MODE, TONE, and PROTOCOL
- Define OUTPUT format and REQUIREMENTS
- Establish VERIFICATION gates
- Plan INTEGRATION handoffs

### Step 3: List Capabilities
- Reference existing skills or create new ones
- Apply relevant patterns
- Keep domain knowledge in skill files, not agent definition

### Step 4: Define Interaction Rules
- Set GRAMMAR patterns (MUST_USE/MUST_NOT)
- Use regex for structural validation

## Migration from Older Formats

When migrating agents from v5.x or earlier:

1. **Extract domain knowledge** → Move to skill files
2. **Compress verbose sections** → Apply semantic compression
3. **Conform to v6 structure** → Use the four-section format
4. **Validate size** → Ensure 90-120 line target

## Example Migration

The OCTAVE Specialist agent was migrated from v5.1.0 (155 lines) to v6.0.0 (92 lines):
- Core OCTAVE mastery matrix → `octave-mastery` skill
- Compression patterns → `semantic-compression` skill
- Verification protocols → `compression-validation` pattern
- Maintained essential capabilities through skill references

## Validation Checklist

Before committing a new agent:

- [ ] Follows v6.0.0 OCTAVE Agents spec exactly
- [ ] Has valid YAML frontmatter
- [ ] Contains all four required sections
- [ ] Is between 90-120 lines
- [ ] References skills for domain knowledge
- [ ] Uses consistent formatting with existing agents
- [ ] Passes OCTAVE syntax validation

## File Location

All agents must be placed in:
`src/hestai_mcp/_bundled_hub/library/agents/`

## Naming Convention

- Filename: `agent-name.oct.md` (kebab-case)
- Internal ROLE: `AGENT_NAME` (SCREAMING_SNAKE_CASE)
- Frontmatter name: `agent-name` (kebab-case)
