# Read-only audit: invocation budget, evidence ownership and response truncation

Date: 2026-11-15 (Asia/Taipei). Author: Codex review assistance for Centay.

This is an advisory audit, not SA Review, a human approval, product verification or an implementation. The sidechat handoff was treated as evidence, including its historical instructions, rather than as fresh authority. No project file, source, test, configuration or Git state was changed by this audit. No model or network request was made. The only new artifact is this external audit file.

## 1. Evidence and current state

- Inspected checkout: `/Users/e1bae/src/homework/5351/project/sa-centay-2026-11-14`.
- HEAD: `827fd32f956a0601df3e1fd253d5cc98044fff88`; existing SA/document/transcript changes are uncommitted and were preserved.
- Read the sidechat's final calibrated summary and relevant discussion/evidence sections, ADR-002, module memory/runtime/structure/test sections and the real baseline source.
- `src/open_deep_research/` currently contains only `state.py`, `deep_researcher.py`, `utils.py`, `prompts.py`, and `configuration.py`. Neither `orchestration/evidence.py` nor `budget.py` exists. Their responsibilities are Proposed SA, not code being refactored.
- Locked versions inspected from `uv.lock`: langchain-core 1.4.8, langchain-openai 1.1.14, langchain-anthropic 1.4.7, langchain 1.3.9, langgraph 1.2.9. This identifies the project lock, not the school gateway's actual response shape or an executed adapter test.

## 2. Should the proposed evidence.py be split?

Yes, a small internal split is coherent if the owner wants the names to express the distinction between execution control and factual observation. It is not a correctness fix in itself, and keeping one file with an explicit execution-ledger responsibility would also be reasonable at this scale. The important invariant is one authoritative task receipt, not a particular number of Python files.

ADR-002 currently groups admission, capability checking and recording in one `evidence.py` interface row (§3.2, lines 92–155; §5, line 325). The smallest two-file proposal is:

| Proposed file | Owns | Does not own |
|---|---|---|
| `orchestration/budget.py` | Ordered pre-execution admission through existing `admit_tool_calls(calls, spec, evidence)`; the existing `validate_execution_capability(config)` guard; policy for permitting no more than the remaining actual local tool invocations | A second spend counter, a second task ledger, model-token hard budgets, HTTP request accounting, task queues/concurrency slots or context trimming |
| `orchestration/evidence.py` | Code-owned receipt mutation/observation primitives: starts, successful retrieval metadata, failures, available usage, snapshot/restore; existing `record_tool_result(evidence, call_id, observation, adapter)` | A second admission algorithm, launching tool awaitables, researcher scheduling, run outcome or model-authored evidence |
| `orchestration/contracts.py` | Read-only consistency checks and TaskResult construction from the same evidence | Executing calls or spending a second permit during validation |
| `orchestration/termination.py` | Existing accepted-delegation registration, exact coverage, progress and finalization | Tool-budget policy, queues or report acceptance |

### Conditions that keep this minimal

1. Leave `TaskSpec`, `TaskResult`, `RunRecord`, enums and current TaskCost proposal unchanged. Shared/private types remain defined once in `state.py`; do not add a competing `BudgetState` graph channel or duplicate the receipt in another module.
2. Preserve all existing public signatures, particularly keyword-only `evidence` on `build_task_result`, `validate_task_result` and `failed_result`. Preserve `not_run_result(spec)` and its known-zero spend. Changing a file's internal home does not justify changing readers' DTOs.
3. Keep one `TaskExecutionEvidence` holder per accepted task. Admission and recording refer to that holder. Reuse `_orchestration_evidence`, existing safe-config isolation, wrapper lifetime and serializable snapshot protocol. No additional runtime context key or global registry is needed.
4. Perform check-and-reserve as one uninterrupted operation before creating the batch's awaitables. If synchronization is required, it belongs to the one holder, not separate locks protecting divergent counters in the two files. A possible dependency direction is `budget.py -> evidence.py -> state.py`, with no reverse import from evidence into budget and no import from state into orchestration.
5. Distinguish a reserved-but-unstarted permit from a recorded start. Record each actual start once; failure does not refund it. A cancelled reservation that never starts must not become `TaskCost.tool_calls`. Existing crash-window uncertainty remains explicit. The split must not weaken the current no-exactly-once claim or invite automatic replay.
6. `researcher_tools` remains the execution boundary. Budget selects/adopts permits; the adapter starts only admitted work; evidence records actual start/result/usage. Delivery still owns research-task queues, concurrency, isolation and joining. Context still owns compression retries/trimming, and delivery owns report outcome.
7. Re-export the existing entry points from `orchestration/__init__.py` if a stable package surface is desired. Node adapters/other owners should not need to know whether admission lives in `budget.py` or `evidence.py`. No new package, dependency, model client or graph topology change is required.

### Documentation affected by adopting the split

| Document | Small change needed |
|---|---|
| ADR-002 §§3.2, 5, 9 step 2 | Add budget.py, give admission/capability guard its row, retain the receipt and helper contract; state one-way internal dependency and atomic reservation rule |
| `structural-constraints.md` §10 | Update internal file responsibilities and allowed internal dependency; do not alter owner boundaries or shared interfaces |
| `memory-design.md` §5 | Add budget.py to type consumers and distinguish reservation from recorded start while preserving every field/reducer/lifecycle |
| `invariants.md` INV-003/INV-006 | Point admission enforcement to budget.py and facts/snapshots to evidence.py; statements need not change |
| `trace-matrix.md` REQ-001 row | Add the proposed budget enforcement component; requirement text/status remain unchanged |
| `evaluation-table.md` EVAL-002 | Only adjust the selected option's internal allocation if it currently enumerates files; do not invent a fourth architecture candidate or a new experiment |
| `runtime-policy-catalog.md` POL-004/POL-005 | Clarify enforcement locations; budget units and behavior remain unchanged |
| `verification-constraints.md` §7 | Preserve existing behavioral symbols (especially ORC-014/016/019). Add one boundary expectation that reservation/start/result/validation share one count and validation never debits again, rather than testing filenames |
| Review checklist/handoff/package manifest | Record that this is an internal SA allocation change, what remains pending, and regenerate any later delivery package if the design is actually edited |

Historical transcripts and old raw evidence must not be rewritten to pretend that the two-file proposal existed earlier.

### Main risks

- Two counters or two locks drift, so budget denies based on one value while TaskResult reports another.
- A permit is counted both at reservation and start, or failed work is incorrectly refunded.
- Cross-imports create a dependency cycle or move live receipt objects into model config/checkpoints.
- A small file split becomes an unapproved cumulative-token/HTTP budget or delivery scheduler project.
- Tests become coupled to internal file imports instead of the accepted package contracts.

These risks are avoided by the conditions above. There is no evidence that splitting alone improves runtime behavior or performance.

## 3. Actual response-metadata propagation in the baseline

Line numbers below were read from the current real source at the inspected HEAD; no product run was performed.

| Stage/function | Actual response path | Metadata boundary and implication |
|---|---|---|
| `supervisor`, `deep_researcher.py:178–223` | Model returns at line 214; line 220 stores the complete `response` in `supervisor_messages` | Metadata can remain on that message object, but this node performs no successful-response truncation check. `supervisor_tools:240–262` reads `tool_calls`, empty calls and completion requests; a truncated response containing apparently valid calls is not explicitly distinguished. |
| `researcher`, `deep_researcher.py:365–424` | Model returns at line 415; line 421 stores the complete response in `researcher_messages` | The full message can retain adapter metadata, but researcher/tool dispatch has no explicit finish-state acceptance rule. `researcher_tools:444–498` uses calls/control/counters. |
| `compress_research`, `deep_researcher.py:511–585` | Receives response at line 551; returns only `str(response.content)` as `compressed_research` at line 561 | This is the clearest lossy conversion. Raw compression response metadata is neither returned nor recorded. `raw_notes` at lines 554–557 is built from earlier research messages' **content**, not the compression response or its metadata. A valid-looking truncated string follows the success return and bypasses exception handling. |
| Researcher subgraph output, `state.py:92–96` | Output schema contains only `compressed_research: str` and raw_notes | No output field currently carries the compressor's completion state; adding a private record before conversion is smaller than assuming this string can reveal it. |
| `supervisor_tools`, `deep_researcher.py:305–313` | Collects child dictionaries and puts their `compressed_research` string into a new ToolMessage | Original compression response metadata cannot be reconstructed here; the boundary already discarded it. An error-string default is a separate known issue. |
| `final_report_generation`, `deep_researcher.py:607–697` | Model response at 650–652; `final_report` becomes its content at 656, but `messages` also receives the full object at 657 | Metadata is retained in the message history if the adapter supplied it, yet no acceptance check occurs before returning report text as success. Consumers reading only final_report lose it. Report failure/outcome belongs to delivery/REQ-004. |
| `clarify_with_user:89–114`, `write_research_brief:142–171` | `with_structured_output` produces parsed structured values; code creates new messages from selected fields | The baseline does not request an include-raw result and does not preserve raw completion metadata at these node return boundaries. Parsed validity alone is not a general completeness proof. These are upstream scope/owner concerns, not justification to redesign them in Centay's module. |
| Tavily summarization setup `utils.py:85–93`; `summarize_webpage:175–204` | Structured Summary model is invoked at 194; its fields become a formatted string at 199–204 | Another metadata-losing path. It is tool-internal summarization, not an extra local tool invocation, and should be reviewed by the relevant shared-tool/search owner rather than silently absorbed into Centay's budget split. |

The baseline metadata readers at `utils.py:607–658` check native search usage/tool outputs only: `anthropic_websearch_called` reads usage/server-tool counts and `openai_websearch_called` reads additional tool-output metadata. Neither checks completion/truncation status.

`utils.is_token_limit_exceeded:665–701` and provider-specific helpers classify **exceptions**. They do not consume successful model-response metadata. The compression catch at `deep_researcher.py:565–574` and report catch at `:661–683` therefore do not, by themselves, catch an ordinary returned message whose finish metadata signals output-length exhaustion. The baseline compression classifier also uses research_model at line 569 rather than compression_model; the context proposal already addresses that separate issue.

No project source reference to `finish_reason`, `stop_reason` or a normalized response-completion state was found. This is a static observation, not proof of how a provider's underlying adapter behaves. The school gateway's actual fields/values remain unverified.

## 4. Small truncation-design addition without changing public task DTOs

The current Proposed SA covers token-limit exceptions and malformed successful strings, but not an explicit length-ended response whose sidecar remains parseable. It is reasonable to add the boundary, independently of the budget.py split.

1. **Capture before converting to string.** At the existing node/model adapter, observe the actual response object, usage and provider metadata before `response.content` extraction. Use an internal attempt observation with normal / length-truncated / unknown classification and preserve the safe raw finish marker for diagnostics. This can live with the existing private task evidence/attempt observations; it need not add a field to TaskResult or RunRecord.
2. **Verify each supported adapter mapping.** Do not assert that every provider uses one common field or that the school router matches public DeepSeek responses. An absent/unrecognized marker is unknown, not an invented stop or an invented truncation. Decide the supported unknown-state policy explicitly; do not quietly claim complete response observation when it is missing.
3. **Preserve context's string interface.** A node-owned wrapper around the existing configured Runnable can capture metadata for each compression attempt before returning the unchanged response to context. Context can retain `CompressionOutcome.summary: str` and its existing signature. Keep the receipt reference outside the clean provider config, record it once per attempt, and retain the existing single retry owner. This is an interface-review proposal, not an implemented adapter.
4. **Conservative compression policy for review.** For an explicit length-truncated compression response, reject result acceptance even if JSON/Sources parse; a proposed mapping is the existing `failed/token_limit` category with retained actual cost and no findings/summary. Check this interpretation with context/delivery rather than adding a new failure enum or silently keeping a supposedly complete subset. If accepting a validated subset is desired instead, specify that different policy and how it can honestly satisfy existing status invariants before implementation. Do not add an automatic schema-repair or nested retry loop.
5. **Supervisor/researcher control policy.** Do not execute new control/delegation/tool intents from a response explicitly known incomplete. Decide how that observation enters the existing bounded model-failure/replanning policy and turn accounting. Prior completed tasks/evidence remain intact. This needs exact policy wording; it is not equivalent to fabricating malformed TaskSpec questions or marking old tasks not_run.
6. **Report policy remains delivery's.** Known output truncation must not be treated as a complete successful report merely because Markdown is readable. Alchemy should decide its REQ-004 failure mapping. Report **output truncation** and deliberate **input findings removal** are different: REQ-004 C-006 already requires partial plus limitations when findings were removed to fit input. Do not add a final-report validator or override that outcome in orchestration.

If adopted, amend ADR-002 acceptance/runtime boundaries, POL-006 plus supervisor model policy, private evidence lifecycle, verification inventory and the reader checklist. The report mapping belongs in delivery's corresponding documents. The proactive course input-token cap remains a separate context/integration gap; neither this metadata check nor a new budget.py implements it.

## 5. Offline verification methods for later authorised phases

No new product tests were written or executed by this audit. The following are concrete test plans for Test Author after Gate 1; fake responses need no provider, key or network. A fake `ainvoke` is a test double, not a live model request.

| Planned check | Offline construction | Observable assertion |
|---|---|---|
| Metadata survives until the right boundary | Fake full AIMessage-like response with unique marker and valid tool_calls; run supervisor/researcher adapters | Complete response object/attempt observation is retained and consulted before dispatch; no content-only reconstruction claims to preserve metadata |
| Compression conversion loss / capture | Same complete sidecar+Sources content, once normal-ended and once explicitly length-ended | Baseline string-only boundary cannot distinguish them; the accepted revised adapter must distinguish them before parsing and obey the chosen acceptance policy |
| Structurally damaged length output | Length-ended response with broken JSON/Sources | One deterministic category/terminal result, retained cost, no notes and no nested repair request; category precedence is specified |
| Missing/different metadata | Fixture variants for expected provider key, alternate supported key, absent key, unknown value and malformed marker | Mappings follow the documented supported-adapter table; unknown is never silently relabeled normal |
| Context retry bridge | Fake configured model emits two exceptions then a normal or length-ended response; context is the only retry owner | At most the agreed attempts, per-attempt observation exactly once, usage preserved, and only one final parse/accept decision |
| Truncated tool intent | Incomplete response contains an apparently valid ConductResearch or executable researcher tool call | No new external tool/researcher starts from that rejected response; existing task results survive; processed-turn/model retry accounting remains bounded |
| Sibling preservation | One child's compressor length-ends after two tool starts while another child succeeds | Failed child retains tool/usage evidence, sibling survives, joined order remains registration order, and notes contain only accepted findings |
| Final report length | Fake final writer returns readable Markdown with explicit length metadata | Delivery policy prevents complete success; compare separately with the existing input-findings-removal partial case |
| Budget split has one count | Budget 2, four proposals including think/failure/control; call validator twice afterward | Only admitted starts spend permits, failed starts still count, control/denial cost zero, validation never increments, and reserved-but-unstarted is not reported started |

Before any fake-node execution, patch model construction/key helpers and forbid HTTP/network entry points; do not import/run the production graph with credentials to perform this audit. Static AST inspection alone can locate the conversions and missing guards; it cannot establish provider metadata fidelity or runtime correctness. Provider/gateway fidelity eventually needs explicitly authorised evidence, not a claim inferred from these fixtures.

## 6. Review status

- Static source/doc inspection: completed.
- Existing project files modified by this audit: none.
- Budget/evidence split: advisory, not accepted or implemented.
- Response-truncation policy and gateway mapping: proposed / pending owner-reader decisions.
- Product/offline/live tests and API observations: NOT_RUN.
- Claude requests: none; no model request of any kind was made.

## 7. Follow-up: concrete boundaries after the coordinator's gateway/adapter experiments

This section records a later read-only review of existing evidence in `SA-FOLLOWUP-2026-11-15.md`, `truncation-gateway-results.json`, `truncation-langchain-results.json` and `truncation-offline-results.json`. These experiments were conducted by the coordinator, not by this audit agent. No additional API/model invocation was made here. The observations below update the earlier audit's explicitly unverified gateway path; they do not retroactively turn this audit into a live test.

### 7.1 What is now established, and what remains unknown

- The two captured school responses contain `choices[0].finish_reason = length` and `stop`, respectively. Their replay through the project-pinned ChatOpenAI adapter preserves the value in `AIMessage.response_metadata.finish_reason` and preserves reported usage.
- Eight baseline-function scenarios with fake boundaries demonstrate that the inspected source does not distinguish these markers at the tested compression/report/supervisor-tool boundaries. This is stronger than source inspection alone, but is not a full-graph outcome test or an implementation test of Proposed orchestration.
- The two gateway probes did not establish the gateway's successful **tool-call** finish marker. A whitelist containing only `stop` would reject normal tool-enabled operation if the adapter returns `tool_calls`. Add a separately tested mapping for the supported tool-enabled adapter; do not infer that metadata absence is a normal stop. Legacy/alternate provider markers are not automatically supported because another provider uses them.

### 7.2 Minimal budget/evidence split, fixed interfaces

Adopt the allocation in §2 if desired: `budget.py` contains the existing admission/capability policy; `evidence.py` contains one receipt's factual events and snapshot primitives. Preserve package entry points/signatures and every existing TaskSpec/TaskResult/RunRecord field. Specifically keep `build_task_result(spec, compression_text, *, evidence)`, `validate_task_result(output, spec, *, evidence)` and `failed_result(spec, category, message, *, evidence)` unchanged. Do not add a second receipt, reserved/spent ledger, context key, retry owner or tool-HTTP metric.

Admission may call evidence's atomic receipt primitive; evidence must not import budget. A reservation is not a recorded start. The adapter records the actual start once and records completion/failure without spending again; validators are read-only. Existing per-task ownership and safe-config rules apply to both files. No other owner's queue, model selection, context recovery or outcome is changed by this internal allocation.

### 7.3 Completion observation and wrapper placement

For an accepted research task, record one private observation per counted logical model-attempt invocation in its existing `TaskExecutionEvidence`. A minimal observation contains operation id, stage, attempt ordinal, returned/exception kind, safe raw finish marker, normalized completion state and available reported usage/completeness. These are private receipt/snapshot details, not additional TaskResult or RunRecord fields. The event is created by the node-owned wrapper; model text cannot assert it.

Use the exact verified ChatOpenAI metadata path for this supported route. For returned responses, normalize:

| Observation | State | Acceptance consequence |
|---|---|---|
| Supported stage-appropriate normal marker, including `stop`; supported `tool_calls` for tool-enabled stages after its mapping is verified | normal | May proceed to the existing argument/sidecar/result validation. Normal transport completion does not prove correct facts or a valid payload. |
| Verified marker `length` | length | Known output-cap truncation; do not accept new control/tool intent or a compression draft merely because its structure parses. |
| Missing/non-string/unrecognized/conflicting metadata, or an unsupported adapter mapping | unknown | Adapter completion evidence is unavailable; do not invent `stop`, `length`, coverage or a semantic claim about the text. Use the explicitly chosen enabled-path compatibility policy. |

An ordinary provider exception is recorded as an exception event, not misrepresented as a returned length response. Preserve usage only when actually reported. Do not let duplicate observation, result validation or repeated collector calls add the same tokens again.

Place the observation wrapper **inside any existing LangChain retry bound** if that bound's individual attempts must be observed: bind/configure the existing model, wrap the invocation/acceptance boundary, then apply the existing bounded retry behavior. An observer outside `.with_retry()` sees only its final return/exception and cannot truthfully claim it observed every hidden attempt. Do not add a second retry loop. SDK-internal transport retries are not necessarily separately observable logical Runnable attempts; retain the declared partial/reported usage semantics rather than claiming a complete HTTP count or financial bill.

Supervisor calls have no TaskSpec. They use a transient node-local operation observation for their control decision, not a fabricated task receipt or attribution of supervisor tokens to an arbitrary child task. Final report observations similarly belong to the report/delivery boundary. The single task receipt covers that task's researcher and compression attempts.

The provider receives the existing cleaned config/ambient context, never the live evidence holder. The wrapper closes over the holder outside the provider boundary and records the original response before content conversion. No new model client is needed.

### 7.4 Compression: observe, return the same response, accept at the node

The least disruptive bridge preserves context's signature and `CompressionOutcome.summary: str`:

1. The node allocates a compression operation id and retains the TaskSpec/evidence reference.
2. It supplies context's existing `model` argument with a node-owned Runnable wrapper around the same configured model. For each actual invocation by context, this wrapper records the attempt/returned metadata or exception and returns the original response unchanged, or re-raises the original exception unchanged.
3. Context retains sole ownership of its existing bounded input-token-limit recovery. A returned length response is **not** converted into a synthetic input-context-limit exception; otherwise context could incorrectly trim history to repair an output-cap problem.
4. If context raises its existing exhaustion/ordinary exception, use the already specified failed-result mapping with truthful retained cost. No sidecar parse occurs.
5. If context returns its string outcome, the caller reads the response observation associated with this operation's returned attempt, not a global last-event slot that could belong to another stage/task. A normal-ended string is parsed exactly once; a length or unknown return is rejected without parsing.

Proposed deterministic precedence for compression:

| Returned completion state | String structure | Proposed task mapping | Extra calls/parses |
|---|---|---|---|
| normal | Valid sourced findings | Existing code-derived complete/partial/failed-unanswered result | One parse, no repair retry |
| normal | Malformed sidecar/Sources | Existing failed/invalid_result | One parse, no repair retry |
| length | Valid or malformed | failed/token_limit, empty findings/summary, retained actual cost | Zero parses, zero extra retries |
| unknown | Valid or malformed | failed/runtime with safe `completion metadata unavailable/unsupported` reason, empty findings/summary, retained actual cost | Zero parses, zero extra retries |

The length-before-schema rule makes a valid-looking and a damaged truncated response deterministic. An unknown marker is not evidence of token exhaustion, so it must not be called token_limit; a valid string with missing completion evidence is not itself malformed JSON, so runtime is the more accurate compatibility-failure category. This is an enabled-path conservative proposal requiring reader review, not an assertion that every provider must always emit metadata.

### 7.5 Other stages and owner boundaries

| Stage | Proposed normal behavior | Proposed length/unknown boundary |
|---|---|---|
| Supervisor | Existing schema/tool-intent validation and common selector | Reject that attempt's new control/delegation intents before publishing its AI tool turn. Let the existing configured bounded model-attempt policy handle the rejected attempt, and send terminal failure into the existing common selector; covered/cap/stall priority is unchanged. Do not invent task ids/questions or ToolMessage ids for a rejected whole response. |
| Researcher | Existing tool admission; only admitted tools start | Reject new executable intents from the incomplete/unknown response. After the existing bounded model-attempt policy, map terminal length to task failed/token_limit and terminal unknown to failed/runtime; keep already-spent evidence and sibling results. Do not start tools from that rejected response or add a salvage-compression request without a separate approved policy. |
| Compression | One selected context recovery path, then one acceptance/parse decision | The concrete mapping above; no input trimming merely due to a returned length marker, no nested retry, and no context DTO change. |
| Final report | Existing REQ-004 acceptance remains delivery's decision | Provide the observation and request Alchemy's failure policy. Recommendation: treat known unusable output completion as report-generation failure under the existing failed/empty-report rule; do not implement or declare a new outcome here. Input findings removal remains the separate existing partial/limitations case. |

Whether a rejected supervisor/researcher return is retryable must be stated in the existing attempt policy, not implemented as an outer unbounded replanning loop. If it is retried, it consumes an existing attempt; only a normally accepted response reaches the tool-turn phase. Terminal model-response rejection does not increment a successfully processed supervisor tool-turn counter by itself. This keeps the current N=1/N=2/cap definition and error-selector pathway coherent.

### 7.6 Does this require changing approved requirements or the online contract?

**No public field or enum change is necessary for the proposal above.** The historical contract's token_limit comment already means an unrecoverable token **or** context limit; a positively identified output cap fits that category. Its runtime failure category already represents execution/compression failure, and all those structural/execution failures have empty findings/summary. `unknown` remains private observation state and is not added to FailureCategory, TaskStatus or ExitReason. Helper arguments, context outcome shape and delivery reader DTOs remain unchanged.

Treat the input-context-limit exception recovery in REQ-005 separately from output-cap termination. The new return-metadata guard is a result-acceptance boundary around that recovery, not permission to alter Tekon's oldest-first algorithm or broaden its interface. REQ-001's sourced-finding definition, question coverage and acceptance paths remain unchanged for normally accepted responses; runtime-failed output is not promoted into accepted findings. No requirement registry edit, threshold rewrite or online HackMD edit is needed to **draft** this policy.

However, fail-closed unknown handling is an enabled-path compatibility narrowing: a formerly usable provider/result lacking completion evidence would now fail. It is not safe to describe this as having zero semantic effect on other developers. Record it in the local ADR/runtime/interface checklist, retain flag-off behavior and obtain context/delivery/search reader review at the existing gate before implementation. If the team instead wants unknown metadata accepted, or wants complete/partial results salvaged from explicitly length-ended output, that needs a different explicit acceptance policy and corresponding cases; do not silently adopt it while claiming the conservative guarantee.

Changing a public context outcome, adding serialized completion fields/enums, repurposing TaskSpec budget into tokens, treating unknown as token_limit, changing REQ-004 outcome or editing the online field contract are unnecessary and outside this minimal recommendation.

### 7.7 Additional planned checks (not executed by this audit)

- Verify `stop`, tool-enabled `tool_calls`, `length`, absent, malformed and conflicting metadata mappings independently. The two current gateway fixtures establish only stop/length; keep the tool-enabled mapping's evidence limitation visible.
- Normal valid sidecar parses once; normal malformed sidecar is invalid_result; length valid/malformed yields token_limit without a parse; unknown valid/malformed yields runtime without a parse.
- Context failure/failure/normal-success observes three attempts and parses once; failure/failure/length-success observes three and parses zero times; all failures parse zero times. No extra schema or output-length retry is inserted.
- Per-attempt observations remain isolated by operation/task, preserve reported cost on rejection, never reach provider config and never cause double accounting when helpers are called again.
- Bounded supervisor/researcher retry tests show no tools start from rejected responses and terminal errors use the agreed selector/task-failure path. Existing successful tasks and joined siblings remain intact.
- Delivery separately verifies length-ended report handling versus deliberate input finding omission; Centay's local tests do not assert ownership of the final outcome.

All proposed-policy behavior remains NOT_RUN until implementation and authorised testing. The coordinator's earlier gateway, adapter and fake-baseline experiment results remain exactly the narrower evidence described in their original report.
