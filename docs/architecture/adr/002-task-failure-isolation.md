# ADR-002: A researcher failure fails only its own task, and every delegation is run and joined

- **Status:** Proposed
- **Date:** 2026-11-17
- **Module:** delivery
- **Owner:** AlchemyHAN
- **Evaluation:** EVAL-002 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-002 | C-001, C-002, C-003 | One exception must fail one task, not the research phase, and must not discard the findings of sibling tasks. This rules out one `try` block around one `asyncio.gather`. |
| REQ-002 | C-004, C-006, M-001 | Delegations above the concurrency limit must be queued, not rejected, and nothing may still be running when the fan-out returns. This needs a bounded-concurrency primitive and a join point. |
| REQ-002 | C-007, M-002 | Failure text must never reach `notes`. Failures must travel as typed results, not as text. |
| REQ-002 | C-005 | Delegations left when the loop exits end `not_run`. The exit decision belongs to ADR-001; this ADR only needs the result type. |

## 2. Context

Baseline (`deep_researcher.py`, line numbers at commit `daf6947`):

- L289-342: the fan-out runs inside one `try` block whose handler tests `is_token_limit_exceeded(...) or True`, so every researcher exception ends the research phase as if it had finished.
- L305: `asyncio.gather` re-raises the first exception; the findings of siblings that succeeded are lost while those siblings keep running.
- L291-292, L315-321: delegations above `max_concurrent_research_units` are never run; each gets an error string.
- L316-321 (the overflow string), L310 (the placeholder used when `compressed_research` is missing) and L582-585 (the compression placeholder): these texts become `ToolMessage`s and are read into `notes` by `get_notes_from_tool_calls` (`utils.py` L599-601).

The task contract (`TaskSpec`, `TaskResult`) comes from ADR-001 and lives in `state.py`, so this module does not import `orchestration/`.

## 3. Decision

Use EVAL-002 option B: one function in `src/open_deep_research/delivery/execution.py` owns the fan-out. It is active when `task_contract_enabled` is `True` (ADR-001 §3).

```python
async def run_delegations(
    specs: Sequence[TaskSpec],
    run_one: Callable[[TaskSpec], Awaitable[Mapping[str, Any]]],
    *,
    max_concurrent: int,
    research_model: str,
) -> tuple[list[TaskResult], list[str]]
```

1. **Bounded concurrency.** All specs start at once; an `asyncio.Semaphore(max(1, max_concurrent))` lets at most `max_concurrent` run, and the rest wait for a free slot. So the limit queues work instead of rejecting it, and a slow task never holds back a free slot.
2. **Isolation.** Results are collected with `asyncio.gather(..., return_exceptions=True)`, so one failure neither cancels nor discards a sibling.
3. **Classification.** An exception becomes `TaskResult.failed(spec, category, str(exc))`, with category `token_limit` when `utils.is_token_limit_exceeded(exc, research_model)` is true and `runtime` otherwise. A researcher output without a valid `task_result` becomes `failed` with category `invalid_result`.
4. **Cancellation.** `asyncio.CancelledError` is re-raised and never turned into a task result, so stopping a run still works.
5. **Join.** The function returns only after every task it started has finished. It returns exactly one `TaskResult` per spec, in spec order, and the `raw_notes` of the researchers that returned them.

`run_one` is a closure built in `supervisor_tools`: it invokes `researcher_subgraph` with the spec (ADR-001 §3.1) and returns the subgraph output. The rest of the turn — `not_run` results at the cap, `ToolMessage`s, `notes` and the exit decision — is ADR-001 §3.4. `notes` are rendered only from the counted findings of `complete` and `partial` results, so failure and placeholder text cannot reach them (C-007).

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — patch `supervisor_tools` in place | Queuing, classification and join stay inside one long node, so every test has to drive a whole supervisor turn. |
| C — `asyncio.TaskGroup` | A task group cancels the siblings when one child fails, which discards completed findings — the exact loss C-002 forbids. |
| Strict batches of `max_concurrent` | Each batch waits for its slowest task; a semaphore keeps the same limit without the wait. |

The full comparison is in EVAL-002.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `delivery/execution.py` | Run, isolate, classify and join the delegated tasks of one turn | `run_delegations(...)` as in §3 | `supervisor_tools` |
| `delivery/execution.py` | Classify one exception | `classify_task_error(exc, research_model) -> Literal["token_limit", "runtime"]` | `run_delegations` |

Shared contracts used: `TaskSpec`, `TaskResult`, `TaskResult.failed` (ADR-001, `state.py`). No shared contract is added by this ADR.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none of its own. The results are written to `task_results` by `supervisor_tools` (ADR-001).
- **Runtime policies:** POL-001, POL-002, POL-003, POL-005; POL-007 for a missing `task_result`.
- **Invariants:** INV-007; INV-002 for the research phase.
- **Deterministic boundary:** whether a task failed, and with which category, is decided from exceptions and the output shape, never from model text.

## 7. Verification

The cases for REQ-002 are in `verification-constraints.md` §7 (delivery). They call `run_delegations` with fake `run_one` functions that return, raise, sleep or are cancelled, and they need no model or network.

## 8. Consequences

- **Positive:** one researcher failure no longer ends the research phase; findings already paid for are kept; every delegation ends with exactly one result.
- **Negative:** queued delegations now run, so a turn with many delegations costs more tokens and time than the baseline, which rejected them (RISK-002).
- **Neutral:** with the flag off, the baseline fan-out is unchanged.

## 9. Implementation Steps

1. Add `delivery/__init__.py` and `delivery/execution.py` with `run_delegations` and `classify_task_error`; add `open_deep_research.delivery` to `[tool.setuptools] packages`. Docstrings name `REQ-002, ADR-002, INV-007`.
2. In `supervisor_tools`, when `task_contract_enabled` is on, replace the `try` block, the slice, the overflow messages and the `except ... or True` handler with one call to `run_delegations`, as placed in ADR-001 §3.4 step 2. Keep the baseline code for the flag-off path.
3. Run the checks in `verification-constraints.md` §4 and record them in `docs/build-reports/REQ-002.md`.
