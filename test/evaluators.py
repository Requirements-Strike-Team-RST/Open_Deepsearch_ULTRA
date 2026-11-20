"""LangSmith adapters for the evaluation metric groups (REQ-009, ADR-007 §3, §5).

A thin adapter over ``test.evaluation.metrics``: it keeps the baseline function
names, signatures and return shapes so that ``test/run_evaluate.py`` does not
change, and creates no model client at import (POL-020). Every result's
``comment`` starts with its status: ``scored:`` or ``not_evaluable:``. A
``not_evaluable`` metric has ``score=None`` and its reason in the comment.
"""

from typing import Optional

from test.evaluation import metrics
from test.evaluation.metrics import (
    CompletenessScore,
    CorrectnessScore,
    GroundednessClaim,
    GroundednessScore,
    MetricResult,
    OverallQualityScore,
    RelevanceScore,
    StructureScore,
    evaluate_metrics,
)
from test.prompts import (
    COMPLETENESS_PROMPT,
    CORRECTNESS_PROMPT,
    GROUNDEDNESS_PROMPT,
    OVERALL_QUALITY_PROMPT,
    RELEVANCE_PROMPT,
    STRUCTURE_PROMPT,
)

__all__ = [
    "COMPLETENESS_PROMPT",
    "CORRECTNESS_PROMPT",
    "GROUNDEDNESS_PROMPT",
    "OVERALL_QUALITY_PROMPT",
    "RELEVANCE_PROMPT",
    "STRUCTURE_PROMPT",
    "eval_completeness",
    "eval_correctness",
    "eval_groundedness",
    "eval_overall_quality",
    "eval_relevance",
    "eval_structure",
    # The strict judge schemas stay importable from the adapter (ADR-007 §5).
    "CompletenessScore",
    "CorrectnessScore",
    "GroundednessClaim",
    "GroundednessScore",
    "OverallQualityScore",
    "RelevanceScore",
    "StructureScore",
]

QUALITY_KEYS = (
    "research_depth_score",
    "source_quality_score",
    "analytical_rigor_score",
    "practical_value_score",
    "balance_and_objectivity_score",
    "writing_quality_score",
)


def _format_input_query(inputs: dict) -> str:
    """Return the user input of the baseline LangSmith example."""
    messages = inputs.get("messages", [])
    if len(messages) == 1:
        return messages[0]["content"]

    role_to_string_format_map = {
        "user": "<user_input>\n{content}\n</user_input>",
        "assistant": "<assistant_follow_up>\n{content}\n</assistant_follow_up>",
    }

    return "\n\n".join(
        role_to_string_format_map[message["role"]].format(content=message["content"])
        for message in messages
    )


def _evidence(outputs: dict) -> Optional[str]:
    """Return the raw notes of the example as the evidence a task run produced."""
    notes = outputs.get("raw_notes")
    if not notes:
        return None
    return "\n".join(str(note) for note in notes)


def _metrics(inputs: dict, outputs: dict, reference_outputs: dict | None) -> dict:
    """Score one LangSmith example and index the results by metric name."""
    reference = reference_outputs or {}
    results = evaluate_metrics(
        _format_input_query(inputs),
        outputs.get("final_report", ""),
        reference_answer=reference.get("answer"),
        research_brief=outputs.get("research_brief"),
        evidence=_evidence(outputs),
        judge=metrics.default_judge(),
    )
    return {result.metric: result for result in results}


def _entry(result: MetricResult) -> dict:
    """Return the baseline ``{key, score, comment}`` shape of one metric."""
    return {
        "key": result.metric,
        "score": result.score,
        "comment": f"{result.status}:{result.reason}",
    }


def eval_overall_quality(inputs: dict, outputs: dict):
    """Return the six overall-quality scores of the baseline evaluator."""
    results = _metrics(inputs, outputs, None)
    return [_entry(results[metric]) for metric in QUALITY_KEYS]


def eval_relevance(inputs: dict, outputs: dict):
    """Return the relevance score of the baseline evaluator."""
    return _entry(_metrics(inputs, outputs, None)["relevance_score"])


def eval_structure(inputs: dict, outputs: dict):
    """Return the structure and cohesiveness score of the baseline evaluator."""
    return _entry(_metrics(inputs, outputs, None)["structure_and_cohesiveness_score"])


def eval_correctness(inputs: dict, outputs: dict, reference_outputs: dict):
    """Return the correctness score of the baseline evaluator."""
    return _entry(_metrics(inputs, outputs, reference_outputs)["correctness_score"])


def eval_groundedness(inputs: dict, outputs: dict):
    """Return the groundedness score of the baseline evaluator."""
    return _entry(_metrics(inputs, outputs, None)["groundedness_score"])


def eval_completeness(inputs: dict, outputs: dict):
    """Return the completeness score of the baseline evaluator."""
    return _entry(_metrics(inputs, outputs, None)["completeness_score"])
