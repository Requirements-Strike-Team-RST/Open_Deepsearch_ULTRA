"""REQ-007 (and the `search_fallback` rule of REQ-008): the search configuration is validated before research.

Covers TC-SRC-01 to TC-SRC-09 and TC-SRC-18 (``verification-constraints.md`` §7,
search) and INV-005. The interface is ``search/validation.py``, called first in
`clarify_with_user` and `researcher` (ADR-006 §3.1, §3.3, §3.4). The fake model
fails the test when it is called and the MCP loader is fake; no network is used.
"""

import pytest

from test.offline import helpers

SUPPORTED_VALUES = ("anthropic", "openai", "tavily", "none")
PROJECT_ENVIRONMENT_VARIABLES = (
    "SEARCH_API",
    "RESEARCH_MODEL",
    "MCP_CONFIG",
    "TASK_CONTRACT_ENABLED",
    "SEARCH_FALLBACK",
    "ALLOW_CLARIFICATION",
)


class FakeTool:
    """Minimal tool object that carries a name."""

    def __init__(self, name: str):
        self.name = name

    async def ainvoke(self, _args, _config=None):
        return "result"


class ForbiddenModel:
    """Fake model that fails the test when any code calls it before validation passes."""

    def __init__(self):
        self.calls = 0

    def bind_tools(self, _tools):
        return self

    def with_retry(self, **_kwargs):
        return self

    def with_config(self, _config):
        return self

    def with_structured_output(self, *_args, **_kwargs):
        return self

    async def ainvoke(self, *_args, **_kwargs):
        self.calls += 1
        raise AssertionError(
            "the model must not be called before the configuration is valid"
        )


@pytest.fixture
def config(monkeypatch):
    """Return a builder for a runtime configuration that no environment variable overrides."""

    def build(**values) -> dict:
        for name in PROJECT_ENVIRONMENT_VARIABLES:
            monkeypatch.delenv(name, raising=False)
        base = {"task_contract_enabled": False}
        base.update(values)
        return {"configurable": base}

    return build


@pytest.fixture
def fake_tools(monkeypatch):
    """Replace the search tool and the MCP loader of `utils` with fakes (ADR-006 §3.3)."""
    from open_deep_research import utils

    state = {
        "search_tool": FakeTool("tavily_search"),
        "mcp": [FakeTool("self_hosted_search")],
    }

    async def get_search_tool(_search_api):
        return [state["search_tool"]] if state["search_tool"] else []

    async def load_mcp_tools(_config, _existing):
        return list(state["mcp"])

    monkeypatch.setattr(utils, "get_search_tool", get_search_tool)
    monkeypatch.setattr(utils, "load_mcp_tools", load_mcp_tools)
    return state


###################
# Configuration rules (TC-SRC-01 to 04, 07, 18)
###################
@pytest.mark.parametrize(
    ("search_api", "research_model"),
    [("anthropic", "openai:gpt-4.1"), ("openai", "claude-sonnet-4")],
)
def test_native_search_model_mismatch_rejected(config, search_api, research_model):
    """TC-SRC-01 / C-001; INV-005: a native search paired with another provider's model is rejected."""
    from open_deep_research.search.validation import (
        SearchConfigError,
        load_search_config,
    )

    with pytest.raises(SearchConfigError) as failure:
        load_search_config(config(search_api=search_api, research_model=research_model))

    message = str(failure.value)
    assert "search_api" in message and "research_model" in message


@pytest.mark.parametrize(
    "mcp_config",
    [None, {"tools": ["self_hosted_search"]}, {"url": "https://mcp.example.org"}],
)
def test_no_search_tool_rejected(config, mcp_config):
    """TC-SRC-02 / C-002; INV-005: search_api none without a usable MCP declaration is rejected."""
    from open_deep_research.search.validation import (
        SearchConfigError,
        load_search_config,
    )

    with pytest.raises(SearchConfigError) as failure:
        load_search_config(config(search_api="none", mcp_config=mcp_config))

    message = str(failure.value)
    assert "search_api" in message and "mcp_config" in message


def test_unsupported_provider_rejected(config, monkeypatch):
    """TC-SRC-03 / C-003; INV-005: an unknown provider lists the supported values, from config or environment."""
    from open_deep_research.search.validation import (
        SearchConfigError,
        load_search_config,
    )

    with pytest.raises(SearchConfigError) as failure:
        load_search_config(config(search_api="bing"))
    assert all(value in str(failure.value) for value in SUPPORTED_VALUES)

    monkeypatch.setenv("SEARCH_API", "bing")
    with pytest.raises(SearchConfigError) as environment_failure:
        load_search_config({"configurable": {}})
    assert all(value in str(environment_failure.value) for value in SUPPORTED_VALUES)


def test_valid_tavily_configuration_accepted(config, fake_tools):
    """TC-SRC-04 / C-004: Tavily is accepted and the assembled tools include tavily_search."""
    from open_deep_research import utils
    from open_deep_research.search.validation import (
        load_search_config,
        require_search_tools,
    )

    runtime = config(search_api="tavily", research_model="openai:gpt-4.1")
    configuration = load_search_config(runtime)
    assert configuration.search_api.value == "tavily"

    tools = helpers.run_async(utils.get_all_tools(runtime))
    names = {getattr(tool, "name", None) for tool in tools}
    assert "tavily_search" in names
    assert require_search_tools(tools, search_api="tavily") is None


@pytest.mark.parametrize(
    ("search_api", "research_model", "accepted"),
    [
        ("openai", "gpt-4.1", True),
        ("openai", "o3-mini", True),
        ("openai", "openai:gpt-4.1", True),
        ("anthropic", "claude-sonnet-4", True),
        ("anthropic", "anthropic:claude-sonnet-4", True),
        ("openai", "azure_openai:gpt-4.1", False),
        ("anthropic", "anthropic_bedrock:claude-sonnet-4", False),
        ("openai", "openrouter:openai/gpt-4.1", False),
        ("openai", "mystery-model", False),
    ],
)
def test_native_search_provider_allowlist(config, search_api, research_model, accepted):
    """TC-SRC-07 / U-3: allowlisted providers are accepted (bare or prefixed); every other one fails closed."""
    from open_deep_research.search.validation import (
        SearchConfigError,
        load_search_config,
        model_provider,
    )

    runtime = config(search_api=search_api, research_model=research_model)
    if accepted:
        assert model_provider(research_model) == search_api
        assert load_search_config(runtime) is not None
        return
    assert model_provider(research_model) not in {"openai", "anthropic"}
    with pytest.raises(SearchConfigError) as failure:
        load_search_config(runtime)
    assert "research_model" in str(failure.value)


def test_task_contract_rejects_native_search(config):
    """TC-SRC-06 / REQ-001 rule: the task contract cannot use native search (ADR-001 §3.2)."""
    from open_deep_research.search.validation import (
        SearchConfigError,
        load_search_config,
    )

    with pytest.raises(SearchConfigError) as failure:
        load_search_config(
            config(
                search_api="openai",
                research_model="openai:gpt-4.1",
                task_contract_enabled=True,
            )
        )

    message = str(failure.value)
    assert "task_contract_enabled" in message and "search_api" in message


@pytest.mark.parametrize("entry", ["openai", "not_in_mcp_config"])
def test_unknown_fallback_entry_rejected(config, entry):
    """TC-SRC-18 / REQ-008 rule: an unknown search_fallback entry is rejected before the run."""
    from open_deep_research.search.validation import (
        SearchConfigError,
        load_search_config,
    )

    runtime = config(
        search_api="tavily",
        search_fallback=[entry],
        mcp_config={"url": "https://mcp.example.org", "tools": ["self_hosted_search"]},
    )
    with pytest.raises(SearchConfigError) as failure:
        load_search_config(runtime)
    assert "search_fallback" in str(failure.value) and entry in str(failure.value)


###################
# The run stops before any model call (TC-SRC-08)
###################
def test_mcp_without_tools_stops_run(config, fake_tools, monkeypatch):
    """TC-SRC-08 / U-1; INV-005: with MCP configured but no tool loaded, clarify_with_user stops the run."""
    from open_deep_research import deep_researcher
    from open_deep_research.search.validation import SearchUnavailableError

    model = ForbiddenModel()
    helpers.install_model(monkeypatch, deep_researcher, model)
    fake_tools["search_tool"] = None
    fake_tools["mcp"] = []

    runtime = config(
        search_api="none",
        allow_clarification=True,
        mcp_config={"url": "https://mcp.example.org", "tools": ["self_hosted_search"]},
    )
    state = {"messages": [helpers.human_message("battery recycling")]}

    with pytest.raises(SearchUnavailableError) as failure:
        helpers.run_async(deep_researcher.clarify_with_user(state, runtime))

    assert "mcp_config" in str(failure.value)
    assert model.calls == 0


###################
# The researcher checks its tools (TC-SRC-05, 09)
###################
def test_researcher_requires_search_tool(config, monkeypatch):
    """TC-SRC-09 / U-4; INV-005: only core tools raise before the model call; a search tool lets the call proceed."""
    from langchain_core.messages import AIMessage

    from open_deep_research import deep_researcher
    from open_deep_research.search.validation import (
        SearchUnavailableError,
        require_search_tools,
    )

    core = [FakeTool("ResearchComplete"), FakeTool("think_tool")]
    with pytest.raises(SearchUnavailableError):
        require_search_tools(core, search_api="tavily")
    assert (
        require_search_tools(core + [FakeTool("tavily_search")], search_api="tavily")
        is None
    )

    # The researcher node itself, with the tools `get_all_tools` returns.
    offered = {"tools": core}

    async def assembled(_config):
        return list(offered["tools"])

    monkeypatch.setattr(deep_researcher, "get_all_tools", assembled)
    state = {
        "researcher_messages": [helpers.human_message("question")],
        "research_brief": "topic",
    }

    forbidden = ForbiddenModel()
    helpers.install_model(monkeypatch, deep_researcher, forbidden)
    with pytest.raises(SearchUnavailableError):
        helpers.run_async(
            deep_researcher.researcher(state, config(search_api="tavily"))
        )
    assert forbidden.calls == 0, "no model call without a search tool"

    offered["tools"] = core + [FakeTool("tavily_search")]
    model = helpers.RecordingRunnable([AIMessage(content="", tool_calls=[])])
    helpers.install_model(monkeypatch, deep_researcher, model)
    command = helpers.run_async(
        deep_researcher.researcher(state, config(search_api="tavily"))
    )
    assert helpers.command_goto(command) == "researcher_tools"
    assert len(model.invocations) == 1, "with a search tool the researcher proceeds"


def test_require_search_tools_names_mcp_config(config):
    """ADR-006 §3.3: the "no search available" error names mcp_config when search_api is none."""
    from open_deep_research.search.validation import (
        SearchUnavailableError,
        require_search_tools,
    )

    core = [FakeTool("ResearchComplete"), FakeTool("think_tool")]
    with pytest.raises(SearchUnavailableError) as failure:
        require_search_tools(core, search_api="none")
    assert "mcp_config" in str(failure.value)


def test_researcher_entry_validates(config, monkeypatch):
    """TC-SRC-05: a direct researcher call validates the configuration before the model call."""
    from open_deep_research import deep_researcher
    from open_deep_research.search.validation import SearchConfigError

    model = ForbiddenModel()
    helpers.install_model(monkeypatch, deep_researcher, model)

    runtime = config(search_api="anthropic", research_model="openai:gpt-4.1")
    state = {
        "researcher_messages": [helpers.human_message("question")],
        "research_brief": "topic",
    }

    with pytest.raises(SearchConfigError):
        helpers.run_async(deep_researcher.researcher(state, runtime))
    assert model.calls == 0


def test_researcher_entry_validates_its_tools(config, monkeypatch):
    """TC-SRC-05 / ADR-006 §3.4: the researcher checks for a search tool as well, before the model call."""
    from open_deep_research import deep_researcher
    from open_deep_research.search.validation import SearchUnavailableError

    model = ForbiddenModel()
    helpers.install_model(monkeypatch, deep_researcher, model)

    async def core_only(_config):
        return [FakeTool("ResearchComplete"), FakeTool("think_tool")]

    monkeypatch.setattr(deep_researcher, "get_all_tools", core_only)

    state = {
        "researcher_messages": [helpers.human_message("question")],
        "research_brief": "topic",
    }
    with pytest.raises(SearchUnavailableError):
        helpers.run_async(
            deep_researcher.researcher(state, config(search_api="tavily"))
        )
    assert model.calls == 0
