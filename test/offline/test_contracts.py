"""REQ-001: the shared task-contract types behave as ADR-001 §5 specifies.

Covers the shared contract of REQ-001 (`TaskSpec`, `Source`, `Finding`,
`TaskResult`, `normalize_question`, `unanswered_questions`) named in
``architecture-blueprint.md`` §5 and required to live here by
``verification-constraints.md`` §3. On a baseline without these types every case
here fails with a missing behaviour, never with a collection error. No model and
no network are used.
"""

import pytest

Q1 = "Which regulation governs battery recycling?"
Q2 = "How many battery recycling plants opened in 2024?"
URL_A = "https://example.org/a"


def state_types():
    """Return the contract types and helpers of ``state.py`` (ADR-001 §5)."""
    import open_deep_research.state as state

    for name in (
        "TaskSpec",
        "Source",
        "Finding",
        "TaskResult",
        "normalize_question",
        "unanswered_questions",
    ):
        if not hasattr(state, name):
            pytest.fail(f"state.py must define {name} (ADR-001 §5)", pytrace=False)
    return state


def finding(questions: list[str] | None = None):
    """Return one finding that answers the given questions from the retrieved URL."""
    state = state_types()
    return state.Finding(
        claim="claim",
        answers=list(questions or [Q1]),
        sources=[state.Source(title="source", url=URL_A)],
    )


def result(status: str, questions: list[str], answered: list[str] | None = None):
    """Return a contract task result with one sourced finding per answered question."""
    state = state_types()
    answered = questions if answered is None else answered
    return state.TaskResult(
        task_id="T1",
        status=status,
        must_answer=list(questions),
        findings=[finding([question]) for question in answered],
        summary="summary",
        tool_calls=1,
        failure_category=None if status == "complete" else "unanswered",
        reason=""
        if status == "complete"
        else ", ".join(q for q in questions if q not in answered),
    )


def test_each_contract_type_is_exported():
    """ADR-001 §5: `state.py` defines the four types and the two question helpers."""
    state = state_types()

    for name in ("TaskSpec", "Source", "Finding", "TaskResult"):
        assert isinstance(getattr(state, name), type), (
            f"state.py defines {name} as a type"
        )
    for name in ("normalize_question", "unanswered_questions"):
        assert callable(getattr(state, name))


def test_task_spec_requires_one_to_five_questions():
    """ADR-001 §3.1: a spec holds an id, a topic, a scope, 1-5 questions and the tool budget."""
    TaskSpec = state_types().TaskSpec

    spec = TaskSpec(
        task_id="T1",
        research_topic="topic",
        scope="EU",
        must_answer=[Q1, Q2],
        max_tool_calls=7,
    )
    assert (spec.task_id, spec.research_topic, spec.scope) == ("T1", "topic", "EU")
    assert spec.must_answer == [Q1, Q2]
    assert spec.max_tool_calls == 7

    with pytest.raises(Exception):
        TaskSpec(
            task_id="T2",
            research_topic="topic",
            scope="",
            must_answer=[],
            max_tool_calls=1,
        )
    with pytest.raises(Exception):
        TaskSpec(
            task_id="T3",
            research_topic="topic",
            scope="",
            must_answer=[f"q{index}" for index in range(6)],
            max_tool_calls=1,
        )


def test_a_spec_with_a_blank_topic_is_rejected():
    """POL-006: a spec whose topic is blank cannot become a runnable task."""
    TaskSpec = state_types().TaskSpec

    with pytest.raises(Exception):
        TaskSpec(
            task_id="T1",
            research_topic="   ",
            scope="",
            must_answer=[Q1],
            max_tool_calls=5,
        )


def test_finding_needs_a_claim_an_answer_and_a_source():
    """ADR-001 §3.3: a finding is a claim, the questions it answers and at least one source."""
    state = state_types()

    source = state.Source(title="Source A", url=URL_A)
    assert (source.title, source.url) == ("Source A", URL_A)

    valid = state.Finding(claim="Directive 2006/66/EC", answers=[Q1], sources=[source])
    assert valid.claim == "Directive 2006/66/EC"
    assert valid.answers == [Q1]
    assert [item.url for item in valid.sources] == [URL_A]

    with pytest.raises(Exception):
        state.Finding(claim="unsourced", answers=[Q1], sources=[])


def test_complete_result_has_no_failure_category_and_failed_result_has_no_content():
    """ADR-001 §5: `complete` carries findings and no category; `failed` carries neither findings nor summary."""
    state = state_types()
    spec = state.TaskSpec(
        task_id="T1",
        research_topic="topic",
        scope="",
        must_answer=[Q1],
        max_tool_calls=4,
    )

    complete = state.TaskResult(
        task_id="T1",
        status="complete",
        must_answer=[Q1],
        findings=[finding()],
        summary="summary",
        tool_calls=2,
        failure_category=None,
        reason="",
    )
    assert (complete.status, complete.failure_category, complete.tool_calls) == (
        "complete",
        None,
        2,
    )

    failed = state.TaskResult.failed(spec, "runtime", "boom", tool_calls=3)
    assert (failed.task_id, failed.status, failed.failure_category, failed.reason) == (
        "T1",
        "failed",
        "runtime",
        "boom",
    )
    assert failed.findings == [] and failed.summary == ""
    assert failed.must_answer == [Q1] and failed.tool_calls == 3


def test_question_comparison_ignores_case_and_spacing():
    """ADR-001 §3.1: questions are compared after collapsing whitespace and ignoring case."""
    normalize_question = state_types().normalize_question

    assert normalize_question("  How   MANY  plants ") == normalize_question(
        "how many plants"
    )
    assert normalize_question(Q1) == normalize_question(Q1.upper())
    assert normalize_question(Q1) != normalize_question(Q2)


def test_unanswered_questions_lists_the_required_questions_without_a_counted_finding():
    """ADR-001 §5: `unanswered_questions` returns, in spec order, the questions no finding answered."""
    state = state_types()
    partial = result("partial", [Q1, Q2], answered=[Q1])
    failed = state.TaskResult.failed(
        state.TaskSpec(
            task_id="T2",
            research_topic="topic",
            scope="",
            must_answer=["a third question"],
            max_tool_calls=1,
        ),
        "runtime",
        "boom",
    )

    assert state.unanswered_questions([partial, failed]) == [Q2, "a third question"]
    assert state.unanswered_questions([partial]) == [Q2]


def test_a_question_answered_twice_is_answered():
    """ADR-001 §3.4: coverage counts distinct questions, so a repeated answer leaves no gap."""
    state = state_types()
    twice = [result("complete", [Q1]), result("complete", [Q1])]

    assert state.unanswered_questions(twice) == []
