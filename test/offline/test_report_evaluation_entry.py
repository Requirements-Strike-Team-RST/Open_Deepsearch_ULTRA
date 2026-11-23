"""REQ-010: an existing report can be evaluated without running research.

Covers TC-EVA-06 and TC-EVA-07 (``verification-constraints.md`` §7, evaluation)
and POL-023. The interface is ``test/evaluation/entry.py`` (`evaluate_existing_report`,
`EvaluationInputError`, `main`, ADR-007 §3). The research graph build and every
search function are patched to fail if called; the judge is fake.
"""

import hashlib
import json

import pytest

REPORT_TEXT = "# Battery recycling\n\nDirective 2006/66/EC was replaced in 2023 [1].\n\n### Sources\n[1] A: https://example.org/a"
QUESTION = "Which regulation governs battery recycling?"


class FakeJudge:
    """Fake judge that records every request and answers each schema."""

    def __init__(self):
        self.requests: list[tuple[object, list]] = []

    def with_structured_output(self, schema):
        judge = self

        class Bound:
            def with_retry(self, **_kwargs):
                return self

            def invoke(self, messages):
                judge.requests.append((schema, messages))
                return judge.answer(schema)

            async def ainvoke(self, messages):
                return self.invoke(messages)

        return Bound()

    def with_retry(self, **_kwargs):
        return self

    def answer(self, schema):
        name = getattr(schema, "__name__", "")
        if name == "GroundednessScore":
            from test.offline.test_evaluator_validity import Claim

            return type("Result", (), {"claims": [Claim(claim="c", grounded=True)]})()
        if name == "OverallQualityScore":
            return type(
                "Result",
                (),
                {
                    "research_depth": 4,
                    "source_quality": 4,
                    "analytical_rigor": 4,
                    "practical_value": 4,
                    "balance_and_objectivity": 4,
                    "writing_quality": 4,
                },
            )()
        return type("Result", (), {"score": 4, "reasoning": "reason"})()


def forbid_research(monkeypatch):
    """Make the research graph and every search entry point fail when called."""
    import importlib

    def forbidden(*_args, **_kwargs):
        raise AssertionError("the evaluation entry must not run research or search")

    deep_researcher = importlib.import_module("open_deep_research.deep_researcher")
    monkeypatch.setattr(
        deep_researcher, "deep_researcher_builder", forbidden, raising=False
    )
    monkeypatch.setattr(deep_researcher, "deep_researcher", forbidden, raising=False)
    monkeypatch.setattr(
        deep_researcher.researcher_subgraph, "ainvoke", forbidden, raising=False
    )
    monkeypatch.setattr(
        deep_researcher.supervisor_subgraph, "ainvoke", forbidden, raising=False
    )

    utils = importlib.import_module("open_deep_research.utils")
    for name in ("tavily_search", "tavily_search_async", "get_all_tools"):
        if hasattr(utils, name):
            monkeypatch.setattr(utils, name, forbidden)


def request_text(messages) -> str:
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


###################
# Scoring a supplied report (TC-EVA-06)
###################
def test_entry_scores_supplied_report_without_research(monkeypatch):
    """TC-EVA-06 / C-001: the report and question reach the judge unchanged, no research or search runs."""
    forbid_research(monkeypatch)
    from test.evaluation.entry import evaluate_existing_report

    judge = FakeJudge()
    result = evaluate_existing_report(QUESTION, REPORT_TEXT, judge=judge)

    assert judge.requests, "the judge is asked"
    all_text = "\n".join(request_text(messages) for _schema, messages in judge.requests)
    assert REPORT_TEXT in all_text, "the report is scored as given"
    assert QUESTION in all_text
    assert result.report_id == hashlib.sha256(REPORT_TEXT.encode("utf-8")).hexdigest()
    assert result.metrics, "one result per metric"
    assert all(
        metric.status in {"scored", "not_evaluable"} for metric in result.metrics
    )


def test_entry_accepts_the_optional_inputs(monkeypatch):
    """REQ-010: the optional reference answer, brief and evidence reach their metrics; research is not run."""
    forbid_research(monkeypatch)
    from test.evaluation.entry import evaluate_existing_report

    judge = FakeJudge()
    evaluate_existing_report(
        QUESTION,
        REPORT_TEXT,
        reference_answer="ANSWER_MARKER",
        research_brief="BRIEF_MARKER",
        evidence="EVIDENCE_MARKER",
        judge=judge,
    )

    all_text = "\n".join(request_text(messages) for _schema, messages in judge.requests)
    assert (
        "ANSWER_MARKER" in all_text
        and "BRIEF_MARKER" in all_text
        and "EVIDENCE_MARKER" in all_text
    )


###################
# Blank input (TC-EVA-07)
###################
@pytest.mark.parametrize(
    ("question", "report"),
    [
        ("", REPORT_TEXT),
        ("   ", REPORT_TEXT),
        (None, REPORT_TEXT),
        (QUESTION, ""),
        (QUESTION, " \n\t "),
        (QUESTION, None),
        (42, REPORT_TEXT),
    ],
    ids=[
        "blank_question",
        "spaces_question",
        "none_question",
        "blank_report",
        "whitespace_report",
        "none_report",
        "non_string",
    ],
)
def test_blank_input_rejected(monkeypatch, question, report):
    """TC-EVA-07 / C-002; POL-023: blank or non-string input raises before any evaluator runs."""
    from test.evaluation.entry import EvaluationInputError, evaluate_existing_report

    judge = FakeJudge()

    with pytest.raises(EvaluationInputError):
        evaluate_existing_report(question, report, judge=judge)
    assert judge.requests == []


@pytest.mark.parametrize(
    ("question", "report_text"),
    [(QUESTION, "   \n"), ("   ", REPORT_TEXT)],
    ids=["blank_report", "blank_question"],
)
def test_command_exits_with_2_on_blank_input(
    tmp_path, monkeypatch, question, report_text
):
    """TC-EVA-07 / POL-023: the command rejects blank input with exit code 2 and no judge call."""
    forbid_research(monkeypatch)
    from test.evaluation import entry, metrics

    judges: list[FakeJudge] = []

    def make_judge():
        judges.append(FakeJudge())
        return judges[-1]

    monkeypatch.setattr(entry, "default_judge", make_judge, raising=False)
    monkeypatch.setattr(metrics, "default_judge", make_judge)
    report = tmp_path / "report.md"
    report.write_text(report_text, encoding="utf-8")

    exit_code = entry.main(["--question", question, "--report", str(report)])

    assert exit_code == 2
    assert all(judge.requests == [] for judge in judges), "the judge is called 0 times"
    assert judges == [], "no judge client is created for rejected input"


def test_command_prints_json_for_a_report_file(tmp_path, monkeypatch, capsys):
    """REQ-010 / ADR-007 §3: the command prints the per-metric result as JSON and exits with 0."""
    forbid_research(monkeypatch)
    from test.evaluation import entry

    report = tmp_path / "report.md"
    report.write_text(REPORT_TEXT, encoding="utf-8")
    judge = FakeJudge()
    monkeypatch.setattr(entry, "default_judge", lambda: judge, raising=False)

    exit_code = entry.main(["--question", QUESTION, "--report", str(report)])

    printed = capsys.readouterr().out
    assert exit_code == 0
    payload = json.loads(printed)
    assert (
        payload["report_id"] == hashlib.sha256(REPORT_TEXT.encode("utf-8")).hexdigest()
    )
    assert isinstance(payload["metrics"], list) and payload["metrics"]
    assert judge.requests


def test_entry_does_not_import_research_at_module_level():
    """REQ-010 / ADR-007 §3: the entry module does not import the research graph or `utils`."""
    import inspect

    from test.evaluation import entry

    source = inspect.getsource(entry)
    assert "deep_researcher import" not in source
    assert "open_deep_research.utils" not in source
