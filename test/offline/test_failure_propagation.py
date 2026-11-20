"""REQ-002: no delegated research task is lost or silently treated as completed.

Covers TC-DLV-01 to TC-DLV-08 and TC-DLV-17 (``verification-constraints.md`` §7,
delivery) and INV-007. The fan-out interface is ``delivery/execution.py``
(`run_delegations`, `classify_task_error`, ADR-002 §3); the cap branch and the
`notes` of the flag-on turn are ADR-001 §3.4. Researchers are fake coroutines.
"""

import asyncio

import pytest
from langchain_core.messages import ToolMessage

from test.offline import helpers

URL_A = "https://example.org/a"
RESEARCH_MODEL = "openai:gpt-4.1"


def state_types():
    """Return the contract types of ``state.py`` (ADR-001 §5)."""
    import open_deep_research.state as state

    return state


def spec(task_id: str, topic: str = "topic"):
    """Return one delegated task."""
    state = state_types()
    return state.TaskSpec(
        task_id=task_id,
        research_topic=topic,
        scope="",
        must_answer=[f"{topic} question"],
        max_tool_calls=5,
    )


def complete_output(task_spec) -> dict:
    """A researcher output with one sourced finding for the task's question."""
    state = state_types()
    task_result = state.TaskResult(
        task_id=task_spec.task_id,
        status="complete",
        must_answer=task_spec.must_answer,
        findings=[
            state.Finding(
                claim=f"claim of {task_spec.task_id}",
                answers=[task_spec.must_answer[0]],
                sources=[state.Source(title="A", url=URL_A)],
            )
        ],
        summary=f"summary of {task_spec.task_id}",
        tool_calls=1,
        failure_category=None,
        reason="",
    )
    return {
        "task_result": task_result,
        "raw_notes": [f"raw note of {task_spec.task_id}"],
        "compressed_research": "text",
    }


###################
# The fan-out in isolation (ADR-002 §3)
###################
def run_delegations(specs, run_one, max_concurrent=5):
    """Call `run_delegations` with the interface of ADR-002 §3."""
    from open_deep_research.delivery.execution import run_delegations as run

    return helpers.run_async(
        run(
            specs, run_one, max_concurrent=max_concurrent, research_model=RESEARCH_MODEL
        )
    )


def test_child_exception_becomes_failed_result():
    """TC-DLV-01 / C-001: one RuntimeError fails only its task, with category runtime and the original message."""

    async def run_one(spec_: object):
        raise RuntimeError("boom")

    results, notes = run_delegations([spec("T1")], run_one)

    assert len(results) == 1
    failed = results[0]
    assert (failed.status, failed.failure_category) == ("failed", "runtime")
    assert "boom" in failed.reason
    assert failed.task_id == "T1"
    assert notes == []


def test_sibling_result_kept_on_failure(monkeypatch):
    """TC-DLV-02 / C-002: the finding of the sibling is kept and only the raising task fails."""

    async def run_one(spec_: object):
        if spec_.task_id == "T2":
            raise RuntimeError("provider error")
        return complete_output(spec_)

    results, notes = run_delegations([spec("T1"), spec("T2")], run_one)

    assert [r.task_id for r in results] == ["T1", "T2"]
    assert results[0].status == "complete" and len(results[0].findings) == 1
    assert (results[1].status, results[1].failure_category) == ("failed", "runtime")
    # ADR-002 §3.5: the raw notes of the researchers that returned are kept.
    assert notes == ["raw note of T1"]

    # Through the flag-on turn: the finding reaches the tool messages and raw_notes.
    from open_deep_research import deep_researcher

    monkeypatch.setattr(
        deep_researcher, "researcher_subgraph", RaisingResearcher(raise_for="T2")
    )
    calls = [
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": topic, "must_answer": [], "scope": ""},
            call_id,
        )
        for topic, call_id in (("topic", "c1"), ("other topic", "c2"))
    ]

    update = helpers.command_update(
        helpers.run_async(deep_researcher.supervisor_tools(turn(calls), config()))
    )

    messages = {
        message.tool_call_id: helpers.message_text(message)
        for message in update["supervisor_messages"]
        if isinstance(message, ToolMessage)
    }
    assert "complete" in messages["c1"] and "summary of T1" in messages["c1"]
    assert "failed" in messages["c2"]
    assert "raw note of T1" in "\n".join(update.get("raw_notes", []))
    assert [r.status for r in result_list(update)] == ["complete", "failed"]


def test_token_limit_error_is_task_failure():
    """TC-DLV-03 / C-003: a recognised token-limit error fails the task with category token_limit."""

    async def run_one(_spec: object):
        raise helpers.token_limit_error("openai")

    results, _notes = run_delegations([spec("T1")], run_one)

    assert (results[0].status, results[0].failure_category) == ("failed", "token_limit")


def test_classification_uses_the_research_model():
    """ADR-002 §3.3: `classify_task_error` maps a token-limit error and anything else to the two categories."""
    from open_deep_research.delivery.execution import classify_task_error

    assert (
        classify_task_error(helpers.token_limit_error("openai"), RESEARCH_MODEL)
        == "token_limit"
    )
    assert (
        classify_task_error(
            helpers.token_limit_error("anthropic"), "anthropic:claude-sonnet-4"
        )
        == "token_limit"
    )
    assert classify_task_error(ValueError("bad"), RESEARCH_MODEL) == "runtime"


def test_overflow_delegations_are_queued():
    """TC-DLV-04 / C-004, M-001; INV-007: three delegations at limit 1 all run, one at a time."""
    running = 0
    peak = 0
    order: list[str] = []

    async def run_one(spec_: object):
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        order.append(spec_.task_id)
        await asyncio.sleep(0.01)
        running -= 1
        return complete_output(spec_)

    specs = [spec("T1"), spec("T2"), spec("T3")]
    results, _notes = run_delegations(specs, run_one, max_concurrent=1)

    assert [r.task_id for r in results] == ["T1", "T2", "T3"], (
        "one result per spec, in spec order"
    )
    assert peak == 1, "at most max_concurrent tasks run at once"
    assert sorted(order) == ["T1", "T2", "T3"]
    dropped_delegation_count = len(specs) - len(results)
    assert dropped_delegation_count == 0


def test_no_task_running_after_join():
    """TC-DLV-06 / C-006; INV-007: the fan-out returns only after every task it started has finished."""
    finished: set[str] = set()

    async def run_one(spec_: object):
        if spec_.task_id == "T1":
            raise RuntimeError("fails at once")
        await asyncio.sleep(0.02)
        finished.add(spec_.task_id)
        return complete_output(spec_)

    # The sibling is still sleeping when the raising task has failed.
    results, _notes = run_delegations([spec("T1"), spec("T2")], run_one)

    assert len(results) == 2
    assert finished == {"T2"}, (
        "no started task is still pending when run_delegations returns"
    )
    assert (results[0].status, results[1].status) == ("failed", "complete")


async def run_delegations_async(specs, run_one, max_concurrent=5):
    """Await `run_delegations` inside a running loop."""
    from open_deep_research.delivery.execution import run_delegations as run

    return await run(
        specs, run_one, max_concurrent=max_concurrent, research_model=RESEARCH_MODEL
    )


def test_cancellation_is_not_swallowed():
    """TC-DLV-08 / INV-007: asyncio.CancelledError propagates and creates no task result."""
    started = asyncio.Event()

    async def run_one(_spec: object):
        started.set()
        await asyncio.sleep(30)
        return complete_output(_spec)

    async def scenario():
        task = asyncio.ensure_future(run_delegations_async([spec("T1")], run_one))
        await started.wait()
        task.cancel()
        return await task

    with pytest.raises(asyncio.CancelledError):
        helpers.run_async(scenario())


def test_missing_task_result_becomes_failed():
    """TC-DLV-17 / POL-007: an output without task_result fails that task, siblings keep their results."""

    async def run_one(spec_: object):
        if spec_.task_id == "T2":
            return {"compressed_research": "text", "raw_notes": []}
        return complete_output(spec_)

    results, _notes = run_delegations([spec("T1"), spec("T2")], run_one)

    assert results[0].status == "complete"
    assert (results[1].status, results[1].failure_category) == (
        "failed",
        "invalid_result",
    )


def test_unexpected_result_type_becomes_failed():
    """TC-DLV-17: a task_result of another shape is not accepted as a validated finding."""

    async def run_one(_spec: object):
        return {"task_result": {"status": "complete"}, "raw_notes": []}

    results, _notes = run_delegations([spec("T1")], run_one)

    assert (results[0].status, results[0].failure_category) == (
        "failed",
        "invalid_result",
    )


###################
# The flag-on turn (TC-DLV-01, 02, 05, 07)
###################
class RaisingResearcher:
    """Fake researcher subgraph that raises for a given task id."""

    def __init__(self, raise_for: str | None = None, error: Exception | None = None):
        self.raise_for = raise_for
        self.error = error or RuntimeError("boom")

    async def ainvoke(self, inputs: dict, config=None, **_kwargs):
        spec_: object = inputs["task_spec"]
        if spec_.task_id == self.raise_for:
            raise self.error
        return complete_output(spec_)


def turn(calls: list[dict], **state) -> dict:
    """State for one supervisor_tools call holding the given delegations."""
    return {
        "supervisor_messages": [helpers.ai_message(tool_calls=calls)],
        "research_brief": "b",
        "notes": [],
        "raw_notes": [],
        "research_iterations": state.pop("research_iterations", 1),
        "task_results": state.pop("task_results", []),
        "stalled_turns": 0,
        **state,
    }


def config(**values) -> dict:
    """Runtime configuration with the task contract on."""
    base = {
        "task_contract_enabled": True,
        "search_api": "tavily",
        "research_model": RESEARCH_MODEL,
        "summarization_model": "openai:gpt-4.1-mini",
        "max_react_tool_calls": 5,
        "max_researcher_iterations": 3,
        "max_concurrent_research_units": 5,
    }
    base.update(values)
    return {"configurable": base}


def result_list(update: dict):
    """Return the task results of a flag-on turn, failing with the missing behaviour instead of a KeyError."""
    if "task_results" not in update:
        pytest.fail("the flag-on turn must write task_results", pytrace=False)
    return update["task_results"]


def test_child_exception_does_not_end_the_research_phase(monkeypatch):
    """TC-DLV-01 / C-001: a raising researcher routes the turn back to the supervisor, not to END."""
    from open_deep_research import deep_researcher

    # The flag-on turn cannot dispatch a spec nor record a result without the contract types.
    state_types().TaskSpec
    monkeypatch.setattr(
        deep_researcher, "researcher_subgraph", RaisingResearcher(raise_for="T1")
    )
    call = helpers.tool_call(
        "ConductResearch",
        {"research_topic": "topic", "must_answer": [], "scope": ""},
        "c1",
    )

    command = helpers.run_async(
        deep_researcher.supervisor_tools(turn([call]), config())
    )

    assert helpers.command_goto(command) == "supervisor"
    update = helpers.command_update(command)
    assert "exit_reason" not in update, (
        "a researcher failure must not end the research phase"
    )
    if "task_results" not in update:
        pytest.fail(
            "the flag-on turn must record one task result per delegation", pytrace=False
        )
    failed = update["task_results"][0]
    assert (failed.status, failed.failure_category) == ("failed", "runtime")
    assert "boom" in failed.reason


def test_failure_text_not_in_notes(monkeypatch):
    """TC-DLV-07 / C-007, M-002; INV-002: notes hold only validated findings, both failures only as results."""
    from open_deep_research import deep_researcher

    class MixedResearcher:
        async def ainvoke(self, inputs: dict, config=None, **_kwargs):
            spec_: object = inputs["task_spec"]
            if spec_.task_id == "T1":
                raise RuntimeError("provider exploded")
            return {
                "compressed_research": "Error synthesizing research report: Maximum retries exceeded",
                "raw_notes": [],
            }

    monkeypatch.setattr(deep_researcher, "researcher_subgraph", MixedResearcher())
    calls = [
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": "a", "must_answer": [], "scope": ""},
            "c1",
        ),
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": "b", "must_answer": [], "scope": ""},
            "c2",
        ),
    ]

    # The previous turn already made no progress, so this one ends the loop
    # (stalled) and writes `notes` (ADR-001 §3.4 step 7).
    command = helpers.run_async(
        deep_researcher.supervisor_tools(turn(calls, stalled_turns=1), config())
    )
    update = helpers.command_update(command)

    assert helpers.command_goto(command) == "__end__"
    assert "notes" in update, "the ending turn writes notes"
    written = helpers.override_value(update["notes"])
    notes = "\n".join(written)
    assert "provider exploded" not in notes
    assert "Error synthesizing research report" not in notes
    assert all(not note.strip() for note in written), (
        "nothing validated, so nothing is noted"
    )

    failed = [result for result in result_list(update) if result.status == "failed"]
    assert len(failed) == 2
    failure_text_in_notes_count = sum(
        1 for note in written if "Error" in note or "exploded" in note
    )
    assert failure_text_in_notes_count == 0


def test_delegations_left_at_exit_are_failed(monkeypatch):
    """TC-DLV-05 / C-005; INV-007: delegations on the cap turn end failed/not_run, each with a ToolMessage."""
    from open_deep_research import deep_researcher

    ran: list[str] = []

    class AlwaysRun:
        async def ainvoke(self, inputs: dict, config=None, **_kwargs):
            ran.append(inputs["task_spec"].task_id)
            return complete_output(inputs["task_spec"])

    monkeypatch.setattr(deep_researcher, "researcher_subgraph", AlwaysRun())
    calls = [
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": "a", "must_answer": [], "scope": ""},
            "c1",
        ),
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": "b", "must_answer": [], "scope": ""},
            "c2",
        ),
    ]
    # Task ids continue across the run (ADR-001 §3.1), so this turn's tasks are
    # T2 and T3; each ToolMessage must still answer its own delegation call.
    state = turn(
        calls,
        research_iterations=4,
        task_results=[
            state_types().TaskResult.failed(spec("T1"), "unanswered", "none")
        ],
    )

    command = helpers.run_async(
        deep_researcher.supervisor_tools(state, config(max_researcher_iterations=3))
    )
    update = helpers.command_update(command)

    assert ran == [], "no delegation runs on the cap turn"
    results = result_list(update)
    assert [r.task_id for r in results] == ["T2", "T3"]
    assert all(
        r.status == "failed" and r.failure_category == "not_run" for r in results
    )
    tool_messages = [
        m for m in update["supervisor_messages"] if isinstance(m, ToolMessage)
    ]
    assert {m.tool_call_id for m in tool_messages} == {"c1", "c2"}
    assert helpers.command_goto(command) == "__end__"
    assert update.get("exit_reason") == "budget_exhausted"


def test_every_delegation_of_a_turn_ends_with_a_result(monkeypatch):
    """INV-007 / M-001: a mixed turn yields exactly one result per accepted delegation."""
    from open_deep_research import deep_researcher

    monkeypatch.setattr(
        deep_researcher, "researcher_subgraph", RaisingResearcher(raise_for="T2")
    )
    calls = [
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": f"topic {i}", "must_answer": [], "scope": ""},
            f"c{i}",
        )
        for i in range(1, 4)
    ]

    update = helpers.command_update(
        helpers.run_async(deep_researcher.supervisor_tools(turn(calls), config()))
    )

    assert [r.task_id for r in result_list(update)] == ["T1", "T2", "T3"]
    tool_messages = [
        m for m in update["supervisor_messages"] if isinstance(m, ToolMessage)
    ]
    assert {m.tool_call_id for m in tool_messages} == {"c1", "c2", "c3"}
    dropped_delegation_count = len(calls) - len(result_list(update))
    assert dropped_delegation_count == 0
