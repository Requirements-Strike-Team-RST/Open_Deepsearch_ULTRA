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

- **Statement:** Each research loop is bounded by its iteration cap and each task by its tool-call budget; every loop exit records exactly one exit reason, and only `covered` can lead to outcome `complete`.
- **Module:** orchestration
- **Source:** REQ-001, REQ-003
- **Status:** Proposed
- **Enforcing component:** the termination check in the supervisor loop; the task budget in the task specification.
- **Verification:** `test/offline/test_research_termination.py`, `test/offline/test_task_contract.py`; monitor `exit_without_single_reason_count == 0`.
- **Fallback:** at the cap, start no new delegations, end unrun delegations as failed with reason `not_run`, and exit with `budget_exhausted`. A completion request below the coverage threshold is refused, not accepted.

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

## INV-006 — No fallback after an empty successful result

- **Statement:** A search that returns no hits without error is a successful search and terminates the fallback sequence; no further source is tried.
- **Module:** search
- **Source:** REQ-008 (C-004)
- **Status:** Proposed
- **Enforcing component:** the fallback coordinator (`search/`, ADR-002): an empty `SearchOutcome` (`found=False`) is a success and stops the attempt loop.
- **Verification:** `test/offline/test_search_fallback.py` — planned case for C-004 (empty result suppresses fallback); see ADR-002 §11 and `verification-constraints.md` §7.
- **Fallback:** return the empty success to the researcher as no evidence; do not advance to the next configured source.

## INV-007 — No fallback after an ineligible error

- **Statement:** An ineligible search error (for example a malformed query) is returned without trying any further source; fallback advances only on an eligible error.
- **Module:** search
- **Source:** REQ-008 (C-005)
- **Status:** Proposed
- **Enforcing component:** the error classification in the fallback coordinator (`search/`, ADR-002): an ineligible `SearchTerminatedFailure` ends the loop immediately.
- **Verification:** `test/offline/test_search_fallback.py` — planned case for C-005 (ineligible error suppresses fallback); see ADR-002 §11 and `verification-constraints.md` §7.
- **Fallback:** return the ineligible failure to the researcher as an error; never substitute another source.

## INV-008 — Configured source order is preserved

- **Statement:** When an eligible failure triggers fallback, the configured fallback sources are tried in their configured order, and no source is skipped or reordered.
- **Module:** search
- **Source:** REQ-008 (C-001, C-002)
- **Status:** Proposed
- **Enforcing component:** the ordered attempt loop in the fallback coordinator (`search/`, ADR-002).
- **Verification:** `test/offline/test_search_fallback.py` — planned cases for C-001 and C-002 (ordered fallback); see ADR-002 §11 and `verification-constraints.md` §7.
- **Fallback:** never reorder or skip; if the configured order cannot be followed, the run receives an explicit failure rather than a silently different order.

## INV-009 — Exhausting all eligible sources produces an explicit failure

- **Statement:** When every configured source fails with an eligible error, the researcher receives one explicit all-sources-failed result that lists each attempted source and its error and cannot be mistaken for an empty search result.
- **Module:** search
- **Source:** REQ-008 (C-003)
- **Status:** Proposed
- **Enforcing component:** the all-failed aggregation in the fallback coordinator (`search/`, ADR-002), rendered by the thin tool-facing adapter into a distinct `ToolMessage`.
- **Verification:** `test/offline/test_search_fallback.py` — planned case for C-003 (explicit aggregate); see ADR-002 §11 and `verification-constraints.md` §7.
- **Fallback:** return the aggregate failure with every attempted source and its error; never fabricate a result and never return the empty-success marker.

## Adding an Entry

Copy an entry, take the next free `INV-NNN` number, and fill every field. Never reuse a retired number. Add the INV ID to the requirement's row in `trace-matrix.md` and to the ADR's §6. At integration the integrator may renumber entries and updates every reference.
