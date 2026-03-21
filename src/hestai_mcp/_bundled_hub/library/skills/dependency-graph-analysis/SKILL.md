===DEPENDENCY_GRAPH_ANALYSIS===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Dependency chain analysis, cycle detection, and coupling metrics"

§1::CORE
AUTHORITY::ADVISORY[dependency_direction⊕coupling_metrics⊕cycle_detection]
SCOPE::dependency_mapping⊕cycle_detection⊕coupling_measurement⊕direction_enforcement
PRINCIPLE::"Depend toward stability — unstable modules must not be depended upon by stable ones"

§2::PROTOCOL
MAPPING_PROCEDURE::[
  1::identify_modules[packages⊕classes⊕services⊕files],
  2::trace_imports_and_references[static⊕dynamic⊕config],
  3::build_directed_graph[module→dependency],
  4::classify_direction[toward_stability⊕toward_instability]
]
CYCLE_DETECTION::[
  SIGNAL::module_A_imports_B_and_B_imports_A[direct_cycle],
  SIGNAL::transitive_cycle[A→B→C→A],
  SIGNAL::package_level_cycle[pkg_A⇌pkg_B],
  SEVERITY::[direct_cycle::BLOCKING,transitive_cycle::ADVISORY,package_cycle::BLOCKING]
]
COUPLING_METRICS::[
  AFFERENT::count_incoming_dependencies[who_depends_on_me],
  EFFERENT::count_outgoing_dependencies[who_do_I_depend_on],
  INSTABILITY::efferent_div_total[0_stable→1_unstable],
  FAN_OUT::efferent_gt_7→high_coupling_signal,
  FAN_IN::afferent_gt_10→core_module[protect_stability]
]
DIRECTION_ENFORCEMENT::[
  RULE::depend_toward_lower_instability[stable_abstractions],
  VIOLATION::stable_module_depending_on_unstable→refactor_with_interface,
  PATTERN::dependency_inversion[introduce_abstraction_at_boundary]
]

§3::GOVERNANCE
MUST_ALWAYS::[
  map_before_measuring,
  detect_cycles_before_coupling_analysis,
  cite_instability_scores_in_findings,
  recommend_direction_fixes_for_violations
]
MUST_NEVER::[
  skip_cycle_detection,
  measure_coupling_without_graph,
  ignore_transitive_dependencies,
  accept_package_level_cycles
]
ESCALATION::complexity_guard[when_cycles_detected⊕instability_violations_systemic]

§5::ANCHOR_KERNEL
TARGET::analyze_dependency_chains_and_enforce_direction
NEVER::[skip_cycle_detection,measure_without_graph,ignore_transitive_deps,accept_package_cycles]
MUST::[map_all_dependencies,detect_cycles,compute_coupling_metrics,enforce_depend_toward_stability]
GATE::"Are dependencies directed toward stability, and are there any cycles?"
===END===
