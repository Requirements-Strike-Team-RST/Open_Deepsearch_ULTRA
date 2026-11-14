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
| POL-001 | Compress call exceeds the token limit and whole turns can still be removed | `classify_token_limit(exc, compression_model)` returns `True` and `plan_trim()` returns a `TrimPlan` | Drop the oldest removable research turn as a whole (`AIMessage` + its `ToolMessage`s), keep the preamble/topic, the instruction and the newest turn, then retry the call | At most 3 attempts (`max_attempts`), one turn removed per attempt by default (`max_removals_per_attempt = 1`); degradation is lossy only for the removed turns | None on its own: a later successful attempt returns a normal summary, so the run outcome is unaffected | REQ-005 C-001, INV-001 | `test/offline/test_context_compaction.py::test_oldest_turns_removed_first` |
| POL-002 | Compress call exceeds the token limit and nothing removable is left, or the attempt budget is exhausted | `plan_trim()` returns `None`, or `attempt == max_attempts` after a token-limit error | Raise `TokenLimitExceeded(attempts, removed_turn_indices, last_exception)`; `compress_research` maps it to a REQ-001 task result with status `failed` and category `token_limit` and returns no summary text | No further retry. No fallback text; the placeholder literal is removed | Counts as a failed research task; the run can no longer be `complete` and degrades to `partial` or `failed` per REQ-004 | REQ-005 C-004, INV-001 | `test/offline/test_context_compaction.py::test_unreducible_history_ends_failed` |
| POL-003 | Compress call raises an error that is not a token-limit error | `classify_token_limit(...)` returns `False` | Re-raise the original exception unchanged; the module does not retry and does not trim | None in this module | Handled by the researcher/supervisor failure path owned by REQ-002 and reported by REQ-004; this module never converts it into a summary | REQ-005 (scope boundary), ADR-005 §3(d) | `test/offline/test_context_compaction.py::test_non_token_error_is_propagated` |

Classification note: `classify_token_limit` is always called with `configurable.compression_model`, never with `research_model`; this is what fixes REQ-005 C-003 and is asserted by `test_classification_uses_compression_model`.
