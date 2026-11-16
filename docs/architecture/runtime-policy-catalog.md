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
