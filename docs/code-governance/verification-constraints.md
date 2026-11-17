# Verification Constraints

> **Purpose:** One shared way to decide that a requirement is really done.
> **Authoritative for:** verification layers, test conventions, commands, CI gates, verdicts and evidence, module test requirements and the Definition of Done.
> **Maintained by:** humans for §1–§6 and §8; each module owner writes their module's test requirements in §7, integrated before SA Review.
> **Last updated:** 2026-11-17

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

Each module lists one or more cases for every acceptance criterion (C-/M-) of its requirements and for every invariant it enforces, plus the existing suites it can affect. Case IDs are `TC-<MODULE>-NN` with the prefixes ORC, DLV, CTX, CIT, SRC and EVA. Test names copied from a requirement's `verification` field must stay exactly as written there. Unless a case says otherwise, it runs with the module's flag on, uses fake models or fake researchers, and makes no network call. At integration, check that no criterion or invariant is left without a case.

### orchestration (REQ-001, REQ-003, ADR-001)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-ORC-01 | REQ-001 C-001 | normal | A scripted supervisor turn with one valid delegation | The researcher receives a `TaskSpec` with task id, topic, scope, 1–5 required questions and `max_tool_calls = max_react_tool_calls` | `test/offline/test_task_contract.py::test_delegation_is_valid_task_spec` |
| TC-ORC-02 | REQ-001 C-002 | normal | Findings answer two of three questions with URLs the task's tools returned | Status `partial`; the unanswered question is in `reason` | `test/offline/test_task_contract.py::test_status_derived_from_sourced_findings` |
| TC-ORC-03 | REQ-001 C-003, M-001; INV-006 | exception | Every question claimed, one finding cites a URL no tool in the task returned | That finding is not counted; status comes from the rest; `unsourced_finding_counted_count == 0` | `test/offline/test_task_contract.py::test_unretrieved_source_does_not_count` |
| TC-ORC-04 | REQ-001 C-004; INV-006 | exception | Compression text with no findings block, invalid JSON, an unknown question or an unknown source number | `failed` with category `invalid_result` | `test/offline/test_task_contract.py::test_malformed_result_becomes_failed` |
| TC-ORC-05 | INV-006 | boundary | Delegations with a blank topic, six questions, and an empty question list | The first two get an error `ToolMessage` and create no task; the third becomes a task whose only question is the topic | `test/offline/test_task_contract.py::test_invalid_delegation_is_rejected` |
| TC-ORC-06 | INV-003 | boundary | Budget 2; the model asks for 4 calls in one batch, one of which raises | Only the first 2 run and both count (including the failing one); the other 2 get a budget message; the researcher goes to compression | `test/offline/test_task_contract.py::test_tool_budget_limits_calls` |
| TC-ORC-07 | REQ-003 C-001 | normal | Results answer every required question; once with and once without `ResearchComplete` | Exit reason `covered` in both runs | `test/offline/test_research_termination.py::test_full_coverage_exits_covered` |
| TC-ORC-08 | REQ-003 C-002, M-002 | boundary | Coverage 0.5, threshold 0.8, the supervisor calls `ResearchComplete` | The loop continues; the next supervisor input lists the unanswered questions; `premature_complete_accepted_count == 0` | `test/offline/test_research_termination.py::test_complete_below_threshold_is_refused` |
| TC-ORC-09 | REQ-003 C-003 | boundary | Two delegation turns that add no coverage, with a `think_tool`-only turn between them | Exit reason `stalled` after the second delegation turn | `test/offline/test_research_termination.py::test_turns_without_progress_exit_stalled` |
| TC-ORC-10 | REQ-003 C-004 | boundary | Coverage below the threshold when the iteration cap is reached | Exit reason `budget_exhausted` | `test/offline/test_research_termination.py::test_iteration_cap_exits_budget_exhausted` |
| TC-ORC-11 | REQ-003 C-005 | exception | The supervisor model raises on every retry | Exit reason `failed` with the error in `exit_detail`; no unhandled exception | `test/offline/test_research_termination.py::test_supervisor_model_error_exits_failed` |
| TC-ORC-12 | REQ-003 M-001; INV-003 | boundary | States where several exit conditions hold at once (covered and cap; cap and stall; stall and supervisor error) | Exactly one reason, chosen in the order `covered > budget_exhausted > stalled > failed`; `exit_without_single_reason_count == 0` over the suite | `test/offline/test_research_termination.py::test_exit_reason_precedence` |
| TC-ORC-13 | REQ-003 C-006 | live | The two baseline queries on a configuration with Tavily or MCP search | At least one exit `covered` and at most one at the cap | `test/live/test_research_termination_live.py::test_baseline_queries_exit_reasons` |
| TC-ORC-14 | flag off | regression | `task_contract_enabled = False` | The supervisor binds the baseline `ConductResearch`; no new state field is written | `test/offline/test_task_contract.py::test_flag_off_keeps_baseline` |

- **Regression:** all of `test/offline/`, including `test/offline/test_contracts.py` for the shared types.
- **Live or human checks:** TC-ORC-13 (`automated: false`). The team's earlier baseline ran with search disabled, so a human chooses a search-capable configuration before the run; evidence goes to `docs/test-reports/REQ-003.md`.

### delivery (REQ-002, REQ-004, ADR-002, ADR-003)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-DLV-01 | REQ-002 C-001 | exception | One delegation whose researcher raises `RuntimeError("boom")` | The task is `failed/runtime` with message `boom`; `supervisor_tools` routes back to the supervisor, not to END | `test/offline/test_failure_propagation.py::test_child_exception_becomes_failed_result` |
| TC-DLV-02 | REQ-002 C-002 | exception | Two delegations; one returns a finding, the other raises | The finding is in the tool messages and `raw_notes`; only the other task is failed | `test/offline/test_failure_propagation.py::test_sibling_result_kept_on_failure` |
| TC-DLV-03 | REQ-002 C-003 | exception | A researcher raises a recognised token-limit error | The task is `failed/token_limit`; the research phase does not end | `test/offline/test_failure_propagation.py::test_token_limit_error_is_task_failure` |
| TC-DLV-04 | REQ-002 C-004, M-001; INV-007 | boundary | Three delegations, concurrency limit 1 | All three run, never more than one at a time, and each ends with one result; `dropped_delegation_count == 0` | `test/offline/test_failure_propagation.py::test_overflow_delegations_are_queued` |
| TC-DLV-05 | REQ-002 C-005; INV-007 | boundary | The cap is reached on a turn with two delegations | Both end `failed/not_run`, each with a `ToolMessage` | `test/offline/test_failure_propagation.py::test_delegations_left_at_exit_are_failed` |
| TC-DLV-06 | REQ-002 C-006; INV-007 | exception | One researcher raises at once while a sibling is still sleeping | When `supervisor_tools` returns, no task it started is pending | `test/offline/test_failure_propagation.py::test_no_task_running_after_join` |
| TC-DLV-07 | REQ-002 C-007, M-002; INV-002 | exception | One failed task and one whose compression returned the placeholder | `notes` hold only the counted findings of complete or partial tasks; `failure_text_in_notes_count == 0` | `test/offline/test_failure_propagation.py::test_failure_text_not_in_notes` |
| TC-DLV-08 | INV-007 | exception | The run is cancelled while a researcher is sleeping | `asyncio.CancelledError` propagates; no task result is created for it | `test/offline/test_failure_propagation.py::test_cancellation_is_not_swallowed` |
| TC-DLV-09 | REQ-004 C-001 | normal | All tasks complete, exit `covered` | Outcome `complete`; `failed_tasks` empty; no limitations section | `test/offline/test_run_outcome.py::test_covered_run_is_complete` |
| TC-DLV-10 | REQ-004 C-002; INV-002 | exception | Two tasks, one failed; the fake report model does not mention it | Outcome `partial`; `failed_tasks` names the task and reason; the limitations section names it | `test/offline/test_run_outcome.py::test_failed_task_makes_run_partial` |
| TC-DLV-11 | REQ-004 C-003 | boundary | All tasks complete; exit `stalled`, and separately `budget_exhausted` | Outcome `partial` in both | `test/offline/test_run_outcome.py::test_non_covered_exit_is_partial` |
| TC-DLV-12 | REQ-004 C-004 | boundary | No task is complete or partial | Outcome `failed`; the report model is called 0 times; `final_report` is empty | `test/offline/test_run_outcome.py::test_no_finding_run_is_failed` |
| TC-DLV-13 | REQ-004 C-005 | exception | The report model raises a non-token-limit error | Outcome `failed`; `final_report` empty; the error only in `outcome_detail` | `test/offline/test_run_outcome.py::test_report_error_run_is_failed` |
| TC-DLV-14 | REQ-004 C-006 | boundary | Findings must be cut to fit the report model, then a report is produced | Outcome `partial`; the limitations section says findings were left out | `test/offline/test_run_outcome.py::test_truncated_findings_make_run_partial` |
| TC-DLV-15 | REQ-004 M-001; INV-002 | boundary | Exit `failed` with every task complete; and a report whose truncation retries run out | Outcome `failed` in both; across the suite `false_complete_outcome_count == 0` | `test/offline/test_run_outcome.py::test_failed_exit_is_failed_outcome` |
| TC-DLV-16 | flag off | regression | `task_contract_enabled = False` | `check_research_outcome` forwards to `final_report_generation` without an update; the report and `notes` are as in the baseline | `test/offline/test_run_outcome.py::test_flag_off_keeps_baseline_report` |

- **Regression:** all of `test/offline/`, including `test/offline/test_contracts.py`.
- **Live or human checks:** none.

### context (REQ-005, ADR-004)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-CTX-01 | REQ-005 C-001, M-001; INV-001 | normal | Topic, three AI turns with tool results, instruction; the fake model rejects the request until two turns are removed | The two oldest turns are removed; topic, newest turn with its results and instruction are kept in order; `latest_turn_preservation_rate == 1.0` | `test/offline/test_context_compaction.py::test_oldest_turns_removed_first` |
| TC-CTX-02 | REQ-005 C-002, M-002; INV-001 | boundary | Histories with 0–3 turns, a turn with several tool calls of which one result is missing, and a tool message whose id matches no AI message | Every kept tool result follows the AI message that requested it; the unmatched one is kept; `orphan_tool_message_count == 0` | `test/offline/test_context_compaction.py::test_no_orphan_tool_messages` |
| TC-CTX-03 | REQ-005 C-003 | exception | `research_model = openai:gpt-4.1`, `compression_model = anthropic:...`; the fake raises an Anthropic-shaped token-limit error | The error is recognised and a turn is removed before the retry | `test/offline/test_context_compaction.py::test_classification_uses_compression_model` |
| TC-CTX-04 | REQ-005 C-004; INV-001 | exception | Topic, one AI turn and instruction; the model always raises a token-limit error; `task_contract_enabled` on | The task is `failed/token_limit`; no placeholder text appears as a summary | `test/offline/test_context_compaction.py::test_unreducible_history_ends_failed` |
| TC-CTX-05 | REQ-005 (scope); POL-014 | exception | A one-turn history whose model raises a rate-limit error twice and then succeeds; a model that always raises it | First: a normal summary. Second: `CompressionFailed(runtime)` after 3 attempts | `test/offline/test_context_compaction.py::test_non_token_errors_are_retried` |
| TC-CTX-06 | flag off | regression | `context_trimming = False` | The baseline loop and its placeholder are used | `test/offline/test_context_compaction.py::test_flag_off_keeps_baseline` |

- **Regression:** all of `test/offline/`.
- **Live or human checks:** none.

### citations (REQ-006, ADR-005)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-CIT-01 | REQ-006 C-001; INV-008 | normal | The assembled `compress_research_system_prompt` | One Citation Rules block with `### Sources`; no `List of All Relevant Sources` and no `[Title](URL)` | `test/offline/test_prompt_citation_contract.py::test_compression_prompt_has_single_sources_format` |
| TC-CIT-02 | REQ-006 C-002; INV-008 | normal | The assembled `final_report_generation_prompt` | Numbered citations required; no `[Title](URL)`; the renumbering instruction appears once | `test/offline/test_prompt_citation_contract.py::test_report_prompt_has_single_citation_format` |
| TC-CIT-03 | REQ-006 C-003; INV-008 | normal | Both assembled prompts | The text between `<Citation Rules>` and `</Citation Rules>` is identical | `test/offline/test_prompt_citation_contract.py::test_prompts_share_citation_format` |
| TC-CIT-04 | ADR-005 §3 | exception | Both prompts formatted with all their runtime placeholders | No error; no `{citation_rules}`-style placeholder is left | `test/offline/test_prompt_citation_contract.py::test_assembled_prompts_format_without_leftover_placeholders` |
| TC-CIT-05 | REQ-006 C-004 | live | The two baseline queries | Every inline `[n]` has exactly one matching `### Sources` entry; runs with truncated findings are reported separately | `test/live/test_report_citations_live.py::test_reports_use_numbered_citations` |

- **Regression:** all of `test/offline/` (every graph test imports `prompts.py`).
- **Live or human checks:** TC-CIT-05 (`automated: false`), run with the semantic evaluation of the prompt change; evidence in `docs/test-reports/REQ-006.md`.

### search (REQ-007, ADR-006)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-SRC-01 | REQ-007 C-001; INV-005 | exception | `search_api = anthropic`, `research_model = openai:gpt-4.1`; also `search_api = openai` with `gpt-4.1` (no prefix) | `SearchConfigError` naming `search_api` and `research_model`; the fake model is never called | `test/offline/test_search_configuration.py::test_native_search_model_mismatch_rejected` |
| TC-SRC-02 | REQ-007 C-002; INV-005 | exception | `search_api = none` with no MCP config, with an MCP config without `url`, and with one without `tools` | `SearchConfigError` naming `search_api` and `mcp_config` before any research | `test/offline/test_search_configuration.py::test_no_search_tool_rejected` |
| TC-SRC-03 | REQ-007 C-003; INV-005 | exception | `search_api = "bing"` in `configurable`, and `SEARCH_API=bing` in the environment | `SearchConfigError` listing `anthropic, openai, tavily, none` | `test/offline/test_search_configuration.py::test_unsupported_provider_rejected` |
| TC-SRC-04 | REQ-007 C-004 | normal | `search_api = tavily` with a Tavily key | No error; the researcher tools include the Tavily search tool (named `tavily_search`; see blueprint §11, open item 5) | `test/offline/test_search_configuration.py::test_valid_tavily_configuration_accepted` |
| TC-SRC-05 | INV-005 | exception | An invalid configuration passed directly to the researcher subgraph | `SearchConfigError` before the researcher's model call | `test/offline/test_search_configuration.py::test_researcher_entry_validates` |
| TC-SRC-06 | INV-005 (REQ-001 rule) | exception | `task_contract_enabled = True` with `search_api = openai` | `SearchConfigError` naming both settings | `test/offline/test_search_configuration.py::test_task_contract_rejects_native_search` |
| TC-SRC-07 | REQ-007 C-005 | human | A reviewer follows the README without reading source code | They can configure each built-in provider and an MCP search server and find the needed keys | `docs/review-memo.md` (search provider configuration review) |

- **Regression:** all of `test/offline/`.
- **Live or human checks:** TC-SRC-07 (`automated: false`), recorded as a `REVIEW-NNN` entry.

### evaluation (REQ-009, REQ-010, ADR-007)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-EVA-01 | REQ-009 C-001 | normal | Distinct markers for question, report, reference answer, brief and evidence; a fake judge that records requests | Correctness gets question, report and reference answer; completeness gets the brief; groundedness gets the evidence; no placeholder is left unformatted | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |
| TC-EVA-02 | REQ-009 C-002, M-001; INV-009 | boundary | Ratings `1` and `5`; then `0`, `6`, `True`, `"4"`, `4.0`, `4.5`, `NaN`, `inf`, `None` | Scores `0.2` and `1.0`; every other value gives `not_evaluable` with no score; `out_of_range_score_count == 0` | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |
| TC-EVA-03 | REQ-009 C-003; INV-009 | exception | Missing or blank reference answer, brief or evidence, one at a time | Only the metric that needs it is `not_evaluable`; the others are scored | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |
| TC-EVA-04 | REQ-009 C-004; INV-009 | exception | No extracted claim; a non-boolean `grounded` value; a metric group that raises; two grounded claims out of four | The first three make only the affected metric `not_evaluable`; the last gives `0.5` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |
| TC-EVA-05 | INV-009 | regression | Import `test.evaluators` with no API key; call each adapter with a fake judge | No model client at import; names, keys and return shapes as in the baseline; `not_evaluable` gives `score=None` | `test/offline/test_evaluator_validity.py::test_adapter_keeps_baseline_shape` |
| TC-EVA-06 | REQ-010 C-001 | normal | An existing report and question through `evaluate_existing_report`, with the research graph build and search functions patched to fail if called | The judge requests contain both texts unchanged; research and search call counts are 0; `report_id` is the SHA-256 of the report | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research` |
| TC-EVA-07 | REQ-010 C-002 | exception | A blank or whitespace-only report or question, directly and through the command | `EvaluationInputError` (command exit code 2); the judge is called 0 times | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |
| TC-EVA-08 | REQ-010 C-003 | human | A reviewer follows the README to score a report file | They can run it and read the per-metric results without changing code | `docs/review-memo.md` (report evaluation entry review) |

- **Regression:** all of `test/offline/`; the six function names of `test/evaluators.py` used by `test/run_evaluate.py`.
- **Live or human checks:** TC-EVA-08 (`automated: false`), recorded as a `REVIEW-NNN` entry.

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
