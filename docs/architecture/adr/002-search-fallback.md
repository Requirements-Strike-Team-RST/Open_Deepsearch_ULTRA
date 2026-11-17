# ADR-002: Ordered Search Fallback Through a Dedicated Coordinator

- **Status:** Proposed
- **Date:** 2026-11-17
- **Module:** search
- **Owner:** sszfot
- **Evaluation:** EVAL-002 (`docs/architecture/evaluation-table.md`)
- **SA Review:** pending (no `SA-NNN` recorded)

> This decision is *Proposed*. It is not approved until SA Review accepts it (`Prompt.md` §4, Gate 1). Nothing below is implemented. Decisions still open for the team are listed in §12. REQ-008 depends on REQ-007, which is itself still Proposed (ADR-001); this ADR does not assume ADR-001 has been approved.

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-008 | C-001, C-002, C-003, C-004, C-005 | Ordered fallback, eligible-vs-ineligible gating, empty-is-success and an explicit all-failed failure fix where the loop, the classification and the aggregation live, and what the researcher receives. |
| REQ-007 (dependency) | U-5 / structured MCP load result | Distinguishing a source that could not be loaded from one that returned nothing needs the structured load result; without it the load-stage outcome is unrecoverable. |

Architectural drivers (ASR), provisional IDs used consistently across EVAL-002, this ADR and the module section:

| ID | Statement |
|---|---|
| ASR-008-01 | The system tries a configured ordered list of Tavily/MCP sources, next source on eligible failure, until one succeeds (C-001, C-002). |
| ASR-008-02 | Eligible errors (timeout, connection failure, rate limit, provider server error, rejected credential) trigger fallback; ineligible errors return without fallback (C-001, C-002, C-005). |
| ASR-008-03 | A search that returns no hits is a success and does not trigger fallback (C-004). |
| ASR-008-04 | When every source fails, the researcher receives an explicit failure listing each attempted source and its error, not mistakable for an empty result (C-003). |
| ASR-008-05 | A successful result is used identically regardless of which source produced it (statement). |
| ASR-008-06 | Fallback operates only on client-side sources (Tavily/MCP); native OpenAI/Anthropic search is never a fallback substitute (out of scope). |
| ASR-008-07 | Error classification is deterministic and offline-testable with fake sources and injected errors. |
| ASR-008-08 | With no fallback configured, behaviour is unchanged (today's single-source error path). |
| ASR-008-09 | REQ-008 explicitly depends on REQ-007 (especially U-5, the structured MCP load result); that dependency must be tracked, and unapproved REQ-007 decisions must not be treated as implemented guarantees. |
| ASR-008-10 | A configured-but-unloadable MCP source is represented deterministically (a distinct load-stage diagnostic), not silently dropped. |
| ASR-008-11 | The fallback path is exposed as one stable model-callable search tool, so `tools_by_name` dispatch keeps working. |

## 2. Context

REQ-008 is `approved`; the architecture is Proposed. Baseline behaviour:

- A failed client-side search is never retried with another source. A Tavily exception (`utils.py:138-173`) reaches `execute_tool_safely` (`deep_researcher.py:427-432`), which catches every exception and returns the string `"Error executing tool: ..."`; the researcher sees only that text.
- `researcher_tools` (`deep_researcher.py:435-509`) reloads tools via `get_all_tools` (`:467`), keys them by `tool.name` or `.get("name","web_search")` (`:468-471`), runs all calls in parallel through `execute_tool_safely` (`:474-479`), and wraps each result into a `ToolMessage` content string.
- An empty Tavily result is a specific success string, `"No valid search results found..."` (`utils.py:125-127`), not an error.
- Tavily's tool takes `queries: List[str]` (`utils.py:43-49`); MCP tools expose server-defined schemas, so the two are **not** schema-compatible.
- `wrap_mcp_authenticate_tool` (`utils.py:385-447`) re-raises non-MCP errors and converts MCP `-32003` to `ToolException` (`:440`), so some MCP error structure is lost unless classified before wrapping.
- `load_mcp_tools` (`utils.py:449-524`) returns `[]` for connection failure, zero usable tools and missing authentication (`:478-479,502-504`), so the load outcome is unrecoverable today (ADR-001 §8.1a, U-5).

Only Tavily and MCP tools run client-side; native OpenAI/Anthropic search runs inside the model call and cannot be invoked as a substitute, consistent with REQ-008 `out_of_scope`.

## 3. Decision

Adopt a **dedicated fallback coordinator** in the `search` module that owns the fallback algorithm, exposed to the researcher through a **thin tool-facing adapter**:

1. **Normalise the request.** One `SearchRequest` (queries, limits, topic) is the provider-agnostic input.
2. **Adapt per source.** Each Tavily/MCP source has an adapter that translates a `SearchRequest` into that source's native schema and maps native results and exceptions back to the typed contracts. Sources are not assumed schema-compatible.
3. **Coordinate in order.** `FallbackCoordinator` iterates the configured sources in order, **classifying each failure before any exception becomes a string** (`execute_tool_safely` is never in the classification path).
4. **Distinguish outcomes.** A success returns its result; an empty result is a success; an ineligible failure terminates fallback immediately and is returned; only when every eligible source is exhausted is `AllSourcesFailed` produced.
5. **Expose as one tool.** A thin adapter registers the coordinator as the single model-callable search tool under a stable name, so `tools_by_name` dispatch (`deep_researcher.py:468-471`) is unchanged.
6. **Consume the structured MCP load result.** The coordinator receives availability from the MCP load result rather than inferring it from an empty tool list.

Do not change the graph topology or state. Do not substitute native model search. Keep REQ-007 validation separate (this ADR does not perform or replace configuration validation). The MCP load-result contract is a dependency (see §2, §9, and REQ-007 U-5).

**Empty fallback configuration (intent vs evidence).** The architectural *intent* is that an empty (or absent) fallback list preserves today's single-source behaviour exactly: one search source, and on failure the current error path through `execute_tool_safely` (`deep_researcher.py:427-432`) is unchanged (ASR-008-08). This is **architectural intent only, not verified behaviour**: it is not yet implemented, and it must be confirmed by the planned regression case `::test_no_fallback_configuration_preserved` (§11) before it can be claimed. Until that case runs and passes, no statement here should be read as proving backward compatibility.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A. Researcher-level fallback (`execute_tool_safely`/`researcher_tools` loops over sources) | Puts the loop and classification in the orchestration node (thin-node rule, `structural-constraints.md` §2.1); classifies **after** `execute_tool_safely` (`deep_researcher.py:427-432`) has flattened the exception to a string, destroying error identity; no reusable, unit-testable interface; entangles fallback with REQ-007 node validation. |
| C as a standalone implementation | A tool-facing adapter alone does not decide ordering, classification or aggregation; it only routes results. It complements the coordinator rather than replacing it. (This is distinct from REQ-007's rejected "validation in tool assembly" option, which concerned validation timing, not result routing.) |

The full comparison is in EVAL-002.

## 5. Components and Interfaces

These are architectural contracts, not implemented code.

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `search/request.py` (new) | Provider-agnostic search intent. Immutable, owned by the coordinator per call. | `SearchRequest(queries: list[str], max_results: int, topic: str)` | Coordinator |
| `search/adapters/` (new) | Per-source translation: build the native call from a `SearchRequest`; map native result/exception to the typed outcome/failure. One adapter per Tavily/MCP source; not interchangeable. | `class SearchSource(Protocol): name: str; async def invoke(req: SearchRequest) -> SearchOutcome; load_status: McpLoadStatus \| None` | Coordinator |
| `search/fallback.py` (new) | Ordered attempt loop, classification, result normalisation, all-failed aggregation. Pure over injected `SearchSource`s. | `class FallbackCoordinator: async def run(req: SearchRequest, sources: Sequence[SearchSource]) -> SearchOutcome \| SearchTerminatedFailure \| AllSourcesFailed` | Tool-facing adapter |
| `search/errors.py` (new) | Typed outcomes and classification. | `SearchOutcome(found: bool, content: str, source_name: str)`; `SearchAttemptFailure(source_name: str, stage: FailureStage, classification: ErrorClassification, detail: str)` where `FailureStage ∈ {LOAD, INVOKE}`; `SearchTerminatedFailure(failure: SearchAttemptFailure)`; `AllSourcesFailed(failures: list[SearchAttemptFailure])`; `ErrorClassification(eligible: bool, category: str)` | Coordinator |
| Tool-facing adapter (new) | Expose the coordinator as the single model-callable search tool under a stable name; render success/empty/all-failed into `ToolMessage` content. | registered as the search tool with a stable name | `get_all_tools` assembly |
| `utils.get_all_tools` / `get_search_tool` | Assembly entry unchanged in contract; provides the configured sources and the MCP load result. | as-is (or structured per U-5) | `researcher`, `researcher_tools` |

Shared contracts changed (`structural-constraints.md` §6): a new `Configuration` field for the ordered fallback list (see §8, D-2) and, under REQ-007 U-5 Option B, the `utils.load_mcp_tools` return type — both need the affected owners' approval.

**Contract details**

- `SearchRequest` — owned by the coordinator; built once per tool call from the model's arguments; failure semantics: never raises (it is data).
- `SearchSource` — one per configured Tavily/MCP source; `invoke` raises only the typed failures or returns a `SearchOutcome`; `load_status` carries the REQ-007 load result (`LOADED`/`ZERO_USABLE_TOOLS`/`AUTH_MISSING`/`LOAD_FAILED` or `None` for Tavily).
- `SearchOutcome` — `found=False` means an empty **success** (C-004), never a failure.
- `SearchAttemptFailure` — recorded per attempted source; `classification` decides whether to continue. Its `stage` field distinguishes a **load-stage** failure (`LOAD`) from an **invocation-stage** failure (`INVOKE`). A source unavailable at load time is recorded with `stage=LOAD` and its `detail` naming the load cause; this explicitly records that the source's search tool was **never invoked**, so it must not be presented as an invocation error. An invocation error is recorded with `stage=INVOKE` after `invoke` actually raised. Both stages still appear in `AllSourcesFailed`, tagged by `stage`, so the aggregate never falsely claims an unavailable source was called.
- `SearchTerminatedFailure` — wraps the single ineligible failure that stopped fallback (C-005).
- `AllSourcesFailed` — the aggregate of every attempted source and its error (C-003).
- `ErrorClassification` — `eligible: bool` plus a `category` from a closed set (timeout, connection, rate_limit, server_error, credential_rejected, load_failed, malformed, other).

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none (no graph state field added or changed).
- **Runtime policies:** a new fallback policy (proposed; see the runtime-policy module section) plus a **pending** conditional revision of REQ-007 `POL-002` for the multi-source case (D-1). Neither is approved.
- **Invariants:** INV-005 (Proposed); this ADR refines the empty-vs-failed semantics it depends on.
- **Deterministic boundary:** eligibility, ordering, empty-vs-failed and the all-failed aggregate are decided by deterministic code; no model decides them.

### 6.1 Failure semantics (explicit)

| Situation | Behaviour |
|---|---|
| Eligible invocation failure | Attempt the next configured source. |
| Ineligible invocation failure (e.g. malformed query) | Terminate fallback immediately; return the failure (`SearchTerminatedFailure`). |
| Empty successful result | Return success; do **not** fall back. |
| Every eligible source exhausted | Return `AllSourcesFailed` listing every attempted source and its error. |
| Source unavailable during loading | Record `SearchAttemptFailure(stage=LOAD, category=load_failed)` naming the load cause; the source's search tool was never invoked. The run-terminating decision is **subject to D-1 approval**. |
| Missing required authentication configuration | Configuration failure (not an invocation error); not auto-repaired. |
| Credential rejected during invocation | Eligible fallback error; no automatic credential recovery. |

Not every error becomes `AllSourcesFailed`: an ineligible failure terminates as `SearchTerminatedFailure`, and an empty result is a `SearchOutcome` with `found=False`.

## 7. Error Classification

Classification uses **explicit exception types, structured error codes, or documented status metadata**, not generic message matching.

| Category | Eligible | Tavily signal | MCP signal |
|---|---|---|---|
| timeout | yes | `asyncio.TimeoutError` / client timeout | tool-call timeout |
| connection | yes | client transport/connection error | `McpError` transport failure |
| rate_limit | yes | `UsageLimitExceededError`, HTTP 429/432/433 | `McpError` rate-limit code if surfaced |
| server_error | yes | HTTP 5xx (`status_code` metadata) | `McpError` 5xx code |
| credential_rejected | yes | `InvalidAPIKeyError`, `ForbiddenError` (401/403) | MCP auth error (classified before `wrap_mcp_authenticate_tool` rewrites `-32003`) |
| malformed | no | `BadRequestError` (400) | `McpError` invalid-params |
| auth_config_missing | no | n/a | `AUTH_MISSING` at load stage |
| other / unclassifiable | **no** | — | — |

- **Tavily** exposes typed exceptions (`BadRequestError`, `InvalidAPIKeyError`, `UsageLimitExceededError`, plus `ForbiddenError`) without a shared base; classification keys on those types and on `status_code` metadata where present.
- **MCP** errors carry `McpError.error.code`/`data`; the adapter must classify on the **original** exception before `wrap_mcp_authenticate_tool` converts `-32003` to `ToolException` (`utils.py:440`).
- **Do not assume MCP errors carry HTTP status codes.** Where neither a typed exception nor a structured code is available, the error is **ineligible by default**, pending an explicit policy decision (D-3).
- Substring matching is **not** used as an automatic fallback mechanism; where typed information is genuinely absent it may only be used under a documented policy (D-3).

## 8. Integration with REQ-007

REQ-007 (ADR-001) validates configuration before model/search calls and checks whether usable search capability exists; REQ-008 handles failures **during search execution**. The proposed interaction boundary:

- **Load stage (REQ-007 concern).** A source that cannot be loaded keeps a distinct `load_failed` diagnostic. Whether that terminates the run is **conditional on D-1**: the proposal below narrows ADR-001 §9/POL-002 so that a failed **fallback** MCP source is recorded without terminating the run when other validated, usable sources remain; a lone unusable source still stops.
- **Invocation stage (REQ-008 concern).** Eligible invocation failures fall over to the next source; ineligible ones terminate.
- **Capability.** The REQ-007 capability predicate (ADR-001 §8.3) should count usable configured fallback sources toward "search capability exists" (rule 3 of the review policy). This is a proposed amendment, not made here.
- **Authentication.** Missing authentication configuration is a configuration failure (rule 6). A credential **rejected at invocation** is eligible for fallback (rule 7), with no automatic credential recovery.

**Proposed conditional revision of POL-002 (Pending Team Approval; not applied here).** Amend ADR-001 §9 / POL-002 so that, when a validated fallback MCP source fails to load, the failure is recorded as a per-source diagnostic and does not terminate the run **if other validated, usable sources remain**; if no usable source remains, the run stops with an explicit error as today. ADR-001 and POL-002 are **not** edited by this ADR.

## 9. Consequences, Risks, Assumptions, Unresolved Decisions and Rollback

- **Positive:** typed classification before stringification; single-responsibility coordinator; one stable tool name; empty-vs-failed unambiguous; all source-level logic offline-testable with fake sources.
- **Negative / neutral:** a new `search` subpackage and a new configuration field; a dependency on the structured MCP load result; a thin adapter to keep dispatch stable.
- **Risks:** Tavily's generic client errors (connection/5xx) may lack a stable type, so classification may default to ineligible (D-3); `wrap_mcp_authenticate_tool` loses MCP code structure unless classification precedes it; adding a configuration field touches a shared contract; the D-1/POL-002 narrowing changes documented REQ-007 behaviour and needs approval; REQ-008 cannot fully verify load-stage cases while U-5 is open.
- **Assumptions:** the fallback list contains only Tavily and configured MCP sources; native search is excluded; `execute_tool_safely` is not in the classification path.

Unresolved / conditionally recommended decisions (none approved):

- **D-1 (Open; conditionally recommended):** Split load-stage (REQ-007) from invocation-stage (REQ-008) failures; narrow POL-002 so an unloadable fallback MCP source is recorded, not run-terminating, when other usable sources remain. Requires team approval.
- **D-2 (Open):** Fallback configuration field — name, placement (`Configuration` vs `MCPConfig`), precedence vs `search_api`, default empty (opt-in). Recommended default empty; requires shared-contract approval.
- **D-3 (Open; recommended typed-classification):** Eligibility signals: typed exceptions + structured codes + status metadata; unclassifiable → ineligible. Requires approval of the Tavily generic-error gap policy.
- **D-4 (Open):** Unavailable MCP fallback source: recorded `load_failed` and listed in `AllSourcesFailed` (recommended) versus excluded silently. Depends on U-5.
- **D-5 (Open):** Hard dependency on REQ-007 U-5 structured load result (or equivalent); no silent degradation to an empty tool list. Requires approval of the dependency.
- **D-6 (Open; recommended):** Coordinator algorithm behind a thin tool-facing adapter with a stable tool name. Requires approval of the exposed tool name/schema.
- **D-7 (Open; recommended):** All-failed rendering is a distinct, unambiguous `ToolMessage` (structured/typed content, never equal to the empty marker at `utils.py:127`). Requires approval of the contract.
- **D-8 (Open; recommended):** Missing auth configuration = configuration failure (stop); credential rejected at invocation = eligible fallback (no auto-recovery). Requires approval of the boundary.

- **Rollback:** remove the fallback coordinator, adapters and tool adapter, and the configuration field; with the field default empty, baseline behaviour is restored.

## 10. Implementation Steps

Ordered steps for a future Coding Agent (none performed here):

1. Create `src/open_deep_research/search/request.py`, `search/errors.py`, `search/fallback.py` and `search/adapters/` with the contracts in §5; docstrings name `REQ-008, ADR-002, INV-005`.
2. Add the package to `[tool.setuptools] packages` in `pyproject.toml`.
3. Obtain the structured MCP load result (REQ-007 U-5, or an equivalent adapter) so `load_status` is available to each MCP source; do not infer availability from an empty tool list.
4. Add the ordered fallback configuration field (D-2), default empty, with `x_oap_ui_config` metadata; baseline behaviour preserved when empty.
5. Implement the tool-facing adapter and register it through `get_all_tools` under a stable tool name (D-6), leaving `tools_by_name` dispatch unchanged.
6. Implement classification per §7, before any exception is stringified.
7. Implement rendering of success / empty / `AllSourcesFailed` into `ToolMessage` content (D-7).
8. Add the module section to `verification-constraints.md` §7, `runtime-policy-catalog.md`, `structural-constraints.md` §10, `invariants.md`, `trace-matrix.md`.
9. Verify per §11; record evidence in `docs/test-reports/REQ-008.md`.

## 11. Verification

Status of these cases, stated precisely:

- **Planned test cases are documented** as entries in `verification-constraints.md` §7 (`REQ-008 fallback (ADR-002)`), as `TC-027` through `TC-037`.
- **Test implementation is not created:** no `test/offline/test_search_fallback.py` exists yet.
- **Tests are not executed:** none of these cases has been run; there is no pass/fail evidence.

IDs continue after REQ-007's `TC-026` to avoid collision (the module example rows TC-001…TC-003 are placeholders, not real cases).

| Criterion | Verification case | Test name (planned) |
|---|---|---|
| C-001 | TC-027 | `test/offline/test_search_fallback.py::test_primary_failure_uses_fallback` |
| C-002 | TC-028 | `::test_fallbacks_follow_configured_order` |
| C-003 | TC-029 | `::test_all_sources_fail_explicitly` |
| C-004 | TC-030 | `::test_empty_result_does_not_trigger_fallback` |
| C-005 | TC-031 | `::test_ineligible_error_does_not_trigger_fallback` |
| Typed classification (§7) | TC-032 | `::test_error_classification_typed` |
| Load-stage diagnostic contract (§6.1, ASR-008-10) | TC-033 | `::test_mcp_load_stage_failure_recorded` |
| Conditional continuation after load failure (D-1/D-4, ASR-008-08) | TC-037 | `::test_load_failure_continuation_decision` |
| No-fallback backward compatibility (ASR-008-08) | TC-034 | `::test_no_fallback_configuration_preserved` |
| Auth boundary (D-8) | TC-035 | `::test_auth_boundary_classification` |
| Tool dispatch + adapter schema (ASR-008-11) | TC-036 | `::test_tool_dispatch_and_adapter_schema` |

The cases are documented as Planned / Not Implemented / Not Executed in `verification-constraints.md` §7; this ADR does not claim any of them has been implemented or passed.

## 12. Modules and Documents to Update at Integration

`evaluation-table.md` (EVAL-002), `adr/002-search-fallback.md` (this file), `invariants.md` (INV-005 refinement), `runtime-policy-catalog.md` (fallback policy; conditional POL-002 revision per D-1), `trace-matrix.md` (REQ-008 row), `structural-constraints.md` §10, `verification-constraints.md` §7. `memory-design.md` does not change (no state). ADR-001 and POL-002 are not edited by this ADR.
