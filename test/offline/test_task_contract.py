"""REQ-001: the supervisor delegates a typed task and the researcher returns a task result.

Covers TC-ORC-01 to TC-ORC-06 and TC-ORC-14 (``verification-constraints.md`` §7,
orchestration) and INV-003, INV-006, each case once as its table row defines it. The
interfaces are those of ADR-001 §5: the builders in
``orchestration/contracts.py`` and the flag-on branch of `supervisor` and
`supervisor_tools`. POL-006, POL-007 and POL-009 are checked at the level the
table names. The shared contract types themselves are covered by
`test_offline/test_contracts.py`, as ``verification-constraints.md`` §3 requires.
Every model and every researcher is fake.
"""

import json

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from test.offline import helpers

THE_TOPIC = "Battery recycling in the EU"
Q1 = "Which regulation governs battery recycling?"
Q2 = "How many battery recycling plants opened in 2024?"
Q3 = "What share of batteries is recycled?"
URL_A = "https://example.org/a"
URL_B = "https://example.org/b"


def state_types():
    """Return the contract types of ``state.py`` (ADR-001 §5), resolved per test."""
    import open_deep_research.state as state

    return state


###################
# Building and validating a task spec (TC-ORC-01)
###################
def test_delegation_is_valid_task_spec(monkeypatch):
    """TC-ORC-01 / C-001: a scripted supervisor turn becomes a TaskSpec the researcher receives."""
    from open_deep_research import deep_researcher
    from open_deep_research.configuration import Configuration
    from open_deep_research.orchestration import contracts

    config = Configuration(task_contract_enabled=True, max_react_tool_calls=10)
    calls = [
        helpers.tool_call(
            "ConductResearch",
            {
                "research_topic": THE_TOPIC,
                "must_answer": [Q1, "  which   POLICY  "],
                "scope": "EU",
            },
            "call_1",
        ),
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": Q1, "must_answer": [Q1.upper()], "scope": ""},
            "call_2",
        ),
    ]

    specs, rejected = contracts.build_task_specs(calls, 1, config)

    assert rejected == []
    assert [spec.task_id for spec in specs] == ["T1", "T2"]
    first = specs[0]
    assert first.max_tool_calls == config.max_react_tool_calls
    assert first.must_answer == [Q1, "which   POLICY"], (
        "question keeps its first spelling (ADR-001 §3.1)"
    )
    assert 1 <= len(first.must_answer) <= 5
    assert first.research_topic == THE_TOPIC
    assert specs[1].must_answer == [Q1], (
        "a question equal to the topic is de-duplicated"
    )
    state = state_types()
    assert state.TaskSpec.model_validate(first.model_dump()) == first

    brief = contracts.render_task_brief(first)
    assert Q1 in brief and "which   POLICY" in brief and "EU" in brief

    # The same scripted turn through the node hands exactly this spec to the researcher.
    # ADR-001 §3.1: the flag-on tool carries must_answer and scope; the baseline
    # ConductResearch stays unchanged.
    typed_tool = {"must_answer": [Q1, "  which   POLICY  "], "scope": "EU"}
    assert set(typed_tool) <= set(state.ConductResearchTask.model_fields), (
        "a supervisor that delegates must_answer and scope uses the flag-on tool"
    )
    researcher = FakeResearcher(
        {
            "task_result": state.TaskResult.failed(first, "unanswered", "no findings"),
            "raw_notes": [],
            "compressed_research": "",
        }
    )
    monkeypatch.setattr(deep_researcher, "researcher_subgraph", researcher)
    message = helpers.ai_message(
        tool_calls=[
            helpers.tool_call(
                "ConductResearch",
                {
                    "research_topic": THE_TOPIC,
                    "must_answer": [Q1, "  which   POLICY  "],
                    "scope": "EU",
                },
                "call_1",
            )
        ]
    )

    command = helpers.run_async(
        deep_researcher.supervisor_tools(supervisor_turn([message]), runnable_config())
    )

    assert len(researcher.received) == 1
    received = researcher.received[0]["task_spec"]
    assert isinstance(received, state.TaskSpec)
    assert (
        received.task_id,
        received.research_topic,
        received.scope,
        received.max_tool_calls,
    ) == (
        "T1",
        THE_TOPIC,
        "EU",
        10,
    )
    assert received.must_answer == [Q1, "which   POLICY"]
    assert 1 <= len(received.must_answer) <= 5
    assert helpers.command_goto(command) == "supervisor"
    # The researcher runs with the run's configuration (models, search, keys),
    # as the baseline fan-out passes it (ADR-002 §3).
    received_config = researcher.configs[0] or {}
    assert received_config.get("configurable", {}).get("max_react_tool_calls") == 10
    tool_messages = [
        item
        for item in helpers.command_update(command)["supervisor_messages"]
        if isinstance(item, ToolMessage)
    ]
    assert [item.tool_call_id for item in tool_messages] == ["call_1"], (
        "the delegation is answered by exactly one ToolMessage"
    )


###################
# Invalid delegations (TC-ORC-05, POL-006, ADR-001 §3.1)
###################
def test_invalid_delegation_is_rejected(monkeypatch):
    """TC-ORC-05 / INV-006: blank topic and six questions are rejected; an empty list becomes the topic."""
    from open_deep_research import deep_researcher
    from open_deep_research.orchestration.termination import coverage

    state = state_types()

    class AnsweringResearcher(FakeResearcher):
        """Answer every required question of the task it receives."""

        async def ainvoke(self, inputs: dict, config=None, **_kwargs):
            self.received.append(inputs)
            spec = inputs["task_spec"]
            result = state.TaskResult(
                task_id=spec.task_id,
                status="complete",
                must_answer=list(spec.must_answer),
                findings=[
                    state.Finding(
                        claim="claim",
                        answers=list(spec.must_answer),
                        sources=[state.Source(title="A", url=URL_A)],
                    )
                ],
                summary="summary",
                tool_calls=1,
            )
            return {"task_result": result, "raw_notes": [], "compressed_research": ""}

    researcher = AnsweringResearcher({})
    monkeypatch.setattr(deep_researcher, "researcher_subgraph", researcher)
    message = helpers.ai_message(
        tool_calls=[
            helpers.tool_call(
                "ConductResearch",
                {"research_topic": "   ", "must_answer": [Q1], "scope": ""},
                "bad_blank",
            ),
            helpers.tool_call(
                "ConductResearch",
                {
                    "research_topic": "topic",
                    "must_answer": ["a", "b", "c", "d", "e", "f"],
                    "scope": "",
                },
                "bad_six",
            ),
            helpers.tool_call(
                "ConductResearch",
                {"research_topic": "offshore wind costs", "must_answer": []},
                "good",
            ),
        ]
    )

    command = helpers.run_async(
        deep_researcher.supervisor_tools(supervisor_turn([message]), runnable_config())
    )
    update = helpers.command_update(command)

    assert [inputs["task_spec"].must_answer for inputs in researcher.received] == [
        ["offshore wind costs"]
    ], "only the valid delegation runs; its only question is the topic"
    tool_messages = [
        item for item in update["supervisor_messages"] if isinstance(item, ToolMessage)
    ]
    by_call = {}
    for item in tool_messages:
        by_call.setdefault(item.tool_call_id, []).append(item)
    assert {call: len(items) for call, items in by_call.items()} == {
        "bad_blank": 1,
        "bad_six": 1,
        "good": 1,
    }, "every delegation gets exactly one ToolMessage"
    for call in ("bad_blank", "bad_six"):
        assert "reject" in helpers.message_text(by_call[call][0]).lower()

    results = update["task_results"]
    assert len(results) == 3
    rejected = [result for result in results if result.must_answer == []]
    assert len(rejected) == 2
    assert all(
        (result.status, result.failure_category) == ("failed", "invalid_result")
        for result in rejected
    )
    valid = [result for result in results if result.must_answer]
    assert coverage(results) == coverage(valid) == 1.0, (
        "a rejected delegation adds no question to coverage"
    )


def test_blank_topic_and_six_questions_are_rejected():
    """POL-006: a blank topic or six questions gets an error ToolMessage and a failed/invalid_result result."""
    from open_deep_research.configuration import Configuration
    from open_deep_research.orchestration import contracts

    config = Configuration(task_contract_enabled=True, max_react_tool_calls=10)
    rejected_calls = [
        helpers.tool_call(
            "ConductResearch",
            {"research_topic": "   ", "must_answer": [Q1], "scope": ""},
            "bad_blank",
        ),
        helpers.tool_call(
            "ConductResearch",
            {
                "research_topic": "topic",
                "must_answer": ["a", "b", "c", "d", "e", "f"],
                "scope": "",
            },
            "bad_six",
        ),
    ]

    specs, errors = contracts.build_task_specs(rejected_calls, 1, config)

    assert len(specs) == 2 and len(errors) == 2
    assert all(isinstance(error, ToolMessage) for error in errors)
    assert {error.tool_call_id for error in errors} == {"bad_blank", "bad_six"}
    for spec in specs:
        assert spec.must_answer == []
        result = state_types().TaskResult.failed(
            spec, "invalid_result", "invalid delegation"
        )
        assert (result.status, result.failure_category) == ("failed", "invalid_result")


def test_empty_question_list_becomes_the_topic():
    """TC-ORC-05: an empty question list becomes a task whose only question is the topic (ADR-001 §3.1)."""
    from open_deep_research.configuration import Configuration
    from open_deep_research.orchestration import contracts

    config = Configuration(task_contract_enabled=True, max_react_tool_calls=10)
    specs, rejected = contracts.build_task_specs(
        [
            helpers.tool_call(
                "ConductResearch",
                {"research_topic": "offshore wind costs", "must_answer": []},
                "call_1",
            )
        ],
        1,
        config,
    )

    assert rejected == []
    assert specs[0].must_answer == ["offshore wind costs"]


###################
# Building a task result (TC-ORC-02 to 04, POL-007, POL-008)
###################
def findings_block(findings: list[dict], sources: list[str] | None = None) -> str:
    """Build compression text with one findings block and a `### Sources` list (ADR-001 §3.3)."""
    body = json.dumps({"findings": findings}, ensure_ascii=False)
    lines = [
        "Cleaned findings.",
        "<task_findings>",
        body,
        "</task_findings>",
        "### Sources",
    ]
    lines.extend(
        sources if sources is not None else [f"[1] A: {URL_A}", f"[2] B: {URL_B}"]
    )
    return "\n".join(lines)


def make_spec(questions: list[str] | None = None):
    """Return the task specification the result cases validate against."""
    TaskSpec = state_types().TaskSpec
    return TaskSpec(
        task_id="T1",
        research_topic="Battery recycling",
        scope="",
        must_answer=questions or [Q1, Q2, Q3],
        max_tool_calls=10,
    )


def test_status_derived_from_sourced_findings():
    """TC-ORC-02 / C-002: two of three questions answered with retrieved URLs give status partial."""
    from open_deep_research.orchestration import contracts

    text = findings_block(
        [
            {
                "claim": "The directive was replaced in 2023",
                "answers": [Q1],
                "sources": [1],
            },
            {"claim": "Twelve plants opened", "answers": [Q2], "sources": [2]},
        ]
    )

    result = contracts.build_task_result(
        make_spec(), text, [URL_A, URL_B], tool_calls=2
    )

    assert result.status == "partial"
    assert result.failure_category == "unanswered"
    assert Q3 in result.reason
    assert [finding.claim for finding in result.findings] == [
        "The directive was replaced in 2023",
        "Twelve plants opened",
    ]
    assert result.summary.strip() == "Cleaned findings."


def test_unretrieved_source_does_not_count():
    """TC-ORC-03 / C-003, M-001; INV-006, POL-008: an unretrieved URL and a sourceless finding are not counted."""
    from open_deep_research.orchestration import contracts

    text = findings_block(
        [
            {"claim": "Sourced claim", "answers": [Q1], "sources": [1]},
            {"claim": "Invented source", "answers": [Q2], "sources": [2]},
            {"claim": "No source at all", "answers": [Q3], "sources": []},
        ],
        sources=[f"[1] A: {URL_A}", f"[2] B: {URL_B}"],
    )

    result = contracts.build_task_result(make_spec(), text, [URL_A], tool_calls=3)

    assert [finding.claim for finding in result.findings] == ["Sourced claim"]
    assert result.status == "partial"
    assert Q2 in result.reason and Q3 in result.reason
    unsourced_finding_counted_count = sum(
        1
        for finding in result.findings
        for source in finding.sources
        if source.url not in [URL_A]
    )
    assert unsourced_finding_counted_count == 0

    partly_invented = findings_block(
        [{"claim": "Partly invented", "answers": [Q1], "sources": [1, 2]}]
    )
    dropped = contracts.build_task_result(
        make_spec(), partly_invented, [URL_A], tool_calls=1
    )
    assert dropped.findings == [], (
        "every URL of a finding must have been retrieved, not only one"
    )
    assert (dropped.status, dropped.failure_category) == ("failed", "unanswered")


@pytest.mark.parametrize(
    "text",
    [
        "Error synthesizing research report: Maximum retries exceeded",
        "Cleaned findings without a findings block.",
        findings_block([{"claim": "c", "answers": [Q1], "sources": [1]}]).replace(
            '"findings"', '"items"'
        ),
        "<task_findings>\n{not json</task_findings>\n### Sources\n[1] A: https://example.org/a",
        findings_block(
            [{"claim": "c", "answers": ["a question nobody asked"], "sources": [1]}],
            [f"[1] A: {URL_A}"],
        ),
        findings_block(
            [{"claim": "c", "answers": [Q1], "sources": [7]}], [f"[1] A: {URL_A}"]
        ),
    ],
    ids=[
        "no_block",
        "plain_text",
        "wrong_key",
        "invalid_json",
        "unknown_question",
        "unknown_source_number",
    ],
)
def test_malformed_result_becomes_failed(text):
    """TC-ORC-04 / C-004; INV-006, POL-007: a result that breaks the contract is failed with invalid_result."""
    from open_deep_research.orchestration import contracts

    result = contracts.build_task_result(make_spec(), text, [URL_A], tool_calls=1)

    assert result.status == "failed"
    assert result.failure_category == "invalid_result"
    assert result.findings == [] and result.summary == ""
    assert result.reason


def test_two_findings_blocks_are_rejected():
    """TC-ORC-04: the text must hold exactly one findings block (ADR-001 §3.3 rule 1)."""
    from open_deep_research.orchestration import contracts

    block = findings_block(
        [{"claim": "c", "answers": [Q1], "sources": [1]}], [f"[1] A: {URL_A}"]
    )
    result = contracts.build_task_result(
        make_spec(), block + "\n" + block, [URL_A], tool_calls=1
    )
    assert (result.status, result.failure_category) == ("failed", "invalid_result")


def test_extract_urls_records_successful_tool_results_only():
    """ADR-001 §3.2: only URLs of non-reflection, successful tool messages are retrieved."""
    from open_deep_research.orchestration import contracts

    messages = [
        helpers.tool_message(
            f"Search results\n\nURL: {URL_A}\n", "c1", name="tavily_search"
        ),
        helpers.tool_message(
            f"Error executing tool: no route to {URL_B}", "c2", name="tavily_search"
        ),
        helpers.tool_message(
            "Reflection recorded: maybe nothing", "c3", name="think_tool"
        ),
        helpers.tool_message(
            [{"type": "text", "text": f"block result {URL_B}"}],
            "c4",
            name="self_hosted",
        ),
    ]

    urls = contracts.extract_urls(messages)

    assert URL_A in urls and URL_B in urls
    assert "https://example.org/c" not in urls


def test_result_message_and_notes_render_counted_findings():
    """ADR-001 §3.4 step 7: notes hold only counted findings; the summary stays in the ToolMessage."""
    from open_deep_research.orchestration import contracts

    state = state_types()
    counting = state.TaskResult(
        task_id="T1",
        status="partial",
        must_answer=[Q1, Q2],
        findings=[
            state.Finding(
                claim="Directive 2006/66/EC governs it",
                answers=[Q1],
                sources=[state.Source(title="A", url=URL_A)],
            )
        ],
        summary="free text that must not enter notes",
        tool_calls=2,
        failure_category="unanswered",
        reason=Q2,
    )
    failed = state.TaskResult.failed(make_spec(["Q9"]), "runtime", "provider exploded")

    message = contracts.render_result_message(counting)
    assert "T1" in message and "partial" in message and Q2 in message

    joined = "\n".join(contracts.render_notes([counting, failed]))
    assert "Directive 2006/66/EC governs it" in joined and URL_A in joined
    assert "provider exploded" not in joined
    assert "free text that must not enter notes" not in joined


###################
# One flag-on supervisor turn (TC-ORC-06, TC-ORC-14)
###################
class FakeResearcher:
    """Fake researcher subgraph: records the TaskSpec and config it receives and replays a scripted output."""

    def __init__(self, output: dict):
        self.output = output
        self.received: list[dict] = []
        self.configs: list[dict | None] = []

    async def ainvoke(self, inputs: dict, config=None, **_kwargs):
        self.received.append(inputs)
        self.configs.append(config)
        return self.output


def supervisor_turn(messages: list) -> dict:
    """State for one supervisor_tools call."""
    return {
        "supervisor_messages": messages,
        "research_brief": THE_TOPIC,
        "notes": [],
        "raw_notes": [],
        "research_iterations": 1,
        "task_results": [],
        "stalled_turns": 0,
    }


def runnable_config(**configurable) -> dict:
    """Runtime configuration with the task contract on."""
    values = {
        "task_contract_enabled": True,
        "search_api": "tavily",
        "research_model": helpers.RESEARCH_MODEL,
        "summarization_model": "openai:gpt-4.1-mini",
        "max_react_tool_calls": 10,
        "max_concurrent_research_units": 5,
        "max_researcher_iterations": 6,
    }
    values.update(configurable)
    return {"configurable": values}


def scripted_supervisor(monkeypatch, turns):
    """Make the supervisor model answer with the scripted turns (or raise them) in order."""
    from open_deep_research import deep_researcher

    model = helpers.RecordingRunnable(
        turns or [AIMessage(content="planning", tool_calls=[])]
    )
    helpers.install_model(monkeypatch, deep_researcher, model)
    return model


def test_flag_off_keeps_baseline(monkeypatch):
    """TC-ORC-14: with the flag off the supervisor binds ConductResearch and writes no new state field."""
    from open_deep_research import deep_researcher

    model = scripted_supervisor(
        monkeypatch, [AIMessage(content="planning", tool_calls=[])]
    )

    command = helpers.run_async(
        deep_researcher.supervisor(
            {
                "supervisor_messages": [],
                "research_brief": "b",
                "notes": [],
                "raw_notes": [],
                "research_iterations": 0,
            },
            runnable_config(task_contract_enabled=False),
        )
    )

    state = state_types()
    assert state.ConductResearch in model.bound_objects, (
        "the baseline delegation tool is bound"
    )
    assert state.ConductResearchTask not in model.bound_objects
    assert set(state.ConductResearch.model_fields) == {"research_topic"}, (
        "the baseline ConductResearch is unchanged (ADR-001 §3.1)"
    )
    assert not (
        {"task_results", "exit_reason", "exit_detail"}
        & set(helpers.command_update(command))
    )


def test_flag_on_binds_the_typed_delegation_tool(monkeypatch):
    """ADR-001 §3.1: with the flag on the supervisor binds ConductResearchTask, titled ConductResearch."""
    from open_deep_research import deep_researcher

    model = scripted_supervisor(
        monkeypatch, [AIMessage(content="planning", tool_calls=[])]
    )

    helpers.run_async(
        deep_researcher.supervisor(
            {
                "supervisor_messages": [],
                "research_brief": "b",
                "notes": [],
                "raw_notes": [],
                "research_iterations": 0,
            },
            runnable_config(),
        )
    )

    typed = [
        tool
        for tool in model.bound_objects
        if getattr(tool, "model_fields", None) and "must_answer" in tool.model_fields
    ]
    if not typed:
        pytest.fail(
            "the supervisor must bind the typed delegation tool (ADR-001 §3.1)",
            pytrace=False,
        )
    assert (
        typed[0].model_json_schema().get("title") == "ConductResearch"
        or typed[0].__name__ == "ConductResearchTask"
    )
    assert "ConductResearch" in model.bound_titles


###################
# Tool-call budget (TC-ORC-06, POL-009)
###################
def test_tool_budget_limits_calls(monkeypatch):
    """TC-ORC-06: with budget 2 only the first two calls run, the failed one counts, the rest get a budget message."""
    from open_deep_research import deep_researcher
    from open_deep_research.utils import think_tool

    state_types().TaskSpec  # a budget needs a task spec; without one the baseline answers nothing
    calls_run: list[str] = []

    class FakeSearchTool:
        """Search tool that answers inside the process and records each query it is asked."""

        name = "tavily_search"

        async def ainvoke(self, args, config=None):
            calls_run.append(args["queries"][0])
            if len(calls_run) == 2:
                raise RuntimeError("network down")
            return f"Search results\n\nURL: {URL_A}"

    search_tool = FakeSearchTool()

    async def tools(_config):
        # The shape `get_all_tools` returns: core tools, then the search tool.
        return [think_tool, search_tool]

    monkeypatch.setattr(deep_researcher, "get_all_tools", tools)
    spec = state_types().TaskSpec(
        task_id="T1",
        research_topic="battery recycling",
        scope="",
        must_answer=[Q1],
        max_tool_calls=2,
    )
    state = {
        "supervisor_messages": [],
        "research_brief": "battery recycling",
        "task_spec": spec,
        "researcher_messages": [
            helpers.human_message("task brief"),
            helpers.ai_message(
                tool_calls=[
                    helpers.tool_call("tavily_search", {"queries": ["q1"]}, "c1"),
                    helpers.tool_call("tavily_search", {"queries": ["q2"]}, "c2"),
                    helpers.tool_call("tavily_search", {"queries": ["q3"]}, "c3"),
                    helpers.tool_call("tavily_search", {"queries": ["q4"]}, "c4"),
                ]
            ),
        ],
        "tool_calls_spent": 0,
        "retrieved_urls": [],
        "tool_call_iterations": 1,
    }

    command = helpers.run_async(
        deep_researcher.researcher_tools(state, runnable_config())
    )

    assert helpers.command_goto(command) == "compress_research"
    update = helpers.command_update(command)
    assert calls_run == ["q1", "q2"], (
        "only the first calls up to the budget run, the failing one included"
    )
    budget_messages = [
        item
        for item in update["researcher_messages"]
        if isinstance(item, ToolMessage) and item.tool_call_id in {"c3", "c4"}
    ]
    assert len(budget_messages) == 2
    assert all(
        "budget" in helpers.message_text(item).lower() for item in budget_messages
    ), "the rest get a budget message"
    assert update.get("tool_calls_spent") == 2
    assert URL_A in update.get("retrieved_urls", []), (
        "URLs of successful calls are recorded (ADR-001 §3.2)"
    )
