# Memory and State Design

> **Purpose:** How the research agent stores, passes and discards state and memory: state structure, ownership and lifecycle.
> **Authoritative for:** state and memory design. Graph state types live in `src/open_deep_research/state.py`.
> **Maintained by:** owners of modules that add or change state write a module section (§5); §1–§4 are integrated from those sections before SA Review. Modules that do not touch state add nothing.
> **Last updated:** 2026-11-17

## 1. State Model

Baseline fields are unchanged. New fields are written only when their flag is on and stay empty otherwise. Each field belongs to one module; the nodes that write it are listed in §5, and where there are two they are on different paths of the same run (for example the normal exit and the model-failure exit).

| State type | Graph | New fields | Owning module | Shared contract? |
|---|---|---|---|---|
| `AgentState` | `deep_researcher` | `task_results`, `exit_reason`, `exit_detail` (copied from the supervisor subgraph); `research_outcome`, `outcome_detail`, `failed_tasks` | orchestration; delivery | Yes: read by delivery, evaluation and callers |
| `SupervisorState` | supervisor subgraph | `task_results`, `exit_reason`, `exit_detail`, `stalled_turns` | orchestration | Yes: `task_results` read by delivery |
| `ResearcherState` | researcher subgraph | `task_spec`, `retrieved_urls`, `tool_calls_spent` | orchestration | No |
| `ResearcherOutputState` | researcher subgraph output | `task_result` | orchestration | Yes: read by delivery |

The types `TaskSpec`, `Finding` and `TaskResult` are defined once in `state.py` (ADR-001 §5). A change to them needs the approval of orchestration, delivery and context (`structural-constraints.md` §6).

## 2. Lifecycle

- **Start of a run.** With `task_contract_enabled` on, `write_research_brief` resets `task_results` (override `[]`), `exit_reason` and `exit_detail`. The supervisor subgraph starts from these values.
- **During research.** Each supervisor turn appends its new task results to `task_results` as a plain list (the existing `override_reducer` appends lists). A task result is appended once, by `supervisor_tools`.
- **Inside a researcher.** `task_spec` is set when the researcher subgraph is invoked; `researcher_tools` adds to `retrieved_urls` and `tool_calls_spent`; `compress_research` returns `task_result`. The researcher state is discarded when the subgraph returns.
- **Loop exit.** `supervisor_tools` (or `supervisor` on a model failure) writes `exit_reason`, `exit_detail` and `notes` (override, counted findings only). When the subgraph ends, its `task_results`, `exit_reason` and `exit_detail` are copied to `AgentState`; because the parent list was reset at the start, the copy holds each result once.
- **After research.** `check_research_outcome` writes `failed_tasks`, and on the `failed` path also `research_outcome`, `outcome_detail` and an empty `final_report`. Otherwise `final_report_generation` writes `research_outcome`, `outcome_detail` and `final_report`. `final_report_generation` clears `notes` as in the baseline.
- **Kept fields.** `task_results`, `exit_reason`, `research_outcome`, `outcome_detail` and `failed_tasks` stay in the output until the next run on the same thread resets or overwrites them.

## 3. Context and Memory Limits

| Limit | Value (default) | Kind | Where |
|---|---|---|---|
| `research_model_max_tokens` | 10,000 | output tokens | supervisor and researcher calls |
| `compression_model_max_tokens` | 8,192 | output tokens | `compress_research` |
| `final_report_model_max_tokens` | 10,000 | output tokens | `final_report_generation` |
| `summarization_model_max_tokens` | 8,192 | output tokens | Tavily page summaries |
| `max_content_length` | 50,000 | characters | Tavily page content before summarising |
| `max_react_tool_calls` | 10 | researcher model turns; with `task_contract_enabled` also the tool-call budget of each task | researcher |
| `max_researcher_iterations` | 6 | supervisor turns | supervisor loop |

There is no input-token budget that is checked before a call. Token limits are handled after the provider rejects a request:

- **Compression:** with `context_trimming` on, whole turns are removed from the oldest end and the call is retried (ADR-004); the topic or task brief, the instruction and the newest turn are always kept.
- **Report:** the baseline cuts findings from the end and retries; with `task_contract_enabled` on, this makes the run `partial` and is named in the limitations section (ADR-003).
- **Researcher and supervisor:** a researcher token-limit error fails only its task (ADR-002); a supervisor error ends the loop through `select_exit` (ADR-001).

Checking input size before a call is deferred (EVAL-004 option C, RISK-012).

## 4. Persistence

The deployed graph (`langgraph.json`) is compiled without a checkpointer; the evaluation scripts `test/run_evaluate.py` and `test/supervisor_parallel_evaluation.py` add a `MemorySaver`. When the graph runs on a LangGraph server, the server keeps the thread state between runs. The supervisor and researcher subgraphs are compiled with the default per-invocation mode, so their private fields (`stalled_turns`, the researcher fields) start empty on every call. Nothing is stored outside the graph state.

## 5. Module Sections

### Orchestration (REQ-001, REQ-003, ADR-001)

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `ResearcherState` | `task_spec` | `TaskSpec \| None` | last write | researcher subgraph input built in `supervisor_tools` | `researcher_tools`, `compress_research` | subgraph start → subgraph end |
| `ResearcherState` | `retrieved_urls` | `list[str]` | `operator.add` | `researcher_tools` | `compress_research` | subgraph start → subgraph end |
| `ResearcherState` | `tool_calls_spent` | `int` | last write | `researcher_tools` | `researcher_tools`, `compress_research` | `0` → subgraph end |
| `ResearcherOutputState` | `task_result` | `TaskResult \| None` | last write | `compress_research` | `run_delegations` (delivery) | subgraph end → copied into `task_results` |
| `SupervisorState`, `AgentState` | `task_results` | `list[TaskResult]` | `override_reducer` | `supervisor_tools`; reset by `write_research_brief` | `select_exit`, delivery, evaluation, callers | reset at run start → appended each turn → kept |
| `SupervisorState`, `AgentState` | `exit_reason` | `"covered" \| "budget_exhausted" \| "stalled" \| "failed" \| None` | last write | `supervisor_tools`, or `supervisor` when its model call fails | `check_research_outcome`, `final_report_generation` | reset at run start → set once at loop exit |
| `SupervisorState`, `AgentState` | `exit_detail` | `str` | last write | same as `exit_reason` | delivery | reset at run start → set once at loop exit |
| `SupervisorState` | `stalled_turns` | `int` | last write | `supervisor_tools` | `select_exit` | `0` → subgraph end |

`notes` keeps its type and reducer; with the flag on it is written once at loop exit (by `supervisor_tools`, or `supervisor` on a model failure), as an override, from the counted findings of `complete` and `partial` tasks.

### Delivery (REQ-002, REQ-004, ADR-002, ADR-003)

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `AgentState` | `research_outcome` | `"complete" \| "partial" \| "failed" \| None` | last write | `check_research_outcome` (failed path) or `final_report_generation` | callers, evaluation | set once per run |
| `AgentState` | `outcome_detail` | `str` | last write | same as `research_outcome` | callers | set once per run |
| `AgentState` | `failed_tasks` | `list[TaskResult]` | `override_reducer`, always written as an override | `check_research_outcome` | `final_report_generation`, callers | set once per run |

`run_delegations` keeps no state of its own; its results reach state through `supervisor_tools`.

### Context, citations, search, evaluation

No state. Context trims a local copy of the messages; the stored `researcher_messages` are not changed.
