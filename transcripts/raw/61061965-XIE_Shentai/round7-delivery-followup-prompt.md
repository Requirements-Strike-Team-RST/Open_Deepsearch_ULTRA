Follow-up reconciliation of your simulated peer review. You remain AI OpenCode plan on CityU DeepSeek, NOT the real teammate or a human gate. NO TOOLS, file reads/edits, commands, other providers, Claude or delegation. All current changed text needed is below. Return <=600 words: which of your original new gaps remain, if any, and distinguish source-supported findings from assumptions you retract. No runtime PASS/approval.

Current updates: RegisteredDelegation/JoinedTurn proposed delivery port with injected contract callbacks (no extension-to-extension import), code-owned node-retained per-task evidence map, accepted-task-only result delta, original call order regardless of completion order, all children joined. Consumer canonically renders a valid typed result when auxiliary compressed_research is missing; real producer fills all required output fields. Report notes stay separate from code-generated supervisor failure feedback. Shared computed unanswered_questions uses existing must_answer/findings.answers, no new serialized field or float/task-count calculation. New planned ORC044-046 cover queue/failure ordering/legacy field mutation, global unanswered calculation, and 3-attempt/parse-once/canonical-output boundary. No project tests were executed.

CORRECTIONS TO PRIOR ASSUMPTIONS:
- TaskResult ALREADY has findings[*].answers; RunRecord has task_results, so question data were not absent. Concrete case: T1 answers Q1-Q8; T2 partial answers Q9 of Q9/Q10; T3 failed repeats Q1. Distinct coverage9/10, global unanswered[Q10], T3 local unanswered[Q1], delivery partial despite covered. Task count2/3 is not coverage.
- A concurrency1 queue does NOT start all3 children simultaneously; completion-order robustness is independently covered with concurrency2.
- Context has no implemented recovery.py in this baseline. Its proposed attempt=0, while attempt<3, increment on exception gives failure/failure/success =3 calls. Success counting does not imply only2 calls. Stale instruction indices are a risk requiring recomputation, not a demonstrated implementation bug.
- Context helper does not need an evidence parameter when the node retains the receipt in a local variable outside the clean coroutine and maps returned success/typed exception after await.
- Default0.8 is converted as decimal4/5. A caller supplying 0.1+0.7 has supplied a different value; rounding all thresholds to one decimal would be wrong.
- Shared raw consumer hunk and off/on remain declared reader decisions; ordinary compression exceptions were swallowed in the baseline, not propagated. We did not edit another member's draft.

CURRENT ADDED CONTRACT TEXT:
**Delivery port (Proposed, reader approval required).** `accepted` is an ordered
list of `RegisteredDelegation(call_id: str, spec: TaskSpec)`. Rejected raw intents
are handled by the node and are not variants in this accepted-task list. The
node/dispatch boundary allocates a separate evidence holder per spec and retains
the mapping while the collector runs. Delivery receives the existing contract
validator/failure factory/renderer as callables; it does not import orchestration
internals or reimplement status/coverage. Dispatch still owns per-child config
copies, queueing, isolation and joining.

`JoinedTurn` contains only `task_results: list[TaskResult]`,
`tool_messages: list[MessageLikeRepresentation]` and `raw_notes: list[str]`.
Every accepted call appears once in result/tool-message order matching `accepted`,
**independent of completion order**. All started children have joined before it
returns; task handles and live collectors are neither serialized nor returned as
state. The node merges these messages with its own control/rejection feedback in
the original supervisor tool-call order, then publishes the result delta once.

`render_supervisor_result` includes code-generated task identity, status, safe
failure category/reason and unanswered questions, followed by canonical findings
for complete/partial tasks. Such typed failure feedback is useful to the
supervisor but is never a report finding: final notes are rendered separately
from findings, not scraped from these ToolMessages. No legacy placeholder, raw
compression body or sidecar is used. Control/rejection feedback for held raw calls
is included in the same terminal tool-turn update even when it exits; a supervisor
entry with no unprocessed response invents no feedback and starts no request to
flush diagnostics. No cross-crash exactly-once feedback guarantee is added.

`RunRecord.unanswered_questions()` derives the globally unanswered distinct
questions from the existing `task_results[*].must_answer` and
`findings[*].answers`, using the same question-identity calculation as coverage
and preserving first original occurrence order. It adds no serialized field.
Delivery also has `TaskResult.unanswered()` for per-task limitations; a question
answered by another task can be globally covered while an earlier task remains
failed. Never derive these lists from task counts, rounded coverage or reason text.

`from_state` returns None for an absent run (empty/absent results and all terminal
fields absent/None), raises ValueError for an incomplete/inconsistent final
snapshot, and is **not** used on intermediate supervisor checkpoints. Reader
failure policy belongs to delivery. `to_state_update` emits all five run fields
together plus explicit override envelopes for task_results and notes **inside the
supervisor subgraph**. Its reducers consume these envelopes; compiled subgraph
output carries plain final lists. The unchanged parent node appends these lists
to the empty public channels prepared by write_research_brief. It does not receive
a magical cross-subgraph override. Finalizers
check registration/result cardinality as well as the model's structural validators.


Parse exactly once after the selected recovery path returns a successful string.
A syntactically successful model response with a malformed sidecar ends as
invalid_result; it does not start another compression/format-repair loop. Before
calling recovery in the cleaned Runnable context, the node saves strong local
references to its TaskSpec and execution evidence. Recovery needs no evidence
parameter: its success/typed exception returns to the node, which still holds the
receipt and performs result mapping outside that clean model context.

The enabled producer always returns the legacy required output fields as well as
the typed result: `compressed_research` (canonical finding text or `""`),
`raw_notes` (diagnostic list), and `task_result`. A consumer validates the typed
result against the registered spec and its own retained receipt; it never trusts
the child's auxiliary string. If a test double/raw mapping omits that string but
contains a valid evidence-consistent result, render it canonically rather than
adding a placeholder or second result. Missing/invalid TaskResult itself becomes
failed/invalid_result. An output-schema exception before a usable result reaches
the collector is an output-contract failure, not fabricated successful research.


Evaluate only your delivery gaps G1-G4 and state whether each is resolved by these clauses.
