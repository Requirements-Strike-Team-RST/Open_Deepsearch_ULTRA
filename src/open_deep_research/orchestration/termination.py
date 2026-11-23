"""Coverage of the research brief and the single exit reason of the research loop.

REQ-003, ADR-001 §3.4, INV-003: the model's ``ResearchComplete`` call and a turn
without tool calls are requests, never decisions. Only ``select_exit``, running
on validated task results, ends the loop, and every exit records exactly one
reason. No function in this module calls a model.
"""

from typing import Optional, Sequence

from open_deep_research.state import (
    ExitReason,
    answered_questions,
    normalize_question,
)

STALL_LIMIT = 2


def _questions_of(result) -> list:
    """Return the required questions of one task result, contract type or plain record."""
    return list(getattr(result, "must_answer", None) or [])


def _required_questions(results: Sequence) -> set[str]:
    """Return the normalised required questions of every task result."""
    questions: set[str] = set()
    for result in results or []:
        for question in _questions_of(result):
            questions.add(normalize_question(question))
    return questions


def _answered_keys(results: Sequence) -> set[str]:
    """Return the normalised questions a counted finding answers."""
    return {normalize_question(question) for question in answered_questions(results)}


def coverage(results: Sequence) -> float:
    """Return the share of required questions with at least one counted finding.

    REQ-003, ADR-001 §3.4: the ratio counts distinct questions across all task
    results of the run, including failed and ``not_run`` ones, and is ``0`` when
    no question was delegated.
    """
    required = _required_questions(results)
    if not required:
        return 0.0
    return len(required & _answered_keys(results)) / len(required)


def select_exit(
    before: Sequence,
    after: Sequence,
    *,
    stalled_turns: int,
    turn_is_eligible: bool,
    cap_reached: bool,
    supervisor_error: bool,
    threshold: float,
) -> tuple[Optional[ExitReason], int]:
    """Decide whether the research loop ends and with which reason.

    Returns ``(reason, stalled_turns)``. The reasons are checked in the order
    ``covered`` > ``budget_exhausted`` > ``stalled`` > ``failed``; ``None`` means
    the loop continues. ``before`` and ``after`` are the task results before and
    after the turn. A turn that is not eligible (a ``think_tool``-only turn)
    leaves the stall counter as it is; an eligible turn adds 1 when the number
    of answered questions did not grow and resets the counter when it grew.
    """
    required = _required_questions(after)
    if required and coverage(after) >= threshold:
        # ADR-001 §3.4 step 4.1: `covered` is first in the precedence order, so
        # a run whose task results settle the ratio ends here with a reset stall
        # counter, whatever this turn did.
        return "covered", 0

    if cap_reached:
        return "budget_exhausted", stalled_turns

    counter = stalled_turns
    if turn_is_eligible:
        grew = len(_answered_keys(after)) > len(_answered_keys(before))
        counter = 0 if grew else stalled_turns + 1
    if counter >= STALL_LIMIT:
        return "stalled", counter

    if supervisor_error:
        return "failed", counter

    return None, counter
