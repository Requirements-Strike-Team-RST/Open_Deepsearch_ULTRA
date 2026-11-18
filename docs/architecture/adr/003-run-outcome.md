# ADR-003: The run output states its outcome, decided before and after the report

- **Status:** Proposed
- **Date:** 2026-11-17
- **Module:** delivery
- **Owner:** AlchemyHAN
- **Evaluation:** EVAL-003 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-004 | C-004 | When no validated finding exists, the report model must not be called. The decision must run **before** `final_report_generation`. |
| REQ-004 | C-005, C-006 | A report error makes the run `failed`; truncated findings make it `partial`. These are known only **inside** `final_report_generation`. |
| REQ-004 | C-001, C-002, C-003, M-001 | `complete` only for a `covered` exit with every task complete; the failed-task list and the limitations section are written by code. |

## 2. Context

- `deep_researcher.py` L715 wires `research_supervisor → final_report_generation` unconditionally; nothing can stop the report model from running.
- `final_report_generation` (L607-697) returns its errors as report text (L670-674, L686-690, L693-697) and cuts findings from the end on a token-limit error (L676-682) without saying so.
- `AgentState` (`state.py` L65-72) has no field for the outcome.
- The graph is compiled at import time (L719), so a configuration flag can change behaviour but not topology.

## 3. Decision

Use EVAL-003 option B. Active when `task_contract_enabled` is `True`.

### 3.1 One new node before the report

```text
research_supervisor → check_research_outcome → final_report_generation → END
                                             ↘ END   (outcome failed)
```

`check_research_outcome` is a thin node that calls `assess_research(task_results, exit_reason, exit_detail)` and routes with `Command(goto=...)`, as the baseline nodes do. The edge `research_supervisor → final_report_generation` is replaced by `research_supervisor → check_research_outcome`. No other edge changes. With the flag off the node returns `Command(goto="final_report_generation")` with no update.

### 3.2 Outcome rule

`assess_research` applies, in order:

1. `failed` when `exit_reason` is `failed`, or when no task result is `complete` or `partial` (no validated finding). The node then ends the run with `research_outcome = "failed"`, `final_report = ""`, `outcome_detail` and `failed_tasks`, and `notes` cleared (override `[]`, as the baseline report node does); it adds no message, and the report model is never called.
2. `complete` when `exit_reason` is `covered` and every task result is `complete`.
3. `partial` otherwise.

For outcomes 2 and 3 the node writes `failed_tasks` and goes to `final_report_generation`. It does not store the provisional outcome: `final_report_generation` calls `assess_research` again on the same state and gets the same answer, because the function is pure.

### 3.3 After the report

When the flag is on, `final_report_generation` keeps its retry loop but no longer returns error text as a report. At the end it calls `finish_outcome(decision, report_error=..., findings_truncated=...)` with the decision from `assess_research`:

- a report error (non-token-limit error, unknown model limit, or retries used up) → `failed`, `final_report = ""`, the error in `outcome_detail`; the node adds no error `AIMessage` to `messages`, so error text appears only in `outcome_detail`;
- findings truncated and a report generated → `partial` (a `complete` run becomes `partial`);
- otherwise the provisional outcome.

When the outcome is `partial`, the node appends `render_limitations(task_results, findings_truncated)` to the report: one line per failed or partial task with its reason, the unanswered questions (`unanswered_questions(task_results)`, `state.py`), and a line when findings were left out. The text is built from structured results only; the report model never writes it. The `AIMessage` added to `messages` holds the same text as `final_report`, including the limitations section, because chat clients show `messages`.

### 3.4 Known limit

"No finding was left out of the report" is checked only for findings the system cut. If the report model silently omits a finding it was given, nothing detects it (RISK-001). Checking the report body is out of scope (REQ-006, INV-004 Deferred).

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — compute the outcome inside `final_report_generation` from `notes` | By then the report model is already running, so C-004 cannot hold, and `notes` carry no task status. |
| C — a separate error node behind a conditional edge | Two nodes would assemble the outcome; two places could decide `complete`. |
| One `finalize` node that runs twice, before and after the report (an earlier draft of this ADR) | Needs a `run_finalized` marker to tell its passes apart and loops until the recursion limit if the marker is missed. The post-report step fits inside `final_report_generation`, which already knows about errors and truncation. |

The full comparison is in EVAL-003.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `delivery/outcome.py` | Pre-report outcome | `assess_research(task_results, exit_reason, exit_detail) -> OutcomeDecision` | `check_research_outcome`, `final_report_generation` |
| `delivery/outcome.py` | Post-report outcome | `finish_outcome(decision, *, report_error: str \| None, findings_truncated: bool) -> tuple[Outcome, str]` | `final_report_generation` |
| `delivery/outcome.py` | Limitations section | `render_limitations(task_results, findings_truncated) -> str` | `final_report_generation` |
| `deep_researcher.py` | New thin node | `check_research_outcome(state: AgentState, config) -> Command[Literal["final_report_generation", "__end__"]]` | graph |

`OutcomeDecision` fields: `outcome` (`complete`, `partial`, `failed`), `report_allowed: bool`, `detail: str`, `failed_tasks: list[TaskResult]` (results with status `failed`). All three functions are pure: no I/O, no model, no mutation of their arguments.

Shared contracts changed: new `AgentState` fields `research_outcome`, `outcome_detail`, `failed_tasks` (`memory-design.md` §5). Readers: evaluation and any caller of the graph.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** `AgentState.research_outcome`, `outcome_detail`, `failed_tasks`. Reads `task_results`, `exit_reason`, `exit_detail` from ADR-001.
- **Runtime policies:** POL-015, POL-016, POL-017.
- **Invariants:** INV-002.
- **Deterministic boundary:** the outcome, whether the report model may run, and the limitations text are decided by `delivery/outcome.py` from structured state.

## 7. Verification

The cases for REQ-004 are in `verification-constraints.md` §7 (delivery). `assess_research`, `finish_outcome` and `render_limitations` are tested as pure functions; C-002, C-004 and C-005 also run the graph with a fake report model.

## 8. Consequences

- **Positive:** a caller can tell complete, partial and failed runs apart without reading the report; a run with nothing found never calls the report model; a cooperative-sounding report cannot hide a failed task.
- **Negative:** the topology gains one node, recorded in blueprint §3; `final_report_generation` gets a flag-on branch.
- **Neutral:** with the flag off, the new node only forwards to the report node, and the report content is as in the baseline.

## 9. Implementation Steps

1. `state.py`: add `research_outcome: Literal["complete", "partial", "failed"] | None`, `outcome_detail: str` and `failed_tasks: Annotated[list[TaskResult], override_reducer]` to `AgentState`.
2. Add `delivery/outcome.py` with the functions of §5. Docstrings name `REQ-004, ADR-003, INV-002`.
3. Add the node `check_research_outcome` and rewire `research_supervisor → check_research_outcome`. Do not add conditional edges.
4. In `final_report_generation`, when the flag is on: record `findings_truncated` and the report error instead of returning error text; call `finish_outcome`; append `render_limitations` when the outcome is `partial`; write `final_report`, `research_outcome` and `outcome_detail`. Keep the baseline return values for the flag-off path.
5. Run the checks in `verification-constraints.md` §4 and record them in `docs/build-reports/REQ-004.md`.
