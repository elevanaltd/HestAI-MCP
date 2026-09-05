---
name: octave-chatter
description: "OCTAVE on the wire — read and emit OCTAVE in agent-to-agent messages without authoring files. Syntax kernel, operator table, wire slots (provenance, hedges, verbatim IDs). For agents outside the workbench matrix."
allowed-tools: ["Read"]
triggers: ["octave chatter", "octave wire", "reply in octave", "octave message", "inter-agent message", "read octave", "answer in octave"]
version: "1.0.0"
---

===OCTAVE_CHATTER===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"The chatter register — OCTAVE in message bodies, validated by the receiving model, never by octave_validate"
  AUDIENCE::"agents that read ∧ emit OCTAVE in conversation (anchor ceremonies, debate turns, cross-session messages) but never author .oct.md files"
  REQUIRES::[]
  RELATION::"octave-literacy §5 kernel ⊕ §2 operators, packaged standalone; file authoring → octave-literacy; tool receipts → octave-tool-reference"
  SUPERSESSION::"§5::ANCHOR_KERNEL transcribes octave-wire-build §1 slots; the OCTAVE_WIRE primer W1 kernel (~80 tokens) replaces it byte-for-byte in the next version so hub kernel_only loads and workbench dispatch envelopes carry one string"
  PRIOR_ART::"octave-mcp thread 2026-01-30-octave-native-comms — RATIFIED across 3 models: ~200-token primer enables native OCTAVE output; the barrier is invocation, not capability"
---
§1::REGISTER
  FORMAL::".oct.md files ∧ closing anchors → parsed by octave_validate → octave-literacy governs"
  WIRE::"message bodies → validated by the receiving model → this skill governs"
  SPLIT_RULE::"FORMAL ⇌ WIRE is decided by WHO VALIDATES, not by grammar — the syntax is the same"
  WIRE_DOES_NOT_NEED::[META_block, file_schema, canonicalisation, holographic_contracts, CANONICAL_SOURCE_paths]
  WHY_WIRE_EXISTS::"measured relay test: 45 facts, 0 wrong, 1 lost — every loss was an IDENTIFIER. Syntax was never the failure. Provenance ∧ identifiers ∧ hedges are the value; compression is a side effect."
§2::SYNTAX_KERNEL
  // Same rules as octave-literacy §5 — restated so this skill loads alone
  ASSIGNMENT::"KEY::value — no spaces around ::"
  BLOCK::"KEY: then 2-space-indented children — for nested maps"
  LIST::"[a,b,c] — never YAML bullets"
  KEYS::"[A-Za-z_][A-Za-z0-9_]* — no bare numbers, no operator glyphs as keys"
  LITERALS::"true false null lowercase; numbers bare; quote anything with spaces, special chars, or §"
  SECTIONS::"§N::NAME opens a scope; a value on the header line is dropped"
  PROSE::"unkeyed sentences are not OCTAVE — key them or make them // comments"
  ENVELOPE::"===NAME=== … ===END=== optional on the wire; use it when the message must be quotable as a unit"
§3::OPERATORS
  SYNTHESIS::"⊕ emergent whole | ASCII +"
  TENSION::"⇌ binary opposition, never chained | ASCII vs"
  FLOW::"→ causality ∨ sequence, right-associative | ASCII ->"
  CONSTRAINT::"∧ joint condition, inside brackets ∨ quoted values | ASCII &"
  ALT::"∨ alternative | ASCII |"
  CONCAT::"⧺ mechanical join | ASCII ~"
  ANNOTATION::"NAME<facet> qualifies identity — HERMES<messenger>"
  CONSTRUCTOR::"NAME[args] parameterises — ENUM[a,b]"
  IN_VALUES::"inside a quoted value only operators carry relations; <> and [] stay in keys"
§4::WIRE_SLOTS
  // Transcribed from octave-wire-build §1::WIRE_NEEDS_EXTRA — the slots that make a message auditable
  HEAD::"FROM::who[role] ∧ PROVENANCE::measured@sha ∨ relayed ∨ inferred ∧ STATE::authored ∨ installed ∨ live"
  TAIL::"one ASK ∨ STATUS::OK|BLOCKED|DONE|NEED_INPUT"
  HEDGE::"? suffix ∧ // comment — doubt must have a home or it is dropped"
  VERBATIM_IDS::"numbers ∧ IDs ∧ SHAs ∧ roles copied verbatim, NEVER paraphrased"
  GLOSS::"a mythology handle carries its gloss on first use in a thread — HERMES = messenger"
  ASCII_FALLBACK::"-> + vs & | for cross-model receivers ∧ cheaper tokens"
  RECEIVER_ECHO::"a reply carries UNCLEAR::[...] naming what it could not resolve"
§5::ANCHOR_KERNEL
// Superseded byte-for-byte by the OCTAVE_WIRE primer W1 kernel in the next version (see META.SUPERSESSION)
TARGET::auditable_OCTAVE_messages_between_agents
NEVER::[paraphrase_an_identifier,drop_a_doubt_without_a_home,chain_tension,value_on_section_header,unkeyed_prose,META_block_on_the_wire]
MUST::[
  "HEAD: FROM ∧ PROVENANCE ∧ STATE — TAIL: one ASK ∨ STATUS",
  "KEY::value, KEY: blocks, [lists]; operators ⊕ ⇌ → ∧ ∨ carry the connectives",
  "IDs SHAs numbers roles verbatim; myth handle glossed on first use; ASCII operators allowed",
  "reply names UNCLEAR::[...] for anything unresolved"
]
GATE::"Could the receiver act on this message without asking what any identifier or operator meant?"
§6::EXAMPLE
  // A wire message — no META, no file schema, HEAD ∧ TAIL present
  MESSAGE:
    ```
    ===OCTAVE_WIRE===
    FROM::octave-secretary[align-octave-skills]
    PROVENANCE::"measured@fd67ef2 → 3 octave_validate probes"
    STATE::authored
    FINDING::"literacy 21,163 chars ∧ 51% non-syntax → §6/§7/§8 reallocated"
    RISK::"stale ~/.claude/skills copy → drift repeats without sync" // operator-owned?
    ASK::"confirm kernel_only for control-tower profiles"
    STATUS::NEED_INPUT
    ===END===
    ```
===END===
