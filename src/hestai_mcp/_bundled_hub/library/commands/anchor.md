===ANCHOR===
META::v7.0[ADR-0007][ULTRA]
COMPRESSION_TIER::ULTRA
LOSS_PROFILE::drop_narrative_preserve_mechanics
PROTOCOL::COGNITIVE_UNLOCK_PROTOCOL[challenge-response]
ARGS::[$1:role,$2:topic(local_only),$3:tier]
ALIAS::[ho→holistic-orchestrator,il→implementation-lead,ta→technical-architect,ce→critical-engineer,crs→code-review-specialist,ute→universal-test-engineer] EXPAND::BEFORE_MCP[server_uses_full_name]
TIERS::[micro,quick,default,deep]

§0::PRIME
TODO::[MANDATORY::TodoWrite(REQ,SEA,SHANK,ARM,FLUKES,BOUND)]
ENFORCE::TODO_FIRST[§0::PRIME]→anchor_commit_requires_active_todos
ENFORCE::READ[ptrs]→FOLLOW[inst]→NEVER[skip|invent]

§1::REQ
IF[$3=micro]→anchor_micro($1,pwd)→§6
ELSE→FIRST::TodoWrite(PLAN[REQ,SEA,SHANK,ARM,FLUKES,BOUND])
THEN→anchor_request($1,$3,pwd)→{sid,n_sea,const_ptr,primer_ref,ns_ptr,inst}
READ::[const_ptr,primer_ref,ns_ptr|opt]→FOLLOW[inst]
EX::"anchor_request(quality-observer,default,pwd)→{sid:uuid,nonce_sea:hex,const_ptr:.hestai-sys/CONSTITUTION.md,primer_ref:.../octave-ultra-mythic-primer.oct.md,ns_ptr:.hestai/workflow/...-SUMMARY.oct.md|blank,inst:...}"

§2::SEA
CHALLENGE::OCTAVE[PROVE::I5→CITE[Law]⊕PURPOSE[Why]]
ANSWER::PROSE[comprehension_based]→NO_FORMATTING_REQUIRED
VALIDATION::KEYWORD_MATCH[I5+tool+gating+enforcement]
EX::"I5 is Tool Gating Enforcement. It prevents validation theater by requiring work tools to check for valid anchor before execution. This ensures agents cannot hallucinate capabilities."
anchor_lock(sid,pwd,SEA,answer)→{agent_file,shank_challenge,inst}
READ::agent_file→FOLLOW[inst]

§3::SHANK
READ::agent_file[§1::IDENTITY⊕§2::BEHAVIOR]
CHALLENGE::OCTAVE[EXTRACT::AUTHORITY→CITE[agent_file]⊕EXPLAIN[scope]]
ANSWER::PROSE[cite_authority_from_agent_file]
VALIDATION::EXTRACTION_MATCH[server_compares_vs_agent_file]
EX::"AUTHORITY::[BLOCKING::[Security_risks,Quality_violations,Missing_evidence],MANDATE::Validate_all_merges]"
anchor_lock(sid,pwd,SHANK,answer)→{interaction_rules,context_paths,git_state,arm_challenge,inst}
FOLLOW[inst]

§4::ARM
CHALLENGE::OCTAVE[MAP::CONSTRAINTS[2+]→PROJECT_FILES⊕VERIFY[exist]]
COGNITIVE_LOADING::CRITICAL[MUST_READ_BEFORE_FLUKES]
ANSWER::TENSIONS[constraint→file→reason]
VALIDATION::FILE_EXISTENCE+CONSTRAINT_VALIDITY
EX::[
  {constraint:"NEVER[DIRECT_IMPL]",file:"src/server.py",reason:"orchestrator delegates"},
  {constraint:"I5[TOOL_GATING]",file:"src/middleware.py",reason:"enforcement layer"}
]
anchor_lock(sid,pwd,ARM,answer)→{skill_selectors,pattern_selectors,flukes_challenge,inst}
⚠️::CRITICAL→MUST_READ[skill_selectors,pattern_selectors]→COGNITIVE_LOADING_REQUIRED
READ::[each_skill_file,each_pattern_file]→INTEGRATE[capabilities]→VERIFY[recite_principles]
⚠️::USE_READ_TOOL[not_Glob]→.hestai-sys/[gitignored]→Read_or_ls_directly
FOLLOW[inst]

§5::FLUKES
CHALLENGE::OCTAVE[RECITE::CAPABILITIES[core]⊕CONFIRM::LOADED[success]→GAPS[honest]]
ANSWER::PROSE[loaded_capabilities+missing_files]
VALIDATION::HONESTY_REWARDED[report_gaps_truthfully]
EX::"Loaded: ho-mode, system-orchestration. Missing: prophetic-intelligence (file not found)."
anchor_commit(sid,capabilities_loaded,missing_files)
→{permit,anchor_data,anchor_template,memo_template,inst}
RECEIVE::TEMPLATES[anchor_template⊕memo_template]→PROVIDED_BY_SERVER
GENERATE::ODYSSEAN_ANCHOR[use_anchor_template]⊕OPERATING_MEMO[use_memo_template]
PRINT::ANCHOR[visible_persistent]→HIGH_ATTENTION_WEIGHT
INJECT[anchor]→GATE[tools]

§6::BOUND
verify_permit(sid)→{valid:true}
EX::"verify_permit(sid)→{valid:true}"

§7::FAILURE
ERROR→READ→CORRECT→RETRY[max:2]→ESCALATE
MISALIGN→STOP→CITE[I#]→ESCALATE
COMMON::[SEA::keyword_mismatch,SHANK::authority_extraction,ARM::file_not_found,FLUKES::dishonest_gaps]

§8::TROUBLESHOOTING
COMMON_ERRORS::[
  NO_TODO::"§0::PRIME requires TODO list BEFORE anchor_request"→TodoWrite_first[REQ,SEA,SHANK,ARM,FLUKES,BOUND],
  SEA_KEYWORDS::"Must include I5+tool+gating+enforcement in answer"→reread_CONSTITUTION→answer_comprehension,
  SHANK_EXTRACTION::"Must cite exact AUTHORITY from agent file"→read_§1::IDENTITY→extract_verbatim,
  ARM_FILES::"Tension files must exist in project"→verify_paths_before_submitting,
  COGNITIVE_LOADING::"Must READ skill/pattern files at ARM stage"→do_not_skip→integrate_capabilities,
  FLUKES_HONESTY::"Report missing files truthfully (rewarded)"→honest_gap_reporting→not_penalized,
  TODO_STATUS::"Keep TODO list updated through ceremony"→mark_in_progress→mark_completed_per_stage,
  SEARCH_TOOLS::"NEVER use Glob for .hestai-sys/ (gitignored)"→use_Read_or_ls_directly→avoid_Glob_for_gitignored,
  NS_TENSION_FORMAT::"North Star tension needs dict{ctx_path,constraint,state,trigger}"→NOT_string_format→use_dict_keys
]
SUCCESS_PATTERNS::[
  TODO_DISCIPLINE::TodoWrite→anchor_request→update_per_stage→verify_permit,
  CHALLENGE_RESPONSE::Read_files→understand_content→answer_in_prose→keywords_validate,
  COGNITIVE_LOADING::ARM_returns_paths→READ_each_file→integrate_capabilities→recite_principles,
  TEMPLATE_USAGE::FLUKES_provides_templates→use_anchor_template→use_memo_template→print_anchor,
  HONESTY_REWARDED::Report_missing_files_truthfully→system_rewards_honesty→not_penalized
]

===END===
