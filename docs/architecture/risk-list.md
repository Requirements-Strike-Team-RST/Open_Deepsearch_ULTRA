# Risk List

> **Purpose:** The risks, assumptions and preconditions behind the architectural decisions, and what would make the team re-evaluate them.
> **Authoritative for:** risk tracking per module. The decisions themselves are in `docs/architecture/adr/`; the option comparisons are in `evaluation-table.md`.
> **Maintained by:** each module owner adds the risks of their module; reviewed at every SA Review.
> **Status:** All entries are *Open* until SA Review; a risk closed by evidence is marked *Closed* with the evidence.
> **Last updated:** 2026-11-15

Every entry uses the same fields:

- **Risk** — what could go wrong.
- **Module / Source** — the module and the requirement or invariant it threatens.
- **Likelihood / Impact** — High, Medium or Low.
- **Assumption** — what has to hold for the current design to be acceptable.
- **Mitigation** — what reduces it, or why it is accepted.
- **Re-evaluate when** — the observation that invalidates the assumption.

## RISK-001 — A report can still be incomplete without the run being marked partial

- **Risk:** The outcome is `complete` although the report model paraphrased away or silently omitted a finding it was given. Because the delivery module does not parse the report body, nothing detects the omission.
- **Module / Source:** delivery; REQ-004 ("no finding was left out of the report"), ADR-002 §3.6.
- **Likelihood:** Medium. Report models are known to drop findings under a long `findings` block, and the baseline prompt asks for a *comprehensive* report without a completeness check.
- **Impact:** High. This is the exact harm upstream #283 describes: a normal-looking report that hides missing research.
- **Assumption:** Deterministic checking of the report body belongs to a later requirement (REQ-006 lists deterministic citation validation as out of scope), so this delivery only detects findings the system itself withheld — those dropped by report-stage truncation.
- **Mitigation:** `final_report_generation_prompt` already instructs the model to include all findings; the truncation path, which is the mechanical cause of loss, is detected and reported. `INV-004` (deferred) is the registered home for the stronger property.
- **Re-evaluate when:** a live run produces a report that omits a finding while the outcome is `complete`, or when REQ-006's scope is extended to deterministic citation and coverage checks.

## RISK-002 — The task contract from REQ-001 changes shape under this module

- **Risk:** The delivery module consumes `TaskSpec`, `TaskResult`, `TaskFailure`, `derive_task_status` and the error categories from the orchestration module (REQ-001, ADR-00X). If that ADR renames or reshapes a field after this one is implemented, `run_delegations` and `outcome.py` break, and the two ADRs may also disagree on which component derives the task status.
- **Module / Source:** delivery + orchestration; REQ-002 and REQ-004 both `depends_on` REQ-001.
- **Likelihood:** Medium. The field names in `requirements.yaml` are explicitly "proposals for the design review", so the orchestration ADR may still change them.
- **Impact:** Medium. The delivery tests would need rewriting, and a merged implementation would stop importing.
- **Assumption:** The orchestration owner's contract is stable by integration, and `derive_task_status` stays the single place that decides `complete` / `partial` / `failed` for one task; delivery never re-derives it. Merging the two module branches therefore needs one owner's approval of the other's interface.
- **Mitigation:** ADR-001 §5 places the task contract in the shared `state.py` and states that an existing orchestration definition is adopted verbatim; `structural-constraints.md` §10 records it as a shared contract; and neither ADR defines a competing type. The integration step (Prompt.md §4.2) checks for overlapping responsibilities and two owners writing the same state field.
- **Re-evaluate when:** the orchestration ADR changes a field name or moves status derivation, or the integrator finds both modules deriving a task status.

## RISK-003 — The new `finalize` node behaves differently across LangGraph versions

- **Risk:** `finalize` returns a `Command` with `goto`, and it runs twice in one run. Behaviour depends on how the installed LangGraph version handles a node that is both the source and the target of a conditional edge, and on how a subgraph's state update merges into the parent `AgentState` with `operator.add` reducers. A version bump could change routing or duplicate the `failed_tasks` entries.
- **Module / Source:** delivery; REQ-004 C-001–C-006, ADR-002 §3.1–§3.4.
- **Likelihood:** Medium. `pyproject.toml` pins `langgraph>=0.5.4`, a lower bound, so the resolved version can move.
- **Impact:** High if it recurses: a `finalize` that routes back to itself without a state change is an infinite loop rather than a wrong answer.
- **Assumption:** LangGraph keeps `Command(goto=...)` semantics and applies the `operator.add` reducer once per node return in an equal-or-newer version.
- **Mitigation:** `finalize` decides which pass it is in from state (`research_outcome` and `final_report`), not from a counter, so a second entry without the first pass's write is impossible to confuse; TC-004-01 to TC-004-06 each run the two passes; the offline suites pin the behaviour on the resolved version. If the loop becomes a problem, the fallback is EVAL-002 option A (no topology change, coarser outcome).
- **Re-evaluate when:** a `langgraph` upgrade changes `Command` routing or reducer application, or a run shows `finalize` executing more than twice.

## RISK-004 — Queued delegations raise token cost and turn latency

- **Risk:** The baseline rejected overflow delegations for free. Queuing them runs every task, so a turn with many delegations costs more tokens and takes longer than before, and a burst of queued work can hit provider rate limits even at the same peak concurrency.
- **Module / Source:** delivery; REQ-002 C-004, POL-003, ADR-001 §8.
- **Likelihood:** High. The baseline team trace already showed about 34,000 tokens for a three-sentence question (`requirements.yaml` REQ-001 notes).
- **Impact:** Low to Medium. It is the intended trade — the work is no longer silently lost — but it can surface as a cost or rate-limit complaint.
- **Assumption:** `max_concurrent_research_units` stays the binding limit on peak concurrency, and a queued task is worth its tokens because its result is kept rather than discarded.
- **Mitigation:** the semaphore keeps peak concurrency at the configured value while every slot stays busy; `REQ-001`'s per-task budget is where over-delegation will be limited later; `Configuration` remains the operator's lever.
- **Re-evaluate when:** a live run shows queued tasks dominating cost, or providers start rejecting work that the baseline would have avoided by rejecting it first.

## RISK-005 — `TaskRunRecord` is not visible after the fan-out

- **Risk:** The records of what was queued, when, and how many attempts each task made live only for the duration of `run_delegations`. They are not stored in state, so a checkpoint replay or a post-mortem cannot show the schedule, and `dropped_delegation_count` is computable only from the fan-out's own records, not from a stored run.
- **Module / Source:** delivery; REQ-002 M-001, `memory-design.md` §5 (delivery).
- **Likelihood:** High — this is the design as written. The per-task `TaskResult`s do reach state through `task_results`, but the scheduling records do not.
- **Impact:** Low. The invariant is enforced and tested; only the retrospective evidence is thinner.
- **Assumption:** Storing per-task scheduling records in the checkpoint is not worth the state growth for this delivery, because the outcomes (one `TaskResult` per task, in `task_results`) are already persisted.
- **Mitigation:** the outcome and the failed-task list are persisted; the drop metric is asserted offline. If operational visibility is needed, add a `delivery_records` list to state in a later ADR.
- **Re-evaluate when:** someone needs to explain a past run's scheduling from its checkpoint, or M-001 has to be measured on production runs.

## Adding an Entry

Copy an entry style, take the next free `RISK-NNN` number, and fill every field. Add the risk to the module section of the ADR that introduced it. Never reuse a number; a closed risk keeps its number and states the evidence.
