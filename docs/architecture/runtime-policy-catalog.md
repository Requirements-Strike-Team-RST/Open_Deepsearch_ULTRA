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

### evaluation (REQ-009, REQ-010, ADR-001)

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-002 | The evaluation entry receives a non-string, blank or whitespace-only question or report | Type and `str.strip()` checks on both required inputs before any judge call | Raise `EvaluationInputError`; the CLI writes `error: ...` to stderr and exits `2` | None; no evaluator or judge call | N/A (evaluation-only, not a research run) | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |
| POL-003 | A metric's optional input is absent or blank: reference answer, research brief or evidence | Presence and non-blank check before the metric's judge call | Mark only the dependent metric `not_evaluable`; evaluate the other metrics | None | N/A | REQ-009 C-003 / INV-006 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |
| POL-004 | The judge returns a rating that is not a strict integer `1..5` | `type(raw_value) is int` and range check on the raw value before Pydantic or other type conversion; booleans, floats including `4.0`, strings, `None` and non-finite values are rejected | Mark that metric `not_evaluable` with `score=None` and `invalid_rating`; do not clamp or default | None; the metric is not retried into a score | N/A | REQ-009 C-002, M-001 / INV-006 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| POL-005 | The judge extracts no claim for groundedness | Non-empty list check before the ratio | Mark groundedness `not_evaluable` with `score=None` and `no_claims` | None | N/A | REQ-009 C-004 / INV-006 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |
| POL-006 | A judge call or evaluator raises an exception | `try/except Exception` around each metric group | Mark only that group's metrics `not_evaluable` with `evaluator_error`; continue the other groups | No module-level retry; provider retries are outside this policy | N/A | REQ-009 C-004 / INV-006 | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |
| POL-007 | The CLI receives an argument or report-file error | Argument parsing and file read before evaluation | Write `error: ...` to stderr; no evaluator runs; exit `2` | None | N/A | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |
| POL-008 | A CLI evaluation completes with every metric `not_evaluable` | Scan the returned metric statuses | Print the JSON result on stdout, notify on stderr and exit `1`; exit `0` when at least one metric is `scored` | None | N/A | REQ-009 / REQ-010 | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |
