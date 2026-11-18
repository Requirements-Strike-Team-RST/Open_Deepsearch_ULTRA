# AI review disposition — orchestration SA

These are AI coordinator decisions on a proposed local draft, not student intervention, peer approval, runtime verification or Gate 1.

| Review item | Disposition in the final proposed draft |
|---|---|
| OpenCode F1: cap bound/test specificity | Clarified existing semantics: N=1/N=2 all-delegation fixtures dispatch exactly 1/2 turns; no supervisor request N+1. The core selector order was retained. |
| F2: raw compression body | Adopted stronger boundary: discard free-text body/sidecar from reader-facing summary and compressed_research; render complete/partial validated findings/sources. Failed tasks never enter notes. |
| F3: budget comparability | Explicit consequence: enabled max_react_tool_calls is an actual invocation maximum, tighter than baseline turns times batch size; record this in live comparisons. |
| F4: incomplete token usage | Add proposed TaskCost.usage_complete=False; exact retained started-tool count is distinct from partial reported token totals. Do not reject useful partial totals or invent complete billing evidence. |
| F5: unknown/mixed tools | Unknown/non-executable names receive diagnostics and cost zero. Completion is a non-executed control; valid mixed work runs within admission/cap bounds. |
| F6/F7: hunk and flags | Centay owns parse/render adapter before delivery. Off/on creates no orchestration run fields and no RunRecord; context/delivery failure policy remains pending. |
| F8: schema burden | Added model-compliance cost/reopen condition for persistent invalid delegation output. No measured rejection rate is claimed. |
| F9: deterministic authority wording | Already corrected during review: model-proposed findings affect computed results after validation; model self-reported status/exit/provenance has no authority. |
| F10: float threshold | Threshold is Fraction(str(value)); decimal 0.3/0.8 boundaries appear in the planned cases. No hidden rounding of a different configured value is proposed. |
| Codex source audit: helper drift | Unified build_task_result(spec, compression_text, *, evidence). |
| Codex source audit: invalid IDs | Invalid-ID transport turn is rejected before task registration, without fabricated ToolMessage IDs; ORC-043. |
| Codex source audit: two-level reducers | Final override applies inside SupervisorState. Compiled output is a plain list appended once to AgentState channels cleared by the brief boundary. ORC-040 covers this actual propagation. |
| Codex source audit: ambient config | Clean bound and ambient config; set_config_context plus asyncio.create_task(context=...) executes the entire model coroutine in the clean context. Fake model must inspect actual config, not only prompt text. |
| Codex source audit: private lifecycle | Keep default per-invocation compile mode; public fields reset in main, private channels start fresh per child invocation. Same-call resume preserves checkpoints. Official LangGraph guide consulted; runtime case remains planned. |

Round 4 was a bounded no-tool static reading of the current supplied ADR. OpenCode reported no remaining contradiction in that text and explicitly disclaimed runtime PASS, human approval and Gate 1. It did not inspect other documents in that final round; the independent static document audit checks their scope and references.

## Student-requested simulated peer challenge (rounds5–8)

- Delivery G1: adopted a precise RegisteredDelegation/JoinedTurn port, injected contract callbacks, original publication order independent of completion order and no unjoined handles; ORC044.
- Delivery G2: premise retracted by reviewer. TaskResult already carries must_answer/findings.answers. Added a computed RunRecord.unanswered_questions convenience reader without a new stored field; ORC045 fixes the concrete9/10 example, not a task-count ratio.
- Delivery G3: adopted producer output completeness and consumer canonical rendering from a valid typed result even when an auxiliary legacy string is missing. No placeholder, second result or schema-repair LLM call.
- Delivery G4: made the remaining cap-entry deferred-diagnostic case explicit for both entry paths. Stable code-owned response IDs and receipt feedback marks publish with feedback; no model/dispatch is started to flush it. ORC043 covers replay.
- Context G1: retained as peer-owned design-seam risk, not a demonstrated recovery.py bug. ADR002§6 and R10 explicitly require instruction/current-list indices to be recomputed after trimming; the peer draft needs reader agreement.
- Context G2/G4/G5: reviewer retracted incorrect max-two-calls, missing-evidence-parameter and default-threshold claims. Caller-retained evidence and exact configured decimal conversion remain. No one-decimal rounding or unnecessary evidence argument was added to context.
- Context G3: parse once after recovery success; no nested retry. Shared consumer-hunk ownership and off/on policy remain declared decisions. An unchanged incomplete integration is not asserted safe.

The direct arithmetic record confirms9/10 globally, with Q10 unresolved and failed T3 locally unresolvedQ1. It imports no project code and is not a passing functional test. The follow-up model assessments are preserved unchanged; the final deferred-diagnostic wording was added afterward to close the one narrow delivery residual. No new runtime outcome or teammate approval is inferred.
