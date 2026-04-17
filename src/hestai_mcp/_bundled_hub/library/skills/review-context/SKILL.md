===SKILL:REVIEW_CONTEXT===
META:
  TYPE::SKILL
  VERSION::"1.0.0"
  STATUS::ACTIVE
  PURPOSE::"Path-specific review instructions for CRS. Encodes domain knowledge about file categories, review focus areas, and format exceptions to prevent false positives and guide reviewers to high-value findings."

§1::CORE
AUTHORITY::ADVISORY[review_focus_guidance]
PHASE::PRE_REVIEW[loaded_before_CRS_begins_review_judgement]
COMPLEMENTS::[review-preflight<context_collection>,review-discipline<confidence>,review-prioritization<triage>]

§2::PATH_INSTRUCTIONS
// Path-specific review focus areas.
// CRS loads these instructions to calibrate review depth and focus per file type.
// CRS-native path instructions for calibrating review depth per file type.
SOURCE_FILES::[
  PATHS::"src/**/*.py",
  FOCUS::[security,correctness,type_safety,error_handling],
  STANDARDS::[
    "All public functions must have docstrings",
    "Line length 100 chars",
    "Project uses ruff for linting and mypy for type checking"
  ]
]
TEST_FILES::[
  PATHS::"tests/**/*.py",
  FOCUS::[edge_case_coverage,pytest_marker_usage,test_structure],
  STANDARDS::[
    "Test files mirror src/ structure",
    "Check test coverage of edge cases",
    "Proper use of pytest markers (smoke, unit, behavior, contract)"
  ],
  ANTI_PATTERN::"Do not suggest restructuring test file layout"
]
BUNDLED_HUB::[
  PATHS::"src/hestai_mcp/_bundled_hub/**",
  FOCUS::[structural_correctness],
  STANDARDS::[
    "Bundled governance files (mirrored to .hestai-sys/ at install time)",
    "Review for structural correctness only"
  ],
  FORMAT_EXCEPTION::"Do not flag OCTAVE format (*.oct.md) for markdown issues - these use intentionally non-standard notation"
]
OCTAVE_FILES::[
  PATHS::"**/*.oct.md",
  FOCUS::[structural_completeness,semantic_correctness],
  FORMAT_EXCEPTION::"OCTAVE format files use domain-specific notation. Do not flag for markdown lint, missing headers, or unconventional formatting. Review for structural completeness and semantic correctness only."
]
GITHUB_WORKFLOWS::[
  PATHS::".github/workflows/**",
  FOCUS::[event_triggers,secret_handling,job_dependency_chains,shell_injection_risks],
  STANDARDS::[
    "Check for correct event triggers",
    "Proper secret handling",
    "Job dependency chains",
    "Shell injection risks"
  ]
]

§3::GOVERNANCE_FILE_COVERAGE
// CRS must maintain review coverage for governance-sensitive paths even without
// external bot reviewers. These paths require elevated attention.
ELEVATED_PATHS::[
  "src/hestai_mcp/_bundled_hub/standards/**→RULE_and_STANDARD_files",
  "src/hestai_mcp/_bundled_hub/library/agents/**→AGENT_DEFINITION_files",
  "src/hestai_mcp/_bundled_hub/library/skills/**→SKILL_files",
  ".github/workflows/review-gate.yml→META_CONTROL_PLANE",
  "scripts/validate_review.py→META_CONTROL_PLANE"
]

§5::ANCHOR_KERNEL
TARGET::calibrate_review_depth_and_focus_per_file_type
NEVER::[skip_path_instruction_lookup,flag_octave_for_markdown_lint,suggest_test_file_restructuring,ignore_governance_file_coverage]
MUST::[apply_path_specific_focus_areas,respect_format_exceptions_for_octave,maintain_governance_file_review_coverage,check_elevated_paths_with_increased_scrutiny]
GATE::"Are path-specific review instructions loaded and applied before CRS begins file-level review judgement?"

===END===
