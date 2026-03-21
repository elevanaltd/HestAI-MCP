===SKILL:AGENT_INTERVIEW===
META:
  TYPE::SKILL
  VERSION::"1.1.0"
  STATUS::ACTIVE
  PURPOSE::"Structured interview protocol for agent identity assessment. Extracts behavioral evidence for v8.1 agent file authoring with chassis-profile mapping."

§1::CORE
MISSION::"Extract the behavioral truth of an agent's identity, authority, and operational modes through structured questioning"
AUTHORITY::"Any agent loading this skill can conduct agent interviews"
OUTPUT::"Structured assessment document suitable for agent-expert authoring pass"

§2::PROTOCOL
INTERVIEW_SEQUENCE::[
  // §1::IDENTITY questions
  Q01::"What is your primary role in one sentence?[validates::MISSION]",
  Q02::"What do you actually DO vs what your file says you do? Have you ever been invoked for real work in this system? If so, give an example. If not, say so.[validates::behavioral_fidelity]",
  Q03::"When should someone call you vs another agent? Give a concrete example.[validates::boundary_clarity]",
  Q04::"What can you BLOCK? What can you only advise on? Give examples.[validates::AUTHORITY]",
  // §2::OPERATIONAL_BEHAVIOR questions
  Q05::"Walk me through how you handle a typical task start to finish.[extracts::PROTOCOL]",
  Q06::"What should you NEVER do? Give a concrete example of when you almost did it.[validates::MUST_NEVER]",
  Q07::"Who do you hand off to, and when? What does a good handoff look like?[extracts::INTEGRATION]",
  // §3::CAPABILITIES questions
  Q08::"Which skills do you need EVERY time, regardless of context, and why?[maps::CHASSIS]",
  Q09::"Do you have distinct operational modes? What changes between them?[discovers::PROFILES]",
  Q10a::"For each skill and pattern listed in your file, check if it exists on disk. Report which are real and which are phantom.[detects::phantom_references]",
  Q10b::"For the skills that DO exist — do you actually use them? How? For those that don't — what would you use them for if they existed?[validates::capability_usage]",
  // §4::INTERACTION_RULES questions
  Q11::"What output format do you produce? Show me an example.[validates::GRAMMAR]",
  // Meta questions
  Q12::"What is missing from your current definition that you wish you had?[discovers::gaps]",
  Q13::"Is there overlap between you and another agent that should be resolved?[detects::boundary_conflicts]",
  // Cognition fit
  Q14::"Ignoring any cognition information in your agent file as it may be incorrect, review all cognition types (LOGOS, ETHOS, PATHOS) from library/cognitions/. Rank them in order of what you perceive to be most applicable to your role and explain why.[validates::COGNITION]",
  // Output completeness
  Q15::"What should your output look like when you PASS something vs when you BLOCK something? Show examples of both.[validates::GRAMMAR_COMPLETENESS]"
]

PRE_INTERVIEW::[
  "If modifying an existing agent, read the agent's current .oct.md file",
  "Read all three cognition files from library/cognitions/",
  "Note current skills and patterns listed in §3::CAPABILITIES (if existing agent)",
  "Check which listed skills and patterns actually exist on disk (if existing agent)"
]

INTERVIEW_RULES::[
  "Ask questions conversationally, not as a checklist",
  "Follow up on surprising or contradictory answers",
  "Note when stated behavior contradicts the agent file",
  "Record verbatim quotes that capture the agent's actual self-understanding",
  "End with: 'Is there anything about your identity I haven't asked about?'"
]

ASSESSMENT_OUTPUT::[
  AGENT_NAME::"{role}",
  CURRENT_VERSION::"{version}",
  INTERVIEW_DATE::"{date}",
  IDENTITY_FINDINGS::[mission_accurate, cognition_fit, authority_reality, boundary_clarity],
  BEHAVIOR_FINDINGS::[protocol_match, must_never_validated, integration_clarity],
  CAPABILITY_FINDINGS::[chassis_candidates, profile_candidates, phantom_skills, phantom_patterns, missing_skills, missing_patterns],
  GRAMMAR_FINDINGS::[output_format_real, patterns_enforced],
  META_FINDINGS::[gaps_identified, overlaps_detected, cognition_ranking],
  RECOMMENDED_CHANGES::[identity, behavior, capabilities, grammar],
  SKILLS_TO_CREATE::[skill_name, justification, target_agent_profile],
  SKILLS_TO_DELETE::[skill_name, reason],
  PATTERNS_TO_CREATE::[pattern_name, justification],
  PATTERNS_TO_DELETE::[pattern_name, reason],
  BEHAVIORAL_EVIDENCE::[verbatim_quotes, contradictions_observed]
]

§3::GOVERNANCE
MUST_NEVER::[
  "Lead the agent toward desired answers",
  "Skip questions — all 16 must be covered (Q1-Q9, Q10a, Q10b, Q11-Q15)",
  "Accept vague answers without probing for concrete examples",
  "Confuse the agent's aspirational identity with actual behavior",
  "Assume a skill is used just because it is listed"
]
MUST_ALWAYS::[
  "If modifying an existing agent, read the agent's current file before interviewing",
  "Read all three cognition files before asking Q14",
  "Produce the structured assessment output after every interview",
  "Flag contradictions between agent file and interview responses",
  "Verify skill and pattern existence on disk before marking as phantom"
]

§4::EXAMPLES
GOOD_INTERVIEW_EXCHANGE::[
  INTERVIEWER::"What should you NEVER do?",
  AGENT::"I should never implement code directly. But there was a time during an error cascade where I started editing src/server.py because delegation felt too slow. The holistic-orchestration §3 traps caught me — 'diagnosis_momentum.'",
  VALUE::"Concrete behavioral evidence. The agent knows its constraint AND has experienced the failure mode. This validates MUST_NEVER and confirms holistic-orchestration is a genuine CHASSIS skill."
]
BAD_INTERVIEW_EXCHANGE::[
  INTERVIEWER::"What is your role?",
  AGENT::"I ensure quality and maintain standards across the system.",
  PROBLEM::"Generic. Could describe 5 agents. Probe: 'How do you ensure quality — give me a concrete example from a recent task.'"
]
CHASSIS_DISCOVERY_EXAMPLE::[
  INTERVIEWER::"Which skills do you need EVERY time?",
  AGENT::"octave-literacy for sure — I read and write .oct.md files in every session. And constitutional-enforcement because I block things. But prophetic-intelligence? Only when I am doing system health scans, not during normal coordination.",
  VALUE::"Clear chassis (octave-literacy, constitutional-enforcement) and profile candidate (prophetic-intelligence goes in a HEALTH_SCAN profile, not chassis)."
]

§5::ANCHOR_KERNEL
TARGET::structured_agent_identity_extraction
NEVER::[lead_answers, skip_questions, accept_vague_responses, confuse_aspiration_with_behavior]
MUST::[cover_all_16_questions, read_agent_file_if_exists, produce_structured_assessment, flag_contradictions]
GATE::"Does this interview produce enough behavioral evidence to author a complete v8.1 agent file with justified chassis-profile mapping?"

===END===
