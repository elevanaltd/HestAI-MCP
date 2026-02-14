===ISSUE_222_SESSION_1_FINDINGS===
META:
  TYPE::SESSION_FINDINGS
  ISSUE::222
  SESSION_DATE::"2026-02-14"
  SESSION_BRANCH::issue-222---skills
  STATUS::HANDOFF_TO_SESSION_2
  PURPOSE::"Extracted knowledge from HO review session for skills-expert continuation"

§1::SETTLED_DECISIONS

OCTAVE_SYNTAX_STAYS::[
  DECISION::"Retain :: delimiter across ecosystem",
  EVIDENCE::"Deep research confirms 'models follow ANY consistent delimiter equally well once established'. OCTAVE :: is consistent across ALL agents/skills/patterns/governance. Ecosystem consistency > marginal pretraining prior of colon-space.",
  DEBATE_IDS::["2026-02-13-skills-format-v2-standard", "2026-02-13-skills-format-v2-premium"]
]

OCTAVE_BODY_IS_VALUE::[
  DECISION::"Full OCTAVE body content IS what makes skills actionable for LLMs. Not just the kernel.",
  EVIDENCE::"HO consumed 7 skills + 2 patterns in full OCTAVE during anchor ceremony. KEY::VALUE with [list] syntax gave unambiguous constraints. build-philosophy §4::DECISION_GATES, tdd-discipline §3::ANTI_PATTERNS — these are instruction sets, not documentation.",
  COUNTER::"Previous debates (round 1) wrongly concluded 'body is plain text nobody parses'. The LLM IS the parser."
]

SPECS_ARE_CORRECT::[
  DECISION::"Skills v7 spec (YAML + OCTAVE + §ANCHOR_KERNEL) and Patterns v1 spec (OCTAVE-only + §ANCHOR_KERNEL) are structurally correct",
  CAVEAT::"The content within skills following these specs is NOT consistently good — that's the real problem"
]

ACTIVE_SKILLS_IN_AGENT::[
  DECISION::"Active/background distinction belongs in AGENT §3::CAPABILITIES, not in skill file",
  REASONING::"A skill doesn't know if it's active — depends on who loads it. ho-mode is active for HO but background for critical-engineer",
  FORMAT::"ACTIVE_SKILLS::[ho-mode, ho-orchestrate] in agent §3::CAPABILITIES",
  MAX_ACTIVE::"1-3 active skills. More than that = too much full body in context"
]

§2::ANCHOR_LOADING_REALITY

WHAT_ACTUALLY_HAPPENS::[
  STEP_1::"anchor_commit loads full file via load_skill_content()",
  STEP_2::"Calls extract_skill_kernel() which cascades: §ANCHOR_KERNEL → §2::BEHAVIOR → §2::{CUSTOM} → SIGNALS/PATTERNS → WARN::UNSTRUCTURED",
  STEP_3::"Returns EXTRACTED KERNELS in skill_contents, NOT full bodies",
  STEP_4::"Agent also Read()s full files during FLUKES stage (ceremony instruction)"
]

KERNEL_EXTRACTION_QUALITY::[
  TOTAL_LOADED::9,
  SUCCESSFUL_EXTRACTION::7,
  FAILED_EXTRACTION::2,
  FAILURE_RATE::"22% (subagent-rules, phase-transition-cleanup)",
  ROOT_CAUSE::"Cascading heuristics miss content in non-standard §section names",
  IMPLICATION::"Either §ANCHOR_KERNEL must be authored/auto-generated, or extraction must be smarter (LLM-based)"
]

HO_CAPABILITY_USAGE::[
  HEAVILY_USED::"ho-mode (lane discipline), subagent-rules (delegation template) — needed FULL BODY",
  MODERATELY_USED::"ho-orchestrate (quality gates), system-orchestration (coordination flow) — borderline",
  LIGHTLY_USED::"constitutional-enforcement, prophetic-intelligence, gap-ownership, mip-orchestration — KERNEL would suffice",
  UNUSED::"phase-transition-cleanup — not relevant to this task",
  CONCLUSION::"2 needed full body, 2 borderline, 5 fine with kernels"
]

§3::UNSOLVED_PROBLEMS

CONTENT_QUALITY::[
  PROBLEM::"52 skills have wildly inconsistent content quality, §section naming, structure, and density",
  EVIDENCE::"build-execution §1::PHILOSOPHY_DELEGATION vs testing §1::TEST_MARKERS vs prophetic-intelligence §1::CORE_CAPABILITY — no two skills use the same section names",
  CONWAYS_LAW::"Reformatting bad content into consistently-formatted bad content is still bad. A one-time converter script doesn't fix content quality.",
  APPROACH::"Deep dive into 2-3 agents' skill sets, apply MIP to content, establish the pattern, THEN scale"
]

CANONICAL_SECTION_STRUCTURE::[
  PROBLEM::"No standard §section names exist. Every skill invents its own.",
  NEEDED::"Agreement on canonical sections that all skills should follow",
  CANDIDATES_FROM_DEBATES::"§1::ESSENCE, §2::BEHAVIOR, §3::INTERACTION — but needs validation against real skills"
]

SKILLS_PATTERNS_TAXONOMY::[
  PROBLEM::"Some agents list patterns under SKILLS in §3::CAPABILITIES",
  PROBLEM::"mip-build (pattern) and build-philosophy (skill) cover same domain — is that intentional duplication or taxonomy confusion?",
  PROBLEM::"~20 skills referenced by agents don't exist, ~13 skills exist unreferenced"
]

§4::DEEP_RESEARCH_FINDINGS

// Deep research ran successfully 2026-02-13. Key findings preserved here since /tmp files are gone.

STRUCTURE_VS_PROSE::[
  FINDING::"Structured prompts outperform prose by +3-15pp on tool selection accuracy",
  FINDING::"Numbered constraints with short imperatives reduce violations by ~15-35% (relative)",
  FINDING::"JSON-like key:value + enumerated constraints = measurable improvement",
  IMPLICATION::"OCTAVE's KEY::VALUE with [list] syntax IS this pattern with different delimiters"
]

TOKEN_EFFICIENCY::[
  FINDING::"300-700 tokens per skill body is optimal range",
  FINDING::"'Compress semantics, not meaning' — short labels + IDs + enums over verbose prose",
  FINDING::"Headers + bullets, not paragraphs — OCTAVE §SECTIONS with KEY::VALUE IS this",
  FINDING::"Over-structured prompts that bloat tokens IMPAIR performance"
]

MULTI_SKILL_LOADING::[
  FINDING::"Limit in-context tools/skills to 3-7 via retrieval",
  FINDING::"Capability indexing + router selects minimal active set per turn",
  FINDING::"Namespace skills, avoid synonym collisions across skills"
]

CUSTOM_DSL_QUESTION::[
  FINDING::"'Be cautious with custom DSLs unless you control fine-tuning'",
  COUNTER::"OCTAVE is used across ENTIRE ecosystem. By the time skills load, LLM has been 'fine-tuned in-context' on OCTAVE from constitution, North Star, agent files. Ecosystem consistency argument is decisive."
]

SKILL_TEMPLATE_BEST_PRACTICE::[
  FINDING::"Section headers matching planner needs: Objective, Inputs, Procedure, Invariants, Output",
  FINDING::"Declarative constraints EARLY in file",
  FINDING::"1-2 canonical examples + 1 anti-example",
  FINDING::"5-8 procedure steps mapped to specific tools",
  FINDING::"Do/Don't constraints before procedures",
  FINDING::"Single source of truth for tools; don't mention tools not in allowed-tools"
]

§5::DEBATE_SYNTHESIS_SUMMARY

ROUND_1_STANDARD::"2026-02-13-skills-format-strategy — FLAWED: Wrongly concluded OCTAVE body has no value. Proposed v8 with markdown body. Rejected."
ROUND_1_PREMIUM::"2026-02-13-skills-format-premium — FLAWED: Same false premise. 'Embedded Kernel' architecture. Rejected."
ROUND_2_STANDARD::"2026-02-13-skills-format-v2-standard — CORRECTED: 'Librarian Compiler' pattern. Specs are correct, tooling needed for compliance."
ROUND_2_PREMIUM::"2026-02-13-skills-format-v2-premium — CORRECTED: AI-Driven Librarian + Elastic Context Loading. '§ANCHOR_KERNEL is a compile-time artifact, not a source-time requirement.'"

KEY_DEBATE_INSIGHT::"'Density and Discovery are compiled properties, not authored properties' — but this only applies to HEADERS and KERNELS. The BODY content itself must be authored well."

§6::NEXT_SESSION_APPROACH

RECOMMENDED_APPROACH::[
  1::"Pick 2-3 agents with representative skill sets (e.g., implementation-lead, holistic-orchestrator, critical-engineer)",
  2::"For each agent, read ALL their skills and patterns in full",
  3::"Apply MIP to each skill: What's essential? What's accumulative? What's missing?",
  4::"Identify the canonical §section pattern that emerges from good skills",
  5::"Refactor 2-3 skills as exemplars",
  6::"Use exemplars as the template for all others"
]

GOOD_EXAMPLE_SKILLS::[
  "ho-mode: Well-structured coordination skill with clear MUST_DELEGATE/DIRECT_WRITE",
  "build-philosophy: Rich decision framework with practical examples",
  "tdd-discipline: Clean pattern — tight, focused, actionable",
  "mip-build: Good pattern with enforcement framework and decision gates"
]

QUESTIONABLE_SKILLS::[
  "build-execution: Pure delegation — does it need to exist as a separate skill?",
  "prophetic-intelligence: Contains accuracy percentages that can't be verified",
  "stub-detection: 255 lines — probably too long, could be a pattern + resource"
]

§7::TOOL_DECISIONS

SKILL_CREATOR_TOOL::[
  DECISION::"Not overengineering — but a new MCP tool is premature",
  REASONING::"skill-developer skill already exists. Combined with octave_write, it can produce consistent output",
  PREFERRED_PATH::"Enhance skill-developer skill + use octave_write for new skills",
  CONVERTER::"One-time converter script is wrong (Conway's Law). Human+AI review per skill is right."
]

LIBRARIAN_COMPILER::[
  DECISION::"Valuable for YAML frontmatter and §ANCHOR_KERNEL auto-generation",
  MECHANISM::"LLM-based extraction, NOT regex (proven: regex cascade has 22% failure rate)",
  TIMING::"After content quality is fixed, not before"
]

===END===
