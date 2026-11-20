# ADR-008: Ordered search fallback inside the search module

- **Status:** Accepted
- **Date:** 2026-11-18
- **Module:** search
- **Owner:** sszfot
- **Evaluation:** EVAL-008 (`docs/architecture/evaluation-table.md`)
- **SA Review:** passed in the SA integration PR [#22](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/22) (approved by BroZhai and DopplerXD, merged 2026-11-18)
- **History:** proposed in PR #20 as ADR-002; renumbered and narrowed at integration (blueprint §11, decision 7)

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-008 | C-001, C-002 | Fallback must follow a configured order, so the order is a configuration value and the loop lives in one place. |
| REQ-008 | C-003 | When every source fails, the researcher must get an explicit failure that lists each source and cannot be mistaken for an empty result. |
| REQ-008 | C-004, C-005 | An empty result and an ineligible error must not trigger fallback, so errors must be classified by type before `execute_tool_safely` turns them into text. |
| REQ-007 (dependency) | ADR-006 | Fallback sources are checked with the rest of the search configuration before the run starts. |

## 2. Context

Baseline (line numbers at commit `daf6947`):

- `utils.py` L138-173: `tavily_search_async` lets Tavily errors through. The client raises typed errors (`tavily.errors`: `TimeoutError`, `UsageLimitExceededError`, `InvalidAPIKeyError`, `ForbiddenError`, `BadRequestError`, `MissingAPIKeyError`); other HTTP errors come from `httpx` (`raise_for_status()`), and connection errors are `httpx` transport errors.
- `deep_researcher.py` L427-432: `execute_tool_safely` catches every exception and returns `"Error executing tool: ..."`; the researcher sees only that text, and no other source is tried.
- `deep_researcher.py` L467-471: `researcher_tools` reloads the tools and looks them up by name; a fallback must keep each tool's name and argument schema.
- `utils.py` L125-127: an empty Tavily search returns the success text `"No valid search results found..."`.
- `utils.py` L43-49: the Tavily tool takes `queries: list[str]`; MCP tools have their own schemas.
- Only Tavily and MCP tools run on the client. Native OpenAI and Anthropic search run inside the model call and cannot be a fallback (REQ-008 out of scope).

## 3. Decision

Use EVAL-008 option B: `src/open_deep_research/search/fallback.py` wraps the search tools so that a failed call tries the configured fallback sources in order. No graph, state or node logic changes.

### 3.1 Configuration

`Configuration.search_fallback: list[str] = []`. Each entry is `"tavily"` or the name of an MCP tool listed in `mcp_config.tools`, in the order to try. An empty list means no fallback and the baseline behaviour. When the value comes from the environment variable `SEARCH_FALLBACK`, it is comma-separated text, which a `Configuration` validator splits into the list. ADR-006's validator rejects any other entry (for example a native provider) before the run starts.

### 3.2 Which calls fall back

`apply_search_fallback(tools, configurable) -> list` returns the tool list with the search tools wrapped; the name, description and argument schema of each wrapped tool stay the same, so the model and the name lookup in `researcher_tools` see no difference. Each wrapper is a new `StructuredTool` whose coroutine takes `config: RunnableConfig` and calls every source with `source.ainvoke(args, config)`, so API keys from the run configuration still reach Tavily. The original tool objects are never modified; the Tavily tool is a shared module-level object. When `search_fallback` is empty, the function returns the tools unchanged. Otherwise a tool is wrapped when it is the Tavily tool (`tavily_search`) or an MCP tool named in `search_fallback`, and at least one other source is listed. Other tools, including MCP tools that are not in the list, are never wrapped and never fall back.

When the model calls a wrapped tool, the sources are tried in this order: the called tool first, then every `search_fallback` entry except the called tool, in list order. Tavily is a fallback source only when `"tavily"` is in the list. Each source is used at most once per call; an MCP source used with several queries receives one call per query (§3.3).

### 3.3 Passing the query between sources

- From Tavily: the call's `queries` list.
- From an MCP tool: the value of its single required string argument, as a one-item list.
- To Tavily: `queries` (with its default `max_results` and `topic`).
- To an MCP tool: one call per query with its single required string argument; the outputs are joined in query order. The text of an MCP output is its content when it is a string, otherwise the `text` parts of its content blocks joined.

An MCP fallback source must therefore have exactly one required string argument. A listed MCP tool that did not load, or has a different shape, is recorded as `not available` when its turn comes and the next source is tried. It never stops the run on its own: the run stops only when no search tool exists at all (ADR-006 §3.3, Discussion #19 U-1).

### 3.4 Outcomes

`classify_search_error(exc) -> tuple[bool, str]` decides from exception types, MCP error codes and HTTP status codes only. It looks at the exception, then follows `__cause__` and the members of an exception group until one matches:

| Category | Eligible | Signals |
|---|---|---|
| `timeout` | yes | `tavily.errors.TimeoutError`, `httpx.TimeoutException`, `asyncio.TimeoutError`; `McpError` with code 408 (the MCP client's request timeout) |
| `connection` | yes | other `httpx.TransportError`; `McpError` with code -32000 (`CONNECTION_CLOSED`) |
| `rate_limit` | yes | `UsageLimitExceededError`; `httpx.HTTPStatusError` with status 429 |
| `server_error` | yes | `httpx.HTTPStatusError` with status 5xx |
| `credential_rejected` | yes | `InvalidAPIKeyError`, `ForbiddenError`; `httpx.HTTPStatusError` with status 401 or 403 |
| `malformed` | no | `BadRequestError`; `httpx.HTTPStatusError` with status 400 |
| `missing_credential` | no | `MissingAPIKeyError` (a configuration error) |
| `other` | no | anything else, including an MCP tool's own error result (`ToolException`); message text is never parsed |

| Situation | Result |
|---|---|
| A source returns, with or without hits | That result, unchanged, whichever source returned it (C-001, C-004) |
| A source fails with an eligible error | Record the attempt; try the next source (C-001, C-002) |
| The called tool fails with an ineligible error | Re-raise the original error; no further source is tried (C-005). `execute_tool_safely` turns it into `"Error executing tool: ..."` as today |
| A later (fallback) source fails with an ineligible error | Record the attempt and try the next source, so the earlier attempts are not lost; for example a fallback Tavily without a key |
| Every source failed or was not available | Raise `AllSourcesFailedError`, whose message starts `All search sources failed:` and lists each source with its category and error text (C-003). It never equals the empty-result text |

The wrapper only raises; turning errors into text stays in `execute_tool_safely`, so `researcher_tools` only gains the call to `apply_search_fallback`. With `task_contract_enabled`, one model call counts as one tool call against the task budget however many sources are tried, and the URLs of the source that answered reach `retrieved_urls` through its tool message (ADR-001 §3.2).

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — a fallback loop in `researcher_tools` / `execute_tool_safely` | Logic in a graph node, and by then the exception has already become text. |
| C — fallback inside `utils.tavily_search` | Covers only Tavily as the primary source and puts search policy into the shared `utils.py`. |
| The first draft (PR #20): a normalised `SearchRequest`, one adapter per source behind a `SearchSource` protocol, three result types and a structured MCP load result with load and invoke stages | The load result depends on REQ-007 U-5, which the team did not adopt (ADR-006 rejects the MCP load adapter); the adapter layer gives no rule for calling an MCP tool with an arbitrary schema. The rule in §3.3 and one `not available` entry cover C-001 to C-005 with one file. |

The full comparison is in EVAL-008.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `search/fallback.py` | Wrap search tools; try sources in order; classify errors; build the all-failed error | `apply_search_fallback(tools: list, configurable: Configuration) -> list`; `classify_search_error(exc: BaseException) -> tuple[bool, str]`; `class AllSourcesFailedError(RuntimeError)` with `attempts: list[tuple[str, str, str]]` (source, category, error text) | `researcher_tools` |
| `search/validation.py` | Check `search_fallback` entries before the run (rule added to ADR-006 §3.1) | existing `validate_search_config` | `clarify_with_user`, `researcher` |
| `configuration.py` | Ordered fallback list | `search_fallback: list[str] = []` with `x_oap_ui_config` metadata | all nodes |

`fallback.py` may import `utils.tavily_search` to call Tavily when it is only a fallback source; this follows the normal direction (extension module → shared module). Shared contract added: the `search_fallback` configuration field.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none.
- **Runtime policies:** POL-024.
- **Invariants:** INV-010.
- **Deterministic boundary:** whether to try another source, in which order, and what the researcher receives are decided by code from exception types and the configuration.

## 7. Verification

Cases in `verification-constraints.md` §7 (search, TC-SRC-11 to TC-SRC-17). They use fake Tavily and MCP tools that return, return nothing, or raise chosen errors, and need no network.

## 8. Consequences

- **Positive:** an eligible failure no longer loses the search; the researcher gets either a result or an explicit list of what failed; an empty list keeps the baseline.
- **Negative:** MCP tools that raise untyped errors are classified `other` and do not fall back (RISK-014); a fallback call can take longer, because sources are tried one after another.
- **Neutral:** native search is never a fallback; the graph and the state are unchanged; `researcher_tools` gains one call and keeps its error handling. Passing the assembled tools through `apply_search_fallback` in `researcher_tools` is a recorded exception to `structural-constraints.md` §3 (blueprint §6).

## 9. Implementation Steps

1. `configuration.py`: add `search_fallback: list[str] = []` with `x_oap_ui_config` metadata.
2. `search/validation.py`: add the `search_fallback` rule of ADR-006 §3.1.
3. Add `search/fallback.py` with the interface of §5. Docstrings name `REQ-008, ADR-008, INV-010`.
4. `researcher_tools`: call `apply_search_fallback(tools, configurable)` on the assembled tools before building the name lookup.
5. README search section: how to configure `search_fallback`, which errors fall back, and the shape an MCP fallback tool needs.
6. Run the checks in `verification-constraints.md` §4 and record them in `docs/build-reports/REQ-008.md`.
