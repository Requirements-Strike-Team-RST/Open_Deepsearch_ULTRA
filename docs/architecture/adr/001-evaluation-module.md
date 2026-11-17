# ADR-001: Evaluation module — valid metric results and an evaluation-only entry

- **Status:** Proposed
- **Date:** 2026-11-17
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
- `open_deep_research.utils` is not a safe dependency for this module: at import it pulls in `AsyncTavilyClient`, `MultiServerMCPClient` and the search tools. The evaluation module therefore uses a local, standard-library date helper instead of `utils.get_today_str()`.

The blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. This conflicts with `structural-constraints.md` §1, which lists top-level `test/` as “No” for new work; the conflict is recorded as a proposed whitelist and module-review question in `structural-constraints.md` §10 and must be confirmed before SA acceptance, not silently resolved here. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The design keeps evaluation logic in `test/evaluation/` and leaves `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter.

## 3. Decision

Adopt **option B**: a `test/evaluation/` package containing the evaluation types, validation, judge access, metric evaluation and the evaluation-only entry, plus a compatibility adapter in `test/evaluators.py`.

### 3.1 Package layout

```text
test/evaluation/
  __init__.py           # public exports
  types.py              # MetricStatus, MetricResult, EvaluationResult, EvaluationInputError, judge errors
  validation.py         # strict rating, groundedness ratio, input-presence checks
  judge.py              # Judge protocol, lazy default judge, provider-error mapping
  metrics.py            # metric groups, local date helper, normalisation, failure isolation
  entry.py              # evaluate_existing_report(...)
  evaluate_report.py    # CLI entry point
test/evaluators.py      # compatibility adapter only; no evaluation logic
```

### 3.2 Types and result contract

`MetricStatus` has exactly two values: `scored` and `not_evaluable`. A `MetricResult` states `metric`, `status`, `score`, `reason` and a machine-readable `reason_code`. Its invariant is: `score` is a `float` in `[0, 1]` when and only when `status == "scored"`; otherwise `score is None`. Scored results use `judge_rating` or `grounded_ratio`; `not_evaluable` results use `invalid_rating`, `missing_input`, `no_claims`, `invalid_claim`, `evaluator_error`, `judge_unavailable`, `judge_authentication` or `judge_permission`.

`EvaluationResult` states `report_id`, the tuple of `MetricResult` objects, `judge_model` and `judge_failure`. `report_id` is the lowercase hexadecimal SHA-256 of the original report text encoded as UTF-8. `judge_model` is the model identifier of the default judge, or `None` when a caller injected a judge. `judge_failure` is `None` or a `JudgeFailure` value: `initialization`, `authentication` or `permission`.

`EvaluationInputError(ValueError)` is raised when the entry's required question or report is blank or not a string. It is not a metric result: no evaluator may run before it is raised.

`JudgeUnavailableError(RuntimeError)` means the judge could not be initialised or its credentials are unavailable. `JudgeAuthenticationError(JudgeUnavailableError)` means a judge call returned an authentication failure (HTTP 401). `JudgePermissionError(JudgeUnavailableError)` means a judge call returned a permission failure (HTTP 403).

### 3.3 Metric names

The public metric names preserve the baseline LangSmith keys: `research_depth_score`, `source_quality_score`, `analytical_rigor_score`, `practical_value_score`, `balance_and_objectivity_score`, `writing_quality_score`, `relevance_score`, `structure_and_cohesiveness_score`, `correctness_score`, `groundedness_score` and `completeness_score`. The six overall-quality dimensions are six independent metric results, not one aggregate.

### 3.4 Inputs per metric

- Question and report: all metrics except groundedness; the entry requires both to be non-blank.
- Reference answer: correctness only.
- Research brief: completeness only.
- Evidence (`raw_notes` equivalent): groundedness only.

If an optional input is missing, empty or whitespace-only, only the metrics that require it become `not_evaluable`; the other metrics are still evaluated. If the question or report is missing in the LangSmith adapter, every metric that needs it becomes `not_evaluable`; the adapter does not raise.

### 3.5 Strict rating validation

The raw judge rating must be validated before any Pydantic or other type conversion. The judge response schema therefore keeps rating fields as raw values (`Any`, or the raw structured tool-call arguments); it must not declare them as `int`, because Pydantic's default lax mode would coerce `4.0` and `"4"` to `4` and hide an invalid rating. `validation.validate_rating(raw_value)` performs the first check: `type(raw_value) is int` and `1 <= raw_value <= 5`. Booleans, floats including `4.0`, strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `raw_value / 5`. An invalid rating produces `status="not_evaluable"`, `score=None` and `reason_code="invalid_rating"`. Scores are never clamped, rounded, defaulted or replaced by zero.

Groundedness is the only ratio metric: the judge's claims must be a non-empty list; the score is `grounded_count / total_claims`; an empty list produces `status="not_evaluable"` with reason code `no_claims`. The same raw-value rule applies to the `grounded` field: it is not declared as `bool` before validation. A non-boolean `grounded` value produces `status="not_evaluable"` with reason code `invalid_claim`, rather than being coerced.

### 3.6 Failure isolation

Metric groups are evaluated independently. A group is one judge call and the metrics it produces: overall quality produces six metrics from one call; each other evaluator produces one metric from one call. An exception in a group makes only that group's metrics `not_evaluable`; the remaining groups still run. The implementation catches `Exception`, never `BaseException`, so interruption and process exit are not swallowed.

Provider authentication and permission failures are special cases:

- `openai.AuthenticationError` (HTTP 401) is mapped to `JudgeAuthenticationError`; the affected group's metrics become `not_evaluable` with `reason_code="judge_authentication"` and `judge_failure="authentication"`.
- `openai.PermissionDeniedError` (HTTP 403) is mapped to `JudgePermissionError`; the affected group's metrics become `not_evaluable` with `reason_code="judge_permission"` and `judge_failure="permission"`.
- Other exceptions remain per-metric `evaluator_error` and do not set `judge_failure`.

Completed scores are never discarded. The CLI uses `judge_failure` to choose exit code `3` after printing the full per-metric result.

### 3.7 Evaluation-only entry

`evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`:

1. Rejects a non-string, blank or whitespace-only `question` or `report` with `EvaluationInputError` before any judge call.
2. Computes `report_id` as the SHA-256 of the supplied report text; the report text is passed to the judge unchanged.
3. Obtains the judge: the injected judge, or `default_judge()` constructed lazily. If `default_judge()` raises `JudgeUnavailableError`, the entry returns an `EvaluationResult` whose metrics are all `not_evaluable` with `judge_unavailable` and `judge_failure="initialization"`.
4. Runs the metric groups against the supplied inputs. A group-level judge authentication or permission failure is recorded per group; the other groups are still attempted.
5. Returns `EvaluationResult`; it never compiles or invokes the research graph, imports `open_deep_research.deep_researcher` or `open_deep_research.utils`, calls a search provider or generates a replacement report.

`Judge` is a protocol with `invoke(messages, schema) -> Mapping[str, object]`, returning the raw structured field values so rating values reach `validation.py` before any typed conversion. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key.

`metrics.py` provides `today_str()` using the standard library:

```python
from datetime import datetime

def today_str() -> str:
    now = datetime.now()
    return f"{now:%a} {now:%b} {now.day}, {now:%Y}"
```

This matches the baseline format without importing `open_deep_research.utils`.

### 3.8 CLI

`python -m test.evaluation.evaluate_report --report <path> --question <text>` accepts optional `--reference-answer`, `--research-brief` and `--evidence`. It prints the result as JSON on stdout. Exit codes are:

| Code | Meaning |
|---|---|
| `0` | Evaluation completed with at least one `scored` metric and no judge failure. |
| `1` | Evaluation completed with every metric `not_evaluable` and no judge failure. |
| `2` | Input, argument or report-file error; the message is written to stderr as `error: ...` and no evaluator runs. |
| `3` | Judge initialisation, credential, authentication (401) or permission (403) failure. The full JSON result is still printed, including completed scores. |

Precedence is `2` (input error) → `3` (judge failure) → `1` (all metrics unavailable) → `0` (at least one score). The README gains a short section showing the command, how to read the per-metric result and the exit-code meanings (REQ-010 C-003).

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

### 3.10 Prompt and request binding

Every prompt template's placeholders must exactly match the keyword arguments the metric passes to `format()`. `CORRECTNESS_PROMPT` gains `{user_question}`, `{report}`, `{answer}` and `{today}`. `GROUNDEDNESS_PROMPT` keeps `{context}` and `{report}`; the unused `today` argument is removed from the groundedness format call.

The full judge request is part of the contract, not only the template:

- overall quality: system message contains `OVERALL_QUALITY_PROMPT` with today; user message contains the question and report;
- relevance: system message contains `RELEVANCE_PROMPT` with today; user message contains the question and report;
- structure: user message contains question, report and today;
- correctness: user message contains question, report, reference answer and today;
- groundedness: user message contains evidence/context and report;
- completeness: user message contains research brief, question, report and today.

No unformatted placeholder may remain in any rendered message.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — harden `test/evaluators.py` in place and add a separate entry file | Keeps judge construction, validation, LangSmith serialisation and entry logic in one module; the import side effect and the mixing of adapter and core logic remain, and pure validation is harder to test offline. |
| C — duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | Two sources of truth for the same metrics; the REQ-009 fixes would not reach the benchmark path; violates the “extend, never replace” rule and doubles maintenance. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `test/evaluation/types.py` | Result, failure and error types | `MetricStatus`, `MetricResult`, `EvaluationResult`, `EvaluationInputError`, `JudgeFailure`, `JudgeUnavailableError`, `JudgeAuthenticationError`, `JudgePermissionError` | all evaluation components; adapters |
| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(raw_value) -> float` (raises `InvalidRating`), `groundedness_ratio(claims) -> float` (raises `NoClaims`/`InvalidClaim`), `require_text(value) -> bool` | `metrics.py`, `entry.py` |
| `test/evaluation/judge.py` | Judge boundary, lazy model construction, provider-error mapping | `Judge.invoke(messages, schema) -> Mapping[str, object]`, `invoke_judge(judge, messages, schema)`, `map_provider_error(exc)`, `default_judge() -> Judge` | `metrics.py`, `entry.py` |
| `test/evaluation/metrics.py` | Run metric groups, format prompts, normalise and isolate failures | `evaluate_metrics(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> tuple[MetricResult, ...]`, `today_str() -> str`, `not_evaluable_metrics(reason_code) -> tuple[MetricResult, ...]` | `entry.py`, `test/evaluators.py` |
| `test/evaluation/entry.py` | Evaluation-only public entry | `evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult` | CLI, callers, `test/evaluators.py` |
| `test/evaluation/evaluate_report.py` | CLI and exit-code handling | `main(argv=None) -> int`; `python -m test.evaluation.evaluate_report` | humans, scripts |
| `test/evaluators.py` | Baseline LangSmith adapter | `eval_overall_quality(inputs, outputs)`, `eval_relevance(inputs, outputs)`, `eval_structure(inputs, outputs)`, `eval_correctness(inputs, outputs, reference_outputs)`, `eval_groundedness(inputs, outputs)`, `eval_completeness(inputs, outputs)` | `test/run_evaluate.py` |
| `test/prompts.py` | Judge templates | `CORRECTNESS_PROMPT` gains `{user_question}`, `{report}`, `{answer}` and `{today}`; groundedness formatting drops the unused today argument | `metrics.py` |

**Shared contracts changed (`structural-constraints.md` §6):** none. The module adds no `state.py` type and no graph state field. The baseline LangSmith evaluator key and return-shape contract is preserved by the adapter; `test/run_evaluate.py` does not change.

**Dependency layers.**

| Layer | Rule | Evidence |
|---|---|---|
| Import dependency | `test/evaluation` imports no `open_deep_research.deep_researcher`, `open_deep_research.utils`, `test.run_evaluate` or search/MCP module. Provider SDK imports are lazy inside `judge.py`. | TC-EVAL-011 clean subprocess |
| Client creation | Exactly one evaluation judge client may be created, only by `default_judge()` when called. No client is created at import and no research/search client is created. | TC-EVAL-009, TC-EVAL-011 |
| Network request | The only permitted network request is a judge model call. Research and search network requests are zero. | TC-EVAL-010 socket and call blockers |

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none. The module does not add or change graph state; `memory-design.md` §5 has no evaluation entry.
- **Runtime policies:** POL-002 to POL-011 (`runtime-policy-catalog.md` §2), covering blank input, missing optional input, invalid rating, empty or invalid claims, evaluator exception, CLI errors, judge initialisation, authentication and permission failures.
- **Invariants:** INV-006 (valid or `not_evaluable` metric results) and INV-007 (evaluation-only entry does not perform research or search).
- **Deterministic boundary:** the model supplies ratings and claim judgements only. Deterministic code decides whether the rating is a valid integer `1..5`, whether the normalised score is in `[0, 1]`, whether at least one valid claim exists, whether required inputs are present, whether a metric is `not_evaluable`, whether an exception is a provider authentication or permission failure, and whether an exception stays local to its metric group.

## 7. Verification

| Requirement and criterion | Verification |
|---|---|
| REQ-009 C-001 | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs`, `::test_prompt_placeholders_match_arguments`, `::test_judge_request_binds_all_inputs` |
| REQ-009 C-002 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| REQ-009 C-003 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable`, `::test_adapter_missing_required_inputs` |
| REQ-009 C-004 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |
| REQ-009 M-001 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| INV-006 | `test/offline/test_evaluator_validity.py` (all cases; no out-of-range score, no score on `not_evaluable`; completed scores survive judge failures) |
| REQ-010 C-001 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research`, `::test_entry_identifies_report` |
| REQ-010 C-002 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected`, `::test_cli_blank_input_exit_code`, `::test_cli_judge_unavailable_exit_code`, `::test_cli_authentication_error_exit_code`, `::test_cli_permission_denied_exit_code` |
| REQ-010 C-003 | manual review recorded as `REVIEW-NNN` in `docs/review-memo.md` |
| INV-007 | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph`, `::test_entry_scores_supplied_report_without_research` |

**Verification basis and status.** LangSmith compatibility was checked on 2026-11-17 against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output and feedback documentation. This is a type-contract check only; no live `aevaluate` call, experiment run or UI check was performed. The live check and all behavioural tests remain `NOT_RUN`; SA Review and Gate 2 are also not performed. The authentication and permission cases construct the real `openai.AuthenticationError` (401) and `openai.PermissionDeniedError` (403) classes with a synthetic `httpx.Response` and request, so the mapping can be tested without a network call.

The module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7.

## 8. Consequences

**Positive.** Every metric either carries a defensible score in `[0, 1]` or an explicit `not_evaluable` result with a reason. Correctness receives the question, report and reference answer. A single broken metric no longer hides the others or crashes a run. Existing reports can be scored without spending research tokens or calling search. Offline tests can inject a fake judge and run without network or keys. The benchmark entry keeps its evaluator names and return shapes. Judge authentication and permission failures are distinguishable from metric-level failures and preserve completed scores.

**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change.

**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.

### Alternatives for the evaluation judge client

These alternatives are not exhaustive.

| Option | Feasibility | Why it is not the current choice |
|---|---|---|
| Inject a judge only | High; `evaluate_existing_report(..., judge=...)` already accepts one | Tests and library callers are covered, but the CLI still needs a default judge |
| Side-effect-free shared model factory | Feasible; a new shared `make_chat_model()` module could avoid search/MCP imports and serve the graph and evaluation | Changes the shared model boundary and §4, outside the REQ-009/REQ-010 SA scope; a candidate follow-up ADR |
| Reuse `configurable_model` | Low; it lives in `deep_researcher.py`, which §5 forbids this module from importing | Requires moving the shared model factory or changing the dependency rule |
| Current exception: one lazy, injectable evaluation client in `judge.py` | High; smallest boundary, preserves injection and import isolation | Still a proposed exception to §4 and needs review |

The current exception is recommended because it preserves the import boundary and does not refactor the research graph. The shared-factory option remains technically viable if the team wants to remove the exception later.

### Dependency layers

Import dependency, client creation and network requests are separate concerns:

| Layer | Rule |
|---|---|
| Import dependency | No `open_deep_research.deep_researcher`, `open_deep_research.utils`, `test.run_evaluate` or search/MCP import; provider SDK imports are lazy inside `judge.py` |
| Client creation | One lazy, injectable evaluation judge client in `judge.py`; no client at import; no research/search client |
| Network request | Only judge model calls; zero research/search calls or connections |

### Rule status

**Approved rules that remain binding.** `structural-constraints.md` §5 dependency direction, §7 deterministic boundary for safety-relevant code, §8 configuration and prompt placement, and the §4 baseline rule that the research graph reuses the shared model client.

**Proposed exceptions, not yet approved.**

1. **Path whitelist (BroZhai suggestion):** add `test/evaluation/` as an explicit exception in `structural-constraints.md` §1. Proposed §1 rows:

   | Path | Role | New work goes here? |
   |---|---|---|
   | `test/` | Existing LLM- and API-dependent evaluation scripts | No (except `test/evaluation/`) |
   | `test/evaluation/` | Evaluation module (REQ-009, REQ-010); offline paths make no network calls | Yes, evaluation owner only |

   `test/evaluation/` is code, not a test location; tests remain in `test/offline/` and `test/live/`. §1 is human-owned and is not edited by this ADR.

2. **Evaluation judge client:** `judge.py` may construct one lazy, injectable evaluation-only chat client. This is an exception to §4 because the shared `configurable_model` lives in `deep_researcher.py`, which §5 forbids the module from importing. Provider credential resolution is delegated to the client/provider rather than `utils.get_api_key_for_model()`, because importing `utils` would pull search/MCP modules. If accepted, the exception is recorded in `architecture-blueprint.md` §6.

**Open for module review.** Confirm the proposed `test/evaluation/` whitelist and the evaluation-only judge-client exception at module review and integration. Both remain proposed until SA Review records them.

## 9. Implementation Steps

Tests for §7 are written by the Test Author after Gate 1; the steps below are the Build work that follows Gate 2.

1. Create `test/evaluation/__init__.py` and export the public types and `evaluate_existing_report`.
2. Add `test/evaluation/types.py`: `MetricStatus`, `MetricResult`, `EvaluationResult` (including `judge_failure`), `EvaluationInputError`, `JudgeFailure`, `JudgeUnavailableError`, `JudgeAuthenticationError` and `JudgePermissionError`, with the score/status invariant.
3. Add `test/evaluation/validation.py`: strict `1..5` integer validation on the raw value before any conversion, `raw_value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats including `4.0`, strings, `None` and non-finite values; reject a non-boolean `grounded` field as `invalid_claim`.
4. Add `test/evaluation/judge.py`: the `Judge` protocol that returns raw structured field values, `invoke_judge()` that maps `openai.AuthenticationError` (401) to `JudgeAuthenticationError` and `openai.PermissionDeniedError` (403) to `JudgePermissionError`, and a `default_judge()` that imports the provider SDK and constructs the baseline `ChatOpenAI` only when called. Wrap construction/credential failures in `JudgeUnavailableError`; do not declare rating fields as `int`.
5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, a local `today_str()` using `datetime.now()`, per-group `try/except Exception`, deterministic reason codes, and `not_evaluable_metrics()`. Call `invoke_judge()` and `validate_rating()` before constructing a `MetricResult`; map `InvalidRating` to `not_evaluable`/`invalid_rating`, and map authentication/permission failures to their reason codes while continuing the other groups.
6. Add `test/evaluation/entry.py`: `evaluate_existing_report`, blank-input rejection before the judge, SHA-256 `report_id`, the no-research/no-search import boundary, and the initialisation-failure result with all metrics `not_evaluable`.
7. Add `test/evaluation/evaluate_report.py`: the CLI, JSON output and exit codes `0/1/2/3`; write input errors to stderr as `error: ...`; print the full JSON result before exiting `3`.
8. In `test/prompts.py`, add `{user_question}`, `{report}`, `{answer}` and `{today}` to `CORRECTNESS_PROMPT`; remove the unused `today` argument from the groundedness format call; keep the rubric wording unchanged.
9. Replace the bodies of the six functions in `test/evaluators.py` with adapter calls; remove the module-level `eval_model` and the `get_today_str` import; preserve names, signatures, baseline keys, the six-item list for overall quality and the single-dict shape for the others; add `status` metadata and the null-score/`value="not_evaluable"` mapping.
10. Add the README section for `python -m test.evaluation.evaluate_report`, the per-metric result and the exit-code meanings (REQ-010 C-003).
11. Add `"test.evaluation"` to `[tool.setuptools] packages` in `pyproject.toml`; the dependency-file change is accepted for the implementation PR and is not made in this SA change.
12. Run `uv run ruff check test/evaluation test/evaluators.py test/prompts.py` and `uv run pytest test/offline` after the Test Author's tests exist. Do not modify `test/run_evaluate.py`, `src/` or the tests.
