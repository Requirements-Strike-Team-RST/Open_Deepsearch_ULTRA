"""Split a research history into whole turns and remove the oldest one.

REQ-005, ADR-004 §3, INV-001. A turn is one ``AIMessage`` plus the
``ToolMessage``s whose ``tool_call_id`` is in that message's ``tool_calls``;
pairing is by id, not by position. The preamble (messages before the first
``AIMessage``), the compression instruction (the last message) and the newest
turn are never removed, and a tool result whose id matches no ``AIMessage`` is
kept as it is. No function here calls a model.
"""

from collections.abc import Sequence

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage


def _requested_ids(message: AIMessage) -> set[str]:
    """Return the ids of the tool calls an AI message made."""
    return {str(call.get("id")) for call in message.tool_calls or [] if call.get("id")}


def _index_turns(
    body: Sequence[BaseMessage], first_ai: int
) -> list[tuple[int, list[int]]]:
    """Return ``(AI index, paired tool-result indices)`` for each turn of ``body``.

    A tool result belongs to the nearest earlier ``AIMessage`` that requested
    its id; a result that no earlier ``AIMessage`` requested belongs to no turn.
    """
    turns: list[tuple[int, list[int]]] = []
    for index in range(first_ai, len(body)):
        message = body[index]
        if isinstance(message, AIMessage):
            turns.append((index, []))
            continue
        if not isinstance(message, ToolMessage):
            continue
        call_id = str(message.tool_call_id)
        for ai_index, paired in reversed(turns):
            if call_id in _requested_ids(body[ai_index]):
                paired.append(index)
                break
    return turns


def _split(
    messages: Sequence[BaseMessage],
) -> tuple[list[BaseMessage], list[tuple[int, list[int]]], int | None]:
    """Return the message list, its turns as indices and the index of the first AI message."""
    items = list(messages or [])
    if not items:
        raise ValueError(
            "a compression history ends with its instruction, so it is never empty"
        )
    body = items[:-1]
    first_ai = next(
        (index for index, message in enumerate(body) if isinstance(message, AIMessage)),
        None,
    )
    turns = [] if first_ai is None else _index_turns(body, first_ai)
    return items, turns, first_ai


def split_turns(
    messages: Sequence[BaseMessage],
) -> tuple[list[BaseMessage], list[list[BaseMessage]], BaseMessage]:
    """Return ``(preamble, turns, instruction)`` for a research history (REQ-005, ADR-004 §5).

    Each turn lists its ``AIMessage`` and then the tool results paired with it
    by id, in their original order. A message that belongs to no turn (for
    example a tool result whose id matches no ``AIMessage``) is not part of
    any turn, so trimming never removes it.
    """
    items, turns, first_ai = _split(messages)
    preamble = items[: len(items) - 1] if first_ai is None else items[:first_ai]
    return (
        preamble,
        [[items[ai_index], *(items[i] for i in paired)] for ai_index, paired in turns],
        items[-1],
    )


def trim_oldest_turn(messages: Sequence[BaseMessage]) -> list[BaseMessage] | None:
    """Remove the oldest whole turn and keep the original order (REQ-005, ADR-004 §3, INV-001).

    Returns ``None`` when at most one turn is left, because the newest turn is
    never removed. Only the oldest ``AIMessage`` and the tool results paired
    with it go; the preamble, the instruction, later turns and unmatched tool
    results stay where they are.
    """
    items, turns, _first_ai = _split(messages)
    if len(turns) <= 1:
        return None
    ai_index, paired = turns[0]
    removed = {ai_index, *paired}
    return [message for index, message in enumerate(items) if index not in removed]
