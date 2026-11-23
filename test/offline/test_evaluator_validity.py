"""REQ-009: evaluator scores are valid, bounded and based on their stated inputs.

Covers TC-EVA-01 to TC-EVA-05 (``verification-constraints.md`` §7, evaluation)
and INV-009. The interface is ``test/evaluation/metrics.py`` (`MetricResult`,
`InvalidMetricInput`, `validate_rating`, `groundedness_ratio`,
`evaluate_metrics`), the strict judge schemas and the thin LangSmith adapter of
``test/evaluators.py`` (ADR-007 §3, §5). The judge is fake: no model client is
created and no API key is needed.
"""

import dataclasses

import pytest

QUESTION_MARKER = "QUESTION_MARKER_42"
REPORT_MARKER = "REPORT_MARKER_42"
ANSWER_MARKER = "ANSWER_MARKER_42"
BRIEF_MARKER = "BRIEF_MARKER_42"
EVIDENCE_MARKER = "EVIDENCE_MARKER_42"

BASELINE_KEYS = {
    "research_depth_score",
    "source_quality_score",
    "analytical_rigor_score",
    "practical_value_score",
    "balance_and_objectivity_score",
    "writing_quality_score",
    "relevance_score",
    "structure_and_cohesiveness_score",
    "correctness_score",
    "groundedness_score",
    "completeness_score",
}


###################
# Fake judge
###################
class FakeJudge:
    """Fake judge: records every request and answers each schema from a script."""

    def __init__(
        self, outputs: dict[str, object] | None = None, error: Exception | None = None
    ):
        self.outputs = outputs or {}
        self.error = error
        self.requests: list[tuple[object, list]] = []

    def with_structured_output(self, schema):
        return BoundJudge(self, schema)

    def with_retry(self, **_kwargs):
        return self

    def invoke(self, messages):
        return self.answer(None, messages)

    async def ainvoke(self, messages):
        return self.answer(None, messages)

    def answer(self, schema, messages):
        self.requests.append((schema, messages))
        if self.error is not None:
            raise self.error
        name = getattr(schema, "__name__", "default")
        output = self.outputs.get(name, self.outputs.get("default"))
        return output() if callable(output) else output


class BoundJudge:
    """`with_structured_output` result bound to one schema."""

    def __init__(self, judge: FakeJudge, schema):
        self.judge = judge
        self.schema = schema

    def with_retry(self, **_kwargs):
        return self

    def invoke(self, messages):
        return self.judge.answer(self.schema, messages)

    async def ainvoke(self, messages):
        return self.judge.answer(self.schema, messages)


class Instance:
    """Plain record the fake judge returns instead of a Pydantic model."""

    def __init__(self, **values):
        self.__dict__.update(values)


class Claim(Instance):
    """A claim with a grounded flag."""


def scored_rating(value: int) -> dict[str, object]:
    """Scripted output for each rating schema with the same rating."""
    return {
        "OverallQualityScore": lambda: Instance(
            research_depth=value,
            source_quality=value,
            analytical_rigor=value,
            practical_value=value,
            balance_and_objectivity=value,
            writing_quality=value,
        ),
        "RelevanceScore": lambda: Instance(score=value, reasoning="reason"),
        "StructureScore": lambda: Instance(score=value, reasoning="reason"),
        "CorrectnessScore": lambda: Instance(score=value, reasoning="reason"),
        "CompletenessScore": lambda: Instance(score=value, reasoning="reason"),
    }


def text_of(messages) -> str:
    """Join the text of a judge request."""
    parts = []
    for message in messages:
        content = (
            message.get("content")
            if isinstance(message, dict)
            else getattr(message, "content", message)
        )
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            parts.extend(
                block.get("text", "") for block in content if isinstance(block, dict)
            )
    return "\n".join(parts)


def evaluate(judge: FakeJudge, **overrides):
    """Call `evaluate_metrics` with the markers and the given overrides."""
    from test.evaluation.metrics import evaluate_metrics

    inputs = {
        "question": QUESTION_MARKER,
        "report": REPORT_MARKER,
        "reference_answer": ANSWER_MARKER,
        "research_brief": BRIEF_MARKER,
        "evidence": EVIDENCE_MARKER,
        "judge": judge,
    }
    inputs.update(overrides)
    return evaluate_metrics(**inputs)


def load_evaluators():
    """Return a fresh copy of ``test/evaluators.py`` imported with a dummy API key.

    The baseline module creates its judge client at import time, and importing it
    is what the cases here observe. They pass a dummy ``OPENAI_API_KEY`` so that
    the import itself needs no real credential and still makes no network call;
    what the module must stop doing is creating a client at all.
    """
    import importlib
    import os

    os.environ.setdefault("OPENAI_API_KEY", "offline-placeholder")
    import test.evaluators as evaluators

    return importlib.reload(evaluators)


def by_metric(results) -> dict:
    """Index metric results by metric name."""
    return {result.metric: result for result in results}


###################
# Inputs (TC-EVA-01)
###################
def test_evaluators_receive_their_inputs():
    """TC-EVA-01 / C-001: each metric receives the inputs it is defined over."""
    judge = FakeJudge(scored_rating(4))

    results = evaluate(judge)

    assert len(judge.requests) >= 4, "each metric group asks the judge once"
    requests = {
        getattr(schema, "__name__", ""): text_of(messages)
        for schema, messages in judge.requests
    }
    for name, text in requests.items():
        assert QUESTION_MARKER in text and REPORT_MARKER in text, (
            f"the {name} request carries the question and the report"
        )
        assert "{" not in text.replace("{{", "").replace("}}", ""), (
            f"no placeholder is left unformatted in the {name} request"
        )
    assert ANSWER_MARKER in requests["CorrectnessScore"], (
        "correctness sees the reference answer"
    )
    assert BRIEF_MARKER in requests["CompletenessScore"], (
        "completeness sees the research brief"
    )
    assert EVIDENCE_MARKER in requests["GroundednessScore"], (
        "groundedness sees the evidence"
    )
    assert {result.metric for result in results} <= BASELINE_KEYS


###################
# Ratings (TC-EVA-02)
###################
def _assert_normalised_rating(rating, score):
    """Ratings 1 and 5 give 0.2 and 1.0 (TC-EVA-02)."""
    from test.evaluation.metrics import validate_rating

    assert validate_rating(rating) == pytest.approx(score)


@pytest.mark.parametrize(
    "value",
    [0, 6, True, False, "4", 4.0, 4.5, float("nan"), float("inf"), None],
    ids=[
        "zero",
        "six",
        "true",
        "false",
        "string",
        "float",
        "fraction",
        "nan",
        "inf",
        "none",
    ],
)
def _rejected_rating(value):
    """Every other raw value is refused, never clamped or defaulted (TC-EVA-02, M-001)."""
    from test.evaluation.metrics import InvalidMetricInput, validate_rating

    with pytest.raises(InvalidMetricInput):
        validate_rating(value)


def _lax_judge_value_not_parsed():
    """Strict mode: `4.0` and `"4"` do not parse as `4` (TC-EVA-02, ADR-007 §3)."""
    evaluators = load_evaluators()

    schema = evaluators.RelevanceScore
    assert schema.model_config.get("strict") is True
    for value in (4.0, "4"):
        with pytest.raises(Exception):
            schema(score=value, reasoning="r")
    assert schema(score=4, reasoning="r").score == 4


def _out_of_range_value(value):
    """A rating outside 1-5 gives not_evaluable with no score (TC-EVA-02, M-001)."""
    results = evaluate(FakeJudge(scored_rating(value)))

    assert results
    assert all(result.score is None or 0.0 <= result.score <= 1.0 for result in results)
    sentiment_metrics = [
        result
        for result in results
        if result.metric in {"relevance_score", "correctness_score"}
    ]
    assert sentiment_metrics and all(
        result.status == "not_evaluable" for result in sentiment_metrics
    )
    assert all(result.reason for result in sentiment_metrics)
    out_of_range_score_count = sum(
        1
        for result in results
        if result.score is not None and not (0.0 <= result.score <= 1.0)
    )
    assert out_of_range_score_count == 0


def test_ratings_are_validated():
    """TC-EVA-02 / C-002, M-001; INV-009: 1 and 5 score, every other raw value is not_evaluable."""
    from test.evaluation.metrics import validate_rating

    assert validate_rating(1) == pytest.approx(0.2)
    assert validate_rating(5) == pytest.approx(1.0)
    for value in (0, 6, True, False, "4", 4.0, 4.5, float("nan"), float("inf"), None):
        _rejected_rating(value)
    _lax_judge_value_not_parsed()
    _out_of_range_value(0)
    _out_of_range_value(6)


def test_metric_result_shape():
    """ADR-007 §3: a result states the metric name, a status, a score and a reason."""
    from test.evaluation.metrics import MetricResult

    fields = {field.name for field in dataclasses.fields(MetricResult)}
    assert {"metric", "status", "score", "reason"} <= fields


###################
# Missing inputs (TC-EVA-03)
###################
@pytest.mark.parametrize(
    ("missing", "affected"),
    [
        ("reference_answer", "correctness_score"),
        ("research_brief", "completeness_score"),
        ("evidence", "groundedness_score"),
    ],
)
@pytest.mark.parametrize("value", [None, "", "   "], ids=["missing", "empty", "blank"])
def test_missing_input_is_not_evaluable(missing, affected, value):
    """TC-EVA-03 / C-003; INV-009: only the metric that needs the missing input is not_evaluable."""
    results = by_metric(evaluate(FakeJudge(scored_rating(4)), **{missing: value}))

    assert results[affected].status == "not_evaluable"
    assert results[affected].score is None
    assert results[affected].reason
    others = [name for name, result in results.items() if name != affected]
    assert others and any(results[name].status == "scored" for name in others)


###################
# Groundedness and errors (TC-EVA-04)
###################
def _groundedness_ratio_of_two_grounded_claims():
    """Two grounded claims out of four give 0.5 (TC-EVA-04)."""
    from test.evaluation.metrics import groundedness_ratio

    claims = [
        Claim(claim="a", grounded=True),
        Claim(claim="b", grounded=False),
        Claim(claim="c", grounded=True),
        Claim(claim="d", grounded=False),
    ]
    assert groundedness_ratio(claims) == pytest.approx(0.5)


def _rejected_claim_list(claims):
    """No claim or a non-boolean `grounded` value makes the ratio impossible (TC-EVA-04)."""
    from test.evaluation.metrics import InvalidMetricInput, groundedness_ratio

    with pytest.raises(InvalidMetricInput):
        groundedness_ratio(claims)


def _groundedness_not_evaluable_alone():
    """An empty claim list leaves groundedness unscored and the others scored (TC-EVA-04, C-004)."""
    outputs = {**scored_rating(3), "GroundednessScore": lambda: Instance(claims=[])}
    results = by_metric(evaluate(FakeJudge(outputs)))

    assert results["groundedness_score"].status == "not_evaluable"
    assert results["groundedness_score"].score is None
    assert results["relevance_score"].status == "scored"


def _raising_group_is_contained():
    """A judge call that raises makes its group not_evaluable, not the whole evaluation (TC-EVA-04, POL-022)."""
    from test.evaluation.metrics import MetricResult

    results = evaluate(FakeJudge(error=RuntimeError("judge unavailable")))

    assert results and all(isinstance(result, MetricResult) for result in results)
    assert all(
        result.status == "not_evaluable" and result.score is None for result in results
    )
    assert all(result.reason for result in results)


def test_groundedness_and_errors():
    """TC-EVA-04 / C-004; INV-009, POL-022: no claim, a non-boolean flag and a raising group stay contained."""
    _groundedness_ratio_of_two_grounded_claims()
    for claims in (
        [],
        [Claim(claim="a", grounded="yes")],
        [Claim(claim="a", grounded=1)],
    ):
        _rejected_claim_list(claims)
    _groundedness_not_evaluable_alone()
    _raising_group_is_contained()


###################
# The adapter keeps the baseline shape (TC-EVA-05)
###################
ADAPTER_NAMES = (
    "eval_overall_quality",
    "eval_relevance",
    "eval_structure",
    "eval_correctness",
    "eval_groundedness",
    "eval_completeness",
)


def adapter_inputs() -> tuple[dict, dict, dict]:
    """The baseline LangSmith inputs, outputs and reference outputs."""
    inputs = {"messages": [{"role": "user", "content": QUESTION_MARKER}]}
    outputs = {
        "final_report": REPORT_MARKER,
        "research_brief": BRIEF_MARKER,
        "raw_notes": [EVIDENCE_MARKER],
    }
    reference = {"answer": ANSWER_MARKER}
    return inputs, outputs, reference


def test_adapter_keeps_baseline_shape(monkeypatch):
    """TC-EVA-05 / INV-009: no client at import; adapters keep names, keys and `score=None` when not evaluable."""
    from test.evaluation import metrics

    evaluators = load_evaluators()

    for name in ADAPTER_NAMES:
        assert callable(getattr(evaluators, name))
    assert not hasattr(evaluators, "eval_model"), "no model client is created at import"

    monkeypatch.setattr(
        metrics, "default_judge", lambda: FakeJudge(error=RuntimeError("no key"))
    )
    inputs, outputs, reference = adapter_inputs()

    overall = evaluators.eval_overall_quality(inputs, outputs)
    assert {entry["key"] for entry in overall} == {
        "research_depth_score",
        "source_quality_score",
        "analytical_rigor_score",
        "practical_value_score",
        "balance_and_objectivity_score",
        "writing_quality_score",
    }

    for result in (
        evaluators.eval_relevance(inputs, outputs),
        evaluators.eval_structure(inputs, outputs),
        evaluators.eval_correctness(inputs, outputs, reference),
        evaluators.eval_groundedness(inputs, outputs),
        evaluators.eval_completeness(inputs, outputs),
    ):
        assert {"key", "score", "comment"} <= set(result)
        assert result["score"] is None
        assert result["comment"].startswith("not_evaluable:")


def test_adapter_reports_scored_status(monkeypatch):
    """TC-EVA-05 / ADR-007 §5: a scored adapter result carries a number and a `scored:` comment."""
    from test.evaluation import metrics

    evaluators = load_evaluators()
    monkeypatch.setattr(metrics, "default_judge", lambda: FakeJudge(scored_rating(5)))
    inputs, outputs, _reference = adapter_inputs()

    result = evaluators.eval_relevance(inputs, outputs)

    assert result["key"] == "relevance_score"
    assert result["score"] == pytest.approx(1.0)
    assert result["comment"].startswith("scored:")


def test_no_client_is_created_at_import():
    """TC-EVA-05: importing the evaluation modules creates no chat model client."""
    import importlib

    import test.evaluation.metrics as metrics

    module = importlib.reload(metrics)
    assert not hasattr(module, "eval_model")
    for value in vars(module).values():
        assert not type(value).__module__.startswith("langchain_openai"), (
            "no OpenAI client at import"
        )
