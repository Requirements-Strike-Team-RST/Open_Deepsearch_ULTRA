# ADR-001: Evaluation module — valid metric results and an evaluation-only entry

- **Status:** Proposed
- **Date:** 2026-11-13
- **Module:** evaluation
- **Owner:** DopplerXD
- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), to be assigned at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-009 | C-001, C-002, C-003, C-004, M-001 | The judge must receive every metric input; scores must come only from a strict integer rating `1..5` or a groundedness ratio over at least one claim; missing inputs, empty claims and evaluator exceptions must not abort the other metrics. REQ-009 is `safety_relevant`, so validation and normalisation are deterministic code. |
| REQ-010 | C-001, C-002, C-003 | An existing report must be evaluable without compiling or invoking the research graph, calling a search provider or generating a replacement report; blank input must be rejected before any evaluator runs. The entry is therefore a separate component with an import boundary, not a new graph target. |

## 2. Context

The evaluation code is a set of LangSmith evaluator functions in `test/evaluators.py`; `test/run_evaluate.py` passes them to `Client.aevaluate`. The baseline has these defects:

- `test/evaluators.py` L17-19 constructs `ChatOpenAI(model="gpt-4.1")` at module import. Importing the module therefore has a model-client side effect even when no evaluation runs.
- `CORRECTNESS_PROMPT` in `test/prompts.py` L95-104 contains no placeholder, so `eval_correctness` at `test/evaluators.py` L199-201 formats the question, report and reference answer into nothing. The judge never sees the inputs its metric is defined over.
- Ratings declared as integers `1..5` are divided by `5` without validation at `test/evaluators.py` L90-98, L140, L179, L219 and L312. A rating of `0`, `6`, a boolean, a string, a fraction or a non-finite number produces an out-of-range or invalid score.
- `eval_groundedness` at `test/evaluators.py` L265-270 divides by `len(claims)` and raises `ZeroDivisionError` when the judge extracts no claim.
- Missing `reference_outputs["answer"]`, `raw_notes` or `research_brief` raises `KeyError` at `test/evaluators.py` L196-198, L239-244 and L286-293; there is no failure isolation, so one broken metric prevents the remaining metrics from being reported.
- `test/run_evaluate.py` L32-61 compiles and invokes the full research graph for every dataset example; L9-11 also runs `load_dotenv("../.env")` and constructs a LangSmith `Client` at import. There is no entry that scores an already generated report.

The blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. This conflicts with `structural-constraints.md` §1, which lists top-level `test/` as “No” for new work; the conflict is recorded as a module-review question in `structural-constraints.md` §10 and must be confirmed before SA acceptance, not silently resolved here. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The design keeps evaluation logic in `test/evaluation/` and leaves `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter.

## 3. Decision

Adopt **option B**: a `test/evaluation/` package containing the evaluation types, validation, judge access, metric evaluation and the evaluation-only entry, plus a compatibility adapter in `test/evaluators.py`.

### 3.1 Package layout

```text
test/evaluation/
  __init__.py           # public exports
  types.py              # MetricStatus, MetricResult, EvaluationResult, EvaluationInputError
  validation.py         # strict rating, groundedness ratio, input-presence checks
  judge.py              # Judge protocol and lazy default judge
  metrics.py            # metric groups, normalisation, per-group failure isolation
  entry.py              # evaluate_existing_report(...)
  evaluate_report.py    # CLI entry point
test/evaluators.py      # compatibility adapter only; no evaluation logic
```

### 3.2 Types and result contract

`MetricStatus` has exactly two values: `scored` and `not_evaluable`. A `MetricResult` states `metric`, `status`, `score`, `reason` and a machine-readable `reason_code`. Its invariant is: `score` is a `float` in `[0, 1]` when and only when `status == "scored"`; otherwise `score is None`. Scored results use `judge_rating` or `grounded_ratio`; `not_evaluable` results use `invalid_rating`, `missing_input`, `no_claims`, `invalid_claim` or `evaluator_error`.

`EvaluationResult` states `report_id`, the tuple of `MetricResult` objects and `judge_model`. `report_id` is the lowercase hexadecimal SHA-256 of the original report text encoded as UTF-8. There is no caller-supplied report id in the first version. `judge_model` is the model identifier of the default judge, or `None` when a caller injected a judge.

`EvaluationInputError(ValueError)` is raised when the entry's required question or report is blank. It is not a metric result: no evaluator may run before it is raised.

### 3.3 Metric names

The public metric names preserve the baseline LangSmith keys: `research_depth_score`, `source_quality_score`, `analytical_rigor_score`, `practical_value_score`, `balance_and_objectivity_score`, `writing_quality_score`, `relevance_score`, `structure_and_cohesiveness_score`, `correctness_score`, `groundedness_score` and `completeness_score`. The six overall-quality dimensions are six independent metric results, not one aggregate.

### 3.4 Inputs per metric

- Question and report: all metrics except groundedness; the entry requires both to be non-blank.
- Reference answer: correctness only.
- Research brief: completeness only.
- Evidence (`raw_notes` equivalent): groundedness only.

If an optional input is missing or blank, only the metrics that require it become `not_evaluable`; the other metrics are still evaluated. If the question or report is missing in the LangSmith adapter, every metric that needs it becomes `not_evaluable` and the adapter does not raise.

### 3.5 Strict rating validation

The raw judge rating must be validated before any Pydantic or other type conversion. The judge response schema therefore keeps rating fields as raw values (`Any`, or the raw structured tool-call arguments); it must not declare them as `int`, because Pydantic's default lax mode would coerce `4.0` and `"4"` to `4` and hide an invalid rating. `validation.validate_rating(raw_value)` performs the first check: `type(raw_value) is int` and `1 <= raw_value <= 5`. Booleans, floats including `4.0`, strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `raw_value / 5`. An invalid rating produces `status="not_evaluable"`, `score=None` and `reason_code="invalid_rating"`. Scores are never clamped, rounded, defaulted or replaced by zero.

Groundedness is the only ratio metric: the judge's claims must be a non-empty list; the score is `grounded_count / total_claims`; an empty list produces `status="not_evaluable"` with reason code `no_claims`. A claim whose `grounded` field is not a boolean makes the metric `not_evaluable` rather than being coerced.

### 3.6 Failure isolation

Metric groups are evaluated independently. A group is one judge call and the metrics it produces: overall quality produces six metrics from one call; each other evaluator produces one metric from one call. An exception in a group makes only that group's metrics `not_evaluable` with a reason code such as `evaluator_error`; the remaining groups still run. The implementation catches `Exception`, never `BaseException`, so interruption and process exit are not swallowed.

### 3.7 Evaluation-only entry

`evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`:

1. Rejects a non-string, blank or whitespace-only `question` or `report` with `EvaluationInputError` before any judge call.
2. Computes `report_id` as the SHA-256 of the supplied report text; the report text is passed to the judge unchanged.
3. Runs the metric groups against the supplied inputs.
4. Returns `EvaluationResult`; it never compiles or invokes the research graph, imports `open_deep_research.deep_researcher`, calls a search provider or generates a replacement report.

`Judge` is a protocol with `invoke(messages, schema) -> Mapping[str, object]`, returning the raw structured field values so rating values reach `validation.py` before any typed conversion. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key.

### 3.8 CLI

`python -m test.evaluation.evaluate_report --report <path> --question <text>` accepts optional `--reference-answer`, `--research-brief` and `--evidence`. It prints the result as JSON on stdout. Exit codes are:

| Code | Meaning |
|---|---|
| `0` | Evaluation completed and at least one metric is `scored`. |
| `1` | Evaluation completed but every metric is `not_evaluable`. |
| `2` | Input, argument or report-file error; the message is written to stderr as `error: ...` and no evaluator runs. |

The README gains a short section showing the command and how to read the per-metric result (REQ-010 C-003).

### 3.9 LangSmith compatibility adapter

`test/evaluators.py` keeps the six baseline function names and signatures and delegates to `test/evaluation`. It removes the module-level `eval_model` and does not construct a client at import. `overall_quality` still returns a list of six dictionaries; the other evaluators return one dictionary. Each dictionary keeps `key`, `score` and `comment` and adds `status` in `metadata`.

The conversion is:

```python
# scored
{"key": "correctness_score", "score": 0.8, "comment": "<reason>",
 "metadata": {"status": "scored"}}

# not_evaluable
{"key": "groundedness_score", "score": None, "value": "not_evaluable",
 "comment": "not_evaluable:no_claims: <detail>",
 "metadata": {"status": "not_evaluable", "reason_code": "no_claims"}}
```

`score=None` is permitted by the LangSmith `EvaluationResult` score type and by `create_feedback`. `not_evaluable` must never be converted to `0`: a null score is not counted as a numeric score, while `value` and `metadata` keep the status and reason visible. If a whole evaluator group fails before producing any metric, the adapter returns every key that group owns as `not_evaluable`, so LangSmith still sees all metric keys.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — harden `test/evaluators.py` in place and add a separate entry file | Keeps judge construction, validation, LangSmith serialisation and entry logic in one module; the import side effect and the mixing of adapter and core logic remain, and pure validation is harder to test offline. |
| C — duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | Two sources of truth for the same metrics; the REQ-009 fixes would not reach the benchmark path; violates the “extend, never replace” rule and doubles maintenance. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `test/evaluation/types.py` | Result and error types | `MetricStatus`, `MetricResult`, `EvaluationResult`, `EvaluationInputError` | all evaluation components; adapters |
| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(raw_value) -> float` (raises `InvalidRating`), `groundedness_ratio(claims) -> float` (raises `NoClaims`/`InvalidClaim`), `require_text(value) -> bool` | `metrics.py`, `entry.py` |
| `test/evaluation/judge.py` | Judge boundary; lazy model construction and raw structured output | `Judge.invoke(messages, schema) -> Mapping[str, object]`, `default_judge() -> Judge` | `metrics.py`, `entry.py` |
| `test/evaluation/metrics.py` | Run metric groups, normalise and isolate failures | `evaluate_metrics(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> tuple[MetricResult, ...]` | `entry.py`, `test/evaluators.py` |
| `test/evaluation/entry.py` | Evaluation-only public entry | `evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult` | CLI, callers, `test/evaluators.py` |
| `test/evaluation/evaluate_report.py` | CLI and exit-code handling | `main(argv=None) -> int`; `python -m test.evaluation.evaluate_report` | humans, scripts |
| `test/evaluators.py` | Baseline LangSmith adapter | `eval_overall_quality(inputs, outputs)`, `eval_relevance(inputs, outputs)`, `eval_structure(inputs, outputs)`, `eval_correctness(inputs, outputs, reference_outputs)`, `eval_groundedness(inputs, outputs)`, `eval_completeness(inputs, outputs)` | `test/run_evaluate.py` |
| `test/prompts.py` | Judge templates | `CORRECTNESS_PROMPT` gains `{user_question}`, `{report}`, `{answer}` and `{today}` placeholders | `metrics.py` |

**Shared contracts changed (`structural-constraints.md` §6):** none. The module adds no `state.py` type and no graph state field. The baseline LangSmith evaluator key and return-shape contract is preserved by the adapter; `test/run_evaluate.py` does not change.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none. The module does not add or change graph state; `memory-design.md` §5 has no evaluation entry.
- **Runtime policies:** POL-002 to POL-008 (`runtime-policy-catalog.md` §2), covering blank input, missing optional input, invalid rating, empty claims, evaluator exception and CLI exit codes.
- **Invariants:** INV-006 (valid or `not_evaluable` metric results) and INV-007 (evaluation-only entry does not run research or search).
- **Deterministic boundary:** the model supplies ratings and claim judgements only. Deterministic code decides whether the rating is a valid integer `1..5`, whether the normalised score is in `[0, 1]`, whether at least one claim exists, whether required inputs are present, whether a metric is `not_evaluable` and whether an exception stays local to its metric group.

## 7. Verification

| Requirement and criterion | Verification |
|---|---|
| REQ-009 C-001 | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |
| REQ-009 C-002 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| REQ-009 C-003 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |
| REQ-009 C-004 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors`, `::test_one_metric_error_does_not_abort_others` |
| REQ-009 M-001 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| INV-006 | `test/offline/test_evaluator_validity.py` (all cases; no out-of-range score, no score on `not_evaluable`) |
| REQ-010 C-001 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research`, `::test_entry_identifies_report` |
| REQ-010 C-002 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected`, `::test_cli_blank_input_exit_code` |
| REQ-010 C-003 | manual review recorded as `REVIEW-NNN` in `docs/review-memo.md` |
| INV-007 | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |

**Verification basis and status.** LangSmith compatibility was checked on 2026-11-13 against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output and feedback documentation. This is a type-contract check only; no live `aevaluate` call, experiment run or UI check was performed. The live check and all behavioural tests remain `NOT_RUN`; SA Review and Gate 2 are also not performed.

The module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7.

## 8. Consequences

**Positive.** Every metric either carries a defensible score in `[0, 1]` or an explicit `not_evaluable` result with a reason. Correctness receives the question, report and reference answer. A single broken metric no longer hides the others or crashes a run. Existing reports can be scored without spending research tokens or calling search. Offline tests can inject a fake judge and run without network or keys. The benchmark entry keeps its evaluator names and return shapes.

**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change.

**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.

**Open for module review.** `structural-constraints.md` §1 lists top-level `test/` as “No” for new work, while `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm the exception at module review and integration; §1 is human-owned and is not edited by this ADR.

## 9. Implementation Steps

Tests for §7 are written by the Test Author after Gate 1; the steps below are the Build work that follows Gate 2.

1. Create `test/evaluation/__init__.py` and export the public types and `evaluate_existing_report`.
2. Add `test/evaluation/types.py`: `MetricStatus`, `MetricResult`, `EvaluationResult` and `EvaluationInputError`, with the score/status invariant.
3. Add `test/evaluation/validation.py`: strict `1..5` integer validation on the raw value before any conversion, `raw_value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats including `4.0`, strings, `None` and non-finite values.
4. Add `test/evaluation/judge.py`: the `Judge` protocol that returns raw structured field values, and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. Do not declare rating fields as `int`; no model construction at import.
5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Call `validate_rating` on the raw judge value before constructing a `MetricResult`, and map `InvalidRating` to `not_evaluable` with `invalid_rating`. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.
6. Add `test/evaluation/entry.py`: `evaluate_existing_report`, blank-input rejection before the judge, SHA-256 `report_id`, and the no-research/no-search import boundary.
7. Add `test/evaluation/evaluate_report.py`: the CLI, JSON output and exit codes `0/1/2`; write input errors to stderr as `error: ...`.
8. In `test/prompts.py`, add `{user_question}`, `{report}`, `{answer}` and `{today}` to `CORRECTNESS_PROMPT`; do not change its rubric wording.
9. Replace the bodies of the six functions in `test/evaluators.py` with adapter calls; remove the module-level `eval_model`; preserve names, signatures, baseline keys, the six-item list for overall quality and the single-dict shape for the others; add `status` metadata and the null-score/`value="not_evaluable"` mapping.
10. Add the README section for `python -m test.evaluation.evaluate_report` and the per-metric result (REQ-010 C-003).
11. Add `"test.evaluation"` to `[tool.setuptools] packages` in `pyproject.toml`; the dependency-file change is accepted for the implementation PR and is not made in this SA change.
12. Run `uv run ruff check test/evaluation test/evaluators.py test/prompts.py` and `uv run pytest test/offline` after the Test Author's tests exist. Do not modify `test/run_evaluate.py`, `src/` or the tests.
