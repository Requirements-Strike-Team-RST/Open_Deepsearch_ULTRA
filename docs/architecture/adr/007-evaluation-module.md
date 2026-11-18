# ADR-007: Valid metric results and an evaluation-only entry

- **Status:** Proposed
- **Date:** 2026-11-17
- **Module:** evaluation
- **Owner:** DopplerXD
- **Evaluation:** EVAL-007 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-009 | C-001 | Each judge request must contain every input its metric uses. |
| REQ-009 | C-002, C-003, C-004, M-001 | A score comes only from a valid integer rating 1–5 or a groundedness ratio over at least one claim; anything else is `not_evaluable`, and one failing metric never stops the others. This must be deterministic code (`safety_relevant: true`). |
| REQ-010 | C-001, C-002 | An existing report must be scored without running research or search, and blank input must be rejected before any evaluator runs. The entry must not import the research graph. |
| REQ-010 | C-003 | The entry must be documented in the README. |

## 2. Context

Baseline (`test/`, line numbers at commit `daf6947`):

- `evaluators.py` L17-19 creates `ChatOpenAI(model="gpt-4.1")` at import time.
- `prompts.py` L95-104: `CORRECTNESS_PROMPT` has no placeholders, so the judge never sees the question, report or reference answer (`evaluators.py` L195-219).
- `evaluators.py` L90-98, L140, L179, L219, L312 divide ratings by 5 without a range check.
- `evaluators.py` L265-270: groundedness divides by the number of claims and raises `ZeroDivisionError` when there is none.
- Missing `reference_outputs["answer"]`, `raw_notes` or `research_brief` raises `KeyError` (L196-198, L239-244, L286-293), which stops the remaining metrics.
- `run_evaluate.py` L32-61 always runs the full research graph; there is no way to score an existing report.
- `open_deep_research.utils` imports the Tavily and MCP clients, so the evaluation code must not import it.

## 3. Decision

Use EVAL-007 option B: a small package `test/evaluation/` holds the logic; `test/evaluators.py` becomes a thin adapter that keeps the LangSmith function names and return shapes, so `test/run_evaluate.py` does not change.

**Metric results.** `MetricResult(metric, status, score, reason)`, where `status` is `scored` or `not_evaluable`. `score` is a float in `[0, 1]` when `scored` and `None` otherwise. The metric names stay the baseline LangSmith keys (`research_depth_score`, ..., `correctness_score`, `groundedness_score`, `completeness_score`).

**Rating validation.** The judge schemas keep their types (`score: int`, `grounded: bool`) so that the JSON schema sent to the judge stays typed, but they use Pydantic strict mode (`model_config = ConfigDict(strict=True)`). In lax mode Pydantic would silently turn `4.0` or `"4"` into `4` and `"true"` into `True`; in strict mode these values fail to parse, and a parse failure makes the metric `not_evaluable`. `validate_rating(raw)` then accepts only `type(raw) is int` and `1 <= raw <= 5` and returns `raw / 5`; otherwise it raises `InvalidMetricInput` (a `ValueError`). Booleans, floats (including `4.0`), strings, `None`, `NaN` and infinities make the metric `not_evaluable`. Scores are never clamped or defaulted to zero.

**Groundedness.** The claim list must be non-empty and each `grounded` value must be a real boolean; the score is grounded claims / all claims. Otherwise `groundedness_ratio` raises `InvalidMetricInput` and the metric is `not_evaluable`.

**Inputs.** Each prompt receives exactly the inputs of its metric: the question and the report for every metric (REQ-009 names both for each evaluator, so groundedness gets the question too); plus the reference answer for correctness, the research brief for completeness, and the evidence (raw notes) for groundedness. `CORRECTNESS_PROMPT` gains `{user_question}`, `{report}`, `{answer}` and `{today}`; `{today}` comes from a small standard-library date helper in `metrics.py`, because the module must not import `utils.get_today_str`. A missing or blank optional input makes only the metrics that need it `not_evaluable`.

**Failure isolation.** Each judge call (one metric group) runs in its own `try/except Exception`. An exception makes only that group's metrics `not_evaluable`; the other groups still run.

**Evaluation-only entry.** `evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`:

1. rejects a non-string or blank `question` or `report` with `EvaluationInputError` before any judge call;
2. uses the injected `judge`, or creates the default judge (the baseline `ChatOpenAI` model) on first use;
3. returns `EvaluationResult(report_id, metrics)`, where `report_id` is the SHA-256 of the report text, so the result identifies the report that was scored.

It never imports `open_deep_research.deep_researcher` or `open_deep_research.utils`, never builds the research graph and never calls a search provider. The command `python -m test.evaluation.entry --question ... --report <file>` prints the result as JSON and exits with `0`, or with `2` on an input error.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — fix `test/evaluators.py` in place and add an entry script | Validation, judge creation and LangSmith formatting stay mixed, and the import-time model client is hard to remove. |
| C — a separate evaluation service next to the old evaluators | Two copies of every metric; the REQ-009 fixes would not reach the benchmark path. |
| Six files with special exit codes for HTTP 401/403 (an earlier draft) | Not required by REQ-009 or REQ-010; an authentication error is an evaluator error like any other. |

The full comparison is in EVAL-007.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `test/evaluation/metrics.py` | Result type, validation, metric groups, default judge | `MetricResult`; `InvalidMetricInput(ValueError)`; `validate_rating(raw) -> float`; `groundedness_ratio(claims) -> float` (both raise `InvalidMetricInput`, which `evaluate_metrics` turns into `not_evaluable`); `evaluate_metrics(question, report, *, reference_answer, research_brief, evidence, judge) -> list[MetricResult]`; `default_judge()` | `entry.py`, `test/evaluators.py` |
| `test/evaluation/entry.py` | Evaluation-only entry and command line | `evaluate_existing_report(...) -> EvaluationResult`; `EvaluationInputError`; `main(argv=None) -> int` | users, scripts |
| `test/evaluators.py` | LangSmith adapter | the six baseline functions; every result's `comment` starts with its status (`scored:` or `not_evaluable:`); a `not_evaluable` metric has `score=None` and the reason in `comment` | `test/run_evaluate.py` |
| `test/prompts.py` | Judge templates | `CORRECTNESS_PROMPT` gains its placeholders | `metrics.py` |

Exceptions to the general rules, recorded in blueprint §6: new code under `test/evaluation/` (`structural-constraints.md` §1), and one evaluation-only judge client created in `metrics.py` (§4), because the shared model lives in `deep_researcher.py`, which this module must not import.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none.
- **Runtime policies:** POL-020 to POL-023.
- **Invariants:** INV-009.
- **Deterministic boundary:** the judge supplies ratings and claim judgements; code decides whether they are valid and what the score is.

## 7. Verification

Cases in `verification-constraints.md` §7 (evaluation). All use a fake judge and need no network or keys. REQ-010 C-003 is a human review of the README, recorded in `docs/review-memo.md`.

## 8. Consequences

- **Positive:** every score is valid or explicitly `not_evaluable`; correctness sees its inputs; one broken metric no longer hides the others; existing reports can be scored without research cost.
- **Negative:** `not_evaluable` metrics have no number, so they drop out of LangSmith averages (RISK-011).
- **Neutral:** `test/run_evaluate.py` and the research graph are unchanged; `pairwise_evaluation.py`, `supervisor_parallel_evaluation.py` and `extract_langsmith_data.py` are out of scope.

## 9. Implementation Steps

1. Add `test/evaluation/__init__.py`, `metrics.py` and `entry.py`; add `test.evaluation` to `[tool.setuptools] packages`. Docstrings name `REQ-009` or `REQ-010`, `ADR-007`, `INV-009`.
2. `test/prompts.py`: add the placeholders of §3 to `CORRECTNESS_PROMPT`; keep the rubric text.
3. `test/evaluators.py`: remove the module-level model; make the six functions call `evaluate_metrics` and keep their names, signatures and return shapes.
4. Add a README section with the command, how to read the per-metric result and the exit codes (REQ-010 C-003).
5. Run `uv run ruff check test/evaluation test/evaluators.py test/prompts.py` and `uv run pytest test/offline`; record them in `docs/build-reports/REQ-009.md` and `REQ-010.md`.
