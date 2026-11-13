# Verification Constraints

> **Purpose:** One shared way to decide that a requirement is really done.
> **Authoritative for:** verification layers, test conventions, commands, CI gates, verdicts and evidence, module test requirements and the Definition of Done.
> **Maintained by:** humans for §1–§6 and §8; each module owner writes their module's test requirements in §7, integrated before SA Review.
> **Last updated:** 2026-11-12

## 1. Three Verification Layers

| Layer | Meaning | Where it runs |
|---|---|---|
| **Structural** | Code organisation, schemas, module boundaries, docstring RIDs and lint conform to the rules | CI: schema and static-analysis gates |
| **Regression** | Existing behaviour and shared contracts still hold | CI: every suite in `test/offline/` |
| **Behavioural** | The requirement's behaviour meets its fit criterion | New offline tests; `test/live/` or `test/run_evaluate.py` when a case needs a real model; human confirmation |

## 2. Principles

1. Every fit-criterion check and metric in `requirements.yaml` has at least one test or a named piece of review evidence; its `verification` field points to it.
2. Every invariant has a test that fails when the invariant is violated.
3. A change runs its new tests and every prior offline suite; any regression blocks the merge.
4. Module test requirements (§7) are approved in SA Review (Gate 1) before tests are written, and the tests are approved before implementation (Gate 2). Tests are written by Test Author and never changed by Build.
5. Prefer deterministic offline tests; use live tests for final behavioural evidence only.

## 3. Test Conventions

- **Offline tests** (`test/offline/`) use fake models and fake researchers, make no network calls and need no API keys, so supervisor logic, termination, scheduling and context handling run in CI at no token cost.
- **Live tests** (`test/live/`) call real models or APIs, run on demand rather than on every commit, and are marked `automated: false` in `requirements.yaml` when a human must judge the result.
- **Names:** test files are named after the behaviour they cover, `test_<topic>.py` (for example `test_failure_propagation.py`); test functions describe the expected behaviour. Requirement IDs are not part of file names, so renumbering requirements does not rename tests.
- **Traceability:** the first line of every test module's docstring lists the RIDs it verifies, for example `"""REQ-002: no delegated task is lost or silently treated as completed."""`. The requirement's `verification` field gives the exact `path::test_name`.
- **Shared contract tests:** when a requirement defines a shared contract (`structural-constraints.md` §6), its contract tests live in `test/offline/test_contracts.py` and every PR runs them.

## 4. Commands

| Check | Command |
|---|---|
| Requirements schema and ID consistency | `uv run python scripts/validate_requirements.py` |
| Lint (gated paths) | `uv run ruff check src/open_deep_research test/offline scripts` |
| Type check (optional, not gated) | `uv run mypy src/open_deep_research` |
| Offline tests | `uv run pytest test/offline` |
| Live and evaluation tests | `uv run pytest test/live`, `uv run python test/run_evaluate.py` |

`ruff format` is applied to new files and changed lines only; do not reformat untouched baseline code. Install tools with `uv sync --extra dev`.

## 5. CI Gates

The course requires six blocking gates. Their state in `.github/workflows/ci.yml`:

| Course gate | CI job | What it checks | Status |
|---|---|---|---|
| Schema | `requirements-schema` | `requirements.yaml` against `req-schema.json`, plus unique and resolvable IDs | Active |
| Static analysis | `static-analysis` | `ruff check` on the gated paths | Active; mypy planned |
| Regression | `offline-tests` | `pytest test/offline` | Active; reports `NOT_RUN` while the directory has no tests |
| Test approval | — | The approval record has Gate 2 for every PR that changes `src/`, and the PR's tests match the approved test commit | Planned |
| AI-use log | — | `docs/ai-use-log.yaml` is valid and has an entry for the PR | Planned |
| Semantic evaluation | — | Live evaluation of fit criteria for prompt or model changes | Planned |

Lint debt outside the gated paths is tracked in `docs/debt-register.md`; a path joins the static-analysis gate once it is clean.

## 6. Verdicts and Evidence

- Verdicts are only `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED` and `N/A`. A skipped test is `NOT_RUN`, never `PASS`.
- No check is reported as passed without execution evidence. A mandatory check that is `FAIL`, `NOT_RUN` or `BLOCKED` keeps the requirement from `verified`.
- Evidence goes to `docs/test-reports/<task-id>.md`: the baseline run by Test Author and the verification by Verify, each with commit, commands, verdict per check, and logs or diffs where relevant.
- Offline tests run without network or secrets (§3). Verify changes no file other than its report; the PR diff shows any change made during verification.

## 7. Module Test Requirements

Copy the example for your module. Every acceptance criterion (C-/M-) of the module's requirements and every invariant it enforces needs at least one case, and the module lists the existing suites it can affect. At integration, check that no criterion or invariant is left without a case.

### <Module> (REQ-NNN, ADR-NNN)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-001 | REQ-NNN C-NNN | normal | | | `test/offline/<file>::<test>` |
| TC-002 | INV-NNN | exception | | | |
| TC-003 | REQ-NNN M-NNN | boundary | | | |

- **Regression:** existing suites to re-run, including `test/offline/test_contracts.py` if a shared contract changes.
- **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.

### evaluation (REQ-009, REQ-010, ADR-001)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-EVAL-001 | REQ-009 C-001 | normal | Distinct question, report, reference-answer, research-brief and evidence markers; a fake judge that records requests | Every metric's judge request contains its declared inputs unchanged; correctness receives question, report and reference answer; completeness receives the brief; groundedness receives the evidence | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |
| TC-EVAL-002 | REQ-009 C-002 / INV-006 | boundary | Ratings `1` and `5` | Scores `0.2` and `1.0`, status `scored` | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| TC-EVAL-003 | REQ-009 C-002 / INV-006 | exception | Ratings `0`, `6`, `True`, `"4"`, `4.0`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| TC-EVAL-004 | REQ-009 C-003 / INV-006 | exception | Missing reference answer, research brief and evidence, one at a time | Correctness, completeness or groundedness respectively is `not_evaluable`; the other metrics are still `scored` | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |
| TC-EVAL-005 | REQ-009 C-004 / INV-006 | boundary | Judge returns an empty claim list | Groundedness is `not_evaluable` with `score=None`; no `ZeroDivisionError` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |
| TC-EVAL-006 | REQ-009 C-004 | normal | Four claims, two grounded | Groundedness score `0.5` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |
| TC-EVAL-007 | REQ-009 C-004 / INV-006 | exception | One evaluator or judge call raises | Only that group's metrics are `not_evaluable`; the remaining metrics are still evaluated | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |
| TC-EVAL-008 | REQ-009 M-001 / INV-006 | boundary | Sweep of valid and invalid ratings across every metric | `out_of_range_score_count == 0`; every `scored` result is in `[0, 1]`; every invalid result has a null score | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| TC-EVAL-009 | INV-006 | regression | Import `test.evaluators` with no API key and no network; call each adapter with a fake judge | Import has no model-client or network side effect; baseline `key`/return shapes hold; `not_evaluable` maps to null `score`, `value="not_evaluable"` and status metadata | `test/offline/test_evaluator_validity.py::test_adapter_contract_and_import_is_side_effect_free` |
| TC-EVAL-010 | REQ-010 C-001 / INV-007 | normal | A supplied report and question with markers; research-graph and search entry points patched to fail if called | Judge requests contain the supplied text unchanged; graph and search call counts are zero; `report_id` is the report SHA-256 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research` |
| TC-EVAL-011 | INV-007 | regression | Import the entry in a subprocess with no research modules preloaded | `open_deep_research.deep_researcher` is absent from `sys.modules` | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |
| TC-EVAL-012 | REQ-010 C-002 / INV-007 | exception | Empty, whitespace-only and `None` question or report | `EvaluationInputError`; fake judge call count is zero | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |
| TC-EVAL-013 | REQ-010 C-001 | boundary | Same report submitted twice, and a report differing by one character | `report_id` is stable for the same text and differs for the changed text; it equals the lowercase SHA-256 of the UTF-8 report | `test/offline/test_report_evaluation_entry.py::test_entry_identifies_report` |
| TC-EVAL-014 | REQ-010 C-003 | human | Reviewer follows the README to evaluate a report file and read the per-metric results | The procedure works without modifying source code; verdict recorded as `REVIEW-NNN` | `docs/review-memo.md` (report evaluation entry review) |
| TC-EVAL-015 | REQ-010 C-002 / INV-007 / POL-007 | exception | CLI with a blank question or a missing report file | stderr contains `error: ...`; exit code `2`; no judge call | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |
| TC-EVAL-016 | POL-008 | boundary | CLI completes with all metrics `not_evaluable`; CLI completes with at least one `scored` metric | Exit code `1` and JSON on stdout in the first case; exit code `0` and JSON in the second | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |

- **Regression:** re-run `uv run pytest test/offline`; the adapter contract in `test/offline/test_evaluator_validity.py`; and the import surface of `test/run_evaluate.py` (the six evaluator names and their call signatures must remain available). No live model or network call is needed for any case above.
- **Live or human checks:** REQ-010 C-003 is the only `automated: false` criterion in this module; its evidence is the `REVIEW-NNN` record in `docs/review-memo.md`.
- **LangSmith type-contract check:** `PASS` (2026-11-13) against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output and feedback documentation; this is not a live service test.
- **LangSmith live compatibility:** `NOT_RUN`; a live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation.
- **Raw-rating test note:** `TC-EVAL-003` deliberately includes `4.0` and `"4"`: a lax `int` schema would coerce both to `4`; the test must observe `not_evaluable` with `invalid_rating`.

## 8. Definition of Done

| # | Condition | Done by |
|---|---|---|
| 1 | Every fit-criterion item has an approved test or recorded review, and the tests pass | Test Author (tests), Build (passing), confirmed by Verify |
| 2 | All prior offline suites pass | Verify |
| 3 | All active CI gates are green | CI |
| 4 | Behaviour conforms to the fit criterion, with evidence in `docs/test-reports/` | Verify, confirmed by a human |
| 5 | `trace-matrix.md` row complete for architecture, code and tests | Module owner |
| 6 | If a boundary changed: `invariants.md` updated and its test passes | Human, Test Author |
| 7 | If an architectural decision arose: ADR accepted or `evaluation-table.md` entry recorded | Human |
| 8 | `docs/ai-use-log.yaml` and `docs/review-memo.md` updated | Human |
| 9 | Gate 3 passed: two approvals, PR merged | Humans |
| 10 | `status` in `requirements.yaml` advanced to `verified` | Human |
