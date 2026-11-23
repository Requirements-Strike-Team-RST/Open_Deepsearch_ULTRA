# ADR-006: Validate the search configuration before any model call

- **Status:** Accepted
- **Date:** 2026-11-17
- **Module:** search
- **Owner:** sszfot
- **Evaluation:** EVAL-006 (`docs/architecture/evaluation-table.md`)
- **SA Review:** passed in the SA integration PR [#22](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/22) (approved by BroZhai and DopplerXD, merged 2026-11-18)
- **Team decisions:** U-1 to U-4 decided in [Discussion #19](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/discussions/19) on 2026-11-17 (U-1 A, U-2 reworded, U-3 B, U-4 B)

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-007 | C-001, C-002, C-003 | Invalid configurations must be rejected before any model or search call. The check must therefore run before `clarify_with_user` calls its model, not during tool assembly in `researcher`. |
| REQ-007 | C-004 | A valid configuration must behave as before. |
| REQ-007 | C-005 | The README must explain the providers, their model requirements and MCP search. |

REQ-008 (search fallback) belongs to the same module and is decided in ADR-008; this ADR only adds its configuration rule (§3.1).

## 2. Context

Baseline (line numbers at commit `daf6947`):

- `configuration.py` L11-17, L78-93: `search_api` is `anthropic`, `openai`, `tavily` or `none`. Nothing checks that native search matches the research model; the UI only shows a note.
- `configuration.py` L236-247: `from_runnable_config` reads the environment variable (`SEARCH_API`) first and `configurable` second. An unknown value already fails Pydantic validation, but with a raw Pydantic message, and only when a node first builds the configuration.
- `deep_researcher.py` L101 and L154: the first model calls happen in `clarify_with_user` and `write_research_brief`, long before the researcher assembles its tools (L384).
- `deep_researcher.py` L384-389: the "no tools" guard never fires, because `get_all_tools` always adds `ResearchComplete` and `think_tool` (`utils.py` L579).
- `utils.py` L449-524: `load_mcp_tools` returns an empty list for every MCP problem (missing settings, missing token, connection error, no matching tool name). With `search_api=none` and such an MCP problem, research runs without any search.
- LangChain 1.3.9 (`langchain/chat_models/base.py`, `_parse_model` and `_attempt_infer_model_provider`): `init_chat_model` takes the text before `:` as the provider when it is a known provider; otherwise it infers `openai` for names starting with `gpt-`, `o1`, `o3`, `chatgpt` or `text-davinci`, and `anthropic` for names starting with `claude`.

## 3. Decision

Use EVAL-006 option B: the search module checks the configuration with pure functions, called from two nodes. No configuration flag: valid configurations are not affected.

### 3.1 Configuration check (before any model call)

`load_search_config(config: RunnableConfig) -> Configuration` builds the configuration with `Configuration.from_runnable_config` and applies the rules below. It raises `SearchConfigError` (a `ValueError`) whose message names the setting to change.

| Rule | Check | Error names |
|---|---|---|
| Supported provider (C-003) | Building the configuration fails on `search_api` | `search_api` / `SEARCH_API` and the supported values `anthropic, openai, tavily, none` (lower-case) |
| Native search matches the model (C-001) | `search_api` is `openai` or `anthropic`, and the provider of `research_model` (§3.2) is not on that search's allowlist | `search_api` and `research_model` |
| Some search source is configured (C-002) | `search_api` is `none` and `mcp_config` is missing, has no `url` or has no `tools` | `search_api` and `mcp_config` |
| Task contract needs tool results (REQ-001) | `task_contract_enabled` is on and `search_api` is `openai` or `anthropic` | `task_contract_enabled` and `search_api` (ADR-001 §3.2) |
| Valid fallback sources (REQ-008, ADR-008) | An entry of `search_fallback` is neither `"tavily"` nor a tool name listed in `mcp_config.tools` | `search_fallback` and the entry |

### 3.2 Provider of the research model (U-3: B)

`model_provider(model: str) -> str | None` follows `init_chat_model`'s rules (§2) with a small local table, without importing LangChain internals: a known `provider:` prefix first; otherwise `gpt-`, `o1`, `o3`, `chatgpt`, `text-davinci` → `openai` and `claude` → `anthropic`; otherwise `None`.

The allowlist contains only verified combinations:

| Native search | Allowed providers |
|---|---|
| `openai` | `openai` |
| `anthropic` | `anthropic` |

Everything else fails closed with `SearchConfigError`: for example `azure_openai:`, `anthropic_bedrock:`, `openrouter:` and names whose provider cannot be resolved. A provider is added to the allowlist only after its native search has been verified, through a change to this ADR.

### 3.3 Search tool check (U-1: A, U-4: B)

`require_search_tools(tools) -> None` raises `SearchUnavailableError` (a `RuntimeError`) when the assembled tool list holds no tool other than `ResearchComplete` and `think_tool`. The message says that no search is available and, when `search_api` is `none`, names `mcp_config`. The function does not try to tell connection, token and tool-name problems apart.

It is called in two places:

- **At the start of the run**, in `clarify_with_user`, right after `load_search_config`: the node calls `utils.get_all_tools(config)` and passes the result. Assembling tools loads the MCP tool list but calls no model and no search, so the run stops before any model call (U-1).
- **In `researcher`**, in place of the dead `len(tools) == 0` guard (U-4). This covers a direct call of the researcher subgraph and an MCP server that disappears during the run; with `task_contract_enabled` on, the error fails only that task (ADR-002).

### 3.4 Call order and wording

| Node | First statements |
|---|---|
| `clarify_with_user` | `load_search_config`; `get_all_tools`; `require_search_tools`; then the existing `allow_clarification` check |
| `researcher` | `load_search_config`; the existing `get_all_tools`; `require_search_tools` instead of the old guard |

A rejected configuration is "rejected before the first model or search call of a run" (U-2); configuration is read per run, so there is no separate start-up phase.

The README's search section explains: that the researcher model decides when to search; how to select each built-in provider and which research models the native providers accept; which keys are needed; and how to add a custom or self-hosted search server through `mcp_config`.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — checks written inside `clarify_with_user` | Logic in a graph node, no reusable interface, and the researcher subgraph entry would need a copy. |
| C — checks inside `utils.get_all_tools` | Runs only in `researcher`, after the model calls at L101 and L154, so C-001 fails. |
| Strict `provider:` prefix only (Discussion #19, U-3 A) | Rejects bare names such as `gpt-4.1` that `init_chat_model` resolves without problems. |
| Leaving runtime MCP failure to delivery (U-1 B) | The run would still start research with no search source and spend tokens before failing. |
| Environment snapshots, an MCP load adapter that tells each MCP failure apart, and a configured/bound/executed state model (an earlier draft) | Not needed for C-001 to C-005 or for the U-1 to U-4 decisions; one "no search available" error is enough. |

The full comparison is in EVAL-006.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `search/validation.py` | Build and check the configuration; resolve the model provider; check that a search tool exists | `load_search_config(config: RunnableConfig) -> Configuration`; `validate_search_config(configurable: Configuration) -> None`; `model_provider(model: str) -> str \| None`; `require_search_tools(tools: list) -> None`; `SearchConfigError(ValueError)`; `SearchUnavailableError(RuntimeError)` | `clarify_with_user`, `researcher` |
| `README.md` | Search set-up guide | — | readers (C-005) |

The module's functions are pure: they read values and tool lists passed in, and never call a model, a search provider or an MCP server themselves. No shared contract is added.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none.
- **Runtime policies:** POL-018, POL-019.
- **Invariants:** INV-005.
- **Deterministic boundary:** whether a configuration is valid and whether search is available are decided by code.

## 7. Verification

Cases in `verification-constraints.md` §7 (search). They build configurations and tool lists in memory, use a fake model that fails the test if it is called and a fake MCP loader, and need no network. The provider rules are pinned by tests, so a LangChain upgrade that changes `init_chat_model` inference shows up as a failing test. C-005 is a human review recorded in `docs/review-memo.md`.

## 8. Consequences

- **Positive:** invalid set-ups and runs without any search source stop at the start with a clear message instead of in the middle of research; bare model names keep working with native search.
- **Negative:** each run assembles the researcher tools once more at the start, which loads the MCP tool list. Provider and search combinations that might work but are not verified (Azure OpenAI, Bedrock, OpenRouter) are rejected until added to the allowlist (RISK-009). With `task_contract_enabled`, native search cannot be used at all (RISK-010).
- **Neutral:** valid configurations, tool assembly and the graph topology are unchanged. The replaced guard in `researcher` is a recorded change to baseline code (`structural-constraints.md` §10, search).

## 9. Implementation Steps

1. Add `search/__init__.py` and `search/validation.py` with the interface of §5; add `open_deep_research.search` to `[tool.setuptools] packages`. Docstrings name `REQ-007, ADR-006, INV-005`.
2. `clarify_with_user`: before the `allow_clarification` check, call `load_search_config(config)`, then `require_search_tools(await get_all_tools(config))`; use the returned configuration in the node.
3. `researcher`: call `load_search_config(config)` first, and replace the `len(tools) == 0` guard with `require_search_tools(tools)`.
4. Update the search section of `README.md` (C-005), including the allowlist of §3.2.
5. Run the checks in `verification-constraints.md` §4 and record them in `docs/build-reports/REQ-007.md`.
