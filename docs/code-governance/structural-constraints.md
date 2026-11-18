# Structural Constraints

> **Purpose:** The rules every member follows when changing code structure, so that parallel work by six people can be merged.
> **Authoritative for:** source layout, change rules, dependency direction and code-level traceability. *Which* modules exist is decided in `docs/architecture/architecture-blueprint.md` §4; where a specific requirement lands is decided in its ADR.
> **Maintained by:** humans for §1–§9; each module owner writes their module's section in §10, integrated before SA Review.
> **Last updated:** 2026-11-17

## 1. Source Layout

| Path | Role | New work goes here? |
|---|---|---|
| `src/open_deep_research/` | Baseline implementation: `deep_researcher.py` (graphs and nodes), `state.py`, `configuration.py`, `prompts.py`, `utils.py` | Yes |
| `src/open_deep_research/<extension>/` | One extension module per architectural element (blueprint §4) | Yes, by its owner |
| `src/security/` | Supabase JWT and LangGraph auth, loaded through `langgraph.json` | Only with separate review |
| `test/` | Existing LLM- and API-dependent evaluation scripts | No, except `test/evaluation/` |
| `test/evaluation/` | Evaluation module code (REQ-009, REQ-010; ADR-007). Code, not tests | Yes, by the evaluation owner |
| `test/offline/` | Deterministic tests: no network, no LLM calls, run in CI | Yes, primary test location |
| `test/live/` | Tests that call real models or APIs, run on demand | Yes, when a module test case requires it (`verification-constraints.md` §7) |
| `scripts/` | Project tooling used by CI and humans, e.g. `validate_requirements.py` | Only with human approval |

`[tool.setuptools] packages` in `pyproject.toml` lists `open_deep_research` and `test`. A new subpackage (for example `open_deep_research.delivery` or `test.evaluation`) is added to that list in the same PR, or a non-editable install omits it.

## 2. Graphs and Nodes

1. **Thin nodes** (accepted 2026-10-13): graph wiring, node names and node signatures stay in `deep_researcher.py`; a node body calls the module that owns its logic and contains no architectural logic of its own.
2. **Topology:** the three baseline graphs and their nodes (blueprint §3) stay unchanged. Adding or removing a node or edge needs an accepted ADR.
3. **Routing:** nodes choose the next node by returning `Command(goto=...)`, as the baseline nodes do; do not add `add_conditional_edges` for the same decision.

## 3. Tool Assembly

1. Researcher tools have one entry point, `utils.get_all_tools(config)`, which adds core tools (`ResearchComplete`, `think_tool`), then search tools for the configured `SearchAPI` (`utils.get_search_tool`), then MCP tools (`utils.load_mcp_tools`, wrapped by `utils.wrap_mcp_authenticate_tool`; `existing_tool_names` prevents name clashes).
2. `SearchAPI` values are `tavily`, `openai`, `anthropic` and `none`.
3. The supervisor's tools (`ConductResearch`, `ResearchComplete`, `think_tool`) are bound directly in the `supervisor` node.

A new researcher tool is implemented in `utils.py` or the owning extension module and registered through `get_all_tools()`; no node assembles its own tool set.

## 4. Models and API Keys

1. The baseline creates chat models in two places only: the shared `configurable_model` in `deep_researcher.py`, configured per call for `research_model`, `compression_model` and `final_report_model`, and the summarization model in `utils.tavily_search` (`summarization_model`). New code in `src/` reuses these and creates no other model client.
2. API keys are obtained only through `utils.get_api_key_for_model()` (or `utils.get_tavily_api_key()` for Tavily), never read directly.
3. Exception: the evaluation module may create one judge model lazily, inside `test/evaluation/metrics.py`, because it must not import `deep_researcher.py` or `utils.py` (ADR-007; blueprint §6).

## 5. Module Boundaries and Dependency Direction

| Rule | Description |
|---|---|
| One element, one module | Each architectural element in the blueprint maps to exactly one module, and a module takes on no second responsibility. |
| Dependency direction | `deep_researcher.py` → extension modules → shared modules (`state.py`, `configuration.py`, `prompts.py`, `utils.py`). No module imports `deep_researcher.py`, and no extension module imports another extension module. Any exception is recorded in blueprint §6. |
| No logic in configuration and prompts | `prompts.py` holds templates only; `configuration.py` imports no other project module. |
| Extend, never replace | Do not delete baseline nodes, tools or configuration fields, and do not build a parallel implementation of existing behaviour. Fix or extend it in place. |
| Auth is independent | The research graph does not import `src/security/auth.py`. |

## 6. Shared Contracts

A change to a type in `state.py`, or to any interface another owner's module reads, needs the approval of every owner who reads it, recorded in the PR review. Shared contracts introduced by a requirement are defined in that requirement's ADR and covered by the shared contract tests (`verification-constraints.md` §3). The current shared contracts are listed in blueprint §5.

## 7. Safety-Relevant Code

Code implementing a requirement marked `safety_relevant: true` in `requirements.yaml` must:

1. make the decision in deterministic code that does not call a model — the model's output is input to the decision, never the decision itself;
2. have an accepted ADR and a review by a second owner besides the author;
3. have a test that fails when the related invariant is violated.

## 8. Where New Work Goes

1. **Logic for an improvement:** in the owner's extension module, called from the existing node.
2. **Configuration:** a field in `Configuration` (MCP settings in `MCPConfig`) with `x_oap_ui_config` metadata. An improvement that changes runtime behaviour gets one flag so it can be compared with the baseline; requirements that depend on each other and cannot work apart share one flag (blueprint §8 lists the flags). The default stays at the baseline behaviour until the requirements behind the flag are `verified`, and the PR that marks them verified switches the default. A change that only rejects invalid input or only edits prompt text needs no flag.
3. **Prompts:** in `prompts.py`, filled through `format()`. Moving prompts to versioned `prompts/*.yaml` is proposed in blueprint §11.
4. **Dependencies:** declared in `pyproject.toml` with their purpose, locked in `uv.lock`, agreed with the human first.

## 9. Traceability in Code

Every new module and public function names, in its docstring, the requirement ID and the ADR or invariant it implements, for example `REQ-003, ADR-001, INV-003`. Every test module states the RIDs it verifies in its docstring (`verification-constraints.md` §3).

## 10. Module Constraints

One section per module. At integration, check that responsibilities do not overlap, every dependency follows §5 or is listed in blueprint §6, and no two modules write the same state field. Every module below may also use the standard library and the LangChain and LangGraph packages already in `pyproject.toml`.

### orchestration (REQ-001, REQ-003, ADR-001)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/orchestration/`: `contracts.py`, `termination.py` |
| Responsibility | Build task specifications and task results, and decide when the research loop ends |
| Public interface | `build_task_specs`, `render_task_brief`, `extract_urls`, `build_task_result`, `render_result_message`, `render_notes` (`contracts.py`); `coverage`, `select_exit` (`termination.py`) |
| Called from | `supervisor`, `supervisor_tools`, `researcher_tools`, `compress_research` |
| May depend on | `state.py`, `configuration.py`, `prompts.py` |
| Must not depend on | `deep_researcher.py`, other extension modules, any model client |
| Shared contracts | Owns `ConductResearchTask`, `TaskSpec`, `Finding`, `TaskResult` and the helpers in `state.py`; writes the state fields in `memory-design.md` §5 (orchestration) |
| Configuration flag | `task_contract_enabled = False` (shared with delivery); `coverage_threshold = 0.8` |

### delivery (REQ-002, REQ-004, ADR-002, ADR-003)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/delivery/`: `execution.py`, `outcome.py` |
| Responsibility | Run the delegated tasks of a turn with failure isolation and join; decide the run outcome and write the limitations section |
| Public interface | `run_delegations`, `classify_task_error` (`execution.py`); `assess_research`, `finish_outcome`, `render_limitations` (`outcome.py`) |
| Called from | `supervisor_tools` (fan-out), `check_research_outcome`, `final_report_generation` |
| May depend on | `state.py`, `configuration.py`, `utils.is_token_limit_exceeded` |
| Must not depend on | `deep_researcher.py` (the researcher is passed in as `run_one`), other extension modules, any model client |
| Shared contracts | Reads `TaskSpec`, `TaskResult`, `task_results`, `exit_reason`, `exit_detail`; writes `research_outcome`, `outcome_detail`, `failed_tasks` |
| Configuration flag | `task_contract_enabled` (shared with orchestration) |

`supervisor_tools` is edited by both orchestration and delivery: delivery owns the fan-out call (`run_delegations`), orchestration owns everything else in the flag-on branch (ADR-001 §3.4). Agree the edit before changing that function.

### context (REQ-005, ADR-004)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/context/`: `trimming.py`, `recovery.py` |
| Responsibility | Remove whole turns from the oldest end when compression exceeds the token limit, and report an unreducible history as a typed failure |
| Public interface | `split_turns`, `trim_oldest_turn` (`trimming.py`); `compress_with_recovery`, `CompressionFailed` (`recovery.py`) |
| Called from | `compress_research` only |
| May depend on | `utils.is_token_limit_exceeded` |
| Must not depend on | `deep_researcher.py`, `prompts.py`, other extension modules; trimming code calls no model |
| Shared contracts | None added. `compress_research` maps `CompressionFailed` to `TaskResult.failed` (ADR-001) |
| Configuration flag | `context_trimming = False` |

### citations (REQ-006, ADR-005)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/citations/contract.py` |
| Responsibility | Hold the citation format of the research prompts, as text only |
| Public interface | `CITATION_RULES_BLOCK`, `SOURCES_SECTION_POINTER`, `RENUMBER_ACROSS_FINDINGS_INSTRUCTION` |
| Called from | `prompts.py` (dependency exception, blueprint §6) |
| May depend on | nothing |
| Must not depend on | any project module |
| Shared contracts | The citation format used by both prompts and by the findings block of ADR-001 |
| Configuration flag | None; the prompt change is versioned instead (`Prompt.md` §9) |

### search (REQ-007, ADR-006)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/search/validation.py` (REQ-008 will add its own file) |
| Responsibility | Reject an invalid search configuration, or a run without any search tool, before any model or search call |
| Public interface | `load_search_config`, `validate_search_config`, `model_provider`, `require_search_tools`, `SearchConfigError`, `SearchUnavailableError` |
| Called from | `clarify_with_user` and `researcher`, as their first statements (ADR-006 §3.4); the nodes pass in the tools from `utils.get_all_tools` |
| May depend on | `configuration.py` |
| Must not depend on | `deep_researcher.py`, `utils.py`, other extension modules, any model or MCP client |
| Shared contracts | None |
| Configuration flag | None; only invalid configurations are affected |
| Baseline code changed | The dead `len(tools) == 0` guard in `researcher` is replaced by `require_search_tools(tools)` (Discussion #19, U-4). Approved exception to "Extend, never replace" (§5) |

### evaluation (REQ-009, REQ-010, ADR-007)

| Item | Constraint |
|---|---|
| Path | `test/evaluation/`: `metrics.py`, `entry.py`; `test/evaluators.py` stays as a thin adapter |
| Responsibility | Produce valid or `not_evaluable` metric results, and score an existing report without running research |
| Public interface | `MetricResult`, `validate_rating`, `groundedness_ratio`, `evaluate_metrics` (`metrics.py`); `evaluate_existing_report`, `EvaluationInputError`, `main` (`entry.py`) |
| Called from | `test/evaluators.py` (and so `test/run_evaluate.py`); the command line |
| May depend on | `test/prompts.py`, `pydantic`; the judge model SDK only inside `default_judge()` |
| Must not depend on | `open_deep_research.deep_researcher`, `open_deep_research.utils`, any search or MCP module; no model client is created at import |
| Shared contracts | Reads graph output fields only when a caller passes them in; the LangSmith function names and return shapes of `test/evaluators.py` stay the same |
| Configuration flag | None |
| Path | `src/open_deep_research/search/` |
| Responsibility | Resolve and validate a search configuration on each run before a model/search call, decide whether a run has search capability, and classify the MCP load outcome, without model calls or implicit process-environment access during static validation; apply the runtime MCP stop-and-error policy (Proposed, pending SA Review). |
| Public interface | `resolve_search_api(raw_configurable, environ: Mapping) -> SearchAPI` (pure; caller passes the environment snapshot); `resolve_configuration(raw_configurable, environ) -> Configuration` (builds from validated effective inputs, §7.2); `validate_search_configuration(search_api, research_model, mcp) -> None` (raises a domain error); `classify_mcp(mcp: MCPConfig \| None) -> MCPStatus`; `model_provider(model: str) -> str`; `load_mcp_result(config, existing_tool_names) -> McpLoadResult` (MCP load distinction, §8.1a; U-5); `has_search_capability(evidence: SearchEvidence) -> bool` (evaluated after binding, step 4) |
| Called from | `clarify_with_user` (public boundary: effective configuration resolution and static validation only — no tool assembly, MCP loading or native binding) and `researcher` (subgraph boundary, which runs the §8.0 order: validate → assemble → bind → capability → invoke) in `deep_researcher.py` |
| May depend on | `configuration.py` (`Configuration`, `SearchAPI`, `MCPConfig`); an explicit environment snapshot passed by the caller. MCP loading follows the chosen U-5 option: Option A — the module owns the load and does **not** import `utils.load_mcp_tools`; Option B — `utils.load_mcp_tools` (produced by orchestration) yields `McpLoadResult` that is **passed in**, so the module consumes the value and neither imports nor invokes the runtime loader |
| Must not depend on | `deep_researcher.py`, other extension modules, model clients; private LangChain internals; implicit `os.environ` reads; global environment mutation; and, under either option, the `search` module never invokes the runtime MCP loader |
| Shared contracts | None: reads `Configuration`/`MCPConfig` and the assembled tool list as an argument; reads no state field and writes none |
| Configuration flag | None: baseline behaviour is preserved and no new `Configuration` field is added |

REQ-008 (search fallback) will also live in this module and is designed separately; this section covers REQ-007 only. Two call sites are intentional: `clarify_with_user` is the public boundary, and `researcher` is required because the researcher subgraph is compiled and directly invokable (ADR-001 §2.2, §10). `supervisor` binds no search tool and `researcher_tools` is reached only after `researcher` validated, so neither needs a check.

### search — REQ-008 fallback (REQ-008, ADR-002) — Proposed

The REQ-007 responsibilities above are unchanged. REQ-008 adds the following components to the same `search/` module (not yet implemented; Proposed, pending SA Review).

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/search/` (same module as REQ-007) |
| Responsibility | Execute an ordered fallback over configured client-side search sources on eligible failures, classify errors before they are stringified, distinguish empty success from failure, and aggregate an explicit all-sources-failed result. |
| Public interface | `SearchRequest(queries, max_results, topic)`; `SearchSource` adapters (`name`, `async invoke(SearchRequest) -> SearchOutcome`, `load_status`); `FallbackCoordinator.run(req, sources) -> SearchOutcome \| SearchTerminatedFailure \| AllSourcesFailed`; `SearchAttemptFailure(source_name, stage ∈ {LOAD, INVOKE}, classification, detail)`, `SearchTerminatedFailure`, `AllSourcesFailed`, `ErrorClassification(eligible, category)`; a thin tool-facing adapter exposing the coordinator as one stable model-callable search tool |
| Called from | The model-callable search tool registered through `get_all_tools`; invoked during `researcher_tools` tool execution. The **fallback algorithm is not implemented in `deep_researcher.py`** or any orchestration node; the node only dispatches the assembled tool. |
| May depend on | `configuration.py` (ordered fallback list, `MCPConfig`); the structured MCP load result (REQ-007 U-5, or equivalent) passed in by orchestration; the assembled source tools as arguments |
| Must not depend on | `deep_researcher.py`, other extension modules, model clients; native model search (out of scope); direct MCP client use where REQ-007 U-5 Option A already owns loading; `execute_tool_safely` (classification must precede stringification) |
| Shared contracts | **Approval-dependent:** a new `Configuration` field for the ordered fallback list (default empty; D-2) and, under U-5 Option B, the `utils.load_mcp_tools` return type. Both need the affected owners' approval (`§6`). |
| Configuration flag | Ordered fallback list field, default empty = single-source baseline behaviour (architectural intent; ADR-002 §3 notes it is not yet verified). |

REQ-008 follows the same dependency direction as REQ-007 (`deep_researcher.py → search/ → configuration.py`). Native OpenAI/Anthropic search is excluded from fallback (REQ-008 out of scope). The load-stage/invocation-stage distinction and the proposed exception to POL-002 require D-1 approval (ADR-002 §12).
