# Requirement Traceability Matrix

> **Purpose:** Trace every requirement through Design, Code, Test and runtime Monitor, so that any requirement can be followed forward to its evidence at any time.
> **Authoritative for:** the links between artifacts. Requirement content, type and status come from `docs/req/requirements.yaml`; if a cell here disagrees with it, the YAML wins and the row is corrected.
> **Maintained by:** each module owner fills the rows of their requirements: architectural consequence, ADR / invariant, component and verification method during SA; code and test evidence after implementation.
> **Last updated:** 2026-11-17

Cell conventions: `TBD` = not decided yet; `Proposed:` = from a document that is not yet accepted; `planned:` = named in the requirement's `verification` field but not written yet. Update the row in the same PR whenever the requirement's design, code or tests change. Test cases per criterion are in `verification-constraints.md` §7.

## Traceability Matrix

| Requirement ID | Title | Type | Status | Architectural Consequence | ADR / Invariant | Enforcing Component / Code | Test / Evidence | Runtime Monitor |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | Typed task contract | functional | approved | Proposed: code builds a `TaskSpec` per delegation; task status is derived by code from findings whose URLs a tool in that task returned | ADR-001 / INV-006 (Proposed) | Proposed: types in `state.py`; `orchestration/contracts.py`; called from `supervisor_tools`, `researcher_tools`, `compress_research` | planned: `test/offline/test_task_contract.py` (TC-ORC-01 to 06) | `unsourced_finding_counted_count` |
| REQ-002 | No task lost or silently completed | invariant | approved | Proposed: bounded, fail-isolated fan-out with one join; one `TaskResult` per delegation; `notes` built only from complete and partial tasks | ADR-002, ADR-001 / INV-007, INV-002 (Proposed) | Proposed: `delivery/execution.py` (`run_delegations`); cap branch and `render_notes` in orchestration | planned: `test/offline/test_failure_propagation.py` (TC-DLV-01 to 08) | `dropped_delegation_count`, `failure_text_in_notes_count` |
| REQ-003 | Coverage-based termination | invariant | approved | Proposed: completion is a request; one pure `select_exit` chooses `covered > budget_exhausted > stalled > failed` | ADR-001 / INV-003 (Proposed) | Proposed: `orchestration/termination.py`; called from `supervisor`, `supervisor_tools` | planned: `test/offline/test_research_termination.py`, `test/live/test_research_termination_live.py` (TC-ORC-07 to 13) | `exit_without_single_reason_count`, `premature_complete_accepted_count` |
| REQ-004 | Run outcome in output | functional | approved | Proposed: new node `check_research_outcome` before the report; `final_report_generation` folds in report errors and truncation; limitations written by code | ADR-003 / INV-002 (Proposed) | Proposed: `delivery/outcome.py`; node `check_research_outcome`; `AgentState.research_outcome`, `outcome_detail`, `failed_tasks` | planned: `test/offline/test_run_outcome.py` (TC-DLV-09 to 16) | `false_complete_outcome_count` |
| REQ-005 | Compression keeps newest context | invariant | approved | Proposed: remove whole turns from the oldest end; classify with `compression_model`; an unreducible history ends `failed/token_limit` | ADR-004 / INV-001 (Proposed) | Proposed: `context/trimming.py`, `context/recovery.py`; called from `compress_research` | planned: `test/offline/test_context_compaction.py` (TC-CTX-01 to 06) | `latest_turn_preservation_rate`, `orphan_tool_message_count` |
| REQ-006 | One citation format | invariant | approved | Proposed: one text contract inserted into both prompts; report checking stays out of scope | ADR-005 / INV-008 (Proposed); INV-004 (Deferred) | Proposed: `citations/contract.py`, used by `prompts.py` | planned: `test/offline/test_prompt_citation_contract.py`, `test/live/test_report_citations_live.py` (TC-CIT-01 to 05) | live citation check (C-004) |
| REQ-007 | Search setup documented and validated | functional | approved | Proposed: pure validator runs first in `clarify_with_user` and `researcher`; README search guide | ADR-006 / INV-005 (Proposed) | Proposed: `search/validation.py`; `README.md` | planned: `test/offline/test_search_configuration.py` (TC-SRC-01 to 06); review in `docs/review-memo.md` (TC-SRC-07) | TBD |
| REQ-008 | Search fallback | functional | approved | TBD: SA not started | TBD | Proposed: `search/` | planned: `test/offline/test_search_fallback.py` | TBD |
| REQ-009 | Valid evaluator scores | invariant | approved | Proposed: raw rating validated by code; failing metrics isolated as `not_evaluable` | ADR-007 / INV-009 (Proposed) | Proposed: `test/evaluation/metrics.py`; adapter `test/evaluators.py` | planned: `test/offline/test_evaluator_validity.py` (TC-EVA-01 to 05) | `out_of_range_score_count` |
| REQ-010 | Evaluate an existing report | functional | approved | Proposed: evaluation-only entry that imports no research or search code | ADR-007 (Proposed) | Proposed: `test/evaluation/entry.py` | planned: `test/offline/test_report_evaluation_entry.py` (TC-EVA-06, 07); review in `docs/review-memo.md` (TC-EVA-08) | TBD |

## Example (Reference Only — VHIS Course Example)

| Requirement ID | Title | Type | Status | Architectural Consequence | ADR / Invariant | Enforcing Component / Code | Test / Evidence | Runtime Monitor |
|---|---|---|---|---|---|---|---|---|
| REQ-VHIS-NFR-SAFETY-001 | Over-limit claims are never auto-approved | invariant | verified (example) | Fail-closed boundary: over-limit claims cannot be auto-approved | ADR-001 / INV-001 | Policy Core: `enforce_business_limits()` | Boundary ±1 tests; adversarial fuzzing (0 escapes) | `over_limit_auto_approve_count` = 0 |
