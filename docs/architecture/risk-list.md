# Risk List

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
- **Mitigation:** the malformed-block rule keeps an unclaimed `ToolMessage` block in the protected region instead of removing it (ADR-005 §3(a)); TC-003 covers a malformed trailing block; the orphan monitor is computed from the same helpers.
- **Re-evaluation condition:** REQ-001 lands a task specification in `researcher_messages`, or `utils.py` changes how native web-search results are appended. Either trigger reopens the ADD round for how the protected region is located (pass it explicitly from the node instead of inferring it).

## RISK-003 — Some providers may report token limits in ways pattern matching cannot see

- **Module:** context
- **Source:** REQ-005 C-003; ADR-005 §3(c); POL-001
- **Assumption:** `utils.is_token_limit_exceeded` plus the wrapper's cross-provider retry recognise token-limit errors for every provider the project supports (`openai`, `anthropic`, `gemini`/`google`, and Bedrock-routed models).
- **Why it may fail:** the checkers match exception class names and message keywords (`utils.py` L703-785). A provider that returns a 413, a GraphQL-truncation detail, or a local Ollama server message is not matched, so the wrapper reports "not a token limit", POL-003 re-raises, and the task fails through REQ-002 instead of recovering.
- **Severity:** Medium — recovery is lost, but the failure is visible and is not a silent data loss.
- **Mitigation:** the wrapper also tries all provider patterns when the exception class disagrees with the model prefix, which covers the reported C-003 case; no silent conversion to a summary occurs.
- **Re-evaluation condition:** any live run or user report shows a provider token-limit error classified as a non-token error. Then classification should move from message patterns to a provider-declared error code, which is a widening of REQ-005's scope and needs a requirement change.

## RISK-004 — REQ-001's task-result type may not accept a `token_limit` category

- **Module:** context
- **Source:** REQ-005 C-004; ADR-005 §5; `structural-constraints.md` §6
- **Assumption:** the REQ-001 task result has a status, a category and a reason, and the category enumeration includes `token_limit` (or can be extended by its owner).
- **Why it may fail:** REQ-005 `depends_on` REQ-001, and REQ-001 is owned by another member and is still in design. If REQ-001 lands a closed enumeration without `token_limit`, or with a different failure vocabulary, the node cannot record the mandated outcome and C-004 cannot be met as written.
- **Severity:** High — C-004 is a must-have criterion of a safety-relevant requirement.
- **Mitigation:** ADR-005 deliberately defines no second result type and records the shared-contract approval as a Gate 1 condition; the node's behaviour is isolated in one place so the mapping can change without touching `plan_trim`.
- **Re-evaluation condition:** REQ-001's ADR is accepted. The context owner must then confirm the category name and the field layout, and update ADR-005 §5 and TC-006 if they differ. If they cannot be reconciled, escalate to SA Review rather than inventing a parallel type.

## RISK-005 — Three attempts may be too few once turns are the unit

- **Module:** context
- **Source:** REQ-005 C-004; POL-001, POL-002; ADR-005 §9 step 5
- **Assumption:** removing one turn per attempt and retrying at most three times is enough, matching the baseline's `max_attempts = 3` (`deep_researcher.py` L541-542).
- **Why it may fail:** each attempt costs a provider round-trip, and a history with six turns needs up to five removals. With one removal per attempt the loop exhausts the budget and returns `failed` / `token_limit` although a reducible history remained — an avoidable failure that still looks correct to C-004.
- **Severity:** Medium — no invariant is violated, but research is lost that the design could have saved.
- **Mitigation:** `max_removals_per_attempt` is a parameter defaulting to 1, and TC-001 uses a model that fails until two turns are gone, which forces the loop to prove it can reach that state.
- **Re-evaluation condition:** a test or live run shows `TokenLimitExceeded` while `plan_trim` would still return a `TrimPlan`. Then raise `max_removals_per_attempt` or make removal geometric (halve the removable turns), which is an ADR amendment of a still-*Proposed* ADR, not a new ADR.

## RISK-006 — The behaviour flag may hide the improvement

- **Module:** context
- **Source:** REQ-005; `structural-constraints.md` §8; ADR-005 §3 "Behaviour switch", §9 step 12
- **Assumption:** `context_trimming = False` by default keeps baseline behaviour comparable, and the flipping PR arrives once REQ-005 is `verified`.
- **Why it may fail:** if the flip is forgotten, the requirement is `verified` while production runs the defective path — the worst combination, since the evidence would describe code that never executes. Conversely, flipping early makes the A/B comparison meaningless.
- **Severity:** High — the shipped behaviour would contradict the requirement's `verified` status.
- **Mitigation:** TC-009 pins the default; the flip is a separate, explicitly numbered step (ADR-005 §9 step 12) with its own review; Definition of Done item 10 keeps the status at `verified` only after the flip.
- **Re-evaluation condition:** any PR that changes the default without REQ-005 being `verified`, or any release that contains the flag still `False` after the requirement closed. The second case is a defect for `docs/bug-diary.md`, not a new risk.

## RISK-007 — Fixing the consumer default may overlap another module's scope

- **Module:** context
- **Source:** REQ-005 C-004; ADR-005 §2 defect 4, §9 step 10; INV-002
- **Assumption:** the `supervisor_tools` default at `deep_researcher.py` L310 can be narrowed to a non-silent no-result message without taking over the handling of researcher exceptions, which REQ-002 (orchestration) owns.
- **Why it may fail:** L310 sits in the same `try/except` block as the researcher failure branch (L332-342). A broad rewrite of the default can accidentally change what happens when the subgraph raises, and REQ-002 or REQ-004 may edit the same lines in the same integration cycle, producing a merge conflict or two competing policies for one message.
- **Severity:** Medium — a scope overlap, not a data-loss path; the final report content is affected only when the key is already missing.
- **Mitigation:** ADR-005 §9 step 10 fixes the wording of the default only and states explicitly that exception handling is out of scope; the success path is required to stay byte-identical; TC-010 asserts both branches.
- **Re-evaluation condition:** review rejects the L310 change as out of scope, or REQ-002's ADR assigns a different behaviour to a missing `compressed_research`. Then withdraw step 10 and keep only the L582-585 removal, and record the resulting gap as a note for REQ-002's owner.

## Retired or Accepted Risks

| Risk ID | Outcome | Reference |
|---|---|---|
| — | none yet | — |
