# ADR-001: A researcher failure fails only its own task, and every delegation is run and joined

- **Status:** Proposed
- **Date:** 2026-11-15
- **Module:** delivery
- **Owner:** AlchemyHAN
- **Evaluation:** EVAL-001 and EVAL-002 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance
- **Split:** this ADR records the failure-handling decision of EVAL-001. The graph-shape decision of EVAL-002 is recorded separately in ADR-002, so that a change to the topology is reviewed on its own.

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-002 | C-001, C-002, C-003, C-004, C-005, C-006, C-007; M-001, M-002 | One exception must stop one task, not the phase; completed siblings must keep their findings; delegations above the concurrency limit must still run; delegations left unrun at loop exit must end `not_run`; the join must leave nothing pending; failure text must never enter `notes`. Together these decide that the fan-out needs per-task records, a bounded concurrency primitive and a join point, instead of one `try` block. |
| REQ-001 (consumed) | C-001, C-002, C-003, C-004 | Supplies the task contract — `TaskSpec`, `TaskResult`, the error categories, task-status derivation. Owned by orchestration; placed in the shared `state.py` so neither module imports the other (§5), and the `task_results` field that carries the results to later nodes is defined with that owner (ADR-002 §3.2). |
| REQ-003 (consumed) | C-004, C-005 | Owns the loop-exit decision, i.e. which delegations count as unrun. This module only produces their `not_run` results. |

## 2. Context

`supervisor_tools` (`src/open_deep_research/deep_researcher.py` L288–342) runs the researcher fan-out inside one `try` block. The handler at L332–342 tests `is_token_limit_exceeded(e, configurable.research_model) or True`, so it is always true and every exception ends the research phase as if it had finished. `asyncio.gather` at L305 re-raises the first exception, so the findings of siblings that succeeded are discarded although those siblings keep running and spending tokens. Delegations above `max_concurrent_research_units` are sliced off at L291–292 and answered with an error string at L315–321 instead of being run. The overflow string and the `compress_research` placeholder `"Error synthesizing research report: Maximum retries exceeded"` (L310, L582–585) are stored as `ToolMessage`s and read back into `notes` by `get_notes_from_tool_calls` (`utils.py` L599–601), so report generation receives failure text as if it were a finding.

Forces:

- `structural-constraints.md` §7 requires the decision to be made by deterministic code that does not call a model; REQ-002 is `safety_relevant: true`.
- `structural-constraints.md` §5 forbids a dependency between two extension modules, so the task contract cannot be imported from `orchestration/`.
- `verification-constraints.md` §3 requires offline tests with fake researchers, so the unit under test must not be the whole node.
- `supervisor_tools` is also edited by orchestration for REQ-003. Two owners in one function is a coordination hazard, so §5 fixes the split explicitly.

## 3. Decision

**3.1 One function owns the fan-out (`delivery/execution.py`):**

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

It launches every spec at once and bounds concurrency with an `asyncio.Semaphore(max_concurrent)`, so a slow task never holds back a free slot and peak concurrency stays at the configured limit. It collects every result with `asyncio.gather(..., return_exceptions=True)`, so one failure can neither cancel nor discard a sibling. It maps each exception to an error category and always produces exactly one `TaskResult` per `TaskSpec`, including specs it was told to leave unrun, which end `failed` with an error category and reason of `not_run`. It returns a `DelegationOutcome` with the records, the results, the validated findings that may become notes, and the failures. No exception escapes `run_delegations` except `asyncio.CancelledError`.

**3.2 Deterministic categorisation.** A token or context limit that `is_token_limit_exceeded(exc, research_model)` recognises becomes an error category of `token_limit`; any other `BaseException` becomes `runtime`, with `str(exc)` as the message. A result that fails contract validation becomes `failed` with reason `invalid_result`, as REQ-001 requires: that check belongs to the contract and its verdict is carried through, not re-implemented here.

**3.3 Notes carry findings only.** `DelegationOutcome.notes` holds only validated findings. Failure text, overflow text and the compression placeholder are attached to a `TaskResult` instead, so they can never reach report generation as a finding.

**3.4 The unrun case is split by ownership.** Which delegations count as unrun is decided by the research loop (orchestration, REQ-003). Producing their `not_run` results is this module's job, through `run_delegations(unrun_reason="not_run")`. Delivery never decides to exit the loop.

**3.5 The flag.** `Configuration.enforce_delivery_outcome: bool = False`. While it is `False`, `supervisor_tools` keeps its baseline body; while it is `True`, the fan-out region calls `run_delegations`. The graph shape is not this ADR's concern (ADR-002), and the import-time compilation at L719 means the flag cannot select a topology.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| Patch `supervisor_tools` in place (EVAL-001 A) | Concurrency limiting (C-004), join (C-006) and note separation (C-007) would all live inside one node body; every test would have to re-simulate a whole supervisor turn; no record from which `dropped_delegation_count` could be computed. |
| `asyncio.TaskGroup` / structured concurrency (EVAL-001 C) | A task group cancels its siblings when one child fails, discarding a successful sibling's findings — the exact loss C-002 and M-001 forbid. |
| Strictly sequential batches of `max_concurrent` (a variant of EVAL-001 B) | A batch waits for its slowest task before the next starts, so concurrency drops to the slowest task's pace; a semaphore over one `gather` keeps the limit without the stall, at the same complexity. |
| Importing `TaskSpec` / `TaskResult` from `orchestration/` | A dependency between two extension modules, forbidden by `structural-constraints.md` §5. The types live in the shared `state.py` instead (§5). |
| Converting `asyncio.CancelledError` into a failed task result | It would turn a user cancellation or a shutdown into a research finding, and would make `run_delegations` swallow the signal LangGraph uses to stop a run. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `state.py` (shared) | Home of the task contract and the field that carries the results across the subgraph boundary | `TaskSpec`, `TaskResult`, `TaskFailure`, `derive_task_status`; `SupervisorState.task_results` / `AgentState.task_results` (ADR-002 §3.2) | `delivery/`, `orchestration/`, `deep_researcher.py` |
| `delivery/execution.py` | Own the fan-out: bound concurrency, isolate failures, join every task, emit one `TaskResult` per `TaskSpec` | `async run_delegations(*, specs, researcher, config, max_concurrent, research_model, unrun_reason="not_run") -> DelegationOutcome` | the fan-out region of `supervisor_tools` |
| `delivery/execution.py` | Categorise an exception deterministically | `classify_task_error(exc: BaseException, research_model: str) -> TaskFailure` | `run_delegations` |
| `delivery/execution.py` | Per-task bookkeeping for scheduling and the drop metric | `TaskRunRecord` (dataclass: `task_id`, `spec`, `state` ∈ {`queued`, `running`, `done`}, `result`) | `run_delegations`; tests |
| `delivery/execution.py` | Return value of the fan-out | `DelegationOutcome` (dataclass: `records`, `results`, `notes`, `failures`; property `dropped_count` = the number of specs that have **no terminal `TaskResult` at all**) | the fan-out region of `supervisor_tools` |
| `delivery/execution.py` | Type of the researcher callable so tests can inject a fake | `ResearcherCallable = Callable[[TaskSpec, RunnableConfig], Awaitable[TaskResult]]` | `supervisor_tools`, tests |

**Code ownership inside `supervisor_tools`.** The node is edited by two modules. This split is binding for both ADRs.

| Region of `supervisor_tools` | Owner | Contract |
|---|---|---|
| Exit-condition evaluation (iteration cap, no tool calls, `ResearchComplete`) and the early return | orchestration (REQ-003) | When it returns early, it passes the turn's `ConductResearch` calls to `run_delegations` with `unrun_reason="not_run"` so delivery produces their results. The exit decision is never made by delivery. |
| `think_tool` handling | unchanged | Neither module rewrites it. |
| The `ConductResearch` fan-out — the `try` block, the slice at L291–292, the overflow messages at L315–321, the `asyncio.gather` at L305 | delivery (REQ-002) | Replaced by one `run_delegations` call, guarded by `enforce_delivery_outcome`. |
| Building `ToolMessage`s from the results, setting `raw_notes`, and appending every `TaskResult` to `task_results` | delivery (REQ-002) | One `ToolMessage` per `ConductResearch` call, so no tool call is left unanswered. `task_results` is a state field (ADR-002 §3.2) because only state crosses the subgraph boundary; a returned `DelegationOutcome` would be dropped. |
| The `failed_tasks` write | `finalize` (ADR-002) | Not written inside `supervisor_tools`; it is derived from `task_results`. |

Shared contracts changed (`structural-constraints.md` §6): `TaskSpec`, `TaskResult`, `TaskFailure`, `derive_task_status` added to `state.py`. Owners who must approve: orchestration (REQ-001), the integrator (blueprint §5), and delivery. If the orchestration ADR already defines the contract, that definition is adopted verbatim in `state.py`; nothing is renamed.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** `task_results` is written from this module's fan-out region (field defined with orchestration, ADR-002 §3.2). No other state is added by this ADR; `failed_tasks` is derived by ADR-002's `finalize`. `DelegationOutcome` and `TaskRunRecord` are in-process values of a single node execution.
- **Runtime policies:** POL-001 (researcher raises), POL-002 (researcher token limit), POL-003 (delegation above the concurrency limit), POL-004 (delegation left unrun at loop exit). POL-005 to POL-007 belong to ADR-002. Details in `runtime-policy-catalog.md` §2 (delivery).
- **Invariants:** INV-002 conditions S1–S4 (failure isolation, sibling results kept, join, notes separation) and INV-006 (every delegation ends with a terminal result). Details in `invariants.md`.
- **Deterministic boundary:** which task fails, with which error category, and whether a delegation ran at all are decided by `classify_task_error` and `run_delegations` from exceptions and records — never from model output.

## 7. Verification

| Criterion | How it is verified | Test file |
|---|---|---|
| REQ-002 C-001, C-003 | Fake researcher raising `RuntimeError` / a recognised token-limit error; assert a `failed` result with the right category and message and that no exception escapes | `test/offline/test_failure_propagation.py` |
| REQ-002 C-002 | Two specs, one returning a finding, one raising; the finding is in `DelegationOutcome.notes`, only the other task is failed | `test/offline/test_failure_propagation.py` |
| REQ-002 C-004, M-001 | Three specs, `max_concurrent=1`; three `done` records, three results, `dropped_count == 0`, peak concurrency never above 1 | `test/offline/test_failure_propagation.py` |
| REQ-002 C-005 | Specs passed with `unrun_reason="not_run"`; each ends `failed` with an error category and reason of `not_run`, and `dropped_count == 0` because each has a terminal result (M-001) | `test/offline/test_failure_propagation.py` |
| REQ-002 C-006 | One fake raises immediately, a sibling is still pending; no `asyncio.Task` from the call is pending after return | `test/offline/test_failure_propagation.py` |
| REQ-002 C-007, M-002 | A failed task and a placeholder-compression task; `notes` holds only validated findings, both failures sit in the results | `test/offline/test_failure_propagation.py` |
| INV-006 | Every spec has exactly one terminal result; no record left `queued` or `running` | `test/offline/test_failure_propagation.py` |

## 8. Consequences

**Positive**

- A single researcher failure can no longer end the research phase, and findings already paid for are kept — the silent-truncation path of upstream #283 is removed.
- Every delegation has a terminal result, so "how many tasks were dropped" becomes a reported number instead of an absence.
- A semaphore keeps peak concurrency at the configured limit without a slow task holding back the rest, so queuing costs time only in proportion to the work.
- The task contract in `state.py` lets orchestration and delivery evolve without a module-to-module import.

**Negative**

- `supervisor_tools` is edited by two modules, so integration must merge that function against the ownership table rather than pick one side.
- Concurrency above the limit now runs work the baseline rejected, so a turn spends tokens it used to discard (RISK-004).
- A wider return value from the fan-out (tool messages plus notes plus failures) makes the node body longer than a single `gather`.

**Neutral**

- With `enforce_delivery_outcome=False` the behaviour is the baseline.
- `run_delegations` takes the researcher callable as an argument, so `researcher_subgraph` stays owned by `deep_researcher.py`.

## 9. Implementation Steps

The coding agent implements these in order; each step names the files it changes.

1. **Add the task contract to the shared state module.** In `src/open_deep_research/state.py`, add `TaskSpec`, `TaskResult`, `TaskFailure` (Pydantic models, beside the other structured outputs) and `derive_task_status`. If the orchestration branch already added them, adopt that definition verbatim. Docstring names `REQ-001, ADR-001`. This is the only definition; `delivery/` imports it from `state.py` and must not import from `orchestration/`.

2. **Create the module skeleton.** Add `src/open_deep_research/delivery/__init__.py` exporting `run_delegations`, `classify_task_error`, `TaskRunRecord`, `DelegationOutcome`, `ResearcherCallable`. Add `"open_deep_research.delivery"` to `packages` in `pyproject.toml` (`[tool.setuptools]`), or a non-editable install omits the subpackage. Module docstring: `REQ-002, ADR-001, INV-002, INV-006`.

3. **Add the execution types** to `delivery/execution.py`: `TaskRunRecord`, `DelegationOutcome` (with `dropped_count` counting records whose result is missing or whose status is `failed` with reason `not_run`), and the `ResearcherCallable` alias.

4. **Implement `classify_task_error`**: return a `TaskFailure` with an error category of `token_limit` when `is_token_limit_exceeded(exc, research_model)` from `open_deep_research.utils` is true, otherwise `runtime`, with `str(exc)` as the message.

5. **Implement `run_delegations`** as decided in §3.1: one record per spec, an `asyncio.Semaphore` bounding `max_concurrent` (clamp to at least 1), all specs launched at once, one `asyncio.gather(..., return_exceptions=True)`, every exception classified, one `TaskResult` per spec, notes taken only from results whose findings are validated, specs that must not run ended `failed` with an error category and reason of `not_run`. Compute `dropped_count` as the number of records that have **no terminal `TaskResult`** — a `not_run` result is terminal, so it is not counted as dropped. Assert before returning that no record is left `queued` or `running`. Let `asyncio.CancelledError` propagate. Docstring names `REQ-002, ADR-001, INV-002, INV-006`.

6. **Rewire only the fan-out inside `supervisor_tools`** in `src/open_deep_research/deep_researcher.py`, respecting the ownership table in §5. Keep the exit-condition evaluation, the early return and the `think_tool` handling as they are; if orchestration's ADR changes them, take that version. Replace only the `try` block, the slice, the overflow messages and the `except ... or True` handler with one `run_delegations` call whose `researcher` argument invokes `researcher_subgraph` for a spec. Build one `ToolMessage` per `ConductResearch` call from `DelegationOutcome.results`, set `raw_notes` from `DelegationOutcome.notes`, and **append every `TaskResult` to the `task_results` state field** (ADR-002 §3.2) — do not return `DelegationOutcome.failures` expecting a later node to read it, because only state fields cross the subgraph boundary. Guard the new path with `configurable.enforce_delivery_outcome`, leaving the baseline body intact for the `False` case.

7. **Add the configuration flag** `enforce_delivery_outcome: bool = Field(default=False, metadata={"x_oap_ui_config": {"type": "boolean", "default": False, "description": "..."}})` to `src/open_deep_research/configuration.py`, in the style of the neighbouring fields. The default stays `False` (`structural-constraints.md` §8.2).

8. **Check.** Run `uv run python scripts/validate_requirements.py`, `uv run ruff check src/open_deep_research`, `uv run ruff format` on the new and changed files only, and `uv run pytest test/offline`. Record the commands and results in `docs/build-reports/REQ-002.md`.

9. **Do not** change the approved tests, the acceptance thresholds, or any file outside `delivery/execution.py`, `state.py`, `configuration.py` and the fan-out region of `deep_researcher.py`. If the interface cannot be implemented as written, or `supervisor_tools` turns out to be owned differently than in §5, stop and report it: that is an architecture change (`Prompt.md` §10).
