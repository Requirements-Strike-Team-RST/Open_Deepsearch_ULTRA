# Invariants

> **Purpose:** Properties of the research agent (the product) that no change may violate, each traced to a requirement, an enforcing component, a test and a fallback. Rules for coding agents belong in `docs/architecture/permission-model.md` and `.opencode/rules.md`, not here.
> **Authoritative for:** the detailed rule behind each `invariant`-type or safety-relevant requirement. Where an entry here differs from `docs/req/requirements.yaml`, the requirement wins and the difference must be reported.
> **Maintained by:** each module owner adds the entries for their module; they are integrated and renumbered before SA Review.
> **Status:** All entries are *Proposed* until SA Review. Enforcing components are responsibility assignments, not implemented code.
> **Last updated:** 2026-11-12

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
- **Enforcing component:** the token-limit branch of `compress_research` and its trimming helper (module assigned in Design).
- **Verification:** `test/offline/test_context_compaction.py`; monitor `latest_turn_preservation_rate == 1.0`.
- **Fallback:** remove whole turns from the oldest end; if the limit still cannot be met, end the task with a failed result of category `token_limit`. Never drop the latest turn and never return placeholder text as a summary.

## INV-002 — No failure is reported as complete research

- **Statement:** A run with an unhandled exception, a failed or partial research task, a non-`covered` exit or a failed report generation never ends with research outcome `complete`.
- **Module:** delivery
- **Source:** REQ-002, REQ-004
- **Status:** Proposed
- **Enforcing component:** the failure branch of `supervisor_tools`; the run-outcome computation before and after `final_report_generation`.
- **Verification:** `test/offline/test_failure_propagation.py`, `test/offline/test_run_outcome.py`; monitor `false_complete_outcome_count == 0`.
- **Fallback:** record the failed task with category and message, keep sibling results, and deliver outcome `partial` with a system-added limitations section, or `failed` with an empty report. Never swallow an exception.

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

- **Statement:** Every search source is reached through the single tool entry point and returns the same result contract; an unknown provider is rejected at start-up, an invalid result is a failed search, and an empty result is a successful search that carries no evidence.
- **Module:** search
- **Source:** REQ-007, REQ-008
- **Status:** Proposed
- **Enforcing component:** search configuration validation at graph start; the search adapter called through `utils.get_all_tools()`.
- **Verification:** `test/offline/test_search_configuration.py`, `test/offline/test_search_fallback.py` with fake providers (normal, empty, timeout, invalid, unknown).
- **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured.

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

## Adding an Entry

Copy an entry, take the next free `INV-NNN` number, and fill every field. Never reuse a retired number. Add the INV ID to the requirement's row in `trace-matrix.md` and to the ADR's §6. At integration the integrator may renumber entries and updates every reference.
