"""REQ-008: a failed search falls back to the configured alternative sources in order.

Covers TC-SRC-11 to TC-SRC-17 (``verification-constraints.md`` §7, search) and
INV-010. The interface is ``search/fallback.py`` (`apply_search_fallback`,
`classify_search_error`, `AllSourcesFailedError`, ADR-008 §5), used from
`researcher_tools`. Tavily and MCP tools are fake; no network is used.
"""

import asyncio

import httpx
import pytest
from langchain_core.tools import ToolException
from pydantic import create_model

from open_deep_research.configuration import Configuration
from test.offline import helpers

EMPTY_RESULT_TEXT = "No valid search results found. Please try different search queries or use a different search API."


def http_status_error(status: int) -> httpx.HTTPStatusError:
    """Build an `httpx.HTTPStatusError` with a given status code."""
    request = httpx.Request("GET", "https://api.example.org/search")
    response = httpx.Response(status, request=request)
    return httpx.HTTPStatusError(f"HTTP {status}", request=request, response=response)


def tavily_errors():
    """Return the typed Tavily errors the classifier knows (ADR-008 §3.4)."""
    from tavily import errors

    return errors


def mcp_error(code: int) -> Exception:
    """Build the MCP client's `McpError` with an error code."""
    from mcp import McpError
    from mcp.types import ErrorData

    return McpError(ErrorData(code=code, message=f"code {code}"))


class FakeSearchTool:
    """Fake tool with a name, a description, one required string argument and scripted behaviour."""

    def __init__(self, name: str, behaviour, description: str | None = None):
        self.name = name
        self.description = description or f"The {name} tool."
        self._behaviour = behaviour
        self.calls: list[dict] = []
        self.args_schema = create_model(
            f"{name.title().replace('_', '')}Arguments", query=(str, ...)
        )

    async def ainvoke(self, args, config=None, **_kwargs):
        self.calls.append(dict(args))
        # The scripted behaviours are plain functions that return or raise.
        return self._behaviour(**args)


class FakeTavilyTool(FakeSearchTool):
    """Fake Tavily tool with the baseline argument shape (`queries: list[str]`, plus defaults)."""

    def __init__(self, behaviour):
        super().__init__(
            "tavily_search",
            behaviour,
            "A search engine optimized for comprehensive, accurate results.",
        )
        self.args_schema = create_model("TavilyArguments", queries=(list[str], ...))


def configuration(fallback: list[str]) -> Configuration:
    """Configuration with an ordered fallback list."""
    return Configuration(search_api="tavily", search_fallback=fallback)


def apply(tools, configurable) -> list:
    """Call `apply_search_fallback`."""
    from open_deep_research.search.fallback import apply_search_fallback

    return apply_search_fallback(tools, configurable)


def invoke(tool, args):
    """Invoke a (possibly wrapped) tool offline."""
    return helpers.run_async(tool.ainvoke(args))


def mcp_tool() -> FakeSearchTool:
    """Return the fake MCP search tool."""
    return FakeSearchTool(
        "self_hosted_search", lambda query: f"self-hosted result for {query}"
    )


###################
# Fallback behaviour (TC-SRC-11 to 15)
###################
def test_primary_failure_uses_fallback(monkeypatch):
    """TC-SRC-11 / C-001; INV-010: a timing-out Tavily call falls back to the configured MCP source."""
    errors = tavily_errors()
    primary = FakeTavilyTool(lambda **_kwargs: _raise(errors.TimeoutError("timed out")))
    fallback = mcp_tool()
    tools = apply([primary, fallback], configuration(["self_hosted_search"]))

    result = invoke(tools[0], {"queries": ["battery recycling"]})

    assert result == "self-hosted result for battery recycling", (
        "the fallback's result is returned unchanged"
    )
    assert len(primary.calls) == 1, "the primary is tried once"
    assert fallback.calls == [{"query": "battery recycling"}]


def _raise(error: BaseException):
    """Raise an exception from inside a fake tool."""
    raise error


def test_fallbacks_follow_configured_order():
    """TC-SRC-12 / C-002: the first two sources fail with eligible errors and the third answers."""
    errors = tavily_errors()
    primary = FakeTavilyTool(lambda **_kwargs: _raise(errors.TimeoutError("timed out")))
    second = FakeSearchTool(
        "self_hosted_search", lambda **_kwargs: _raise(http_status_error(503))
    )
    third = FakeSearchTool(
        "archive_search", lambda query: f"archive result for {query}"
    )
    tools = apply(
        [primary, second, third],
        configuration(["self_hosted_search", "archive_search"]),
    )

    result = invoke(tools[0], {"queries": ["battery recycling"]})

    assert result == "archive result for battery recycling"
    assert len(primary.calls) == 1 and len(second.calls) == 1 and len(third.calls) == 1


def test_all_sources_fail_explicitly(monkeypatch):
    """TC-SRC-13 / C-003; INV-010: every failure is listed and the text cannot be mistaken for an empty result."""
    from open_deep_research.search.fallback import AllSourcesFailedError

    errors = tavily_errors()
    primary = FakeTavilyTool(lambda **_kwargs: _raise(errors.TimeoutError("timed out")))
    tools = apply([primary], configuration(["self_hosted_search"]))

    with pytest.raises(AllSourcesFailedError) as failure:
        invoke(tools[0], {"queries": ["battery recycling"]})

    message = str(failure.value)
    assert message.startswith("All search sources failed:")
    assert "tavily_search" in message and "timeout" in message
    assert "self_hosted_search" in message and "not available" in message
    assert EMPTY_RESULT_TEXT not in message
    attempts = failure.value.attempts
    assert [attempt[0] for attempt in attempts] == [
        "tavily_search",
        "self_hosted_search",
    ]
    assert all(len(attempt) == 3 for attempt in attempts), (
        "each attempt is (source, category, error text)"
    )

    # TC-SRC-13 also lists a fallback Tavily without a key: its ineligible error
    # is recorded with the others instead of hiding them (ADR-008 §3.4).
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("GET_API_KEYS_FROM_CONFIG", raising=False)
    primary_mcp = FakeSearchTool(
        "self_hosted_search", lambda **_kwargs: _raise(httpx.ConnectError("refused"))
    )
    tools = apply(
        [primary_mcp],
        configuration(["self_hosted_search", "archive_search", "tavily"]),
    )

    with pytest.raises(AllSourcesFailedError) as failure:
        invoke(tools[0], {"query": "battery recycling"})

    message = str(failure.value)
    assert message.startswith("All search sources failed:")
    assert EMPTY_RESULT_TEXT not in message
    assert [
        (source, category) for source, category, _error in failure.value.attempts
    ] == [
        ("self_hosted_search", "connection"),
        ("archive_search", "not available"),
        ("tavily_search", "missing_credential"),
    ]


def test_listed_mcp_tool_with_wrong_shape_is_not_available():
    """ADR-008 §3.3: a loaded MCP tool without exactly one required string argument is `not available`."""
    from open_deep_research.search.fallback import AllSourcesFailedError

    errors = tavily_errors()
    primary = FakeTavilyTool(lambda **_kwargs: _raise(errors.TimeoutError("timed out")))
    wrong_shape = FakeSearchTool("self_hosted_search", lambda query: "never called")
    wrong_shape.args_schema = create_model(
        "TwoArguments", query=(str, ...), limit=(int, ...)
    )

    tools = apply([primary, wrong_shape], configuration(["self_hosted_search"]))

    with pytest.raises(AllSourcesFailedError) as failure:
        invoke(tools[0], {"queries": ["q"]})
    assert "self_hosted_search" in str(failure.value) and "not available" in str(
        failure.value
    )
    assert wrong_shape.calls == []


def test_ineligible_error_of_the_called_tool_is_reraisable():
    """ADR-008 §3.4: an ineligible error of a later source is recorded, one of the called tool is re-raised.

    A tool is wrapped only when at least one *other* source is listed
    (ADR-008 §3.2), so every case here lists two sources.
    """
    from open_deep_research.search.fallback import AllSourcesFailedError

    errors = tavily_errors()

    # A later source's ineligible error is recorded and does not hide the first attempt.
    primary = FakeTavilyTool(lambda **_kwargs: _raise(errors.TimeoutError("timed out")))
    later = FakeSearchTool(
        "self_hosted_search", lambda **_kwargs: _raise(ValueError("plain failure"))
    )
    tools = apply([primary, later], configuration(["self_hosted_search"]))

    with pytest.raises(AllSourcesFailedError) as failure:
        invoke(tools[0], {"queries": ["q"]})
    assert [
        (source, category) for source, category, _error in failure.value.attempts
    ] == [
        ("tavily_search", "timeout"),
        ("self_hosted_search", "other"),
    ]

    # The called tool's own ineligible error is re-raised unchanged; nothing else runs.
    called = FakeSearchTool(
        "self_hosted_search", lambda **_kwargs: _raise(ToolException("tool failed"))
    )
    tavily_fallback = FakeTavilyTool(lambda **_kwargs: "never used")
    tools = apply(
        [tavily_fallback, called], configuration(["self_hosted_search", "tavily"])
    )
    wrapped_called = next(tool for tool in tools if tool.name == "self_hosted_search")

    with pytest.raises(ToolException):
        invoke(wrapped_called, {"query": "q"})
    assert tavily_fallback.calls == []

    from open_deep_research.search.fallback import classify_search_error

    # tavily-python's MissingAPIKeyError takes no argument.
    assert classify_search_error(errors.MissingAPIKeyError()) == (
        False,
        "missing_credential",
    )


def test_empty_result_does_not_trigger_fallback():
    """TC-SRC-14 / C-004: a source that returns no hits is a success; no fallback is tried."""
    primary = FakeTavilyTool(lambda **_kwargs: EMPTY_RESULT_TEXT)
    fallback = mcp_tool()
    tools = apply([primary, fallback], configuration(["self_hosted_search"]))

    assert invoke(tools[0], {"queries": ["rare query"]}) == EMPTY_RESULT_TEXT
    assert fallback.calls == []


def test_ineligible_error_does_not_trigger_fallback():
    """TC-SRC-15 / C-005: a malformed query raises the original error; no fallback is tried."""
    errors = tavily_errors()
    primary = FakeTavilyTool(
        lambda **_kwargs: _raise(errors.BadRequestError("malformed query"))
    )
    fallback = mcp_tool()
    tools = apply([primary, fallback], configuration(["self_hosted_search"]))

    with pytest.raises(errors.BadRequestError):
        invoke(tools[0], {"queries": ["??"]})
    assert fallback.calls == []


def test_mcp_primary_falls_back_to_tavily():
    """ADR-008 §3.2, §3.3: a listed MCP tool falls back to Tavily, which receives one call with the query list.

    Only an MCP tool named in ``search_fallback`` is wrapped (ADR-008 §3.2), so
    the MCP primary is listed before ``tavily``.
    """
    from open_deep_research import utils

    tavily_calls: list[dict] = []

    async def fake_tavily(queries, max_results=5, topic="general", config=None):
        tavily_calls.append(
            {"queries": queries, "max_results": max_results, "topic": topic}
        )
        return f"search results for {queries}"

    tavily_tool = utils.tavily_search
    original = tavily_tool.coroutine
    tavily_tool.coroutine = fake_tavily
    try:
        primary = FakeSearchTool(
            "self_hosted_search", lambda **_kwargs: _raise(http_status_error(429))
        )
        tools = apply([primary], configuration(["self_hosted_search", "tavily"]))
        result = invoke(tools[0], {"query": "battery recycling"})
    finally:
        tavily_tool.coroutine = original

    assert "search results for" in result
    assert tavily_calls == [
        {"queries": ["battery recycling"], "max_results": 5, "topic": "general"}
    ]


###################
# Classification (TC-SRC-16)
###################
def wrapped(cause: BaseException) -> Exception:
    """Wrap an exception as `__cause__`, as a client library does."""
    outer = RuntimeError("request failed")
    try:
        raise outer from cause
    except RuntimeError as raised:
        return raised


@pytest.mark.parametrize(
    ("factory", "category", "eligible"),
    [
        (lambda: tavily_errors().TimeoutError("slow"), "timeout", True),
        (lambda: httpx.TimeoutException("slow"), "timeout", True),
        (lambda: asyncio.TimeoutError(), "timeout", True),
        (lambda: mcp_error(408), "timeout", True),
        (lambda: httpx.ConnectError("refused"), "connection", True),
        (lambda: mcp_error(-32000), "connection", True),
        (lambda: tavily_errors().UsageLimitExceededError("quota"), "rate_limit", True),
        (lambda: http_status_error(429), "rate_limit", True),
        (lambda: http_status_error(503), "server_error", True),
        (
            lambda: tavily_errors().InvalidAPIKeyError("bad key"),
            "credential_rejected",
            True,
        ),
        (
            lambda: tavily_errors().ForbiddenError("forbidden"),
            "credential_rejected",
            True,
        ),
        (lambda: http_status_error(401), "credential_rejected", True),
        (lambda: http_status_error(403), "credential_rejected", True),
        (lambda: tavily_errors().BadRequestError("bad"), "malformed", False),
        (lambda: http_status_error(400), "malformed", False),
        (
            lambda: tavily_errors().MissingAPIKeyError(),
            "missing_credential",
            False,
        ),
        (lambda: ToolException("tool failed"), "other", False),
        (lambda: ValueError("plain"), "other", False),
        (lambda: wrapped(httpx.ConnectError("refused")), "connection", True),
    ],
    ids=[
        "tavily_timeout",
        "httpx_timeout",
        "asyncio_timeout",
        "mcp_408",
        "httpx_connect",
        "mcp_connection_closed",
        "usage_limit",
        "http_429",
        "http_503",
        "invalid_key",
        "forbidden",
        "http_401",
        "http_403",
        "bad_request",
        "http_400",
        "missing_key",
        "tool_exception",
        "plain_value_error",
        "wrapped_httpx",
    ],
)
def test_error_classification_is_typed(factory, category, eligible):
    """TC-SRC-16 / INV-010: each signal gets the category and eligibility of ADR-008 §3.4."""
    from open_deep_research.search.fallback import classify_search_error

    assert classify_search_error(factory()) == (eligible, category)


def test_exception_group_is_followed():
    """ADR-008 §3.4: the classifier follows the members of an exception group."""
    from open_deep_research.search.fallback import classify_search_error

    group = ExceptionGroup(  # noqa: F821 - ruff reads the target version from pyproject.toml
        "group", [wrapped(httpx.ConnectError("refused")), ValueError("plain")]
    )
    assert classify_search_error(group) == (True, "connection")


def test_message_text_is_never_parsed():
    """ADR-008 §3.4: a plain error whose text mentions a timeout stays `other`."""
    from open_deep_research.search.fallback import classify_search_error

    assert classify_search_error(RuntimeError("timeout: connection refused")) == (
        False,
        "other",
    )


###################
# Tools unchanged without fallback (TC-SRC-17)
###################
def test_tools_unchanged_without_fallback():
    """TC-SRC-17 / INV-010: an empty `search_fallback` returns the tools as they are."""
    primary = FakeTavilyTool(lambda **_kwargs: "result")
    other = FakeSearchTool("think_tool", lambda **_kwargs: "reflect")

    assert apply([primary, other], configuration([])) == [primary, other]


@pytest.mark.parametrize("called", ["tavily_search", "self_hosted_search"])
def test_wrapped_tools_keep_name_and_schema(called):
    """TC-SRC-17: a wrapped tool keeps its name, description and argument schema."""
    primary = FakeTavilyTool(lambda **_kwargs: "result")
    mcp = mcp_tool()
    tools = apply([primary, mcp], configuration(["self_hosted_search", "tavily"]))

    wrapped_tool = next(tool for tool in tools if tool.name == called)
    original = primary if called == "tavily_search" else mcp
    assert wrapped_tool is not original, (
        "the fallback wraps the tool instead of changing it"
    )
    assert wrapped_tool.description == original.description
    assert set(wrapped_tool.args_schema.model_fields) == set(
        original.args_schema.model_fields
    )
    assert primary.args_schema.model_fields["queries"].annotation == list[str]


def test_other_tools_are_not_wrapped():
    """ADR-008 §3.2: tools outside the configured search sources are never wrapped."""
    reflection = FakeSearchTool("think_tool", lambda **_kwargs: "reflect")
    mcp = mcp_tool()

    tools = apply([reflection, mcp], configuration(["self_hosted_search", "tavily"]))

    assert tools[0] is reflection
    assert tools[1] is not mcp


def test_a_tool_without_another_listed_source_is_not_wrapped():
    """ADR-008 §3.2: a search tool is wrapped only when at least one other source is listed."""
    mcp = mcp_tool()

    tools = apply([mcp], configuration(["self_hosted_search"]))

    assert tools == [mcp]


def test_each_source_is_used_at_most_once():
    """ADR-008 §3.2, §3.3: the called tool runs once; an MCP fallback gets one call per query."""
    errors = tavily_errors()
    primary = FakeTavilyTool(lambda **_kwargs: _raise(errors.TimeoutError("timed out")))
    fallback = mcp_tool()
    tools = apply([primary, fallback], configuration(["self_hosted_search"]))

    invoke(tools[0], {"queries": ["q1", "q2"]})

    assert len(primary.calls) == 1
    assert fallback.calls == [{"query": "q1"}, {"query": "q2"}]
