"""Valid, bounded metric results for the research-report evaluators.

REQ-009, ADR-007 §3, INV-009. The judge supplies ratings and claim judgements;
this module decides with code whether they are valid and what the score is.
Every metric either scores in ``[0, 1]`` or is explicitly ``not_evaluable``:
nothing is clamped, defaulted to zero or silently parsed from a looser type.
Each metric group runs in its own ``try/except`` (POL-022), so one broken group
never hides the others.

The module creates no model client at import (POL-020): ``default_judge`` builds
the baseline judge on first use, and an injected judge is used instead in tests.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field

from test.prompts import (
    COMPLETENESS_PROMPT,
    CORRECTNESS_PROMPT,
    GROUNDEDNESS_PROMPT,
    OVERALL_QUALITY_PROMPT,
    RELEVANCE_PROMPT,
    STRUCTURE_PROMPT,
)

SCORED = "scored"
NOT_EVALUABLE = "not_evaluable"


class InvalidMetricInput(ValueError):
    """A raw value a metric cannot turn into a valid score (ADR-007 §3)."""


@dataclass
class MetricResult:
    """One metric's result (ADR-007 §3).

    ``status`` is ``scored`` or ``not_evaluable``; ``score`` is a float in
    ``[0, 1]`` when ``scored`` and ``None`` otherwise; ``reason`` explains a
    ``not_evaluable`` result and carries the judge's own comment when scored.
    """

    metric: str
    status: str
    score: Optional[float]
    reason: str = ""


def _today() -> str:
    """Return today's date as text for the prompt's ``{today}``.

    ADR-007 §3: the module must not import ``open_deep_research.utils``, so it
    uses the standard library instead of ``utils.get_today_str``.
    """
    return date.today().strftime("%Y-%m-%d")


def validate_rating(raw) -> float:
    """Return ``raw / 5`` for an integer rating 1-5, else raise ``InvalidMetricInput``.

    ADR-007 §3: only ``type(raw) is int`` and ``1 <= raw <= 5`` is accepted.
    Booleans (which are ``int`` subclasses), floats including ``4.0``, strings,
    ``None``, ``NaN`` and infinities are refused, never clamped or defaulted.
    """
    if type(raw) is not int:  # noqa: E721 - a bool is an int subclass
        raise InvalidMetricInput(
            f"a rating must be an integer 1-5, not {type(raw).__name__}: {raw!r}"
        )
    if not 1 <= raw <= 5:
        raise InvalidMetricInput(f"a rating must be between 1 and 5, not {raw!r}")
    return raw / 5


def groundedness_ratio(claims: Sequence) -> float:
    """Return grounded claims / all claims, or raise ``InvalidMetricInput``.

    ADR-007 §3: the claim list must be non-empty and each ``grounded`` value
    must be a real boolean, so a missing claim or a truthy string is refused
    instead of counting as grounded.
    """
    items = list(claims or [])
    if not items:
        raise InvalidMetricInput("groundedness needs at least one claim")
    grounded = []
    for claim in items:
        flag = getattr(claim, "grounded", None)
        if type(flag) is not bool:  # noqa: E721 - a bool field is required
            raise InvalidMetricInput(
                "every claim needs a boolean 'grounded' value, not "
                f"{type(flag).__name__}: {flag!r}"
            )
        grounded.append(flag)
    return sum(1 for flag in grounded if flag) / len(grounded)


###################
# Judge schemas (strict, typed for the JSON schema sent to the judge)
###################
class _Strict(BaseModel):
    """Base for the judge schemas: strict mode refuses a looser value (ADR-007 §3)."""

    model_config = ConfigDict(strict=True)


class OverallQualityScore(_Strict):
    """Score the overall quality of the report against specific criteria."""

    research_depth: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria)."
    )
    source_quality: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria)."
    )
    analytical_rigor: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria)."
    )
    practical_value: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria)."
    )
    balance_and_objectivity: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria)."
    )
    writing_quality: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria)."
    )


class RelevanceScore(_Strict):
    """Score the report relevance against specific criteria."""

    reasoning: str = Field(
        description="The reason for the score, including specific examples from the report."
    )
    score: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria for relevance (1 = doesn't meet at all, 5 = meets all criteria)."
    )


class StructureScore(_Strict):
    """Score the report structure against specific criteria."""

    reasoning: str = Field(
        description="The reason for the score, including specific examples from the report."
    )
    score: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria for structure and flow (1 = doesn't meet at all, 5 = meets all criteria)."
    )


class CorrectnessScore(_Strict):
    """Score the report correctness against specific criteria."""

    reasoning: str = Field(
        description="The reason for the score, including specific examples from the report."
    )
    score: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria for correctness (1 = doesn't meet at all, 5 = meets all criteria)."
    )


class CompletenessScore(_Strict):
    """Score the report completeness against specific criteria."""

    reasoning: str = Field(
        description="The reason for the score, including specific examples from the report."
    )
    score: int = Field(
        description="Integer score 1-5 showing whether the report meets the provided criteria for completeness (1 = doesn't meet at all, 5 = meets all criteria)."
    )


class GroundednessClaim(_Strict):
    """A claim from the report, and whether or not it is grounded in the context."""

    claim: str = Field(description="The claim extracted from the report.")
    grounded: bool = Field(description="Whether the claim is grounded in the context.")


class GroundednessScore(_Strict):
    """Extract the claims and whether they are grounded in the context."""

    claims: list[GroundednessClaim] = Field(
        description="All claims extracted from the report, and whether or not they are grounded in the context."
    )


###################
# The default judge (created on first use, never at import)
###################
def default_judge():
    """Return the baseline judge client (ADR-007 §3, POL-020).

    Created on first use, so importing this module or ``test/evaluators.py``
    makes no client and needs no key. The client is the baseline ``ChatOpenAI``
    model; the shared model of ``deep_researcher`` is not imported because this
    module must not import the research graph or ``utils``.
    """
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model="gpt-4.1")


###################
# Input handling
###################
def _present(value) -> bool:
    """Return ``True`` when an optional input is a non-blank string."""
    return isinstance(value, str) and bool(value.strip())


def _text(value) -> str:
    """Return a missing optional input as empty text."""
    return value if isinstance(value, str) else ""


def _ask(judge, schema, messages):
    """Ask the judge one schema-bound question."""
    return judge.with_structured_output(schema).invoke(messages)


def _ask_with_retry(judge, schema, messages):
    """Ask the judge with the baseline's three attempts (the groundedness evaluator)."""
    return (
        judge.with_structured_output(schema)
        .with_retry(stop_after_attempt=3)
        .invoke(messages)
    )


def _message(content: str) -> dict:
    """Return one chat message (a mapping is what the baseline passes)."""
    return {"role": "user", "content": content}


def _rated(metric: str, raw, comment: str = "") -> MetricResult:
    """Return a scored result for a rating 1-5, or ``not_evaluable`` when it is invalid."""
    try:
        return MetricResult(metric, SCORED, validate_rating(raw), comment)
    except InvalidMetricInput as exc:
        return MetricResult(metric, NOT_EVALUABLE, None, str(exc))


def _group_failed(metric: str, exc: Exception) -> MetricResult:
    """Return ``not_evaluable`` for a judge call that raised (POL-022)."""
    return MetricResult(metric, NOT_EVALUABLE, None, f"the judge call failed: {exc}")


def _needs(metric: str, missing: str) -> MetricResult:
    """Return ``not_evaluable`` because the metric's input is missing."""
    return MetricResult(
        metric, NOT_EVALUABLE, None, f"the metric needs {missing}, which is missing"
    )


###################
# Metric groups
###################
QUALITY_KEYS = (
    ("research_depth", "research_depth_score"),
    ("source_quality", "source_quality_score"),
    ("analytical_rigor", "analytical_rigor_score"),
    ("practical_value", "practical_value_score"),
    ("balance_and_objectivity", "balance_and_objectivity_score"),
    ("writing_quality", "writing_quality_score"),
)


def _overall_quality(question: str, report: str, judge) -> list[MetricResult]:
    """Score the six overall-quality dimensions in one judge call."""
    prompt = _report_request(question, report)
    try:
        result = _ask(
            judge,
            OverallQualityScore,
            [
                {
                    "role": "system",
                    "content": OVERALL_QUALITY_PROMPT.format(today=_today()),
                },
                _message(prompt),
            ],
        )
    except Exception as exc:  # noqa: BLE001 - one group's failure stays contained
        return [_group_failed(metric, exc) for _field, metric in QUALITY_KEYS]
    return [
        _rated(metric, getattr(result, field, None)) for field, metric in QUALITY_KEYS
    ]


def _single(
    metric: str,
    messages: list[dict],
    schema,
    judge,
) -> MetricResult:
    """Score one dimension: the judge's rating, or ``not_evaluable`` on any error."""
    try:
        result = _ask(judge, schema, messages)
    except Exception as exc:  # noqa: BLE001 - one group's failure stays contained
        return _group_failed(metric, exc)
    return _rated(
        metric, getattr(result, "score", None), str(getattr(result, "reasoning", ""))
    )


def _report_request(question: str, report: str) -> str:
    """Return the baseline user message that carries the question and the report."""
    return f"""User input: {question}\n\nReport: \n\n{report}\n\nEvaluate whether the report meets the criteria and provide detailed justification for your evaluation."""


def evaluate_metrics(
    question: str,
    report: str,
    *,
    reference_answer: Optional[str] = None,
    research_brief: Optional[str] = None,
    evidence: Optional[str] = None,
    judge=None,
) -> list[MetricResult]:
    """Score a report and return one ``MetricResult`` per metric (REQ-009, ADR-007 §3).

    Every metric sees the question and the report; correctness also sees the
    reference answer, completeness the research brief and groundedness the
    evidence (raw notes). A metric whose optional input is missing is
    ``not_evaluable`` and the others still run; so is a metric whose judge call
    raised. ``judge`` is injected by tests; without it the default judge is
    created on first use.
    """
    if judge is None:
        judge = default_judge()
    question = _text(question)
    report = _text(report)

    results: list[MetricResult] = []
    results.extend(_overall_quality(question, report, judge))

    results.append(
        _single(
            "relevance_score",
            # The baseline sends the relevance rubric as the system message.
            [
                {"role": "system", "content": RELEVANCE_PROMPT.format(today=_today())},
                _message(_report_request(question, report)),
            ],
            RelevanceScore,
            judge,
        )
    )
    results.append(
        _single(
            "structure_and_cohesiveness_score",
            [
                _message(
                    STRUCTURE_PROMPT.format(
                        user_question=question, report=report, today=_today()
                    )
                )
            ],
            StructureScore,
            judge,
        )
    )

    if _present(reference_answer):
        results.append(
            _single(
                "correctness_score",
                [
                    _message(
                        CORRECTNESS_PROMPT.format(
                            user_question=question,
                            report=report,
                            answer=reference_answer,
                            today=_today(),
                        )
                    )
                ],
                CorrectnessScore,
                judge,
            )
        )
    else:
        results.append(_needs("correctness_score", "a reference answer"))

    if _present(evidence):
        # ADR-007 §3: groundedness gets the question too; its template has no
        # placeholder for it, so the question precedes the template text.
        request = (
            f"<user_question>\n{question}\n</user_question>\n"
            + GROUNDEDNESS_PROMPT.format(context=evidence, report=report)
        )
        try:
            judged = _ask_with_retry(judge, GroundednessScore, [_message(request)])
            ratio = groundedness_ratio(getattr(judged, "claims", None))
            results.append(
                MetricResult("groundedness_score", SCORED, ratio, str(judged.claims))
            )
        except InvalidMetricInput as exc:
            results.append(
                MetricResult("groundedness_score", NOT_EVALUABLE, None, str(exc))
            )
        except Exception as exc:  # noqa: BLE001 - one group's failure stays contained
            results.append(_group_failed("groundedness_score", exc))
    else:
        results.append(_needs("groundedness_score", "the evidence of the run"))

    if _present(research_brief):
        results.append(
            _single(
                "completeness_score",
                [
                    _message(
                        COMPLETENESS_PROMPT.format(
                            research_brief=research_brief,
                            user_question=question,
                            report=report,
                            today=_today(),
                        )
                    )
                ],
                CompletenessScore,
                judge,
            )
        )
    else:
        results.append(_needs("completeness_score", "a research brief"))

    return results
