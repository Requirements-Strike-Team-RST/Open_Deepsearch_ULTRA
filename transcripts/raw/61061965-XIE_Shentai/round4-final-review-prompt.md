Final bounded OpenCode plan review, CityU DeepSeek only. DO NOT call any tools, delegate, read files, edit, run commands, or invoke another provider/Claude. All relevant current text is below. Return <=700 words, <=5 actual contradictions; if none, say no remaining contradiction found in this static review (not runtime PASS, human approval or Gate1).

The student prioritises Tekon/Alchemy standards. Approved requirement summary: every accepted research delegation has a valid spec and terminal result; status derives from findings with URLs actually returned by tools in that task; strict budget means individual executed calls. Coverage controls exit with covered > iteration cap > two unchanged eligible turns (ignore think-only) > supervisor model retries exhausted. Completion requests below coverage are refused. Child scheduling/join/errors/outcome are delivery-owned, context trims/retries, citations owns format, all gates pending.

Prior reviewer findings were addressed: actual budget deliberately tighter than baseline turns; summaries/notes render only complete/partial validated findings, raw prose dropped; usage_complete makes token partial totals visible; explicit unknown-tool and invalid-ID handling; exact N1/N2 model/dispatch bounds; decimal threshold; child envelopes consumed internally then plain output appends to cleared main channels; default per-invocation private state; ambient/bound RunnableConfig cleaned via set_config_context plus create_task(context=...). Stateful crash replay is NOT exactly-once; unresolved receipt and off/on policy are declared reader decisions. Input-token cap is a declared course integration/Gate1 gap, not falsely implemented.

Please identify only a concrete contradiction or algorithm path still undefined that is NOT already a named reader/integration decision. Do not ask for source implementation, human acceptance or tests now; this is SA. Don't insist on semantic proof of source entailment or final-report citation validation (out of scope). Don't repeat prior findings unless the correction itself is wrong. Do not write a replacement ADR.

CURRENT ADR (Proposed, authored by Codex coordinator and assistants after your initial analysis/EVAL):
# ADR-002: Typed research tasks and deterministic coverage termination

- **Status:** Proposed
- **Date:** 2026-11-14
- **Module:** orchestration
- **Owner:** Centay — XIE Shentai, 61061965
- **Evaluation:** EVAL-002 (`docs/architecture/evaluation-table.md`)
- **SA Review:** pending; no Gate 1 or Gate 2 approval exists.

This is a local SA proposal against `827fd32f956a0601df3e1fd253d5cc98044fff88`.
It supersedes neither approved requirements nor another owner's draft. Differences
from the historical v0.5 field discussion and reader decisions are listed in
`../orchestration-review-checklist.md`. Types, algorithms and test names below are
planned interfaces, not implemented behavior.

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-001 | C-001 | A code-created specification must cross the supervisor/researcher boundary before execution. |
| REQ-001 | C-002, C-003, M-001 | Code derives status from question-linked findings and task-local retrieved sources; model prose cannot establish coverage. |
| REQ-001 | C-004 | Invalid output has a typed failure path rather than an unvalidated summary. |
| REQ-003 | C-001, C-002, M-002 | Model completion is a request; a deterministic coverage check controls exit. |
| REQ-003 | C-003, C-004, C-005, M-001 | Progress, iteration bounds and supervisor errors share one ordered exit selector. |
| REQ-003 | C-006 | Two historical queries require later live evidence; offline design arguments cannot prove this criterion. |
| REQ-002, contributor | C-005, C-007 | Valid unrun delegations receive results, and failure/placeholder prose cannot become report findings. Dispatch, queuing and joining remain delivery's responsibility. |

Relevant proposed invariants: INV-003, INV-006 and INV-007. The complete case
inventory is the orchestration section of `verification-constraints.md` §7.

## 2. Context

At the baseline, `state.py::ConductResearch` has only `research_topic`; researcher
output is free text. `supervisor_tools` exits before dispatch on model completion,
empty tool calls or `research_iterations > max_researcher_iterations`
(`deep_researcher.py:240–262`). Results above the concurrency slice are lost and a
child exception ends the phase (`:288–342`, delivery's area). `researcher` increments
a model-turn counter (`:422`), while `researcher_tools` checks the limit only after
executing a whole tool batch (`:473–498`). `compress_research` returns unstructured
text or a placeholder (`:511–585`). `utils.get_notes_from_tool_calls` collects tool
text without an evidence boundary (`utils.py:599–601`).

`state.py::override_reducer` **appends ordinary lists**; it replaces a value only
for `{"type": "override", "value": ...}`. A full cumulative list returned as an
ordinary delta would duplicate old entries. `ResearcherOutputState` is a separate
output schema, so a new internal field alone would not reach delivery.

The project requires thin existing nodes, unchanged graph topology and extension
modules importing shared types. `state.py` and `configuration.py` must not import
orchestration. Python remains 3.12; no dependency or permission change is proposed.

## 3. Decision

Choose EVAL-002 option B: shared types in `state.py`, with pure contract, execution
evidence and termination helpers in `orchestration/`. Existing nodes call those
helpers. Keep delivery's fan-out/join and context's trimming algorithms with their
owners. Every behavior below is behind `orchestration_enabled`, default `False`.

### 3.1 Accepting delegations

The enabled schema is `ConductResearchV2`, exposed to the model under the unchanged
tool name **ConductResearch**. Keep the original class for the disabled path.

Validate raw arguments before dispatch. Normalize question identity with
`" ".join(text.split()).casefold()`, preserving the first original question for
messages and unanswered lists. Remove duplicates in first-occurrence order.
An empty question list falls back to the nonblank topic. More than five distinct
questions, blank/non-string entries, a blank topic or a wrong field type are
validation errors, not silently truncated tasks. Missing scope defaults to `""`.
Assign `T1`, `T2`, … to accepted specifications in original call order.

Record every raw call by `tool_call_id` in `delegation_receipts`. A malformed raw
intent receives a `rejected` diagnostic and a matching validation-error
ToolMessage, is never dispatched, and contributes no invented question to coverage.
Only an accepted valid TaskSpec is a delegated research task. Every accepted task
must have exactly one TaskResult, including accepted-but-unrun tasks. This explicit
interpretation of malformed intent requires delivery/owner review; it is not a
silent exception or a change to approved requirement text.

Replaying a known call ID with identical arguments reuses its registration/result.
For different arguments under that ID, reject the new intent with a diagnostic
response, preserve the original registration/result, and add no task or question;
normal turn/cap/stall handling still applies. Validate nonblank string call IDs
before accepting any intent in a turn. An invalid ID rejects that transport-level
turn before dispatch: retain its raw diagnostic outside model history, replace
the malformed AI turn with bounded replanning feedback, and create no invented
ToolMessage ID or fake task. The rejected turn consumes one eligible processed
turn. A completed task is never
converted into `not_run`. This bookkeeping prevents duplicate *state* entries; it
does not promise exactly-once external side effects across a process crash.

### 3.2 Actual execution budget and trusted evidence

`TaskSpec.max_tool_calls` is a maximum of **started executable tool invocations**,
not model turns, HTTP requests inside a tool, search queries inside one invocation,
or token cost. Initially use the configured `max_react_tool_calls` as that maximum.
This deliberately makes the enabled budget tighter than the old value interpreted
as turns times an arbitrary batch size; enabled behavior is not flag-off parity,
and live comparisons must record this change. It must be an integer at least one;
retain the original model-turn watchdog as an
additional bound, with its existing value and disabled-path semantics.

Before creating concurrent execution awaitables, admit executable calls in model
call order, reserving at most the remaining permits. Each started invocation costs
one permit, including a tool that raises and `think_tool`. A denied call costs zero
and receives a matching budget-denied response. `ResearchComplete` is a control
signal with no executable invocation, so costs zero; resolve all other calls in a
mixed batch before compression. Once permits are exhausted, start no more tools
and proceed to compression after all admitted calls join.

An unknown/non-executable tool name is a rejected model intent with a matching
diagnostic response and zero spend, not an attempted invocation. In a researcher
turn it consumes the existing model-turn watchdog but cannot manufacture evidence;
the eventual task status still comes from valid findings. Supervisor unknown-tool
intents are likewise diagnosed, with valid same-turn delegations still processed.
Native tool definitions that execute remotely must pass the capability guard
before model binding; they are not silently treated as local executable tools.

Each accepted task has a code-owned `TaskExecutionEvidence` receipt. The task
wrapper retains it and passes it through a fresh per-task copy of RunnableConfig's
private configurable key `_orchestration_evidence`. Do not mutate shared config,
forward this key into model configuration, or include the live object in prompts.
Because LangChain also inherits ambient RunnableConfig, merely omitting the key
from `.with_config()` is insufficient. The model-call adapter builds a fresh safe
config without the holder in configurable/metadata, uses the locked library
`set_config_context(safe_config)` context manager, and runs/awaits the entire model
coroutine via Python 3.12 `asyncio.create_task(..., context=clean_context)`. Retain
only safe callbacks/tags and existing model settings; bound model configs must
also be clean. Creating a coroutine inside a context but awaiting it outside
does not isolate it. This adapter reuses existing model objects, not new clients.
It records call IDs/starts, trusted returned URLs and available usage metadata.
State stores only serializable `task_evidence_snapshot` checkpoints. A wrapper that
catches a child exception can therefore preserve already-spent tool calls instead
of falsely returning zero. Missing usage metadata is recorded as incomplete in the
receipt. `TaskCost.usage_complete` defaults to False and is True only when every
counted model attempt has valid usage metadata. Token counters sum available
**reported** usage and remain partial totals when that flag is False, not billing
totals. Malformed usage observations produce incomplete-evidence diagnostics,
never authoritative negative, boolean or nonfinite cost.

Only successful retrieval receipts matched to admitted tool IDs can add HTTP(S)
URLs. Tavily's returned source fields/anchored source entries and explicitly
supported MCP metadata adapters are eligible. `think_tool` echoes, error strings,
model messages, arbitrary prose URLs and an output's self-declared `retrieved_urls`
are ineligible. Unknown MCP result shapes add no trusted URLs; do not guess.
Use exact returned URL strings, with no query/fragment removal or redirect
equivalence. The ledger survives message trimming and does not rely on `raw_notes`.

Native OpenAI/Anthropic search executes inside model calls and lacks an audited
strict per-task admission/count contract in this baseline. The proposed enabled
path rejects those search modes before the first researcher request that could
execute native tools, with an
explicit compatibility error; it never substitutes a provider. This restriction
needs search/delivery review. Flag-off retains the existing provider behavior.
No native search or live project run was performed during this SA task.

### 3.3 Compression draft protocol and result acceptance

Preserve context ADR-005's `CompressionOutcome.summary: str`. On the enabled path,
the existing compression request produces ordinary Markdown with exactly one
sidecar **before** the final, unique `### Sources` section:

````text
<task_findings_v1>
```json
{"schema_version":1,"findings":[{"claim":"A claim","source_numbers":[1],"answers":["Exact required question"]}]}
```
</task_findings_v1>
### Sources
[1] Source title: https://example.org/evidence
````

The delimiters must be standalone lines, there must be exactly one block and one
JSON object, and the block allows only the shown keys. Require integer version 1,
nonblank claims, positive integer source numbers (booleans excluded), and answer
strings exactly matching that task's original `must_answer` items. Parse sources
only as `[n] Title: HTTP(S)-URL` lines in the final section; identifiers are unique,
sequential from one and URLs are unique. Titles are display text, not authority.

Missing/duplicate delimiters, malformed JSON, extra keys, wrong types, unknown
question/source references or ambiguous source numbering fail the task as
`invalid_result`. A structurally valid finding that refers to a URL absent from
the trusted task receipt is discarded; derive status from the remaining findings.
This distinction implements C-003 without treating all invalid output alike.

Code builds TaskResult's identity, questions, cost, retrieved URLs, coverage and
status. The model only proposes claims/answer links/source references. The
Centay's compressor adapter consumes the raw context string, discards its free-text
body and sidecar from reader-facing strings, and deterministically renders
`TaskResult.summary` and `compressed_research` from complete/partial tasks'
validated findings and their sources before returning to delivery. Raw compression prose is diagnostic raw_notes
only; it cannot bypass this adapter into a ConductResearch ToolMessage or report
findings. Malformed results return no summary. Context still returns a string;
orchestration decides which validated content leaves that boundary.

At finalization, construct `notes` deterministically only from **complete/partial**
tasks' validated Finding.claim and their referenced validated sources, in task/finding
order. A failed/unanswered task may have a sourced tangential finding with no
required-question answer; it still contributes no summary or notes. Never copy
free-text compression prose, raw notes, the sidecar, reflections or failure diagnostics into
report findings. Findings retain per-task numbered citations and one Sources list
per task; final cross-task renumbering remains citations/report prompt's job.
URL membership establishes retrieval provenance, **not semantic entailment**.

### 3.4 Coverage, turns and one exit selector

Let Q be the distinct normalized required questions of all accepted registered
tasks, including failed and not_run tasks. A question is answered if a validated
finding in any task answers it. Coverage is `|answered| / |Q|`, or zero for empty Q.
Use exact fractions internally; convert the finite configured threshold with
`Fraction(str(threshold))`, not `Fraction(threshold)` on a binary float. Serialize
coverage with `float(answered_count / total_count)` from the same exact fraction,
and recompute/compare that value when validating a final snapshot. Re-delegating
the same question does not increase the denominator. New unanswered questions can
lower coverage. Require nonempty Q and a finite threshold `0 < threshold <= 1`
before covered; proposed default `coverage_threshold = 0.8` needs SA Review.

`completed_supervisor_turns` starts at zero. It counts successfully processed
supervisor responses, including think-only, no-tool and completion-only turns.
At tools entry, register all raw intents before evaluating an early exit. If the
count is already N=`max_researcher_iterations`, accepted pending tasks are not
dispatched and receive `failed/not_run`. Otherwise process the turn, join every
started task, then increment the count and evaluate exit. At supervisor entry an
already reached cap finalizes without a new model request. Thus an all-delegation,
below-threshold N=1 fixture dispatches exactly one turn and N=2 exactly two; neither
starts a supervisor request N+1. No new request starts after cap selection; each
of those at most N calls has at most the existing configured retry attempts.
Keep the old `research_iterations`
counter and comparisons confined to flag-off or diagnostic compatibility.

For an eligible processed turn, compare coverage immediately before and after the
turn using its prior and new registered ledgers. Equal coverage increments
`unchanged_eligible_turns`; any change resets it to zero. Ignore think-only turns
for this streak, without resetting it; they still consume the global turn budget.
No-tool, completion-only and mixed turns are eligible. Two unchanged eligible
turns with a think-only turn between them therefore stall. Registering new
questions is part of the after-turn denominator, not evidence of progress by itself.

One pure `select_exit` chooses, in this order:

1. **covered:** nonempty Q and coverage meets threshold;
2. **budget_exhausted:** processed-turn cap reached;
3. **stalled:** two unchanged eligible turns;
4. **failed:** supervisor's own model call exhausted its existing configured retries;
5. otherwise continue.

At a supervisor error, pass the error to this same selector, using current state;
do not hardcode failed and overwrite a higher-priority condition. Child failures
become task results through delivery and do not independently end research.
ResearchComplete and no-tool turns are requests, never completion authority. If
the loop continues, return unresolved original questions in deterministic order.
Tool calls receive matching ToolMessages; no-tool feedback uses a HumanMessage,
not a fabricated tool-call ID. Mixed completion/delegation turns process all valid
delegations unless an already applicable early exit prevents dispatch.

Before any early exit, resolve every accepted pending registration to its actual
result or not_run, then recompute Q/coverage and select the final reason. Example:
old 4/5 coverage plus two distinct pending unanswered questions becomes 4/7;
at cap it exits budget_exhausted. Repeating the same questions leaves 4/5 and
covered wins. Never reuse a stale `run_coverage` value.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| Prompt-only gating | Cannot establish code-derived status, provenance or exit authority; fails critical drivers. |
| Whole-node orchestration takeover | Can be correct, but absorbs delivery's dispatch/join scope and maximizes shared-node coordination. |

The full qualitative comparison is in EVAL-002. No prototype, latency measurement
or passing behavior test is claimed by this selection.

## 5. Components and Interfaces

### Shared types, defined once in `state.py`

| Type | Fields / constraints |
|---|---|
| ConductResearchV2 | `research_topic: str`, `must_answer: list[str]=[]`, `scope: str=""`; validation per §3.1; exported tool name ConductResearch. |
| TaskSpec | `task_id: str`, `research_topic: str`, `must_answer: list[str]`, `scope: str`, `max_tool_calls: int`; code-created, nonempty valid questions and budget. |
| Source | `source_id: str` (S1…), `url: str`, `title: str=""`; ID unique within task. |
| Finding | `claim: str`, `source_ids: list[str]`, `answers: list[str]`; nonempty valid sources, exact task question references. |
| TaskCost | `tool_calls: int=0`, `input_tokens: int=0`, `output_tokens: int=0`; strict nonnegative integers, no boolean coercion. New proposed `usage_complete: bool=False` makes incomplete token totals visible without changing tool-call units. |
| TaskResult | `task_id`, `status`, optional `failure_category/failure_reason`, `summary=""`, `findings=[]`, `sources=[]`, `retrieved_urls=[]`, `must_answer`, `coverage=0.0`, `cost`; fresh collection defaults. |
| RunRecord | `exit_reason`, optional `exit_detail`, `run_coverage`, `coverage_threshold`, `task_results=[]`; final snapshot only. |
| TaskExecutionEvidence / SerializableReceipt | Private code-owned live execution receipt and its serializable snapshots; no model-authored authority fields. |

Enums remain v0.5's `complete|partial|failed`,
`covered|budget_exhausted|stalled|failed`, and
`unanswered|invalid_result|runtime|token_limit|not_run`.
Complete requires coverage 1 and no failure fields; partial requires 0<coverage<1
and unanswered; failed requires coverage 0. Every noncomplete result has category
and reason. Runtime/token_limit/invalid_result/not_run failures have no findings or
summary; an unanswered result with no valid findings also has an empty rendered
summary. `unanswered()` preserves question order.
Reject nonfinite coverage/threshold, duplicate IDs, identity/question mismatches,
and claimed cost/provenance inconsistent with the code receipt.

| Component | Responsibility | Interface (planned) | Called by |
|---|---|---|---|
| contracts.py | Valid specs, draft parsing, result validation and failure construction | `build_task_spec(tool_call, task_id: str, config) -> TaskSpec`; `render_task_message(spec) -> str` | delivery dispatch; thin nodes |
| contracts.py | Build trusted results | `build_task_result(spec, compression_text: str, *, evidence) -> TaskResult`; `validate_task_result(output, spec, *, evidence) -> TaskResult` | compression adapter; delivery collector |
| contracts.py | Typed failures with actual cost | `failed_result(spec, category, message, *, evidence) -> TaskResult`; `not_run_result(spec) -> TaskResult` | delivery/context exception mapping; cap finalization |
| evidence.py | Admit executable calls, record receipts and supported source metadata, snapshot evidence | `admit_tool_calls(calls, spec, evidence)`; `record_tool_result(evidence, call_id, observation, adapter)`; `validate_execution_capability(config) -> None` | researcher / researcher_tools; orchestration entry |
| termination.py | Registration, exact coverage, progress and exit selection | `register_delegations(calls, receipts, config)`; `coverage_snapshot(results)`; `select_exit(snapshot, *, cap_reached, unchanged_turns, supervisor_error)` | supervisor_tools; supervisor error/entry |
| termination.py | Validate completeness and produce one terminal update | `finalize_run(receipts, results, selection, threshold) -> RunRecord`; `RunRecord.to_state_update() -> dict` | thin node finalization |
| state.py | Read final output | `RunRecord.from_state(state) -> RunRecord \| None` | delivery and any final-state reader |

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

Shared readers must review this contract: Alchemy (delivery), Tekon/BroZhai
(context), and the citations owner for the compression protocol. Evaluation's
current draft consumes report/brief/evidence rather than requiring a new
orchestration import; preserve those inputs without introducing a dependency.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** the orchestration section of memory-design §5 owns the field table,
  defaults, writer and lifecycle. New supervisor-private counters/receipts and
  researcher evidence snapshots must not become AgentState output fields.
- **Runtime policies:** POL-002–POL-010, detailed in the module policy section.
- **Invariants:** INV-003, INV-006 and INV-007, all Proposed.
- **Deterministic boundary:** input acceptance, execution permits, source admission,
  result validation/status, coverage, progress and exit selection do not call a
  model. Model proposals enter these boundaries as untrusted data.

Delivery returns each turn's ordered **plain list delta** via
`update_payload["task_results"]`. The node computes old+delta transiently, then
returns the delta once when continuing. On exit it returns the final override
instead of both delta and override. No extension directly mutates graph state;
the node is the single channel writer. At the parent boundary the final lists
are appended once to cleared public channels; ORC-040 must include old parent
notes/results, the brief reset, and this actual child-to-parent propagation. A
direct caller with nonempty channels must clear them explicitly before accepting
this output. The existing `write_research_brief` return
initializes a new enabled run by clearing **public** terminal fields/results and
notes. Private counters/receipts are not AgentState fields and cannot be reset by
that main-graph update. Keep the existing default `supervisor_builder.compile()`
per-invocation mode: each new subgraph call gets fresh private channels, read with
explicit zero/empty defaults; resuming the same invocation restores its private
checkpoint instead. Do not change it to `checkpointer=True` or infer a fresh run
from None exit_reason. Direct entry must distinguish new input from same-call
checkpoint resume; ORC-039 verifies two calls on the same parent thread.
This follows the documented [LangGraph subgraph persistence modes](https://docs.langchain.com/oss/python/langgraph/use-subgraphs#per-invocation-default),
not an executed project test. Flag-off writes none of the new fields.

### Per-turn context and compaction contract (course D2.2)

| Call | Ordered assembly | Protected / re-injected authority |
|---|---|---|
| Supervisor | system instructions and tool schema → immutable research brief → conversation/tool results → deterministic unresolved-question feedback | Completion rule, cap and unresolved original question texts are supplied by code, not copied from retrieved text. |
| Researcher | research system instruction → first HumanMessage from TaskSpec → AI/tool history | Topic, scope, exact questions and tool budget remain in the protected preamble; tool observations remain untrusted data. |
| Compression, every attempt | fixed system prompt with compression/citation instructions and immutable TaskSpec/trusted-source map → surviving history → protected final compression instruction with sidecar rules | Pass the assembled fixed authority block via context's existing `system_prompt` argument, which its internal retry loop retains on every attempt. The ledger itself stays outside mutable messages. Insert JSON/schema fragments **after** existing `.format(...)`, avoiding accidental format braces. |

The baseline output caps are research 10,000 tokens, compression 8,192, report
10,000 and Tavily summarization 8,192. They are configurable **output** maxima;
`max_content_length=50,000` is a **character** cap. Neither is an input-token cap.
`get_model_token_limit` is a static lookup, may return None, and does not enforce
request input size. Do not present it as a verified provider context window.

The current bounded compaction trigger is a recognized compression token-limit
error, classified against **compression_model**, followed by context ADR-005's
oldest-whole-turn recovery, at most three attempts. For on/on there is one recovery
loop, not nested three-by-three retries. Context must preserve the preamble,
compression instruction and newest AI/tool turn. Orchestration re-injects critical
spec/format/source references for every attempt; it does not implement trimming.

**Integration gap:** a proactive input-token cap/compaction threshold with an
approved tokenizer/model-window source is not defined in current main or the
context draft. Course D2.2 requires the whole-system policy. Ask Tekon/Alchemy to
resolve it at integration; this ADR supplies the boundary and reactive behavior,
not a fabricated numerical input cap or an unapproved tokenizer dependency.

Flag combinations: off/off keeps baseline; on/off uses typed acceptance and the
bounded baseline compression attempts; on/on uses context's one recovery loop
followed by this parser; off/on has no TaskSpec and needs context/delivery to agree
their typed-exception mapping. Its orchestration run fields stay absent; a final
reader returns None, and no RunRecord is constructed for that path. Do not invent
orchestration fields for off/on or
claim it is baseline-equivalent when context is enabled.

## 7. Verification

Every REQ-001 C-001–C-004/M-001 and REQ-003 C-001–C-006/M-001–M-002 maps to its
exact requirement-specified path in verification-constraints §7. Additional
planned cases cover budget admission before fan-out, failed-call cost, forged
provenance, sidecar parsing/stripping, stable duplicate questions, threshold
boundaries, denominator growth, precedence, N=1/N=2, idempotent registration,
delta/override behavior, new-run reset and flags. Each proposed invariant has
named violation tests. Run the shared contract suite and every existing offline
suite after implementation; do not author those tests before Gate 1.

REQ-003 C-006 is **NOT_RUN**. The recovered historical query texts and the old
search-disabled configuration are recorded in the raw evidence reference. A
source-capable live configuration must be reviewed before claiming sourced
coverage; preserve query text and disclose configuration differences. No Claude
API is permitted by this student's task authorization.

Actual SA checks, their commands and verdicts are recorded in the review checklist.
Document checks do not establish runtime correctness, live fit or human approval.

## 8. Consequences

**Positive:** code decides authoritative status/exit; trusted evidence survives
trimming; each accepted task is traceable; readers have one terminal snapshot;
the extension can be tested with fake models and literal fixtures.

**Costs:** several existing node hooks and shared state additions require coordinated
review. Strict parsing can reject useful but malformed model output. Findings
inherit the model's question/claim association: URL provenance is narrower than
fact verification. Coverage is of delegated questions, not proof that the model
decomposed the entire research brief correctly. Native-search compatibility is
narrowed on the enabled path until strict budget support is designed.

**Operational limits:** receipt state deduplication is not durable exactly-once
tool execution. A crash after an external request but before checkpointing can
leave uncertain cost/side effects; do not automatically replay that window or
claim a verified result. Diagnostics must avoid credentials and stack traces in
reader-facing reasons; original safe error text/category remains available to
delivery. No new retention service or cross-version checkpoint migration is added.

Reopen this decision when any shared field/helper or citation protocol changes;
native search gains auditable pre-request caps; receipt/ledger invariants fail;
input-budget policy cannot protect the declared context layers; real compression
frequently fails the strict schema; live C-006 is unmet; a requirement changes; or
checkpoint/resume needs stronger crash guarantees. Persistent rejection of the
new delegation schema is also a reopen trigger: its increased prompt/schema
burden is a model-compliance cost, not a measured improvement. Reopen through ADD/ADR and SA
Review, with affected tests returning to Gate 2; never weaken tests to fit output.

## 9. Implementation Steps

These are future Build steps **after Gate 1, Test Author baseline evidence and
Gate 2**. No step below has been performed in this documentation branch.

1. In `state.py`, define the shared types and validators once; add own fields to
   the existing state classes and task_result to ResearcherOutputState. Leave
   baseline ConductResearch and existing reducer behavior intact.
2. Add `orchestration/__init__.py`, `contracts.py`, `evidence.py`, `termination.py`.
   Implement the pure algorithms in §3 and the interfaces in §5. Add the new
   subpackage to `[tool.setuptools] packages` in `pyproject.toml` with human review;
   this is packaging, not a new dependency or permission change.
3. Add only `orchestration_enabled=False` and validated `coverage_threshold=0.8`
   to Configuration with `x_oap_ui_config`. Add enabled-run initialization to
   `write_research_brief`'s existing return for public fields only. Retain the
   default per-invocation subgraph compilation and private zero/empty defaults;
   specify fresh versus resumed direct inputs in helper documentation/fixtures.
4. In `supervisor`, select the enabled tool schema, check the processed-turn cap
   before another request and map exhausted configured model retries through the
   same exit selector. Add no new model client and no unbounded retry loop.
5. In `supervisor_tools`, register intents once, apply pre-dispatch exits, and use
   delivery's approved wrapper for task-scoped evidence, queuing, isolation and
   join. **Alchemy owns dispatch/gather/consumer error handling.** Centay supplies
   contract/registration helpers and the pre/post-turn selector. Agree the hunk
   split before editing; context's proposed change to the missing-summary default
   is the same delivery hunk, not a second owner.
6. In `researcher`/`researcher_tools`, validate enabled execution capability, carry
   the protected TaskSpec, allocate permits before task creation, capture matching
   receipts and maintain serializable snapshots. Isolate every model attempt in
   the cleaned Runnable context described in §3.2, including context recovery
   attempts; a fake model must inspect the actual received config for leakage. Keep baseline tool assembly at
   `get_all_tools`; do not change provider selection or search fallback policy.
7. In `compress_research`, call exactly one selected recovery path. On success
   parse/strip its string response and build TaskResult with the trusted receipt;
   on typed context exhaustion or other failure use the evidence-aware helper.
   **Tekon owns trimming/classification/recovery**, Centay the successful result
   adapter and the common exhausted-result mapping, Alchemy exception collection.
8. Draft enabled-only prompt additions in `prompts.py`, reusing the citations
   owner's format and avoiding format-brace collisions. Jeremy/citations and
   Tekon review the added protected instructions. Keep the original disabled
   strings and existing graph topology; record prompt version/evaluation in the
   integrator's approved scheme rather than inventing a version-file migration.
9. At every finalization, verify all accepted registrations have one result, apply
   final precedence, emit all terminal fields together, override results/notes
   within the subgraph, and append its final lists once to the reset parent
   channels. Keep internal counters/receipts out of main output. Delivery alone computes
   run outcome and limitations from that snapshot.
10. Run the approved contract/new/all-prior offline suites and active project
    gates; Verify independently records real results. Run the approved live queries
    on an authorized non-Claude configuration only after the required reviews.
    Update code/test evidence in trace-matrix and the actual AI-use/review records;
    never mark the requirement verified from this SA draft.
