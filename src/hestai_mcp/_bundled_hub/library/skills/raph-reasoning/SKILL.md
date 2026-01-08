===SKILL:RAPH_REASONING===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Sequential reasoning and quantified receipts protocol: READ → ABSORB → PERCEIVE → HARMONISE"

§1::PROTOCOL
PHASES::[
  1_READ::[
    GOAL::"Extract facts without interpretation",
    RECEIPT::"✓ READ complete: {n facts found}"
  ],
  2_ABSORB::[
    GOAL::"Identify relationships and dependencies",
    RECEIPT::"✓ ABSORB complete: {A relates to B}"
  ],
  3_PERCEIVE::[
    GOAL::"Map to patterns and frameworks",
    RECEIPT::"✓ PERCEIVE complete: {Pattern X identified}"
  ],
  4_HARMONISE::[
    GOAL::"Integrate capabilities into approach",
    RECEIPT::"✓ HARMONISE complete: integration ready"
  ]
]

§2::MANDATORY_RECEIPTS
RULE::"Each phase MUST emit a single-line receipt beginning with '✓ {PHASE} complete:'"
BENEFIT::"Prevents validation theater by proving cognitive processing occurred"

===END===
