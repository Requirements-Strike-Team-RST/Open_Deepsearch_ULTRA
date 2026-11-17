# Invariants

> **Purpose:** Properties of the research agent (the product) that no change may violate, each traced to a requirement, an enforcing component, a test and a fallback. Rules for coding agents belong in `docs/architecture/permission-model.md` and `.opencode/rules.md`, not here.
> **Authoritative for:** the detailed rule behind each `invariant`-type or safety-relevant requirement. Where an entry here differs from `docs/req/requirements.yaml`, the requirement wins and the difference must be reported.
> **Maintained by:** each module owner adds the entries for their module; they are integrated and renumbered before SA Review.
> **Status:** All entries are *Proposed* until SA Review. Enforcing components are responsibility assignments, not implemented code.
> **Last updated:** 2026-11-13

Every entry uses the same fields:

- **Statement** — the property, in one or two sentences.
- **Module** — the module from `architecture-blueprint.md` §4 that enforces it.
- **Source** — the requirement IDs it details.
- **Status** — *Proposed*, *Accepted*, *Deferred* or *Retired*.
- **Enforcing component** — where the property is enforced.
- **Verification** — the offline test that fails on violation, plus any runtime monitor.
- **Fallback** — what the system does when the property cannot be kept.

## INV-001 — Compression never drops the newest context

- **Statement:** When compression trims context to fit a token limit, the research topic, the compression instruction, the latest AI turn and the tool results after it are never removed, and no tool result is kept without the AI message that requested it.
- **Module:** context
- **Source:** REQ-005
- **Status:** Proposed
- **Enforcing component:** `plan_trim()` in `src/open_deep_research/context/trimming.py`, reached through `compress_with_recovery()` in `context/recovery.py` from the token-limit branch of `compress_research` (`deep_researcher.py` L511-585). The protected region is computed from message types by `segment_turns()` in `context/messages.py`.
- **Verification:** `test/offline/test_context_compaction.py::test_oldest_turns_removed_first`, `::test_no_orphan_tool_messages`; monitors `latest_turn_preservation_rate == 1.0` and `orphan_tool_message_count == 0`, computed from the same helpers.
- **Fallback:** remove whole turns from the oldest end, continuing until no removable turn is left; if the limit still cannot be met, end the task with a failed result of category `token_limit` carried by the declared `ResearcherOutputState.research_outcome` field, which `supervisor_tools` reads. Never drop the latest turn, never return placeholder text as a summary on the new path, and never re-raise out of the researcher subgraph, because `asyncio.gather` would discard every parallel researcher's result.

## INV-002 — No failure is reported as complete research

- **Statement:** A run with an unhandled exception, a failed or partial research task, a non-`covered` exit or a failed report generation never ends with research outcome `complete`.
- **Module:** delivery
- **Source:** REQ-002, REQ-004
- **Status:** Proposed
- **Enforcing component:** `delivery.execution.run_delegations` (failure isolation, queuing and join); `delivery.outcome.evaluate_before_report` / `evaluate_after_report` (outcome and limitations section).
- **Verification:** `test/offline/test_failure_propagation.py`, `test/offline/test_run_outcome.py`; monitor `false_complete_outcome_count == 0`. The conditions S1–S6 below each name their test.
- **Fallback:** record the failed task with category and message, keep sibling results, and deliver outcome `partial` with a system-added limitations section, or `failed` with an empty report. Never swallow an exception.
- **Conditions (delivery module):** the statement is expanded into conditions S1–S6 in `INV-002-d` below, so that a test can fail on each one separately.

## INV-003 — Research is bounded and every exit has one reason

- **Statement:** With orchestration enabled, every research-loop exit records exactly one reason selected deterministically in the order `covered > budget_exhausted > stalled > failed`; neither a completion request nor a child failure independently ends the loop. The loop processes at most its configured number of supervisor turns, and each task starts at most its actual tool-invocation budget; only `covered` is eligible for a `complete` run outcome, whose decision belongs to REQ-004.
- **Module:** orchestration
- **Source:** REQ-001, REQ-003
- **Status:** Proposed
- **Enforcing component:** Proposed ADR-002 `orchestration/termination.py` and `orchestration/budget.py`, using the one receipt maintained by `orchestration/evidence.py` and called from the existing nodes. `completed_supervisor_turns` increments once after processing and joining a turn; `unchanged_eligible_turns` ignores think-only turns. Execution permits are reserved before local awaitables start; unstarted reservations are not counted as actual starts, and validation never spends permits again.
- **Verification:** PLANNED: `test/offline/test_research_termination.py::test_exit_reason_precedence`, `::test_iteration_cap_counts_n1_n2`, `::test_turns_without_progress_exit_stalled`, and `test/offline/test_task_contract.py::test_tool_budget_counts_started_invocations`; complete cases are in `verification-constraints.md` §7. Proposed monitors: `exit_without_single_reason_count == 0`, `premature_complete_accepted_count == 0`; none is implemented or measured yet.
- **Fallback:** refuse premature completion and return the original unanswered questions. At a cap, dispatch nothing further, record pending valid delegations as `failed/not_run`, then apply the same selector after including their questions; `covered` still has precedence. Refuse unsupported native-search execution before the first researcher request capable of native tool execution while orchestration is enabled. Supervisor retry exhaustion is a selector input, not an unconditional `failed` override; retries remain bounded.

## INV-004 — Every report citation resolves to a retrieved source

- **Statement:** Every citation identifier in a report resolves to exactly one source that was retrieved during the run; a report whose required facts lack resolvable citations is not delivered as complete.
- **Module:** citations
- **Source:** none. REQ-006 covers citation format only and lists deterministic citation validation as out of scope.
- **Status:** Deferred
- **Enforcing component:** a citation validator at report generation (proposed).
- **Verification:** offline fixed-source tests for missing, duplicate and malformed identifiers and unsourced facts; monitor `citation_integrity_violation_count == 0`.
- **Fallback:** correct only format issues that the source list determines; otherwise mark the evidence as missing. Never fabricate a URL or reference.

## INV-005 — Search results are never mistaken for evidence they do not contain

- **Statement:** On every run, before any model or search call, a search configuration that names an unsupported provider, pairs a native provider with a `research_model` of another provider, or leaves no search and no valid MCP declaration is rejected. A statically declared MCP that cannot provide a usable search tool at runtime fails that research explicitly, while a search that returns no results is a successful search that carries no evidence.
- **Module:** search
- **Source:** REQ-007, REQ-008
- **Status:** Proposed
- **Enforcing component:** the pure search-configuration validator and search-capability predicate in `search/`, called from `clarify_with_user` and `researcher` (ADR-001, Proposed); the runtime MCP failure policy `POL-002` (Proposed; ADR-001 §9, U-1). The search adapter is reached through `utils.get_all_tools()`.
- **Verification:** `test/offline/test_search_configuration.py`, `test/offline/test_search_fallback.py` with fake providers (normal, empty, timeout, invalid, unknown); see ADR-001 §11 and `verification-constraints.md` §7.
- **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured. (Fallback behaviour itself is REQ-008 and out of REQ-007 scope.)

## INV-006 — Task evidence and status are derived from the task's execution

- **Statement:** With orchestration enabled, every counted finding references only HTTP(S) URLs returned by matched, successful tool invocations of that same task, and task status and coverage are derived from those validated findings. Model-supplied provenance, status, cost and prose never establish evidence; recorded spending includes started invocations even when they fail.
- **Module:** orchestration
- **Source:** REQ-001 C-001–C-004, M-001
- **Status:** Proposed
- **Enforcing component:** ADR-002 shared types in `state.py`; `orchestration/evidence.py` holds a separate code-owned `TaskExecutionEvidence` for each task; `orchestration/contracts.py` parses and validates the compression sidecar against the registered spec and receipt. The receipt survives trimming outside model history, with a serializable `task_evidence_snapshot` for checkpoints. ADR-002 §3.5 also checks the matching code-observed compression completion before parsing: explicit length or unknown completion cannot gain authority from parseable text; no extra DTO field or context retry is introduced.
- **Verification:** PLANNED: `test/offline/test_task_contract.py::test_unretrieved_source_does_not_count`, `::test_model_cannot_forge_task_evidence`, `::test_failure_preserves_execution_cost`, `::test_task_evidence_survives_context_trimming`, and `::test_sidecar_schema_and_source_resolution`; shared schema cases are in `test/offline/test_contracts.py::test_task_result_contract_boundaries`. Proposed monitor: `unsourced_finding_counted_count == 0`; URL membership does not prove semantic entailment.
- **Fallback:** discard a syntactically valid finding whose source was not retrieved, then recompute status; a malformed sidecar/result becomes `failed/invalid_result`. Preserve trusted tool-call cost and reported token totals on failures instead of inventing zero spending; usage_complete=False makes incomplete usage explicit. Reject malformed well-identified raw arguments with a diagnostic and matching tool response; reject malformed IDs before registration with bounded valid-history feedback, without inventing a question or dispatching a researcher; the proposed distinction between a raw intent and an accepted delegation requires reader review in ADR-002.

## INV-007 — Final research output is one complete run snapshot

- **Statement:** Every accepted valid delegation has one terminal result, and the supervisor never finalizes while a task it started remains running; receipt replay must not duplicate or relabel a finished task. Final output replaces the run's results and notes together, and notes contain only deterministic renderings of validated finding claims and their sources, with no sidecar, failure, placeholder, reflection or unvalidated summary text.
- **Module:** orchestration; delivery supplies dispatch/join and result collection
- **Source:** REQ-001, REQ-003; contributor interface for REQ-002 C-005, C-006, C-007
- **Status:** Proposed
- **Enforcing component:** ADR-002 `orchestration/contracts.py` final snapshot builder and `orchestration/termination.py` finalization, after delivery's join boundary. Supervisor-local `delegation_receipts` tracks raw intent and accepted task lifecycles; plain result deltas append during the run, while final `task_results` and `notes` use override envelopes. `RunRecord.from_state()` reads final main snapshots only.
- **Verification:** PLANNED: `test/offline/test_contracts.py::test_run_record_final_snapshot_contract`, `::test_task_results_reducer_append_and_override`, and `test/offline/test_orchestration_integration.py::test_finalization_joins_then_replaces_notes_and_results`, `::test_receipt_replay_does_not_duplicate_tasks`, `::test_new_run_resets_private_progress`; `test/offline/test_task_contract.py::test_notes_render_only_validated_findings` covers the report boundary. These do not claim process-crash exactly-once execution.
- **Fallback:** terminalize pending valid delegations as `not_run` before exit selection; retain sibling results and actual cost. Reject inconsistent final snapshots with `ValueError` for the REQ-004 reader's explicit policy; never repair a missing result with successful prose or reuse a prior run's ledger. A running supervisor delta without `exit_reason` is internal state, not an invalid final snapshot.
## INV-006 — Every delegated task ends with a terminal result

- **Statement:** For every delegation the supervisor makes, exactly one terminal `TaskResult` exists by the time the research phase ends; no delegation is left queued, running or unanswered, and a delegation that was never run ends `failed` with reason `not_run`.
- **Module:** delivery
- **Source:** REQ-002 (C-004, C-005, C-006; M-001)
- **Status:** Proposed
- **Enforcing component:** `delivery.execution.run_delegations`, which builds one `TaskRunRecord` per `TaskSpec`, bounds concurrency with a semaphore so the limit queues work instead of rejecting it, gathers with `return_exceptions=True`, and asserts before returning that no record is still `queued` or `running`. The results reach the rest of the run through the `task_results` state field (ADR-002 §3.2).
- **Verification:** `test/offline/test_failure_propagation.py` (C-004, C-005, C-006); monitor `dropped_delegation_count == 0`, computed from `DelegationOutcome.dropped_count`, which counts only specs with **no terminal `TaskResult` at all**. A `not_run` result is terminal and therefore not dropped.
- **Fallback:** a delegation that cannot be run ends `failed` with an error category and reason of `not_run` and its original error; the phase never ends while a task it started is still pending. Never answer a delegation with a text that is not a `TaskResult`, and never drop a delegation silently.
- **Ownership note:** which delegations count as unrun is decided by the research loop (orchestration, REQ-003); producing their `not_run` results is this module's job. The split of `supervisor_tools` is in ADR-001 §5.

## INV-002-d — Detailed conditions for INV-002 (delivery)

**Module:** delivery. The statement in INV-002 is unchanged; these conditions say what "reported", "complete" and "failure" concretely mean for this module, so that a test can fail on each one separately.

| # | Condition | Enforced by | Test |
|---|---|---|---|
| S1 | An exception raised while one task runs makes only that task `failed`, with an error category and the original message; it never ends the research phase on its own. | `delivery.execution.classify_task_error`, `run_delegations` | `test/offline/test_failure_propagation.py::test_child_exception_becomes_failed_result` |
| S2 | A failed task does not remove a sibling's result: findings of tasks that succeeded reach the tool messages and `notes`. | `run_delegations` (`return_exceptions=True`) | `::test_sibling_result_kept_on_failure` |
| S3 | No task the supervisor started is still pending when the fan-out returns. | `run_delegations` final assertion | `::test_no_task_running_after_join` |
| S4 | Failure text and placeholder text never become a finding; `notes` contains only validated findings, and every failure appears only in `failed_tasks`. | `run_delegations` note filtering; `supervisor_tools` | `::test_failure_text_not_in_notes` |
| S5 | The outcome is `complete` only when the exit reason is `covered`, every task result is `complete` and no finding was withheld by the system; any other end is `partial`, and a `failed` exit, no validated finding or a failed report generation is `failed`. | `delivery.outcome.evaluate_before_report`, `evaluate_after_report` | `test/offline/test_run_outcome.py::test_covered_run_is_complete`, `::test_failed_task_makes_run_partial`, `::test_non_covered_exit_is_partial`, `::test_no_finding_run_is_failed`, `::test_report_error_run_is_failed` |
| S6 | When the outcome is `partial`, the limitations section naming each failed or partial task, each unanswered required question and any withheld findings is written by code from structured results and appended to the report; the report model is never asked to disclose it. When the outcome is `failed`, the report is empty and error text appears only in the failure fields. | `delivery.outcome.render_limitations`; `supervisor_tools` and `final_report_generation` | `::test_failed_task_makes_run_partial`, `::test_truncated_findings_make_run_partial`, `::test_no_finding_run_is_failed` |

**Status:** Proposed. **Runtime monitor:** `false_complete_outcome_count == 0` (REQ-004 M-001).
## INV-006 — The two research prompts state one identical citation format

- **Statement:** `compress_research_system_prompt` and `final_report_generation_prompt` each state exactly one citation format, and both state the same one: numbered inline citations `[n]` and a closing `### Sources` section listing each cited URL once as `[n] Title: URL`, numbered without gaps, with the report prompt renumbering the citations of all findings into one sequence.
- **Module:** citations
- **Source:** REQ-006
- **Status:** Proposed
- **Enforcing component:** `src/open_deep_research/citations/contract.py` as the single source of truth, interpolated into both prompts in `prompts.py` (ADR-001).
- **Verification:** `test/offline/test_prompt_citation_contract.py` (C-001, C-002, C-003, the format-safety guard `test_assembled_prompts_format_without_leftover_placeholders`, and the negative test `test_format_checks_detect_violations`); live check `test/live/test_report_citations_live.py` (C-004) monitors renumbering in generated reports.
- **Fallback:** a CI failure of the offline inspection tests blocks the merge; revert to the last green prompt version. Renumbering correctness in generated reports is monitored, not enforced.

## INV-006 — Every metric result is valid or explicitly not evaluable

- **Statement:** Every metric result is either `scored` with a score in `[0, 1]`, or `not_evaluable` with a null score and a reason. A `scored` result comes only from a strict integer judge rating `1..5`, validated on the raw judge value before any Pydantic or other type conversion, or, for groundedness only, from a ratio over at least one valid extracted claim. An invalid rating, missing input, empty claim list, invalid claim or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics. A judge authentication or permission failure marks the affected group `not_evaluable`, preserves every completed score and sets the run-level `judge_failure`.
- **Module:** evaluation
- **Source:** REQ-009
- **Status:** Proposed
- **Enforcing component:** `test/evaluation/validation.py`, `test/evaluation/metrics.py`, `test/evaluation/judge.py` and the compatibility adapter in `test/evaluators.py`.
- **Verification:** `test/offline/test_evaluator_validity.py`; monitor `out_of_range_score_count == 0`; the CLI judge-failure cases are in `test/offline/test_report_evaluation_entry.py`.
- **Fallback:** return `not_evaluable` with `score=None` and a reason code such as `invalid_rating`, `missing_input`, `no_claims`, `invalid_claim`, `evaluator_error`, `judge_unavailable`, `judge_authentication` or `judge_permission`; continue the other metric groups. Never clamp, round, default or replace a missing score with zero.

## INV-007 — Evaluation-only entry does not perform research or search

- **Statement:** The evaluation-only entry scores exactly the report it is given, using its question and optional reference answer, research brief and evidence. At the import layer it imports no `open_deep_research.deep_researcher`, `open_deep_research.utils`, `test.run_evaluate` or search/MCP module. At the client layer it creates no research/search client. At the network layer it makes no research/search request; the only permitted network request is the judge model call. It rejects a blank question or report before any evaluator runs.
- **Module:** evaluation
- **Source:** REQ-010
- **Status:** Proposed
- **Enforcing component:** `test/evaluation/entry.py`, `test/evaluation/judge.py` and the CLI; the import boundary keeps `open_deep_research.deep_researcher`, `open_deep_research.utils` and search tools out of the entry.
- **Verification:** `test/offline/test_report_evaluation_entry.py`, including `::test_entry_does_not_import_research_graph` and `::test_entry_scores_supplied_report_without_research`; review of the README procedure for REQ-010 C-003.
- **Fallback:** raise `EvaluationInputError` (CLI exit `2`) for blank input and report `JudgeUnavailableError`/`JudgeAuthenticationError`/`JudgePermissionError` as the corresponding exit `3` path; never fall back to running research, searching, or generating a report. Report the metric result as `not_evaluable` when an input the metric needs is absent.

## Adding an Entry

Copy an entry, take the next free `INV-NNN` number, and fill every field. Never reuse a retired number. Add the INV ID to the requirement's row in `trace-matrix.md` and to the ADR's §6. At integration the integrator may renumber entries and updates every reference.
