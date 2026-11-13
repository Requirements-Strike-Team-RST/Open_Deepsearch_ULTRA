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

`compress_research` (`src/open_deep_research/deep_researcher.py` L511-585) is the last node of the researcher subgraph. It has three defects on the token-limit path:

1. **Wrong direction of removal.** On a token-limit error it calls `remove_up_to_last_ai_message` (L569-571). That helper (`src/open_deep_research/utils.py` L848-866) returns `messages[:i]` for the last index `i` holding an `AIMessage`, so it drops the newest AI turn, every `ToolMessage` after it, and the compression instruction appended at L538. The newest research is lost; the run continues.
2. **Misleading documentation.** The call-site comment says older messages are removed, while the helper docstring says recent context is removed. Two readings of the same function exist in the repository.
3. **Wrong model for classification.** The error is classified with `configurable.research_model` (L569) although the call used `configurable.compression_model` (L528). `utils.is_token_limit_exceeded` (L665-701) picks a provider-specific checker from the model-name prefix. With an `openai:*` research model and an Anthropic compression model, an Anthropic `BadRequestError` is handed to `_check_openai_token_limit` (L703-734), which requires an OpenAI exception class and returns `False`; `_check_anthropic_token_limit` (L736-757) is never consulted. The error is therefore unrecognised, the same request is retried unchanged, and after three attempts the node returns the string `"Error synthesizing research report: Maximum retries exceeded"` (L582-585) as the compressed summary.

Downstream, `supervisor_tools` (`deep_researcher.py` L298-330) reads `researcher_output_compressed_research` as normal research notes. The placeholder therefore reaches the final report as if it were a finding.

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
    messages.py          # ResearchTurn, TurnLayout, segment_turns(), extract_tool_source_urls()
    trimming.py          # plan_trim(), TrimPlan, ProtectedRegion
    classification.py    # classify_token_limit()
    recovery.py          # compress_with_recovery(), TokenLimitExceeded
```

### (a) Unit of removal — a research turn

A **research turn** is one `AIMessage` together with the contiguous `ToolMessage`s that immediately follow it. Everything before the first `AIMessage` is the **preamble** (the research topic `HumanMessage` written by `supervisor_tools` at L298). The compression instruction is appended last and is not a turn.

Invariants enforced by construction:

- A `ToolMessage` is never separated from the `AIMessage` that requested it, because removal happens on whole turns.
- A trailing `ToolMessage` block with no preceding `AIMessage` (a malformed history) belongs to no turn, is treated as part of the protected region, and is never removed. The history is not modified to repair it; that is outside REQ-005.

### (b) Protected region

The protected region is computed from message types, never from the model's text:

1. the preamble (position 0, the research topic),
2. the compression instruction (the last `HumanMessage`, identified by the node passing its index),
3. the newest AI turn and its tool results.

`plan_trim` may remove only turns strictly between the preamble and the newest turn, and only whole turns, starting from the oldest. The newest turn is protected and is never a candidate, which is what C-001 and M-001 assert.

### (c) Classification bound to the invoked model

`classification.classify_token_limit(exc, model_name)` is the only entry point used by the recovery loop, and the loop passes `configurable.compression_model`. It delegates to the existing `utils.is_token_limit_exceeded` so that provider patterns stay in one place, and adds the two cases the baseline misses:

- the model prefix selects the provider checker; an unknown prefix checks all patterns (baseline behaviour, preserved),
- an exception that carries provider metadata inconsistent with `model_name` is still recognised when another provider's pattern matches, so a compression call made with a model string of one provider and an exception class of another cannot silently classify as "not a token limit".

`utils.is_token_limit_exceeded` keeps its current signature and behaviour for `final_report_generation`; the new entry point is additive.

### (d) When the history can no longer be reduced

The recovery loop stops when `plan_trim` returns `None`, i.e. no removable turn is left, or when the attempt budget is exhausted. It then raises `TokenLimitExceeded(attempts, removed_turn_ids, last_exception)`; it never returns a string as a summary. The node maps the exception to the REQ-001 task result with status `failed` and category `token_limit`. The placeholder literal `"Error synthesizing research report: Maximum retries exceeded"` is removed.

### Behaviour switch

`Configuration.context_trimming: bool = False` (baseline default) selects the new path. While `False`, `compress_research` keeps the baseline code path byte-for-byte; the PR that marks REQ-005 `verified` flips the default (`structural-constraints.md` §8).

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — turn-aware trimming written directly inside `compress_research`, with a rewritten helper in `utils.py` | Smallest diff, but it puts architectural logic in a graph node, against `structural-constraints.md` §2 and §8, and leaves the protected region testable only end-to-end through the node. The second requirement that touches compression (REQ-001 task results) would force a second move. |
| C — estimate the token budget before the call and trim proactively | Solves a different problem (avoiding the failed call instead of recovering correctly after it), needs a provider-neutral tokenizer and therefore a new dependency, and contradicts REQ-005's `out_of_scope` boundary around token-limit configuration. The reactive path it keeps is exactly this decision, so it is a later extension on top of ADR-005, not an alternative. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `context/messages.py` | Split a message list into preamble, turns, trailing block; collect the tool-call ids and source URLs of a turn | `segment_turns(messages: list[MessageLikeRepresentation], instruction_index: int \| None) -> TurnLayout`   `TurnLayout(preamble: list[Message], turns: list[ResearchTurn], trailing: list[Message], instruction: Message \| None)`   `ResearchTurn(index: int, ai_message: AIMessage, tool_messages: list[ToolMessage], tool_call_ids: frozenset[str], source_urls: frozenset[str])` | `context/trimming.py`, `context/recovery.py` |
| `context/trimming.py` | Pure, deterministic decision about which turns to drop | `plan_trim(messages: list[MessageLikeRepresentation], *, instruction_index: int \| None, max_removals: int \| None = None) -> TrimPlan \| None`   `TrimPlan(messages: list[Message], removed_turn_indices: tuple[int, ...])` | `context/recovery.py` tests |
| `context/classification.py` | Decide once whether an exception is a token-limit error for the invoked model | `classify_token_limit(exc: BaseException, model_name: str) -> bool` | `context/recovery.py` |
| `context/recovery.py` | Run the retry loop, apply the trim plan, prepare the failed outcome | `async def compress_with_recovery(*, model: Runnable, system_prompt: str, messages: list[MessageLikeRepresentation], instruction: HumanMessage, model_name: str, max_attempts: int = 3, max_removals_per_attempt: int = 1) -> CompressionOutcome`   `CompressionOutcome(summary: str, raw_notes: str, removed_turn_indices: tuple[int, ...])`   `class TokenLimitExceeded(Exception): attempts, removed_turn_indices, last_exception` | `compress_research` in `deep_researcher.py` |
| `compress_research` node (thin) | Read configuration, call the module, map the outcome to state | existing `async def compress_research(state: ResearcherState, config: RunnableConfig)` signature unchanged | LangGraph (`researcher_builder`) |

**Error and result contract.**

- `TokenLimitExceeded` is raised only when the limit still applies after trimming or when nothing is removable.
- The node catches `TokenLimitExceeded` and builds the REQ-001 task result: `status="failed"`, `category="token_limit"`, `reason` listing the attempts and the removed turn indices, and `raw_notes` from the surviving messages. None of these is returned as a summary.
- If REQ-001's task-result type is not yet merged, the node records the failure in the researcher subgraph's failure field defined by REQ-001's ADR; this ADR does not define a second type.

**Shared contracts changed (`structural-constraints.md` §6):** the REQ-001 task-result type (owner: centay, orchestration) must be approved by centay and BroZhai before implementation. `state.py` is unchanged by this ADR, so no additional state owner is involved.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none added or changed. `ResearcherState` already carries `research_topic` (L88) and `researcher_messages` (L86), which are sufficient. No new field, no reducer change; details, if required by REQ-001, follow REQ-001's entry in `memory-design.md`.
- **Runtime policies:** three policies for `runtime-policy-catalog.md` §2 — POL to be numbered at integration:
  - *token-limit on compression, reducible history* → trim the oldest turn and retry, at most `max_attempts`;
  - *token-limit on compression, unreducible history* → stop, raise `TokenLimitExceeded`, task result `failed` / `token_limit`;
  - *non-token exception on compression* → not handled by this module; it propagates as today so REQ-002/REQ-004 own it.
- **Invariants:** INV-001 (details in `invariants.md`).
- **Deterministic boundary:** `plan_trim` decides which turns to remove, and `classify_token_limit` decides whether the exception is a token-limit error; both are pure functions with no model call. The model only produces the compressed text and the provider error that is passed in as input. The decision to end the task as `failed` rather than to summarise is made by code, not by prompt text.

## 7. Verification

| Criterion | How it is verified | Test |
|---|---|---|
| C-001 / M-001 `latest_turn_preservation_rate == 1.0` | `plan_trim` is called with a fake history of preamble + three AI turns with tool results + instruction. The result must remove exactly the two oldest turns, keep the preamble, the newest turn with its tool results and the instruction; the newest turn index must never appear in `removed_turn_indices`. A second case runs `compress_with_recovery` with a fake model that raises a token-limit error until two turns are gone. | `test/offline/test_context_compaction.py::test_oldest_turns_removed_first` |
| C-002 / M-002 `orphan_tool_message_count == 0` | Property-style over generated histories: every `ToolMessage` in the trimmed list must follow an `AIMessage` whose `tool_calls` contain its `tool_call_id`; count of orphans must be 0. | `test/offline/test_context_compaction.py::test_no_orphan_tool_messages` |
| C-003 | Fake Anthropic `BadRequestError` ("prompt is too long") with `compression_model="anthropic:..."` and `research_model="openai:..."`: `classify_token_limit(exc, compression_model)` is `True`, the loop trims before the second call, and a fake that fails the same request twice is never retried unchanged. | `test/offline/test_context_compaction.py::test_classification_uses_compression_model` |
| C-004 | History of preamble + one AI turn + instruction, with a model that always raises a token-limit error: `compress_with_recovery` raises `TokenLimitExceeded`, the node returns status `failed` with category `token_limit`, and no summary contains the placeholder string. | `test/offline/test_context_compaction.py::test_unreducible_history_ends_failed` |
| INV-001 | The union of the four cases above fails if any invariant clause is broken; the `latest_turn_preservation_rate` and `orphan_tool_message_count` monitors are computed from the same helpers. | `test/offline/test_context_compaction.py` |
| Thin node (`structural-constraints.md` §2) | Static check that `compress_research` contains no trimming or classification logic, only configuration reading, one module call and state mapping. | Reviewed in the PR diff; recorded in `docs/review-memo.md` |
| Regression | Full offline suite, including `test/offline/test_contracts.py` if the REQ-001 task-result type changes. | `uv run pytest test/offline` |

The module's case table (TC-IDs, input and expected result per case) is written in `verification-constraints.md` §7 at the module-sections step.

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

- The graph topology, prompts, configuration of models and `state.py` are unchanged; the behaviour switch defaults to the baseline.
- `remove_up_to_last_ai_message` has no remaining caller on the new path. It is kept with a corrected docstring and a deprecation note rather than deleted, because deletion of a public helper is a separate change (`structural-constraints.md` §5, "Extend, never replace").

**Effect on other modules**

- *orchestration* (REQ-001): must accept the `failed` / `token_limit` result; shared-contract approval required.
- *delivery* (REQ-004): gains a clean failure signal, so an outcome of `partial` or `failed` can be derived without parsing text.
- *evaluation*: unchanged; the compression prompt is untouched, so no prompt version bump.

**Risks and alternatives:** the risks this decision carries are RISK-001 to RISK-006 in `docs/architecture/risk-list.md`; the rejected options and their re-evaluation conditions are OPL-001 and OPL-002 in `docs/architecture/option-ledger.md`.

## 9. Implementation Steps

Ordered steps for the coding agent. Each step names the files it changes and the acceptance criterion it serves. Steps 1–7 are new code; step 8 wires the node; step 9 adds the flag; step 10 is regression.

1. **Create the package.** Add `src/open_deep_research/context/__init__.py` exporting `plan_trim`, `TrimPlan`, `segment_turns`, `TurnLayout`, `ResearchTurn`, `classify_token_limit`, `compress_with_recovery`, `CompressionOutcome`, `TokenLimitExceeded`. Add `open_deep_research.context` to `[tool.setuptools] packages` in `pyproject.toml` (this file needs human confirmation, `permission-model.md` §3). Docstring of `__init__.py` names `REQ-005, ADR-005, INV-001`.

2. **Message segmentation.** Implement `src/open_deep_research/context/messages.py`:
   - `ResearchTurn` dataclass: `index`, `ai_message`, `tool_messages`, `tool_call_ids` (from `ai_message.tool_calls[*]["id"]`), `source_urls` (URLs in tool results, reused later by REQ-001's source check).
   - `segment_turns(messages, instruction_index)`: walk the list once; start a new turn at each `AIMessage`; append following `ToolMessage`s to the current turn; messages before the first `AIMessage` go to `preamble`; a `ToolMessage` block with no current turn, and the message at `instruction_index`, go to `trailing`/`instruction`. Covers C-002.

3. **Trimming policy.** Implement `src/open_deep_research/context/trimming.py`:
   - `TrimPlan` dataclass: `messages` (the list to send) and `removed_turn_indices` (tuple of `ResearchTurn.index`).
   - `plan_trim(messages, *, instruction_index, max_removals=None)`: call `segment_turns`, compute the protected newest turn as `turns[-1]`, and choose the oldest up-to-`max_removals` turns among `turns[:-1]`; keep `preamble + instruction + surviving turns + trailing` in the original order. Return `None` when `turns` has fewer than two entries or when `turns[:-1]` is empty. No model call, no I/O. Covers C-001, C-002, M-001, M-002.

4. **Classification.** Implement `src/open_deep_research/context/classification.py`: `classify_token_limit(exc, model_name)` returns `True` when `utils.is_token_limit_exceeded(exc, model_name)` is `True`; otherwise, extract the provider prefix from `model_name` and, when the prefix names a provider, additionally try `utils.is_token_limit_exceeded(exc, "")` so an exception whose class does not match the model string is still recognised. Log nothing; the caller records the decision. Covers C-003. `utils.py` is not modified in this step.

5. **Recovery loop.** Implement `src/open_deep_research/context/recovery.py`:
   - `class TokenLimitExceeded(Exception)` with fields `attempts`, `removed_turn_indices`, `last_exception`.
   - `compress_with_recovery(...)`: build `[SystemMessage(system_prompt)] + current_messages`; `attempt = 0`; loop while `attempt < max_attempts`; call `await model.ainvoke(...)`; on success return `CompressionOutcome(summary=str(response.content), raw_notes=..., removed_turn_indices=...)`; on exception increment `attempt`, call `classify_token_limit(exc, model_name)`; if not a token-limit error, re-raise the original exception unchanged (REQ-002/REQ-004 own it); if it is, call `plan_trim(current_messages, instruction_index=...)`; if `None`, raise `TokenLimitExceeded`; otherwise replace `current_messages` with `plan.messages` and continue. After the loop raise `TokenLimitExceeded`. Covers C-001, C-003, C-004.

6. **Raw notes helper.** In `context/recovery.py`, compute `raw_notes` from the surviving messages with `filter_messages(messages, include_types=["tool", "ai"])` and the same `"\n".join(str(m.content) ...)` format as the baseline (L554-557), so the note format seen by `supervisor_tools` does not change.

7. **Export and docs.** Check every public function's docstring names `REQ-005, ADR-005, INV-001` (`structural-constraints.md` §9). No `print` and no `logging` of message content.

8. **Make the node thin.** Rewrite the body of `compress_research` in `src/open_deep_research/deep_researcher.py` (L511-585):
   - read `Configuration` and build `synthesizer_model` exactly as today (L526-532) from `configurable.compression_model`;
   - keep the baseline branch when `configurable.context_trimming` is `False`, unchanged, including the current three-attempt loop;
   - when `True`: build `researcher_messages` from `state["researcher_messages"]`, append the compression instruction (L538), call `await compress_with_recovery(...)` with `model_name=configurable.compression_model`, `max_attempts=3`, and return `{"compressed_research": outcome.summary, "raw_notes": [outcome.raw_notes]}`;
   - catch `TokenLimitExceeded` and return the REQ-001 `failed` / `token_limit` task result; do not return any placeholder string.
   - The node must not import trimming or classification helpers directly; it imports only the package's public names.

9. **Configuration flag.** Add to `src/open_deep_research/configuration.py`, near the compression fields (after L183): `context_trimming: bool = Field(default=False, metadata={"x_oap_ui_config": {"type": "boolean", "default": False, "description": "REQ-005: remove whole research turns from the oldest end when compression exceeds the model token limit"}})`. Default stays at the baseline behaviour (`structural-constraints.md` §8).

10. **Correct the stale helper and docs.** In `src/open_deep_research/utils.py`, correct the docstring of `remove_up_to_last_ai_message` (L848-857) to state that it removes up to and excluding the last `AIMessage`, add a note that it is not used by the REQ-005 path, and keep the function so no other caller breaks. Do not change its behaviour.

11. **Checks.** Run `uv run ruff check src/open_deep_research test/offline scripts`, `uv run pytest test/offline`, and `uv run python scripts/validate_requirements.py`; record each command and its result in `docs/build-reports/REQ-005.md` (`permission-model.md` §4, `Prompt.md` §7).

12. **After verification only.** In the PR that marks REQ-005 `verified`, flip `context_trimming`'s default to `True`. This is a separate change from steps 1–11 and needs its own review.
