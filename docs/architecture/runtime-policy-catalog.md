# Runtime Policy Catalog

> **Purpose:** What the research agent does at runtime when something goes wrong: exceptions, retries, degradation and failure paths.
> **Authoritative for:** runtime handling policies. Each policy traces to a requirement or invariant.
> **Maintained by:** owners of modules with exception, retry, degradation or failure handling write a module section (§2); §1 is integrated from those sections before SA Review. Modules without such handling add nothing.
> **Last updated:** 2026-11-13

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

### context (REQ-005, ADR-005)

All three policies apply only while `Configuration.context_trimming` is `True`; while it is `False` the baseline behaviour is unchanged.

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-001 | Compress call exceeds the token limit and whole turns can still be removed | `classify_token_limit(exc, compression_model)` returns `True` and `plan_trim()` returns a `TrimPlan` | Drop the oldest removable research turn as a whole (`AIMessage` + the `ToolMessage`s whose `tool_call_id` it issued), keep the preamble/topic, the instruction and the newest turn, then retry the call | One turn removed per attempt (`max_removals_per_attempt = 1`); the loop continues until no removable turn is left, so the budget is derived from the history rather than fixed at three; degradation is lossy only for the removed turns | None on its own: a later successful attempt returns a normal summary, so the run outcome is unaffected | REQ-005 C-001, INV-001 | `test/offline/test_context_compaction.py::test_oldest_turns_removed_first` |
| POL-002 | Compress call exceeds the token limit and nothing removable is left | `plan_trim()` returns `None` | Raise `TokenLimitExceeded(attempts, removed_turn_indices, last_exception)`; `compress_research` returns it as `research_outcome` (status `failed`, category `token_limit`) alongside `compressed_research` and `raw_notes` | No further retry. No fallback text on the new path; the raise is not propagated out of the subgraph, because `asyncio.gather` at L305 would discard every parallel researcher's result | Counts as a failed research task; the run can no longer be `complete` and degrades to `partial` or `failed` per REQ-004 | REQ-005 C-004, INV-001 | `test/offline/test_context_compaction.py::test_unreducible_history_ends_failed` |
| POL-003 | Compress call raises an error that is not a token-limit error | `classify_token_limit(...)` returns `False` | Retry the unchanged request, as the baseline does, so transient 429/5xx errors still recover; no trimming | Retried until the attempt budget is spent; then fails through the same `research_outcome` path with a category owned by REQ-001 (not `token_limit`). The exception is not re-raised | Handled locally instead of by the researcher/supervisor failure path, because re-raising would escape into `asyncio.gather` (L305) and discard every parallel researcher's result | REQ-005 (scope boundary), ADR-005 §6 | `test/offline/test_context_compaction.py::test_non_token_errors_are_retried` |

Classification note: `classify_token_limit` is always called with `configurable.compression_model`, never with `research_model`; this is what fixes REQ-005 C-003 and is asserted by `test_classification_uses_compression_model`.
