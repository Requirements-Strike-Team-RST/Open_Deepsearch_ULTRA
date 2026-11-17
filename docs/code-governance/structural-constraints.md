# Structural Constraints

> **Purpose:** The rules every member follows when changing code structure, so that parallel work by six people can be merged.
> **Authoritative for:** source layout, change rules, dependency direction and code-level traceability. *Which* modules exist is decided in `docs/architecture/architecture-blueprint.md` §4; where a specific requirement lands is decided in its ADR.
> **Maintained by:** humans for §1–§9; each module owner writes their module's section in §10, integrated before SA Review.
> **Last updated:** 2026-11-12

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

### orchestration (REQ-001, REQ-003; EVAL-002, ADR-002 — Proposed)

This module section is a design proposal, not approval to write source or tests. ADR-002 defines the interfaces; shared-reader review and Gates 1–2 remain required.

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/orchestration/` with `contracts.py` (spec/result parsing, validation, rendering and final snapshots), `budget.py` (ordered admission and execution-capability policy), `evidence.py` (one per-task factual receipt, completion observations and snapshots), `termination.py` (coverage and exit selection), and a thin `__init__.py`. Add the package to setuptools in the later implementation PR; no new dependency is proposed. |
| Responsibility | Produce typed task contracts from valid delegation intents, derive status from retrieved-source findings, enforce actual local tool-call budgets, and decide bounded supervisor termination. Queueing, sibling isolation/join and run outcome remain delivery responsibilities; trimming remains context's. |
| Types defined once | All orchestration public and state-carried types, including `ConductResearchV2`, `TaskSpec`, `Source`, `Finding`, `TaskCost`, `TaskResult`, `RunRecord`, `TaskExecutionEvidence` and serializable receipt types, are defined in `state.py`. Extension modules import them; `state.py` and `configuration.py` never import extension modules. Preserve `TaskCost.tool_calls/input_tokens/output_tokens`; the proposed additive `usage_complete: bool=False` marks incomplete token totals. Preserve the original `ConductResearch` class. New state fields are explicit additive changes to the state classes. |
| Public interface | `build_task_spec(tool_call, task_id, config)`, `render_task_message(spec) -> str`, `build_task_result(spec, compression_text, *, evidence)`, `validate_task_result(output, spec, *, evidence)`, `failed_result(spec, category, message, *, evidence)`, `not_run_result(spec)`, `render_supervisor_result(result)`, computed `RunRecord.unanswered_questions()`, and the pure coverage/selector/finalization interfaces in ADR-002 §5. Callers wrap the rendered text in `HumanMessage`. A started task's failure helper requires its evidence; only `not_run_result` has known zero cost. |
| Called from | Existing `supervisor` tool binding/model-failure adapter; `supervisor_tools` registration, cap entry and joined end-of-turn adapter; `researcher_tools` admission/recording adapter; `compress_research` success/failure adapter. Nodes retain their signatures and graph topology. Delivery receives validators/factories/renderers as node-injected callables at its proposed JoinedTurn port, preserving dependency direction; context returns raw compression text to the node adapter. |
| May depend on | Shared `state.py`, `configuration.py` and existing tool/model utilities at their existing adapter boundaries. `contracts.py` and `termination.py` decisions are deterministic and make no model, search or network call. Existing model construction and key helpers remain the sole entry points (§4). |
| Must not depend on | `deep_researcher.py`, `security/`, `delivery/`, `context/`, `citations/`, or `search/` from inside `orchestration/`; no reverse import from a shared module. Shared-node adapters coordinate context and orchestration without introducing extension-to-extension imports. Do not implement delivery scheduling/outcomes, context trimming, search fallback or a final-report citation validator here. |
| Evidence ownership | The node/dispatch boundary allocates and retains a distinct code-owned receipt per accepted task, passing that mapping to the delivery collector; a copied child invocation config injects it only under `_orchestration_evidence`. The wrapper retains it through exceptions. Never share one mutable child config across tasks, send receipts to a model, or trust model/serialized result claims as retrieval evidence. Clean ambient RunnableConfig as well as bound model config, and execute/await each model coroutine in the clean context (§3.2 of ADR-002); omission from .with_config alone is insufficient. State stores serializable `task_evidence_snapshot` data, not live collector objects; no process-crash exactly-once guarantee is proposed. |
| Shared contracts and reducers | Delivery's `update_payload["task_results"]` is a plain per-turn delta, appended by the existing reducer; final `task_results` and `notes` use explicit override envelopes inside SupervisorState. The compiled child returns plain lists, appended once to the parent channels already cleared by write_research_brief; no override envelope crosses that boundary. Final main snapshots carry run fields together; private `completed_supervisor_turns`, `unchanged_eligible_turns`, `delegation_receipts` and task evidence do not propagate to main. RegisteredDelegation and JoinedTurn are runtime DTOs, not new persisted channels. Collector result order follows original accepted call order regardless of completion order, and no task handle crosses this port. Review every public shape/signature change with all readers. |
| Compression protocol | Keep context's `CompressionOutcome.summary: str`. The node passes it through the strict `<task_findings_v1>` fenced-JSON sidecar parser specified in ADR-002 before returning `compressed_research` and TaskResult.summary rendered only from complete/partial tasks' validated findings/sources; discard the raw free-text compression body from reader-facing strings. The sidecar precedes the unique final `### Sources` section; source entries are `[n] Title: URL`. Producer always fills compressed_research/raw_notes/task_result. A valid typed result with a missing legacy string is canonically rendered by the consumer, never filled with a placeholder; a missing/invalid typed result fails. No sidecar/schema/error text or free summary enters final notes; notes are rendered from validated claims/sources only. Prompt insertion needs the citations owner's review and preserves one sources heading and existing format calls. |
| Delegation admission | After §3.5 accepts a control response as normal, every well-identified raw `ConductResearch` intent receives a terminal receipt and matching ToolMessage. A whole-response completion rejection has only a node-private operation diagnostic and no registered intents or fabricated IDs. A malformed/missing call ID rejects the transport turn before registration, retains a raw diagnostic outside model history and uses bounded replanning feedback without inventing a tool ID. Validate before dispatch: malformed input is a recorded rejection without invented questions; only a schema-valid registered TaskSpec is counted as an accepted delegation. This interpretation and diagnostic interface remain a reader-review item. Replay uses the receipt key and never duplicates or relabels a terminal task. |
| Configuration flag | Add `orchestration_enabled: bool = False` and finite `coverage_threshold` with `0 < value <= 1` (proposed default 0.8). Preserve all flag-off orchestration paths. Native search is rejected before a request only when orchestration is enabled until strict pre-request caps and auditable counts exist; do not alter the search validator or switch provider. The four orchestration/context flag combinations and the off/on failure boundary require shared review. |
| Response-completion boundary | Node-owned observing Runnable records logical attempts before context converts response content to a string. Keep the same model argument, CompressionOutcome.summary:str, DTOs and helper parameters. Observer returns/re-raises unchanged and does not trigger output-length retries. Accept known normal compression once; length maps to failed/token_limit, unknown to failed/runtime, both without parsing or extra calls. Supervisor/researcher reject unusable control intents through existing failure boundaries. Phase-specific adapter support and report handling remain reader-review items; delivery alone decides report outcome. |
| Shared edit boundaries | Centay owns contract/termination/budget adapters and typed compression result creation; delivery owns dispatch/gather/except and report outcome; context owns compression recovery; citations owns citation prompt format. Shared-node and prompt edits require those owners' review. On/on compression uses one context retry owner, never nested retry loops. ADR-002 §9 supplies implementation steps; no baseline line-number ownership is assumed. |
