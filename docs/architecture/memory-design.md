# Memory and State Design

> **Purpose:** How the research agent stores, passes and discards state and memory: state structure, ownership and lifecycle.
> **Authoritative for:** state and memory design. Graph state types live in `src/open_deep_research/state.py`.
> **Maintained by:** owners of modules that add or change state write a module section (§5); §1–§4 are integrated from those sections before SA Review. Modules that do not touch state add nothing.
> **Last updated:** 2026-11-12

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

### <Module> (REQ-NNN, ADR-NNN)

**Fields added or changed**

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `SupervisorState` | `<field>` | `<type>` | override / append | `<component>` | `<components>` | `<when>` → `<when>` |

- **Ownership:** which component is the only writer of each field.
- **Lifecycle:** when the fields are created, updated and cleared within a run.
- **Shared contract:** whether other modules read these fields, and which owners must approve changes (`structural-constraints.md` §6).

### delivery (REQ-002, REQ-004, ADR-001)

**Fields added or changed**

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `SupervisorState` | `failed_tasks` | `list[dict]` (each entry: `task_id`, `reason`, `category`, `message`) | `operator.add` | `supervisor_tools` in `deep_researcher.py`, from `DelegationOutcome.failures` | the exit branch of `supervisor_tools`; `evaluate_before_report` after the subgraph returns | first fan-out with a failure → carried into `AgentState` when the subgraph ends; never cleared inside the subgraph |
| `AgentState` | `failed_tasks` | `list[dict]` (same entry shape) | `operator.add` | the `research_supervisor` subgraph's return value, then `finalize` after the report stage | `evaluate_before_report`, `evaluate_after_report`, `render_limitations` | first write when the research phase ends → kept to the end of the run so the caller sees it |
| `AgentState` | `research_outcome` | `str` ∈ {`complete`, `partial`, `failed`} | last write wins (plain field, no reducer) | `finalize` in `deep_researcher.py` (both passes) | `finalize` (second pass); any caller reading the run output | set by the first `finalize` pass; overwritten by the second pass with the report-stage verdict |

- **Ownership:** `finalize` is the only writer of `research_outcome`. `supervisor_tools` (through `run_delegations`) is the only writer of `SupervisorState.failed_tasks`; the subgraph hands it to `AgentState.failed_tasks` unchanged, and nothing appends to `AgentState.failed_tasks` outside the subgraph return.
- **Lifecycle:** `failed_tasks` starts absent (empty by reducer). It is appended once per failed or unrun delegation during the research phase, survives the subgraph boundary, and is read twice by the outcome functions — before report generation to decide `report_allowed`, and after it to render the limitations section. `research_outcome` is absent until the first `finalize` pass, so `finalize` tells its two passes apart by which of `research_outcome` and `final_report` are set. Neither field is cleared at the end of a run: they are part of the run output.

  ```text
  supervisor_tools --failed_tasks--> SupervisorState
          │ (subgraph return)
          ▼
  AgentState.failed_tasks --evaluate_before_report--> OutcomeDecision --finalize--> research_outcome
          │
  final_report_generation --report, truncated--> evaluate_after_report --finalize--> research_outcome (final), final_report
  ```

- **Shared contract:** yes. `AgentState.failed_tasks` and `AgentState.research_outcome` are new fields of a type other modules also edit, and `SupervisorState.failed_tasks` sits beside the orchestration fields of the same state. Owners who must approve a change to them (`structural-constraints.md` §6): the orchestration owner (reads the subgraph state and writes the exit reason for REQ-003), the integrator (blueprint §5 interface table), and the delivery owner. `DelegationOutcome` is an in-process value and is not stored in state, so what was queued and when is visible only for the duration of the fan-out and not to a checkpoint replay.
