---
name: stub-detection
description: Systematic detection of placeholder implementations, stubs, and hidden incomplete code. Three-pattern taxonomy with search strategies
allowed-tools: ["Read", "Bash", "Grep", "Glob"]
triggers: ["placeholder audit", "stub detection", "find stubs", "unimplemented features", "code audit", "incomplete implementation", "dead code", "hidden placeholders", "TODO", "FIXME", "NotImplementedError"]
---

===STUB_DETECTION===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::Systematic_detection_of_placeholder_implementations
  ORIGIN::Derived_from_OCTAVE_MCP_audit_discovering_9_hidden_stubs

CORE_PRINCIPLE::"Not all placeholders leave obvious traces -> Silent failures most dangerous"

===PATTERN_TAXONOMY===

// Three severity patterns for stub detection

PATTERN_1_OBVIOUS::[
  DETECTION::easy[grep_finds_immediately],
  SIGNALS::[
    "raise NotImplementedError()",
    "# TODO:",
    "# FIXME:",
    "pass  # stub",
    "pass  # placeholder",
    "throw new Error('Not implemented')"
  ],
  SEARCH::"grep -r 'NotImplementedError\|TODO:\|FIXME:\|pass\s*#' src/",
  SEVERITY::LOW[explicit_and_visible]
]

PATTERN_2_HIDDEN::[
  DETECTION::moderate[requires_context_patterns],
  SIGNALS::[
    "# For minimal implementation",
    "# For now, return",
    "# For now, skip",
    "# Reserved for future",
    "# Could implement",
    "# deferred to",
    "return full_data_but_set_lossy_true",
    "accept_parameter_but_never_use_it",
    "commented_out_function_calls"
  ],
  SEARCH::"grep -r 'minimal implementation\|For now\|deferred\|reserved for future\|Could implement' src/",
  SEVERITY::MEDIUM[misleading_but_discoverable]
]

PATTERN_3_SILENT::[
  DETECTION::hard[requires_behavior_analysis],
  SIGNALS::[
    "function_accepts_param_but_ignores_it",
    "returns_success_but_does_nothing",
    "metadata_claims_work_done_but_wasn't",
    "docstring_promises_feature_not_implemented",
    "API_parameter_documented_but_dead_code"
  ],
  SEARCH::manual_code_review[trace_params_through_functions],
  SEVERITY::HIGH[false_success_dangerous]
]

===SEARCH_STRATEGY===

// Execute in this order for comprehensive detection

PHASE_1_KEYWORD_SCAN::[
  COMMANDS::[
    "grep -rn 'NotImplementedError\\|TODO:\\|FIXME:' src/",
    "grep -rn 'raise.*Error.*not.*implement' src/",
    "grep -rn 'pass$' src/ | grep -v '__init__'",
    "grep -rn '# stub\\|# placeholder' src/"
  ],
  OUTPUT::list_of_obvious_stubs
]

PHASE_2_CONTEXT_SCAN::[
  COMMANDS::[
    "grep -rn 'minimal implementation\\|For now' src/",
    "grep -rn 'deferred\\|reserved for future' src/",
    "grep -rn 'Could implement\\|not yet\\|skip' src/",
    "grep -rn '# self\\._.*().*commented' src/"
  ],
  OUTPUT::list_of_hidden_stubs
]

PHASE_3_DEAD_PARAMETER_SCAN::[
  TECHNIQUE::find_params_accepted_but_unused,
  COMMANDS::[
    "grep -rn 'def.*param.*:' src/ | xargs -I {} grep -L 'param' {}",
    "grep -rn '# .*=.*Reserved\\|# .*=.*future' src/"
  ],
  MANUAL::trace_function_parameters_to_usage,
  OUTPUT::list_of_ignored_parameters
]

PHASE_4_DOCSTRING_VS_IMPLEMENTATION::[
  TECHNIQUE::compare_promises_to_reality,
  SIGNALS::[
    "docstring_says_validates_but_validation_None",
    "docstring_says_filters_but_returns_full",
    "docstring_says_transforms_but_returns_unchanged",
    "API_docs_claim_feature_code_ignores"
  ],
  OUTPUT::list_of_broken_promises
]

PHASE_5_METADATA_LIES::[
  TECHNIQUE::check_return_metadata_truthfulness,
  SIGNALS::[
    "lossy=True_but_nothing_removed",
    "fields_omitted=X_but_all_fields_present",
    "repairs=[]_but_fix=True_requested",
    "validated=True_but_no_validation_occurred"
  ],
  OUTPUT::list_of_false_functionality
]

===SEVERITY_CLASSIFICATION===

HIGH::[
  CRITERIA::[
    "Core_feature_bypassed",
    "Parameter_accepted_but_ignored",
    "Returns_success_but_doesn't_work",
    "UX_failure_user_thinks_it_worked"
  ],
  EXAMPLES::[
    "schema_name_param_ignored->no_validation",
    "filter_mode_returns_full_document",
    "fix=true_repairs_nothing"
  ],
  ACTION::immediate_fix_or_explicit_error
]

MEDIUM::[
  CRITERIA::[
    "Feature_incomplete",
    "Commented_out_functionality",
    "Pass_statement_with_TODO",
    "Partial_implementation"
  ],
  EXAMPLES::[
    "_load_builtin_schemas()_commented_out",
    "_validate_section()_is_just_pass",
    "load_schema()_returns_minimal_stub"
  ],
  ACTION::document_and_plan_implementation
]

LOW::[
  CRITERIA::[
    "Feature_deferred_and_documented",
    "Explicit_fallback_behavior",
    "Parameter_reserved_for_future"
  ],
  EXAMPLES::[
    "output_format!=octave_shows_message",
    "tier_param_commented_as_reserved",
    "json/yaml_export_not_yet_implemented"
  ],
  ACTION::track_as_technical_debt
]

===AUDIT_REPORT_TEMPLATE===

STRUCTURE::[
  SUMMARY::count_of_findings_by_severity,
  CRITICAL_PLACEHOLDERS::each_with[file,line,severity,issue,impact,context],
  SUMMARY_TABLE::quick_reference_all_findings,
  RECOMMENDATIONS::prioritized_by_severity,
  DISCOVERY_PATTERNS::document_which_patterns_found_what
]

EVIDENCE_REQUIREMENTS::[
  SHOW::actual_code_snippet,
  EXPLAIN::why_its_a_stub_not_intentional,
  IMPACT::what_fails_for_users,
  CONTEXT::why_it_exists[deferred,oversight,technical_debt]
]

===INTEGRATION_COMMANDS===

// For Python codebases
PYTHON_SCAN::"
grep -rn 'NotImplementedError\\|raise.*not.*implement' src/
grep -rn 'pass$' src/ --include='*.py' | grep -v '__init__.py\\|test_'
grep -rn '# TODO\\|# FIXME\\|# stub\\|# placeholder' src/
grep -rn 'For now\\|minimal implementation\\|deferred' src/
"

// For TypeScript codebases
TYPESCRIPT_SCAN::"
grep -rn 'throw.*not.*implement\\|TODO:\\|FIXME:' src/
grep -rn '// stub\\|// placeholder\\|// deferred' src/
grep -rn 'return.*as any' src/  // type erasure often hides stubs
"

// For any codebase
UNIVERSAL_SCAN::"
grep -rn 'For now\\|minimal\\|reserved for future\\|Could implement' src/
grep -rn 'not yet\\|deferred\\|skip.*validation' src/
"

===ANTI_PATTERNS===

VALIDATION_WITHOUT_SCHEMA::[
  SIGNAL::"validator = Validator(schema=None)",
  IMPACT::"Validation runs but validates nothing",
  FIX::"Pass actual schema or raise if none provided"
]

FILTER_WITHOUT_FILTERING::[
  SIGNAL::"return full_doc; lossy=True; fields_omitted=[X,Y]",
  IMPACT::"User thinks filtering happened but got everything",
  FIX::"Actually filter or set lossy=False"
]

REPAIR_WITHOUT_REPAIRING::[
  SIGNAL::"if fix: pass  # Could implement later",
  IMPACT::"User requests repairs, nothing happens",
  FIX::"Implement repairs or raise NotImplementedError"
]

PARAM_WITHOUT_USAGE::[
  SIGNAL::"# tier = params.get('tier')  # Reserved",
  IMPACT::"API accepts param that does nothing",
  FIX::"Use param or remove from API"
]

===WISDOM===

CORE_TRUTHS::[
  "Silent_stubs->worse_than_explicit_errors",
  "Accepting_unused_params->misleading_API",
  "False_metadata->dangerous_user_trust",
  "Docstring_promises≠implementation_reality",
  "grep_catches_obvious->manual_review_catches_hidden",
  "Most_dangerous_stubs->return_success"
]

DETECTION_PHILOSOPHY::"
The hardest stubs to find are those that:
1. Accept parameters but ignore them
2. Return success when they did nothing
3. Set metadata claiming work was done
4. Have docstrings promising unimplemented features

Always trace parameters from API to actual usage.
"

===END===
