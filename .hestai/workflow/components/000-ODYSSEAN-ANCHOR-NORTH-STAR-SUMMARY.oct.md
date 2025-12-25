===ODYSSEAN_ANCHOR_NORTH_STAR_SUMMARY===
// Component Summary: Odyssean Anchor
// REFERENCE: component-of 000-MCP-PRODUCT-NORTH-STAR.md (not a standalone North Star)

META:
  TYPE::COMPONENT_SUMMARY
  COMPONENT::ODYSSEAN_ANCHOR
  PARENT::.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md

IMMUTABLES::[
  I1::UNIFIED_BINDING_PATH[One_protocol_for_all_agents],
  I2::STRUCTURAL_VALIDATION[RAPH_Vector_enforcement],
  I3::MANDATORY_SELF_CORRECTION[Reject_guidance_retry_loop],
  I4::CONTEXTUAL_PROOF[ARM_must_match_git_state],
  I5::AUTHORITY_INHERITANCE[Subagents_cite_parent_FLUKE],
  I6::TOOL_GATING_ENFORCEMENT[Tools_check_anchor_before_exec],
  I7::COGNITIVE_BINDING_PERSISTENCE[Vector_returned_to_context]
]

CONSTRAINTS::[
  MUST_USE_OA_LOAD,
  MUST_VALIDATE_SCHEMA,
  NEVER_ALLOW_SILENT_FAILURE
]

RELATIONSHIPS::[
  IMPLEMENTS::Product_I5[Odyssean_Identity_Binding],
  ENFORCES::System_I1[Verifiable_Spec],
  SUPPORTS::Living_Artifacts[Provides_Session_Context]
]

===END===
