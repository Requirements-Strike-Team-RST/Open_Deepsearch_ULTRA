"""Decide the run outcome and write the limitations section.

REQ-004, ADR-003, INV-002, POL-015 to POL-017. ``assess_research`` decides before
the report whether the report model may run at all; ``finish_outcome`` decides
after it, because only then are report errors and truncation known;
``render_limitations`` builds the limitations text from structured task results.
All three are pure: no I/O, no model, no mutation of their arguments.
"""

from dataclasses import dataclass, field
from typing import Optional, Sequence

from open_deep_research.state import (
    ResearchOutcome,
    TaskResult,
    unanswered_questions,
)

LIMITATIONS_HEADING = "## Limitations"


@dataclass
class OutcomeDecision:
    """The pre-report decision of ADR-003 §3.2."""

    outcome: ResearchOutcome
    report_allowed: bool
    detail: str = ""
    failed_tasks: list[TaskResult] = field(default_factory=list)


def _answered(result: TaskResult) -> bool:
    """Return ``True`` when a task produced at least one validated finding."""
    return getattr(result, "status", None) in ("complete", "partial") and bool(
        getattr(result, "findings", None)
    )


def assess_research(
    task_results: Sequence[TaskResult],
    exit_reason: Optional[str],
    exit_detail: str,
) -> OutcomeDecision:
    """Decide the run outcome before the report (ADR-003 §3.2).

    ``failed`` when the research loop exited with reason ``failed`` or when no
    task result holds a validated finding; ``complete`` when the exit reason is
    ``covered`` and every task result is ``complete``; ``partial`` otherwise.
    """
    results = list(task_results or [])
    failed_tasks = [
        result for result in results if getattr(result, "status", None) == "failed"
    ]
    if exit_reason == "failed":
        return OutcomeDecision(
            outcome="failed",
            report_allowed=False,
            detail=exit_detail or "the research loop failed",
            failed_tasks=failed_tasks,
        )
    if not any(_answered(result) for result in results):
        return OutcomeDecision(
            outcome="failed",
            report_allowed=False,
            detail=exit_detail or "no validated finding was produced",
            failed_tasks=failed_tasks,
        )
    if exit_reason == "covered" and all(
        getattr(result, "status", None) == "complete" for result in results
    ):
        return OutcomeDecision(
            outcome="complete",
            report_allowed=True,
            detail="",
            failed_tasks=failed_tasks,
        )
    return OutcomeDecision(
        outcome="partial",
        report_allowed=True,
        detail=exit_detail,
        failed_tasks=failed_tasks,
    )


def finish_outcome(
    decision: OutcomeDecision,
    *,
    report_error: Optional[str],
    findings_truncated: bool,
) -> tuple[ResearchOutcome, str]:
    """Decide the final outcome after the report (ADR-003 §3.3).

    A report error makes the run ``failed`` and its text goes to
    ``outcome_detail``; findings that had to be cut to fit the report model make
    the run ``partial`` at best; otherwise the pre-report outcome stands.
    """
    if report_error:
        return "failed", report_error
    if decision.outcome == "failed":
        return "failed", decision.detail
    if findings_truncated:
        return "partial", "findings were left out of the report"
    return decision.outcome, decision.detail


def render_limitations(
    task_results: Sequence[TaskResult],
    findings_truncated: bool,
) -> str:
    """Build the limitations section a partial report carries (ADR-003 §3.3).

    One line per failed or partial task with its reason, the unanswered required
    questions, and a line when findings were left out of the report. The text is
    built from structured results only; the report model never writes it.
    """
    results = list(task_results or [])
    lines: list[str] = []
    for result in results:
        status = getattr(result, "status", None)
        if status not in ("failed", "partial"):
            continue
        reason = (
            getattr(result, "reason", "")
            or getattr(result, "failure_category", "")
            or "unknown reason"
        )
        lines.append(f"- Task {result.task_id} ({status}): {reason}")
    missing = unanswered_questions(results)
    for question in missing:
        lines.append(f"- Unanswered required question: {question}")
    if findings_truncated:
        lines.append("- Some findings were left out of the report to fit the model.")
    if not lines:
        return ""
    return LIMITATIONS_HEADING + "\n\n" + "\n".join(lines) + "\n"
