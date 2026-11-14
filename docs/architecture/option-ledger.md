# Option Ledger

> **Purpose:** Every option that was considered and not chosen, why it lost, and the conditions under which it should be reconsidered. The evaluation table records the comparison at the moment of decision; this ledger keeps the road not taken so that a later change is a deliberate re-evaluation rather than a re-discovery.
> **Authoritative for:** the status of rejected and deferred options. The comparison itself stays in `docs/architecture/evaluation-table.md`; the decision stays in its ADR. Where this ledger disagrees with an EVAL entry, the EVAL entry wins and this row is corrected.
> **Maintained by:** each module owner adds rows for their module's EVAL entries; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-13

## How to Add an Entry

1. One row per **rejected or deferred option**, not per EVAL entry; an EVAL entry with two rejected options adds two rows.
2. `Option` names the EVAL entry and the option letter, so a reader can find the full comparison.
3. `Status`: **Dropped** (not viable now and unlikely to become viable), **Deferred** (viable later, on a stated trigger), or **Partially adopted** (a piece of it survives inside the chosen option).
4. `Reconsider when` must be an observable condition, not "if it becomes better". If the condition has no owner who could observe it, the option is not really deferrable and should be **Dropped**.
5. When an option is adopted later, do not edit the old row: mark it `Promoted to ADR-NNN` and add a new row pointing at the new EVAL entry. History stays readable.

## Ledger

| Ledger ID | Module | EVAL / ADR | Option | Status | Why it lost | Reconsider when |
|---|---|---|---|---|---|---|
| OPL-001 | context | EVAL-001 / ADR-005 | A — turn-aware trimming inside `compress_research`, helper in `utils.py` | Dropped | Places architectural logic in a graph node (`structural-constraints.md` §2, §8) and leaves the protected region untestable except through a node | Only if a later ADR dissolved the extension modules back into the nodes (no requirement motivates this) |
| OPL-002 | context | EVAL-001 / ADR-005 | C — token-budget estimator ahead of the call | Deferred | Solves "avoid the failed call", not "recover after it"; needs a provider-neutral tokenizer and drifts into REQ-005's `out_of_scope` | Repeated `token_limit` failures a budget check would avoid, or scope widened to token-limit configuration, or a tokenizer already in the dependency set, or run-level cost evidence |

## OPL-001 — Trimming written directly in the `compress_research` node

- **Module:** context
- **Evaluation entry:** EVAL-001, option A (`docs/architecture/evaluation-table.md`)
- **Decision it was offered against:** ADR-005
- **Status:** Dropped
- **Shape of the option:** `compress_research` itself splits the history into preamble, turns and instruction, removes from the oldest end, retries, and returns the failed `token_limit` result; `utils.remove_up_to_last_ai_message` is replaced by a turn-aware helper.
- **Why it lost:** it works and is the smallest diff, but it places architectural logic in a graph node, which `structural-constraints.md` §2 (thin nodes) and §8 (logic in the owner's extension module) forbid, and it leaves the protected region testable only end-to-end through a node that needs a model.
- **Salvage:** its grouping rule (one `AIMessage` plus its following `ToolMessage`s) is exactly what ADR-005 §3(a) adopts; only the *location* was rejected, not the algorithm.
- **Reconsider when:** never as an alternative to ADR-005. This row would only be revisited if the `context` module were dissolved — that is, if a later ADR merged every extension module back into the nodes, which no requirement currently motivates.

## OPL-002 — Proactive token-budget estimation before the compression call

- **Module:** context
- **Evaluation entry:** EVAL-001, option C (`docs/architecture/evaluation-table.md`)
- **Decision it was offered against:** ADR-005
- **Status:** Deferred
- **Shape of the option:** the compression path estimates the serialised request size for `compression_model` (via `utils.get_model_token_limit` plus a counting heuristic), trims oldest whole turns *before* the first call so the request fits, and keeps the reactive token-limit branch only as a backstop.
- **Why it lost:** it solves a different problem — avoiding the failed call — while REQ-005 asks for correct recovery *after* it. It also needs a provider-neutral tokenizer (a new dependency, `AGENTS.md` §4) and drifts into REQ-005's `out_of_scope` entry on token-limit configuration. Because it keeps the reactive path, it is a superset of ADR-005 rather than a competitor.
- **Salvage:** `get_model_token_limit` already exists in `utils.py` (L831-846) and could feed a planner without new dependencies if an approximate counter is acceptable.
- **Reconsider when:** **any** of the following becomes true —
  1. a live run or user report shows compression repeatedly exhausting the three attempts and ending as `failed` / `token_limit` while a budget check would have avoided it (this is the same trigger as RISK-005, so the two are tracked together);
  2. a requirement or an accepted ADR widens REQ-005's scope to cover token-limit configuration, so the `out_of_scope` barrier no longer applies;
  3. the project adopts a provider-neutral tokenizer that is already a dependency (for example through the LangChain model objects), so the "new dependency" objection disappears;
  4. cost or latency data shows the wasted first call on every token-limit retry is significant at the run level.

  Whichever fires, the change is an ADD round on the `context` module (`Prompt.md` §10): a new EVAL entry, and an ADR that either amends ADR-005 while it is still *Proposed* or supersedes it once *Accepted*.

## Promotion Records

| Ledger ID | Promoted to | Date | Notes |
|---|---|---|---|
| — | none yet | — | — |
