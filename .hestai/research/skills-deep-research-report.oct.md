===LLM_SKILL_FORMATS_RESEARCH===
META:
  TYPE::RESEARCH_REPORT
  VERSION::"2.0.0"
  STATUS::VALIDATED
  PURPOSE::"Evidence-based guide to skill structure, routing, tool gating, and token efficiency across agent runtimes"
  COMPRESSION_TIER::CONSERVATIVE
  LOSS_PROFILE::"~10% — dropped: prose connectives, some citation verbosity. All data points, API names, conceptual frameworks, and causal insights preserved."
  NARRATIVE_DEPTH::COMPREHENSIVE_WITH_EVIDENCE
  SOURCE::"skills-deep-research-report.md"
  FRAMEWORKS_STUDIED::[Claude_Code,MCP,Claude_API,LangChain,CrewAI,AutoGen]
  ASSUMPTIONS::"x86 Linux runtime, lexical+semantic retrieval layers, standard JSON Schema validator (Ajv/fastjsonschema/jsonschema)"
§0::CORE_THESIS
  PRINCIPLE::"Less tool context → more accuracy and performance"
  MECHANISM::"Runtime-consumed structure outperforms prompt formatting"
  CONVERGENCE::"all_frameworks→TRIPLET_PATTERN"
DESCRIPTION_TRUTH::"Descriptions are retrieval hints, NOT enforceable constraints"
EVIDENCE_GAPS::"Where empirical data missing, strongest evidence from (a) tool retrieval benchmarks and (b) long-context studies (Lost in the Middle)"
§1::CLAUDE_CODE_SKILLS_DISCOVERY
  DISCOVERY_MECHANISM::YAML_frontmatter
  RUNTIME_PARSING::["name→dispatch routing⊕search index","description→retrieval ranking (BM25⊕embeddings)","allowed-tools→permission gating (deny→ask→allow)","disable-model-invocation→auto invoke control","context→skill context injection"]
  AUTO_DISCOVERY::"SKILL.md files; permissions via /permissions; MCP policies via allowedMcpServers/deniedMcpServers"
  RETRIEVAL::"hybrid: BM25 over name+description, embeddings over body"
  CONSTRAINT::"k small (1-3 skills) to avoid prompt bloat"
  TOOL_SEARCH_TRIGGER::"tool descriptions exceeding 10% context window→selective loading"
  §1b::RUNTIME_CONSUMED_LITMUS_TEST
    HEURISTIC::"Does the runtime parse it into typed fields and change behaviour if wrong/missing? If yes → runtime-consumed"
    ENFORCEABLE::[name,allowed_tools,input_schema,disable_model_invocation,context]
    ADVISORY::[description] // MCP spec: hint only
    MCP_INTEROP::"inputSchema→input_schema rename required for Claude API conversion"
    STRICT_MODE::"strict:true guarantees schema conformance — no type mismatches or missing fields"
  §1c::THREE_FORM_TAXONOMY
    // Conceptual framework for structure types
    YAML_FRONTMATTER::"configuration carrier — enforceability depends on runtime parser"
    JSON_SCHEMA::"contract — for arguments and/or outputs"
    TOOL_REGISTRATION_APIS::"in-memory registries + dispatch wiring — schema inference + provider-format conversion"
    YAML_FIELDS::"name, description, disable-model-invocation, allowed-tools, context"
    YAML_ENFORCES::"invocation control + tool access control via permissions"
    YAML_PREVENTS::"unwanted auto-invocation; over-permissioned tool use"
    YAML_OVERHEAD::"parsed at startup or file change, not per request"
    SCHEMA_FIELDS::"inputSchema/input_schema, outputSchema"
    SCHEMA_ENFORCES::"argument shape/type validation; error typing; guaranteed conformance (strict modes)"
    SCHEMA_PREVENTS::"malformed arguments; brittle string-parsing; schema drift"
    SCHEMA_OVERHEAD::"validator compilation non-trivial but far below LLM inference"
    API_FIELDS::"name, description, schema from annotations/types, binding lists"
    API_ENFORCES::"tool list gating; dispatch by name; orchestration loops"
    API_PREVENTS::"hallucinated/unregistered tools; callable vs executable mismatch"
    API_OVERHEAD::"avoids repeated parsing; conversion to provider formats still required"
§2::LLM_COMPREHENSION
  CORE_INSIGHT::"Structure consumed PROGRAMMATICALLY provides largest gains"
  YAML_WITHOUT_RUNTIME::"minimal benefit beyond human readability"
  §2b::EVIDENCE_HIERARCHY
§2c::ENFORCEMENT_AS_RETRY_REDUCTION
  // Key causal insight — inverts naive expectation that enforcement adds overhead
  MECHANISM::"Enforcement improves performance by reducing retries and unnecessary inference cycles, NOT through local parsing cost"
  STRICT_TRUE::"eliminates type mismatches/missing fields→removes retry loops and exception handling in production"
  MCP_ERROR_MODEL::["protocol errors (unknown tool, malformed requests) vs tool execution errors (isError:true)","execution errors passed back to model→enables self-correction","structured mechanism for reducing repeated failures and improving convergence"]
  TOKEN_LATENCY::"cutting 50% of prompt→only 1-5% latency gain unless massive; real gain is fewer retries"
  INSIGHT::"Enforcement removes overhead by eliminating failure-retry cycles"
§2d::CONTEXT_BLOAT_EVIDENCE
  ANTHROPIC_55K::"55K+ tokens consumed by 58 tool definitions"
  ANTHROPIC_134K::"134K tokens pre-optimisation"
  ON_DEMAND_DISCOVERY::"77K→8.7K tokens via Anthropic Tool Search"
  LANGCHAIN_OFFLOAD::"tool outputs exceeding 20K tokens→filesystem"
  SELECTIVE_THRESHOLD::"10% context window triggers MCP Tool Search selective loading"
§2e::PARSING_OVERHEAD
  // negligible vs inference
  BENCHMARK_ENV::"Python 3.11, Linux x86_64, ~6-field skill frontmatter, median measurements"
  JSON_LOADS::"~3 microseconds per parse"
  JSON_SCHEMA_VALIDATE::"~45 microseconds per validate (Draft 2020-12)"
  YAML_SAFE_LOAD::"~0.56 milliseconds per parse"
  RANKING::"JSON parse then schema validate then YAML parse — all sub-millisecond"
  COMPILATION_CAVEAT::"JSON Schema validator compilation can dominate: low ms to tens of ms depending on engine (AJV compilation may exceed specialised compilers)"
  PRACTICAL_RULE::"Optimise token overhead first; optimise parsing only when CPU-bound"
§3::TRIPLET_PATTERN
  UNIVERSAL::"name⊕description⊕schema_gates"
  CONVERGENCE::[Claude_Code,MCP,Claude_API,CrewAI,LangChain,AutoGen]
  DIFFERENCES::"enforcement mechanism (IDE vs runtime) ⊕ routing topology (single vs multi-agent)"
  DESCRIPTION_INSIGHT::"intentionally non-enforceable across ALL frameworks; used for selection only, never constrains execution"
  §3b::FRAMEWORK_MAPPING
    CLAUDE_CODE::"name→dispatch, description→search_index, allowed-tools⊕permissions(allow/ask/deny)→gating"
    MCP::"params.name→tools/call, description→hint, inputSchema required, outputSchema optional"
    CLAUDE_API::"tools[].name, tools[].description, input_schema⊕strict:true→guaranteed conformance"
    CREWAI::"name, role/backstory, per-task tools⊕output_json/output_pydantic⊕guardrails"
    LANGCHAIN::"name, description, bind_tools⊕tool_choice forcing⊕with_structured_output(json_schema vs function_calling)"
    AUTOGEN::"name, description, register_for_llm/register_for_execution split; FunctionTool generates schemas from type annotations"
  §3c::COMPREHENSIVE_COMPARISON
    // Per-framework: parsed fields, registration APIs, enforcement examples, perf notes, known limitations
    CLAUDE_CODE::["parsed: YAML frontmatter (name, description, disable-model-invocation, allowed-tools); permissions (allow/ask/deny)","APIs: SKILL.md auto-discovery, /permissions, allowedMcpServers/deniedMcpServers","enforcement: deny overrides allow; wildcard specifiers constrain Bash/WebFetch/MCP; allowed-tools limits per-skill","perf: MCP Tool Search defers when descriptions exceed 10% context window","limits: third-party MCP servers expose prompt injection risk; trust boundary explicit"]
    MCP::["parsed: name (required), inputSchema (required), description (hint), outputSchema (structured results)","APIs: tools/list discovery, tools/call invocation, JSON-RPC schema reference","enforcement: servers MUST validate inputs; clients SHOULD validate results; unknown tools→JSON-RPC error","perf: model-controlled invocation; recommends human-in-loop UI for security","limits: tool annotations untrusted unless trusted server; semantics beyond schema require runtime controls"]
    CLAUDE_API::["parsed: name, description, input_schema; strict:true→guaranteed conformance","APIs: Messages API tools array, tool_use/tool_result workflow; inputSchema→input_schema conversion for MCP","enforcement: stop_reason=tool_use; strict mode removes type-mismatch/missing-field failures","perf: on-demand discovery reduces overhead; improved accuracy in internal tests","limits: without search/deferral, large libraries consume 50K+ tokens and harm selection"]
    CREWAI::["parsed: task tools field (agent limited to these); output_json/output_pydantic; guardrails","APIs: YAML config for agents/tasks; Crew orchestration; tools supplied to agents/tasks","enforcement: tool set constrained per Task; Pydantic models structure output; guardrail validates before next task","perf: no official token benchmark; depends on tool list size and task chaining (assumption)","limits: YAML correctness and naming matters; task/agent wiring sensitive to config/method name matches"]
    LANGCHAIN::["parsed: schema+function pairings; bind_tools; tool calls (name, args); tool_choice; structured output (JSON Schema vs function-calling)","APIs: bind_tools, tool decorators, agent loop; with_structured_output supports json_schema vs function_calling methods","enforcement: available tools by binding list; forced tool choice; structured output methods change enforcement strategy","perf: Deep Agents offloads outputs exceeding 20K tokens; summarises at context thresholds","limits: too many tools→poor decisions; motivates multi-agent decomposition"]
    AUTOGEN::["parsed: name/description, schema from type annotations; callable vs executable registration","APIs: register_for_llm, register_for_execution, register_function; FunctionTool generates schemas","enforcement: wiring to LLM-caller and executor; annotations→schema generation for input validation and serialization","perf: no official latency benchmarks; dominated by tool count and model inference (assumption)","limits: output type correctness remains user responsibility; schema covers inputs but not always outputs"]
§4::STRUCTURE_VS_PROSE
  SCHEMA_WINS::["JSON Schema→order-of-magnitude reduction vs prose","compact name/description→improved retrieval precision","allowed-tools→reduced off-task tool use","permission gating (deny→ask→allow)→replaces repeated prompt warnings"]
  OVER_STRUCTURING_HURTS::["tool definition bloat→wrong selection⊕incorrect parameters (Anthropic finding)","Lost in Middle→performance degradation in long input contexts","token reduction→modest latency gain (1-5% from 50% cut) unless massive prompt"]
  PRACTICAL_RULE::"Use structure your runtime can consume programmatically. Everything else is noise."
  §4b::COMPRESSION_STRATEGIES
§5::OPTIMAL_SKILL_TEMPLATE
  STRUCTURE::["section headers: Objective, Inputs, Procedure, Invariants, Output","declarative constraints EARLY, before procedures","do/dont constraints before procedures","5-8 procedure steps mapped to specific tools","single tool source of truth: never mention tools not in allowed-tools"]
  EXAMPLES::"1-2 canonical ⊕ 1 anti-example; 1 example per 200 tokens of abstraction"
  SIZE::"SKILL.md under 500 lines; body 300-700 tokens; bulk reference→separate files on demand"
§6::RETRIEVAL_AND_ROUTING
  PRIMARY_INDEXABLE::"name⊕description"
  ANTHROPIC_TOOL_SEARCH::"matches against names and descriptions; clear definitions improve discovery accuracy"
  SERVER_INSTRUCTIONS::"Claude Code emphasises server instructions and descriptive metadata for tool search with many MCP servers"
  §6a::RETRIEVAL_MECHANICS
    BM25::"term overlap; names/descriptions should include user-facing nouns/verbs (invoice, refund, order, customer) and domain constraints (date range, status)"
    DENSE::"semantic similarity, paraphrase robustness; misses exact entity/field matches→hybrid compensates"
  §6b::HYBRID_EVIDENCE
    ELASTIC::"hybrid search balancing BM25F lexical scoring with semantic understanding in single API"
    WEAVIATE::"blends BM25 and vector scores; exposes tuning parameters to weight each component"
    PINECONE::"single-request hybrid query→reduces latency and complexity vs separate indexes"
    ANTHROPIC_OPTIONS::"regex-based and BM25-based tool search out of box; allows custom strategies including embeddings"
    RESEARCH::"BM25 and semantic retrieval are standard approaches for tool selection improvement"
  §6c::GRANULARITY
    TOO_COARSE::"few mega-tools→ambiguous routing⊕broad schemas⊕hidden sub-modes→parameter misuse"
    TOO_FINE::"hundreds of micro-tools→context bloat⊕overlapping names→selection failures"
    CONCRETE_EXAMPLE::"notification-send-user vs notification-send-channel causes ambiguity at scale"
    LANGCHAIN_SIGNAL::"too many tools→poor decisions→motivates multi-agent decomposition"
    TOOLSCOPE::"overlapping names/descriptions introduce ambiguity and degrade selection"
    SWEET_SPOT::"per-decision toolsets small (single-digit to low tens) ⊕ retrieval for scale"
    CLAUDE_TARGET::"3-5 relevant tools per search"
    CLAUDE_TRIGGER::"MCP tool descriptions exceeding 10% context window→forced selective loading"
  §6d::INJECTION_SAFETY
    MITIGATION::"trust boundaries ⊕ runtime enforcement, NOT delimiters"
    WARNINGS::["Claude Code: third-party MCP servers unverified→prompt injection risk (especially untrusted content fetchers)","MCP spec: tool annotations untrusted unless from trusted servers; recommends human-in-the-loop"]
    ENFORCEABLE_CONTROLS::["MCP server allowlist/denylist: allowedMcpServers/deniedMcpServers; denylist takes precedence","tool-level permissions: deny high-risk Bash patterns, constrain WebFetch by domain, OS-level sandboxing","protocol-level: JSON-RPC schemas and error classes; unknown tools and invalid args→protocol errors distinct from execution errors"]
    RULE::"descriptions are routing metadata only — never trusted instructions; keep short, specific, non-executable"
§7::TOOL_GATING_EVIDENCE
  §7a::NARROWING_IMPROVES_FIDELITY
    LESS_IS_MORE::"dynamic tool reduction: execution time -70%, power -40%, success rate up (arXiv 2411.15399)"
    ANTHROPIC_TOOL_SEARCH::"Opus4: 49%→74%, Opus4.5: 79.5%→88.1% MCP eval accuracy"
    TOOLSCOPE::"selection accuracy +8.38% to +38.6% via tool merging⊕context-aware filtering (top-k selection, toolset compression)"
  §7b::FAILURE_MODES_WITHOUT_GATING
    TOOL_SELECTION_HALLUCINATION::"model picks wrong tool→erroneous execution⊕increased computational cost"
    TOOL_USAGE_HALLUCINATION::"model misuses tool or bad arguments→erroneous execution⊕increased cost"
    RETRIEVAL_DEGRADATION::"weak retrieval→degraded end-to-end pass rates; even STRONG IR models perform poorly on tool retrieval"
    CONTEXT_DEGRADATION::"Lost in Middle ⊕ tool definition bloat compounds→harms selection and argument reasoning"
  §7c::TIERED_GATING_PATTERN
§7d::PER_FRAMEWORK_ENFORCEMENT
  CLAUDE_CODE::"permission rules (allow/ask/deny, wildcarded specifiers) for MCP tools⊕subagents; deny takes precedence; allowed-tools⊕disable-model-invocation per skill"
  MCP::"tools/list discovery, tools/call invocation; unknown tool→protocol error; servers MUST validate inputs; clients SHOULD validate results before LLM"
  CREWAI::"per-task tools attribute (agent limited to these); per-task tool gating is first-class"
  LANGCHAIN::"bind_tools required; tool calls from structured fields; tool_choice forces specific tool"
  AUTOGEN::"register_for_llm (proposal) vs register_for_execution (execution)→explicit dispatch/execution boundary; FunctionTool generates schemas from type annotations"
§8::RECOMMENDATIONS
  SKILL_AUTHORS::["names: unique⊕short⊕domain-specific; avoid near-duplicates (notification-send-user vs notification-send-channel)","descriptions: task verbs⊕objects⊕constraints⊕entities (invoice, refund, date range, status); write for retrieval","prefer schema constraints over prose; use strict modes to prevent missing fields/type mismatches","keep in-context bodies short→load reference on demand; SKILL.md under 500 lines"]
  RUNTIME_ENGINEERS::["tiered gating: select→bind→validate→enforce→error-correct; MCP protocol vs execution errors as template","hybrid sparse+dense routing for tool libraries beyond context limits (Elastic/Weaviate/Pinecone + Anthropic Tool Search BM25)","invest in tool-doc quality→retrieval quality directly impacts agent pass rates","treat all tool metadata and outputs as untrusted; MCP requires input validation; sanitise outputs"]
§9::BOTTOM_LINE
  THESIS::"Tool gating and selective loading are not optional optimisations"
  EVIDENCE::"repeatedly shown to improve efficiency⊕correctness across research and vendor evaluations"
  FORMULA::"less tool context → more accuracy ⊕ more performance"
===END===