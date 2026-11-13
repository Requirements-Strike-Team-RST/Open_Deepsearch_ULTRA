# Structural Constraints

> **Purpose:** The rules every member follows when changing code structure, so that parallel work by six people can be merged.
> **Authoritative for:** source layout, change rules, dependency direction and code-level traceability. *Which* modules exist is decided in `docs/architecture/architecture-blueprint.md` §4; where a specific requirement lands is decided in its ADR.
> **Maintained by:** humans for §1–§9; each module owner writes their module's section in §10, integrated before SA Review.
> **Last updated:** 2026-11-13

## 1. Source Layout

| Path | Role | New work goes here? |
|---|---|---|
| `src/open_deep_research/` | Baseline implementation: `deep_researcher.py` (graphs and nodes), `state.py`, `configuration.py`, `prompts.py`, `utils.py` | Yes |
| `src/open_deep_research/<extension>/` | One extension module per architectural element (blueprint §4) | Yes, by its owner |
| `src/security/` | Supabase JWT and LangGraph auth, loaded through `langgraph.json` | Only with separate review |
| `test/` | Existing LLM- and API-dependent evaluation scripts | No |
| `test/offline/` | Deterministic tests: no network, no LLM calls, run in CI | Yes, primary test location |
| `test/live/` | Tests that call real models or APIs, run on demand | Yes, when a module test case requires it (`verification-constraints.md` §7) |
| `scripts/` | Project tooling used by CI and humans, e.g. `validate_requirements.py` | Only with human approval |

`[tool.setuptools] packages` in `pyproject.toml` lists `open_deep_research` and `test`. A new extension subpackage is added to that list in the same PR, or a non-editable install omits it.

## 2. Graphs and Nodes

1. **Thin nodes** (accepted 2026-10-13): graph wiring, node names and node signatures stay in `deep_researcher.py`; a node body calls the module that owns its logic and contains no architectural logic of its own.
2. **Topology:** the three baseline graphs and their nodes (blueprint §3) stay unchanged. Adding or removing a node or edge needs an accepted ADR.

## 3. Tool Assembly

1. Researcher tools have one entry point, `utils.get_all_tools(config)`, which adds core tools (`ResearchComplete`, `think_tool`), then search tools for the configured `SearchAPI` (`utils.get_search_tool`), then MCP tools (`utils.load_mcp_tools`, wrapped by `utils.wrap_mcp_authenticate_tool`; `existing_tool_names` prevents name clashes).
2. `SearchAPI` values are `tavily`, `openai`, `anthropic` and `none`.
3. The supervisor's tools (`ConductResearch`, `ResearchComplete`, `think_tool`) are bound directly in the `supervisor` node.

A new researcher tool is implemented in `utils.py` or the owning extension module and registered through `get_all_tools()`; no node assembles its own tool set.

## 4. Models and API Keys

1. The baseline creates chat models in two places only: the shared `configurable_model` in `deep_researcher.py`, configured per call for `research_model`, `compression_model` and `final_report_model`, and the summarization model in `utils.tavily_search` (`summarization_model`). New code reuses these and creates no other model client.
2. API keys are obtained only through `utils.get_api_key_for_model()` (or `utils.get_tavily_api_key()` for Tavily), never read directly.

## 5. Module Boundaries and Dependency Direction

| Rule | Description |
|---|---|
| One element, one module | Each architectural element in the blueprint maps to exactly one module, and a module takes on no second responsibility. |
| Dependency direction | `deep_researcher.py` → extension modules → shared modules (`state.py`, `configuration.py`, `prompts.py`, `utils.py`). No module imports `deep_researcher.py`. Any exception is recorded in blueprint §6. |
| No logic in configuration and prompts | `prompts.py` holds templates only; `configuration.py` imports no other project module. |
| Extend, never replace | Do not delete baseline nodes, tools or configuration fields, and do not build a parallel implementation of existing behaviour. Fix or extend it in place. |
| Auth is independent | The research graph does not import `src/security/auth.py`. |

## 6. Shared Contracts

A change to a type in `state.py`, or to any interface another owner's module reads, needs the approval of every owner who reads it, recorded in the PR review. Shared contracts introduced by a requirement are defined in that requirement's ADR and covered by the shared contract tests (`verification-constraints.md` §3).

## 7. Safety-Relevant Code

Code implementing a requirement marked `safety_relevant: true` in `requirements.yaml` must:

1. make the decision in deterministic code that does not call a model — the model's output is input to the decision, never the decision itself;
2. have an accepted ADR and a review by a second owner besides the author;
3. have a test that fails when the related invariant is violated.

## 8. Where New Work Goes

1. **Logic for an improvement:** in the owner's extension module, called from the existing node.
2. **Configuration:** a field in `Configuration` (MCP settings in `MCPConfig`) with `x_oap_ui_config` metadata. An improvement that changes runtime behaviour gets one flag so it can be compared with the baseline; the default stays at the baseline behaviour until the requirement is `verified`, and the PR that marks it verified switches the default.
3. **Prompts:** in `prompts.py`, filled through `format()`. Moving prompts to versioned `prompts/*.yaml` is proposed in blueprint §11.
4. **Dependencies:** declared in `pyproject.toml` with their purpose, locked in `uv.lock`, agreed with the human first.

## 9. Traceability in Code

Every new module and public function names, in its docstring, the requirement ID and the ADR or invariant it implements, for example `REQ-003, ADR-002, INV-003`. Every test module states the RIDs it verifies in its docstring (`verification-constraints.md` §3).

## 10. Module Constraints

Copy the example for your module. At integration, check that responsibilities do not overlap, every dependency follows §5 or is listed in blueprint §6, and no two modules write the same state field.

### <Module> (REQ-NNN, ADR-NNN)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/<module>/` |
| Responsibility | One sentence; what the module decides or produces |
| Public interface | Functions and types other code may call |
| Called from | Nodes or modules that call it, e.g. `supervisor_tools` in `deep_researcher.py` |
| May depend on | e.g. `state.py`, `configuration.py`, `utils.py` |
| Must not depend on | e.g. `deep_researcher.py`, other extension modules, model clients in deterministic code |
| Shared contracts | Types or state fields it reads or writes that other modules also use |
| Configuration flag | `Configuration` field that switches the behaviour, and its default (§8) |

### context (REQ-005, ADR-005)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/context/` with `__init__.py`, `messages.py`, `trimming.py`, `classification.py`, `recovery.py`; added to `[tool.setuptools] packages` in `pyproject.toml` in the same PR |
| Responsibility | Decide, without calling a model, which whole research turns to remove when compression exceeds the model token limit, classify token-limit errors for the invoked compression model, and report an unreducible history as a typed failure instead of a summary |
| Public interface | `segment_turns()`, `TurnLayout`, `ResearchTurn` (`messages.py`); `plan_trim()`, `TrimPlan` (`trimming.py`); `classify_token_limit()` (`classification.py`); `compress_with_recovery()`, `CompressionOutcome`, `TokenLimitExceeded` (`recovery.py`); exported through `context/__init__.py` only |
| Called from | `compress_research` in `deep_researcher.py` (the token-limit branch), and nothing else |
| May depend on | `langchain_core.messages`, `configuration.py` (`Configuration` values passed in as arguments, not constructed), `utils.py` (`is_token_limit_exceeded`, `filter_messages` usage pattern) |
| Must not depend on | `deep_researcher.py`, `prompts.py`, any other extension module (`orchestration/`, `delivery/`, `search/`, `citations/`), any model client, any network call, and `src/security/` |
| Shared contracts | Reads `ResearcherState.researcher_messages`; returns `compressed_research` and `raw_notes` in their existing types and format. The failed `token_limit` result uses the REQ-001 task-result type; ADD-005 §5 requires the orchestration owner's approval before implementation. Adds no state field |
| Purity rule | `segment_turns`, `plan_trim` and `classify_token_limit` are pure: no I/O, no model, no logging of message content, no mutation of the input list. `compress_with_recovery` is the only coroutine and the only place that awaits a model |
| Configuration flag | `context_trimming: bool = False` (baseline behaviour preserved until REQ-005 is `verified`; the flipping PR is separate) |
| Baseline code touched | `compress_research` body in `deep_researcher.py` (becomes thin, baseline branch kept verbatim under `context_trimming = False`); docstring correction only in `utils.remove_up_to_last_ai_message`. `state.py` and `prompts.py` unchanged; `utils.is_token_limit_exceeded` behaviour unchanged because `final_report_generation` also uses it |