===CONTEXT_REGISTRY_SPECIFICATION===

META:
  NAME::"Context Registry System"
  VERSION::"0.1.0"
  PURPOSE::"Document categorization and visibility management for agent clock-in"

METADATA::[
  type::specification,
  domain::context-steward,
  status::proposed,
  owners::[system-steward,context-steward],
  created::2025-12-19,
  id::context-registry-spec,
  canonical::hub/governance/specs/context-registry-spec.oct.md,
  format::octave,
  tags::[context|registry|visibility|clock-in|categorization]
]

===PROBLEM_STATEMENT===

CURRENT_STATE::[
  clock_in_returns_all_context_files,
  no_relevance_filtering,
  no_priority_ordering,
  agents_load_unnecessary_context,
  token_waste+cognitive_overhead
]

DESIRED_STATE::[
  registry_categorizes_documents,
  visibility_rules_per_role_phase,
  priority_ordering,
  minimal_necessary_context,
  token_efficiency+clarity
]

===REGISTRY_SCHEMA===

DOCUMENT_ENTRY::[
  path::string[relative_to_project_root],
  category::ENUM[core|operational|governance|auxiliary],
  visibility::ENUM[always|role_specific|phase_specific|optional],
  priority::INTEGER[1-10]→higher_more_important,
  roles::[implementation-lead|critical-engineer|...],
  phases::[D1|D2|D3|B0|B1|B2|B3|B4],
  tags::[north-star|context|history|checklist|roadmap],
  description::string[why_this_matters]
]

CATEGORY_DEFINITIONS::[
  CORE::[
    definition::"Always needed for any agent work",
    examples::[PROJECT-NORTH-STAR,PROJECT-CONTEXT],
    visibility::always
  ],

  OPERATIONAL::[
    definition::"Active work state and coordination",
    examples::[PROJECT-CHECKLIST,PROJECT-HISTORY],
    visibility::role_specific
  ],

  GOVERNANCE::[
    definition::"Standards, rules, and methodology",
    examples::[TEST-STRUCTURE-STANDARD,NAMING-STANDARD],
    visibility::phase_specific
  ],

  AUXILIARY::[
    definition::"Reference material, loaded on demand",
    examples::[context-negatives,app-specific-contexts],
    visibility::optional
  ]
]

===VISIBILITY_RULES===

ALWAYS_VISIBLE::[
  .hestai/workflow/000-PROJECT-NORTH-STAR.oct.md,
  .hestai/context/PROJECT-CONTEXT.oct.md
]

ROLE_SPECIFIC_MAPPING::[
  implementation-lead::[
    PROJECT-CHECKLIST.oct.md[priority:8],
    PROJECT-ROADMAP.oct.md[priority:7],
    BUILD-EXECUTION-STANDARDS.md[priority:9]
  ],

  critical-engineer::[
    PROJECT-HISTORY.oct.md[priority:9],
    TEST-STRUCTURE-STANDARD.md[priority:10],
    ARCHITECTURE-DECISIONS.md[priority:8]
  ],

  workspace-architect::[
    PROJECT-CONTEXT.oct.md[priority:10],
    PROJECT-CHECKLIST.oct.md[priority:8],
    NAMING-STANDARD.md[priority:7]
  ]
]

PHASE_SPECIFIC_MAPPING::[
  D1_D2_D3::[governance_docs,north_star,methodology],
  B0_B1::[test_standards,workspace_setup,architecture],
  B2_B3_B4::[operational_state,checklist,history]
]

===REGISTRY_IMPLEMENTATION===

FILE_LOCATION::.hestai/registry/context-registry.json

REGISTRY_FORMAT::JSON[
  {
    "version": "1.0.0",
    "updated_at": "ISO8601_timestamp",
    "entries": [
      {
        "path": ".hestai/workflow/000-PROJECT-NORTH-STAR.oct.md",
        "category": "core",
        "visibility": "always",
        "priority": 10,
        "roles": [],
        "phases": [],
        "tags": ["north-star", "requirements"],
        "description": "Immutable project requirements"
      },
      {
        "path": ".hestai/context/PROJECT-CHECKLIST.oct.md",
        "category": "operational",
        "visibility": "role_specific",
        "priority": 8,
        "roles": ["implementation-lead", "workspace-architect"],
        "phases": ["B2", "B3", "B4"],
        "tags": ["checklist", "tasks"],
        "description": "Active task tracking"
      }
    ]
  }
]

===CLOCK_IN_INTEGRATION===

ENHANCED_FLOW::[
  1::agent_calls_clock_in[role,working_dir,focus],
  2::load_registry_from_.hestai/registry/,
  3::filter_by_visibility_rules[role,phase,focus],
  4::sort_by_priority[descending],
  5::return_categorized_context_paths
]

RESPONSE_STRUCTURE::[
  session_id::string,
  context_paths::{
    core::[high_priority_always_visible],
    required::[role_and_phase_specific],
    optional::[auxiliary_available_if_needed]
  },
  visibility_metadata::{
    total_available::INTEGER,
    loaded::INTEGER,
    filtered_out::INTEGER,
    reason::string
  }
]

===REGISTRY_MAINTENANCE===

UPDATE_TRIGGERS::[
  new_document_created→auto_categorize,
  document_moved→update_path,
  role_added→update_mappings,
  phase_transition→refresh_visibility
]

AUTO_CATEGORIZATION_RULES::[
  IF::filename_contains["NORTH-STAR"]→category:core,
  IF::path_contains[".hestai/context/"]→category:operational,
  IF::path_contains[".hestai/workflow/"]→category:governance,
  IF::filename_contains["negatives"|"archive"]→category:auxiliary
]

===BENEFITS===

TOKEN_EFFICIENCY::[
  BEFORE::all_docs_loaded→5000-10000_tokens,
  AFTER::filtered_relevant→1000-3000_tokens,
  SAVINGS::60-70%_token_reduction
]

COGNITIVE_CLARITY::[
  agents_see_only_relevant_context,
  priority_ordering_guides_attention,
  reduced_confusion_from_irrelevant_docs
]

MAINTAINABILITY::[
  central_registry_for_visibility_rules,
  easier_to_update_than_hardcoded_paths,
  visibility_logic_separated_from_code
]

===MIGRATION_PATH===

PHASE_1::create_registry_structure[manual_population]
PHASE_2::update_clock_in_to_read_registry
PHASE_3::implement_auto_categorization
PHASE_4::add_registry_maintenance_tools

===EXAMPLE_USAGE===

```python
# In clock_in.py enhancement
def clock_in_with_registry(role, working_dir, focus):
    # Load registry
    registry = load_context_registry(working_dir)

    # Filter by visibility rules
    context_paths = registry.filter_for_agent(
        role=role,
        phase=detect_phase_from_focus(focus),
        focus=focus
    )

    # Return categorized paths
    return {
        "session_id": session_id,
        "context_paths": {
            "core": context_paths.core,  # Always loaded
            "required": context_paths.required,  # Role/phase specific
            "optional": context_paths.optional  # Available if needed
        },
        "visibility_metadata": {
            "total_available": registry.total_docs,
            "loaded": len(context_paths.all),
            "filtered_out": registry.total_docs - len(context_paths.all),
            "reason": f"Filtered for {role} in {focus}"
        }
    }
```

===FUTURE_ENHANCEMENTS===

DYNAMIC_LEARNING::[
  track_which_docs_agents_actually_use,
  adjust_priorities_based_on_usage_patterns,
  ML_based_relevance_scoring
]

DEPENDENCY_GRAPHS::[
  IF::doc_A_loaded→THEN::doc_B_also_needed,
  transitive_dependency_resolution,
  circular_dependency_detection
]

VERSIONING::[
  registry_version_per_project_phase,
  different_visibility_rules_over_time,
  historical_registry_snapshots
]

===END===
