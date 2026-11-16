# ADR-005: Token-limit recovery in compression keeps the newest research turn

- **Status:** Proposed
- **Date:** 2026-11-13
- **Module:** context
- **Owner:** BroZhai
- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-005 (`invariant`, `safety_relevant: true`) | C-001, M-001 `latest_turn_preservation_rate == 1.0` | The decision of what to discard is made by deterministic code, not by the model (`structural-constraints.md` §7). It defines a new boundary between the graph node and the `context` module. |
| REQ-005 | C-002, M-002 `orphan_tool_message_count == 0` | The trimming unit is a *whole turn* (`AIMessage` + its `ToolMessage`s). This forces a message-shape contract on the module rather than "remove N messages". |
| REQ-005 | C-003 | The token-limit classification must be bound to the model that was called (`compression_model`). This puts classification in one named component instead of a call-site argument that can drift. |
| REQ-005 | C-004 | Fail-closed: an unreducible history produces a failed task of category `token_limit` instead of text. This ties the module to the REQ-001 task-result contract and to the REQ-004 run outcome. |
| REQ-005 `out_of_scope` | — | The prompt wording, model selection, token-limit configuration and the graph topology must not change. The decision is limited to the token-limit branch of `compress_research`. |
| INV-001 | fallback chain | The invariant's fallback ("remove whole turns from the oldest end, then fail") is implemented by exactly one component. |
| REQ-001 (dependency) | task result carries status and reason | The category `token_limit` must travel inside the REQ-001 task result, so the context module cannot invent its own result type. |

## 2. Context

### Baseline behaviour

`compress_research` (`src/open_deep_research/deep_researcher.py` L511-585) is the last node of the researcher subgraph. Defects 1-3 are in the node; defect 4 is at its consumer, `supervisor_tools`:

1. **Wrong direction of removal.** On a token-limit error it calls `remove_up_to_last_ai_message` (L569-571). That helper (`src/open_deep_research/utils.py` L848-866) returns `messages[:i]` for the last index `i` holding an `AIMessage`, so it drops the newest AI turn, every `ToolMessage` after it, and the compression instruction appended at L538. The newest research is lost; the run continues.
2. **Misleading documentation.** The call-site comment says older messages are removed, while the helper docstring says recent context is removed. Two readings of the same function exist in the repository.
3. **Wrong model for classification.** The error is classified with `configurable.research_model` (L569) although the call used `configurable.compression_model` (L528). `utils.is_token_limit_exceeded` (L665-701) picks a provider-specific checker from the model-name prefix. With an `openai:*` research model and an Anthropic compression model, an Anthropic `BadRequestError` is handed to `_check_openai_token_limit` (L703-734), which requires an OpenAI exception class and returns `False`; `_check_anthropic_token_limit` (L736-757) is never consulted. The error is therefore unrecognised, the same request is retried unchanged, and after three attempts the node returns the string `"Error synthesizing research report: Maximum retries exceeded"` (L582-585) as the compressed summary.

4. **A second placeholder at the consumer.** Downstream, `supervisor_tools` (`deep_researcher.py` L298-330) reads the compressed summary as normal research notes, so the placeholder reaches the final report as if it were a finding. Independently of the node, `supervisor_tools` passes the same literal as a default to `dict.get` when it builds the `ConductResearch` tool result: `observation.get("compressed_research", "Error synthesizing research report: Maximum retries exceeded")` (L310). This fires whenever the researcher subgraph returns without the `compressed_research` key — for example when a node raises, or when the output state omits the field — and it converts a missing result into note text with no error. The two literals are duplicate definitions of the same fallback. REQ-005's `in_scope` covers "Task result when the limit cannot be met", so the new path must never reach this default. It does not change that default; instead the node always returns `compressed_research` and carries the failure in the declared `research_outcome` field, so the consumer default stays part of the untouched baseline (see the behaviour switch below).

### Forces and constraints

- The three graphs and their nodes must not change (`structural-constraints.md` §2): the node `compress_research` stays, only its body becomes thin.
- Architectural logic goes to the owner's extension module (`structural-constraints.md` §8), which the blueprint §4 names `src/open_deep_research/context/` for REQ-005.
- Dependency direction is `deep_researcher.py` → extension module → shared modules; the module may not import `deep_researcher.py` (`structural-constraints.md` §5).
- A safety-relevant requirement needs deterministic code and a test that fails on violation (`structural-constraints.md` §7).
- Offline tests use fake models and no network (`verification-constraints.md` §3); a test needs a seam that does not require a provider.
- REQ-005 depends on REQ-001. Until REQ-001 lands, the failure must still be representable; the module therefore raises a typed error and the node decides how to record it.
- `utils.is_token_limit_exceeded` is also used by `final_report_generation` (L334 uses it with `or True`, REQ-004's area). Its behaviour must not change for other callers.

## 3. Decision

Implement **option B** of EVAL-001: a dedicated `context` module with a pure trimming policy, a single classification entry point and an explicit recovery loop, called from a thin `compress_research`.

### Module layout

```
src/open_deep_research/context/
    __init__.py          # public exports only
    messages.py          # ResearchTurn, TurnLayout, segment_turns()
    trimming.py          # plan_trim(), TrimPlan
    classification.py    # classify_token_limit()
    recovery.py          # compress_with_recovery(), CompressionOutcome, TokenLimitExceeded
```

### (a) Unit of removal — a research turn

A **research turn** is one `AIMessage` together with the `ToolMessage`s that answer its tool calls. Everything before the first `AIMessage` is the **preamble** (the research topic `HumanMessage` written by `supervisor_tools` at L298). The compression instruction is appended by the node at L538 and is the **last message** of the list; it is not a turn.

Pairing rule: a `ToolMessage` belongs to a turn when its `tool_call_id` appears in that turn's `AIMessage.tool_calls[*]["id"]`. Pairing is by identifier, not by position, because an `AIMessage` may issue several calls and only some of their results may be present; positional grouping would attach an answer to a turn that did not request it and would break the C-002 assertion.

Invariants enforced by construction:

- A `ToolMessage` is never separated from the `AIMessage` that requested it, because removal happens on whole turns.
- A `ToolMessage` whose `tool_call_id` matches no `AIMessage` is a malformed history. It belongs to no turn, is treated as part of the protected region and is never removed. The history is not modified to repair it; that is outside REQ-005.

### (b) Protected region

The protected region is computed from message types, never from the model's text:

1. the preamble (position 0, the research topic),
2. the compression instruction (the last message, produced by the node at L538; its index is passed in so it cannot be confused with the topic),
3. the newest AI turn and its tool results.

`plan_trim` may remove only turns strictly between the preamble and the newest turn, and only whole turns, starting from the oldest. The newest turn is protected and is never a candidate, which is what C-001 and M-001 assert.

Rebuilding the list keeps the **original message order**: preamble first, then the surviving turns, then the instruction last. The instruction is never hoisted in front of the turns, because the model must read the research record before the instruction that asks it to compress that record, and because a hoisted instruction would also invalidate the `instruction_index` the caller passed in.

### (c) Classification bound to the invoked model

`classification.classify_token_limit(exc, model_name)` is the only entry point used by the recovery loop, and the loop passes `configurable.compression_model`. It delegates to the existing `utils.is_token_limit_exceeded` and returns its result unchanged: no provider is retried or second-guessed when the named provider's checker declines the exception.

Passing `compression_model` is sufficient for C-003. In the baseline the defect is that `research_model` was passed (L569) although the call used `compression_model` (L528); correcting the argument is what makes the Anthropic `BadRequestError` reach `_check_anthropic_token_limit`.

An earlier draft of this ADR added a fallback that tried every other provider when the named one declined. It was dropped: `_check_openai_token_limit` (`utils.py` L726-732) accepts any exception carrying `type == "invalid_request_error"` without checking which provider raised it, so a fallback would let that loose rule classify another provider's exception as a token limit. A second draft of the fallback in step 4 called `is_token_limit_exceeded(exc, "")` for the same purpose and had the same defect, since an empty model name makes `utils` check all three providers.

`utils.is_token_limit_exceeded` keeps its current signature and behaviour for `final_report_generation`; the new entry point is additive and wraps it. `final_report_generation` does not adopt the wrapper in this ADR, because that code is REQ-004's.

### (d) When the history can no longer be reduced

The recovery loop stops when `plan_trim` returns `None`, i.e. no removable turn is left. It then raises `TokenLimitExceeded(attempts, removed_turn_indices, last_exception)`; it never returns a string as a summary. The loop's budget is derived from the history rather than fixed, so "nothing removable" is the only condition that ends it in the token-limit case (ADR-005 step 5).

The node does not swallow that exception silently and does not return a placeholder. It converts it into the declared output field `ResearcherOutputState.research_outcome` (a `ResearchOutcome` with status `failed` and category `token_limit`) and returns it together with `compressed_research` and `raw_notes`. `supervisor_tools` reads the field and reports the task as failed instead of presenting note text.

The field is required because `ResearcherOutputState` is a Pydantic model (`state.py` L92-96) that keeps only declared fields: any other key returned by the node is filtered out before the caller sees it, so a task result returned under an undeclared name would silently disappear. The declared field also keeps the failure local to the researcher that produced it: `supervisor_tools` gathers all parallel researchers with `asyncio.gather` (L305), so letting the exception escape the subgraph would discard every other researcher's result. Step 11 below declares the field; step 8 returns it.

The placeholder literal at L582-585 is removed from the new path; the consumer default at L310 is left unchanged (see the behaviour switch below).

### Behaviour switch

`Configuration.context_trimming: bool = False` (baseline default) selects the new path. While `False`, `compress_research` keeps the baseline code path byte-for-byte, **including the placeholder at L582-585 and the untouched `supervisor_tools` default at L310**. While `True`, the new path is used and neither site can emit the placeholder: the node returns the declared `research_outcome` field instead of a summary-on-failure, and the consumer default is never reached for a task that ended `failed`.

`supervisor_tools` (L310) is **not** modified by this ADR. Gating it on `context_trimming` would make one node read another node's configuration and would change the baseline consumer path, which defeats the purpose of a switch that exists precisely to keep the pre-fix behaviour available for A/B comparison. The remaining baseline default is recorded as RISK-007 with the condition that reopens it.

The PR that marks REQ-005 `verified` flips the default (`structural-constraints.md` §8).

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — turn-aware trimming written directly inside `compress_research`, with a rewritten helper in `utils.py` | Smallest diff, but it puts architectural logic in a graph node, against `structural-constraints.md` §2 and §8, and leaves the protected region testable only end-to-end through the node. The second requirement that touches compression (REQ-001 task results) would force a second move. |
| C — estimate the token budget before the call and trim proactively | Solves a different problem (avoiding the failed call instead of recovering correctly after it), needs a provider-neutral tokenizer and therefore a new dependency, and contradicts REQ-005's `out_of_scope` boundary around token-limit configuration. The reactive path it keeps is exactly this decision, so it is a later extension on top of ADR-005, not an alternative. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `context/messages.py` | Split a message list into preamble, turns and instruction, pairing tool results to the AI message that requested them | `segment_turns(messages: list[MessageLikeRepresentation], *, instruction_index: int \| None = None) -> TurnLayout`   `TurnLayout(preamble: list[Message], turns: list[ResearchTurn], instruction: Message \| None)`   `ResearchTurn(index: int, ai_message: AIMessage, tool_messages: list[ToolMessage])` | `context/trimming.py`, `context/recovery.py` |
| `context/trimming.py` | Pure, deterministic decision about which turns to drop | `plan_trim(messages: list[MessageLikeRepresentation], *, instruction_index: int \| None = None, max_removals: int = 1) -> TrimPlan \| None`   `TrimPlan(messages: list[Message], removed_turn_indices: tuple[int, ...])` | `context/recovery.py`, tests |
| `context/classification.py` | Decide once whether an exception is a token-limit error for the invoked model | `classify_token_limit(exc: BaseException, model_name: str) -> bool` | `context/recovery.py` |
| `context/recovery.py` | Run the retry loop, apply the trim plan, prepare the failed outcome | `async def compress_with_recovery(*, model: Runnable, system_prompt: str, messages: list[MessageLikeRepresentation], instruction: HumanMessage, model_name: str, max_attempts: int \| None = None, max_removals_per_attempt: int = 1) -> CompressionOutcome`   `CompressionOutcome(summary: str, raw_notes: str, removed_turn_indices: tuple[int, ...])`   `class TokenLimitExceeded(Exception): attempts, removed_turn_indices, last_exception` | `compress_research` in `deep_researcher.py` |
| `compress_research` node (thin) | Read configuration, call the module, map the outcome to state | existing `async def compress_research(state: ResearcherState, config: RunnableConfig)` signature unchanged; returns `compressed_research`, `raw_notes` and, on failure only, `research_outcome` | LangGraph (`researcher_builder`) |
| `ResearcherOutputState.research_outcome` | Carry a failed task result out of the researcher subgraph | `research_outcome: ResearchOutcome \| None = None` (declared in `state.py`) | read by `supervisor_tools` in `deep_researcher.py` |

**Error and result contract.**

- `TokenLimitExceeded` is raised only when the limit still applies after trimming or when nothing is removable.
- The node catches `TokenLimitExceeded` and returns `research_outcome` (REQ-001 type: `status="failed"`, `category="token_limit"`, `reason` listing the attempts and the removed turn indices) alongside `compressed_research` and `raw_notes`. It never returns placeholder text as a summary.
- The node does not re-raise. `supervisor_tools` gathers parallel researchers with `asyncio.gather` (L305), and a raised exception there discards every other researcher's result.
- Non-token exceptions are retried on the new path and, when the budget is spent, end the same way: `failed` with a category owned by REQ-001, not `token_limit`.

**Shared contracts changed (`structural-constraints.md` §6):** the REQ-001 task-result type (owner: centay, orchestration) must be approved by centay and BroZhai before implementation. `ResearcherOutputState` gains one declared field (details in `memory-design.md` §5), which is also read by `supervisor_tools`; that change needs centay's approval for the same reason.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** `ResearcherOutputState` gains one declared field, `research_outcome` (step 11), which carries a failed task result out of the researcher subgraph. `ResearcherState` is unchanged: it already carries `research_topic` (L88) and `researcher_messages` (L86), which are sufficient. No reducer change. The field, its writer and its reader are recorded in `memory-design.md` §5.
- **Runtime policies:** three policies for `runtime-policy-catalog.md` §2 — POL-001 to POL-003:
  - *token-limit on compression, reducible history* → trim the oldest turn and retry, until the removable turns are exhausted;
  - *token-limit on compression, unreducible history* → stop, raise `TokenLimitExceeded`, task result `failed` / `token_limit`;
  - *non-token exception on compression* → retry the unchanged request on the new path, as the baseline does, until the attempt budget is spent; then end with `failed`, do not re-raise. Re-raising would escape `compress_research` into `asyncio.gather` (L305) and discard every parallel researcher's result, and would also drop the retry that transient 429/5xx errors need.
- **Invariants:** INV-001 (details in `invariants.md`).
- **Deterministic boundary:** `plan_trim` decides which turns to remove, and `classify_token_limit` decides whether the exception is a token-limit error; both are pure functions with no model call. The model only produces the compressed text and the provider error that is passed in as input. The decision to end the task as `failed` rather than to summarise is made by code, not by prompt text.

## 7. Verification

| Criterion | How it is verified | Test |
|---|---|---|
| C-001 / M-001 `latest_turn_preservation_rate == 1.0` | `plan_trim` is called with a fake history of preamble + three AI turns with tool results + instruction. The result must remove exactly the two oldest turns, keep the preamble, the newest turn with its tool results and the instruction; the newest turn index must never appear in `removed_turn_indices`. A second case runs `compress_with_recovery` with a fake model that raises a token-limit error until two turns are gone. | `test/offline/test_context_compaction.py::test_oldest_turns_removed_first` |
| C-002 / M-002 `orphan_tool_message_count == 0` | Property-style over generated histories: every `ToolMessage` in the trimmed list must follow an `AIMessage` whose `tool_calls` contain its `tool_call_id`; count of orphans must be 0. | `test/offline/test_context_compaction.py::test_no_orphan_tool_messages` |
| C-003 | Fake Anthropic `BadRequestError` ("prompt is too long") with `compression_model="anthropic:..."` and `research_model="openai:..."`: `classify_token_limit(exc, compression_model)` is `True`, the loop trims before the second call, and a fake that fails the same request twice is never retried unchanged. | `test/offline/test_context_compaction.py::test_classification_uses_compression_model` |
| C-004 | History of preamble + one AI turn + instruction, with a model that always raises a token-limit error: `compress_with_recovery` raises `TokenLimitExceeded`, the node returns `research_outcome` with status `failed` and category `token_limit`, and no summary contains the placeholder string. | `test/offline/test_context_compaction.py::test_unreducible_history_ends_failed` |
| C-004 through the subgraph output | The node's return value is validated against `ResearcherOutputState`: `research_outcome` is present and non-`None` on the failure path, and `None` on the success path. This is the case that would have caught the field being undeclared and silently filtered out. | `test/offline/test_context_compaction.py::test_outcome_survives_output_state` |
| C-004 at the consumer (defect 4) | `supervisor_tools` is given a researcher output carrying a failed `research_outcome`: the resulting `ToolMessage` must state that the task failed with `token_limit` and must not equal the placeholder literal. The `supervisor_tools` code itself is unchanged, so this is a behavioural test of the new output contract, not of a modified consumer. | `test/offline/test_context_compaction.py::test_no_placeholder_at_consumer` |
| Attempt budget (C-004 boundary) | History with N removable turns where the model rejects every request: the loop removes turns one per attempt and only fails once nothing is removable, so `removed_turn_indices` has N entries, not `max_attempts - 1`. | `test/offline/test_context_compaction.py::test_budget_covers_all_removable_turns` |
| Non-token error (POL-003) | Model raises a transient 429-style exception twice and then succeeds: the loop retries the unchanged request and returns a normal outcome. A model that raises a non-token error for every attempt ends `failed` and does not raise out of the node. | `test/offline/test_context_compaction.py::test_non_token_errors_are_retried` |
| TC-007 / INV-001 | The invariant clauses asserted directly, union of the cases above. | `test/offline/test_context_compaction.py::test_newest_context_never_dropped` |
| TC-008 (REQ-005 M-002 monitor) | `orphan_tool_message_count` computed over the trimmed history is 0 in every generated case. | `test/offline/test_context_compaction.py::test_no_orphan_tool_messages` |
| TC-009 (flag default) | `Configuration()` and `Configuration(context_trimming=False)` both select the baseline branch; `True` selects the new path. | `test/offline/test_context_compaction.py::test_flag_defaults_to_baseline` |
| INV-001 | The union of the acceptance-criterion cases above fails if any invariant clause is broken; the `latest_turn_preservation_rate` and `orphan_tool_message_count` monitors are computed from the same helpers. | `test/offline/test_context_compaction.py` |
| Thin node (`structural-constraints.md` §2) | Static check that `compress_research` contains no trimming or classification logic, only configuration reading, one module call and state mapping. | Reviewed in the PR diff; recorded in `docs/review-memo.md` |
| Regression | Full offline suite, including `test/offline/test_contracts.py` if the REQ-001 task-result type changes. | `uv run pytest test/offline` |

The module's case table (TC-001 to TC-012, with input and expected result per case) is in `verification-constraints.md` §7. The cases listed there and the tests named in the table above are the ones this ADR is verified by; no other test is required for REQ-005.

## 8. Consequences

**Positive**

- The newest research survives every token-limit retry (C-001), and the removal unit makes orphan tool messages structurally impossible (C-002).
- The misclassification defect disappears because classification is bound once to `compression_model` (C-003).
- An unreducible history ends as an explicit `failed` / `token_limit` task instead of a placeholder that reads as a finding (C-004), which removes a false-`complete` route for REQ-004.
- `plan_trim` and `classify_token_limit` are pure functions, so all acceptance criteria run offline in CI without tokens or network.
- The direction of trimming is now documented once, in one place, ending the comment/docstring contradiction in `utils.py`.

**Negative**

- One new interface and five files instead of a two-line fix; reviewers must check the module boundary.
- The module depends on REQ-001's task-result type for the failure path; until that type is merged, the failure handling cannot be completed end-to-end.
- `utils.is_token_limit_exceeded` remains with two callers in different areas (`final_report_generation` and, through the wrapper, compression). This is deliberate to avoid touching REQ-004, but it is a shared function that two modules read.

**Neutral**

- The graph topology and prompts are unchanged, and the behaviour switch defaults to the baseline.
- `state.py` changes in exactly one place: `ResearcherOutputState` gains the declared `research_outcome` field. `ResearcherState` and every reducer are untouched.
- The two baseline placeholder sites (L583 in the node, L310 at the consumer) are retained behind the flag. Removing them is deferred to the PR that flips the flag, because removing them now would break the byte-for-byte baseline the flag exists to preserve.
- `remove_up_to_last_ai_message` has no remaining caller on the new path. It is kept with a corrected docstring and a deprecation note rather than deleted, because deletion of a public helper is a separate change (`structural-constraints.md` §5, "Extend, never replace").

**Effect on other modules**

- *orchestration* (REQ-001): must accept the `failed` / `token_limit` result; shared-contract approval required.
- *delivery* (REQ-004): gains a clean failure signal, so an outcome of `partial` or `failed` can be derived without parsing text.
- *evaluation*: unchanged; the compression prompt is untouched, so no prompt version bump.

**Risks and alternatives:** the risks this decision carries are RISK-001 to RISK-007 in `docs/architecture/risk-list.md`, with RISK-007 now covering the retained `supervisor_tools` default rather than a change to it; the rejected options and their re-evaluation conditions are OPL-001 and OPL-002 in `docs/architecture/option-ledger.md`.

## 9. Implementation Steps

Ordered steps for the coding agent. Each step names the files it changes and the acceptance criterion it serves.

| Steps | Purpose |
|---|---|
| 1–7 | New `context` module code (package, segmentation, trimming, classification, recovery, raw notes, docstrings) |
| 8 | Make `compress_research` a thin node that calls the module and carries the failure in `research_outcome` |
| 9 | Add the `context_trimming` configuration flag, defaulting to the baseline |
| 10 | Leave the consumer default and the baseline placeholder in place; correct the stale helper docstring |
| 11 | Declare `ResearcherOutputState.research_outcome` in `state.py` |
| 12 | Run the checks and record them in the build report |
| 13 | Flip the flag default after REQ-005 is `verified` (separate change) |

1. **Create the package.** Add `src/open_deep_research/context/__init__.py` exporting `plan_trim`, `TrimPlan`, `segment_turns`, `TurnLayout`, `ResearchTurn`, `classify_token_limit`, `compress_with_recovery`, `CompressionOutcome`, `TokenLimitExceeded`. Docstring of `__init__.py` names `REQ-005, ADR-005, INV-001`.

   In `pyproject.toml`, add `"open_deep_research.context"` to `[tool.setuptools] packages` (currently `["open_deep_research", "test"]`, L57). Because `[tool.setuptools.package-dir]` (L59-61) maps the literal package name `open_deep_research` to `src/open_deep_research`, the subpackage must be listed under its dotted name so that setuptools resolves it to `src/open_deep_research/context/`. `pyproject.toml` is a dependency/configuration file and needs human confirmation (`permission-model.md` §3). Verify after the change with `uv sync --extra dev` followed by `uv run python -c "import open_deep_research.context"`, and confirm that a non-editable build (`uv build`) contains `open_deep_research/context/__init__.py` in the wheel — `structural-constraints.md` §1 names this as the failure mode when the entry is missing.

2. **Message segmentation.** Implement `src/open_deep_research/context/messages.py`:
   - `ResearchTurn` dataclass: `index`, `ai_message`, `tool_messages`.
   - `segment_turns(messages, *, instruction_index=None)`: walk the list once; start a new turn at each `AIMessage`; attach a `ToolMessage` to the turn whose `ai_message.tool_calls[*]["id"]` contains its `tool_call_id`; messages before the first `AIMessage` go to `preamble`; the message at `instruction_index` (default: the last message) goes to `instruction`. A `ToolMessage` whose `tool_call_id` matches no turn stays with the preamble-side survivors and is never removable. There is no separate `trailing` collection: the instruction is always last, so nothing can follow it. Covers C-002.

3. **Trimming policy.** Implement `src/open_deep_research/context/trimming.py`:
   - `TrimPlan` dataclass: `messages` (the list to send) and `removed_turn_indices` (tuple of `ResearchTurn.index`).
   - `plan_trim(messages, *, instruction_index=None, max_removals=1)`: call `segment_turns`, compute the protected newest turn as `turns[-1]`, and choose the oldest `max_removals` turns among `turns[:-1]`. Rebuild the list in the **original order**: preamble, surviving turns in order, instruction last. Never reorder the instruction to the front. Return `None` when `turns` has fewer than two entries, i.e. when nothing is removable. No model call, no I/O. Covers C-001, C-002, M-001, M-002.

4. **Classification.** Implement `src/open_deep_research/context/classification.py`: `classify_token_limit(exc, model_name)` returns `utils.is_token_limit_exceeded(exc, model_name)` unchanged. No provider fallback, no second attempt with an empty model name: both would let `_check_openai_token_limit`'s unguarded `invalid_request_error` branch classify another provider's exception (see §3(c)). Log nothing; the caller records the decision. Covers C-003. `utils.py` is not modified in this step.

5. **Recovery loop.** Implement `src/open_deep_research/context/recovery.py`:
   - `class TokenLimitExceeded(Exception)` with fields `attempts`, `removed_turn_indices`, `last_exception`.
   - `compress_with_recovery(...)`: build `[SystemMessage(system_prompt)] + current_messages`; `attempt = 0`; loop until the removable turns are exhausted. The budget is **not** a fixed 3: with one turn removed per attempt, a fixed budget of 3 could only ever remove two turns and would end the task `failed` while removable history remained, which C-004 does not allow. Loop while `attempt < max_attempts`, where `max_attempts` defaults to `None` and, when `None`, is computed as the number of removable turns plus one (the extra attempt is the one that fails after the last turn is gone).
   - On each iteration call `await model.ainvoke(...)`; on success return `CompressionOutcome(summary=..., raw_notes=..., removed_turn_indices=...)`.
   - On exception increment `attempt` and call `classify_token_limit(exc, model_name)`.
     - If it is a token-limit error: call `plan_trim(current_messages, instruction_index=..., max_removals=max_removals_per_attempt)`; if it returns `None`, raise `TokenLimitExceeded`; otherwise replace `current_messages` with `plan.messages` and continue.
     - If it is not a token-limit error: **do not re-raise**. Retry the unchanged request, as the baseline does, so transient 429/5xx errors still recover, and continue the loop. When the loop ends, raise `TokenLimitExceeded`-style failure through the same node path with a category owned by REQ-001, not `token_limit`. Re-raising would escape into `asyncio.gather` (L305) and discard every parallel researcher's result.
   - The caller must not pass `max_removals_per_attempt` implicitly: step 8 passes it explicitly. `plan_trim`'s own default is `1`, so a caller that omits it removes one turn per attempt rather than all removable turns. Covers C-001, C-003, C-004.

6. **Raw notes helper.** In `context/recovery.py`, compute `raw_notes` from the surviving messages with `filter_messages(messages, include_types=["tool", "ai"])` and the same `"\n".join(str(m.content) ...)` format as the baseline (L554-557), so the note format seen by `supervisor_tools` does not change.

7. **Export and docs.** Check every public function's docstring names `REQ-005, ADR-005, INV-001` (`structural-constraints.md` §9). No `print` and no `logging` of message content.

8. **Make the node thin.** Rewrite the body of `compress_research` in `src/open_deep_research/deep_researcher.py` (L511-585):
   - read `Configuration` and build `synthesizer_model` exactly as today (L526-532) from `configurable.compression_model`;
   - keep the baseline branch when `configurable.context_trimming` is `False`, **byte-for-byte**, including the current three-attempt loop and the placeholder at L582-585;
   - when `True`: build `researcher_messages` from `state["researcher_messages"]`, append the compression instruction (L538), call `await compress_with_recovery(...)` with `model_name=configurable.compression_model` and `max_removals_per_attempt=1` passed **explicitly**, and return `{"compressed_research": outcome.summary, "raw_notes": [outcome.raw_notes]}`. `outcome.raw_notes` is the string computed in step 6; the node wraps it in a one-element list to match the existing `raw_notes` reducer format (`structural-constraints.md` §6: the format seen by `supervisor_tools` does not change);
   - catch `TokenLimitExceeded` and return `{"compressed_research": ..., "raw_notes": [...], "research_outcome": <failed ResearchOutcome with category "token_limit">}`. `research_outcome` is the declared `ResearcherOutputState` field added in step 11; a key that is not declared there is filtered out by Pydantic before `supervisor_tools` sees it, so the failure must travel in this field or not at all;
   - do not re-raise, and do not return placeholder text as a summary.
   - The node must not import trimming or classification helpers directly; it imports only the package's public names.

9. **Configuration flag.** Add to `src/open_deep_research/configuration.py`, near the compression fields (after L183): `context_trimming: bool = Field(default=False, metadata={"x_oap_ui_config": {"type": "boolean", "default": False, "description": "REQ-005: remove whole research turns from the oldest end when compression exceeds the model token limit"}})`. Default stays at the baseline behaviour (`structural-constraints.md` §8).

10. **Leave the consumer default alone and correct the stale helper.**
    - `supervisor_tools` in `src/open_deep_research/deep_researcher.py` (L308-313) is **not modified** by this ADR. The `dict.get` default at L310 stays as it is, so the flag-off path remains byte-identical to the baseline. This is deliberate: gating L310 on `context_trimming` would make `supervisor_tools` read `compress_research`'s configuration and would change the baseline consumer path, which defeats a switch whose purpose is to keep the pre-fix behaviour for A/B comparison. The remaining default is recorded as RISK-007.
    - The new path never reaches L310's default for a failed task, because the node returns a failed `research_outcome` and a normal `compressed_research`/`raw_notes` pair; it does not omit the key.
    - Grep for the literal `"Error synthesizing research report: Maximum retries exceeded"` and record every hit. The expected result is exactly two hits in `src/open_deep_research/deep_researcher.py`: L583 (baseline branch, retained intentionally) and L310 (consumer default, retained intentionally). The check is that **no third hit appears** and that neither retained hit sits on the `context_trimming = True` code path. A "zero hits" requirement is not used, because it could only be met by changing the baseline the flag is meant to preserve.
    - In `src/open_deep_research/utils.py`, correct the docstring of `remove_up_to_last_ai_message` (L848-857) to state that it removes up to and excluding the last `AIMessage`, and add a note that the REQ-005 path no longer uses it. Keep the function so no other caller breaks; do not change its behaviour.

11. **Declare the output field.** In `src/open_deep_research/state.py` (`ResearcherOutputState`, L92-96), add `research_outcome: ResearchOutcome | None = None`. This is the only state change in this ADR, and it is what carries a failed task result out of the researcher subgraph (see §3(d) and §5). `ResearchOutcome` is REQ-001's type; until it is merged, the field cannot be implemented end-to-end and step 8's `research_outcome` branch stays unrealised. `memory-design.md` §5 records the field, its writer and its reader. `ResearcherState` is unchanged.

12. **Checks.** Run `uv run ruff check src/open_deep_research test/offline scripts`, `uv run pytest test/offline`, and `uv run python scripts/validate_requirements.py`; record each command and its result in `docs/build-reports/REQ-005.md` (`permission-model.md` §4, `Prompt.md` §7). Include in the report the grep result from step 10, showing the two intentionally retained hits and no third one, and state explicitly that neither retained hit is on the `context_trimming = True` path.

13. **After verification only.** In the PR that marks REQ-005 `verified`, flip `context_trimming`'s default to `True` and decide, in that same PR, whether the two retained placeholder sites may then be removed. This is a separate change from steps 1–12 and needs its own review.
