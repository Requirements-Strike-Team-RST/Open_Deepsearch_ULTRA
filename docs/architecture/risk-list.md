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
> **Purpose:** Risks and assumptions that an architectural decision depends on, and the conditions under which that decision must be re-evaluated.
> **Authoritative for:** module risks, the assumptions behind an accepted or proposed decision, and the re-evaluation triggers. A risk is not a defect: defects go to `docs/bug-diary.md`, debt to `docs/debt-register.md`, and open alternatives to `option-ledger.md`.
> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-13

## How to Add an Entry

1. Copy an entry, take the next free `RISK-NNN` number and keep the same fields. Never reuse a retired number.
2. Link the risk to the requirement or requirement ID it threatens and to the ADR and EVAL entry that carries the decision.
3. Every risk names a **trigger**: the observable event that means the risk has materialised or the assumption no longer holds. A risk without a trigger is a wish.
4. State the **mitigation** (what the design already does about it) separately from the **re-evaluation condition** (when the owner reopens the ADD round, `Prompt.md` §10).
5. At integration the integrator may renumber entries and updates every reference.

Severity: **High** = the requirement's fit criterion can fail without any other warning; **Medium** = quality degrades but a test catches it; **Low** = cost or maintenance only.

## Risk Register

| Risk ID | Module | Requirement / ADR | Risk or assumption | Severity | Trigger | Status |
|---|---|---|---|---|---|---|
| RISK-001 | context | REQ-005 / ADR-005 | Compression can be made to fit the token limit by trimming whole turns | Medium | C-004 fires while a partial turn would still have been removable | Active |
| RISK-002 | context | REQ-005 / ADR-005 | The protected region is identifiable from message types alone | High | A message is inserted before the topic, or native web-search results arrive without `tool_calls` | Active |
| RISK-003 | context | REQ-005 / ADR-005 | Token-limit errors are recognisable by provider pattern | Medium | A provider token-limit error is classified as a non-token error | Active |
| RISK-004 | context | REQ-005 / ADR-005 | A failed `token_limit` result is accepted by the supervisor | High | REQ-001's ADR is accepted with a category vocabulary that lacks `token_limit` | Active |
| RISK-005 | context | REQ-005 / ADR-005 | Trimming is bounded by the attempt budget | Medium | `TokenLimitExceeded` is raised although `plan_trim` would still return a `TrimPlan` | Active |
| RISK-006 | context | REQ-005 / ADR-005 | The new behaviour can be A/B-compared through the flag | High | The flag is flipped before `verified`, or stays `False` after the requirement closes | Active |
| RISK-007 | context | REQ-005 / ADR-005 | The consumer-side default can be fixed without touching REQ-002's exception handling | Medium | Review finds the L310 change also swallows a researcher exception, or REQ-002 changes L310 in the same cycle | Active |

## RISK-001 — The token limit may not be reachable by removing whole turns

- **Module:** context
- **Source:** REQ-005 C-001, C-004; ADR-005 §3(a), §3(d); EVAL-001 option B
- **Assumption:** if the history exceeds the compression model's token limit, removing one whole research turn per attempt, at most three attempts, frees enough context.
- **Why it may fail:** the preamble (the research topic, `deep_researcher.py` L297-300) and the compression instruction, plus the newest turn, may together exceed the limit on their own — a very long topic with a very long single answer, or a model whose limit is smaller than `compression_token_limit`. In that case `plan_trim` returns `None` on the first attempt and C-004 governs, which is correct but means the task produces no summary at all.
- **Severity:** Medium — the failure is explicit (`failed` / `token_limit`), never silent.
- **Mitigation:** the design fails closed rather than returning text (ADR-005 §3(d)); the node returns a typed result, so the loss is visible in the run outcome.
- **Re-evaluation condition:** a case appears where C-004 fires while the history still contains data that a *partial* turn could have saved, or a live run shows a topic that alone exceeds the limit. Then reopening the ADD round should evaluate partial-turn trimming (splitting the largest tool result) as a fourth candidate.

## RISK-002 — The protected region may not be derivable from message types

- **Module:** context
- **Source:** REQ-005 C-001, C-002; ADR-005 §3(b); INV-001
- **Assumption:** the preamble is position 0 (the topic `HumanMessage`), the instruction is the last `HumanMessage`, and every `ToolMessage` belongs to the `AIMessage` that precedes it. `segment_turns` groups by these positional rules.
- **Why it may fail:** a change upstream that inserts a message before the topic (for example a REQ-001 task specification as a second `SystemMessage`), or a native web-search call that yields tool results without `tool_calls` on the AI message (`openai_websearch_called`, `anthropic_websearch_called`), breaks the grouping. Then a turn boundary is misidentified and trimming could cut inside a turn.
- **Severity:** High if it happens silently — it would violate INV-001's "no orphan" clause without an error.
- **Mitigation:** the orphan rule keeps an `AIMessage`-less `ToolMessage` in the protected region instead of removing it (ADR-005 §3(a)); TC-003 covers an orphan `ToolMessage` whose `tool_call_id` matches no `AIMessage`; the orphan monitor is computed from the same helpers.
- **Re-evaluation condition:** REQ-001 lands a task specification in `researcher_messages`, or `utils.py` changes how native web-search results are appended. Either trigger reopens the ADD round for how the protected region is located (pass it explicitly from the node instead of inferring it).

## RISK-003 — Some providers may report token limits in ways pattern matching cannot see

- **Module:** context
- **Source:** REQ-005 C-003; ADR-005 §3(c); POL-001
- **Assumption:** `utils.is_token_limit_exceeded` recognises token-limit errors for every provider the project supports (`openai`, `anthropic`, `gemini`/`google`, and Bedrock-routed models) once it is given the model that actually made the call (`compression_model`).
- **Why it may fail:** the checkers match exception class names and message keywords (`utils.py` L703-785). A provider that returns a 413, a GraphQL-truncation detail, or a local Ollama server message is not matched, so `classify_token_limit` returns `False` and POL-003 treats the error as a transient non-token error: the request is retried unchanged against its own budget until exhausted, then the task fails with category `provider_transient`, without ever trimming. The recovery that REQ-005 promises therefore does not happen for that provider. The classifier deliberately does not fall back to other providers' patterns, because that fallback would let `_check_openai_token_limit`'s unguarded `invalid_request_error` branch misclassify other providers (ADR-005 §3(c)).
- **Severity:** Medium — recovery is lost, but the failure is visible and is not a silent data loss.
- **Mitigation:** passing `compression_model` covers the reported C-003 case (an Anthropic compression model beside an OpenAI research model), because the prefix then selects the correct checker; no silent conversion to a summary occurs on the new path.
- **Re-evaluation condition:** any live run or user report shows a provider token-limit error classified as a non-token error. Then classification should move from message patterns to a provider-declared error code, which is a widening of REQ-005's scope and needs a requirement change.

## RISK-004 — REQ-001's task-result type may not accept a `token_limit` category

- **Module:** context
- **Source:** REQ-005 C-004; ADR-005 §5; `structural-constraints.md` §6
- **Assumption:** the REQ-001 task result has a status, a category and a reason, and the category enumeration includes `token_limit` (or can be extended by its owner).
- **Why it may fail:** REQ-005 `depends_on` REQ-001, and REQ-001 is owned by another member and is still in design. If REQ-001 lands a closed enumeration without `token_limit`, or with a different failure vocabulary, the node cannot record the mandated outcome and C-004 cannot be met as written.
- **Severity:** High — C-004 is a must-have criterion of a safety-relevant requirement.
- **Mitigation:** ADR-005 deliberately defines no second result type and records the shared-contract approval as a Gate 1 condition; the node's behaviour is isolated in one place so the mapping can change without touching `plan_trim`.
- **Re-evaluation condition:** REQ-001's ADR is accepted. The context owner must then confirm the category name and the field layout, and update ADR-005 §5 and TC-006 if they differ. If they cannot be reconciled, escalate to SA Review rather than inventing a parallel type.

## RISK-005 — Resolved: the trimming budget covers every removable turn

- **Module:** context
- **Source:** REQ-005 C-004; POL-001, POL-002; ADR-005 §9 step 5
- **Original concern:** removing one turn per attempt with a fixed budget of three retries could only ever remove two turns, so the loop would return `failed` / `token_limit` although a reducible history remained — an avoidable failure that still looked correct to C-004.
- **Resolution:** trimming now has its own budget, `max_trim_attempts`, derived from the history: the loop continues until the removable turns are exhausted, so `TokenLimitExceeded` is raised only when `plan_trim` returns `None`, exactly as C-004 requires.
- **A regression found during review of this fix:** the first version shared a single budget between trimming and transient-error retries. On a one-turn history that evaluated to `1`, so a 429 was not retried at all, fewer than the baseline's three; and a couple of transient errors could consume the allowance trimming needed. The budgets are now **separate**: `max_trim_attempts` (derived) and `max_transient_attempts` (default 3, matching the baseline). `TC-008` covers the one-turn case explicitly.
- **Residual risk:** each trimming attempt costs a provider round-trip, so a very long history may take many calls. This is accepted: correctness under C-004 takes precedence over call count, and the cost is bounded by the number of turns.
- **Re-evaluation condition:** a live run shows the trimming loop dominating the research time. Then make removal geometric (halve the removable turns per attempt), which is an ADR amendment of a still-*Proposed* ADR, not a new ADR.

## RISK-006 — The behaviour flag may hide the improvement

- **Module:** context
- **Source:** REQ-005; `structural-constraints.md` §8; ADR-005 §3 "Behaviour switch", §9 step 12
- **Assumption:** `context_trimming = False` by default keeps baseline behaviour comparable, and the flipping PR arrives once REQ-005 is `verified`.
- **Why it may fail:** if the flip is forgotten, the requirement is `verified` while production runs the defective path — the worst combination, since the evidence would describe code that never executes. Conversely, flipping early makes the A/B comparison meaningless.
- **Severity:** High — the shipped behaviour would contradict the requirement's `verified` status.
- **Mitigation:** TC-009 pins the default; the flip is a separate, explicitly numbered step (ADR-005 §9 step 12) with its own review; Definition of Done item 10 keeps the status at `verified` only after the flip.
- **Re-evaluation condition:** any PR that changes the default without REQ-005 being `verified`, or any release that contains the flag still `False` after the requirement closed. The second case is a defect for `docs/bug-diary.md`, not a new risk.

## RISK-007 — The consumer guard is new code on a shared path

- **Module:** context
- **Source:** REQ-005 C-004; ADR-005 §2 defect 4, §3(d), step 10
- **Assumption:** adding one guard to `supervisor_tools` (L308-313) that reads `research_outcome` is safe because the field is `None` whenever `context_trimming = False`, so the `else` branch is the baseline line unchanged and baseline behaviour is preserved.
- **Why it may fail:** L310 sits in the same `try/except` block as the researcher failure branch (L332-342), which contains `or True`. If the guard is written too broadly — for example by inspecting `compressed_research` text instead of the structured field, or by changing what happens when the key is absent — it can alter the baseline path that the flag exists to preserve. REQ-002 or REQ-004 may also edit the same lines in the same integration cycle, producing a merge conflict or two competing policies for one message.
- **Severity:** Medium — a scope overlap on a shared line, not a data-loss path; the extra branch is unreachable while the flag is off.
- **Mitigation:** the guard's condition is `research_outcome is not None and outcome.status == "failed"`; the `else` branch is the baseline expression verbatim; TC-011 asserts both branches (failure present, and `None`); ADR-005 step 10 fixes the exact code shape and requires a grep proving this guard is the field's only reader.
- **Re-evaluation condition:** review rejects the guard as out of scope, or REQ-002's ADR assigns a different behaviour to a researcher result carrying a failed outcome. Then withdraw step 10 and reopen the transport question, recording that the failure cannot leave the subgraph without a consumer-side change.

## Retired or Accepted Risks

| Risk ID | Outcome | Reference |
|---|---|---|
| — | none yet | — |
