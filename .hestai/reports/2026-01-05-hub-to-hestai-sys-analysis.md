# Hub → .hestai-sys Governance Injection Analysis

**Date:** 2026-01-05
**Role:** holistic-orchestrator
**Focus:** Review hub vs .hestai-sys mechanics post-PR #157

---

## Executive Summary

**Status:** ✅ **COMPLETE** - `.hestai-sys` creation is fully automated via PR #157

PR #157 successfully implements the complete hub→.hestai-sys pipeline. Governance injection happens automatically at MCP server startup via `bootstrap_system_governance()`.

**Key Finding:** No additional work is required. The system is operational.

---

## Architecture Flow

### 1. Hub Bundling (Build Time)

```
hub/                              (source of truth)
  ↓
pyproject.toml                    (package-data: hestai_mcp._bundled_hub/**)
  ↓
src/hestai_mcp/_bundled_hub/     (shipped in wheel/editable install)
  ├── VERSION
  ├── governance/
  ├── agents/
  ├── library/
  └── templates/
```

**Evidence:**
- `pyproject.toml:56-57` - Package data configuration
- 34 files bundled (Glob confirmed)
- `src/hestai_mcp/mcp/server.py:73-95` - `get_hub_path()` locates bundled hub

### 2. Governance Injection (Runtime)

```
MCP Server Startup
  ↓
main() → bootstrap_system_governance(None)      [server.py:469]
  ↓
Reads HESTAI_PROJECT_ROOT from env              [server.py:225]
  ↓
ensure_system_governance(project_root)          [server.py:172-208]
  ↓
inject_system_governance(project_root)          [server.py:116-169]
  ↓
.hestai-sys/ created atomically                 [atomic swap via tmp dir]
  ├── governance/
  ├── agents/
  ├── library/
  ├── templates/
  └── .version
```

**Evidence:**
- `server.py:469` - Bootstrap called at `main()` entry point
- `server.py:225` - Reads `HESTAI_PROJECT_ROOT` env var
- `server.py:116-169` - Atomic injection via temp dir + rename
- `server.py:172-208` - Idempotent: checks version + required dirs before reinject

### 3. Tool-Level Re-Validation

```
clock_in / odyssean_anchor
  ↓
ensure_system_governance(working_dir)           [server.py:368, 434]
  ↓
Validates .hestai-sys/.version matches hub      [idempotent]
  ↓
Reinjects only if stale or incomplete
```

**Evidence:**
- `server.py:368` - `clock_in` ensures governance before session start
- `server.py:434` - `odyssean_anchor` ensures governance before identity validation
- Tests confirm idempotent behavior (no-op when version matches)

---

## Critical Validations

### Fail-Closed Security (ADR-0033)

1. **Project Identity Check** (`server.py:46-66`)
   - Requires `.git` OR `.hestai` directory
   - Prevents governance injection into arbitrary directories

2. **Environment Validation** (`server.py:224-235`)
   - `HESTAI_PROJECT_ROOT` required if `project_root=None`
   - Prevents writing into CWD

3. **Hub Integrity** (`server.py:98-113`)
   - `VERSION` file must exist (fail-closed packaging validation)
   - Required dirs validated before injection

### Atomic Operations (Production Safety)

```python
# server.py:116-169
tmp_dir = project_root / ".hestai-sys.__tmp__"
# ... build complete tree in tmp_dir ...
tmp_dir.rename(hestai_sys_dir)  # atomic swap
```

No partial injection states - process interruption safe.

---

## Current Status: OPERATIONAL

| Component | Status | Evidence |
|-----------|--------|----------|
| Hub bundling | ✅ COMPLETE | pyproject.toml + 34 files shipped |
| Startup bootstrap | ✅ COMPLETE | `main()` calls `bootstrap_system_governance()` |
| Tool-level validation | ✅ COMPLETE | `clock_in` + `odyssean_anchor` ensure governance |
| Atomic injection | ✅ COMPLETE | Temp dir + rename pattern |
| Idempotency | ✅ COMPLETE | Version check prevents unnecessary reinjects |
| Tests | ✅ COMPLETE | 511 tests passing (unit coverage verified) |

---

## Gap Analysis: NONE FOUND

### Original Question: "Does this automatically create .hestai-sys?"

**Answer: YES** - via three triggers:

1. **MCP Server Startup** (`main()` → line 469)
   - Requires `HESTAI_PROJECT_ROOT` env var
   - Creates `.hestai-sys` in target directory

2. **Tool Invocation** (`clock_in` + `odyssean_anchor`)
   - Validates governance present before operation
   - Re-injects if stale/incomplete

3. **Explicit Bootstrap** (`bootstrap_system_governance(path)`)
   - Can be called programmatically
   - Used in tests with explicit paths

### Configuration Required

**Deployment:**
```bash
# In MCP server config (e.g., Claude Desktop settings)
HESTAI_PROJECT_ROOT=/path/to/your/project
```

**Evidence:** `server.py:225` + `README.md:57-58` (System layer delivery via MCP injection)

---

## Prophetic Assessment: LOW RISK

**Confidence:** 90%

**Known Constraints:**
- Requires `HESTAI_PROJECT_ROOT` env var set correctly
- Symlinks in `.git` (worktrees) handled correctly via `exists()` check
- Version mismatch triggers full reinjection (safe but may surprise users)

**Monitoring:**
- `.hestai-sys/.version` tracks deployed hub version
- Tool-level validation provides runtime safety net
- Atomic operations prevent corruption

---

## Recommendations

### NONE REQUIRED - System operational as designed

### Optional Enhancement Opportunities (Future)

1. **User Visibility** (UX improvement, non-blocking)
   - MCP tools could return governance status in responses
   - Example: `clock_in` → "✓ Governance v1.0.0 active"

2. **Version Update Notifications** (DX improvement, non-blocking)
   - Log when reinjection occurs due to version mismatch
   - Currently silent (idempotent behavior)

3. **Multi-Project Support** (Future scope)
   - Currently requires `HESTAI_PROJECT_ROOT` env var
   - Could support per-tool `working_dir` override (already implemented!)
   - `clock_in` and `odyssean_anchor` accept explicit `working_dir`

---

## Constitutional Compliance

| Requirement | Status |
|------------|--------|
| I2: Structural Integrity Priority | ✅ Fail-closed validation |
| I3: Dual-Layer Authority | ✅ System (.hestai-sys) read-only, delivered by MCP |
| ADR-0033: System vs Product | ✅ Clear separation enforced |
| Security: Path Traversal | ✅ Validated via `validate_working_dir()` |
| Production Safety | ✅ Atomic operations + idempotency |

---

## Conclusion

**PR #157 delivers complete governance injection pipeline.** No pending implementation work.

The hub→.hestai-sys mechanism is:
- ✅ Fully automated
- ✅ Fail-closed secure
- ✅ Production-safe (atomic operations)
- ✅ Idempotent (version-based reinject)
- ✅ Test-covered (511 tests passing)

**System ready for operational use.**

---

**Artifacts:**
- This report: `.hestai/reports/2026-01-05-hub-to-hestai-sys-analysis.md`
- Code references: `src/hestai_mcp/mcp/server.py:116-209,469`
- Tests: `tests/unit/mcp/test_server.py:217-360`
