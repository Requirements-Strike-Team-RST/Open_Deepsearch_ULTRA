"""Retry a compression call, freeing context from the oldest end on a token-limit error.

REQ-005, ADR-004 §3, INV-001, POL-012 to POL-014. Token-limit errors are
recognised for the model that made the call (``model_name`` is the caller's
``compression_model``), whole turns are removed from the oldest end, and a
history that cannot be reduced raises ``CompressionFailed`` instead of returning
placeholder text. Other errors retry the same request at most three times; the
two counters are separate.
"""

from collections.abc import Sequence

from langchain_core.messages import BaseMessage, SystemMessage

from open_deep_research.context.trimming import trim_oldest_turn
from open_deep_research.utils import is_token_limit_exceeded


class CompressionFailed(Exception):
    """A compression call that could not produce a summary (ADR-004 §5).

    ``category`` is ``token_limit`` when the history could not be made small
    enough and ``runtime`` when another error persisted; ``removed_turns`` is
    the number of turns the recovery removed before giving up.
    """

    def __init__(self, category: str, reason: str, removed_turns: int = 0):
        """Record the failure category, its reason and the turns already removed."""
        super().__init__(reason)
        self.category = category
        self.reason = reason
        self.removed_turns = removed_turns


async def compress_with_recovery(
    model,
    system_prompt: str,
    messages: Sequence[BaseMessage],
    model_name: str,
    max_transient_attempts: int = 3,
) -> str:
    """Compress ``messages`` with ``model`` and return the response text (REQ-005, ADR-004 §3).

    Every attempt sends ``system_prompt`` as the system message, followed by
    the history (preamble, turns, compression instruction). On a token-limit
    error recognised for ``model_name`` the oldest whole turn is removed and the
    call is retried; when nothing removable is left the function raises
    ``CompressionFailed(token_limit)``. Any other error retries the same
    request, at most ``max_transient_attempts`` times in total, and then raises
    ``CompressionFailed(runtime)``. The caller's list is never changed.
    """
    history: list[BaseMessage] = list(messages)
    removed = 0
    transient_attempts = 0

    while True:
        try:
            response = await model.ainvoke(_request(system_prompt, history))
            return _response_text(response)
        except Exception as exc:  # noqa: BLE001 - classified below
            if is_token_limit_exceeded(exc, model_name):
                trimmed = trim_oldest_turn(history)
                if trimmed is None:
                    raise CompressionFailed(
                        "token_limit",
                        f"the history still exceeds the token limit of {model_name} "
                        "and no turn can be removed",
                        removed_turns=removed,
                    ) from exc
                history = trimmed
                removed += 1
                continue
            transient_attempts += 1
            if transient_attempts >= max_transient_attempts:
                raise CompressionFailed(
                    "runtime",
                    f"compression failed after {transient_attempts} attempts: {exc}",
                    removed_turns=removed,
                ) from exc


def _request(system_prompt: str, history: Sequence[BaseMessage]) -> list[BaseMessage]:
    """Return the messages of one attempt: the system prompt, then the (trimmed) history."""
    if not system_prompt:
        return list(history)
    return [SystemMessage(content=system_prompt), *history]


def _response_text(response) -> str:
    """Return a chat model response as text."""
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    return "\n".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in content or []
    )
