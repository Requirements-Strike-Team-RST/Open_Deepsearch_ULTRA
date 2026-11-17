# Runtime Policy Catalog

> **Purpose:** What the research agent does at runtime when something goes wrong: exceptions, retries, degradation and failure paths.
> **Authoritative for:** runtime handling policies. Each policy traces to a requirement or invariant.
> **Maintained by:** owners of modules with exception, retry, degradation or failure handling write a module section (§2); §1 is integrated from those sections before SA Review. Modules without such handling add nothing.
> **Last updated:** 2026-11-12

## 1. Policies

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Module | Source | Test |
|---|---|---|---|---|---|---|---|---|
| POL-001 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## 2. Module Sections

Copy the example for your module and number policies with the next free `POL-NNN`; numbers are unified at integration.

### <Module> (REQ-NNN, ADR-NNN)

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-NNN | e.g. a researcher raises an exception | how deterministic code recognises it | what the system does | retries, limits, fallback, or none | effect on the run outcome (`complete`, `partial`, `failed`, REQ-004) | REQ-NNN / INV-NNN | `test/offline/<file>::<test>` |

### search (REQ-007, ADR-001) — proposed, awaiting approval

The entries below are **proposed** and are not approved until SA Review and the human decide them (ADR-001 §9, U-1). They introduce no fallback behaviour; fallback belongs to REQ-008 and is out of scope. Implementation **depends** on the MCP load adapter or refactor in ADR-001 §8.1a (U-5): the current `load_mcp_tools` returns an empty list for every failure, so the three failure states are not distinguishable today.

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-002 | A declared MCP is the effective search source (`search_api=none` with `MCP_DECLARED`) and cannot provide a usable search tool at runtime | `McpLoadResult.status` is `LOAD_FAILED` (connection/loading failure), `ZERO_USABLE_TOOLS` (loaded but none match), or `AUTH_MISSING` (required token unresolvable). Requires the ADR-001 §8.1a adapter/refactor (U-5); not available in the current `load_mcp_tools` | Stop the affected research and raise an explicit error naming the cause (and `mcp_config.url`); no source substitution | None | Research for the affected task fails explicitly; no silent no-search run; a `LOADED` tool that returns no hits is not this policy and remains a success | REQ-007 / INV-005 (Proposed) | planned: `test/offline/test_search_configuration.py` (TC-016, TC-017, TC-018, TC-024) |

### search (REQ-008, ADR-002) — proposed, awaiting approval

The policy below is **proposed** and not approved until SA Review (ADR-002, EVAL-002). It introduces no change to native model search (out of scope) and does not amend POL-002.

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-003 | A search invocation on a configured client-side source (Tavily or a configured MCP search tool) fails, or a source is unavailable at load time, while an ordered fallback list is configured | Error classification in the fallback coordinator (ADR-002 §7) using typed exceptions, structured error codes or documented status metadata — not generic message matching. Eligible = timeout, connection, rate limit, provider server error, rejected credential at invocation; ineligible = e.g. malformed query, unclassifiable (default ineligible). Load-stage unavailability is recorded as `SearchAttemptFailure(stage=LOAD)` — the source was never invoked | Try the next configured source in order on an eligible invocation failure; stop immediately on an ineligible failure; on a source unavailable at load the recorded `stage=LOAD` failure is included in the aggregate (run-terminating behaviour subject to the pending D-1 exception below); an empty result is a success and stops fallback; when every source fails, return `AllSourcesFailed` listing each attempted source, its stage and its error | None (sequential, no parallel, no source substitution); missing authentication *configuration* is a configuration failure and is not retried; a credential rejected at invocation is eligible and does not trigger automatic credential recovery | Research receives either a successful result (from any source, used identically), the empty-success result, an ineligible failure, or an explicit all-sources-failed result distinct from the empty marker; never a fabricated result | REQ-008 / INV-006, INV-007, INV-008, INV-009 (Proposed) | planned: `test/offline/test_search_fallback.py` (REQ-008 cases, TC-027 onward) |

**Proposed exception to POL-002 — Pending Team Approval.** POL-002 currently stops the run unconditionally when a declared MCP cannot provide a usable tool. The proposed REQ-008 policy narrows this only for a **fallback** MCP source: when a declared fallback source fails at **load** stage and other validated, usable sources remain, the load failure is recorded and fallback continues instead of terminating the run; when no usable source remains, the run stops as POL-002 describes. This amendment is **not applied** to POL-002 here; it requires team approval (ADR-002 D-1; related REQ-007 U-1 and U-5). Until approved, POL-002 stands as written.
