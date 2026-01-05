# Solution: `.hestai-sys` Visibility for Agents

## The Problem

`.hestai-sys` is invisible to agents because:
1. **Gitignored** - Doesn't show in `git status`, `git ls-files`, etc.
2. **Not referenced** - No MCP tools currently read from it
3. **Not discoverable** - Agents don't know it exists or contains governance

This creates a paradox: The governance that should guide agents is invisible to them!

## Current State Analysis

### What `.hestai-sys` Contains
```
.hestai-sys/
├── governance/       # Rules agents should follow
│   ├── rules/       # Naming standards, visibility rules
│   └── workflow/    # North Stars, methodology
├── agents/          # Agent constitutions
├── library/         # Commands, skills, specs
│   ├── commands/    # Like /bind command
│   ├── skills/      # Reusable patterns
│   └── specs/       # Protocols (Odyssean Anchor, etc)
└── templates/       # Project templates
```

### How Agents Currently Access Governance

**They don't!** Currently agents rely on:
- `.claude/` files (user-specific)
- `.hestai/workflow/` (project-specific)
- Hardcoded knowledge

## Proposed Solutions

### Solution 1: Make Tools Governance-Aware (Recommended)

**Modify `clock_in` to return governance paths:**

```python
# clock_in returns context paths, should ALSO return governance
def clock_in(...):
    # Existing: returns .hestai/context/* paths
    context_paths = [...]

    # NEW: Also return .hestai-sys paths
    governance_paths = [
        ".hestai-sys/governance/rules/naming-standard.oct.md",
        ".hestai-sys/governance/workflow/000-SYSTEM-HESTAI-NORTH-STAR.md",
        ".hestai-sys/agents/{role}.oct.md",  # Role-specific constitution
    ]

    return {
        "context_paths": context_paths,
        "governance_paths": governance_paths,  # NEW
        "governance_note": "Read-only system governance in .hestai-sys/"
    }
```

### Solution 2: Add Explicit Governance Discovery Tool

**New tool: `discover_governance`**

```python
@app.tool()
def discover_governance(working_dir: str) -> dict:
    """Discover and list governance files in .hestai-sys.

    Returns paths to:
    - System rules
    - Agent constitutions
    - Commands and skills
    - North Stars
    """
    hestai_sys = Path(working_dir) / ".hestai-sys"

    if not hestai_sys.exists():
        return {"error": "No .hestai-sys found - run MCP server first"}

    return {
        "governance_root": str(hestai_sys),
        "rules": list((hestai_sys / "governance/rules").glob("*.md")),
        "agent_constitutions": list((hestai_sys / "agents").glob("*.oct.md")),
        "commands": list((hestai_sys / "library/commands").glob("*.md")),
        "skills": list((hestai_sys / "library/skills").glob("*/SKILL.md")),
        "note": "These files are read-only system governance"
    }
```

### Solution 3: Session Hook Notification

**Add to session-start hook:**

```bash
# In session_start/setup-dependencies.sh or new hook

if [ -d ".hestai-sys" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📚 GOVERNANCE AVAILABLE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "System governance loaded at: .hestai-sys/"
    echo "Key files:"
    echo "  • .hestai-sys/governance/rules/ - System rules"
    echo "  • .hestai-sys/agents/ - Agent constitutions"
    echo "  • .hestai-sys/library/commands/bind.md - Binding ceremony"
    echo "Note: These are read-only, delivered by MCP server"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
```

### Solution 4: README Visibility Marker

**Add `.hestai-sys/README.md` that's always visible:**

```markdown
# System Governance Directory

This directory contains read-only system governance delivered by the MCP server.

## ⚠️ DO NOT MODIFY
These files are automatically managed and will be replaced on server restart.

## Contents
- `governance/` - System rules and workflows
- `agents/` - Agent constitutions
- `library/` - Commands, skills, and specs
- `templates/` - Project templates

## For Agents
Use `Read` tool to access these files for governance guidance.
Example: `Read .hestai-sys/governance/rules/naming-standard.oct.md`
```

## Recommended Implementation Plan

### Phase 1: Immediate (This PR)
1. ✅ Add README.md to `.hestai-sys` for discoverability
2. ✅ Document in main README that `.hestai-sys` exists

### Phase 2: Next PR
1. Modify `clock_in` to return governance paths
2. Add path validation to Write/Edit (security hardening)

### Phase 3: Future
1. Add `discover_governance` tool
2. Session hook notifications
3. Agent constitution auto-loading

## Benefits

- **Discoverability**: Agents know governance exists
- **Accessibility**: Clear paths to read governance
- **Consistency**: All agents see same rules
- **Maintainability**: Single source of truth

## Implementation Notes

The key insight: **Gitignored doesn't mean invisible to agents!**

Agents can still:
- Use `Read` tool on `.hestai-sys/*` paths
- Use `Glob` to discover files
- Receive paths from tools

We just need to tell them it's there!
