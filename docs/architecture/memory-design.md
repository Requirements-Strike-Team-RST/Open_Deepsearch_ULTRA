# Memory and State Design

> **Purpose:** How the research agent stores, passes and discards state and memory: state structure, ownership and lifecycle.
> **Authoritative for:** state and memory design. Graph state types live in `src/open_deep_research/state.py`.
> **Maintained by:** owners of modules that add or change state write a module section (§5); §1–§4 are integrated from those sections before SA Review. Modules that do not touch state add nothing.
> **Last updated:** 2026-11-15

## 1. State Model

| State type | Graph | Key fields | Owning module | Shared contract? |
|---|---|---|---|---|
| `AgentState` | `deep_researcher` | TBD | TBD | TBD |
| `SupervisorState` | supervisor subgraph | TBD | TBD | TBD |
| `ResearcherState` / `ResearcherOutputState` | researcher subgraph | TBD | TBD | TBD |

## 2. Lifecycle

How each field is created, updated (reducer), passed between graphs and cleared. *TBD.*

## 3. Context and Memory Limits

Token budgets, trimming and compression rules. *TBD.*

## 4. Persistence

Checkpointers and anything stored beyond a single run. *TBD.*

## 5. Module Sections

Copy the example for your module. Before SA Review, check §5 of the other modules for conflicting field names, reducers or owners.

### delivery (REQ-002, REQ-004, ADR-001, ADR-002)

**Fields added or changed**

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `SupervisorState` | `task_results` | `Annotated[list[TaskResult], …]` | `operator.add` | co-owned, append-only: the delivery-owned fan-out region of `supervisor_tools` (one entry per call it ran) **and** orchestration's early-return branch (the `not_run` entries) | orchestration's coverage check (REQ-003); carried to `AgentState` when the subgraph ends | appended per turn → carried across the subgraph boundary |
| `AgentState` | `task_results` | same | `operator.add` | the subgraph output | `evaluate_before_report`, `evaluate_after_report`, `render_limitations`; orchestration's coverage check | first write when research ends → kept to the end of the run |
| `AgentState` | `failed_tasks` | `list[dict]` (each entry: `task_id`, `reason`, `category`, `message`) | `override_reducer` — each writer sends `{"type": "override", "value": [...]}`, the convention `notes` already uses | `finalize`, first pass only; derived from `task_results` | `evaluate_before_report`, `evaluate_after_report`, `render_limitations`; the caller | written once when research ends → kept to the end of the run; never written a second time |
| `AgentState` | `research_outcome` | `str` ∈ {`complete`, `partial`, `failed`} | last write wins (plain field, no reducer) | `finalize`, both passes | `finalize` (second pass); the caller | set by the first pass → overwritten by the second pass with the report-stage verdict |
| `AgentState` | `run_finalized` | `bool` | last write wins | `finalize` first pass only — through `evaluate_before_report`'s `update` when `enforce_delivery_outcome` is `True`, directly by the node when it is `False` | `finalize`, to tell its two passes apart | absent/`False` → set `True` by the first pass on both the report and the failed path, so the first pass cannot run twice |
| `AgentState` | `report_truncated` | `bool` | last write wins | `final_report_generation` | `evaluate_after_report`, `render_limitations` | default `False` → `True` when findings were cut to fit the report model; `False` again on a successful report |
| `AgentState` | `report_error` | `str` | last write wins | `final_report_generation` | `evaluate_after_report` | `""` on success → the error text when the report stage failed; this text never enters `final_report` |

`SupervisorState` gains only `task_results`, which carries the per-task results (the REQ-001 contract type) across the subgraph boundary; without it a LangGraph node's returned value would be dropped and `finalize` would see nothing.

- **Ownership:** `task_results` is **co-owned and append-only**: the delivery-owned fan-out region of `supervisor_tools` appends the results of the calls it runs, and orchestration's early-return branch appends the `not_run` results of a turn that exits before the fan-out. Two modules appending to one field is safe here because the field is `operator.add` over disjoint sets of calls — a call reaches exactly one of the two regions — but the integrator's "no state field written by two modules" check will flag it, so the split is recorded in ADR-001 §5. `finalize` is the only writer of `failed_tasks`, `research_outcome` and `run_finalized`; when `enforce_delivery_outcome` is `True`, `run_finalized` is written through `evaluate_before_report`'s `update`, and when it is `False` the `finalize` node writes it directly because `delivery/outcome.py` is not called. `final_report_generation` is the only writer of `report_truncated` and `report_error`.
- **Lifecycle:** `task_results` accumulates one entry per `ConductResearch` call during the research phase and survives the subgraph boundary unchanged, so `finalize` and orchestration's coverage check read the same evidence. `failed_tasks` is absent until the first `finalize` pass, which derives the whole list from `task_results` and writes it in one override — there is no append path, so the same failure cannot be recorded twice, which is why the field uses `override_reducer` rather than `operator.add`. `research_outcome` is absent until the first pass and finalised by the second. `run_finalized` separates the passes; `finalize` must not infer its pass from whether `final_report` is set, because a failed report leaves that field empty. `report_truncated` and `report_error` are written by the report node just before `finalize` reads them. None of these fields is cleared at the end of a run: they are part of the run output.

  ```text
  supervisor_tools --task_results (state)--> SupervisorState
          │ (subgraph return)
          ▼
  finalize (1st pass) --evaluate_before_report--> research_outcome, failed_tasks (override), run_finalized
          │ report_allowed → goto final_report_generation
          ▼
  final_report_generation --report_truncated, report_error--> finalize (2nd pass)
          │ --evaluate_after_report--> research_outcome (final) → goto END
          ▼
         END
  ```

- **Shared contract:** yes. `task_results` sits in both state types and is read by orchestration's coverage check, so it is co-owned with the REQ-001 / REQ-003 owner; the other five fields are new fields of `AgentState`, a type other modules also edit. Owners who must approve a change to them (`structural-constraints.md` §6): the orchestration owner (REQ-001, REQ-003), the integrator (blueprint §5 interface table), and the delivery owner. `DelegationOutcome` and `TaskRunRecord` are in-process values and are not checkpointed, so what was queued and when is visible only for the duration of the fan-out (RISK-005).

### <Module> (REQ-NNN, ADR-NNN)

**Fields added or changed**

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `SupervisorState` | `<field>` | `<type>` | override / append | `<component>` | `<components>` | `<when>` → `<when>` |

- **Ownership:** which component is the only writer of each field.
- **Lifecycle:** when the fields are created, updated and cleared within a run.
- **Shared contract:** whether other modules read these fields, and which owners must approve changes (`structural-constraints.md` §6).
