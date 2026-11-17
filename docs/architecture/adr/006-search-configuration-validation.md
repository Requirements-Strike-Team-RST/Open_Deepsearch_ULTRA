# ADR-006: Validate the search configuration before any model call

- **Status:** Proposed
- **Date:** 2026-11-17
- **Module:** search
- **Owner:** sszfot
- **Evaluation:** EVAL-006 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-007 | C-001, C-002, C-003 | Invalid configurations must be rejected before any model or search call. The check must therefore run before `clarify_with_user` calls its model, not during tool assembly in `researcher`. |
| REQ-007 | C-004 | A valid configuration must behave as before. |
| REQ-007 | C-005 | The README must explain the providers, their model requirements and MCP search. |

REQ-008 (search fallback) also belongs to this module but has no design yet; it is not covered by this ADR.

## 2. Context

Baseline (line numbers at commit `daf6947`):

- `configuration.py` L11-17, L78-93: `search_api` is `anthropic`, `openai`, `tavily` or `none`. Nothing checks that native search matches the research model; the UI only shows a note.
- `configuration.py` L236-247: `from_runnable_config` reads the environment variable (`SEARCH_API`) first and `configurable` second. An unknown value already fails Pydantic validation, but with a raw Pydantic message, and only when a node first builds the configuration.
- `deep_researcher.py` L101 and L154: the first model calls happen in `clarify_with_user` and `write_research_brief`, long before the researcher assembles its tools (L384).
- `deep_researcher.py` L384-389: the "no tools" guard never fires, because `get_all_tools` always adds `ResearchComplete` and `think_tool` (`utils.py` L579). With `search_api=none` and no MCP, research runs without any search.

## 3. Decision

Use EVAL-006 option B: one pure validator in `src/open_deep_research/search/validation.py`, called at the start of two nodes. No configuration flag: valid configurations are not affected.

`load_search_config(config: RunnableConfig) -> Configuration` builds the configuration with `Configuration.from_runnable_config` and then applies the rules below. It raises `SearchConfigError` (a `ValueError`) whose message names the setting to change.

| Rule | Check | Error names |
|---|---|---|
| Supported provider (C-003) | Building the configuration fails on `search_api` | `search_api` / `SEARCH_API` and the supported values `anthropic, openai, tavily, none` (lower-case) |
| Native search matches the model (C-001) | `search_api` is `openai` or `anthropic` and the provider prefix of `research_model` (the text before `:`) is different or missing | `search_api` and `research_model` |
| Some search source exists (C-002) | `search_api` is `none` and `mcp_config` is missing, has no `url` or has no `tools` | `search_api` and `mcp_config` |
| Task contract needs tool results (REQ-001) | `task_contract_enabled` is on and `search_api` is `openai` or `anthropic` | `task_contract_enabled` and `search_api` (ADR-001 §3.2) |

Native search needs an explicit provider prefix, for example `openai:gpt-4.1`. A model name without a prefix is rejected for native search, because guessing the provider would copy LangChain's inference rules into this module.

Call sites:

- `clarify_with_user`, as its first statement, before the `allow_clarification` check. This covers every normal run.
- `researcher`, as its first statement, because the researcher subgraph is compiled and can be invoked directly.

The validator only reads configuration values. It does not load MCP tools, call a model or use the network. Whether a declared MCP server is reachable at runtime is not checked (RISK-009). The dead `len(tools) == 0` guard stays as it is.

The README's search section explains: that the researcher model decides when to search; how to select each built-in provider and which `research_model` prefix the native providers need; which keys are needed; and how to add a custom or self-hosted search server through `mcp_config`.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — checks written inside `clarify_with_user` | Logic in a graph node, no reusable interface, and the researcher subgraph entry would need a copy. |
| C — checks inside `utils.get_all_tools` | Runs only in `researcher`, after the model calls at L101 and L154, so C-001 fails. |
| Environment snapshots, an MCP load adapter and a configured/bound/executed state model (an earlier draft) | Not needed for C-001 to C-005; runtime MCP failure is outside REQ-007. |

The full comparison is in EVAL-006.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `search/validation.py` | Build and validate the configuration | `load_search_config(config: RunnableConfig) -> Configuration`; `validate_search_config(configurable: Configuration) -> None`; `class SearchConfigError(ValueError)` | `clarify_with_user`, `researcher` |
| `README.md` | Search set-up guide | — | readers (C-005) |

No shared contract is added.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none.
- **Runtime policies:** POL-018.
- **Invariants:** INV-005.
- **Deterministic boundary:** whether a configuration is valid is decided by code from configuration values.

## 7. Verification

Cases in `verification-constraints.md` §7 (search). They build configurations in memory, use a fake model that fails the test if it is called, and need no network. C-005 is a human review recorded in `docs/review-memo.md`.

## 8. Consequences

- **Positive:** invalid set-ups fail at start with a clear message instead of in the middle of research.
- **Negative:** a bare model name such as `gpt-4.1` is rejected for native OpenAI search; the error message and the README say to add the prefix.
- **Neutral:** valid configurations, tool assembly and the graph are unchanged.

## 9. Implementation Steps

1. Add `search/__init__.py` and `search/validation.py`; add `open_deep_research.search` to `[tool.setuptools] packages`. Docstrings name `REQ-007, ADR-006, INV-005`.
2. Call `load_search_config(config)` first in `clarify_with_user` and in `researcher`, and use the returned configuration in those nodes.
3. Update the search section of `README.md` (C-005).
4. Run the checks in `verification-constraints.md` §4 and record them in `docs/build-reports/REQ-007.md`.
