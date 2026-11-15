# ADR-002: A `finalize` node between the research phase and the report decides the run outcome

- **Status:** Proposed
- **Date:** 2026-11-15
- **Module:** delivery
- **Owner:** AlchemyHAN
- **Evaluation:** EVAL-002 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance
- **Builds on:** ADR-001 (task failure isolation, queuing and join). ADR-001 produces per-task results; this ADR decides what the run reports about them.

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-004 | C-001, C-002, C-003, C-004, C-005, C-006; M-001 | The outcome and the failed-task list must appear in the run output; a run with no validated finding must not call the report model; a failed report must not surface as report text; truncation must make the run `partial`. The decision therefore needs data from before *and* after report generation, which is a graph-shape question, not only a function question. |
| REQ-003 (consumed) | C-001, C-002, C-004, C-005 | Supplies the single exit reason the outcome rule reads. |
| REQ-002 (produced by ADR-001) | C-005, C-007 | Supplies the per-task results and the failed-task list the outcome is computed from. |

This ADR is deliberately the **topology** decision only. The failure handling inside the research phase (isolation, concurrency limit, join, notes separation) is ADR-001. Both are needed; neither is usable alone.

## 2. Context

The baseline wires `research_supervisor → final_report_generation` unconditionally (`src/open_deep_research/deep_researcher.py` L715) and `AgentState` (`state.py` L65–72) has no field stating whether research succeeded. `final_report_generation` (L607–697) returns its own errors as report text (L670–674, L686–690, L693–697), truncates findings from the end on a token-limit error (L676–682), and still ends the run normally. Nothing in the graph can therefore *refuse* to generate a report, and nothing can label the run afterwards.

Two facts constrain the shape:

1. The decision must see the research exit reason and the task results, which exist **before** report generation, and the report-stage error and truncation flags, which exist **only after** it.
2. The graph is compiled at import time (`deep_researcher.py` L719), before any run-time `Configuration` exists, so the flag of §4 cannot choose a different topology.

`structural-constraints.md` §2 keeps the baseline topology fixed unless an accepted ADR changes it. This is that ADR.

## 3. Decision

**3.1 One new node.** The top-level graph becomes:

```text
clarify_with_user → write_research_brief → research_supervisor → finalize
finalize → final_report_generation    (only when the outcome allows a report)
finalize → END                        (the failed path; the report model is never called)
final_report_generation → finalize
finalize → END                        (second pass, after the report stage)
```

`clarify_with_user`, its early `END`, `write_research_brief` and the supervisor subgraph are untouched. `finalize` has **no edge to or from `research_supervisor`** — once the research phase ends, it never runs again.

**3.2 Two passes, identified by an explicit marker.** `finalize` tells its passes apart by `run_finalized`, never by whether `final_report` holds a value: a failed report leaves that field empty, so the presence test would be ambiguous exactly in the case that matters.

- First pass (`run_finalized` absent or `False`): calls `evaluate_before_report`. If `report_allowed` is true it returns `Command(goto="final_report_generation")` and writes the marker; otherwise it returns `Command(goto=END)` with the failed outcome, an empty `final_report`, the failed-task list and the marker.
- Second pass (`run_finalized` true): calls `evaluate_after_report`, returns `Command(goto=END)` with the final outcome. It writes neither `failed_tasks` nor anything else the first pass owns.

**3.3 Where the decision lives.** `finalize` stays thin: it does no accounting of its own and calls `delivery/outcome.py` (ADR-001 §5), which is pure Python over state. The node's only architectural responsibility is routing and writing the decision into `AgentState`.

**3.4 The flag cannot select a topology.** Because of the import-time compilation, `finalize` is always in the graph. `Configuration.enforce_delivery_outcome` changes behaviour only: while it is `False`, `finalize` is a transparent pass-through (`goto="final_report_generation"` on the first pass with only the marker, and returns the report unchanged on the second), so the baseline behaviour and results are preserved. There is no second graph to maintain and no build-time switch.

**3.5 The state fields this ADR introduces.** `AgentState.failed_tasks` (`override_reducer`, written once by the first pass), `AgentState.research_outcome` (both passes), `AgentState.run_finalized` (the pass marker), `AgentState.report_truncated` and `AgentState.report_error` (written by `final_report_generation`, read by the second pass). Details in `memory-design.md` §5 (delivery).

**3.6 Limitation, recorded deliberately.** "No finding was left out of the report" is checked only for findings the system withheld itself, because truncation happens in `final_report_generation` and is reported through `report_truncated`. Whether the report model paraphrased or omitted a finding it was given is not parsed out of the report body; deterministic checking of generated reports is out of scope for REQ-006 and is not widened here. Recorded as RISK-001.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| Compute the outcome inside `final_report_generation`, reading only `notes` (EVAL-002 A) | `notes` is free text with no task id, status or reason, so the failed-task list cannot be produced; the report model would already have been called before anything could say it must not be; the report model would remain the only guard against a failed run looking complete. |
| A dedicated error node behind a conditional edge (EVAL-002 C) | The outcome assembly and the limitations text would be duplicated in two nodes, giving two places that can decide `complete` and two places to keep consistent, plus more edges. |
| Select a baseline graph at run time when the flag is `False` | Not implementable: the graph is compiled at import time, when no run-time `Configuration` exists. |
| Leave the graph unchanged and post-process the result outside LangGraph | The caller's result would then come from wrapper code rather than from the graph's own output, and `M-001` (`false_complete_outcome_count`) would have to be measured on the wrapper; it also cannot prevent the report-model call that C-004 forbids. |

The full comparison is in EVAL-002.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `deep_researcher.py` | Thin node: route and write the decision into state; never compute the decision | `async finalize(state: AgentState, config: RunnableConfig) -> Command[Literal["final_report_generation", "__end__"]]` | graph edges |
| `deep_researcher.py` | Router for the conditional edge out of `finalize` | `def route_after_finalize(state: AgentState) -> Literal["final_report_generation", "__end__"]` | `add_conditional_edges("finalize", ...)` |
| `deep_researcher.py` | Write the report-stage signals instead of swallowing them | `final_report_generation` returns `report_truncated: bool` and `report_error: str` alongside the report | graph edge to `finalize` |
| `delivery/outcome.py` | The decision itself (see ADR-001 §5) | `evaluate_before_report`, `evaluate_after_report`, `render_limitations`, `OutcomeDecision` | `finalize` |

**Graph changes, exhaustively:**

| Change | Detail |
|---|---|
| Node added | `add_node("finalize", finalize)` |
| Edge replaced | `research_supervisor → final_report_generation` becomes `research_supervisor → finalize` + conditional edge to `final_report_generation` or `END` |
| Edge added | `final_report_generation → finalize` |
| Edge added | `finalize → END` (the second pass and the failed path) |
| Unchanged | `START → clarify_with_user`, `clarify_with_user → write_research_brief` / `END`, `write_research_brief → research_supervisor`, and the supervisor subgraph's internal edges |

Shared contracts changed (`structural-constraints.md` §6): `AgentState.failed_tasks`, `research_outcome`, `run_finalized`, `report_truncated`, `report_error`. Owners who must approve: orchestration (REQ-001, REQ-003 — the fields sit in a state type it also extends), the integrator (blueprint §5 interface table and §7 data flow), and delivery.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** the five `AgentState` fields of §3.5; details in `memory-design.md` §5 (delivery).
- **Runtime policies:** POL-005 (report model raises), POL-006 (findings truncated), POL-007 (no validated finding). POL-001 to POL-004 belong to ADR-001. Details in `runtime-policy-catalog.md` §2 (delivery).
- **Invariants:** INV-002 conditions S5 and S6 (outcome rule and system-written limitations section). INV-006 belongs to ADR-001.
- **Deterministic boundary:** `complete` / `partial` / `failed`, whether the report model may be called, and the text of the limitations section are decided by `delivery/outcome.py` from structured state. The report model's text is data appended to, never a source of, those decisions.

## 7. Verification

| Criterion | How it is verified | Test file |
|---|---|---|
| REQ-004 C-001 | Covered exit, all tasks complete: `complete`, empty `failed_tasks`, no limitations section | `test/offline/test_run_outcome.py` |
| REQ-004 C-002 | One failed task of two: `partial`, the task named, limitations section naming it although the fake report model does not | `test/offline/test_run_outcome.py` |
| REQ-004 C-003 | Exit reason `stalled` / `budget_exhausted`: `partial` | `test/offline/test_run_outcome.py` |
| REQ-004 C-004 | No validated finding: `failed`, the report model not called, `final_report` empty, no limitations section | `test/offline/test_run_outcome.py` |
| REQ-004 C-005 | `report_error` set: `failed`, `final_report` empty, no error text in the report field | `test/offline/test_run_outcome.py` |
| REQ-004 C-006 | `report_truncated` set: `partial` with a limitations line about left-out findings | `test/offline/test_run_outcome.py` |
| INV-002 S5, S6 | The outcome rule and the single appended limitations section; see TC-004-01 to TC-004-09 | `test/offline/test_run_outcome.py` |
| Pass marker | A failed report (empty `final_report`) still detected as the second pass (TC-004-11) | `test/offline/test_run_outcome.py` |
| No duplicate records | The second pass does not append to `failed_tasks` (TC-004-10) | `test/offline/test_run_outcome.py` |

## 8. Consequences

**Positive**

- The run output states its own outcome, so a caller can tell complete from partial or failed without reading the report.
- The report model can be *prevented* from running when nothing was found, instead of being asked to admit it.
- The limitations section is written by code from structured results, so a cooperative-sounding report model cannot hide a failure.
- Both passes are thin calls into pure functions, so the decision is testable without a graph.

**Negative**

- The baseline topology gains one node and three edges; every later reader of the blueprint must see this as a recorded exception.
- `finalize` runs twice and stays in the graph even with the flag off, so the pass-through path must be tested as well as the active path; its docstring has to explain both.
- Five fields are added to a state type another owner also extends, so the merge order with the orchestration branch matters.
- `report_error` / `report_truncated` make `final_report_generation`'s return value wider, which orchestration and the Verify role must account for when reading state.

**Neutral**

- With `enforce_delivery_outcome=False` the observable behaviour is the baseline, at the cost of one extra node execution per run.

## 9. Implementation Steps

The coding agent implements these in order. Steps 1–3 are independent of ADR-001 and can land first.

1. **Add the state fields.** In `src/open_deep_research/state.py`, add to `AgentState`: `failed_tasks: Annotated[list[dict], override_reducer] = []`, `research_outcome: str`, `run_finalized: bool = False`, `report_truncated: bool = False`, `report_error: str`. Use the existing `override_reducer` (L55–60) for `failed_tasks`, as `notes` does; do not use `operator.add`. Do not change existing fields and do not add these to `SupervisorState`.

2. **Write the report-stage signals** in `final_report_generation` (`deep_researcher.py`): on the truncation branch return `report_truncated=True` instead of only cutting `findings`; on a non-token-limit error return `report_error=str(e)` with `final_report=""` instead of error text as the report; on the "maximum retries exceeded" path set `report_error` too; on success return `report_truncated=False` and `report_error=""`. Keep the existing retries and the `enforce_delivery_outcome` guard so the baseline return value is unchanged while the flag is off.

3. **Add the `finalize` node** to `deep_researcher.py` as decided in §3.2. Read the pass from `state.get("run_finalized", False)`; never infer it from `final_report`. When `enforce_delivery_outcome` is `False`, return `Command(goto="final_report_generation", update={"run_finalized": True})` on the first pass and `Command(goto=END)` with the state unchanged on the second. When it is `True`, call the `delivery/outcome.py` functions and write `failed_tasks` as `{"type": "override", "value": [...]}` on the first pass only.

4. **Add the router** `route_after_finalize` beside the node, returning the destination that `finalize` decided. It reads state only and calls no model.

5. **Wire the graph** as tabulated in §5: add the node, replace the `research_supervisor → final_report_generation` edge, add the conditional edges out of `finalize`, and add `final_report_generation → finalize`. Do **not** try to compile a second graph for the flag-off case: the graph is compiled at import time (L719) and the flag only changes node behaviour.

6. **Check.** Run `uv run python scripts/validate_requirements.py`, `uv run ruff check src/open_deep_research`, `uv run ruff format` on the new and changed files only, and `uv run pytest test/offline`. Record the commands and results in `docs/build-reports/REQ-004.md`.

7. **Do not** change the approved tests, the acceptance thresholds, or any file outside `delivery/outcome.py`, `state.py`, `configuration.py` and `deep_researcher.py`. If the graph change does not behave as §5 describes, or `finalize` cannot route as written, stop and report it: that is an architecture change (`Prompt.md` §10).
