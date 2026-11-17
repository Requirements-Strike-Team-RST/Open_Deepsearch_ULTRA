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

### Orchestration (REQ-001, REQ-003, ADR-002)

**Status: Proposed.** The field contract and helper signatures are defined in ADR-002 §5; this section defines their ownership and lifecycle. All shared types, including serializable receipt/evidence snapshot types, are defined once in `state.py`. `orchestration/contracts.py`, `budget.py`, `evidence.py` and `termination.py` import those types; neither `state.py` nor `configuration.py` imports an extension module. Adding the fields below changes the existing state classes; the original baseline `ConductResearch` class remains unchanged. The 11/15 internal split changes no DTO, helper argument or context return type.
### context (REQ-005, ADR-005)

**Fields added or changed**

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `ResearcherState` | `task_spec` | `TaskSpec \| None`, absent/`None` by default | last write | Researcher-subgraph entry boundary in `supervisor_tools`, using the registered spec | Researcher budget/evidence wrapper; compression result mapping | Accepted delegation, before researcher invocation → researcher invocation ends |
| `ResearcherState`, `ResearcherOutputState` | `task_result` | `TaskResult \| None`, absent/`None` by default | last write | `compress_research` node's single result-mapping boundary | Delivery's output validator; researcher-subgraph caller | Successful compression or a mapped compression failure → returned with researcher output, then copied into the run ledger |
| `ResearcherState` only | `task_evidence_snapshot` | Serializable evidence snapshot, initially zero spend and no retrieved URLs | last write of the complete snapshot | Researcher node adapter after its evidence wrapper records an event | Compression assembly and validation; diagnostics | Before the first researcher call → researcher invocation ends; never exported as a separate main-state field |
| `SupervisorState`, `AgentState` | `task_results` | `list[TaskResult]`, default `[]` | `override_reducer`: plain list appends; explicit override envelope replaces | `supervisor_tools` node's single orchestration update boundary; terminal supervisor error uses the same finalizer | Coverage selector; final `RunRecord` reader; delivery/evaluation readers | Cleared for a new enabled run → append one result per accepted delegation → final complete-ledger override; retained until the next run reset |
| `SupervisorState`, `AgentState` | `exit_reason` | `ExitReason \| None`, default `None` | last write | Common run finalizer called by the supervisor node boundary or tool-turn boundary | `RunRecord.from_state`; delivery/evaluation readers | New-run reset → exactly one selected final reason → next-run reset |
| `SupervisorState`, `AgentState` | `exit_detail` | `str \| None`, default `None` | last write | Same common run finalizer | Same readers | New-run reset → final explanation, required for non-`covered` → next-run reset |
| `SupervisorState`, `AgentState` | `run_coverage` | `float \| None`, default `None` | last write | Same common run finalizer, from exact question counts | Same readers | New-run reset → final computed value → next-run reset |
| `SupervisorState`, `AgentState` | `coverage_threshold` | `float \| None`, default `None` | last write | Same common run finalizer, recording the configured value used for the run | Same readers | New-run reset → final finite value in `(0, 1]` → next-run reset |
| `SupervisorState` only | `completed_supervisor_turns` | `int`, default `0` | last write | Orchestration tool-turn adapter at the end of one successfully processed turn | Entry cap guard and common exit selector | First enabled supervisor entry → increment after processing/join, including think-only/completion-only/no-tool turns → next-run reset |
| `SupervisorState` only | `unchanged_eligible_turns` | `int`, default `0` | last write | Same end-of-turn adapter | Common exit selector | First enabled supervisor entry → increment/reset by exact before/after coverage; think-only leaves it untouched → next-run reset |
| `SupervisorState` only | `delegation_receipts` | Ordered `dict[str, SerializableReceipt]`, default `{}`; key is the run's `tool_call_id` | last write of the complete receipt map | Orchestration registration/result-acceptance boundary within `supervisor_tools` | Delivery dispatch adapter; pending-delegation handling; coverage/finalization validation | First intent in a normally accepted control response → rejected diagnostic or accepted spec → terminal result reference → next-run reset |
| Existing `SupervisorState`, `AgentState` field | `notes` | Existing `list[str]` | Existing `override_reducer`; enabled finalization uses an explicit override | Common run finalizer; existing report-generation cleanup remains its later lifecycle event | `final_report_generation` | New-run reset → validated findings rendered in task order at exit → existing report-generation cleanup |

**Ownership and run lifecycle**

- At a new enabled main-graph research run, the brief-to-supervisor boundary clears the previous public run snapshot and notes with explicit overrides where required. Keep `supervisor_builder.compile()` in its existing default per-invocation mode: private channels start fresh for a new call, with explicit zero/empty defaults; a resume restores that same invocation's private checkpoint. Do not try to reset supervisor-private keys through `AgentState`, change to per-thread `checkpointer=True`, or infer freshness from `exit_reason is None`. The [LangGraph subgraph guide](https://docs.langchain.com/oss/python/langgraph/use-subgraphs#per-invocation-default) documents this distinction; ORC-039 must verify it against the locked project version before runtime success is claimed. Cross-mode checkpoint reuse needs a reviewed reset/migration policy; flag comparison fixtures start from fresh state.
- After ADR-002 §3.5 accepts the control response as normal, every observed delegation intent is registered in original tool-call order before dispatch or final coverage selection. A valid spec receives the next run-local task ID. Invalid intent, including no valid topic/question or more than five distinct valid questions, produces a rejected diagnostic receipt, without inventing a spec or a coverage question. The definition of an accepted delegation and this diagnostic representation require shared-reader Review.
- A receipt records the original call identity, accepted serialized spec/task ID or rejection diagnostic, and its eventual terminal result reference, plus feedback_for_response_ids for code-owned supervisor response IDs. Receipt mark and feedback are published atomically; terminal supervisor entry also flushes a genuinely pending rejection diagnostic without a model request, but never adds a new task/question. Re-observing the same unchanged receipt does not create another task or append another result. A reused ID with different intent is a conflict diagnostic, not a second silently accepted task. An already terminal receipt is not converted to `not_run` on a cap resume.
- The proposed RegisteredDelegation/JoinedTurn port in ADR-002 §5 is runtime-only, not an extra graph channel: node retains each evidence holder, delivery receives contract callables and returns accepted-task results/messages in original call order after all started children join. Rejections/control feedback are separate node-owned messages merged in original tool-call order. Delivery produces dispatch inputs and one ordered result delta; it does not directly mutate graph state or choose an exit. The node's orchestration boundary validates that delta, updates receipts, and emits each new terminal result once. These are event responsibilities at one integration point, not two modules writing the same field.
- While the supervisor runs, its ledger may be nonempty with `exit_reason is None`. This is a valid **running** state. `RunRecord.from_state()` is exclusively a reader of the final main snapshot and rejects an incomplete final snapshot; it is not called on the running supervisor ledger. The final record already carries each task's must_answer and findings.answers. RunRecord.unanswered_questions computes the globally unresolved original questions from those values, using the same pure shared question identity calculation as coverage; no new stored unanswered-list field or reason-string parsing is introduced. The five final run fields are published together through one finalization update inside the supervisor subgraph. Its override envelopes are consumed there; the compiled child returns plain final lists, which the unchanged parent node appends once to channels cleared by the brief boundary. ORC-040 must exercise this actual two-level reducer behavior, not assume an envelope crosses graphs. Private counters, receipts and evidence snapshots are not main output fields.
- Per-turn `update_payload["task_results"]` is a plain delta: the reducer appends it. The coverage calculation may temporarily inspect `old_results + delta`, but must not return that full list as a plain update. At finalization, both `task_results` and `notes` use `{"type": "override", "value": ...}`. Notes contain only complete/partial tasks' rendered validated claims and their validated source references, never the untrusted complete summary, JSON sidecar, error, placeholder or reflection.

**Execution evidence and context**

- Each accepted task gets one live `TaskExecutionEvidence` holder. The dispatch wrapper makes a separate copy of `RunnableConfig` and of its `configurable` mapping, then injects the holder under the runtime-private key `_orchestration_evidence`. Parallel tasks never share this holder. It is passed only to the orchestration execution adapters; strip that private key before constructing model configuration, prompt content or exported diagnostics. Also isolate ambient inherited RunnableConfig: build a safe config, use set_config_context, and execute/await the entire model coroutine in its returned clean context via asyncio.create_task(context=...), as specified in ADR-002 §3.2. Merely omitting the key from .with_config is insufficient. Do not put the live holder, locks, permits, callbacks, model clients or awaitables in graph state; state contains serializable snapshots only.
- Budget admission and evidence mutation share that one holder and its synchronization; no second spend counter, BudgetState channel or runtime key is introduced. A released reservation with no actual start costs zero; a started failure is never refunded. Read-only contract validation cannot reserve or spend again.
- Private completion observations use operation ID, phase and logical-attempt ordinal, plus a bounded safe finish marker, normal/truncated/unknown classification and available usage. The node-owned model wrapper records each return/exception once before string conversion; context receives the same Runnable interface and returns the same CompressionOutcome. Pair the string with that operation's final returned observation; missing/stale/mismatched records are unknown, never borrowed from a sibling, prior phase or prior run. Keep only serializable observations in task_evidence_snapshot. Supervisor has no accepted TaskSpec: retain its observation in existing node-private diagnostic state, not a fake task or child cost. Live closures/holders remain outside clean model config and main outputs.

- The wrapper owns the live holder for the entire invocation, including exceptional returns. Before starting local awaitables, it reserves ordered permits within the remaining actual-call budget; it records each started executable invocation, including `think_tool` and failures. Rejected calls and the non-executed `ResearchComplete` control signal spend zero. Factories `build_task_result`, `validate_task_result` and `failed_result` receive the holder through the required keyword-only `evidence` argument, so a model cannot submit authoritative cost or retrieved URLs. TaskCost.usage_complete defaults False and distinguishes partial reported token totals from complete observations; actual tool-call count remains exact for retained process-local receipts. `not_run_result(spec)` uses zero-spend evidence by construction.
- Spec, remaining budget, receipts and trusted retrieved URLs survive message trimming. The node captures its spec/evidence references before entering a clean recovery coroutine; the context helper itself needs no live-evidence parameter. After the first returned string, require its matching normal completion observation and parse once; length/unknown uses zero parses and no extra request. Failed attempts or rejected responses never start a nested repair loop. Before every compression attempt, assembly restores the immutable spec/authority and the sidecar rules outside expendable history. A serializable evidence snapshot supports inspection/checkpoint validation, but does not turn a live external tool's side effects into a transaction.
- Checkpoint or trace adapters must exclude the runtime-private holder itself. Receipt deduplication protects local registration/result publication, not cross-process exactly-once tool execution: a crash after an external call but before a terminal receipt is durable leaves a replay window. Safe recovery of an unfinished receipt requires an explicit policy; no automatic side-effect replay guarantee is made here.
- Existing model `*_max_tokens` fields are output limits and `max_content_length` is a character limit. This design supplies no measured input/context-window token cap. Reactive compression token-limit handling, at most three attempts, remains the current trigger; proactive course input-budget compliance is a documented integration gap, not an implemented threshold.

**Feature flags and shared-reader Review**

| `orchestration_enabled` | `context_trimming` | Proposed lifecycle |
|---|---|---|
| `False` | `False` | Exact baseline path; no new orchestration fields, injected holder or altered tool binding. |
| `True` | `False` | Task contract/evidence and typed result mapping apply; retain the baseline compression retry/trimming path rather than taking over context policy. Only a successful string with matching normal observation is parsed; length/unknown and exceptions are mapped using retained evidence. |
| `True` | `True` | Context exclusively owns the single recovery loop, at most three attempts; it returns its existing string outcome. The matching normal observation is required before parsing; length/unknown has zero parses. Orchestration discards its free-text body from reader-facing summary/compressed_research and renders validated complete/partial findings and maps `TokenLimitExceeded` through `failed_result(..., evidence=...)`; no nested retry loop. |
| `False` | `True` | Context's exception can exist without a TaskSpec. Its propagation/delivery behavior is **pending context/delivery Review**; do not manufacture orchestration fields or claim this combination is the baseline. Orchestration run fields stay absent and a final RunRecord reader returns None. |

- **Shared contract:** delivery/Alchemy reads or creates results through helpers; context/BroZhai (Tekon) maps compression failure through the same factory; citations/Jeremy reviews the optional machine-readable sidecar and protected prompt placement; evaluation/Doppler reads only final outputs. Reader approval is pending. Native search is rejected before the first enabled researcher request that could execute native tools until strict pre-request tool caps and auditable provenance/counts are agreed; search's existing configuration validator and provider selection stay separate.
- **Planned verification:** `test/offline/test_contracts.py::{test_task_results_reducer_append_and_override,test_run_record_final_snapshot_contract}` and `test/offline/test_orchestration_integration.py::{test_receipt_replay_does_not_duplicate_tasks,test_new_run_resets_private_progress,test_finalization_joins_then_replaces_notes_and_results,test_flag_combinations,test_enabled_context_assembly_preserves_authority}`. These are planned case references, not executed tests.
| `ResearcherOutputState` | `research_outcome` | `ResearchOutcome \| None` (default `None`) | none (single value) | `compress_research` (the `token_limit` and `provider_transient` failure paths only) | `supervisor_tools` in `deep_researcher.py`, at the guard in L308-313 | set when the task ends `failed` → never cleared within a run |

- **Ownership:** `compress_research` is the only writer. `supervisor_tools` only reads it; it never sets or clears it.
- **Lifecycle:** absent (`None`) on every successful run and on every baseline run (`context_trimming = False`), so the success path and the flag-off path are unchanged. Set exactly once, when the compression history cannot be reduced (`token_limit`) or the provider rejects the request repeatedly (`provider_transient`). It is not cleared, because a researcher subgraph instance runs once per `ConductResearch` call.
- **Why a field is needed at all:** `ResearcherOutputState` is a Pydantic model that keeps only the fields it declares, so any extra key returned by `compress_research` is filtered out before `supervisor_tools` sees it. Without a declared field the failure cannot leave the researcher subgraph. An exception cannot carry it either: `supervisor_tools` gathers all parallel researchers with `asyncio.gather` (`deep_researcher.py` L305), so one raising researcher would discard every other researcher's result. A declared output field keeps the failure local to the researcher that produced it.
- **Who reads it:** exactly one place, the guard added to `supervisor_tools` at L308-313 (`observation.get("research_outcome")` followed by a `status == "failed"` check). Nothing else in the repository reads a researcher subgraph result. Because the field is always `None` when `context_trimming = False`, the guard's `else` branch reproduces the baseline line unchanged.
- **Type owner:** `ResearchOutcome` is REQ-001's task-result type (owner: centay, orchestration). REQ-005 does not define a second type; ADR-005 §5 records the approval gate. The category values `token_limit` and `provider_transient` are REQ-005's own vocabulary inside that type.
- **Shared contract:** the field is read by `supervisor_tools`, which belongs to orchestration/REQ-002. Adding it is a joint change and needs centay's approval before implementation (`structural-constraints.md` §6).
- **Companion value:** on the failure path `compressed_research` is a descriptive sentence naming the task and the category, not an empty string, so a supervisor that ignores `research_outcome` still sees why the result is missing (ADR-005 §3(d)).
- **Existing fields untouched:** `compressed_research` and `raw_notes` keep their current type and format, so the data `supervisor_tools` already consumes does not change.

**Trimming is not persisted.** Turn removal happens on a local message list inside `context/recovery.py`; the trimmed history is never written back to `ResearcherState.researcher_messages`. The removed indices (`CompressionOutcome.removed_turn_indices`, `TokenLimitExceeded.removed_turn_indices`) are call-local values, not state. A checkpoint replay therefore starts from the untrimmed history and trims again, deterministically, because `plan_trim` is pure. No field is added to `ResearcherState` for trimming.
