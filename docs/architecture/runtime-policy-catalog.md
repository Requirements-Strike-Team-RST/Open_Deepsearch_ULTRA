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

### search (REQ-007, ADR-001) — deferred, not approved

The entries below record an open question. They are **not** approved policies and must not be implemented until SA Review and the human decide them.

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-DEF-001 | `mcp_config` is a valid declaration (`MCP_DECLARED`) but `utils.load_mcp_tools` returns zero tools at runtime, while `search_api=none` | `get_all_tools` yields only `ResearchComplete`/`think_tool` although a valid MCP declaration exists | TBD — no guard implemented (ADR-001 §12 U-1); today the run proceeds with no search | None | TBD | REQ-007 / INV-005 (Proposed) | none yet |
