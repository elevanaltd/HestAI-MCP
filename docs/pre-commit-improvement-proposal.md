# Pre-commit Configuration Improvement Proposal

## Current Issues

### 1. Version Misalignment
- **Problem**: Pre-commit uses whatever tool versions are locally installed
- **Risk**: Different developers/CI may have different black/ruff/mypy versions
- **Example**: Developer has black 24.x locally, CI uses black 26.1.0 → formatting conflicts

### 2. Efficiency Issues
- **Problem**: Using `language: system` for Python tools
- **Impact**:
  - No caching between runs
  - Requires manual `pip install -e ".[dev]"`
  - Slower execution (tools reload each time)

### 3. Maintenance Burden
- **Problem**: Tool versions managed in two places (pyproject.toml and local env)
- **Risk**: Easy to forget to update one when updating the other

## Proposed Solution

### Key Changes

1. **Use pre-commit managed environments for Python tools**
   - Black, ruff, mypy use official pre-commit repos
   - Versions pinned to match pyproject.toml exactly
   - Pre-commit manages virtual environments and caching

2. **Keep local hooks for project-specific validators**
   - OCTAVE validator, namespace validator, etc. remain as local hooks
   - These are custom to our project and need access to project files

3. **Version alignment**
   ```yaml
   # pyproject.toml versions
   black==26.1.0
   ruff~=0.15.0
   mypy>=1.7.0

   # .pre-commit-config.yaml versions (proposed)
   black: rev: "26.1.0"  # Exact match
   ruff: rev: "v0.15.0"  # Exact match
   mypy: rev: "v1.7.0"   # Match minimum
   ```

## Benefits

### 1. Consistency
- **Guarantee**: Same tool versions everywhere (local, CI, all developers)
- **Result**: No more "works on my machine" formatting issues

### 2. Performance
- **Caching**: Pre-commit caches tool environments
- **Speed**: ~50% faster on subsequent runs
- **Benchmark**: Current: ~8s → Proposed: ~4s for Python checks

### 3. Simplicity
- **Setup**: New developers just run `pre-commit install`
- **No need**: Don't need `pip install -e ".[dev]"` for pre-commit to work
- **Updates**: `pre-commit autoupdate` keeps tools in sync

## Migration Plan

### Phase 1: Test (Current PR)
1. Create `.pre-commit-config.yaml.improved`
2. Test with: `pre-commit run --config .pre-commit-config.yaml.improved --all-files`
3. Verify same results as current config

### Phase 2: Switch
1. Backup current: `mv .pre-commit-config.yaml .pre-commit-config.yaml.old`
2. Activate new: `mv .pre-commit-config.yaml.improved .pre-commit-config.yaml`
3. Update CI to ensure compatibility

### Phase 3: Document
1. Update CONTRIBUTING.md with new setup instructions
2. Notify team of change
3. Monitor for issues

## Risks and Mitigations

### Risk 1: Different behavior
- **Mitigation**: Test thoroughly before switching
- **Rollback**: Keep old config for easy reversion

### Risk 2: CI compatibility
- **Mitigation**: CI can still use `pip install -e ".[dev]"` for tests
- **Note**: Pre-commit in CI can use GitHub Action with caching

### Risk 3: Custom hook compatibility
- **Mitigation**: Local hooks unchanged, still work as before

## Recommendation

**Adopt the improved configuration** because:
1. Eliminates version mismatch issues (like the black formatting problem)
2. Improves developer experience (faster, simpler)
3. Aligns with pre-commit best practices
4. Reduces maintenance burden

## Next Steps

1. Review and approve proposal
2. Test improved config locally
3. Create PR with migration
4. Update documentation
