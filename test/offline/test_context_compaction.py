"""REQ-005: token-limit recovery in compression removes the oldest whole turns.

Covers TC-CTX-01 to TC-CTX-06 (``verification-constraints.md`` §7, context) and
INV-001. The interface is ``context/trimming.py`` (`split_turns`,
`trim_oldest_turn`) and ``context/recovery.py`` (`compress_with_recovery`,
`CompressionFailed`), ADR-004 §5. Every model is fake.
"""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from test.offline import helpers
from test.offline.helpers import install_model

TOPIC = "Battery recycling in the EU"
INSTRUCTION = "All above messages are about research. Please clean up these findings."
URLS = [f"https://example.org/{index}" for index in range(1, 4)]


def build_history(turns: int = 3) -> list:
    """Topic, `turns` AI turns (ids a1..) with their tool results, then the compression instruction."""
    messages = [SystemMessage(content=TOPIC)]
    for index in range(1, turns + 1):
        call = helpers.tool_call(
            "tavily_search", {"queries": [f"q{index}"]}, f"call_{index}"
        )
        messages.append(
            helpers.ai_message("", tool_calls=[call], message_id=f"a{index}")
        )
        messages.append(
            ToolMessage(
                content=f"Search results\n\nURL: {URLS[index - 1]}",
                tool_call_id=f"call_{index}",
                name="tavily_search",
            )
        )
    messages.append(HumanMessage(content=INSTRUCTION))
    return messages


def ai_ids(messages) -> list[str]:
    """Return the ids of the AI messages in a list."""
    return [message.id for message in messages if isinstance(message, AIMessage)]


def tool_ids(messages) -> set[str]:
    """Return the tool-call ids answered by a tool message in a list."""
    return {
        message.tool_call_id for message in messages if isinstance(message, ToolMessage)
    }


###################
# Trimming (TC-CTX-01, TC-CTX-02)
###################
def test_split_turns_separates_preamble_turns_and_instruction():
    """ADR-004 §3: the preamble precedes the first AI message; the instruction is the last message."""
    from open_deep_research.context.trimming import split_turns

    preamble, turns, instruction = split_turns(build_history())

    assert preamble == [SystemMessage(content=TOPIC)]
    assert len(turns) == 3
    assert all(isinstance(turn[0], AIMessage) for turn in turns)
    assert instruction.content == INSTRUCTION


def test_trim_oldest_turn_removes_a_whole_turn():
    """ADR-004 §3: the oldest AI turn goes with its tool results; the rest keeps the original order."""
    from open_deep_research.context.trimming import trim_oldest_turn

    trimmed = trim_oldest_turn(build_history())

    assert trimmed is not None
    assert ai_ids(trimmed) == ["a2", "a3"]
    assert "call_1" not in tool_ids(trimmed), (
        "the tool result of the removed turn is gone with it"
    )
    assert {"call_2", "call_3"} <= tool_ids(trimmed)
    assert trimmed[0] == SystemMessage(content=TOPIC)
    assert trimmed[-1].content == INSTRUCTION


def test_newest_turn_is_never_removed():
    """ADR-004 §3: once only the newest turn is left, there is nothing to trim."""
    from open_deep_research.context.trimming import trim_oldest_turn

    once = trim_oldest_turn(build_history())
    twice = trim_oldest_turn(once)

    assert ai_ids(twice) == ["a3"]
    assert "call_3" in tool_ids(twice)
    assert trim_oldest_turn(twice) is None


def test_unmatched_tool_result_is_kept():
    """ADR-004 §3: a tool result whose id matches no AI message is kept as it is."""
    from open_deep_research.context.trimming import trim_oldest_turn

    messages = build_history(turns=2)
    messages.insert(
        2,
        ToolMessage(content="orphan result", tool_call_id="ghost", name="self_hosted"),
    )

    trimmed = trim_oldest_turn(messages)

    assert ai_ids(trimmed) == ["a2"]
    assert "ghost" in tool_ids(trimmed)


def test_no_orphan_tool_messages():
    """TC-CTX-02 / C-002, M-002; INV-001: every kept tool result follows an AI message present in the list."""
    from open_deep_research.context.trimming import trim_oldest_turn

    # A turn with two tool calls of which one result is missing.
    missing_result = build_history(turns=2)
    missing_result[1].tool_calls.append(
        helpers.tool_call("tavily_search", {"queries": ["q2b"]}, "call_2b")
    )
    # Pairing is by id, not position (ADR-004 §3): the first turn's result
    # arrives after the second AI message.
    preamble, a1, tool_1, a2, tool_2, instruction = build_history(turns=2)
    out_of_order = [preamble, a1, a2, tool_2, tool_1, instruction]
    # A tool message whose id matches no AI message is kept as it is.
    unmatched = build_history(turns=2)
    unmatched.insert(
        2,
        ToolMessage(content="orphan result", tool_call_id="ghost", name="self_hosted"),
    )

    parents = {
        call["id"]: message.id
        for message in build_history()
        if isinstance(message, AIMessage)
        for call in message.tool_calls
    }
    histories = [build_history(turns=turns) for turns in range(0, 4)] + [
        missing_result,
        out_of_order,
        unmatched,
    ]

    orphan_tool_message_count = 0
    for messages in histories:
        trimmed = trim_oldest_turn(messages)
        for kept in (messages, trimmed):
            if kept is None:
                continue
            kept_ai_ids = set(ai_ids(kept))
            for message in kept:
                if isinstance(message, ToolMessage) and message.tool_call_id in parents:
                    if parents[message.tool_call_id] not in kept_ai_ids:
                        orphan_tool_message_count += 1
        if trimmed is not None:
            # Exactly the oldest turn goes; the newest turn always stays.
            assert set(ai_ids(messages)) - set(ai_ids(trimmed)) == {ai_ids(messages)[0]}
            assert ai_ids(trimmed)[-1] == ai_ids(messages)[-1]
            assert trimmed[0] == messages[0] and trimmed[-1] == messages[-1]
    assert orphan_tool_message_count == 0

    trimmed = trim_oldest_turn(out_of_order)
    assert trimmed == [preamble, a2, tool_2, instruction], (
        "the late result of the removed turn goes with it, the rest keeps its order"
    )
    assert "ghost" in tool_ids(trim_oldest_turn(unmatched))


###################
# The recovery loop (TC-CTX-01, 03, 05)
###################
class FakeCompressionModel(helpers.RecordingRunnable):
    """Fake compression model: raises a token-limit error while the request is too large."""

    def __init__(self, reject_until_turns: int, provider: str = "openai"):
        super().__init__()
        self.reject_until_turns = reject_until_turns
        self.provider = provider
        self.requests: list[list] = []

    def _next(self, messages):
        self.requests.append(list(messages))
        if (
            sum(1 for message in messages if isinstance(message, AIMessage))
            > self.reject_until_turns
        ):
            raise helpers.token_limit_error(self.provider)
        return AIMessage(content="compressed summary")


def compression_config(**values) -> dict:
    """Runtime configuration for the compression node cases."""
    base = {
        "task_contract_enabled": True,
        "context_trimming": True,
        "search_api": "tavily",
        "compression_model": "openai:gpt-4.1",
        "research_model": helpers.RESEARCH_MODEL,
        "summarization_model": "openai:gpt-4.1-mini",
    }
    base.update(values)
    return {"configurable": base}


def compress(model, messages, model_name="openai:gpt-4.1"):
    """Call `compress_with_recovery` with the interface of ADR-004 §5."""
    from open_deep_research.context.recovery import compress_with_recovery

    return helpers.run_async(
        compress_with_recovery(model, "system prompt", messages, model_name)
    )


def test_oldest_turns_removed_first():
    """TC-CTX-01 / C-001, M-001; INV-001: two rejections remove the two oldest turns and keep the newest context."""
    model = FakeCompressionModel(reject_until_turns=1)
    history = build_history()

    summary = compress(model, history)

    assert summary == "compressed summary"
    last = model.requests[-1]
    assert last[0] == SystemMessage(content="system prompt"), (
        "every attempt sends the caller's system prompt first"
    )
    topic, _a1, _t1, _a2, _t2, a3, tool_3, instruction = history
    assert last[1:] == [topic, a3, tool_3, instruction], (
        "topic, newest turn with its result and instruction are kept, in order"
    )
    assert ai_ids(last) == ["a3"], "only the newest turn survives"
    assert "URL: https://example.org/3" in helpers.message_text(
        next(message for message in last if isinstance(message, ToolMessage))
    )
    latest_turn_preservation_rate = 1.0 if ai_ids(last) == ["a3"] else 0.0
    assert latest_turn_preservation_rate == 1.0


def test_classification_uses_compression_model(monkeypatch):
    """TC-CTX-03 / C-003: an Anthropic token-limit error from the compression model is recognised."""
    model = FakeCompressionModel(reject_until_turns=2, provider="anthropic")

    summary = compress(model, build_history(), model_name="anthropic:claude-sonnet-4")

    assert summary == "compressed summary"
    assert ai_ids(model.requests[0]) == ["a1", "a2", "a3"]
    assert ai_ids(model.requests[1]) == ["a2", "a3"], (
        "a turn was removed before the retry"
    )

    # Through the node: research_model is OpenAI, compression_model is Anthropic,
    # and the error is classified with the model that made the call.
    from open_deep_research import deep_researcher

    node_model = FakeCompressionModel(reject_until_turns=2, provider="anthropic")
    install_model(monkeypatch, deep_researcher, node_model)
    state = {
        "researcher_messages": build_history()[:-1],
        "research_topic": TOPIC,
        "tool_call_iterations": 3,
    }

    update = helpers.run_async(
        deep_researcher.compress_research(
            state,
            compression_config(
                task_contract_enabled=False,
                research_model="openai:gpt-4.1",
                compression_model="anthropic:claude-sonnet-4",
            ),
        )
    )

    assert update["compressed_research"] == "compressed summary"
    assert ai_ids(node_model.requests[0]) == ["a1", "a2", "a3"]
    assert ai_ids(node_model.requests[1]) == ["a2", "a3"], (
        "the node recognised the Anthropic error and removed a turn before the retry"
    )


def test_unreducible_history_ends_failed(monkeypatch):
    """TC-CTX-04 / C-004; INV-001: a history that cannot shrink fails with token_limit, never with summary text."""
    from open_deep_research.context.recovery import CompressionFailed

    with pytest.raises(CompressionFailed) as failure:
        compress(FakeCompressionModel(reject_until_turns=0), build_history(turns=1))
    assert failure.value.category == "token_limit"
    assert failure.value.removed_turns == 0

    # The node maps the failure to a failed TaskResult with no summary.
    from open_deep_research import deep_researcher

    install_model(
        monkeypatch, deep_researcher, FakeCompressionModel(reject_until_turns=0)
    )
    import open_deep_research.state as state_module

    task_spec = state_module.TaskSpec(
        task_id="T1",
        research_topic=TOPIC,
        scope="",
        must_answer=["q"],
        max_tool_calls=5,
    )
    state = {
        "researcher_messages": build_history(turns=1),
        "supervisor_messages": [],
        "research_brief": TOPIC,
        "research_topic": TOPIC,
        "task_spec": task_spec,
        "tool_calls_spent": 1,
        "retrieved_urls": [],
        "tool_call_iterations": 1,
    }

    update = helpers.run_async(
        deep_researcher.compress_research(state, compression_config())
    )

    assert update["task_result"].status == "failed"
    assert update["task_result"].failure_category == "token_limit"
    assert update["compressed_research"] == ""
    assert "Maximum retries exceeded" not in update["compressed_research"]


def test_non_token_errors_are_retried():
    """TC-CTX-05 / POL-014: other errors retry the same request, at most 3 attempts, then CompressionFailed(runtime)."""
    from open_deep_research.context.recovery import CompressionFailed

    class RateLimited(helpers.RecordingRunnable):
        def __init__(self, failures: int):
            super().__init__()
            self.failures = failures
            self.calls = 0

        def _next(self, _messages):
            self.calls += 1
            if self.calls <= self.failures:
                raise RuntimeError("429 rate limit")
            return AIMessage(content="summary after retry")

    one_turn = build_history(turns=1)

    flaky = RateLimited(failures=2)
    assert compress(flaky, one_turn) == "summary after retry"
    assert flaky.calls == 3

    always = RateLimited(failures=99)
    with pytest.raises(CompressionFailed) as failure:
        compress(always, one_turn)
    assert failure.value.category == "runtime"
    assert always.calls == 3


def test_flag_off_keeps_baseline(monkeypatch):
    """TC-CTX-06: with context_trimming off the baseline loop and its placeholder are used."""
    from open_deep_research import deep_researcher

    class AlwaysFails(helpers.RecordingRunnable):
        def __init__(self):
            super().__init__()

        def _next(self, _messages):
            raise RuntimeError("provider down")

    install_model(monkeypatch, deep_researcher, AlwaysFails())
    state = {
        "researcher_messages": build_history(turns=1),
        "supervisor_messages": [],
        "research_brief": TOPIC,
        "research_topic": TOPIC,
        "tool_call_iterations": 1,
    }

    update = helpers.run_async(
        deep_researcher.compress_research(
            state, compression_config(context_trimming=False)
        )
    )

    assert (
        update["compressed_research"]
        == "Error synthesizing research report: Maximum retries exceeded"
    )
    assert update.get("task_result") is None
