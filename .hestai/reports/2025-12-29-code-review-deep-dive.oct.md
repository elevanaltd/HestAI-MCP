# HestAI MCP Code Review Deep Dive (2025-12-29)

## Carry-forward recommendations
- Unify the synchronous and async `clock_in` flows behind a shared helper so validation, metadata, FAST updates, and context resolution cannot drift. Both versions currently duplicate the same blocks of code and parameters, increasing the risk of divergence.【F:src/hestai_mcp/mcp/tools/clock_in.py†L350-L520】
- Thread the resolved `project_root` from `clock_in` through to `clock_out` instead of searching only `cwd`/parent. The current heuristic scan will miss sessions started from other roots or worktrees, yielding false “not found” errors.【F:src/hestai_mcp/mcp/server.py†L193-L247】
- Harden redaction so tool payloads that are lists/tuples or mixed container types are also sanitized before archiving; the present implementation only recurses into dictionaries and leaves list entries untouched.【F:src/hestai_mcp/mcp/tools/clock_out.py†L60-L110】

### Genius insight #1
- Treat governance injection (`inject_system_governance`) as a versioned, idempotent startup hook that writes a manifest of copied files and hashes. This would allow drift detection and safe, automatic upgrades of `.hestai-sys` without user intervention, turning the server into a self-healing source of truth for governance assets.【F:src/hestai_mcp/mcp/server.py†L33-L108】

## New findings from deeper dive
- Expand transcript metrics to count tool-use and tool-result events (not just user/assistant messages) so session analytics reflect the actual interaction volume; the current counter intentionally omits these event types, skewing activity summaries.【F:src/hestai_mcp/mcp/tools/clock_out.py†L176-L183】
- Reduce reliance on heuristic transcript discovery by persisting an explicit session-to-transcript map (e.g., written during `clock_in` alongside `session.json`). The resolver currently scans recent JSONL files and project metadata with time and count limits, which can miss files under heavy load or custom layouts.【F:src/hestai_mcp/mcp/tools/shared/path_resolution.py†L1-L120】
- Make the bundled hub lookup resilient to packaging layouts by using `importlib.resources.files("hestai_mcp.hub")` (or similar) instead of a relative `Path(__file__)` hop. The current path math assumes a flat installed tree and will break if the package is zipped or relocated by a build tool.【F:src/hestai_mcp/mcp/server.py†L33-L58】

### Genius insight #2
- Add a tamper-evident session ledger: each `clock_in`/`clock_out` writes a signed manifest (hash chain) of session metadata, transcript path, and archive artifacts. The ledger would enable integrity verification, automatic replays to rebuild FAST/state layers, and safe cross-host replication without trusting filesystem timestamps.
