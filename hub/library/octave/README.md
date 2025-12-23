# OCTAVE Library Reference

This directory previously contained local copies of OCTAVE specifications.

**Canonical Source:** `/Volumes/OCTAVE/octave/specs/`

## Specification Files (v5.1.0)

| File | Purpose |
|------|---------|
| `octave-5-llm-core.oct.md` | Core syntax, operators, types |
| `octave-5-llm-data.oct.md` | Data mode patterns |
| `octave-5-llm-schema.oct.md` | Schema mode (holographic) |
| `octave-5-llm-execution.oct.md` | Runtime execution |
| `octave-5-llm-rationale.oct.md` | Design decisions |
| `octave-5-llm-agents.oct.md` | Agent definitions |
| `octave-5-llm-skills.oct.md` | Skills format |
| `octave-mcp-architecture.oct.md` | MCP tool architecture |

## MCP Tools

- `octave_ingest` - Parse, normalize, validate OCTAVE content
- `octave_eject` - Project to various formats, generate templates

## Skills

Load via Claude Code skills system:
1. `octave-literacy` - Essential syntax
2. `octave-mastery` - Semantic vocabulary (requires literacy)
3. `octave-compression` - Transformation workflow

## HestAI Integration

See `.hestai/workflow/octave-integration-guide.md` for usage patterns.
