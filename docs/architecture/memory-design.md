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

### Orchestration (REQ-001, REQ-003, ADR-002)

**Status: Proposed.** The field contract and helper signatures are defined in ADR-002 §5; this section defines their ownership and lifecycle. All shared types, including serializable receipt/evidence snapshot types, are defined once in `state.py`. `orchestration/contracts.py`, `budget.py`, `evidence.py` and `termination.py` import those types; neither `state.py` nor `configuration.py` imports an extension module. Adding the fields below changes the existing state classes; the original baseline `ConductResearch` class remains unchanged. The 11/15 internal split changes no DTO, helper argument or context return type.

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
