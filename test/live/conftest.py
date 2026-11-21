"""Shared setup for the live checks (TC-ORC-13, TC-CIT-05).

The live files call a real model and a real search provider and are run on
demand (`uv run pytest test/live`), never in CI (``verification-constraints.md``
§3). They are marked ``live``; the repository has no marker registration yet, so
the module registers it on import.

Neither file chooses a configuration on its own: `verification-constraints.md`
§7 leaves that to a human, because the team's earlier baseline ran with search
disabled. A human selects the search-capable configuration through the
environment variables below and runs the files; when a variable is missing the
test reports which one, instead of guessing a provider.
"""

import asyncio
import os

import pytest

# What a human must provide before a live run (REQ-003 C-006, REQ-006 C-004).
REQUIRED_SETTINGS = {
    "OPEN_DEEP_RESEARCH_LIVE_SEARCH_API": "tavily or the name of an MCP search tool",
    "OPEN_DEEP_RESEARCH_LIVE_RESEARCH_MODEL": "the research model, e.g. openai:gpt-4.1",
}


def pytest_configure(config):
    """Register the ``live`` marker so a plain `pytest test/live` does not warn."""
    config.addinivalue_line(
        "markers", "live: calls a real model or search provider; run on demand"
    )


def live_settings() -> dict:
    """Return the configuration a human chose, or skip with the list of missing settings."""
    missing = [name for name in REQUIRED_SETTINGS if not os.environ.get(name)]
    if missing:
        wanted = "; ".join(f"{name} ({REQUIRED_SETTINGS[name]})" for name in missing)
        pytest.skip(
            f"a human must choose a search-capable configuration first: set {wanted}"
        )
    values = {name: os.environ[name] for name in REQUIRED_SETTINGS}
    values["mcp_config"] = os.environ.get("OPEN_DEEP_RESEARCH_LIVE_MCP_CONFIG")
    return values


def run_config(settings: dict, **overrides) -> dict:
    """Runtime configuration for a live run, with the task contract and its flags on.

    Clarification is off: an unattended run cannot answer a clarifying question,
    and a run that stops there never researches.
    """
    configurable = {
        "allow_clarification": False,
        "task_contract_enabled": True,
        "context_trimming": True,
        "search_api": settings["OPEN_DEEP_RESEARCH_LIVE_SEARCH_API"],
        "research_model": settings["OPEN_DEEP_RESEARCH_LIVE_RESEARCH_MODEL"],
        "coverage_threshold": 0.8,
    }
    if settings.get("mcp_config"):
        configurable["mcp_config"] = settings["mcp_config"]
    configurable.update(overrides)
    return {"configurable": configurable}


def run_query(query: str, config: dict) -> dict:
    """Run the research graph on one query and return its final state.

    Every graph node is ``async``, so the graph is streamed with ``astream``.
    """
    from open_deep_research.deep_researcher import deep_researcher

    async def stream() -> dict:
        final_state: dict = {}
        async for chunk in deep_researcher.astream(
            {"messages": [("user", query)]}, config, stream_mode="values"
        ):
            final_state = chunk
        return final_state

    return asyncio.run(stream())
