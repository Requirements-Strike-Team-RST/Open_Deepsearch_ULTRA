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
| REQ-003 (consumed) | C-001, C-002, C-004, C-005 | Supplies the single exit reason the outcome rule reads, and reads the same task results to compute coverage. |
| REQ-002 (produced by ADR-001) | C-005, C-007 | Supplies the per-task results the outcome is computed from. |

This ADR is deliberately the **topology and outcome** decision only. The failure handling inside the research phase is ADR-001. Both are needed; neither is usable alone.

## 2. Context

The baseline wires `research_supervisor → final_report_generation` unconditionally (`src/open_deep_research/deep_researcher.py` L715) and `AgentState` (`state.py` L65–72) has no field stating whether research succeeded. `final_report_generation` (L607–697) returns its own errors as report text (L670–674, L686–690, L693–697), truncates findings from the end on a token-limit error (L676–682), and still ends the run normally. Nothing in the graph can *refuse* to generate a report, and nothing can label the run afterwards.

Three facts constrain the shape:

1. The decision must see the research exit reason and the task results, which exist **before** report generation, and the report-stage error and truncation flags, which exist **only after** it.
2. A LangGraph node can only pass data to the next node through **state fields**; a value that is returned but has no matching state field is dropped. So the task results must be a field that spans the subgraph boundary — this is why §3.2 adds one.
3. The graph is compiled at import time (`deep_researcher.py` L719), before any run-time `Configuration` exists, so the flag of §3.5 cannot choose a different topology.

`structural-constraints.md` §2 keeps the baseline topology fixed unless an accepted ADR changes it. This is that ADR. The baseline nodes route with `Command(goto=...)` (L77, L464) and use no `add_conditional_edges`; this ADR follows the same convention (§3.4).

## 3. Decision

**3.1 One new node.** The top-level graph becomes:

```text
clarify_with_user → write_research_brief → research_supervisor → finalize
final_report_generation → finalize → END
```

Baseline edges kept verbatim: `START → clarify_with_user`, `clarify_with_user → write_research_brief` / `END` (via `Command`), `write_research_brief → research_supervisor`, and the supervisor subgraph's internal edges. Changed: the edge `research_supervisor → final_report_generation` now goes to `finalize`. Added: `final_report_generation → finalize`. Nothing else is added.

`finalize` has **no edge to or from `research_supervisor`**; once the research phase ends it never runs again.

**3.2 The task results survive the subgraph boundary.** `DelegationOutcome` is an in-process value and cannot cross from the supervisor subgraph to `finalize`, so the results are carried in state:

- `SupervisorState.task_results: Annotated[list[TaskResult], operator.add]` — written by the delivery-owned fan-out region of `supervisor_tools` (ADR-001 §5), one entry per `ConductResearch` call, appended across turns.
- `AgentState.task_results: Annotated[list[TaskResult], operator.add]` — receives the subgraph's output when the research phase ends; read by `evaluate_before_report` and by orchestration's coverage check (REQ-003).

`TaskResult` is the REQ-001 contract type, so the field is **defined together with the orchestration owner**: orchestration needs it to compute coverage and delivery needs it to compute the outcome. The field name, the type and the reducer are fixed in `state.py` and approved by both owners before implementation (RISK-002). `failed_tasks` is *derived* from `task_results` by `finalize`, not carried separately through the subgraph.

**3.3 Two passes, identified by an explicit marker.** `finalize` tells its passes apart by `run_finalized`, never by whether `final_report` holds a value: a failed report leaves that field empty, so the presence test would be ambiguous exactly in the case that matters.

- First pass (`run_finalized` absent or `False`): calls `evaluate_before_report`. If `report_allowed` is true it returns `Command(goto="final_report_generation")` and writes the marker; otherwise it returns `Command(goto=END)` with the failed outcome, an empty `final_report`, the failed-task list and the marker.
- Second pass (`run_finalized` true): calls `evaluate_after_report`, returns `Command(goto=END)` with the final outcome. It writes neither `failed_tasks` nor anything else the first pass owns.

**3.4 Routing uses `Command` only.** `finalize` decides its destination by returning `Command(goto=...)`, exactly as `clarify_with_user` (L77) and `researcher_tools` (L464) already do. There is **no** `route_after_finalize` function, no `add_conditional_edges`, and no `finalize → END` edge: those would be a second place deciding the same thing, and a later edit could update one and forget the other. The only edges `finalize` participates in are the one coming in from `research_supervisor`, the one coming in from `final_report_generation`, and the ones its `Command` declares.

**3.5 The flag cannot select a topology.** Because of the import-time compilation, `finalize` is always in the graph. `Configuration.enforce_delivery_outcome` changes behaviour only: while it is `False`, `finalize` is a transparent pass-through (`goto="final_report_generation"` on the first pass with only the marker, and `goto=END` with the report unchanged on the second), so the baseline behaviour and results are preserved. There is no second graph to maintain and no build-time switch.

**3.6 The outcome rule.** `evaluate_before_report` applies the rule in this order, which is INV-002 condition **S5** restated with each step named:

1. `failed` when the exit reason is `failed`, or when no validated finding exists. `report_allowed` is `False` in exactly these two cases.
2. `complete` when the exit reason is `covered` **and** every task result is `complete` **and** no finding was withheld by the system.
3. `partial` otherwise — exit reason `budget_exhausted` or `stalled`, some task result not `complete`, or findings withheld.

`evaluate_after_report` folds in the report stage: a non-empty `report_error` makes the outcome `failed`; `report_truncated` makes it `partial`; an outcome already `failed` stays `failed`. `render_limitations` writes the section from structured results and is not called when the outcome is `failed` (POL-007).

**3.7 Limitation, recorded deliberately.** "No finding was left out of the report" is checked only for findings the system withheld itself, because truncation happens in `final_report_generation` and is reported through `report_truncated`. Whether the report model paraphrased or omitted a finding it was given is not parsed out of the report body; deterministic checking of generated reports is out of scope for REQ-006 and is not widened here. Recorded as RISK-001.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| Compute the outcome inside `final_report_generation`, reading only `notes` (EVAL-002 A) | `notes` is free text with no task id, status or reason, so the failed-task list cannot be produced; the report model would already have been called before anything could say it must not be; the report model would remain the only guard against a failed run looking complete. |
| A dedicated error node behind a conditional edge (EVAL-002 C) | The outcome assembly and the limitations text would be duplicated in two nodes, giving two places that can decide `complete` and two places to keep consistent, plus more edges. |
| Conditional edges plus a router function next to `finalize` | Two mechanisms deciding the same destination; a later edit can change one and miss the other. The baseline already uses `Command` for every conditional jump. |
| Return `DelegationOutcome.failures` from `supervisor_tools` and expect `finalize` to read it | A LangGraph node only communicates through state fields; an unnamed return value is dropped at the subgraph boundary. The results must be a state field (§3.2). |
| Select a baseline graph at run time when the flag is `False` | Not implementable: the graph is compiled at import time, when no run-time `Configuration` exists. |
| Post-process the result outside LangGraph | The caller's result would come from wrapper code rather than from the graph's own output, `M-001` would have to be measured on the wrapper, and the report-model call that C-004 forbids could not be prevented. |

The full comparison is in EVAL-002.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `state.py` (shared) | Carry per-task results across the subgraph boundary; the REQ-001 contract type | `SupervisorState.task_results: Annotated[list[TaskResult], operator.add]`; `AgentState.task_results: Annotated[list[TaskResult], operator.add]` | `supervisor_tools` (write), `finalize` and orchestration's coverage check (read) |
| `deep_researcher.py` | Thin node: route with `Command` and write the decision into state; never compute the decision | `async finalize(state: AgentState, config: RunnableConfig) -> Command[Literal["final_report_generation", "__end__"]]` | graph edges |
| `deep_researcher.py` | Write the report-stage signals instead of swallowing them | `final_report_generation` returns `report_truncated: bool` and `report_error: str` alongside the report | graph edge to `finalize` |
| `delivery/outcome.py` | Decide the outcome before report generation and whether the model may run | `evaluate_before_report(state: Mapping) -> OutcomeDecision` | `finalize`, first pass |
| `delivery/outcome.py` | Fold the report stage into the outcome and produce the final update | `evaluate_after_report(state: Mapping) -> OutcomeDecision` | `finalize`, second pass |
| `delivery/outcome.py` | Write the system limitations section from structured results, never from model text | `render_limitations(outcome: str, results: Sequence[TaskResult], unanswered: Sequence[str], truncated: bool) -> str` | `evaluate_after_report` |
| `delivery/outcome.py` | The decision value; `update` is the dict `finalize` merges into its `Command` | `OutcomeDecision` (dataclass) | `finalize` |

**`OutcomeDecision` fields:**

| Field | Type | Meaning |
|---|---|---|
| `outcome` | `Literal["complete", "partial", "failed"]` | the outcome this pass decides |
| `report_allowed` | `bool` | whether `final_report_generation` may run; `True` for every outcome except `failed` on the first pass |
| `failed_tasks` | `list[dict]` | one entry per failed or unrun task: `task_id`, `reason`, `category`, `message`; derived from `task_results` |
| `unanswered` | `list[str]` | required questions no validated finding answered (empty when orchestration does not provide them) |
| `reason_code` | `str` | the exit reason or report-stage cause that produced the decision, e.g. `covered`, `budget_exhausted`, `stalled`, `no_finding`, `report_error`, `report_truncated` |
| `update` | `dict` | the state update `finalize` applies: `research_outcome`, `final_report`, and on the first pass `failed_tasks` as `{"type": "override", "value": [...]}` |

Both functions are **pure**: they take a mapping, return a decision, mutate no argument and perform no I/O. `finalize` never derives an outcome itself; it only routes and merges `update`.

**Graph changes, exhaustively:**

| Change | Detail |
|---|---|
| Node added | `add_node("finalize", finalize)` |
| Edge changed | `add_edge("research_supervisor", "finalize")` replaces `add_edge("research_supervisor", "final_report_generation")` |
| Edge added | `add_edge("final_report_generation", "finalize")` |
| Routing | inside the nodes only, through `Command(goto=...)` — no `add_conditional_edges`, no `finalize → END` edge |
| Unchanged | `START → clarify_with_user`, `clarify_with_user → write_research_brief` / `END`, `write_research_brief → research_supervisor`, and the supervisor subgraph's internal edges |

Shared contracts changed (`structural-constraints.md` §6): `SupervisorState.task_results`, `AgentState.task_results` (co-owned with orchestration, since REQ-003 reads them), and `AgentState.failed_tasks`, `research_outcome`, `run_finalized`, `report_truncated`, `report_error`. Owners who must approve: orchestration (REQ-001, REQ-003), the integrator (blueprint §5 and §7), and delivery.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** `task_results` (both states, `operator.add`), plus the five `AgentState` fields of §3.3 and §3.5. Details in `memory-design.md` §5 (delivery).
- **Runtime policies:** POL-005 (report model raises), POL-006 (findings truncated), POL-007 (no validated finding). POL-001 to POL-004 belong to ADR-001. Details in `runtime-policy-catalog.md` §2 (delivery).
- **Invariants:** INV-002 conditions S5 (outcome rule) and S6 (system-written limitations section).
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
| INV-002 S5, S6 | The outcome rule and the single appended limitations section; TC-004-01 to TC-004-09 | `test/offline/test_run_outcome.py` |
| `task_results` crosses the boundary | A subgraph output carrying task results is visible to `finalize`; without the field, `evaluate_before_report` sees nothing (TC-004-12) | `test/offline/test_run_outcome.py` |
| Pass marker | A failed report (empty `final_report`) still detected as the second pass (TC-004-11) | `test/offline/test_run_outcome.py` |
| No duplicate records | The second pass does not append to `failed_tasks` (TC-004-10) | `test/offline/test_run_outcome.py` |
| Routing | `finalize` reaches `final_report_generation` on the first pass and `END` otherwise, with no conditional-edge router (TC-004-13) | `test/offline/test_run_outcome.py` |

## 8. Consequences

**Positive**

- The run output states its own outcome, so a caller can tell complete from partial or failed without reading the report.
- The report model can be *prevented* from running when nothing was found, instead of being asked to admit it.
- The limitations section is written by code from structured results, so a cooperative-sounding report model cannot hide a failure.
- `task_results` in state gives orchestration's coverage check and delivery's outcome rule the same evidence, instead of two views of the same run.
- Routing stays in one place (`Command`), matching every existing node, so there is no second router to keep in sync.

**Negative**

- The baseline topology gains one node and one edge; every later reader of the blueprint must see this as a recorded exception.
- `finalize` runs twice and stays in the graph even with the flag off, so the pass-through path must be tested as well as the active path.
- `task_results` is a co-owned field: a change needs orchestration's agreement, so the two branches must be merged in a known order.
- Five fields are added to `AgentState` and one to `SupervisorState`, so the merge with the orchestration branch matters.

**Neutral**

- With `enforce_delivery_outcome=False` the observable behaviour is the baseline, at the cost of one extra node execution per run.

## 9. Implementation Steps

The coding agent implements these in order.

1. **Agree the shared field with the orchestration owner** before writing code: `SupervisorState.task_results` and `AgentState.task_results`, both `Annotated[list[TaskResult], operator.add]`, where `TaskResult` is the REQ-001 contract type. Record the agreement in the PR review. If orchestration wants a different field name, use theirs and update §3.2 and §5 of this ADR in the same PR.

2. **Add the state fields** in `src/open_deep_research/state.py`: `task_results` on `SupervisorState` and `AgentState`; and on `AgentState` only, `failed_tasks: Annotated[list[dict], override_reducer] = []`, `research_outcome: str`, `run_finalized: bool = False`, `report_truncated: bool = False`, `report_error: str`. Use the existing `override_reducer` (L55–60) for `failed_tasks`, as `notes` does; do **not** use `operator.add` for it. Do not change existing fields.

3. **Create `delivery/outcome.py`** with `OutcomeDecision` (the six fields of §5) and the three functions. Docstring names `REQ-004, ADR-002, INV-002`.
   - `evaluate_before_report(state)`: apply the ordered rule of §3.6 exactly. Read the exit reason, `task_results` and the validated findings from the mapping; derive `failed_tasks` from the task results; set `report_allowed` to `False` only for the two `failed` cases; put `research_outcome`, `final_report` (empty on failure) and, on the first pass, `failed_tasks` as `{"type": "override", "value": [...]}` into `update`.
   - `evaluate_after_report(state)`: read `report_error` and `report_truncated`; a non-empty `report_error` gives `failed`, `report_truncated` gives `partial`, an already-`failed` outcome stays `failed`; call `render_limitations` only when the outcome is `partial`; put `research_outcome`, `final_report` and `run_finalized: True` into `update`.
   - `render_limitations(outcome, results, unanswered, truncated)`: build the section from the failed and partial task results, the unanswered questions and `truncated`; it must contain no model-generated text and must not be produced when the outcome is `failed`.
   - All three are pure: return a new decision, mutate no argument, no I/O, no model client, no import from another extension module.

4. **Add the delivery package skeleton** if ADR-001 has not already: `src/open_deep_research/delivery/__init__.py` exporting `evaluate_before_report`, `evaluate_after_report`, `render_limitations`, `OutcomeDecision`, and add `"open_deep_research.delivery"` to `packages` in `pyproject.toml`.

5. **Write the report-stage signals** in `final_report_generation` (`deep_researcher.py`): on the truncation branch return `report_truncated=True` instead of only cutting `findings`; on a non-token-limit error return `report_error=str(e)` with `final_report=""` instead of error text as the report; on the "maximum retries exceeded" path set `report_error` too; on success return `report_truncated=False` and `report_error=""`. Keep the existing retries and the `enforce_delivery_outcome` guard so the baseline return value is unchanged while the flag is off.

6. **Add the `finalize` node** to `deep_researcher.py`. Read the pass from `state.get("run_finalized", False)`; never infer it from `final_report`. Return `Command(goto="final_report_generation")` on the first pass when `report_allowed`, and `Command(goto=END)` otherwise, merging `OutcomeDecision.update` into the command's update. When `enforce_delivery_outcome` is `False`, return `Command(goto="final_report_generation", update={"run_finalized": True})` on the first pass and `Command(goto=END)` with the state unchanged on the second. Do **not** add a router function or a conditional edge.

7. **Wire the graph** as tabulated in §5: `add_node("finalize", finalize)`, `add_edge("research_supervisor", "finalize")` replacing the old edge, and `add_edge("final_report_generation", "finalize")`. Do not add `finalize → END` and do not add `add_conditional_edges`. Do not compile a second graph for the flag-off case: the graph is compiled at import time (L719).

8. **Write `task_results` from the fan-out.** In the delivery-owned region of `supervisor_tools` (ADR-001 §5), append one `TaskResult` per `ConductResearch` call to `task_results`, so it reaches `AgentState` when the subgraph ends. Do not return `DelegationOutcome` expecting `finalize` to read it — only state fields cross the boundary.

9. **Check.** Run `uv run python scripts/validate_requirements.py`, `uv run ruff check src/open_deep_research`, `uv run ruff format` on the new and changed files only, and `uv run pytest test/offline`. Record the commands and results in `docs/build-reports/REQ-004.md`.

10. **Do not** change the approved tests, the acceptance thresholds, or any file outside `delivery/outcome.py`, `state.py`, `configuration.py` and `deep_researcher.py`. If the graph change does not behave as §5 describes, or `task_results` cannot be agreed with orchestration, stop and report it: that is an architecture change (`Prompt.md` §10).
