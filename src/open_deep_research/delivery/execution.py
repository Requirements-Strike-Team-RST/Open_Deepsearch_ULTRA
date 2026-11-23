"""Run, isolate, classify and join the delegated tasks of one supervisor turn.

REQ-002, ADR-002, INV-007, POL-001 to POL-003, POL-005, POL-007. One researcher
exception fails only its own task; delegations above the concurrency limit are
queued and run; the function returns only after every task it started has
finished, with exactly one task result per specification in specification order.
The researcher is passed in as ``run_one``, so this module never imports
``deep_researcher.py``; the task contract comes from ``state.py``.
"""

import asyncio
from typing import Any, Awaitable, Callable, Literal, Mapping, Sequence

from open_deep_research.state import TaskResult, TaskSpec
from open_deep_research.utils import is_token_limit_exceeded


def classify_task_error(
    exc: BaseException, research_model: str
) -> Literal["token_limit", "runtime"]:
    """Map a researcher exception to ``token_limit`` or ``runtime`` (REQ-002, ADR-002 §3 step 3)."""
    if is_token_limit_exceeded(exc, research_model):
        return "token_limit"
    return "runtime"


def _validated_result(output: Any, spec: TaskSpec) -> TaskResult:
    """Return the researcher's ``TaskResult`` for ``spec``, or ``failed/invalid_result`` (POL-007).

    ADR-002 §3 step 3: an output without a ``TaskResult`` of this task is not
    accepted as validated findings.
    """
    raw = output.get("task_result") if isinstance(output, Mapping) else None
    if isinstance(raw, TaskResult) and raw.task_id == spec.task_id:
        return raw
    return TaskResult.failed(
        spec, "invalid_result", "the researcher output holds no valid task result"
    )


def _error_text(exc: BaseException) -> str:
    """Return the error message, or the error type when the message is empty."""
    return str(exc) or type(exc).__name__


async def run_delegations(
    specs: Sequence[TaskSpec],
    run_one: Callable[[TaskSpec], Awaitable[Mapping[str, Any]]],
    *,
    max_concurrent: int,
    research_model: str,
) -> tuple[list[TaskResult], list[str]]:
    """Run the delegations with bounded concurrency and join them (REQ-002, ADR-002 §3, INV-007).

    Every specification starts at once; a semaphore lets at most
    ``max_concurrent`` run and the rest wait for a free slot instead of being
    rejected. Exceptions are collected, never re-raised, so a failed task
    cannot cancel or discard a sibling; ``asyncio.CancelledError`` is re-raised
    so that stopping a run still works. Returns one ``TaskResult`` per
    specification, in specification order, and the ``raw_notes`` of the
    researchers that returned them.
    """
    if not specs:
        return [], []

    limit = asyncio.Semaphore(max(1, int(max_concurrent)))

    async def run_spec(spec: TaskSpec) -> tuple[TaskResult, list[str]]:
        async with limit:
            try:
                output = await run_one(spec)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # isolated: only this task fails
                category = classify_task_error(exc, research_model)
                return TaskResult.failed(spec, category, _error_text(exc)), []
        raw_notes = output.get("raw_notes") if isinstance(output, Mapping) else None
        return _validated_result(output, spec), [str(note) for note in raw_notes or []]

    gathered = await asyncio.gather(
        *(run_spec(spec) for spec in specs), return_exceptions=True
    )

    results: list[TaskResult] = []
    notes: list[str] = []
    for outcome in gathered:
        if isinstance(outcome, BaseException):
            # Only cancellation reaches this point: ``run_spec`` contains every
            # other exception.
            raise outcome
        result, raw_notes = outcome
        results.append(result)
        notes.extend(note for note in raw_notes if note)
    return results, notes
