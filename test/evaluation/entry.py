"""Score an existing report without running research or search.

REQ-010, ADR-007 §3, POL-023. ``evaluate_existing_report`` rejects blank input
before any judge call and then hands the report to the metric groups;
``python -m test.evaluation.entry --question ... --report <file>`` prints the
result as JSON. This module imports neither the research graph module nor the
shared search utility module, so it never builds the graph, never opens a search
client and needs no search key.
"""

# The command's output is standard output and its errors go to standard error;
# ruff reports ``print`` by default, which is the point of a command line here.
# ruff: noqa: T201

import argparse
import dataclasses
import hashlib
import json
import sys
from dataclasses import dataclass, field
from typing import Optional, Sequence

from test.evaluation.metrics import MetricResult, default_judge, evaluate_metrics

EXIT_OK = 0
EXIT_INPUT_ERROR = 2


class EvaluationInputError(ValueError):
    """The question or the report is missing, blank or not text (POL-023)."""


@dataclass
class EvaluationResult:
    """The per-metric result of one scored report (ADR-007 §3)."""

    report_id: str
    metrics: list[MetricResult] = field(default_factory=list)

    def as_dict(self) -> dict:
        """Return the JSON-friendly form the command prints."""
        return {
            "report_id": self.report_id,
            "metrics": [dataclasses.asdict(metric) for metric in self.metrics],
        }


def _checked(name: str, value) -> str:
    """Return a non-blank string, or raise ``EvaluationInputError`` for ``name``."""
    if not isinstance(value, str) or not value.strip():
        raise EvaluationInputError(f"{name} must be non-blank text")
    return value


def evaluate_existing_report(
    question: str,
    report: str,
    *,
    reference_answer: Optional[str] = None,
    research_brief: Optional[str] = None,
    evidence: Optional[str] = None,
    judge=None,
) -> EvaluationResult:
    """Score ``report`` against ``question`` without running research (REQ-010, ADR-007 §3).

    A blank or non-string question or report raises ``EvaluationInputError``
    before any judge call. ``report_id`` is the SHA-256 of the report text, so
    the result names exactly the report that was scored.
    """
    question = _checked("the question", question)
    report = _checked("the report", report)
    metrics = evaluate_metrics(
        question,
        report,
        reference_answer=reference_answer,
        research_brief=research_brief,
        evidence=evidence,
        judge=judge,
    )
    report_id = hashlib.sha256(report.encode("utf-8")).hexdigest()
    return EvaluationResult(report_id=report_id, metrics=list(metrics))


def _parser() -> argparse.ArgumentParser:
    """Return the command-line parser of the evaluation entry."""
    parser = argparse.ArgumentParser(
        prog="python -m test.evaluation.entry",
        description="Score an existing report without running research.",
    )
    parser.add_argument("--question", required=True, help="the research question")
    parser.add_argument("--report", required=True, help="path to the report file")
    parser.add_argument("--reference-answer", default=None)
    parser.add_argument("--research-brief", default=None)
    parser.add_argument("--evidence", default=None)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the command and return its exit code (ADR-007 §3, POL-023).

    ``0`` when the report was scored, ``2`` on an input error. The per-metric
    result is printed as JSON on standard output.
    """
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        with open(args.report, encoding="utf-8") as handle:
            report = handle.read()
    except OSError as exc:
        print(f"cannot read the report file: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    try:
        # POL-023: blank input is rejected before a judge client is even created.
        _checked("the question", args.question)
        _checked("the report", report)
        result = evaluate_existing_report(
            args.question,
            report,
            reference_answer=args.reference_answer,
            research_brief=args.research_brief,
            evidence=args.evidence,
            judge=default_judge(),
        )
    except EvaluationInputError as exc:
        print(f"invalid evaluation input: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    print(json.dumps(result.as_dict(), ensure_ascii=False))
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - exercised through ``main``
    raise SystemExit(main())
