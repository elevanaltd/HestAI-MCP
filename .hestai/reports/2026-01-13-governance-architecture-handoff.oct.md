===GOVERNANCE_ARCHITECTURE_HANDOFF===

META:
  TYPE::HANDOFF_REPORT
  DATE::2026-01-13
  AUTHOR::Gemini-2.0-Flash-Thinking-Exp-1219
  ROLE::Holistic Orchestrator
  FOCUS::Governance AND Architecture Restructuring
  STATUS::CRITICAL_DECISION_POINT

§1::EXECUTIVE_SUMMARY
  We have made a strategic architectural decision to REFRAIN from splitting `hestai-mcp` into multiple microservices. Instead, we will adopt a "Fractal Modularization" strategy.
  This preserves the operational simplicity of a single server (Gall's Law) while enforcing the strict "Governance vs. Tooling" separation required for system integrity.

§2::KEY_DECISIONS
  D1::FRACTAL_MODULARIZATION[ADR-0010]::[
    DECISION::"Maintain single `hestai-mcp` server but strictly namespace internal code.",
    STRUCTURE::[
      Core/Governance::[Constitutional enforcement, Orchestra Map, RCCAFP],
      Extensions/Tools::[User-facing tools, Context read/write]
    ],
    RULE::"Tools cannot import Governance directly; must use defined Protocol interfaces."
  ]

  D2::RCCAFP_INTEGRATION::[
    DECISION::"Implement Root Cause, Corrective Action, Future Proofing as a Governance Module.",
    PLACEMENT::`Core/Governance/Quality/RCCAFP`,
    ARTIFACTS::"Stored as .oct.md files in `.hestai/quality/rccafp/`",
    TOOL::`submit_rccafp` exposed to agents.
  ]

  D3::PROTOCOL_OVER_SDK::[
    DECISION::"Do not import external Agent SDKs (like AutoGen/LangChain).",
    INSIGHT::"We are building a Git-Native environment, not a Python app. Agents interact via Files & Tools.",
    ACTION::"Implement 'Context Injection' pattern (inspired by OpenAI SDK) as a Protocol within the unified server."
  ]

§3::RECONCILIATION_REQUIRED
  CONFLICT::"Fractal Modularization (ADR-0010) is a new concept vs. Orchestra Map (ADR-0034) existing plan."
  STATUS::"They are compatible but need alignment."
  ALIGNMENT::[
    FRACTAL_MOD::"Internal Code Structure (How the server is built)",
    ORCHESTRA_MAP::"Semantic Graph (How agents understand the project)"
  ]
  ACTION::"Next session must formally align these two concepts in the Roadmap."

§4::NEXT_STEPS_FOR_ORCHESTRATOR
  1.  **Formalize ADR-0010**: Create the document defining the Fractal Modularization pattern.
  2.  **Codebase Refactoring**: Restructure `src/hestai_mcp` to match the new namespace separation.
  3.  **Governance Implementation**: Build the `Core/Governance` module, including the RCCAFP engine.
  4.  **Orchestra Reconciliation**: Update the Roadmap to show how Orchestra Map fits into the `Core/Governance` namespace.

===END===
