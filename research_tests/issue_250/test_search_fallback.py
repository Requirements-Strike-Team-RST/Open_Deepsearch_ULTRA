"""Regression tests for issue #250: deterministic search fallback mode.

These tests verify the minimal, backward-compatible search_mode design:

- ``search_mode="agent"`` (default) preserves the existing tool exposure, the
  built-in ``tavily_search`` tool name, and MCP tool availability.
- ``search_mode="fallback"`` builds a single composite ``web_search`` tool that
  invokes the providers listed in ``search_tool_order`` in order, returning the
  first result whose ``ainvoke`` completes without raising, and raising a
  ``ToolException`` when every provider fails.
"""

import pytest
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

import open_deep_research.utils as utils
from open_deep_research.configuration import Configuration, SearchAPI
from open_deep_research.utils import (
    ToolException,
    _resolve_fallback_search_tool,
    _validate_fallback_config,
    get_all_tools,
)


def make_config(search_mode="agent", search_tool_order=None, search_api="tavily"):
    """Build a minimal RunnableConfig with the requested search settings."""
    configurable = {"search_mode": search_mode}
    if search_tool_order is not None:
        configurable["search_tool_order"] = search_tool_order
    if search_api is not None:
        configurable["search_api"] = search_api
    return {"configurable": configurable}


def fake_tool(name, coro):
    """Build a fake executable LangChain tool for tests."""
    return tool(name, description=f"fake {name}")(coro)


def tool_names(tools):
    """Return the names of the given tools."""
    return [t.name for t in tools]


###########################
# Configuration contract
###########################


def test_default_mode_is_agent():
    assert Configuration().search_mode == "agent"


def test_search_provider_enum_unchanged():
    assert set(SearchAPI.__members__) == {"ANTHROPIC", "OPENAI", "TAVILY", "NONE"}
    assert {member.value for member in SearchAPI.__members__.values()} == {
        "anthropic",
        "openai",
        "tavily",
        "none",
    }


###########################
# Agent mode (unchanged behavior)
###########################


@pytest.mark.asyncio
async def test_agent_mode_preserves_existing_tool_exposure(monkeypatch):
    async def mcp_search(queries):
        return "mcp-search"

    async def helper():
        return "helper"

    mcp_tools = [
        fake_tool("fake_mcp_search", mcp_search),
        fake_tool("fake_helper_tool", helper),
    ]

    async def fake_load_mcp(config, existing_names):
        return mcp_tools

    monkeypatch.setattr(utils, "load_mcp_tools", fake_load_mcp)

    tools = await get_all_tools(make_config(search_mode="agent", search_api="tavily"))
    names = tool_names(tools)

    # The built-in provider keeps its existing name; no composite tool.
    assert "tavily_search" in names
    assert "web_search" not in names
    # Core tools and MCP tools all remain exposed.
    assert {"ResearchComplete", "think_tool", "fake_mcp_search", "fake_helper_tool"} <= set(names)


@pytest.mark.asyncio
async def test_existing_search_invocation_unchanged(monkeypatch):
    async def mcp_search(queries):
        return "mcp-search"

    async def fake_load_mcp(config, existing_names):
        return [fake_tool("fake_mcp_search", mcp_search)]

    monkeypatch.setattr(utils, "load_mcp_tools", fake_load_mcp)

    tools = await get_all_tools(make_config(search_mode="agent", search_api="tavily"))
    names = tool_names(tools)

    assert "tavily_search" in names
    assert "web_search" not in names
    # The composite fallback tool is never built in agent mode.
    assert all(name != "web_search" for name in names)


###########################
# Fallback mode
###########################


@pytest.mark.asyncio
async def test_fallback_exposes_composite_only(monkeypatch):
    async def mcp_search(queries):
        return "mcp-search"

    async def helper():
        return "helper"

    mcp_tools = [
        fake_tool("fake_mcp_search", mcp_search),
        fake_tool("fake_helper_tool", helper),
    ]

    async def fake_load_mcp(config, existing_names):
        return mcp_tools

    monkeypatch.setattr(utils, "load_mcp_tools", fake_load_mcp)

    config = make_config(
        search_mode="fallback",
        search_tool_order=["tavily_search", "fake_mcp_search"],
    )
    tools = await get_all_tools(config)
    names = tool_names(tools)

    # The composite tool is exposed under the name 'web_search'.
    assert "web_search" in names
    assert names.count("web_search") == 1
    # Participating providers are not exposed individually.
    assert "tavily_search" not in names
    assert "fake_mcp_search" not in names
    # Non-participating MCP tool and core tools remain.
    assert "fake_helper_tool" in names
    assert {"ResearchComplete", "think_tool"} <= set(names)


@pytest.mark.asyncio
async def test_fallback_mode_name_conflicts_safe(monkeypatch):
    async def mcp_search(queries):
        return "mcp-search"

    async def fake_load_mcp(config, existing_names):
        return [fake_tool("fake_mcp_search", mcp_search)]

    captured = {}

    async def recording_load_mcp(config, existing_names):
        captured["existing_names"] = set(existing_names)
        return [fake_tool("fake_mcp_search", mcp_search)]

    monkeypatch.setattr(utils, "load_mcp_tools", recording_load_mcp)

    config = make_config(
        search_mode="fallback",
        search_tool_order=["tavily_search", "fake_mcp_search"],
    )
    tools = await get_all_tools(config)
    names = tool_names(tools)

    # The composite name 'web_search' is protected from conflicts.
    assert "web_search" in captured["existing_names"]
    assert "ResearchComplete" in captured["existing_names"]
    assert "think_tool" in captured["existing_names"]
    assert names.count("web_search") == 1
    assert "fake_mcp_search" not in names


@pytest.mark.asyncio
async def test_fallback_provider_order_is_deterministic():
    calls = []

    async def first_provider(queries, config: RunnableConfig = None):
        calls.append("first")
        raise RuntimeError("first failed")

    async def second_provider(queries, config: RunnableConfig = None):
        calls.append("second")
        return "second result"

    first = fake_tool("first_tool", first_provider)
    second = fake_tool("second_tool", second_provider)

    composite = await _resolve_fallback_search_tool(["first_tool", "second_tool"], [first, second])
    result = await composite.ainvoke({"queries": ["q"]})

    assert result == "second result"
    assert calls == ["first", "second"]


@pytest.mark.asyncio
async def test_fallback_calls_next_provider_only_after_previous_fails():
    calls = []

    async def flaky(queries, config: RunnableConfig = None):
        calls.append("flaky")
        raise RuntimeError("flaky down")

    async def backup(queries, config: RunnableConfig = None):
        calls.append("backup")
        return "backup result"

    flaky_tool = fake_tool("flaky_tool", flaky)
    backup_tool = fake_tool("backup_tool", backup)

    composite = await _resolve_fallback_search_tool(["flaky_tool", "backup_tool"], [flaky_tool, backup_tool])
    result = await composite.ainvoke({"queries": ["q"]})

    assert result == "backup result"
    # The successful provider is not invoked after a failure.
    assert calls == ["flaky", "backup"]


@pytest.mark.asyncio
async def test_successful_primary_prevents_fallback_invocation():
    calls = []

    async def healthy(queries, config: RunnableConfig = None):
        calls.append("healthy")
        return "primary result"

    async def unused(queries, config: RunnableConfig = None):
        calls.append("unused")
        return "should not run"

    healthy_tool = fake_tool("healthy_tool", healthy)
    unused_tool = fake_tool("unused_tool", unused)

    composite = await _resolve_fallback_search_tool(["healthy_tool", "unused_tool"], [healthy_tool, unused_tool])
    result = await composite.ainvoke({"queries": ["q"]})

    assert result == "primary result"
    assert calls == ["healthy"]


@pytest.mark.asyncio
async def test_all_providers_fail_raises_clear_tool_exception():
    async def dead(queries, config: RunnableConfig = None):
        raise RuntimeError("provider A exploded")

    async def dead_too(queries, config: RunnableConfig = None):
        raise RuntimeError("provider B exploded")

    dead_tool = fake_tool("dead_tool", dead)
    dead_too_tool = fake_tool("dead_too_tool", dead_too)

    composite = await _resolve_fallback_search_tool(
        ["dead_tool", "dead_too_tool"], [dead_tool, dead_too_tool]
    )

    with pytest.raises(ToolException) as excinfo:
        await composite.ainvoke({"queries": ["q"]})

    message = str(excinfo.value)
    assert "All search providers failed" in message
    assert "provider A exploded" in message
    assert "provider B exploded" in message


@pytest.mark.asyncio
async def test_mcp_search_tool_can_participate_in_fallback():
    calls = []

    async def mcp_search(queries, config: RunnableConfig = None):
        calls.append("mcp_search")
        return "mcp result"

    mcp_tool = fake_tool("fake_mcp_search", mcp_search)

    composite = await _resolve_fallback_search_tool(["fake_mcp_search"], [mcp_tool])
    result = await composite.ainvoke({"queries": ["q"]})

    assert result == "mcp result"
    assert calls == ["mcp_search"]


@pytest.mark.asyncio
async def test_non_search_mcp_tools_remain_exposed(monkeypatch):
    async def mcp_search(queries):
        return "mcp-search"

    async def helper():
        return "helper"

    mcp_tools = [
        fake_tool("fake_mcp_search", mcp_search),
        fake_tool("fake_helper_tool", helper),
    ]

    async def fake_load_mcp(config, existing_names):
        return mcp_tools

    monkeypatch.setattr(utils, "load_mcp_tools", fake_load_mcp)

    config = make_config(
        search_mode="fallback",
        search_tool_order=["tavily_search", "fake_mcp_search"],
    )
    tools = await get_all_tools(config)
    names = tool_names(tools)

    assert "fake_helper_tool" in names
    assert "web_search" in names
    assert "fake_mcp_search" not in names


###########################
# Fallback validation
###########################


def test_fallback_rejects_missing_search_tool_order():
    configurable = Configuration(search_mode="fallback", search_tool_order=None)
    with pytest.raises(ValueError, match="search_tool_order"):
        _validate_fallback_config(configurable, None)


def test_fallback_rejects_empty_search_tool_order():
    configurable = Configuration(search_mode="fallback", search_tool_order=[])
    with pytest.raises(ValueError, match="search_tool_order"):
        _validate_fallback_config(configurable, [])


@pytest.mark.asyncio
async def test_fallback_mode_rejects_missing_order_via_get_all_tools():
    config = make_config(search_mode="fallback", search_tool_order=None)
    with pytest.raises(ValueError, match="search_tool_order"):
        await get_all_tools(config)


def test_fallback_rejects_openai_native_web_search():
    configurable = Configuration(search_mode="fallback", search_api=SearchAPI.OPENAI)
    with pytest.raises(ValueError, match="OpenAI or Anthropic"):
        _validate_fallback_config(configurable, ["tavily_search"])


def test_fallback_rejects_anthropic_native_web_search():
    configurable = Configuration(search_mode="fallback", search_api=SearchAPI.ANTHROPIC)
    with pytest.raises(ValueError, match="OpenAI or Anthropic"):
        _validate_fallback_config(configurable, ["tavily_search"])


@pytest.mark.asyncio
async def test_fallback_rejects_unknown_provider_names_at_construction():
    async def mcp_search(queries):
        return "mcp-search"

    async def helper():
        return "helper"

    mcp_tools = [
        fake_tool("fake_mcp_search", mcp_search),
        fake_tool("fake_helper_tool", helper),
    ]

    async def fake_load_mcp(config, existing_names):
        return mcp_tools

    unknown = "nonexistent_provider"
    config = make_config(
        search_mode="fallback",
        search_tool_order=["tavily_search", unknown],
    )

    # The error surfaces when the composite is built, not when it is invoked.
    with pytest.raises(ValueError, match=unknown):
        await _resolve_fallback_search_tool(["tavily_search", unknown], mcp_tools)


@pytest.mark.asyncio
async def test_fallback_rejects_unknown_provider_names_via_get_all_tools(monkeypatch):
    async def mcp_search(queries):
        return "mcp-search"

    async def fake_load_mcp(config, existing_names):
        return [fake_tool("fake_mcp_search", mcp_search)]

    monkeypatch.setattr(utils, "load_mcp_tools", fake_load_mcp)

    unknown = "does_not_exist"
    config = make_config(
        search_mode="fallback",
        search_tool_order=["tavily_search", unknown],
    )

    with pytest.raises(ValueError, match=unknown):
        await get_all_tools(config)