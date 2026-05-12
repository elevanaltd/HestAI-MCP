---
name: octave-literacy
description: "LLM-native structured communication format. Teaches OCTAVE syntax rules, canonical forms, and warning prevention for zero-error .oct.md authoring."
allowed-tools: ["Read", "Write", "Edit"]
triggers: ["octave format", "write octave", "octave syntax", "structured output", "OCTAVE basics", "OCTAVE literacy", "OCTAVE structure", "key::value", "OCTAVE notation", "llm communication", "token economy", "loss accounting"]
version: "3.0.0"
---

===OCTAVE_LITERACY===
META:
  TYPE::SKILL
  VERSION::"3.0.0"
  STATUS::ACTIVE
  PURPOSE::"Zero-error OCTAVE authoring — syntax rules, canonical forms, warning prevention"
  OCTAVE::"Olympian Common Text And Vocabulary Engine — loss accounting system for LLM communication"
  AUDIENCE::LLM<exclusively>
  SPEC_REFERENCE::octave-core-spec.oct.md
  NEXT_SKILLS::[octave-mastery,octave-compression]
---
§0::CONSUMPTION_DIRECTIVE
  // You are writing for LLM consumption only. No prose. No narrative. Every token carries payload.
  // Optimize for parsing efficiency and token density. Readability is irrelevant.
  MYTHOLOGY::"Use as compression — zero-shot, trust it. ATHENA<strategic_wisdom> = 1 token replacing 15."
  MYTHOLOGY_ANTI_PATTERN::"ZEUS::executive_decision — use EXECUTIVE::decision when literal is equally clear"
  // Full vocabulary: octave-mastery §1
§1::CORE_SYNTAX
  ASSIGNMENT::"KEY::value — double colon, no spaces around ::"
  BLOCK::"KEY: + newline + 2-space indent — use when value has nested children"
  CHOICE::"scalar value → ASSIGNMENT. nested children → BLOCK. Never mix."
  LIST::"[a,b,c] — square brackets, no YAML bullets ever"
  STRING::"bare_word if no spaces/special chars, else double-quoted"
  NUMBER::"42 or 3.14 or -1e10 — no quotes"
  BOOLEAN::"true or false — lowercase only"
  NULL_VALUE::"null — lowercase only"
  COMMENT::"// — line start or after value"
  §1b::BRACKET_FORMS
    CONTAINER::"[a,b,c] — bare brackets = list"
    ANNOTATION::"NAME<qualifier> — semantic facet on identity (ATHENA<strategic_wisdom>, LLM<exclusively>)"
    ANNOTATION_DISCIPLINE::"Annotations are SHORT qualifiers (1-3 words, ≤32 chars, identifier-only). Multi-word reasoning belongs in a sibling RATIONALE value with quoted prose."
    ANNOTATION_WRONG::"I6<migration_on_moving_target_is_anti_pattern_for_zero_warnings>"
    ANNOTATION_RIGHT::"I6<production_grade_quality> + RATIONALE::\"Migration on moving target is anti-pattern for strict typing during data model changes.\""
    CONSTRUCTOR::"NAME[args] — structured arguments on identifier (REGEX[pattern], ENUM[a,b], JIT_GRAMMAR_COMPILATION[META→GBNF])"
    // These are SEPARATE forms. <> qualifies what something IS. [] parameterizes what something DOES.
    // ATHENA<strategic_wisdom> = annotation (identity facet). ENUM[a,b,c] = constructor (validation args).
    // Lenient parser canonicalizes []→<> ONLY for annotation-context uses. Genuine constructors keep [].
    // When in doubt: identity/archetype qualifier → <>. Parameterized operation/schema → [].
    INLINE_MAP::"[key::val, key2::val2] — dense key-value pairs, values must be atoms, no nesting"
  §1c::LITERAL_ZONES
    // Fenced code blocks pass through with ZERO processing
    SYNTAX::"KEY then newline then fence of 3+ backticks"
    RULES::[
      zero_processing_between_fences,
      tabs_allowed,
      NFC_bypass,
      info_tag_preserved
    ]
    USE_CASES::[
      embedded_code,
      teaching_examples,
      verbatim_content,
      OCTAVE_about_OCTAVE
    ]
    FENCE_SCALING::"use N+1 backticks to wrap content containing N-backtick fences"
§2::OPERATORS
  // Each operator encodes a relationship in a single token
  CONTAINER::"[] — List [a,b,c]"
  CONCAT::"⧺ — Mechanical join A⧺B | ASCII: ~"
  SYNTHESIS::"⊕ — Emergent whole A⊕B | ASCII: +"
  TENSION::"⇌ — Binary opposition A⇌B | ASCII: vs (requires word boundaries)"
  CONSTRAINT::"∧ — Inside brackets only [A∧B∧C] | ASCII: &"
  ALT::"∨ — Alternative A∨B | ASCII: |"
  FLOW::"→ — Right-associative A→B→C, often in lists [A→B→C] | ASCII: ->"
  SECTION_REF::"§ — target anchor e.g. §3c::ASSEMBLY_RULES"
  LINE_COMMENT::"// — line start or after value"
  ASCII_RULE::"All operators accept both unicode and ASCII. Always emit unicode."
  VS_RULE::"vs requires word boundaries: 'A vs B' valid, 'AvsB' invalid"
§3::CRITICAL_RULES
  R1::"No spaces around :: (KEY::value not KEY :: value)"
  R2::"Indent exactly 2 spaces per level — NO TABS"
  R3::"Keys must match [A-Za-z_][A-Za-z0-9_]* — start with letter or underscore"
  R4::"Envelopes: ===NAME=== open, ===END=== close (NAME must be [A-Z_][A-Z0-9_]*)"
  R5::"true, false, null — lowercase only (NOT True, False, NULL)"
  R6::"∧ only inside brackets: [A∧B∧C] valid, bare A∧B invalid"
  R7::"⇌ is binary only: A⇌B valid, chained A⇌B⇌C invalid"
  R8::"Values containing § must be quoted: \"see §3b\" not bare §3b"
  R9::"File extension .oct.md is canonical"
  R10::"Bare numeric keys trigger W_NUMERIC_KEY_DROPPED — use R1, STEP_1, not 1"
  R11::"Unkeyed prose sentences trigger W_BARE_LINE_DROPPED — comments (//) and list body lines are exempt"
  §3b::V6_ENVELOPE_STRUCTURE
    FILE_STRUCTURE::"===NAME=== then META then optional --- separator then BODY then ===END==="
    SEPARATOR::"--- signals metadata boundary to discovery/indexing tools. Place after META block."
    META_REQUIRED::[TYPE,VERSION]
    META_COMMON_OPTIONAL::[
      STATUS,
      UPDATED,
      COMPRESSION_TIER,
      LOSS_PROFILE,
      CONTRACT,
      GRAMMAR
    ]
    // STATUS in META = document lifecycle (ACTIVE, DRAFT). STATUS in BODY = subject state. Both valid.
    COMPRESSION_TIER::ENUM[LOSSLESS,CONSERVATIVE,AGGRESSIVE,ULTRA]
    LOSS_PROFILE::"[preserve:causal_chains,drop:verbose_phrasing] — loss is explicit, never hidden"
    // NOTE: LOSS_PROFILE is spec-valid but not yet in octave-validator allowed_meta — validator gap, not spec error
    CONTRACT::HOLOGRAPHIC<validation_law_in_document>
    GRAMMAR::GBNF_COMPILER<generate_constrained_output>
  §3c::ASSEMBLY_RULES
    RULE::"When concatenating profiles, omit intermediate ===END=== — only final one terminates"
    USE_CASES::[
      agent_context_injection,
      specification_layering,
      multi_part_documents
    ]
  §3d::SECTION_PATH_REFERENCES
    SYNTAX::"§N::NAME — section reference. §3b::V6_ENVELOPE_STRUCTURE is a valid cross-reference."
    QUOTING::"Quote § when used as content value: VALUE::\"see §3b\" not VALUE::§3b"
    NESTING::"§3b inside §3 — subsection. Prefix digit tracks depth."
§4::WARNING_PREVENTION
  // octave_write returns warnings[] — each warning is silent data loss
  W_BARE_LINE_DROPPED::"Cause: line has no key:: prefix. Fix: add a key or use // comment."
  W_NUMERIC_KEY_DROPPED::"Cause: bare integer key (1::thing). Fix: use R1::thing or STEP_1::thing."
  W_CHECK::"After every octave_write call, inspect warnings[]. Today: Empty = clean. Non-empty = data lost. AFTER ADR-0006 SR1-T4: see §6 — empty no longer implies clean."
  // Semantic of warnings[] is changing. See §6::FORTHCOMING_BEHAVIOR for timing markers.
§5::WORKED_EXAMPLE
  // Shows: envelope, META with optional fields, separator, operators, annotation, loss accounting
  EXAMPLE:
    ```
===DECISION===
META:
  TYPE::DECISION
  VERSION::"1.0.0"
  COMPRESSION_TIER::CONSERVATIVE
  LOSS_PROFILE::"[preserve:causal_chains,drop:verbose_phrasing]"
---
STATUS::ACTIVE
CONTEXT::API_redesign[KAIROS<Q2_window>]
DECISION::microservice_extraction[auth⊕payments→independent_services]
PHASES:
  PLAN::[Research→Design]
  BUILD::[Code⊕Test]
METRICS:
  LATENCY::"<200ms p99"
  AVAILABILITY::"99.95%"
===END===
    ```
  // KAIROS<Q2_window> = annotation form. Semantic facet on identifier, not a list.
  // META carries COMPRESSION_TIER and LOSS_PROFILE — loss is auditable.
  // PHASES uses BLOCK because children are nested. STATUS uses ASSIGNMENT because scalar.
§6::FORTHCOMING_BEHAVIOR
  // Per ADR-0006 (Writer/Reader Symmetry Programme). The writer surface is bifurcating.
  // This section is truthful BEFORE and AFTER the milestones land — read the timing markers.
  REF::"octave-mcp:docs/adr/ADR-0006-writer-reader-symmetry.md"
  // ^ path is in the octave-mcp repo (upstream OCTAVE spec authority), not this repo.
  §6a::TIMELINE
    TODAY::"octave_write canonicalises (normalises syntax) on every write. warnings[] enumerates what changed during normalisation. Empty warnings[] ⇒ source was already canonical."
    AFTER_SR1_T4::"Default behaviour becomes NO-OP normalisation. octave_write commits bytes as supplied (subject to schema validation). warnings[] enumerates what would have changed had normalisation been ATTEMPTED. Empty warnings[] ⇒ no normalisation was attempted — NOT a guarantee of canonicality. Sprint 1 milestone."
    AFTER_SR3_T2::"Canonicalisation moves to a separate octave_fmt tool. Use octave_write to PERSIST bytes; use octave_fmt to CANONICALISE on demand. Two distinct calls, two distinct receipts. Sprint 3 milestone."
  §6b::SEMANTIC_SHIFT_OF_EMPTY_WARNINGS
    // The same wire shape (warnings: []) carries different meaning across the timeline.
    TODAY::"warnings:[] ≡ source_already_canonical[no_changes_needed]"
    AFTER_SR1_T4::"warnings:[] ≡ no_normalisation_attempted[canonicality_unknown]"
    IMPLICATION::"Post-SR1-T4, do NOT infer canonicality from absence of warnings. Run octave_fmt (post-SR3-T2) or call octave_validate to check canonicality."
    I4_RECEIPT::"This semantic shift is itself a TRANSFORM_AUDITABILITY event — logged here in skill text rather than absorbed silently into existing wording. PROD::I4."
  §6c::AGENT_GUIDANCE_BY_PHASE
    PHASE_TODAY::[
      "Use octave_write for both persistence AND canonicalisation",
      "Inspect warnings[] to learn what was normalised",
      "Empty warnings[] = clean[input was canonical]"
    ]
    PHASE_AFTER_SR1_T4::[
      "Use octave_write for persistence",
      "Inspect warnings[] to learn what WOULD have been normalised — these are now diagnostics, not data-loss receipts",
      "Empty warnings[] = NOT a canonicality guarantee — call octave_validate or (post-SR3-T2) octave_fmt"
    ]
    PHASE_AFTER_SR3_T2::[
      "octave_write::persistence_only[no_canonicalisation]",
      "octave_fmt::explicit_canonicalisation[on_demand,returns_diff_receipt]",
      "Two-call pattern: write_then_fmt for canonical persistence; write_only for raw persistence"
    ]
  §6d::INVARIANT_RELOCATION_NOT_RELAXATION
    // PROD::I1 (SYNTACTIC_FIDELITY: normalization_alters_syntax_never_semantics) is NOT being weakened.
    // The bifurcation RELOCATES the I1 enforcement locus from octave_write to octave_fmt.
    // octave_fmt remains bound by I1 (idempotent, bijective on semantic space).
    // octave_write becomes a pure persistence path; canonicalisation is opt-in.
    AUTHORS::"Treat octave_write as 'commit bytes' and octave_fmt as 'canonicalise bytes' — they compose, they do not duplicate."
§7::REPAIRLOG_AUDIT_COMPLETENESS
  // ADR-0006 SR1-T1 Step 3 (v1.12.0): RepairLog is the complete I4 record.
  POST_V1_12_0::"RepairLog is the complete I4 (TRANSFORM_AUDITABILITY) record. All TIER_NORMALIZATION events (whitespace, blank-line, identifier dequoting, triple-quote collapse, W002) emit corrections via the central core/grammar/tier_normalize channel."
  EMPTY_LOG_SEMANTICS::"An empty RepairLog means no normalisation was applied. Do not assert empty-log on documents containing trivia normalisation (blank-line stripping, triple-quote collapse) — those now produce corrections."
  CONSUMER_GUIDANCE::[
    "If your test pre-v1.12.0 asserted len(corrections)==0 on a document that strips blank lines or collapses triple-quoted empties, it will now see corrections — this reflects correct I4 behaviour. The prior empty-list was an under-reporting bug.",
    "To detect content normalisation: filter corrections by tier=='NORMALIZATION'.",
    "To detect schema repairs: filter by tier=='REPAIR'."
  ]
===END===
