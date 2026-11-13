# ADR-001: Validate Search Configuration with a Pure Validator Before Research

- **Status:** Proposed
- **Date:** 2026-11-13
- **Module:** search
- **Owner:** sszfot
- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)
- **SA Review:** pending (no `SA-NNN` recorded)

> This decision is *Proposed*. It is not approved until SA Review accepts it (`Prompt.md` §4, Gate 1). Everything below describes intended behaviour; none of it is implemented yet.

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-007 | C-001, C-002, C-003, C-004, C-005 | The decision must reject invalid search configurations *before any model or search call*, which fixes where validation runs in the graph and whether it may use a model or network. |
| REQ-007 | ASR-007-01 to ASR-007-08 (below) | These sub-drivers fix purity, module boundary, provider/model rules, MCP static-vs-runtime split and documentation consistency. |

Architectural drivers (ASR), provisional IDs used consistently across EVAL-001, this ADR and the module sections:

| ID | Statement |
|---|---|
| ASR-007-01 | Every entry path into the research chain validates search configuration before the first model or search call. |
| ASR-007-02 | Native providers (`anthropic`, `openai`) require a `research_model` of the same provider; other providers impose no model constraint; only `research_model` is in scope. |
| ASR-007-03 | A configuration is search-capable iff it names a built-in provider that yields a search tool, or names an MCP server with a well-formed URL and at least one declared tool (static declaration). |
| ASR-007-04 | Unsupported `search_api` values are rejected with an error listing the supported set. |
| ASR-007-05 | Validation is pure and offline-testable: no model calls, no network, no MCP connection. |
| ASR-007-06 | Valid existing configurations and the graph topology behave exactly as before. |
| ASR-007-07 | Documentation and validation messages are consistent: the README explains behaviour, providers, required models, credentials and MCP-as-search; errors name the setting and supported values. |
| ASR-007-08 | An unreachable MCP that was statically declared must not silently produce a no-search run. (Placement unresolved; see §12 U-1.) |

## 2. Context

Upstream issue #250 reports that it is unclear when the agent searches and how to use another or a self-hosted search provider. The baseline behaviour being changed:

- `SearchAPI` enumerates `anthropic`, `openai`, `tavily`, `none`, and nothing in `Configuration` validates provider/model pairing (`src/open_deep_research/configuration.py:11-17,78-93,153-162`). The only guard is a UI note, "Make sure your Researcher Model supports the selected search API" (`configuration.py:84,159`).
- `get_search_tool` returns native search *definitions* for `anthropic`/`openai`, the `tavily_search` tool for `tavily`, and `[]` for `none`; an unknown value falls through silently to `[]` (`src/open_deep_research/utils.py:531-567`). `SearchAPI(...)` on an unsupported string raises a bare enum `ValueError` (`utils.py:583,881-890`).
- `load_mcp_tools` returns `[]` for any invalid MCP configuration and swallows connection errors (`utils.py:470-481,499-504`), so a broken MCP search degrades silently to "no search".
- The researcher's empty-tool guard is dead code: `get_all_tools` always includes `ResearchComplete` and `think_tool`, so `len(tools) == 0` is never true (`deep_researcher.py:384-389` vs `utils.py:579`).
- The README search section only points to `search_api` and `mcp_config` (`README.md:77`).

Entry paths that can reach a model or search call (from `deep_researcher.py` wiring at lines 353-363, 589-605, 701-716):

| Path | Entry | First model call |
|---|---|---|
| P1 | `deep_researcher` `START → clarify_with_user` | `clarify_with_user`, L101 (only when `allow_clarification=True`) |
| P2 | `clarify_with_user → write_research_brief` | L154 |
| P3 | `write_research_brief → research_supervisor` | `supervisor`, L214 |
| P4 | `supervisor_tools → researcher_subgraph.ainvoke` | `researcher`, L415 |
| P5 | `researcher` (researcher subgraph `START`, L601) | L415 |
| P6 | `researcher_tools` | none (tool execution only) |
| P7 | `supervisor` (supervisor subgraph `START`, L360) | L214 |

Because `clarify_with_user` and `write_research_brief` already call the research model, validation inside tool assembly would run *after* those calls on the standard path — the exact late failure #250 reports.

## 3. Decision

Use a **pure, centralized search configuration validator** in the `search` module, invoked at the beginning of `clarify_with_user` and of `researcher`, before any model or search call. Do not change the graph topology, tool assembly, state or configuration fields. Constrain only `research_model` against native providers. Treat a statically declared MCP capability as distinct from runtime MCP availability. Reject `search_api=none` when no valid MCP tool declaration exists. Keep REQ-008 fallback out of scope. Record runtime MCP loading failure as an open decision (§12 U-1); implement no runtime guard now. Do not treat the dead `len(tools) == 0` check as proof that search capability exists.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A. Validation directly inside the research graph entry point | Violates the thin-node rule (`structural-constraints.md` §2.1); correctness depends on placing the call before the `allow_clarification` early return; no reusable, unit-testable interface; duplicates MCP capability logic. |
| C. Validation layer integrated with existing search tool assembly (`utils.get_all_tools`) | Runs only inside `researcher` (`deep_researcher.py:384,467`), i.e. after the L101 and L154 model calls on the standard path, so it fails C-001's "before any model or search call"; grows an already overloaded `utils.py`; conflates validation with REQ-008 fallback and repeats the shape of the unmerged `fix/issue-250` branch. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `search/configuration_validator.py` (new) | Statically validate search configuration and classify MCP capability; raise a domain error naming the offending setting(s) and supported values. No I/O, no model, no tool objects. | `validate_search_configuration(configurable: Configuration) -> None` (raises `SearchConfigurationError`); `classify_mcp(mcp: MCPConfig \| None) -> MCPStatus`; `model_provider(model: str) -> str` | `clarify_with_user`, `researcher` |
| `clarify_with_user` (existing node) | Call the validator as its first statement, before the `allow_clarification` early return and any model call. Stays thin. | unchanged (`deep_researcher.py:60`) | graph `START` |
| `researcher` (existing node) | Call the validator as its first statement, before `get_all_tools`. Stays thin. The existing `len(tools) == 0` guard is not relied on as proof of search capability; its disposition (keep or replace) is unresolved (U-4) and this ADR neither approves nor requires a change to it. | unchanged (`deep_researcher.py:365`) | researcher subgraph `START` |
| `utils.get_all_tools` / `get_search_tool` / `load_mcp_tools` | Unchanged by this design. | as-is | `researcher`, `researcher_tools` |
| `README.md` | Document behaviour, providers, required models, credentials and the MCP search recipe (C-005). | — | human readers |

Shared contracts changed (`structural-constraints.md` §6): **none**. No state field and no `Configuration` field is added; the validator reads existing fields only.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none (no field added or changed; `memory-design.md` needs no section).
- **Runtime policies:** none approved. A deferred, not-approved runtime-policy entry records the open MCP-load-failure question (§12 U-1; `runtime-policy-catalog.md`).
- **Invariants:** INV-005 (Proposed).
- **Deterministic boundary:** search-configuration validity is decided by deterministic code; no model decides it. REQ-007 is `safety_relevant: false`, but the validator is model-free.

## 7. Configuration Validation Rules

The validator reads only `Configuration`/`MCPConfig`. Canonical provider set is the `SearchAPI` enum: `anthropic`, `openai`, `tavily`, `none`.

| `search_api` | Rule | On violation |
|---|---|---|
| `anthropic` | `research_model` provider prefix must be `anthropic:`. | Raise, naming both `search_api=anthropic` and `research_model=<value>` (C-001). |
| `openai` | `research_model` provider prefix must be `openai:`. | Raise, naming both settings (C-001). |
| `tavily` | No model constraint; accepted with any `research_model` (C-004). Credential absence is a runtime condition, not a configuration error; do not reject on it. | Accept. |
| `none` | Accepted only if the MCP configuration is a valid *declaring* config (see §8). | Raise, naming `search_api=none` and `mcp_config` (C-002). |
| unsupported value (any string outside the enum, `None`, empty, non-string) | Reject after normalising the value, independently of the bare enum `ValueError`. | Raise, listing the supported values `anthropic, openai, tavily, none` (C-003). |

Provider prefix extraction: `model.split(":", 1)[0].strip().lower()`. A model string without `:` is treated as its own provider token, so `gpt-4.1` does not match `openai:`. Alias handling (e.g. `openai_chat:`) is unresolved (§12 U-3).

## 8. MCP Configuration Versus Runtime Availability

The validator classifies MCP configuration into exactly one of:

| Class | Condition | Counts as search capability (C-002)? |
|---|---|---|
| `MCP_ABSENT` | `mcp_config is None` | No |
| `MCP_INVALID_DECLARATION` | `mcp_config` present but `url` missing/empty or `tools` missing/empty | No |
| `MCP_DECLARED` | `url` present and `tools` non-empty; `auth_required` recorded | Yes (statically) |

- **Configuration validity** is what the validator decides: are the fields well-formed and self-consistent?
- **Runtime availability** is whether the server is reachable, the named tools exist and authentication succeeds. The validator does **not** decide this and never calls `MultiServerMCPClient`.
- Therefore `search_api=none` with `MCP_DECLARED` is accepted at start-up; it is not proof that the MCP search works. Failure to load a declared MCP at runtime is the open decision U-1.

## 9. Integration Points and Dependency Direction

- Dependency direction follows `structural-constraints.md` §5: `deep_researcher.py → search/ → configuration.py`. The `search` module must not import `deep_researcher.py`, `utils.py`, any model client or the MCP client.
- Two call sites: first statement of `clarify_with_user` and first statement of `researcher`.
- No change to `get_all_tools`, `get_search_tool`, `load_mcp_tools`, `state.py`, the graphs or `Configuration` fields.
- The new subpackage is added to `[tool.setuptools] packages` in `pyproject.toml` in the implementation PR (`structural-constraints.md` §1), or a non-editable install omits it. This is a Coding-Agent step, not part of this documentation change.
- Blueprint §6 already records the exception `utils.py → search/` for `get_all_tools()`; this ADR does not require it, because the validator is called from the graph, not from `utils.py`.

## 10. Implementation Steps

Ordered steps for a future Coding Agent (none performed here):

1. Create `src/open_deep_research/search/__init__.py` and `search/configuration_validator.py` with `validate_search_configuration`, `classify_mcp` and `model_provider`; docstring names `REQ-007, ADR-001, INV-005`.
2. Add the package to `[tool.setuptools] packages` in `pyproject.toml`.
3. Call `validate_search_configuration(Configuration.from_runnable_config(config))` as the first statement of `clarify_with_user`, before the `allow_clarification` check.
4. Add the same guard as the first statement of `researcher`, before `get_all_tools`. Do **not** rely on the existing `len(tools) == 0` guard; leave it unchanged in this step. Any replacement of that guard is gated on the U-4 decision (§12) and is not part of this ADR's approved scope.
5. Update `README.md`'s search section with the provider matrix and MCP recipe (C-005).
6. Add the module sections referenced in `structural-constraints.md` §10, `verification-constraints.md` §7, `invariants.md` and `trace-matrix.md`.
7. Verify per §11; record evidence in `docs/test-reports/REQ-007.md`.

## 11. Verification

| Check | Type | Test or evidence |
|---|---|---|
| C-001 | offline | `test/offline/test_search_configuration.py::test_native_search_model_mismatch_rejected` — error names both settings |
| C-002 | offline | `::test_no_search_tool_rejected` — `none`+no MCP rejected; `none`+`MCP_DECLARED` accepted; `none`+`MCP_INVALID_DECLARATION` rejected |
| C-003 | offline | `::test_unsupported_provider_rejected` — error lists `anthropic, openai, tavily, none` |
| C-004 | offline | `::test_valid_tavily_configuration_accepted` — no error; `web_search` present in assembled tools |
| C-005 | human review | `docs/review-memo.md` (search provider configuration review), `automated: false` |
| INV-005 | offline | `test_search_configuration.py` (unknown provider rejected) |
| Regression | offline | `uv run pytest test/offline`; existing suites still pass |

The cases are listed in the `search` module section of `verification-constraints.md` §7. Offline tests use fake models, make no network calls and need no API keys.

## 12. Consequences, Risks, Assumptions, Unresolved Decisions and Rollback

- **Positive:** invalid configurations rejected before the first model/search call; single-responsibility, offline-testable module; matches the `search/` module boundary and dependency direction; no topology change.
- **Negative / neutral:** two call sites to keep in step; a new import in two nodes; no runtime guarantee that a declared MCP search is reachable.
- **Risks:** false rejection of a valid configuration (mitigated by the tested provider rules and by treating Tavily credentials as runtime); divergence between the README and the validator (mitigated by C-005 review).

Unresolved decisions (for team review; none decided here):

- **U-1** Runtime handling when `mcp_config` is `MCP_DECLARED` but loading yields zero tools: currently silent. Whether REQ-007 must raise an explicit no-search error here, or the failure-handling module (REQ-002/REQ-004) owns it, is deferred. No runtime guard is implemented.
- **U-2** INV-005 says "unknown provider is rejected at start-up"; configuration is per-run via `from_runnable_config`, so validation is node-level. Confirm wording or reword INV-005.
- **U-3** Provider-prefix strictness: whether aliases such as `openai_chat:` count as `openai`. Current rule is strict prefix match.
- **U-4** Disposition of the dead `len(tools) == 0` guard (`deep_researcher.py:385-389`): keep untouched or replace with a validator-driven capability check. Recommended: replace; deferred to approval.

- **Rollback:** remove the two call sites and the `search` module; nothing in the baseline depends on the validator, so removal restores the pre-change behaviour.

## 13. Modules and Documents to Update at Integration

`evaluation-table.md` (EVAL-001), `trace-matrix.md` (REQ-007 row), `invariants.md` (INV-005), `structural-constraints.md` §10, `verification-constraints.md` §7, `runtime-policy-catalog.md` (deferred entry). `memory-design.md` does not change (no state).
