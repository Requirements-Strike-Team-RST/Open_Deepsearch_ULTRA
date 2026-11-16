# Verification Constraints

> **Purpose:** One shared way to decide that a requirement is really done.
> **Authoritative for:** verification layers, test conventions, commands, CI gates, verdicts and evidence, module test requirements and the Definition of Done.
> **Maintained by:** humans for §1–§6 and §8; each module owner writes their module's test requirements in §7, integrated before SA Review.
> **Last updated:** 2026-11-13

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

### context (REQ-005, ADR-005)

Tests are deterministic offline tests: fake message lists and fake model/exception objects, no network, no API keys (`verification-constraints.md` §3). Every case drives the public interface of `context/__init__.py`, never a private helper, so Build can reorganise the files without invalidating Gate 2.

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-001 | REQ-005 C-001 | normal | `plan_trim` with preamble (`HumanMessage` topic), three AI turns each followed by its `ToolMessage`s, and the instruction index; fake model that raises a token-limit error until two turns are gone | Removed turns are exactly the two oldest; preamble, instruction and newest turn with its tool results are kept; returned message order is the original order minus the removed turns | `test/offline/test_context_compaction.py::test_oldest_turns_removed_first` |
| TC-002 | REQ-005 M-001 | boundary | Same history as TC-001, asserting the measurement | `latest_turn_preservation_rate == 1.0`; the newest turn index never appears in `removed_turn_indices` | `test/offline/test_context_compaction.py::test_oldest_turns_removed_first` |
| TC-003 | REQ-005 C-002 | exception | Generated histories (0, 1, 2, 3 turns; a turn with 0, 1 and 3 tool results; an `AIMessage` issuing two calls of which only one result is present; an orphan `ToolMessage` whose `tool_call_id` matches no `AIMessage`) fed to `plan_trim` | Every `ToolMessage` in the result belongs to an `AIMessage` whose `tool_calls` contain its `tool_call_id` (pairing by id, not by position); the orphan is preserved, not removed | `test/offline/test_context_compaction.py::test_no_orphan_tool_messages` |
| TC-004 | REQ-005 M-002 | boundary | Result of TC-003 | `orphan_tool_message_count == 0` | `test/offline/test_context_compaction.py::test_no_orphan_tool_messages` |
| TC-005 | REQ-005 C-003 | exception | Anthropic `BadRequestError`-shaped fake exception with message `"prompt is too long"`; `compression_model = "anthropic:claude-..."`, `research_model = "openai:gpt-4.1"`; fake model that fails identically twice | `classify_token_limit(exc, compression_model)` is `True`; the loop trims before the retry; the identical request is never sent twice without a trim | `test/offline/test_context_compaction.py::test_classification_uses_compression_model` |
| TC-006 | REQ-005 C-004 | exception | History of preamble + one AI turn + instruction; fake model that always raises a token-limit error | `compress_with_recovery` raises `TokenLimitExceeded`; the node returns status `failed`, category `token_limit`; no summary is returned and the placeholder literal does not appear anywhere in the result | `test/offline/test_context_compaction.py::test_unreducible_history_ends_failed` |
| TC-007 | INV-001 | exception | Union of TC-001 to TC-006, TC-010, TC-011 and TC-012, asserting the invariant clauses directly: newest turn kept, no orphan, `token_limit` failure, failure carried by the declared output field, no placeholder on the new path | The invariant holds in every case; the monitors are computed from the same helpers | `test/offline/test_context_compaction.py::test_newest_context_never_dropped` |
| TC-008 | REQ-005 (scope boundary), POL-003 | exception | Fake model raising a non-token error (e.g. `ValueError("bad request")`) on the first two calls and a normal response on the third; second case raising it on every call | On the new path the exception is **not** propagated: the unchanged request is retried, the third call returns a normal outcome, and the case that always fails ends `failed` without raising out of the node | `test/offline/test_context_compaction.py::test_non_token_errors_are_retried` |
| TC-009 | `structural-constraints.md` §8 (behaviour flag default) | normal | `Configuration()` defaults; `Configuration(context_trimming=False)`; `Configuration(context_trimming=True)` | `context_trimming` defaults to `False`, so the baseline branch is selected and REQ-005 behaviour is opt-in; `True` selects the new path | `test/offline/test_context_compaction.py::test_flag_defaults_to_baseline` |
| TC-010 | REQ-005 C-004 (output contract, ADR-005 §3(d) and §5) | exception | `compress_research` return value validated against `ResearcherOutputState`, on the failure path and on the success path | `research_outcome` is present and non-`None` on failure and `None` on success; an undeclared key would be filtered out, which is why the field must be declared | `test/offline/test_context_compaction.py::test_outcome_survives_output_state` |
| TC-011 | REQ-005 C-004 (consumer site) | exception | `supervisor_tools` given a researcher output carrying a failed `research_outcome` | The resulting `ToolMessage` states that the task failed with `token_limit` and is not the placeholder literal; the `supervisor_tools` code is unchanged by this requirement | `test/offline/test_context_compaction.py::test_no_placeholder_at_consumer` |
| TC-012 | REQ-005 C-004 (attempt budget) | boundary | History with N removable turns; fake model that rejects every request | Removing one turn per attempt, the loop consumes all N removable turns before failing; `removed_turn_indices` has N entries, not `max_attempts - 1` | `test/offline/test_context_compaction.py::test_budget_covers_all_removable_turns` |

- **Helpers:** cases may use shared fixtures in `test/offline/` for building AI turns with tool calls and for a fake token-limit exception per provider; the fixtures must not call a model or read environment variables.
- **Regression:** `uv run pytest test/offline` in full. `test/offline/test_contracts.py` must be re-run if the REQ-001 task-result type changes in the same PR. No existing suite reads `remove_up_to_last_ai_message` behaviour, but the helper's docstring correction is reviewed in the diff.
- **Live or human checks:** none. All REQ-005 criteria are `automated: true` in `requirements.yaml`, and the requirement has no `automated: false` case, so no live test is needed. The thin-node check (`structural-constraints.md` §2) is human review evidence recorded in `docs/review-memo.md`, not a test.
- **Evidence location:** `docs/test-reports/REQ-005.md` — baseline run by Test Author, verification by Verify (`verification-constraints.md` §6).

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
