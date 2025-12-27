===RESEARCH_LAYER3_BASIC_MEMORY_INTEGRATION===

META:
  TYPE::RESEARCH_ARTIFACT
  DATE::2025-12-15
  RESEARCHER::research-analyst (Gemini)
  STATUS::GO_CONDITIONAL
  PHASE::3_EXPANSION

---

## EXECUTIVE_SUMMARY

VERDICT::GO_CONDITIONAL[
  CONDITION::"Basic Memory as Read-Only Semantic Index (Projection) of Layers 1-2, NOT primary Source of Truth",
  WHY_GO::"Solves Conversational Query problem that JSON output cannot easily answer for LLM",
  RISK::"Split-Brain state where wiki-links diverge from codebase",
  FIX::"Hydration Pipeline - programmatically seed/update from unified-graph.json"
]

---

## INTEGRATION_ARCHITECTURE::HYDRATION_PATTERN

PRINCIPLE::CQRS[Command_Query_Responsibility_Segregation]

WRITE_SIDE::[
  SOURCE_OF_TRUTH::[
    code::src/**/*.py[Layer_1],
    anchors::specs/**/*.spec.py[Layer_2],
    generator::orchestra_map_generator.py→unified-graph.json
  ]
]

READ_SIDE::[
  LAYER_3::Basic_Memory[
    importer::map-to-memory-sync[reads_unified-graph.json],
    storage::~/basic-memory/generated/[machine_managed_markdown],
    enrichment::~/basic-memory/wiki/[human_managed_files_link_to_generated]
  ]
]

DATA_FLOW::[
  Code+Specs→AST_Analysis→unified-graph.json,
  unified-graph.json→Hydration_Script→Basic_Memory_MCP,
  Basic_Memory→Writes→~/basic-memory/generated/AuthService.md,
  Human/Agent→Writes→~/basic-memory/wiki/Governance.md,
  wiki/Governance.md→Wiki_Link→generated/AuthService
]

ROT_PREVENTION::[
  RULE::"NEVER manually edit files in ~/basic-memory/generated/",
  SYNC::"Hydration Script runs on pre-commit or CI, overwrites generated/",
  PERSISTENCE::"Human knowledge in separate wiki/ files, links remain valid on regeneration"
]

---

## USE_CASES_LAYER3

1::CONVERSATIONAL_IMPACT_ANALYSIS::[
  QUERY::"What concepts are impacted if I refactor AuthService?",
  MECHANISM::"Basic Memory walks graph: AuthService←AuthSpec←AUTH-POLICY-001"
]

2::DOMAIN_GOVERNANCE::[
  PROBLEM::"Layer 1/2 cannot map 'security-specialist role owns this folder'",
  SOLUTION::"Layer 3 file security-specialist.md with: Governs: [[generated/src/auth]]"
]

3::CONCEPT_TO_CONCEPT::[
  EXAMPLE::"AUTH-POLICY-001.md links to USER-PRIVACY-002.md",
  VALUE::"Higher-level web of requirements that doesn't exist in code"
]

---

## POC_CLOCKIN_HYDRATION

OBJECTIVE::"Prove we can turn unified-graph.json into queryable semantic graph"

SCOPE::[
  1::Setup[install_modelcontextprotocol/server-memory_or_equivalent],
  2::Input[use_existing_clockin_feature_graph_from_A8_POC],
  3::Tool[create_scripts/hydrate_memory.py::[
    reads_unified-graph.json,
    for_each_node(Code,Concept)→create_markdown_file,
    for_each_edge→append_wiki-link_line
  ]],
  4::Verification[LLM_asks_"What_does_ClockInTool_implement?"→retrieves_Concept_ID_via_Memory_tool]
]

SUCCESS_CRITERIA::"LLM can query Basic Memory and retrieve concept relationships from hydrated graph"

---

## RISKS_AND_MITIGATIONS

WIKI_LINK_ROT::[
  IMPACT::"Links point to non-existent files",
  MITIGATION::"Filename Stability Policy - generated filenames match Code path (e.g., src_auth_service.md)"
]

DUPLICATE_TRUTH::[
  IMPACT::"Basic Memory contradicts Code",
  MITIGATION::"One-Way Sync - Basic Memory NEVER source of structural truth, downstream view only"
]

NOISE::[
  IMPACT::"Too many files in Memory",
  MITIGATION::"Filter - only hydrate Public API files or explicitly Anchored files, not every utility"
]

---

## BREAKTHROUGH_ALTERNATIVE::VIRTUAL_MEMORY

CONCEPT::"Instead of syncing to files, custom MCP Resource Server serves unified-graph.json as virtual resources"

MECHANISM::"memory://graph/node/X → direct access to graph data"

PROS::[zero_sync_latency, zero_duplication]
CONS::[higher_engineering_effort, custom_MCP_server_vs_off-the-shelf]

RECOMMENDATION::"Stick to Hydration Pattern (Files) for POC - easier to debug, leverages existing tools"

---

## RECOMMENDATIONS

IMMEDIATE::[
  1::Use_Hydration_Pattern_for_POC,
  2::Create_hydrate_memory.py_script,
  3::Test_with_clockin_unified-graph.json,
  4::Verify_LLM_can_query_relationships
]

FUTURE::[
  1::Evaluate_Virtual_Memory_if_files_too_clunky,
  2::Consider_custom_MCP_server_for_zero-latency_queries,
  3::Explore_bidirectional_sync_for_human_annotations
]

---

## DECISION_RECORD

| Date | Actor | Action |
|------|-------|--------|
| 2025-12-15 | research-analyst | Basic Memory integration research complete |
| 2025-12-15 | research-analyst | Verdict: GO_CONDITIONAL (Hydration Pattern) |
| TBD | technical-architect | POC implementation decision |

===END===
