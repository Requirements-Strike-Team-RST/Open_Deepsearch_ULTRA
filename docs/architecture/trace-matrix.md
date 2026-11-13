# Requirement Traceability Matrix

> **Purpose:** Trace every requirement through Design, Code, Test and runtime Monitor, so that any requirement can be followed forward to its evidence at any time.
> **Authoritative for:** the links between artifacts. Requirement content, type and status come from `docs/req/requirements.yaml`; if a cell here disagrees with it, the YAML wins and the row is corrected.
> **Maintained by:** each module owner fills the rows of their requirements: architectural consequence, ADR / invariant, component and verification method during SA; code and test evidence after implementation.
> **Last updated:** 2026-11-12

Cell conventions: `TBD` = not decided yet; `Proposed:` = from a document that is not yet accepted; `planned:` = named in the requirement's `verification` field but not written yet. Update the row in the same PR whenever the requirement's design, code or tests change.

## Traceability Matrix

| Requirement ID | Title | Type | Status | Architectural Consequence | ADR / Invariant | Enforcing Component / Code | Test / Evidence | Runtime Monitor |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | Typed task contract | functional | approved | TBD | INV-003 (Proposed) | Proposed: `orchestration/` | planned: `test/offline/test_task_contract.py` | `unsourced_finding_counted_count` |
| REQ-002 | No task lost or silently completed | invariant | approved | TBD | INV-002 (Proposed) | Proposed: `orchestration/` or `delivery/` | planned: `test/offline/test_failure_propagation.py` | `dropped_delegation_count`, `failure_text_in_notes_count` |
| REQ-003 | Coverage-based termination | invariant | approved | TBD | INV-003 (Proposed) | Proposed: `orchestration/` | planned: `test/offline/test_research_termination.py`, `test/live/test_research_termination_live.py` | `exit_without_single_reason_count`, `premature_complete_accepted_count` |
| REQ-004 | Run outcome in output | functional | approved | TBD | INV-002 (Proposed) | Proposed: `delivery/` | planned: `test/offline/test_run_outcome.py` | `false_complete_outcome_count` |
| REQ-005 | Compression keeps newest context | invariant | approved | TBD | INV-001 (Proposed) | Proposed: `context/` | planned: `test/offline/test_context_compaction.py` | `latest_turn_preservation_rate`, `orphan_tool_message_count` |
| REQ-006 | One citation format | invariant | approved | TBD | TBD | Proposed: `citations/` | planned: `test/offline/test_prompt_citation_contract.py`, `test/live/test_report_citations_live.py` | TBD |
| REQ-007 | Search setup documented and validated | functional | approved | Fail-fast: pure search-configuration validation before any model/search call; static MCP declaration is distinct from runtime availability | INV-005 (Proposed); ADR-001 (Proposed) | Proposed: `search/` validator called from `clarify_with_user` and `researcher` | planned: `test/offline/test_search_configuration.py`; review in `docs/review-memo.md` (C-005) | TBD |
| REQ-008 | Search fallback | functional | approved | TBD | INV-005 (Proposed) | Proposed: `search/` | planned: `test/offline/test_search_fallback.py` | TBD |
| REQ-009 | Valid evaluator scores | invariant | approved | TBD | TBD | Proposed: `test/evaluation/` | planned: `test/offline/test_evaluator_validity.py` | `out_of_range_score_count` |
| REQ-010 | Evaluate an existing report | functional | approved | TBD | TBD | Proposed: `test/evaluation/` | planned: `test/offline/test_report_evaluation_entry.py`; review in `docs/review-memo.md` | TBD |

## Example (Reference Only — VHIS Course Example)

| Requirement ID | Title | Type | Status | Architectural Consequence | ADR / Invariant | Enforcing Component / Code | Test / Evidence | Runtime Monitor |
|---|---|---|---|---|---|---|---|---|
| REQ-VHIS-NFR-SAFETY-001 | Over-limit claims are never auto-approved | invariant | verified (example) | Fail-closed boundary: over-limit claims cannot be auto-approved | ADR-001 / INV-001 | Policy Core: `enforce_business_limits()` | Boundary ±1 tests; adversarial fuzzing (0 escapes) | `over_limit_auto_approve_count` = 0 |
