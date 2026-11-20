"""REQ-003: the research loop ends on a deterministic coverage check with exactly one exit reason.

Covers TC-ORC-07 to TC-ORC-12 (``verification-constraints.md`` §7, orchestration)
and INV-003, each case once as its table row defines it. The interface is
``orchestration/termination.py`` (`coverage`, `select_exit`) plus the flag-on
`supervisor` and `supervisor_tools` of ADR-001 §3.4; POL-010 and POL-011 are
checked at the level the table names.

`coverage` and `select_exit` read task results, so on a baseline that lacks the
contract types (ADR-001 §5) they report that missing module when called and the
tests build the contract types for the cases where the table names them. The
supervisor model and the researcher subgraph are fake.
"""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from test.offline import helpers

URL_A = "https://example.org/a"
Q1 = "Which regulation governs battery recycling?"
Q2 = "How many battery recycling plants opened in 2024?"
Q3 = "What share of batteries is recycled?"


###################
# Contract helpers (ADR-001 §5, resolved inside the tests)
###################
def state_types():
    """Return the contract types and helpers of ``state.py`` (ADR-001 §5)."""
    import open_deep_research.state as state

    return state


def outcome(task_id: str, answered: list[str], required: list[str]):
    """Return a contract task result that answered ``answered`` of ``required`` (ADR-001 §3.4).

    ``select_exit`` reads task results (ADR-001 §5), so the record is the
    contract type with one counted finding per answered question.
    """
    status = (
        "complete"
        if set(answered) >= set(required)
        else ("partial" if answered else "failed")
    )
    return task_result(task_id, status, required, answered=answered)


def task_result(
    task_id: str, status: str, questions: list[str], answered: list[str] | None = None
):
    """Build a contract task result with one sourced finding per answered question (ADR-001 §5)."""
    state = state_types()
    answered = (
        answered
        if answered is not None
        else (questions if status == "complete" else [])
    )
    findings = [
        state.Finding(
            claim=f"claim for {question}",
            answers=[question],
            sources=[state.Source(title="A", url=URL_A)],
        )
        for question in answered
    ]
    return state.TaskResult(
        task_id=task_id,
        status=status,
        must_answer=list(questions),
        findings=findings,
        summary="" if status == "failed" else "summary",
        tool_calls=1,
        failure_category=None if status == "complete" else "unanswered",
        reason="" if status == "complete" else "unanswered questions",
    )


def decide(
    before,
    after,
    *,
    stalled_turns=0,
    turn_is_eligible=True,
    cap_reached=False,
    supervisor_error=False,
):
    """Call `select_exit` with the default coverage threshold of 0.8."""
    from open_deep_research.orchestration.termination import select_exit

    return select_exit(
        before,
        after,
        stalled_turns=stalled_turns,
        turn_is_eligible=turn_is_eligible,
        cap_reached=cap_reached,
        supervisor_error=supervisor_error,
        threshold=0.8,
    )


###################
# The exit decision (TC-ORC-07 to 12)
###################
def test_full_coverage_exits_covered():
    """TC-ORC-07 / C-001: every required question answered exits covered, whatever the turn did."""
    answers = [Q1, Q2]
    covered = [outcome("T1", answers, answers)]
    for turn_is_eligible in (True, False):
        before = [] if turn_is_eligible else covered
        assert decide(before, covered, turn_is_eligible=turn_is_eligible) == (
            "covered",
            0,
        ), "the exit reason is the same with and without ResearchComplete"
    twice = [outcome("T1", answers, answers), outcome("T2", answers, answers)]
    assert decide(twice, twice) == ("covered", 0), (
        "answering a question twice still covers it"
    )


def test_complete_below_threshold_is_refused():
    """TC-ORC-08 / C-002, M-002; POL-010: a completion request at coverage 0.5 does not end the loop."""
    after = [outcome("T1", [Q1], [Q1, Q2])]
    reason, _stalled = decide([], after, turn_is_eligible=True)

    assert reason is None, (
        "a completion request below the threshold must not end the loop"
    )
    assert state_types().unanswered_questions(after) == [Q2]
    premature_complete_accepted_count = int(reason is not None and reason != "covered")
    assert premature_complete_accepted_count == 0


def test_turns_without_progress_exit_stalled(monkeypatch):
    """TC-ORC-09 / C-003: two non-think turns that add no answered question exit stalled."""
    same = [outcome("T1", [Q1], [Q1, Q2])]

    reason, stalled = decide(same, same, stalled_turns=0, turn_is_eligible=True)
    assert (reason, stalled) == (None, 1)

    reason, stalled = decide(same, same, stalled_turns=stalled, turn_is_eligible=False)
    assert (reason, stalled) == (None, 1), (
        "a think_tool-only turn leaves the counter as it is"
    )

    after = [same[0], outcome("T2", [], [Q3])]
    reason, stalled = decide(same, after, stalled_turns=stalled, turn_is_eligible=True)
    assert (reason, stalled) == ("stalled", 2), (
        "a new question that stays unanswered is not progress"
    )

    # Answering one more question (2 of 3, still below the threshold) is progress.
    grown = [same[0], outcome("T2", [Q3], [Q3])]
    assert decide(same, grown, stalled_turns=1) == (None, 0), (
        "a turn that grows the answered-question count resets the counter"
    )

    # The table's input through the flag-on loop: delegation, think_tool only,
    # delegation of a new question; nothing is ever answered.
    reflection = helpers.ai_message(
        tool_calls=[helpers.tool_call("think_tool", {"reflection": "what next?"}, "t1")]
    )
    turns = [
        delegation(Q1, [Q1], "c1"),
        reflection,
        delegation(Q2, [Q2], "c2"),
    ]
    researcher = FakeResearcher(answered=set())

    state = run_loop(
        monkeypatch, turns, Q1, researcher=researcher, max_researcher_iterations=6
    )

    assert state.get("exit_reason") == "stalled"
    assert [spec.task_id for spec in researcher.received] == ["T1", "T2"], (
        "the loop exits after the second delegation turn, not after the think_tool turn"
    )


def test_iteration_cap_exits_budget_exhausted():
    """TC-ORC-10 / C-004: the cap below the threshold exits budget_exhausted."""
    after = [outcome("T1", [Q1], [Q1, Q2])]
    reason, _ = decide([], after, cap_reached=True)
    assert reason == "budget_exhausted"


def test_supervisor_model_error_exits_failed(monkeypatch):
    """TC-ORC-11 / C-005; POL-011: a supervisor model failure exits failed even with nothing covered."""
    after = [outcome("T1", [Q1], [Q1, Q2])]
    reason, _ = decide(after, after, turn_is_eligible=False, supervisor_error=True)
    assert reason == "failed"

    # The node maps the failure to the reason, with the error in exit_detail and no exception.
    from open_deep_research import deep_researcher

    model = helpers.RecordingRunnable([RuntimeError("supervisor model unavailable")])
    helpers.install_model(monkeypatch, deep_researcher, model)

    command = helpers.run_async(
        deep_researcher.supervisor(
            supervisor_state(Q1), config(max_structured_output_retries=1)
        )
    )

    assert helpers.command_goto(command) == "__end__"
    update = helpers.command_update(command)
    assert update.get("exit_reason") == "failed"
    assert "supervisor model unavailable" in (update.get("exit_detail") or "")


@pytest.mark.parametrize(
    ("state_values", "expected"),
    [
        ({"task_results": "covered"}, "covered"),
        ({"research_iterations": 4}, "budget_exhausted"),
        ({"stalled_turns": 2}, "stalled"),
    ],
    ids=["covered_run_stays_covered", "cap", "stall"],
)
def test_supervisor_model_error_goes_through_select_exit(
    monkeypatch, state_values, expected
):
    """ADR-001 §3.4 step 5, POL-011: a failing supervisor ends with the reason `select_exit` returns."""
    from open_deep_research import deep_researcher

    model = helpers.RecordingRunnable([RuntimeError("supervisor model unavailable")])
    helpers.install_model(monkeypatch, deep_researcher, model)
    state = supervisor_state(Q1)
    if state_values.get("task_results") == "covered":
        state["task_results"] = [outcome("T1", [Q1], [Q1])]
    else:
        state.update(state_values)

    command = helpers.run_async(
        deep_researcher.supervisor(
            state, config(max_structured_output_retries=1, max_researcher_iterations=3)
        )
    )

    assert helpers.command_goto(command) == "__end__"
    update = helpers.command_update(command)
    assert update.get("exit_reason") == expected
    notes = helpers.override_value(update.get("notes"))
    assert isinstance(notes, list), "the exit writes notes as at any other exit"
    if expected == "covered":
        assert any("claim for" in note for note in notes)


@pytest.mark.parametrize(
    ("covered", "cap_reached", "supervisor_error", "stalled_turns", "expected"),
    [
        (True, True, True, 5, "covered"),
        (False, True, True, 5, "budget_exhausted"),
        (False, False, True, 2, "stalled"),
        (False, False, True, 0, "failed"),
    ],
    ids=[
        "covered_beats_all",
        "cap_beats_stall_and_error",
        "stall_beats_error",
        "error_alone",
    ],
)
def test_exit_reason_precedence(
    covered, cap_reached, supervisor_error, stalled_turns, expected
):
    """TC-ORC-12 / M-001; INV-003: one reason, chosen as covered > budget_exhausted > stalled > failed."""
    before = [outcome("T1", [Q1], [Q1, Q2])]
    after = [outcome("T1", [Q1, Q2], [Q1, Q2])] if covered else before
    reason, _ = decide(
        before,
        after,
        stalled_turns=stalled_turns,
        cap_reached=cap_reached,
        supervisor_error=supervisor_error,
    )
    assert reason == expected
    exit_without_single_reason_count = int(
        not isinstance(reason, str)
        or reason not in {"covered", "budget_exhausted", "stalled", "failed"}
    )
    assert exit_without_single_reason_count == 0


###################
# The flag-on loop (TC-ORC-07, 08)
###################
class FakeResearcher:
    """Fake researcher subgraph: answers a chosen subset of the task's required questions."""

    def __init__(self, answered: set[str] | None = None):
        self.answered = answered
        self.received: list[object] = []

    async def ainvoke(self, inputs: dict, config=None, **_kwargs):
        task_spec = inputs["task_spec"]
        self.received.append(task_spec)
        answered = (
            task_spec.must_answer
            if self.answered is None
            else [
                question
                for question in task_spec.must_answer
                if question in self.answered
            ]
        )
        result = task_result(
            task_spec.task_id, "complete", task_spec.must_answer, answered=answered
        )
        if answered != task_spec.must_answer:
            result = result.model_copy(
                update={
                    "status": "partial" if answered else "failed",
                    "failure_category": "unanswered",
                    "summary": "summary" if answered else "",
                    "reason": ", ".join(
                        q for q in task_spec.must_answer if q not in answered
                    ),
                }
            )
        return {
            "task_result": result,
            "raw_notes": [],
            "compressed_research": result.summary,
        }


def scripted_supervisor(monkeypatch, turns):
    """Make the supervisor model answer with the scripted turns (or raise them) in order."""
    from open_deep_research import deep_researcher

    model = helpers.RecordingRunnable(turns)
    helpers.install_model(monkeypatch, deep_researcher, model)
    return model


def config(**values) -> dict:
    """Runtime configuration for the loop cases (flag on, coverage threshold 0.8)."""
    base = {
        "task_contract_enabled": True,
        "search_api": "tavily",
        "coverage_threshold": 0.8,
        "research_model": helpers.RESEARCH_MODEL,
        "summarization_model": "openai:gpt-4.1-mini",
        "max_react_tool_calls": 5,
        "max_researcher_iterations": 3,
        "max_concurrent_research_units": 2,
    }
    base.update(values)
    return {"configurable": base}


def supervisor_state(question: str) -> dict:
    """Initial supervisor state for one loop run."""
    return {
        "supervisor_messages": [helpers.human_message(question)],
        "research_brief": question,
        "notes": [],
        "raw_notes": [],
        "research_iterations": 0,
        "task_results": [],
        "stalled_turns": 0,
    }


def delegation(question: str, questions: list[str], call_id: str) -> AIMessage:
    """One supervisor turn that delegates the given questions."""
    return helpers.ai_message(
        tool_calls=[
            helpers.tool_call(
                "ConductResearch",
                {"research_topic": question, "must_answer": questions, "scope": ""},
                call_id,
            )
        ]
    )


def run_loop(
    monkeypatch,
    turns,
    question: str,
    researcher: FakeResearcher | None = None,
    **config_values,
) -> dict:
    """Run the compiled supervisor subgraph and return the state the loop ended with.

    The subgraph applies the state's reducers (``override_reducer`` appends a
    plain list and replaces on an override), exactly as in a real run, so a
    turn's update is merged the way ADR-001 §3.4 and ``memory-design.md`` §2
    describe instead of replacing the conversation or the task results.
    """
    from open_deep_research import deep_researcher

    # The loop can have observed nothing only when the contract types are missing.
    state_types().TaskResult
    scripted_supervisor(monkeypatch, turns)
    monkeypatch.setattr(
        deep_researcher, "researcher_subgraph", researcher or FakeResearcher()
    )
    state = supervisor_state(question)
    state.update(config_values.pop("state", {}))
    runtime = {**config(**config_values), "recursion_limit": 30}
    return helpers.run_async(
        deep_researcher.supervisor_subgraph.ainvoke(state, runtime)
    )


@pytest.mark.parametrize(
    "with_complete", [False, True], ids=["without_complete", "with_complete"]
)
def test_loop_exits_covered(monkeypatch, with_complete):
    """TC-ORC-07 / C-001: a run that answers every question exits covered, with or without ResearchComplete."""
    calls = [
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": Q1, "must_answer": [Q1], "scope": ""},
            "c1",
        )
    ]
    if with_complete:
        calls.append(helpers.tool_call("ResearchComplete", {}, "c2"))
    turns = [helpers.ai_message(tool_calls=calls)]

    state = run_loop(monkeypatch, turns, Q1)

    assert state.get("exit_reason") == "covered"
    assert state.get("exit_detail") == ""
    assert state.get("notes"), "notes hold the counted findings"
    assert [result.task_id for result in state.get("task_results")] == ["T1"]


def test_loop_refuses_completion_below_threshold(monkeypatch):
    """TC-ORC-08 / C-002: ResearchComplete at coverage 0.5 continues and the supervisor is told what is missing."""
    turns = [
        delegation(Q1, [Q1, Q2], "c1"),
        helpers.ai_message(
            tool_calls=[helpers.tool_call("ResearchComplete", {}, "c2")]
        ),
        helpers.ai_message(content="no more tools", tool_calls=[]),
    ]
    researcher = FakeResearcher(answered={Q1})

    state = run_loop(
        monkeypatch, turns, Q1, researcher=researcher, max_researcher_iterations=6
    )

    assert state.get("exit_reason") != "covered"
    assert [result.task_id for result in state.get("task_results")] == ["T1"], (
        "the run keeps its task results across turns"
    )
    refusals = [
        item
        for item in state.get("supervisor_messages", [])
        if isinstance(item, (ToolMessage, HumanMessage))
        and Q2 in helpers.message_text(item)
    ]
    assert refusals, (
        "a completion request below the threshold names the unanswered question"
    )
    complete_answer = next(
        item
        for item in state.get("supervisor_messages", [])
        if isinstance(item, ToolMessage) and item.tool_call_id == "c2"
    )
    assert Q2 in helpers.message_text(complete_answer), (
        "the ResearchComplete call itself is answered with the unanswered question"
    )
