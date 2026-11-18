I'll start by reading the contract documents and the current state of the module sections I need to reason about.

I'll read the contract documents directly with read/grep.

Session-confirmed per-user workspace; reading with dedicated tools.

Now the checklist, module sections, and requirements.

# Simulated peer review — context/compression integration
**Perspective:** Tekon/BroZhai (context), using the supplied ADR-005 draft as standard. **Role:** AI reviewer, not Tekon, not a human, not Gate 1. All project tests: PLANNED / NOT_RUN.

## (1) Scenario table and document-level assessment

| # | Concrete input | Expected task status | Cost | Coverage | Exit / outcome | Note boundary |
|---|---|---|---|---|---|---|
| 1 | Both flags on. Fake compression model returns one string: free-text body, exactly one `<task_findings_v1>` block, unique final `### Sources`. Consumer hunk untouched, so the string is read raw through `TaskResult.summary`/`compressed_research`/notes. | `complete`/`partial` per parsed findings | receipt from evidence | from validated findings only | parser runs **once per attempt**; no second LLM pass | Body, sidecar and header must be stripped. With the consumer hunk unchanged, body reaches notes → violates ADR-002 §3.3 and INV-007. **Real gap (G3).** `CompressionOutcome.summary: str` is preserved — internally consistent with ADR-002 L159 and R-04. |
| 2 | Attempt 1 raises a token-limit error; oldest turn removed; attempt 2 has fewer history messages. | proceeds; on success as row 1 | unchanged | unchanged | context's loop only | `system_prompt` is rebuilt as `SystemMessage` inside each iteration (`recovery.py`), so it is not trimmed — **internally consistent**. `instruction_index` is computed once for the original list, then reused for a shorter list with messages already dropped in the middle (G1), and the loop counts every attempt toward `max_attempts` even successful ones → max calls = 2, not 3 (G2). No nesting **if** orchestration performs zero model calls in `compress_research`; otherwise ADR-002 L473–477 and L163–171 invite a second attempt (G3). |
| 3a | Unreducible: preamble + one AI turn + instruction; token error every time. | `failed`, `token_limit`, empty findings/summary | real started-tool cost via `evidence`; `usage_complete` as observed (False if any usage missing) | not counted | POL-006 | `compress_with_recovery` has **no `evidence` parameter**, and `TokenLimitExceeded` carries only attempts/indices/exception, so `failed_result(..., evidence=...)` cannot be satisfied (G4). |
| 3b | Ordinary runtime exception on compression. | `runtime` through the delivery/runtime owner; flag-off re-raises as today | same as 3a | none | flag-off and both-on together close the path, but **on/off** has an open type combination (G4) | Baseline `except: continue` then placeholder is replaced by re-raise; "propagates as today" (ADR-005 §6) is **inaccurate about today**. |
| 4a | Context on, orchestration off. No `TaskSpec`, no receipt. | `failed`, `token_limit` — no TaskResult exists | **not evidenced**: this path still uses `raw_notes`, which contains only AI/tool text, so executed calls are not counted | none | RunRecord `None`; outcome `failed`/`partial` pending delivery policy | `off/on` is a **declared pending decision** (POL-010, ADR-002 L386–390, memory §89, R-05). Needs a minimal honesty note: not baseline-equivalent, no evidence, no coverage (G4). |
| 4b | Orchestration on, context off. | typed result with degraded compression | receipt-backed | from validated findings | on/off | Baseline trimming (drop up to last AI, retry unchanged three times, placeholder) is the deliberate documented deviation from approved REQ-005 L446–454 and INV-001. That is a rollout state, but the document should say so explicitly (G5). Protected receipt/spec assembly must still be verified (ORC-041/018). |
| 5 | Model-invented `retrieved_urls`/cost/status/prose URLs; retrieved page says "ignore previous instructions"; duplicate fences; trimmed tool messages; fake model inspects received config. | status derived by code | receipt only | validated findings only | one selector | Assembling in a **fresh** `RunnableConfig` is a **shared joint decision** with delivery/dispatch and is **missing** from context's contract (G4). The question "can clean ambient config lose the evidence collector" is answered by ADR-002 L123–131 using `set_config_context` plus `create_task(context=...)` — a **declared** decision, not a contradiction. `source_urls` from `ResearchTurn` and from `ControlMessage` metadata in the baseline must not be treated as authority. |
| 6 | Task `T1` must answer Q1. Model returns a sourced, syntactically valid finding that answers nothing; `T1` has zero answered questions. Second case: coverage exactly `Fraction(str(threshold))`. Third: malformed sidecar. | `failed`/`unanswered`, empty summary → contributes no notes | cost retained | `T1`'s questions stay in denominator | exit per selector | ADR-002 L196–200 and L290–294 state this behaviour; INV-007 and ORC-024 cover it — **internally consistent**. "Deterministic threshold" is precision-dependent: L210 also says `Fraction(str(threshold))`, but L216 says `coverage_threshold = 0.8`. For example, `0.1 + 0.7 == 0.7999999999999999` (G5). |

**Document-level assessment.** The proposal is strongly aligned: exact signatures, typed failure, deterministic trimming/classification, honest NOT_RUN verdicts, the source of the request is recorded, the single-owner principle is respected, and context never duplicates ownership. Defects are mostly integration seams where the contract assumes a caller-side argument that no documented signature supplies.

## (2) At most five actionable new gaps

**G1 — `plan_trim` cannot apply a second trim to a shorter history.**
- **Anchor:** proposed ADR-005 §3(b), §5 (`plan_trim(..., instruction_index: int | None, ...)`), step 3; `utils.py:665-701` (unknown prefix tries every provider).
- **Why it matters:** with `max_attempts=3`, removing two turns is policy-correct (ADR-005 §7 C-001) but impossible: after the first removal, `instruction_index` and every `ResearchTurn.index` still refer to the original list. Implementation must recompute the index and the turn index after each trim.
- **Smallest fix:** after each trim, let `plan_trim` locate the instruction message by identity and return indices relative to the list just passed in. Adding one line to the interface with `str(instruction)` is not enough.

**G2 — attempt counting and budget.**
- **Anchor:** ADR-005 §5 `compress_with_recovery(..., max_attempts: int = 3, max_removals_per_attempt: int = 1)`; step 5 loop `while attempt < max_attempts`; ADR-002 L371–374; memory §88; POL-006.
- **Why it matters:** orchestrators can read "at most three attempts" as three model calls, but successful attempts also count, so the draft yields at most two model invocations. That is a downstream interface.
- **Smallest fix:** rename to `max_model_calls`, or state in §3(d) plainly "at most N−1 calls".

**G3 — parsing frequency and the unchanged consumer hunk.**
- **Anchor:** ADR-002 §3.3 L159–171 end ("it is not done per context attempt" is absent), L188–194, L473–477; structural §10 R-04 L105; checklist R-04/R-09; ADR-005 step 10 touching L310.
- **Why it matters:** step 10 proposes an edit to L310, which is delivery's `alchemy` region (R-09). Two conditional edits to the same line risk losing the other. There is also risk of duplicated or missing parsing.
- **Smallest fix:** state as an integration rule: one parse per validated successful `summary`; the disabled/no-result tool-response content is decided by a single resolved owner. Use no two literals. This is a stated R-09 decision, not a contract for the context module to implement.

**G4 — typed failures cannot be evidence-aware, and clean config is missing.**
- **Anchor:** ADR-002 §5 `failed_result(spec, category, message, *, evidence)`; ADR-005 step 8 catch; POL-010; R-02/R-05.
- **Why it matters:** `compress_with_recovery` never receives configuration or evidence, so both `token_limit` and `runtime` maps must recover the collector from outside the trimmed messages; otherwise cost becomes zero or `usage_complete` is silently lost (ORC-016, ORC-018).
- **Smallest fix:** add an interface note saying: "the `compress_research` node resolves evidence from configurable `_orchestration_evidence` with a fresh `RunnableConfig`; `not_run_result` is the only zero-cost case; the flag-off runtime category is a declared joint decision, not invented here."

**G5 — precision wording and an overclaim about baseline.**
- **Anchor:** ADR-002 L216 vs L210; §8 L425–427; ADR-005 §6 ("non-token exception → propagates as today").
- **Why it matters:** `0.1 + 0.7 == 0.7999999999999999`, so "is exactly 0.8" is wrong at that precision; float equality never decides coverage. Also, "propagates as today" is false: today, every exception in the three-attempt loop is swallowed and becomes a placeholder.
- **Smallest fix:** L216 should read "exactly 0.8 at 1-decimal precision"; L425–427 gains a qualified exception: "unless orchestration dispatch bounds the compression wait; no new guarantee is added"; ADR-005 §6 should read: re-raising replaces the baseline swallow-and-placeholder.

## (3) Consistency ledger

- **Internally consistent (not new findings):**
  - `CompressionOutcome.summary: str` is preserved.
  - The protected region is defined by message position, not model text.
  - Whole turns are removed; orphans are structurally impossible.
  - A `system_prompt` that is rebuilt per attempt is not trimmed.
  - No placeholder is returned as a summary.
  - A failed task contributes no notes; the threshold uses exact fractions.
  - One selector; one retry-other.

  These are consistent with ADR-002 §3.3/§3.4/§5 and INV-001/INV-007.
- **Declared pending reader decisions (do not call contradictions):**
  - on/on parse placement and renderer, plus a single notification channel.
  - off/on lifecycle and whether context re-raises or the node maps the failure (TEKON-or-Alchemy).
  - the single owner of compression failure mapping and R-09 consumer hunks (R-02, R-03, R-05, R-09).
  - whether dispatched children run in a clean config (compatibility, not clearly stated).
  - the exact probe order for cross-provider classification (`BaseException` vs `Exception`).
  - the proactive input-token budget gap (D2.2).
- **Actually missing contracts:**
  - the evidence handle passed into the node's failure mapping.
  - the flag-off runtime type for an ordinary compression exception.
  - a trim index model that survives a second attempt.
  - the precision semantics of the default threshold.
  - the quality of the `compress_research`→`supervisor_tools` output when the content is plain Markdown: it must not be read as notes. That behaviour is consistent only if step 10 is implemented by exactly one owner.

**Verdict.** Proposal is **sound in structure but not locally implementable** until G1–G5 are written down. No runtime PASS, no acceptance, and no other student's approval is implied.
