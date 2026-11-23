# Bug Diary

> **Purpose:** Significant bugs: symptom, reproduction, root cause, fix, and the invariant gap each one revealed.
> **Maintained by:** humans; agents propose entries in their reports.
> **Last updated:** 2026-11-23

## Entry Template

### BUG-NNN: <one-line symptom>

- **Date found / fixed:** YYYY-MM-DD / YYYY-MM-DD
- **Requirement / invariant:** REQ-NNN / INV-NNN
- **Symptom:** what was observed.
- **Reproduction:** minimal steps or test.
- **Root cause:** file and line, and why.
- **Fix:** PR link and summary.
- **Invariant gap:** which missing rule or test let it through, and the entry added.

## Entries

This diary covers bugs introduced by this team's implementation or tests, and failures exposed by the new behaviour in live runs. It excludes defects already present in upstream Open Deep Research.

The first implementation pass reported 13 failing offline cases and attributed them to the tests. After the tests were corrected and strengthened against the ADRs, 29 cases failed on the first-pass code. These are test counts, not distinct bug counts. The [build report](build-reports/REQ-001-010-build.md#5-correction-pass-2026-11-20) and [test-defect record](build-reports/REQ-008-test-defects.md) give the full findings. Implementation and harness fixes are in [PR #24](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/24) unless otherwise noted.

### BUG-001: A failed run still called the report model

- **Date found / fixed:** 2026-11-20 / 2026-11-20
- **Requirement / invariant:** REQ-004 / INV-002
- **Symptom:** A run assessed as `failed` still invoked `final_report_generation`.
- **Reproduction:** `test/offline/test_run_outcome.py`, case C-004, on the compiled graph from `check_research_outcome`.
- **Root cause:** `deep_researcher_builder` had a static edge from `check_research_outcome` to `final_report_generation`. LangGraph follows that edge as well as the `Command(goto=END)` returned on the failed path.
- **Fix:** PR #24 (`c8a008c`). The static edge was removed. The node routes only with `Command`: `final_report_generation` when a report is allowed, `END` when the outcome is `failed` (ADR-003 §3.1).
- **Invariant gap:** The first tests checked the `Command` and did not run the compiled graph, so the extra edge was invisible. C-004, C-002 and C-005 now start from the compiled graph.

### BUG-002: A supervisor model failure skipped exit selection

- **Date found / fixed:** 2026-11-20 / 2026-11-20
- **Requirement / invariant:** REQ-003 / INV-003
- **Symptom:** When the supervisor model raised, the loop ended `failed` and wrote no `notes`, whatever the task results already in state would have justified.
- **Reproduction:** `test/offline/test_research_termination.py`, the supervisor-failure exit.
- **Root cause:** `supervisor` caught the model error and returned a hard-coded failure instead of calling `select_exit`.
- **Fix:** PR #24 (`c8a008c`). The failure goes through `select_exit` (ADR-001 §3.4 step 5), so an already covered run can still exit `covered`.
- **Invariant gap:** The exit-reason tests did not drive the model-failure branch. That branch is now part of `test_research_termination.py`.

### BUG-003: Context trimming separated a tool result from the wrong turn

- **Date found / fixed:** 2026-11-20 / 2026-11-20
- **Requirement / invariant:** REQ-005 / INV-001
- **Symptom:** With tool results stored out of call order, trimming deleted a tool result that belonged to a turn it kept, and could drop the newest turn's result.
- **Reproduction:** `test/offline/test_context_compaction.py` (TC-CTX-02) covers both out-of-order results (`a1, a2, tool_2, tool_1`) and a separate history with an unmatched tool result.
- **Root cause:** `context/trimming.py` paired each `ToolMessage` with an `AIMessage` by position in the list. ADR-004 §3 pairs them by `tool_call_id`.
- **Fix:** PR #24 (`c8a008c`). `trim_oldest_turn` indexes turns by `AIMessage.tool_calls[].id`, deletes the oldest whole turn, and leaves an unmatched tool result in place.
- **Invariant gap:** The first test repeated one `AIMessage` object, so it could not tell position pairing from id pairing. The history is now a real id-paired one. The same pass also fixed `compress_with_recovery` dropping the compression system prompt on retry (ADR-004 §3).

### BUG-004: Search fallback did not follow the configured sources

- **Date found / fixed:** 2026-11-20 / 2026-11-20
- **Requirement / invariant:** REQ-008 / INV-010
- **Symptom:** The wrapper could try sources outside the configured order. A call to the supplied Tavily tool could also bypass it and invoke the shared `utils.tavily_search` instead.
- **Reproduction:** `test/offline/test_search_fallback.py` (TC-SRC-13 and the ineligible-error case).
- **Root cause:** `search/fallback.py` applied wrapping rules beyond ADR-008 §3.2–§3.4.
- **Fix:** PR #24 (`c8a008c`). `apply_search_fallback` wraps only listed Tavily and MCP tools, tries each configured source at most once, and raises `AllSourcesFailedError` with every attempt when all of them fail. The original tools are not mutated. `classify_search_error` uses the exception type, not the message text.
- **Invariant gap:** The first fakes awaited a plain return value and constructed `MissingAPIKeyError` with an argument that tavily-python 0.7.x does not accept, so the suite failed before it could check the fallback order. Those fakes were corrected first; the code failures that remained were this defect.

### BUG-005: Later delegations were answered with an empty tool-call id

- **Date found / fixed:** 2026-11-20 / 2026-11-20
- **Requirement / invariant:** REQ-001, REQ-002 / INV-007
- **Symptom:** On a turn after the first, the `ToolMessage` written for a delegation had an empty `tool_call_id`, so the supervisor model did not receive that task's result as the reply to its call. A rejected delegation produced two tool messages.
- **Reproduction:** `test/offline/test_failure_propagation.py` with a prior task `T1` still in state, and `test/offline/test_task_contract.py`.
- **Root cause:** `supervisor_tools` built the tool message without copying the id from that turn's tool call, and the rejection path appended a second message.
- **Fix:** PR #24 (`c8a008c`). Each accepted delegation gets one `ToolMessage` whose `tool_call_id` is the call's id. A rejected delegation gets one message. The researcher is invoked with the run's config (ADR-001 §3.4, ADR-002 §3).
- **Invariant gap:** The first loop merged state with `dict.update`, so a reducer bug and a missing id could not be told apart. The tests now run the compiled supervisor subgraph.

### BUG-006: Live tests called the synchronous graph API

- **Date found / fixed:** 2026-11-21 / 2026-11-21
- **Requirement / invariant:** REQ-003 C-006 and REQ-006 C-004 (live test harness).
- **Symptom:** `TypeError: No synchronous function provided to "clarify_with_user"` stopped the live citation test before research began. [NoPumpkinz](https://github.com/NoPumpkinz) found and reported it while testing PR #24.
- **Reproduction:** Run `test/live/test_report_citations_live.py::test_reports_use_numbered_citations` with live settings on the pre-fix revision. The termination suite used the same synchronous entry point.
- **Root cause:** The tests called `graph.stream()`, but the research graph nodes are async.
- **Fix:** [PR #24 follow-up](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/24#issuecomment-7062017465) (`150302f`). Both tests now share a helper built on `astream()`. Clarification is disabled because unattended runs cannot answer a follow-up question.
- **Invariant gap:** Offline CI did not exercise the live harness. The follow-up run reached the model call but was blocked by HTTP 402 (insufficient balance); this confirmed the async entry fix, not a live citation pass.

### BUG-007: The offline test harness overwrote task results between turns

- **Date found / fixed:** 2026-11-20 / 2026-11-20
- **Requirement / invariant:** REQ-003 C-002 / INV-003.
- **Symptom:** A test of premature completion lost previously collected task results. The supervisor's next response no longer listed the already known unanswered questions.
- **Reproduction:** In the first test harness, apply a later `Command.update` containing a plain task-results list after an earlier turn has already recorded results.
- **Root cause:** `run_loop` in `test/offline/test_research_termination.py` used `dict.update`. This replaced the list instead of letting the graph's reducer append to it.
- **Fix:** PR #24. `run_loop` now invokes the compiled supervisor subgraph so the real state reducers apply. See `test_loop_refuses_completion_below_threshold`.
- **Invariant gap:** A single-turn test could not reveal that the test harness and the real graph merged state differently. The corrected test checks the unanswered questions across multiple turns.

### BUG-008: Long compression output was truncated inside the findings block

- **Date observed / mitigated:** 2026-11-20 / 2026-11-20
- **Requirement / invariant:** REQ-001 / INV-006; the no-report outcome is governed by REQ-004 / INV-002.
- **Symptom:** With the task contract enabled, a DeepSeek and Tavily trial ended with `invalid_result` tasks and no report. A separate reproduction produced an opening `<task_findings>` tag but no closing tag or `### Sources` section.
- **Reproduction:** Run a research task with several long required questions and substantial retrieved material, using the 8,192-token compression output setting. Inspect the compression output and task result.
- **Root cause:** The required structured findings and sources follow a long prose summary. In the reproduction, the configured **output** budget ran out before those sections were complete. This was not an input-context rejection, so token-limit recovery did not trim any turns.
- **Mitigation, not a code fix:** At 32,768 compression output tokens, a repeat run of the same question exited `covered` and produced a `complete` report. The repository default is unchanged. See [RISK-003](architecture/risk-list.md); this is evidence for the tested configuration, not formal live acceptance.
- **Invariant gap:** Rejecting an incomplete findings block worked as intended. Offline fixtures did not reproduce a real model exhausting its output budget on a long response.

### BUG-009: The evaluation command constructed a judge before rejecting blank input

- **Date found / fixed:** 2026-11-20 / 2026-11-20
- **Requirement / invariant:** REQ-010 C-002.
- **Symptom:** The new evaluation CLI could require model credentials even to reject an empty question or report.
- **Reproduction:** Run `test/offline/test_report_evaluation_entry.py::test_command_exits_with_2_on_blank_input` against the first implementation with the judge constructor instrumented.
- **Root cause:** `main()` in `test/evaluation/entry.py` constructed the default judge before the input validation in `evaluate_existing_report()` could run.
- **Fix:** [PR #24](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/24) (`c8a008c`). The command now rejects blank input before constructing the judge.
- **Invariant gap:** Testing only the evaluation function or the exit code did not prove the CLI avoided the judge constructor. The corrected tests check blank questions and blank reports and assert that no judge is constructed.
