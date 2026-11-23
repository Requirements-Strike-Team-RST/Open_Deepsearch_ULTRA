"""Shared, offline-only helpers for the research-agent tests (REQ-001 to REQ-010).

These tests make no network call and need no API key
(``verification-constraints.md`` §3). The helpers build the messages, errors and
state the ADRs describe and never import an extension module, so a test module
that imports one observes a missing behaviour and fails for that reason.
"""

import asyncio

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# A model name whose token-limit errors the classifier recognises, used by the
# delivery cases that classify a researcher exception (ADR-002 §3.3).
RESEARCH_MODEL = "openai:gpt-4.1"


def run_async(coro):
    """Run a coroutine to completion on a private event loop."""
    return asyncio.run(coro)


def ai_message(
    content: str = "", tool_calls=None, message_id: str | None = None
) -> AIMessage:
    """Build an ``AIMessage``, optionally with tool calls."""
    kwargs = {"content": content}
    if tool_calls:
        kwargs["tool_calls"] = tool_calls
    if message_id is not None:
        kwargs["id"] = message_id
    return AIMessage(**kwargs)


def tool_call(name: str, args: dict, call_id: str) -> dict:
    """Build one tool call in the shape a LangChain message carries it."""
    return {"name": name, "args": args, "id": call_id}


def tool_message(content, call_id: str, name: str | None = None) -> ToolMessage:
    """Build a ``ToolMessage``."""
    return ToolMessage(content=content, tool_call_id=call_id, name=name)


def human_message(content: str) -> HumanMessage:
    """Build a ``HumanMessage``."""
    return HumanMessage(content=content)


def message_text(message) -> str:
    """Return a message's text, joining the text parts of block content (ADR-001 §3.2)."""
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)


class RecordingRunnable:
    """Wrap a model so a node can bind tools, retry and configure it without a client.

    The baseline builds its shared model once at import time with
    ``configurable_fields``; binding tools or configuring it then materialises a
    real client. A fake therefore has to be installed both as the shared model and
    as the ``init_chat_model`` factory, and it has to survive the fluent calls the
    nodes chain between them. Every call returns this same object (or, for
    ``ainvoke``, the scripted turn).
    """

    def __init__(self, turns=None):
        self.turns = list(turns or [])
        self.bound_titles: list[str] = []
        self.bound_objects: list[object] = []
        self.invocations: list[list] = []

    def _bind(self, tools):
        self.bound_objects = list(tools)
        self.bound_titles = [_tool_title(tool) for tool in tools]
        return self

    def bind_tools(self, tools, **_kwargs):
        return self._bind(tools)

    def with_retry(self, **_kwargs):
        return self

    def with_config(self, _config=None, **_kwargs):
        return self

    def with_structured_output(self, schema=None, **_kwargs):
        if schema is None:
            return self
        # A structured call returns an instance of the schema; without a scripted
        # answer the test cannot expect a particular one.
        self.structured_schema = schema
        return self

    def invoke(self, messages, **_kwargs):
        return self._next(messages)

    async def ainvoke(self, messages, **_kwargs):
        return self._next(messages)

    def _next(self, messages):
        self.invocations.append(messages)
        if not self.turns:
            raise AssertionError(
                "the node made more model calls than the test scripted"
            )
        turn = self.turns.pop(0)
        if isinstance(turn, Exception):
            raise turn
        return turn


def _tool_title(tool) -> str:
    """Return the name a bound tool advertises to the model."""
    if hasattr(tool, "model_json_schema"):
        try:
            schema = tool.model_json_schema()
        except Exception:  # a callable model with injected arguments
            return getattr(tool, "__name__", str(tool))
        return schema.get("title") or getattr(tool, "__name__", str(tool))
    return getattr(tool, "name", str(tool))


def install_model(monkeypatch, module, model) -> None:
    """Make every model a module creates or holds resolve to ``model``.

    ``init_chat_model`` is patched for a module that imports it at call time and
    ``configurable_model`` for one that holds the shared model from import time.
    """
    if hasattr(module, "init_chat_model"):
        monkeypatch.setattr(module, "init_chat_model", lambda *_a, **_k: model)
    if hasattr(module, "configurable_model"):
        monkeypatch.setattr(module, "configurable_model", model)


def command_update(command) -> dict:
    """Return the state update a node returned with its ``Command``."""
    update = getattr(command, "update", None) or {}
    return update if isinstance(update, dict) else {}


def command_goto(command):
    """Return the destination of the ``Command`` a node returned."""
    return getattr(command, "goto", None)


def override_value(value):
    """Return the list an update writes, unwrapping an ``override_reducer`` override.

    ``state.override_reducer`` replaces a field with ``{"type": "override",
    "value": [...]}`` and appends a plain list; a node update holds either shape
    (``memory-design.md`` §5), so the cases read both through this helper.
    """
    if isinstance(value, dict) and value.get("type") == "override":
        return value.get("value")
    return value


def provider_error(message: str, provider: str = "openai") -> Exception:
    """Build a provider-shaped error the baseline token-limit classifier reads.

    ``utils.is_token_limit_exceeded`` inspects the exception's class name, its
    module name, ``code``, ``type`` and message, so no third-party client class
    is needed. ``provider`` selects the OpenAI or the Anthropic shape.
    """
    base = type("BadRequestError", (Exception,), {})
    base.__module__ = ("anthropic" if provider == "anthropic" else "openai") + ".errors"
    error = base(message)
    error.code = (
        "prompt_too_long" if provider == "anthropic" else "context_length_exceeded"
    )
    error.type = "invalid_request_error"
    return error


def token_limit_error(provider: str = "openai") -> Exception:
    """Return an error that ``utils.is_token_limit_exceeded`` recognises."""
    if provider == "anthropic":
        return provider_error(
            "prompt is too long: 250000 tokens > 200000 maximum", "anthropic"
        )
    return provider_error(
        "This model's maximum context length is 128000 tokens", "openai"
    )


async def run_graph(compiled_graph, inputs: dict, config: dict) -> dict:
    """Run a compiled graph and return its final state.

    ``stream_mode="values"`` keeps the last complete state, including the fields
    a node wrote before routing with a ``Command``.
    """
    final_state: dict = {}
    async for chunk in compiled_graph.astream(inputs, config, stream_mode="values"):
        final_state = chunk
    return final_state


async def drain(compiled_graph, inputs: dict, config: dict) -> list[dict]:
    """Return every state snapshot a graph run emitted, in order."""
    return [
        chunk
        async for chunk in compiled_graph.astream(inputs, config, stream_mode="values")
    ]
