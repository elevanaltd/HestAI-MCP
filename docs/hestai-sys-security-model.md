# Security Model: `.hestai-sys` Governance Protection

## Overview

`.hestai-sys` contains read-only system governance that MUST NOT be modified by agents or tools. This document describes the security model protecting this critical system layer.

## Current Protection Model

### 1. Write Protection at Server Level

**Only the MCP server itself can create/update `.hestai-sys`:**

```python
# src/hestai_mcp/mcp/server.py

# ONLY these functions can modify .hestai-sys:
- inject_system_governance()     # Lines 116-170
- ensure_system_governance()      # Lines 172-209
- bootstrap_system_governance()   # Lines 216-240

# Called at:
- Server startup (main() line 469)
- Tool invocation validation (clock_in line 368, odyssean_anchor line 434)
```

**No MCP tools have write access:**
- `clock_in` - Reads context only
- `clock_out` - Writes to `.hestai/sessions/` only
- `odyssean_anchor` - Validates identity only
- `document_submit` - (TODO) Will write to `.hestai/` only

### 2. Atomic Operations Prevent Corruption

```python
# Atomic swap pattern (server.py:142-164)
1. Build complete tree in .hestai-sys.__tmp__/
2. Rename .hestai-sys → .hestai-sys.__old__
3. Rename .hestai-sys.__tmp__ → .hestai-sys
4. Delete .hestai-sys.__old__
```

No partial states possible - either complete update or rollback.

### 3. Version Checking Prevents Downgrades

```python
# Version validation (server.py:194-201)
if current_version == desired_version && has_required_dirs:
    return  # No modification
else:
    inject_system_governance()  # Full replacement
```

### 4. `.gitignore` Prevents Commits

```bash
# .gitignore line 12
.hestai-sys/
```

Governance is never committed, always fresh from MCP package.

## Attack Vectors & Mitigations

### Vector 1: Agent Attempts Direct Write

**Attempt:** Agent uses `Write` or `Edit` tool on `.hestai-sys/` files

**Mitigation:**
- ✅ Already protected by North Star rules
- ✅ `.hestai-sys` is read-only by convention
- ⚠️ **Current gap:** No technical enforcement in Write/Edit tools

**Recommendation:** Add path validation to Write/Edit tools:
```python
def validate_write_path(path: Path) -> None:
    if ".hestai-sys" in path.parts:
        raise PermissionError("Cannot modify .hestai-sys - read-only governance")
```

### Vector 2: Malicious MCP Server

**Attempt:** Compromised MCP server package injects malicious governance

**Mitigation:**
- ✅ Package signing (PyPI/npm)
- ✅ Version pinning in requirements
- ✅ Code review before updates
- ⚠️ **Current gap:** No signature verification of hub content

**Recommendation:** Future versions should include:
```python
# Cryptographic verification of hub content
hub_signature = get_hub_signature()
verify_signature(hub_path, hub_signature, TRUSTED_PUBLIC_KEY)
```

### Vector 3: Environment Variable Manipulation

**Attempt:** Set `HESTAI_PROJECT_ROOT` to sensitive location

**Mitigation:**
- ✅ `_validate_project_identity()` requires `.git` or `.hestai` marker
- ✅ Path traversal protection in `validate_working_dir()`
- ✅ CWD default reduces need for env var

### Vector 4: Race Condition During Update

**Attempt:** Modify `.hestai-sys` during atomic swap

**Mitigation:**
- ✅ Atomic rename operations
- ✅ Temp directory pattern
- ✅ Old directory cleanup

## Future Enhancements

### Phase 1: Tool-Level Protection (Immediate)
```python
# Add to Write/Edit tools
PROTECTED_PATHS = [".hestai-sys", ".git", ".env"]
if any(protected in path for protected in PROTECTED_PATHS):
    raise PermissionError(f"Protected path: {path}")
```

### Phase 2: Filesystem Permissions (Medium-term)
```python
# After creation, set read-only
os.chmod(hestai_sys_dir, 0o555)  # r-xr-xr-x
for file in hestai_sys_dir.rglob("*"):
    os.chmod(file, 0o444)  # r--r--r--
```

### Phase 3: Cryptographic Verification (Long-term)
- Sign hub content at build time
- Verify signatures at injection time
- Include hash manifest in package
- Validate individual file integrity

## Security Principles

1. **Least Privilege:** Tools can only write to their designated areas
2. **Defense in Depth:** Multiple layers of protection
3. **Fail Closed:** Errors prevent modification, not allow it
4. **Auditability:** All modifications logged with version tracking
5. **Immutability:** Once injected, `.hestai-sys` is read-only until next version

## Summary

**Current State: SECURE with caveats**

✅ **Strengths:**
- Only MCP server can modify `.hestai-sys`
- Atomic operations prevent corruption
- Version checking prevents downgrades
- Not committed to git

⚠️ **Gaps to address:**
1. Write/Edit tools lack path validation (easy fix)
2. No cryptographic verification (future enhancement)
3. No filesystem permission enforcement (medium-term)

**Recommendation:** Implement Tool-Level Protection immediately in next PR.
