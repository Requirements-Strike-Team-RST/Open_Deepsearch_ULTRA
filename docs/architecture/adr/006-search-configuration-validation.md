# ADR-001: Validate Search Configuration with a Pure Validator Before Research

- **Status:** Proposed
- **Date:** 2026-11-13
- **Module:** search
- **Owner:** sszfot
- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)
- **SA Review:** pending (no `SA-NNN` recorded)

> This decision is *Proposed*. It is not approved until SA Review accepts it (`Prompt.md` §4, Gate 1). Everything below describes intended behaviour; none of it is implemented yet. Decisions still open for the team are listed in §12.

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-007 | C-001, C-002, C-003, C-004, C-005 | The decision must reject invalid search configurations *before any model or search call*, which fixes where validation runs in the graph and whether it may use a model or network. |
| REQ-007 | ASR-007-01 to ASR-007-09 (below) | These sub-drivers fix purity, module boundary, provider/model rules, MCP static-vs-runtime split and documentation consistency. |

Architectural drivers (ASR), provisional IDs used consistently across EVAL-001, this ADR and the module sections:

| ID | Statement |
|---|---|
| ASR-007-01 | Every entry path into the research chain validates search configuration on each run before its first model or search call. |
| ASR-007-02 | Native providers (`anthropic`, `openai`) require a `research_model` of the same provider; other providers impose no model constraint; only `research_model` is in scope. |
| ASR-007-03 | A configuration is statically search-capable iff it names a built-in provider that yields a search tool, or names an MCP server with a well-formed URL and at least one declared tool. |
| ASR-007-04 | Unsupported `search_api` values are rejected with an error listing the supported set, including when they arrive through the environment variable. |
| ASR-007-05 | Static validation is pure and offline-testable: no model calls, no network, no MCP connection. |
| ASR-007-06 | Valid existing configurations and the graph topology behave exactly as before. |
| ASR-007-07 | Documentation and validation messages are consistent: the README explains behaviour, providers, required models, credentials and MCP-as-search; errors name the setting and supported values. |
| ASR-007-08 | A statically declared MCP that cannot provide a usable search tool at runtime fails the run explicitly instead of silently continuing without search. |
| ASR-007-09 | The presence of search capability is decided by an explicit predicate, not by a tool count that always includes non-search tools. |

## 2. Context

Upstream issue #250 reports that it is unclear when the agent searches and how to use another or a self-hosted search provider. The baseline behaviour being changed:

- `SearchAPI` enumerates `anthropic`, `openai`, `tavily`, `none`, and nothing in `Configuration` validates provider/model pairing (`src/open_deep_research/configuration.py:11-17,78-93,153-162`). The only guard is a UI note, "Make sure your Researcher Model supports the selected search API" (`configuration.py:84,159`).
- `Configuration.from_runnable_config` already rejects an invalid `search_api` **during Pydantic model construction**: every field is read from the environment variable first and the `configurable` dict second (`configuration.py:243-246`), `None` values are dropped (`:247`), and a value that is not a `SearchAPI` member raises a `ValidationError` listing the valid set. This happens before any node body runs, so a validator that receives an already-constructed `Configuration` never sees an invalid enum value.
- `get_search_tool` returns native search *definitions* for `anthropic`/`openai`, the `tavily_search` tool for `tavily`, and `[]` for `none`; an unknown value falls through silently to `[]` (`src/open_deep_research/utils.py:531-567`).
- `load_mcp_tools` returns `[]` for any malformed MCP configuration and swallows connection errors (`utils.py:470-481,499-504`), so a broken MCP search degrades silently to "no search".
- The researcher's empty-tool guard is dead code: `get_all_tools` always includes `ResearchComplete` and `think_tool`, so `len(tools) == 0` is never true (`deep_researcher.py:384-389` vs `utils.py:579`).
- The README search section only points to `search_api` and `mcp_config` (`README.md:77`).

### 2.1 Configuration precedence and `search_api` value handling

`Configuration.from_runnable_config` resolves each field once, with this precedence (`configuration.py:243-247`): the upper-case environment variable (`SEARCH_API`) **always overrides** the `configurable.search_api` value, and a value of `None` is dropped so the field default applies. The observed behaviour of the current code, which the design must preserve, is:

| Input | Observed result | Reason |
|---|---|---|
| key omitted, no env var | `SearchAPI.TAVILY` | field default (`configuration.py:79`) |
| explicit `None` | `SearchAPI.TAVILY` | `None` dropped by `:247`, default applies |
| `"bing"` (unsupported) | rejected | Pydantic enum construction fails |
| `""` (empty) | rejected | Pydantic enum construction fails |
| `"TAVILY"` (uppercase) | rejected | enum values are lower-case; no normalisation |
| `SEARCH_API=bing` with a valid `configurable` value | rejected | env var wins, then enum construction fails |

The proposed mechanism must not normalise an invalid value into an accepted one. It documents that values are case-sensitive and lower-case, and it must respect the environment-variable precedence above.

### 2.2 Entry paths that can reach a model or search call

From the `deep_researcher.py` wiring (links at lines 353-363, 589-605, 701-716):

| Path | Entry | First model call | Search tool bound? |
|---|---|---|---|
| P1 | `deep_researcher` `START → clarify_with_user` (public entry) | `clarify_with_user`, L101, only when `allow_clarification=True` | no |
| P2 | `clarify_with_user → write_research_brief` | L154 | no |
| P3 | `write_research_brief → research_supervisor` | `supervisor`, L214 | no (supervisor binds `ConductResearch`/`ResearchComplete`/`think_tool`, L202) |
| P4 | `supervisor_tools → researcher_subgraph.ainvoke` | `researcher`, L415 | yes (`researcher`, L408) |
| P5 | `researcher` (researcher subgraph `START`, L601) | L415 | yes |
| P6 | `researcher_tools` | none (tool execution only; `get_all_tools` at L467) | yes (via assembly) |
| P7 | `supervisor` (supervisor subgraph `START`, L360) | L214 | no |

Both subgraphs are compiled (`supervisor_builder.compile()`, `researcher_builder.compile()`) and can be invoked directly, so P5 is a real entry path that does not pass through `clarify_with_user`. P1 and P2 call the research model before any tool assembly, so validation that lives only in tool assembly is too late on the standard path — the late failure #250 reports.

## 3. Decision

Validate search configuration with a small, pure `search` module that runs **on each run**, split into three ordered steps so that each step only sees inputs it can actually reject:

1. **Raw-input resolution (`resolve_search_api`).** Reads the raw `configurable` dict and the environment with the precedence of §2.1, applies the documented defaults (omitted or `None` → `tavily`), and rejects any other value that is not a supported lower-case provider with a single error listing `anthropic, openai, tavily, none`. This is the **only** C-003 mechanism, because it sees the raw value before Pydantic construction.
2. **Construction.** `Configuration.from_runnable_config(config)` runs as today and remains a defensive backstop; it is not the user-facing C-003 path.
3. **Cross-field validation (`validate_search_configuration`).** Receives the resolved, valid `SearchAPI` and the MCP classification and checks only C-001 (native provider ↔ `research_model`) and C-002 (`none` ⇒ a valid static MCP declaration). It never claims to catch an invalid enum value.

Steps 1–3 run at the start of `clarify_with_user` (public boundary) and at the start of `researcher` (subgraph boundary), before that node's model or search call, for both `allow_clarification=True` and `False`.

Do not change the graph topology, tool assembly, state or `Configuration` fields. Constrain only `research_model` against native providers. Treat a statically declared MCP capability as distinct from runtime MCP availability. Reject `search_api=none` when no valid MCP tool declaration exists. Replace the dead `len(tools) == 0` guard with an explicit search-capability predicate (§8). On runtime MCP failure, stop the affected research with an explicit error (§9); do not fall back to another source (that is REQ-008, out of scope). The runtime MCP failure policy is *Proposed* and awaits approval (U-1).

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A. Validation directly inside the research graph entry point | Violates the thin-node rule (`structural-constraints.md` §2.1); correctness depends on placing the call before the `allow_clarification` early return; no reusable, unit-testable interface; duplicates MCP capability logic. |
| C. Validation layer integrated with existing search tool assembly (`utils.get_all_tools`) | Runs only inside `researcher` (`deep_researcher.py:384,467`), i.e. after the L101 and L154 model calls on the standard path, so it fails C-001's "before any model or search call"; grows an already overloaded `utils.py`; conflates validation with REQ-008 fallback and repeats the shape of the unmerged `fix/issue-250` branch. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `search/configuration_validator.py` (new) | Resolve and validate the search provider and its cross-field constraints; build the effective `Configuration` from validated inputs; classify MCP capability. Deterministic and pure: no model, no network, no tool objects, and **no implicit process-environment access** (the caller passes an environment snapshot). | `resolve_search_api(raw_configurable: Mapping[str, Any], environ: Mapping[str, str]) -> SearchAPI`; `resolve_configuration(raw_configurable: Mapping[str, Any], environ: Mapping[str, str]) -> Configuration` (§7.2 boundary); `validate_search_configuration(search_api: SearchAPI, research_model: str, mcp: MCPConfig \| None) -> None` (raises `SearchConfigurationError`); `classify_mcp(mcp: MCPConfig \| None) -> MCPStatus`; `model_provider(model: str) -> str` | `clarify_with_user`, `researcher` |
| `search/capability.py` (new, or same module) | Decide whether a run has search capability, from explicit evidence passed by the caller after binding (never from implicit globals). | `has_search_capability(evidence: SearchEvidence) -> bool` where `SearchEvidence` records `search_api`, `mcp_status`, `mcp_load_status`, `native_bound` (see §8.3) and the assembled tools | `researcher` (after binding, step 4) |
| `clarify_with_user` (existing node) | Perform effective configuration resolution and static cross-field validation before the `allow_clarification` early return and any model call. It does **not** assemble search tools, load MCP tools, or bind native search; the six-step §8.0 sequence applies to `researcher`. Stays thin. | unchanged (`deep_researcher.py:60`) | graph `START` |
| `researcher` (existing node) | Run the §8.0 sequence: validate → assemble → bind → evaluate capability (step 4, after binding) → invoke model → optional post-response observation. Stays thin. | unchanged (`deep_researcher.py:365`) | researcher subgraph `START` |
| `search/mcp_status.py` (new) | Distinguish the MCP runtime outcomes: Option A (adapter owns the load and captures each branch) or Option B (consume the structured `McpLoadResult` produced by a refactored `utils.load_mcp_tools`, passed in by the orchestration caller) — §8.1a, U-5. **Implementation dependency: does not exist today.** | `load_mcp_result(config, existing_tool_names) -> McpLoadResult` | `researcher` (via capability/policy); under Option B the loader runs in orchestration and only its result is passed in |
| `utils.get_all_tools` / `get_search_tool` / `load_mcp_tools` | Option A: unchanged; `search/mcp_status.py` does not import `load_mcp_tools`. Option B: `utils.load_mcp_tools` produces the structured `McpLoadResult` and its callers read `.tools` (U-5, shared-contract change); `search` receives the result, it does not invoke the loader. | as-is (Option A) or `-> McpLoadResult` (Option B) | `researcher`, `researcher_tools` |
| `README.md` | Document behaviour, providers, required models, credentials and the MCP search recipe (C-005). | — | human readers |

Shared contracts changed (`structural-constraints.md` §6): **none**. No state field and no `Configuration` field is added; the module reads existing fields only.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none (no field added or changed; `memory-design.md` needs no section).
- **Runtime policies:** one proposed policy, `POL-002` in `runtime-policy-catalog.md`, marked pending approval (§9, U-1).
- **Invariants:** INV-005 (Proposed).
- **Deterministic boundary:** search-configuration validity and search capability are decided by deterministic code; no model decides them. REQ-007 is `safety_relevant: false`, but the code is model-free.

## 7. Configuration Validation Rules

Step 3 (`validate_search_configuration`) receives a valid `SearchAPI` and the `research_model` string. Canonical provider set is the `SearchAPI` enum: `anthropic`, `openai`, `tavily`, `none`.

| `search_api` | Rule | On violation |
|---|---|---|
| `anthropic` | `research_model` must resolve to the `anthropic` provider (§7.1). | Raise, naming both `search_api=anthropic` and `research_model=<value>` (C-001). |
| `openai` | `research_model` must resolve to the `openai` provider (§7.1). | Raise, naming both settings (C-001). |
| `tavily` | No model constraint; accepted with any `research_model` (C-004). Credential absence is a runtime condition, not a configuration error; do not reject on it. | Accept. |
| `none` | Accepted only if the MCP configuration is a valid *declaring* config (§8). | Raise, naming `search_api=none` and `mcp_config` (C-002). |
| unsupported value | Handled in step 1, not here. Step 1 rejects any non-default value that is not a supported lower-case provider; step 3 never sees one. | See §7.2 (C-003). |

### 7.1 Provider resolution: strict prefix versus LangChain-compatible inference (U-3, open)

Two policies are possible for deciding whether `research_model` matches a native provider. The choice is **open** (U-3); the teammate preference for strict matching is recorded as a proposal (P-1), not an approved decision.

- **Strict prefix.** Provider = `research_model.split(":", 1)[0].strip().lower()`. Consequences with observed LangChain behaviour:
  - `openai:gpt-4.1` → `openai` (matches `openai`).
  - `gpt-4.1` → `gpt-4.1` (does **not** match `openai`, although LangChain infers the OpenAI provider) → a false rejection.
  - `anthropic.claude-3` → `anthropic.claude-3` (does **not** match `anthropic`, although LangChain routes it to Bedrock) → a false rejection.
- **LangChain-compatible inference.** Reproduce the public, documented behaviour of provider inference without importing private internals: treat `provider:model` as a provider prefix when `provider` is a known provider name, otherwise leave the model to LangChain's inference (bare `gpt-4.1` → `openai`; `anthropic.claude-3` → Bedrock, not Anthropic). Only the native pairings `openai`/`anthropic` are constrained; a model that resolves to any other provider is a mismatch for those native providers.

The design keeps the resolution logic behind `model_provider()` so either policy can be selected at implementation time. It does **not** make importing private LangChain internals an architectural requirement; a small local provider table plus tests is sufficient. Proposal **P-1** (strict matching, raised by a teammate) and the default leaning toward LangChain-compatible inference are both recorded in §12; **U-3 is decided at SA Review**.

### 7.2 Provider-value validation (C-003), step 1

`resolve_search_api` applies the precedence of §2.1 and then this decision table. It does not normalise accepted values and it does not turn an invalid value into a valid one:

| Raw condition | Result |
|---|---|
| no `SEARCH_API`, no `configurable.search_api` | default `tavily` |
| `None` in either source | default `tavily` (treated as unset) |
| lower-case value in `{anthropic, openai, tavily, none}` | that provider |
| any other value (`"bing"`, `""`, `"TAVILY"`, `"Tavily"`, non-string) | raise, listing `anthropic, openai, tavily, none` |

Because step 1 runs before construction and reads the same two sources in the same precedence order, an invalid value in either the environment or the `configurable` dict is rejected with the same user-facing error, and step 2 never produces the raw Pydantic message for the user.

**Purity and resolution drift.** `resolve_search_api` is a deterministic pure function: the caller passes an explicit environment snapshot (`environ: Mapping[str, str]`, e.g. a copy of `os.environ` taken once at the start of the node) and the raw `configurable` mapping; the resolver never calls `os.environ` itself.

**Configuration-resolution boundary (Correction B).** Passing the resolved value only through `configurable` is **not sufficient**: `Configuration.from_runnable_config` gives the `SEARCH_API` environment variable precedence over `configurable.search_api` (`configuration.py:244`), so Pydantic would still let a present `SEARCH_API` win over the value the resolver validated. The boundary must therefore construct `Configuration` from the **validated effective inputs**, not by re-reading the live environment. The design requires one of:

- **Option 1 — build from explicit values.** Construct `Configuration` with the resolved search fields set directly (e.g. `Configuration(search_api=resolved_search_api, **other_fields)`) rather than through `from_runnable_config`, so no environment re-read occurs. The resolver output is the single source of truth for `search_api`. Because `from_runnable_config` applies env-over-configurable precedence and default handling to **every** field (not only `search_api`), Option 1 is acceptable only if it reproduces that effective-resolution semantics for all relevant fields identically. If that cannot be guaranteed, the additive snapshot-aware factory (**Option 2**) is required instead.
- **Option 2 — pass the same snapshot.** A future `from_runnable_config(config, environ=snapshot)` variant (implementation dependency, see below) that reads the provided snapshot instead of `os.environ`, called with the exact snapshot the resolver used; it preserves the existing per-field precedence and defaults by construction.

In both options the boundary captures the environment **once**, validates the raw values, and constructs the model from exactly those validated effective inputs. It does not mutate `os.environ` (no global side effects) and it preserves the semantics: `SEARCH_API` still outranks `configurable.search_api` **within the snapshot**, omitted/`None` → `tavily`, and provider values stay case-sensitive. Resolution drift is impossible because there is only one read of one snapshot.

**Future implementation dependency.** The current `Configuration.from_runnable_config` reads `os.environ` directly and has no `environ` parameter (`configuration.py:236-247`). Option 1 needs no change to that factory (it constructs the model directly); Option 2 needs a small, additive factory refactor to accept an `environ` mapping while defaulting to `os.environ` so existing callers are unaffected. This is recorded as an implementation dependency, not an approved decision.

## 8. MCP Configuration, Runtime Availability and Search Capability

### 8.0 Exact execution order in `researcher`

The steps must run in this order; each later step depends on an earlier one and must not be moved ahead of it:

1. **Raw and cross-field static validation** — `resolve_search_api` then `validate_search_configuration` on the raw config and validated effective inputs (§7). Raises before anything else runs.
2. **Search tool assembly** — `get_all_tools` / `get_search_tool` produce the tool list (native definition or Tavily object) and MCP tools are loaded (§8.1, §8.1a).
3. **Native model tool binding** — `bind_tools(...)` is called with the assembled tools. A successful bind is recorded as `native_bound = True`.
4. **Runtime search-capability evidence** — `has_search_capability(SearchEvidence)` is evaluated using the results of steps 2 and 3 (`native_bound`, `mcp_load_status`, assembled tools). This step runs **after** binding, so `native_bound` is already known; the predicate must not require `native_bound` before step 3 has run. Steps 2–3 produce the evidence; the `POL-002` runtime MCP policy is applied here after the predicate.
5. **Model invocation** — the researcher model is invoked with the bound tools.
6. **Optional post-response observation** — after a response, check `anthropic_websearch_called`/`openai_websearch_called` (or metadata) to observe whether a search actually executed ("executed" state, §8.2). This observation never gates capability and is not required for validation.

A successful bind (step 3) proves only that the definition was accepted locally; it is **not** proof that a remote search will execute. Execution is observed only in step 6.

### 8.1 MCP classification (static, step 3)

| Class | Condition | Counts as static capability (C-002)? |
|---|---|---|
| `MCP_ABSENT` | `mcp_config is None` | No |
| `MCP_INVALID_DECLARATION` | `mcp_config` present but `url` missing/empty or `tools` missing/empty | No |
| `MCP_DECLARED` | `url` present and `tools` non-empty; `auth_required` recorded | Yes (statically) |

Configuration validity is what step 3 decides. Runtime availability (reachable server, tools exist, authentication succeeds) is decided only after MCP tools are loaded; the validator never calls `MultiServerMCPClient`. So `search_api=none` with `MCP_DECLARED` is accepted at static validation; that acceptance is **not** proof the MCP search works.

### 8.1a Runtime outcomes are not distinguishable from the current `load_mcp_tools` return value

The current `load_mcp_tools` (`utils.py:449-524`) returns a single `list[BaseTool]` and collapses every failure into an empty list:

- configuration incomplete (missing `url`/`tools`) → `[]` at `utils.py:478-479`;
- `auth_required=True` with no resolvable token → `[]` at the same guard;
- connection / `get_tools()` exception → `[]` at `utils.py:502-504`;
- successful load that yields zero tools after the declared-name/name-conflict filter → `configured_tools == []` at `utils.py:506-524`.

All four are an empty list, so a caller cannot tell them apart from the return value alone. An adapter that merely calls `load_mcp_tools` and inspects the returned list **cannot** recover the original reason: the reason is discarded inside `load_mcp_tools` before the adapter sees anything. The distinction is therefore only implementable in one of two ways, both of which change behaviour that exists today (U-5, open; neither is approved):

- **Option A — adapter owns the load operation.** `search/mcp_status.py` does not call `load_mcp_tools`; it performs the MCP load itself (the `MultiServerMCPClient` setup, auth handling and result filtering that `load_mcp_tools` performs today) and records the outcome at each branch, returning `McpLoadResult(status: McpLoadStatus, tools: list[BaseTool])` with `LOADED` / `ZERO_USABLE_TOOLS` / `AUTH_MISSING` / `LOAD_FAILED`. It captures the outcome *before* information is discarded. This duplicates the loading logic until `utils.load_mcp_tools` is removed or redirected to the adapter.
- **Option B — internal loader refactor emits structured results.** `utils.load_mcp_tools` returns the same `McpLoadResult` directly, and existing callers (`get_all_tools`, `researcher_tools`) are updated to read `.tools`, preserving their current behaviour. This is a shared-contract change (`utils.py` return type) that needs owner approval (`structural-constraints.md` §6).

**Dependency direction.** The two options have opposite import directions and the ADR does not require both:

- Option A: `search/mcp_status.py` imports the MCP client and the shared config helpers, and does **not** import `utils.load_mcp_tools`.
- Option B: `utils.load_mcp_tools` produces the structured `McpLoadResult`; the orchestration caller (`get_all_tools`/`researcher`) runs the loader and passes the resulting `McpLoadResult` into the pure `search` validation/capability functions. The `search` module does **not** import or invoke the loader — it only consumes the passed-in result.

Whichever option is chosen, the rule is consistent: either the `search` module owns the load (Option A, no import of `utils.load_mcp_tools`) or orchestration produces the structured result and `search` consumes it as a value (Option B, `search` neither imports nor invokes the loader). The design never simultaneously forbids importing `utils.load_mcp_tools` and requires the `search` module to call it. Under Option B the runtime loader stays in `utils`/orchestration; the `search` functions remain pure over the passed-in `McpLoadResult`.

The ADR does not claim the current code distinguishes these states; it states the required distinction and the two implementable designs. Until one of them exists, `POL-002` cannot be implemented and remains Proposed.

The "successful tool invocation returning zero search results" outcome is **not** a loading state: it is observed at tool-call time when a loaded tool runs and returns no hits. It is a success (§9), not a load-status value, and does not need the loader change.

### 8.2 Native search: configured, bound, executed — the three states

Native Anthropic/OpenAI search is not a client-side tool. `get_search_tool` returns a *definition* (`utils.py:540-550`): Anthropic `{"type": "web_search_20250305", ...}`, OpenAI `{"type": "web_search_preview"}`. The researcher binds these via `configurable_model.bind_tools(tools)` (`deep_researcher.py:406-411`). Binding is a local, synchronous operation that succeeds whenever the definition is well-formed; it does **not** contact the provider. The three states must not be conflated:

| State | Meaning | How it is established | Testable with |
|---|---|---|---|
| **Configured** | `search_api` selects a native provider and `get_search_tool` produced its definition. | Config + `get_search_tool` output. | Fake config; inspect the definition dict. |
| **Bound** | `bind_tools(...)` completed without raising for that definition. | The bind call returns a model; wrap it so binding success is observable. | Fake model whose `bind_tools` records the definitions it received. |
| **Executed** | A model call actually performed a server-side search (e.g. `anthropic_websearch_called`/`openai_websearch_called`, `utils.py:607-658`). | Post-response inspection of message metadata. | Fake response with/without search metadata. |

Configuration does **not** imply binding, and binding does **not** imply that the provider's search service will answer. Availability at execution time is only observable after a model call and is outside static validation.

### 8.3 Search-capability predicate (U-4, replaces `len(tools) == 0`)

`get_all_tools` always returns `ResearchComplete` and `think_tool`, so a non-zero length never proves search capability. The predicate takes explicit **evidence**, not just the provider and a tool list, so it can distinguish configured from bound for native providers and loaded-usable from loaded-empty for MCP. Its input type `SearchEvidence` records: `search_api`; `mcp_status` (static class, §8.1); `mcp_load_status` (`LOADED`/`ZERO_USABLE_TOOLS`/`AUTH_MISSING`/`LOAD_FAILED`, §8.1a, or `None` when MCP is not the source); the assembled `tools`; and `native_bound: bool | None` (whether the native definition was observed at bind time, `None` when not applicable).

| Provider | Capability is true when | Notes |
|---|---|---|
| Anthropic native | `search_api == anthropic` and `native_bound is True` | Requires the observed bind result, not just the configured definition. No client tool object exists. |
| OpenAI native | `search_api == openai` and `native_bound is True` | The definition is a dict with **no `name` key**; never key on a name. |
| Tavily | `search_api == tavily` and `tavily_search` is among the assembled tools | The tool object's `name` is `tavily_search`; `web_search` is only its `metadata["name"]` alias. |
| MCP-only (`none`) | `mcp_status == MCP_DECLARED` and `mcp_load_status == LOADED` with ≥1 assembled tool | Static declaration alone is not capability; only `LOADED` with tools establishes it. |

`none` with `MCP_ABSENT`/`MCP_INVALID_DECLARATION` is already rejected by C-002; the predicate returns false as a defensive re-check. The predicate is evaluated at step 4 (§8.0), **after** native binding (step 3) has produced `native_bound`, so it never requires `native_bound` before binding occurred. It is pure and testable with fake bindings (a fake model recording the definitions passed to `bind_tools`) and fake tool objects; no network or model call is needed to exercise it.

**When runtime availability can actually be established:** `native_bound` exists only after step 3, and `mcp_load_status` only after step 2's MCP load; the predicate (step 4) therefore runs between binding and model invocation. Native execution success is observable only post-response (step 6, the "executed" state) and is not part of capability; a successful bind does not prove a remote search will run.

## 9. Runtime MCP Failure — Proposed Stop-and-Error Policy (U-1, open)

When a declared MCP is the effective search source (typically `search_api=none` with `MCP_DECLARED`), distinguish these outcomes. None of them is a fallback: the design never substitutes another source (that is REQ-008, out of scope).

| Outcome | Detection (via the §8.1a adapter/refactor; not available today) | Proposed behaviour |
|---|---|---|
| Connection or loading failure | `McpLoadResult.status == LOAD_FAILED` (the `get_tools()` exception branch, today `utils.py:502-504`) | Stop the affected research; raise an explicit error naming `mcp_config.url` and "connection failed". |
| Loaded, zero usable declared search tools | `McpLoadResult.status == ZERO_USABLE_TOOLS` (empty after the declared-name/name-conflict filter, today `utils.py:506-524`) | Stop; raise an explicit error that the declared MCP tools are not available. |
| Missing required authentication | `McpLoadResult.status == AUTH_MISSING` (`auth_required=True`, no token, today `utils.py:475-479`) | Stop; raise an explicit error that the MCP server requires authentication. |
| Loaded and usable, tool returns no hits | `McpLoadResult.status == LOADED`; the tool runs and returns zero results | Success with no evidence; not an error and no stop (belongs to INV-005 / REQ-008). |

This policy is recorded as `POL-002` (Proposed, awaiting approval) in `runtime-policy-catalog.md`. Its placement (in `researcher` after assembly, versus deferral to the failure-handling module of REQ-002/REQ-004) is U-1 and is **open**. The mechanism should surface the failure as a raised error that the existing failure handling can carry, without introducing fallback.

## 10. Integration Points and Dependency Direction

- Dependency direction follows `structural-constraints.md` §5: `deep_researcher.py → search/ → configuration.py`. The `search` module must not import `deep_researcher.py`, `utils.py`, any model client or the MCP client; it reads the assembled tool list only as an argument.
- Call sites and justification (see §2.2):
  - `clarify_with_user` — the **public boundary**; dominates P1–P4 and P6 for the normal top-level run.
  - `researcher` — the **subgraph boundary**; required because the researcher subgraph is compiled and can be invoked directly (P5), bypassing `clarify_with_user`. The same node also hosts the capability predicate and the runtime MCP policy, which need the assembled tools.
  - `supervisor` (P7) and `researcher_tools` (P6) — **no** search-configuration check: P7 binds no search tool, and P6 is reached only after `researcher` (L365→L435→L509) has validated, so a check there would be redundant. This claim holds only because the call graph in §2.2 proves it.
- No change to `get_all_tools`, `get_search_tool`, `load_mcp_tools`, `state.py`, the graphs or `Configuration` fields.
- The new subpackage is added to `[tool.setuptools] packages` in `pyproject.toml` in the implementation PR (`structural-constraints.md` §1), or a non-editable install omits it. This is a Coding-Agent step, not part of this documentation change.
- Blueprint §6 already records the exception `utils.py → search/` for `get_all_tools()`; this ADR does not require it, because the module is called from the graph, not from `utils.py`.

## 11. Implementation Steps

Ordered steps for a future Coding Agent (none performed here):

1. Create `src/open_deep_research/search/__init__.py`, `search/configuration_validator.py` and `search/mcp_status.py` (or an equivalent) with `resolve_search_api`, `validate_search_configuration`, `classify_mcp`, `model_provider`, the MCP load adapter (`McpLoadResult`/`McpLoadStatus`) and `has_search_capability`; docstring names `REQ-007, ADR-001, INV-005`.
2. Add the package to `[tool.setuptools] packages` in `pyproject.toml`.
3. Introduce the MCP load distinction (§8.1a) by **one** of two options (U-5; owner approval required): Option A — `search/mcp_status.py` owns the load and captures `LOADED` / `ZERO_USABLE_TOOLS` / `AUTH_MISSING` / `LOAD_FAILED` before information is discarded, and does not import `utils.load_mcp_tools`; or Option B — refactor `utils.load_mcp_tools` to return `McpLoadResult` and update `get_all_tools`/`researcher_tools` to read `.tools`. A wrapper that only inspects `load_mcp_tools`'s returned list is not sufficient. This is a prerequisite for step 5.
4. In `clarify_with_user`, before the `allow_clarification` check and any model call, capture one environment snapshot and run `resolve_search_api(raw_configurable, snapshot)` then `validate_search_configuration(...)`; construct `Configuration` from exactly the validated effective inputs (§7.2 “Configuration-resolution boundary”), not by re-reading the live environment.
5. In `researcher`, follow the §8.0 order: validate → assemble tools → `bind_tools` (record `native_bound`) → evaluate `has_search_capability(SearchEvidence)` after binding and apply the `POL-002` runtime MCP policy using `McpLoadResult` → invoke the model → optionally observe execution post-response.
6. Update `README.md`'s search section with the provider matrix and MCP recipe (C-005).
7. Add the module sections referenced in `structural-constraints.md` §10, `verification-constraints.md` §7, `invariants.md`, `runtime-policy-catalog.md` and `trace-matrix.md`.
8. Verify per the matrix in `verification-constraints.md` §7; record evidence in `docs/test-reports/REQ-007.md`.

## 12. Consequences, Risks, Assumptions, Unresolved Decisions and Rollback

- **Positive:** invalid configurations rejected before the first model/search call on every entry path; single-responsibility, offline-testable module; matches the `search/` module boundary and dependency direction; no topology change; no reliance on a tool count that is never zero.
- **Negative / neutral:** two call sites to keep in step; a new import in two nodes; a small runtime capability check in `researcher`; a required adapter or refactor of `load_mcp_tools` before the runtime policy can be implemented.
- **Risks:** false rejection of a valid configuration (mitigated by the tested provider rules, by preserving the omitted/`None` defaults, and by treating Tavily credentials as runtime); divergence between the README and the validator (mitigated by C-005 review); a provider-resolution policy that disagrees with LangChain's inference (mitigated by the U-3 decision and tests); the runtime MCP policy stopping a run that might have recovered (mitigated by scoping "stop" to declared-but-unusable, not to slowness or empty results); resolution drift between step 1 and step 2 if they do not share one environment snapshot (mitigated by §7.2).

Unresolved decisions (for team review; none decided here):

- **U-1 (open):** Adopt the stop-and-error runtime MCP policy (§9, `POL-002`) under REQ-007 now, or defer to the failure-handling module (REQ-002/REQ-004)? Placement in `researcher` after assembly?
- **U-2 (open, wording):** Replace all "start-up" claims with per-run validation before each entry node's model/search call; confirm the INV-005 wording in §13.
- **U-3 (open):** Strict provider-prefix matching (P-1, teammate preference) versus LangChain-compatible inference (§7.1). Neither is approved.
- **U-4 (open):** Approve replacing the dead `len(tools) == 0` guard with the `has_search_capability` predicate (§8.3)?
- **U-5 (open):** Adopt the MCP load adapter versus a `load_mcp_tools` return-contract refactor (§8.1a); the latter is a shared-contract change needing owner approval.

Proposals recorded but not approved:

- **P-1:** Use strict provider-prefix matching for native-provider compatibility (teammate preference). Compatibility consequence: `gpt-4.1` and `anthropic.claude-3` would be rejected for native `openai`/`anthropic` search unless the caller writes an explicit prefix.
- **P-2:** Adopt the runtime MCP stop-and-error policy as REQ-007 behaviour (see U-1).
- **P-3:** Replace the dead guard with `has_search_capability` (see U-4).
- **P-4:** Introduce the MCP load adapter returning `McpLoadResult` so the four runtime outcomes are distinguishable (see U-5).

- **Rollback:** remove the two call sites and the `search` module; nothing in the baseline depends on it, so removal restores the pre-change behaviour.

## 13. Modules and Documents to Update at Integration

`evaluation-table.md` (EVAL-001), `trace-matrix.md` (REQ-007 row), `invariants.md` (INV-005), `structural-constraints.md` §10, `verification-constraints.md` §7, `runtime-policy-catalog.md` (`POL-002`). `memory-design.md` does not change (no state).
