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

### delivery (REQ-002, REQ-004, ADR-001)

Case IDs are `TC-<REQ>-<nn>`. Every criterion of REQ-002 and REQ-004 and both invariants the module enforces (INV-002, INV-006) appear below. All cases are offline; none needs a network, an API key or a real model.

**REQ-002 — task failure isolation, queuing and join** (`test/offline/test_failure_propagation.py`)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-002-01 | REQ-002 C-001 | exception | one delegation; fake researcher raises `RuntimeError("boom")` | `run_delegations` returns a `failed` result with category `runtime` and message `"boom"`; no exception escapes; the caller routes back to the supervisor rather than `END` | `test_failure_propagation.py::test_child_exception_becomes_failed_result` |
| TC-002-02 | REQ-002 C-002 | normal + exception | two delegations; one returns a finding, the other raises | the finding appears in the tool messages and in `notes`; only the other task is `failed` | `::test_sibling_result_kept_on_failure` |
| TC-002-03 | REQ-002 C-003 | exception (boundary of classification) | fake raises a recognised token-limit error | result is `failed` with category `token_limit`; the phase does not end | `::test_token_limit_error_is_task_failure` |
| TC-002-04 | REQ-002 C-004, M-001 | boundary | three delegations, `max_concurrent_research_units = 1` | all three records end `done`, three `TaskResult`s, `dropped_count == 0` | `::test_overflow_delegations_are_queued` |
| TC-002-05 | REQ-002 C-005 | boundary (loop exit) | exit cap reached with two delegations in the last turn | both end `failed` with reason `not_run`, each with a `ToolMessage` | `::test_delegations_left_at_exit_are_failed` |
| TC-002-06 | REQ-002 C-006 | exception (join) | one fake raises immediately, sibling still sleeping | after return no `asyncio.Task` started by the call is pending | `::test_no_task_running_after_join` |
| TC-002-07 | REQ-002 C-007, M-002 | exception | one failed task and one placeholder-compression task | `notes` contains only validated findings; both failures appear only in `failed_tasks`; `failure_text_in_notes_count == 0` | `::test_failure_text_not_in_notes` |
| TC-002-08 | INV-006 | boundary | specs supplied as unrun with `unrun_reason="not_run"` | exactly one terminal result per spec; no record left `queued` or `running` | `::test_unrun_specs_all_end_not_run` |
| TC-002-09 | INV-002 S1 | exception (cancellation) | the run is cancelled while a researcher is sleeping | `asyncio.CancelledError` propagates; it is not converted into a `failed` task result | `::test_cancellation_is_not_swallowed` |
| TC-002-10 | REQ-002 C-001 (negative control) | normal | `max_concurrent = 0` passed by mistake | clamped to 1, the task still runs and ends with a result | `::test_non_positive_concurrency_clamped` |

**REQ-004 — run outcome and limitations section** (`test/offline/test_run_outcome.py`)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-004-01 | REQ-004 C-001 | normal | covered exit, all task results complete, report generated | `research_outcome == "complete"`, `failed_tasks == []`, no limitations section | `test_run_outcome.py::test_covered_run_is_complete` |
| TC-004-02 | REQ-004 C-002 | exception | two tasks, one failed; fake report model never mentions the failure | outcome `partial`; `failed_tasks` names the task and its reason; the limitations section names it | `::test_failed_task_makes_run_partial` |
| TC-004-03 | REQ-004 C-003 | boundary | all tasks complete, exit reason `stalled` and separately `budget_exhausted` | outcome `partial` in both cases | `::test_non_covered_exit_is_partial` |
| TC-004-04 | REQ-004 C-004 | boundary (no data) | no validated finding | outcome `failed`, `report_allowed` false, `final_report` empty, fake report model call count `0` | `::test_no_finding_run_is_failed` |
| TC-004-05 | REQ-004 C-005 | exception | fake report model raises a non-token-limit error | outcome `failed` with that reason, `final_report` empty, no error text in the report field | `::test_report_error_run_is_failed` |
| TC-004-06 | REQ-004 C-006, M-001 | boundary | findings exceed the limit and are truncated | outcome `partial`; limitations section states findings were left out; `false_complete_outcome_count == 0` at aggregate level | `::test_truncated_findings_make_run_partial` |
| TC-004-07 | INV-002 S5 | boundary | exit reason `failed` after retries | outcome `failed` even if every task result is complete | `::test_supervisor_failure_is_failed_outcome` |
| TC-004-08 | INV-002 S6 | normal (negative control) | a partial run whose report model *does* mention the failure | exactly one limitations section is appended; the model's mention is not duplicated or removed | `::test_limitations_appended_once` |
| TC-004-09 | INV-002 S5 (determinism) | exception | failing task list mutated after the first pass | `evaluate_before_report` is a pure function: the same state yields the same decision twice | `::test_outcome_decision_is_pure` |

- **Regression:** every existing suite in `test/offline/` (CI job `offline-tests`), and `test/offline/test_contracts.py` if the task-contract shared contract changes. With `enforce_delivery_outcome = False` the baseline supervisor behaviour must be unchanged, so also re-run any suite the test author writes for the baseline `supervisor_tools` path.
- **Live or human checks:** none for this module. REQ-004's criteria are all scripted with fake models; REQ-003's live check (`test/live/test_research_termination_live.py`) belongs to orchestration. The `false_complete_outcome_count` and `dropped_delegation_count` monitors are computed from the offline scenarios above, not from live runs.

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
