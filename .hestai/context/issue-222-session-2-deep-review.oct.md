===ISSUE_222_SESSION_2_DEEP_REVIEW===
META:
  TYPE::SESSION_FINDINGS
  ISSUE::222
  SESSION::2
  SESSION_DATE::"2026-02-14"
  SESSION_BRANCH::skills-expert-review
  STATUS::IN_PROGRESS
  PURPOSE::"Skills-expert deep review of 3 agents' skill/pattern sets with MIP analysis"

§1::AGENTS_REVIEWED

IMPLEMENTATION_LEAD::[
  SKILLS::[build-execution, build-philosophy, build-anti-patterns, clarification-gate, constitutional-enforcement],
  PATTERNS::[tdd-discipline, verification-protocols, mip-build]
]

HOLISTIC_ORCHESTRATOR::[
  SKILLS::[prophetic-intelligence, gap-ownership, system-orchestration, constitutional-enforcement, ho-mode, ho-orchestrate, subagent-rules],
  PATTERNS::[mip-orchestration, phase-transition-cleanup]
]

CRITICAL_ENGINEER::[
  SKILLS::[validation-methodology, production-readiness, constitutional-enforcement],
  PATTERNS::[] // NONE LISTED — finding in itself
]

§2::STRUCTURAL_AUDIT

YAML_FRONTMATTER_COMPLIANCE::[
  HAS_YAML::[build-philosophy, build-anti-patterns, ho-mode, ho-orchestrate, subagent-rules],
  MISSING_YAML::[build-execution, clarification-gate, constitutional-enforcement, prophetic-intelligence, gap-ownership, system-orchestration, validation-methodology, production-readiness],
  COMPLIANCE_RATE::"5/13 = 38% — FAILING"
]

ANCHOR_KERNEL_COMPLIANCE::[
  HAS_KERNEL::NONE,
  COMPLIANCE_RATE::"0/13 = 0% — TOTAL FAILURE"
]

SECTION_NAME_CONSISTENCY::[
  PROBLEM::"No two skills use the same §section naming convention",
  EVIDENCE::[
    "build-execution: §1::PHILOSOPHY_DELEGATION, §2::MCP_TOOL_INTEGRATION, §3::TDD_ENFORCEMENT, §4::VERIFICATION_REQUIREMENTS, §5::DELEGATION_NOTES",
    "build-philosophy: §1::SYSTEM_AWARENESS_MANDATE, §2::MINIMAL_INTERVENTION_PRINCIPLE, §3::PHILOSOPHY_FRAMEWORK, §4::DECISION_GATES, §5::PRACTICAL_EXAMPLES, §6::WISDOM",
    "build-anti-patterns: §1-§9 per anti-pattern name, §10::DETECTION_FRAMEWORK, §11::WISDOM",
    "clarification-gate: §1::GATE_TRIGGER, §2::AMBIGUITY_DETECTION, §3::PROTOCOL",
    "constitutional-enforcement: §1::CONSTITUTIONAL_ESSENTIALS, §2::ENFORCEMENT_PROTOCOL, §3::ESCALATION",
    "prophetic-intelligence: §1::CORE_CAPABILITY, §2::EARLY_WARNING_SIGNALS, §3::FAILURE_PATTERNS, §4::OUTPUT_STRUCTURE",
    "gap-ownership: §1::FRAMEWORK, §2::GAP_PATTERNS, §3::VERIFICATION",
    "system-orchestration: §1::CORE_PHILOSOPHY, §2::CONVERGENCE, §3::CAPABILITIES",
    "ho-mode: §1::ACTIVATION, §2::GOVERNANCE, §3::DELEGATION, §4::TRAPS, §5::EMERGENCY, §6::INTEGRATION",
    "ho-orchestrate: §1::ACTIVATION, §2::IL_DELEGATION, §3::QUALITY_GATES, §4::DEBATE_ESCALATION, §5::WORKFLOW",
    "subagent-rules: §1::ROUTING_RULE, §2::TEMPLATE, §3::TIER_SELECTION, §4::EXAMPLES, §5::WHY_OA_ROUTER, §6::ANTI_PATTERNS",
    "validation-methodology: §1::CORE_PROTOCOL, §2::CONSTRAINT_TYPES, §3::HEURISTICS",
    "production-readiness: §1::VALIDATION_FRAMEWORK, §2::DOMAIN_ACCOUNTABILITY, §3::ARTIFACT_REQUIREMENTS"
  ],
  PATTERNS_SECTIONS::[
    "tdd-discipline: §1::CORE_PROTOCOL, §2::GIT_WORKFLOW, §3::ANTI_PATTERNS",
    "verification-protocols: §1::MANDATORY_ARTIFACTS, §2::QUALITY_GATES, §3::ANTI_VALIDATION_THEATER",
    "mip-build: §1::CORE_PRINCIPLE, §2::ENFORCEMENT_FRAMEWORK, §3::DECISION_GATES, §4::RED_FLAGS, §5::EXAMPLE, §6::USED_BY",
    "mip-orchestration: §1::CORE_PRINCIPLE, §2::METRICS, §3::DECISION_FRAMEWORK, §4::USED_BY",
    "phase-transition-cleanup: §1::TRIGGER_POINTS, §2::EXECUTION, §3::REFERENCE"
  ]
]

§3::SIZE_ANALYSIS

// Research finding: 300-700 tokens optimal. ~1.3 tokens/word for OCTAVE.
// So optimal range is ~230-540 words.

SIZING_TABLE::[
  "build-execution: 68 lines, 225 words — UNDERSIZED (mostly delegation pointers)",
  "build-philosophy: 153 lines, 598 words — OPTIMAL (rich, actionable)",
  "build-anti-patterns: 176 lines, 683 words — AT UPPER LIMIT (comprehensive but dense)",
  "clarification-gate: 26 lines, 90 words — SEVERELY UNDERSIZED (too thin to be useful)",
  "constitutional-enforcement: 29 lines, 90 words — SEVERELY UNDERSIZED (too thin to be useful)",
  "prophetic-intelligence: 36 lines, 174 words — UNDERSIZED (aspirational percentages, thin content)",
  "gap-ownership: 27 lines, 86 words — SEVERELY UNDERSIZED (framework sketch, not actionable)",
  "system-orchestration: 22 lines, 82 words — SEVERELY UNDERSIZED (abstract philosophy, not actionable)",
  "ho-mode: 90 lines, 206 words — GOOD SIZE (compressed, actionable, OCTAVE-dense)",
  "ho-orchestrate: 40 lines, 58 words — UNDERSIZED (ultra-compressed, requires ho-mode context)",
  "subagent-rules: 131 lines, 406 words — GOOD (practical templates and examples)",
  "validation-methodology: 34 lines, 126 words — UNDERSIZED (protocol sketch, needs examples)",
  "production-readiness: 35 lines, 85 words — SEVERELY UNDERSIZED (list of concerns, not actionable)"
]

PATTERNS_SIZING::[
  "tdd-discipline: 30 lines, 115 words — GOOD for pattern (concise, actionable)",
  "verification-protocols: 30 lines, 79 words — GOOD for pattern (focused)",
  "mip-build: 48 lines, 183 words — GOOD for pattern (principle + framework + examples)",
  "mip-orchestration: 28 lines, 87 words — GOOD for pattern (focused decision aid)",
  "phase-transition-cleanup: 17 lines, 43 words — THIN (barely a pattern, more a procedure pointer)"
]

§4::MIP_ANALYSIS_PER_SKILL

// For each skill: ESSENTIAL (keeps agent on-mission), ACCUMULATIVE (adds burden without value),
// or MISSING (content the agent needs but doesn't have)

IMPLEMENTATION_LEAD_ASSESSMENT::[
  BUILD_EXECUTION::[
    VERDICT::MERGE_OR_DELETE,
    ESSENTIAL::"MCP tool integration (Context7, Repomix workflow)",
    ACCUMULATIVE::"§1 (pure delegation pointers — 'see build-philosophy'), §3 (duplicates tdd-discipline pattern), §4 (duplicates verification-protocols pattern), §5 (delegation notes are meta-commentary not instruction)",
    REASONING::"This skill is 80% pointers to other skills. The only unique content is §2::MCP_TOOL_INTEGRATION. Either absorb §2 into build-philosophy or delete this skill entirely and let the agent's §3::CAPABILITIES list handle the loading.",
    RECOMMENDATION::"DELETE skill. Move §2::MCP_TOOL_INTEGRATION into build-philosophy as a new section. The rest is delegation overhead."
  ],
  BUILD_PHILOSOPHY::[
    VERDICT::EXEMPLAR_KEEP,
    ESSENTIAL::"§1 system awareness mandate, §2 MIP definition, §3 UNDERSTAND→SHAPE→ACT, §4 decision gates, §5 practical examples",
    ACCUMULATIVE::"§6::WISDOM (3 lines of aphorisms — low value vs context cost)",
    REASONING::"Best skill reviewed. Rich decision frameworks with concrete examples. The ripple map example and with/without comparison are exactly what research says works: 'concrete examples + anti-examples'. Token count is at optimal range.",
    RECOMMENDATION::"KEEP as exemplar. Minor: trim §6 wisdom, absorb MCP_TOOL_INTEGRATION from build-execution. Add YAML frontmatter (already has). Add §ANCHOR_KERNEL."
  ],
  BUILD_ANTI_PATTERNS::[
    VERDICT::KEEP_RESTRUCTURE,
    ESSENTIAL::"All 9 anti-patterns with their SYMPTOMS/DETECT/PREVENT structure",
    ACCUMULATIVE::"§10::DETECTION_FRAMEWORK (duplicates the detect sections), §11::WISDOM (2 lines of aphorisms)",
    REASONING::"Good content but structurally unusual. Uses §1-§9 as individual anti-pattern sections rather than a canonical §-structure. The pattern of SYMPTOMS→EXAMPLE→DETECT→PREVENT is excellent and consistent WITHIN this skill. Detection framework at §10 is a convenient index but duplicates content above.",
    RECOMMENDATION::"KEEP but trim §10 (or keep only as quick-reference index) and §11. Consider whether this should be a PATTERN not a SKILL — it's a decision framework ('how to detect and prevent'), not operational instruction ('what to do')."
  ],
  CLARIFICATION_GATE::[
    VERDICT::MERGE_OR_DELETE,
    ESSENTIAL::"The concept of stopping to clarify ambiguity before implementation",
    ACCUMULATIVE::"The entire skill is 26 lines / 90 words — below minimum viable content. The 5 ambiguity signals are useful but don't warrant a standalone skill.",
    REASONING::"This is a procedure, not a skill. The concept ('ask before you code if unclear') is so fundamental that any competent agent already knows it. The specific signals (priority conflicts, dependency choices, etc.) could be a 3-line checklist in build-philosophy §3::UNDERSTAND.",
    RECOMMENDATION::"DELETE as standalone skill. Absorb the 5 ambiguity signals into build-philosophy §3::UNDERSTAND section as a BEFORE_STARTING checklist."
  ],
  CONSTITUTIONAL_ENFORCEMENT::[
    VERDICT::REWRITE,
    ESSENTIAL::"Phase gate sequence, quality gate sequence, RACI consultation list, blocking authority criteria, escalation criteria",
    ACCUMULATIVE::"Nothing — the skill is too thin, not too bloated. At 29 lines / 90 words it's severely undersized.",
    MISSING::"Examples of enforcement in action. What does 'phase progression with missing essential artifacts' look like concretely? What does the agent DO when it detects a violation? Currently just lists what to block, not HOW to block or what to output.",
    REASONING::"This skill is shared across ALL THREE agents reviewed. It's the most cross-cutting skill in the system. But it's also the least developed — just a skeleton of lists without actionable procedure.",
    RECOMMENDATION::"REWRITE with enforcement procedures, detection examples, and output templates. This is a critical shared skill that deserves 200-400 words of actionable content."
  ]
]

IMPLEMENTATION_LEAD_PATTERNS_ASSESSMENT::[
  TDD_DISCIPLINE::[
    VERDICT::EXEMPLAR_KEEP,
    ESSENTIAL::"All content — RED/GREEN/REFACTOR cycle, git workflow pattern, anti-patterns",
    ACCUMULATIVE::NONE,
    REASONING::"Tight, focused, actionable. 30 lines / 115 words. Perfect pattern size. Has §CORE_PROTOCOL, §GIT_WORKFLOW, §ANTI_PATTERNS — a structure that maps well to the patterns spec recommendation of §1::CORE_PRINCIPLE, §3::DECISION_FRAMEWORK. Anti-patterns section is particularly valuable.",
    RECOMMENDATION::"KEEP as exemplar pattern. Add §ANCHOR_KERNEL (easy to extract — the RED→GREEN→REFACTOR cycle IS the kernel)."
  ],
  VERIFICATION_PROTOCOLS::[
    VERDICT::KEEP,
    ESSENTIAL::"Mandatory artifacts list, quality gate thresholds, anti-validation-theater rejections",
    ACCUMULATIVE::NONE,
    REASONING::"Focused and actionable. The anti-validation-theater section is the most valuable part — it gives concrete examples of what to REJECT ('I ran tests' without output). 30 lines / 79 words.",
    RECOMMENDATION::"KEEP. Add §ANCHOR_KERNEL. Consider adding §USED_BY per patterns spec."
  ],
  MIP_BUILD::[
    VERDICT::KEEP,
    ESSENTIAL::"Core principle, enforcement framework with authority chain, decision gates, red flags",
    ACCUMULATIVE::"§5::EXAMPLE (duplicates the same ripple map example from build-philosophy — pick one location)",
    REASONING::"Good pattern. Has the recommended sections from the spec (§1::CORE_PRINCIPLE, §6::USED_BY). The authority chain (implementation-lead→code-review-specialist→critical-engineer) is uniquely valuable here. 48 lines / 183 words.",
    RECOMMENDATION::"KEEP. Remove duplicate example (keep in build-philosophy where it has more context). Add §ANCHOR_KERNEL."
  ]
]

HOLISTIC_ORCHESTRATOR_ASSESSMENT::[
  PROPHETIC_INTELLIGENCE::[
    VERDICT::REWRITE,
    ESSENTIAL::"The 5 failure patterns (assumption cascades, scale brittleness, phase transition blindness, integration debt, Conway's revenge) — these are genuinely useful mental models",
    ACCUMULATIVE::"§1::CORE_CAPABILITY with accuracy percentages ('80%+ historical accuracy') — unverifiable claims that add no behavioral value. The percentages per pattern (85.2%, 80.0%, 90.0%, etc.) are fiction — there is no rolling 6-month accuracy measurement system in place.",
    MISSING::"What does the HO actually DO with a prophecy? The output structure (§4) is template-level but there's no procedure for scanning, triggering, or acting on predictions.",
    REASONING::"Session 1 finding confirmed: 'Contains accuracy percentages that can't be verified.' The failure patterns ARE valuable (they encode real architectural wisdom). But the quantitative dressing is aspiration presented as measurement.",
    RECOMMENDATION::"REWRITE. Strip all percentages. Keep the 5 failure patterns as a decision framework. Add procedure: When to scan, what triggers a prophecy, what to do with it. This might be better as a PATTERN (decision framework) than a SKILL."
  ],
  GAP_OWNERSHIP::[
    VERDICT::MERGE_INTO_SYSTEM_ORCHESTRATION,
    ESSENTIAL::"Default ownership concept, retained accountability principle, the 5 gap patterns",
    ACCUMULATIVE::"The entire skill is a 27-line framework sketch. No actionable procedures.",
    MISSING::"How to identify a gap. How to assign ownership. How to track closure. What 'verify coherence' means in practice.",
    REASONING::"Gap ownership is a CONCEPT that the HO needs, not a standalone SKILL. The 5 gap patterns overlap heavily with prophetic-intelligence's failure patterns. Both describe boundary failures from different angles.",
    RECOMMENDATION::"MERGE into system-orchestration as a §section, or merge with prophetic-intelligence into a single 'system health' skill. Currently too thin to justify context window cost as standalone."
  ],
  SYSTEM_ORCHESTRATION::[
    VERDICT::REWRITE,
    ESSENTIAL::"The 6-step constitutional progression (PERCEIVE→SYNTHESIZE→VALIDATE→ORCHESTRATE→SYNTHESIZE→ENFORCE). The convergence point concept.",
    ACCUMULATIVE::"§3::CAPABILITIES is a list of capabilities without procedures — 'parallel_quest_architecture' is a label, not an instruction.",
    MISSING::"This is the HO's CORE SKILL and it's the most underdeveloped at 22 lines / 82 words. No procedures, no examples, no decision framework.",
    REASONING::"The HO's most important operational skill is a skeleton. ho-mode (90 lines, actionable) and ho-orchestrate (40 lines, compressed but procedural) contain the ACTUAL orchestration instructions. system-orchestration is the philosophical foundation that those two reference, but it's too abstract to be useful on its own.",
    RECOMMENDATION::"REWRITE significantly. Absorb gap-ownership concepts. Add concrete procedures for each step of the constitutional progression. Target 300-400 words with real examples. OR merge into ho-mode which already has the operational procedures."
  ],
  HO_MODE::[
    VERDICT::EXEMPLAR_KEEP,
    ESSENTIAL::"§2::GOVERNANCE (DIRECT_WRITE vs MUST_DELEGATE matrix), §3::DELEGATION (handoff template), §4::TRAPS (diagnosis→impl momentum etc.), §5::EMERGENCY protocol",
    ACCUMULATIVE::"§6::WISDOM (3 aphorisms — marginal value). §1::ACTIVATION (trigger list — operational but could be YAML frontmatter trigger field instead).",
    REASONING::"This is the best HO skill. Concrete file-path globs for what the HO can/cannot edit. Specific delegation matrix. Named traps with explanations. Emergency override protocol. This is what 'actionable skill' looks like — an LLM reading this WILL behave differently.",
    RECOMMENDATION::"KEEP as exemplar. Trim §6 wisdom. Already has YAML frontmatter and allowed-tools. Add §ANCHOR_KERNEL (extract governance matrix + trap names)."
  ],
  HO_ORCHESTRATE::[
    VERDICT::KEEP,
    ESSENTIAL::"§2 IL delegation pattern, §3 quality gate chain with tiers, §4 debate escalation triggers",
    ACCUMULATIVE::"At 40 lines / 58 words this is ultra-compressed. EXTENDS::ho-mode is correct — this builds on ho-mode.",
    REASONING::"Good companion to ho-mode. Adds the multi-model orchestration layer (CRS→CE chain, debate-hall escalation). Very compressed but each line carries instruction.",
    RECOMMENDATION::"KEEP. Consider slight expansion of §3 quality gate tiers with examples. Already has YAML frontmatter."
  ],
  SUBAGENT_RULES::[
    VERDICT::KEEP_RESTRUCTURE,
    ESSENTIAL::"§1 routing rule, §2 template, §4 examples, §6 anti-patterns",
    ACCUMULATIVE::"§5::WHY_OA_ROUTER (26 lines explaining history — useful for understanding but not for execution. Could be a comment block instead of a section.)",
    REASONING::"This skill uses MARKDOWN (# headers, | tables |, ``` code blocks) inside what should be an OCTAVE body. It violates the skill spec's 'No markdown headers' rule. Content is good — practical templates and examples. But format needs alignment.",
    RECOMMENDATION::"RESTRUCTURE to pure OCTAVE format. Keep §1-§4 and §6. Compress §5 to a 2-line NOTE::. Already has YAML frontmatter."
  ],
  MIP_ORCHESTRATION_PATTERN::[
    VERDICT::KEEP,
    ESSENTIAL::"Core principle (essential vs accumulative orchestration), 62/38 target metric, decision framework questions",
    ACCUMULATIVE::NONE,
    REASONING::"Good pattern. Focused, 28 lines, has §USED_BY. The 62/38 metric gives the HO a concrete target.",
    RECOMMENDATION::"KEEP. Add §ANCHOR_KERNEL."
  ],
  PHASE_TRANSITION_CLEANUP_PATTERN::[
    VERDICT::REWRITE_OR_DELETE,
    ESSENTIAL::"Trigger points (B1_02, B2_04, etc.)",
    ACCUMULATIVE::"At 17 lines / 43 words, this is barely a pattern. It's a single procedure step: 'invoke directory-curator → receive report → delegate → validate'. That's not a decision framework.",
    REASONING::"Session 1 identified this as a failed extraction (22% kernel extraction failure rate). It references 'visibility-rules.oct.md' and 'workspace-architect' — neither of which are actionable in the pattern itself. This is more of a CI pipeline step than a decision framework.",
    RECOMMENDATION::"DELETE as pattern. If the procedure is important, embed it as a trigger in the HO's agent §2::BEHAVIOR section or as a line in constitutional-enforcement."
  ]
]

CRITICAL_ENGINEER_ASSESSMENT::[
  VALIDATION_METHODOLOGY::[
    VERDICT::REWRITE,
    ESSENTIAL::"The 6-step validation protocol (natural law → resources → capability → timeline → evidence → verdict). The constraint classification (HARD/SOFT/FANTASY).",
    ACCUMULATIVE::"§3 heuristics are sensible but generic ('physics constraints = always HARD'). The LLM acceleration factor (10-20x) is a specific, useful heuristic.",
    MISSING::"At 34 lines / 126 words, this needs examples. What does 'Step 1: Natural Law' look like for a software system? The 6 steps are labels, not procedures.",
    RECOMMENDATION::"REWRITE with concrete examples for each step. Add an example validation walkthrough. Target 250-350 words."
  ],
  PRODUCTION_READINESS::[
    VERDICT::REWRITE,
    ESSENTIAL::"The 5 critical lenses (WILL_IT_BREAK × WILL_IT_SCALE × WHO_MAINTAINS × WHAT_ATTACKS × WHY_COMPLEX). The 12 domain accountability list. The mandatory evidence mapping.",
    ACCUMULATIVE::NONE,
    MISSING::"Procedures. The 5 lenses are a checklist, not a methodology. How does the CE apply each lens? What does a GO vs BLOCKED assessment look like?",
    REASONING::"The CE agent's §2::BEHAVIOR mandates 'Start response with VERDICT: [GO|BLOCKED|CONDITIONAL]'. But this skill doesn't show how to arrive at that verdict. It lists concerns without decision procedures.",
    RECOMMENDATION::"REWRITE. Add verdict decision tree: which lens findings → BLOCKED vs CONDITIONAL vs GO. Add example assessments. Target 300-400 words."
  ],
  CONSTITUTIONAL_ENFORCEMENT::[
    VERDICT::"See implementation-lead assessment above — same skill, same issues"
  ],
  MISSING_PATTERNS::[
    FINDING::"The critical-engineer has NO patterns in §3::CAPABILITIES. This is a gap.",
    EVIDENCE::"The CE's mode is VALIDATION (agent §2::CONDUCT::MODE). Every validation assessment is a decision framework application. verification-protocols pattern would be a natural fit. The CE should reference patterns that encode its decision methodology.",
    RECOMMENDATION::"Add verification-protocols to CE §3::CAPABILITIES::PATTERNS. Consider creating a 'constraint-classification' pattern (HARD/SOFT/FANTASY framework from validation-methodology)."
  ]
]

§5::CROSS_CUTTING_FINDINGS

SHARED_SKILL_ANALYSIS::[
  CONSTITUTIONAL_ENFORCEMENT::[
    SHARED_BY::[implementation-lead, holistic-orchestrator, critical-engineer],
    FINDING::"Most cross-cutting skill in the system is also the least developed (29 lines / 90 words). If this skill matters enough to load for ALL THREE agents, it deserves proportional investment.",
    PRIORITY::HIGH
  ]
]

SKILL_VS_PATTERN_TAXONOMY::[
  FINDING::"Several skills should be patterns (decision frameworks, not operational instructions)",
  CANDIDATES_FOR_RECLASSIFICATION::[
    "prophetic-intelligence → pattern (failure pattern recognition framework)",
    "gap-ownership → merge into system-orchestration skill OR reclassify as pattern",
    "build-anti-patterns → could be pattern (detection/prevention framework)"
  ],
  DISTINCTION_RULE::"If it tells the agent HOW TO DECIDE → pattern. If it tells the agent WHAT TO DO → skill."
]

FORMAT_CONSISTENCY::[
  YAML_COMPLIANCE::"38% — 8 of 13 skills missing frontmatter",
  ANCHOR_KERNEL::"0% — no skill has a §ANCHOR_KERNEL",
  MARKDOWN_IN_OCTAVE::"subagent-rules uses markdown (#, |tables|, ```code```) inside OCTAVE body — spec violation",
  SECTION_NAMING::"Zero consistency across skills. 13 skills use 13 different naming conventions."
]

§6::CANONICAL_SECTION_STRUCTURE_PROPOSAL

// Based on what WORKS across the best skills (ho-mode, build-philosophy, tdd-discipline)
// and the patterns spec (§1::CORE_PRINCIPLE, §2::METRICS, §3::DECISION_FRAMEWORK, §4::USED_BY)

SKILLS_CANONICAL_STRUCTURE::[
  YAML_FRONTMATTER::"REQUIRED — name, description (with 'Use when' trigger), allowed-tools, triggers, version",
  OCTAVE_ENVELOPE::"===SKILL_NAME=== ... ===END===",
  META::"TYPE::SKILL, VERSION, STATUS, PURPOSE",
  §1::CORE::"What this skill IS. The core principle, definition, or mission in 2-5 lines. NOT a delegation pointer. NOT a philosophy essay.",
  §2::PROTOCOL::"What the agent DOES. Step-by-step procedures, decision trees, or execution sequences. The actionable heart.",
  §3::GOVERNANCE::"Boundaries. MUST_ALWAYS / MUST_NEVER / BLOCKED / ALLOWED constraints. File globs, tool restrictions, escalation paths.",
  §4::EXAMPLES::"1-2 concrete examples + 1 anti-example. OPTIONAL for small skills but REQUIRED for complex ones.",
  §ANCHOR_KERNEL::"Auto-extractable summary for anchor injection. TARGET + NEVER + MUST + GATE format per patterns spec."
]

RATIONALE::[
  §1_CORE::"From build-philosophy §1::SYSTEM_AWARENESS_MANDATE and ho-mode LANE_DISCIPLINE — the best skills open with a crisp identity statement",
  §2_PROTOCOL::"From ho-mode §2::GOVERNANCE and §3::DELEGATION — the best skills have PROCEDURES not just principles",
  §3_GOVERNANCE::"From ho-mode §2 (DIRECT_WRITE/MUST_DELEGATE) and constitutional-enforcement (blocking authority) — constraints need explicit boundaries",
  §4_EXAMPLES::"From build-philosophy §5 and subagent-rules §4 — research confirms examples + anti-examples improve compliance 15-35%",
  §ANCHOR_KERNEL::"From patterns spec §3 and session 1 finding that kernel extraction fails 22% with regex"
]

WHY_NOT_MORE_SECTIONS::[
  "Session 1 research: 300-700 tokens optimal. 4 body sections + kernel ≈ 350-500 tokens at healthy density.",
  "build-anti-patterns works with 9 sections because each section IS a use case — the §numbers are items not categories",
  "Adding §5::WISDOM, §6::INTEGRATION, §7::REFERENCES adds context cost without behavioral benefit",
  "Catalog-style skills (anti-patterns, failure-patterns) can use §1-§N per item structure instead"
]

PATTERNS_CANONICAL_STRUCTURE::[
  NO_YAML::"Patterns spec explicitly forbids YAML frontmatter",
  §1::CORE_PRINCIPLE::"What the pattern optimizes for AND prevents",
  §2::DECISION_FRAMEWORK::"Questions/checks the agent applies (BEFORE_X gates)",
  §3::ANTI_PATTERNS::"What violating this pattern looks like (concrete examples)",
  §ANCHOR_KERNEL::"TARGET + NEVER + MUST + GATE (REQUIRED per spec)"
]

§7::SKILL_DISPOSITION_MATRIX

// KEEP = good as-is with minor tweaks
// REWRITE = right concept, wrong execution
// MERGE = absorb into another skill
// DELETE = provides no unique behavioral value
// RECLASSIFY = should be a different artifact type

IMPLEMENTATION_LEAD::[
  "build-execution → DELETE (merge §2 into build-philosophy)",
  "build-philosophy → KEEP (exemplar — add §ANCHOR_KERNEL, absorb MCP integration)",
  "build-anti-patterns → KEEP (restructure — consider pattern reclassification)",
  "clarification-gate → DELETE (merge 5 signals into build-philosophy §2::PROTOCOL as BEFORE_STARTING checklist)",
  "constitutional-enforcement → REWRITE (shared skill, critically underdeveloped)",
  "tdd-discipline → KEEP (exemplar pattern — add §ANCHOR_KERNEL)",
  "verification-protocols → KEEP (add §ANCHOR_KERNEL, §USED_BY)",
  "mip-build → KEEP (remove duplicate example, add §ANCHOR_KERNEL)"
]

HOLISTIC_ORCHESTRATOR::[
  "prophetic-intelligence → REWRITE (strip fake percentages, add procedures, consider pattern reclassification)",
  "gap-ownership → MERGE into system-orchestration",
  "system-orchestration → REWRITE (absorb gap-ownership, add procedures, currently skeleton)",
  "constitutional-enforcement → REWRITE (same as above)",
  "ho-mode → KEEP (exemplar — add §ANCHOR_KERNEL, trim §6 wisdom)",
  "ho-orchestrate → KEEP (slight expansion of §3 gate tiers)",
  "subagent-rules → KEEP (restructure from markdown to OCTAVE, compress §5)",
  "mip-orchestration → KEEP (add §ANCHOR_KERNEL)",
  "phase-transition-cleanup → DELETE (embed as trigger in agent §2 or constitutional-enforcement)"
]

CRITICAL_ENGINEER::[
  "validation-methodology → REWRITE (add examples for each step, expand from skeleton)",
  "production-readiness → REWRITE (add verdict decision tree, example assessments)",
  "constitutional-enforcement → REWRITE (same as above)",
  "MISSING: Add verification-protocols to §3::CAPABILITIES::PATTERNS"
]

SUMMARY_COUNTS::[
  KEEP::8,
  REWRITE::5,
  MERGE::2,
  DELETE::3,
  TOTAL_UNIQUE::18
]

§8::EXEMPLAR_CANDIDATES

BEST_CURRENT_SKILLS::[
  "ho-mode: Best operational skill. Concrete governance matrix, named traps, delegation template.",
  "build-philosophy: Best knowledge skill. Rich framework with decision gates and real examples.",
  "tdd-discipline: Best pattern. Tight, focused, actionable protocol with anti-patterns."
]

EXEMPLARS_TO_CREATE::[
  "constitutional-enforcement: REWRITE to canonical structure — most cross-cutting, currently worst quality",
  "validation-methodology: REWRITE to canonical structure — represents CE domain, currently skeleton",
  "tdd-discipline: ADD §ANCHOR_KERNEL to demonstrate kernel authoring pattern"
]

§9::RESEARCH_CROSS_REFERENCES

// Cross-referenced against .hestai/research/skills-deep-research-report.oct.md (v2.0.0)
// Research covers: Claude Code, MCP, Claude API, LangChain, CrewAI, AutoGen

CONFIRMED_BY_RESEARCH::[
  SIZING::[
    OUR_FINDING::"300-700 tokens optimal (§3::SIZE_ANALYSIS)",
    RESEARCH::"§5::OPTIMAL_SKILL_TEMPLATE: 'body 300-700 tokens; bulk reference→separate files on demand'",
    VALIDATION::"Direct match. Our severely undersized skills (clarification-gate: 90 words, gap-ownership: 86 words) are well below minimum even at OCTAVE's ~1.3 tokens/word."
  ],
  SECTION_STRUCTURE::[
    OUR_FINDING::"§1::CORE, §2::PROTOCOL, §3::GOVERNANCE, §4::EXAMPLES (§6::CANONICAL_SECTION_STRUCTURE_PROPOSAL)",
    RESEARCH::"§5: 'section headers: Objective, Inputs, Procedure, Invariants, Output'",
    VALIDATION::"Close mapping. §1::CORE≈Objective, §2::PROTOCOL≈Procedure, §3::GOVERNANCE≈Invariants, §4::EXAMPLES≈Inputs/Output examples."
  ],
  CONSTRAINTS_EARLY::[
    OUR_FINDING::"§3::GOVERNANCE contains MUST/NEVER boundaries",
    RESEARCH::"§5: 'declarative constraints EARLY, before procedures' and 'do/dont constraints before procedures'",
    REFINEMENT::"Research suggests constraints BEFORE procedures. Consider: §1::CORE+constraints → §2::PROTOCOL → §3::EXAMPLES. Or keep 4 sections but front-load MUST_NEVER into §1::CORE."
  ],
  EXAMPLES_DENSITY::[
    OUR_FINDING::"§4::EXAMPLES — 1-2 examples + 1 anti-example",
    RESEARCH::"§5: '1-2 canonical ⊕ 1 anti-example; 1 example per 200 tokens of abstraction'",
    VALIDATION::"Exact match. Research adds density rule: 1 example per 200 tokens of abstraction."
  ],
  OCTAVE_BODY_VALUE::[
    OUR_FINDING::"Session 1: 'OCTAVE body IS the value — the LLM is the parser'",
    RESEARCH::"§4: 'Use structure your runtime can consume programmatically. Everything else is noise.'",
    VALIDATION::"OCTAVE KEY::VALUE syntax IS programmatic structure for the LLM. Strongest validation."
  ]
]

NEW_INSIGHTS_FROM_RESEARCH::[
  DESCRIPTION_IS_RETRIEVAL_ONLY::[
    RESEARCH::"§0: 'Descriptions are retrieval hints, NOT enforceable constraints'",
    IMPACT::"YAML description is for discovery routing only. Behavioral enforcement lives in the OCTAVE body. Our focus on body content quality (§4::MIP_ANALYSIS) is correct.",
    SPEC_IMPLICATION::"octave-skills-spec should explicitly state this."
  ],
  DUAL_RETRIEVAL_LAYERS::[
    RESEARCH::"§1: 'hybrid: BM25 over name+description, embeddings over body'",
    IMPACT::"Two retrieval paths: name+description→lexical matching, body→semantic matching. Names need domain terms. Descriptions need task verbs + triggers. Body matters for semantic retrieval beyond direct instruction."
  ],
  ENFORCEMENT_REDUCES_OVERHEAD::[
    RESEARCH::"§2c: 'Enforcement improves performance by reducing retries, NOT through local parsing cost'",
    IMPACT::"Inverts 'governance adds overhead' objection. Well-structured skills REDUCE total cost by preventing retry loops. Aligns with empirical evidence (3x agent turns without skills, 70% unnecessary work)."
  ],
  PER_DECISION_TOOL_COUNT::[
    RESEARCH::"§6c: 'per-decision toolsets small (single-digit to low tens)' and §7a: 'Opus4: 49%→74% with tool search'",
    IMPACT::"Validates agent §3::CAPABILITIES model: 3-7 skills per agent. Anchor JIT loading empirically supported. Selective loading: 49%→74% accuracy."
  ],
  EXAMPLE_DENSITY_RULE::[
    RESEARCH::"§5: '1 example per 200 tokens of abstraction'",
    IMPACT::"New authoring heuristic. 400-token body→2 examples. build-philosophy (780 tokens)→should have 3-4, has 2.",
    MISSING_FROM_SPEC::"octave-skills-spec should include this heuristic."
  ]
]

SPEC_CHANGE_IMPLICATIONS::[
  OCTAVE_SKILLS_SPEC::[
    "Add: descriptions are retrieval hints, not behavioral constraints (research §0)",
    "Add: example density heuristic — 1 example per 200 tokens of abstraction (research §5)",
    "Add: recommended canonical §section names for skill bodies (§1::CORE, §2::PROTOCOL, §3::GOVERNANCE, §4::EXAMPLES)",
    "Clarify: constraints should appear EARLY in skill body, before procedures (research §5)"
  ],
  OCTAVE_AGENTS_SPEC::[
    "Clarify: relationship between v6 4-section hub format and expanded user-level format from agent-creation skill",
    "Consider: should agents spec document canonical skill §section naming recommendations?"
  ]
]

§10::SKILLS_EXPERT_AGENT_REWRITE

OLD_AGENT::[
  LOCATION::"/Users/shaunbuswell/.claude/agents/skills-expert.oct.md",
  SIZE::"385 lines",
  FORMAT::"Pre-v6 (8 custom sections + markdown headers in body)",
  ISSUES::[duplicate_META, markdown_in_OCTAVE, missing_§3_CAPABILITIES, missing_§4_INTERACTION_RULES, domain_knowledge_in_agent_identity, Claude_Code_only_scope]
]

NEW_AGENT::[
  LOCATION::"src/hestai_mcp/_bundled_hub/library/agents/skills-expert.oct.md",
  SIZE::"104 lines",
  FORMAT::"v6.0.0 dual-lock schema",
  ARCHETYPE::[ARGUS{spec_compliance_vigilance}, THEMIS{standards_enforcement}, ATHENA{discovery_optimization}],
  NOTE::"PHAEDRUS initially used but not in canonical set. Issue: odyssean-anchor-mcp#102 to open archetype set."
]

===END===
