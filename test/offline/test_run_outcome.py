"""REQ-004: the run output states whether research was complete, partial or failed.

Covers TC-DLV-09 to TC-DLV-16 (``verification-constraints.md`` §7, delivery) and
INV-002, each case once as its table row defines it. The interface is
``delivery/outcome.py`` (`assess_research`, `finish_outcome`,
`render_limitations`, ADR-003 §5), the node `check_research_outcome` and the
flag-on branch of `final_report_generation`; POL-015 to POL-017 are checked at
the level the table names. As ADR-003 §7 requires, C-002, C-004 and C-005 also
run the compiled graph from `check_research_outcome` on with a fake report model.

The decision rule and the rendering read task results (ADR-001 §5), so every
record here is a contract type.
"""

import pytest
from langchain_core.messages import AIMessage

from test.offline import helpers

URL_A = "https://example.org/a"


def state_types():
    """Return the contract types of ``state.py`` (ADR-001 §5)."""
    import open_deep_research.state as state

    return state


def record(task_id: str, status: str, question: str, reason: str = ""):
    """Return a contract task result with the fields the outcome rule reads (ADR-003 §3.2).

    A complete record answers ``question``; a partial one answers a second
    question of its own and leaves ``question`` unanswered; a failed one has no
    finding.
    """
    state = state_types()
    if status == "failed":
        spec = state.TaskSpec(
            task_id=task_id,
            research_topic="topic",
            scope="",
            must_answer=[question],
            max_tool_calls=1,
        )
        return state.TaskResult.failed(spec, "runtime", reason or "failed")
    answered = question if status == "complete" else f"question answered by {task_id}"
    required = [question] if status == "complete" else [answered, question]
    return state.TaskResult(
        task_id=task_id,
        status=status,
        must_answer=required,
        findings=[
            state.Finding(
                claim=f"claim {task_id}",
                answers=[answered],
                sources=[state.Source(title="A", url=URL_A)],
            )
        ],
        summary="summary",
        tool_calls=1,
        failure_category=None if status == "complete" else "unanswered",
        reason=reason,
    )


def complete(
    task_id: str = "T1", question: str = "Which regulation governs battery recycling?"
):
    """A complete task result with one sourced finding."""
    return record(task_id, "complete", question)


def failed(task_id: str = "T2", reason: str = "provider error"):
    """A failed task result whose reason names the failure."""
    return record(task_id, "failed", "What share is recycled?", reason=reason)


def partial(task_id: str = "T3", question: str = "What share is recycled?"):
    """A partial task result whose reason names the unanswered question."""
    return record(task_id, "partial", question, reason=question)


###################
# The outcome rule (TC-DLV-09 to 15)
###################
def test_covered_run_is_complete():
    """TC-DLV-09 / C-001: all tasks complete and exit covered gives complete, no failed task, no limitations."""
    from open_deep_research.delivery.outcome import (
        assess_research,
        finish_outcome,
        render_limitations,
    )

    results = [complete("T1"), complete("T2")]
    decision = assess_research(results, "covered", "")

    assert decision.outcome == "complete"
    assert decision.report_allowed is True
    assert decision.failed_tasks == []
    outcome, detail = finish_outcome(
        decision, report_error=None, findings_truncated=False
    )
    assert (outcome, detail) == ("complete", "")
    assert render_limitations(results, findings_truncated=False) == ""


def test_failed_task_makes_run_partial(monkeypatch):
    """TC-DLV-10 / C-002; INV-002: one failed task makes the run partial and the limitations name it."""
    from open_deep_research.delivery.outcome import (
        assess_research,
        finish_outcome,
        render_limitations,
    )

    results = [complete("T1"), failed("T2")]
    decision = assess_research(results, "covered", "")

    assert decision.outcome == "partial"
    assert [task.task_id for task in decision.failed_tasks] == ["T2"]
    assert decision.failed_tasks[0].reason == "provider error"
    outcome, _detail = finish_outcome(
        decision, report_error=None, findings_truncated=False
    )
    assert outcome == "partial"

    limitations = render_limitations(results, findings_truncated=False)
    assert "T2" in limitations and "provider error" in limitations
    assert "T1" not in limitations, "a complete task is not a limitation"
    partial_limitations = render_limitations([partial("T3")], findings_truncated=False)
    assert "T3" in partial_limitations
    assert "What share is recycled?" in partial_limitations, (
        "a partial task lists its unanswered question"
    )

    # Through the graph (ADR-003 §7): the fake report does not mention T2.
    model = FakeReportModel(["# Battery Recycling\n\nA report without any limitation."])
    final = run_after_research(
        monkeypatch,
        [
            task_result("complete", "T1", QUESTION),
            task_result("failed", "T2", "What share is recycled?"),
        ],
        model,
    )

    assert final["research_outcome"] == "partial"
    assert [task.task_id for task in final["failed_tasks"]] == ["T2"]
    assert final["failed_tasks"][0].reason == "provider error"
    assert "T2" in final["final_report"] and "provider error" in final["final_report"]
    assert final["messages"][-1].content == final["final_report"]
    assert len(model.prompts) == 1


@pytest.mark.parametrize("exit_reason", ["stalled", "budget_exhausted"])
def test_non_covered_exit_is_partial(exit_reason):
    """TC-DLV-11 / C-003: a covered exit is required for complete; stall and cap exits are partial."""
    from open_deep_research.delivery.outcome import assess_research

    decision = assess_research(
        [complete("T1"), complete("T2")], exit_reason, "stopped early"
    )
    assert decision.outcome == "partial"
    assert decision.report_allowed is True


def test_no_finding_run_is_failed(monkeypatch):
    """TC-DLV-12 / C-004: with no complete or partial task the run is failed and the report is not allowed."""
    from open_deep_research.delivery.outcome import assess_research

    decision = assess_research([failed("T1")], "covered", "")

    assert decision.outcome == "failed"
    assert decision.report_allowed is False
    assert decision.failed_tasks and decision.failed_tasks[0].task_id == "T1"

    # Through the graph (ADR-003 §3.1, §7): the run ends before the report node.
    model = FakeReportModel(["a report that must never be written"])
    final = run_after_research(
        monkeypatch, [task_result("failed", "T1", QUESTION)], model
    )

    assert model.prompts == [], "the report model is called 0 times"
    assert final["research_outcome"] == "failed"
    assert final["final_report"] == ""
    assert [task.task_id for task in final["failed_tasks"]] == ["T1"]


def test_report_error_run_is_failed(monkeypatch):
    """TC-DLV-13 / C-005: a report error gives outcome failed, whatever the pre-report decision was."""
    from open_deep_research.delivery.outcome import assess_research, finish_outcome

    decision = assess_research([complete("T1")], "covered", "")
    outcome, detail = finish_outcome(
        decision, report_error="model said no", findings_truncated=False
    )

    assert outcome == "failed"
    assert "model said no" in detail

    # Through the graph (ADR-003 §3.3, §7): the error appears only in outcome_detail.
    model = FakeReportModel([RuntimeError("writer model unavailable")])
    final = run_after_research(
        monkeypatch, [task_result("complete", "T1", QUESTION)], model
    )

    assert final["research_outcome"] == "failed"
    assert final["final_report"] == ""
    assert "writer model unavailable" in final["outcome_detail"]
    assert all(
        "writer model unavailable" not in helpers.message_text(message)
        for message in final["messages"]
    )


def test_truncated_findings_make_run_partial():
    """TC-DLV-14 / C-006: truncated findings turn complete into partial and the limitations say so."""
    from open_deep_research.delivery.outcome import (
        assess_research,
        finish_outcome,
        render_limitations,
    )

    results = [complete("T1")]
    decision = assess_research(results, "covered", "")
    outcome, _detail = finish_outcome(
        decision, report_error=None, findings_truncated=True
    )

    assert outcome == "partial"
    limitations = render_limitations(results, findings_truncated=True)
    assert "left out" in limitations.lower()


def test_failed_exit_is_failed_outcome():
    """TC-DLV-15 / M-001; INV-002: exit failed stays failed, and exhausted truncation retries fail too."""
    from open_deep_research.delivery.outcome import assess_research, finish_outcome

    decision = assess_research([complete("T1")], "failed", "supervisor model error")
    assert decision.outcome == "failed"
    assert "supervisor model error" in decision.detail
    assert (
        finish_outcome(decision, report_error=None, findings_truncated=False)[0]
        == "failed"
    )

    retries_used_up = assess_research([complete("T1")], "covered", "")
    outcome, detail = finish_outcome(
        retries_used_up,
        report_error="maximum retries exceeded",
        findings_truncated=True,
    )
    assert outcome == "failed" and detail
    false_complete_outcome_count = int(outcome == "complete")
    assert false_complete_outcome_count == 0


###################
# The node and the report (TC-DLV-10, 12 to 16)
###################
class FakeReportModel(helpers.RecordingRunnable):
    """Fake chat model for the report: records the prompts and returns or raises as scripted."""

    def __init__(self, responses):
        super().__init__(
            [
                AIMessage(content=response)
                if not isinstance(response, Exception)
                else response
                for response in responses
            ]
        )
        self.prompts: list[str] = []

    def _next(self, messages):
        self.prompts.append(helpers.message_text(messages[-1]))
        if not self.turns:
            raise AssertionError(
                "the report model made more calls than the test scripted"
            )
        turn = self.turns.pop(0)
        if isinstance(turn, Exception):
            raise turn
        return turn


def install_report_model(monkeypatch, model):
    """Make the report node use ``model`` through the shared model of ``deep_researcher``."""
    from open_deep_research import deep_researcher

    helpers.install_model(monkeypatch, deep_researcher, model)


def report_config(**values) -> dict:
    """Runtime configuration for the outcome cases."""
    base = {
        "task_contract_enabled": True,
        "search_api": "tavily",
        "final_report_model": "openai:gpt-4.1",
        "research_model": "openai:gpt-4.1",
        "summarization_model": "openai:gpt-4.1-mini",
    }
    base.update(values)
    return {"configurable": base}


def task_result(status: str, task_id: str, question: str, reason: str = ""):
    """Build a contract task result for the node cases (ADR-001 §5)."""
    state = state_types()
    finding = state.Finding(
        claim=f"claim {task_id}",
        answers=[question],
        sources=[state.Source(title="A", url=URL_A)],
    )
    if status == "failed":
        spec = state.TaskSpec(
            task_id=task_id,
            research_topic="topic",
            scope="",
            must_answer=[question],
            max_tool_calls=1,
        )
        return state.TaskResult.failed(spec, "runtime", reason or "provider error")
    return state.TaskResult(
        task_id=task_id,
        status=status,
        must_answer=[question],
        findings=[finding],
        summary="summary",
        tool_calls=1,
        failure_category=None if status == "complete" else "unanswered",
        reason=reason,
    )


QUESTION = "Which regulation governs battery recycling?"


def agent_state(results: list, exit_reason="covered", exit_detail="") -> dict:
    """Agent state as `check_research_outcome` receives it."""
    return {
        "messages": [helpers.human_message(QUESTION)],
        "supervisor_messages": [],
        "research_brief": "battery recycling",
        "raw_notes": [],
        "notes": [f"Task T1: topic\n- claim [1]\n### Sources\n[1] A: {URL_A}"],
        "task_results": results,
        "exit_reason": exit_reason,
        "exit_detail": exit_detail,
        "final_report": "",
    }


def run_after_research(
    monkeypatch, results: list, model, exit_reason="covered", exit_detail=""
) -> dict:
    """Run the compiled top-level graph from the end of research on (ADR-003 §7).

    The graph is the real builder of ``deep_researcher`` with an in-memory
    checkpointer, so its own edges decide which nodes run after
    ``research_supervisor``; the state is recorded as that node's output.
    """
    from langgraph.checkpoint.memory import MemorySaver

    from open_deep_research import deep_researcher

    install_report_model(monkeypatch, model)
    graph = deep_researcher.deep_researcher_builder.compile(checkpointer=MemorySaver())
    runtime = report_config()
    runtime["configurable"]["thread_id"] = "run-outcome"

    async def scenario():
        await graph.aupdate_state(
            runtime,
            agent_state(results, exit_reason, exit_detail),
            as_node="research_supervisor",
        )
        return await graph.ainvoke(None, runtime)

    return helpers.run_async(scenario())


def test_check_research_outcome_ends_a_findingless_run(monkeypatch):
    """TC-DLV-12 / C-004; POL-015: no finding ends the run with an empty report and no report model call."""
    from open_deep_research import deep_researcher

    model = FakeReportModel([])
    install_report_model(monkeypatch, model)

    command = helpers.run_async(
        deep_researcher.check_research_outcome(
            agent_state([task_result("failed", "T1", QUESTION)]), report_config()
        )
    )

    assert helpers.command_goto(command) == "__end__"
    update = helpers.command_update(command)
    assert update["research_outcome"] == "failed"
    assert update["final_report"] == ""
    failed_tasks = helpers.override_value(update["failed_tasks"])
    assert failed_tasks and failed_tasks[0].task_id == "T1"
    assert model.prompts == [], "the report model is never called"
    assert update.get("notes") in ([], {"type": "override", "value": []})
    assert "messages" not in update, "the failed path adds no message"


def test_check_research_outcome_forwards_a_scored_run():
    """ADR-003 §3.1, §3.2: a run with validated findings goes to the report with failed_tasks written."""
    from open_deep_research import deep_researcher

    results = [
        task_result("complete", "T1", QUESTION),
        task_result("failed", "T2", "What share is recycled?"),
    ]

    command = helpers.run_async(
        deep_researcher.check_research_outcome(agent_state(results), report_config())
    )

    assert helpers.command_goto(command) == "final_report_generation"
    update = helpers.command_update(command)
    assert update["failed_tasks"] == {"type": "override", "value": [results[1]]}, (
        "failed_tasks is always written as an override (memory-design.md §5)"
    )
    assert "research_outcome" not in update, "the provisional outcome is not stored"


def test_report_generation_appends_limitations(monkeypatch):
    """TC-DLV-10 / C-002: a partial run gets the limitations section although the fake report omits it."""
    from open_deep_research import deep_researcher

    model = FakeReportModel(["# Battery Recycling\n\nA report without any limitation."])
    install_report_model(monkeypatch, model)
    results = [
        task_result("complete", "T1", QUESTION),
        task_result("failed", "T2", "What share is recycled?"),
    ]

    update = helpers.run_async(
        deep_researcher.final_report_generation(agent_state(results), report_config())
    )

    assert update["research_outcome"] == "partial"
    report = update["final_report"]
    assert report.startswith("# Battery Recycling")
    assert "T2" in report and "provider error" in report
    aimessages = [
        message for message in update["messages"] if isinstance(message, AIMessage)
    ]
    assert aimessages and aimessages[-1].content == report, (
        "the chat message holds the same text"
    )
    assert update["notes"] == {"type": "override", "value": []}, (
        "the report node clears notes as the baseline does (ADR-003 §3.2)"
    )
    assert "failed_tasks" not in update, (
        "only check_research_outcome writes failed_tasks"
    )


def test_report_generation_keeps_a_report_without_limitation(monkeypatch):
    """ADR-003 §3.3: a complete run gets no limitations section from the node either."""
    from open_deep_research import deep_researcher

    model = FakeReportModel(["# Battery Recycling\n\nA complete report."])
    install_report_model(monkeypatch, model)

    update = helpers.run_async(
        deep_researcher.final_report_generation(
            agent_state([task_result("complete", "T1", QUESTION)]), report_config()
        )
    )

    assert update["research_outcome"] == "complete"
    assert update["final_report"] == "# Battery Recycling\n\nA complete report."


def test_report_error_empties_the_report(monkeypatch):
    """TC-DLV-13 / C-005; POL-016: a non-token report error empties the report and goes only to outcome_detail."""
    from open_deep_research import deep_researcher

    model = FakeReportModel([RuntimeError("writer model unavailable")])
    install_report_model(monkeypatch, model)

    update = helpers.run_async(
        deep_researcher.final_report_generation(
            agent_state([task_result("complete", "T1", QUESTION)]), report_config()
        )
    )

    assert update["research_outcome"] == "failed"
    assert update["final_report"] == ""
    assert "writer model unavailable" in update["outcome_detail"]
    assert all(
        "writer model unavailable" not in helpers.message_text(message)
        for message in update.get("messages", [])
    )
    assert update["notes"] == {"type": "override", "value": []}


def test_truncated_findings_report_is_partial(monkeypatch):
    """TC-DLV-14 / C-006; POL-017: truncating findings to fit the model makes the outcome partial and says so."""
    from open_deep_research import deep_researcher

    model = FakeReportModel(
        [helpers.token_limit_error("openai"), "# Report\n\nShort report."]
    )
    install_report_model(monkeypatch, model)

    update = helpers.run_async(
        deep_researcher.final_report_generation(
            agent_state([task_result("complete", "T1", QUESTION)]), report_config()
        )
    )

    assert update["research_outcome"] == "partial"
    assert "left out" in update["final_report"].lower()


def test_flag_off_keeps_baseline_report(monkeypatch):
    """TC-DLV-16: with the flag off check_research_outcome only forwards and the report is the baseline one."""
    from open_deep_research import deep_researcher

    results = [task_result("complete", "T1", QUESTION)]
    command = helpers.run_async(
        deep_researcher.check_research_outcome(
            agent_state(results), report_config(task_contract_enabled=False)
        )
    )
    assert helpers.command_goto(command) == "final_report_generation"
    assert not (
        {"research_outcome", "outcome_detail", "failed_tasks", "final_report"}
        & set(helpers.command_update(command))
    )

    model = FakeReportModel(["# Baseline report"])
    install_report_model(monkeypatch, model)
    update = helpers.run_async(
        deep_researcher.final_report_generation(
            agent_state(results), report_config(task_contract_enabled=False)
        )
    )

    assert update["final_report"] == "# Baseline report"
    assert update["notes"] == {"type": "override", "value": []}
    assert "research_outcome" not in update
