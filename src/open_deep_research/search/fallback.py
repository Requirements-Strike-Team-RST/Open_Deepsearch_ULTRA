"""Ordered search fallback inside the search module.

REQ-008, ADR-008, INV-010, POL-024. ``apply_search_fallback`` wraps the search
tools so that a failed call tries the configured fallback sources in order;
``classify_search_error`` decides from exception types, MCP error codes and HTTP
status codes whether a failure allows a fallback, never from message text. The
wrapper only raises; turning an error into text stays in ``execute_tool_safely``.
"""

import asyncio
from collections.abc import Mapping
from typing import Any, Optional

import httpx
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool, ToolException
from tavily import errors as tavily_errors

from open_deep_research import utils
from open_deep_research.configuration import Configuration

ALL_SOURCES_FAILED_PREFIX = "All search sources failed:"
TAVILY_ENTRY = "tavily"
TAVILY_TOOL_NAME = "tavily_search"
NOT_AVAILABLE = "not available"

# ADR-008 §3.4: the typed Tavily errors with their eligibility and category.
_TAVILY_ERRORS: tuple[tuple[type[BaseException], bool, str], ...] = (
    (tavily_errors.TimeoutError, True, "timeout"),
    (tavily_errors.UsageLimitExceededError, True, "rate_limit"),
    (tavily_errors.InvalidAPIKeyError, True, "credential_rejected"),
    (tavily_errors.ForbiddenError, True, "credential_rejected"),
    (tavily_errors.BadRequestError, False, "malformed"),
    (tavily_errors.MissingAPIKeyError, False, "missing_credential"),
)
# ADR-008 §3.4: 408 is the MCP client's request timeout, -32000 CONNECTION_CLOSED.
_MCP_ERROR_CODES: dict[int, tuple[bool, str]] = {
    408: (True, "timeout"),
    -32000: (True, "connection"),
}


class AllSourcesFailedError(RuntimeError):
    """Every configured search source failed or was not available (ADR-008 §3.4).

    ``attempts`` holds one ``(source, category, error text)`` per source, in the
    order the sources were tried. The message starts with
    ``All search sources failed:``, so it never reads like an empty result.
    """

    def __init__(self, attempts: list[tuple[str, str, str]]):
        """Store the attempts and build the message that lists them."""
        self.attempts = list(attempts)
        details = "; ".join(
            f"{source} ({category}): {error}"
            for source, category, error in self.attempts
        )
        super().__init__(f"{ALL_SOURCES_FAILED_PREFIX} {details}")


def _is_mcp_error(exc: BaseException) -> bool:
    """Return whether ``exc`` is the MCP client's ``McpError``.

    The type is matched by name and package so that this module needs no MCP
    client import (``structural-constraints.md`` §10, search).
    """
    return any(
        cls.__name__ == "McpError" and cls.__module__.split(".")[0] == "mcp"
        for cls in type(exc).__mro__
    )


def _classify_one(exc: BaseException) -> Optional[tuple[bool, str]]:
    """Classify one exception by its type, MCP code or HTTP status; ``None`` if nothing matches."""
    for error_type, eligible, category in _TAVILY_ERRORS:
        if isinstance(exc, error_type):
            return eligible, category
    if _is_mcp_error(exc):
        code = getattr(getattr(exc, "error", None), "code", None)
        if code in _MCP_ERROR_CODES:
            return _MCP_ERROR_CODES[code]
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        if status == 429:
            return True, "rate_limit"
        if 500 <= status < 600:
            return True, "server_error"
        if status in (401, 403):
            return True, "credential_rejected"
        if status == 400:
            return False, "malformed"
        return None
    # ``TimeoutException`` is a ``TransportError``, so it is checked first.
    if isinstance(exc, httpx.TimeoutException):
        return True, "timeout"
    if isinstance(exc, httpx.TransportError):
        return True, "connection"
    if isinstance(exc, asyncio.TimeoutError):
        return True, "timeout"
    if isinstance(exc, ToolException):
        return False, "other"
    return None


def classify_search_error(exc: BaseException) -> tuple[bool, str]:
    """Return ``(eligible, category)`` for a search failure (REQ-008, ADR-008 §3.4).

    The exception is checked first, then its ``__cause__`` and the members of an
    exception group, until one signal matches. Message text is never parsed,
    so anything without a known signal is ``other`` and not eligible.
    """
    pending: list[BaseException] = [exc]
    seen: set[int] = set()
    while pending:
        current = pending.pop(0)
        if id(current) in seen:
            continue
        seen.add(id(current))
        match = _classify_one(current)
        if match is not None:
            return match
        # The members of an exception group (``BaseExceptionGroup.exceptions``).
        members = getattr(current, "exceptions", None)
        if isinstance(members, list | tuple):
            pending.extend(m for m in members if isinstance(m, BaseException))
        if current.__cause__ is not None:
            pending.append(current.__cause__)
    return False, "other"


def _tool_name(tool: Any) -> Optional[str]:
    """Return the name of a client-side tool; native search tools (dicts) have none here."""
    if isinstance(tool, Mapping):
        return None
    name = getattr(tool, "name", None)
    return name if isinstance(name, str) else None


def _source_name(entry: str) -> str:
    """Return the tool name of a ``search_fallback`` entry (``tavily`` is ``tavily_search``)."""
    return TAVILY_TOOL_NAME if entry == TAVILY_ENTRY else entry


def _required_string_argument(tool: Any) -> Optional[str]:
    """Return the single required string argument of an MCP tool, or ``None`` (ADR-008 §3.3)."""
    schema = getattr(tool, "args_schema", None)
    if isinstance(schema, Mapping):
        # MCP tools carry the server's JSON schema.
        required = list(schema.get("required") or [])
        properties = schema.get("properties") or {}
        if len(required) != 1:
            return None
        kind = (properties.get(required[0]) or {}).get("type")
        return required[0] if kind == "string" else None
    fields = getattr(schema, "model_fields", None) or {}
    required = [name for name, field in fields.items() if field.is_required()]
    if len(required) != 1 or fields[required[0]].annotation is not str:
        return None
    return required[0]


def _queries_of(tool: Any, arguments: Mapping[str, Any]) -> list[str]:
    """Return the queries of a call: Tavily's ``queries``, or an MCP tool's one string argument."""
    if _tool_name(tool) == TAVILY_TOOL_NAME:
        values = arguments.get("queries")
        if not isinstance(values, list | tuple):
            return []
        return [value for value in values if isinstance(value, str) and value.strip()]
    argument = _required_string_argument(tool)
    value = arguments.get(argument) if argument else None
    return [value] if isinstance(value, str) and value.strip() else []


def _text(output: Any) -> str:
    """Return a tool output as text, joining the text parts of block content (ADR-008 §3.3)."""
    if isinstance(output, str):
        return output
    if isinstance(output, list | tuple):
        return "\n".join(
            str(block.get("text", "")) if isinstance(block, Mapping) else str(block)
            for block in output
        )
    return str(output)


def _error_text(exc: BaseException) -> str:
    """Return an error's text, or its type name when it has none."""
    return str(exc) or type(exc).__name__


async def _call_fallback(
    name: str, source: Any, queries: list[str], config: RunnableConfig
) -> Any:
    """Call one fallback source with the queries of the failed call (ADR-008 §3.3)."""
    if name == TAVILY_TOOL_NAME:
        return await source.ainvoke({"queries": queries}, config)
    argument = _required_string_argument(source)
    outputs = [
        _text(await source.ainvoke({argument: query}, config)) for query in queries
    ]
    return "\n\n".join(outputs)


async def _search(
    called_tool: Any,
    arguments: Mapping[str, Any],
    fallbacks: list[str],
    loaded: Mapping[str, Any],
    config: RunnableConfig,
) -> Any:
    """Run the called tool, then the fallback sources in configured order (ADR-008 §3.2, §3.4)."""
    called = called_tool.name
    attempts: list[tuple[str, str, str]] = []
    try:
        return await called_tool.ainvoke(dict(arguments), config)
    except Exception as exc:  # classified below; ineligible errors are re-raised
        eligible, category = classify_search_error(exc)
        if not eligible:
            raise
        attempts.append((called, category, _error_text(exc)))

    queries = _queries_of(called_tool, arguments)
    for name in fallbacks:
        if name == TAVILY_TOOL_NAME:
            # The loaded Tavily tool when search_api is tavily, else the shared one.
            source = loaded.get(TAVILY_TOOL_NAME) or utils.tavily_search
        else:
            source = loaded.get(name)
        if source is None:
            attempts.append(
                (
                    name,
                    NOT_AVAILABLE,
                    "the source listed in search_fallback did not load",
                )
            )
            continue
        if name != TAVILY_TOOL_NAME and _required_string_argument(source) is None:
            attempts.append(
                (
                    name,
                    NOT_AVAILABLE,
                    "an MCP fallback source needs exactly one required string argument",
                )
            )
            continue
        if not queries:
            attempts.append(
                (
                    name,
                    NOT_AVAILABLE,
                    "the failed call carries no query for this source",
                )
            )
            continue
        try:
            return await _call_fallback(name, source, queries, config)
        except Exception as exc:  # recorded, so earlier attempts are not lost
            _eligible, category = classify_search_error(exc)
            attempts.append((name, category, _error_text(exc)))
    raise AllSourcesFailedError(attempts)


def _wrap(tool: Any, fallbacks: list[str], loaded: Mapping[str, Any]) -> StructuredTool:
    """Return a new tool with the same name, description and argument schema that falls back.

    The original tool object is never modified (the Tavily tool is shared), and
    every source is the original tool, never a wrapper.
    """

    async def search_with_fallback(
        config: RunnableConfig = None, **arguments: Any
    ) -> Any:
        return await _search(tool, arguments, fallbacks, loaded, config)

    return StructuredTool(
        name=tool.name,
        description=getattr(tool, "description", None) or "",
        args_schema=tool.args_schema,
        coroutine=search_with_fallback,
        metadata=getattr(tool, "metadata", None),
    )


def apply_search_fallback(tools: list, configurable: Configuration) -> list:
    """Return ``tools`` with the configured search tools wrapped for fallback (REQ-008, ADR-008 §3.2).

    With an empty ``search_fallback`` the list is returned unchanged. Otherwise
    a tool is wrapped when it is the Tavily tool or an MCP tool named in
    ``search_fallback``, and at least one other source is listed. Every other
    tool is returned as it is and never falls back.
    """
    entries: list[str] = []
    for entry in getattr(configurable, "search_fallback", None) or []:
        name = _source_name(entry)
        if name not in entries:
            entries.append(name)
    if not entries:
        return tools

    loaded: dict[str, Any] = {}
    for tool in tools:
        name = _tool_name(tool)
        if name is not None:
            loaded.setdefault(name, tool)

    result = []
    for tool in tools:
        name = _tool_name(tool)
        fallbacks = [entry for entry in entries if entry != name]
        is_source = name == TAVILY_TOOL_NAME or name in entries
        if name is None or not is_source or not fallbacks:
            result.append(tool)
            continue
        result.append(_wrap(tool, fallbacks, loaded))
    return result
