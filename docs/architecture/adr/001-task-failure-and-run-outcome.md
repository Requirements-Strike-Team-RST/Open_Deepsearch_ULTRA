# ADR-001: Task failures are isolated, queued and joined, and every run reports a research outcome

- **Status:** Proposed
- **Date:** 2026-11-15
- **Module:** delivery
- **Owner:** AlchemyHAN
- **Evaluation:** EVAL-001, EVAL-002 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-002 | C-001, C-002, C-003, C-004, C-005, C-006, C-007; M-001, M-002 | One exception must stop one task, not the phase; completed siblings must keep their findings; delegations above the concurrency limit must still run; delegations left at exit must end `not_run`; the join must leave nothing pending; failure text must never enter `notes`. These together decide that fan-out needs per-task records and a join point, not a single `try` block. |
| REQ-004 | C-001, C-002, C-003, C-004, C-005, C-006; M-001 | The run output needs `research_outcome` and `failed_tasks`; a failed run must return an empty report and no report-model call; a partial run needs a system-written limitations section. The outcome depends on data from before and after report generation, which decides where the decision lives. |
| REQ-003 (consumed) | C-001, C-002, C-004, C-005 | Provides the exit reason (`covered`, `budget_exhausted`, `stalled`, `failed`) that REQ-004's outcome rule reads. Owned by orchestration; this ADR only consumes it. |
| REQ-001 (consumed) | C-001, C-002, C-003, C-004 | Provides `TaskSpec`, `TaskResult`, the error categories and `derive_task_status`. Owned by orchestration; this ADR only consumes it. |

## 2. Context

The baseline runs the researcher fan-out inside one `try` block in `supervisor_tools` (`src/open_deep_research/deep_researcher.py` L288–342). The handler at L332–342 tests `is_token_limit_exceeded(e, configurable.research_model) or True`, so the condition is always true and every exception ends the research phase as if it had finished. `asyncio.gather` at L305 re-raises the first exception, so the findings of siblings that succeeded are discarded although those siblings keep running and spending tokens. Delegations above `max_concurrent_research_units` are sliced off at L291–292 and answered with an error string at L315–321 instead of being run. The overflow string and the `compress_research` placeholder `"Error synthesizing research report: Maximum retries exceeded"` (L310, L582–585) are stored as `ToolMessage`s and read back into `notes` by `get_notes_from_tool_calls` (`utils.py` L599–601), so report generation receives failure text as if it were a finding.

On the delivery side, the outer graph wires `research_supervisor → final_report_generation` unconditionally (L715) and `AgentState` (`state.py` L65–72) has no field that states whether research succeeded. `final_report_generation` (L607–697) returns its own errors as report text (L670–674, L686–690, L693–697), truncates findings from the end on a token-limit error (L676–682), and still ends the run normally. A caller therefore cannot distinguish a complete run from a failed one, which is the impact reported in upstream #283.

Forces and constraints:

- `structural-constraints.md` §2 keeps the baseline node topology fixed unless an accepted ADR changes it; this ADR is that ADR for exactly one new node.
- `structural-constraints.md` §7 requires the decision to be made by deterministic code that does not call a model; `requirements.yaml` marks both requirements `safety_relevant: true`.
- `structural-constraints.md` §5 requires extension modules not to import `deep_researcher.py`, so everything this module needs must arrive as arguments.
- `verification-constraints.md` §3 requires offline tests with fake researchers and no network, which rules out a design whose units can only be exercised by running the full graph.
- REQ-002 and REQ-004 depend on REQ-001 (task contract) and REQ-004 additionally on REQ-003 (exit reason). Both are owned by the orchestration module, so this module is a consumer of those contracts and must not redefine them.

## 3. Decision

Two cohesive pieces in a new extension module `src/open_deep_research/delivery/`, plus one new graph node, one new state field set and one configuration flag.

**3.1 Task execution (`delivery/execution.py`).** A single async function owns the fan-out, the queue, the join and the isolation:

```python
async def run_delegations(
    *,
    specs: Sequence[TaskSpec],
    researcher: ResearcherCallable,
    config: RunnableConfig,
    max_concurrent: int,
    research_model: str,
    unrun_reason: str = "not_run",
) -> DelegationOutcome
```

It builds one `TaskRunRecord` per spec, runs the specs in batches of `max_concurrent` so that delegations above the limit are queued and eventually executed rather than rejected, collects every batch with `asyncio.gather(..., return_exceptions=True)` so that one failure cannot cancel or discard a sibling, maps each exception to an error category, and always produces exactly one `TaskResult` per `TaskSpec` — including specs it never got to run, which end `failed` with reason `not_run`. It returns a `DelegationOutcome` holding the records, the results, the validated findings that may become notes, and the failures. No exception escapes `run_delegations`; the caller never needs a `try` block around the fan-out.

Error categorisation is deterministic and does not consult the model: a token or context limit that `is_token_limit_exceeded(exc, research_model)` recognises becomes `token_limit`; any other `BaseException` becomes `runtime` with `str(exc)` as the message. A result that fails contract validation becomes `failed` with reason `invalid_result`, as REQ-001 requires; that check is performed by the orchestration contract and its verdict is carried through, not re-implemented.

**3.2 Run outcome (`delivery/outcome.py`).** Two pure functions, both taking a plain mapping and returning a plain mapping, so either can be unit-tested without a graph, a model or a checkpoint:

```python
def evaluate_before_report(state: Mapping) -> OutcomeDecision
def evaluate_after_report(state: Mapping, report: str, *, truncated: bool) -> OutcomeDecision
```

`evaluate_before_report` reads the exit reason (REQ-003), the task results and the source findings, and decides `failed` when the exit reason is `failed` or when no validated finding exists; otherwise it decides `partial` or `complete` when every task result is complete, and `partial` otherwise. It never calls a model. Its `report_allowed` flag is `False` exactly when the outcome is `failed`, which is what lets the graph skip the report model instead of asking it for an empty answer.

`evaluate_after_report` folds in the report stage: a report-generation failure makes the outcome `failed`; `truncated` makes it `partial`; a pre-report `failed` stays `failed`. It then attaches the limitations text produced by `render_limitations` and returns a partial state update with `research_outcome`, `failed_tasks` and `final_report`.

`render_limitations` writes the section deterministically from the failed and partial task results, the unanswered required questions and the truncation flag — never from model output, so a report model that silently drops a failed task cannot hide it. The text is appended after the report body, not merged into the prompt.

**3.3 Graph wiring.** The top-level graph gains one node:

```text
clarify_with_user → write_research_brief → research_supervisor → finalize
finalize ⇄ research_supervisor, final_report_generation  (conditional)
final_report_generation → finalize → END
```

`finalize` is a thin node: it calls `evaluate_before_report`, returns `Command(goto="final_report_generation")` when `report_allowed` is true, and returns `Command(goto=END)` with the failed outcome otherwise; on the second entry it calls `evaluate_after_report` and returns `Command(goto=END)`. Which pass it is in is derived from state (`final_report` presence plus the outcome already being set), not from a counter.

**3.4 Limitation of scope, recorded deliberately.** "No finding was left out of the report" is checked only for findings the system itself withheld — those dropped by report-stage truncation, which the delivery module knows because it performed the truncation. Whether the report model paraphrased or omitted a finding it was given is not parsed out of the report body; deterministic citation and coverage checking of generated reports is out of scope for REQ-006, and this ADR does not widen it. The gap is recorded as a risk in `docs/architecture/risk-list.md`.

**3.5 The flag.** `Configuration.enforce_delivery_outcome: bool = False`. While the flag is `False` the baseline behaviour and the baseline graph shape are used; while it is `True` the execution wrapper, the `finalize` node and the outcome fields are active. The default flips only when REQ-002 and REQ-004 reach `verified` (`structural-constraints.md` §8.2).

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| Patch `supervisor_tools` in place (EVAL-001 A) | Queuing (C-004), join (C-006) and note separation (C-007) would all live inside one node body; every test would have to re-simulate a whole supervisor turn; no record from which `dropped_delegation_count` could be computed. |
| `asyncio.TaskGroup` / structured concurrency (EVAL-001 C) | A task group cancels its siblings when one child fails, which discards a successful sibling's findings — the exact loss C-002 and M-001 forbid. |
| Compute the outcome inside `final_report_generation` from `notes` (EVAL-002 A) | `notes` is free text with no task id, status or reason, so `failed_tasks` cannot be produced; the report model would already have been called before the outcome could say it must not be; the report model would remain the only guard against a failed run looking complete. |
| Dedicated error node behind a conditional edge (EVAL-002 C) | The outcome assembly and the limitations text would be duplicated in two nodes, giving two places that can decide `complete` and two places to keep consistent. |

The full comparison is in EVAL-001 and EVAL-002.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `delivery/execution.py` | Own the fan-out: queue delegations, run them in batches, isolate failures, join every task, emit one `TaskResult` per `TaskSpec` | `async run_delegations(*, specs, researcher, config, max_concurrent, research_model, unrun_reason="not_run") -> DelegationOutcome` | `supervisor_tools` in `deep_researcher.py` |
| `delivery/execution.py` | Categorise an exception deterministically | `classify_task_error(exc: BaseException, research_model: str) -> TaskFailure` | `run_delegations` |
| `delivery/execution.py` | Per-task bookkeeping for scheduling and the drop metric | `TaskRunRecord` (dataclass: `task_id`, `spec`, `state` ∈ {`queued`, `running`, `done`}, `result`, `attempt`) | `run_delegations`; tests |
| `delivery/execution.py` | Return value of the fan-out | `DelegationOutcome` (dataclass: `records`, `results`, `notes`, `failures`; property `dropped_count`) | `supervisor_tools` |
| `delivery/execution.py` | Type of the researcher callable so tests can inject a fake | `ResearcherCallable = Callable[[TaskSpec, RunnableConfig], Awaitable[TaskResult]]` | `supervisor_tools`, tests |
| `delivery/outcome.py` | Decide the outcome before report generation and whether the model may run | `evaluate_before_report(state: Mapping) -> OutcomeDecision` | `finalize` node |
| `delivery/outcome.py` | Fold the report stage into the outcome and produce the final state update | `evaluate_after_report(state, report: str, *, truncated: bool) -> OutcomeDecision` | `finalize` node |
| `delivery/outcome.py` | Write the system limitations section from structured results, never from model text | `render_limitations(outcome: str, results: Sequence[TaskResult], unanswered: Sequence[str], truncated: bool) -> str` | `evaluate_after_report` |
| `delivery/outcome.py` | Pre-report decision value | `OutcomeDecision` (dataclass: `outcome` ∈ {`complete`, `partial`, `failed`}, `report_allowed: bool`, `failed_tasks: list[dict]`, `unanswered: list[str]`, `reason_code: str`) | `finalize` node |
| `deep_researcher.py` | Thin node that applies both decisions to state and routes | `async finalize(state, config) -> Command[Literal["final_report_generation", "__end__"]]` | graph edges |

**Consumed from other modules (not defined here):**

| Type or field | Owner module | Where defined | Why consumed |
|---|---|---|---|
| `TaskSpec`, `TaskResult`, `TaskFailure`, `derive_task_status`, error categories `token_limit` / `runtime` / `not_run` / `invalid_result` | orchestration (centay) | ADR-00X for REQ-001 | REQ-002 and REQ-004 both depend on REQ-001; redefining them here would create two contracts |
| research exit reason (`covered`, `budget_exhausted`, `stalled`, `failed`) | orchestration (centay) | ADR-00X for REQ-003 | `evaluate_before_report` maps exit reason to outcome, as REQ-004 requires |

Shared contracts changed (`structural-constraints.md` §6): `SupervisorState.failed_tasks`, `AgentState.failed_tasks`, `AgentState.research_outcome` and the `DeliveryOutcome`-shaped value that `supervisor_tools` returns. Other modules that read these fields — orchestration (REQ-003 coverage may read task results), and the integrator for the blueprint §5 interface table — must approve in the PR review. No orchestration type is modified by this ADR.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** `SupervisorState.failed_tasks: Annotated[list[dict], operator.add]`; `AgentState.failed_tasks: Annotated[list[dict], operator.add]`; `AgentState.research_outcome: str`. Lifecycle and reducers are in `memory-design.md` §5 (delivery).
- **Runtime policies:** POL-001 (researcher raises), POL-002 (researcher token limit), POL-003 (delegation above the concurrency limit), POL-004 (delegation left unrun at loop exit), POL-005 (report model raises), POL-006 (findings truncated for the report). Details in `runtime-policy-catalog.md` §2 (delivery).
- **Invariants:** INV-002 (no failure is reported as complete research) and INV-006 (every delegated task ends with a terminal result). Details in `invariants.md`.
- **Deterministic boundary:** the outcome (`complete` / `partial` / `failed`), the failed-task list, whether the report model may be called, and the text of the limitations section are all decided by `delivery/outcome.py`, which is pure Python over state and never calls a model. The error category is decided by `classify_task_error`, which inspects the exception, not model output. The model's report body is treated as data; the final output is the model's body concatenated with the system-written limitations section, and the two outcome fields are never model-generated.

## 7. Verification

Every criterion maps to at least one offline case; the cases are listed in `verification-constraints.md` §7 (delivery) as TC-002-xx and TC-004-xx.

| Criterion | How it is verified | Test file |
|---|---|---|
| REQ-002 C-001, C-003 | Fake researcher raising `RuntimeError` / a recognised token-limit error; assert `run_delegations` returns a `failed` `TaskResult` with the right category and message and that no exception escapes | `test/offline/test_failure_propagation.py` |
| REQ-002 C-002 | Two specs, one fake returning a finding, one raising; assert the finding is in `DelegationOutcome.notes` and only the other task is failed | `test/offline/test_failure_propagation.py` |
| REQ-002 C-004 | Three specs, `max_concurrent=1`; assert three `done` records and three `TaskResult`s | `test/offline/test_failure_propagation.py` |
| REQ-002 C-005 | Specs passed with `unrun_reason="not_run"`; assert each ends `failed` with reason `not_run` | `test/offline/test_failure_propagation.py` |
| REQ-002 C-006 | A fake that raises immediately and a fake still pending; assert no `asyncio.Task` from the call is pending after return | `test/offline/test_failure_propagation.py` |
| REQ-002 C-007, M-002 | State built from a failed task and a placeholder-compression task; assert `notes` contains only validated findings and `failed_tasks` holds both failures | `test/offline/test_failure_propagation.py` |
| REQ-002 M-001 | Aggregate `dropped_count` over the C-004 scenario; assert `0` | `test/offline/test_failure_propagation.py` |
| REQ-004 C-001 | Covered exit, all tasks complete; assert `complete`, empty `failed_tasks`, no limitations section | `test/offline/test_run_outcome.py` |
| REQ-004 C-002 | Two tasks, one failed; assert `partial`, the failed task named with its reason, and the limitations section naming it although the fake report model never does | `test/offline/test_run_outcome.py` |
| REQ-004 C-003 | All tasks complete, exit reason `stalled` / `budget_exhausted`; assert `partial` | `test/offline/test_run_outcome.py` |
| REQ-004 C-004 | No validated finding; assert `failed`, `report_allowed` false, empty `final_report`, fake report model not called | `test/offline/test_run_outcome.py` |
| REQ-004 C-005 | Fake report model raising a non-token-limit error; assert `failed` with that reason and empty `final_report` | `test/offline/test_run_outcome.py` |
| REQ-004 C-006 | Report-stage truncation; assert `partial` and a limitations line stating findings were left out | `test/offline/test_run_outcome.py` |

Live evidence: REQ-004's criteria are all offline-scriptable with fake models, so no live case is added by this ADR. REQ-003 C-006 (live baseline queries) stays with orchestration.

## 8. Consequences

**Positive**

- A single researcher failure can no longer end the research phase, and findings already paid for are kept, which removes the silent-truncation path of upstream #283.
- Every delegation has a terminal result, so "how many tasks were dropped" becomes a number the system reports rather than an absence nobody notices.
- The outcome is a field of the run output, so a caller can tell complete from partial or failed without reading the report.
- The limitations section is written by code from structured results, so a cooperative-sounding report model cannot hide a failure.
- Queuing above the concurrency limit turns a rejection into work, without raising the concurrency and so without raising peak rate-limit pressure.

**Negative**

- The top-level graph gains a node and three edges; the "topology stays unchanged" rule now has one recorded exception, which every later reader of the blueprint must see.
- `finalize` runs twice; readers unfamiliar with the design may expect one pass, so the docstring must state the two-pass contract.
- Three new fields in `state.py` widen a shared contract that another owner also edits, so the merge order with the orchestration branch matters.
- Batched queuing makes a turn with many delegations slower than the baseline's "run some, reject the rest", although it spends the tokens the baseline discarded.

**Neutral**

- With `enforce_delivery_outcome=False` the behaviour is the baseline, so existing suites are unaffected until the flag is switched.
- `run_delegations` takes the researcher callable as an argument, so `researcher_subgraph` remains constructed and owned by `deep_researcher.py` and no module imports the graph builder.

## 9. Implementation Steps

The coding agent implements these in order; each step names the files it changes. Steps 1–4 are delivery-local and can be committed separately from steps 5–8.

1. **Create the module skeleton.** Add `src/open_deep_research/delivery/__init__.py` exporting `run_delegations`, `classify_task_error`, `TaskRunRecord`, `DelegationOutcome`, `ResearcherCallable`, `evaluate_before_report`, `evaluate_after_report`, `render_limitations`, `OutcomeDecision`. Add `"open_deep_research.delivery"` to `packages` in `pyproject.toml` (`[tool.setuptools]`), or a non-editable install omits the subpackage. Module docstring: `REQ-002, REQ-004, ADR-001, INV-002, INV-006`.

2. **Add the task-execution types** to `src/open_deep_research/delivery/execution.py`: `TaskRunRecord` (dataclass, `task_id`, `spec`, `state`, `result`, `attempt`), `DelegationOutcome` (dataclass, `records`, `results`, `notes`, `failures`, property `dropped_count` counting records whose `result` is `None` or whose `result.status == "failed"` with reason `not_run`), and the `ResearcherCallable` alias. Import `TaskSpec`, `TaskResult`, `TaskFailure` from the orchestration contract module; do not copy those types.

3. **Implement `classify_task_error`** in `delivery/execution.py`: return a `TaskFailure` of category `token_limit` when `is_token_limit_exceeded(exc, research_model)` from `open_deep_research.utils` is true, otherwise category `runtime`, with `str(exc)` as the message. Catch `BaseException` at the call site but re-raise `asyncio.CancelledError` so cancellation still propagates.

4. **Implement `run_delegations`** in `delivery/execution.py` as decided in §3.1: batch by `max_concurrent` (clamp to at least 1), one record per spec, `asyncio.gather(..., return_exceptions=True)` per batch, classify exceptions, build one `TaskResult` per spec, collect notes only from results whose findings are validated, and end unrun specs as `failed` with `unrun_reason`. Assert before returning that no record is left `queued` or `running`. Docstring names `REQ-002, ADR-001, INV-002, INV-006`.

5. **Add the state fields** to `src/open_deep_research/state.py`: `failed_tasks: Annotated[list[dict], operator.add]` on both `SupervisorState` and `AgentState`, and `research_outcome: str` on `AgentState`. Do not change existing fields. Mention `REQ-002, REQ-004, ADR-001` in the surrounding comment or docstring.

6. **Implement the outcome functions** in `src/open_deep_research/delivery/outcome.py` as decided in §3.2: `OutcomeDecision`, `evaluate_before_report`, `evaluate_after_report`, `render_limitations`. The functions take and return plain mappings; they import no LangGraph or model client and read the exit reason and task results from state keys agreed with orchestration. Docstring names `REQ-004, ADR-001, INV-002`.

7. **Add the configuration flag** `enforce_delivery_outcome: bool = Field(default=False, metadata={"x_oap_ui_config": {"type": "boolean", "default": False, "description": "..."}})` to `src/open_deep_research/configuration.py`, with the description in the same style as the neighbouring fields. Default stays `False` (`structural-constraints.md` §8.2).

8. **Rewire `supervisor_tools`** in `src/open_deep_research/deep_researcher.py`: keep the `think_tool` handling and the exit conditions; replace the `try` block, the slice, the overflow messages and the `except ... or True` handler with one call to `run_delegations`, passing a `researcher` callable that invokes `researcher_subgraph` for a spec; turn `DelegationOutcome.results` into `ToolMessage`s (one per call, so no tool call is left unanswered) and `DelegationOutcome.notes` into `raw_notes`; set `failed_tasks` from `DelegationOutcome.failures`. When the exit conditions hold, pass the current turn's delegations as unrun specs so they end `not_run` before returning to `END`. Guard all of this with `configurable.enforce_delivery_outcome`.

9. **Add the `finalize` node** to `deep_researcher.py`: a thin async function that calls `evaluate_before_report`, returns `Command(goto="final_report_generation")` when `report_allowed`, otherwise `Command(goto=END, update={...})`; on the second pass calls `evaluate_after_report` and returns `Command(goto=END, update={...})`. Handle the state update in the same shape the other nodes use (a `dict` or a `Command.update`).

10. **Wire the graph** in `deep_researcher.py`: `add_node("finalize", finalize)`, replace the edge `research_supervisor → final_report_generation` with `research_supervisor → finalize` plus a conditional edge from `finalize` to `final_report_generation` or `END`, and add `final_report_generation → finalize` and `finalize → END` for the second pass. Keep `clarify_with_user` and its early `END` untouched. When `enforce_delivery_outcome` is `False`, compile the baseline graph instead, or make `finalize` a pass-through, choosing the one that leaves the baseline behaviour identical.

11. **Make `final_report_generation` report truncation instead of swallowing it.** When a token-limit truncation occurs, record that findings were left out and pass it to `evaluate_after_report` (through `OutcomeDecision`/state), and return an empty `final_report` plus the error only in the failure fields when the exception is not a token limit; do not return error text as report content. Keep the node's retries and the `enforce_delivery_outcome` guard so the baseline path is unchanged while the flag is off.

12. **Check.** Run `uv run python scripts/validate_requirements.py`, `uv run ruff check src/open_deep_research`, `uv run ruff format` on the new and changed files only, and `uv run pytest test/offline`. Re-run the existing suites named in `verification-constraints.md` §7 (delivery) and record the commands and results in `docs/build-reports/REQ-002.md` and `docs/build-reports/REQ-004.md`.

13. **Do not** change the approved tests, the acceptance thresholds, or any file outside the delivery module, `state.py`, `configuration.py`, `deep_researcher.py` and `pyproject.toml`. If an interface in this ADR cannot be implemented as written, stop and report it: that is an architecture change (`Prompt.md` §10).
