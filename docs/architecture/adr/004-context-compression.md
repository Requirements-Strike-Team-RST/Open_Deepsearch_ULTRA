# ADR-004: Token-limit recovery in compression removes the oldest whole turns

- **Status:** Accepted
- **Date:** 2026-11-17
- **Module:** context
- **Owner:** BroZhai
- **Evaluation:** EVAL-004 (`docs/architecture/evaluation-table.md`)
- **SA Review:** passed in the SA integration PR [#22](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/22) (approved by BroZhai and DopplerXD, merged 2026-11-18)

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-005 | C-001, M-001 | What to remove is decided by code; the newest turn is never removed. |
| REQ-005 | C-002, M-002 | The unit of removal is a whole turn (an `AIMessage` with its `ToolMessage`s), so no tool result is left without its request. |
| REQ-005 | C-003 | Token-limit errors are classified with the model that made the call, `compression_model`. |
| REQ-005 | C-004 | A history that cannot be reduced ends as a failed task of category `token_limit` (the REQ-001 result type), not as placeholder text. |

## 2. Context

Baseline (`deep_researcher.py` and `utils.py`, line numbers at commit `daf6947`):

1. On a token-limit error, `compress_research` calls `remove_up_to_last_ai_message` (L569-571, `utils.py` L848-866). It cuts the history at the last `AIMessage`, so it drops the newest turn, its tool results and the compression instruction appended at L538.
2. The call-site comment says older messages are removed; the helper's docstring says recent ones are.
3. The error is classified with `research_model` (L569) although the call used `compression_model` (L528). An Anthropic token-limit error from the compression model is not recognised when the research model is OpenAI, so the same request is retried unchanged.
4. After three attempts the node returns `"Error synthesizing research report: Maximum retries exceeded"` (L582-585) as the summary.

`utils.is_token_limit_exceeded` is also used by `final_report_generation`; its behaviour must not change.

## 3. Decision

Use EVAL-004 option B: a `context` module with a pure trimming function and one recovery loop, called from `compress_research`. Active when `Configuration.context_trimming` is `True` (default `False`).

**Turns and protected messages.** A turn is one `AIMessage` plus the `ToolMessage`s whose `tool_call_id` is in that message's `tool_calls`. Pairing is by id, not position. Messages before the first `AIMessage` are the preamble (the research topic or, with `task_contract_enabled`, the task brief). The last message is the compression instruction. The preamble, the instruction and the newest turn are never removed. A `ToolMessage` whose id matches no `AIMessage` is kept and never removed.

**Trimming.** `trim_oldest_turn(messages)` returns the list without its oldest removable turn, in the original order, or `None` when only the newest turn is left.

**Recovery loop.** `compress_with_recovery(model, system_prompt, messages, model_name)`:

- calls the model; on success returns the response text;
- on an error that `utils.is_token_limit_exceeded(exc, model_name)` recognises (the caller passes `compression_model`), removes the oldest turn and retries; when nothing is left to remove, raises `CompressionFailed(category="token_limit")`;
- on any other error, retries the same request, at most 3 attempts in total as in the baseline; then raises `CompressionFailed(category="runtime")`.

The two counters are separate, so transient errors never use up the trimming that a long history needs, and every removable turn can be tried.

**Failure mapping** (in `compress_research`, ADR-001 §3.3): with `task_contract_enabled` on, `CompressionFailed` becomes `TaskResult.failed(spec, e.category, e.reason, tool_calls=tool_calls_spent)` and `compressed_research` is empty, so nothing reaches `notes`. With `task_contract_enabled` off there is no task result, so the node returns the baseline placeholder; REQ-005 C-004 is verified with both flags on.

The module does not change `supervisor_tools`, `prompts.py` or `utils.py` behaviour. Only the docstring of `remove_up_to_last_ai_message` is corrected.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — turn-aware trimming written inside `compress_research` | Puts the logic in a graph node (`structural-constraints.md` §2, §8); it can only be tested through the node. |
| C — estimate tokens before the call and trim early | Needs a tokenizer for every provider (a new dependency) and token-limit configuration, which REQ-005 puts out of scope. It can be added later on top of this design (RISK-012). |
| A new output field `research_outcome` and a guard in `supervisor_tools` (an earlier draft) | Duplicates the REQ-001 `task_result` field under a name that `AgentState` already uses for the run outcome, and edits delivery's code region. |

The full comparison is in EVAL-004.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `context/trimming.py` | Split turns and remove the oldest one | `split_turns(messages) -> tuple[list, list[list], BaseMessage]` (preamble, turns, instruction); `trim_oldest_turn(messages) -> list \| None` | `context/recovery.py`, tests |
| `context/recovery.py` | Retry loop | `async compress_with_recovery(model, system_prompt, messages, model_name, max_transient_attempts=3) -> str`; `class CompressionFailed(Exception)` with `category`, `reason`, `removed_turns` | `compress_research` |

No shared contract is added. The module itself does not use `TaskResult`; `compress_research` maps `CompressionFailed` to `TaskResult.failed` (ADR-001).

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none. Trimming works on a local copy of the messages; the stored history is not changed.
- **Runtime policies:** POL-012, POL-013, POL-014.
- **Invariants:** INV-001.
- **Deterministic boundary:** which turns are removed and whether an error is a token-limit error are decided by code; the model only writes the summary.

## 7. Verification

The cases for REQ-005 are in `verification-constraints.md` §7 (context). `trim_oldest_turn` is tested with message lists; the loop with a fake model that raises provider-shaped errors.

## 8. Consequences

- **Positive:** the newest research survives every retry; orphan tool messages cannot appear; a mixed-provider setup recovers correctly; an unreducible history is an explicit failure.
- **Negative:** a very long newest turn can still be too large, and then the task fails (RISK-008); errors that do not match the provider patterns are retried as transient (RISK-007); the preamble is found from message types, which a new message type could break (RISK-006); no input size is checked before a call (RISK-012).
- **Neutral:** with the flag off, the baseline loop runs unchanged, including its placeholder.

## 9. Implementation Steps

1. Add `context/__init__.py`, `trimming.py` and `recovery.py`; add `open_deep_research.context` to `[tool.setuptools] packages`. Docstrings name `REQ-005, ADR-004, INV-001`.
2. `configuration.py`: add `context_trimming: bool = False` with `x_oap_ui_config` metadata.
3. `compress_research`: when the flag is on, call `compress_with_recovery(..., model_name=configurable.compression_model)` instead of the baseline loop, and map `CompressionFailed` as in §3. Keep the baseline loop for the flag-off path.
4. `utils.py`: correct the docstring of `remove_up_to_last_ai_message` only.
5. Run the checks in `verification-constraints.md` §4 and record them in `docs/build-reports/REQ-005.md`.
