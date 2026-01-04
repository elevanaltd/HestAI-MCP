===SCHEMA_DEFINITION===
META:
  TYPE::SCHEMA_DEFINITION
  NAME::ODYSSEAN_ANCHOR
  VERSION::5.0
  PURPOSE::"Agent identity binding and cognitive proof"
  REPLACES::RAPH_VECTOR::v4.0

DESCRIPTION::[
  "Defines the structure for agent identity binding documents.",
  "Used by the odyssean_anchor MCP tool to validate agent initialization.",
  "Ensures agents prove identity, context awareness, and commitment."
]

DOCUMENT_TYPE::ODYSSEAN_ANCHOR

SECTIONS::[
  BIND,
  ARM,
  TENSIONS,
  COMMIT
]

FIELD_DEFINITIONS:

  BIND::[
    "Identity Lock - Agent's claimed identity and authority",
    FIELDS::[
      ROLE::{string}::"Agent role name matching constitution",
      COGNITION::{string}::"Type and archetype (e.g., LOGOS::ATHENA)",
      AUTHORITY::{string}::"RESPONSIBLE[scope] or DELEGATED[parent]"
    ]
  ]

  ARM::[
    "Context Proof - Server-injected project state",
    FIELDS::[
      PHASE::{string}::"Current project phase",
      BRANCH::{string}::"Git branch with ahead/behind counts",
      FILES::{string}::"Modified file count and top files",
      FOCUS::{string}::"Current focus topic from session"
    ],
    NOTE::"Server-authoritative, not agent-generated"
  ]

  TENSIONS::[
    "Cognitive Proof - Agent's understanding of constraints",
    TYPE::LIST,
    FORMAT::"L{N}::[constraint]⇌CTX:{path}[state]→TRIGGER[action]",
    MINIMUM_COUNT::{
      quick::1,
      default::2,
      deep::3
    },
    OPERATORS::[
      "⇌"::"tension/opposition (ASCII: <->)",
      "→"::"flow/progression (ASCII: ->)"
    ]
  ]

  COMMIT::[
    "Falsifiable Contract - Agent's deliverable commitment",
    FIELDS::[
      ARTIFACT::{path}::"Concrete file or test path",
      GATE::{string}::"Validation method"
    ]
  ]

VALIDATION_RULES::[
  "ROLE must match provided role parameter",
  "COGNITION type must be in [ETHOS, LOGOS, PATHOS]",
  "COGNITION archetype must be from pantheon",
  "AUTHORITY must have bracketed scope/parent",
  "TENSIONS must cite actual files with CTX:",
  "TENSIONS count must meet tier minimum",
  "ARTIFACT must be concrete path, not generic",
  "No placeholder values (TODO, TBD, FIXME)"
]

EXAMPLE::'''
===ODYSSEAN_ANCHOR===
META:
  TYPE::ODYSSEAN_ANCHOR
  VERSION::5.0

BIND:
  ROLE::holistic-orchestrator
  COGNITION::LOGOS::ATHENA
  AUTHORITY::RESPONSIBLE[octave integration]

ARM:
  PHASE::B1_FOUNDATION
  BRANCH::main[0↑0↓]
  FILES::3[odyssean_anchor.py, octave_transform.py]
  FOCUS::octave compliance

TENSIONS::[
  L1::[Custom format]⇌CTX:odyssean_anchor.py:194[RAPH_VECTOR::v4.0]→TRIGGER[migrate to OCTAVE],
  L2::[Regex parsing]⇌CTX:context_extraction.py:86[pattern matching]→TRIGGER[use octave-mcp]
]

COMMIT:
  ARTIFACT::schemas/odyssean-anchor.oct.md
  GATE::schema_validation

===END===
'''

MIGRATION::[
  "From RAPH_VECTOR::v4.0:",
  "- Remove ::v4.0 from envelope",
  "- Add META section with TYPE and VERSION",
  "- Convert ## headers to field notation",
  "- Wrap TENSION lines in TENSIONS::[ ... ] list"
]

COMPATIBILITY::[
  "Backward: octave_transform.py handles v4.0 → v5.0",
  "Forward: v5.0 is standard OCTAVE, parseable by octave-mcp",
  "Validation: odyssean_anchor.py validates schema rules"
]

===END===
