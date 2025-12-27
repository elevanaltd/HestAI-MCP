===PHANTOM_SUBSTRATE_GIT_REF_RESEARCH===
// Research evidence for git ref behavior in phantom substrate pattern
// Consolidated from raw experiment files per visibility-rules FILE_RETENTION_POLICY

META:
  TYPE::"RESEARCH_EVIDENCE"
  DATE::"2025-12-25"
  AUTHOR::critical-engineer
  PURPOSE::"Validate git ref behavior for phantom substrate context storage"
  ORIGINAL_FILES::[
    evidence_git_ref_behavior.txt,
    evidence_git_index_pollution.txt,
    evidence_ref_reflog_recovery.txt
  ]

RESEARCH_CONTEXT::[
  PROBLEM::"Evaluate using refs/hestai/* for context storage separate from working branch",
  APPROACH::"Controlled experiments in isolated temp repos",
  DATE::"2025-12-25T01:52:00Z"
]

EXPERIMENT_1::REFS_HESTAI_CLONE_BEHAVIOR::[
  HYPOTHESIS::"refs/hestai/* exist on remote but are NOT cloned/fetched by default",
  SETUP::[
    push_heads_trunk_and_refs_hestai_main_to_remote,
    clone_fresh_repo
  ],
  RESULT::CONFIRMED[
    B_MISSING_refs_hestai_main,
    B_MISSING_origin_hestai_main,
    default_fetch_refspec::"+refs/heads/*:refs/remotes/origin/*"
  ],
  CONCLUSION::"Custom refs require explicit fetch refspec to retrieve"
]

EXPERIMENT_2::EXPLICIT_FETCH_REFSPEC::[
  HYPOTHESIS::"Explicit refspec required to fetch refs/hestai/*",
  COMMAND::"git fetch origin +refs/hestai/*:refs/hestai/*",
  RESULT::CONFIRMED[
    after_explicit_fetch::refs_hestai_main_present
  ],
  CONCLUSION::"Must configure explicit refspec for refs/hestai/* sync"
]

EXPERIMENT_3::DEFAULT_PUSH_BEHAVIOR::[
  HYPOTHESIS::"Default push does NOT push refs/hestai/*",
  RESULT::CONFIRMED[
    default_push::only_heads_updated,
    explicit_push::refs_hestai_updated
  ],
  CONCLUSION::"Must explicitly push refs/hestai/* to remote"
]

EXPERIMENT_4::INDEX_POLLUTION_SHARED::[
  HYPOTHESIS::"--work-tree checkout updates shared index causing status pollution",
  COMMAND::"git --work-tree=.hestai checkout refs/hestai/main -- .",
  RESULT::CONFIRMED[
    status_shows::MM_ctx_state_txt,
    index_polluted::true
  ],
  RECOVERY::"git reset --hard restores index to branch HEAD"
]

EXPERIMENT_5::ISOLATED_INDEX_MITIGATION::[
  HYPOTHESIS::"GIT_INDEX_FILE isolates index preventing pollution",
  COMMAND::"GIT_INDEX_FILE=.hestai.index git --work-tree=.hestai checkout refs/hestai/main -- .",
  RESULT::CONFIRMED[
    status_clean::true,
    isolated_index::".hestai.index"
  ],
  CONCLUSION::"Isolated index file required for safe phantom substrate operations"
]

EXPERIMENT_6::REFLOG_AVAILABILITY::[
  HYPOTHESIS::"refs/hestai/* may not have reflog for recovery",
  RESULT::CONFIRMED[
    reflog_enabled::false_by_default,
    after_delete::MISSING,
    recovery::NO_REFLOG_AVAILABLE
  ],
  IMPLICATION::"Deleted refs/hestai/* cannot be recovered via reflog"
]

KEY_FINDINGS::[
  F1::"refs/hestai/* are invisible to standard clone/fetch/push",
  F2::"Explicit refspecs required for remote sync",
  F3::"Shared index pollution occurs without GIT_INDEX_FILE isolation",
  F4::"No reflog recovery for custom refs by default",
  F5::"Reset --hard recovers from index pollution"
]

RECOMMENDATIONS::[
  R1::"Configure explicit fetch/push refspecs for refs/hestai/*",
  R2::"Always use GIT_INDEX_FILE for phantom substrate operations",
  R3::"Consider reflog configuration for refs/hestai/* if recovery needed",
  R4::"Document phantom substrate sync requirements for multi-machine use"
]

RELATED::[
  ADR_0033::"Dual-Layer Context Architecture",
  Issue_65::"External Artifact Store (future)"
]

===END===
