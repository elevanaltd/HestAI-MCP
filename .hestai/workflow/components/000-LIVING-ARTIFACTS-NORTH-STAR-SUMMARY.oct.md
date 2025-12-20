# COMPONENT SUMMARY: LIVING ARTIFACTS

COMPONENT::LIVING_ARTIFACTS
PARENT::.hestai/workflow/000-MCP-PRODUCT-NORTH-STAR.md

IMMUTABLES::[
  I1::SPLIT_ARTIFACT_AUTHORITY[Audit_vs_State_separation],
  I2::QUERY_DRIVEN_FRESHNESS[Runtime_generation_over_storage],
  I3::SINGLE_BRANCH_CI_WRITES[No_orphan_branch_magic],
  I4::BLOCKING_STALENESS[Stale_context_stops_work],
  I5::PERSISTENT_AUDIT_TRACE[Merge_history_never_lost]
]

CONSTRAINTS::[
  MUST_GENERATE_STATE,
  NEVER_WRITE_CROSS_BRANCH,
  MUST_BLOCK_ON_STALE
]

RELATIONSHIPS::[
  IMPLEMENTS::Product_I4[Freshness_Verification],
  ENFORCES::System_I4[Discoverable_Persistence],
  FEEDS::Odyssean_Anchor[Provides_Context_for_ARM]
]
