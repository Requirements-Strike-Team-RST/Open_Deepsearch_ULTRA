# Evaluation Table

> **Purpose:** ADD results: for each architectural question, 2–3 candidate solutions compared on pros, cons, complexity and testability, and the choice made.
> **Authoritative for:** option comparisons. The decision itself is recorded in the ADR named in the entry.
> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-12

## How to Add an Entry

1. Copy the example below, take the next free `EVAL-NNN` number and keep the same fields.
2. **ASR:** list the requirements and the acceptance criteria (C-/M- IDs from `docs/req/requirements.yaml`) that shape the decision.
3. **Candidates:** describe 2–3 options; rate complexity and offline testability as Low, Medium or High.
4. **Choice:** name the chosen option and why it wins, say why each other option was rejected, then write the ADR.

## EVAL-NNN: <Question being decided>

- **Module:** <module from `architecture-blueprint.md` §4>
- **Owner:** <name>
- **Decision recorded in:** ADR-NNN
- **Status:** Open | Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-NNN | C-NNN, M-NNN | e.g. correctness, testability, cost |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | | | | | Low / Medium / High | Low / Medium / High |
| B | | | | | | |
| C (optional) | | | | | | |

**Choice:** <option> — <why it wins>.

**Rejected and why:** <option>: <reason>.

## EVAL-001: How delegated research tasks are executed so that one failure neither ends the phase nor loses a sibling

- **Module:** delivery
- **Owner:** AlchemyHAN
- **Decision recorded in:** ADR-001
- **Status:** Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-002 | C-001, C-002, C-003, C-004, C-005, C-006, C-007; M-001, M-002 | Correctness of failure isolation; testability without a network or a model; preserving completed work (cost already spent); observability of what was run |

The task contract itself — `TaskSpec`, `TaskResult`, the error categories and `derive_task_status` — belongs to the orchestration module (REQ-001, ADR-00X, owner centay). This entry assumes that contract and decides only how the delivery module consumes it.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Patch `supervisor_tools` in place: `asyncio.gather(..., return_exceptions=True)`, classify each outcome inline, replace the overflow slice `[:max]` with a loop that runs the remaining calls after the first batch, and filter `get_notes_from_tool_calls` | `deep_researcher.py` (`supervisor_tools`), `utils.py` | Smallest diff; no new package; no new state field | Four unrelated concerns (fan-out, queuing, classification, note filtering) stay inside one ~150-line node; the exception branch cannot be exercised without driving the whole node; the join guarantee from C-006 has nowhere to live; no place to record per-task outcomes | Medium | Low: only end-to-end node tests |
| B | New `delivery/execution.py`: `run_delegations(calls, config)` builds one `TaskRunRecord` per call, runs them in batches of `max_concurrent_research_units`, collects every outcome with `asyncio.gather(return_exceptions=True)`, classifies exceptions into `token_limit` / `runtime`, produces a `TaskResult` for every call including those left unrun, and returns `DelegationOutcome(records, results, notes, failures)`; `supervisor_tools` becomes a thin caller | New `delivery/execution.py`; `deep_researcher.py` (`supervisor_tools`); `state.py` (`failed_tasks`) | Each concern has one function that can be unit-tested with a fake researcher; queuing, classification and join are testable in isolation; per-call records make `dropped_delegation_count` measurable; matches the "one element, one module" rule and the thin-node rule | New subpackage must be added to `packages` in `pyproject.toml`; `supervisor_tools` keeps a small amount of glue; needs a new state field | Medium | High: fake researchers, no model or network |
| C | `asyncio.TaskGroup` (or `anyio` task groups) for structured concurrency: cancel the group when one researcher raises | `deep_researcher.py` (`supervisor_tools`) | Python-native; guarantees no task outlives the block | A task group cancels its siblings when one child fails, so a successful sibling's findings are discarded — directly contradicts C-002 and M-001; cancellation also spends tokens on work whose result is thrown away | Low | Medium: cancellation timing is hard to assert deterministically |

**Choice:** B — it is the only candidate whose units line up one-to-one with the acceptance criteria: queuing is C-004, classification is C-001/C-003, join is C-006, note separation is C-007, each with an interface that a fake researcher can drive offline.

**Rejected and why:** A — the acceptance criteria C-004, C-006 and C-007 would all land in one node body, so each test would re-simulate the whole supervisor turn and a regression in one concern would be hard to localise; it also leaves no record from which `dropped_delegation_count` can be computed. C — structured concurrency cancels successful siblings, which is exactly the loss REQ-002 forbids; it is the right tool for "all or nothing" work, not for "keep every completed task".

## EVAL-002: Where the research outcome is computed and how it reaches the run output

- **Module:** delivery
- **Owner:** AlchemyHAN
- **Decision recorded in:** ADR-001
- **Status:** Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-004 | C-001, C-002, C-003, C-004, C-005, C-006; M-001 | Caller-visible correctness of `complete` / `partial` / `failed`; the report model must not be able to make a failed run look complete; testability of both the pre-report and post-report decision |
| REQ-002 | C-005, C-007 | The failed-task list must survive into the output, which needs structured records, not note text |

The outcome depends on information from two different moments: the research exit reason and task results (available before report generation) and report-generation success or truncation (known only after it). The decision has to see both.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Compute the outcome inside `final_report_generation`, reading only `notes` and the retry state | `deep_researcher.py` (`final_report_generation`) | No topology change; one file | `notes` is a list of free-text strings, so the task id, status and reason of a failed task are already lost — the failed-task list of C-002 cannot be produced; C-004 ("the report model is not called") cannot be honoured because the node has already started | Low | Medium |
| B | New `delivery/outcome.py`, called from a new `finalize` node: `research_supervisor → finalize → final_report_generation → finalize → END`. The first pass computes the pre-report outcome from the exit reason and task results and decides whether the report model may run at all; the second pass folds in report success or truncation, appends the system-written limitations section and writes `research_outcome` and `failed_tasks` | `delivery/outcome.py`; `deep_researcher.py` (one new node and three edges); `state.py` (`research_outcome`, `failed_tasks`) | The decision sees structured task records, so the failed-task list is exact; the "no report model on a failed run" rule (C-004) is enforced before the model is called; both passes are pure functions of state, so they are testable with no graph and no model; the three baseline graph nodes keep their bodies | Adds one node and three edges to a topology that the baseline rules keep fixed, so it needs this ADR and SA Review; the node runs twice, which readers may find surprising | Medium | High: both passes are pure functions over a state dict |
| C | Keep two nodes and route with a conditional edge: `conditional_edge(research_supervisor)` sends failed runs to a separate `emit_outcome` node and everything else to `final_report_generation` → `emit_outcome` | `deep_researcher.py` (two new nodes, a conditional edge, a new edge) | Failed runs have an obvious dedicated path; no node runs twice | Two nodes must both assemble the outcome and the limitations text, so the same logic is duplicated; the conditional must reach the same verdict as the later node, giving two places where `complete` can be decided; more edges to keep consistent | Medium | Medium |

**Choice:** B — the outcome is computed by pure functions that take structured state, and the same function is used before and after report generation, so there is exactly one place that can produce `complete`. Enforcing "no report model when nothing was found" before the model call is what makes C-004 deterministic rather than a post-hoc check.

**Rejected and why:** A — free-text notes cannot carry per-task status, so the failed-task list and C-004 are unimplementable; it also leaves the report model as the only thing standing between a failed run and a normal-looking report, which is the harm REQ-004 exists to remove. C — duplicating the outcome assembly in two nodes creates two sources of truth for the same decision and more edges than B, for no gain in testability.

**Cross-module note:** both entries consume the REQ-001 task contract owned by orchestration (centay) and the REQ-003 exit reason owned by orchestration. The interface between the two modules is recorded in ADR-001 §5 and in `structural-constraints.md` §10 as a shared contract that the orchestration owner must approve.
