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

### delivery (REQ-002, REQ-004, ADR-001)

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-001 | A researcher raises a non-token-limit exception | `classify_task_error` after `asyncio.gather(..., return_exceptions=True)` collects the exception instead of raising it | Only that task ends `failed` with category `runtime` and `str(exc)` as the message; siblings keep their results; the phase continues and control returns to the supervisor | None in this delivery: a failed task is not retried automatically and not re-planned. The supervisor may re-delegate within `max_researcher_iterations` | `partial` if other tasks produced findings, `failed` if none did | REQ-002 C-001, C-002 / INV-002 S1, S2 | `test/offline/test_failure_propagation.py::test_child_exception_becomes_failed_result` |
| POL-002 | A researcher raises an error that `is_token_limit_exceeded(exc, research_model)` recognises | provider-specific token-limit patterns in `utils.is_token_limit_exceeded`, with the error string as fallback when the provider is unknown | Only that task ends `failed` with category `token_limit`; the research phase does not end, because a researcher's context limit says nothing about the supervisor's | Compression-side recovery belongs to REQ-005 (`context/`), not here. If compression still cannot fit, the task result is `token_limit` all the same | Same rule as POL-001 | REQ-002 C-003 / INV-002 S1 | `::test_token_limit_error_is_task_failure` |
| POL-003 | A supervisor turn holds more `ConductResearch` calls than `max_concurrent_research_units` | `len(specs) > max_concurrent` in `run_delegations` | The delegations are queued and run in successive batches of `max_concurrent`; every one of them ends with a `TaskResult`. The baseline error string for overflow is no longer produced | No retry. Batching keeps peak concurrency at the configured limit, so rate-limit pressure is unchanged | `partial` only if some of the queued tasks still fail | REQ-002 C-004 / INV-006 | `::test_overflow_delegations_are_queued` |
| POL-004 | The research loop exits while a delegation from the current turn has not run (iteration cap reached, or the loop ends without dispatching the turn's calls) | the delegations of the ending turn are passed to `run_delegations` as unrun specs with `unrun_reason="not_run"` | Each such delegation ends `failed` with reason `not_run`, and a `ToolMessage` carries its `TaskResult` so no supervisor tool call is left unanswered | No retry | `partial` when other tasks produced findings, `failed` when none did | REQ-002 C-005 / INV-006 | `::test_delegations_left_at_exit_are_failed` |
| POL-005 | The final report model raises an error that is not a token limit | `final_report_generation` catches the exception and passes it to `evaluate_after_report` | The run ends `failed` with the error in the failure fields; `final_report` is empty and the error text is not returned as report content | The baseline retry loop is kept for token-limit errors only; a non-token-limit error is not retried, because it usually indicates a credential, model-name or request defect | `failed` | REQ-004 C-005 / INV-002 S5, S6 | `test/offline/test_run_outcome.py::test_report_error_run_is_failed` |
| POL-006 | The findings exceed the report model's token limit and are shortened to fit | the truncation branch of `final_report_generation` sets `truncated=True` instead of silently slicing `findings` | The findings that were withheld are recorded, the report is generated from the rest, and the outcome becomes `partial` with a limitations line stating that findings were left out | Progressive truncation retries stay as in the baseline (first to the model limit, then 10% less per retry), bounded by the existing `max_retries` | `partial`, never `complete` | REQ-004 C-006 / INV-002 S5, S6 | `::test_truncated_findings_make_run_partial` |
| POL-007 | The research phase produced no validated finding at all | `evaluate_before_report` finds the source findings empty | The outcome is `failed`, `report_allowed` is `False`, the report model is never called and `final_report` stays empty; the limitations text names the failed tasks that caused it | None | `failed` | REQ-004 C-004 / INV-002 S5 | `::test_no_finding_run_is_failed` |
