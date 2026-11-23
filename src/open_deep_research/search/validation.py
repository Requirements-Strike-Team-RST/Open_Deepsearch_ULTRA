"""Validate the search configuration before any model call.

REQ-007, ADR-006, INV-005, POL-018, POL-019. The functions are pure: they read
values and tool lists that are passed in and never call a model, a search
provider or an MCP server themselves. ``load_search_config`` is called first in
``clarify_with_user`` and ``researcher``; ``require_search_tools`` checks that
the assembled tool list holds a tool other than ``ResearchComplete`` and
``think_tool``.
"""

from typing import Any, Optional

from pydantic import ValidationError

from open_deep_research.configuration import Configuration, MCPConfig, SearchAPI

SUPPORTED_PROVIDERS = tuple(provider.value for provider in SearchAPI)
NATIVE_SEARCH_PROVIDERS = frozenset({SearchAPI.OPENAI.value, SearchAPI.ANTHROPIC.value})
# Verified combinations only; anything else fails closed (ADR-006 §3.2).
NATIVE_SEARCH_ALLOWLIST = {
    SearchAPI.OPENAI.value: frozenset({"openai"}),
    SearchAPI.ANTHROPIC.value: frozenset({"anthropic"}),
}
_KNOWN_PROVIDERS = {
    "openai",
    "anthropic",
    "azure_openai",
    "anthropic_bedrock",
    "openrouter",
    "google",
    "google_vertexai",
    "google_genai",
    "gemini",
    "bedrock",
    "cohere",
    "mistralai",
    "groq",
    "deepseek",
    "ollama",
    "fireworks",
    "upstage",
    "xai",
}
_BARE_MODEL_PROVIDERS = {
    "openai": ("gpt-", "o1", "o3", "chatgpt", "text-davinci"),
    "anthropic": ("claude",),
}
CORE_TOOL_NAMES = frozenset({"ResearchComplete", "think_tool"})


class SearchConfigError(ValueError):
    """The search configuration is invalid; the message names the setting to change."""


class SearchUnavailableError(RuntimeError):
    """No search tool is available, so research would run without searching."""


def model_provider(model: str) -> Optional[str]:
    """Return the provider ``init_chat_model`` would use for ``model``, or ``None``.

    ADR-006 §3.2: a known ``provider:`` prefix wins; otherwise a bare name that
    starts like an OpenAI or Anthropic model resolves to that provider; anything
    else is unresolved and rejected when native search is used.
    """
    text = str(model or "").strip()
    if not text:
        return None
    prefix, separator, _rest = text.partition(":")
    if separator and prefix.lower() in _KNOWN_PROVIDERS:
        return prefix.lower()
    lowered = text.lower()
    for provider, prefixes in _BARE_MODEL_PROVIDERS.items():
        if lowered.startswith(prefixes):
            return provider
    return None


def _search_api_value(configurable: Configuration) -> str:
    """Return the configured search API as its lower-case value."""
    return str(getattr(configurable.search_api, "value", configurable.search_api))


def _mcp_problem(mcp_config: Optional[MCPConfig]) -> Optional[str]:
    """Return why ``mcp_config`` cannot give the researcher any tool, or ``None``."""
    if mcp_config is None:
        return "mcp_config is not set"
    if not mcp_config.url:
        return "mcp_config has no url"
    if not mcp_config.tools:
        return "mcp_config lists no tools"
    return None


def validate_search_config(configurable: Configuration) -> None:
    """Apply the rules of ADR-006 §3.1 and ADR-008 §3.1 to ``configurable``.

    Raises ``SearchConfigError`` naming the setting to change.
    """
    api = _search_api_value(configurable)
    mcp_config = configurable.mcp_config
    if isinstance(mcp_config, dict):
        mcp_config = MCPConfig(**mcp_config)

    if api not in SUPPORTED_PROVIDERS:
        raise SearchConfigError(
            f"search_api is {api!r}, which is not supported; set search_api (or "
            f"SEARCH_API) to one of: {', '.join(SUPPORTED_PROVIDERS)}"
        )

    if api in NATIVE_SEARCH_PROVIDERS:
        provider = model_provider(configurable.research_model)
        if provider not in NATIVE_SEARCH_ALLOWLIST[api]:
            raise SearchConfigError(
                f"search_api={api} requires a research_model of provider {api}; "
                f"research_model={configurable.research_model!r} resolves to "
                f"{provider or 'an unknown provider'}. Set research_model to an "
                "allowed model or choose another search_api."
            )
        if configurable.task_contract_enabled:
            raise SearchConfigError(
                "task_contract_enabled cannot be combined with native search: "
                f"search_api={api} runs inside the model call and returns no tool "
                "results, so findings cannot be checked. Set search_api to tavily "
                "or to none with an MCP search tool."
            )

    if api == SearchAPI.NONE.value:
        problem = _mcp_problem(mcp_config)
        if problem:
            raise SearchConfigError(
                f"search_api=none needs an MCP search server, but {problem}. Set "
                "search_api to a provider or configure mcp_config with a url and tools."
            )

    if configurable.search_fallback:
        if not isinstance(configurable.search_fallback, list | tuple):
            raise SearchConfigError(
                "search_fallback must be a list of 'tavily' or mcp_config tool names"
            )
        listed = set(mcp_config.tools or []) if mcp_config is not None else set()
        for entry in configurable.search_fallback:
            if entry != "tavily" and entry not in listed:
                raise SearchConfigError(
                    f"search_fallback entry {entry!r} is neither 'tavily' nor a tool "
                    "listed in mcp_config.tools; fix search_fallback or mcp_config."
                )


def load_search_config(config: Any) -> Configuration:
    """Build the configuration of a run and validate its search settings.

    Raises ``SearchConfigError`` before any model or search call of the run
    (ADR-006 §3.4). A validation error of another setting is not a search
    error and propagates as it is.
    """
    try:
        configurable = Configuration.from_runnable_config(config)
    except ValidationError as exc:
        if not any(
            error.get("loc", ())[:1] == ("search_api",) for error in exc.errors()
        ):
            raise
        raise SearchConfigError(
            "search_api (or SEARCH_API) is not supported; set it to one of: "
            f"{', '.join(SUPPORTED_PROVIDERS)}. ({exc})"
        ) from exc
    validate_search_config(configurable)
    return configurable


def tool_name(tool: Any) -> str:
    """Return the name a tool advertises to the model (a native search dict is ``web_search``)."""
    if hasattr(tool, "name"):
        return str(tool.name)
    if isinstance(tool, dict):
        return str(tool.get("name", "web_search"))
    return str(tool)


def require_search_tools(tools: list, search_api: Optional[str] = None) -> None:
    """Raise ``SearchUnavailableError`` when the tools hold no search tool (REQ-007, ADR-006 §3.3).

    A tool counts as a search tool when it is neither ``ResearchComplete`` nor
    ``think_tool``. The message names ``mcp_config`` when ``search_api`` is
    ``none``, because that is the setting to add a search tool to.
    """
    names = {tool_name(tool) for tool in tools or []}
    if names - CORE_TOOL_NAMES:
        return
    hint = ""
    if str(getattr(search_api, "value", search_api)) == SearchAPI.NONE.value:
        hint = (
            " search_api is none, so add an MCP search server to mcp_config "
            "(a url and at least one tool name)."
        )
    raise SearchUnavailableError(
        "No search tool is available, so no research can be conducted."
        + hint
        + " Configure a search_api provider or mcp_config."
    )
