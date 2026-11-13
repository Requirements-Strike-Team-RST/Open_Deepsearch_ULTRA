# Evaluation Table

> **Purpose:** ADD results: for each architectural question, 2–3 candidate solutions compared on pros, cons, complexity and testability, and the choice made.
> **Authoritative for:** option comparisons. The decision itself is recorded in the ADR named in the entry.
> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-13

## How to Add an Entry

1. Copy the example below, take the next free `EVAL-NNN` number and keep the same fields.
2. **ASR:** list the requirements and the acceptance criteria (C-/M- IDs from `docs/req/requirements.yaml`) that shape the decision.
3. **Candidates:** describe 2–3 options; rate complexity and offline testability as Low, Medium or High.
4. **Choice:** name the chosen option and why it wins, say why each other option was rejected, then write the ADR.

## EVAL-NNN: <Question being decided>

- **Module:** <module from `architecture-blueprint.md` §4>
- **Owner:** <name>
- **Decision recorded in:** ADR-NNN
- **Status:** Open | Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-NNN | C-NNN, M-NNN | e.g. correctness, testability, cost |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | | | | | Low / Medium / High | Low / Medium / High |
| B | | | | | | |
| C (optional) | | | | | | |

**Choice:** <option> — <why it wins>.

**Rejected and why:** <option>: <reason>.

## EVAL-001: Token-limit recovery in `compress_research` — how the history is reduced

- **Module:** context
- **Owner:** BroZhai
- **Decision recorded in:** ADR-005 (`docs/architecture/adr/005-context_adr.md`)
- **Status:** Open

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-005 (invariant, `safety_relevant: true`) | C-001 (M-001 `latest_turn_preservation_rate == 1.0`) | Correctness: the newest research is never lost; determinism of the trimming decision (`structural-constraints.md` §7) |
| REQ-005 | C-002 (M-002 `orphan_tool_message_count == 0`) | Data integrity: no tool result without its requesting AI message |
| REQ-005 | C-003 | Correctness: token-limit errors are recognised for the model that made the call (`compression_model`, not `research_model`) |
| REQ-005 | C-004 | Fail-closed behaviour: an unreducible history ends the task as failed `token_limit`, never as placeholder text returned as a summary |
| REQ-001 (dependency) | task result carries status and reason | Coupling: the failure category must reach the supervisor through the REQ-001 task-result contract |
| INV-001 | fallback chain | Testability offline: trimming must be provable with fake models and no network |

The decision has to answer four distinct sub-questions sharing one loop: (a) the unit of removal, (b) how the protected region (topic, compression instruction, latest AI turn, tool results after it) is computed and kept, (c) how token-limit errors are classified per model, (d) what happens when the history can no longer be reduced. The candidates below are end-to-end strategies, not isolated patches, because the four sub-questions interact.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | **Turn-aware trimming inside `deep_researcher.py`.** `compress_research` splits `researcher_messages` into typed segments (preamble, research turns defined as one `AIMessage` plus the `ToolMessage`s that follow it, compression instruction), computes the protected region (instruction + latest turn + its tool results, and the research topic/task spec from the REQ-001 task specification carried on the message), then removes whole turns from the oldest end and retries. Classification uses `configurable.compression_model`. When no removable turn is left, the node returns the failed task result of category `token_limit`. | `deep_researcher.py` (`compress_research` only), `utils.py` (replace `remove_up_to_last_ai_message` with a turn-aware helper) | Smallest diff; no new module; no state or contract change; the loop already has a 3-attempt structure | Logic lives in a graph node, which `structural-constraints.md` §2 (thin nodes) and §8 (logic goes in the owner's extension module) forbid; the helper is a free function with no place to unit-test the protected region on its own; leaks REQ-001 task-result construction into the node | Low | Medium: can be tested through the node with fake models, but only end-to-end |
| B | **Dedicated `context` module — pure compaction policy plus an explicit `Compressor` loop.** `src/open_deep_research/context/` exposes (1) a pure, deterministic function `plan_trim(messages, protected, removable_turn_ids) -> TrimPlan` (returns the messages to keep and the turn IDs removed, or `None` when nothing removable is left), (2) `classify_token_limit(exc, model_name) -> bool` as the single entry point for the loop, and (3) `compress_with_recovery(...)`, a small orchestrator that runs the retry loop, asks the model, applies the plan, and on exhaustion raises a typed `TokenLimitExceeded` (or returns a failed task result of category `token_limit`). `compress_research` in `deep_researcher.py` becomes a thin node that calls `compress_with_recovery` and maps the outcome to the state. Failed results are emitted through the REQ-001 task-result type. Configuration flag `context_trimming` (default: baseline behaviour) so the improvement can be A/B-compared. | New `src/open_deep_research/context/` (`plan_trim`, `classify_token_limit`, `compress_with_recovery`, `TrimPlan` type, `TokenLimitExceeded` error); `deep_researcher.py` (`compress_research` becomes thin); `utils.py` (`is_token_limit_exceeded` kept, re-exported/delegated); `configuration.py` (one flag); `state.py` unchanged | Fits the blueprint module list (`context/`, REQ-005) and the thin-node rule; the trimming decision is pure and deterministic, so C-001/C-002/M-001/M-002 are unit-testable without any model; the classification bug (C-003) is fixed at one place; the failure path (C-004) is a typed result that the REQ-001 contract already expects; the flag keeps baseline behaviour until `verified` | More files and one new public interface; the module must not import `deep_researcher.py`, so the node supplies the task spec/topic to protect; coordination needed with the orchestration owner on the REQ-001 task-result type (shared contract, `structural-constraints.md` §6); tests must also prove the node is thin | Medium | High: `plan_trim`, `classify_token_limit` and the exhaustion path are pure functions tested with lists of fake messages and fake exception classes; only the loop needs a fake model |
| C | **Token-budget estimator ahead of the call (proactive trimming).** Instead of reacting to a provider error, the context module estimates the serialised size of the request with a token counter for the `compression_model` (using `utils.get_model_token_limit` plus a character/token heuristic), trims oldest whole turns before the first call so the request fits, and keeps the reactive token-limit branch only as a backstop. | New `context/` module with a counter and a budget planner; `configuration.py` (margin and counter settings); `deep_researcher.py`; `utils.py` | Avoids a wasted provider call and the 3-attempt ceiling; gives a deterministic pre-call invariant that is easy to monitor; helps models whose token-limit errors are not detectable by pattern | Token estimates are approximate (no universal tokenizer across OpenAI/Anthropic/Gemini), so a margin is still needed and the reactive path cannot be removed; the counter becomes a second source of truth that can drift from the provider; much larger scope than REQ-005 asks for (REQ-005's `out_of_scope` excludes token-limit configuration); a real tokenizer dependency would need human agreement (`AGENTS.md` §4) | High | Medium: the planner is testable with a fake counter, but the end-to-end guarantee (C-001) still depends on the reactive path, so it does not remove any test written for B |

**Choice:** **B** — a dedicated `context` module with a pure `plan_trim` decision, a single `classify_token_limit` entry point, and a `compress_with_recovery` loop called from a thin `compress_research`. It is the only option that keeps the safety-relevant decision deterministic and separately testable while staying inside the blueprint's module list, the thin-node rule and the REQ-005 scope. The remaining questions are settled inside B as follows: **(a)** the unit of removal is a *research turn* = one `AIMessage` + the `ToolMessage`s that follow it; **(b)** the protected region is the research topic / task specification, the compression instruction, and the newest AI turn together with its tool results — computed from message types, not from the model's text; **(c)** classification is `classify_token_limit(exc, configurable.compression_model)`, and an unknown provider falls back to checking all provider patterns; **(d)** when `plan_trim` returns `None`, the loop stops and produces a failed task result of category `token_limit`, and the placeholder string is removed.

**Rejected and why:** **A**: the fix is correct but puts architectural logic in a graph node, against `structural-constraints.md` §2 and §8, and leaves the protected region untestable on its own; it would have to be moved once a second requirement touches compression. **C**: solves a different problem (avoiding the failed call) rather than REQ-005's problem (recovering correctly after it), needs a tokenizer with no provider-neutral answer and a new dependency, and contradicts REQ-005's stated scope boundary around token-limit configuration; the reactive path it keeps is exactly B, so C is a later extension on top of B, not an alternative to it.
