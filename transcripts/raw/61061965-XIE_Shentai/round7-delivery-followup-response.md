# Reconciliation of G1–G4 (delivery perspective)

As before, this is an AI review, not a teammate review or gate. Nothing below passed at runtime; no project test was executed.

## G1 — Delivery→orchestration adapter / publish order — **RESOLVED**
The new text defines the port concretely: `accepted: list[RegisteredDelegation(call_id, spec)]`, optional states limited to `accepted`/rejected (rejections stay in the node), injection of the existing validator, failed-result factory and renderer as callables, and `JoinedTurn(task_results, tool_messages, raw_notes)`, with the constraint that every accepted call appears exactly once in the order of `accepted`, "independent of completion order," and every started child has joined before return. This answers what I asked for: the node can build the per-task evidence map without orchestration internals. My "publish order = original call order" guard is now stated, and the accompanying ORC-044 (queue + failure ordering) is the concrete case that ORC-040 lacked.

**Retracted assumption:** I had implied that ordering was only implicitly covered and that three children might be started at once. A concurrency-one queue is meaningfully different, and concurrency-two ordering coverage is the correct way to test completion-order robustness. I treat that part as an error I made, not a gap in the design.

## G2 — Where unanswered questions come from — **RESOLVED (my premise was wrong)**
`TaskResult.must_answer` plus `findings[*].answers` already provide the per-task question data; `RunRecord.task_results` therefore provides the global data. `RunRecord.unanswered_questions()` using the same question-identity calculation as coverage, with first-occurrence order, and `TaskResult.unanswered()` for per-task limitations, avoid any float/task-count derivation. My proposed "additive sentence in memory §5" is unnecessary.

**Retracted:** my claim that no per-question hand-off exists because `RunRecord` "has only verdicts." The contract text supports global unresolved questions and per-task local unresolved questions coexisting: in the stated example T2 makes Q9/Q10 globally 9/10, while T3's failure with local `[Q1]` still yields a partial run even if the coverage check would say "covered." I accept that distinction; it matches REQ-004's "every task result is complete."

**Source-supported residual note (not a new gap):** the text states the issue canonicalization "same as coverage" without naming the ADR-002 §3.1 operation. If the Test Author implements the aliasing from memory, ORC-045's expected order could differ. This is a small comment-level clarification, not a contract I can support as missing.

## G3 — Missing `compressed_research` with a valid typed result — **RESOLVED**
The clauses cover both directions: the enabled producer returns `compressed_research`, `raw_notes` and `task_result` together; the consumer validates the typed result against spec and retained receipt and "never trusts the child's auxiliary string"; a raw mapping that omits the string but contains a result consistent with the evidence is rendered purely from the typed result, with no placeholder and no second result; a missing or invalid `TaskResult` maps to `failed/invalid_result`; an output-schema exception becomes an output-contract failure rather than fabricated research. That covers the adversarial case I designed earlier (typed failure plus sidecar without the string), and ORC-046 assigns the 3-attempt, parse-once, canonical-output case. My ORC-023/ORC-024 extension is no longer needed in the form I proposed.

**Correction accepted:** the baseline consumer does not propagate ordinary compression exceptions; it continuously retries (`deep_researcher.py:565-574`). My "placeholder string and exception" pairing overlapped two different paths. I retract the framing, though my underlying point — placeholder/raw prose must never become a report finding — remains addressed by separating notes rendering from the ToolMessages.

## G4 — Generating diagnostics once the cap is already reached — **PARTIALLY RESOLVED**
The new text now says control/rejection feedback for held raw calls is included in the same terminal tool-turn update even when that update exits, and that a supervisor entry with no unprocessed response invents no feedback and makes no request just to emit diagnostics. That closes the conflict I raised: an entry with no turn starts no supervisor request and emits nothing, while a terminal turn emits exactly once.

**What is not covered:** an entry that *does* have a registered but unanswered raw call which was held from a prior turn but never dispatched. The text covers the "no unprocessed response" case and the "same terminal update" case, but not "unprocessed response present, no dispatch allowed." ORC-042 covers cap-held *accepted* delegations becoming `not_run`; it does not cover a *rejected* receipt whose tool response was deferred. I keep only this narrow residual, not the broader gap.

**Retracted:** my claim that the node lacked any statement of diagnostic-emission ownership across a resume. The clause now addresses that; only the deferred-rejection subcase is unnamed.

## Net position
G1 resolved, G2 resolved (with my earlier premise retracted), G3 resolved, G4 narrowed to one unnamed subcase. R-01/R-03/R-09 and off/on remain declared reader decisions; none are newly contradicted here.
