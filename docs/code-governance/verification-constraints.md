# Verification Constraints

> **Purpose:** One shared way to decide that a requirement is really done.
> **Authoritative for:** verification layers, test conventions, commands, CI gates, verdicts and evidence, module test requirements and the Definition of Done.
> **Maintained by:** humans for §1–§6 and §8; each module owner writes their module's test requirements in §7, integrated before SA Review.
> **Last updated:** 2026-11-12

## 1. Three Verification Layers

| Layer | Meaning | Where it runs |
|---|---|---|
| **Structural** | Code organisation, schemas, module boundaries, docstring RIDs and lint conform to the rules | CI: schema and static-analysis gates |
| **Regression** | Existing behaviour and shared contracts still hold | CI: every suite in `test/offline/` |
| **Behavioural** | The requirement's behaviour meets its fit criterion | New offline tests; `test/live/` or `test/run_evaluate.py` when a case needs a real model; human confirmation |

## 2. Principles

1. Every fit-criterion check and metric in `requirements.yaml` has at least one test or a named piece of review evidence; its `verification` field points to it.
2. Every invariant has a test that fails when the invariant is violated.
3. A change runs its new tests and every prior offline suite; any regression blocks the merge.
4. Module test requirements (§7) are approved in SA Review (Gate 1) before tests are written, and the tests are approved before implementation (Gate 2). Tests are written by Test Author and never changed by Build.
5. Prefer deterministic offline tests; use live tests for final behavioural evidence only.

## 3. Test Conventions

- **Offline tests** (`test/offline/`) use fake models and fake researchers, make no network calls and need no API keys, so supervisor logic, termination, scheduling and context handling run in CI at no token cost.
- **Live tests** (`test/live/`) call real models or APIs, run on demand rather than on every commit, and are marked `automated: false` in `requirements.yaml` when a human must judge the result.
- **Names:** test files are named after the behaviour they cover, `test_<topic>.py` (for example `test_failure_propagation.py`); test functions describe the expected behaviour. Requirement IDs are not part of file names, so renumbering requirements does not rename tests.
- **Traceability:** the first line of every test module's docstring lists the RIDs it verifies, for example `"""REQ-002: no delegated task is lost or silently treated as completed."""`. The requirement's `verification` field gives the exact `path::test_name`.
- **Shared contract tests:** when a requirement defines a shared contract (`structural-constraints.md` §6), its contract tests live in `test/offline/test_contracts.py` and every PR runs them.

## 4. Commands

| Check | Command |
|---|---|
| Requirements schema and ID consistency | `uv run python scripts/validate_requirements.py` |
| Lint (gated paths) | `uv run ruff check src/open_deep_research test/offline scripts` |
| Type check (optional, not gated) | `uv run mypy src/open_deep_research` |
| Offline tests | `uv run pytest test/offline` |
| Live and evaluation tests | `uv run pytest test/live`, `uv run python test/run_evaluate.py` |

`ruff format` is applied to new files and changed lines only; do not reformat untouched baseline code. Install tools with `uv sync --extra dev`.

## 5. CI Gates

The course requires six blocking gates. Their state in `.github/workflows/ci.yml`:

| Course gate | CI job | What it checks | Status |
|---|---|---|---|
| Schema | `requirements-schema` | `requirements.yaml` against `req-schema.json`, plus unique and resolvable IDs | Active |
| Static analysis | `static-analysis` | `ruff check` on the gated paths | Active; mypy planned |
| Regression | `offline-tests` | `pytest test/offline` | Active; reports `NOT_RUN` while the directory has no tests |
| Test approval | — | The approval record has Gate 2 for every PR that changes `src/`, and the PR's tests match the approved test commit | Planned |
| AI-use log | — | `docs/ai-use-log.yaml` is valid and has an entry for the PR | Planned |
| Semantic evaluation | — | Live evaluation of fit criteria for prompt or model changes | Planned |

Lint debt outside the gated paths is tracked in `docs/debt-register.md`; a path joins the static-analysis gate once it is clean.

## 6. Verdicts and Evidence

- Verdicts are only `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED` and `N/A`. A skipped test is `NOT_RUN`, never `PASS`.
- No check is reported as passed without execution evidence. A mandatory check that is `FAIL`, `NOT_RUN` or `BLOCKED` keeps the requirement from `verified`.
- Evidence goes to `docs/test-reports/<task-id>.md`: the baseline run by Test Author and the verification by Verify, each with commit, commands, verdict per check, and logs or diffs where relevant.
- Offline tests run without network or secrets (§3). Verify changes no file other than its report; the PR diff shows any change made during verification.

## 7. Module Test Requirements

Copy the example for your module. Every acceptance criterion (C-/M-) of the module's requirements and every invariant it enforces needs at least one case, and the module lists the existing suites it can affect. At integration, check that no criterion or invariant is left without a case.

### <Module> (REQ-NNN, ADR-NNN)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-001 | REQ-NNN C-NNN | normal | | | `test/offline/<file>::<test>` |
| TC-002 | INV-NNN | exception | | | |
| TC-003 | REQ-NNN M-NNN | boundary | | | |

- **Regression:** existing suites to re-run, including `test/offline/test_contracts.py` if a shared contract changes.
- **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.

### search (REQ-007, ADR-001)

The proposed behaviours are described in ADR-001 §2.1, §7, §8 and §9. Test IDs preserve the requirement's existing `verification` names (C-003, C-004, C-002) and add new IDs without colliding with other modules.

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-001 | C-001 | exception | `search_api=anthropic`, `research_model=openai:gpt-4.1` | Error names both `search_api` and `research_model`; raised before any model or search call | `test/offline/test_search_configuration.py::test_native_search_model_mismatch_rejected` |
| TC-002 | C-001 | normal | `anthropic` + `anthropic:claude-sonnet-4`; `openai` + `openai:gpt-4.1` | No error; native definition bound | `::test_native_provider_valid_combinations_accepted` |
| TC-003 | C-001, U-3 | normal/boundary | `openai` + bare `gpt-4.1` and `anthropic` + `anthropic.claude-3` under each resolution policy (strict vs LangChain-compatible) | Outcome matches the U-3 policy chosen; documents the `gpt-4.1` and `anthropic.claude-3` behaviour | `::test_provider_resolution_policy` |
| TC-004 | C-002 | boundary | `search_api=none`: (a) no MCP, (b) `MCP_DECLARED`, (c) malformed (url set, `tools=[]`), (d) url missing | (a)/(c)/(d) rejected naming `search_api`/`mcp_config`; (b) statically accepted | `::test_no_search_tool_rejected` |
| TC-005 | C-003 | exception | `search_api="bing"` | Rejected listing `anthropic, openai, tavily, none`; zero model calls | `::test_unsupported_provider_rejected` |
| TC-006 | C-003 | exception | `search_api=""` | Rejected, lists supported set | `::test_empty_provider_rejected` |
| TC-007 | C-003 | exception | `search_api="TAVILY"` (uppercase) | Rejected, not normalised to `tavily` | `::test_uppercase_provider_rejected` |
| TC-008 | C-003, ASR-007-04 | exception | `SEARCH_API=bing` with a valid `configurable.search_api` | Rejected because the env var takes precedence | `::test_env_provider_precedence_rejected` |
| TC-009 | D1 | normal | `search_api` omitted | Resolves `tavily`, no error | `::test_omitted_provider_defaults_tavily` |
| TC-010 | D1 | normal | `search_api=None` | Resolves `tavily` (treated as unset), no error | `::test_none_provider_defaults_tavily` |
| TC-011 | C-004 | normal | `search_api=tavily` with any `research_model` (`openai:gpt-4.1`) | No error; the `tavily_search` tool object is present (`tool.name == "tavily_search"`) and its `metadata["name"] == "web_search"`; the two are asserted distinctly | `::test_valid_tavily_configuration_accepted` |
| TC-012 | ASR-007-01 | exception | Invalid config, `allow_clarification=True` | Fake research model records **zero** calls; error before the clarification model call | `::test_invalid_config_zero_model_calls_clarify_true` |
| TC-013 | ASR-007-01 | exception | Invalid config, `allow_clarification=False` | Fake research model records **zero** calls; error before the brief model call | `::test_invalid_config_zero_model_calls_clarify_false` |
| TC-014 | C-002, §8.1 | boundary | `none` with malformed MCP: `url` missing | `MCP_INVALID_DECLARATION`; rejected | `::test_mcp_missing_url_rejected` |
| TC-015 | C-002, §8.1 | boundary | `none` with `auth_required=True` and no resolvable token | Statically `MCP_DECLARED`; the runtime adapter reports `AUTH_MISSING` (distinct from a load failure) — see TC-018 | `::test_mcp_auth_required_classified` |
| TC-016 | ASR-007-08, U-1, U-5 | exception | Declared MCP, `get_tools()` raises, `search_api=none` | Adapter status `LOAD_FAILED`: research stops with explicit error naming `mcp_config.url`; no fallback | `::test_mcp_connection_failure_stops` |
| TC-017 | ASR-007-08, U-1, U-5 | exception | Declared MCP, load succeeds but zero tools match declaration | Adapter status `ZERO_USABLE_TOOLS` (distinct from `LOAD_FAILED`): research stops with explicit error; no fallback | `::test_mcp_zero_usable_tools_stops` |
| TC-018 | ASR-007-08, U-5 | exception | Declared MCP, `auth_required=True`, no token at runtime | Adapter status `AUTH_MISSING` (distinct from `LOAD_FAILED` and `ZERO_USABLE_TOOLS`): research stops with explicit auth error | `::test_mcp_missing_auth_stops` |
| TC-019 | INV-005 | normal | Usable search tool returns no hits | Empty result is success; no error, no stop | `::test_empty_result_is_success` |
| TC-020 | U-4, ASR-007-09, §8.3 | normal | `has_search_capability(SearchEvidence)` for each provider: Anthropic native with `native_bound is True`, OpenAI native with `native_bound is True` (dict without `name`), Tavily (`tavily_search` present), MCP (`MCP_DECLARED` + `mcp_load_status=LOADED` + ≥1 tool), `none`+absent | True except `none`+absent; native uses `native_bound`, never a tool `name`; never keyed on `len(tools)` | `::test_search_capability_predicate` |
| TC-021 | C-004, ASR-007-06 | regression | No `search_api` set, `research_model=openai:gpt-4.1`, no new keys needed | Default Tavily tool assembly unchanged; no validation error | `::test_default_tavily_openai_regression` |
| TC-022 | INV-005 | normal/exception | Empty result vs failure vs unsupported provider | Empty = success; failure = failure; unsupported rejected | `::test_inv005_result_contract` |
| TC-023 | C-005 | human | README provider matrix and MCP recipe | Reviewer configures each provider and an MCP search server from the docs alone | `docs/review-memo.md` (`REVIEW-NNN`), `automated: false` |
| TC-024 | U-5, §8.1a | exception | MCP load fed each branch (Option A: adapter owns the load; Option B: refactored `load_mcp_tools`): missing `url`/`tools`, missing auth token, `get_tools()` raise, successful load with 0 matching tools, successful load with tools | Returns distinct `LOAD_FAILED` / `AUTH_MISSING` / `ZERO_USABLE_TOOLS` / `LOADED` (four states not collapsed to `[]`); a fake MCP client (`get_tools`) is used, no network | `::test_mcp_load_result_distinguishes_states` |
| TC-025 | U-3, §8.2 | normal/boundary | Native binding: fake model records definitions passed to `bind_tools`; "configured" (definition produced) vs "bound" (`native_bound`) vs "executed" (fake response with/without `anthropic_websearch_called`/`openai_websearch_called` metadata) | Predicate uses `native_bound` (available only after binding); execution availability is observed only post-response and does not gate capability; a successful bind is not treated as proof of remote execution | `::test_native_configured_bound_executed` |
| TC-026 | Correction B, §7.2, §8.0 | normal/exception | Env `SEARCH_API` set with a conflicting `configurable.search_api`; a resolver snapshot plus construction from validated effective inputs; a fake model recording call count | The constructed `Configuration` reflects the resolver's effective value (env precedence preserved), no `os.environ` mutation occurs, and the capability predicate is only evaluated after `bind_tools` (step 4). Zero model/search calls before validation | `::test_config_resolution_snapshot_and_order` |

- **Regression:** `uv run pytest test/offline`; no shared contract changes, so `test/offline/test_contracts.py` is unaffected. TC-021 is the default-configuration regression.
- **Live or human checks:** C-005 (TC-023) is human review recorded as `REVIEW-NNN` in `docs/review-memo.md`. TC-016–TC-018 and TC-024 depend on the U-1/U-5 decisions; until approved they are planned, not binding. TC-003 and TC-025 depend on the U-3 decision. TC-026 covers the configuration-resolution boundary (Correction B) and the §8.0 ordering; it is binding regardless of U-5, but its construction step depends on the §7.2 implementation choice (Option 1 needs no factory change; Option 2 needs the additive `environ` parameter).

## 8. Definition of Done

| # | Condition | Done by |
|---|---|---|
| 1 | Every fit-criterion item has an approved test or recorded review, and the tests pass | Test Author (tests), Build (passing), confirmed by Verify |
| 2 | All prior offline suites pass | Verify |
| 3 | All active CI gates are green | CI |
| 4 | Behaviour conforms to the fit criterion, with evidence in `docs/test-reports/` | Verify, confirmed by a human |
| 5 | `trace-matrix.md` row complete for architecture, code and tests | Module owner |
| 6 | If a boundary changed: `invariants.md` updated and its test passes | Human, Test Author |
| 7 | If an architectural decision arose: ADR accepted or `evaluation-table.md` entry recorded | Human |
| 8 | `docs/ai-use-log.yaml` and `docs/review-memo.md` updated | Human |
| 9 | Gate 3 passed: two approvals, PR merged | Humans |
| 10 | `status` in `requirements.yaml` advanced to `verified` | Human |
