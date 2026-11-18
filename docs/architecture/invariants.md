# Invariants

> **Purpose:** Properties of the research agent (the product) that no change may violate, each traced to a requirement, an enforcing component, a test and a fallback. Rules for coding agents belong in `docs/architecture/permission-model.md` and `.opencode/rules.md`, not here.
> **Authoritative for:** the detailed rule behind each `invariant`-type or safety-relevant requirement. Where an entry here differs from `docs/req/requirements.yaml`, the requirement wins and the difference must be reported.
> **Maintained by:** each module owner adds the entries for their module; they are integrated and renumbered before SA Review.
> **Status:** All entries are *Proposed* until SA Review, except INV-004 (*Deferred*). Enforcing components are responsibility assignments, not implemented code.
> **Last updated:** 2026-11-17

Every entry uses the same fields:

- **Statement** — the property, in one or two sentences.
- **Module** — the module from `architecture-blueprint.md` §4 that enforces it.
- **Source** — the requirement IDs it details.
- **Status** — *Proposed*, *Accepted*, *Deferred* or *Retired*.
- **Enforcing component** — where the property is enforced.
- **Verification** — the offline test that fails on violation, plus any runtime monitor.
- **Fallback** — what the system does when the property cannot be kept.

Unless stated otherwise, an invariant holds when the feature flag of its module is on (`structural-constraints.md` §8).

## INV-001 — Compression never drops the newest context

- **Statement:** When compression trims context to fit a token limit, the research topic (or task brief), the compression instruction, the latest AI turn and the tool results after it are never removed, and no tool result is kept without the AI message that requested it.
- **Module:** context
- **Source:** REQ-005
- **Status:** Proposed
- **Enforcing component:** `context/trimming.py` (`trim_oldest_turn`), used by `context/recovery.py` (`compress_with_recovery`) from `compress_research` (ADR-004).
- **Verification:** `test/offline/test_context_compaction.py`; monitors `latest_turn_preservation_rate == 1.0`, `orphan_tool_message_count == 0`.
- **Fallback:** remove whole turns from the oldest end; when nothing removable is left, the task ends `failed` with category `token_limit`. Never drop the latest turn and never return placeholder text as a summary.

## INV-002 — No failure is reported as complete research

- **Statement:** A run with a failed or partial task, a non-`covered` exit, no validated finding or a failed report generation never ends with research outcome `complete`. Failure and placeholder text never reach `notes` or the report; a `partial` report always carries the limitations section written by code.
- **Module:** delivery
- **Source:** REQ-002, REQ-004
- **Status:** Proposed
- **Enforcing component:** `delivery/outcome.py` (`assess_research`, `finish_outcome`, `render_limitations`) called from `check_research_outcome` and `final_report_generation` (ADR-003); `orchestration/contracts.py` (`render_notes`) for `notes` (ADR-001).
- **Verification:** `test/offline/test_run_outcome.py`, `test/offline/test_failure_propagation.py::test_failure_text_not_in_notes`; monitors `false_complete_outcome_count == 0`, `failure_text_in_notes_count == 0`.
- **Fallback:** deliver `partial` with the limitations section, or `failed` with an empty report and the reason in `outcome_detail`. Never swallow an exception.

## INV-003 — Research is bounded and every exit has one reason

- **Statement:** The research loop ends at the baseline iteration cap (`research_iterations > max_researcher_iterations`, checked on every turn) and each task runs at most its tool-call budget. Every loop exit records exactly one exit reason, chosen in the order `covered`, `budget_exhausted`, `stalled`, `failed`. A completion request or a turn without tool calls never ends the loop below the coverage threshold, and only `covered` can lead to outcome `complete`.
- **Module:** orchestration
- **Source:** REQ-001, REQ-003
- **Status:** Proposed
- **Enforcing component:** `orchestration/termination.py` (`select_exit`) called from `supervisor` and `supervisor_tools`; the budget check in `researcher_tools` (ADR-001).
- **Verification:** `test/offline/test_research_termination.py`; monitors `exit_without_single_reason_count == 0`, `premature_complete_accepted_count == 0`.
- **Fallback:** at the cap, run no new delegation, end the turn's delegations as `not_run` and exit with the reason `select_exit` returns. Refuse a completion request below the threshold and send the unanswered questions back to the supervisor.

## INV-004 — Every report citation resolves to a retrieved source

- **Statement:** Every citation identifier in a report resolves to exactly one source that was retrieved during the run; a report whose required facts lack resolvable citations is not delivered as complete.
- **Module:** citations
- **Source:** none. REQ-006 covers citation format only and lists deterministic citation validation as out of scope.
- **Status:** Deferred
- **Enforcing component:** a citation validator at report generation (not designed).
- **Verification:** offline fixed-source tests for missing, duplicate and malformed identifiers and unsourced facts; monitor `citation_integrity_violation_count == 0`.
- **Fallback:** correct only format issues that the source list determines; otherwise mark the evidence as missing. Never fabricate a URL or reference.

## INV-005 — A run never starts research without a valid search source

- **Statement:** A configuration that names an unsupported search provider, pairs native search with a research model whose provider is not on that search's allowlist, has neither a search provider nor a usable MCP declaration, or enables the task contract with native search is rejected before the first model or search call of a run, with an error that names the setting to change. A run whose assembled tools contain no search tool stops before any model call with a "no search available" error.
- **Module:** search
- **Source:** REQ-007 (REQ-001 for the task-contract rule); Discussion #19 (U-1 to U-4)
- **Status:** Proposed
- **Enforcing component:** `search/validation.py` (`load_search_config`, `require_search_tools`) called first in `clarify_with_user` and `researcher` (ADR-006). Holds with no flag.
- **Verification:** `test/offline/test_search_configuration.py` with a fake model that fails the test if it is called and a fake MCP loader.
- **Fallback:** raise `SearchConfigError` or `SearchUnavailableError`; never switch to a provider that is not configured.

## INV-006 — Task status comes only from sourced findings

- **Statement:** A finding counts only if every URL it cites was returned by a tool call in the same task. Task status (`complete`, `partial`, `failed`) is derived by code from the counted findings; the model's own claims about status, coverage or sources are never used. A result that breaks the contract is `failed` with category `invalid_result`.
- **Module:** orchestration
- **Source:** REQ-001
- **Status:** Proposed
- **Enforcing component:** `orchestration/contracts.py` (`extract_urls`, `build_task_result`) called from `researcher_tools` and `compress_research` (ADR-001).
- **Verification:** `test/offline/test_task_contract.py`; monitor `unsourced_finding_counted_count == 0`.
- **Fallback:** drop a finding with an unretrieved URL and derive the status from the rest; a malformed findings block makes the task `failed/invalid_result`.

## INV-007 — Every delegation ends with exactly one task result

- **Statement:** Every accepted delegation ends with exactly one `TaskResult` before the research phase continues or ends. No delegation is dropped or left running: delegations above the concurrency limit are queued and run, delegations left at loop exit end `failed/not_run`, and a researcher exception fails only its own task.
- **Module:** delivery (fan-out and join); orchestration (`not_run` at loop exit)
- **Source:** REQ-002
- **Status:** Proposed
- **Enforcing component:** `delivery/execution.py` (`run_delegations`, ADR-002); the cap branch of `supervisor_tools` (ADR-001 §3.4).
- **Verification:** `test/offline/test_failure_propagation.py`; monitor `dropped_delegation_count == 0`.
- **Fallback:** a task that cannot run or fails ends `failed` with a category and the error message; siblings keep their results. `asyncio.CancelledError` is re-raised, never turned into a result.

## INV-008 — Both research prompts state one identical citation format

- **Statement:** `compress_research_system_prompt` and `final_report_generation_prompt` each state exactly one citation format, and it is the same one: numbered inline citations `[n]` and a closing `### Sources` section listing each cited URL once as `[n] Title: URL`, numbered without gaps. The report prompt also asks for one renumbered sequence across all findings.
- **Module:** citations
- **Source:** REQ-006
- **Status:** Proposed
- **Enforcing component:** `citations/contract.py`, inserted into both prompts by `prompts.py` (ADR-005). Holds with no flag.
- **Verification:** `test/offline/test_prompt_citation_contract.py`; live check `test/live/test_report_citations_live.py`.
- **Fallback:** a failing offline test blocks the merge. Renumbering in generated reports is monitored, not enforced.

## INV-009 — Every metric result is a valid score or explicitly not evaluable

- **Statement:** Every metric result is either `scored` with a score in `[0, 1]`, or `not_evaluable` with no score and a reason. A score comes only from an integer judge rating 1–5 (checked on the raw value) divided by 5, or from a groundedness ratio over at least one claim. One failing metric never stops the others.
- **Module:** evaluation
- **Source:** REQ-009
- **Status:** Proposed
- **Enforcing component:** `test/evaluation/metrics.py` (`validate_rating`, `groundedness_ratio`, `evaluate_metrics`) (ADR-007). Holds with no flag.
- **Verification:** `test/offline/test_evaluator_validity.py`; monitor `out_of_range_score_count == 0`.
- **Fallback:** return `not_evaluable` with a reason; never clamp, round or default a score to zero.

## INV-010 — Search fallback never hides a failure or changes the configured sources

- **Statement:** When a search fails with an eligible error, the configured fallback sources are tried in their configured order, each at most once per call. An empty result and an ineligible error never trigger fallback. When every source fails, the researcher receives one explicit failure that lists each source and its error and cannot be mistaken for an empty result. Only configured Tavily and MCP sources are used.
- **Module:** search
- **Source:** REQ-008
- **Status:** Proposed
- **Enforcing component:** `search/fallback.py` (`apply_search_fallback`, `classify_search_error`) called from `researcher_tools` (ADR-008). Holds whenever `search_fallback` is not empty.
- **Verification:** `test/offline/test_search_fallback.py` with fake tools.
- **Fallback:** raise `AllSourcesFailedError` listing every attempt; never fabricate a result and never use a source that is not configured.

## Adding an Entry

Copy an entry, take the next free `INV-NNN` number, and fill every field. Never reuse a retired number. Add the INV ID to the requirement's row in `trace-matrix.md` and to the ADR's §6. At integration the integrator may renumber entries and updates every reference.
