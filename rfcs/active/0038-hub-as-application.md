# RFC-0038: Hub as Application

**Status**: PENDING (Future B3+ Feature)
**Created**: 2025-12-19
**Updated**: 2025-12-27
**Author**: holistic-orchestrator
**GitHub Issue**: [#38](https://github.com/elevanaltd/HestAI-MCP/issues/38)

> **Note**: Per ADR-0060, RFC folder is deprecated. Future discussion continues in Issue #38. This file retained for reference until decision is made. Related to RFC-0054 (Universal Coordination Hub).

## Summary

Transform the HestAI Hub from a static collection of governance files into an active application that manages governance distribution, version tracking, and project health monitoring across all HestAI-enabled projects.

## Motivation

Currently, the Hub is bundled as static files within the HestAI-MCP package. While this works for single projects, it creates challenges for:

1. **Multi-project governance** - Each project has its own copy of governance files
2. **Version drift** - No central tracking of which projects use which governance versions
3. **Update distribution** - Manual process to update governance across projects
4. **Project visibility** - No dashboard showing health/status of all projects
5. **Breaking changes** - No mechanism to notify projects of governance updates

## Detailed Design

### Phase 1: Project Registry

Create a central registry of all projects using HestAI:

```python
# hub/registry.json
{
  "projects": {
    "eav-monorepo": {
      "path": "/Volumes/HestAI-Projects/eav-monorepo",
      "governance_version": "1.2.0",
      "last_sync": "2025-12-19T10:00:00Z",
      "phase": "B2",
      "health": "green"
    },
    "copy-editor": {
      "path": "/Volumes/HestAI-Projects/copy-editor",
      "governance_version": "1.1.0",
      "last_sync": "2025-12-18T15:00:00Z",
      "phase": "B3",
      "health": "yellow"  // Outdated governance
    }
  }
}
```

### Phase 2: Push Governance Capability

Implement commands to push governance updates to projects:

```bash
# Push to single project
hestai governance push --project eav-monorepo

# Push to all projects
hestai governance push --all

# Dry run to see what would change
hestai governance push --project copy-editor --dry-run

# Push with breaking change warning
hestai governance push --version 2.0.0 --breaking
```

Implementation:
```python
class GovernanceManager:
    def push_governance(self, project_name: str, version: str = "latest"):
        """Push governance files to project's .hestai-sys/"""
        project = self.registry.get_project(project_name)

        # Check version compatibility
        if self.has_breaking_changes(project.governance_version, version):
            if not self.confirm_breaking_changes():
                return

        # Copy governance files
        source = self.hub_path / "governance"
        target = Path(project.path) / ".hestai-sys"

        # Clear and repopulate
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)

        # Update registry
        project.governance_version = version
        project.last_sync = datetime.now()
        self.registry.save()
```

### Phase 3: Version Management

Implement semantic versioning for governance:

```yaml
# hub/governance/version.yaml
version: 1.2.0
changelog:
  1.2.0:
    date: 2025-12-19
    changes:
      - Added new agent: performance-analyst
      - Updated naming-standard.oct.md
    breaking: false

  2.0.0:
    date: 2025-12-25
    changes:
      - Restructured agent architecture
      - New OCTAVE v5 format
    breaking: true
    migration_guide: docs/migration/v2.md
```

### Phase 4: Dashboard UI (Future)

Create a web dashboard for project health monitoring:

```
┌─────────────────────────────────────────────────────────┐
│                  HestAI Project Dashboard               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Project         Phase  Gov Ver  Health  Last Sync      │
│  ─────────────────────────────────────────────────      │
│  eav-monorepo    B2    1.2.0    ✅      2 hours ago    │
│  copy-editor     B3    1.1.0    ⚠️      2 days ago     │
│  scenes-web      B1    1.2.0    ✅      1 hour ago     │
│                                                          │
│  [Push All Updates]  [Check Health]  [View Changelog]   │
└─────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Milestone 1: Registry (Week 1)
- [ ] Create project registry schema
- [ ] Implement registration commands
- [ ] Add project discovery mechanism

### Milestone 2: Push Capability (Week 2)
- [ ] Implement governance push command
- [ ] Add version compatibility checking
- [ ] Create dry-run mode

### Milestone 3: Version Management (Week 3)
- [ ] Implement semantic versioning
- [ ] Add changelog generation
- [ ] Create breaking change notifications

### Milestone 4: Dashboard (Future)
- [ ] Design web UI
- [ ] Implement health checks
- [ ] Add real-time monitoring

## Alternatives Considered

### Alternative 1: Git Submodules
Use git submodules to share governance across projects.
- **Pros**: Native git support, version pinning
- **Cons**: Complex for users, merge conflicts, poor ergonomics

### Alternative 2: NPM Package
Distribute governance as an NPM package.
- **Pros**: Standard package management, version control
- **Cons**: Language-specific, requires package.json in all projects

### Alternative 3: Symbolic Links
Use symlinks to shared governance directory.
- **Pros**: Simple, real-time updates
- **Cons**: Platform issues, breaks with moves, no versioning

## Open Questions

1. **Authentication**: Should push operations require authentication?
2. **Rollback**: How to handle governance rollback if issues occur?
3. **Customization**: Can projects override specific governance rules?
4. **CI Integration**: How to integrate with CI/CD pipelines?
5. **Multi-machine**: How to sync registry across developer machines?

## Security Considerations

- **Write Protection**: Only authorized users can push governance
- **Audit Trail**: Log all governance updates with who/when/what
- **Validation**: Verify governance files before distribution
- **Backup**: Automatic backup before overwriting .hestai-sys/

## Success Metrics

1. **Adoption Rate**: % of projects using latest governance within 7 days
2. **Update Frequency**: Average time between governance updates
3. **Error Rate**: Failed push operations / total pushes
4. **User Satisfaction**: Developer survey on governance management

## Unresolved Questions

- Should the registry be stored in git or as a separate database?
- How to handle projects on different machines/networks?
- What's the migration path for existing projects?
- Should there be a "governance freeze" mechanism for production?

## References

- [ADR-0033: Dual-Layer Context Architecture](../docs/adr/adr-0033-dual-layer-context-architecture.md)
- [HestAI Hub Repository](https://github.com/elevanaltd/HestAI)
- [MCP Specification](https://modelcontextprotocol.io/)
